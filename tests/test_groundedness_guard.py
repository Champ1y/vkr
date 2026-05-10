from __future__ import annotations

from uuid import uuid4

from app.services.orchestration import AskOrchestrationService
from app.services.query_processing import analyze_query
from app.services.types import RankedChunk


def ranked_chunk(
    *,
    title: str,
    section: str,
    text: str,
    score: float,
    semantic_similarity: float,
    lexical_overlap: float,
    title_overlap: float,
    term_overlap: float,
    corpus_type: str = "official",
) -> RankedChunk:
    return RankedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        title=title,
        source_url="https://www.postgresql.org/docs/16/logical-replication.html",
        corpus_type=corpus_type,
        section_path=section,
        chunk_text=text,
        pedagogical_role="overview",
        distance=0.4,
        score=score,
        rank_position=1,
        source_role="base" if corpus_type == "official" else "supplementary",
        semantic_similarity=semantic_similarity,
        lexical_overlap=lexical_overlap,
        title_section_overlap=title_overlap,
        technical_term_overlap=term_overlap,
    )


def test_evidence_guard_rejects_weak_logical_replication_context() -> None:
    analysis = analyze_query("Можно ли logical replication from standby servers в PostgreSQL 16?")
    ranked = [
        ranked_chunk(
            title="LISTEN",
            section="Command Reference / LISTEN",
            text="LISTEN/NOTIFY asynchronous notifications",
            score=0.29,
            semantic_similarity=0.33,
            lexical_overlap=0.03,
            title_overlap=0.02,
            term_overlap=0.0,
        )
    ]

    ok = AskOrchestrationService._has_sufficient_evidence(ranked=ranked, analysis=analysis, answer_mode="short")
    assert ok is False


def test_evidence_guard_accepts_strong_official_context() -> None:
    analysis = analyze_query("Что такое publication и subscription в logical replication?")
    ranked = [
        ranked_chunk(
            title="Logical Replication",
            section="Chapter 31 / Logical Replication",
            text="Logical replication is based on a publication and a subscription.",
            score=0.76,
            semantic_similarity=0.81,
            lexical_overlap=0.31,
            title_overlap=0.34,
            term_overlap=0.62,
        )
    ]

    ok = AskOrchestrationService._has_sufficient_evidence(ranked=ranked, analysis=analysis, answer_mode="short")
    assert ok is True
