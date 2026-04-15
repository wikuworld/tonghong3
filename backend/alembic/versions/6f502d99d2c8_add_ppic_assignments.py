"""add_ppic_assignments

Revision ID: 6f502d99d2c8
Revises: a811e509e799
Create Date: 2026-04-15 21:47:19.854677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '6f502d99d2c8'
down_revision: Union[str, Sequence[str], None] = 'a811e509e799'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('department', sa.String(length=50), nullable=True))
    op.create_table('ppic_assignments',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('po_id', sa.BigInteger(), nullable=False),
    sa.Column('ppic_user_id', sa.BigInteger(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('assigned_at', sa.TIMESTAMP(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['po_id'], ['po_headers.id'], ),
    sa.ForeignKeyConstraint(['ppic_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('ppic_assignments')
    op.drop_column('users', 'department')
