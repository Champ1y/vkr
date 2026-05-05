from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.config import settings
from app.schemas.common import SourceOut


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    pg_version: str = Field(min_length=1, max_length=10)
    mode: Literal["answer", "tutorial"]
    extended_mode: bool = False
    clarification_answer: str | None = None

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

    @model_validator(mode="after")
    def validate_mode_extended(self) -> "AskRequest":
        if self.mode == "answer" and self.extended_mode:
            raise ValueError("extended_mode is allowed only for tutorial mode")
        return self


class TutorialPayload(BaseModel):
    short_explanation: str
    prerequisites: list[str]
    steps: list[str]
    notes: list[str]


class ClarificationPayload(BaseModel):
    question: str
    hint: str = ""


class AnswerResponse(BaseModel):
    mode: Literal["answer"]
    pg_version: str
    answer: str
    sources: list[SourceOut]


class TutorialResponse(BaseModel):
    mode: Literal["tutorial"]
    pg_version: str
    extended_mode: bool
    tutorial: TutorialPayload
    sources: list[SourceOut]


class AskResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"description": "Union response for answer/tutorial modes"})

    mode: Literal["answer", "tutorial"]
    pg_version: str
    answer: str | None = None
    extended_mode: bool | None = None
    tutorial: TutorialPayload | None = None
    clarification: ClarificationPayload | None = None
    sources: list[SourceOut] = []
