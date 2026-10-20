"""Soft-delete flag on delivery headers.

Revision ID: i3j4k5l6m7n8
Revises: h2i3j4k5l6m7
Create Date: 2026-10-20
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "i3j4k5l6m7n8"
down_revision: Union[str, Sequence[str], None] = "h2i3j4k5l6m7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "delivery_headers",
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("delivery_headers", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.add_column("delivery_headers", sa.Column("deleted_by", sa.String(length=100), nullable=True))
    op.add_column("delivery_headers", sa.Column("delete_reason", sa.Text(), nullable=True))
    op.create_index("ix_delivery_headers_is_deleted", "delivery_headers", ["is_deleted"])
    op.execute(
        """
        UPDATE delivery_headers
        SET is_deleted = 1,
            deleted_at = COALESCE(deleted_at, cancelled_at),
            deleted_by = COALESCE(NULLIF(TRIM(deleted_by), ''), cancelled_by),
            delete_reason = COALESCE(NULLIF(TRIM(delete_reason), ''), cancel_reason)
        WHERE LOWER(TRIM(COALESCE(status, ''))) IN ('cancelled', 'canceled')
        """
    )


def downgrade() -> None:
    op.drop_index("ix_delivery_headers_is_deleted", table_name="delivery_headers")
    op.drop_column("delivery_headers", "delete_reason")
    op.drop_column("delivery_headers", "deleted_by")
    op.drop_column("delivery_headers", "deleted_at")
    op.drop_column("delivery_headers", "is_deleted")
