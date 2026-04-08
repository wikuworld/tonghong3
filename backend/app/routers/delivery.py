from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import DeliveryDetail, DeliveryHeader, QcDetail
from app.schemas import (
    DeliveryDetailCreate,
    DeliveryDetailUpdate,
    DeliveryHeaderCreate,
    DeliveryHeaderUpdate,
    row_to_dict,
)
from app.services.business_rules import require_packing_ready
from app.routers.auth import get_current_user, require_roles
from app.services.audit import log_change
from app.services.notifications import create_notification_for_roles

router = APIRouter(tags=["delivery"])


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


@router.post("/delivery/{delivery_id}/mark-surat-jalan-printed")
def mark_surat_jalan_printed(
    delivery_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> dict:
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
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.post("/delivery")
def create_delivery(
    body: DeliveryHeaderCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> dict:
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
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.get("/delivery")
def list_delivery(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search delivery number/destination"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _user=Depends(get_current_user),
) -> list[dict]:
    stmt = select(DeliveryHeader).order_by(DeliveryHeader.id.desc()).limit(limit).offset(offset)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(DeliveryHeader.delivery_number.ilike(like), DeliveryHeader.destination.ilike(like)))
    rows = db.scalars(stmt).all()
    return [row_to_dict(r) for r in rows]


@router.put("/delivery/{delivery_id}")
def update_delivery(
    delivery_id: int,
    body: DeliveryHeaderUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> dict:
    row = db.get(DeliveryHeader, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    before = {"status": row.status, "packing_id": row.packing_id}
    data = body.model_dump(exclude_unset=True)
    if "packing_id" in data and data["packing_id"] is not None:
        require_packing_ready(db, int(data["packing_id"]))
    if "status" in data:
        _require_details_if_sent(db, delivery_id, data["status"], row.status)
    for k, v in data.items():
        setattr(row, k, v)
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
    return row_to_dict(row)


@router.get("/delivery/{delivery_id}")
def get_delivery(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> dict:
    row = db.get(DeliveryHeader, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    return row_to_dict(row)


@router.get("/delivery/{delivery_id}/details")
def list_delivery_details(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[dict]:
    if not db.get(DeliveryHeader, delivery_id):
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    rows = db.scalars(
        select(DeliveryDetail)
        .where(DeliveryDetail.delivery_id == delivery_id)
        .order_by(DeliveryDetail.id.asc())
    ).all()
    return [row_to_dict(r) for r in rows]


@router.post("/delivery/{delivery_id}/details")
def add_delivery_detail(
    delivery_id: int,
    body: DeliveryDetailCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> dict:
    hdr = db.get(DeliveryHeader, delivery_id)
    if not hdr:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    if not _has_qc_ok(db, body.production_detail_id):
        raise HTTPException(
            status_code=400,
            detail="Hanya production detail yang sudah QC OK yang boleh dikirim",
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
    return row_to_dict(row)


@router.put("/delivery-detail/{detail_id}")
def update_delivery_detail(
    detail_id: int,
    body: DeliveryDetailUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> dict:
    row = db.get(DeliveryDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail delivery tidak ditemukan")
    before = {"production_detail_id": row.production_detail_id, "qty": row.qty, "qty_roll": row.qty_roll, "qty_pcs": row.qty_pcs}
    new_pd = body.production_detail_id
    if new_pd is not None and not _has_qc_ok(db, new_pd):
        raise HTTPException(
            status_code=400,
            detail="Hanya production detail yang sudah QC OK yang boleh dikirim",
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
    return row_to_dict(row)
