from __future__ import annotations

from fastapi import status
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError
from app.core.logging import get_logger
from app.schemas.admin import ReindexRequest
from app.services.ingestion.indexer import IndexingPipeline, ReindexStats

logger = get_logger(__name__)


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def reindex(self, payload: ReindexRequest) -> list[ReindexStats]:
        pipeline = IndexingPipeline(self.db)
        stats: list[ReindexStats] = []
        try:
            for version in payload.versions:
                stats.append(
                    pipeline.reindex_version(
                        version=version,
                        include_official=payload.include_official,
                        include_supplementary=payload.include_supplementary,
                        max_pages=payload.max_pages,
                    )
                )
        except RuntimeError as exc:
            self.db.rollback()
            raise DomainError(str(exc), status.HTTP_503_SERVICE_UNAVAILABLE) from exc
        return stats
