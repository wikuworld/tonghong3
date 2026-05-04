"""Zona kirim (dalam kota / luar) untuk aturan cetak commercial invoice.

Revision ID: c1d2e3f4a5b6
Revises: 40fd71aad97c
Create Date: 2026-04-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, Sequence[str], None] = "40fd71aad97c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "delivery_headers",
        sa.Column("delivery_zone", sa.String(length=16), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("delivery_headers", "delivery_zone")
