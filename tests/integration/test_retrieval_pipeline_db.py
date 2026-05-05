from __future__ import annotations

import pytest

from app.core.config import settings
from app.db.enums import AudienceLevel, CorpusType, PedagogicalRole
from app.db.models import Chunk, Document, Embedding, Version
from app.repositories.retrieval import RetrievalRepository
from app.services.adapters.embeddings import HashingEmbeddingService

pytestmark = pytest.mark.integration


def test_retrieval_repository_filters_by_pg_version(db_session) -> None:
    vector_dim = int(Embedding.__table__.c.embedding.type.dim)  # type: ignore[union-attr]
    embedder = HashingEmbeddingService(dimension=vector_dim, seed=settings.hash_embedding_seed)

    version16 = Version(major_version="16", docs_base_url="https://www.postgresql.org/docs/16/", is_supported=True)
    version17 = Version(major_version="17", docs_base_url="https://www.postgresql.org/docs/17/", is_supported=True)
    db_session.add_all([version16, version17])
    db_session.flush()

    doc16 = Document(
        version_id=version16.id,
        title="Logical Replication",
        source_url="https://www.postgresql.org/docs/16/logical-replication.html",
        checksum="doc16",
        corpus_type=CorpusType.OFFICIAL.value,
        audience_level=AudienceLevel.GENERAL.value,
        raw_html=None,
        normalized_text="logical replication publication subscription",
    )
    doc17 = Document(
        version_id=version17.id,
        title="Logical Replication",
        source_url="https://www.postgresql.org/docs/17/logical-replication.html",
        checksum="doc17",
        corpus_type=CorpusType.OFFICIAL.value,
        audience_level=AudienceLevel.GENERAL.value,
        raw_html=None,
        normalized_text="logical replication in version 17",
    )
    db_session.add_all([doc16, doc17])
    db_session.flush()

    chunk16 = Chunk(
        document_id=doc16.id,
        chunk_index=0,
        section_path="Chapter 31 / Logical Replication",
        chunk_text="Logical replication uses publication and subscription.",
        token_count=8,
        content_type="paragraph",
        pedagogical_role=PedagogicalRole.OVERVIEW.value,
    )
    chunk17 = Chunk(
        document_id=doc17.id,
        chunk_index=0,
        section_path="Chapter 31 / Logical Replication",
        chunk_text="Logical replication improvements in PostgreSQL 17.",
        token_count=7,
        content_type="paragraph",
        pedagogical_role=PedagogicalRole.OVERVIEW.value,
    )
    db_session.add_all([chunk16, chunk17])
    db_session.flush()

    db_session.add_all(
        [
            Embedding(
                chunk_id=chunk16.id,
                embedding_model=embedder.model_name,
                embedding_dimension=vector_dim,
                embedding=embedder.embed_text(chunk16.chunk_text),
            ),
            Embedding(
                chunk_id=chunk17.id,
                embedding_model=embedder.model_name,
                embedding_dimension=vector_dim,
                embedding=embedder.embed_text(chunk17.chunk_text),
            ),
        ]
    )
    db_session.commit()

    query_vector = embedder.embed_text("publication subscription logical replication")
    rows = RetrievalRepository(db_session).retrieve(
        query_vector=query_vector,
        pg_version="16",
        corpora=[CorpusType.OFFICIAL.value],
        top_k=5,
    )

    returned_ids = {item.chunk_id for item in rows}
    assert chunk16.id in returned_ids
    assert chunk17.id not in returned_ids
    assert all(item.corpus_type == CorpusType.OFFICIAL.value for item in rows)
