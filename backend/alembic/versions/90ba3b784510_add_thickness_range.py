"""add_thickness_range

Revision ID: 90ba3b784510
Revises: bbbb6bfbe9e4
Create Date: 2026-04-15 20:28:12.314657

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '90ba3b784510'
down_revision: Union[str, Sequence[str], None] = 'bbbb6bfbe9e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("master_items")}
    if "thickness_range" not in columns:
        op.add_column(
            "master_items",
            sa.Column("thickness_range", sa.String(length=80), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {col["name"] for col in inspector.get_columns("master_items")}
    if "thickness_range" in columns:
        op.drop_column("master_items", "thickness_range")
