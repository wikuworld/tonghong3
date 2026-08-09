"""Reverse proxy Tonghong JWT-protected routes → Flask MRP service."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session, selectinload

from app.config import settings
from app.db import get_db
from app.models import PoDetail, PoHeader
from app.routers.auth import get_current_user

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
            detail=upstream.json() if upstream.headers.get("content-type", "").startswith("application/json") else upstream.text,
        )
    data = upstream.json()
    data["pulled"] = len(items)
    return data


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
