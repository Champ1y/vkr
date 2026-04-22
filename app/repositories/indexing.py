from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db.enums import AudienceLevel
from app.db.models import Chunk, Document, Embedding, Version


@dataclass(slots=True)
class ChunkPayload:
    chunk_index: int
    section_path: str
    chunk_text: str
    token_count: int
    content_type: str
    pedagogical_role: str
    embedding: list[float]


@dataclass(slots=True)
class DocumentPayload:
    title: str
    source_url: str
    checksum: str
    corpus_type: str
    audience_level: str
    raw_html: str | None
    normalized_text: str
    chunks: list[ChunkPayload]


class IndexingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_or_create_version(self, major_version: str, docs_base_url: str) -> Version:
        row = self.db.scalar(select(Version).where(Version.major_version == major_version))
        if row:
            row.is_supported = True
            row.docs_base_url = docs_base_url
            return row

        row = Version(major_version=major_version, docs_base_url=docs_base_url, is_supported=True)
        self.db.add(row)
        self.db.flush()
        return row

    def clear_version_corpus(self, version_id, corpus_type: str) -> int:  # type: ignore[no-untyped-def]
        stmt = delete(Document).where(Document.version_id == version_id, Document.corpus_type == corpus_type)
        result = self.db.execute(stmt)
        return int(result.rowcount or 0)

    def insert_documents(
        self,
        *,
        version: Version,
        embedding_model: str,
        embedding_dimension: int,
        documents: list[DocumentPayload],
    ) -> int:
        inserted_chunks = 0
        now = datetime.now(timezone.utc)

        for doc in documents:
            row_doc = Document(
                version_id=version.id,
                title=doc.title,
                source_url=doc.source_url,
                checksum=doc.checksum,
                corpus_type=doc.corpus_type,
                audience_level=doc.audience_level or AudienceLevel.GENERAL.value,
                raw_html=doc.raw_html,
                normalized_text=doc.normalized_text,
                loaded_at=now,
            )
            self.db.add(row_doc)
            self.db.flush()

            for payload in doc.chunks:
                row_chunk = Chunk(
                    document_id=row_doc.id,
                    chunk_index=payload.chunk_index,
                    section_path=payload.section_path,
                    chunk_text=payload.chunk_text,
                    token_count=payload.token_count,
                    content_type=payload.content_type,
                    pedagogical_role=payload.pedagogical_role,
                )
                self.db.add(row_chunk)
                self.db.flush()

                row_embedding = Embedding(
                    chunk_id=row_chunk.id,
                    embedding_model=embedding_model,
                    embedding_dimension=embedding_dimension,
                    embedding=payload.embedding,
                    indexed_at=now,
                )
                self.db.add(row_embedding)
                inserted_chunks += 1

        return inserted_chunks
