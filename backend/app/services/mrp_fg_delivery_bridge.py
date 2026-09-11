"""FG OUT MRP: taut ke packing/delivery yang sudah ada. Surat Jalan hanya dari Outstanding."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import httpx
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import (
    DeliveryHeader,
    PackingHeader,
    ProductionDetail,
)
from app.services.mrp_packing_bridge import kode_packing_from_erp

FG_OUT_MUST_USE_OUTSTANDING = (
    "Surat jalan dibuat dari Outstanding (susun kirim), bukan dari Gudang FG OUT."
)


@dataclass
class BridgeLine:
    source_detail_id: int
    qty_out: Decimal
    qty_roll: int | None = None
    qty_pcs: int | None = None
    weight: Decimal | None = None


@dataclass
class BridgeResult:
    delivery_id: int
    delivery_number: str | None
    packing_id: int
    packing_number: str | None
    created: bool
    line_count: int
    po_detail_ids: list[int] | None = None


def _dec(v: Any) -> Decimal:
    if v is None:
        return Decimal("0")
    if isinstance(v, Decimal):
        return v
    return Decimal(str(v))


def _resolve_production_detail_for_wip(
    db: Session,
    *,
    kode_wip: str | None,
    erp_production_detail_id: int | None,
) -> ProductionDetail | None:
    wip = (kode_wip or "").strip()
    if wip:
        pd = db.scalars(
            select(ProductionDetail).where(ProductionDetail.lot_number == wip).limit(1)
        ).first()
        if pd:
            return pd
    if erp_production_detail_id:
        try:
            return db.get(ProductionDetail, int(erp_production_detail_id))
        except (TypeError, ValueError):
            return None
    return None


def _parse_lines(raw_lines: list[dict[str, Any]]) -> list[BridgeLine]:
    lines: list[BridgeLine] = []
    for raw in raw_lines or []:
        try:
            sid = int(raw.get("source_detail_id"))
        except (TypeError, ValueError):
            continue
        qty = _dec(raw.get("qty_out") if raw.get("qty_out") is not None else raw.get("qty_sq"))
        if qty <= 0:
            continue
        qty_roll = raw.get("qty_roll")
        qty_pcs = raw.get("qty_pcs")
        try:
            qty_roll = int(qty_roll) if qty_roll is not None else None
        except (TypeError, ValueError):
            qty_roll = None
        try:
            qty_pcs = int(qty_pcs) if qty_pcs is not None else None
        except (TypeError, ValueError):
            qty_pcs = None
        weight = raw.get("weight")
        weight_dec = _dec(weight) if weight is not None else None
        lines.append(
            BridgeLine(
                source_detail_id=sid,
                qty_out=qty,
                qty_roll=qty_roll,
                qty_pcs=qty_pcs,
                weight=weight_dec if weight_dec and weight_dec > 0 else None,
            )
        )
    return lines


def _result_from_delivery(db: Session, dh: DeliveryHeader, pk: PackingHeader | None) -> BridgeResult:
    packing_id = int(pk.id) if pk and pk.id else int(dh.packing_id or 0)
    return BridgeResult(
        delivery_id=int(dh.id),
        delivery_number=dh.delivery_number,
        packing_id=packing_id,
        packing_number=pk.packing_number if pk else None,
        created=False,
        line_count=0,
    )


def _stamp_fg(pk: PackingHeader | None, dh: DeliveryHeader | None, mrp_fg_id: int) -> None:
    if pk is not None:
        pk.mrp_fg_id = int(mrp_fg_id)
    if dh is not None and dh.mrp_fg_id is None:
        dh.mrp_fg_id = int(mrp_fg_id)


def bridge_fg_out_to_delivery(
    db: Session,
    *,
    mrp_fg_id: int,
    mrp_packing_id: int | None,
    kode_packing: str | None,
    customer_name: str | None,
    lines: list[dict[str, Any]],
    actor: str | None = None,
    keterangan: str | None = None,
    kode_wip: str | None = None,
    erp_production_detail_id: int | None = None,
) -> BridgeResult:
    """Idempotent taut mrp_fg_id ke packing/SJ yang sudah ada. Tidak membuat Delivery baru."""
    _ = (customer_name, lines, actor, keterangan, kode_wip, erp_production_detail_id)
    if not mrp_fg_id:
        raise HTTPException(status_code=400, detail="mrp_fg_id wajib")
    fg_id = int(mrp_fg_id)

    existing = db.scalars(
        select(DeliveryHeader).where(DeliveryHeader.mrp_fg_id == fg_id).limit(1)
    ).first()
    if existing:
        pk = db.get(PackingHeader, existing.packing_id) if existing.packing_id else None
        _stamp_fg(pk, existing, fg_id)
        return _result_from_delivery(db, existing, pk)

    existing_pk = db.scalars(
        select(PackingHeader).where(PackingHeader.mrp_fg_id == fg_id).limit(1)
    ).first()
    if existing_pk:
        existing_dh = db.scalars(
            select(DeliveryHeader).where(DeliveryHeader.packing_id == existing_pk.id).limit(1)
        ).first()
        if existing_dh:
            _stamp_fg(existing_pk, existing_dh, fg_id)
            return _result_from_delivery(db, existing_dh, existing_pk)

    pk: PackingHeader | None = None
    if mrp_packing_id:
        pk = db.scalars(
            select(PackingHeader)
            .where(PackingHeader.mrp_packing_id == int(mrp_packing_id))
            .order_by(PackingHeader.id.desc())
            .limit(1)
        ).first()
    if pk is None and kode_packing:
        num = f"MRP-{(kode_packing or '').strip()}"[:100]
        pk = db.scalars(
            select(PackingHeader).where(PackingHeader.packing_number == num).limit(1)
        ).first()
    if pk:
        dh = db.scalars(
            select(DeliveryHeader).where(DeliveryHeader.packing_id == pk.id).limit(1)
        ).first()
        if dh:
            _stamp_fg(pk, dh, fg_id)
            db.flush()
            return _result_from_delivery(db, dh, pk)

    raise HTTPException(status_code=400, detail=FG_OUT_MUST_USE_OUTSTANDING)


def _mrp_base() -> str:
    return (settings.mrp_upstream_url or "http://127.0.0.1:5010").rstrip("/")


def _mrp_timeout() -> float:
    return max(float(settings.mrp_sync_timeout_seconds or 8.0), 30.0)


def _http_detail(resp: httpx.Response) -> str:
    try:
        data = resp.json()
        if isinstance(data, dict):
            d = data.get("detail") or data.get("message")
            if isinstance(d, str) and d.strip():
                return d.strip()
            return str(data)[:400]
    except Exception:
        pass
    return (resp.text or f"HTTP {resp.status_code}")[:400]


def _rollback_fg_outs(client: httpx.Client, base: str, fg_ids: list[int], reason: str) -> None:
    for fid in reversed(fg_ids):
        try:
            client.post(
                f"{base}/api/mrp/gudang-fg/{fid}/rollback-out",
                json={"reason": (reason or "ship batch failed")[:255]},
            )
        except Exception:
            pass


def _kode_packing_for(pk: PackingHeader, client: httpx.Client, base: str) -> str:
    kode = kode_packing_from_erp(pk)
    if isinstance(kode, str) and kode.strip() and not kode.upper().startswith("PACK-"):
        return kode.strip()
    mid = getattr(pk, "mrp_packing_id", None)
    if mid:
        try:
            r = client.get(f"{base}/api/mrp/packing/{int(mid)}")
            if r.status_code == 200:
                data = r.json() or {}
                packing = data.get("packing") if isinstance(data, dict) else None
                src = packing if isinstance(packing, dict) else (data if isinstance(data, dict) else {})
                kode2 = str((src or {}).get("kode_packing") or "").strip()
                if kode2:
                    return kode2
        except Exception:
            pass
    return kode.strip() if isinstance(kode, str) else ""


def _find_fg_id_by_kode(client: httpx.Client, base: str, kode: str) -> int | None:
    r = client.get(f"{base}/api/mrp/gudang-fg", params={"q": kode})
    if r.status_code != 200:
        return None
    rows = r.json() if r.content else []
    if not isinstance(rows, list):
        return None
    for row in rows:
        if str((row or {}).get("kode_packing") or "").strip() == kode:
            try:
                return int(row["id"])
            except (TypeError, ValueError, KeyError):
                continue
    return None


def trigger_mrp_fg_out_for_packings(
    db: Session,
    *,
    packings: list[PackingHeader],
    delivery: DeliveryHeader,
    keterangan: str | None = None,
    actor: str | None = None,
) -> list[int]:
    """OUT stok FG MRP setelah SJ Outstanding tersimpan (idempotent). Rollback FG bila gagal."""
    _ = actor
    usable: list[PackingHeader] = []
    for pk in packings or []:
        src = pk.source if isinstance(getattr(pk, "source", None), str) else ""
        if src.lower() != "mrp":
            continue
        usable.append(pk)
    if not usable:
        return []

    base = _mrp_base()
    timeout = _mrp_timeout()
    done: list[int] = []
    note = (keterangan or "").strip() or "Outstanding ship"
    try:
        with httpx.Client(timeout=timeout) as client:
            for pk in usable:
                kode = _kode_packing_for(pk, client, base)
                if not kode:
                    _rollback_fg_outs(client, base, done, "kode_packing packing MRP kosong")
                    raise HTTPException(
                        status_code=400,
                        detail="Packing MRP tanpa kode_packing untuk FG OUT",
                    )
                existing_id = int(pk.mrp_fg_id) if pk.mrp_fg_id else None
                fg_id: int | None = existing_id
                if existing_id is None:
                    r = client.post(
                        f"{base}/api/mrp/gudang-fg/out",
                        json={"kode_packing": kode, "keterangan": note},
                    )
                    if r.status_code >= 400:
                        text = _http_detail(r)
                        if "sudah out" in text.lower():
                            fg_id = _find_fg_id_by_kode(client, base, kode)
                            if fg_id is None:
                                _rollback_fg_outs(client, base, done, text)
                                raise HTTPException(
                                    status_code=400,
                                    detail=f"FG OUT MRP gagal: {text}",
                                )
                        else:
                            _rollback_fg_outs(client, base, done, text)
                            raise HTTPException(
                                status_code=400,
                                detail=f"FG OUT MRP gagal: {text}",
                            )
                    else:
                        body = r.json() if r.content else {}
                        try:
                            fg_id = int((body or {}).get("id"))
                        except (TypeError, ValueError):
                            _rollback_fg_outs(client, base, done, "respons FG OUT tanpa id")
                            raise HTTPException(
                                status_code=400,
                                detail="FG OUT MRP tanpa id",
                            )
                pk.mrp_fg_id = int(fg_id)
                if delivery.mrp_fg_id is None:
                    delivery.mrp_fg_id = int(fg_id)
                try:
                    client.post(
                        f"{base}/api/mrp/gudang-fg/{int(fg_id)}/bridge-result",
                        json={
                            "delivery_id": delivery.id,
                            "delivery_number": delivery.delivery_number,
                            "bridge_status": "ok",
                        },
                    )
                except Exception:
                    pass
                done.append(int(fg_id))
    except HTTPException:
        raise
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"MRP upstream unavailable: {e}") from e
    db.flush()
    return done
