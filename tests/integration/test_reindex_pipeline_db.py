from __future__ import annotations

import pytest
from sqlalchemy import func, select

from app.core.config import settings
from app.db.enums import CorpusType
from app.db.models import Chunk, Document, Embedding, Version
from app.services.adapters.embeddings import HashingEmbeddingService
from app.services.ingestion.indexer import IndexingPipeline
from app.services.ingestion.official_loader import RawWebDocument
from app.services.ingestion.supplementary_loader import RawSupplementaryDocument

pytestmark = pytest.mark.integration


def _count_documents(db_session, version_id, corpus_type: str) -> int:
    count = db_session.scalar(
        select(func.count(Document.id)).where(
            Document.version_id == version_id,
            Document.corpus_type == corpus_type,
        )
    )
    return int(count or 0)


def _count_chunks(db_session, version_id) -> int:  # type: ignore[no-untyped-def]
    count = db_session.scalar(
        select(func.count(Chunk.id))
        .join(Document, Document.id == Chunk.document_id)
        .where(Document.version_id == version_id)
    )
    return int(count or 0)


def _count_embeddings(db_session, version_id) -> int:  # type: ignore[no-untyped-def]
    count = db_session.scalar(
        select(func.count(Embedding.id))
        .join(Chunk, Chunk.id == Embedding.chunk_id)
        .join(Document, Document.id == Chunk.document_id)
        .where(Document.version_id == version_id)
    )
    return int(count or 0)


def test_small_reindex_is_restart_safe_and_indexes_supplementary(monkeypatch, db_session) -> None:
    vector_dim = int(Embedding.__table__.c.embedding.type.dim)  # type: ignore[union-attr]
    embedder = HashingEmbeddingService(dimension=vector_dim, seed=settings.hash_embedding_seed)

    monkeypatch.setattr(
        "app.services.ingestion.indexer.EmbeddingServiceFactory.create",
        lambda: embedder,
    )

    pipeline = IndexingPipeline(
        db_session,
        embedding_batch_size=2,
        commit_every_docs=1,
        progress_every=1,
    )
    monkeypatch.setattr(pipeline, "_persist_artifacts", lambda **_: None)

    official_docs = [
        RawWebDocument(
            source_url="https://www.postgresql.org/docs/16/a.html",
            html="<html><body><h1>Doc A</h1><p>" + ("official alpha " * 20) + "</p></body></html>",
        ),
        RawWebDocument(
            source_url="https://www.postgresql.org/docs/16/b.html",
            html="<html><body><h1>Doc B</h1><p>" + ("official beta " * 20) + "</p></body></html>",
        ),
    ]
    supplementary_docs = [
        RawSupplementaryDocument(
            source_url="supplementary://curated/16/guide.md",
            title="Guide",
            text="\n\n".join(["supplementary guidance " * 15, "follow-up step " * 15]),
            raw_content="# guide",
        )
    ]

    monkeypatch.setattr(pipeline.official_loader, "load_documents", lambda version, max_pages=None: official_docs)
    monkeypatch.setattr(pipeline.supp_loader, "load_documents", lambda version: supplementary_docs)

    stats_first = pipeline.reindex_version(version="16", include_official=True, include_supplementary=True)

    version_id = db_session.scalar(select(Version.id).where(Version.major_version == "16"))
    assert version_id is not None

    official_docs_count = _count_documents(db_session, version_id, CorpusType.OFFICIAL.value)
    supplementary_docs_count = _count_documents(db_session, version_id, CorpusType.SUPPLEMENTARY.value)
    chunks_count = _count_chunks(db_session, version_id)
    embeddings_count = _count_embeddings(db_session, version_id)

    assert stats_first.official_documents == 2
    assert stats_first.supplementary_documents == 1
    assert official_docs_count == 2
    assert supplementary_docs_count == 1
    assert chunks_count > 0
    assert embeddings_count > 0
    assert chunks_count == embeddings_count

    stats_second = pipeline.reindex_version(version="16", include_official=True, include_supplementary=True)

    official_docs_count_2 = _count_documents(db_session, version_id, CorpusType.OFFICIAL.value)
    supplementary_docs_count_2 = _count_documents(db_session, version_id, CorpusType.SUPPLEMENTARY.value)
    chunks_count_2 = _count_chunks(db_session, version_id)
    embeddings_count_2 = _count_embeddings(db_session, version_id)

    assert stats_second.official_documents == 2
    assert stats_second.supplementary_documents == 1
    assert official_docs_count_2 == 2
    assert supplementary_docs_count_2 == 1
    assert chunks_count_2 == embeddings_count_2
    assert chunks_count_2 == chunks_count
