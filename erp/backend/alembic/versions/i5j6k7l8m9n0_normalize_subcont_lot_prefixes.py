"""Normalisasi prefix lot subcont (QYC/PUR → KYC/PUK) dan placeholder legacy.

Revision ID: i5j6k7l8m9n0
Revises: h4i5j6k7l8m9
Create Date: 2026-06-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.exc import OperationalError, ProgrammingError

revision: str = "i5j6k7l8m9n0"
down_revision: Union[str, Sequence[str], None] = "h4i5j6k7l8m9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Skip bila skema belum punya kolom yang dibutuhkan layanan normalisasi.

    Migrasi ini memakai ORM/service yang mengasumsikan kolom lanjutan
    (mis. po_customer_ref_norm). Pada upgrade fresh linear, kolom itu
    belum tentu ada di titik revisi ini — jangan gagalkan seluruh chain.
    """
    conn = op.get_bind()
    cols = {c["name"] for c in sa.inspect(conn).get_columns("po_headers")}
    if "po_customer_ref_norm" not in cols:
        return

    from app.db import SessionLocal
    from app.services.lot_number_normalize import normalize_lot_references

    db = SessionLocal()
    try:
        normalize_lot_references(db, dry_run=False, clear_legacy_placeholders=True)
    except (OperationalError, ProgrammingError):
        db.rollback()
    finally:
        db.close()


def downgrade() -> None:
    # Data migration — tidak di-rollback otomatis.
    pass
