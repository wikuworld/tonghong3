"""Master color swatch recipes (legacy DATA COLOR SWATCH).

Revision ID: f2a3b4c5d6e7
Revises: e1f2a3b4c5d6
Create Date: 2026-05-12

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2a3b4c5d6e7"
down_revision: Union[str, Sequence[str], None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "color_swatch_recipes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("factory_key", sa.String(length=80), nullable=False),
        sa.Column("customer_id", sa.BigInteger(), nullable=True),
        sa.Column("buyer_code", sa.String(length=32), nullable=False),
        sa.Column("brand_id", sa.BigInteger(), nullable=True),
        sa.Column("color_code", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("color_name", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("emboss", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("color_standard", sa.String(length=255), nullable=True),
        sa.Column("backing", sa.String(length=120), nullable=True),
        sa.Column("material_name", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("legacy_urut", sa.String(length=32), nullable=True),
        sa.Column("entered_at", sa.Date(), nullable=True),
        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "factory_key",
            "buyer_code",
            "color_code",
            "material_name",
            "emboss",
            name="uq_color_swatch_recipe_key",
        ),
    )
    op.create_index("ix_color_swatch_factory_key", "color_swatch_recipes", ["factory_key"])
    op.create_index("ix_color_swatch_buyer_code", "color_swatch_recipes", ["buyer_code"])
    op.create_index("ix_color_swatch_material_name", "color_swatch_recipes", ["material_name"], mysql_length=191)
    op.create_index("ix_color_swatch_color_code", "color_swatch_recipes", ["color_code"])


def downgrade() -> None:
    op.drop_table("color_swatch_recipes")
