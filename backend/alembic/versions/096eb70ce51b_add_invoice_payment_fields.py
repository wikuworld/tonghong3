"""add_invoice_payment_fields

Revision ID: 096eb70ce51b
Revises: eb7760d121e6
Create Date: 2026-04-15 20:44:40.713913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = '096eb70ce51b'
down_revision: Union[str, Sequence[str], None] = 'eb7760d121e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('invoices', sa.Column('payment_date', sa.Date(), nullable=True))
    op.add_column('invoices', sa.Column('payment_bank_account', sa.String(length=100), nullable=True))
    op.add_column('invoices', sa.Column('payment_proof_url', sa.String(length=500), nullable=True))
    op.add_column('invoices', sa.Column('payment_status', sa.String(length=20), nullable=False, server_default='unpaid'))


def downgrade() -> None:
    op.drop_column('invoices', 'payment_status')
    op.drop_column('invoices', 'payment_proof_url')
    op.drop_column('invoices', 'payment_bank_account')
    op.drop_column('invoices', 'payment_date')
