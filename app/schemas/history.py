from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class QuerySourceHistoryOut(BaseModel):
    rank_position: int
    similarity_score: Decimal
    source_role: str
    corpus_type: str
    source_title: str
    source_url: str | None
    section_path: str


class QueryHistoryOut(BaseModel):
    id: UUID
    user_question: str
    pg_version: str | None
    mode: str
    answer_text: str | None
    tutorial_json: dict | None
    status: str
    latency_ms: int
    created_at: datetime
    sources: list[QuerySourceHistoryOut]


class QueryHistoryResponse(BaseModel):
    items: list[QueryHistoryOut]
