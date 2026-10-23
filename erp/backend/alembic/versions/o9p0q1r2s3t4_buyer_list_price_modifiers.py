"""Tambahan outside dan diskon pindah ke list harga buyer.

Revision ID: o9p0q1r2s3t4
Revises: n8o9p0q1r2s3
Create Date: 2026-10-22
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "o9p0q1r2s3t4"
down_revision: Union[str, Sequence[str], None] = "n8o9p0q1r2s3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("buyer_price_lists", sa.Column("outside_price_adjust", sa.Numeric(14, 4), nullable=True))
    op.add_column("buyer_price_lists", sa.Column("outside_adjust_type", sa.String(length=20), nullable=True))
    op.add_column(
        "buyer_price_lists",
        sa.Column("discount_modifier_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("buyer_price_lists", sa.Column("discount_modifier", sa.Numeric(14, 4), nullable=True))
    op.add_column(
        "buyer_price_lists",
        sa.Column("discount_modifier_type", sa.String(length=20), nullable=True),
    )
    op.drop_column("customers", "discount_modifier_enabled")
    op.drop_column("customers", "discount_modifier_type")
    op.drop_column("customers", "discount_modifier")
    op.drop_column("customers", "outside_adjust_type")
    op.drop_column("customers", "outside_price_adjust")


def downgrade() -> None:
    op.add_column("customers", sa.Column("outside_price_adjust", sa.Numeric(14, 4), nullable=True))
    op.add_column("customers", sa.Column("outside_adjust_type", sa.String(length=20), nullable=True))
    op.add_column("customers", sa.Column("discount_modifier", sa.Numeric(14, 4), nullable=True))
    op.add_column("customers", sa.Column("discount_modifier_type", sa.String(length=20), nullable=True))
    op.add_column(
        "customers",
        sa.Column("discount_modifier_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.drop_column("buyer_price_lists", "discount_modifier_type")
    op.drop_column("buyer_price_lists", "discount_modifier")
    op.drop_column("buyer_price_lists", "discount_modifier_enabled")
    op.drop_column("buyer_price_lists", "outside_adjust_type")
    op.drop_column("buyer_price_lists", "outside_price_adjust")
