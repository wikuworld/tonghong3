"""add_customer_brand_mappings

Revision ID: 71e9adeb2b81
Revises: db95756201e6
Create Date: 2026-04-15 21:30:40.873559

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '71e9adeb2b81'
down_revision: Union[str, Sequence[str], None] = 'db95756201e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('brand_constraints',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('customer_id', sa.BigInteger(), nullable=False),
    sa.Column('allowed_brand_ids', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('customer_brand_mappings',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('customer_id', sa.BigInteger(), nullable=False),
    sa.Column('brand_id', sa.BigInteger(), nullable=False),
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['brand_id'], ['brands.id'], ),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('customer_id', 'brand_id', name='uq_customer_brand')
    )


def downgrade() -> None:
    op.drop_table('customer_brand_mappings')
    op.drop_table('brand_constraints')
