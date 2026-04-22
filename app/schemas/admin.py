from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from app.core.config import settings


class ReindexRequest(BaseModel):
    versions: list[str] = Field(min_length=1)
    include_official: bool = True
    include_supplementary: bool = True
    max_pages: int | None = None

    @field_validator("versions")
    @classmethod
    def normalize_versions(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        for value in values:
            val = value.strip()
            if not val.isdigit():
                raise ValueError(f"invalid version: {value}")
            if val not in settings.supported_versions:
                supported = ", ".join(settings.supported_versions)
                raise ValueError(f"unsupported version: {val}. Supported versions: {supported}")
            normalized.append(val)
        return sorted(set(normalized))


class ReindexResponse(BaseModel):
    started: bool
    versions: list[str]
    message: str
