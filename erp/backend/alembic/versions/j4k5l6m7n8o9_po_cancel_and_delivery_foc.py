"""Kolom batal SO dan flag FOC surat jalan.

Revision ID: j4k5l6m7n8o9
Revises: i3j4k5l6m7n8
Create Date: 2026-10-21
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "j4k5l6m7n8o9"
down_revision: Union[str, Sequence[str], None] = "i3j4k5l6m7n8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("po_headers", sa.Column("cancel_reason", sa.Text(), nullable=True))
    op.add_column("po_headers", sa.Column("cancelled_at", sa.DateTime(), nullable=True))
    op.add_column("po_headers", sa.Column("cancelled_by", sa.String(length=100), nullable=True))
    op.add_column(
        "delivery_headers",
        sa.Column("is_foc", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("delivery_headers", "is_foc")
    op.drop_column("po_headers", "cancelled_by")
    op.drop_column("po_headers", "cancelled_at")
    op.drop_column("po_headers", "cancel_reason")
