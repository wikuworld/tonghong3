"""add_special_prices

Revision ID: 8bce02b11a07
Revises: 096eb70ce51b
Create Date: 2026-04-15 21:06:48.294031

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '8bce02b11a07'
down_revision: Union[str, Sequence[str], None] = '096eb70ce51b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('special_prices',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('buyer_code', sa.String(length=32), nullable=False),
    sa.Column('material_pattern', sa.String(length=255), nullable=True),
    sa.Column('emboss_pattern', sa.String(length=100), nullable=True),
    sa.Column('color_pattern', sa.String(length=100), nullable=True),
    sa.Column('discount_type', sa.String(length=20), nullable=False),
    sa.Column('discount_value', sa.Numeric(precision=14, scale=4), nullable=False),
    sa.Column('valid_from', sa.Date(), nullable=True),
    sa.Column('valid_to', sa.Date(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('special_prices')
