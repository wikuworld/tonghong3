"""Kode wilayah administrasi Indonesia di master customer.

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-04-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "j0k1l2m3n4o5"
down_revision: Union[str, Sequence[str], None] = "i9j0k1l2m3n4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column("wilayah_province_code", sa.String(length=8), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("wilayah_regency_code", sa.String(length=16), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("wilayah_district_code", sa.String(length=24), nullable=True),
    )
    op.add_column(
        "customers",
        sa.Column("wilayah_village_code", sa.String(length=32), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("customers", "wilayah_village_code")
    op.drop_column("customers", "wilayah_district_code")
    op.drop_column("customers", "wilayah_regency_code")
    op.drop_column("customers", "wilayah_province_code")
