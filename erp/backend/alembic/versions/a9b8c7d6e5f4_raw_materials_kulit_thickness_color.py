"""raw_materials: thickness & color for kulit catalog

Revision ID: a9b8c7d6e5f4
Revises: j9k0l1m2n3o4
Create Date: 2026-09-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a9b8c7d6e5f4"
down_revision: Union[str, Sequence[str], None] = "j9k0l1m2n3o4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("raw_materials", sa.Column("thickness", sa.String(length=80), nullable=True))
    op.add_column("raw_materials", sa.Column("color", sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column("raw_materials", "color")
    op.drop_column("raw_materials", "thickness")
