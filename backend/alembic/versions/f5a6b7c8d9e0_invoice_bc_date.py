"""add bc_date on invoices for outstanding BC document date

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-09-11
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f5a6b7c8d9e0"
down_revision = "e4f5a6b7c8d9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("invoices", sa.Column("bc_date", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("invoices", "bc_date")
