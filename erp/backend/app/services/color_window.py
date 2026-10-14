"""Master Color Window — normalisasi field."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Brand


def normalize_color_window_fields(data: dict[str, Any]) -> dict[str, Any]:
    color_code = (data.get("color_code") or "").strip()
    color_name = (data.get("color_name") or "").strip()
    brand_code = (data.get("brand_code") or "").strip().upper()
    remark = (data.get("remark") or "").strip() or None
    if not color_code or not color_name or not brand_code:
        raise ValueError("color_code, color_name, dan brand wajib diisi")
    return {
        "color_code": color_code,
        "color_name": color_name,
        "brand_code": brand_code,
        "remark": remark,
    }


def ensure_brand_code(db: Session, brand_code: str) -> str:
    code = (brand_code or "").strip().upper()
    row = db.scalars(select(Brand).where(Brand.code == code)).first()
    if not row:
        raise ValueError(f"Brand '{code}' tidak ditemukan di master Brand")
    return code
