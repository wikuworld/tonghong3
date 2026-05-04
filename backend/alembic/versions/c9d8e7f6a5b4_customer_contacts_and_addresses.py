"""Add shipping/billing address fields for customers.

Revision ID: c9d8e7f6a5b4
Revises: a11561a4af3b
Create Date: 2026-04-23
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c9d8e7f6a5b4"
down_revision: Union[str, Sequence[str], None] = "a11561a4af3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("customers", sa.Column("shipping_address", sa.Text(), nullable=True))
    op.add_column("customers", sa.Column("billing_address", sa.Text(), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE customers
            SET shipping_address = address
            WHERE shipping_address IS NULL AND address IS NOT NULL
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE customers
            SET billing_address = COALESCE(bill_to, address)
            WHERE billing_address IS NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_column("customers", "billing_address")
    op.drop_column("customers", "shipping_address")
