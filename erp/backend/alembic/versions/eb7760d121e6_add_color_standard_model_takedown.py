"""add_color_standard_model_takedown

Revision ID: eb7760d121e6
Revises: 541c0fae1605
Create Date: 2026-04-15 20:40:14.315344

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'eb7760d121e6'
down_revision: Union[str, Sequence[str], None] = '541c0fae1605'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('master_items', sa.Column('color_standard', sa.String(length=255), nullable=True))
    op.add_column('master_items', sa.Column('model_takedown', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('master_items', 'model_takedown')
    op.drop_column('master_items', 'color_standard')