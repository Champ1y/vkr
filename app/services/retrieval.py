from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.enums import CorpusType
from app.repositories.retrieval import RetrievalRepository
from app.services.types import RetrievedChunk


class RetrievalService:
    def __init__(self, db: Session) -> None:
        self.repository = RetrievalRepository(db)

    def retrieve(
        self,
        *,
        query_vector: list[float],
        pg_version: str,
        corpora: list[str],
        query_terms: list[str] | None = None,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        rows = self.repository.retrieve(
            query_vector=query_vector,
            pg_version=pg_version,
            corpora=corpora,
            top_k=top_k or settings.retrieval_top_k,
            query_terms=query_terms,
        )
        return self._enforce_version_guard(rows=rows, pg_version=pg_version)

    @staticmethod
    def _enforce_version_guard(*, rows: list[RetrievedChunk], pg_version: str) -> list[RetrievedChunk]:
        expected_token = f"/docs/{pg_version}/"
        filtered: list[RetrievedChunk] = []

        for item in rows:
            if item.corpus_type == CorpusType.OFFICIAL.value and expected_token not in item.source_url:
                continue
            filtered.append(item)
        return filtered
