"""master_item_autofill_fields

Revision ID: o4p5q6r7s8t9
Revises: n3o4p5q6r7s8
Create Date: 2026-04-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "o4p5q6r7s8t9"
down_revision: Union[str, Sequence[str], None] = "n3o4p5q6r7s8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("master_items", sa.Column("softness", sa.String(length=100), nullable=True))
    op.add_column(
        "master_items", sa.Column("color_reference", sa.String(length=255), nullable=True)
    )
    op.add_column("master_items", sa.Column("backing", sa.String(length=255), nullable=True))
    op.add_column(
        "master_items",
        sa.Column("quantity_order_default", sa.Numeric(precision=12, scale=2), nullable=True),
    )
    op.add_column(
        "master_items", sa.Column("style_article", sa.String(length=100), nullable=True)
    )
    op.add_column("master_items", sa.Column("model", sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column("master_items", "model")
    op.drop_column("master_items", "style_article")
    op.drop_column("master_items", "quantity_order_default")
    op.drop_column("master_items", "backing")
    op.drop_column("master_items", "color_reference")
    op.drop_column("master_items", "softness")
