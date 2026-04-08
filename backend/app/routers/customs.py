"""Dokumen pabean (AJU) — master data + impor CSV (opsional)."""

from __future__ import annotations

import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import CustomsAjuSheetRow, CustomsDeclaration
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


@router.get("/customs/declarations", response_model=list[CustomsSummaryOut])
def list_declarations(
    db: Session = Depends(get_db),
    limit: int = 200,
) -> list[CustomsDeclaration]:
    return list(
        db.scalars(select(CustomsDeclaration).order_by(CustomsDeclaration.id.desc()).limit(limit)).all()
    )


@router.post("/customs/declarations", response_model=CustomsSummaryOut)
def create_declaration(body: CustomsDeclarationCreate, db: Session = Depends(get_db)) -> CustomsSummaryOut:
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
    declaration_id: int, body: CustomsDeclarationUpdate, db: Session = Depends(get_db)
) -> CustomsSummaryOut:
    dec = db.get(CustomsDeclaration, declaration_id)
    if not dec:
        raise HTTPException(status_code=404, detail="Deklarasi tidak ditemukan")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(dec, key, val)
    dec.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(dec)
    return dec  # type: ignore[return-value]


@router.put("/customs/declarations/{declaration_id}/sheets-data")
def save_sheets_data(
    declaration_id: int, body: CustomsSheetsSave, db: Session = Depends(get_db)
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
    dec.updated_at = datetime.utcnow()
    db.commit()
    out = declaration_to_api_dict(db, declaration_id)
    if not out:
        raise HTTPException(status_code=404, detail="Deklarasi tidak ditemukan")
    return out


@router.get("/customs/declarations/{declaration_id}")
def get_declaration(declaration_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    out = declaration_to_api_dict(db, declaration_id)
    if not out:
        raise HTTPException(status_code=404, detail="Deklarasi tidak ditemukan")
    return out


@router.get("/customs/declarations/by-nomor/{nomor_aju}")
def get_declaration_by_nomor(nomor_aju: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    dec = db.scalars(
        select(CustomsDeclaration).where(CustomsDeclaration.nomor_aju == nomor_aju)
    ).first()
    if not dec:
        raise HTTPException(status_code=404, detail="Deklarasi tidak ditemukan")
    return declaration_to_api_dict(db, dec.id)


@router.delete("/customs/declarations/{declaration_id}")
def delete_declaration(declaration_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
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
