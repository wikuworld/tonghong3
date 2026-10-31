"""Diskon pabrik kembali ke master customer.

Revision ID: p1q2r3s4t5u6
Revises: o9p0q1r2s3t4
Create Date: 2026-10-31
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "p1q2r3s4t5u6"
down_revision: Union[str, Sequence[str], None] = "o9p0q1r2s3t4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column(
            "discount_modifier_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column("customers", sa.Column("discount_modifier", sa.Numeric(14, 4), nullable=True))
    op.add_column(
        "customers",
        sa.Column("discount_modifier_type", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("customers", "discount_modifier_type")
    op.drop_column("customers", "discount_modifier")
    op.drop_column("customers", "discount_modifier_enabled")
