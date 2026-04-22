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


class OllamaHealthOut(BaseModel):
    status: str
    base_url: str
    reachable: bool
    models: list[str] = Field(default_factory=list)
    missing_models: list[str] = Field(default_factory=list)
    message: str
