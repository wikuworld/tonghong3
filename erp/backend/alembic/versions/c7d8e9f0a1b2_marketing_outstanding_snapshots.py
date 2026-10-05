"""Tabel snapshot master outstanding marketing (JSON baris + filter)."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "c7d8e9f0a1b2"
down_revision = "b2c3d4e5f6a8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "marketing_outstanding_snapshots",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("label", sa.String(length=255), nullable=True),
        sa.Column("filter_params_json", sa.JSON(), nullable=True),
        sa.Column("rows_json", sa.JSON(), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column("created_by_username", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_mkt_out_snap_created_at",
        "marketing_outstanding_snapshots",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_mkt_out_snap_created_at", table_name="marketing_outstanding_snapshots")
    op.drop_table("marketing_outstanding_snapshots")
