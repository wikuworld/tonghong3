from __future__ import annotations

from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Notification, User


def create_notification_for_user(
    db: Session,
    user_id: int,
    *,
    title: str,
    message: str | None = None,
    category: str = "general",
    entity_type: str | None = None,
    entity_id: int | None = None,
    route_path: str | None = None,
    route_query: dict | None = None,
) -> Notification:
    row = Notification(
        user_id=user_id,
        title=title,
        message=message,
        category=category,
        entity_type=entity_type,
        entity_id=entity_id,
        route_path=route_path,
        route_query=route_query,
    )
    db.add(row)
    return row


def create_notification_for_roles(
    db: Session,
    roles: Sequence[str] | Iterable[str],
    *,
    title: str,
    message: str | None = None,
    category: str = "general",
    entity_type: str | None = None,
    entity_id: int | None = None,
    route_path: str | None = None,
    route_query: dict | None = None,
) -> int:
    role_set = {str(r).strip() for r in roles if str(r).strip()}
    if not role_set:
        return 0
    users = db.scalars(
        select(User).where(User.role.in_(tuple(role_set)), User.is_active.is_(True))
    ).all()
    count = 0
    for user in users:
        create_notification_for_user(
            db,
            user.id,
            title=title,
            message=message,
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
            route_path=route_path,
            route_query=route_query,
        )
        count += 1
    return count
