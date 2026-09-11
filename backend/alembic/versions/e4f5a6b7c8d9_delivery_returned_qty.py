"""add returned_qty on delivery_details for goods return

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-09-11
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "e4f5a6b7c8d9"
down_revision = "d3e4f5a6b7c8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "delivery_details",
        sa.Column("returned_qty", sa.Numeric(12, 2), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("delivery_details", "returned_qty")
