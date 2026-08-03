"""Link delivery_headers to customs_declarations (BC 3.0).

Revision ID: v6g7h8i9j0k1
Revises: u5f6g7h8i9j0
Create Date: 2026-08-04

Hanya menambah FK delivery → AJU. Tidak drop pricing/exchange_rates.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "v6g7h8i9j0k1"
down_revision: Union[str, Sequence[str], None] = "u5f6g7h8i9j0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = set(insp.get_table_names())

    if "delivery_headers" not in tables or "customs_declarations" not in tables:
        return

    cols = {c["name"] for c in insp.get_columns("delivery_headers")}
    if "customs_declaration_id" in cols:
        return

    op.add_column(
        "delivery_headers",
        sa.Column("customs_declaration_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_delivery_headers_customs_declaration_id",
        "delivery_headers",
        "customs_declarations",
        ["customs_declaration_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_delivery_headers_customs_declaration_id",
        "delivery_headers",
        ["customs_declaration_id"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = set(insp.get_table_names())
    if "delivery_headers" not in tables:
        return

    cols = {c["name"] for c in insp.get_columns("delivery_headers")}
    if "customs_declaration_id" not in cols:
        return

    op.drop_index("ix_delivery_headers_customs_declaration_id", table_name="delivery_headers")
    op.drop_constraint(
        "fk_delivery_headers_customs_declaration_id", "delivery_headers", type_="foreignkey"
    )
    op.drop_column("delivery_headers", "customs_declaration_id")
