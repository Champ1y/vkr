from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.db.enums import QueryStatus
from app.db.models import QueryHistory, QuerySource, Version
from app.schemas.ask import TutorialPayload
from app.services.types import RankedChunk


class QueryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_query(
        self,
        *,
        version: Version | None,
        question: str,
        mode: str,
        answer_text: str | None,
        tutorial_payload: TutorialPayload | None,
        status: str,
        latency_ms: int,
        sources: list[RankedChunk],
    ) -> QueryHistory:
        row = QueryHistory(
            selected_version_id=version.id if version else None,
            user_question=question,
            mode=mode,
            answer_text=answer_text,
            tutorial_json=tutorial_payload.model_dump() if tutorial_payload else None,
            status=status,
            latency_ms=latency_ms,
        )
        self.db.add(row)
        self.db.flush()

        for source in sources:
            row_source = QuerySource(
                query_id=row.id,
                chunk_id=source.chunk_id,
                rank_position=source.rank_position,
                similarity_score=round(source.score, 5),
                used_in_result=True,
                source_role=source.source_role,
                source_title=source.title,
                source_url=source.source_url,
                section_path=source.section_path,
                corpus_type=source.corpus_type,
            )
            self.db.add(row_source)

        self.db.commit()
        self.db.refresh(row)
        return row

    def create_failed_query(
        self,
        *,
        version: Version | None,
        question: str,
        mode: str,
        latency_ms: int,
    ) -> QueryHistory:
        row = QueryHistory(
            selected_version_id=version.id if version else None,
            user_question=question,
            mode=mode,
            answer_text=None,
            tutorial_json=None,
            status=QueryStatus.FAILED.value,
            latency_ms=latency_ms,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_history(self, *, limit: int = 50) -> list[QueryHistory]:
        stmt = (
            select(QueryHistory)
            .options(joinedload(QueryHistory.version), selectinload(QueryHistory.sources))
            .order_by(QueryHistory.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
