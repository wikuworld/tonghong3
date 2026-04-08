"""Invoice FK ke delivery — alur tagihan setelah pengiriman.

Revision ID: g7h8i9j0k1l2
Revises: f6a7b8c9d0e1
Create Date: 2026-04-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "g7h8i9j0k1l2"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "invoices",
        sa.Column("delivery_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_invoices_delivery_id",
        "invoices",
        "delivery_headers",
        ["delivery_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_invoices_delivery_id", "invoices", ["delivery_id"])


def downgrade() -> None:
    op.drop_index("ix_invoices_delivery_id", table_name="invoices")
    op.drop_constraint("fk_invoices_delivery_id", "invoices", type_="foreignkey")
    op.drop_column("invoices", "delivery_id")
