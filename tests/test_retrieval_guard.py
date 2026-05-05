from __future__ import annotations

from uuid import uuid4

from app.services.retrieval import RetrievalService
from app.services.types import RetrievedChunk


def candidate(*, url: str, corpus_type: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        title="Title",
        source_url=url,
        corpus_type=corpus_type,
        section_path="sec",
        chunk_text="text",
        pedagogical_role="overview",
        distance=0.2,
    )


def test_version_guard_filters_wrong_official_version() -> None:
    rows = [
        candidate(url="https://www.postgresql.org/docs/16/sql-select.html", corpus_type="official"),
        candidate(url="https://www.postgresql.org/docs/17/sql-select.html", corpus_type="official"),
        candidate(url="supplementary://16/guide.md", corpus_type="supplementary"),
    ]

    filtered = RetrievalService._enforce_version_guard(rows=rows, pg_version="16")

    assert len(filtered) == 2
    assert filtered[0].source_url.endswith("/docs/16/sql-select.html")
    assert filtered[1].corpus_type == "supplementary"


def test_version_guard_filters_current_alias_for_version_18() -> None:
    rows = [
        candidate(url="https://www.postgresql.org/docs/current/sql-select.html", corpus_type="official"),
        candidate(url="https://www.postgresql.org/docs/18/sql-select.html", corpus_type="official"),
    ]

    filtered = RetrievalService._enforce_version_guard(rows=rows, pg_version="18")

    assert len(filtered) == 1
    assert filtered[0].source_url.endswith("/docs/18/sql-select.html")
