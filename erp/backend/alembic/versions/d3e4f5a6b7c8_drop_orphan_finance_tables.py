"""drop orphan finance tables (subcon/accounting/journal)

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-09-11

Removes unused Phase-4 accounting UI tables:
- subcon_invoices
- accounting_mappings
- journal_entries
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d3e4f5a6b7c8"
down_revision: Union[str, Sequence[str], None] = "c2d3e4f5a6b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _tables() -> set[str]:
    bind = op.get_bind()
    rows = bind.exec_driver_sql("SHOW TABLES").fetchall()
    return {r[0] for r in rows}


def upgrade() -> None:
    existing = _tables()
    for name in ("journal_entries", "accounting_mappings", "subcon_invoices"):
        if name in existing:
            op.drop_table(name)


def downgrade() -> None:
    existing = _tables()
    if "subcon_invoices" not in existing:
        op.create_table(
            "subcon_invoices",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("po_id", sa.BigInteger(), nullable=False),
            sa.Column("invoice_type", sa.String(length=20), nullable=False),
            sa.Column("invoice_number", sa.String(length=100), nullable=True),
            sa.Column("amount", sa.Numeric(14, 2), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["po_id"], ["po_headers.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if "accounting_mappings" not in existing:
        op.create_table(
            "accounting_mappings",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("transaction_type", sa.String(length=50), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=True),
            sa.Column("coa_code", sa.String(length=20), nullable=False),
            sa.Column("coa_name", sa.String(length=100), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if "journal_entries" not in existing:
        op.create_table(
            "journal_entries",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("transaction_type", sa.String(length=50), nullable=False),
            sa.Column("transaction_id", sa.BigInteger(), nullable=False),
            sa.Column("coa_code", sa.String(length=20), nullable=False),
            sa.Column("coa_name", sa.String(length=100), nullable=False),
            sa.Column("debit", sa.Numeric(14, 2), nullable=False),
            sa.Column("credit", sa.Numeric(14, 2), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("entry_date", sa.Date(), nullable=False),
            sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
