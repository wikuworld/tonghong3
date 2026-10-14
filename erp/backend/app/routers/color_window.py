"""Master Color Window — CRUD."""

from __future__ import annotations

import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Brand, ColorWindowMaster
from app.routers.auth import get_current_user, require_roles
from app.services.color_window import (
    ensure_brand_code,
    normalize_color_window_fields,
)
from app.services.color_window_excel import (
    export_color_windows_template_xlsx,
    export_color_windows_xlsx,
    import_color_windows_xlsx,
)
from app.timeutil import app_now

router = APIRouter(tags=["color-window"])


class ColorWindowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    color_code: str
    color_name: str
    brand_code: str
    remark: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ColorWindowPageOut(BaseModel):
    items: list[ColorWindowOut]
    total: int
    limit: int
    offset: int


class ColorWindowIn(BaseModel):
    color_code: str = Field(..., min_length=1, max_length=64)
    color_name: str = Field(..., min_length=1, max_length=255)
    brand_code: str = Field(..., min_length=1, max_length=50)
    remark: Optional[str] = Field(default=None, max_length=4000)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ColorWindowFormOptionsOut(BaseModel):
    brand_codes: list[str] = Field(default_factory=list)


_SORTABLE = {
    "created_at": ColorWindowMaster.created_at,
    "updated_at": ColorWindowMaster.updated_at,
    "brand_code": ColorWindowMaster.brand_code,
    "color_code": ColorWindowMaster.color_code,
    "color_name": ColorWindowMaster.color_name,
}


@router.get("/masters/color-windows/page", response_model=ColorWindowPageOut)
def list_color_windows_page(
    brand_code: Optional[str] = None,
    q: Optional[str] = Query(None),
    sort_by: Optional[str] = None,
    sort_dir: str = Query("asc"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> ColorWindowPageOut:
    stmt = select(ColorWindowMaster)
    count_stmt = select(func.count(ColorWindowMaster.id))
    if brand_code:
        b = brand_code.strip().upper()
        stmt = stmt.where(ColorWindowMaster.brand_code == b)
        count_stmt = count_stmt.where(ColorWindowMaster.brand_code == b)
    if q:
        like = f"%{q.strip()}%"
        clause = or_(
            ColorWindowMaster.color_name.ilike(like),
            ColorWindowMaster.color_code.ilike(like),
            ColorWindowMaster.brand_code.ilike(like),
            ColorWindowMaster.remark.ilike(like),
        )
        stmt = stmt.where(clause)
        count_stmt = count_stmt.where(clause)
    total = int(db.scalar(count_stmt) or 0)
    col = _SORTABLE.get((sort_by or "").strip().lower())
    if col is not None:
        primary = col.desc() if sort_dir.strip().lower() == "desc" else col.asc()
        order = (primary, ColorWindowMaster.id.asc())
    else:
        order = (ColorWindowMaster.brand_code.asc(), ColorWindowMaster.color_code.asc(), ColorWindowMaster.id.asc())
    items = list(db.scalars(stmt.order_by(*order).limit(limit).offset(offset)).all())
    return ColorWindowPageOut(items=items, total=total, limit=limit, offset=offset)


@router.get("/masters/color-windows/form-options", response_model=ColorWindowFormOptionsOut)
def color_window_form_options(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> ColorWindowFormOptionsOut:
    codes = list(
        db.scalars(
            select(Brand.code)
            .where(Brand.code.is_not(None), Brand.code != "")
            .order_by(Brand.code.asc())
        ).all()
    )
    return ColorWindowFormOptionsOut(brand_codes=[c for c in codes if c])


@router.get("/masters/color-windows/export")
def export_color_windows(
    template: bool = Query(False, description="Jika true, unduh template kosong (header saja)"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    if template:
        excel_content = export_color_windows_template_xlsx()
        filename = "color_window_template.xlsx"
    else:
        excel_content = export_color_windows_xlsx(db)
        filename = "color_window.xlsx"
    return StreamingResponse(
        io.BytesIO(excel_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/masters/color-windows/import")
async def import_color_windows(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File Excel kosong")
    try:
        result = import_color_windows_xlsx(db, content)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result.to_dict()


@router.post("/masters/color-windows", response_model=ColorWindowOut)
def create_color_window(
    body: ColorWindowIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> ColorWindowOut:
    try:
        data = normalize_color_window_fields(body.model_dump())
        ensure_brand_code(db, data["brand_code"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    row = ColorWindowMaster(
        **data,
        created_at=body.created_at or app_now(),
        updated_at=body.updated_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ColorWindowOut.model_validate(row)


@router.put("/masters/color-windows/{row_id}", response_model=ColorWindowOut)
def update_color_window(
    row_id: int,
    body: ColorWindowIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> ColorWindowOut:
    row = db.get(ColorWindowMaster, row_id)
    if not row:
        raise HTTPException(status_code=404, detail="Color Window tidak ditemukan")
    try:
        data = normalize_color_window_fields(body.model_dump())
        ensure_brand_code(db, data["brand_code"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    for k, v in data.items():
        setattr(row, k, v)
    if "created_at" in body.model_fields_set:
        row.created_at = body.created_at
    row.updated_at = body.updated_at if "updated_at" in body.model_fields_set else app_now()
    db.commit()
    db.refresh(row)
    return ColorWindowOut.model_validate(row)


@router.delete("/masters/color-windows/{row_id}")
def delete_color_window(
    row_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(ColorWindowMaster, row_id)
    if not row:
        raise HTTPException(status_code=404, detail="Color Window tidak ditemukan")
    db.delete(row)
    db.commit()
    return {"status": "ok"}
