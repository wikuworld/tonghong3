import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.db import get_db
from app.models import Brand, BrandBuyerMap, PoDetail, PoHeader
from app.services.audit import log_change
from app.services.numbering import next_number
from app.schemas import (
    PoDetailCreate,
    PoDetailOut,
    PoDetailUpdate,
    PoHeaderCreate,
    PoHeaderOut,
    PoHeaderUpdate,
)
from app.services.business_rules import validate_po_status_transition
from app.services.mkt_workflow import (
    MKT_STAGES_ORDER,
    apply_mkt_stage,
    next_mkt_stage,
    validate_mkt_advance,
)
from app.services.notifications import create_notification_for_roles
from app.routers.auth import get_current_user, require_roles

router = APIRouter(tags=["po"])
log = logging.getLogger(__name__)

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


def _validate_customer_brand_buyer(db: Session, data: dict) -> None:
    customer_id = data.get("customer_id")
    brand_id = data.get("brand_id")
    buyer_code = (data.get("buyer") or "").strip()
    if not brand_id:
        return
    brand = db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(status_code=400, detail="Brand tidak ditemukan")
    if customer_id and brand.customer_id and int(brand.customer_id) != int(customer_id):
        raise HTTPException(status_code=400, detail="Brand tidak terkait customer terpilih")
    if buyer_code:
        allowed = db.scalars(
            select(BrandBuyerMap).where(
                BrandBuyerMap.brand_id == brand_id,
                BrandBuyerMap.buyer_code == buyer_code,
            )
        ).first()
        has_any_map = db.scalars(
            select(BrandBuyerMap.id).where(BrandBuyerMap.brand_id == brand_id)
        ).first()
        if has_any_map and not allowed:
            raise HTTPException(
                status_code=400,
                detail="Buyer tidak valid untuk brand ini",
            )


@router.get("/po/mkt-workflow-stages")
def mkt_workflow_stages(_user=Depends(get_current_user)) -> dict:
    return {"stages": list(MKT_STAGES_ORDER)}


@router.get("/po", response_model=list[PoHeaderOut])
def list_po(
    mkt_workflow_stage: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search PO no/customer/buyer"),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[PoHeader]:
    stmt = select(PoHeader).order_by(PoHeader.id.desc()).limit(limit).offset(offset)
    if mkt_workflow_stage:
        stmt = stmt.where(PoHeader.mkt_workflow_stage == mkt_workflow_stage)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                PoHeader.po_number.ilike(like),
                PoHeader.buyer.ilike(like),
                PoHeader.remark.ilike(like),
                PoHeader.po_customer_ref.ilike(like),
                PoHeader.customer_name_snapshot.ilike(like),
                PoHeader.customer_code.ilike(like),
            )
        )
    return list(db.scalars(stmt).all())


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
    db.commit()
    db.refresh(row)
    return row


@router.post("/po", response_model=PoHeaderOut)
def create_po(
    body: PoHeaderCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "marketing", "sales")),
) -> PoHeader:
    data = body.model_dump(exclude_unset=True)
    _validate_customer_brand_buyer(db, data)
    if not data.get("po_number"):
        data["po_number"] = next_number(db, "SO", "SO")
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

    try:
        new_po = PoHeader(
            po_number=next_number(db, "SO", "SO"),
            customer_id=src.customer_id,
            customer_code=src.customer_code,
            po_category=po_category,
            buyer=src.buyer,
            order_date=src.order_date,
            etd=src.etd,
            remark=src.remark,
            status="draft",
            billing_address=src.billing_address,
            delivery_address=src.delivery_address,
            brand_id=src.brand_id,
            marketing_excel_date_serial=None,
            po_customer_ref=src.po_customer_ref,
            order_type_label=src.order_type_label,
            brand_name_snapshot=src.brand_name_snapshot,
            customer_name_snapshot=src.customer_name_snapshot,
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
    return row


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
    merged = {
        "customer_id": row.customer_id,
        "brand_id": row.brand_id,
        "buyer": row.buyer,
        **data,
    }
    _validate_customer_brand_buyer(db, merged)
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
    db.commit()
    db.refresh(row)
    return row


@router.delete("/po/{po_id}")
def delete_po(
    po_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(PoHeader, po_id)
    if not row:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
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
    return {"status": "deleted"}


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
    row = PoDetail(po_id=po_id, **body.model_dump(exclude_unset=True))
    db.add(row)
    db.flush()
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

    # Harga otomatis: hanya admin/finance yang boleh mengubah unit_price langsung.
    if "unit_price" in data and user.role not in ("admin", "finance"):
        raise HTTPException(status_code=403, detail="unit_price dikunci (harga otomatis)")

    before = {
        "material_name": row.material_name,
        "color": row.color,
        "color_family": row.color_family,
        "color_reference": row.color_reference,
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


@router.delete("/po-detail/{detail_id}")
def delete_po_detail(
    detail_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin")),
) -> dict[str, str]:
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
    return {"status": "deleted"}
