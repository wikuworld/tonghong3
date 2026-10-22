"""Jenis adjust outside dan diskon modifier customer.

Revision ID: m7n8o9p0q1r2
Revises: l6m7n8o9p0q1
Create Date: 2026-10-21
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "m7n8o9p0q1r2"
down_revision: Union[str, Sequence[str], None] = "l6m7n8o9p0q1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("customers", sa.Column("outside_adjust_type", sa.String(length=20), nullable=True))
    op.add_column("customers", sa.Column("discount_modifier", sa.Numeric(14, 4), nullable=True))
    op.add_column(
        "customers",
        sa.Column("discount_modifier_type", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("customers", "discount_modifier_type")
    op.drop_column("customers", "discount_modifier")
    op.drop_column("customers", "outside_adjust_type")
