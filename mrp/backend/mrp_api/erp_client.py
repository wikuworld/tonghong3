"""HTTP client MRP → ERP (API-only; no cross-DB SQL)."""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from mrp_api.config import settings

log = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(15.0, connect=5.0)


class ErpApiError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, body: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


def _base_url() -> str:
    return (settings.erp_api_url or "http://127.0.0.1:8001").rstrip("/")


def _headers() -> dict[str, str]:
    token = (settings.erp_service_token or "").strip()
    h = {"Accept": "application/json"}
    if token:
        h["X-Internal-Api-Key"] = token
    return h


def request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json: Any = None,
    timeout: float | None = None,
) -> Any:
    url = f"{_base_url()}/api/v1{path if path.startswith('/') else '/' + path}"
    t = httpx.Timeout(timeout or 15.0, connect=5.0)
    try:
        with httpx.Client(timeout=t, headers=_headers()) as client:
            resp = client.request(method.upper(), url, params=params, json=json)
    except httpx.RequestError as exc:
        raise ErpApiError(f"ERP unreachable: {exc}") from exc
    if resp.status_code >= 400:
        detail: Any
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise ErpApiError(
            f"ERP HTTP {resp.status_code}: {detail}",
            status_code=resp.status_code,
            body=detail,
        )
    if resp.status_code == 204 or not resp.content:
        return None
    try:
        return resp.json()
    except Exception:
        return resp.text


def get(path: str, *, params: dict[str, Any] | None = None, **kw: Any) -> Any:
    return request("GET", path, params=params, **kw)


def post(path: str, *, json: Any = None, params: dict[str, Any] | None = None, **kw: Any) -> Any:
    return request("POST", path, params=params, json=json, **kw)


def put(path: str, *, json: Any = None, **kw: Any) -> Any:
    return request("PUT", path, json=json, **kw)


def delete(path: str, **kw: Any) -> Any:
    return request("DELETE", path, **kw)


# ---- typed helpers ----

def list_warehouses() -> list[dict]:
    data = get("/inventory/warehouses")
    return list(data or [])


def list_warehouses_page(
    *,
    q: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    sort_by: str | None = None,
    sort_dir: str | None = None,
) -> dict:
    params: dict[str, Any] = {}
    if q:
        params["q"] = q
    if page is not None:
        params["page"] = page
    if page_size is not None:
        params["page_size"] = page_size
    if sort_by:
        params["sort_by"] = sort_by
        params["sort_dir"] = sort_dir or "asc"
    data = get("/inventory/warehouses/page", params=params)
    return dict(data or {})


def list_materials(
    *,
    material_type: str | None = None,
    code: str | None = None,
    q: str | None = None,
    active_only: bool = True,
    limit: int = 2000,
) -> list[dict]:
    params: dict[str, Any] = {"limit": limit, "active_only": active_only}
    if material_type:
        params["material_type"] = material_type
    if code:
        params["code"] = code
    if q:
        params["q"] = q
    data = get("/inventory/materials", params=params)
    return list(data or [])


def list_materials_page(
    *,
    material_type: str | None = None,
    code: str | None = None,
    q: str | None = None,
    active_only: bool = True,
    page: int | None = None,
    page_size: int | None = None,
    sort_by: str | None = None,
    sort_dir: str | None = None,
) -> dict:
    params: dict[str, Any] = {"active_only": active_only}
    if material_type:
        params["material_type"] = material_type
    if code:
        params["code"] = code
    if q:
        params["q"] = q
    if page is not None:
        params["page"] = page
    if page_size is not None:
        params["page_size"] = page_size
    if sort_by:
        params["sort_by"] = sort_by
        params["sort_dir"] = sort_dir or "asc"
    data = get("/inventory/materials/page", params=params)
    return dict(data or {})


def get_material(material_id: int) -> Optional[dict]:
    try:
        data = get(f"/inventory/materials/{int(material_id)}")
    except ErpApiError as exc:
        if exc.status_code == 404:
            return None
        raise
    return dict(data) if data else None


def list_stocks(
    *,
    warehouse_id: int | None = None,
    material_id: int | None = None,
    low_stock: bool = False,
) -> list[dict]:
    params: dict[str, Any] = {}
    if warehouse_id:
        params["warehouse_id"] = warehouse_id
    if material_id:
        params["material_id"] = material_id
    if low_stock:
        params["low_stock"] = True
    data = get("/inventory/stocks", params=params)
    return list(data or [])


def list_stocks_page(
    *,
    warehouse_id: int | None = None,
    material_id: int | None = None,
    low_stock: bool = False,
    page: int | None = None,
    page_size: int | None = None,
    sort_by: str | None = None,
    sort_dir: str | None = None,
) -> dict:
    params: dict[str, Any] = {}
    if warehouse_id:
        params["warehouse_id"] = warehouse_id
    if material_id:
        params["material_id"] = material_id
    if low_stock:
        params["low_stock"] = True
    if page is not None:
        params["page"] = page
    if page_size is not None:
        params["page_size"] = page_size
    if sort_by:
        params["sort_by"] = sort_by
        params["sort_dir"] = sort_dir or "asc"
    data = get("/inventory/stocks/page", params=params)
    return dict(data or {})


def stock_summary() -> dict:
    data = get("/inventory/stocks/summary")
    return dict(data or {})


def resolve_customer(q: str, *, create: bool = False) -> Optional[dict]:
    params: dict[str, Any] = {"q": q, "create": create}
    data = get("/customers/resolve", params=params)
    if not data:
        return None
    return dict(data)


def get_customer(customer_id: int) -> Optional[dict]:
    try:
        data = get(f"/customers/{int(customer_id)}")
    except ErpApiError as exc:
        if exc.status_code == 404:
            return None
        raise
    return dict(data) if data else None


def list_customers(*, q: str | None = None, limit: int = 500) -> list[dict]:
    params: dict[str, Any] = {"limit": limit}
    if q:
        params["q"] = q
    data = get("/customers", params=params)
    return list(data or [])


def list_master_items(*, limit: int | None = None) -> list[dict]:
    params: dict[str, Any] = {}
    if limit:
        params["limit"] = limit
    data = get("/masters/items", params=params)
    return list(data or [])


def master_items_page(
    *,
    limit: int = 50,
    offset: int = 0,
    keyword: str | None = None,
    category: str | None = None,
    sort_by: str | None = None,
    sort_dir: str = "asc",
) -> tuple[list[dict], int]:
    params: dict[str, Any] = {"limit": limit, "offset": offset}
    if keyword:
        params["keyword"] = keyword
    if category:
        params["category"] = category
    if sort_by:
        params["sort_by"] = sort_by
        params["sort_dir"] = sort_dir or "asc"
    data = get("/masters/items/page", params=params)
    if isinstance(data, dict):
        return list(data.get("items") or []), int(data.get("total") or 0)
    return list(data or []), len(data or [])


def resolve_master_by_dimensions(
    *,
    material_name: str = "",
    thickness: str = "",
    color: str = "",
    emboss: str = "",
) -> Optional[dict]:
    params: dict[str, Any] = {
        "material_name": material_name,
        "thickness_text": thickness,
        "color": color,
    }
    if emboss and str(emboss).strip() and str(emboss).strip() != "-":
        params["emboss"] = emboss
    data = get("/masters/items/resolve-by-dimensions", params=params)
    if isinstance(data, dict):
        item = data.get("item")
        if item:
            return dict(item)
        candidates = data.get("candidates") or []
        if isinstance(candidates, list) and candidates:
            return dict(candidates[0])
    return None


def list_inventory_units(
    *,
    material_type: str | None = None,
    active_only: bool = True,
) -> list[dict]:
    params: dict[str, Any] = {"active_only": active_only}
    if material_type:
        params["material_type"] = material_type
    data = get("/inventory/units", params=params)
    return list(data) if isinstance(data, list) else []


def create_inventory_unit(body: dict[str, Any]) -> dict:
    data = post("/inventory/units", json=body)
    return dict(data) if data else {}


def update_inventory_unit(unit_id: int, body: dict[str, Any]) -> dict:
    data = put(f"/inventory/units/{int(unit_id)}", json=body)
    return dict(data) if data else {}


def delete_inventory_unit(unit_id: int) -> dict:
    data = delete(f"/inventory/units/{int(unit_id)}")
    return dict(data) if isinstance(data, dict) else {"status": "deactivated"}


def create_material(body: dict[str, Any]) -> dict:
    data = post("/inventory/materials", json=body)
    return dict(data) if data else {}


def update_material(material_id: int, body: dict[str, Any]) -> dict:
    data = put(f"/inventory/materials/{int(material_id)}", json=body)
    return dict(data) if data else {}


def upsert_material(
    *,
    code: str,
    name: str,
    material_type: str,
    unit: str = "kg",
) -> Optional[dict]:
    data = post(
        "/inventory/materials/upsert",
        json={
            "code": code,
            "name": name,
            "material_type": material_type,
            "unit": unit,
            "is_active": True,
        },
    )
    return dict(data) if data else None


def request_po_sync(*, po_id: int | None = None) -> dict:
    """Minta ERP push SO ke MRP (reconcile)."""
    payload: dict[str, Any] = {}
    if po_id is not None:
        payload["po_id"] = int(po_id)
    data = post("/mrp/sync/po", json=payload)
    return dict(data) if isinstance(data, dict) else {"ok": True, "raw": data}


def po_detail_mrp_lines_by_lots(lots: list[str]) -> dict[str, dict[str, str]]:
    """ERP po_detail by Lot No (thi_line_ref) — authoritative when master_po cache stale."""
    cleaned = []
    seen: set[str] = set()
    for raw in lots or []:
        lot = str(raw or "").strip()
        if not lot or lot in seen:
            continue
        seen.add(lot)
        cleaned.append(lot)
    if not cleaned:
        return {}
    params = {"lots": ",".join(cleaned)}
    data = get("/po-details/mrp-lines-by-lots", params=params)
    out: dict[str, dict[str, str]] = {}
    if not isinstance(data, dict):
        return out
    raw = data.get("lines") or {}
    if not isinstance(raw, dict):
        return out
    for k, v in raw.items():
        key = str(k or "").strip()
        if not key or not isinstance(v, dict):
            continue
        out[key] = {str(kk): str(vv or "").strip() for kk, vv in v.items()}
    return out


def po_detail_mrp_lines(ids: list[int]) -> dict[int, dict[str, str]]:
    """Material + lot + PO refs from ERP po_details (for rencana produksi display)."""
    if not ids:
        return {}
    params = {"ids": ",".join(str(i) for i in ids)}
    data = get("/po-details/mrp-lines", params=params)
    out: dict[int, dict[str, str]] = {}
    if not isinstance(data, dict):
        return out
    raw = data.get("lines") or {}
    if not isinstance(raw, dict):
        return out
    for k, v in raw.items():
        try:
            sid = int(k)
        except (TypeError, ValueError):
            continue
        if isinstance(v, dict):
            out[sid] = {str(kk): str(vv or "").strip() for kk, vv in v.items()}
    return out


def po_detail_lot_refs(ids: list[int]) -> dict[int, str]:
    if not ids:
        return {}
    params = {"ids": ",".join(str(i) for i in ids)}
    data = get("/po-details/lot-refs", params=params)
    out: dict[int, str] = {}
    if isinstance(data, dict):
        raw = data.get("refs") or data
        if isinstance(raw, dict):
            for k, v in raw.items():
                try:
                    out[int(k)] = str(v or "").strip()
                except (TypeError, ValueError):
                    continue
        elif isinstance(raw, list):
            for row in raw:
                try:
                    sid = int(row.get("id"))
                except (TypeError, ValueError, AttributeError):
                    continue
                lot = (
                    (row.get("lot_ref") or row.get("thi_line_ref") or row.get("system_reference") or "")
                    .strip()
                )
                if lot:
                    out[sid] = lot
    return out
