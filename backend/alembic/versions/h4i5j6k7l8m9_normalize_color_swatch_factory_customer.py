"""Sinkronkan customer_id & normalisasi factory_key color swatch ke master pabrik.

Revision ID: h4i5j6k7l8m9
Revises: z9y8x7w6v5u4
Create Date: 2026-06-09

"""

from typing import Sequence, Union

from alembic import op

revision: str = "h4i5j6k7l8m9"
down_revision: Union[str, Sequence[str], None] = "z9y8x7w6v5u4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from app.db import SessionLocal
    from app.services.swatch_factory_map import normalize_color_swatch_factory_links

    db = SessionLocal()
    try:
        normalize_color_swatch_factory_links(db, normalize_factory_keys=True, dry_run=False)
    finally:
        db.close()


def downgrade() -> None:
    # Data migration — tidak di-rollback otomatis.
    pass
