"""Buyer price lists: brand_id and multiple periods per buyer.

Revision ID: g1h2i3j4k5l6
Revises: f8c9d0e1f2a3
Create Date: 2026-10-13
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "g1h2i3j4k5l6"
down_revision: Union[str, Sequence[str], None] = "f8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _buyer_code_foreign_keys(bind):
    found = []
    for fk in sa.inspect(bind).get_foreign_keys("buyer_price_lists"):
        if list(fk.get("constrained_columns") or []) == ["buyer_code"] and fk.get("name"):
            found.append(fk)
    return found


def _recreate_foreign_key(fk) -> None:
    ondelete = (fk.get("options") or {}).get("ondelete")
    op.create_foreign_key(
        fk["name"],
        "buyer_price_lists",
        fk["referred_table"],
        list(fk.get("constrained_columns") or []),
        list(fk.get("referred_columns") or []),
        ondelete=ondelete,
    )


def _drop_buyer_code_unique(bind) -> None:
    """Lepas unique buyer_code tanpa menjatuhkan FK yang masih memakai indeks itu."""
    fks = _buyer_code_foreign_keys(bind)
    for fk in fks:
        op.drop_constraint(fk["name"], "buyer_price_lists", type_="foreignkey")

    insp = sa.inspect(bind)
    for uc in insp.get_unique_constraints("buyer_price_lists"):
        cols = list(uc.get("column_names") or [])
        name = uc.get("name")
        if cols == ["buyer_code"] and name:
            op.drop_constraint(name, "buyer_price_lists", type_="unique")
    for ix in sa.inspect(bind).get_indexes("buyer_price_lists"):
        if ix.get("unique") and list(ix.get("column_names") or []) == ["buyer_code"] and ix.get("name"):
            op.drop_index(ix["name"], table_name="buyer_price_lists")
    names = {ix.get("name") for ix in sa.inspect(bind).get_indexes("buyer_price_lists")}
    if "ix_buyer_price_lists_buyer_code" not in names:
        op.create_index("ix_buyer_price_lists_buyer_code", "buyer_price_lists", ["buyer_code"])

    for fk in fks:
        _recreate_foreign_key(fk)


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("buyer_price_lists")}
    if "brand_id" not in cols:
        op.add_column("buyer_price_lists", sa.Column("brand_id", sa.BigInteger(), nullable=True))
        op.create_foreign_key(
            "fk_buyer_price_lists_brand",
            "buyer_price_lists",
            "brands",
            ["brand_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        op.create_index("ix_buyer_price_lists_brand_id", "buyer_price_lists", ["brand_id"])

    _drop_buyer_code_unique(bind)

    rows = bind.execute(
        sa.text(
            """
            SELECT buyer_code, MIN(brand_id) AS brand_id
            FROM brand_buyer_maps
            GROUP BY buyer_code
            HAVING COUNT(*) = 1
            """
        )
    ).fetchall()
    for buyer_code, brand_id in rows:
        bind.execute(
            sa.text(
                """
                UPDATE buyer_price_lists
                SET brand_id = :brand_id
                WHERE buyer_code = :buyer_code AND brand_id IS NULL
                """
            ),
            {"brand_id": brand_id, "buyer_code": buyer_code},
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    fks = {fk.get("name") for fk in insp.get_foreign_keys("buyer_price_lists")}
    if "fk_buyer_price_lists_brand" in fks:
        op.drop_constraint("fk_buyer_price_lists_brand", "buyer_price_lists", type_="foreignkey")
    indexes = {ix.get("name") for ix in insp.get_indexes("buyer_price_lists")}
    if "ix_buyer_price_lists_brand_id" in indexes:
        op.drop_index("ix_buyer_price_lists_brand_id", table_name="buyer_price_lists")
    cols = {c["name"] for c in insp.get_columns("buyer_price_lists")}
    if "brand_id" in cols:
        op.drop_column("buyer_price_lists", "brand_id")
    op.create_unique_constraint(
        "uq_buyer_price_lists_buyer_code",
        "buyer_price_lists",
        ["buyer_code"],
    )
