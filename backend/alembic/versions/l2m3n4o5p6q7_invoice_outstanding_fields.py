"""invoice_outstanding_fields

Revision ID: l2m3n4o5p6q7
Revises: k1l2m3n4o5p6
Create Date: 2026-04-08

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "l2m3n4o5p6q7"
down_revision: Union[str, Sequence[str], None] = "k1l2m3n4o5p6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("invoices", sa.Column("due_date", sa.Date(), nullable=True))
    op.add_column("invoices", sa.Column("tax_invoice_no", sa.String(length=80), nullable=True))
    op.add_column("invoices", sa.Column("tax_invoice_date", sa.Date(), nullable=True))
    op.add_column("invoices", sa.Column("receipt_no", sa.String(length=80), nullable=True))
    op.add_column("invoices", sa.Column("received_by", sa.String(length=120), nullable=True))
    op.add_column("invoices", sa.Column("received_date", sa.Date(), nullable=True))
    op.add_column("invoices", sa.Column("nopen", sa.String(length=80), nullable=True))
    op.add_column("invoices", sa.Column("nomor_aju", sa.String(length=80), nullable=True))


def downgrade() -> None:
    op.drop_column("invoices", "nomor_aju")
    op.drop_column("invoices", "nopen")
    op.drop_column("invoices", "received_date")
    op.drop_column("invoices", "received_by")
    op.drop_column("invoices", "receipt_no")
    op.drop_column("invoices", "tax_invoice_date")
    op.drop_column("invoices", "tax_invoice_no")
    op.drop_column("invoices", "due_date")

