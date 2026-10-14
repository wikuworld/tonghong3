"""Master unit per tipe material inventory + kolom ukuran raw_materials.

Revision ID: e7i8n9v0u1n2
Revises: d2s3u4e5d6e7
Create Date: 2026-10-07
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e7i8n9v0u1n2"
down_revision: Union[str, Sequence[str], None] = "d2s3u4e5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inventory_unit_masters",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("material_type", sa.String(32), nullable=False),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("material_type", "unit", name="uq_inv_unit_type_unit"),
    )
    op.create_index("ix_inv_unit_masters_type", "inventory_unit_masters", ["material_type"])

    op.add_column("raw_materials", sa.Column("size", sa.String(80), nullable=True))

    conn = op.get_bind()
    seeds = [
        ("kulit", "SF"),
        ("kulit", "SQFT"),
        ("kulit", "M2"),
        ("kimia", "KG"),
        ("kimia", "G"),
        ("kimia", "L"),
        ("kimia", "ML"),
        ("kimia", "DRUM"),
        ("kimia", "PAIL"),
        ("kimia", "SAK"),
        ("material_lain", "PCS"),
        ("material_lain", "SET"),
        ("material_lain", "ROLL"),
        ("rp", "KG"),
        ("rp", "PCS"),
        ("rp", "BAG"),
    ]
    for mt, unit in seeds:
        conn.execute(
            sa.text(
                "INSERT IGNORE INTO inventory_unit_masters (material_type, unit, is_active) "
                "VALUES (:mt, :unit, 1)"
            ),
            {"mt": mt, "unit": unit},
        )


def downgrade() -> None:
    op.drop_column("raw_materials", "size")
    op.drop_index("ix_inv_unit_masters_type", table_name="inventory_unit_masters")
    op.drop_table("inventory_unit_masters")
