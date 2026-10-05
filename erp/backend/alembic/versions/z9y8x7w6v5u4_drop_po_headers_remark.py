"""Hapus kolom remark pada po_headers (catatan hanya di level baris detail).

Revision ID: z9y8x7w6v5u4
Revises: g3h4i5j6k7l8
Create Date: 2026-06-05

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "z9y8x7w6v5u4"
down_revision: Union[str, Sequence[str], None] = "g3h4i5j6k7l8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("po_headers", "remark")


def downgrade() -> None:
    op.add_column("po_headers", sa.Column("remark", sa.Text(), nullable=True))
