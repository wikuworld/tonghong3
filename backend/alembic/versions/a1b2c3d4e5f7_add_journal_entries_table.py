"""add_journal_entries_table

Revision ID: a1b2c3d4e5f7
Revises: 6f502d99d2c8
Create Date: 2026-04-15 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f7'
down_revision: Union[str, Sequence[str], None] = '6f502d99d2c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'journal_entries',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('transaction_id', sa.BigInteger(), nullable=False),
        sa.Column('coa_code', sa.String(length=20), nullable=False),
        sa.Column('coa_name', sa.String(length=100), nullable=False),
        sa.Column('debit', sa.Numeric(precision=14, scale=2), nullable=False, server_default='0'),
        sa.Column('credit', sa.Numeric(precision=14, scale=2), nullable=False, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('entry_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('journal_entries')
