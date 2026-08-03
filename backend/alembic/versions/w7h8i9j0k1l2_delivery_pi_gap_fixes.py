"""delivery_details.packing_detail_id + proforma_invoice_records.

Revision ID: w7h8i9j0k1l2
Revises: v6g7h8i9j0k1
Create Date: 2026-08-04
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "w7h8i9j0k1l2"
down_revision: Union[str, Sequence[str], None] = "v6g7h8i9j0k1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    dd_cols = {c["name"] for c in insp.get_columns("delivery_details")}
    if "packing_detail_id" not in dd_cols:
        op.add_column(
            "delivery_details",
            sa.Column("packing_detail_id", sa.BigInteger(), nullable=True),
        )
        op.create_index(
            "ix_delivery_details_packing_detail_id",
            "delivery_details",
            ["packing_detail_id"],
        )
        op.create_foreign_key(
            "fk_delivery_details_packing_detail",
            "delivery_details",
            "packing_details",
            ["packing_detail_id"],
            ["id"],
            ondelete="SET NULL",
        )

    if "proforma_invoice_records" not in insp.get_table_names():
        op.create_table(
            "proforma_invoice_records",
            sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
            sa.Column("pi_number", sa.String(length=120), nullable=False),
            sa.Column("customer_id", sa.BigInteger(), nullable=True),
            sa.Column("customer_name", sa.String(length=255), nullable=True),
            sa.Column("po_ids_json", sa.JSON(), nullable=False),
            sa.Column("po_detail_ids_json", sa.JSON(), nullable=True),
            sa.Column("total_qty", sa.Numeric(14, 2), nullable=True),
            sa.Column("total_amount", sa.Numeric(14, 2), nullable=True),
            sa.Column("created_by", sa.String(length=100), nullable=True),
            sa.Column(
                "created_at",
                sa.TIMESTAMP(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=True,
            ),
            sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("pi_number", name="uq_proforma_invoice_records_pi_number"),
        )
        op.create_index(
            "ix_proforma_invoice_records_customer_id",
            "proforma_invoice_records",
            ["customer_id"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "proforma_invoice_records" in insp.get_table_names():
        op.drop_index("ix_proforma_invoice_records_customer_id", table_name="proforma_invoice_records")
        op.drop_table("proforma_invoice_records")
    dd_cols = {c["name"] for c in insp.get_columns("delivery_details")}
    if "packing_detail_id" in dd_cols:
        op.drop_constraint("fk_delivery_details_packing_detail", "delivery_details", type_="foreignkey")
        op.drop_index("ix_delivery_details_packing_detail_id", table_name="delivery_details")
        op.drop_column("delivery_details", "packing_detail_id")
