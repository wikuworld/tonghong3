from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, select
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
def mark_surat_jalan_printed(delivery_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(DeliveryHeader, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    row.surat_jalan_printed_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.post("/delivery")
def create_delivery(body: DeliveryHeaderCreate, db: Session = Depends(get_db)) -> dict:
    require_packing_ready(db, body.packing_id)
    row = DeliveryHeader(**body.model_dump(exclude_unset=True))
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.get("/delivery")
def list_delivery(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.scalars(select(DeliveryHeader).order_by(DeliveryHeader.id.desc())).all()
    return [row_to_dict(r) for r in rows]


@router.put("/delivery/{delivery_id}")
def update_delivery(
    delivery_id: int, body: DeliveryHeaderUpdate, db: Session = Depends(get_db)
) -> dict:
    row = db.get(DeliveryHeader, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    data = body.model_dump(exclude_unset=True)
    if "packing_id" in data and data["packing_id"] is not None:
        require_packing_ready(db, int(data["packing_id"]))
    if "status" in data:
        _require_details_if_sent(db, delivery_id, data["status"], row.status)
    for k, v in data.items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.get("/delivery/{delivery_id}")
def get_delivery(delivery_id: int, db: Session = Depends(get_db)) -> dict:
    row = db.get(DeliveryHeader, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    return row_to_dict(row)


@router.get("/delivery/{delivery_id}/details")
def list_delivery_details(delivery_id: int, db: Session = Depends(get_db)) -> list[dict]:
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
    delivery_id: int, body: DeliveryDetailCreate, db: Session = Depends(get_db)
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
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/delivery-detail/{detail_id}")
def update_delivery_detail(
    detail_id: int, body: DeliveryDetailUpdate, db: Session = Depends(get_db)
) -> dict:
    row = db.get(DeliveryDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail delivery tidak ditemukan")
    new_pd = body.production_detail_id
    if new_pd is not None and not _has_qc_ok(db, new_pd):
        raise HTTPException(
            status_code=400,
            detail="Hanya production detail yang sudah QC OK yang boleh dikirim",
        )
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)
