from __future__ import annotations

from uuid import uuid4

from app.services.reranking import RerankingService
from app.services.types import RetrievedChunk


def make_candidate(
    *,
    corpus_type: str,
    url: str,
    distance: float,
    text: str,
    title: str = "Doc",
    section_path: str = "Section / Subsection",
    pedagogical_role: str = "overview",
    lexical_score: float = 0.0,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=uuid4(),
        document_id=uuid4(),
        title=title,
        source_url=url,
        corpus_type=corpus_type,
        section_path=section_path,
        chunk_text=text,
        pedagogical_role=pedagogical_role,
        distance=distance,
        lexical_score=lexical_score,
    )


def test_answer_mode_drops_supplementary() -> None:
    reranker = RerankingService()
    candidates = [
        make_candidate(corpus_type="official", url="https://www.postgresql.org/docs/16/sql-select.html", distance=0.2, text="official text"),
        make_candidate(corpus_type="supplementary", url="supplementary://16/guide.md", distance=0.1, text="supp text"),
    ]

    ranked = reranker.rerank(question="select", candidates=candidates, mode="answer", extended_mode=False, top_k=5)

    assert ranked
    assert all(item.corpus_type == "official" for item in ranked)


def test_tutorial_extended_can_include_supplementary_after_official() -> None:
    reranker = RerankingService()
    candidates = [
        make_candidate(corpus_type="official", url="https://www.postgresql.org/docs/16/logical-replication.html", distance=0.3, text="official logical replication"),
        make_candidate(corpus_type="supplementary", url="supplementary://16/guide.md", distance=0.1, text="step by step supplementary"),
    ]

    ranked = reranker.rerank(question="logical replication", candidates=candidates, mode="tutorial", extended_mode=True, top_k=5)

    assert len(ranked) == 2
    assert ranked[0].corpus_type == "official"
    assert ranked[1].corpus_type == "supplementary"


def test_tutorial_extended_reserves_slot_for_supplementary() -> None:
    reranker = RerankingService()
    candidates = [
        make_candidate(
            corpus_type="official",
            url=f"https://www.postgresql.org/docs/16/doc-{idx}.html",
            distance=0.2 + idx * 0.01,
            text=f"official text {idx}",
        )
        for idx in range(6)
    ]
    candidates.append(
        make_candidate(
            corpus_type="supplementary",
            url="supplementary://16/guide.md",
            distance=0.1,
            text="supplementary tutorial guide",
        )
    )

    ranked = reranker.rerank(question="guide", candidates=candidates, mode="tutorial", extended_mode=True, top_k=4)

    assert len(ranked) == 4
    assert ranked[0].corpus_type == "official"
    assert any(item.corpus_type == "supplementary" for item in ranked)


def test_tutorial_without_extended_excludes_supplementary() -> None:
    reranker = RerankingService()
    candidates = [
        make_candidate(
            corpus_type="official",
            url="https://www.postgresql.org/docs/16/logical-replication.html",
            distance=0.25,
            text="Logical replication uses publication and subscription.",
        ),
        make_candidate(
            corpus_type="supplementary",
            url="supplementary://16/guide.md",
            distance=0.01,
            text="Some supplementary guide",
        ),
    ]

    ranked = reranker.rerank(
        question="Объясни logical replication",
        candidates=candidates,
        mode="tutorial",
        extended_mode=False,
        top_k=5,
    )

    assert ranked
    assert all(item.corpus_type == "official" for item in ranked)


def test_logical_replication_query_penalizes_unrelated_mechanisms() -> None:
    reranker = RerankingService()
    candidates = [
        make_candidate(
            corpus_type="official",
            url="https://www.postgresql.org/docs/16/sql-listen.html",
            distance=0.15,
            text="LISTEN and NOTIFY provide asynchronous notifications between sessions.",
            title="LISTEN",
            section_path="Command Reference / LISTEN",
            lexical_score=0.2,
        ),
        make_candidate(
            corpus_type="official",
            url="https://www.postgresql.org/docs/16/logical-replication.html",
            distance=0.27,
            text="Logical replication uses publication/subscription and replication slots.",
            title="Logical Replication",
            section_path="Chapter 31 / Logical Replication",
            lexical_score=1.4,
        ),
    ]

    ranked = reranker.rerank(
        question="Можно ли logical replication from standby servers в PostgreSQL 16?",
        candidates=candidates,
        mode="answer",
        extended_mode=False,
        top_k=2,
    )

    assert ranked[0].source_url.endswith("/logical-replication.html")


def test_logical_replication_parameters_prefers_config_over_basebackup() -> None:
    reranker = RerankingService()
    candidates = [
        make_candidate(
            corpus_type="official",
            url="https://www.postgresql.org/docs/16/runtime-config-replication.html",
            distance=0.33,
            text="wal_level must be set to logical. max_replication_slots and max_wal_senders control senders/slots.",
            title="Replication Settings",
            section_path="Server Configuration / Replication",
            lexical_score=2.0,
        ),
        make_candidate(
            corpus_type="official",
            url="https://www.postgresql.org/docs/16/app-pgbasebackup.html",
            distance=0.18,
            text="pg_basebackup options for physical backup and replication.",
            title="pg_basebackup",
            section_path="Options",
            lexical_score=0.4,
        ),
    ]

    ranked = reranker.rerank(
        question="Какие параметры проверить для logical replication в PostgreSQL 16?",
        candidates=candidates,
        mode="answer",
        extended_mode=False,
        top_k=2,
    )

    assert ranked[0].source_url.endswith("/runtime-config-replication.html")


def test_tutorial_procedural_prefers_publication_subscription_steps() -> None:
    reranker = RerankingService()
    candidates = [
        make_candidate(
            corpus_type="official",
            url="https://www.postgresql.org/docs/16/sql-alterpublication.html",
            distance=0.34,
            text="ALTER PUBLICATION pub ADD TABLE my_table;",
            title="ALTER PUBLICATION",
            section_path="SQL Command Reference / ALTER PUBLICATION",
            pedagogical_role="step",
            lexical_score=2.3,
        ),
        make_candidate(
            corpus_type="official",
            url="https://www.postgresql.org/docs/16/sql-altersubscription.html",
            distance=0.36,
            text="ALTER SUBSCRIPTION sub REFRESH PUBLICATION;",
            title="ALTER SUBSCRIPTION",
            section_path="SQL Command Reference / ALTER SUBSCRIPTION",
            pedagogical_role="step",
            lexical_score=2.1,
        ),
        make_candidate(
            corpus_type="official",
            url="https://www.postgresql.org/docs/16/app-pgdump.html",
            distance=0.16,
            text="pg_dump and pg_restore usage.",
            title="pg_dump",
            section_path="Notes",
            pedagogical_role="overview",
            lexical_score=0.1,
        ),
    ]

    ranked = reranker.rerank(
        question="Объясни для новичка, как добавить новую таблицу в существующую logical replication.",
        candidates=candidates,
        mode="tutorial",
        extended_mode=False,
        top_k=3,
    )

    urls = [item.source_url for item in ranked]
    assert urls[0].endswith(("/sql-alterpublication.html", "/sql-altersubscription.html"))
    assert urls[1].endswith(("/sql-alterpublication.html", "/sql-altersubscription.html"))
    assert urls[2].endswith("/app-pgdump.html")
