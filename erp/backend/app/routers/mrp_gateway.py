"""Reverse proxy Tonghong JWT-protected routes → Flask MRP service."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload


from app.config import settings
from app.db import get_db
from app.models import QcDetail, QcHeader
from app.routers.auth import get_current_user, require_roles
from app.services.mrp_fg_delivery_bridge import FG_OUT_MUST_USE_OUTSTANDING, bridge_fg_out_to_delivery
from app.services.mrp_packing_bridge import ensure_erp_packing_from_mrp_finish
from app.services.mrp_color_swatch_bridge import (
    combination_from_swatch,
    fields_from_swatch,
    load_swatch_recipes,
    options_for_rencana,
)
from app.services.mrp_master_item_bridge import (
    list_erp_rows,
    load_master_items,
)
from app.services.mrp_po_sync import sync_po_details_to_mrp, try_sync_po_details_to_mrp
from app.services.mrp_production_bridge import upsert_production_mirror
from app.services.mrp_stock_bridge import issue_stock_from_mrp

router = APIRouter(prefix="/mrp", tags=["mrp"])

require_mrp_write = require_roles("admin", "production", "ppic", "warehouse")


def _mrp_proxy_user(request: Request, user=Depends(get_current_user)):
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return user
    return require_mrp_write(user)

_UPSTREAM = (settings.mrp_upstream_url or "http://mrp:5010").rstrip("/")
_HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}


def _num(v: Any) -> float:
    if v is None:
        return 0.0
    if isinstance(v, Decimal):
        return float(v)
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _distribute_qty(weights: list[float], total: float) -> list[float]:
    """Bagi qty aktual ke beberapa baris PO; baris terakhir menyesuaikan sisa pembulatan."""
    n = len(weights)
    if n <= 0:
        return []
    if n == 1:
        return [float(total)]
    wsum = sum(max(0.0, float(w or 0.0)) for w in weights)
    if wsum <= 0:
        base = round(float(total) / n, 4)
        parts = [base] * (n - 1)
        parts.append(round(float(total) - sum(parts), 4))
        return parts
    parts: list[float] = []
    assigned = 0.0
    for i, w in enumerate(weights):
        if i == n - 1:
            parts.append(round(float(total) - assigned, 4))
        else:
            q = round(float(total) * (max(0.0, float(w or 0.0)) / wsum), 4)
            parts.append(q)
            assigned += q
    return parts


class MrpBridgeFgOutIn(BaseModel):
    mrp_fg_id: int
    mrp_packing_id: Optional[int] = None
    kode_packing: Optional[str] = None
    customer: Optional[str] = None
    keterangan: Optional[str] = None
    lines: list[dict[str, Any]] = Field(default_factory=list)


def _collect_bridge_lines(detail: dict[str, Any], fg: dict[str, Any]) -> list[dict[str, Any]]:
    """Baris Delivery dari FG: QTY kirim mengikuti ukur aktual FG (total_ukuran)."""
    lines: list[dict[str, Any]] = []
    seen: set[int] = set()

    for bl in detail.get("bridge_lines") or []:
        sid = bl.get("source_detail_id")
        try:
            sid_i = int(sid)
        except (TypeError, ValueError):
            continue
        qty = _num(bl.get("qty_sq") or bl.get("qty_out"))
        if qty <= 0:
            continue
        lines.append({"source_detail_id": sid_i, "qty_out": qty})
        seen.add(sid_i)

    for pp in detail.get("packing_pos") or []:
        sid = pp.get("source_detail_id")
        try:
            sid_i = int(sid)
        except (TypeError, ValueError):
            continue
        if sid_i in seen:
            continue
        qty = _num(pp.get("qty_sq") or pp.get("qty_out"))
        if qty <= 0:
            continue
        lines.append({"source_detail_id": sid_i, "qty_out": qty})
        seen.add(sid_i)

    if not lines:
        return []

    fg_total = _num(fg.get("total_ukuran"))
    if fg_total > 0:
        weights = [_num(x.get("qty_out")) for x in lines]
        parts = _distribute_qty(weights, fg_total)
        for i, line in enumerate(lines):
            line["qty_out"] = parts[i]
    return lines


async def _mrp_json(
    client: httpx.AsyncClient,
    method: str,
    path: str,
    *,
    json_body: dict | None = None,
) -> Any:
    target = f"{_UPSTREAM}/api/mrp/{path.lstrip('/')}"
    upstream = await client.request(method, target, json=json_body)
    if upstream.status_code >= 400:
        try:
            payload = upstream.json()
        except Exception:
            raise HTTPException(status_code=upstream.status_code, detail=upstream.text)
        if isinstance(payload, dict):
            if payload.get("detail") is not None:
                detail = payload["detail"]
            elif payload.get("message") is not None:
                detail = payload["message"]
            else:
                detail = payload
        else:
            detail = payload
        raise HTTPException(status_code=upstream.status_code, detail=detail)
    if not upstream.content:
        return None
    return upstream.json()


class MrpSyncPoIn(BaseModel):
    po_id: Optional[int] = None


@router.post("/sync/po")
def sync_po_from_tonghong(
    body: MrpSyncPoIn | None = None,
    _user=Depends(require_mrp_write),
    db: Session = Depends(get_db),
):
    """ERP push SO → MRP tbl_master_po (jalur utama + retry/reconcile).

    Body opsional ``{ "po_id": N }`` → sync satu SO.
    Tanpa body / tanpa po_id → sync penuh (active + cancelled).
    Boleh dipanggil UI ERP (JWT) atau MRP service (X-Internal-Api-Key).
    """
    from app.models import Notification

    po_id = None
    if body is not None and body.po_id is not None:
        try:
            po_id = int(body.po_id)
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="po_id tidak valid") from None
    try:
        if po_id is not None:
            data = sync_po_details_to_mrp(db, po_id=po_id, raise_on_error=True)
            db.query(Notification).filter(
                Notification.category == "mrp",
                Notification.entity_type == "sales_order",
                Notification.title == "MRP sync gagal",
                Notification.entity_id == po_id,
            ).delete(synchronize_session=False)
        else:
            data = sync_po_details_to_mrp(db, full=True, raise_on_error=True)
            db.query(Notification).filter(
                Notification.category == "mrp",
                Notification.entity_type == "sales_order",
                Notification.title == "MRP sync gagal",
            ).delete(synchronize_session=False)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MRP upstream unavailable: {e}") from e
    return data


class MrpBridgeProductionIn(BaseModel):
    source_detail_id: int
    kode_wip: str
    mrp_packing_id: Optional[int] = None
    qty_planned: Optional[float] = None
    qty_actual: Optional[float] = None
    finish: bool = False


class MrpBridgeStockIssueIn(BaseModel):
    erp_material_id: Optional[int] = None
    material_code: Optional[str] = None
    material_name: Optional[str] = None
    material_type: str = "kimia"
    unit: str = "kg"
    qty: float
    mrp_ref: Optional[str] = None
    warehouse_id: Optional[int] = None


@router.post("/bridge/fg-out")
def bridge_fg_out(
    body: MrpBridgeFgOutIn,
    db: Session = Depends(get_db),
    user=Depends(require_mrp_write),
):
    """Taut mrp_fg_id ke packing/SJ yang sudah ada. Tidak membuat Surat Jalan baru."""
    result = bridge_fg_out_to_delivery(
        db,
        mrp_fg_id=body.mrp_fg_id,
        mrp_packing_id=body.mrp_packing_id,
        kode_packing=body.kode_packing,
        customer_name=body.customer,
        lines=body.lines,
        actor=getattr(user, "username", None),
        keterangan=body.keterangan,
    )
    db.commit()
    if result.po_detail_ids:
        try_sync_po_details_to_mrp(db, detail_ids=result.po_detail_ids)
    return {
        "ok": True,
        "created": result.created,
        "delivery_id": result.delivery_id,
        "delivery_number": result.delivery_number,
        "packing_id": result.packing_id,
        "packing_number": result.packing_number,
        "line_count": result.line_count,
    }


@router.post("/bridge/production-upsert")
def bridge_production_upsert(
    body: MrpBridgeProductionIn,
    db: Session = Depends(get_db),
    user=Depends(require_mrp_write),
):
    result = upsert_production_mirror(
        db,
        source_detail_id=body.source_detail_id,
        kode_wip=body.kode_wip,
        mrp_packing_id=body.mrp_packing_id,
        qty_planned=body.qty_planned,
        qty_actual=body.qty_actual,
        finish=body.finish,
        actor=getattr(user, "username", None),
    )
    db.commit()
    return {
        "ok": True,
        "created": result.created,
        "finished": result.finished,
        "production_id": result.production_id,
        "production_detail_id": result.production_detail_id,
        "production_number": result.production_number,
        "qc_header_id": result.qc_header_id,
    }


@router.post("/bridge/stock-issue")
def bridge_stock_issue(
    body: MrpBridgeStockIssueIn,
    db: Session = Depends(get_db),
    user=Depends(require_mrp_write),
):
    from app.services.mrp_bridge_metrics import snapshot

    result = issue_stock_from_mrp(
        db,
        erp_material_id=body.erp_material_id,
        material_code=body.material_code,
        material_name=body.material_name,
        material_type=body.material_type,
        unit=body.unit,
        qty=body.qty,
        warehouse_id=body.warehouse_id,
        mrp_ref=body.mrp_ref,
        actor=getattr(user, "username", None),
    )
    db.commit()
    return {
        "ok": True,
        "material_id": result.material_id,
        "warehouse_id": result.warehouse_id,
        "qty": float(result.qty),
        "stock_after": float(result.stock_after),
        "metrics": snapshot(),
    }


async def _bridge_stock_from_mrp_response(
    db: Session,
    data: dict,
    user,
) -> dict | None:
    bridge = (data or {}).get("bridge")
    if not bridge or not bridge.get("qty"):
        return None
    result = issue_stock_from_mrp(
        db,
        erp_material_id=bridge.get("erp_material_id"),
        material_code=bridge.get("material_code"),
        material_name=bridge.get("material_name"),
        material_type=bridge.get("material_type") or "kimia",
        unit=bridge.get("unit") or "kg",
        qty=bridge.get("qty"),
        mrp_ref=bridge.get("mrp_ref"),
        actor=getattr(user, "username", None),
    )
    db.commit()
    return {
        "material_id": result.material_id,
        "warehouse_id": result.warehouse_id,
        "stock_after": float(result.stock_after),
    }


async def _run_production_bridge_for_packing(
    client: httpx.AsyncClient,
    db: Session,
    packing_id: int,
    *,
    finish: bool,
    qty_actual: float | None,
    user,
) -> dict | None:
    ctx = await _mrp_json(client, "GET", f"packing/{packing_id}/bridge-context")
    packing = ctx.get("packing") or {}
    lines = ctx.get("lines") or []
    if not lines and ctx.get("line"):
        lines = [ctx.get("line")]
    kode_wip = (packing.get("kode_wip") or "").strip()
    usable = [ln for ln in lines if ln and ln.get("source_detail_id")]
    if not kode_wip or not usable:
        if finish:
            raise HTTPException(
                status_code=400,
                detail="Bridge production gagal: packing tanpa source_detail_id / kode_wip",
            )
        return None
    fg_total = _num(qty_actual) if qty_actual is not None else _num(packing.get("total_ukuran"))
    weights = [_num(ln.get("qty_sq")) for ln in usable]
    if finish and fg_total > 0:
        pack_qtys = _distribute_qty(weights if sum(weights) > 0 else [1.0] * len(usable), fg_total)
    else:
        pack_qtys = [
            (_num(ln.get("qty_sq")) or fg_total or 0.0) for ln in usable
        ]

    mirrored: list[tuple[Any, dict, Any]] = []
    last = None
    for idx, line in enumerate(usable):
        qty_plan = _num(line.get("qty_sq")) or fg_total
        pack_qty = pack_qtys[idx] if idx < len(pack_qtys) else qty_plan
        # qty_planned = alokasi rencana; qty_actual / packing = ukur FG aktual
        last = upsert_production_mirror(
            db,
            source_detail_id=int(line["source_detail_id"]),
            kode_wip=kode_wip,
            mrp_packing_id=packing_id,
            qty_planned=qty_plan if qty_plan > 0 else None,
            qty_actual=pack_qty if finish else (qty_actual if qty_actual is not None else None),
            finish=finish,
            actor=getattr(user, "username", None),
        )
        mirrored.append((last, line, pack_qty if finish else qty_plan))
    if last is None:
        return None
    packing_ready = None
    if finish:
        roll_raw = packing.get("qty_roll")
        if roll_raw is None:
            roll_raw = packing.get("total_rolls")
        try:
            qty_roll = int(roll_raw) if roll_raw is not None else None
        except (TypeError, ValueError):
            qty_roll = None
        packing_ready = ensure_erp_packing_from_mrp_finish(
            db,
            mrp_packing_id=packing_id,
            kode_packing=(packing.get("kode_packing") or "").strip() or None,
            production_id=int(last.production_id),
            lines=[(int(row.production_detail_id), qty) for row, _ln, qty in mirrored],
            actor=getattr(user, "username", None),
            qty_roll=qty_roll,
        )
    db.commit()
    await _mrp_json(
        client,
        "POST",
        f"packing/{packing_id}/production-result",
        json_body={
            "erp_production_id": last.production_id,
            "erp_production_detail_id": last.production_detail_id,
        },
    )
    out = {
        "production_id": last.production_id,
        "production_detail_id": last.production_detail_id,
        "production_number": last.production_number,
        "finished": last.finished,
        "line_count": len(usable),
    }
    if packing_ready is not None:
        out["packing_id"] = packing_ready.packing_id
        out["packing_number"] = packing_ready.packing_number
        out["qc_header_id"] = packing_ready.qc_header_id
    return out


def _sj_rolls_from_fg_detail(fg: dict, packing_rolls: list | None) -> list[dict[str, Any]]:
    fg_status = str(fg.get("status") or "").strip()
    already = fg_status == "out"
    packing_kode = str(fg.get("kode_packing") or "").strip()
    out: list[dict[str, Any]] = []
    for r in packing_rolls or []:
        if not isinstance(r, dict):
            continue
        kode_fg = str(r.get("kode_packing") or packing_kode or "").strip()
        out.append(
            {
                "roll_id": r.get("id"),
                "fg_id": fg.get("id"),
                "kode_fg": kode_fg,
                "kode_packing": kode_fg,
                "packing_kode": packing_kode,
                "roll_no": r.get("roll_no"),
                "lembar": r.get("lembar"),
                "ukuran": r.get("ukuran"),
                "fg_status": fg_status,
                "scanned": already,
            }
        )
    if not out and packing_kode:
        out.append(
            {
                "roll_id": None,
                "fg_id": fg.get("id"),
                "kode_fg": packing_kode,
                "kode_packing": packing_kode,
                "packing_kode": packing_kode,
                "roll_no": 1,
                "lembar": fg.get("total_lembar"),
                "ukuran": fg.get("total_ukuran"),
                "fg_status": fg_status,
                "scanned": already,
            }
        )
    return out


@router.get("/gudang-fg/surat-jalan/pending")
async def gudang_fg_surat_jalan_pending(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Customer yang punya SJ aktif (belum sent) + FG in_stock di MRP."""
    from app.models import DeliveryHeader

    closed = {"sent", "cancelled", "canceled"}
    hdrs = db.scalars(
        select(DeliveryHeader)
        .options(joinedload(DeliveryHeader.customer))
        .where(DeliveryHeader.delivery_number.isnot(None))
        .where(func.trim(DeliveryHeader.delivery_number) != "")
        .order_by(DeliveryHeader.id.desc())
    ).unique().all()

    mrp_by_sj: dict[str, dict[str, Any]] = {}
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            upstream = await client.get(f"{_UPSTREAM}/api/mrp/gudang-fg/surat-jalan/pending")
            if upstream.status_code == 200:
                payload = upstream.json() if upstream.content else {}
                if isinstance(payload, dict):
                    for c in payload.get("customers") or []:
                        cust_name = str((c or {}).get("customer") or "").strip()
                        for d in (c or {}).get("deliveries") or []:
                            key = str((d or {}).get("delivery_number") or "").strip().lower()
                            if not key:
                                continue
                            mrp_by_sj[key] = {**(d or {}), "customer": cust_name}
        except httpx.RequestError:
            pass

    grouped: dict[str, dict[str, Any]] = {}
    seen_sj: set[str] = set()

    for h in hdrs:
        status = str(h.status or "").strip().lower()
        if status in closed:
            continue
        dn = str(h.delivery_number or "").strip()
        if not dn:
            continue
        key = dn.lower()
        mrp = mrp_by_sj.get(key)
        if not mrp and not h.mrp_fg_id:
            continue
        cust = ""
        if h.customer and (h.customer.name or "").strip():
            cust = str(h.customer.name).strip()
        if not cust:
            cust = str((mrp or {}).get("customer") or "").strip() or "—"
        seen_sj.add(key)
        bucket = grouped.setdefault(
            cust,
            {"customer": cust, "customer_id": int(h.customer_id) if h.customer_id else None, "deliveries": []},
        )
        bucket["deliveries"].append(
            {
                "delivery_number": dn,
                "delivery_id": int(h.id),
                "delivery_date": h.delivery_date.isoformat() if h.delivery_date else None,
                "status": h.status,
                "fg_count": (mrp or {}).get("fg_count"),
                "roll_count": (mrp or {}).get("roll_count"),
            }
        )

    for key, mrp in mrp_by_sj.items():
        if key in seen_sj:
            continue
        cust = str(mrp.get("customer") or "").strip() or "—"
        bucket = grouped.setdefault(cust, {"customer": cust, "customer_id": None, "deliveries": []})
        bucket["deliveries"].append(
            {
                "delivery_number": mrp.get("delivery_number"),
                "delivery_id": mrp.get("delivery_id"),
                "delivery_date": None,
                "status": "in_stock",
                "fg_count": mrp.get("fg_count"),
                "roll_count": mrp.get("roll_count"),
            }
        )

    customers = sorted(grouped.values(), key=lambda x: str(x.get("customer") or "").lower())
    return {"customers": customers}


@router.get("/gudang-fg/surat-jalan")
async def gudang_fg_surat_jalan_lookup(
    q: str = "",
    delivery_number: str = "",
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Lookup FG by surat jalan — MRP tbl_gudang_fg, fallback ERP delivery linkage."""
    from app.models import DeliveryDetail, DeliveryHeader, PackingDetail, PackingHeader
    from app.services.delivery_scan_out import resolve_delivery_by_number

    code = (q or delivery_number or "").strip()
    if not code:
        raise HTTPException(status_code=400, detail="Nomor surat jalan wajib")

    async with httpx.AsyncClient(timeout=60.0) as client:
        upstream = await client.get(
            f"{_UPSTREAM}/api/mrp/gudang-fg/surat-jalan",
            params={"q": code},
        )
        if upstream.status_code == 200:
            payload = upstream.json()
            if isinstance(payload, dict) and (payload.get("items") or []):
                return payload

    hdr = resolve_delivery_by_number(db, code)
    fg_ids: set[int] = set()
    if hdr.mrp_fg_id:
        fg_ids.add(int(hdr.mrp_fg_id))
    if hdr.packing_id:
        pk = db.get(PackingHeader, int(hdr.packing_id))
        if pk and pk.mrp_fg_id:
            fg_ids.add(int(pk.mrp_fg_id))
    detail_rows = db.scalars(
        select(DeliveryDetail).where(DeliveryDetail.delivery_id == int(hdr.id))
    ).all()
    pkd_ids = [int(d.packing_detail_id) for d in detail_rows if d.packing_detail_id]
    if pkd_ids:
        for pk in db.scalars(
            select(PackingHeader)
            .join(PackingDetail, PackingDetail.packing_id == PackingHeader.id)
            .where(PackingDetail.id.in_(pkd_ids))
        ).all():
            if pk.mrp_fg_id:
                fg_ids.add(int(pk.mrp_fg_id))

    if not fg_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Surat jalan {code!r} tidak punya FG MRP terhubung",
        )

    items: list[dict[str, Any]] = []
    rolls: list[dict[str, Any]] = []
    customer = ""
    async with httpx.AsyncClient(timeout=60.0) as client:
        for fid in sorted(fg_ids):
            try:
                row = await _mrp_json(client, "GET", f"gudang-fg/{fid}")
            except HTTPException:
                continue
            fg = (row or {}).get("fg") if isinstance(row, dict) else None
            if not isinstance(fg, dict):
                continue
            if not (fg.get("erp_delivery_number") or "").strip():
                fg["erp_delivery_number"] = hdr.delivery_number
            if fg.get("erp_delivery_id") is None:
                fg["erp_delivery_id"] = int(hdr.id)
            items.append(fg)
            rolls.extend(_sj_rolls_from_fg_detail(fg, (row or {}).get("rolls") or []))
            if not customer and (fg.get("customer") or "").strip():
                customer = str(fg.get("customer") or "").strip()

    if not items:
        raise HTTPException(
            status_code=404,
            detail=f"Surat jalan {code!r} tidak punya FG MRP terdaftar",
        )
    return {
        "delivery_number": hdr.delivery_number or code,
        "delivery_id": int(hdr.id),
        "customer": customer,
        "items": items,
        "rolls": rolls,
    }


class MrpGudangFgSjOutIn(BaseModel):
    delivery_number: str
    fg_ids: list[int] = Field(default_factory=list)
    keterangan: Optional[str] = None


@router.post("/gudang-fg/surat-jalan/out")
async def gudang_fg_surat_jalan_out(
    body: MrpGudangFgSjOutIn,
    _user=Depends(require_mrp_write),
):
    """OUT batch FG setelah scan SJ (bypass blokir POST /gudang-fg/out)."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        return await _mrp_json(
            client,
            "POST",
            "gudang-fg/surat-jalan/out",
            json_body={
                "delivery_number": body.delivery_number.strip(),
                "fg_ids": body.fg_ids,
                "keterangan": (body.keterangan or "").strip() or None,
            },
        )


@router.post("/gudang-fg/out")
async def gudang_fg_out_with_bridge(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_mrp_write),
):
    """FG OUT mandiri ditolak. Surat jalan hanya dari Outstanding (susun kirim)."""
    _ = (request, db, user)
    raise HTTPException(status_code=400, detail=FG_OUT_MUST_USE_OUTSTANDING)


@router.post("/packing")
async def packing_create_with_production(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_mrp_write),
):
    body = await request.json()
    async with httpx.AsyncClient(timeout=60.0) as client:
        data = await _mrp_json(client, "POST", "packing", json_body=body)
        packing_id = data.get("id")
        prod = None
        if packing_id:
            try:
                prod = await _run_production_bridge_for_packing(
                    client, db, int(packing_id), finish=False, qty_actual=None, user=user
                )
            except HTTPException:
                db.rollback()
                raise
            except Exception as exc:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Bridge production gagal: {exc}",
                ) from exc
    out = dict(data or {})
    if prod:
        out["erp_production"] = prod
    return out


@router.post("/packing/{packing_id}/actions")
async def packing_actions_with_production(
    packing_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_mrp_write),
):
    body = await request.json()
    action = (body.get("action") or "").strip()
    async with httpx.AsyncClient(timeout=60.0) as client:
        data = await _mrp_json(
            client, "POST", f"packing/{packing_id}/actions", json_body=body
        )
        prod = None
        if action in {"finish", "add_po"}:
            finish = action == "finish"
            qty_actual = None
            if finish:
                detail = await _mrp_json(client, "GET", f"packing/{packing_id}")
                qty_actual = (detail.get("packing") or {}).get("total_ukuran")
            try:
                prod = await _run_production_bridge_for_packing(
                    client,
                    db,
                    packing_id,
                    finish=finish,
                    qty_actual=float(qty_actual) if qty_actual is not None else None,
                    user=user,
                )
            except HTTPException:
                db.rollback()
                raise
            except Exception as exc:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Bridge production gagal: {exc}",
                ) from exc
    out = dict(data or {})
    if prod:
        out["erp_production"] = prod
    return out


async def _proxy_stock_action_with_bridge(
    path: str,
    request: Request,
    db: Session,
    user,
):
    body = await request.json()
    async with httpx.AsyncClient(timeout=60.0) as client:
        data = await _mrp_json(client, "POST", path, json_body=body)
        stock_info = None
        if (body.get("action") == "out") or path.startswith("usage-"):
            if path.startswith("usage-") and not data.get("stok_deducted") and not data.get("bridge"):
                return data
            tujuan = (body.get("tujuan") or data.get("tujuan") or "").strip().lower()
            if body.get("action") == "out" and tujuan in ("lapangan", "mixing"):
                return data
            if not data.get("bridge"):
                return data
            try:
                stock_info = await _bridge_stock_from_mrp_response(db, data, user)
            except Exception as exc:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"Bridge stok ERP gagal: {getattr(exc, 'detail', exc)}",
                ) from exc
    out = dict(data or {})
    if stock_info:
        out["erp_stock"] = stock_info
    return out


@router.post("/stok-kimia")
async def stok_kimia_bridged(
    request: Request, db: Session = Depends(get_db), user=Depends(require_mrp_write)
):
    return await _proxy_stock_action_with_bridge("stok-kimia", request, db, user)


@router.post("/stok-rp")
async def stok_rp_bridged(
    request: Request, db: Session = Depends(get_db), user=Depends(require_mrp_write)
):
    return await _proxy_stock_action_with_bridge("stok-rp", request, db, user)


@router.post("/stok-material-lain")
async def stok_material_lain_bridged(
    request: Request, db: Session = Depends(get_db), user=Depends(require_mrp_write)
):
    return await _proxy_stock_action_with_bridge("stok-material-lain", request, db, user)


@router.post("/usage-color")
async def usage_color_bridged(
    request: Request, db: Session = Depends(get_db), user=Depends(require_mrp_write)
):
    return await _proxy_stock_action_with_bridge("usage-color", request, db, user)


@router.post("/usage-rp")
async def usage_rp_bridged(
    request: Request, db: Session = Depends(get_db), user=Depends(require_mrp_write)
):
    return await _proxy_stock_action_with_bridge("usage-rp", request, db, user)


@router.post("/usage-material-lain")
async def usage_material_lain_bridged(
    request: Request, db: Session = Depends(get_db), user=Depends(require_mrp_write)
):
    return await _proxy_stock_action_with_bridge("usage-material-lain", request, db, user)


@router.post("/checkpoint")
async def checkpoint_create_bridged(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_mrp_write),
):
    """Simpan checkpoint MRP + mirror QcDetail ERP bila treatment = QC."""
    body = await request.json()
    async with httpx.AsyncClient(timeout=60.0) as client:
        data = await _mrp_json(client, "POST", "checkpoint", json_body=body)
        erp_pd = data.get("erp_production_detail_id") or body.get("erp_production_detail_id")
        treatment = str(data.get("treatment") or body.get("treatment") or "").strip()
        is_qc = (not treatment) or treatment.upper() == "QC"
        qc_detail_id = None
        if erp_pd and is_qc:
            try:
                pd_id = int(erp_pd)
                qc = db.scalars(
                    select(QcHeader)
                    .join(QcDetail, QcDetail.qc_id == QcHeader.id)
                    .where(QcDetail.production_detail_id == pd_id)
                    .limit(1)
                ).first()
                if not qc:
                    # attach to any QC for this production detail's production
                    from app.models import ProductionDetail

                    pd = db.get(ProductionDetail, pd_id)
                    if pd and pd.production_id:
                        qc = db.scalars(
                            select(QcHeader)
                            .where(QcHeader.production_id == pd.production_id)
                            .limit(1)
                        ).first()
                        if not qc:
                            from app.services.numbering import next_number
                            from datetime import date as _date

                            qc = QcHeader(
                                qc_number=next_number(db, "QC", "QC"),
                                production_id=pd.production_id,
                                qc_date=_date.today(),
                                operator_name=getattr(user, "username", None) or "mrp",
                            )
                            db.add(qc)
                            db.flush()
                if qc:
                    qd = QcDetail(
                        qc_id=qc.id,
                        production_detail_id=pd_id,
                        thickness_actual=body.get("thickness_actual"),
                        softness_actual=body.get("softness_actual"),
                        result=body.get("result") or ("OK" if data.get("is_ok") else "NG"),
                        is_ok=bool(data.get("is_ok")),
                        remark=body.get("remark") or "Checkpoint MRP",
                        batch_number=body.get("kode_wip"),
                    )
                    db.add(qd)
                    db.flush()
                    qc_detail_id = int(qd.id)
                    db.commit()
                    await _mrp_json(
                        client,
                        "POST",
                        f"checkpoint/{data.get('id')}/qc-result",
                        json_body={"erp_qc_detail_id": qc_detail_id},
                    )
            except Exception as exc:
                db.rollback()
                raise HTTPException(
                    status_code=502,
                    detail=f"Mirror QC ERP gagal: {exc}",
                ) from exc
    out = dict(data or {})
    if qc_detail_id:
        out["erp_qc_detail_id"] = qc_detail_id
    return out


@router.get("/masters/erp")
def masters_erp_from_master_items(
    keyword: Optional[str] = None,
    limit: int = 500,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Sumber tunggal: master_items ERP (bukan salinan master_erp MRP)."""
    lim = max(1, min(int(limit or 500), 2000))
    return list_erp_rows(db, limit=lim, keyword=keyword)


@router.get("/masters/erp/options")
def masters_erp_options_from_swatch_recipes(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return options_for_rencana(db, load_swatch_recipes(db), load_master_items(db))


@router.get("/erp/fields")
def erp_fields_from_master_items(
    thickness: Optional[str] = None,
    material_name: Optional[str] = None,
    color: Optional[str] = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    return fields_from_swatch(
        db,
        load_swatch_recipes(db),
        load_master_items(db),
        thickness=thickness or "",
        material_name=material_name or "",
        color=color or "",
    )


@router.get("/erp/combination")
def erp_combination_from_master_items(
    material_name: str,
    color: str,
    emboss: str,
    thickness: Optional[str] = None,
    color_code: Optional[str] = None,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    master_items = load_master_items(db)
    hits = combination_from_swatch(
        db,
        load_swatch_recipes(db),
        master_items,
        material_name=material_name,
        color=color,
        emboss=emboss,
        thickness=thickness or "",
        color_code=color_code or "",
    )
    if not hits:
        raise HTTPException(
            status_code=404,
            detail="Kombinasi tidak ditemukan di color_swatch_recipes / master_items",
        )
    source = hits[0].get("source") or "color_swatch_recipes"
    return {"options": hits, "source": source}

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_mrp(
    path: str,
    request: Request,
    _user=Depends(_mrp_proxy_user),
):
    target = f"{_UPSTREAM}/api/mrp/{path}"
    if request.url.query:
        target = f"{target}?{request.url.query}"

    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP and k.lower() != "authorization"
    }
    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            upstream = await client.request(
                request.method,
                target,
                content=body,
                headers=headers,
            )
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"MRP upstream unavailable: {e}") from e

    resp_headers = {
        k: v for k, v in upstream.headers.items() if k.lower() not in _HOP_BY_HOP
    }
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        headers=resp_headers,
        media_type=upstream.headers.get("content-type"),
    )
