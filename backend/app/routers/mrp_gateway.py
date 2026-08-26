"""Reverse proxy Tonghong JWT-protected routes → Flask MRP service."""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session


from app.config import settings
from app.db import get_db
from app.models import QcDetail, QcHeader
from app.routers.auth import get_current_user
from app.services.mrp_fg_delivery_bridge import bridge_fg_out_to_delivery
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


@router.post("/sync/po")
def sync_po_from_tonghong(
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Pull PO details from Tonghong DB and upsert into MRP tbl_master_po."""
    try:
        data = sync_po_details_to_mrp(db, full=True, raise_on_error=True)
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
    user=Depends(get_current_user),
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
    user=Depends(get_current_user),
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
    line = ctx.get("line") or {}
    sid = line.get("source_detail_id")
    kode_wip = (packing.get("kode_wip") or "").strip()
    if not sid or not kode_wip:
        return None
    qty = line.get("qty_sq") or packing.get("total_ukuran")
    result = upsert_production_mirror(
        db,
        source_detail_id=int(sid),
        kode_wip=kode_wip,
        mrp_packing_id=packing_id,
        qty_planned=qty,
        qty_actual=qty_actual if qty_actual is not None else (qty if finish else None),
        finish=finish,
        actor=getattr(user, "username", None),
    )
    db.commit()
    await _mrp_json(
        client,
        "POST",
        f"packing/{packing_id}/production-result",
        json_body={
            "erp_production_id": result.production_id,
            "erp_production_detail_id": result.production_detail_id,
        },
    )
    return {
        "production_id": result.production_id,
        "production_detail_id": result.production_detail_id,
        "production_number": result.production_number,
        "finished": result.finished,
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
                if result.po_detail_ids:
                    try_sync_po_details_to_mrp(db, detail_ids=result.po_detail_ids)
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


@router.post("/packing")
async def packing_create_with_production(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
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
            except Exception:
                db.rollback()
                prod = None
    out = dict(data or {})
    if prod:
        out["erp_production"] = prod
    return out


@router.post("/packing/{packing_id}/actions")
async def packing_actions_with_production(
    packing_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
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
            except Exception:
                db.rollback()
                prod = None
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
    request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return await _proxy_stock_action_with_bridge("stok-kimia", request, db, user)


@router.post("/stok-rp")
async def stok_rp_bridged(
    request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return await _proxy_stock_action_with_bridge("stok-rp", request, db, user)


@router.post("/stok-material-lain")
async def stok_material_lain_bridged(
    request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return await _proxy_stock_action_with_bridge("stok-material-lain", request, db, user)


@router.post("/usage-color")
async def usage_color_bridged(
    request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return await _proxy_stock_action_with_bridge("usage-color", request, db, user)


@router.post("/usage-rp")
async def usage_rp_bridged(
    request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)
):
    return await _proxy_stock_action_with_bridge("usage-rp", request, db, user)


@router.post("/checkpoint")
async def checkpoint_create_bridged(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
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
            except Exception:
                db.rollback()
                qc_detail_id = None
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
    hits = combination_from_swatch(
        db,
        load_swatch_recipes(db),
        load_master_items(db),
        material_name=material_name,
        color=color,
        emboss=emboss,
        thickness=thickness or "",
        color_code=color_code or "",
    )
    if not hits:
        raise HTTPException(
            status_code=404,
            detail="Kombinasi tidak ditemukan di color_swatch_recipes",
        )
    return {"options": hits, "source": "color_swatch_recipes"}


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
