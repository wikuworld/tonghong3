"""Normalize legacy MKT stage back_to_mkt → in_outstanding.

Revision ID: x8i9j0k1l2m3
Revises: w7h8i9j0k1l2
Create Date: 2026-08-04

back_to_mkt digabung ke in_outstanding (tahap redundant).
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "x8i9j0k1l2m3"
down_revision: Union[str, Sequence[str], None] = "w7h8i9j0k1l2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "po_headers" not in set(insp.get_table_names()):
        return
    cols = {c["name"] for c in insp.get_columns("po_headers")}
    if "mkt_workflow_stage" not in cols:
        return
    op.execute(
        sa.text(
            "UPDATE po_headers "
            "SET mkt_workflow_stage = 'in_outstanding', "
            "    mkt_workflow_updated_at = UTC_TIMESTAMP() "
            "WHERE mkt_workflow_stage = 'back_to_mkt'"
        )
    )


def downgrade() -> None:
    # Tidak mengembalikan back_to_mkt — data sudah dinormalisasi.
    pass
