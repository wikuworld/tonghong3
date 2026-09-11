from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Warehouse, RawMaterial, MaterialStock
from app.schemas import (
    WarehouseCreate, WarehouseUpdate, WarehouseOut,
    RawMaterialCreate, RawMaterialUpdate, RawMaterialOut,
    MaterialStockOut,
)
from app.routers.auth import get_current_user, require_roles

router = APIRouter(prefix="/inventory", tags=["inventory"])


# === WAREHOUSE ===
@router.get("/warehouses", response_model=list[WarehouseOut])
def list_warehouses(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return db.scalars(select(Warehouse).order_by(Warehouse.name)).all()


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
def list_materials(db: Session = Depends(get_db), _user=Depends(get_current_user)):
    return db.scalars(select(RawMaterial).order_by(RawMaterial.name)).all()


@router.post("/materials", response_model=RawMaterialOut)
def create_material(body: RawMaterialCreate, db: Session = Depends(get_db), _user=Depends(require_roles("admin"))):
    existing = db.scalars(select(RawMaterial).where(RawMaterial.code == body.code)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Kode material sudah ada")
    row = RawMaterial(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/materials/{material_id}", response_model=RawMaterialOut)
def update_material(material_id: int, body: RawMaterialUpdate, db: Session = Depends(get_db), _user=Depends(require_roles("admin"))):
    row = db.get(RawMaterial, material_id)
    if not row:
        raise HTTPException(status_code=404, detail="Material tidak ditemukan")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


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
    warehouse_id: int = None,
    material_id: int = None,
    low_stock: bool = False,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user)
):
    query = select(MaterialStock)
    if warehouse_id:
        query = query.where(MaterialStock.warehouse_id == warehouse_id)
    if material_id:
        query = query.where(MaterialStock.material_id == material_id)
    
    results = db.scalars(query.order_by(MaterialStock.id)).all()
    
    if low_stock:
        results = [r for r in results if r.material and r.current_stock < (r.material.min_stock or 0)]
    
    return results


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

