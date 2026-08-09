"""Issue stok kimia/RP dari MRP → potong material_stocks ERP (buku finansial)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import MaterialStock, RawMaterial, Warehouse
from app.services.audit import log_change


@dataclass
class StockIssueResult:
    material_id: int
    warehouse_id: int
    qty: Decimal
    stock_after: Decimal
    created_stock_row: bool


def _dec(v: Any) -> Decimal:
    if v is None:
        return Decimal("0")
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


def _resolve_warehouse(db: Session, warehouse_id: int | None = None) -> Warehouse:
    if warehouse_id:
        wh = db.get(Warehouse, int(warehouse_id))
        if not wh:
            raise HTTPException(status_code=400, detail=f"warehouse_id #{warehouse_id} tidak ada")
        return wh
    code = (settings.mrp_shopfloor_warehouse_code or "SHOPFLOOR").strip()
    wh = db.scalars(select(Warehouse).where(Warehouse.code == code).limit(1)).first()
    if wh:
        return wh
    # auto-create shopfloor warehouse for bridge
    wh = Warehouse(code=code, name="MRP Shopfloor", location="MRP", is_active=True)
    db.add(wh)
    db.flush()
    return wh


def ensure_raw_material(
    db: Session,
    *,
    code: str,
    name: str,
    material_type: str,
    unit: str = "kg",
) -> RawMaterial:
    code = (code or "").strip()
    if not code:
        raise HTTPException(status_code=400, detail="kode material ERP wajib")
    row = db.scalars(select(RawMaterial).where(RawMaterial.code == code).limit(1)).first()
    if row:
        return row
    row = RawMaterial(
        code=code,
        name=(name or code)[:255],
        material_type=material_type[:50],
        unit=(unit or "kg")[:20],
        is_active=True,
    )
    db.add(row)
    db.flush()
    return row


def issue_stock_from_mrp(
    db: Session,
    *,
    erp_material_id: int | None = None,
    material_code: str | None = None,
    material_name: str | None = None,
    material_type: str = "kimia",
    unit: str = "kg",
    qty: Decimal | float | int,
    warehouse_id: int | None = None,
    allow_negative: bool = True,
    mrp_ref: str | None = None,
    actor: str | None = None,
) -> StockIssueResult:
    qty_d = _dec(qty)
    if qty_d <= 0:
        raise HTTPException(status_code=400, detail="qty issue harus > 0")

    if erp_material_id:
        mat = db.get(RawMaterial, int(erp_material_id))
        if not mat:
            raise HTTPException(status_code=400, detail=f"raw_materials #{erp_material_id} tidak ada")
    else:
        mat = ensure_raw_material(
            db,
            code=material_code or f"MRP-{material_type.upper()}",
            name=material_name or material_code or "MRP material",
            material_type=material_type,
            unit=unit,
        )

    wh = _resolve_warehouse(db, warehouse_id)
    stock = db.scalars(
        select(MaterialStock).where(
            MaterialStock.material_id == mat.id,
            MaterialStock.warehouse_id == wh.id,
        )
    ).first()
    created = False
    if not stock:
        stock = MaterialStock(
            material_id=mat.id,
            warehouse_id=wh.id,
            current_stock=Decimal("0"),
            reserved_stock=Decimal("0"),
        )
        db.add(stock)
        db.flush()
        created = True

    after = _dec(stock.current_stock) - qty_d
    if after < 0 and not allow_negative:
        raise HTTPException(
            status_code=400,
            detail=f"Stok ERP tidak cukup ({stock.current_stock}) untuk issue {qty_d}",
        )
    stock.current_stock = after
    stock.updated_at = datetime.utcnow()

    log_change(
        db,
        entity_type="material_stock",
        entity_id=stock.id,
        action="mrp_stock_issue",
        after={
            "material_id": mat.id,
            "warehouse_id": wh.id,
            "qty": str(qty_d),
            "stock_after": str(after),
            "mrp_ref": mrp_ref,
        },
        actor=actor or "system",
    )
    db.flush()
    return StockIssueResult(
        material_id=int(mat.id),
        warehouse_id=int(wh.id),
        qty=qty_d,
        stock_after=after,
        created_stock_row=created,
    )
