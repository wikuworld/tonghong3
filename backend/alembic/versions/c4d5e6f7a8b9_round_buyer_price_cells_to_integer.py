"""Round buyer price cells to integer values.

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-04-23
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, Sequence[str], None] = "b3c4d5e6f7a8"
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


def _to_int(value):
    if value in (None, ""):
        return ""
    try:
        return int(round(float(value)))
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
        new_cells = dict(cells)
        changed = False
        for key, val in list(new_cells.items()):
            if str(key).strip().upper() not in PRICE_KEYS:
                continue
            new_val = _to_int(val)
            if new_val != val:
                new_cells[key] = new_val
                changed = True
        if changed:
            bind.execute(sa.update(table).where(table.c.id == row_id).values(cells=new_cells))


def downgrade() -> None:
    return None
