"""Add updated_at to fluorescent_color_masters.

Revision ID: r2s3t4u5v6w7
Revises: q1r2s3t4u5v6
Create Date: 2026-08-03
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "r2s3t4u5v6w7"
down_revision: Union[str, Sequence[str], None] = "q1r2s3t4u5v6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "fluorescent_color_masters",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("fluorescent_color_masters", "updated_at")
