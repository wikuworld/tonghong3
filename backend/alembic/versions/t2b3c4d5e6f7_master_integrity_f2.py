"""Master integrity F2: material_aliases, fluorescent.brand_id, seed aliases, safe rename.

Revision ID: t2b3c4d5e6f7
Revises: t1a2b3c4d5e6
Create Date: 2026-08-03
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "t2b3c4d5e6f7"
down_revision: Union[str, Sequence[str], None] = "t1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# alias (upper trimmed) → canonical material_name di master_items
ALIAS_SEEDS = [
    ("PM GENERIC PU COATED", "GENERIC PU COATED LEATHER"),
    ("(PM) GENERIC PU COATED", "GENERIC PU COATED LEATHER"),
    ("(PM) GENERIC PU COATED LEATHER", "GENERIC PU COATED LEATHER"),
    ("SOFT PU COATED", "SOFT PU COATED LEATHER"),
    ("VIRGIN HYDRO", "VIRGIN HYDRO PU LEATHER"),
    ("VIRGIN HYRDO PU", "VIRGIN HYDRO PU LEATHER"),
    ("VIRGIN HIDRO PU", "VIRGIN HYDRO PU LEATHER"),
    ("VIRGIN HDRO PU", "VIRGIN HYDRO PU LEATHER"),
]


def upgrade() -> None:
    op.create_table(
        "material_aliases",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("alias_name", sa.String(length=500), nullable=False),
        sa.Column("canonical_name", sa.String(length=500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("alias_name", name="uq_material_aliases_alias"),
    )

    op.add_column(
        "fluorescent_color_masters",
        sa.Column("brand_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_fluorescent_brand_id",
        "fluorescent_color_masters",
        "brands",
        ["brand_id"],
        ["id"],
        ondelete="SET NULL",
    )

    conn = op.get_bind()
    for alias, canonical in ALIAS_SEEDS:
        conn.execute(
            sa.text(
                """
                INSERT IGNORE INTO material_aliases (alias_name, canonical_name, is_active)
                VALUES (:a, :c, 1)
                """
            ),
            {"a": alias, "c": canonical},
        )

    conn.execute(
        sa.text(
            """
            UPDATE fluorescent_color_masters f
            JOIN brands b ON UPPER(b.code) = UPPER(f.buyer_code)
            SET f.brand_id = b.id
            WHERE f.brand_id IS NULL
              AND f.buyer_code IS NOT NULL
              AND UPPER(TRIM(f.buyer_code)) != 'GLOBAL'
            """
        )
    )

    # Safe rename: only when target unique key free
    for alias, canonical in ALIAS_SEEDS:
        rows = conn.execute(
            sa.text(
                """
                SELECT id, factory_key, buyer_code, color_code, emboss, material_name
                FROM color_swatch_recipes
                WHERE is_active = 1
                  AND UPPER(TRIM(material_name)) = UPPER(TRIM(:alias))
                """
            ),
            {"alias": alias},
        ).mappings().all()
        for r in rows:
            conflict = conn.execute(
                sa.text(
                    """
                    SELECT id FROM color_swatch_recipes
                    WHERE factory_key = :fk AND buyer_code = :bc AND color_code = :cc
                      AND material_name = :mat AND emboss = :em AND id != :id
                    LIMIT 1
                    """
                ),
                {
                    "fk": r["factory_key"],
                    "bc": r["buyer_code"],
                    "cc": r["color_code"],
                    "mat": canonical,
                    "em": r["emboss"],
                    "id": r["id"],
                },
            ).first()
            if conflict:
                continue
            conn.execute(
                sa.text(
                    "UPDATE color_swatch_recipes SET material_name = :mat WHERE id = :id"
                ),
                {"mat": canonical, "id": r["id"]},
            )


def downgrade() -> None:
    # reverse rename best-effort via aliases
    conn = op.get_bind()
    for alias, canonical in ALIAS_SEEDS:
        conn.execute(
            sa.text(
                """
                UPDATE color_swatch_recipes
                SET material_name = :alias
                WHERE UPPER(TRIM(material_name)) = UPPER(TRIM(:canonical))
                  AND source_file LIKE '%DATA COLOR%'
                """
            ),
            {"alias": alias, "canonical": canonical},
        )
    op.drop_constraint("fk_fluorescent_brand_id", "fluorescent_color_masters", type_="foreignkey")
    op.drop_column("fluorescent_color_masters", "brand_id")
    op.drop_table("material_aliases")
