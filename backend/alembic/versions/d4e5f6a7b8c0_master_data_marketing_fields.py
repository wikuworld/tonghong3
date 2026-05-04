"""Master item, master harga matrix, jadwal kirim per baris SO, kolom marketing/EXIM.

Revision ID: d4e5f6a7b8c0
Revises: a1b2c3d4e5f6
Create Date: 2026-04-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c0"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "master_items",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("item_code", sa.String(length=50), nullable=False),
        sa.Column("thickness_mm", sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column("material_name", sa.String(length=500), nullable=True),
        sa.Column("emboss", sa.String(length=500), nullable=True),
        sa.Column("color", sa.String(length=500), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_code", name="uq_master_items_item_code"),
    )

    op.create_table(
        "master_prices",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("line_no", sa.Integer(), nullable=True),
        sa.Column("material_category", sa.String(length=255), nullable=True),
        sa.Column("material_type", sa.String(length=255), nullable=True),
        sa.Column("material_name", sa.String(length=500), nullable=True),
        sa.Column("thickness_range", sa.String(length=80), nullable=True),
        sa.Column("price_white_usd", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("price_black_usd", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("price_color_usd", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("price_metallic_usd", sa.Numeric(precision=14, scale=4), nullable=True),
        sa.Column("remark", sa.String(length=255), nullable=True),
        sa.Column("price_tier", sa.String(length=32), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_master_prices_material_name", "master_prices", ["material_name"])

    op.create_table(
        "po_detail_deliveries",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("po_detail_id", sa.BigInteger(), nullable=False),
        sa.Column("sequence_no", sa.SmallInteger(), nullable=False),
        sa.Column("qty", sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column("delivery_date", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["po_detail_id"],
            ["po_details.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "po_detail_id",
            "sequence_no",
            name="uq_po_detail_deliveries_detail_seq",
        ),
    )
    op.create_index(
        "ix_po_detail_deliveries_po_detail_id",
        "po_detail_deliveries",
        ["po_detail_id"],
    )

    op.add_column(
        "po_headers",
        sa.Column("marketing_excel_date_serial", sa.Integer(), nullable=True),
    )
    op.add_column(
        "po_headers",
        sa.Column("po_customer_ref", sa.Text(), nullable=True),
    )
    op.add_column(
        "po_headers",
        sa.Column("order_type_label", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "po_headers",
        sa.Column("brand_name_snapshot", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "po_headers",
        sa.Column("customer_name_snapshot", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "po_details",
        sa.Column("master_item_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "po_details",
        sa.Column("thi_line_ref", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "po_details",
        sa.Column("emboss", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "po_details",
        sa.Column("thickness_text", sa.String(length=80), nullable=True),
    )
    op.add_column(
        "po_details",
        sa.Column("vir_softness_type", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "po_details",
        sa.Column("rtd_text", sa.String(length=80), nullable=True),
    )
    op.add_column(
        "po_details",
        sa.Column("etd_excel_serial", sa.Integer(), nullable=True),
    )
    op.add_column(
        "po_details",
        sa.Column("stock_wh_qty", sa.Numeric(precision=14, scale=2), nullable=True),
    )
    op.add_column(
        "po_details",
        sa.Column("balance_qty", sa.Numeric(precision=14, scale=2), nullable=True),
    )
    op.add_column(
        "po_details",
        sa.Column("system_reference", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "po_details",
        sa.Column("detail_remark", sa.Text(), nullable=True),
    )
    op.create_foreign_key(
        "fk_po_details_master_item_id",
        "po_details",
        "master_items",
        ["master_item_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_po_details_thi_line_ref", "po_details", ["thi_line_ref"])


def downgrade() -> None:
    op.drop_index("ix_po_details_thi_line_ref", table_name="po_details")
    op.drop_constraint("fk_po_details_master_item_id", "po_details", type_="foreignkey")
    for col in (
        "detail_remark",
        "system_reference",
        "balance_qty",
        "stock_wh_qty",
        "etd_excel_serial",
        "rtd_text",
        "vir_softness_type",
        "thickness_text",
        "emboss",
        "thi_line_ref",
        "master_item_id",
    ):
        op.drop_column("po_details", col)

    for col in (
        "customer_name_snapshot",
        "brand_name_snapshot",
        "order_type_label",
        "po_customer_ref",
        "marketing_excel_date_serial",
    ):
        op.drop_column("po_headers", col)

    op.drop_index("ix_po_detail_deliveries_po_detail_id", table_name="po_detail_deliveries")
    op.drop_table("po_detail_deliveries")
    op.drop_index("ix_master_prices_material_name", table_name="master_prices")
    op.drop_table("master_prices")
    op.drop_table("master_items")
