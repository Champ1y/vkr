from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class VersionOut(BaseModel):
    id: UUID
    major_version: str
    docs_base_url: str
    is_supported: bool
    loaded_at: datetime


class VersionsResponse(BaseModel):
    versions: list[VersionOut]
