"""restore fase3 orphan list tables (pricing/finance/inventory receipts)

Revision ID: j9k0l1m2n3o4
Revises: i8j9k0l1m2n3
Create Date: 2026-09-20

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "j9k0l1m2n3o4"
down_revision: Union[str, Sequence[str], None] = "i8j9k0l1m2n3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _tables() -> set[str]:
    bind = op.get_bind()
    rows = bind.exec_driver_sql("SHOW TABLES").fetchall()
    return {r[0] for r in rows}


def upgrade() -> None:
    existing = _tables()
    if "special_prices" not in existing:
        op.create_table(
            "special_prices",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("buyer_code", sa.String(length=32), nullable=False),
            sa.Column("material_pattern", sa.String(length=255), nullable=True),
            sa.Column("emboss_pattern", sa.String(length=100), nullable=True),
            sa.Column("color_pattern", sa.String(length=100), nullable=True),
            sa.Column("discount_type", sa.String(length=20), nullable=False),
            sa.Column("discount_value", sa.Numeric(14, 4), nullable=False),
            sa.Column("valid_from", sa.Date(), nullable=True),
            sa.Column("valid_to", sa.Date(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if "customer_special_prices" not in existing:
        op.create_table(
            "customer_special_prices",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("customer_id", sa.BigInteger(), nullable=False),
            sa.Column("buyer_code", sa.String(length=32), nullable=False),
            sa.Column("material_pattern", sa.String(length=255), nullable=True),
            sa.Column("price_override", sa.Numeric(14, 4), nullable=True),
            sa.Column("discount_percentage", sa.Numeric(5, 2), nullable=True),
            sa.Column("valid_from", sa.Date(), nullable=True),
            sa.Column("valid_to", sa.Date(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
            sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
    if "quotation_headers" not in existing:
        op.create_table(
            "quotation_headers",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("quotation_number", sa.String(length=100), nullable=True),
            sa.Column("customer_id", sa.BigInteger(), nullable=True),
            sa.Column("quotation_date", sa.Date(), nullable=True),
            sa.Column("currency", sa.String(length=3), nullable=True),
            sa.Column("payment_terms", sa.String(length=255), nullable=True),
            sa.Column("valid_until", sa.Date(), nullable=True),
            sa.Column("salesperson", sa.String(length=100), nullable=True),
            sa.Column("remark", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=32), nullable=False),
            sa.Column("total_amount", sa.Numeric(14, 2), nullable=True),
            sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("quotation_number"),
        )
    if "quotation_lines" not in existing:
        op.create_table(
            "quotation_lines",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("quotation_id", sa.BigInteger(), nullable=False),
            sa.Column("line_no", sa.Integer(), nullable=False),
            sa.Column("master_item_id", sa.BigInteger(), nullable=True),
            sa.Column("item_code", sa.String(length=80), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("color", sa.String(length=200), nullable=True),
            sa.Column("specification", sa.String(length=500), nullable=True),
            sa.Column("quantity", sa.Numeric(12, 2), nullable=True),
            sa.Column("unit", sa.String(length=20), nullable=True),
            sa.Column("unit_price", sa.Numeric(14, 4), nullable=True),
            sa.Column("discount_amount", sa.Numeric(14, 2), nullable=True),
            sa.Column("tax_rate", sa.Numeric(5, 2), nullable=True),
            sa.Column("line_amount", sa.Numeric(14, 2), nullable=True),
            sa.ForeignKeyConstraint(["quotation_id"], ["quotation_headers.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["master_item_id"], ["master_items.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
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
    if "outstanding_materials" not in existing:
        op.create_table(
            "outstanding_materials",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("po_detail_id", sa.BigInteger(), nullable=False),
            sa.Column("material_name", sa.String(length=255), nullable=True),
            sa.Column("total_qty", sa.Numeric(12, 2), nullable=True),
            sa.Column("delivered_qty", sa.Numeric(12, 2), nullable=True),
            sa.Column("balance_qty", sa.Numeric(12, 2), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["po_detail_id"], ["po_details.id"]),
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
        op.execute(
            """
            INSERT INTO accounting_mappings
              (transaction_type, status, coa_code, coa_name, description, is_active)
            VALUES
              ('po_created', 'draft', '1-1100', 'Account Receivable', 'Piutang usaha saat PO dibuat', 1),
              ('invoice', 'sent', '1-1200', 'AR - Export', 'Piutang ekspor saat invoice dikirim', 1),
              ('invoice', 'paid', '1-1300', 'Cash/Bank', 'Kas/bank saat invoice dilunasi', 1),
              ('payment', NULL, '2-1000', 'Cost of Goods Sold', 'Harga pokok penjualan', 1)
            """
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
    if "material_receipts" not in existing:
        op.create_table(
            "material_receipts",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("receipt_number", sa.String(length=50), nullable=False),
            sa.Column("supplier_name", sa.String(length=255), nullable=True),
            sa.Column("receipt_date", sa.Date(), nullable=False),
            sa.Column("warehouse_id", sa.BigInteger(), nullable=False),
            sa.Column("total_amount", sa.Numeric(14, 2), nullable=True),
            sa.Column("remark", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("created_at", sa.TIMESTAMP(), nullable=True),
            sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("receipt_number"),
        )
    if "material_receipt_details" not in existing:
        op.create_table(
            "material_receipt_details",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("receipt_id", sa.BigInteger(), nullable=False),
            sa.Column("material_id", sa.BigInteger(), nullable=False),
            sa.Column("quantity", sa.Numeric(12, 2), nullable=False),
            sa.Column("unit_cost", sa.Numeric(14, 4), nullable=True),
            sa.Column("total_cost", sa.Numeric(14, 2), nullable=True),
            sa.Column("remark", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(["receipt_id"], ["material_receipts.id"]),
            sa.ForeignKeyConstraint(["material_id"], ["raw_materials.id"]),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    existing = _tables()
    for name in (
        "material_receipt_details",
        "material_receipts",
        "journal_entries",
        "accounting_mappings",
        "outstanding_materials",
        "subcon_invoices",
        "quotation_lines",
        "quotation_headers",
        "customer_special_prices",
        "special_prices",
    ):
        if name in existing:
            op.drop_table(name)
