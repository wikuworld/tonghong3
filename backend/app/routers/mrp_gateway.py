"""Reverse proxy Tonghong JWT-protected routes → Flask MRP service."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.db import get_db
from app.models import PoDetail, PoHeader
from app.routers.auth import get_current_user
from app.services.mrp_fg_delivery_bridge import bridge_fg_out_to_delivery

router = APIRouter(prefix="/mrp", tags=["mrp"])

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


def _thickness_text(d: PoDetail) -> str:
    if d.thickness_text:
        return str(d.thickness_text).strip()
    if d.thickness_min is not None and d.thickness_max is not None:
        return f"{d.thickness_min}-{d.thickness_max}"
    if d.thickness_min is not None:
        return str(d.thickness_min)
    return ""


def _map_po_detail(d: PoDetail) -> Optional[dict]:
    po: Optional[PoHeader] = d.po
    if not po:
        return None
    no_po = (po.po_number or po.po_customer_ref or "").strip()
    if not no_po:
        return None
    item_name = (d.material_name or d.style_article or f"LINE-{d.id}").strip()
    swatch = ""
    if d.color_swatch_recipe is not None:
        swatch = (d.color_swatch_recipe.color_code or d.color_swatch_recipe.color_name or "").strip()
    if not swatch:
        swatch = (d.color_reference or d.color_standard or "").strip()
    qty = _num(d.balance_qty) if d.balance_qty is not None else _num(d.quantity_order)
    return {
        "source_detail_id": d.id,
        "no_po": no_po,
        "no_so": (po.po_customer_ref or po.po_number or "").strip() or None,
        "customer": (po.customer_name_snapshot or po.customer_code or "").strip() or None,
        "item_name": item_name,
        "warna": (d.color or "").strip(),
        "tebal": _thickness_text(d),
        "emboss": (d.emboss or "").strip(),
        "color_swatch": swatch or None,
        "sq_ft": qty,
        "qty_order": qty,
    }


class MrpBridgeFgOutIn(BaseModel):
    mrp_fg_id: int
    mrp_packing_id: Optional[int] = None
    kode_packing: Optional[str] = None
    customer: Optional[str] = None
    keterangan: Optional[str] = None
    lines: list[dict[str, Any]] = Field(default_factory=list)


def _collect_bridge_lines(detail: dict[str, Any], fg: dict[str, Any]) -> list[dict[str, Any]]:
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
            qty = _num(fg.get("total_ukuran"))
        if qty <= 0:
            continue
        lines.append({"source_detail_id": sid_i, "qty_out": qty})
        seen.add(sid_i)

    # Fallback: satu baris dari packing_pos/bridge kosong → bagi total_ukuran ke semua
    if not lines:
        return []

    total_assigned = sum(_num(x.get("qty_out")) for x in lines)
    fg_total = _num(fg.get("total_ukuran"))
    if total_assigned <= 0 and fg_total > 0 and len(lines) == 1:
        lines[0]["qty_out"] = fg_total
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
        detail: Any
        try:
            detail = upstream.json()
        except Exception:
            detail = upstream.text
        raise HTTPException(status_code=upstream.status_code, detail=detail)
    if not upstream.content:
        return None
    return upstream.json()


@router.post("/sync/po")
async def sync_po_from_tonghong(
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Pull PO details from Tonghong DB and upsert into MRP tbl_master_po."""
    details = (
        db.query(PoDetail)
        .options(
            selectinload(PoDetail.po),
            selectinload(PoDetail.color_swatch_recipe),
        )
        .join(PoHeader, PoDetail.po_id == PoHeader.id)
        .filter(PoHeader.status.notin_(["cancelled", "void"]))
        .order_by(PoDetail.id.desc())
        .limit(2000)
        .all()
    )
    items = []
    for d in details:
        mapped = _map_po_detail(d)
        if mapped:
            items.append(mapped)
    if not items:
        return {"ok": True, "inserted": 0, "updated": 0, "total": 0, "detail": "no PO lines"}

    target = f"{_UPSTREAM}/api/mrp/masters/po/sync"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            upstream = await client.post(target, json={"items": items})
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"MRP upstream unavailable: {e}") from e

    if upstream.status_code >= 400:
        raise HTTPException(
            status_code=upstream.status_code,
            detail=upstream.json()
            if upstream.headers.get("content-type", "").startswith("application/json")
            else upstream.text,
        )
    data = upstream.json()
    data["pulled"] = len(items)
    return data


@router.post("/bridge/fg-out")
def bridge_fg_out(
    body: MrpBridgeFgOutIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Buat Delivery draft ERP dari FG OUT MRP (idempotent per mrp_fg_id)."""
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
    return {
        "ok": True,
        "created": result.created,
        "delivery_id": result.delivery_id,
        "delivery_number": result.delivery_number,
        "packing_id": result.packing_id,
        "packing_number": result.packing_number,
        "line_count": result.line_count,
    }


@router.post("/gudang-fg/out")
async def gudang_fg_out_with_bridge(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """FG OUT MRP + bridge Delivery draft ERP; rollback lokal jika bridge gagal."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    if not isinstance(body, dict):
        body = {}
    kode_packing = (body.get("kode_packing") or "").strip()
    keterangan = body.get("keterangan") or ""
    if not kode_packing:
        raise HTTPException(status_code=400, detail="kode_packing wajib")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            out_data = await _mrp_json(
                client,
                "POST",
                "gudang-fg/out",
                json_body={"kode_packing": kode_packing, "keterangan": keterangan},
            )
            fg_id = int(out_data.get("id"))
            detail = await _mrp_json(client, "GET", f"gudang-fg/{fg_id}")
            fg = detail.get("fg") or {}
            packing = detail.get("packing") or {}
            lines = _collect_bridge_lines(detail, fg)

            try:
                result = bridge_fg_out_to_delivery(
                    db,
                    mrp_fg_id=fg_id,
                    mrp_packing_id=fg.get("packing_id") or packing.get("id"),
                    kode_packing=kode_packing,
                    customer_name=fg.get("customer"),
                    lines=lines,
                    actor=getattr(user, "username", None),
                    keterangan=keterangan,
                )
                db.commit()
            except Exception as bridge_exc:
                db.rollback()
                reason = str(getattr(bridge_exc, "detail", None) or bridge_exc)[:255]
                try:
                    await _mrp_json(
                        client,
                        "POST",
                        f"gudang-fg/{fg_id}/rollback-out",
                        json_body={"reason": reason},
                    )
                except Exception:
                    pass
                if isinstance(bridge_exc, HTTPException):
                    raise bridge_exc
                raise HTTPException(status_code=400, detail=f"Bridge Delivery gagal: {reason}") from bridge_exc

            await _mrp_json(
                client,
                "POST",
                f"gudang-fg/{fg_id}/bridge-result",
                json_body={
                    "delivery_id": result.delivery_id,
                    "delivery_number": result.delivery_number,
                    "bridge_status": "ok",
                },
            )
    except HTTPException:
        raise
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"MRP upstream unavailable: {e}") from e

    return {
        "ok": True,
        "id": fg_id,
        "kode_packing": kode_packing,
        "erp_delivery_id": result.delivery_id,
        "erp_delivery_number": result.delivery_number,
        "erp_packing_id": result.packing_id,
        "bridge_created": result.created,
        "bridge_status": "ok",
    }


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_mrp(
    path: str,
    request: Request,
    _user=Depends(get_current_user),
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
