"""add_ppic_assignment_po_detail_id

Revision ID: xxxx
Revises: 6f502d99d2c8
Create Date: 2026-04-15 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'xxxx'
down_revision: Union[str, Sequence[str], None] = '6f502d99d2c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'ppic_assignments',
        sa.Column('po_detail_id', sa.BigInteger(), nullable=True)
    )
    op.create_foreign_key(
        'fk_ppic_assignments_po_detail_id',
        'ppic_assignments',
        'po_details',
        ['po_detail_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('fk_ppic_assignments_po_detail_id', 'ppic_assignments', type_='foreignkey')
    op.drop_column('ppic_assignments', 'po_detail_id')