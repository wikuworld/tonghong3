"""Master CSI color catalog — page, CRUD, import bundled."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import CsiColorMaster
from app.routers.auth import get_current_user, require_roles
from app.services.buyer_registry import ensure_buyer_code, list_active_buyer_codes
from app.services.color_links import list_color_link_options, lookup_color_links
from app.services.csi_color import (
    apply_csi_fields,
    parse_csi_workbook,
    upsert_csi_rows,
)

router = APIRouter(tags=["csi-colors"])


class CsiColorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    buyer_code: str
    color_code: str
    color_name: str
    source_file: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CsiColorPageOut(BaseModel):
    items: list[CsiColorOut]
    total: int
    limit: int
    offset: int


class CsiColorIn(BaseModel):
    buyer_code: str = Field(..., min_length=1, max_length=32)
    color_code: str = Field(..., min_length=1, max_length=64)
    color_name: str = Field(..., min_length=1, max_length=255)
    source_file: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = True


class CsiImportResultOut(BaseModel):
    inserted: int
    updated: int
    total: int
    warnings: list[str] = Field(default_factory=list)


class CsiFormOptionsOut(BaseModel):
    buyer_codes: list[str] = Field(default_factory=list)
    colors_by_buyer: dict[str, list[CsiColorOut]] = Field(default_factory=dict)


class ColorLinkCsiOut(BaseModel):
    id: int
    buyer_code: str
    color_code: str
    color_name: str
    label: str


class ColorLinkFluorescentOut(BaseModel):
    id: int
    buyer_code: str
    color_code: Optional[str] = None
    color_name: str
    season_label: Optional[str] = None
    color_class: Optional[str] = None


class ColorLinksOut(BaseModel):
    color_code: str = ""
    color_qualifier: Optional[str] = None
    item_label: str = ""
    in_csi: bool = False
    in_swatch: bool = False
    csi: list[ColorLinkCsiOut] = Field(default_factory=list)
    swatch_count: int = 0
    swatch_factories: list[str] = Field(default_factory=list)
    fluorescent: list[ColorLinkFluorescentOut] = Field(default_factory=list)


class ColorLinkOptionOut(BaseModel):
    label: str
    value: str
    color_code: str
    color_name: str


class ColorLinkOptionsOut(BaseModel):
    options: list[ColorLinkOptionOut] = Field(default_factory=list)


_SORTABLE = {
    "created_at": CsiColorMaster.created_at,
    "updated_at": CsiColorMaster.updated_at,
    "buyer_code": CsiColorMaster.buyer_code,
    "color_code": CsiColorMaster.color_code,
    "color_name": CsiColorMaster.color_name,
}


@router.get("/masters/color-links", response_model=ColorLinksOut)
def get_color_links(
    color: Optional[str] = Query(None, description="Teks item, mis. BLACK (00A)"),
    color_code: Optional[str] = Query(None, description="Kode langsung, mis. 00A"),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> ColorLinksOut:
    return ColorLinksOut.model_validate(lookup_color_links(db, color=color, color_code=color_code))


@router.get("/masters/color-links/options", response_model=ColorLinkOptionsOut)
def get_color_link_options(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> ColorLinkOptionsOut:
    return ColorLinkOptionsOut(options=list_color_link_options(db))


@router.get("/masters/csi-colors/page", response_model=CsiColorPageOut)
def list_csi_colors_page(
    buyer_code: Optional[str] = None,
    q: Optional[str] = Query(None),
    sort_by: Optional[str] = None,
    sort_dir: str = Query("asc"),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> CsiColorPageOut:
    stmt = select(CsiColorMaster).where(CsiColorMaster.is_active.is_(True))
    count_stmt = select(func.count(CsiColorMaster.id)).where(CsiColorMaster.is_active.is_(True))
    if buyer_code:
        b = buyer_code.strip().upper()
        stmt = stmt.where(CsiColorMaster.buyer_code == b)
        count_stmt = count_stmt.where(CsiColorMaster.buyer_code == b)
    if q:
        like = f"%{q.strip()}%"
        where_clause = or_(
            CsiColorMaster.color_name.ilike(like),
            CsiColorMaster.color_code.ilike(like),
            CsiColorMaster.buyer_code.ilike(like),
        )
        stmt = stmt.where(where_clause)
        count_stmt = count_stmt.where(where_clause)
    total = int(db.scalar(count_stmt) or 0)
    col = _SORTABLE.get((sort_by or "").strip().lower())
    if col is not None:
        primary = col.desc() if sort_dir.strip().lower() == "desc" else col.asc()
        order = (primary, CsiColorMaster.id.asc())
    else:
        order = (CsiColorMaster.buyer_code.asc(), CsiColorMaster.color_code.asc())
    items = list(db.scalars(stmt.order_by(*order).limit(limit).offset(offset)).all())
    return CsiColorPageOut(items=items, total=total, limit=limit, offset=offset)


@router.get("/masters/csi-colors/form-options", response_model=CsiFormOptionsOut)
def csi_form_options(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> CsiFormOptionsOut:
    rows = list(
        db.scalars(
            select(CsiColorMaster)
            .where(CsiColorMaster.is_active.is_(True))
            .order_by(CsiColorMaster.buyer_code.asc(), CsiColorMaster.color_code.asc())
        ).all()
    )
    by_buyer: dict[str, list[CsiColorOut]] = {}
    for row in rows:
        by_buyer.setdefault(row.buyer_code, []).append(CsiColorOut.model_validate(row))
    buyers = sorted(set(list_active_buyer_codes(db)) | set(by_buyer))
    return CsiFormOptionsOut(buyer_codes=buyers, colors_by_buyer=by_buyer)


@router.post("/masters/csi-colors", response_model=CsiColorOut)
def create_csi_color(
    body: CsiColorIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> CsiColorOut:
    data = apply_csi_fields(body.model_dump())
    ensure_buyer_code(db, data["buyer_code"])
    existing = db.scalars(
        select(CsiColorMaster).where(
            CsiColorMaster.buyer_code == data["buyer_code"],
            CsiColorMaster.color_code == data["color_code"],
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Kode CSI sudah ada untuk buyer ini")
    row = CsiColorMaster(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return CsiColorOut.model_validate(row)


@router.put("/masters/csi-colors/{row_id}", response_model=CsiColorOut)
def update_csi_color(
    row_id: int,
    body: CsiColorIn,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "marketing")),
) -> CsiColorOut:
    row = db.get(CsiColorMaster, row_id)
    if not row:
        raise HTTPException(status_code=404, detail="CSI tidak ditemukan")
    data = apply_csi_fields(body.model_dump())
    ensure_buyer_code(db, data["buyer_code"])
    clash = db.scalars(
        select(CsiColorMaster).where(
            CsiColorMaster.buyer_code == data["buyer_code"],
            CsiColorMaster.color_code == data["color_code"],
            CsiColorMaster.id != row_id,
        )
    ).first()
    if clash:
        raise HTTPException(status_code=400, detail="Kode CSI sudah ada untuk buyer ini")
    for k, v in data.items():
        setattr(row, k, v)
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return CsiColorOut.model_validate(row)


@router.delete("/masters/csi-colors/{row_id}")
def delete_csi_color(
    row_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> dict[str, str]:
    row = db.get(CsiColorMaster, row_id)
    if not row:
        raise HTTPException(status_code=404, detail="CSI tidak ditemukan")
    row.is_active = False
    row.updated_at = datetime.utcnow()
    db.commit()
    return {"status": "ok"}


@router.post("/masters/csi-colors/import-bundled", response_model=CsiImportResultOut)
def import_csi_bundled(
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
) -> CsiImportResultOut:
    candidates = [
        Path("/app/dokumentasi") / "CSI ALL BUYER.xlsx",
        Path(__file__).resolve().parents[2] / "dokumentasi" / "CSI ALL BUYER.xlsx",
        Path(__file__).resolve().parents[3] / "dokumentasi" / "CSI ALL BUYER.xlsx",
    ]
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        raise HTTPException(status_code=404, detail="CSI ALL BUYER.xlsx tidak ditemukan")
    rows = parse_csi_workbook(path)
    if not rows:
        raise HTTPException(status_code=400, detail="Tidak ada baris CSI valid")
    stats = upsert_csi_rows(db, rows)
    db.commit()
    return CsiImportResultOut(**stats)
