from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import PoHeader, SubconInvoice
from app.paging import apply_sort, page_dict, parse_page_params
from app.schemas import SubconInvoiceCreate, SubconInvoiceOut, SubconInvoiceUpdate
from app.routers.auth import get_current_user, require_roles
from app.services.audit import log_change

router = APIRouter(tags=["subcon"])


def _subcon_invoice_out(row: SubconInvoice, po: PoHeader | None) -> SubconInvoiceOut:
    base = SubconInvoiceOut.model_validate(row)
    return base.model_copy(
        update={
            "po_number": po.po_number if po else None,
            "customer_name": po.customer_name_snapshot if po else None,
        }
    )


@router.post("/subcon-invoices", response_model=SubconInvoiceOut)
def create_subcon_invoice(
    body: SubconInvoiceCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> SubconInvoiceOut:
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

    return _subcon_invoice_out(row, po)


@router.get("/subcon-invoices")
def list_subcon_invoices(
    db: Session = Depends(get_db),
    po_id: Optional[int] = Query(None, description="Filter by PO ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    invoice_type: Optional[str] = Query(None, description="Filter by invoice type"),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="date|code|status|created_at|invoice_number"),
    sort_dir: Optional[str] = Query(None),
    _user=Depends(get_current_user),
) -> dict:
    params = parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    stmt = select(SubconInvoice)
    count_stmt = select(func.count(SubconInvoice.id))

    if po_id:
        stmt = stmt.where(SubconInvoice.po_id == po_id)
        count_stmt = count_stmt.where(SubconInvoice.po_id == po_id)
    if status:
        stmt = stmt.where(SubconInvoice.status == status)
        count_stmt = count_stmt.where(SubconInvoice.status == status)
    if invoice_type:
        stmt = stmt.where(SubconInvoice.invoice_type == invoice_type)
        count_stmt = count_stmt.where(SubconInvoice.invoice_type == invoice_type)

    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "date": SubconInvoice.created_at,
            "created_at": SubconInvoice.created_at,
            "code": SubconInvoice.invoice_number,
            "invoice_number": SubconInvoice.invoice_number,
            "status": SubconInvoice.status,
            "id": SubconInvoice.id,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(SubconInvoice.id.desc(),),
    )
    rows = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    items = [_subcon_invoice_out(r, db.get(PoHeader, r.po_id)) for r in rows]
    return page_dict(items=items, total=total, params=params)


@router.get("/subcon-invoices/{invoice_id}", response_model=SubconInvoiceOut)
def get_subcon_invoice(
    invoice_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> SubconInvoiceOut:
    row = db.get(SubconInvoice, invoice_id)
    if not row:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")

    po = db.get(PoHeader, row.po_id)
    return _subcon_invoice_out(row, po)


@router.put("/subcon-invoices/{invoice_id}", response_model=SubconInvoiceOut)
def update_subcon_invoice(
    invoice_id: int,
    body: SubconInvoiceUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> SubconInvoiceOut:
    row = db.get(SubconInvoice, invoice_id)
    if not row:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")

    if row.status == "cancelled":
        raise HTTPException(status_code=400, detail="Tidak dapat mengubah invoice yang sudah dibatalkan")

    before = SubconInvoiceOut.model_validate(row).model_dump(mode="json")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)

    log_change(
        db,
        entity_type="subcon_invoice",
        entity_id=row.id,
        action="update",
        before=before,
        after=SubconInvoiceOut.model_validate(row).model_dump(mode="json"),
        actor=user.username,
    )
    db.commit()
    db.refresh(row)

    po = db.get(PoHeader, row.po_id)
    return _subcon_invoice_out(row, po)


@router.delete("/subcon-invoices/{invoice_id}", response_model=SubconInvoiceOut)
def delete_subcon_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> SubconInvoiceOut:
    row = db.get(SubconInvoice, invoice_id)
    if not row:
        raise HTTPException(status_code=404, detail="Invoice tidak ditemukan")

    if row.status == "cancelled":
        raise HTTPException(status_code=400, detail="Invoice sudah dibatalkan")

    before = SubconInvoiceOut.model_validate(row).model_dump(mode="json")
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

    po = db.get(PoHeader, row.po_id)
    return _subcon_invoice_out(row, po)


@router.post("/subcon-invoices/generate-from-po/{po_id}", response_model=list[SubconInvoiceOut])
def generate_invoices_from_po(
    po_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "finance")),
) -> list[SubconInvoiceOut]:
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

    created: list[SubconInvoiceOut] = []
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

        created.append(_subcon_invoice_out(row, po))

    db.commit()
    return created
