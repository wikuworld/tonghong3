"""CR: exchange rate, audit, brands/PIC, SO addresses & line ETD, QC reject qty, packing.

Revision ID: a1b2c3d4e5f6
Revises: 91749ac20ed0
Create Date: 2026-04-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "91749ac20ed0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "exchange_rates",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("idr_per_usd", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_exchange_rates_effective_date", "exchange_rates", ["effective_date"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", sa.BigInteger(), nullable=True),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("payload_before", sa.Text(), nullable=True),
        sa.Column("payload_after", sa.Text(), nullable=True),
        sa.Column("actor", sa.String(length=120), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])

    op.create_table(
        "brands",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.BigInteger(), nullable=True),
        sa.Column("code", sa.String(length=50), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "customer_pics",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("customer_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("title", sa.String(length=120), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("po_headers", sa.Column("billing_address", sa.Text(), nullable=True))
    op.add_column("po_headers", sa.Column("delivery_address", sa.Text(), nullable=True))
    op.add_column("po_headers", sa.Column("brand_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key("fk_po_headers_brand", "po_headers", "brands", ["brand_id"], ["id"])

    op.add_column("po_details", sa.Column("line_etd", sa.Date(), nullable=True))
    op.add_column(
        "po_details",
        sa.Column("unit_price", sa.Numeric(precision=14, scale=4), nullable=True),
    )
    op.add_column(
        "po_details",
        sa.Column("copied_from_detail_id", sa.BigInteger(), nullable=True),
    )

    op.add_column(
        "qc_details",
        sa.Column("qty_checked", sa.Numeric(precision=12, scale=2), nullable=True),
    )
    op.add_column(
        "qc_details",
        sa.Column("qty_reject", sa.Numeric(precision=12, scale=2), nullable=True),
    )
    op.add_column("qc_details", sa.Column("reject_reason", sa.Text(), nullable=True))

    op.create_table(
        "packing_headers",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("packing_number", sa.String(length=100), nullable=True),
        sa.Column("production_id", sa.BigInteger(), nullable=True),
        sa.Column("qc_header_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(["production_id"], ["production_orders.id"]),
        sa.ForeignKeyConstraint(["qc_header_id"], ["qc_headers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("packing_number"),
    )

    op.create_table(
        "packing_details",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("packing_id", sa.BigInteger(), nullable=True),
        sa.Column("production_detail_id", sa.BigInteger(), nullable=True),
        sa.Column("qty_packed", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.ForeignKeyConstraint(
            ["packing_id"], ["packing_headers.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["production_detail_id"], ["production_details.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column("delivery_headers", sa.Column("packing_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "fk_delivery_headers_packing", "delivery_headers", "packing_headers", ["packing_id"], ["id"]
    )

    op.add_column(
        "production_details",
        sa.Column(
            "is_over_production",
            sa.Boolean(),
            nullable=True,
            server_default=sa.text("0"),
        ),
    )

    op.create_table(
        "document_sequences",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("doc_type", sa.String(length=20), nullable=False),
        sa.Column("period", sa.String(length=10), nullable=False),
        sa.Column("last_value", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("doc_type", "period", name="uq_document_sequences_doc_period"),
    )


def downgrade() -> None:
    op.drop_table("document_sequences")

    op.drop_constraint("fk_delivery_headers_packing", "delivery_headers", type_="foreignkey")
    op.drop_column("delivery_headers", "packing_id")

    op.drop_table("packing_details")
    op.drop_table("packing_headers")

    op.drop_column("qc_details", "reject_reason")
    op.drop_column("qc_details", "qty_reject")
    op.drop_column("qc_details", "qty_checked")

    op.drop_column("po_details", "copied_from_detail_id")
    op.drop_column("po_details", "unit_price")
    op.drop_column("po_details", "line_etd")

    op.drop_constraint("fk_po_headers_brand", "po_headers", type_="foreignkey")
    op.drop_column("po_headers", "brand_id")
    op.drop_column("po_headers", "delivery_address")
    op.drop_column("po_headers", "billing_address")

    op.drop_column("production_details", "is_over_production")

    op.drop_table("customer_pics")
    op.drop_table("brands")

    op.drop_table("audit_logs")
    op.drop_table("exchange_rates")
