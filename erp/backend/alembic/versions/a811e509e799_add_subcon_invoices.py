"""add_subcon_invoices

Revision ID: a811e509e799
Revises: 71e9adeb2b81
Create Date: 2026-04-15 21:39:44.375269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a811e509e799'
down_revision: Union[str, Sequence[str], None] = '71e9adeb2b81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'subcon_invoices',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('po_id', sa.BigInteger(), nullable=False),
        sa.Column('invoice_type', sa.String(length=20), nullable=False),
        sa.Column('invoice_number', sa.String(length=100), nullable=True),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['po_id'], ['po_headers.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('subcon_invoices')
