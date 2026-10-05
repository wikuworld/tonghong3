"""Aksi batch dari halaman Outstanding: jadwal kirim, packing options, susun delivery."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    DeliveryDetail,
    DeliveryHeader,
    PackingDetail,
    PackingHeader,
    PoDetail,
    PoDetailDelivery,
    PoHeader,
    ProductionDetail,
)
from app.schemas import (
    DeliveryScheduleItem,
    OutstandingScheduleBatchIn,
    OutstandingShipBatchIn,
)
from app.services.audit import log_change
from app.services.business_rules import require_packing_ready
from app.services.delivery_shipment import (
    _has_qc_ok,
    brand_key,
    list_ready_to_ship_for_po_details,
    qty_available_for_packing_line,
    validate_same_customer_and_brand,
)
from app.services.mkt_workflow import (
    mkt_stage_index,
    normalize_mkt_stage,
    sync_mkt_for_delivery,
    sync_mkt_workflow_auto_advance,
)
from app.services.mrp_fg_delivery_bridge import trigger_mrp_fg_out_for_packings
from app.services.document_numbers import allocate_surat_jalan_number
from app.services.notifications import create_notification_for_roles
from app.services.po_delivery_balance import (
    remaining_schedule_qty,
    validate_delivery_qty_against_po_balance,
    validate_schedule_total_against_order,
)

PO_MAX_DELIVERY_SCHEDULES = 21


def _replace_schedules(db: Session, detail_id: int, schedules: list[DeliveryScheduleItem]) -> None:
    seq_seen: set[int] = set()
    for item in schedules:
        if item.sequence_no < 1 or item.sequence_no > PO_MAX_DELIVERY_SCHEDULES:
            raise HTTPException(
                status_code=400,
                detail=f"sequence_no harus 1–{PO_MAX_DELIVERY_SCHEDULES}",
            )
        if item.sequence_no in seq_seen:
            raise HTTPException(status_code=400, detail=f"sequence_no duplikat: {item.sequence_no}")
        seq_seen.add(item.sequence_no)
    validate_schedule_total_against_order(db, detail_id, schedules)
    db.query(PoDetailDelivery).filter(PoDetailDelivery.po_detail_id == detail_id).delete(
        synchronize_session=False
    )
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


def apply_outstanding_schedule_batch(
    db: Session,
    body: OutstandingScheduleBatchIn,
    *,
    actor: str,
) -> dict[str, Any]:
    if not body.lines:
        raise HTTPException(status_code=400, detail="Pilih minimal satu baris untuk direncanakan")

    grouped: dict[int, list] = defaultdict(list)
    for ln in body.lines:
        grouped[int(ln.po_detail_id)].append(ln)

    updated: list[int] = []
    po_ids: set[int] = set()
    for detail_id, detail_lines in grouped.items():
        drow = db.get(PoDetail, detail_id)
        if not drow:
            raise HTTPException(status_code=404, detail=f"Detail PO #{detail_id} tidak ditemukan")

        existing = list(
            db.scalars(
                select(PoDetailDelivery)
                .where(PoDetailDelivery.po_detail_id == drow.id)
                .order_by(PoDetailDelivery.sequence_no.asc())
            ).all()
        )

        etd = drow.line_etd if isinstance(getattr(drow, "line_etd", None), date) else None
        po_id_raw = getattr(drow, "po_id", None)
        po_id = po_id_raw if isinstance(po_id_raw, int) else None
        ph = db.get(PoHeader, po_id) if po_id is not None else None
        order_raw = getattr(ph, "order_date", None) if ph else None
        order_dt = order_raw if isinstance(order_raw, date) else None

        prepared: list[tuple[Any, Decimal]] = []
        for ln in detail_lines:
            qty = ln.qty
            if qty is None:
                if body.mode == "replace" and len(detail_lines) == 1:
                    qty = drow.quantity_order or Decimal(0)
                elif body.mode == "append" and len(detail_lines) == 1:
                    qty = remaining_schedule_qty(db, int(drow.id), existing)
                    if qty <= 0:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Baris #{drow.id} sudah penuh direncanakan (tidak ada sisa qty)",
                        )
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Qty wajib diisi untuk setiap slot pada baris #{drow.id}",
                    )
            if ln.delivery_date and order_dt and ln.delivery_date < order_dt:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Tanggal rencana ({ln.delivery_date}) sebelum tanggal order ({order_dt}) "
                        f"untuk baris #{drow.id}"
                    ),
                )
            if ln.delivery_date and etd and ln.delivery_date > etd:
                from datetime import timedelta

                if ln.delivery_date > etd + timedelta(days=90):
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            f"Tanggal rencana ({ln.delivery_date}) terlalu jauh setelah reply ETD ({etd}) "
                            f"untuk baris #{drow.id}"
                        ),
                    )
            prepared.append((ln, qty))

        if body.mode == "replace":
            prepared_sorted = sorted(
                prepared,
                key=lambda pair: (
                    int(pair[0].sequence_no) if pair[0].sequence_no is not None else 10_000,
                ),
            )
            if len(prepared_sorted) > PO_MAX_DELIVERY_SCHEDULES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Baris #{drow.id} melebihi batas {PO_MAX_DELIVERY_SCHEDULES} slot rencana",
                )
            schedules = [
                DeliveryScheduleItem(
                    sequence_no=i,
                    qty=qty,
                    delivery_date=ln.delivery_date,
                )
                for i, (ln, qty) in enumerate(prepared_sorted, start=1)
            ]
        else:
            schedules = [
                DeliveryScheduleItem(
                    sequence_no=int(e.sequence_no),
                    qty=e.qty,
                    delivery_date=e.delivery_date,
                )
                for e in existing
            ]
            next_seq = max((e.sequence_no for e in existing), default=0) + 1
            for ln, qty in prepared:
                if ln.sequence_no is not None:
                    next_seq = int(ln.sequence_no)
                if next_seq > PO_MAX_DELIVERY_SCHEDULES:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Baris #{drow.id} sudah penuh ({PO_MAX_DELIVERY_SCHEDULES} slot rencana)",
                    )
                schedules.append(
                    DeliveryScheduleItem(sequence_no=next_seq, qty=qty, delivery_date=ln.delivery_date)
                )
                next_seq += 1

        _replace_schedules(db, int(drow.id), schedules)
        if drow.line_etd is None and prepared:
            drow.line_etd = prepared[0][0].delivery_date
        updated.append(int(drow.id))
        if po_id is not None:
            po_ids.add(po_id)
        log_change(
            db,
            entity_type="po_detail",
            entity_id=int(drow.id),
            action="outstanding_schedule",
            after={
                "mode": body.mode,
                "slots": [
                    {
                        "sequence_no": int(s.sequence_no),
                        "delivery_date": s.delivery_date.isoformat() if s.delivery_date else None,
                        "qty": str(s.qty) if s.qty is not None else None,
                    }
                    for s in schedules
                ],
            },
            actor=actor,
        )

    db.commit()
    for sid in po_ids:
        sync_mkt_workflow_auto_advance(db, sid, actor=actor)
    if po_ids:
        db.commit()
    return {"ok": True, "updated_count": len(updated), "po_detail_ids": updated}


def packing_options_for_details(db: Session, po_detail_ids: list[int]) -> list[dict[str, Any]]:
    from app.services.mrp_fg_packing_options import (
        enrich_packing_options_from_mrp_fg,
        hydrate_mrp_roll_pcs_on_options,
    )

    rows = list_ready_to_ship_for_po_details(db, po_detail_ids)
    extra = enrich_packing_options_from_mrp_fg(db, po_detail_ids, rows)
    if extra:
        rows = [*rows, *extra]
        db.commit()
    hydrate_mrp_roll_pcs_on_options(db, rows)
    db.flush()
    return rows


def apply_outstanding_ship_batch(
    db: Session,
    body: OutstandingShipBatchIn,
    *,
    actor: str,
) -> dict[str, Any]:
    if not body.lines:
        raise HTTPException(status_code=400, detail="Pilih minimal satu baris packing untuk dikirim")

    # Minimal stage: in_outstanding (atau lebih lanjut)
    min_idx = mkt_stage_index("in_outstanding")
    customer_ids: set[int] = set()
    customer_names: set[str] = set()
    for ln in body.lines:
        drow = db.get(PoDetail, int(ln.po_detail_id))
        if not drow:
            raise HTTPException(status_code=404, detail=f"Detail PO #{ln.po_detail_id} tidak ditemukan")
        ph = db.get(PoHeader, int(drow.po_id)) if drow.po_id else None
        if not ph:
            raise HTTPException(status_code=400, detail=f"Baris #{ln.po_detail_id} tanpa header SO")
        stage = normalize_mkt_stage(ph.mkt_workflow_stage)
        if mkt_stage_index(stage) < min_idx:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"SO {ph.po_number or ph.id} belum di tahap Outstanding "
                    f"(sekarang: {stage}). Konfirmasi SO dulu."
                ),
            )
        if ph.customer_id:
            customer_ids.add(int(ph.customer_id))
        else:
            name = (ph.customer_name_snapshot or "").strip().casefold()
            if name:
                customer_names.add(name)

    if len(customer_ids) > 1 or (not customer_ids and len(customer_names) > 1):
        raise HTTPException(
            status_code=400,
            detail=(
                "Buat SJ dari packing hanya untuk satu customer name. "
                "Tidak boleh silang customer dalam satu batch."
            ),
        )

    # Satu SJ per buyer + tanggal (boleh lintas packing / SO, customer sudah dijamin sama).
    groups: dict[tuple[int, str, date | None], list] = defaultdict(list)
    for ln in body.lines:
        drow = db.get(PoDetail, int(ln.po_detail_id))
        ph = db.get(PoHeader, int(drow.po_id)) if drow and drow.po_id else None
        cust_id = int(ph.customer_id) if ph and ph.customer_id else 0
        groups[(cust_id, brand_key(ph), ln.delivery_date)].append(ln)

    delivery_ids: list[int] = []
    delivery_numbers: list[str] = []
    for (_cust, _bk, ship_date), lines in groups.items():
        packing_ids = {int(x.packing_id) for x in lines}
        for pid in packing_ids:
            require_packing_ready(db, pid)
        pd_ids = [int(x.production_detail_id) for x in lines]
        customer_id, _brand = validate_same_customer_and_brand(db, pd_ids)
        first_packing = int(lines[0].packing_id)
        first_detail = db.get(PoDetail, int(lines[0].po_detail_id))
        po_for_num = (
            db.get(PoHeader, int(first_detail.po_id))
            if first_detail and first_detail.po_id
            else None
        )
        hdr = DeliveryHeader(
            delivery_number=allocate_surat_jalan_number(
                db, po=po_for_num, on_date=ship_date or date.today()
            ),
            customer_id=customer_id or None,
            packing_id=first_packing,
            delivery_date=ship_date or date.today(),
            delivery_type=body.delivery_type or "production",
            delivery_zone=body.delivery_zone or "outtown",
            vehicle_number=body.vehicle_number,
            driver_name=body.driver_name,
            destination=body.destination,
            status="draft",
        )
        db.add(hdr)
        db.flush()
        line_audit: list[dict[str, Any]] = []
        for ln in lines:
            prod_id = int(ln.production_detail_id)
            packing_id = int(ln.packing_id)
            if not _has_qc_ok(db, prod_id):
                raise HTTPException(
                    status_code=400,
                    detail=f"Production detail #{prod_id} belum QC OK",
                )
            qty = ln.qty
            if qty is None or qty <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Qty kirim wajib > 0 (production detail #{prod_id})",
                )
            available = qty_available_for_packing_line(
                db,
                packing_id=packing_id,
                production_detail_id=prod_id,
                packing_detail_id=int(ln.packing_detail_id) if ln.packing_detail_id else None,
            )
            if qty > available:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Qty kirim ({qty}) melebihi sisa packing tersedia ({available}) "
                        f"untuk production detail #{prod_id}"
                    ),
                )
            validate_delivery_qty_against_po_balance(
                db,
                production_detail_id=prod_id,
                qty=qty,
            )
            pd = db.get(ProductionDetail, prod_id)
            resolved_pod = int(pd.po_detail_id) if pd and pd.po_detail_id else None
            body_pod = int(ln.po_detail_id) if ln.po_detail_id else None
            if body_pod and resolved_pod and body_pod != resolved_pod:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"po_detail_id {body_pod} tidak cocok dengan production detail "
                        f"#{prod_id} (SO line {resolved_pod})"
                    ),
                )
            po_detail_id = resolved_pod or body_pod
            if po_detail_id is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"production detail #{prod_id} tidak tertaut baris SO",
                )
            pkd = None
            if ln.packing_detail_id:
                pkd = db.get(PackingDetail, int(ln.packing_detail_id))
            if pkd is None:
                pkd = db.scalars(
                    select(PackingDetail).where(
                        PackingDetail.packing_id == packing_id,
                        PackingDetail.production_detail_id == prod_id,
                    )
                ).first()
            qty_roll = int(pkd.qty_roll) if pkd and pkd.qty_roll is not None else None
            qty_pcs = int(pkd.qty_pcs) if pkd and pkd.qty_pcs is not None else None
            db.add(
                DeliveryDetail(
                    delivery_id=hdr.id,
                    production_detail_id=prod_id,
                    packing_detail_id=int(pkd.id) if pkd else (
                        int(ln.packing_detail_id) if ln.packing_detail_id else None
                    ),
                    po_detail_id=int(po_detail_id),
                    qty=qty,
                    qty_roll=qty_roll,
                    qty_pcs=qty_pcs,
                )
            )
            line_audit.append(
                {
                    "po_detail_id": int(po_detail_id),
                    "production_detail_id": prod_id,
                    "packing_id": packing_id,
                    "packing_detail_id": int(pkd.id) if pkd else (
                        int(ln.packing_detail_id) if ln.packing_detail_id else None
                    ),
                    "qty": str(qty),
                    "qty_roll": qty_roll,
                }
            )
        log_change(
            db,
            entity_type="delivery",
            entity_id=hdr.id,
            action="create_from_outstanding_packing",
            after={
                "packing_id": first_packing,
                "packing_ids": sorted(packing_ids),
                "delivery_number": hdr.delivery_number,
                "line_count": len(lines),
                "lines": line_audit,
            },
            actor=actor,
        )
        mrp_pks = []
        for pid in packing_ids:
            pk = db.get(PackingHeader, pid)
            if pk:
                mrp_pks.append(pk)
        trigger_mrp_fg_out_for_packings(
            db,
            packings=mrp_pks,
            delivery=hdr,
            keterangan=body.destination,
            actor=actor,
        )
        sync_mkt_for_delivery(db, hdr.id, actor=actor)
        from app.services.delivery_auto_invoice import ensure_invoice_for_delivery

        ensure_invoice_for_delivery(db, int(hdr.id), actor=actor)
        delivery_ids.append(int(hdr.id))
        if hdr.delivery_number:
            delivery_numbers.append(str(hdr.delivery_number))

    try:
        create_notification_for_roles(
            db,
            roles=("admin", "warehouse", "marketing"),
            title="Delivery draft dari Outstanding",
            message=f"{len(delivery_ids)} surat jalan draft dibuat dari packing list.",
            category="delivery",
            route_path="/admin/delivery",
        )
    except Exception:
        pass

    db.commit()
    sj_label = "surat jalan" if len(delivery_ids) == 1 else "surat jalan"
    return {
        "ok": True,
        "delivery_ids": delivery_ids,
        "delivery_numbers": delivery_numbers,
        "delivery_count": len(delivery_ids),
        "message": f"{len(delivery_ids)} {sj_label} dibuat dari packing list",
    }
