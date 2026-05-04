"""Drop unused customer address fields.

Revision ID: e8f9a0b1c2d3
Revises: d6e7f8a9b0c1
Create Date: 2026-04-29
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e8f9a0b1c2d3"
down_revision: Union[str, Sequence[str], None] = "d6e7f8a9b0c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("customers")}
    if "shipping_address" in cols:
        op.drop_column("customers", "shipping_address")
    if "bill_to" in cols:
        op.drop_column("customers", "bill_to")
    if "address_line2" in cols:
        op.drop_column("customers", "address_line2")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("customers")}
    if "address_line2" not in cols:
        op.add_column("customers", sa.Column("address_line2", sa.Text(), nullable=True))
    if "bill_to" not in cols:
        op.add_column("customers", sa.Column("bill_to", sa.Text(), nullable=True))
    if "shipping_address" not in cols:
        op.add_column("customers", sa.Column("shipping_address", sa.Text(), nullable=True))
