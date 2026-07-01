"""Normalisasi prefix lot subcont (QYC/PUR → KYC/PUK) dan placeholder legacy.

Revision ID: i5j6k7l8m9n0
Revises: h4i5j6k7l8m9
Create Date: 2026-06-22
"""

from typing import Sequence, Union

from alembic import op

revision: str = "i5j6k7l8m9n0"
down_revision: Union[str, Sequence[str], None] = "h4i5j6k7l8m9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from app.db import SessionLocal
    from app.services.lot_number_normalize import normalize_lot_references

    db = SessionLocal()
    try:
        normalize_lot_references(db, dry_run=False, clear_legacy_placeholders=True)
    finally:
        db.close()


def downgrade() -> None:
    # Data migration — tidak di-rollback otomatis.
    pass
