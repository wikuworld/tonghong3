"""po_details.color_family untuk kategori warna (harga sheet).

Revision ID: r7s8t9u0v1w2
Revises: p5q6r7s8t9u0
Create Date: 2026-04-09

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "r7s8t9u0v1w2"
down_revision: Union[str, None] = "p5q6r7s8t9u0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("po_details", sa.Column("color_family", sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column("po_details", "color_family")
