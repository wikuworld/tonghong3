"""add_customer_special_prices

Revision ID: db95756201e6
Revises: 8bce02b11a07
Create Date: 2026-04-15 21:14:54.272399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'db95756201e6'
down_revision: Union[str, Sequence[str], None] = '8bce02b11a07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('customer_special_prices',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('customer_id', sa.BigInteger(), nullable=False),
    sa.Column('buyer_code', sa.String(length=32), nullable=False),
    sa.Column('material_pattern', sa.String(length=255), nullable=True),
    sa.Column('price_override', sa.Numeric(precision=14, scale=4), nullable=True),
    sa.Column('discount_percentage', sa.Numeric(precision=5, scale=2), nullable=True),
    sa.Column('valid_from', sa.Date(), nullable=True),
    sa.Column('valid_to', sa.Date(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('customer_special_prices')
