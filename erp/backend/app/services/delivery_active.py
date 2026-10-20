"""Filter delivery header yang masih aktif (bukan soft-delete / legacy cancelled)."""

from __future__ import annotations

from sqlalchemy import and_, func

from app.models import DeliveryHeader


def delivery_header_is_active_clause():
    """SQLAlchemy clause: header belum soft-delete dan status bukan cancelled legacy."""
    status = func.lower(func.trim(func.coalesce(DeliveryHeader.status, "")))
    return and_(
        DeliveryHeader.is_deleted.is_(False),
        status.notin_(("cancelled", "canceled")),
    )


def delivery_header_is_deleted(row: DeliveryHeader | None) -> bool:
    if row is None:
        return False
    if bool(getattr(row, "is_deleted", False)):
        return True
    return (getattr(row, "status", None) or "").strip().lower() in ("cancelled", "canceled")
