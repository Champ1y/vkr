from __future__ import annotations

from sqlalchemy import Select, case, func, literal, or_, select
from sqlalchemy.orm import Session

from app.db.models import Chunk, Document, Embedding, Version
from app.services.types import RetrievedChunk


class RetrievalRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def retrieve(
        self,
        *,
        query_vector: list[float],
        pg_version: str,
        corpora: list[str],
        top_k: int,
        query_terms: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        vector_limit = max(top_k * 3, top_k)
        keyword_limit = max(top_k * 2, top_k)

        vector_rows = self._fetch_vector_candidates(
            query_vector=query_vector,
            pg_version=pg_version,
            corpora=corpora,
            limit=vector_limit,
        )
        keyword_rows: list[RetrievedChunk] = []
        if query_terms:
            keyword_rows = self._fetch_keyword_candidates(
                query_vector=query_vector,
                pg_version=pg_version,
                corpora=corpora,
                query_terms=query_terms,
                limit=keyword_limit,
            )

        merged = self._merge_candidates(vector_rows + keyword_rows)
        merged.sort(key=self._pre_rank, reverse=True)
        return merged[:vector_limit]

    def _fetch_vector_candidates(
        self,
        *,
        query_vector: list[float],
        pg_version: str,
        corpora: list[str],
        limit: int,
    ) -> list[RetrievedChunk]:
        distance_expr = Embedding.embedding.cosine_distance(query_vector).label("distance")
        lexical_score_expr = literal(0.0).label("lexical_score")

        stmt: Select = (
            select(
                Chunk.id,
                Chunk.document_id,
                Document.title,
                Document.source_url,
                Document.corpus_type,
                Chunk.section_path,
                Chunk.chunk_text,
                Chunk.pedagogical_role,
                distance_expr,
                lexical_score_expr,
            )
            .join(Document, Chunk.document_id == Document.id)
            .join(Version, Document.version_id == Version.id)
            .join(Embedding, Embedding.chunk_id == Chunk.id)
            .where(Version.major_version == pg_version)
            .where(Document.corpus_type.in_(corpora))
            .order_by(distance_expr.asc())
            .limit(limit)
        )

        rows = self.db.execute(stmt).all()
        return [self._to_candidate(row) for row in rows]

    def _fetch_keyword_candidates(
        self,
        *,
        query_vector: list[float],
        pg_version: str,
        corpora: list[str],
        query_terms: list[str],
        limit: int,
    ) -> list[RetrievedChunk]:
        distance_expr = Embedding.embedding.cosine_distance(query_vector).label("distance")
        predicates = []
        lexical_score = literal(0.0)

        for term in query_terms[:16]:
            normalized = term.strip().lower()
            if len(normalized) < 3:
                continue
            pattern = f"%{normalized}%"

            title_match = func.lower(Document.title).like(pattern)
            section_match = func.lower(Chunk.section_path).like(pattern)
            text_match = func.lower(Chunk.chunk_text).like(pattern)

            predicates.extend([title_match, section_match, text_match])
            lexical_score = (
                lexical_score
                + case((title_match, 1.8), else_=0.0)
                + case((section_match, 1.4), else_=0.0)
                + case((text_match, 1.0), else_=0.0)
            )

        if not predicates:
            return []

        lexical_score_expr = lexical_score.label("lexical_score")
        stmt: Select = (
            select(
                Chunk.id,
                Chunk.document_id,
                Document.title,
                Document.source_url,
                Document.corpus_type,
                Chunk.section_path,
                Chunk.chunk_text,
                Chunk.pedagogical_role,
                distance_expr,
                lexical_score_expr,
            )
            .join(Document, Chunk.document_id == Document.id)
            .join(Version, Document.version_id == Version.id)
            .join(Embedding, Embedding.chunk_id == Chunk.id)
            .where(Version.major_version == pg_version)
            .where(Document.corpus_type.in_(corpora))
            .where(or_(*predicates))
            .order_by(lexical_score_expr.desc(), distance_expr.asc())
            .limit(limit)
        )

        rows = self.db.execute(stmt).all()
        return [self._to_candidate(row) for row in rows]

    @staticmethod
    def _to_candidate(row) -> RetrievedChunk:  # type: ignore[no-untyped-def]
        return RetrievedChunk(
            chunk_id=row[0],
            document_id=row[1],
            title=row[2],
            source_url=row[3],
            corpus_type=row[4],
            section_path=row[5],
            chunk_text=row[6],
            pedagogical_role=row[7],
            distance=float(row[8]),
            lexical_score=float(row[9] or 0.0),
        )

    def _merge_candidates(self, rows: list[RetrievedChunk]) -> list[RetrievedChunk]:
        by_chunk: dict[str, RetrievedChunk] = {}

        for item in rows:
            key = str(item.chunk_id)
            existing = by_chunk.get(key)
            if existing is None or self._pre_rank(item) > self._pre_rank(existing):
                by_chunk[key] = item

        return list(by_chunk.values())

    @staticmethod
    def _pre_rank(item: RetrievedChunk) -> float:
        semantic_similarity = max(0.0, 1.0 - (item.distance / 2.0))
        lexical_signal = min(item.lexical_score / 8.0, 1.0)
        return 0.74 * semantic_similarity + 0.26 * lexical_signal
