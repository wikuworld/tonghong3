"""Proxy baca katalog ERP yang dibutuhkan UI MRP (customers, color-swatch form-options)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from mrp_api import erp_client
from mrp_api.models import MrpUser
from mrp_api.routers.auth import get_current_user

router = APIRouter(tags=["erp-catalog-proxy"])


def _proxy_error(exc: erp_client.ErpApiError) -> HTTPException:
    return HTTPException(status_code=exc.status_code or 502, detail=str(exc))


@router.get("/customers")
def proxy_list_customers(
    q: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    _user: MrpUser = Depends(get_current_user),
) -> list[dict[str, Any]]:
    try:
        rows = erp_client.list_customers(q=q, limit=limit)
    except erp_client.ErpApiError as exc:
        raise _proxy_error(exc) from exc
    if offset:
        rows = rows[offset:]
    return rows


@router.get("/customers/{customer_id}")
def proxy_get_customer(customer_id: int, _user: MrpUser = Depends(get_current_user)):
    try:
        row = erp_client.get_customer(int(customer_id))
    except erp_client.ErpApiError as exc:
        raise _proxy_error(exc) from exc
    if not row:
        raise HTTPException(status_code=404, detail="Customer tidak ditemukan")
    return row


@router.get("/masters/color-swatch-recipes/form-options")
def proxy_color_swatch_form_options(_user: MrpUser = Depends(get_current_user)) -> Any:
    try:
        return erp_client.get("/masters/color-swatch-recipes/form-options")
    except erp_client.ErpApiError as exc:
        raise _proxy_error(exc) from exc
