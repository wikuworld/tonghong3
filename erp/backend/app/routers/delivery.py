from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.timeutil import app_now
from app.paging import apply_sort, page_dict, parse_page_params
from app.models import (
    DeliveryDetail,
    DeliveryHeader,
    PackingHeader,
    PoDetail,
    PoHeader,
    ProductionDetail,
    ProductionOrder,
    QcDetail,
)
from app.services.po_delivery_balance import validate_delivery_qty_against_po_balance
from app.schemas import (
    DeliveryCancelIn,
    DeliveryDeleteIn,
    DeliveryDetailCreate,
    DeliveryDetailEnrichedOut,
    DeliveryDetailOut,
    DeliveryDetailReturnIn,
    DeliveryDetailReturnOut,
    DeliveryDetailUpdate,
    DeliveryFromPackingLinesIn,
    DeliveryHeaderCreate,
    DeliveryHeaderOut,
    DeliveryHeaderPageOut,
    DeliveryHeaderUpdate,
    DeliveryScanOutIn,
    DeliveryScanOutOut,
    ReadyToShipLineOut,
)
from app.services.business_rules import require_packing_ready
from app.routers.auth import get_current_user, require_roles
from app.services.audit import log_change
from app.services.notifications import create_notification_for_roles
from app.services.mkt_workflow import sync_mkt_for_delivery, sync_mkt_workflow_auto_advance
from app.services.business_rules import po_numbers_from_delivery
from app.services.document_numbers import (
    allocate_surat_jalan_number,
    raise_floor_surat_jalan_sequence,
)
from app.services.delivery_return import apply_delivery_line_return
from app.services.delivery_active import delivery_header_is_active_clause, delivery_header_is_deleted
from app.services.delivery_cancel import cancel_delivery, soft_delete_delivery
from app.services.delivery_auto_invoice import sync_invoice_lines_from_delivery
from app.services.delivery_shipment import (
    list_ready_to_ship,
    lot_number_for_line,
    qty_available_for_packing_line,
    so_number_for_line,
    validate_delivery_detail_fits_header,
    validate_same_customer_and_brand,
)
from app.routers.reports import _order_type_label, _thickness_display

router = APIRouter(tags=["delivery"])

_DRAFT_BLOCKED = frozenset({"sent", "delivered", "completed", "cancelled", "canceled"})


def _parse_iso_date_optional(s: Optional[str]) -> Optional[date]:
    if not s or not str(s).strip():
        return None
    try:
        return date.fromisoformat(str(s).strip()[:10])
    except ValueError:
        return None


def _require_draft_delivery(hdr: DeliveryHeader) -> None:
    if delivery_header_is_deleted(hdr):
        raise HTTPException(status_code=400, detail="Delivery sudah dihapus")
    status = (hdr.status or "").strip().lower()
    if status in ("sent", "delivered", "completed"):
        raise HTTPException(
            status_code=400,
            detail="Surat jalan sudah terkirim. Ubah atau hapus baris tidak diizinkan; gunakan retur.",
        )
    if status in _DRAFT_BLOCKED:
        raise HTTPException(status_code=400, detail="Hanya surat jalan draft yang boleh diubah")


def _sync_open_invoice_from_delivery(db: Session, delivery_id: int) -> None:
    from app.models import Invoice

    inv = db.scalars(
        select(Invoice).where(Invoice.delivery_id == int(delivery_id)).limit(1)
    ).first()
    if inv is None or getattr(inv, "voided_at", None) is not None:
        return
    sync_invoice_lines_from_delivery(db, int(inv.id), force=True)


def _void_open_invoice_if_no_lines(
    db: Session,
    delivery_id: int,
    *,
    actor: str,
) -> None:
    from decimal import Decimal

    from app.models import Invoice

    remaining = db.scalars(
        select(DeliveryDetail.id).where(DeliveryDetail.delivery_id == int(delivery_id)).limit(1)
    ).first()
    if remaining is not None:
        return
    inv = db.scalars(
        select(Invoice).where(Invoice.delivery_id == int(delivery_id)).limit(1)
    ).first()
    if inv is None or getattr(inv, "voided_at", None) is not None:
        return
    paid = (inv.payment_status or "").strip().lower() == "paid"
    amount = Decimal(str(inv.payment_amount or 0))
    has_cn = bool((inv.credit_note_no or "").strip()) or Decimal(str(inv.credit_note_amount or 0)) > 0
    if paid or amount > 0 or has_cn:
        raise HTTPException(
            status_code=400,
            detail="Invoice sudah dibayar atau punya credit note. Hapus baris terakhir tidak diizinkan.",
        )
    reason = "Baris surat jalan dikosongkan"
    inv.voided_at = app_now()
    inv.void_reason = reason
    log_change(
        db,
        entity_type="invoice",
        entity_id=int(inv.id),
        action="void",
        before={"voided_at": None},
        after={"voided_at": inv.voided_at.isoformat(), "void_reason": reason},
        actor=actor,
    )


def _resolve_delivery_line_masters(
    db: Session, dd: DeliveryDetail
) -> tuple[ProductionDetail | None, PoDetail | None, PoHeader | None]:
    """SO bisa lewat production_detail_id (ERP) atau po_detail_id langsung (MRP)."""
    pd = db.get(ProductionDetail, dd.production_detail_id) if dd.production_detail_id else None
    pod = None
    if dd.po_detail_id:
        pod = db.get(PoDetail, int(dd.po_detail_id))
    if pod is None and pd and pd.po_detail_id:
        pod = db.get(PoDetail, int(pd.po_detail_id))
    ph = db.get(PoHeader, pod.po_id) if pod and pod.po_id else None
    return pd, pod, ph


def _delivery_detail_enriched(
    dd: DeliveryDetail,
    pd: ProductionDetail | None,
    pod: PoDetail | None,
    ph: PoHeader | None,
    *,
    leather_color: str = "",
    leather_in_date: str = "",
) -> DeliveryDetailEnrichedOut:
    return DeliveryDetailEnrichedOut(
        id=dd.id,
        delivery_id=dd.delivery_id,
        production_detail_id=dd.production_detail_id,
        packing_detail_id=dd.packing_detail_id,
        qty=float(dd.qty) if dd.qty is not None else None,
        qty_roll=dd.qty_roll,
        qty_pcs=dd.qty_pcs,
        weight=float(dd.weight) if dd.weight is not None else None,
        po_id=int(ph.id) if ph else None,
        po_number=(ph.po_number or "").strip() if ph else "",
        po_customer_ref=(ph.po_customer_ref or "").strip() if ph else "",
        po_detail_id=int(pod.id) if pod else (int(dd.po_detail_id) if dd.po_detail_id else None),
        system_no=so_number_for_line(ph, pod),
        lot_number=lot_number_for_line(pod, pd),
        material_name_line=((pod.material_name or "").strip()) if pod else "",
        thickness_display=_thickness_display(pod) if pod else "",
        color_line=((pod.color or "").strip()) if pod else "",
        leather_color=leather_color or "",
        leather_in_date=leather_in_date or "",
        order_type=_order_type_label(ph) if ph else "",
    )


def _require_details_if_sent(
    db: Session, delivery_id: int, new_status: str | None, prev_status: str
) -> None:
    if new_status is None:
        return
    if (new_status or "").lower() != "sent":
        return
    if (prev_status or "").lower() == "sent":
        return
    one = db.scalars(
        select(DeliveryDetail)
        .where(DeliveryDetail.delivery_id == delivery_id)
        .limit(1)
    ).first()
    if not one:
        raise HTTPException(
            status_code=400,
            detail="Tambah minimal satu baris detail delivery sebelum status 'sent'",
        )


def _user_can_bypass_qc(user) -> bool:
    return getattr(user, "role", None) == "admin"


def _has_qc_ok(db: Session, production_detail_id: int | None) -> bool:
    if production_detail_id is None:
        return False
    row = db.scalars(
        select(QcDetail).where(
            and_(
                QcDetail.production_detail_id == production_detail_id,
                QcDetail.is_ok.is_(True),
            )
        )
    ).first()
    return row is not None


@router.post("/delivery-shipments/scan-out", response_model=DeliveryScanOutOut)
def scan_packing_list_delivery_out(
    body: DeliveryScanOutIn,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> dict:
    """Scan nomor surat jalan (utama) atau packing list → status sent."""
    from app.services.delivery_scan_out import scan_out

    return scan_out(
        db,
        delivery_number=body.delivery_number,
        packing_id=body.packing_id,
        packing_number=body.packing_number,
        actor=user.username,
    )


@router.post("/delivery/{delivery_id}/mark-surat-jalan-printed", response_model=DeliveryHeaderOut)
def mark_surat_jalan_printed(
    delivery_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse", "marketing")),
) -> DeliveryHeader:
    row = db.get(DeliveryHeader, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    before = {"surat_jalan_printed_at": row.surat_jalan_printed_at}
    row.surat_jalan_printed_at = app_now()
    log_change(
        db,
        entity_type="delivery",
        entity_id=row.id,
        action="mark_surat_jalan_printed",
        before=before,
        after={"surat_jalan_printed_at": row.surat_jalan_printed_at},
        actor=user.username,
    )
    sync_mkt_for_delivery(db, delivery_id, actor=user.username)
    db.commit()
    db.refresh(row)
    return row


@router.get("/delivery-shipments/ready", response_model=list[ReadyToShipLineOut])
def delivery_ready_to_ship(
    db: Session = Depends(get_db),
    packing_id: Optional[int] = Query(None),
    lot_keyword: Optional[str] = Query(None, description="Cari nomor lot / SO / material"),
    customer_id: Optional[int] = Query(None),
    limit: int = Query(500, ge=1, le=2000),
    _user=Depends(get_current_user),
) -> list[ReadyToShipLineOut]:
    rows = list_ready_to_ship(
        db,
        packing_id=packing_id,
        lot_keyword=lot_keyword,
        customer_id=customer_id,
        limit=limit,
    )
    return [ReadyToShipLineOut.model_validate(r) for r in rows]


@router.post("/delivery-shipments/from-packing-lines", response_model=DeliveryHeaderOut)
def create_delivery_from_packing_lines(
    body: DeliveryFromPackingLinesIn,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> DeliveryHeader:
    if not body.lines:
        raise HTTPException(status_code=400, detail="Pilih minimal satu baris lot")
    packing_ids = {
        int(ln.packing_id) if ln.packing_id is not None else int(body.packing_id)
        for ln in body.lines
    }
    packing_ids.add(int(body.packing_id))
    for pid in packing_ids:
        require_packing_ready(db, pid)
    pd_ids = [int(ln.production_detail_id) for ln in body.lines]
    customer_id, _brand = validate_same_customer_and_brand(
        db, pd_ids, expected_customer_id=body.customer_id
    )
    po_for_num: PoHeader | None = None
    if pd_ids:
        pd0 = db.get(ProductionDetail, int(pd_ids[0]))
        if pd0 and pd0.po_detail_id:
            pod0 = db.get(PoDetail, int(pd0.po_detail_id))
            if pod0 and pod0.po_id:
                po_for_num = db.get(PoHeader, int(pod0.po_id))
    hdr = DeliveryHeader(
        delivery_number=allocate_surat_jalan_number(
            db, po=po_for_num, on_date=body.delivery_date
        ),
        customer_id=customer_id or body.customer_id,
        packing_id=body.packing_id,
        delivery_date=body.delivery_date,
        delivery_type=body.delivery_type,
        delivery_zone=body.delivery_zone,
        vehicle_number=body.vehicle_number,
        driver_name=body.driver_name,
        destination=body.destination,
        status="draft",
    )
    db.add(hdr)
    db.flush()
    for ln in body.lines:
        line_packing_id = int(ln.packing_id) if ln.packing_id is not None else int(body.packing_id)
        if not _has_qc_ok(db, ln.production_detail_id):
            raise HTTPException(
                status_code=400,
                detail=f"Production detail #{ln.production_detail_id} belum QC OK",
            )
        qty = ln.qty
        if qty is None or qty <= 0:
            raise HTTPException(
                status_code=400,
                detail=f"Qty kirim wajib > 0 (production detail #{ln.production_detail_id})",
            )
        available = qty_available_for_packing_line(
            db,
            packing_id=line_packing_id,
            production_detail_id=int(ln.production_detail_id),
            packing_detail_id=int(ln.packing_detail_id) if ln.packing_detail_id else None,
        )
        if qty > available:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Qty kirim ({qty}) melebihi sisa packing tersedia ({available}) "
                    f"untuk production detail #{ln.production_detail_id}"
                ),
            )
        validate_delivery_qty_against_po_balance(
            db,
            production_detail_id=int(ln.production_detail_id),
            qty=qty,
        )
        db.add(
            DeliveryDetail(
                delivery_id=hdr.id,
                production_detail_id=ln.production_detail_id,
                packing_detail_id=ln.packing_detail_id,
                qty=qty,
                qty_roll=ln.qty_roll,
                qty_pcs=ln.qty_pcs,
                weight=ln.weight,
            )
        )
    log_change(
        db,
        entity_type="delivery",
        entity_id=hdr.id,
        action="create_from_packing_lines",
        after={
            "packing_id": body.packing_id,
            "packing_ids": sorted(packing_ids),
            "line_count": len(body.lines),
        },
        actor=user.username,
    )
    po_numbers = po_numbers_from_delivery(db, hdr.id)
    for pn in po_numbers:
        ph = db.scalars(select(PoHeader).where(PoHeader.po_number == pn).limit(1)).first()
        if ph:
            sync_mkt_workflow_auto_advance(db, ph.id, actor=user.username)
    from app.services.delivery_auto_invoice import ensure_invoice_for_delivery

    ensure_invoice_for_delivery(db, int(hdr.id), actor=user.username)
    db.commit()
    db.refresh(hdr)
    return hdr


@router.post("/delivery", response_model=DeliveryHeaderOut)
def create_delivery(
    body: DeliveryHeaderCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> DeliveryHeader:
    require_packing_ready(db, body.packing_id)
    data = body.model_dump(exclude_unset=True)
    if not (data.get("delivery_number") or "").strip():
        po_for_num: PoHeader | None = None
        ph_pack = db.get(PackingHeader, body.packing_id)
        if ph_pack and ph_pack.production_id:
            pr = db.get(ProductionOrder, ph_pack.production_id)
            if pr and pr.po_id:
                po_for_num = db.get(PoHeader, int(pr.po_id))
        data["delivery_number"] = allocate_surat_jalan_number(
            db, po=po_for_num, on_date=data.get("delivery_date")
        )
    row = DeliveryHeader(**data)
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="delivery",
        entity_id=row.id,
        action="create",
        after={"delivery_number": row.delivery_number, "status": row.status},
        actor=user.username,
    )

    po_numbers = po_numbers_from_delivery(db, row.id)
    for pn in po_numbers:
        ph = db.scalars(select(PoHeader).where(PoHeader.po_number == pn).limit(1)).first()
        if ph:
            sync_mkt_workflow_auto_advance(db, ph.id, actor=user.username)

    from app.services.delivery_auto_invoice import ensure_invoice_for_delivery

    ensure_invoice_for_delivery(db, int(row.id), actor=user.username)
    db.commit()
    db.refresh(row)
    return row


@router.get("/delivery", response_model=DeliveryHeaderPageOut)
def list_delivery(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search delivery number/destination"),
    customer_id: Optional[int] = Query(None),
    delivery_date_from: Optional[str] = Query(None, description="YYYY-MM-DD"),
    delivery_date_to: Optional[str] = Query(None, description="YYYY-MM-DD"),
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, description="id|delivery_number|delivery_date|status|created_at"),
    sort_dir: Optional[str] = Query(None),
    _user=Depends(get_current_user),
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
    filters = [delivery_header_is_active_clause()]
    if q:
        like = f"%{q}%"
        filters.append(
            or_(DeliveryHeader.delivery_number.ilike(like), DeliveryHeader.destination.ilike(like))
        )
    if customer_id is not None:
        filters.append(DeliveryHeader.customer_id == int(customer_id))
    d_from = _parse_iso_date_optional(delivery_date_from)
    d_to = _parse_iso_date_optional(delivery_date_to)
    if d_from is not None:
        filters.append(DeliveryHeader.delivery_date >= d_from)
    if d_to is not None:
        filters.append(DeliveryHeader.delivery_date <= d_to)
    count_stmt = select(func.count(DeliveryHeader.id)).where(*filters)
    stmt = select(DeliveryHeader).where(*filters)
    total = int(db.scalar(count_stmt) or 0)
    stmt = apply_sort(
        stmt,
        sortable={
            "id": DeliveryHeader.id,
            "delivery_number": DeliveryHeader.delivery_number,
            "delivery_date": DeliveryHeader.delivery_date,
            "status": DeliveryHeader.status,
            "created_at": DeliveryHeader.created_at,
        },
        sort_by=params.sort_by,
        sort_dir=params.sort_dir,
        default_order=(DeliveryHeader.id.desc(),),
    )
    rows = list(db.scalars(stmt.limit(params.limit).offset(params.offset)).all())
    return page_dict(items=rows, total=total, params=params)


@router.put("/delivery/{delivery_id}", response_model=DeliveryHeaderOut)
def update_delivery(
    delivery_id: int,
    body: DeliveryHeaderUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> DeliveryHeader:
    row = db.get(DeliveryHeader, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    if delivery_header_is_deleted(row):
        raise HTTPException(status_code=400, detail="Delivery sudah dihapus")
    before = {
        "status": row.status,
        "packing_id": row.packing_id,
        "delivery_number": row.delivery_number,
    }
    data = body.model_dump(exclude_unset=True)
    if "status" in data and (data.get("status") or "").strip().lower() in ("cancelled", "canceled"):
        raise HTTPException(
            status_code=400,
            detail="Status cancelled tidak dipakai. Hapus delivery lewat aksi Hapus.",
        )
    if "delivery_number" in data:
        _require_draft_delivery(row)
        new_no = (data.get("delivery_number") or "").strip()
        if not new_no:
            raise HTTPException(status_code=400, detail="Nomor surat jalan wajib diisi")
        clash = db.scalars(
            select(DeliveryHeader).where(
                DeliveryHeader.delivery_number == new_no,
                DeliveryHeader.id != int(delivery_id),
            ).limit(1)
        ).first()
        if clash is not None:
            raise HTTPException(
                status_code=409,
                detail=f"Nomor surat jalan {new_no} sudah dipakai",
            )
        data["delivery_number"] = new_no
        raise_floor_surat_jalan_sequence(db, new_no)
    if "packing_id" in data and data["packing_id"] is not None:
        require_packing_ready(db, int(data["packing_id"]))
    prev_status = row.status
    if "status" in data:
        _require_details_if_sent(db, delivery_id, data["status"], prev_status)
    for k, v in data.items():
        setattr(row, k, v)
    if row.status == "sent" and before["status"] != "sent":
        create_notification_for_roles(
            db,
            ("admin", "warehouse", "finance", "marketing"),
            title=f"Delivery {row.delivery_number or row.id} terkirim",
            message="Dokumen siap untuk proses invoice",
            category="delivery",
            entity_type="delivery",
            entity_id=row.id,
            route_path="/admin/delivery",
            route_query={"delivery_id": row.id},
        )
    log_change(
        db,
        entity_type="delivery",
        entity_id=row.id,
        action="update",
        before=before,
        after={
            "status": row.status,
            "packing_id": row.packing_id,
            "delivery_number": row.delivery_number,
        },
        actor=user.username,
    )
    if (row.status or "").lower() == "sent":
        sync_mkt_for_delivery(db, row.id, actor=user.username)
    db.commit()
    db.refresh(row)
    return row


@router.post("/delivery/{delivery_id}/delete", response_model=DeliveryHeaderOut)
def delete_delivery_route(
    delivery_id: int,
    body: DeliveryDeleteIn,
    db: Session = Depends(get_db),
    user=Depends(require_roles("warehouse", "finance", "admin")),
) -> DeliveryHeader:
    return soft_delete_delivery(
        db,
        delivery_id,
        reason=body.reason,
        actor=user.username,
        role=getattr(user, "role", None),
    )


@router.post("/delivery/{delivery_id}/cancel", response_model=DeliveryHeaderOut)
def cancel_delivery_route(
    delivery_id: int,
    body: DeliveryCancelIn,
    db: Session = Depends(get_db),
    user=Depends(require_roles("warehouse", "finance", "admin")),
) -> DeliveryHeader:
    """Alias lama → soft-delete."""
    return cancel_delivery(
        db,
        delivery_id,
        reason=body.reason,
        actor=user.username,
        role=getattr(user, "role", None),
    )


@router.get("/delivery/{delivery_id}", response_model=DeliveryHeaderOut)
def get_delivery(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> DeliveryHeader:
    row = db.get(DeliveryHeader, delivery_id)
    if not row:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    if delivery_header_is_deleted(row):
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    return row


@router.get("/delivery/{delivery_id}/details", response_model=list[DeliveryDetailEnrichedOut])
def list_delivery_details(
    delivery_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user)
) -> list[DeliveryDetailEnrichedOut]:
    if not db.get(DeliveryHeader, delivery_id):
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    rows = list(
        db.scalars(
            select(DeliveryDetail)
            .where(DeliveryDetail.delivery_id == delivery_id)
            .order_by(DeliveryDetail.id.asc())
        ).all()
    )
    from app.services.mrp_wip_leather_info import fetch_wip_leather_info

    masters = [_resolve_delivery_line_masters(db, dd) for dd in rows]
    lots = [lot_number_for_line(pod, pd) for pd, pod, _ph in masters]
    leather_map = fetch_wip_leather_info(lots)
    out: list[DeliveryDetailEnrichedOut] = []
    for dd, (pd, pod, ph) in zip(rows, masters):
        lot = (lot_number_for_line(pod, pd) or "").strip()
        meta = leather_map.get(lot) or {}
        out.append(
            _delivery_detail_enriched(
                dd,
                pd,
                pod,
                ph,
                leather_color=str(meta.get("warna_kulit") or ""),
                leather_in_date=str(meta.get("tanggal_masuk_pabrik") or ""),
            )
        )
    return out


@router.post("/delivery/{delivery_id}/details", response_model=DeliveryDetailOut)
def add_delivery_detail(
    delivery_id: int,
    body: DeliveryDetailCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
    bypass_qc: bool = Query(False, description="Admin: izinkan baris tanpa QC OK"),
) -> DeliveryDetail:
    hdr = db.get(DeliveryHeader, delivery_id)
    if not hdr:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    if bypass_qc and not _user_can_bypass_qc(user):
        raise HTTPException(status_code=403, detail="bypass_qc hanya untuk role admin")
    qc_ok = _has_qc_ok(db, body.production_detail_id)
    if not qc_ok and not (bypass_qc and _user_can_bypass_qc(user)):
        raise HTTPException(
            status_code=400,
            detail="Hanya production detail yang sudah QC OK yang boleh dikirim",
        )
    validate_delivery_qty_against_po_balance(
        db,
        production_detail_id=body.production_detail_id,
        qty=body.qty,
    )
    validate_delivery_detail_fits_header(db, delivery_id, int(body.production_detail_id))
    row = DeliveryDetail(
        delivery_id=delivery_id, **body.model_dump(exclude_unset=True)
    )
    db.add(row)
    db.flush()
    log_change(
        db,
        entity_type="delivery_line",
        entity_id=row.id,
        action="create",
        after={"delivery_id": delivery_id, "production_detail_id": row.production_detail_id, "qty": row.qty},
        actor=user.username,
    )
    from app.services.delivery_auto_invoice import ensure_invoice_for_delivery

    ensure_invoice_for_delivery(db, int(delivery_id), actor=user.username)
    db.commit()
    db.refresh(row)
    return row


@router.put("/delivery-detail/{detail_id}", response_model=DeliveryDetailOut)
def update_delivery_detail(
    detail_id: int,
    body: DeliveryDetailUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
    bypass_qc: bool = Query(False, description="Admin: izinkan baris tanpa QC OK"),
) -> DeliveryDetail:
    row = db.get(DeliveryDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail delivery tidak ditemukan")
    hdr = db.get(DeliveryHeader, int(row.delivery_id))
    if not hdr:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    _require_draft_delivery(hdr)
    before = {"production_detail_id": row.production_detail_id, "qty": row.qty, "qty_roll": row.qty_roll, "qty_pcs": row.qty_pcs}
    new_pd = body.production_detail_id
    if bypass_qc and not _user_can_bypass_qc(user):
        raise HTTPException(status_code=403, detail="bypass_qc hanya untuk role admin")
    if new_pd is not None:
        qc_ok = _has_qc_ok(db, new_pd)
        if not qc_ok and not (bypass_qc and _user_can_bypass_qc(user)):
            raise HTTPException(
                status_code=400,
                detail="Hanya production detail yang sudah QC OK yang boleh dikirim",
            )
    target_pd = new_pd if new_pd is not None else row.production_detail_id
    target_qty = body.qty if body.qty is not None else row.qty
    if target_pd is not None:
        validate_delivery_qty_against_po_balance(
            db,
            production_detail_id=int(target_pd),
            qty=target_qty,
            exclude_delivery_detail_id=detail_id,
        )
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    log_change(
        db,
        entity_type="delivery_line",
        entity_id=row.id,
        action="update",
        before=before,
        after={"production_detail_id": row.production_detail_id, "qty": row.qty, "qty_roll": row.qty_roll, "qty_pcs": row.qty_pcs},
        actor=user.username,
    )
    _sync_open_invoice_from_delivery(db, int(row.delivery_id))
    db.commit()
    db.refresh(row)
    return row


@router.delete("/delivery-detail/{detail_id}", status_code=204, response_class=Response)
def delete_delivery_detail(
    detail_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse")),
) -> Response:
    from decimal import Decimal

    row = db.get(DeliveryDetail, detail_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detail delivery tidak ditemukan")
    hdr = db.get(DeliveryHeader, int(row.delivery_id))
    if not hdr:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")
    _require_draft_delivery(hdr)
    returned = Decimal(str(row.returned_qty or 0))
    if returned > 0:
        raise HTTPException(
            status_code=400,
            detail="Baris sudah ada retur. Hapus tidak diizinkan.",
        )
    delivery_id = int(row.delivery_id)
    before = {
        "delivery_id": delivery_id,
        "production_detail_id": row.production_detail_id,
        "qty": float(row.qty) if row.qty is not None else None,
    }
    db.delete(row)
    db.flush()
    log_change(
        db,
        entity_type="delivery_line",
        entity_id=detail_id,
        action="delete",
        before=before,
        after=None,
        actor=user.username,
    )
    _sync_open_invoice_from_delivery(db, delivery_id)
    _void_open_invoice_if_no_lines(db, delivery_id, actor=user.username)
    db.commit()
    return Response(status_code=204)


@router.post("/delivery-detail/{detail_id}/return", response_model=DeliveryDetailReturnOut)
def return_delivery_detail(
    detail_id: int,
    body: DeliveryDetailReturnIn,
    db: Session = Depends(get_db),
    user=Depends(require_roles("admin", "warehouse", "finance", "marketing")),
) -> DeliveryDetailReturnOut:
    """Retur qty baris SJ → credit note invoice (mengurangi outstanding AR)."""
    result = apply_delivery_line_return(
        db,
        detail_id=detail_id,
        qty=body.qty,
        remark=body.remark,
        actor=user.username,
    )
    log_change(
        db,
        entity_type="delivery_line",
        entity_id=detail_id,
        action="return",
        after={
            "return_qty": result["return_qty_this"],
            "credit_amount": result["credit_amount"],
            "invoice_id": result.get("invoice_id"),
            "returned_qty": result["returned_qty"],
            "remark": result.get("remark"),
        },
        actor=user.username,
    )
    db.commit()
    return DeliveryDetailReturnOut(
        **{k: v for k, v in result.items() if k in DeliveryDetailReturnOut.model_fields}
    )
