"""List harga per buyer (NB, ADIDAS, NIKE, UA) — baris lengkap sebagai JSON.

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-04-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "buyer_price_lists",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("buyer_code", sa.String(length=32), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("period_label", sa.Text(), nullable=True),
        sa.Column("period_start", sa.Date(), nullable=True),
        sa.Column("period_end", sa.Date(), nullable=True),
        sa.Column("source_label", sa.String(length=255), nullable=True),
        sa.Column("meta_json", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("buyer_code", name="uq_buyer_price_lists_buyer_code"),
    )
    op.create_index("ix_buyer_price_lists_buyer_code", "buyer_price_lists", ["buyer_code"])

    op.create_table(
        "buyer_price_sheet_rows",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("list_id", sa.BigInteger(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("cells", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["list_id"],
            ["buyer_price_lists.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "list_id",
            "row_number",
            name="uq_buyer_price_sheet_rows_list_row",
        ),
    )
    op.create_index(
        "ix_buyer_price_sheet_rows_list_id",
        "buyer_price_sheet_rows",
        ["list_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_buyer_price_sheet_rows_list_id", table_name="buyer_price_sheet_rows")
    op.drop_table("buyer_price_sheet_rows")
    op.drop_index("ix_buyer_price_lists_buyer_code", table_name="buyer_price_lists")
    op.drop_table("buyer_price_lists")
