"""add_buyer_price_currency

Revision ID: 541c0fae1605
Revises: 90ba3b784510
Create Date: 2026-04-15 20:36:07.911526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '541c0fae1605'
down_revision: Union[str, Sequence[str], None] = '90ba3b784510'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('buyer_price_lists', sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'))


def downgrade() -> None:
    op.drop_column('buyer_price_lists', 'currency')
