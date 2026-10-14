"""Add color_window_masters table.

Revision ID: c1w2i3n4d5o6
Revises: b0c1d2e3f4a5
Create Date: 2026-10-05
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c1w2i3n4d5o6"
down_revision: Union[str, Sequence[str], None] = "b0c1d2e3f4a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "color_window_masters",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("color_code", sa.String(length=64), nullable=False),
        sa.Column("color_name", sa.String(length=255), nullable=False),
        sa.Column("brand_code", sa.String(length=50), nullable=False),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_color_window_masters_brand",
        "color_window_masters",
        ["brand_code"],
        unique=False,
    )
    op.create_index(
        "ix_color_window_masters_code",
        "color_window_masters",
        ["color_code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_color_window_masters_code", table_name="color_window_masters")
    op.drop_index("ix_color_window_masters_brand", table_name="color_window_masters")
    op.drop_table("color_window_masters")
