"""Inventory read-proxy ke ERP API (write katalog hanya di ERP UI)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from mrp_api import erp_client
from mrp_api.models import MrpUser
from mrp_api.routers.auth import get_current_user

router = APIRouter(prefix="/inventory", tags=["inventory"])

_WRITE_BLOCKED = "Mutasi inventory hanya di ERP. Gunakan UI/API ERP (/inventory)."


class WarehouseIn(BaseModel):
    code: str
    name: str
    location: Optional[str] = None
    is_active: bool = True


class WarehousePatch(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class MaterialIn(BaseModel):
    code: str
    name: str
    material_type: str
    unit: str
    default_warehouse_id: Optional[int] = None
    min_stock: Optional[float] = None
    cost_price: Optional[float] = None
    thickness: Optional[str] = None
    color: Optional[str] = None
    leather_type: Optional[str] = None
    is_active: bool = True


class MaterialPatch(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    material_type: Optional[str] = None
    unit: Optional[str] = None
    default_warehouse_id: Optional[int] = None
    min_stock: Optional[float] = None
    cost_price: Optional[float] = None
    thickness: Optional[str] = None
    color: Optional[str] = None
    leather_type: Optional[str] = None
    is_active: Optional[bool] = None


def _map_stock_row(row: dict[str, Any]) -> dict[str, Any]:
    """Flatten nested ERP MaterialStockOut for MRP UI compatibility."""
    mat = row.get("material") or {}
    wh = row.get("warehouse") or {}
    return {
        "id": row.get("id"),
        "material_id": row.get("material_id"),
        "warehouse_id": row.get("warehouse_id"),
        "current_stock": row.get("current_stock"),
        "reserved_stock": row.get("reserved_stock"),
        "updated_at": row.get("updated_at"),
        "material_code": mat.get("code") if isinstance(mat, dict) else None,
        "material_name": mat.get("name") if isinstance(mat, dict) else None,
        "material_unit": mat.get("unit") if isinstance(mat, dict) else None,
        "min_stock": mat.get("min_stock") if isinstance(mat, dict) else None,
        "warehouse_name": wh.get("name") if isinstance(wh, dict) else None,
        "material": mat,
        "warehouse": wh,
    }


@router.get("/warehouses")
def list_warehouses(_user: MrpUser = Depends(get_current_user)):
    try:
        return erp_client.list_warehouses()
    except erp_client.ErpApiError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc)) from exc


@router.get("/warehouses/page")
def list_warehouses_page(
    q: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    sort_by: str | None = None,
    sort_dir: str | None = None,
    _user: MrpUser = Depends(get_current_user),
):
    try:
        return erp_client.list_warehouses_page(
            q=q, page=page, page_size=page_size, sort_by=sort_by, sort_dir=sort_dir
        )
    except erp_client.ErpApiError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc)) from exc


@router.post("/warehouses")
def create_warehouse(body: WarehouseIn, _user: MrpUser = Depends(get_current_user)):
    raise HTTPException(status_code=403, detail=_WRITE_BLOCKED)


@router.put("/warehouses/{warehouse_id}")
def update_warehouse(
    warehouse_id: int, body: WarehousePatch, _user: MrpUser = Depends(get_current_user)
):
    raise HTTPException(status_code=403, detail=_WRITE_BLOCKED)


@router.delete("/warehouses/{warehouse_id}")
def delete_warehouse(warehouse_id: int, _user: MrpUser = Depends(get_current_user)):
    raise HTTPException(status_code=403, detail=_WRITE_BLOCKED)


@router.get("/materials")
def list_materials(_user: MrpUser = Depends(get_current_user)):
    try:
        return erp_client.list_materials(active_only=False, limit=5000)
    except erp_client.ErpApiError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc)) from exc


@router.get("/materials/page")
def list_materials_page(
    material_type: str | None = None,
    code: str | None = None,
    q: str | None = None,
    active_only: bool = True,
    page: int | None = None,
    page_size: int | None = None,
    sort_by: str | None = None,
    sort_dir: str | None = None,
    _user: MrpUser = Depends(get_current_user),
):
    try:
        return erp_client.list_materials_page(
            material_type=material_type,
            code=code,
            q=q,
            active_only=active_only,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
    except erp_client.ErpApiError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc)) from exc


@router.post("/materials")
def create_material(body: MaterialIn, user: MrpUser = Depends(get_current_user)):
    if user.role not in ("admin", "warehouse", "gudang", "supervisor"):
        raise HTTPException(status_code=403, detail=_WRITE_BLOCKED)
    try:
        return erp_client.create_material(body.model_dump(exclude_none=True))
    except erp_client.ErpApiError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc)) from exc


@router.put("/materials/{material_id}")
def update_material(
    material_id: int, body: MaterialPatch, user: MrpUser = Depends(get_current_user)
):
    if user.role not in ("admin", "warehouse", "gudang", "supervisor"):
        raise HTTPException(status_code=403, detail=_WRITE_BLOCKED)
    try:
        return erp_client.update_material(
            material_id, body.model_dump(exclude_unset=True)
        )
    except erp_client.ErpApiError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc)) from exc


@router.delete("/materials/{material_id}")
def delete_material(material_id: int, _user: MrpUser = Depends(get_current_user)):
    raise HTTPException(status_code=403, detail=_WRITE_BLOCKED)


@router.get("/stocks")
def list_stocks(
    warehouse_id: int | None = None,
    material_id: int | None = None,
    low_stock: bool = False,
    _user: MrpUser = Depends(get_current_user),
):
    try:
        rows = erp_client.list_stocks(
            warehouse_id=warehouse_id, material_id=material_id, low_stock=low_stock
        )
    except erp_client.ErpApiError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc)) from exc
    return [_map_stock_row(r) if isinstance(r, dict) else r for r in rows]


@router.get("/stocks/page")
def list_stocks_page(
    warehouse_id: int | None = None,
    material_id: int | None = None,
    low_stock: bool = False,
    page: int | None = None,
    page_size: int | None = None,
    sort_by: str | None = None,
    sort_dir: str | None = None,
    _user: MrpUser = Depends(get_current_user),
):
    try:
        data = erp_client.list_stocks_page(
            warehouse_id=warehouse_id,
            material_id=material_id,
            low_stock=low_stock,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
    except erp_client.ErpApiError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc)) from exc
    if isinstance(data, dict):
        items = data.get("items") or []
        data = {
            **data,
            "items": [_map_stock_row(r) if isinstance(r, dict) else r for r in items],
        }
    return data


@router.get("/stocks/summary")
def stock_summary(_user: MrpUser = Depends(get_current_user)):
    try:
        return erp_client.stock_summary()
    except erp_client.ErpApiError as exc:
        raise HTTPException(status_code=exc.status_code or 502, detail=str(exc)) from exc
