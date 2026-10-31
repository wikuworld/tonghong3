"""Master color swatch recipes — CRUD, import CSV, export/import Excel, lookup PO."""

from __future__ import annotations

import io
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.timeutil import app_now
from app.models import ColorSwatchRecipe, CsiColorMaster, Customer, MasterItem
from app.routers.auth import get_current_user, require_roles
from app.services.color_swatch import (
    _VALID_BUYERS,
    UnknownBuyerRejectError,
    filter_swatch_recipes_by_dimensions,
    import_recipes,
    iter_csv_recipes,
    iter_upload_recipes,
    normalize_factory_key,
    recipe_to_po_fill,
    suggest_next_color_standard,
)
from app.services.color_swatch_excel import (
    export_color_swatches_template_xlsx,
    export_color_swatches_xlsx,
    import_color_swatches_xlsx,
)
from app.services.master_item_dimensions import distinct_material_names
from app.services.swatch_factory_map import resolve_swatch_customer_id

router = APIRouter(tags=["color-swatch"])


class ColorSwatchRecipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    factory_key: str
    customer_id: Optional[int] = None
    customer_code: Optional[str] = None
    buyer_code: str
    brand_id: Optional[int] = None
    color_code: str
    color_name: str
    csi_color_master_id: Optional[int] = None
    csi_buyer_code: Optional[str] = None
    csi_color_name: Optional[str] = None
    emboss: str
    color_standard: Optional[str] = None
    backing: Optional[str] = None
    material_name: str
    legacy_urut: Optional[str] = None
    entered_at: Optional[date] = None
    source_file: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


_SORTABLE_COLUMNS = {
    "created_at": ColorSwatchRecipe.created_at,
    "updated_at": ColorSwatchRecipe.updated_at,
    "entered_at": ColorSwatchRecipe.entered_at,
    "factory_key": ColorSwatchRecipe.factory_key,
    "buyer_code": ColorSwatchRecipe.buyer_code,
    "color_code": ColorSwatchRecipe.color_code,
    "color_name": ColorSwatchRecipe.color_name,
    "material_name": ColorSwatchRecipe.material_name,
}


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
    csi_color_master_id: Optional[int] = None
    color_code: str = Field(default="", max_length=64)
    color_name: str = Field(default="", max_length=255)
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
    deactivated: int = 0
    total: int
    warnings: list[str] = Field(default_factory=list)


class SwatchCsiBackfillOut(BaseModel):
    linked: int
    orphan_remaining: int


class ColorSwatchCustomerOptionOut(BaseModel):
    id: int
    code: Optional[str] = None
    name: Optional[str] = None


class ColorSwatchFormOptionsOut(BaseModel):
    customers: list[ColorSwatchCustomerOptionOut] = Field(default_factory=list)
    factory_keys: list[str] = Field(default_factory=list)
    factory_keys_by_customer: dict[int, list[str]] = Field(default_factory=dict)
    buyer_codes: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    colors_by_material: dict[str, list[str]] = Field(default_factory=dict)
    embosses_by_material: dict[str, list[str]] = Field(default_factory=dict)
    backings: list[str] = Field(default_factory=list)
    csi_by_buyer: dict[str, list[dict[str, Any]]] = Field(default_factory=dict)


def _recipe_to_out(db: Session, recipe: ColorSwatchRecipe) -> ColorSwatchRecipeOut:
    out = ColorSwatchRecipeOut.model_validate(recipe)
    if recipe.customer_id:
        cust = db.get(Customer, recipe.customer_id)
        out.customer_code = cust.code if cust else None
    if recipe.csi_color_master_id:
        csi = db.get(CsiColorMaster, recipe.csi_color_master_id)
        if csi:
            out.csi_buyer_code = csi.buyer_code
            out.csi_color_name = csi.color_name
    return out


def _apply_in(data: ColorSwatchRecipeIn, db: Session | None = None) -> dict[str, Any]:
    color_standard = (data.color_standard or "").strip() or None
    customer_id = data.customer_id
    factory_key = normalize_factory_key(data.factory_key)
    buyer_code = data.buyer_code.strip().upper()
    if customer_id is None and db is not None:
        customer_id = resolve_swatch_customer_id(
            db, factory_key, color_standard=color_standard
        )
    if db is not None and buyer_code:
        from app.services.buyer_registry import ensure_buyer_code

        ensure_buyer_code(db, buyer_code)
    color_code = (data.color_code or "").strip()
    color_name = (data.color_name or "").strip()
    csi_id = data.csi_color_master_id
    if db is not None:
        from app.services.csi_color import apply_csi_to_swatch_fields

        csi_id, color_code, color_name = apply_csi_to_swatch_fields(
            db,
            csi_id=csi_id,
            buyer_code=buyer_code,
            color_code=color_code,
            color_name=color_name,
        )
    if not color_standard and db is not None:
        cust_code = None
        if customer_id:
            cust = db.get(Customer, customer_id)
            cust_code = (cust.code if cust else None) or None
        color_standard = suggest_next_color_standard(
            db,
            customer_code=cust_code,
            factory_key=factory_key,
            on_date=data.entered_at,
        )
    return {
        "factory_key": factory_key,
        "customer_id": customer_id,
        "buyer_code": buyer_code,
        "brand_id": data.brand_id,
        "csi_color_master_id": csi_id,
        "color_code": color_code,
        "color_name": color_name,
        "emboss": (data.emboss or "").strip(),
        "color_standard": color_standard,
        "backing": (data.backing or "").strip() or None,
        "material_name": (data.material_name or "").strip(),
        "legacy_urut": (data.legacy_urut or "").strip() or None,
        "entered_at": data.entered_at,
        "source_file": data.source_file,
        "is_active": data.is_active,
    }


@router.get("/masters/color-swatch-recipes/form-options", response_model=ColorSwatchFormOptionsOut)
def color_swatch_form_options(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> ColorSwatchFormOptionsOut:
    """Opsi dropdown form tambah/edit — dari master customer, items, & swatch existing."""
    customers = list(
        db.scalars(
            select(Customer)
            .where(Customer.is_active.is_(True))
            .order_by(Customer.code.asc())
        ).all()
    )
    recipes = list(
        db.scalars(select(ColorSwatchRecipe).where(ColorSwatchRecipe.is_active.is_(True))).all()
    )
    master_rows = list(db.scalars(select(MasterItem).order_by(MasterItem.item_code)).all())

    from app.services.buyer_registry import list_active_buyer_codes

    factory_keys = sorted({r.factory_key for r in recipes if r.factory_key})
    factory_by_customer: dict[int, list[str]] = {}
    buyer_codes: set[str] = set(list_active_buyer_codes(db)) | set(_VALID_BUYERS)
    materials: set[str] = set(distinct_material_names(master_rows))
    colors_by_material: dict[str, set[str]] = {}
    embosses_by_material: dict[str, set[str]] = {}
    backings: set[str] = set()

    for row in master_rows:
        mat = (row.material_name or "").strip()
        if mat:
            materials.add(mat)
        if mat and row.color:
            colors_by_material.setdefault(mat, set()).add(str(row.color).strip())
        if mat and row.emboss:
            embosses_by_material.setdefault(mat, set()).add(str(row.emboss).strip())

    for recipe in recipes:
        if recipe.buyer_code:
            buyer_codes.add(recipe.buyer_code.strip().upper())
        mat = (recipe.material_name or "").strip()
        if mat:
            materials.add(mat)
        if mat and recipe.color_name:
            colors_by_material.setdefault(mat, set()).add(recipe.color_name.strip())
        if mat and recipe.emboss:
            embosses_by_material.setdefault(mat, set()).add(recipe.emboss.strip())
        if recipe.backing:
            backings.add(recipe.backing.strip())
        if recipe.customer_id and recipe.factory_key:
            factory_by_customer.setdefault(int(recipe.customer_id), set()).add(recipe.factory_key)

    csi_rows = list(
        db.scalars(
            select(CsiColorMaster)
            .where(CsiColorMaster.is_active.is_(True))
            .order_by(CsiColorMaster.buyer_code.asc(), CsiColorMaster.color_code.asc())
        ).all()
    )
    csi_by_buyer: dict[str, list[dict[str, Any]]] = {}
    for csi in csi_rows:
        csi_by_buyer.setdefault(csi.buyer_code, []).append(
            {
                "id": int(csi.id),
                "color_code": csi.color_code,
                "color_name": csi.color_name,
                "label": f"{csi.color_code} — {csi.color_name}",
            }
        )

    return ColorSwatchFormOptionsOut(
        customers=[
            ColorSwatchCustomerOptionOut(id=c.id, code=c.code, name=c.name) for c in customers
        ],
        factory_keys=factory_keys,
        factory_keys_by_customer={
            cid: sorted(keys) for cid, keys in sorted(factory_by_customer.items())
        },
        buyer_codes=sorted(buyer_codes),
        materials=sorted(materials),
        colors_by_material={k: sorted(v) for k, v in sorted(colors_by_material.items())},
        embosses_by_material={k: sorted(v) for k, v in sorted(embosses_by_material.items())},
        backings=sorted(backings),
        csi_by_buyer=csi_by_buyer,
    )


class ColorSwatchSuggestStandardOut(BaseModel):
    color_standard: Optional[str] = None


@router.get(
    "/masters/color-swatch-recipes/suggest-color-standard",
    response_model=ColorSwatchSuggestStandardOut,
)
def suggest_color_swatch_standard(
    customer_id: Optional[int] = Query(None),
    factory_key: Optional[str] = Query(None),
    on_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> ColorSwatchSuggestStandardOut:
    """Pratinjau autofill Color standard untuk form tambah resep."""
    cust_code = None
    if customer_id:
        cust = db.get(Customer, customer_id)
        cust_code = (cust.code if cust else None) or None
    suggested = suggest_next_color_standard(
        db,
        customer_code=cust_code,
        factory_key=normalize_factory_key(factory_key) if factory_key else None,
        on_date=on_date,
    )
    return ColorSwatchSuggestStandardOut(color_standard=suggested)


@router.get("/masters/color-swatch-recipes/page", response_model=ColorSwatchRecipePageOut)
def list_color_swatch_page(
    factory_key: Optional[str] = Query(None),
    buyer_code: Optional[str] = Query(None),
    material_name: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Search code/name/emboss/factory/material"),
    active_only: bool = Query(True),
    sort_by: Optional[str] = Query(
        None,
        description="Kolom sort: created_at, updated_at, entered_at, factory_key, buyer_code, color_code, color_name, material_name",
    ),
    sort_dir: str = Query("asc", description="asc atau desc"),
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

    sort_key = (sort_by or "").strip().lower()
    col = _SORTABLE_COLUMNS.get(sort_key)
    if col is not None:
        descending = sort_dir.strip().lower() == "desc"
        primary = col.desc() if descending else col.asc()
        order_clauses = (primary, ColorSwatchRecipe.id.asc())
    else:
        order_clauses = (
            ColorSwatchRecipe.factory_key.asc(),
            ColorSwatchRecipe.buyer_code.asc(),
            ColorSwatchRecipe.color_name.asc(),
        )

    items = list(
        db.scalars(stmt.order_by(*order_clauses).limit(limit).offset(offset)).all()
    )
    return ColorSwatchRecipePageOut(
        items=[_recipe_to_out(db, row) for row in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/masters/color-swatch-recipes/lookup", response_model=list[ColorSwatchRecipeOut])
def lookup_color_swatch(
    buyer_code: str = Query(..., min_length=1),
    factory_key: Optional[str] = Query(
        None,
        description="Deprecated untuk filter: diabaikan. Lookup SO global per buyer (semua factory_key).",
    ),
    customer_id: Optional[int] = Query(
        None,
        description="Deprecated untuk filter: diabaikan. Lookup SO global per buyer (semua factory_key).",
    ),
    material_name: Optional[str] = Query(None),
    color_name: Optional[str] = Query(None, description="Filter warna (toleran suffix kode, mis. WOLF GREY (01V))"),
    emboss: Optional[str] = Query(None, description="Filter emboss (toleran suffix deskripsi, mis. AR-167 (DEEP MATTE))"),
    include_all_materials: bool = Query(
        False, description="Abaikan filter material (tampilkan semua resep buyer)"
    ),
    q: Optional[str] = Query(None),
    limit: int = Query(40, ge=1, le=100),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> list[ColorSwatchRecipe]:
    """Lookup resep aktif per buyer — tanpa filter pabrik/customer (SO boleh tarik seluruh swatch)."""
    # factory_key / customer_id tetap diterima agar FE lama tidak 422; sengaja tidak memfilter.
    _ = factory_key, customer_id
    buyer = buyer_code.strip().upper()
    stmt = select(ColorSwatchRecipe).where(
        ColorSwatchRecipe.is_active.is_(True),
        ColorSwatchRecipe.buyer_code == buyer,
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
    fetch_limit = min(limit * 5, 200) if (color_name or emboss) else limit
    rows = list(
        db.scalars(stmt.order_by(ColorSwatchRecipe.color_name.asc()).limit(fetch_limit)).all()
    )
    if color_name or emboss or material_name:
        rows = filter_swatch_recipes_by_dimensions(
            rows,
            material_name=material_name,
            color_name=color_name,
            emboss=emboss,
            db=db,
        )
    return rows[:limit]


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


@router.post("/masters/color-swatch-recipes/backfill-csi", response_model=SwatchCsiBackfillOut)
def backfill_swatch_csi(
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> SwatchCsiBackfillOut:
    from app.services.color_links import backfill_swatch_csi_exact

    stats = backfill_swatch_csi_exact(db)
    db.commit()
    return SwatchCsiBackfillOut(**stats)


@router.get("/masters/color-swatch-recipes/export")
def export_color_swatches(
    template: bool = Query(False, description="Jika true, unduh template kosong (header saja)"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    if template:
        excel_content = export_color_swatches_template_xlsx()
        filename = "color_swatch_template.xlsx"
    else:
        excel_content = export_color_swatches_xlsx(db)
        filename = "color_swatch.xlsx"
    return StreamingResponse(
        io.BytesIO(excel_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/masters/color-swatch-recipes/import")
async def import_color_swatches(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File Excel kosong")
    try:
        result = import_color_swatches_xlsx(db, content)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return result.to_dict()


@router.get("/masters/color-swatch-recipes/{recipe_id}", response_model=ColorSwatchRecipeOut)
def get_color_swatch(
    recipe_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> ColorSwatchRecipeOut:
    row = db.get(ColorSwatchRecipe, recipe_id)
    if not row or not row.is_active:
        raise HTTPException(status_code=404, detail="Resep color swatch tidak ditemukan")
    return _recipe_to_out(db, row)


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
) -> ColorSwatchRecipeOut:
    data = _apply_in(body, db)
    if not data["color_name"]:
        raise HTTPException(status_code=400, detail="Nama warna wajib (pilih CSI atau isi manual)")
    row = ColorSwatchRecipe(**data)
    db.add(row)
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Kombinasi resep sudah ada") from exc
    db.refresh(row)
    return _recipe_to_out(db, row)


@router.put("/masters/color-swatch-recipes/{recipe_id}", response_model=ColorSwatchRecipeOut)
def update_color_swatch(
    recipe_id: int,
    body: ColorSwatchRecipeIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> ColorSwatchRecipeOut:
    row = db.get(ColorSwatchRecipe, recipe_id)
    if not row:
        raise HTTPException(status_code=404, detail="Resep color swatch tidak ditemukan")
    data = _apply_in(body, db)
    if not data["color_name"]:
        raise HTTPException(status_code=400, detail="Nama warna wajib (pilih CSI atau isi manual)")
    for k, v in data.items():
        setattr(row, k, v)
    row.updated_at = app_now()
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="Kombinasi resep bentrok dengan baris lain") from exc
    db.refresh(row)
    return _recipe_to_out(db, row)


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
    row.updated_at = app_now()
    db.commit()
    return {"status": "deactivated"}


@router.post("/masters/color-swatch-recipes/import-csv", response_model=ImportResultOut)
async def import_color_swatch_csv(
    file: UploadFile = File(...),
    replace_inactive: bool = Query(
        True,
        description="Nonaktifkan resep aktif yang tidak ada di file (default: seluruh master)",
    ),
    replace_inactive_scope: str = Query(
        "global",
        description="global = seluruh tabel; pair = hanya factory+buyer yang tersentuh file",
    ),
    reject_unknown_buyer: bool = Query(
        False,
        description="Tolak import (400) jika ada buyer_code di luar registry",
    ),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> ImportResultOut:
    raw = await file.read()
    source = file.filename or "upload.csv"
    recipes = iter_upload_recipes(raw, source)
    if not recipes:
        raise HTTPException(status_code=400, detail="Tidak ada baris valid dalam file CSV")
    try:
        stats = import_recipes(
            db,
            recipes,
            replace_inactive=replace_inactive,
            replace_inactive_scope=replace_inactive_scope,
            reject_unknown_buyer=reject_unknown_buyer,
        )
    except UnknownBuyerRejectError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ImportResultOut(**stats)


@router.post("/masters/color-swatch-recipes/import-bundled", response_model=ImportResultOut)
def import_color_swatch_bundled(
    replace_inactive: bool = Query(
        True, description="Nonaktifkan resep aktif yang tidak ada di file bundled"
    ),
    replace_inactive_scope: str = Query(
        "global",
        description="global = seluruh tabel; pair = hanya factory+buyer yang tersentuh file",
    ),
    reject_unknown_buyer: bool = Query(
        False,
        description="Tolak import (400) jika ada buyer_code di luar registry",
    ),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> ImportResultOut:
    """Import Color Swatch dari folder dokumentasi (dev/seed).

    Prefer DATA_CS_2026-07-28.csv; fallback ke DATA COLOR SWATCH.csv.
    """
    dok = Path(__file__).resolve().parents[2] / "dokumentasi"
    candidates = [
        dok / "master-color-standart" / "DATA_CS_2026-07-28.csv",
        dok / "DATA COLOR SWATCH.csv",
    ]
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        raise HTTPException(
            status_code=404,
            detail="File tidak ditemukan: "
            + " atau ".join(str(p) for p in candidates),
        )
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    recipes = iter_csv_recipes(io.StringIO(text), str(path.name))
    if not recipes:
        raise HTTPException(status_code=400, detail="Tidak ada baris valid")
    try:
        stats = import_recipes(
            db,
            recipes,
            replace_inactive=replace_inactive,
            replace_inactive_scope=replace_inactive_scope,
            reject_unknown_buyer=reject_unknown_buyer,
        )
    except UnknownBuyerRejectError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ImportResultOut(**stats)
