"""Packing detail: roll, pcs, berat netto untuk INVPL / delivery."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "k2l3m4n5o6p7"
down_revision: Union[str, None] = "j1k2l3m4n5o6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("packing_details")}
    if "qty_roll" not in cols:
        op.add_column("packing_details", sa.Column("qty_roll", sa.Integer(), nullable=True))
    if "qty_pcs" not in cols:
        op.add_column("packing_details", sa.Column("qty_pcs", sa.Integer(), nullable=True))
    if "weight_net" not in cols:
        op.add_column("packing_details", sa.Column("weight_net", sa.Numeric(12, 3), nullable=True))


def downgrade() -> None:
    op.drop_column("packing_details", "weight_net")
    op.drop_column("packing_details", "qty_pcs")
    op.drop_column("packing_details", "qty_roll")
