"""Audit trail (CR §3.x mandatory audit)."""

from __future__ import annotations

import json
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models import AuditLog


def log_change(
    db: Session,
    *,
    entity_type: str,
    entity_id: Optional[int],
    action: str,
    before: Optional[dict[str, Any]] = None,
    after: Optional[dict[str, Any]] = None,
    actor: str = "system",
) -> None:
    row = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        payload_before=json.dumps(before, default=str) if before is not None else None,
        payload_after=json.dumps(after, default=str) if after is not None else None,
        actor=actor,
    )
    db.add(row)
