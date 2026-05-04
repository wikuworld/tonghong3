from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.db import get_db
from app.models import Warehouse, RawMaterial, MaterialStock, MaterialReceipt, MaterialReceiptDetail
from app.schemas import (
    WarehouseCreate, WarehouseUpdate, WarehouseOut,
    RawMaterialCreate, RawMaterialUpdate, RawMaterialOut,
    MaterialStockOut,
    MaterialReceiptCreate, MaterialReceiptUpdate, MaterialReceiptOut,
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


# === MATERIAL RECEIPT ===
@router.get("/receipts", response_model=list[MaterialReceiptOut])
def list_receipts(
    warehouse_id: int = None,
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user)
):
    query = select(MaterialReceipt)
    if warehouse_id:
        query = query.where(MaterialReceipt.warehouse_id == warehouse_id)
    if start_date:
        query = query.where(MaterialReceipt.receipt_date >= start_date)
    if end_date:
        query = query.where(MaterialReceipt.receipt_date <= end_date)
    return db.scalars(query.order_by(MaterialReceipt.receipt_date.desc())).all()


@router.post("/receipts", response_model=MaterialReceiptOut)
def create_receipt(body: MaterialReceiptCreate, db: Session = Depends(get_db), _user=Depends(require_roles("admin", "warehouse"))):
    # Generate receipt number
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
    
    # Create receipt
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
    
    # Create details and update stock
    for detail in body.details or []:
        d = MaterialReceiptDetail(
            receipt_id=row.id,
            material_id=detail.material_id,
            quantity=detail.quantity,
            unit_cost=detail.unit_cost,
            total_cost=detail.quantity * (detail.unit_cost or 0),
            remark=detail.remark,
        )
        db.add(d)
        
        # Update stock
        stock = db.scalars(
            select(MaterialStock).where(
                MaterialStock.material_id == detail.material_id,
                MaterialStock.warehouse_id == body.warehouse_id
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
def update_receipt(receipt_id: int, body: MaterialReceiptUpdate, db: Session = Depends(get_db), _user=Depends(require_roles("admin", "warehouse"))):
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
def confirm_receipt(receipt_id: int, db: Session = Depends(get_db), _user=Depends(require_roles("admin", "warehouse"))):
    row = db.get(MaterialReceipt, receipt_id)
    if not row:
        raise HTTPException(status_code=404, detail="Receipt tidak ditemukan")
    if row.status == "confirmed":
        raise HTTPException(status_code=400, detail="Receipt sudah confirmed")
    row.status = "confirmed"
    db.commit()
    return {"status": "confirmed"}
