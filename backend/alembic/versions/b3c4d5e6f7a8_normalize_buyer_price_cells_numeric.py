"""Normalize buyer price addon cells into numeric JSON values.

Revision ID: b3c4d5e6f7a8
Revises: a2b3c4d5e6f7
Create Date: 2026-04-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "b3c4d5e6f7a8"
down_revision: Union[str, Sequence[str], None] = "a2b3c4d5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PRICE_KEYS = {
    "COLOR WHITE",
    "COLOR BLACK",
    "FLOURASENT",
    "METALIC",
    "EMBOSS",
    "SPESIAL EMBOSS",
}


def _to_numeric(value):
    if value is None:
        return ""
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return ""
    else:
        raw = value
    try:
        return float(raw)
    except (TypeError, ValueError):
        return value


def upgrade() -> None:
    bind = op.get_bind()
    table = sa.table(
        "buyer_price_sheet_rows",
        sa.column("id", sa.BigInteger),
        sa.column("cells", sa.JSON),
    )
    rows = bind.execute(sa.select(table.c.id, table.c.cells)).all()
    for row_id, cells in rows:
        if not isinstance(cells, dict):
            continue
        updated = False
        new_cells = dict(cells)
        for key, val in list(new_cells.items()):
            if str(key).strip().upper() not in PRICE_KEYS:
                continue
            new_val = _to_numeric(val)
            if new_val != val:
                new_cells[key] = new_val
                updated = True
        if updated:
            bind.execute(
                sa.update(table).where(table.c.id == row_id).values(cells=new_cells)
            )


def downgrade() -> None:
    # Keep JSON numeric values; downgrade does not coerce back to string.
    return None
