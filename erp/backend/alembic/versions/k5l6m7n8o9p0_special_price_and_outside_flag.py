"""Modifier special price di baris SO dan flag outside customer.

Revision ID: k5l6m7n8o9p0
Revises: j4k5l6m7n8o9
Create Date: 2026-10-21
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "k5l6m7n8o9p0"
down_revision: Union[str, Sequence[str], None] = "j4k5l6m7n8o9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "po_details",
        sa.Column("is_special_price", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("po_details", sa.Column("discount_type", sa.String(length=20), nullable=True))
    op.add_column("po_details", sa.Column("discount_value", sa.Numeric(14, 4), nullable=True))
    op.add_column("po_details", sa.Column("list_unit_price", sa.Numeric(14, 4), nullable=True))
    op.add_column(
        "customers",
        sa.Column("outside_banten", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.execute(
        "UPDATE customers SET outside_banten = 1 "
        "WHERE UPPER(TRIM(code)) IN ('BI020', 'AF001')"
    )


def downgrade() -> None:
    op.drop_column("customers", "outside_banten")
    op.drop_column("po_details", "list_unit_price")
    op.drop_column("po_details", "discount_value")
    op.drop_column("po_details", "discount_type")
    op.drop_column("po_details", "is_special_price")
