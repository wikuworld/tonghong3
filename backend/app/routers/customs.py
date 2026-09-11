"""Dokumen pabean (AJU) — master data + impor CSV (opsional)."""

from __future__ import annotations

import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.timeutil import app_now
from app.models import (
    CustomsAjuSheetRow,
    CustomsDeclaration,
)
from app.routers.auth import get_current_user, require_roles
from app.schemas import (
    CustomsDeclarationCreate,
    CustomsDeclarationUpdate,
    CustomsSheetsSave,
)
from app.services.customs_import import (
    declaration_to_api_dict,
    load_folder_csvs,
    persist_declaration,
)
from app.services.customs_export import export_declaration_zip
from app.services.customs_from_delivery import create_declaration_from_delivery

router = APIRouter(tags=["customs"])


def _normalize_cell_value(val: Any) -> Any:
    if val is None:
        return ""
    if isinstance(val, (str, int, float, bool)):
        return val
    return str(val)


def _dedupe_column_keys(raw: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in raw:
        k = (x or "").strip()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(k)
    return out


class CustomsSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nomor_aju: str
    kode_dokumen: Optional[str] = None
    source_label: Optional[str] = None
    versi_template: Optional[str] = None
    delivery_number: Optional[str] = None
    po_number: Optional[str] = None
    customer_name: Optional[str] = None
    sheet_count: int = 0


def _summary_from_declaration(dec: CustomsDeclaration) -> CustomsSummaryOut:
    meta = dec.meta_json or {}
    row_counts = meta.get("row_counts") or {}
    return CustomsSummaryOut(
        id=dec.id,
        nomor_aju=dec.nomor_aju,
        kode_dokumen=dec.kode_dokumen,
        source_label=dec.source_label,
        versi_template=dec.versi_template,
        delivery_number=meta.get("delivery_number"),
        po_number=meta.get("po_number"),
        customer_name=meta.get("customer_name"),
        sheet_count=len(row_counts),
    )


@router.get("/customs/declarations", response_model=list[CustomsSummaryOut])
def list_declarations(
    db: Session = Depends(get_db),
    limit: int = Query(200, ge=1, le=1000),
    _user=Depends(get_current_user),
) -> list[CustomsSummaryOut]:
    rows = list(
        db.scalars(select(CustomsDeclaration).order_by(CustomsDeclaration.id.desc()).limit(limit)).all()
    )
    return [_summary_from_declaration(d) for d in rows]


@router.post("/customs/declarations", response_model=CustomsSummaryOut)
def create_declaration(
    body: CustomsDeclarationCreate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "exim")),
) -> CustomsSummaryOut:
    nomor = body.nomor_aju.strip()
    if not nomor:
        raise HTTPException(status_code=400, detail="Nomor AJU wajib diisi")
    existing = db.scalars(select(CustomsDeclaration).where(CustomsDeclaration.nomor_aju == nomor)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Nomor AJU sudah terdaftar")
    dec = CustomsDeclaration(
        nomor_aju=nomor,
        kode_dokumen=body.kode_dokumen,
        source_label=body.source_label,
        versi_template=body.versi_template,
        meta_json={"sheet_column_keys": {}, "row_counts": {}},
    )
    db.add(dec)
    db.commit()
    db.refresh(dec)
    return dec  # type: ignore[return-value]


@router.put("/customs/declarations/{declaration_id}", response_model=CustomsSummaryOut)
def update_declaration(
    declaration_id: int,
    body: CustomsDeclarationUpdate,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "exim")),
) -> CustomsSummaryOut:
    dec = db.get(CustomsDeclaration, declaration_id)
    if not dec:
        raise HTTPException(status_code=404, detail="Deklarasi tidak ditemukan")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(dec, key, val)
    dec.updated_at = app_now()
    db.commit()
    db.refresh(dec)
    return dec  # type: ignore[return-value]


@router.put("/customs/declarations/{declaration_id}/sheets-data")
def save_sheets_data(
    declaration_id: int,
    body: CustomsSheetsSave,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "exim")),
) -> dict[str, Any]:
    dec = db.get(CustomsDeclaration, declaration_id)
    if not dec:
        raise HTTPException(status_code=404, detail="Deklarasi tidak ditemukan")

    db.execute(delete(CustomsAjuSheetRow).where(CustomsAjuSheetRow.declaration_id == declaration_id))

    sheet_column_keys: dict[str, list[str]] = {}
    row_counts: dict[str, int] = {}

    for raw_code, sheet in body.sheets.items():
        code = (raw_code or "").strip().upper()
        if not code:
            continue
        keys = _dedupe_column_keys(sheet.column_keys)
        sheet_column_keys[code] = keys
        for i, raw_cells in enumerate(sheet.rows):
            if not isinstance(raw_cells, dict):
                raw_cells = {}
            cells = {k: _normalize_cell_value(raw_cells.get(k)) for k in keys}
            db.add(
                CustomsAjuSheetRow(
                    declaration_id=declaration_id,
                    sheet_code=code,
                    row_number=i,
                    cells=cells,
                )
            )
        row_counts[code] = len(sheet.rows)

    meta = dict(dec.meta_json or {})
    meta["sheet_column_keys"] = sheet_column_keys
    meta["row_counts"] = row_counts
    dec.meta_json = meta
    dec.updated_at = app_now()
    db.commit()
    out = declaration_to_api_dict(db, declaration_id)
    if not out:
        raise HTTPException(status_code=404, detail="Deklarasi tidak ditemukan")
    return out


@router.get("/customs/declarations/{declaration_id}")
def get_declaration(
    declaration_id: int,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict[str, Any]:
    out = declaration_to_api_dict(db, declaration_id)
    if not out:
        raise HTTPException(status_code=404, detail="Deklarasi tidak ditemukan")
    return out


@router.get("/customs/declarations/by-nomor/{nomor_aju}")
def get_declaration_by_nomor(
    nomor_aju: str,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
) -> dict[str, Any]:
    dec = db.scalars(
        select(CustomsDeclaration).where(CustomsDeclaration.nomor_aju == nomor_aju)
    ).first()
    if not dec:
        raise HTTPException(status_code=404, detail="Deklarasi tidak ditemukan")
    return declaration_to_api_dict(db, dec.id)


@router.delete("/customs/declarations/{declaration_id}")
def delete_declaration(
    declaration_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "exim")),
) -> dict[str, str]:
    dec = db.get(CustomsDeclaration, declaration_id)
    if not dec:
        raise HTTPException(status_code=404, detail="Deklarasi tidak ditemukan")
    db.delete(dec)
    db.commit()
    return {"status": "deleted"}


@router.post("/customs/declarations/import-upload")
async def import_upload(
    db: Session = Depends(get_db),
    files: list[UploadFile] = File(...),
    source_label: Optional[str] = Form(None),
    _user=Depends(require_roles("admin", "exim")),
) -> dict[str, Any]:
    """Unggah banyak file `NN_SHEET.csv` (satu paket AJU)."""
    if not files:
        raise HTTPException(status_code=400, detail="Tidak ada file")
    with tempfile.TemporaryDirectory() as tmp:
        tpath = Path(tmp)
        for uf in files:
            raw = await uf.read()
            dest = tpath / (uf.filename or "unknown.csv")
            dest.write_bytes(raw)
        sheets = load_folder_csvs(tpath)
        if not sheets:
            raise HTTPException(status_code=400, detail="Tidak ada CSV valid")
        try:
            dec = persist_declaration(db, sheets, source_label)
            db.commit()
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e)) from e
    return declaration_to_api_dict(db, dec.id)


@router.post("/customs/declarations/import-zip")
async def import_zip(
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    source_label: Optional[str] = Form(None),
    _user=Depends(require_roles("admin", "exim")),
) -> dict[str, Any]:
    """ZIP berisi CSV `NN_*.csv` (struktur sama folder ekstraksi)."""
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="File kosong")
    with tempfile.TemporaryDirectory() as tmp:
        tpath = Path(tmp)
        zpath = tpath / "upload.zip"
        zpath.write_bytes(raw)
        try:
            with zipfile.ZipFile(zpath) as zf:
                zf.extractall(tpath)
        except zipfile.BadZipFile as e:
            raise HTTPException(status_code=400, detail="Bukan ZIP valid") from e
        sheets = load_folder_csvs(tpath)
        if not sheets:
            raise HTTPException(status_code=400, detail="Tidak ada CSV di ZIP")
        try:
            dec = persist_declaration(db, sheets, source_label)
            db.commit()
        except ValueError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e)) from e
    return declaration_to_api_dict(db, dec.id)


@router.post("/customs/generate-from-delivery/{delivery_id}")
def generate_aju_from_delivery(
    delivery_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "exim")),
) -> dict[str, Any]:
    """Buat draft AJU dari delivery, simpan ke DB, tautkan delivery & PO."""
    return create_declaration_from_delivery(db, delivery_id)


@router.get("/customs/declarations/{declaration_id}/export-zip")
def export_declaration_zip_file(
    declaration_id: int,
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin", "exim")),
) -> Response:
    """Unduh ZIP CSV format Core Customs (BC 3.0) untuk unggah ke CEISA."""
    dec = db.get(CustomsDeclaration, declaration_id)
    if not dec:
        raise HTTPException(status_code=404, detail="Deklarasi tidak ditemukan")
    try:
        data, filename = export_declaration_zip(db, declaration_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return Response(
        content=data,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
