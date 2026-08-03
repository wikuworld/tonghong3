"""Merge alembic heads: packing (k2) + marketing outstanding (d8).

Revision ID: m0a1b2c3d4e5
Revises: k2l3m4n5o6p7, d8e9f0a1b2c3
Create Date: 2026-08-03
"""

from __future__ import annotations

from typing import Sequence, Union

revision: str = "m0a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = ("k2l3m4n5o6p7", "d8e9f0a1b2c3")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
