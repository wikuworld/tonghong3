"""Drop unused source_label from buyer price lists.

Revision ID: a2b3c4d5e6f7
Revises: f9e8d7c6b5a4
Create Date: 2026-04-23
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, Sequence[str], None] = "f9e8d7c6b5a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("buyer_price_lists") as batch_op:
        batch_op.drop_column("source_label")


def downgrade() -> None:
    with op.batch_alter_table("buyer_price_lists") as batch_op:
        batch_op.add_column(sa.Column("source_label", sa.String(length=255), nullable=True))
