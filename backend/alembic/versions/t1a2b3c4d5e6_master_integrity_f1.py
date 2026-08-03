"""Master integrity F1: unique brand.code, seed PUMA/REEBOK, buyer_codes, backfill swatch.brand_id.

Revision ID: t1a2b3c4d5e6
Revises: s3t4u5v6w7x8
Create Date: 2026-08-03
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "t1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "s3t4u5v6w7x8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SEED_BRANDS = ("PUMA", "REEBOK")


def upgrade() -> None:
    conn = op.get_bind()

    # --- unique brands.code (duplikat harus 0) ---
    dups = conn.execute(
        sa.text(
            """
            SELECT code, COUNT(*) c FROM brands
            WHERE code IS NOT NULL AND TRIM(code) != ''
            GROUP BY code HAVING c > 1
            """
        )
    ).fetchall()
    if dups:
        raise RuntimeError(f"Tidak bisa UNIQUE brands.code; duplikat: {dups}")

    # nullable unique di MySQL mengizinkan beberapa NULL — ok
    op.create_unique_constraint("uq_brands_code", "brands", ["code"])

    # --- seed PUMA / REEBOK ---
    for code in SEED_BRANDS:
        exists = conn.execute(
            sa.text("SELECT id FROM brands WHERE UPPER(code) = :c LIMIT 1"),
            {"c": code},
        ).first()
        if not exists:
            conn.execute(
                sa.text("INSERT INTO brands (code, name) VALUES (:c, :n)"),
                {"c": code, "n": code},
            )
        brand_id = conn.execute(
            sa.text("SELECT id FROM brands WHERE UPPER(code) = :c LIMIT 1"),
            {"c": code},
        ).scalar()
        if brand_id:
            mapped = conn.execute(
                sa.text(
                    """
                    SELECT 1 FROM brand_buyer_maps
                    WHERE brand_id = :bid AND UPPER(buyer_code) = :c LIMIT 1
                    """
                ),
                {"bid": brand_id, "c": code},
            ).first()
            if not mapped:
                conn.execute(
                    sa.text(
                        "INSERT INTO brand_buyer_maps (brand_id, buyer_code) VALUES (:bid, :c)"
                    ),
                    {"bid": brand_id, "c": code},
                )

    # --- backfill color_swatch_recipes.brand_id ---
    conn.execute(
        sa.text(
            """
            UPDATE color_swatch_recipes r
            JOIN brands b ON UPPER(b.code) = UPPER(r.buyer_code)
            SET r.brand_id = b.id
            WHERE r.brand_id IS NULL
              AND r.buyer_code IS NOT NULL
              AND TRIM(r.buyer_code) != ''
            """
        )
    )

    # --- buyer_codes registry ---
    op.create_table(
        "buyer_codes",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_buyer_codes_code"),
    )

    # seed union from existing sources + hardcode
    seed_sql = sa.text(
        """
        INSERT IGNORE INTO buyer_codes (code, name, is_active)
        SELECT u.code, u.code, 1 FROM (
          SELECT 'GLOBAL' AS code
          UNION SELECT 'NB' UNION SELECT 'ADIDAS' UNION SELECT 'UA'
          UNION SELECT 'NIKE' UNION SELECT 'PUMA' UNION SELECT 'REEBOK'
          UNION SELECT 'OIA' UNION SELECT 'OIA NIKE'
          UNION SELECT UPPER(TRIM(buyer_code)) FROM buyer_price_lists
            WHERE buyer_code IS NOT NULL AND TRIM(buyer_code) != ''
          UNION SELECT UPPER(TRIM(buyer_code)) FROM brand_buyer_maps
            WHERE buyer_code IS NOT NULL AND TRIM(buyer_code) != ''
          UNION SELECT UPPER(TRIM(buyer_code)) FROM color_swatch_recipes
            WHERE buyer_code IS NOT NULL AND TRIM(buyer_code) != ''
          UNION SELECT UPPER(TRIM(buyer_code)) FROM fluorescent_color_masters
            WHERE buyer_code IS NOT NULL AND TRIM(buyer_code) != ''
        ) u
        WHERE u.code IS NOT NULL AND u.code != ''
        """
    )
    conn.execute(seed_sql)


def downgrade() -> None:
    op.drop_table("buyer_codes")
    op.drop_constraint("uq_brands_code", "brands", type_="unique")
    # seed brands PUMA/REEBOK dibiarkan (aman additive); backfill brand_id tidak di-null-kan massal
