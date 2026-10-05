"""Outstanding ship: opsi packing dari stok FG MRP (lot SO) → mirror ERP idempotent."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from sqlalchemy import select

from app.models import PackingDetail, PackingHeader, PoDetail, PoHeader, ProductionDetail
from app.services.delivery_shipment import (
    _packing_line_row,
    brand_key,
    lot_number_for_line,
    so_number_for_line,
)
from app.services.mrp_packing_bridge import ensure_erp_packing_from_mrp_finish
from app.services.mrp_production_bridge import upsert_production_mirror

logger = logging.getLogger(__name__)


def _mrp_base() -> str:
    return (settings.mrp_upstream_url or "http://127.0.0.1:8002").rstrip("/")


def _fetch_mrp_packing_roll_pcs(mrp_packing_id: int) -> tuple[int | None, int | None]:
    """Rolls = jumlah baris roll; Pieces = total lembar (selaras INVPL MRP)."""
    if not mrp_packing_id:
        return None, None
    base = _mrp_base()
    timeout = max(float(settings.mrp_sync_timeout_seconds or 8.0), 20.0)
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.get(f"{base}/api/mrp/packing/{int(mrp_packing_id)}")
            if r.status_code != 200:
                return None, None
            body = r.json() if r.content else {}
            if not isinstance(body, dict):
                return None, None
            packing = body.get("packing") if isinstance(body.get("packing"), dict) else {}
            rolls_raw = body.get("rolls")
            rolls = [x for x in rolls_raw if isinstance(x, dict)] if isinstance(rolls_raw, list) else []
            roll_count: int | None = None
            if rolls:
                roll_count = len(rolls)
            elif packing.get("total_rolls") is not None:
                try:
                    roll_count = int(packing["total_rolls"])
                except (TypeError, ValueError):
                    roll_count = None
            pieces: int | None = None
            try:
                p = int(packing.get("total_lembar") or packing.get("total_pieces") or 0)
                pieces = p if p > 0 else None
            except (TypeError, ValueError):
                pieces = None
            if pieces is None and rolls:
                try:
                    s = sum(int(x.get("lembar") or 0) for x in rolls)
                    pieces = s if s > 0 else None
                except (TypeError, ValueError):
                    pieces = None
            return roll_count, pieces
    except httpx.HTTPError as exc:
        logger.warning("MRP packing/%s unavailable: %s", mrp_packing_id, exc)
    return None, None


def _rolls_pieces_from_fg(fg: dict[str, Any], mrp_packing_id: int) -> tuple[int | None, int | None]:
    rolls, pieces = _fetch_mrp_packing_roll_pcs(mrp_packing_id)
    if pieces is None:
        try:
            p = int(fg.get("total_lembar") or 0)
            pieces = p if p > 0 else None
        except (TypeError, ValueError):
            pass
    return rolls, pieces


def hydrate_mrp_roll_pcs_on_options(db: Session, rows: list[dict[str, Any]]) -> None:
    """Isi qty_roll / qty_pcs dari MRP bila mirror ERP kosong (outstanding Buat SJ)."""
    cache: dict[int, tuple[int | None, int | None]] = {}
    for item in rows:
        try:
            pk_id = int(item.get("packing_id") or 0)
        except (TypeError, ValueError):
            continue
        if not pk_id:
            continue
        pk = db.get(PackingHeader, pk_id)
        if not pk or not pk.mrp_packing_id:
            continue
        mid = int(pk.mrp_packing_id)
        if mid not in cache:
            cache[mid] = _fetch_mrp_packing_roll_pcs(mid)
        rolls, pieces = cache[mid]
        if rolls is not None:
            item["qty_roll"] = rolls
        if pieces is not None:
            item["qty_pcs"] = pieces
        pd_id = item.get("production_detail_id")
        if pd_id is None:
            continue
        pkd = db.scalars(
            select(PackingDetail).where(
                PackingDetail.packing_id == pk_id,
                PackingDetail.production_detail_id == int(pd_id),
            )
        ).first()
        if not pkd:
            continue
        if rolls is not None and pkd.qty_roll is None:
            pkd.qty_roll = int(rolls)
        if pieces is not None and pkd.qty_pcs is None:
            pkd.qty_pcs = int(pieces)


def _fetch_fg_rows_by_lot(lot_no: str, *, status: str = "in_stock") -> list[dict[str, Any]]:
    lot = (lot_no or "").strip()
    if not lot:
        return []
    base = _mrp_base()
    timeout = max(float(settings.mrp_sync_timeout_seconds or 8.0), 20.0)
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.get(
                f"{base}/api/mrp/gudang-fg/by-lot",
                params={"lot_no": lot, "status": status},
            )
            if r.status_code != 200:
                logger.warning("MRP gudang-fg/by-lot %s: %s", r.status_code, r.text[:200])
                return []
            body = r.json()
            if isinstance(body, list):
                return [x for x in body if isinstance(x, dict)]
    except httpx.HTTPError as exc:
        logger.warning("MRP gudang-fg/by-lot unavailable: %s", exc)
    return []


def _option_key(row: dict[str, Any]) -> tuple[int, int]:
    return (int(row["packing_id"]), int(row["production_detail_id"]))


def enrich_packing_options_from_mrp_fg(
    db: Session,
    po_detail_ids: list[int],
    existing: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Tambah opsi packing ERP dari FG MRP in_stock yang lot-nya cocok dengan baris SO."""
    wanted = {int(x) for x in po_detail_ids if x is not None}
    if not wanted:
        return []
    seen = {_option_key(r) for r in existing if r.get("packing_id") and r.get("production_detail_id")}
    out: list[dict[str, Any]] = []

    for pod_id in sorted(wanted):
        pod = db.get(PoDetail, pod_id)
        if not pod:
            continue
        lot = lot_number_for_line(pod, None)
        if not lot:
            continue
        ph = db.get(PoHeader, pod.po_id) if pod.po_id else None
        fg_rows = _fetch_fg_rows_by_lot(lot, status="in_stock")
        for fg in fg_rows:
            try:
                mrp_packing_id = int(fg.get("packing_id") or 0)
                mrp_fg_id = int(fg.get("id") or 0)
            except (TypeError, ValueError):
                continue
            if not mrp_packing_id:
                continue
            kode_wip = (fg.get("kode_wip") or lot).strip()
            qty = fg.get("total_ukuran")
            qty_dec = Decimal(str(qty)) if qty is not None else Decimal(0)
            if qty_dec <= 0:
                continue
            qty_roll, qty_pcs = _rolls_pieces_from_fg(fg, mrp_packing_id)

            mirror = upsert_production_mirror(
                db,
                source_detail_id=pod_id,
                kode_wip=kode_wip,
                mrp_packing_id=mrp_packing_id,
                qty_planned=pod.quantity_order,
                qty_actual=qty_dec,
                finish=True,
            )
            ready = ensure_erp_packing_from_mrp_finish(
                db,
                mrp_packing_id=mrp_packing_id,
                kode_packing=(fg.get("kode_packing") or "").strip() or None,
                production_id=mirror.production_id,
                lines=[(mirror.production_detail_id, qty_dec)],
                qty_roll=qty_roll if qty_roll and qty_roll > 0 else None,
                qty_pcs=qty_pcs if qty_pcs and qty_pcs > 0 else None,
            )
            pk = db.get(PackingHeader, ready.packing_id)
            if pk and mrp_fg_id and not pk.mrp_fg_id:
                pk.mrp_fg_id = mrp_fg_id
            if not pk:
                continue
            pd = db.get(ProductionDetail, mirror.production_detail_id)
            pkd = db.scalars(
                select(PackingDetail).where(
                    PackingDetail.packing_id == pk.id,
                    PackingDetail.production_detail_id == mirror.production_detail_id,
                )
            ).first()
            line = _packing_line_row(db, pk, pd, pkd)
            if not line:
                continue
            key = _option_key(line)
            if key in seen:
                continue
            seen.add(key)
            item = dict(line)
            item["po_detail_id"] = pod_id
            item["lot_no"] = lot
            item["so_number"] = so_number_for_line(ph, pod)
            item["brand"] = brand_key(ph)
            item["material_name"] = (pod.material_name or "").strip()
            if qty_roll is not None:
                item["qty_roll"] = qty_roll
            if qty_pcs is not None:
                item["qty_pcs"] = qty_pcs
            out.append(item)
    db.flush()
    return out
