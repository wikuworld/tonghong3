from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import RolePermission
from app.routers.auth import get_current_user, require_roles

router = APIRouter(tags=["permissions"])

DEFAULT_PERMISSION_MATRIX: dict[str, dict[str, list[str]]] = {
    "customers": {
        "view": ["marketing", "sales", "finance"],
        "create": ["marketing", "sales"],
        "update": ["marketing", "sales"],
        "delete": [],
    },
    "po": {
        "view": ["marketing", "ppic", "sales", "production", "finance"],
        "create": ["marketing", "ppic", "sales"],
        "update": ["marketing", "ppic", "finance"],
        "delete": [],
        "advance": ["marketing", "ppic"],
    },
    "production": {
        "view": ["production", "ppic", "qc"],
        "create": ["production", "ppic"],
        "update": ["production"],
    },
    "qc": {
        "view": ["qc", "warehouse", "production"],
        "create": ["qc"],
        "update": ["qc"],
    },
    "packing": {
        "view": ["warehouse"],
        "create": ["warehouse"],
        "update": ["warehouse"],
        "print": ["warehouse"],
    },
    "delivery": {
        "view": ["warehouse", "marketing"],
        "create": ["warehouse"],
        "update": ["warehouse"],
        "print": ["warehouse", "marketing"],
    },
    "invoice": {
        "view": ["finance"],
        "create": ["finance"],
        "update": ["finance"],
    },
    "reports": {
        "view": ["marketing", "ppic", "finance", "exim", "sales"],
        "export": ["marketing", "ppic", "finance", "exim", "sales"],
    },
    "masterImport": {"view": [], "create": []},
    "userAccess": {"view": [], "create": [], "update": []},
}


def _write_matrix(db: Session, matrix: dict[str, dict[str, list[str]]]) -> None:
    db.query(RolePermission).delete()
    for module_key, actions in matrix.items():
        if not isinstance(actions, dict):
            continue
        for action, roles in actions.items():
            if not isinstance(roles, list):
                continue
            for role in roles:
                db.add(
                    RolePermission(
                        role=str(role).strip(),
                        module_key=str(module_key).strip(),
                        action=str(action).strip(),
                        allowed=True,
                    )
                )
    db.commit()


def ensure_default_permissions(db: Session) -> None:
    n = db.query(RolePermission).count()
    if n == 0:
        _write_matrix(db, DEFAULT_PERMISSION_MATRIX)


@router.get("/permissions/matrix")
def get_permission_matrix(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict:
    ensure_default_permissions(db)
    rows = db.scalars(select(RolePermission).order_by(RolePermission.role.asc(), RolePermission.module_key.asc())).all()
    out: dict[str, dict[str, list[str]]] = {}
    for r in rows:
        if not r.allowed:
            continue
        out.setdefault(r.module_key, {})
        out[r.module_key].setdefault(r.action, [])
        out[r.module_key][r.action].append(r.role)
    return {"matrix": out}


@router.put("/permissions/matrix")
def save_permission_matrix(
    body: dict,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict:
    matrix = (body or {}).get("matrix") or {}
    _write_matrix(db, matrix)
    return {"status": "ok"}

