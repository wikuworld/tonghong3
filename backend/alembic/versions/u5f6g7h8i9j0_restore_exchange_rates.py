"""Restore exchange_rates if missing (dashboard + ExchangeRatePage).

Revision ID: u5f6g7h8i9j0
Revises: t4d5e6f7g8h9
Create Date: 2026-08-03
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "u5f6g7h8i9j0"
down_revision: Union[str, Sequence[str], None] = "t4d5e6f7g8h9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    if "exchange_rates" in insp.get_table_names():
        # pastikan kolom valid_from/valid_to ada (migrasi bbbb6bfbe9e4)
        cols = {c["name"] for c in insp.get_columns("exchange_rates")}
        if "valid_from" not in cols:
            op.add_column("exchange_rates", sa.Column("valid_from", sa.Date(), nullable=True))
        if "valid_to" not in cols:
            op.add_column("exchange_rates", sa.Column("valid_to", sa.Date(), nullable=True))
        return

    op.create_table(
        "exchange_rates",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("idr_per_usd", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_to", sa.Date(), nullable=True),
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


def downgrade() -> None:
    # Jangan drop di downgrade — tabel boleh sudah ada sebelum revisi ini.
    pass
