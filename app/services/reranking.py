from __future__ import annotations

from app.core.config import settings
from app.db.enums import CorpusType, SourceRole
from app.services.query_processing import (
    QueryAnalysis,
    analyze_query,
    logical_confusion_penalty,
    overlap_ratio,
    technical_term_overlap,
    tokenize,
)
from app.services.types import RankedChunk, RetrievedChunk


class RerankingService:
    @staticmethod
    def _limit_per_document(
        rows: list[tuple[RetrievedChunk, float, float, float, float, float]],
        *,
        max_per_document: int,
    ) -> list[tuple[RetrievedChunk, float, float, float, float, float]]:
        per_doc: dict[str, int] = {}
        filtered: list[tuple[RetrievedChunk, float, float, float, float, float]] = []
        for row in rows:
            candidate = row[0]
            doc_key = str(candidate.document_id)
            if per_doc.get(doc_key, 0) >= max_per_document:
                continue
            per_doc[doc_key] = per_doc.get(doc_key, 0) + 1
            filtered.append(row)
        return filtered

    @staticmethod
    def _role_bonus(*, mode: str, intent: str, role: str) -> float:
        if mode == "tutorial":
            base = {
                "prerequisite": 0.08,
                "step": 0.10,
                "example": 0.07,
                "warning": 0.06,
                "overview": 0.03,
            }.get(role, 0.0)
            if intent == "procedural" and role in {"prerequisite", "step", "example"}:
                base += 0.04
            return base

        base = {
            "overview": 0.07,
            "warning": 0.06,
            "example": 0.03,
            "step": 0.01,
            "prerequisite": 0.01,
        }.get(role, 0.0)
        if intent in {"definition", "factual"} and role in {"overview", "warning"}:
            base += 0.03
        return base

    def rerank(
        self,
        *,
        question: str,
        candidates: list[RetrievedChunk],
        mode: str,
        extended_mode: bool,
        query_analysis: QueryAnalysis | None = None,
        top_k: int | None = None,
    ) -> list[RankedChunk]:
        if not candidates:
            return []

        effective_top_k = top_k or settings.rerank_top_k
        analysis = query_analysis or analyze_query(question)
        q_tokens = analysis.tokens

        scored: list[tuple[RetrievedChunk, float, float, float, float, float]] = []
        for candidate in candidates:
            body_tokens = tokenize(candidate.chunk_text)
            title_section = f"{candidate.title} {candidate.section_path}"
            title_section_tokens = tokenize(title_section)

            lexical_overlap = overlap_ratio(q_tokens, body_tokens)
            title_section_overlap = overlap_ratio(q_tokens, title_section_tokens)
            term_overlap = max(
                technical_term_overlap(candidate.chunk_text, analysis.technical_terms),
                technical_term_overlap(title_section, analysis.technical_terms),
            )
            logical_anchor_overlap = max(
                technical_term_overlap(candidate.chunk_text, {"logical replication", "publication", "subscription"}),
                technical_term_overlap(title_section, {"logical replication", "publication", "subscription"}),
            )

            # cosine distance expected in [0, 2] for pgvector cosine_distance
            semantic_similarity = max(0.0, 1.0 - (candidate.distance / 2.0))
            lexical_signal = min(candidate.lexical_score / 8.0, 1.0)

            corpus_bonus = 0.18 if candidate.corpus_type == CorpusType.OFFICIAL.value else -0.05
            role_bonus = self._role_bonus(mode=mode, intent=analysis.intent, role=candidate.pedagogical_role)
            confusion_penalty = logical_confusion_penalty(
                text=f"{candidate.title}\n{candidate.section_path}\n{candidate.chunk_text}",
                analysis=analysis,
            )
            comparative_bonus = 0.0
            lowered_path = title_section.lower()
            if analysis.intent == "comparative" and any(marker in lowered_path for marker in ("release", "what's new", "нов")):
                comparative_bonus = 0.07
            compatibility_bonus = 0.0
            compatibility_penalty = 0.0
            if analysis.intent == "compatibility":
                if any(marker in lowered_path for marker in ("restriction", "compatibility", "version", "publisher", "subscriber")):
                    compatibility_bonus = 0.20
                else:
                    compatibility_penalty = 0.08
            logical_anchor_bonus = 0.0
            if analysis.is_logical_replication and any(
                marker in lowered_path for marker in ("logical replication", "publication", "subscription")
            ):
                logical_anchor_bonus = 0.10
            configuration_bonus = 0.0
            if analysis.parameter_focus and any(
                marker in lowered_path for marker in ("configuration", "runtime-config-replication", "publishers", "subscribers")
            ):
                configuration_bonus = 0.16
            missing_anchor_penalty = 0.0
            if analysis.is_logical_replication and logical_anchor_overlap == 0.0 and term_overlap < 0.45:
                missing_anchor_penalty = 0.32

            score = (
                0.42 * semantic_similarity
                + 0.18 * lexical_overlap
                + 0.11 * title_section_overlap
                + 0.16 * term_overlap
                + 0.07 * lexical_signal
                + corpus_bonus
                + role_bonus
                + comparative_bonus
                + compatibility_bonus
                + logical_anchor_bonus
                + configuration_bonus
                - confusion_penalty
                - missing_anchor_penalty
                - compatibility_penalty
            )
            scored.append((candidate, score, semantic_similarity, lexical_overlap, title_section_overlap, term_overlap))

        official = sorted(
            [row for row in scored if row[0].corpus_type == CorpusType.OFFICIAL.value],
            key=lambda item: item[1],
            reverse=True,
        )
        supplementary = sorted(
            [row for row in scored if row[0].corpus_type == CorpusType.SUPPLEMENTARY.value],
            key=lambda item: item[1],
            reverse=True,
        )
        official = self._limit_per_document(official, max_per_document=2)
        supplementary = self._limit_per_document(supplementary, max_per_document=1)

        if mode == "answer":
            selected = official[:effective_top_k]
        elif not extended_mode:
            selected = official[:effective_top_k]
        else:
            # Preserve official as primary context; supplementary augments but never replaces.
            supplementary_quota = 0
            if supplementary:
                supplementary_quota = max(1, effective_top_k // 4)
            official_quota = max(1, effective_top_k - supplementary_quota)

            selected = official[:official_quota] + supplementary[:supplementary_quota]
            if len(selected) < effective_top_k:
                selected += official[official_quota:effective_top_k]
            if len(selected) < effective_top_k:
                selected += supplementary[supplementary_quota:effective_top_k]
            selected = selected[:effective_top_k]

        ranked: list[RankedChunk] = []
        for idx, (candidate, score, semantic_similarity, lexical_overlap, title_section_overlap, term_overlap) in enumerate(
            selected, start=1
        ):
            source_role = SourceRole.BASE.value if candidate.corpus_type == CorpusType.OFFICIAL.value else SourceRole.SUPPLEMENTARY.value
            ranked.append(
                RankedChunk(
                    chunk_id=candidate.chunk_id,
                    document_id=candidate.document_id,
                    title=candidate.title,
                    source_url=candidate.source_url,
                    corpus_type=candidate.corpus_type,
                    section_path=candidate.section_path,
                    chunk_text=candidate.chunk_text,
                    pedagogical_role=candidate.pedagogical_role,
                    distance=candidate.distance,
                    score=score,
                    rank_position=idx,
                    source_role=source_role,
                    semantic_similarity=semantic_similarity,
                    lexical_overlap=lexical_overlap,
                    title_section_overlap=title_section_overlap,
                    technical_term_overlap=term_overlap,
                )
            )

        return ranked
