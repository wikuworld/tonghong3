import logging
import re
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Brand, CustomerBrandMapping, FluorescentColorMaster, PoDetail, PoDetailDelivery, PoHeader, SubconInvoice, PpicsAssignment
from app.services.audit import log_change
from app.services.numbering import next_number, peek_number
from app.schemas import (
    DeliveryScheduleItem,
    DeliverySchedulesPayload,
    LotGenerateIn,
    LotGenerateOut,
    PoDetailCreate,
    PoDetailDeliveryOut,
    PoDetailOut,
    PoDetailUpdate,
    PoHeaderCreate,
    PoHeaderOut,
    PoHeaderPageOut,
    PoHeaderUpdate,
    PoMaterialHintsOut,
    PoMaterialHintItemOut,
    PoMarketingReviseBody,
    MktWorkflowStagesOut,
    StatusDeletedOut,
)
from app.services.business_rules import validate_po_status_transition
from app.services.mkt_workflow import (
    MKT_STAGES_ORDER,
    apply_mkt_stage,
    get_stuck_reason,
    next_mkt_stage,
    prev_mkt_stage,
    sync_mkt_workflow_auto_advance,
    validate_mkt_advance,
)
from app.services.po_header_snapshots import apply_header_snapshots, resolve_header_snapshots_for_list
from app.services.po_list_summary import attach_po_list_summaries, compute_po_list_summaries, serialize_po_headers_for_list
from app.services.lot_numbers import (
    _material_group_from_inputs,
    generate_lot_number,
    generate_po_detail_lot_number,
    peek_lot_number,
)
from app.services.notifications import create_notification_for_roles
from app.routers.auth import get_current_user, require_roles

router = APIRouter(tags=["po"])

PO_MAX_DELIVERY_SCHEDULES = 21
log = logging.getLogger(__name__)


def _parse_query_date(s: Optional[str]) -> Optional[date]:
    if not s or not str(s).strip():
        return None
    try:
        return date.fromisoformat(str(s).strip()[:10])
    except ValueError:
        return None

_ALLOWED_PO_CATEGORY_DUP = frozenset(
    {"production", "sample", "claim", "return", "subcont", "suede"},
)


def _normalize_po_category_duplicate(raw: Optional[str]) -> str:
    v = (raw or "production").strip().lower()
    return v if v in _ALLOWED_PO_CATEGORY_DUP else "production"


# Field skalar PoDetail yang disalin saat duplikasi PO (tanpa jadwal kirim).
_PO_DETAIL_DUPLICATE_FIELDS = (
    "master_item_id",
    "material_name",
    "color",
    "color_family",
    "thickness_min",
    "thickness_max",
    "thickness_text",
    "emboss",
    "vir_softness_type",
    "softness",
    "color_reference",
    "color_standard",
    "backing",
    "quantity_order",
    "style_article",
    "model",
    "line_etd",
    "rtd_text",
    "etd_excel_serial",
    "stock_wh_qty",
    "balance_qty",
    "system_reference",
    "detail_remark",
    "unit_price",
)


def _detail_loaded(db: Session, detail_id: int) -> Optional[PoDetail]:
    return db.scalars(
        select(PoDetail)
        .options(selectinload(PoDetail.delivery_schedules))
        .where(PoDetail.id == detail_id)
    ).first()


def _normalize_po_customer_ref(raw: Optional[str]) -> str:
    return (raw or "").strip()


def _find_po_customer_ref_conflict(
    db: Session,
    *,
    customer_id: Optional[int],
    po_customer_ref: Optional[str],
    exclude_po_id: Optional[int] = None,
) -> Optional[PoHeader]:
    ref = _normalize_po_customer_ref(po_customer_ref)
    if not ref or customer_id is None:
        return None
    stmt = select(PoHeader).where(
        PoHeader.customer_id == customer_id,
        func.lower(func.trim(PoHeader.po_customer_ref)) == ref.lower(),
    )
    if exclude_po_id is not None:
        stmt = stmt.where(PoHeader.id != exclude_po_id)
    return db.scalars(stmt).first()


def _validate_po_customer_ref_unique(
    db: Session,
    *,
    customer_id: Optional[int],
    po_customer_ref: Optional[str],
    exclude_po_id: Optional[int] = None,
) -> None:
    ref = _normalize_po_customer_ref(po_customer_ref)
    if not ref or customer_id is None:
        return
    existing = _find_po_customer_ref_conflict(
        db,
        customer_id=customer_id,
        po_customer_ref=ref,
        exclude_po_id=exclude_po_id,
    )
    if existing:
        po_label = existing.po_number or f"ID {existing.id}"
        raise HTTPException(
            status_code=409,
            detail=f"No. PO customer '{ref}' sudah dipakai pada {po_label}.",
        )


def _validate_customer_brand_buyer(db: Session, data: dict) -> None:
    customer_id = data.get("customer_id")
    brand_id = data.get("brand_id")
    if not brand_id:
        return
    brand = db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=400, detail="Brand tidak ditemukan")
    if customer_id:
        mapping = db.scalars(
            select(CustomerBrandMapping).where(
                CustomerBrandMapping.customer_id == customer_id,
                CustomerBrandMapping.brand_id == brand_id,
            )
        ).first()
        if not mapping:
            raise HTTPException(status_code=400, detail="Brand tidak terkait customer terpilih")


def _season_candidates_from_date(order_date) -> list[str]:
    if not order_date:
        return []
    year = int(order_date.year)
    month = int(order_date.month)
    if month <= 6:
        return [f"SS {year}", f"SPSU {year}", f"SP/SU {str(year)[-2:]}"]
    return [f"FW {year}", f"FA/HO {str(year)[-2:]}", f"FAHO {str(year)[-2:]}"]


def _validate_fluorescent_color_master(
    db: Session,
    po: PoHeader,
    *,
    color_family: Optional[str],
    color: Optional[str],
) -> None:
    if (color_family or "").strip().lower() != "fluorescent":
        return
    color_raw = (color or "").strip()
    if not color_raw:
        return
    buyer_code = (po.buyer or "").strip().upper()
    if not buyer_code:
        return
    strict_buyers = {"NB", "ADIDAS", "UA", "NIKE", "OIA", "OIA NIKE"}

    color_norm = re.sub(r"\s+", " ", color_raw).strip().lower()
    color_code_hint = None
    m = re.search(r"\(([A-Za-z0-9\-]+)\)\s*$", color_raw)
    if m:
        color_code_hint = m.group(1).strip().lower()

    season_labels = _season_candidates_from_date(po.order_date)
    season_set = {s.lower() for s in season_labels}

    rows = db.scalars(
        select(FluorescentColorMaster).where(
            FluorescentColorMaster.buyer_code.in_([buyer_code, "GLOBAL"]),
            FluorescentColorMaster.is_active.is_(True),
        )
    ).all()
    if buyer_code not in strict_buyers and not any(r.buyer_code == buyer_code for r in rows):
        return

    def row_match(row: FluorescentColorMaster) -> bool:
        name = re.sub(r"\s+", " ", str(row.color_name or "")).strip().lower()
        code = str(row.color_code or "").strip().lower()
        if color_norm and (color_norm == name or color_norm in name or name in color_norm):
            pass
        elif color_code_hint and code and color_code_hint == code:
            pass
        else:
            return False
        if not season_set:
            return True
        if not row.season_label:
            return True
        return str(row.season_label).strip().lower() in season_set

    if any(row_match(r) for r in rows):
        return
    raise HTTPException(
        status_code=400,
        detail=(
            f"Warna fluorescent '{color_raw}' tidak terdaftar untuk buyer {buyer_code} "
            f"pada season terkait. Silakan cek master fluorescent color."
        ),
    )


@router.get("/po/mkt-workflow-stages", response_model=MktWorkflowStagesOut)
def mkt_workflow_stages(_user=Depends(get_current_user)) -> MktWorkflowStagesOut:
    return MktWorkflowStagesOut(stages=list(MKT_STAGES_ORDER))


class NextPoNumberOut(BaseModel):
    po_number: str


class PoCustomerRefCheckOut(BaseModel):
    exists: bool
    po_number: Optional[str] = None
    po_id: Optional[int] = None


@router.get("/po/next-number", response_model=NextPoNumberOut)
def preview_next_po_number(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> NextPoNumberOut:
    """Preview nomor SO berikutnya tanpa increment sequence."""
    return NextPoNumberOut(po_number=peek_number(db, "SO", "SO"))


@router.get("/po/check-customer-ref", response_model=PoCustomerRefCheckOut)
def check_po_customer_ref(
    customer_id: int = Query(..., ge=1),
    po_customer_ref: str = Query(..., min_length=1),
    exclude_po_id: Optional[int] = Query(None, ge=1),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> PoCustomerRefCheckOut:
    """Cek apakah No. PO customer sudah dipakai untuk customer yang sama."""
    existing = _find_po_customer_ref_conflict(
        db,
        customer_id=customer_id,
        po_customer_ref=po_customer_ref,
        exclude_po_id=exclude_po_id,
    )
    if existing:
        return PoCustomerRefCheckOut(
            exists=True,
            po_number=existing.po_number,
            po_id=existing.id,
        )
    return PoCustomerRefCheckOut(exists=False)


@router.get("/po", response_model=list[PoHeaderOut])
def list_po(
    mkt_workflow_stage: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search PO no/customer/buyer"),
    customer_id: Optional[int] = Query(None),
    buyer: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    po_category: Optional[str] = Query(None),
    order_date: Optional[str] = Query(None, description="Filter by order date (YYYY-MM-DD), exact day"),
    order_date_from: Optional[str] = Query(None, description="Rentang order_date: awal (YYYY-MM-DD)"),
    order_date_to: Optional[str] = Query(None, description="Rentang order_date: akhir (YYYY-MM-DD)"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[PoHeader]:
    stmt = select(PoHeader).order_by(PoHeader.id.desc()).limit(limit).offset(offset)
    if mkt_workflow_stage:
        stmt = stmt.where(PoHeader.mkt_workflow_stage == mkt_workflow_stage)
    if customer_id is not None:
        stmt = stmt.where(PoHeader.customer_id == customer_id)
    if buyer:
        stmt = stmt.where(PoHeader.buyer == buyer)
    if status:
        stmt = stmt.where(PoHeader.status == status)
    if po_category:
        stmt = stmt.where(PoHeader.po_category == po_category)
    d_from = _parse_query_date(order_date_from)
    d_to = _parse_query_date(order_date_to)
    d_one = _parse_query_date(order_date)
    if d_from is not None or d_to is not None:
        if d_from is not None:
            stmt = stmt.where(PoHeader.order_date.is_not(None), PoHeader.order_date >= d_from)
        if d_to is not None:
            stmt = stmt.where(PoHeader.order_date.is_not(None), PoHeader.order_date <= d_to)
    elif d_one is not None:
        stmt = stmt.where(PoHeader.order_date == d_one)
    if q:
        like = f"%{q}%"
        po_ids_by_detail_material = select(PoDetail.po_id).where(PoDetail.material_name.ilike(like))
        stmt = stmt.where(
            or_(
                PoHeader.po_number.ilike(like),
                PoHeader.buyer.ilike(like),
                PoHeader.po_customer_ref.ilike(like),
                PoHeader.customer_name_snapshot.ilike(like),
                PoHeader.customer_code.ilike(like),
                PoHeader.id.in_(po_ids_by_detail_material),
            )
        )
    results = list(db.scalars(stmt).all())
    return serialize_po_headers_for_list(db, results)


@router.get("/po/page", response_model=PoHeaderPageOut)
def list_po_page(
    mkt_workflow_stage: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search PO no/customer/buyer"),
    customer_id: Optional[int] = Query(None),
    buyer: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    po_category: Optional[str] = Query(None),
    order_date: Optional[str] = Query(None, description="Filter by order date (YYYY-MM-DD), exact day"),
    order_date_from: Optional[str] = Query(None, description="Rentang order_date: awal (YYYY-MM-DD)"),
    order_date_to: Optional[str] = Query(None, description="Rentang order_date: akhir (YYYY-MM-DD)"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> PoHeaderPageOut:
    stmt = select(PoHeader)
    count_stmt = select(func.count(PoHeader.id))
    if mkt_workflow_stage:
        stmt = stmt.where(PoHeader.mkt_workflow_stage == mkt_workflow_stage)
        count_stmt = count_stmt.where(PoHeader.mkt_workflow_stage == mkt_workflow_stage)
    if customer_id is not None:
        stmt = stmt.where(PoHeader.customer_id == customer_id)
        count_stmt = count_stmt.where(PoHeader.customer_id == customer_id)
    if buyer:
        stmt = stmt.where(PoHeader.buyer == buyer)
        count_stmt = count_stmt.where(PoHeader.buyer == buyer)
    if status:
        stmt = stmt.where(PoHeader.status == status)
        count_stmt = count_stmt.where(PoHeader.status == status)
    if po_category:
        stmt = stmt.where(PoHeader.po_category == po_category)
        count_stmt = count_stmt.where(PoHeader.po_category == po_category)
    d_from = _parse_query_date(order_date_from)
    d_to = _parse_query_date(order_date_to)
    d_one = _parse_query_date(order_date)
    if d_from is not None or d_to is not None:
        if d_from is not None:
            w = (PoHeader.order_date.is_not(None), PoHeader.order_date >= d_from)
            stmt = stmt.where(*w)
            count_stmt = count_stmt.where(*w)
        if d_to is not None:
            w = (PoHeader.order_date.is_not(None), PoHeader.order_date <= d_to)
            stmt = stmt.where(*w)
            count_stmt = count_stmt.where(*w)
    elif d_one is not None:
        stmt = stmt.where(PoHeader.order_date == d_one)
        count_stmt = count_stmt.where(PoHeader.order_date == d_one)
    if q:
        like = f"%{q}%"
        po_ids_by_detail_material = select(PoDetail.po_id).where(PoDetail.material_name.ilike(like))
        where_clause = or_(
            PoHeader.po_number.ilike(like),
            PoHeader.buyer.ilike(like),
            PoHeader.po_customer_ref.ilike(like),
            PoHeader.customer_name_snapshot.ilike(like),
            PoHeader.customer_code.ilike(like),
            PoHeader.id.in_(po_ids_by_detail_material),
        )
        stmt = stmt.where(where_clause)
        count_stmt = count_stmt.where(where_clause)
    total = int(db.scalar(count_stmt) or 0)
    items = list(
        db.scalars(
            stmt.order_by(PoHeader.id.desc()).limit(limit).offset(offset)
        ).all()
    )
    items_out = serialize_po_headers_for_list(db, items)
    return PoHeaderPageOut(items=items_out, total=total, limit=limit, offset=offset)


@router.get("/po/material-hints", response_model=PoMaterialHintsOut)
def list_po_material_hints(
    po_ids: str = Query(..., description="ID PO dipisah koma, mis. 1,2,3"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> PoMaterialHintsOut:
    parsed: list[int] = []
    for part in po_ids.split(","):
        part = part.strip()
        if part.isdigit():
            parsed.append(int(part))
    if not parsed:
        return PoMaterialHintsOut(items=[])
    parsed = parsed[:200]
    summaries = compute_po_list_summaries(db, parsed)
    return PoMaterialHintsOut(
        items=[
            PoMaterialHintItemOut(
                po_id=po_id,
                detail_line_count=summary["detail_line_count"],
                material_hint=summary["material_hint"],
                etd_display=summary["etd_display"],
            )
            for po_id, summary in summaries.items()
        ]
    )


@router.post("/po/{po_id}/mkt-workflow/advance", response_model=PoHeaderOut)
def advance_mkt_workflow(
    po_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing", "ppic")),
) -> PoHeader:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    nxt = next_mkt_stage(row.mkt_workflow_stage)
    if not nxt:
        raise HTTPException(status_code=400, detail="PO sudah di tahap akhir alur MKT")
    validate_mkt_advance(db, po_id, nxt)
    apply_mkt_stage(db, po_id, nxt)
    create_notification_for_roles(
        db,
        ("admin", "marketing", "ppic"),
        title=f"PO {row.po_number or row.id} masuk tahap {nxt}",
        message=f"Tahap alur marketing diperbarui menjadi: {nxt}",
        category="workflow",
        entity_type="sales_order",
        entity_id=row.id,
        route_path="/admin/marketing-flow",
        route_query={"po_id": row.id},
    )
    log_change(
        db,
        entity_type="sales_order",
        entity_id=row.id,
        action="workflow_advance",
        after={"mkt_workflow_stage": nxt},
        actor=_user.username,
    )
    db.commit()
    db.refresh(row)
    return row


@router.post("/po/{po_id}/mkt-workflow/rollback", response_model=PoHeaderOut)
def rollback_mkt_workflow(
    po_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing", "ppic")),
) -> PoHeader:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    prev = prev_mkt_stage(row.mkt_workflow_stage)
    if not prev:
        raise HTTPException(status_code=400, detail="PO sudah di tahap awal alur MKT")
    apply_mkt_stage(db, po_id, prev)
    create_notification_for_roles(
        db,
        ("admin", "marketing", "ppic"),
        title=f"PO {row.po_number or row.id} rollback ke tahap {prev}",
        message=f"Tahap alur marketing dirollback menjadi: {prev}",
        category="workflow",
        entity_type="sales_order",
        entity_id=row.id,
        route_path="/admin/marketing-flow",
        route_query={"po_id": row.id},
    )
    log_change(
        db,
        entity_type="sales_order",
        entity_id=row.id,
        action="workflow_rollback",
        after={"mkt_workflow_stage": prev},
        actor=_user.username,
    )
    db.commit()
    db.refresh(row)
    return row


@router.post("/po", response_model=PoHeaderOut)
def create_po(
    body: PoHeaderCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "sales")),
) -> PoHeader:
    try:
        data = body.model_dump(exclude_unset=True)
        _validate_customer_brand_buyer(db, data)
        _validate_po_customer_ref_unique(
            db,
            customer_id=data.get("customer_id"),
            po_customer_ref=data.get("po_customer_ref"),
        )
        apply_header_snapshots(db, data, force=True)
        if not data.get("po_number"):
            data["po_number"] = next_number(db, "SO", "SO")
        else:
            # Check if po_number already exists, auto-generate if duplicate
            existing = db.scalars(
                select(PoHeader).where(PoHeader.po_number == data["po_number"])
            ).first()
            if existing:
                data["po_number"] = next_number(db, "SO", "SO")
        # Auto-generate po_customer_ref if empty
        if not data.get("po_customer_ref"):
            data["po_customer_ref"] = f"PO-{data['po_number']}"
        row = PoHeader(**data)
        db.add(row)
        db.flush()
        log_change(
            db,
            entity_type="sales_order",
            entity_id=row.id,
            action="create",
            after={"po_number": row.po_number, "status": row.status},
            actor=user.username,
        )
        create_notification_for_roles(
            db,
            ("admin", "marketing", "ppic"),
            title=f"PO baru {row.po_number}",
            message=f"Sales order dibuat oleh {user.username}",
            category="po",
            entity_type="sales_order",
            entity_id=row.id,
            route_path="/admin/po",
            route_query={"po_id": row.id},
        )
        db.commit()
        db.refresh(row)
        return row
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        log.warning("create_po integrity_error: %s", e)
        raise HTTPException(
            status_code=409,
            detail="Simpan PO gagal (konflik data, misalnya nomor PO unik).",
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        log.exception("create_po failed")
        orig_msg = ""
        if getattr(e, "orig", None) is not None:
            orig_msg = str(e.orig)
        low = f"{e} {orig_msg}".lower()
        if "unknown column" in low or "doesn't exist" in low or "does not exist" in low:
            raise HTTPException(
                status_code=503,
                detail="Skema database belum selaras dengan kode. Jalankan migrasi: alembic upgrade head (folder backend).",
            ) from e
        raise HTTPException(
            status_code=500,
            detail="Simpan PO gagal (database). Cek log server untuk detail.",
        ) from e


@router.post("/po/{po_id}/duplicate", response_model=PoHeaderOut)
def duplicate_po(
    po_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "sales")),
) -> PoHeader:
    """Salin header + semua baris ke PO baru (draft, nomor lot baris dikosongkan)."""
    src = db.get(PoHeader, po_id)
    if not src:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")

    details_src = list(
        db.scalars(
            select(PoDetail).where(PoDetail.po_id == po_id).order_by(PoDetail.id.asc())
        ).all()
    )

    merged = {
        "customer_id": src.customer_id,
        "brand_id": src.brand_id,
        "buyer": (src.buyer or "").strip() or None,
    }
    _validate_customer_brand_buyer(db, merged)

    po_category = _normalize_po_category_duplicate(getattr(src, "po_category", None))
    snapshot_data = {
        "customer_id": src.customer_id,
        "customer_code": src.customer_code,
        "brand_id": src.brand_id,
        "brand_name_snapshot": src.brand_name_snapshot,
        "customer_name_snapshot": src.customer_name_snapshot,
    }
    apply_header_snapshots(db, snapshot_data, force=True)

    try:
        new_po = PoHeader(
            po_number=next_number(db, "SO", "SO"),
            customer_id=src.customer_id,
            customer_code=snapshot_data.get("customer_code") or src.customer_code,
            po_category=po_category,
            buyer=src.buyer,
            order_date=src.order_date,
            etd=src.etd,
            status="draft",
            billing_address=src.billing_address,
            delivery_address=src.delivery_address,
            brand_id=src.brand_id,
            marketing_excel_date_serial=None,
            po_customer_ref=src.po_customer_ref or None,
            order_type_label=src.order_type_label,
            brand_name_snapshot=snapshot_data.get("brand_name_snapshot"),
            customer_name_snapshot=snapshot_data.get("customer_name_snapshot"),
            customs_declaration_id=src.customs_declaration_id,
            mkt_workflow_stage="input_system",
            mkt_workflow_updated_at=None,
            rekap_printed_at=None,
            material_followup_remark=None,
            material_followup_done=False,
        )
        db.add(new_po)
        db.flush()

        for d in details_src:
            kwargs = {k: getattr(d, k) for k in _PO_DETAIL_DUPLICATE_FIELDS}
            db.add(
                PoDetail(
                    po_id=new_po.id,
                    thi_line_ref=None,
                    copied_from_detail_id=d.id,
                    **kwargs,
                )
            )

        # Pakai action "create" agar kompatibel dengan filter/ENUM audit di DB lama.
        log_change(
            db,
            entity_type="sales_order",
            entity_id=new_po.id,
            action="create",
            after={
                "po_number": new_po.po_number,
                "status": new_po.status,
                "duplicated_from_po_id": po_id,
                "line_count": len(details_src),
                "via": "duplicate_po",
            },
            actor=user.username,
        )
        create_notification_for_roles(
            db,
            ("admin", "marketing", "ppic"),
            title=f"PO salinan {new_po.po_number}",
            message=f"Duplikat dari PO {src.po_number or po_id} oleh {user.username}",
            category="po",
            entity_type="sales_order",
            entity_id=new_po.id,
            route_path="/admin/po",
            route_query={"po_id": new_po.id},
        )
        db.commit()
        db.refresh(new_po)
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        log.warning("duplicate_po integrity_error po_id=%s: %s", po_id, e)
        raise HTTPException(
            status_code=409,
            detail="Duplikasi gagal (konflik data, misalnya nomor PO unik).",
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        log.exception("duplicate_po failed po_id=%s", po_id)
        orig_msg = ""
        if getattr(e, "orig", None) is not None:
            orig_msg = str(e.orig)
        low = f"{e} {orig_msg}".lower()
        if "unknown column" in low or "doesn't exist" in low or "does not exist" in low:
            raise HTTPException(
                status_code=503,
                detail="Skema database belum selaras dengan kode. Jalankan migrasi: alembic upgrade head (folder backend).",
            ) from e
        raise HTTPException(
            status_code=500,
            detail="Duplikasi PO gagal (database). Cek log server untuk detail.",
        ) from e

    return new_po


@router.get("/po/{po_id}", response_model=PoHeaderOut)
def get_po(
    po_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> PoHeader:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    return serialize_po_headers_for_list(db, [row])[0]


@router.get("/po/{po_id}/details", response_model=list[PoDetailOut])
def list_po_details(
    po_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[PoDetail]:
    if not db.get(PoHeader, po_id):
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    rows = db.scalars(
        select(PoDetail)
        .options(selectinload(PoDetail.delivery_schedules))
        .where(PoDetail.po_id == po_id)
        .order_by(PoDetail.id.asc())
    ).all()
    return list(rows)


@router.put("/po/{po_id}", response_model=PoHeaderOut)
def update_po(
    po_id: int,
    body: PoHeaderUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "ppic")),
) -> PoHeader:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    before = {"status": row.status, "mkt_workflow_stage": row.mkt_workflow_stage}
    data = body.model_dump(exclude_unset=True)
    if "order_date" in data:
        new_od = data["order_date"]
        old_od = row.order_date
        if old_od is not None and new_od != old_od:
            raise HTTPException(
                status_code=400,
                detail="Tanggal PO tidak dapat diubah setelah ditetapkan.",
            )
    merged = {
        "customer_id": row.customer_id,
        "brand_id": row.brand_id,
        "buyer": row.buyer,
        "po_customer_ref": row.po_customer_ref,
        **data,
    }
    _validate_customer_brand_buyer(db, merged)
    _validate_po_customer_ref_unique(
        db,
        customer_id=merged.get("customer_id"),
        po_customer_ref=merged.get("po_customer_ref"),
        exclude_po_id=po_id,
    )
    apply_header_snapshots(db, merged, force="brand_id" in data or "customer_id" in data)
    for snap_key in ("brand_name_snapshot", "customer_name_snapshot", "customer_code"):
        if merged.get(snap_key) is not None:
            data[snap_key] = merged[snap_key]
    if "status" in data:
        validate_po_status_transition(row.status, data["status"])
    for k, v in data.items():
        setattr(row, k, v)
    if "status" in data and data["status"] != before["status"]:
        create_notification_for_roles(
            db,
            ("admin", "marketing", "ppic", "production"),
            title=f"Status PO {row.po_number or row.id}: {data['status']}",
            message=f"Diubah oleh {user.username}",
            category="po_status",
            entity_type="sales_order",
            entity_id=row.id,
            route_path="/admin/po",
            route_query={"po_id": row.id},
        )
    log_change(
        db,
        entity_type="sales_order",
        entity_id=row.id,
        action="update",
        before=before,
        after={"status": row.status, "mkt_workflow_stage": row.mkt_workflow_stage},
        actor=user.username,
    )
    sync_mkt_workflow_auto_advance(db, po_id, actor=user.username)
    db.commit()
    db.refresh(row)
    return row


def _validate_delivery_schedule_items(schedules: list[DeliveryScheduleItem]) -> None:
    seq_seen: set[int] = set()
    for item in schedules:
        if item.sequence_no <= 0:
            raise HTTPException(status_code=400, detail="Nomor urutan delivery harus lebih dari 0")
        if item.sequence_no > PO_MAX_DELIVERY_SCHEDULES:
            raise HTTPException(
                status_code=400,
                detail=f"Nomor urutan delivery maksimal {PO_MAX_DELIVERY_SCHEDULES} (selaras lembar outstanding marketing).",
            )
        if item.sequence_no in seq_seen:
            raise HTTPException(
                status_code=400,
                detail=f"Nomor urutan delivery duplikat: {item.sequence_no}",
            )
        seq_seen.add(item.sequence_no)


def _replace_po_detail_delivery_schedules_core(
    db: Session,
    detail_id: int,
    schedules: list[DeliveryScheduleItem],
) -> None:
    _validate_delivery_schedule_items(schedules)
    db.query(PoDetailDelivery).filter(PoDetailDelivery.po_detail_id == detail_id).delete(synchronize_session=False)
    db.flush()
    for item in sorted(schedules, key=lambda x: x.sequence_no):
        db.add(
            PoDetailDelivery(
                po_detail_id=detail_id,
                sequence_no=item.sequence_no,
                qty=item.qty,
                delivery_date=item.delivery_date,
            )
        )


@router.patch("/po/{po_id}/marketing-revise", response_model=PoHeaderOut)
def marketing_revise_po(
    po_id: int,
    body: PoMarketingReviseBody,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing")),
) -> PoHeader:
    """Perbarui field marketing/planning saja; tidak memicu penjurnalan. Tanggal order tidak boleh diubah di sini."""
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    if body.header is None and not body.lines:
        raise HTTPException(status_code=400, detail="Berikan bagian header atau daftar baris untuk revisi.")
    try:
        if body.header:
            h = body.header.model_dump(exclude_unset=True)
            allowed = {
                "etd",
                "delivery_address",
                "material_followup_remark",
                "material_followup_done",
            }
            for k, v in h.items():
                if k in allowed:
                    setattr(row, k, v)
        if body.lines:
            for ln in body.lines:
                drow = db.get(PoDetail, ln.detail_id)
                if not drow or drow.po_id != po_id:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Detail PO #{ln.detail_id} tidak termasuk PO ini",
                    )
                pdata = ln.model_dump(exclude_unset=True)
                pdata.pop("detail_id", None)
                sched_raw = pdata.pop("delivery_schedules", None)
                for k, v in pdata.items():
                    if k in ("line_etd", "detail_remark", "marketing_outstanding_remark", "rtd_text"):
                        setattr(drow, k, v)
                if sched_raw is not None:
                    schedules = [
                        DeliveryScheduleItem.model_validate(x) if isinstance(x, dict) else x
                        for x in sched_raw
                    ]
                    _replace_po_detail_delivery_schedules_core(db, int(drow.id), schedules)
        log_change(
            db,
            entity_type="sales_order",
            entity_id=row.id,
            action="marketing_revise",
            before=None,
            after={
                "header": body.header.model_dump(exclude_unset=True) if body.header else None,
                "lines": [x.model_dump(exclude_unset=True) for x in (body.lines or [])],
            },
            actor=user.username,
        )
        sync_mkt_workflow_auto_advance(db, po_id, actor=user.username)
        db.commit()
    except IntegrityError as e:
        db.rollback()
        log.warning("marketing_revise_po integrity_error po_id=%s: %s", po_id, e)
        raise HTTPException(
            status_code=409,
            detail="Simpan revisi marketing gagal (konflik data). Periksa jadwal delivery.",
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        log.exception("marketing_revise_po failed po_id=%s", po_id)
        raise HTTPException(status_code=500, detail="Simpan revisi marketing gagal (database).") from e
    db.refresh(row)
    return row


@router.delete("/po/{po_id}", response_model=StatusDeletedOut)
def delete_po(
    po_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> StatusDeletedOut:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    
    active_invoices = db.query(SubconInvoice).filter(
        SubconInvoice.po_id == po_id,
        SubconInvoice.status.notin_(["cancelled", "paid"])
    ).count()
    if active_invoices > 0:
        raise HTTPException(
            status_code=400,
            detail="Tidak dapat menghapus PO dengan subcon invoice yang aktif"
        )
    
    active_assignments = db.query(PpicsAssignment).filter(
        PpicsAssignment.po_id == po_id,
        PpicsAssignment.status.notin_(["completed", "cancelled"])
    ).count()
    if active_assignments > 0:
        raise HTTPException(
            status_code=400,
            detail="Tidak dapat menghapus PO dengan PPIC assignment yang aktif"
        )
    
    log_change(
        db,
        entity_type="sales_order",
        entity_id=row.id,
        action="delete",
        before={"po_number": row.po_number, "status": row.status},
        actor=user.username,
    )
    db.delete(row)
    db.commit()
    return StatusDeletedOut(status="deleted")


@router.post("/po/{po_id}/details", response_model=PoDetailOut)
def add_po_detail(
    po_id: int,
    body: PoDetailCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "sales")),
) -> PoDetail:
    po = db.get(PoHeader, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    payload = body.model_dump(exclude_unset=True)
    _validate_fluorescent_color_master(
        db,
        po,
        color_family=payload.get("color_family"),
        color=payload.get("color"),
    )
    row = PoDetail(po_id=po_id, **payload)
    db.add(row)
    db.flush()
    factory = (po.factory_code or "").strip()
    if factory:
        try:
            group = _material_group_from_inputs(
                db,
                master_item_id=row.master_item_id,
                material_name=row.material_name,
                vir_softness_type=row.vir_softness_type,
            )
            row.thi_line_ref = generate_lot_number(
                db,
                po_category=po.po_category or "production",
                factory_code=factory,
                material_group=group,
            )
            db.flush()
        except HTTPException as exc:
            log.warning(
                "auto_lot_skipped po_id=%s detail_id=%s: %s",
                po_id,
                row.id,
                exc.detail,
            )
    log_change(
        db,
        entity_type="sales_order_line",
        entity_id=row.id,
        action="create",
        after={
            "po_id": po_id,
            "material_name": row.material_name,
            "color": row.color,
            "color_family": row.color_family,
            "quantity_order": row.quantity_order,
            "unit_price": row.unit_price,
        },
        actor=user.username,
    )
    db.commit()
    out = _detail_loaded(db, row.id)
    return out or row


@router.put("/po-detail/{detail_id}", response_model=PoDetailOut)
def update_po_detail(
    detail_id: int,
    body: PoDetailUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "ppic", "finance")),
) -> PoDetail:
    row = db.get(PoDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail PO tidak ditemukan")
    data = body.model_dump(exclude_unset=True)
    po = db.get(PoHeader, row.po_id)
    if po:
        _validate_fluorescent_color_master(
            db,
            po,
            color_family=data.get("color_family", row.color_family),
            color=data.get("color", row.color),
        )

    # Harga otomatis: hanya admin/finance yang boleh mengubah unit_price langsung.
    if "unit_price" in data and user.role not in ("admin", "finance"):
        raise HTTPException(status_code=403, detail="unit_price dikunci (harga otomatis)")

    before = {
        "material_name": row.material_name,
        "color": row.color,
        "color_family": row.color_family,
        "color_reference": row.color_reference,
        "color_standard": row.color_standard,
        "thickness_text": row.thickness_text,
        "thickness_min": row.thickness_min,
        "thickness_max": row.thickness_max,
        "quantity_order": row.quantity_order,
        "line_etd": row.line_etd,
        "backing": row.backing,
        "unit_price": row.unit_price,
    }
    for k, v in data.items():
        setattr(row, k, v)
    log_change(
        db,
        entity_type="sales_order_line",
        entity_id=row.id,
        action="update",
        before=before,
        after={
            "material_name": row.material_name,
            "color": row.color,
            "color_family": row.color_family,
            "color_reference": row.color_reference,
            "color_standard": row.color_standard,
            "thickness_text": row.thickness_text,
            "thickness_min": row.thickness_min,
            "thickness_max": row.thickness_max,
            "quantity_order": row.quantity_order,
            "line_etd": row.line_etd,
            "backing": row.backing,
            "unit_price": row.unit_price,
        },
        actor=user.username,
    )
    db.commit()
    out = _detail_loaded(db, detail_id)
    return out or row


@router.post("/po-detail/{detail_id}/generate-lot", response_model=PoDetailOut)
def generate_lot_for_po_detail(
    detail_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "sales")),
) -> PoDetail:
    """Generate nomor lot untuk kolom THI/Lot (thi_line_ref) sesuai format marketing."""
    row = db.get(PoDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail PO tidak ditemukan")
    try:
        before_thi = row.thi_line_ref
        lot = generate_po_detail_lot_number(db, detail_id)
        row.thi_line_ref = lot
        log_change(
            db,
            entity_type="sales_order_line",
            entity_id=row.id,
            action="update",
            before={"thi_line_ref": before_thi},
            after={"thi_line_ref": lot, "via": "generate_lot"},
            actor=user.username,
        )
        db.commit()
        out = _detail_loaded(db, detail_id)
        return out or row
    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError as e:
        db.rollback()
        log.exception("generate_lot_for_po_detail failed detail_id=%s", detail_id)
        raise HTTPException(status_code=500, detail="Generate lot gagal (database).") from e


@router.post("/po/generate-lot", response_model=LotGenerateOut)
def generate_lot_preview(
    body: LotGenerateIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing", "sales")),
) -> LotGenerateOut:
    """Generate lot number tanpa perlu simpan PO/detail dulu (dipakai saat draft)."""
    data = body.model_dump(exclude_unset=True)
    group = _material_group_from_inputs(
        db,
        master_item_id=data.get("master_item_id"),
        material_name=data.get("material_name"),
        vir_softness_type=data.get("vir_softness_type"),
    )
    lot = peek_lot_number(
        db,
        po_category=data.get("po_category") or "production",
        factory_code=data.get("factory_code") or "",
        material_group=group,
    )
    return LotGenerateOut(lot_number=lot)


@router.delete("/po-detail/{detail_id}", response_model=StatusDeletedOut)
def delete_po_detail(
    detail_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> StatusDeletedOut:
    row = db.get(PoDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail PO tidak ditemukan")
    log_change(
        db,
        entity_type="sales_order_line",
        entity_id=row.id,
        action="delete",
        before={"material_name": row.material_name, "unit_price": row.unit_price},
        actor=user.username,
    )
    db.delete(row)
    db.commit()
    return StatusDeletedOut(status="deleted")


@router.put("/po-detail/{detail_id}/delivery-schedules", response_model=list[PoDetailDeliveryOut])
def set_po_detail_delivery_schedules(
    detail_id: int,
    body: DeliverySchedulesPayload,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing")),
) -> list:
    row = db.get(PoDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail PO tidak ditemukan")

    try:
        _replace_po_detail_delivery_schedules_core(db, detail_id, list(body.schedules))
        db.commit()
        return list(
            db.scalars(
                select(PoDetailDelivery)
                .where(PoDetailDelivery.po_detail_id == detail_id)
                .order_by(PoDetailDelivery.sequence_no.asc())
            ).all()
        )
    except IntegrityError as e:
        db.rollback()
        log.warning("set_po_detail_delivery_schedules integrity_error detail_id=%s: %s", detail_id, e)
        raise HTTPException(
            status_code=409,
            detail="Simpan jadwal delivery gagal (konflik data). Periksa urutan/jadwal yang duplikat.",
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        log.exception("set_po_detail_delivery_schedules failed detail_id=%s", detail_id)
        orig_msg = ""
        if getattr(e, "orig", None) is not None:
            orig_msg = str(e.orig)
        low = f"{e} {orig_msg}".lower()
        if "unknown column" in low or "doesn't exist" in low or "does not exist" in low or "doesn't have a default value" in low:
            raise HTTPException(
                status_code=503,
                detail="Skema database belum selaras untuk jadwal delivery. Jalankan migrasi terbaru (alembic upgrade head).",
            ) from e
        raise HTTPException(
            status_code=500,
            detail="Simpan jadwal delivery gagal (database). Cek log server untuk detail.",
        ) from e


@router.get("/po-detail/{detail_id}/delivery-schedules", response_model=list[PoDetailDeliveryOut])
def get_po_detail_delivery_schedules(
    detail_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list:
    row = db.get(PoDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail PO tidak ditemukan")
    return row.delivery_schedules
