"""add_outstanding_materials

Revision ID: 3b95ed7665f2
Revises: 6f502d99d2c8
Create Date: 2026-04-15 21:58:35.343979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3b95ed7665f2'
down_revision: Union[str, Sequence[str], None] = '6f502d99d2c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "outstanding_materials" not in inspector.get_table_names():
        op.create_table(
            "outstanding_materials",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("po_detail_id", sa.BigInteger(), nullable=False),
            sa.Column("material_name", sa.String(length=255), nullable=True),
            sa.Column("total_qty", sa.Numeric(precision=12, scale=2), nullable=True),
            sa.Column("delivered_qty", sa.Numeric(precision=12, scale=2), nullable=True),
            sa.Column("balance_qty", sa.Numeric(precision=12, scale=2), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["po_detail_id"], ["po_details.id"]),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "outstanding_materials" in inspector.get_table_names():
        op.drop_table("outstanding_materials")
