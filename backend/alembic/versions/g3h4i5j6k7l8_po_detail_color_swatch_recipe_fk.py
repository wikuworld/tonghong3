"""PO detail: FK ke master color swatch recipe.

Revision ID: g3h4i5j6k7l8
Revises: f2a3b4c5d6e7
Create Date: 2026-06-04

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "g3h4i5j6k7l8"
down_revision: Union[str, Sequence[str], None] = "f2a3b4c5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "po_details",
        sa.Column("color_swatch_recipe_id", sa.BigInteger(), nullable=True),
    )
    op.create_index(
        "ix_po_details_color_swatch_recipe_id",
        "po_details",
        ["color_swatch_recipe_id"],
    )
    op.create_foreign_key(
        "fk_po_details_color_swatch_recipe",
        "po_details",
        "color_swatch_recipes",
        ["color_swatch_recipe_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_po_details_color_swatch_recipe", "po_details", type_="foreignkey")
    op.drop_index("ix_po_details_color_swatch_recipe_id", table_name="po_details")
    op.drop_column("po_details", "color_swatch_recipe_id")
