"""Pabean: penyimpanan lengkap AJU (VICTORY-D / Core Customs) + tautan ke SO.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c0
Create Date: 2026-04-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "customs_declarations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("nomor_aju", sa.String(length=64), nullable=False),
        sa.Column("kode_dokumen", sa.String(length=16), nullable=True),
        sa.Column("source_label", sa.String(length=255), nullable=True),
        sa.Column("versi_template", sa.String(length=32), nullable=True),
        sa.Column(
            "meta_json",
            sa.JSON(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nomor_aju", name="uq_customs_declarations_nomor_aju"),
    )
    op.create_index("ix_customs_declarations_kode_dokumen", "customs_declarations", ["kode_dokumen"])

    op.create_table(
        "customs_aju_sheet_rows",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("declaration_id", sa.BigInteger(), nullable=False),
        sa.Column("sheet_code", sa.String(length=64), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("cells", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["declaration_id"],
            ["customs_declarations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "declaration_id",
            "sheet_code",
            "row_number",
            name="uq_customs_aju_sheet_rows_decl_sheet_row",
        ),
    )
    op.create_index(
        "ix_customs_aju_sheet_rows_declaration_sheet",
        "customs_aju_sheet_rows",
        ["declaration_id", "sheet_code"],
    )

    op.add_column(
        "po_headers",
        sa.Column(
            "customs_declaration_id",
            sa.BigInteger(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_po_headers_customs_declaration_id",
        "po_headers",
        "customs_declarations",
        ["customs_declaration_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_po_headers_customs_declaration_id",
        "po_headers",
        ["customs_declaration_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_po_headers_customs_declaration_id", table_name="po_headers")
    op.drop_constraint("fk_po_headers_customs_declaration_id", "po_headers", type_="foreignkey")
    op.drop_column("po_headers", "customs_declaration_id")

    op.drop_index("ix_customs_aju_sheet_rows_declaration_sheet", table_name="customs_aju_sheet_rows")
    op.drop_table("customs_aju_sheet_rows")

    op.drop_index("ix_customs_declarations_kode_dokumen", table_name="customs_declarations")
    op.drop_table("customs_declarations")
