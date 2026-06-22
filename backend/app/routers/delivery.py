from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import DeliveryDetail, DeliveryHeader, PoDetail, PoHeader, ProductionDetail, QcDetail
from app.services.po_delivery_balance import validate_delivery_qty_against_po_balance
from app.schemas import (
    DeliveryDetailCreate,
    DeliveryDetailEnrichedOut,
    DeliveryDetailOut,
    DeliveryDetailUpdate,
    DeliveryHeaderCreate,
    DeliveryHeaderOut,
    DeliveryHeaderUpdate,
)
from app.services.business_rules import require_packing_ready
from app.routers.auth import get_current_user, require_roles
from app.services.audit import log_change
from app.services.notifications import create_notification_for_roles
from app.services.mkt_workflow import sync_mkt_for_delivery, sync_mkt_workflow_auto_advance
from app.services.business_rules import po_numbers_from_delivery
from app.routers.reports import _order_type_label, _thickness_display

router = APIRouter(tags=["delivery"])


def _delivery_detail_enriched(
    dd: DeliveryDetail,
    pd: ProductionDetail | None,
    pod: PoDetail | None,
    ph: PoHeader | None,
) -> DeliveryDetailEnrichedOut:
    lot_number = ((pd.lot_number or "").strip()) if pd else ""
    if not lot_number and pod:
        lot_number = (pod.thi_line_ref or "").strip()
    return DeliveryDetailEnrichedOut(
        id=dd.id,
        delivery_id=dd.delivery_id,
        production_detail_id=dd.production_detail_id,
        qty=float(dd.qty) if dd.qty is not None else None,
        qty_roll=dd.qty_roll,
        qty_pcs=dd.qty_pcs,
        weight=float(dd.weight) if dd.weight is not None else None,
        po_id=int(ph.id) if ph else None,
        po_number=(ph.po_number or "").strip() if ph else "",
        po_detail_id=int(pod.id) if pod else None,
        system_no=((pod.system_reference or pod.thi_line_ref or "").strip()) if pod else "",
        lot_number=lot_number,
        material_name_line=((pod.material_name or "").strip()) if pod else "",
        thickness_display=_thickness_display(pod) if pod else "",
        color_line=((pod.color or "").strip()) if pod else "",
        order_type=_order_type_label(ph) if ph else "",
    )


def _require_details_if_sent(
    db: Session, delivery_id: int, new_status: str | None, prev_status: str
) -> None:
    if new_status is None:
        return
    if (new_status or "").lower() != "sent":
        return
    if (prev_status or "").lower() == "sent":
        return
    one = db.scalars(
        select(DeliveryDetail)
        .where(DeliveryDetail.delivery_id == delivery_id)
        .limit(1)
    ).first()
    if not one:
        raise HTTPException(
            status_code=400,
            detail="Tambah minimal satu baris detail delivery sebelum status 'sent'",
        )


def _user_can_bypass_qc(user) -> bool:
    return getattr(user, "role", None) == "admin"


def _has_qc_ok(db: Session, production_detail_id: int | None) -> bool:
    if production_detail_id is None:
        return False
    row = db.scalars(
        select(QcDetail).where(
            and_(
                QcDetail.production_detail_id == production_detail_id,
                QcDetail.is_ok.is_(True),
            )
        )
    ).first()
    return row is not None


@router.post("/delivery/{delivery_id}/mark-surat-jalan-printed", response_model=DeliveryHeaderOut)
def mark_surat_jalan_printed(
    delivery_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse", "marketing")),
) -> DeliveryHeader:
    row = db.get(DeliveryHeader, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    before = {"surat_jalan_printed_at": row.surat_jalan_printed_at}
    row.surat_jalan_printed_at = datetime.utcnow()
    log_change(
        db,
        entity_type="delivery",
        entity_id=row.id,
        action="mark_surat_jalan_printed",
        before=before,
        after={"surat_jalan_printed_at": row.surat_jalan_printed_at},
        actor=user.username,
    )
    sync_mkt_for_delivery(db, delivery_id, actor=user.username)
    db.commit()
    db.refresh(row)
    return row


@router.post("/delivery", response_model=DeliveryHeaderOut)
def create_delivery(
    body: DeliveryHeaderCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> DeliveryHeader:
    require_packing_ready(db, body.packing_id)
    row = DeliveryHeader(**body.model_dump(exclude_unset=True))
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="delivery",
        entity_id=row.id,
        action="create",
        after={"delivery_number": row.delivery_number, "status": row.status},
        actor=user.username,
    )

    po_numbers = po_numbers_from_delivery(db, row.id)
    for pn in po_numbers:
        from app.models import PoHeader
        ph = db.scalars(select(PoHeader).where(PoHeader.po_number == pn).limit(1)).first()
        if ph:
            sync_mkt_workflow_auto_advance(db, ph.id, actor=user.username)

    db.commit()
    db.refresh(row)
    return row


@router.get("/delivery", response_model=list[DeliveryHeaderOut])
def list_delivery(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search delivery number/destination"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _user=Depends(get_current_user),
) -> list[DeliveryHeader]:
    stmt = select(DeliveryHeader).order_by(DeliveryHeader.id.desc()).limit(limit).offset(offset)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(DeliveryHeader.delivery_number.ilike(like), DeliveryHeader.destination.ilike(like)))
    rows = db.scalars(stmt).all()
    return rows


@router.put("/delivery/{delivery_id}", response_model=DeliveryHeaderOut)
def update_delivery(
    delivery_id: int,
    body: DeliveryHeaderUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> DeliveryHeader:
    row = db.get(DeliveryHeader, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    before = {"status": row.status, "packing_id": row.packing_id}
    data = body.model_dump(exclude_unset=True)
    if "packing_id" in data and data["packing_id"] is not None:
        require_packing_ready(db, int(data["packing_id"]))
    prev_status = row.status
    if "status" in data:
        _require_details_if_sent(db, delivery_id, data["status"], prev_status)
    for k, v in data.items():
        setattr(row, k, v)
    new_status = (row.status or "").lower()
    if new_status in ("cancelled", "canceled") and (prev_status or "").lower() not in ("cancelled", "canceled"):
        create_notification_for_roles(
            db,
            ("admin", "marketing", "warehouse", "finance"),
            title=f"Delivery {row.delivery_number or row.id} dibatalkan",
            message="Status delivery diubah menjadi cancelled; tinjau alur SJ / INVPL / invoice bila dokumen sudah diproses.",
            category="delivery",
            entity_type="delivery",
            entity_id=row.id,
            route_path="/admin/delivery",
            route_query={"delivery_id": row.id},
        )
    if row.status == "sent" and before["status"] != "sent":
        create_notification_for_roles(
            db,
            ("admin", "warehouse", "finance", "marketing"),
            title=f"Delivery {row.delivery_number or row.id} terkirim",
            message="Dokumen siap untuk proses invoice",
            category="delivery",
            entity_type="delivery",
            entity_id=row.id,
            route_path="/admin/delivery",
            route_query={"delivery_id": row.id},
        )
    log_change(
        db,
        entity_type="delivery",
        entity_id=row.id,
        action="update",
        before=before,
        after={"status": row.status, "packing_id": row.packing_id},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    return row


@router.get("/delivery/{delivery_id}", response_model=DeliveryHeaderOut)
def get_delivery(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> DeliveryHeader:
    row = db.get(DeliveryHeader, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    return row


@router.get("/delivery/{delivery_id}/details", response_model=list[DeliveryDetailEnrichedOut])
def list_delivery_details(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[DeliveryDetailEnrichedOut]:
    if not db.get(DeliveryHeader, delivery_id):
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    joined = db.execute(
        select(DeliveryDetail, ProductionDetail, PoDetail, PoHeader)
        .outerjoin(ProductionDetail, DeliveryDetail.production_detail_id == ProductionDetail.id)
        .outerjoin(PoDetail, ProductionDetail.po_detail_id == PoDetail.id)
        .outerjoin(PoHeader, PoDetail.po_id == PoHeader.id)
        .where(DeliveryDetail.delivery_id == delivery_id)
        .order_by(DeliveryDetail.id.asc())
    ).all()
    return [_delivery_detail_enriched(dd, pd, pod, ph) for dd, pd, pod, ph in joined]


@router.post("/delivery/{delivery_id}/details", response_model=DeliveryDetailOut)
def add_delivery_detail(
    delivery_id: int,
    body: DeliveryDetailCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
    bypass_qc: bool = Query(False, description="Admin: izinkan baris tanpa QC OK"),
) -> DeliveryDetail:
    hdr = db.get(DeliveryHeader, delivery_id)
    if not hdr:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    if bypass_qc and not _user_can_bypass_qc(user):
        raise HTTPException(status_code=403, detail="bypass_qc hanya untuk role admin")
    qc_ok = _has_qc_ok(db, body.production_detail_id)
    if not qc_ok and not (bypass_qc and _user_can_bypass_qc(user)):
        raise HTTPException(
            status_code=400,
            detail="Hanya production detail yang sudah QC OK yang boleh dikirim",
        )
    validate_delivery_qty_against_po_balance(
        db,
        production_detail_id=body.production_detail_id,
        qty=body.qty,
    )
    row = DeliveryDetail(
        delivery_id=delivery_id, **body.model_dump(exclude_unset=True)
    )
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="delivery_line",
        entity_id=row.id,
        action="create",
        after={"delivery_id": delivery_id, "production_detail_id": row.production_detail_id, "qty": row.qty},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    return row


@router.put("/delivery-detail/{detail_id}", response_model=DeliveryDetailOut)
def update_delivery_detail(
    detail_id: int,
    body: DeliveryDetailUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
    bypass_qc: bool = Query(False, description="Admin: izinkan baris tanpa QC OK"),
) -> DeliveryDetail:
    row = db.get(DeliveryDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail delivery tidak ditemukan")
    before = {"production_detail_id": row.production_detail_id, "qty": row.qty, "qty_roll": row.qty_roll, "qty_pcs": row.qty_pcs}
    new_pd = body.production_detail_id
    if bypass_qc and not _user_can_bypass_qc(user):
        raise HTTPException(status_code=403, detail="bypass_qc hanya untuk role admin")
    if new_pd is not None:
        qc_ok = _has_qc_ok(db, new_pd)
        if not qc_ok and not (bypass_qc and _user_can_bypass_qc(user)):
            raise HTTPException(
                status_code=400,
                detail="Hanya production detail yang sudah QC OK yang boleh dikirim",
            )
    target_pd = new_pd if new_pd is not None else row.production_detail_id
    target_qty = body.qty if body.qty is not None else row.qty
    if target_pd is not None:
        validate_delivery_qty_against_po_balance(
            db,
            production_detail_id=int(target_pd),
            qty=target_qty,
            exclude_delivery_detail_id=detail_id,
        )
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    log_change(
        db,
        entity_type="delivery_line",
        entity_id=row.id,
        action="update",
        before=before,
        after={"production_detail_id": row.production_detail_id, "qty": row.qty, "qty_roll": row.qty_roll, "qty_pcs": row.qty_pcs},
        actor=user.username,
    )
    db.commit()
    db.refresh(row)
    return row
