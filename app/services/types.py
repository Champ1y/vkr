from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from app.schemas.ask import TutorialPayload


@dataclass(slots=True)
class RetrievedChunk:
    chunk_id: UUID
    document_id: UUID
    title: str
    source_url: str
    corpus_type: str
    section_path: str
    chunk_text: str
    pedagogical_role: str
    distance: float
    lexical_score: float = 0.0


@dataclass(slots=True)
class RankedChunk:
    chunk_id: UUID
    document_id: UUID
    title: str
    source_url: str
    corpus_type: str
    section_path: str
    chunk_text: str
    pedagogical_role: str
    distance: float
    score: float
    rank_position: int
    source_role: str
    semantic_similarity: float = 0.0
    lexical_overlap: float = 0.0
    title_section_overlap: float = 0.0
    technical_term_overlap: float = 0.0


@dataclass(slots=True)
class AskResult:
    mode: Literal["answer", "tutorial"]
    pg_version: str
    answer: str | None
    tutorial: TutorialPayload | None
    extended_mode: bool
    ranked_sources: list[RankedChunk]


@dataclass(slots=True)
class PersistedQueryResult:
    query_id: UUID
    latency_ms: int
    mode: str
    status: str
    answer_text: str | None
    tutorial_json: dict | None
