"""add_accounting_mappings

Revision ID: 6eb55b8ac8c3
Revises: 3b95ed7665f2
Create Date: 2026-04-15 22:08:54.724045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6eb55b8ac8c3'
down_revision: Union[str, Sequence[str], None] = '3b95ed7665f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('accounting_mappings',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('transaction_type', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=True),
    sa.Column('coa_code', sa.String(length=20), nullable=False),
    sa.Column('coa_name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.execute("""
        INSERT INTO accounting_mappings (transaction_type, status, coa_code, coa_name, description, is_active)
        VALUES
            ('po_created', 'draft', '1-1100', 'Account Receivable', 'Piutang usaha saat PO dibuat', 1),
            ('invoice', 'sent', '1-1200', 'AR - Export', 'Piutang ekspor saat invoice dikirim', 1),
            ('invoice', 'paid', '1-1300', 'Cash/Bank', 'Kas/bank saat invoice dilunasi', 1),
            ('payment', NULL, '2-1000', 'Cost of Goods Sold', 'Harga pokok penjualan', 1)
    """)


def downgrade() -> None:
    op.drop_table('accounting_mappings')
