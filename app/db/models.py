from __future__ import annotations

import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.db.base import Base
from app.db.enums import AudienceLevel, CorpusType, ModeType, PedagogicalRole, QueryStatus, SourceRole


class Version(Base):
    __tablename__ = "versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    major_version: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    docs_base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    is_supported: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    loaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    documents: Mapped[list[Document]] = relationship(back_populates="version", cascade="all, delete-orphan")
    query_history: Mapped[list[QueryHistory]] = relationship(back_populates="version")


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("version_id", "source_url", "corpus_type", name="uq_documents_version_url_corpus"),
        CheckConstraint(
            f"corpus_type IN ('{CorpusType.OFFICIAL.value}', '{CorpusType.SUPPLEMENTARY.value}')",
            name="ck_documents_corpus_type",
        ),
        CheckConstraint(
            f"audience_level IN ('{AudienceLevel.GENERAL.value}', '{AudienceLevel.NOVICE.value}')",
            name="ck_documents_audience_level",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("versions.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_url: Mapped[str] = mapped_column(String(700), nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    corpus_type: Mapped[str] = mapped_column(String(30), nullable=False)
    audience_level: Mapped[str] = mapped_column(String(30), nullable=False)
    raw_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    loaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    version: Mapped[Version] = relationship(back_populates="documents")
    chunks: Mapped[list[Chunk]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"
    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_chunks_document_chunk_index"),
        CheckConstraint(
            (
                "pedagogical_role IN "
                f"('{PedagogicalRole.OVERVIEW.value}', '{PedagogicalRole.PREREQUISITE.value}', "
                f"'{PedagogicalRole.STEP.value}', '{PedagogicalRole.EXAMPLE.value}', '{PedagogicalRole.WARNING.value}')"
            ),
            name="ck_chunks_pedagogical_role",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    section_path: Mapped[str] = mapped_column(String(700), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False, default="paragraph")
    pedagogical_role: Mapped[str] = mapped_column(String(30), nullable=False, default=PedagogicalRole.OVERVIEW.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    document: Mapped[Document] = relationship(back_populates="chunks")
    embedding: Mapped[Embedding | None] = relationship(back_populates="chunk", uselist=False, cascade="all, delete-orphan")
    query_sources: Mapped[list[QuerySource]] = relationship(back_populates="chunk")


class Embedding(Base):
    __tablename__ = "embeddings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chunks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    embedding_model: Mapped[str] = mapped_column(String(120), nullable=False)
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.embedding_dimension), nullable=False)
    indexed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    chunk: Mapped[Chunk] = relationship(back_populates="embedding")


class QueryHistory(Base):
    __tablename__ = "query_history"
    __table_args__ = (
        CheckConstraint(
            f"mode IN ('{ModeType.SHORT.value}', '{ModeType.DETAILED.value}', '{ModeType.TUTORIAL.value}')",
            name="ck_query_history_mode",
        ),
        CheckConstraint(
            f"status IN ('{QueryStatus.SUCCESS.value}', '{QueryStatus.FAILED.value}')",
            name="ck_query_history_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    selected_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_question: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[str] = mapped_column(String(30), nullable=False)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    tutorial_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default=QueryStatus.SUCCESS.value)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    version: Mapped[Version | None] = relationship(back_populates="query_history")
    sources: Mapped[list[QuerySource]] = relationship(back_populates="query", cascade="all, delete-orphan")


class QuerySource(Base):
    __tablename__ = "query_sources"
    __table_args__ = (
        CheckConstraint(
            f"source_role IN ('{SourceRole.BASE.value}', '{SourceRole.SUPPLEMENTARY.value}')",
            name="ck_query_sources_source_role",
        ),
        CheckConstraint(
            f"corpus_type IN ('{CorpusType.OFFICIAL.value}', '{CorpusType.SUPPLEMENTARY.value}')",
            name="ck_query_sources_corpus_type",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("query_history.id", ondelete="CASCADE"), nullable=False)
    chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chunks.id", ondelete="SET NULL"),
        nullable=True,
    )
    rank_position: Mapped[int] = mapped_column(Integer, nullable=False)
    similarity_score: Mapped[float] = mapped_column(Numeric(8, 5), nullable=False)
    used_in_result: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    source_role: Mapped[str] = mapped_column(String(30), nullable=False)
    source_title: Mapped[str] = mapped_column(String(500), nullable=False)
    source_url: Mapped[str] = mapped_column(String(700), nullable=False)
    section_path: Mapped[str] = mapped_column(String(700), nullable=False)
    corpus_type: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    query: Mapped[QueryHistory] = relationship(back_populates="sources")
    chunk: Mapped[Chunk | None] = relationship(back_populates="query_sources")
