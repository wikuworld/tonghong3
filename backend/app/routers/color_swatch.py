"""Master color swatch recipes — CRUD, import CSV, lookup PO."""

from __future__ import annotations

import io
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ColorSwatchRecipe
from app.routers.auth import get_current_user, require_roles
from app.services.color_swatch import (
    import_recipes,
    iter_csv_recipes,
    normalize_factory_key,
    recipe_to_po_fill,
    resolve_swatch_factory_keys,
)

router = APIRouter(tags=["color-swatch"])


class ColorSwatchRecipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    factory_key: str
    customer_id: Optional[int] = None
    buyer_code: str
    brand_id: Optional[int] = None
    color_code: str
    color_name: str
    emboss: str
    color_standard: Optional[str] = None
    backing: Optional[str] = None
    material_name: str
    legacy_urut: Optional[str] = None
    entered_at: Optional[date] = None
    source_file: Optional[str] = None
    is_active: bool = True


class ColorSwatchRecipePageOut(BaseModel):
    items: list[ColorSwatchRecipeOut]
    total: int
    limit: int
    offset: int


class ColorSwatchRecipeIn(BaseModel):
    factory_key: str = Field(..., min_length=1, max_length=80)
    customer_id: Optional[int] = None
    buyer_code: str = Field(..., min_length=1, max_length=32)
    brand_id: Optional[int] = None
    color_code: str = Field(default="", max_length=64)
    color_name: str = Field(..., min_length=1, max_length=255)
    emboss: str = Field(default="", max_length=255)
    color_standard: Optional[str] = Field(default=None, max_length=255)
    backing: Optional[str] = Field(default=None, max_length=120)
    material_name: str = Field(..., min_length=1, max_length=500)
    legacy_urut: Optional[str] = Field(default=None, max_length=32)
    entered_at: Optional[date] = None
    source_file: Optional[str] = None
    is_active: bool = True


class ImportResultOut(BaseModel):
    inserted: int
    updated: int
    skipped: int
    total: int


def _apply_in(data: ColorSwatchRecipeIn) -> dict[str, Any]:
    return {
        "factory_key": normalize_factory_key(data.factory_key),
        "customer_id": data.customer_id,
        "buyer_code": data.buyer_code.strip().upper(),
        "brand_id": data.brand_id,
        "color_code": (data.color_code or "").strip(),
        "color_name": (data.color_name or "").strip(),
        "emboss": (data.emboss or "").strip(),
        "color_standard": (data.color_standard or "").strip() or None,
        "backing": (data.backing or "").strip() or None,
        "material_name": (data.material_name or "").strip(),
        "legacy_urut": (data.legacy_urut or "").strip() or None,
        "entered_at": data.entered_at,
        "source_file": data.source_file,
        "is_active": data.is_active,
    }


@router.get("/masters/color-swatch-recipes/page", response_model=ColorSwatchRecipePageOut)
def list_color_swatch_page(
    factory_key: Optional[str] = Query(None),
    buyer_code: Optional[str] = Query(None),
    material_name: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search code/name/emboss/factory/material"),
    active_only: bool = Query(True),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> ColorSwatchRecipePageOut:
    stmt = select(ColorSwatchRecipe)
    count_stmt = select(func.count(ColorSwatchRecipe.id))
    if active_only:
        stmt = stmt.where(ColorSwatchRecipe.is_active.is_(True))
        count_stmt = count_stmt.where(ColorSwatchRecipe.is_active.is_(True))
    if factory_key and factory_key.strip():
        fk = f"%{factory_key.strip().upper()}%"
        stmt = stmt.where(ColorSwatchRecipe.factory_key.ilike(fk))
        count_stmt = count_stmt.where(ColorSwatchRecipe.factory_key.ilike(fk))
    if buyer_code and buyer_code.strip():
        b = buyer_code.strip().upper()
        stmt = stmt.where(ColorSwatchRecipe.buyer_code == b)
        count_stmt = count_stmt.where(ColorSwatchRecipe.buyer_code == b)
    if material_name and material_name.strip():
        like = f"%{material_name.strip()}%"
        stmt = stmt.where(ColorSwatchRecipe.material_name.ilike(like))
        count_stmt = count_stmt.where(ColorSwatchRecipe.material_name.ilike(like))
    if q and q.strip():
        like = f"%{q.strip()}%"
        where = or_(
            ColorSwatchRecipe.color_name.ilike(like),
            ColorSwatchRecipe.color_code.ilike(like),
            ColorSwatchRecipe.emboss.ilike(like),
            ColorSwatchRecipe.factory_key.ilike(like),
            ColorSwatchRecipe.material_name.ilike(like),
            ColorSwatchRecipe.color_standard.ilike(like),
        )
        stmt = stmt.where(where)
        count_stmt = count_stmt.where(where)
    total = int(db.scalar(count_stmt) or 0)
    items = list(
        db.scalars(
            stmt.order_by(
                ColorSwatchRecipe.factory_key.asc(),
                ColorSwatchRecipe.buyer_code.asc(),
                ColorSwatchRecipe.color_name.asc(),
            )
            .limit(limit)
            .offset(offset)
        ).all()
    )
    return ColorSwatchRecipePageOut(items=items, total=total, limit=limit, offset=offset)


@router.get("/masters/color-swatch-recipes/lookup", response_model=list[ColorSwatchRecipeOut])
def lookup_color_swatch(
    buyer_code: str = Query(..., min_length=1),
    factory_key: Optional[str] = Query(None, description="Kode/nama pabrik (KODE SYSTEM atau factory_key swatch)"),
    customer_id: Optional[int] = Query(None, description="Customer PO untuk map kode pabrik ke factory_key swatch"),
    material_name: Optional[str] = Query(None),
    include_all_materials: bool = Query(
        False, description="Abaikan filter material (tampilkan semua resep pabrik+buyer)"
    ),
    q: Optional[str] = Query(None),
    limit: int = Query(40, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[ColorSwatchRecipe]:
    buyer = buyer_code.strip().upper()
    if not (factory_key or "").strip() and not customer_id:
        raise HTTPException(
            status_code=400,
            detail="factory_key atau customer_id wajib untuk lookup swatch",
        )
    factory_keys = resolve_swatch_factory_keys(
        db, factory_hint=factory_key, customer_id=customer_id
    )
    if not factory_keys:
        return []
    stmt = select(ColorSwatchRecipe).where(
        ColorSwatchRecipe.is_active.is_(True),
        ColorSwatchRecipe.buyer_code == buyer,
        ColorSwatchRecipe.factory_key.in_(factory_keys),
    )
    if material_name and material_name.strip() and not include_all_materials:
        like = f"%{material_name.strip()}%"
        stmt = stmt.where(ColorSwatchRecipe.material_name.ilike(like))
    if q and q.strip():
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                ColorSwatchRecipe.color_name.ilike(like),
                ColorSwatchRecipe.color_code.ilike(like),
            )
        )
    rows = db.scalars(
        stmt.order_by(ColorSwatchRecipe.color_name.asc()).limit(limit)
    ).all()
    return list(rows)


@router.get("/masters/color-swatch-recipes/factory-keys", response_model=list[str])
def list_factory_keys(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[str]:
    rows = db.scalars(
        select(ColorSwatchRecipe.factory_key)
        .where(ColorSwatchRecipe.is_active.is_(True))
        .distinct()
        .order_by(ColorSwatchRecipe.factory_key.asc())
    ).all()
    return [str(r) for r in rows if r]


@router.get("/masters/color-swatch-recipes/{recipe_id}", response_model=ColorSwatchRecipeOut)
def get_color_swatch(
    recipe_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> ColorSwatchRecipe:
    row = db.get(ColorSwatchRecipe, recipe_id)
    if not row or not row.is_active:
        raise HTTPException(status_code=404, detail="Resep color swatch tidak ditemukan")
    return row


@router.get("/masters/color-swatch-recipes/{recipe_id}/po-fill")
def get_color_swatch_po_fill(
    recipe_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict[str, Any]:
    row = db.get(ColorSwatchRecipe, recipe_id)
    if not row or not row.is_active:
        raise HTTPException(status_code=404, detail="Resep color swatch tidak ditemukan")
    return recipe_to_po_fill(row)


@router.post("/masters/color-swatch-recipes", response_model=ColorSwatchRecipeOut)
def create_color_swatch(
    body: ColorSwatchRecipeIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> ColorSwatchRecipe:
    data = _apply_in(body)
    row = ColorSwatchRecipe(**data)
    db.add(row)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Kombinasi resep sudah ada") from exc
    db.refresh(row)
    return row


@router.put("/masters/color-swatch-recipes/{recipe_id}", response_model=ColorSwatchRecipeOut)
def update_color_swatch(
    recipe_id: int,
    body: ColorSwatchRecipeIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> ColorSwatchRecipe:
    row = db.get(ColorSwatchRecipe, recipe_id)
    if not row:
        raise HTTPException(status_code=404, detail="Resep color swatch tidak ditemukan")
    for k, v in _apply_in(body).items():
        setattr(row, k, v)
    row.updated_at = datetime.utcnow()
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Kombinasi resep bentrok dengan baris lain") from exc
    db.refresh(row)
    return row


@router.delete("/masters/color-swatch-recipes/{recipe_id}")
def delete_color_swatch(
    recipe_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(ColorSwatchRecipe, recipe_id)
    if not row:
        raise HTTPException(status_code=404, detail="Resep color swatch tidak ditemukan")
    row.is_active = False
    row.updated_at = datetime.utcnow()
    db.commit()
    return {"status": "deactivated"}


@router.post("/masters/color-swatch-recipes/import-csv", response_model=ImportResultOut)
async def import_color_swatch_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> ImportResultOut:
    raw = await file.read()
    source = file.filename or "upload.csv"
    recipes = iter_csv_recipes(io.BytesIO(raw), source)
    if not recipes:
        raise HTTPException(status_code=400, detail="Tidak ada baris valid dalam file CSV")
    stats = import_recipes(db, recipes)
    return ImportResultOut(**stats)


@router.post("/masters/color-swatch-recipes/import-bundled", response_model=ImportResultOut)
def import_color_swatch_bundled(
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> ImportResultOut:
    """Import dari dokumentasi/DATA COLOR SWATCH.csv di repo (dev/seed)."""
    path = Path(__file__).resolve().parents[2] / "dokumentasi" / "DATA COLOR SWATCH.csv"
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"File tidak ditemukan: {path}")
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    recipes = iter_csv_recipes(io.StringIO(text), str(path.name))
    if not recipes:
        raise HTTPException(status_code=400, detail="Tidak ada baris valid")
    stats = import_recipes(db, recipes)
    return ImportResultOut(**stats)
