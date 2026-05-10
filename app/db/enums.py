from __future__ import annotations

from enum import StrEnum


class CorpusType(StrEnum):
    OFFICIAL = "official"
    SUPPLEMENTARY = "supplementary"


class AudienceLevel(StrEnum):
    GENERAL = "general"
    NOVICE = "novice"


class ModeType(StrEnum):
    SHORT = "short"
    DETAILED = "detailed"
    TUTORIAL = "tutorial"


class SourceRole(StrEnum):
    BASE = "base"
    SUPPLEMENTARY = "supplementary"


class PedagogicalRole(StrEnum):
    OVERVIEW = "overview"
    PREREQUISITE = "prerequisite"
    STEP = "step"
    EXAMPLE = "example"
    WARNING = "warning"


class QueryStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
