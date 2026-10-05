"""PPIC workflow endpoints — serah terima SO ke tim PPIC (otomatis di pipeline MKT)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.timeutil import app_now
from app.models import OutstandingMaterial, PoDetail, PoHeader, PpicsAssignment, User
from app.paging import apply_sort, page_dict, parse_page_params
from app.routers.auth import get_current_user, require_roles
from app.schemas import (
    OutstandingMaterialCreate,
    OutstandingMaterialOut,
    OutstandingMaterialPageOut,
    OutstandingMaterialUpdate,
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

    # Meeting 17/9: PPIC completed → stock sisa (MRP) status approved
    if (assignment.status or "").strip().lower() == "completed" and assignment.po_id:
        try:
            import httpx
            from app.config import settings

            base = (settings.mrp_upstream_url or "http://127.0.0.1:8002").rstrip("/")
            with httpx.Client(timeout=8.0) as client:
                client.post(f"{base}/api/mrp/stock-sisa/sync-ppic")
        except Exception:
            pass

    return _assignment_out_model(assignment)


# --- Outstanding Materials ---


def _outstanding_material_out(m: OutstandingMaterial) -> OutstandingMaterialOut:
    po = m.po_detail.po if m.po_detail else None
    return OutstandingMaterialOut(
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
    )


@router.get("/outstanding-materials", response_model=OutstandingMaterialPageOut)
def list_outstanding_materials(
    db: Session = Depends(get_db),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    status: Optional[str] = Query(None, description="Filter by status (pending, partial, fulfilled)"),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="id|status|updated_at|material_name"),
    sort_dir: Optional[str] = Query(None),
    _user: User = Depends(get_current_user),
) -> dict:
    params = parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_dir=sort_dir or "desc",
        default_page_size=20,
    )
    filters = []
    join_po = customer_id is not None
    if status:
        filters.append(OutstandingMaterial.status == status)

    count_stmt = select(func.count(OutstandingMaterial.id))
    stmt = select(OutstandingMaterial).options(
        selectinload(OutstandingMaterial.po_detail).selectinload(PoDetail.po)
    )
    if join_po or customer_id:
        count_stmt = count_stmt.join(PoDetail, OutstandingMaterial.po_detail_id == PoDetail.id).join(
            PoHeader, PoDetail.po_id == PoHeader.id
        )
        stmt = stmt.join(PoDetail, OutstandingMaterial.po_detail_id == PoDetail.id).join(
            PoHeader, PoDetail.po_id == PoHeader.id
        )
        if customer_id:
            filters.append(PoHeader.customer_id == customer_id)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "id": OutstandingMaterial.id,
            "status": OutstandingMaterial.status,
            "updated_at": OutstandingMaterial.updated_at,
            "material_name": OutstandingMaterial.material_name,
            "created_at": OutstandingMaterial.updated_at,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(OutstandingMaterial.id.desc(),),
    )
    materials = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    items = [_outstanding_material_out(m) for m in materials]
    return page_dict(items=items, total=total, params=params)


@router.post("/outstanding-materials", response_model=OutstandingMaterialOut)
def create_outstanding_material(
    body: OutstandingMaterialCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin", "marketing", "ppic")),
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
        updated_at=app_now(),
    )
    db.add(material)
    db.commit()
    db.refresh(material)

    po_detail = db.scalars(
        select(PoDetail).options(selectinload(PoDetail.po)).where(PoDetail.id == material.po_detail_id)
    ).first()
    material.po_detail = po_detail
    return _outstanding_material_out(material)


@router.put("/outstanding-materials/{material_id}", response_model=OutstandingMaterialOut)
def update_outstanding_material(
    material_id: int,
    body: OutstandingMaterialUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin", "marketing", "ppic")),
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

    material.updated_at = app_now()
    db.commit()
    db.refresh(material)

    return _outstanding_material_out(material)


@router.delete("/outstanding-materials/{material_id}")
def delete_outstanding_material(
    material_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin", "marketing", "ppic")),
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
    _user: User = Depends(require_roles("admin", "marketing", "ppic")),
) -> list[OutstandingMaterialOut]:
    po = db.scalars(select(PoHeader).where(PoHeader.id == po_id)).first()
    if not po:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")

    details = db.scalars(select(PoDetail).where(PoDetail.po_id == po_id)).all()

    result = []
    for detail in details:
        existing = db.scalars(
            select(OutstandingMaterial).where(OutstandingMaterial.po_detail_id == detail.id)
        ).first()
        if existing:
            continue

        total_qty = detail.quantity_order or Decimal("0")
        material = OutstandingMaterial(
            po_detail_id=detail.id,
            material_name=detail.material_name,
            total_qty=total_qty,
            delivered_qty=Decimal("0"),
            balance_qty=total_qty,
            status="pending",
            updated_at=app_now(),
        )
        db.add(material)
        result.append(material)

    db.commit()

    materials = []
    for m in result:
        db.refresh(m)
        po_detail = db.scalars(
            select(PoDetail).options(selectinload(PoDetail.po)).where(PoDetail.id == m.po_detail_id)
        ).first()
        m.po_detail = po_detail
        materials.append(_outstanding_material_out(m))

    return materials


@router.put("/outstanding-materials/{material_id}/deliver", response_model=OutstandingMaterialOut)
def deliver_outstanding_material(
    material_id: int,
    body: dict,
    db: Session = Depends(get_db),
    _user: User = Depends(require_roles("admin", "marketing", "ppic")),
) -> OutstandingMaterialOut:
    qty = body.get("delivered_qty")
    if qty is None:
        raise HTTPException(status_code=400, detail="delivered_qty diperlukan")

    increment = Decimal(str(qty))
    if increment <= 0:
        raise HTTPException(status_code=400, detail="delivered_qty harus lebih dari 0")

    material = db.scalars(
        select(OutstandingMaterial)
        .options(selectinload(OutstandingMaterial.po_detail).selectinload(PoDetail.po))
        .where(OutstandingMaterial.id == material_id)
    ).first()

    if not material:
        raise HTTPException(status_code=404, detail="Material tidak ditemukan")

    new_delivered = (material.delivered_qty or Decimal("0")) + increment
    total = material.total_qty or Decimal("0")
    if new_delivered > total:
        raise HTTPException(status_code=400, detail="Qty kirim melebihi sisa outstanding")

    material.delivered_qty = new_delivered
    material.balance_qty = total - new_delivered
    if material.balance_qty < 0:
        material.balance_qty = Decimal("0")

    if material.balance_qty == 0:
        material.status = "fulfilled"
    elif material.delivered_qty > 0:
        material.status = "partial"
    else:
        material.status = "pending"

    material.updated_at = app_now()
    db.commit()
    db.refresh(material)

    return _outstanding_material_out(material)


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
