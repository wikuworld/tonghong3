"""Simplify master_items editable fields.

Revision ID: 7a8b9c0d1e2f
Revises: 2592619169ba
Create Date: 2026-04-29
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "7a8b9c0d1e2f"
down_revision: Union[str, Sequence[str], None] = "2592619169ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Normalisasi kategori ke tiga nilai baku.
    op.execute(
        """
        UPDATE master_items
        SET category = CASE
            WHEN category IS NULL OR TRIM(category) = '' THEN 'PU'
            WHEN LOWER(TRIM(category)) = 'pu' THEN 'PU'
            WHEN LOWER(TRIM(category)) IN ('suide', 'suede') THEN 'Suide'
            WHEN LOWER(TRIM(category)) IN ('subkon', 'subcont', 'subcontract') THEN 'SubKon'
            ELSE category
        END
        """
    )
    # Kolom lama tidak dipakai lagi di form input Master Item.
    op.execute(
        """
        UPDATE master_items
        SET thickness_mm = NULL,
            softness = NULL,
            color_reference = NULL,
            color_standard = NULL,
            backing = NULL,
            quantity_order_default = NULL,
            style_article = NULL,
            model = NULL,
            model_takedown = NULL,
            exim_material_code = NULL
        """
    )


def downgrade() -> None:
    # Data lama tidak dapat dipulihkan otomatis.
    pass
