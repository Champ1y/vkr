"""Switch query_history.mode to short/detailed/tutorial.

Revision ID: 20260505_0003
Revises: 20260504_0002
Create Date: 2026-05-05 17:20:00
"""
from __future__ import annotations

from alembic import op


revision = "20260505_0003"
down_revision = "20260504_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop previous constraint first, otherwise UPDATE to 'short' violates old CHECK.
    op.execute("ALTER TABLE query_history DROP CONSTRAINT IF EXISTS ck_query_history_mode")
    # Rows from the earlier two-mode schema used mode='answer'. Keep them as short answers.
    op.execute("UPDATE query_history SET mode = 'short' WHERE mode = 'answer'")
    op.execute("ALTER TABLE query_history ADD CONSTRAINT ck_query_history_mode CHECK (mode IN ('short', 'detailed', 'tutorial'))")


def downgrade() -> None:
    # Drop current constraint first, otherwise UPDATE to 'answer' violates CHECK.
    op.execute("ALTER TABLE query_history DROP CONSTRAINT IF EXISTS ck_query_history_mode")
    # Both short and detailed are collapsed back into the earlier answer mode.
    op.execute("UPDATE query_history SET mode = 'answer' WHERE mode IN ('short', 'detailed')")
    op.execute("ALTER TABLE query_history ADD CONSTRAINT ck_query_history_mode CHECK (mode IN ('answer', 'tutorial'))")
