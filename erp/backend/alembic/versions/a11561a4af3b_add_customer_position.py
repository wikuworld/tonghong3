"""add_customer_position

Revision ID: a11561a4af3b
Revises: u0v1w2x3y4z5
Create Date: 2026-04-15 20:07:07.315686

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a11561a4af3b'
down_revision: Union[str, Sequence[str], None] = 'u0v1w2x3y4z5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('customers', sa.Column('position', sa.String(length=120), nullable=True))


def downgrade() -> None:
    op.drop_column('customers', 'position')
