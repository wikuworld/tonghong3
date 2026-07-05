from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import AuditLog
from app.routers.auth import get_current_user

router = APIRouter(tags=["audit"])


def _try_json(s: str | None) -> Any:
    if not s:
        return None
    try:
        return json.loads(s)
    except Exception:
        return s


@router.get("/audit/logs")
def list_audit_logs(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[dict[str, Any]]:
    stmt = select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)
    if entity_type:
        stmt = stmt.where(AuditLog.entity_type == entity_type)
    if entity_id is not None:
        stmt = stmt.where(AuditLog.entity_id == entity_id)
    rows = db.scalars(stmt).all()
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "id": r.id,
                "entity_type": r.entity_type,
                "entity_id": r.entity_id,
                "action": r.action,
                "before": _try_json(r.payload_before),
                "after": _try_json(r.payload_after),
                "actor": r.actor,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
        )
    return out

