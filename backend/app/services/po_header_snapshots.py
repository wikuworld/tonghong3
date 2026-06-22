"""Snapshot brand/customer pada header PO (denormalisasi untuk list & laporan)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models import Brand, Customer, PoHeader

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def apply_header_snapshots(db: Session, data: dict, *, force: bool = False) -> None:
    """Isi brand_name_snapshot / customer_name_snapshot / customer_code dari master jika perlu."""
    brand_id = data.get("brand_id")
    if brand_id and (force or not str(data.get("brand_name_snapshot") or "").strip()):
        brand = db.get(Brand, brand_id)
        if brand:
            data["brand_name_snapshot"] = (brand.name or brand.code or "").strip() or None

    customer_id = data.get("customer_id")
    if customer_id:
        cust = db.get(Customer, customer_id)
        if cust:
            if force or not str(data.get("customer_name_snapshot") or "").strip():
                data["customer_name_snapshot"] = (cust.name or "").strip() or None
            if force or not str(data.get("customer_code") or "").strip():
                data["customer_code"] = (cust.code or "").strip() or None


def resolve_header_snapshots_for_list(db: Session, items: list[PoHeader]) -> None:
    """Fallback tampilan list: isi snapshot kosong dari FK tanpa menulis DB."""
    if not items:
        return

    brand_ids = {
        p.brand_id
        for p in items
        if p.brand_id and not str(p.brand_name_snapshot or "").strip()
    }
    customer_ids = {
        p.customer_id
        for p in items
        if p.customer_id
        and (not str(p.customer_name_snapshot or "").strip() or not str(p.customer_code or "").strip())
    }

    brand_map: dict[int, str] = {}
    if brand_ids:
        for brand in db.scalars(select(Brand).where(Brand.id.in_(brand_ids))).all():
            brand_map[brand.id] = (brand.name or brand.code or "").strip()

    customer_map: dict[int, Customer] = {}
    if customer_ids:
        for cust in db.scalars(select(Customer).where(Customer.id.in_(customer_ids))).all():
            customer_map[cust.id] = cust

    for po in items:
        if po.brand_id and not str(po.brand_name_snapshot or "").strip():
            po.brand_name_snapshot = brand_map.get(po.brand_id)
        if po.customer_id and po.customer_id in customer_map:
            cust = customer_map[po.customer_id]
            if not str(po.customer_name_snapshot or "").strip():
                po.customer_name_snapshot = (cust.name or "").strip() or None
            if not str(po.customer_code or "").strip():
                po.customer_code = (cust.code or "").strip() or None
