"""Switch embeddings to BAAI/bge-m3 vector(1024) with destructive corpus reset.

Revision ID: 20260504_0002
Revises: 20260401_0001
Create Date: 2026-05-04 16:00:00

NOTE:
- This migration is destructive for indexed corpus data.
- It truncates documents (CASCADE), which also clears chunks, embeddings, and query_sources.
- A full reindex of official + supplementary corpora is required after upgrade/downgrade.
"""
from __future__ import annotations

from alembic import op


revision = "20260504_0002"
down_revision = "20260401_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("TRUNCATE TABLE documents CASCADE")
    op.execute("ALTER TABLE embeddings ALTER COLUMN embedding TYPE vector(1024)")


def downgrade() -> None:
    op.execute("TRUNCATE TABLE documents CASCADE")
    op.execute("ALTER TABLE embeddings ALTER COLUMN embedding TYPE vector(768)")
