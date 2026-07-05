from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Notification
from app.routers.auth import get_current_user
from app.schemas import NotificationOut

router = APIRouter(tags=["notifications"])


@router.get("/notifications", response_model=list[NotificationOut])
def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> list[Notification]:
    stmt = (
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.id.desc())
        .limit(limit)
        .offset(offset)
    )
    if unread_only:
        stmt = stmt.where(Notification.is_read.is_(False))
    return list(db.scalars(stmt).all())


@router.get("/notifications/unread-count")
def unread_count(db: Session = Depends(get_db), user=Depends(get_current_user)) -> dict:
    n = db.scalar(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user.id, Notification.is_read.is_(False))
    )
    return {"unread_count": int(n or 0)}


@router.post("/notifications/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> Notification:
    row = db.get(Notification, notification_id)
    if not row or row.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notifikasi tidak ditemukan")
    if not row.is_read:
        row.is_read = True
        row.read_at = datetime.utcnow()
        db.commit()
        db.refresh(row)
    return row


@router.post("/notifications/read-all")
def mark_all_read(db: Session = Depends(get_db), user=Depends(get_current_user)) -> dict:
    rows = db.scalars(
        select(Notification).where(
            Notification.user_id == user.id, Notification.is_read.is_(False)
        )
    ).all()
    now = datetime.utcnow()
    for row in rows:
        row.is_read = True
        row.read_at = now
    db.commit()
    return {"updated": len(rows)}
