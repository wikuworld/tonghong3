"""Add color_standard to po_details for marketing line (color standart)."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "b2c3d4e5f6a8"
down_revision = "z1a2b3c4d5e6"
branch_labels = None
depends_on = None


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        cols = insp.get_columns(table_name)
    except Exception:
        return False
    return any(c.get("name") == column_name for c in cols)


def upgrade() -> None:
    if not _has_column("po_details", "color_standard"):
        op.add_column(
            "po_details",
            sa.Column("color_standard", sa.String(length=255), nullable=True),
        )


def downgrade() -> None:
    if _has_column("po_details", "color_standard"):
        op.drop_column("po_details", "color_standard")
