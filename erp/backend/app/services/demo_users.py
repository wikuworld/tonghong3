"""User demo per role untuk uji RBAC / alur MKT (dev & staging)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import User
from app.routers.auth import hash_password

DEMO_ROLE_USERS: tuple[tuple[str, str, Optional[str]], ...] = (
    ("demo_sales", "sales", "sales"),
    ("demo_marketing", "marketing", "marketing"),
    ("demo_ppic", "ppic", "ppic"),
    ("demo_production", "production", "production"),
    ("demo_qc", "qc", "qc"),
    ("demo_warehouse", "warehouse", "warehouse"),
    ("demo_finance", "finance", "finance"),
)


@dataclass(frozen=True)
class DemoUserSeedResult:
    created: list[str]
    skipped: list[str]


def ensure_demo_role_users(db: Session) -> DemoUserSeedResult:
    """Buat user demo jika username belum ada (idempotent)."""
    password = (settings.demo_users_password or "").strip()
    if not password:
        return DemoUserSeedResult(created=[], skipped=[])

    created: list[str] = []
    skipped: list[str] = []
    pw_hash = hash_password(password)

    for username, role, department in DEMO_ROLE_USERS:
        existing = db.scalars(select(User).where(User.username == username).limit(1)).first()
        if existing:
            skipped.append(username)
            continue
        db.add(
            User(
                username=username,
                password_hash=pw_hash,
                role=role,
                department=department,
                is_active=True,
            )
        )
        created.append(username)

    if created:
        db.commit()

    return DemoUserSeedResult(created=created, skipped=skipped)
