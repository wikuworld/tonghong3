"""Modul penawaran (quotation) header + baris material.

Revision ID: f4a5b6c7d8e9
Revises: e3f4a5b6c7d8
Create Date: 2026-04-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f4a5b6c7d8e9"
down_revision: Union[str, Sequence[str], None] = "e3f4a5b6c7d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "quotation_headers",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("quotation_number", sa.String(length=100), nullable=True),
        sa.Column("customer_id", sa.BigInteger(), nullable=True),
        sa.Column("quotation_date", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True, server_default="USD"),
        sa.Column("payment_terms", sa.String(length=255), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("salesperson", sa.String(length=100), nullable=True),
        sa.Column("remark", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("quotation_number"),
    )
    op.create_index("ix_quotation_headers_customer_id", "quotation_headers", ["customer_id"])
    op.create_index("ix_quotation_headers_status", "quotation_headers", ["status"])
    op.create_index("ix_quotation_headers_quotation_date", "quotation_headers", ["quotation_date"])

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
        sa.Column("unit", sa.String(length=20), nullable=True, server_default="S/F"),
        sa.Column("unit_price", sa.Numeric(14, 4), nullable=True),
        sa.Column("discount_amount", sa.Numeric(14, 2), nullable=True, server_default="0"),
        sa.Column("tax_rate", sa.Numeric(5, 2), nullable=True, server_default="0"),
        sa.Column("line_amount", sa.Numeric(14, 2), nullable=True),
        sa.ForeignKeyConstraint(["master_item_id"], ["master_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["quotation_id"], ["quotation_headers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_quotation_lines_quotation_id", "quotation_lines", ["quotation_id"])


def downgrade() -> None:
    op.drop_index("ix_quotation_lines_quotation_id", table_name="quotation_lines")
    op.drop_table("quotation_lines")
    op.drop_index("ix_quotation_headers_quotation_date", table_name="quotation_headers")
    op.drop_index("ix_quotation_headers_status", table_name="quotation_headers")
    op.drop_index("ix_quotation_headers_customer_id", table_name="quotation_headers")
    op.drop_table("quotation_headers")
