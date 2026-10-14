"""cancel fields on delivery and void fields on invoice

Revision ID: f8c9d0e1f2a3
Revises: e7i8n9v0u1n2
Create Date: 2026-10-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "f8c9d0e1f2a3"
down_revision = "e7i8n9v0u1n2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("delivery_headers", sa.Column("cancel_reason", sa.Text(), nullable=True))
    op.add_column("delivery_headers", sa.Column("cancelled_at", sa.DateTime(), nullable=True))
    op.add_column("delivery_headers", sa.Column("cancelled_by", sa.String(length=100), nullable=True))
    op.add_column("invoices", sa.Column("voided_at", sa.DateTime(), nullable=True))
    op.add_column("invoices", sa.Column("void_reason", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("invoices", "void_reason")
    op.drop_column("invoices", "voided_at")
    op.drop_column("delivery_headers", "cancelled_by")
    op.drop_column("delivery_headers", "cancelled_at")
    op.drop_column("delivery_headers", "cancel_reason")
