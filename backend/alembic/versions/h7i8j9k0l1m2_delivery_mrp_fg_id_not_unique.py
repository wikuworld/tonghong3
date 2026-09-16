"""Allow several surat jalan from one MRP packing FG.

Revision ID: h7i8j9k0l1m2
Revises: g6h7i8j9k0l1
Create Date: 2026-09-14
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

revision: str = "h7i8j9k0l1m2"
down_revision: Union[str, Sequence[str], None] = "g6h7i8j9k0l1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    indexes = {ix["name"]: ix for ix in inspect(op.get_bind()).get_indexes("delivery_headers")}
    ix = indexes.get("ix_delivery_headers_mrp_fg_id")
    if not ix:
        op.create_index(
            "ix_delivery_headers_mrp_fg_id",
            "delivery_headers",
            ["mrp_fg_id"],
            unique=False,
        )
        return
    if ix.get("unique"):
        op.drop_index("ix_delivery_headers_mrp_fg_id", table_name="delivery_headers")
        op.create_index(
            "ix_delivery_headers_mrp_fg_id",
            "delivery_headers",
            ["mrp_fg_id"],
            unique=False,
        )


def downgrade() -> None:
    indexes = {ix["name"]: ix for ix in inspect(op.get_bind()).get_indexes("delivery_headers")}
    ix = indexes.get("ix_delivery_headers_mrp_fg_id")
    if ix and not ix.get("unique"):
        op.drop_index("ix_delivery_headers_mrp_fg_id", table_name="delivery_headers")
        op.create_index(
            "ix_delivery_headers_mrp_fg_id",
            "delivery_headers",
            ["mrp_fg_id"],
            unique=True,
        )
