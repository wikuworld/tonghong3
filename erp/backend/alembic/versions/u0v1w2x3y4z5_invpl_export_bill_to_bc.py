"""Export customer (Bill To), kode material ekspor, BC di surat jalan.

Revision ID: u0v1w2x3y4z5
Revises: s8t9u0v1w2x3
Create Date: 2026-04-09

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "u0v1w2x3y4z5"
down_revision: Union[str, None] = "s8t9u0v1w2x3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column("is_export_customer", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column("customers", sa.Column("bill_to", sa.Text(), nullable=True))
    op.add_column(
        "master_items",
        sa.Column("exim_material_code", sa.String(length=80), nullable=True),
    )
    op.add_column(
        "delivery_headers",
        sa.Column("bc_number", sa.String(length=80), nullable=True),
    )
    op.add_column("delivery_headers", sa.Column("bc_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("delivery_headers", "bc_date")
    op.drop_column("delivery_headers", "bc_number")
    op.drop_column("master_items", "exim_material_code")
    op.drop_column("customers", "bill_to")
    op.drop_column("customers", "is_export_customer")
