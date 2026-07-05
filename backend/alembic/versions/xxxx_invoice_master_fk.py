"""Add customer_id and po_id FKs to invoices

Revision ID: xxxx_invoice_master_fk
Revises: 5b2e04f5ef69
Create Date: 2026-04-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "xxxx_invoice_master_fk"
down_revision: Union[str, Sequence[str], None] = "5b2e04f5ef69"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "invoices",
        sa.Column("customer_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_invoices_customer_id",
        "invoices",
        "customers",
        ["customer_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_invoices_customer_id", "invoices", ["customer_id"])

    op.add_column(
        "invoices",
        sa.Column("po_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_invoices_po_id",
        "invoices",
        "po_headers",
        ["po_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_invoices_po_id", "invoices", ["po_id"])


def downgrade() -> None:
    op.drop_index("ix_invoices_po_id", table_name="invoices")
    op.drop_constraint("fk_invoices_po_id", "invoices", type_="foreignkey")
    op.drop_column("invoices", "po_id")

    op.drop_index("ix_invoices_customer_id", table_name="invoices")
    op.drop_constraint("fk_invoices_customer_id", "invoices", type_="foreignkey")
    op.drop_column("invoices", "customer_id")
