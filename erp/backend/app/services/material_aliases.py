"""Material alias resolve (master integrity F2)."""

from __future__ import annotations

import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import MasterItem, MaterialAlias


def _norm_key(name: str | None) -> str:
    return re.sub(r"\s+", " ", (name or "").strip()).upper()


def resolve_canonical_material_name(db: Session, material_name: str | None) -> str:
    raw = (material_name or "").strip()
    if not raw:
        return ""
    key = _norm_key(raw)
    for alias in db.scalars(select(MaterialAlias).where(MaterialAlias.is_active.is_(True))).all():
        if _norm_key(alias.alias_name) == key:
            return alias.canonical_name
    return raw


def material_missing_in_master_items(db: Session, material_name: str | None) -> bool:
    """True if resolved name tidak ada exact match di master_items."""
    name = resolve_canonical_material_name(db, material_name)
    if not name:
        return True
    found = db.scalars(
        select(MasterItem.id).where(
            func.upper(func.trim(MasterItem.material_name)) == name.strip().upper()
        ).limit(1)
    ).first()
    return found is None
