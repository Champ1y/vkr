"""Drop query_history.extended_mode.

Revision ID: 20260507_0004
Revises: 20260505_0003
Create Date: 2026-05-07 12:00:00
"""
from __future__ import annotations

from alembic import op


revision = "20260507_0004"
down_revision = "20260505_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE query_history DROP COLUMN IF EXISTS extended_mode")


def downgrade() -> None:
    op.execute("ALTER TABLE query_history ADD COLUMN IF NOT EXISTS extended_mode BOOLEAN NOT NULL DEFAULT false")
