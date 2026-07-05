"""po_details.marketing_outstanding_remark untuk catatan marketing di modul outstanding.

Revision ID: s8t9u0v1w2x3
Revises: r7s8t9u0v1w2
Create Date: 2026-04-09

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "s8t9u0v1w2x3"
down_revision: Union[str, None] = "r7s8t9u0v1w2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "po_details",
        sa.Column("marketing_outstanding_remark", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("po_details", "marketing_outstanding_remark")
