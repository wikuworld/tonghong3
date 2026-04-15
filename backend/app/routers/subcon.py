from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PoHeader, SubconInvoice
from app.schemas import SubconInvoiceCreate, SubconInvoiceUpdate, row_to_dict
from app.routers.auth import get_current_user, require_roles
from app.services.audit import log_change

router = APIRouter(tags=["subcon"])


@router.post("/subcon-invoices")
def create_subcon_invoice(
    body: SubconInvoiceCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> dict:
    if body.invoice_type not in ("barang", "jasa"):
        raise HTTPException(status_code=400, detail="invoice_type harus 'barang' atau 'jasa'")
    
    po = db.get(PoHeader, body.po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    
    data = body.model_dump(exclude_unset=True)
    row = SubconInvoice(**data)
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="subcon_invoice",
        entity_id=row.id,
        action="create",
        after={"invoice_type": row.invoice_type, "amount": str(row.amount)},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    
    result = row_to_dict(row)
    result["po_number"] = po.po_number
    result["customer_name"] = po.customer_name_snapshot
    return result


@router.get("/subcon-invoices")
def list_subcon_invoices(
    db: Session = Depends(get_db),
    po_id: Optional[int] = Query(None, description="Filter by PO ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    invoice_type: Optional[str] = Query(None, description="Filter by invoice type"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _user=Depends(get_current_user),
) -> list[dict]:
    stmt = select(SubconInvoice).order_by(SubconInvoice.id.desc()).limit(limit).offset(offset)
    
    if po_id:
        stmt = stmt.where(SubconInvoice.po_id == po_id)
    if status:
        stmt = stmt.where(SubconInvoice.status == status)
    if invoice_type:
        stmt = stmt.where(SubconInvoice.invoice_type == invoice_type)
    
    rows = db.scalars(stmt).all()
    out = []
    for r in rows:
        x = row_to_dict(r)
        po = db.get(PoHeader, r.po_id)
        x["po_number"] = po.po_number if po else None
        x["customer_name"] = po.customer_name_snapshot if po else None
        out.append(x)
    return out


@router.get("/subcon-invoices/{invoice_id}")
def get_subcon_invoice(
    invoice_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> dict:
    row = db.get(SubconInvoice, invoice_id)
    if not row:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    result = row_to_dict(row)
    po = db.get(PoHeader, row.po_id)
    result["po_number"] = po.po_number if po else None
    result["customer_name"] = po.customer_name_snapshot if po else None
    return result


@router.put("/subcon-invoices/{invoice_id}")
def update_subcon_invoice(
    invoice_id: int,
    body: SubconInvoiceUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> dict:
    row = db.get(SubconInvoice, invoice_id)
    if not row:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    if row.status == "cancelled":
        raise HTTPException(status_code=400, detail="Tidak dapat mengubah invoice yang sudah dibatalkan")
    
    before = row_to_dict(row)
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    
    log_change(
        db,
        entity_type="subcon_invoice",
        entity_id=row.id,
        action="update",
        before=before,
        after=row_to_dict(row),
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    
    result = row_to_dict(row)
    po = db.get(PoHeader, row.po_id)
    result["po_number"] = po.po_number if po else None
    result["customer_name"] = po.customer_name_snapshot if po else None
    return result


@router.delete("/subcon-invoices/{invoice_id}")
def delete_subcon_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> dict:
    row = db.get(SubconInvoice, invoice_id)
    if not row:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")
    
    if row.status == "cancelled":
        raise HTTPException(status_code=400, detail="Invoice sudah dibatalkan")
    
    before = row_to_dict(row)
    row.status = "cancelled"
    
    log_change(
        db,
        entity_type="subcon_invoice",
        entity_id=row.id,
        action="cancel",
        before=before,
        after={"status": "cancelled"},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    
    result = row_to_dict(row)
    po = db.get(PoHeader, row.po_id)
    result["po_number"] = po.po_number if po else None
    result["customer_name"] = po.customer_name_snapshot if po else None
    return result


@router.post("/subcon-invoices/generate-from-po/{po_id}")
def generate_invoices_from_po(
    po_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> list[dict]:
    po = db.get(PoHeader, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    
    if po.po_category != "subcont":
        raise HTTPException(status_code=400, detail="Hanya PO subcont yang bisa generate invoice")
    
    existing = db.scalars(
        select(SubconInvoice).where(
            and_(SubconInvoice.po_id == po_id, SubconInvoice.status != "cancelled")
        )
    ).all()
    existing_types = {r.invoice_type for r in existing}
    
    created = []
    for inv_type in ("barang", "jasa"):
        if inv_type in existing_types:
            continue
        
        row = SubconInvoice(
            po_id=po_id,
            invoice_type=inv_type,
            amount=0,
            status="draft",
        )
        db.add(row)
        db.flush()
        
        log_change(
            db,
            entity_type="subcon_invoice",
            entity_id=row.id,
            action="generate_from_po",
            after={"invoice_type": inv_type, "po_id": po_id},
            actor=user.username,
        )
        
        result = row_to_dict(row)
        result["po_number"] = po.po_number
        result["customer_name"] = po.customer_name_snapshot
        created.append(result)
    
    db.commit()
    return created
