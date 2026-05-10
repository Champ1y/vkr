from __future__ import annotations

from uuid import uuid4

from app.db.enums import CorpusType
from app.services.orchestration import AskOrchestrationService
from app.services.types import RetrievedChunk


def test_resolve_corpora_short_mode() -> None:
    assert AskOrchestrationService.resolve_corpora("short") == ["official"]


def test_resolve_corpora_detailed_mode() -> None:
    assert AskOrchestrationService.resolve_corpora("detailed") == ["official"]


def test_resolve_corpora_tutorial_mode() -> None:
    assert AskOrchestrationService.resolve_corpora("tutorial") == ["official", "supplementary"]


def _candidate(*, corpus_type: str, url: str) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        title="Doc",
        source_url=url,
        corpus_type=corpus_type,
        section_path="Section / Intro",
        chunk_text="text",
        pedagogical_role="step",
        distance=0.3,
        lexical_score=0.0,
    )


def test_tutorial_mode_adds_supplementary_candidates_when_missing() -> None:
    class FakeRetrieval:
        def __init__(self) -> None:
            self.calls: list[list[str]] = []

        def retrieve(self, **kwargs):  # type: ignore[no-untyped-def]
            self.calls.append(kwargs["corpora"])
            return [
                _candidate(
                    corpus_type=CorpusType.SUPPLEMENTARY.value,
                    url="supplementary://curated/16/tutorial.md",
                )
            ]

    service = AskOrchestrationService.__new__(AskOrchestrationService)
    service.retrieval = FakeRetrieval()

    base = [_candidate(corpus_type=CorpusType.OFFICIAL.value, url="https://www.postgresql.org/docs/16/logical-replication.html")]
    merged = service._ensure_tutorial_supplementary(
        answer_mode="tutorial",
        question_vector=[0.1, 0.2],
        pg_version="16",
        query_terms=["logical replication", "guide"],
        candidates=base,
    )

    assert service.retrieval.calls == [[CorpusType.SUPPLEMENTARY.value]]
    assert any(item.corpus_type == CorpusType.SUPPLEMENTARY.value for item in merged)
    assert any(item.corpus_type == CorpusType.OFFICIAL.value for item in merged)


def test_short_mode_does_not_fetch_supplementary() -> None:
    class FakeRetrieval:
        def retrieve(self, **kwargs):  # type: ignore[no-untyped-def]
            raise AssertionError("retrieve should not be called")

    service = AskOrchestrationService.__new__(AskOrchestrationService)
    service.retrieval = FakeRetrieval()

    base = [_candidate(corpus_type=CorpusType.OFFICIAL.value, url="https://www.postgresql.org/docs/16/sql-select.html")]
    merged = service._ensure_tutorial_supplementary(
        answer_mode="short",
        question_vector=[0.1],
        pg_version="16",
        query_terms=["select"],
        candidates=base,
    )

    assert merged == base
