"""Rename master_items category Suide -> Suede.

Revision ID: d2s3u4e5d6e7
Revises: c1w2i3n4d5o6
Create Date: 2026-10-05
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "d2s3u4e5d6e7"
down_revision: Union[str, Sequence[str], None] = "c1w2i3n4d5o6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE master_items
        SET category = 'Suede'
        WHERE LOWER(TRIM(category)) = 'suide'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE master_items
        SET category = 'Suide'
        WHERE LOWER(TRIM(category)) = 'suede'
        """
    )
