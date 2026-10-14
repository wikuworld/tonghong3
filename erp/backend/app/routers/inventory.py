from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import (
    Warehouse,
    RawMaterial,
    MaterialStock,
    MaterialReceipt,
    MaterialReceiptDetail,
    InventoryUnitMaster,
)
from app.paging import apply_sort, page_dict, parse_page_params
from app.schemas import (
    WarehouseCreate,
    WarehouseUpdate,
    WarehouseOut,
    RawMaterialCreate,
    RawMaterialUpdate,
    RawMaterialOut,
    MaterialStockOut,
    MaterialReceiptCreate,
    MaterialReceiptUpdate,
    MaterialReceiptOut,
    InventoryUnitMasterCreate,
    InventoryUnitMasterUpdate,
    InventoryUnitMasterOut,
)
from app.routers.auth import get_current_user, require_roles, is_service_mrp

router = APIRouter(prefix="/inventory", tags=["inventory"])


_TYPE_ALIASES = {
    "kimia": "kimia",
    "chemical": "kimia",
    "rp": "rp",
    "material": "material_lain",
    "material_lain": "material_lain",
    "material-lain": "material_lain",
    "accessory": "material_lain",
    "kulit": "kulit",
    "leather": "kulit",
}


def _inventory_write_allowed(user) -> bool:
    return user.role == "admin" or is_service_mrp(user)


def require_inventory_write(user=Depends(get_current_user)):
    if not _inventory_write_allowed(user):
        raise HTTPException(status_code=403, detail="Akses ditolak (role)")
    return user


def _normalize_material_type(material_type: str | None) -> str:
    raw = (material_type or "").strip().lower()
    return _TYPE_ALIASES.get(raw, raw)


_UNIT_TYPE_ALIASES = {
    **{k: k for k in ("kulit", "kimia", "material_lain", "rp")},
    "leather": "kulit",
    "chemical": "kimia",
    "accessory": "material_lain",
    "accesoris": "material_lain",
    "aksesoris": "material_lain",
}


def _normalize_unit_material_type(material_type: str | None) -> str:
    raw = (material_type or "").strip().lower()
    return _UNIT_TYPE_ALIASES.get(raw, raw)


def _page_args(
    page: Optional[int],
    page_size: Optional[int],
    limit: Optional[int],
    offset: Optional[int],
    sort_by: Optional[str],
    sort_dir: Optional[str],
    *,
    default_page_size: int = 20,
):
    return parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir,
        default_page_size=default_page_size,
    )


# === WAREHOUSE ===
@router.get("/warehouses", response_model=list[WarehouseOut])
def list_warehouses(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return list(db.scalars(select(Warehouse).order_by(Warehouse.name)).all())


@router.get("/warehouses/page")
def list_warehouses_page(
    q: Optional[str] = Query(None),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="id|code|name"),
    sort_dir: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    params = _page_args(page, page_size, limit, offset, sort_by, sort_dir or "asc")
    stmt = select(Warehouse)
    count_stmt = select(func.count(Warehouse.id))
    if q and q.strip():
        like = f"%{q.strip()}%"
        where = or_(Warehouse.code.ilike(like), Warehouse.name.ilike(like))
        stmt = stmt.where(where)
        count_stmt = count_stmt.where(where)
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={"id": Warehouse.id, "code": Warehouse.code, "name": Warehouse.name},
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(Warehouse.name.asc(),),
    )
    items = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    return page_dict(items=items, total=total, params=params)


@router.post("/warehouses", response_model=WarehouseOut)
def create_warehouse(body: WarehouseCreate, db: Session = Depends(get_db), _user=Depends(require_roles("admin"))):
    existing = db.scalars(select(Warehouse).where(Warehouse.code == body.code)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Kode warehouse sudah ada")
    row = Warehouse(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/warehouses/{warehouse_id}", response_model=WarehouseOut)
def update_warehouse(warehouse_id: int, body: WarehouseUpdate, db: Session = Depends(get_db), _user=Depends(require_roles("admin"))):
    row = db.get(Warehouse, warehouse_id)
    if not row:
        raise HTTPException(status_code=404, detail="Warehouse tidak ditemukan")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/warehouses/{warehouse_id}")
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db), _user=Depends(require_roles("admin"))):
    row = db.get(Warehouse, warehouse_id)
    if not row:
        raise HTTPException(status_code=404, detail="Warehouse tidak ditemukan")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


# === RAW MATERIAL ===
@router.get("/materials", response_model=list[RawMaterialOut])
def list_materials(
    material_type: Optional[str] = Query(None, description="Filter: kimia|rp|kulit|material_lain"),
    code: Optional[str] = Query(None, description="Exact code match"),
    q: Optional[str] = Query(None, description="Search code/name"),
    active_only: bool = Query(True),
    limit: int = Query(2000, ge=1, le=5000),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    stmt = select(RawMaterial)
    if active_only:
        stmt = stmt.where(RawMaterial.is_active.is_(True))
    if material_type:
        stmt = stmt.where(RawMaterial.material_type == _normalize_material_type(material_type))
    if code and code.strip():
        stmt = stmt.where(RawMaterial.code == code.strip())
    if q and q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            (RawMaterial.code.ilike(like)) | (RawMaterial.name.ilike(like))
        )
    return list(db.scalars(stmt.order_by(RawMaterial.code).limit(limit)).all())


@router.get("/materials/page")
def list_materials_page(
    material_type: Optional[str] = Query(None),
    code: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    active_only: bool = Query(True),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="id|code|name|material_type"),
    sort_dir: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    params = _page_args(page, page_size, limit, offset, sort_by, sort_dir or "asc")
    stmt = select(RawMaterial)
    count_stmt = select(func.count(RawMaterial.id))
    if active_only:
        stmt = stmt.where(RawMaterial.is_active.is_(True))
        count_stmt = count_stmt.where(RawMaterial.is_active.is_(True))
    if material_type:
        mt = _normalize_material_type(material_type)
        stmt = stmt.where(RawMaterial.material_type == mt)
        count_stmt = count_stmt.where(RawMaterial.material_type == mt)
    if code and code.strip():
        stmt = stmt.where(RawMaterial.code == code.strip())
        count_stmt = count_stmt.where(RawMaterial.code == code.strip())
    if q and q.strip():
        like = f"%{q.strip()}%"
        where = or_(RawMaterial.code.ilike(like), RawMaterial.name.ilike(like))
        stmt = stmt.where(where)
        count_stmt = count_stmt.where(where)
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "id": RawMaterial.id,
            "code": RawMaterial.code,
            "name": RawMaterial.name,
            "material_type": RawMaterial.material_type,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(RawMaterial.code.asc(),),
    )
    items = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    return page_dict(items=items, total=total, params=params)


@router.get("/materials/{material_id}", response_model=RawMaterialOut)
def get_material(material_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    row = db.get(RawMaterial, material_id)
    if not row:
        raise HTTPException(status_code=404, detail="Material tidak ditemukan")
    return row


class MaterialUpsertIn(BaseModel):
    code: str
    name: str
    material_type: str
    unit: str = "kg"
    is_active: bool = True


@router.post("/materials/upsert", response_model=RawMaterialOut)
def upsert_material(
    body: MaterialUpsertIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Upsert katalog raw material (admin atau service MRP untuk impor)."""
    if user.role != "admin" and not is_service_mrp(user):
        raise HTTPException(status_code=403, detail="Akses ditolak (role)")
    code = (body.code or "").strip()
    if not code:
        raise HTTPException(status_code=400, detail="code wajib")
    mt = _normalize_material_type(body.material_type)
    row = db.scalars(select(RawMaterial).where(RawMaterial.code == code).limit(1)).first()
    if row:
        row.name = (body.name or code)[:255]
        row.material_type = mt[:50]
        row.unit = (body.unit or "kg")[:20]
        row.is_active = bool(body.is_active)
    else:
        row = RawMaterial(
            code=code[:50],
            name=(body.name or code)[:255],
            material_type=mt[:50],
            unit=(body.unit or "kg")[:20],
            is_active=bool(body.is_active),
        )
        db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.post("/materials", response_model=RawMaterialOut)
def create_material(body: RawMaterialCreate, db: Session = Depends(get_db), _user=Depends(require_inventory_write)):
    existing = db.scalars(select(RawMaterial).where(RawMaterial.code == body.code)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Kode material sudah ada")
    data = body.model_dump()
    data["material_type"] = _normalize_material_type(data.get("material_type"))
    row = RawMaterial(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/materials/{material_id}", response_model=RawMaterialOut)
def update_material(
    material_id: int,
    body: RawMaterialUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_inventory_write),
):
    row = db.get(RawMaterial, material_id)
    if not row:
        raise HTTPException(status_code=404, detail="Material tidak ditemukan")
    for k, v in body.model_dump(exclude_unset=True).items():
        if k == "material_type" and v is not None:
            v = _normalize_material_type(v)
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


# === MASTER UNIT ===
@router.get("/units", response_model=list[InventoryUnitMasterOut])
def list_inventory_units(
    material_type: Optional[str] = Query(None, description="kulit|kimia|material_lain|rp"),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    stmt = select(InventoryUnitMaster)
    if active_only:
        stmt = stmt.where(InventoryUnitMaster.is_active.is_(True))
    if material_type and str(material_type).strip():
        mt = _normalize_unit_material_type(material_type)
        stmt = stmt.where(InventoryUnitMaster.material_type == mt)
    return list(
        db.scalars(
            stmt.order_by(InventoryUnitMaster.material_type.asc(), InventoryUnitMaster.unit.asc())
        ).all()
    )


@router.post("/units", response_model=InventoryUnitMasterOut)
def create_inventory_unit(
    body: InventoryUnitMasterCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_inventory_write),
):
    mt = _normalize_unit_material_type(body.material_type)
    if mt not in ("kulit", "kimia", "material_lain", "rp"):
        raise HTTPException(status_code=400, detail="Tipe harus kulit, kimia, material_lain, atau rp")
    unit = str(body.unit or "").strip()
    if not unit:
        raise HTTPException(status_code=400, detail="Unit wajib")
    existing = db.scalars(
        select(InventoryUnitMaster).where(
            InventoryUnitMaster.material_type == mt,
            InventoryUnitMaster.unit == unit,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Unit untuk tipe ini sudah ada")
    row = InventoryUnitMaster(material_type=mt, unit=unit[:50], is_active=bool(body.is_active))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/units/{unit_id}", response_model=InventoryUnitMasterOut)
def update_inventory_unit(
    unit_id: int,
    body: InventoryUnitMasterUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_inventory_write),
):
    row = db.get(InventoryUnitMaster, unit_id)
    if not row:
        raise HTTPException(status_code=404, detail="Master unit tidak ditemukan")
    data = body.model_dump(exclude_unset=True)
    if "material_type" in data and data["material_type"] is not None:
        mt = _normalize_unit_material_type(data["material_type"])
        if mt not in ("kulit", "kimia", "material_lain", "rp"):
            raise HTTPException(status_code=400, detail="Tipe tidak valid")
        data["material_type"] = mt
    if "unit" in data and data["unit"] is not None:
        data["unit"] = str(data["unit"]).strip()[:50]
        if not data["unit"]:
            raise HTTPException(status_code=400, detail="Unit wajib")
    mt = data.get("material_type", row.material_type)
    unit = data.get("unit", row.unit)
    if "material_type" in data or "unit" in data:
        clash = db.scalars(
            select(InventoryUnitMaster).where(
                InventoryUnitMaster.material_type == mt,
                InventoryUnitMaster.unit == unit,
                InventoryUnitMaster.id != unit_id,
            )
        ).first()
        if clash:
            raise HTTPException(status_code=409, detail="Unit untuk tipe ini sudah ada")
    for k, v in data.items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/units/{unit_id}")
def delete_inventory_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_inventory_write),
):
    row = db.get(InventoryUnitMaster, unit_id)
    if not row:
        raise HTTPException(status_code=404, detail="Master unit tidak ditemukan")
    row.is_active = False
    db.commit()
    return {"status": "deactivated", "id": unit_id}


@router.delete("/materials/{material_id}")
def delete_material(material_id: int, db: Session = Depends(get_db), _user=Depends(require_roles("admin"))):
    row = db.get(RawMaterial, material_id)
    if not row:
        raise HTTPException(status_code=404, detail="Material tidak ditemukan")
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


# === STOCK ===
@router.get("/stocks", response_model=list[MaterialStockOut])
def list_stocks(
    warehouse_id: Optional[int] = None,
    material_id: Optional[int] = None,
    low_stock: bool = False,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = select(MaterialStock).options(
        selectinload(MaterialStock.material),
        selectinload(MaterialStock.warehouse),
    )
    if warehouse_id:
        query = query.where(MaterialStock.warehouse_id == warehouse_id)
    if material_id:
        query = query.where(MaterialStock.material_id == material_id)

    results = list(db.scalars(query.order_by(MaterialStock.id)).all())

    if low_stock:
        results = [r for r in results if r.material and r.current_stock < (r.material.min_stock or 0)]

    return results


@router.get("/stocks/page")
def list_stocks_page(
    warehouse_id: Optional[int] = None,
    material_id: Optional[int] = None,
    low_stock: bool = False,
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="id|current_stock|warehouse_id|material_id"),
    sort_dir: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    params = _page_args(page, page_size, limit, offset, sort_by, sort_dir or "asc")
    stmt = select(MaterialStock).options(
        selectinload(MaterialStock.material),
        selectinload(MaterialStock.warehouse),
    )
    count_stmt = select(func.count(MaterialStock.id))
    if warehouse_id:
        stmt = stmt.where(MaterialStock.warehouse_id == warehouse_id)
        count_stmt = count_stmt.where(MaterialStock.warehouse_id == warehouse_id)
    if material_id:
        stmt = stmt.where(MaterialStock.material_id == material_id)
        count_stmt = count_stmt.where(MaterialStock.material_id == material_id)

    if low_stock:
        # Filter in memory after load (depends on related material.min_stock)
        all_rows = list(db.scalars(stmt.order_by(MaterialStock.id)).all())
        filtered = [
            r for r in all_rows if r.material and r.current_stock < (r.material.min_stock or 0)
        ]
        total = len(filtered)
        reverse = params.sort_dir == "desc"
        key_map = {
            "id": lambda r: r.id,
            "current_stock": lambda r: r.current_stock,
            "warehouse_id": lambda r: r.warehouse_id,
            "material_id": lambda r: r.material_id,
        }
        key_fn = key_map.get((params.sort_by or "").strip().lower()) or (lambda r: r.id)
        filtered.sort(key=key_fn, reverse=reverse)
        page_items = filtered[params.offset : params.offset + params.limit]
        return page_dict(items=page_items, total=total, params=params)

    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "id": MaterialStock.id,
            "current_stock": MaterialStock.current_stock,
            "warehouse_id": MaterialStock.warehouse_id,
            "material_id": MaterialStock.material_id,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(MaterialStock.id.asc(),),
    )
    items = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    return page_dict(items=items, total=total, params=params)


@router.get("/stocks/summary")
def stock_summary(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    """Get summary: total materials, total value, low stock count."""
    materials = db.scalars(select(RawMaterial).where(RawMaterial.is_active)).all()
    stocks = db.scalars(select(MaterialStock)).all()

    total_materials = len(materials)
    total_value = sum((s.current_stock * (s.material.cost_price or 0)) for s in stocks if s.material)
    low_stock_count = sum(1 for s in stocks if s.material and s.current_stock < (s.material.min_stock or 0))

    return {
        "total_materials": total_materials,
        "total_value": float(total_value),
        "low_stock_count": low_stock_count,
        "total_warehouses": db.query(Warehouse).count(),
    }


# === RECEIPTS ===
@router.get("/receipts", response_model=list[MaterialReceiptOut])
def list_receipts(
    warehouse_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    query = select(MaterialReceipt).options(
        selectinload(MaterialReceipt.warehouse),
        selectinload(MaterialReceipt.details).selectinload(MaterialReceiptDetail.material),
    )
    if warehouse_id:
        query = query.where(MaterialReceipt.warehouse_id == warehouse_id)
    if status:
        query = query.where(MaterialReceipt.status == status)
    if start_date:
        query = query.where(MaterialReceipt.receipt_date >= start_date)
    if end_date:
        query = query.where(MaterialReceipt.receipt_date <= end_date)
    return list(db.scalars(query.order_by(MaterialReceipt.receipt_date.desc())).all())


@router.get("/receipts/page")
def list_receipts_page(
    warehouse_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="id|receipt_number|receipt_date|status"),
    sort_dir: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    params = _page_args(page, page_size, limit, offset, sort_by, sort_dir or "desc")
    stmt = select(MaterialReceipt).options(
        selectinload(MaterialReceipt.warehouse),
        selectinload(MaterialReceipt.details).selectinload(MaterialReceiptDetail.material),
    )
    count_stmt = select(func.count(MaterialReceipt.id))
    if warehouse_id:
        stmt = stmt.where(MaterialReceipt.warehouse_id == warehouse_id)
        count_stmt = count_stmt.where(MaterialReceipt.warehouse_id == warehouse_id)
    if status:
        stmt = stmt.where(MaterialReceipt.status == status)
        count_stmt = count_stmt.where(MaterialReceipt.status == status)
    if start_date:
        stmt = stmt.where(MaterialReceipt.receipt_date >= start_date)
        count_stmt = count_stmt.where(MaterialReceipt.receipt_date >= start_date)
    if end_date:
        stmt = stmt.where(MaterialReceipt.receipt_date <= end_date)
        count_stmt = count_stmt.where(MaterialReceipt.receipt_date <= end_date)
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "id": MaterialReceipt.id,
            "receipt_number": MaterialReceipt.receipt_number,
            "receipt_date": MaterialReceipt.receipt_date,
            "status": MaterialReceipt.status,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(MaterialReceipt.receipt_date.desc(), MaterialReceipt.id.desc()),
    )
    items = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    return page_dict(items=items, total=total, params=params)


@router.post("/receipts", response_model=MaterialReceiptOut)
def create_receipt(
    body: MaterialReceiptCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "warehouse")),
):
    today = date.today()
    prefix = f"GR-{today.strftime('%Y%m%d')}"
    last = db.scalars(
        select(MaterialReceipt)
        .where(MaterialReceipt.receipt_number.like(f"{prefix}%"))
        .order_by(MaterialReceipt.receipt_number.desc())
    ).first()

    seq = 1
    if last:
        try:
            seq = int(last.receipt_number.split("-")[-1]) + 1
        except (ValueError, IndexError):
            seq = 1

    receipt_number = f"{prefix}-{seq:04d}"
    row = MaterialReceipt(
        receipt_number=receipt_number,
        supplier_name=body.supplier_name,
        receipt_date=body.receipt_date,
        warehouse_id=body.warehouse_id,
        total_amount=body.total_amount,
        remark=body.remark,
        status="draft",
    )
    db.add(row)
    db.flush()

    for detail in body.details or []:
        d = MaterialReceiptDetail(
            receipt_id=row.id,
            material_id=detail.material_id,
            quantity=detail.quantity,
            unit_cost=detail.unit_cost,
            total_cost=detail.quantity * (detail.unit_cost or Decimal(0)),
            remark=detail.remark,
        )
        db.add(d)

        stock = db.scalars(
            select(MaterialStock).where(
                MaterialStock.material_id == detail.material_id,
                MaterialStock.warehouse_id == body.warehouse_id,
            )
        ).first()

        if stock:
            stock.current_stock += detail.quantity
            stock.updated_at = datetime.utcnow()
        else:
            stock = MaterialStock(
                material_id=detail.material_id,
                warehouse_id=body.warehouse_id,
                current_stock=detail.quantity,
            )
            db.add(stock)

    db.commit()
    db.refresh(row)
    return row


@router.put("/receipts/{receipt_id}", response_model=MaterialReceiptOut)
def update_receipt(
    receipt_id: int,
    body: MaterialReceiptUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "warehouse")),
):
    row = db.get(MaterialReceipt, receipt_id)
    if not row:
        raise HTTPException(status_code=404, detail="Receipt tidak ditemukan")
    if row.status == "confirmed":
        raise HTTPException(status_code=400, detail="Receipt sudah confirmed tidak bisa diubah")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.post("/receipts/{receipt_id}/confirm")
def confirm_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "warehouse")),
):
    row = db.get(MaterialReceipt, receipt_id)
    if not row:
        raise HTTPException(status_code=404, detail="Receipt tidak ditemukan")
    if row.status == "confirmed":
        raise HTTPException(status_code=400, detail="Receipt sudah confirmed")
    row.status = "confirmed"
    db.commit()
    return {"status": "confirmed"}
