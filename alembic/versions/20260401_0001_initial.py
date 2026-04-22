"""Initial schema with pgvector and query traceability

Revision ID: 20260401_0001
Revises: None
Create Date: 2026-04-01 16:15:00
"""
from __future__ import annotations

import os

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql


revision = "20260401_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    embedding_dim = int(os.getenv("EMBEDDING_DIMENSION", "1024"))

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("major_version", sa.String(length=10), nullable=False, unique=True),
        sa.Column("docs_base_url", sa.String(length=255), nullable=False),
        sa.Column("is_supported", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("source_url", sa.String(length=700), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=False),
        sa.Column("corpus_type", sa.String(length=30), nullable=False),
        sa.Column("audience_level", sa.String(length=30), nullable=False),
        sa.Column("raw_html", sa.Text(), nullable=True),
        sa.Column("normalized_text", sa.Text(), nullable=True),
        sa.Column("loaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("corpus_type IN ('official', 'supplementary')", name="ck_documents_corpus_type"),
        sa.CheckConstraint("audience_level IN ('general', 'novice')", name="ck_documents_audience_level"),
        sa.UniqueConstraint("version_id", "source_url", "corpus_type", name="uq_documents_version_url_corpus"),
    )

    op.create_table(
        "chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("section_path", sa.String(length=700), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("content_type", sa.String(length=50), nullable=False, server_default="paragraph"),
        sa.Column("pedagogical_role", sa.String(length=30), nullable=False, server_default="overview"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(
            "pedagogical_role IN ('overview', 'prerequisite', 'step', 'example', 'warning')",
            name="ck_chunks_pedagogical_role",
        ),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_chunks_document_chunk_index"),
    )

    op.create_table(
        "embeddings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("chunk_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chunks.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("embedding_model", sa.String(length=120), nullable=False),
        sa.Column("embedding_dimension", sa.Integer(), nullable=False),
        sa.Column("embedding", Vector(embedding_dim), nullable=False),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "query_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("selected_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("versions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("user_question", sa.Text(), nullable=False),
        sa.Column("mode", sa.String(length=30), nullable=False),
        sa.Column("extended_mode", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("answer_text", sa.Text(), nullable=True),
        sa.Column("tutorial_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="success"),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("mode IN ('answer', 'tutorial')", name="ck_query_history_mode"),
        sa.CheckConstraint("status IN ('success', 'failed')", name="ck_query_history_status"),
    )

    op.create_table(
        "query_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("query_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("query_history.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chunks.id", ondelete="SET NULL"), nullable=True),
        sa.Column("rank_position", sa.Integer(), nullable=False),
        sa.Column("similarity_score", sa.Numeric(8, 5), nullable=False),
        sa.Column("used_in_result", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("source_role", sa.String(length=30), nullable=False),
        sa.Column("source_title", sa.String(length=500), nullable=False),
        sa.Column("source_url", sa.String(length=700), nullable=False),
        sa.Column("section_path", sa.String(length=700), nullable=False),
        sa.Column("corpus_type", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("source_role IN ('base', 'supplementary')", name="ck_query_sources_source_role"),
        sa.CheckConstraint("corpus_type IN ('official', 'supplementary')", name="ck_query_sources_corpus_type"),
    )

    op.create_index("ix_documents_version_corpus", "documents", ["version_id", "corpus_type"])
    op.create_index("ix_chunks_document_chunk_index", "chunks", ["document_id", "chunk_index"])
    op.create_index("ix_query_history_created_at", "query_history", ["created_at"])
    op.create_index("ix_query_sources_query_rank", "query_sources", ["query_id", "rank_position"])
    op.create_index("ix_versions_major_version", "versions", ["major_version"], unique=True)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_embeddings_embedding ON embeddings "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_embeddings_embedding")
    op.drop_index("ix_versions_major_version", table_name="versions")
    op.drop_index("ix_query_sources_query_rank", table_name="query_sources")
    op.drop_index("ix_query_history_created_at", table_name="query_history")
    op.drop_index("ix_chunks_document_chunk_index", table_name="chunks")
    op.drop_index("ix_documents_version_corpus", table_name="documents")

    op.drop_table("query_sources")
    op.drop_table("query_history")
    op.drop_table("embeddings")
    op.drop_table("chunks")
    op.drop_table("documents")
    op.drop_table("versions")
