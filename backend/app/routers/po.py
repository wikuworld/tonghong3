from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import PoDetail, PoHeader
from app.services.audit import log_change
from app.services.numbering import next_number
from app.schemas import (
    PoDetailCreate,
    PoDetailOut,
    PoDetailUpdate,
    PoHeaderCreate,
    PoHeaderOut,
    PoHeaderUpdate,
)
from app.services.business_rules import validate_po_status_transition
from app.services.mkt_workflow import (
    MKT_STAGES_ORDER,
    apply_mkt_stage,
    next_mkt_stage,
    validate_mkt_advance,
)
from app.services.notifications import create_notification_for_roles
from app.routers.auth import get_current_user, require_roles

router = APIRouter(tags=["po"])


def _detail_loaded(db: Session, detail_id: int) -> Optional[PoDetail]:
    return db.scalars(
        select(PoDetail)
        .options(selectinload(PoDetail.delivery_schedules))
        .where(PoDetail.id == detail_id)
    ).first()


@router.get("/po/mkt-workflow-stages")
def mkt_workflow_stages(_user=Depends(get_current_user)) -> dict:
    return {"stages": list(MKT_STAGES_ORDER)}


@router.get("/po", response_model=list[PoHeaderOut])
def list_po(
    mkt_workflow_stage: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search PO no/customer/buyer"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[PoHeader]:
    stmt = select(PoHeader).order_by(PoHeader.id.desc()).limit(limit).offset(offset)
    if mkt_workflow_stage:
        stmt = stmt.where(PoHeader.mkt_workflow_stage == mkt_workflow_stage)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                PoHeader.po_number.ilike(like),
                PoHeader.buyer.ilike(like),
                PoHeader.model.ilike(like),
            )
        )
    return list(db.scalars(stmt).all())


@router.post("/po/{po_id}/mkt-workflow/advance", response_model=PoHeaderOut)
def advance_mkt_workflow(
    po_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing", "ppic")),
) -> PoHeader:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    nxt = next_mkt_stage(row.mkt_workflow_stage)
    if not nxt:
        raise HTTPException(status_code=400, detail="PO sudah di tahap akhir alur MKT")
    validate_mkt_advance(db, po_id, nxt)
    apply_mkt_stage(db, po_id, nxt)
    create_notification_for_roles(
        db,
        ("admin", "marketing", "ppic"),
        title=f"PO {row.po_number or row.id} masuk tahap {nxt}",
        message=f"Tahap alur marketing diperbarui menjadi: {nxt}",
        category="workflow",
        entity_type="sales_order",
        entity_id=row.id,
        route_path="/admin/marketing-flow",
        route_query={"po_id": row.id},
    )
    db.commit()
    db.refresh(row)
    return row


@router.post("/po", response_model=PoHeaderOut)
def create_po(
    body: PoHeaderCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "sales")),
) -> PoHeader:
    data = body.model_dump(exclude_unset=True)
    if not data.get("po_number"):
        data["po_number"] = next_number(db, "SO", "SO")
    row = PoHeader(**data)
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="sales_order",
        entity_id=row.id,
        action="create",
        after={"po_number": row.po_number, "status": row.status},
        actor=user.username,
    )
    create_notification_for_roles(
        db,
        ("admin", "marketing", "ppic"),
        title=f"PO baru {row.po_number}",
        message=f"Sales order dibuat oleh {user.username}",
        category="po",
        entity_type="sales_order",
        entity_id=row.id,
        route_path="/admin/po",
        route_query={"po_id": row.id},
    )
    db.commit()
    db.refresh(row)
    return row


@router.get("/po/{po_id}", response_model=PoHeaderOut)
def get_po(
    po_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> PoHeader:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    return row


@router.get("/po/{po_id}/details", response_model=list[PoDetailOut])
def list_po_details(
    po_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[PoDetail]:
    if not db.get(PoHeader, po_id):
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    rows = db.scalars(
        select(PoDetail)
        .options(selectinload(PoDetail.delivery_schedules))
        .where(PoDetail.po_id == po_id)
        .order_by(PoDetail.id.asc())
    ).all()
    return list(rows)


@router.put("/po/{po_id}", response_model=PoHeaderOut)
def update_po(
    po_id: int,
    body: PoHeaderUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "ppic")),
) -> PoHeader:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    before = {"status": row.status, "mkt_workflow_stage": row.mkt_workflow_stage}
    data = body.model_dump(exclude_unset=True)
    if "status" in data:
        validate_po_status_transition(row.status, data["status"])
    for k, v in data.items():
        setattr(row, k, v)
    if "status" in data and data["status"] != before["status"]:
        create_notification_for_roles(
            db,
            ("admin", "marketing", "ppic", "production"),
            title=f"Status PO {row.po_number or row.id}: {data['status']}",
            message=f"Diubah oleh {user.username}",
            category="po_status",
            entity_type="sales_order",
            entity_id=row.id,
            route_path="/admin/po",
            route_query={"po_id": row.id},
        )
    log_change(
        db,
        entity_type="sales_order",
        entity_id=row.id,
        action="update",
        before=before,
        after={"status": row.status, "mkt_workflow_stage": row.mkt_workflow_stage},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    return row


@router.delete("/po/{po_id}")
def delete_po(
    po_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    log_change(
        db,
        entity_type="sales_order",
        entity_id=row.id,
        action="delete",
        before={"po_number": row.po_number, "status": row.status},
        actor=user.username,
    )
    db.delete(row)
    db.commit()
    return {"status": "deleted"}


@router.post("/po/{po_id}/details", response_model=PoDetailOut)
def add_po_detail(
    po_id: int,
    body: PoDetailCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing", "sales")),
) -> PoDetail:
    po = db.get(PoHeader, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    row = PoDetail(po_id=po_id, **body.model_dump(exclude_unset=True))
    db.add(row)
    db.commit()
    out = _detail_loaded(db, row.id)
    return out or row


@router.put("/po-detail/{detail_id}", response_model=PoDetailOut)
def update_po_detail(
    detail_id: int,
    body: PoDetailUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "ppic", "finance")),
) -> PoDetail:
    row = db.get(PoDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail PO tidak ditemukan")
    data = body.model_dump(exclude_unset=True)

    # Harga otomatis: hanya admin/finance yang boleh mengubah unit_price langsung.
    if "unit_price" in data and user.role not in ("admin", "finance"):
        raise HTTPException(status_code=403, detail="unit_price dikunci (harga otomatis)")

    before = {
        "material_name": row.material_name,
        "color": row.color,
        "thickness_text": row.thickness_text,
        "thickness_min": row.thickness_min,
        "thickness_max": row.thickness_max,
        "quantity_order": row.quantity_order,
        "line_etd": row.line_etd,
        "backing": row.backing,
        "unit_price": row.unit_price,
    }
    for k, v in data.items():
        setattr(row, k, v)
    log_change(
        db,
        entity_type="sales_order_line",
        entity_id=row.id,
        action="update",
        before=before,
        after={
            "material_name": row.material_name,
            "color": row.color,
            "thickness_text": row.thickness_text,
            "thickness_min": row.thickness_min,
            "thickness_max": row.thickness_max,
            "quantity_order": row.quantity_order,
            "line_etd": row.line_etd,
            "backing": row.backing,
            "unit_price": row.unit_price,
        },
        actor=user.username,
    )
    db.commit()
    out = _detail_loaded(db, detail_id)
    return out or row


@router.delete("/po-detail/{detail_id}")
def delete_po_detail(
    detail_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(PoDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail PO tidak ditemukan")
    log_change(
        db,
        entity_type="sales_order_line",
        entity_id=row.id,
        action="delete",
        before={"material_name": row.material_name, "unit_price": row.unit_price},
        actor=user.username,
    )
    db.delete(row)
    db.commit()
    return {"status": "deleted"}
