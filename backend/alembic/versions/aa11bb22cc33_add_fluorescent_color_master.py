"""Add fluorescent color master table.

Revision ID: aa11bb22cc33
Revises: 7a8b9c0d1e2f
Create Date: 2026-04-30
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "aa11bb22cc33"
down_revision: Union[str, Sequence[str], None] = "7a8b9c0d1e2f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fluorescent_color_masters",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("buyer_code", sa.String(length=32), nullable=False, server_default="GLOBAL"),
        sa.Column("season_label", sa.String(length=64), nullable=True),
        sa.Column("season_year", sa.Integer(), nullable=True),
        sa.Column("season_type", sa.String(length=16), nullable=True),
        sa.Column("color_name", sa.String(length=255), nullable=False),
        sa.Column("color_code", sa.String(length=64), nullable=True),
        sa.Column("color_class", sa.String(length=32), nullable=False, server_default="fluorescent"),
        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "buyer_code",
            "season_label",
            "color_code",
            "color_name",
            name="uq_fluorescent_color_master",
        ),
    )
    op.create_index(
        "ix_fluorescent_color_masters_buyer",
        "fluorescent_color_masters",
        ["buyer_code"],
        unique=False,
    )
    op.create_index(
        "ix_fluorescent_color_masters_season",
        "fluorescent_color_masters",
        ["season_label"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_fluorescent_color_masters_season", table_name="fluorescent_color_masters")
    op.drop_index("ix_fluorescent_color_masters_buyer", table_name="fluorescent_color_masters")
    op.drop_table("fluorescent_color_masters")

