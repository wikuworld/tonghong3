"""Merge customer and quotation migration heads.

Revision ID: f9e8d7c6b5a4
Revises: e7f8a9b0c1d2, f4a5b6c7d8e9
Create Date: 2026-04-23
"""

from typing import Sequence, Union


revision: str = "f9e8d7c6b5a4"
down_revision: Union[str, Sequence[str], None] = ("e7f8a9b0c1d2", "f4a5b6c7d8e9")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
