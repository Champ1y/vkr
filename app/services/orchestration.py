from __future__ import annotations

import time

from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import DomainError, NotFoundError
from app.core.logging import get_logger
from app.db.enums import CorpusType, ModeType, QueryStatus
from app.repositories.queries import QueryRepository
from app.repositories.versions import VersionRepository
from app.schemas.ask import AskRequest, AskResponse, TutorialPayload
from app.schemas.common import SourceOut
from app.services.adapters.embeddings import EmbeddingServiceFactory
from app.services.adapters.generation import GenerationService
from app.services.query_processing import QueryAnalysis, analyze_query
from app.services.reranking import RerankingService
from app.services.retrieval import RetrievalService
from app.services.types import RankedChunk, RetrievedChunk

logger = get_logger(__name__)


class AskOrchestrationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.version_repo = VersionRepository(db)
        self.query_repo = QueryRepository(db)
        self.retrieval = RetrievalService(db)
        self.reranker = RerankingService()
        self.embedding = EmbeddingServiceFactory.create()
        self.generator = GenerationService()

    @staticmethod
    def resolve_corpora(answer_mode: str) -> list[str]:
        if answer_mode == ModeType.TUTORIAL.value:
            return [CorpusType.OFFICIAL.value, CorpusType.SUPPLEMENTARY.value]
        return [CorpusType.OFFICIAL.value]

    @staticmethod
    def _has_sufficient_evidence(*, ranked: list[RankedChunk], analysis: QueryAnalysis, answer_mode: str) -> bool:
        if not ranked:
            return False

        official_ranked = [item for item in ranked if item.corpus_type == CorpusType.OFFICIAL.value]
        if not official_ranked:
            return False

        top = official_ranked[0]
        top_window = official_ranked[: min(4, len(official_ranked))]
        max_term_overlap = max(item.technical_term_overlap for item in top_window)
        max_lexical_overlap = max(item.lexical_overlap for item in top_window)
        max_title_overlap = max(item.title_section_overlap for item in top_window)

        weak_score = top.score < 0.32
        weak_signal = (
            top.semantic_similarity < 0.43
            and max_lexical_overlap < 0.06
            and max_title_overlap < 0.06
            and max_term_overlap < 0.10
        )
        if weak_score and weak_signal:
            return False

        min_term_overlap = 0.10 if analysis.intent == "compatibility" else 0.16
        if analysis.is_logical_replication and max_term_overlap < min_term_overlap:
            return False
        if analysis.is_logical_replication:
            anchor_markers = (
                "logical replication",
                "publication",
                "subscription",
                "restriction",
                "compatibility",
                "major version",
                "publisher",
                "subscriber",
                "wal_level",
                "max_replication_slots",
                "max_wal_senders",
                "replication slot",
                "pg_createsubscriber",
            )
            has_anchor_source = any(
                any(marker in f"{item.title} {item.section_path}".lower() for marker in anchor_markers)
                for item in top_window
            )
            if not has_anchor_source:
                return False

        if answer_mode == ModeType.TUTORIAL.value and analysis.intent == "procedural" and max_term_overlap < 0.12:
            return False

        return True

    @staticmethod
    def _insufficient_answer(*, pg_version: str) -> str:
        return (
            f"Недостаточно подтвержденных данных в найденных фрагментах официальной документации PostgreSQL {pg_version}, "
            "чтобы дать точный ответ без домыслов. Уточните формулировку вопроса "
            "или добавьте более конкретные термины (например, publication/subscription/wal_level)."
        )

    @staticmethod
    def _insufficient_tutorial(*, pg_version: str) -> TutorialPayload:
        return TutorialPayload(
            short_explanation=(
                f"В текущем наборе источников PostgreSQL {pg_version} недостаточно подтвержденной информации "
                "для безопасного пошагового руководства."
            ),
            prerequisites=[],
            steps=[],
            notes=[
                "Чтобы избежать недостоверной инструкции, шаги не сгенерированы.",
                "Уточните задачу техническими терминами (например: publication, subscription, replication slot, wal_level).",
            ],
        )

    @staticmethod
    def _merge_retrieved_unique(rows: list[RetrievedChunk]) -> list[RetrievedChunk]:
        unique: dict[str, RetrievedChunk] = {}
        for item in rows:
            key = str(item.chunk_id)
            if key not in unique:
                unique[key] = item
        return list(unique.values())

    def _ensure_tutorial_supplementary(
        self,
        *,
        answer_mode: str,
        question_vector: list[float],
        pg_version: str,
        query_terms: list[str],
        candidates: list[RetrievedChunk],
    ) -> list[RetrievedChunk]:
        if answer_mode != ModeType.TUTORIAL.value:
            return candidates
        if any(item.corpus_type == CorpusType.SUPPLEMENTARY.value for item in candidates):
            return candidates

        supplementary_candidates = self.retrieval.retrieve(
            query_vector=question_vector,
            pg_version=pg_version,
            corpora=[CorpusType.SUPPLEMENTARY.value],
            query_terms=query_terms,
            top_k=max(4, min(settings.retrieval_top_k, settings.rerank_top_k)),
        )
        if not supplementary_candidates:
            return candidates

        merged = self._merge_retrieved_unique(candidates + supplementary_candidates)
        logger.info(
            "Tutorial retrieval added supplementary candidates version=%s base=%d supplementary=%d merged=%d",
            pg_version,
            len(candidates),
            len(supplementary_candidates),
            len(merged),
        )
        return merged

    def handle_ask(self, req: AskRequest) -> AskResponse:
        started = time.perf_counter()
        version = self.version_repo.get_by_major(req.pg_version)

        if not version or not version.is_supported:
            elapsed = int((time.perf_counter() - started) * 1000)
            self.query_repo.create_failed_query(
                version=version,
                question=req.question,
                mode=req.answer_mode,
                latency_ms=elapsed,
            )
            raise NotFoundError(f"Unsupported PostgreSQL version: {req.pg_version}")

        effective_question = req.question
        analysis = analyze_query(effective_question)

        corpora = self.resolve_corpora(req.answer_mode)
        if req.answer_mode in {ModeType.SHORT.value, ModeType.DETAILED.value} and CorpusType.SUPPLEMENTARY.value in corpora:
            raise DomainError("supplementary corpus is forbidden in short/detailed modes")

        try:
            question_vector = self.embedding.embed_text(analysis.embedding_query)
            retrieved = self.retrieval.retrieve(
                query_vector=question_vector,
                pg_version=req.pg_version,
                corpora=corpora,
                query_terms=analysis.expanded_terms,
                top_k=settings.retrieval_top_k,
            )
            retrieved = self._ensure_tutorial_supplementary(
                answer_mode=req.answer_mode,
                question_vector=question_vector,
                pg_version=req.pg_version,
                query_terms=analysis.expanded_terms,
                candidates=retrieved,
            )

            if not retrieved:
                raise DomainError("No relevant documentation fragments found for selected version", status.HTTP_404_NOT_FOUND)

            ranked = self.reranker.rerank(
                question=effective_question,
                candidates=retrieved,
                answer_mode=req.answer_mode,
                query_analysis=analysis,
                top_k=settings.rerank_top_k,
            )

            official_count = sum(1 for item in ranked if item.corpus_type == CorpusType.OFFICIAL.value)
            if official_count == 0:
                raise DomainError(
                    "Official corpus did not return relevant sources for this question and version",
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            has_sufficient_evidence = self._has_sufficient_evidence(ranked=ranked, analysis=analysis, answer_mode=req.answer_mode)
            if not has_sufficient_evidence:
                if req.answer_mode in {ModeType.SHORT.value, ModeType.DETAILED.value}:
                    answer = self._insufficient_answer(pg_version=req.pg_version)
                    tutorial = None
                else:
                    tutorial = self._insufficient_tutorial(pg_version=req.pg_version)
                    answer = None
            else:
                if req.answer_mode in {ModeType.SHORT.value, ModeType.DETAILED.value}:
                    answer = self.generator.generate_answer(
                        question=effective_question,
                        pg_version=req.pg_version,
                        answer_mode=req.answer_mode,
                        ranked_chunks=ranked,
                    )
                    tutorial = None
                else:
                    tutorial = self.generator.generate_tutorial(
                        question=effective_question,
                        pg_version=req.pg_version,
                        ranked_chunks=ranked,
                    )
                    answer = None

            latency_ms = int((time.perf_counter() - started) * 1000)
            self.query_repo.create_query(
                version=version,
                question=req.question,
                mode=req.answer_mode,
                answer_text=answer,
                tutorial_payload=tutorial,
                status=QueryStatus.SUCCESS.value,
                latency_ms=latency_ms,
                sources=ranked,
            )

            sources_out = [
                SourceOut(
                    title=item.title,
                    url=item.source_url,
                    corpus_type=item.corpus_type,
                    source_role=item.source_role,
                    section_path=item.section_path,
                    rank_position=item.rank_position,
                    similarity_score=round(item.score, 5),
                )
                for item in ranked
            ]

            if req.answer_mode in {ModeType.SHORT.value, ModeType.DETAILED.value}:
                return AskResponse(
                    answer_mode=req.answer_mode,
                    pg_version=req.pg_version,
                    answer=answer,
                    sources=sources_out,
                )

            return AskResponse(
                answer_mode="tutorial",
                pg_version=req.pg_version,
                tutorial=tutorial,
                sources=sources_out,
            )

        except DomainError:
            elapsed = int((time.perf_counter() - started) * 1000)
            self.db.rollback()
            self.query_repo.create_failed_query(
                version=version,
                question=req.question,
                mode=req.answer_mode,
                latency_ms=elapsed,
            )
            raise
        except RuntimeError as exc:
            logger.warning("Runtime pipeline error: %s", exc)
            elapsed = int((time.perf_counter() - started) * 1000)
            self.db.rollback()
            self.query_repo.create_failed_query(
                version=version,
                question=req.question,
                mode=req.answer_mode,
                latency_ms=elapsed,
            )
            raise DomainError(str(exc), status.HTTP_503_SERVICE_UNAVAILABLE) from exc
        except Exception as exc:
            logger.exception("Unhandled ask pipeline error: %s", exc)
            elapsed = int((time.perf_counter() - started) * 1000)
            self.db.rollback()
            self.query_repo.create_failed_query(
                version=version,
                question=req.question,
                mode=req.answer_mode,
                latency_ms=elapsed,
            )
            raise DomainError("Internal error while processing request", status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
