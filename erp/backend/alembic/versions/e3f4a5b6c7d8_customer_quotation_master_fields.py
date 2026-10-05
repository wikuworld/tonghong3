"""Field master customer ala legacy quotation: terms, currency, tax, ref, alamat 2, matriks kategori.

Revision ID: e3f4a5b6c7d8
Revises: c1d2e3f4a5b6
Create Date: 2026-04-23

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e3f4a5b6c7d8"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("customers", sa.Column("payment_terms", sa.String(length=120), nullable=True))
    op.add_column("customers", sa.Column("default_currency", sa.String(length=3), nullable=True))
    op.add_column("customers", sa.Column("tax_mode", sa.String(length=32), nullable=True))
    op.add_column("customers", sa.Column("reference_quotation", sa.String(length=100), nullable=True))
    op.add_column("customers", sa.Column("address_line2", sa.Text(), nullable=True))
    op.add_column("customers", sa.Column("category_discount_matrix", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("customers", "category_discount_matrix")
    op.drop_column("customers", "address_line2")
    op.drop_column("customers", "reference_quotation")
    op.drop_column("customers", "tax_mode")
    op.drop_column("customers", "default_currency")
    op.drop_column("customers", "payment_terms")
