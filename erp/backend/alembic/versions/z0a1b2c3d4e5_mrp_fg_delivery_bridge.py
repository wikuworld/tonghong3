"""MRP FG OUT bridge: packing stub refs + delivery po_detail_id.

Revision ID: z0a1b2c3d4e5
Revises: y9j0k1l2m3n4
Create Date: 2026-08-09
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "z0a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "y9j0k1l2m3n4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    ph_cols = {c["name"] for c in insp.get_columns("packing_headers")}
    if "source" not in ph_cols:
        op.add_column(
            "packing_headers",
            sa.Column("source", sa.String(length=16), nullable=True),
        )
    if "mrp_packing_id" not in ph_cols:
        op.add_column(
            "packing_headers",
            sa.Column("mrp_packing_id", sa.BigInteger(), nullable=True),
        )
    if "mrp_fg_id" not in ph_cols:
        op.add_column(
            "packing_headers",
            sa.Column("mrp_fg_id", sa.BigInteger(), nullable=True),
        )
    ph_idx = {i["name"] for i in insp.get_indexes("packing_headers")}
    if "ix_packing_headers_mrp_fg_id" not in ph_idx:
        op.create_index(
            "ix_packing_headers_mrp_fg_id",
            "packing_headers",
            ["mrp_fg_id"],
            unique=True,
        )

    dh_cols = {c["name"] for c in insp.get_columns("delivery_headers")}
    if "mrp_fg_id" not in dh_cols:
        op.add_column(
            "delivery_headers",
            sa.Column("mrp_fg_id", sa.BigInteger(), nullable=True),
        )
    dh_idx = {i["name"] for i in insp.get_indexes("delivery_headers")}
    if "ix_delivery_headers_mrp_fg_id" not in dh_idx:
        op.create_index(
            "ix_delivery_headers_mrp_fg_id",
            "delivery_headers",
            ["mrp_fg_id"],
            unique=True,
        )

    dd_cols = {c["name"] for c in insp.get_columns("delivery_details")}
    if "po_detail_id" not in dd_cols:
        op.add_column(
            "delivery_details",
            sa.Column("po_detail_id", sa.BigInteger(), nullable=True),
        )
        op.create_foreign_key(
            "fk_delivery_details_po_detail_id",
            "delivery_details",
            "po_details",
            ["po_detail_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_index(
            "ix_delivery_details_po_detail_id",
            "delivery_details",
            ["po_detail_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    dd_cols = {c["name"] for c in insp.get_columns("delivery_details")}
    if "po_detail_id" in dd_cols:
        dd_idx = {i["name"] for i in insp.get_indexes("delivery_details")}
        if "ix_delivery_details_po_detail_id" in dd_idx:
            op.drop_index("ix_delivery_details_po_detail_id", table_name="delivery_details")
        try:
            op.drop_constraint(
                "fk_delivery_details_po_detail_id",
                "delivery_details",
                type_="foreignkey",
            )
        except Exception:
            pass
        op.drop_column("delivery_details", "po_detail_id")

    dh_idx = {i["name"] for i in insp.get_indexes("delivery_headers")}
    if "ix_delivery_headers_mrp_fg_id" in dh_idx:
        op.drop_index("ix_delivery_headers_mrp_fg_id", table_name="delivery_headers")
    dh_cols = {c["name"] for c in insp.get_columns("delivery_headers")}
    if "mrp_fg_id" in dh_cols:
        op.drop_column("delivery_headers", "mrp_fg_id")

    ph_idx = {i["name"] for i in insp.get_indexes("packing_headers")}
    if "ix_packing_headers_mrp_fg_id" in ph_idx:
        op.drop_index("ix_packing_headers_mrp_fg_id", table_name="packing_headers")
    ph_cols = {c["name"] for c in insp.get_columns("packing_headers")}
    for col in ("mrp_fg_id", "mrp_packing_id", "source"):
        if col in ph_cols:
            op.drop_column("packing_headers", col)
