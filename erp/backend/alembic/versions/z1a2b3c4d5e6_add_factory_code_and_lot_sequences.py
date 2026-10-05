"""Add factory_code to PO headers and lot_sequences table for lot number generation."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "z1a2b3c4d5e6"
down_revision = "aa11bb22cc33"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tambah kolom factory_code ke po_headers
    op.add_column(
        "po_headers",
        sa.Column("factory_code", sa.String(length=32), nullable=True),
    )

    # Tabel sequence nomor lot per prefix+factory+tanggal
    op.create_table(
        "lot_sequences",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("prefix", sa.String(length=8), nullable=False),
        sa.Column("factory_code", sa.String(length=32), nullable=False),
        sa.Column("date_ymd", sa.String(length=8), nullable=False),
        sa.Column("last_value", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint(
            "prefix",
            "factory_code",
            "date_ymd",
            name="uq_lot_sequences_prefix_factory_date",
        ),
    )


def downgrade() -> None:
    op.drop_table("lot_sequences")
    op.drop_column("po_headers", "factory_code")

