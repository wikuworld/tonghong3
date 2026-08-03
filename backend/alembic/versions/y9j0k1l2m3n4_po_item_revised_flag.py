"""Flag revisi item pada po_headers (edit/hapus baris).

Revision ID: y9j0k1l2m3n4
Revises: x8i9j0k1l2m3
Create Date: 2026-08-04
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "y9j0k1l2m3n4"
down_revision: Union[str, Sequence[str], None] = "x8i9j0k1l2m3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = {c["name"] for c in insp.get_columns("po_headers")}
    if "item_revised_at" not in cols:
        op.add_column(
            "po_headers",
            sa.Column("item_revised_at", sa.DateTime(), nullable=True),
        )
    if "item_revised_has_update" not in cols:
        op.add_column(
            "po_headers",
            sa.Column(
                "item_revised_has_update",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
    if "item_revised_has_delete" not in cols:
        op.add_column(
            "po_headers",
            sa.Column(
                "item_revised_has_delete",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
    indexes = {i["name"] for i in insp.get_indexes("po_headers")}
    if "ix_po_headers_item_revised_at" not in indexes:
        op.create_index(
            "ix_po_headers_item_revised_at",
            "po_headers",
            ["item_revised_at"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    indexes = {i["name"] for i in insp.get_indexes("po_headers")}
    if "ix_po_headers_item_revised_at" in indexes:
        op.drop_index("ix_po_headers_item_revised_at", table_name="po_headers")
    cols = {c["name"] for c in insp.get_columns("po_headers")}
    if "item_revised_has_delete" in cols:
        op.drop_column("po_headers", "item_revised_has_delete")
    if "item_revised_has_update" in cols:
        op.drop_column("po_headers", "item_revised_has_update")
    if "item_revised_at" in cols:
        op.drop_column("po_headers", "item_revised_at")
