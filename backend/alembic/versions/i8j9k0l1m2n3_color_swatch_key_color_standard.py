"""Expand color swatch recipe unique key with color_standard.

Revision ID: i8j9k0l1m2n3
Revises: h7i8j9k0l1m2
Create Date: 2026-09-15
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "i8j9k0l1m2n3"
down_revision: Union[str, Sequence[str], None] = "h7i8j9k0l1m2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _drop_recipe_unique_key() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    uniques = {u["name"] for u in inspector.get_unique_constraints("color_swatch_recipes")}
    if "uq_color_swatch_recipe_key" in uniques:
        op.drop_constraint("uq_color_swatch_recipe_key", "color_swatch_recipes", type_="unique")


def upgrade() -> None:
    _drop_recipe_unique_key()
    # MariaDB 10.3: prefix panjang kolom VARCHAR agar index key tidak melebihi batas.
    op.execute(
        """
        ALTER TABLE color_swatch_recipes
        ADD UNIQUE KEY uq_color_swatch_recipe_key (
            factory_key,
            buyer_code,
            color_code,
            material_name(191),
            emboss(100),
            color_standard(100)
        )
        """
    )


def downgrade() -> None:
    _drop_recipe_unique_key()
    op.execute(
        """
        ALTER TABLE color_swatch_recipes
        ADD UNIQUE KEY uq_color_swatch_recipe_key (
            factory_key,
            buyer_code,
            color_code,
            material_name(191),
            emboss(100)
        )
        """
    )
