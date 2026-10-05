"""Master integrity F3: audit cols Brand/BuyerPriceList; ensure sheet-row unique if missing.

Revision ID: t3c4d5e6f7g8
Revises: t2b3c4d5e6f7
Create Date: 2026-08-03
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "t3c4d5e6f7g8"
down_revision: Union[str, Sequence[str], None] = "t2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("brands", sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True))
    op.add_column("brands", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column("buyer_price_lists", sa.Column("updated_at", sa.DateTime(), nullable=True))

    bind = op.get_bind()
    insp = inspect(bind)
    uq_names = {u.get("name") for u in insp.get_unique_constraints("buyer_price_sheet_rows")}
    if "uq_buyer_price_sheet_rows_list_row" not in uq_names:
        # may already exist from older migration under same/different name
        existing = False
        for u in insp.get_unique_constraints("buyer_price_sheet_rows"):
            cols = u.get("column_names") or []
            if list(cols) == ["list_id", "row_number"]:
                existing = True
                break
        if not existing:
            op.create_unique_constraint(
                "uq_buyer_price_sheet_rows_list_row",
                "buyer_price_sheet_rows",
                ["list_id", "row_number"],
            )


def downgrade() -> None:
    op.drop_column("buyer_price_lists", "updated_at")
    op.drop_column("brands", "updated_at")
    op.drop_column("brands", "created_at")
