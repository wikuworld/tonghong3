"""merge heads

Revision ID: 5b2e04f5ef69
Revises: xxxx, 6eb55b8ac8c3
Create Date: 2026-04-15 15:49:31.626801

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5b2e04f5ef69'
down_revision: Union[str, Sequence[str], None] = ('xxxx', '6eb55b8ac8c3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
