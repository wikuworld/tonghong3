"""Alur MKT sesuai flowchart: tahapan PO, rekap, SJ/INVPL print flags.

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-04-08

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "h8i9j0k1l2m3"
down_revision: Union[str, Sequence[str], None] = "g7h8i9j0k1l2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "po_headers",
        sa.Column(
            "mkt_workflow_stage",
            sa.String(length=48),
            nullable=False,
            server_default="input_system",
        ),
    )
    op.add_column(
        "po_headers",
        sa.Column("mkt_workflow_updated_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "po_headers",
        sa.Column("rekap_printed_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "po_headers",
        sa.Column("material_followup_remark", sa.Text(), nullable=True),
    )
    op.add_column(
        "po_headers",
        sa.Column(
            "material_followup_done",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.alter_column("po_headers", "mkt_workflow_stage", server_default=None)

    op.add_column(
        "delivery_headers",
        sa.Column("surat_jalan_printed_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "packing_headers",
        sa.Column("invpl_printed_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("packing_headers", "invpl_printed_at")
    op.drop_column("delivery_headers", "surat_jalan_printed_at")
    op.drop_column("po_headers", "material_followup_done")
    op.drop_column("po_headers", "material_followup_remark")
    op.drop_column("po_headers", "rekap_printed_at")
    op.drop_column("po_headers", "mkt_workflow_updated_at")
    op.drop_column("po_headers", "mkt_workflow_stage")
