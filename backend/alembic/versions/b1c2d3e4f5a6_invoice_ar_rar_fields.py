"""invoice AR fields for RAR report

Revision ID: b1c2d3e4f5a6
Revises: a0b1c2d3e4f5
Create Date: 2026-09-01

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "a0b1c2d3e4f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("invoices", sa.Column("payment_amount", sa.Numeric(14, 2), nullable=True))
    op.add_column("invoices", sa.Column("payment_remark", sa.String(length=120), nullable=True))
    op.add_column("invoices", sa.Column("credit_note_no", sa.String(length=120), nullable=True))
    op.add_column("invoices", sa.Column("credit_note_date", sa.Date(), nullable=True))
    op.add_column("invoices", sa.Column("credit_note_amount", sa.Numeric(14, 2), nullable=True))
    op.add_column("invoices", sa.Column("oia_export_usd", sa.Numeric(14, 2), nullable=True))
    op.create_index("uq_invoices_tax_invoice_no", "invoices", ["tax_invoice_no"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_invoices_tax_invoice_no", table_name="invoices")
    op.drop_column("invoices", "oia_export_usd")
    op.drop_column("invoices", "credit_note_amount")
    op.drop_column("invoices", "credit_note_date")
    op.drop_column("invoices", "credit_note_no")
    op.drop_column("invoices", "payment_remark")
    op.drop_column("invoices", "payment_amount")
