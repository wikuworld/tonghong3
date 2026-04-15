"""PPIC workflow endpoints - assign PO to PPIC users."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import PoHeader, PpicsAssignment, User
from app.routers.auth import get_current_user
from app.schemas import PpicsAssignmentCreate, PpicsAssignmentOut, PpicsAssignmentUpdate, UserOut

router = APIRouter(prefix="/workflow", tags=["workflow"])


def _assignment_to_out(assignment: PpicsAssignment, po: Optional[PoHeader] = None, user: Optional[User] = None) -> dict:
    return {
        "id": assignment.id,
        "po_id": assignment.po_id,
        "ppic_user_id": assignment.ppic_user_id,
        "status": assignment.status,
        "notes": assignment.notes,
        "assigned_at": assignment.assigned_at,
        "completed_at": assignment.completed_at,
        "po_number": po.po_number if po else None,
        "customer_name": po.customer_name_snapshot if po else None,
        "ppic_username": user.username if user else None,
    }


@router.post("/po/{po_id}/assign-to-ppic", response_model=PpicsAssignmentOut)
def assign_po_to_ppic(
    po_id: int,
    body: PpicsAssignmentCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> PpicsAssignmentOut:
    po = db.scalars(select(PoHeader).where(PoHeader.id == po_id)).first()
    if not po:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")

    if body.ppic_user_id:
        ppic_user = db.scalars(select(User).where(User.id == body.ppic_user_id)).first()
        if not ppic_user:
            raise HTTPException(status_code=404, detail="User PPIC tidak ditemukan")

    existing = db.scalars(
        select(PpicsAssignment)
        .where(PpicsAssignment.po_id == po_id, PpicsAssignment.status.in_(["pending", "in_progress"]))
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="PO sudah memiliki assignment aktif")

    assignment = PpicsAssignment(
        po_id=po_id,
        ppic_user_id=body.ppic_user_id,
        notes=body.notes,
        status="pending",
        assigned_at=datetime.utcnow(),
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return PpicsAssignmentOut(
        id=assignment.id,
        po_id=assignment.po_id,
        ppic_user_id=assignment.ppic_user_id,
        status=assignment.status,
        notes=assignment.notes,
        assigned_at=assignment.assigned_at,
        completed_at=assignment.completed_at,
        po_number=po.po_number,
        customer_name=po.customer_name_snapshot,
        ppic_username=ppic_user.username if body.ppic_user_id else None,
    )


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
        result.append(PpicsAssignmentOut(
            id=a.id,
            po_id=a.po_id,
            ppic_user_id=a.ppic_user_id,
            status=a.status,
            notes=a.notes,
            assigned_at=a.assigned_at,
            completed_at=a.completed_at,
            po_number=a.po.po_number if a.po else None,
            customer_name=a.po.customer_name_snapshot if a.po else None,
            ppic_username=a.ppic_user.username if a.ppic_user else None,
        ))
    return result


@router.put("/ppic/assignments/{assignment_id}/status", response_model=PpicsAssignmentOut)
def update_assignment_status(
    assignment_id: int,
    body: PpicsAssignmentUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> PpicsAssignmentOut:
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
            assignment.completed_at = datetime.utcnow()

    if body.notes is not None:
        assignment.notes = body.notes

    db.commit()
    db.refresh(assignment)

    return PpicsAssignmentOut(
        id=assignment.id,
        po_id=assignment.po_id,
        ppic_user_id=assignment.ppic_user_id,
        status=assignment.status,
        notes=assignment.notes,
        assigned_at=assignment.assigned_at,
        completed_at=assignment.completed_at,
        po_number=assignment.po.po_number if assignment.po else None,
        customer_name=assignment.po.customer_name_snapshot if assignment.po else None,
        ppic_username=assignment.ppic_user.username if assignment.ppic_user else None,
    )


@router.get("/ppic/users", response_model=list[UserOut])
def list_ppic_users(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[UserOut]:
    ppic_users = db.scalars(
        select(User)
        .where(User.department == "ppic", User.is_active == True)
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

    return PpicsAssignmentOut(
        id=assignment.id,
        po_id=assignment.po_id,
        ppic_user_id=assignment.ppic_user_id,
        status=assignment.status,
        notes=assignment.notes,
        assigned_at=assignment.assigned_at,
        completed_at=assignment.completed_at,
        po_number=assignment.po.po_number if assignment.po else None,
        customer_name=assignment.po.customer_name_snapshot if assignment.po else None,
        ppic_username=assignment.ppic_user.username if assignment.ppic_user else None,
    )
