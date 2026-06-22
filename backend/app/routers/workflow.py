"""PPIC workflow endpoints - assign PO to PPIC users."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from decimal import Decimal

from app.db import get_db
from app.models import OutstandingMaterial, PoDetail, PoHeader, PpicsAssignment, User
from app.routers.auth import get_current_user
from app.schemas import (
    OutstandingMaterialCreate,
    OutstandingMaterialOut,
    OutstandingMaterialUpdate,
    PpicsAssignmentCreate,
    PpicsAssignmentOut,
    PpicsAssignmentUpdate,
    UserOut,
)

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
    db.flush()
    from app.services.mkt_workflow import sync_mkt_workflow_auto_advance

    sync_mkt_workflow_auto_advance(db, po_id, actor=_user.username)
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


# --- Outstanding Materials ---
@router.get("/outstanding-materials", response_model=list[OutstandingMaterialOut])
def list_outstanding_materials(
    db: Session = Depends(get_db),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    status: Optional[str] = Query(None, description="Filter by status (pending, partial, fulfilled)"),
    _user: User = Depends(get_current_user),
) -> list[OutstandingMaterialOut]:
    query = (
        select(OutstandingMaterial)
        .options(selectinload(OutstandingMaterial.po_detail).selectinload(PoDetail.po))
        .order_by(OutstandingMaterial.id.desc())
    )

    if customer_id:
        query = query.join(PoDetail).join(PoHeader).where(PoHeader.customer_id == customer_id)
    if status:
        query = query.where(OutstandingMaterial.status == status)

    materials = db.scalars(query).all()

    result = []
    for m in materials:
        po = m.po_detail.po if m.po_detail else None
        result.append(OutstandingMaterialOut(
            id=m.id,
            po_detail_id=m.po_detail_id,
            material_name=m.material_name,
            total_qty=m.total_qty,
            delivered_qty=m.delivered_qty,
            balance_qty=m.balance_qty,
            status=m.status,
            updated_at=m.updated_at,
            po_number=po.po_number if po else None,
            customer_id=po.customer_id if po else None,
            customer_name=po.customer_name_snapshot if po else None,
        ))
    return result


@router.post("/outstanding-materials", response_model=OutstandingMaterialOut)
def create_outstanding_material(
    body: OutstandingMaterialCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> OutstandingMaterialOut:
    po_detail = db.scalars(select(PoDetail).where(PoDetail.id == body.po_detail_id)).first()
    if not po_detail:
        raise HTTPException(status_code=404, detail="PO Detail tidak ditemukan")

    total_qty = body.total_qty or Decimal("0")
    delivered_qty = body.delivered_qty or Decimal("0")
    balance_qty = total_qty - delivered_qty
    if balance_qty < 0:
        balance_qty = Decimal("0")

    if balance_qty == 0:
        status = "fulfilled"
    elif delivered_qty > 0:
        status = "partial"
    else:
        status = "pending"

    material = OutstandingMaterial(
        po_detail_id=body.po_detail_id,
        material_name=body.material_name,
        total_qty=total_qty,
        delivered_qty=delivered_qty,
        balance_qty=balance_qty,
        status=status,
        updated_at=datetime.utcnow(),
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    po = po_detail.po
    return OutstandingMaterialOut(
        id=material.id,
        po_detail_id=material.po_detail_id,
        material_name=material.material_name,
        total_qty=material.total_qty,
        delivered_qty=material.delivered_qty,
        balance_qty=material.balance_qty,
        status=material.status,
        updated_at=material.updated_at,
        po_number=po.po_number if po else None,
        customer_id=po.customer_id if po else None,
        customer_name=po.customer_name_snapshot if po else None,
    )


@router.put("/outstanding-materials/{material_id}", response_model=OutstandingMaterialOut)
def update_outstanding_material(
    material_id: int,
    body: OutstandingMaterialUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> OutstandingMaterialOut:
    material = db.scalars(
        select(OutstandingMaterial)
        .options(selectinload(OutstandingMaterial.po_detail).selectinload(PoDetail.po))
        .where(OutstandingMaterial.id == material_id)
    ).first()

    if not material:
        raise HTTPException(status_code=404, detail="Material tidak ditemukan")

    if body.material_name is not None:
        material.material_name = body.material_name
    if body.total_qty is not None:
        material.total_qty = body.total_qty
    if body.delivered_qty is not None:
        material.delivered_qty = body.delivered_qty
        material.balance_qty = (material.total_qty or Decimal("0")) - (body.delivered_qty or Decimal("0"))
        if material.balance_qty < 0:
            material.balance_qty = Decimal("0")
    if body.balance_qty is not None:
        material.balance_qty = body.balance_qty
    if body.status is not None:
        material.status = body.status

    material.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(material)

    po = material.po_detail.po if material.po_detail else None
    return OutstandingMaterialOut(
        id=material.id,
        po_detail_id=material.po_detail_id,
        material_name=material.material_name,
        total_qty=material.total_qty,
        delivered_qty=material.delivered_qty,
        balance_qty=material.balance_qty,
        status=material.status,
        updated_at=material.updated_at,
        po_number=po.po_number if po else None,
        customer_id=po.customer_id if po else None,
        customer_name=po.customer_name_snapshot if po else None,
    )


@router.delete("/outstanding-materials/{material_id}")
def delete_outstanding_material(
    material_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> dict:
    material = db.scalars(select(OutstandingMaterial).where(OutstandingMaterial.id == material_id)).first()
    if not material:
        raise HTTPException(status_code=404, detail="Material tidak ditemukan")

    db.delete(material)
    db.commit()
    return {"message": "Material berhasil dihapus"}


@router.post("/outstanding-materials/generate-from-po/{po_id}", response_model=list[OutstandingMaterialOut])
def generate_outstanding_materials_from_po(
    po_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[OutstandingMaterialOut]:
    po = db.scalars(select(PoHeader).where(PoHeader.id == po_id)).first()
    if not po:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")

    details = db.scalars(select(PoDetail).where(PoDetail.po_id == po_id)).all()

    result = []
    for detail in details:
        existing = db.scalars(
            select(OutstandingMaterial)
            .where(OutstandingMaterial.po_detail_id == detail.id)
        ).first()
        if existing:
            continue

        total_qty = detail.quantity_order or Decimal("0")
        delivered_qty = Decimal("0")
        balance_qty = total_qty

        material = OutstandingMaterial(
            po_detail_id=detail.id,
            material_name=detail.material_name,
            total_qty=total_qty,
            delivered_qty=delivered_qty,
            balance_qty=balance_qty,
            status="pending",
            updated_at=datetime.utcnow(),
        )
        db.add(material)
        result.append(material)

    db.commit()

    materials = []
    for m in result:
        db.refresh(m)
        po_detail = db.scalars(select(PoDetail).where(PoDetail.id == m.po_detail_id)).first()
        po = po_detail.po if po_detail else None
        materials.append(OutstandingMaterialOut(
            id=m.id,
            po_detail_id=m.po_detail_id,
            material_name=m.material_name,
            total_qty=m.total_qty,
            delivered_qty=m.delivered_qty,
            balance_qty=m.balance_qty,
            status=m.status,
            updated_at=m.updated_at,
            po_number=po.po_number if po else None,
            customer_id=po.customer_id if po else None,
            customer_name=po.customer_name_snapshot if po else None,
        ))

    return materials


@router.put("/outstanding-materials/{material_id}/deliver", response_model=OutstandingMaterialOut)
def deliver_outstanding_material(
    material_id: int,
    body: dict,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> OutstandingMaterialOut:
    qty = body.get("delivered_qty")
    if qty is None:
        raise HTTPException(status_code=400, detail="delivered_qty diperlukan")

    material = db.scalars(
        select(OutstandingMaterial)
        .options(selectinload(OutstandingMaterial.po_detail).selectinload(PoDetail.po))
        .where(OutstandingMaterial.id == material_id)
    ).first()

    if not material:
        raise HTTPException(status_code=404, detail="Material tidak ditemukan")

    material.delivered_qty = Decimal(str(qty))
    material.balance_qty = (material.total_qty or Decimal("0")) - material.delivered_qty
    if material.balance_qty < 0:
        material.balance_qty = Decimal("0")

    if material.balance_qty == 0:
        material.status = "fulfilled"
    elif material.delivered_qty > 0:
        material.status = "partial"
    else:
        material.status = "pending"

    material.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(material)

    po = material.po_detail.po if material.po_detail else None
    return OutstandingMaterialOut(
        id=material.id,
        po_detail_id=material.po_detail_id,
        material_name=material.material_name,
        total_qty=material.total_qty,
        delivered_qty=material.delivered_qty,
        balance_qty=material.balance_qty,
        status=material.status,
        updated_at=material.updated_at,
        po_number=po.po_number if po else None,
        customer_id=po.customer_id if po else None,
        customer_name=po.customer_name_snapshot if po else None,
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

    from app.services.mkt_workflow import sync_mkt_workflow_auto_advance

    sync_mkt_workflow_auto_advance(db, assignment.po_id, actor=_user.username)
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
