"""Unique invoice per delivery_id.

Revision ID: g6h7i8j9k0l1
Revises: f5a6b7c8d9e0
Create Date: 2026-09-14
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect, text

revision: str = "g6h7i8j9k0l1"
down_revision: Union[str, Sequence[str], None] = "f5a6b7c8d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    dups = conn.execute(
        text(
            "SELECT delivery_id FROM invoices "
            "WHERE delivery_id IS NOT NULL GROUP BY delivery_id HAVING COUNT(*) > 1"
        )
    ).fetchall()
    if dups:
        return
    indexes = {ix["name"] for ix in inspect(conn).get_indexes("invoices")}
    # Jangan drop ix_invoices_delivery_id: MariaDB memakainya untuk FK.
    if "uq_invoices_delivery_id" not in indexes:
        op.create_index("uq_invoices_delivery_id", "invoices", ["delivery_id"], unique=True)


def downgrade() -> None:
    indexes = {ix["name"] for ix in inspect(op.get_bind()).get_indexes("invoices")}
    if "uq_invoices_delivery_id" in indexes:
        op.drop_index("uq_invoices_delivery_id", table_name="invoices")
