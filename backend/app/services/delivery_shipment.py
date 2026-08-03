"""Susun delivery dari packing list — lot siap kirim, validasi customer/brand, batch create."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models import (
    Customer,
    DeliveryDetail,
    DeliveryHeader,
    PackingDetail,
    PackingHeader,
    PoDetail,
    PoHeader,
    ProductionDetail,
    ProductionOrder,
    QcDetail,
)


def _dec(v: Decimal | float | int | None) -> Decimal:
    if v is None:
        return Decimal(0)
    return Decimal(str(v))


def brand_key(ph: PoHeader | None) -> str:
    if not ph:
        return ""
    return (ph.brand_name_snapshot or ph.buyer or "").strip().upper()


def lot_number_for_line(pod: PoDetail | None, pd: ProductionDetail | None) -> str:
    if pd and (pd.lot_number or "").strip():
        return (pd.lot_number or "").strip()
    if pod:
        ref = (pod.system_reference or pod.thi_line_ref or "").strip()
        if ref:
            return ref
    return ""


def so_number_for_line(ph: PoHeader | None, pod: PoDetail | None) -> str:
    if ph and (ph.po_number or "").strip():
        return (ph.po_number or "").strip()
    if pod and (pod.system_reference or "").strip():
        return (pod.system_reference or "").strip()
    return ""


def sum_delivered_qty(db: Session, production_detail_id: int) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(DeliveryDetail.qty), 0)).where(
            DeliveryDetail.production_detail_id == production_detail_id
        )
    )
    return _dec(total)


def _has_qc_ok(db: Session, production_detail_id: int) -> bool:
    row = db.scalars(
        select(QcDetail).where(
            and_(QcDetail.production_detail_id == production_detail_id, QcDetail.is_ok.is_(True))
        )
    ).first()
    return row is not None


def _resolve_po_chain(
    db: Session, production_detail_id: int
) -> tuple[ProductionDetail | None, PoDetail | None, PoHeader | None, Customer | None]:
    pd = db.get(ProductionDetail, production_detail_id)
    if not pd:
        return None, None, None, None
    pod = db.get(PoDetail, pd.po_detail_id) if pd.po_detail_id else None
    ph = db.get(PoHeader, pod.po_id) if pod and pod.po_id else None
    cust = db.get(Customer, ph.customer_id) if ph and ph.customer_id else None
    return pd, pod, ph, cust


def validate_same_customer_and_brand(
    db: Session,
    production_detail_ids: list[int],
    *,
    expected_customer_id: int | None = None,
) -> tuple[int, str]:
    """Pastikan semua baris satu customer + satu brand. Return (customer_id, brand_key)."""
    if not production_detail_ids:
        raise HTTPException(status_code=400, detail="Pilih minimal satu baris lot")
    brands: set[str] = set()
    customers: set[int] = set()
    for pd_id in production_detail_ids:
        _, _, ph, cust = _resolve_po_chain(db, int(pd_id))
        if not ph:
            raise HTTPException(status_code=400, detail=f"Baris produksi #{pd_id} tidak terhubung ke PO")
        bk = brand_key(ph)
        if not bk:
            raise HTTPException(status_code=400, detail=f"PO {ph.po_number or ph.id} tidak punya brand/buyer")
        brands.add(bk)
        if ph.customer_id:
            customers.add(int(ph.customer_id))
        elif cust:
            customers.add(int(cust.id))
    if len(brands) > 1:
        raise HTTPException(
            status_code=400,
            detail="Campur buyer/brand dalam satu surat jalan tidak diizinkan",
        )
    if len(customers) > 1:
        raise HTTPException(
            status_code=400,
            detail="Campur customer/pabrik dalam satu surat jalan tidak diizinkan",
        )
    customer_id = next(iter(customers)) if customers else None
    if expected_customer_id is not None and customer_id is not None and int(expected_customer_id) != int(customer_id):
        raise HTTPException(status_code=400, detail="Customer tidak cocok dengan baris lot terpilih")
    return int(customer_id or expected_customer_id or 0), next(iter(brands))


def validate_delivery_detail_fits_header(
    db: Session,
    delivery_id: int,
    production_detail_id: int,
) -> None:
    hdr = db.get(DeliveryHeader, delivery_id)
    if not hdr:
        return
    existing_ids = [
        int(x)
        for x in db.scalars(
            select(DeliveryDetail.production_detail_id).where(DeliveryDetail.delivery_id == delivery_id)
        ).all()
        if x is not None
    ]
    all_ids = existing_ids + [int(production_detail_id)]
    cust_id, _ = validate_same_customer_and_brand(db, all_ids)
    if hdr.customer_id and cust_id and int(hdr.customer_id) != int(cust_id):
        raise HTTPException(status_code=400, detail="Customer baris tidak cocok dengan header delivery")


def _packing_line_row(
    db: Session,
    pk: PackingHeader,
    pd: ProductionDetail,
    pkd: PackingDetail | None,
) -> dict[str, Any] | None:
    if not _has_qc_ok(db, int(pd.id)):
        return None
    pod: PoDetail | None = db.get(PoDetail, pd.po_detail_id) if pd.po_detail_id else None
    ph: PoHeader | None = db.get(PoHeader, pod.po_id) if pod and pod.po_id else None
    po: ProductionOrder | None = db.get(ProductionOrder, pk.production_id) if pk.production_id else None
    if po and ph and po.po_id and int(po.po_id) != int(ph.id):
        return None

    shipped = sum_delivered_qty(db, int(pd.id))
    qty_packed = _dec(pkd.qty_packed if pkd and pkd.qty_packed is not None else None)
    if qty_packed <= 0:
        qty_packed = _dec(pd.qty_actual if pd.qty_actual is not None else pd.qty_planned)
    available = qty_packed - shipped
    if available <= 0:
        return None

    cust = db.get(Customer, ph.customer_id) if ph and ph.customer_id else None
    return {
        "packing_id": pk.id,
        "packing_number": pk.packing_number or str(pk.id),
        "packing_detail_id": pkd.id if pkd else None,
        "production_detail_id": int(pd.id),
        "lot_no": lot_number_for_line(pod, pd),
        "so_number": so_number_for_line(ph, pod),
        "po_customer_ref": (ph.po_customer_ref or "").strip() if ph else "",
        "customer_id": int(ph.customer_id) if ph and ph.customer_id else None,
        "customer_name": (cust.name if cust else ph.customer_name_snapshot if ph else "") or "",
        "brand": brand_key(ph),
        "material_name": (pod.material_name or "").strip() if pod else "",
        "qty_packed": float(qty_packed),
        "qty_shipped": float(shipped),
        "qty_available": float(available),
        "qty_roll": pkd.qty_roll if pkd and pkd.qty_roll is not None else None,
        "qty_pcs": pkd.qty_pcs if pkd and pkd.qty_pcs is not None else None,
        "weight_net": float(pkd.weight_net) if pkd and pkd.weight_net is not None else None,
    }


def list_ready_to_ship(
    db: Session,
    *,
    packing_id: int | None = None,
    lot_keyword: str | None = None,
    customer_id: int | None = None,
    limit: int = 500,
) -> list[dict[str, Any]]:
    stmt = select(PackingHeader).where(PackingHeader.status == "done").order_by(PackingHeader.id.desc())
    if packing_id is not None:
        stmt = stmt.where(PackingHeader.id == packing_id)
    packings = db.scalars(stmt.limit(limit)).all()
    kw = (lot_keyword or "").strip().lower()
    out: list[dict[str, Any]] = []

    for pk in packings:
        if not pk.production_id:
            continue
        pkd_list = db.scalars(
            select(PackingDetail)
            .where(PackingDetail.packing_id == pk.id)
            .order_by(PackingDetail.id.asc())
        ).all()
        pd_list = db.scalars(
            select(ProductionDetail)
            .where(ProductionDetail.production_id == pk.production_id)
            .order_by(ProductionDetail.id.asc())
        ).all()
        if pkd_list:
            pd_by_id = {int(p.id): p for p in pd_list}
            for pkd in pkd_list:
                if not pkd.production_detail_id:
                    continue
                pd = pd_by_id.get(int(pkd.production_detail_id)) or db.get(ProductionDetail, pkd.production_detail_id)
                if not pd:
                    continue
                row = _packing_line_row(db, pk, pd, pkd)
                if row:
                    out.append(row)
        else:
            for pd in pd_list:
                row = _packing_line_row(db, pk, pd, None)
                if row:
                    out.append(row)

    if customer_id is not None:
        out = [r for r in out if r.get("customer_id") == int(customer_id)]
    if kw:
        out = [
            r
            for r in out
            if kw in (r.get("lot_no") or "").lower()
            or kw in (r.get("so_number") or "").lower()
            or kw in (r.get("material_name") or "").lower()
            or kw in (r.get("packing_number") or "").lower()
        ]
    return out
def list_ready_to_ship_for_po_details(
    db: Session,
    po_detail_ids: list[int],
    *,
    limit: int = 500,
) -> list[dict[str, Any]]:
    """Opsi packing list siap kirim untuk baris outstanding (po_detail_id)."""
    wanted = {int(x) for x in po_detail_ids if x is not None}
    if not wanted:
        return []
    rows = list_ready_to_ship(db, limit=limit)
    enriched: list[dict[str, Any]] = []
    for r in rows:
        pd = db.get(ProductionDetail, int(r["production_detail_id"]))
        if not pd or pd.po_detail_id is None:
            continue
        pod_id = int(pd.po_detail_id)
        if pod_id not in wanted:
            continue
        item = dict(r)
        item["po_detail_id"] = pod_id
        enriched.append(item)
    return enriched


def qty_available_for_packing_line(
    db: Session,
    *,
    packing_id: int,
    production_detail_id: int,
    packing_detail_id: int | None = None,
) -> Decimal:
    """Sisa qty packing yang boleh dikirim untuk lot (0 jika belum done / QC / habis)."""
    pk = db.get(PackingHeader, packing_id)
    if not pk or (pk.status or "").strip().lower() != "done":
        return Decimal(0)
    pd = db.get(ProductionDetail, production_detail_id)
    if not pd:
        return Decimal(0)
    pkd: PackingDetail | None = None
    if packing_detail_id is not None:
        pkd = db.get(PackingDetail, packing_detail_id)
        if not pkd or int(pkd.packing_id or 0) != int(packing_id):
            return Decimal(0)
        if pkd.production_detail_id and int(pkd.production_detail_id) != int(production_detail_id):
            return Decimal(0)
    else:
        pkd = db.scalars(
            select(PackingDetail).where(
                and_(
                    PackingDetail.packing_id == packing_id,
                    PackingDetail.production_detail_id == production_detail_id,
                )
            )
        ).first()
    row = _packing_line_row(db, pk, pd, pkd)
    if not row:
        return Decimal(0)
    return _dec(row.get("qty_available"))


def aggregate_overall(lines: list[dict[str, Any]]) -> dict[str, Any]:
    total_sf = Decimal(0)
    total_roll = 0
    total_pcs = 0
    total_weight = Decimal(0)
    for ln in lines:
        total_sf += _dec(ln.get("qty") or ln.get("qty_available"))
        if ln.get("qty_roll") is not None:
            total_roll += int(ln["qty_roll"])
        if ln.get("qty_pcs") is not None:
            total_pcs += int(ln["qty_pcs"])
        if ln.get("weight") is not None:
            total_weight += _dec(ln["weight"])
        elif ln.get("weight_net") is not None:
            total_weight += _dec(ln["weight_net"])
    brands = {str(ln.get("brand") or "").strip() for ln in lines if ln.get("brand")}
    customers = {str(ln.get("customer_name") or "").strip() for ln in lines if ln.get("customer_name")}
    return {
        "line_count": len(lines),
        "total_sf": float(total_sf),
        "total_roll": total_roll,
        "total_pcs": total_pcs,
        "total_weight": float(total_weight),
        "brand": next(iter(brands)) if len(brands) == 1 else "",
        "customer_name": next(iter(customers)) if len(customers) == 1 else "",
    }

