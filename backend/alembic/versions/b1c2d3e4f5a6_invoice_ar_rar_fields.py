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


def _invoice_columns() -> set[str]:
    bind = op.get_bind()
    rows = bind.exec_driver_sql("SHOW COLUMNS FROM invoices").fetchall()
    return {r[0] for r in rows}


def _has_index(name: str) -> bool:
    bind = op.get_bind()
    rows = bind.exec_driver_sql(
        f"SHOW INDEX FROM invoices WHERE Key_name='{name}'"
    ).fetchall()
    return bool(rows)


def upgrade() -> None:
    cols = _invoice_columns()
    if "payment_amount" not in cols:
        op.add_column("invoices", sa.Column("payment_amount", sa.Numeric(14, 2), nullable=True))
    if "payment_remark" not in cols:
        op.add_column("invoices", sa.Column("payment_remark", sa.String(length=120), nullable=True))
    if "credit_note_no" not in cols:
        op.add_column("invoices", sa.Column("credit_note_no", sa.String(length=120), nullable=True))
    if "credit_note_date" not in cols:
        op.add_column("invoices", sa.Column("credit_note_date", sa.Date(), nullable=True))
    if "credit_note_amount" not in cols:
        op.add_column("invoices", sa.Column("credit_note_amount", sa.Numeric(14, 2), nullable=True))
    if "oia_export_usd" not in cols:
        op.add_column("invoices", sa.Column("oia_export_usd", sa.Numeric(14, 2), nullable=True))
    if not _has_index("uq_invoices_tax_invoice_no"):
        op.create_index("uq_invoices_tax_invoice_no", "invoices", ["tax_invoice_no"], unique=True)


def downgrade() -> None:
    if _has_index("uq_invoices_tax_invoice_no"):
        op.drop_index("uq_invoices_tax_invoice_no", table_name="invoices")
    cols = _invoice_columns()
    for name in (
        "oia_export_usd",
        "credit_note_amount",
        "credit_note_date",
        "credit_note_no",
        "payment_remark",
        "payment_amount",
    ):
        if name in cols:
            op.drop_column("invoices", name)
