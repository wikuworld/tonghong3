"""Kolom tambahan master customer (PIC, email, lokasi, NPWP, catatan).

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-04-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "i9j0k1l2m3n4"
down_revision: Union[str, Sequence[str], None] = "h8i9j0k1l2m3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("customers", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column(
        "customers", sa.Column("contact_person", sa.String(length=255), nullable=True)
    )
    op.add_column("customers", sa.Column("country", sa.String(length=100), nullable=True))
    op.add_column("customers", sa.Column("city", sa.String(length=120), nullable=True))
    op.add_column("customers", sa.Column("tax_id", sa.String(length=32), nullable=True))
    op.add_column("customers", sa.Column("remark", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("customers", "remark")
    op.drop_column("customers", "tax_id")
    op.drop_column("customers", "city")
    op.drop_column("customers", "country")
    op.drop_column("customers", "contact_person")
    op.drop_column("customers", "email")
