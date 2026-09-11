"""PPIC workflow endpoints — serah terima SO ke tim PPIC (otomatis di pipeline MKT)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.timeutil import app_now
from app.models import PoHeader, PpicsAssignment, User
from app.routers.auth import get_current_user, require_roles
from app.schemas import (
    PpicsAssignmentCreate,
    PpicsAssignmentOut,
    PpicsAssignmentUpdate,
    UserOut,
)

router = APIRouter(prefix="/workflow", tags=["workflow"])

AUTO_ASSIGN_PREFIX = "[auto]"


def _is_auto_assignment(notes: Optional[str]) -> bool:
    return (notes or "").strip().startswith(AUTO_ASSIGN_PREFIX)


def _first_active_ppic_user(db: Session) -> Optional[User]:
    from sqlalchemy import func, or_

    return db.scalars(
        select(User)
        .where(
            User.is_active.is_(True),
            or_(
                func.lower(func.coalesce(User.role, "")) == "ppic",
                func.lower(func.coalesce(User.department, "")) == "ppic",
            ),
        )
        .order_by(User.id.asc())
    ).first()


def _assignment_to_out(
    assignment: PpicsAssignment, po: Optional[PoHeader] = None, user: Optional[User] = None
) -> dict:
    header = po if po is not None else getattr(assignment, "po", None)
    ppic_user = user if user is not None else getattr(assignment, "ppic_user", None)
    auto = _is_auto_assignment(assignment.notes)
    return {
        "id": assignment.id,
        "po_id": assignment.po_id,
        "ppic_user_id": assignment.ppic_user_id,
        "status": assignment.status,
        "notes": assignment.notes,
        "assigned_at": assignment.assigned_at,
        "completed_at": assignment.completed_at,
        "po_number": header.po_number if header else None,
        "customer_name": header.customer_name_snapshot if header else None,
        "ppic_username": "Tim PPIC" if auto else (ppic_user.username if ppic_user else None),
        "item_revised_at": getattr(header, "item_revised_at", None) if header else None,
        "item_revised_has_update": bool(getattr(header, "item_revised_has_update", False)) if header else False,
        "item_revised_has_delete": bool(getattr(header, "item_revised_has_delete", False)) if header else False,
        "assignment_mode": "auto" if auto else "named",
    }


def _assignment_out_model(
    assignment: PpicsAssignment, po: Optional[PoHeader] = None, user: Optional[User] = None
) -> PpicsAssignmentOut:
    return PpicsAssignmentOut(**_assignment_to_out(assignment, po=po, user=user))


@router.post("/po/{po_id}/assign-to-ppic", response_model=PpicsAssignmentOut)
def assign_po_to_ppic(
    po_id: int,
    body: PpicsAssignmentCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin", "marketing", "ppic")),
) -> PpicsAssignmentOut:
    """Serahkan SO ke tim PPIC. Tanpa ppic_user_id = mode otomatis (pool monitoring)."""
    po = db.scalars(select(PoHeader).where(PoHeader.id == po_id)).first()
    if not po:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")

    # Alur MKT: Confirm SO langsung Outstanding. Assign legacy tetap boleh setelah confirm.
    status_norm = (po.status or "").strip().lower()
    if status_norm not in {"confirmed", "production", "completed"}:
        raise HTTPException(
            status_code=400,
            detail="PO harus di-confirm dulu sebelum assign ke PPIC",
        )
    notes = (body.notes or "").strip() or None
    ppic_user_id = body.ppic_user_id
    if ppic_user_id:
        ppic_user = db.scalars(select(User).where(User.id == ppic_user_id)).first()
        if not ppic_user:
            raise HTTPException(status_code=404, detail="User PPIC tidak ditemukan")
        if (ppic_user.department or "").strip().lower() != "ppic" and (ppic_user.role or "").strip().lower() != "ppic":
            raise HTTPException(status_code=400, detail="User yang dipilih bukan PPIC")
    else:
        # Mode otomatis: satu baris pool (bukan N baris untuk semua user PPIC).
        ppic_user = _first_active_ppic_user(db)
        if not ppic_user:
            raise HTTPException(
                status_code=400,
                detail="Tidak ada user PPIC aktif untuk serah terima otomatis",
            )
        ppic_user_id = int(ppic_user.id)
        if not _is_auto_assignment(notes):
            extra = f" — {notes}" if notes else ""
            notes = f"{AUTO_ASSIGN_PREFIX} Serah terima otomatis ke tim PPIC{extra}"

    existing = db.scalars(
        select(PpicsAssignment)
        .where(PpicsAssignment.po_id == po_id, PpicsAssignment.status.in_(["pending", "in_progress"]))
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="PO sudah memiliki assignment aktif")

    assignment = PpicsAssignment(
        po_id=po_id,
        ppic_user_id=ppic_user_id,
        notes=notes,
        status="pending",
        assigned_at=app_now(),
    )
    db.add(assignment)
    db.flush()
    from app.services.mkt_workflow import sync_mkt_workflow_auto_advance

    sync_mkt_workflow_auto_advance(db, po_id, actor=_user.username)
    db.commit()
    db.refresh(assignment)

    return _assignment_out_model(assignment)


@router.get("/ppic/dashboard", response_model=list[PpicsAssignmentOut])
def ppic_dashboard(
    db: Session = Depends(get_db),
    user_id: Optional[int] = Query(None, description="Filter by PPIC user ID"),
    status: Optional[str] = Query(None, description="Filter by status (pending, in_progress, completed)"),
    _user: User = Depends(get_current_user),
) -> list[PpicsAssignmentOut]:
    query = (
        select(PpicsAssignment)
        .options(selectinload(PpicsAssignment.po), selectinload(PpicsAssignment.ppic_user))
        .order_by(PpicsAssignment.assigned_at.desc())
    )

    if user_id:
        query = query.where(PpicsAssignment.ppic_user_id == user_id)
    if status:
        query = query.where(PpicsAssignment.status == status)

    assignments = db.scalars(query).all()

    result = []
    for a in assignments:
        result.append(_assignment_out_model(a))
    return result


@router.put("/ppic/assignments/{assignment_id}/status", response_model=PpicsAssignmentOut)
def update_assignment_status(
    assignment_id: int,
    body: PpicsAssignmentUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin", "marketing")),
) -> PpicsAssignmentOut:
    """Selesaikan gate PPIC dari Alur Marketing (dashboard PPIC hanya monitoring)."""
    assignment = db.scalars(
        select(PpicsAssignment)
        .options(selectinload(PpicsAssignment.po), selectinload(PpicsAssignment.ppic_user))
        .where(PpicsAssignment.id == assignment_id)
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment tidak ditemukan")

    if body.status:
        valid_statuses = ["pending", "in_progress", "completed"]
        if body.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Status harus salah satu dari: {valid_statuses}")
        assignment.status = body.status
        if body.status == "completed":
            assignment.completed_at = app_now()

    if body.notes is not None:
        assignment.notes = body.notes

    from app.services.mkt_workflow import sync_mkt_workflow_auto_advance

    db.flush()
    sync_mkt_workflow_auto_advance(db, assignment.po_id, actor=_user.username)
    db.commit()
    db.refresh(assignment)

    return _assignment_out_model(assignment)


@router.get("/ppic/users", response_model=list[UserOut])
def list_ppic_users(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[UserOut]:
    ppic_users = db.scalars(
        select(User)
        .where(User.department == "ppic", User.is_active)
        .order_by(User.username)
    ).all()

    return [UserOut.model_validate(u) for u in ppic_users]


@router.get("/po/{po_id}/ppic-assignment", response_model=Optional[PpicsAssignmentOut])
def get_po_ppic_assignment(
    po_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> Optional[PpicsAssignmentOut]:
    assignment = db.scalars(
        select(PpicsAssignment)
        .options(selectinload(PpicsAssignment.po), selectinload(PpicsAssignment.ppic_user))
        .where(PpicsAssignment.po_id == po_id)
        .order_by(PpicsAssignment.id.desc())
        .limit(1)
    ).first()

    if not assignment:
        return None

    return _assignment_out_model(assignment)
