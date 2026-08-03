"""Seed Master Item METAL SHIFT LEATHER for Color Swatch CSV coverage.

Revision ID: q1r2s3t4u5v6
Revises: p8q9r0s1t2u3
Create Date: 2026-08-03
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "q1r2s3t4u5v6"
down_revision: Union[str, Sequence[str], None] = "m0a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ITEM_CODE = "FG06105"
MATERIAL_NAME = "METAL SHIFT LEATHER"


def upgrade() -> None:
    conn = op.get_bind()
    exists = conn.execute(
        sa.text(
            """
            SELECT 1 FROM master_items
            WHERE item_code = :item_code
               OR UPPER(TRIM(material_name)) = :material_name
            LIMIT 1
            """
        ),
        {"item_code": ITEM_CODE, "material_name": MATERIAL_NAME},
    ).first()
    if exists:
        return
    conn.execute(
        sa.text(
            """
            INSERT INTO master_items (
              item_code, material_name, category, thickness_range, emboss
            ) VALUES (
              :item_code, :material_name, 'PU', '1.2-1.4', 'STANDARD EMBOSS'
            )
            """
        ),
        {"item_code": ITEM_CODE, "material_name": MATERIAL_NAME},
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text("DELETE FROM master_items WHERE item_code = :item_code"),
        {"item_code": ITEM_CODE},
    )
