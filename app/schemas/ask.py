from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import settings
from app.schemas.common import SourceOut


class AskRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    question: str = Field(min_length=3, max_length=4000)
    pg_version: str = Field(min_length=1, max_length=10)
    answer_mode: Literal["short", "detailed", "tutorial"]

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 3:
            raise ValueError("question must contain at least 3 characters")
        return cleaned

    @field_validator("pg_version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized.isdigit():
            raise ValueError("pg_version must be a major numeric version, e.g. '16'")
        if normalized not in settings.supported_versions:
            supported = ", ".join(settings.supported_versions)
            raise ValueError(f"pg_version must be one of supported versions: {supported}")
        return normalized


class TutorialPayload(BaseModel):
    short_explanation: str
    prerequisites: list[str]
    steps: list[str]
    notes: list[str]


class AnswerResponse(BaseModel):
    answer_mode: Literal["short", "detailed"]
    pg_version: str
    answer: str
    sources: list[SourceOut]


class TutorialResponse(BaseModel):
    answer_mode: Literal["tutorial"]
    pg_version: str
    tutorial: TutorialPayload
    sources: list[SourceOut]


class AskResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"description": "Union response for short/detailed/tutorial modes"})

    answer_mode: Literal["short", "detailed", "tutorial"]
    pg_version: str
    answer: str | None = None
    tutorial: TutorialPayload | None = None
    sources: list[SourceOut] = []
