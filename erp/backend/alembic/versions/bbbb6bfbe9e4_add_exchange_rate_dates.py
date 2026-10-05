"""add_exchange_rate_dates

Revision ID: bbbb6bfbe9e4
Revises: a11561a4af3b
Create Date: 2026-04-15 20:14:51.455582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bbbb6bfbe9e4'
down_revision: Union[str, Sequence[str], None] = 'a11561a4af3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('exchange_rates', sa.Column('valid_from', sa.Date(), nullable=True))
    op.add_column('exchange_rates', sa.Column('valid_to', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('exchange_rates', 'valid_to')
    op.drop_column('exchange_rates', 'valid_from')
