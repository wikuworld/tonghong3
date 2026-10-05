"""merge journal entries

Revision ID: 85aed59894d1
Revises: 5b2e04f5ef69, a1b2c3d4e5f7
Create Date: 2026-04-15 16:00:11.579547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85aed59894d1'
down_revision: Union[str, Sequence[str], None] = ('5b2e04f5ef69', 'a1b2c3d4e5f7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
