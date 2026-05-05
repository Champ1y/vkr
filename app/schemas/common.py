from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class SourceOut(BaseModel):
    title: str
    url: str | None
    corpus_type: str
    source_role: str
    section_path: str
    rank_position: int
    similarity_score: Decimal


class ErrorOut(BaseModel):
    detail: str


class HealthOut(BaseModel):
    status: str = Field(default="ok")
    timestamp: datetime


class EmbeddingsHealthOut(BaseModel):
    status: str
    provider: str
    model: str
    configured_dimension: int
    max_seq_length: int
    batch_size: int
    app_env: str
    message: str
