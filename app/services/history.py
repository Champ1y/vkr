from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.queries import QueryRepository
from app.schemas.history import QueryHistoryOut, QueryHistoryResponse, QuerySourceHistoryOut


class HistoryService:
    def __init__(self, db: Session) -> None:
        self.repo = QueryRepository(db)

    def get_history(self, *, limit: int = 50) -> QueryHistoryResponse:
        rows = self.repo.list_history(limit=limit)
        items: list[QueryHistoryOut] = []

        for row in rows:
            items.append(
                QueryHistoryOut(
                    id=row.id,
                    user_question=row.user_question,
                    pg_version=row.version.major_version if row.version else None,
                    mode=row.mode,
                    extended_mode=row.extended_mode,
                    answer_text=row.answer_text,
                    tutorial_json=row.tutorial_json,
                    status=row.status,
                    latency_ms=row.latency_ms,
                    created_at=row.created_at,
                    sources=[
                        QuerySourceHistoryOut(
                            rank_position=source.rank_position,
                            similarity_score=source.similarity_score,
                            source_role=source.source_role,
                            corpus_type=source.corpus_type,
                            source_title=source.source_title,
                            source_url=source.source_url,
                            section_path=source.section_path,
                        )
                        for source in sorted(row.sources, key=lambda item: item.rank_position)
                    ],
                )
            )

        return QueryHistoryResponse(items=items)
