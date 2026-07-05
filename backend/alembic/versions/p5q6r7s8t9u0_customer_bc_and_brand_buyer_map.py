"""Customer BC fields and brand-buyer mapping.

Revision ID: p5q6r7s8t9u0
Revises: o4p5q6r7s8t9
Create Date: 2026-04-08
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "p5q6r7s8t9u0"
down_revision: Union[str, Sequence[str], None] = "o4p5q6r7s8t9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("customers", sa.Column("skep_kb_number", sa.String(length=80), nullable=True))
    op.add_column("customers", sa.Column("customs_office_code", sa.String(length=32), nullable=True))
    op.create_table(
        "brand_buyer_maps",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("brand_id", sa.BigInteger(), nullable=False),
        sa.Column("buyer_code", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["brand_id"], ["brands.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("brand_id", "buyer_code", name="uq_brand_buyer_map"),
    )


def downgrade() -> None:
    op.drop_table("brand_buyer_maps")
    op.drop_column("customers", "customs_office_code")
    op.drop_column("customers", "skep_kb_number")
