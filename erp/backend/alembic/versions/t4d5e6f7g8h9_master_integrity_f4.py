"""Master integrity F4: FK buyer_code columns → buyer_codes.code (after seed clean).

Revision ID: t4d5e6f7g8h9
Revises: t3c4d5e6f7g8
Create Date: 2026-08-03
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "t4d5e6f7g8h9"
down_revision: Union[str, Sequence[str], None] = "t3c4d5e6f7g8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_FK_SPECS = (
    ("fk_brand_buyer_maps_buyer_code", "brand_buyer_maps"),
    ("fk_buyer_price_lists_buyer_code", "buyer_price_lists"),
    ("fk_color_swatch_buyer_code", "color_swatch_recipes"),
    ("fk_fluorescent_buyer_code", "fluorescent_color_masters"),
)


def _existing_fk_names(conn, table: str) -> set[str]:
    rows = conn.execute(
        sa.text(
            """
            SELECT CONSTRAINT_NAME
            FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :t
              AND CONSTRAINT_TYPE = 'FOREIGN KEY'
            """
        ),
        {"t": table},
    ).fetchall()
    return {r[0] for r in rows}


def _ensure_all_codes(conn) -> None:
    """Insert any missing buyer codes referenced by child tables."""
    conn.execute(
        sa.text(
            """
            INSERT IGNORE INTO buyer_codes (code, name, is_active)
            SELECT u.code, u.code, 1 FROM (
              SELECT UPPER(TRIM(buyer_code)) AS code FROM brand_buyer_maps
                WHERE buyer_code IS NOT NULL AND TRIM(buyer_code) != ''
              UNION SELECT UPPER(TRIM(buyer_code)) FROM buyer_price_lists
                WHERE buyer_code IS NOT NULL AND TRIM(buyer_code) != ''
              UNION SELECT UPPER(TRIM(buyer_code)) FROM color_swatch_recipes
                WHERE buyer_code IS NOT NULL AND TRIM(buyer_code) != ''
              UNION SELECT UPPER(TRIM(buyer_code)) FROM fluorescent_color_masters
                WHERE buyer_code IS NOT NULL AND TRIM(buyer_code) != ''
            ) u
            WHERE u.code IS NOT NULL AND u.code != ''
            """
        )
    )
    for table in (
        "brand_buyer_maps",
        "buyer_price_lists",
        "color_swatch_recipes",
        "fluorescent_color_masters",
    ):
        conn.execute(
            sa.text(
                f"UPDATE {table} SET buyer_code = UPPER(TRIM(buyer_code)) "
                f"WHERE buyer_code IS NOT NULL AND TRIM(buyer_code) != ''"
            )
        )


def upgrade() -> None:
    conn = op.get_bind()
    _ensure_all_codes(conn)

    for fk_name, table in _FK_SPECS:
        if fk_name in _existing_fk_names(conn, table):
            continue
        op.create_foreign_key(
            fk_name,
            table,
            "buyer_codes",
            ["buyer_code"],
            ["code"],
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    conn = op.get_bind()
    for fk_name, table in reversed(_FK_SPECS):
        if fk_name in _existing_fk_names(conn, table):
            op.drop_constraint(fk_name, table, type_="foreignkey")
