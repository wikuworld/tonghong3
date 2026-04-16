"""merge invoice FK heads

Revision ID: 40fd71aad97c
Revises: 34ff1a23de9b, xxxx_invoice_master_fk
Create Date: 2026-04-16 15:26:24.142142

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40fd71aad97c'
down_revision: Union[str, Sequence[str], None] = ('34ff1a23de9b', 'xxxx_invoice_master_fk')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
