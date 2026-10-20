"""Add buyer-price addon flags on master items.

Revision ID: h2i3j4k5l6m7
Revises: g1h2i3j4k5l6
Create Date: 2026-10-18
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "h2i3j4k5l6m7"
down_revision: Union[str, Sequence[str], None] = "g1h2i3j4k5l6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_FLAG_COLUMNS = (
    "flag_color_black",
    "flag_color",
    "flag_flourasent",
    "flag_metalic",
    "flag_emboss",
    "flag_special_emboss",
)


def upgrade() -> None:
    for name in _FLAG_COLUMNS:
        op.add_column(
            "master_items",
            sa.Column(name, sa.Boolean(), nullable=False, server_default=sa.false()),
        )


def downgrade() -> None:
    for name in reversed(_FLAG_COLUMNS):
        op.drop_column("master_items", name)
