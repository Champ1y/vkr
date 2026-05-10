from __future__ import annotations

from app.db.enums import AudienceLevel, CorpusType, QueryStatus
from app.db.models import Chunk, Document, Version
from app.repositories.queries import QueryRepository
from app.schemas.ask import TutorialPayload
from app.services.types import RankedChunk

import pytest

pytestmark = pytest.mark.integration


def test_query_history_persists_sources_and_payload(db_session) -> None:
    version = Version(major_version="16", docs_base_url="https://www.postgresql.org/docs/16/", is_supported=True)
    db_session.add(version)
    db_session.flush()

    doc = Document(
        version_id=version.id,
        title="Logical Replication",
        source_url="https://www.postgresql.org/docs/16/logical-replication.html",
        checksum="doc-history-16",
        corpus_type=CorpusType.OFFICIAL.value,
        audience_level=AudienceLevel.GENERAL.value,
        raw_html=None,
        normalized_text="logical replication publication subscription",
    )
    db_session.add(doc)
    db_session.flush()

    chunk = Chunk(
        document_id=doc.id,
        chunk_index=0,
        section_path="Chapter 31 / Logical Replication",
        chunk_text="Logical replication is based on publication/subscription.",
        token_count=7,
        content_type="paragraph",
        pedagogical_role="overview",
    )
    db_session.add(chunk)
    db_session.flush()

    ranked = RankedChunk(
        chunk_id=chunk.id,
        document_id=doc.id,
        title=doc.title,
        source_url=doc.source_url,
        corpus_type=CorpusType.OFFICIAL.value,
        section_path=chunk.section_path,
        chunk_text=chunk.chunk_text,
        pedagogical_role=chunk.pedagogical_role,
        distance=0.14,
        score=0.88,
        rank_position=1,
        source_role="base",
    )

    repo = QueryRepository(db_session)
    tutorial_payload = TutorialPayload(
        short_explanation="Краткое объяснение",
        prerequisites=["PostgreSQL 16"],
        steps=["Создайте publication", "Создайте subscription"],
        notes=["Проверьте wal_level=logical"],
    )
    repo.create_query(
        version=version,
        question="Как настроить logical replication?",
        mode="tutorial",
        answer_text=None,
        tutorial_payload=tutorial_payload,
        status=QueryStatus.SUCCESS.value,
        latency_ms=123,
        sources=[ranked],
    )

    history = repo.list_history(limit=10)
    assert history

    row = history[0]
    assert row.user_question == "Как настроить logical replication?"
    assert row.mode == "tutorial"
    assert row.status == QueryStatus.SUCCESS.value
    assert row.answer_text is None
    assert row.tutorial_json is not None
    assert row.tutorial_json["steps"]

    assert len(row.sources) == 1
    src = row.sources[0]
    assert src.rank_position == 1
    assert src.source_url == "https://www.postgresql.org/docs/16/logical-replication.html"
    assert src.corpus_type == CorpusType.OFFICIAL.value
