"""add_inventory_tables

Revision ID: 34ff1a23de9b
Revises: 85aed59894d1
Create Date: 2026-04-16 03:45:21.108287

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '34ff1a23de9b'
down_revision: Union[str, Sequence[str], None] = '85aed59894d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('warehouses',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('code', sa.String(length=32), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('location', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    
    op.create_table('raw_materials',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('material_type', sa.String(length=50), nullable=False),
    sa.Column('unit', sa.String(length=20), nullable=False),
    sa.Column('default_warehouse_id', sa.BigInteger(), nullable=True),
    sa.Column('min_stock', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('cost_price', sa.Numeric(precision=14, scale=4), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['default_warehouse_id'], ['warehouses.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code', name='uq_raw_material_code')
    )
    
    op.create_table('material_receipts',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('receipt_number', sa.String(length=50), nullable=False),
    sa.Column('supplier_name', sa.String(length=255), nullable=True),
    sa.Column('receipt_date', sa.Date(), nullable=False),
    sa.Column('warehouse_id', sa.BigInteger(), nullable=False),
    sa.Column('total_amount', sa.Numeric(precision=14, scale=2), nullable=True),
    sa.Column('remark', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('receipt_number')
    )
    
    op.create_table('material_stocks',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('material_id', sa.BigInteger(), nullable=False),
    sa.Column('warehouse_id', sa.BigInteger(), nullable=False),
    sa.Column('current_stock', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('reserved_stock', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['material_id'], ['raw_materials.id'], ),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('material_id', 'warehouse_id', name='uq_material_warehouse')
    )
    
    op.create_table('material_receipt_details',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('receipt_id', sa.BigInteger(), nullable=False),
    sa.Column('material_id', sa.BigInteger(), nullable=False),
    sa.Column('quantity', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('unit_cost', sa.Numeric(precision=14, scale=4), nullable=True),
    sa.Column('total_cost', sa.Numeric(precision=14, scale=2), nullable=True),
    sa.Column('remark', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['material_id'], ['raw_materials.id'], ),
    sa.ForeignKeyConstraint(['receipt_id'], ['material_receipts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('material_receipt_details')
    op.drop_table('material_stocks')
    op.drop_table('material_receipts')
    op.drop_table('raw_materials')
    op.drop_table('warehouses')
