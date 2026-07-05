"""Impor folder CSV ekstraksi AJU (VICTORY-D / Core Customs) ke `customs_*`."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any, Optional, Tuple

# Urutan tampilan (semua sheet template, meski kosong)
SHEET_CODES_ORDER = [
    "HEADER",
    "ENTITAS",
    "DOKUMEN",
    "PENGANGKUT",
    "KEMASAN",
    "KONTAINER",
    "BARANG",
    "BARANGTARIF",
    "BARANGDOKUMEN",
    "BARANGENTITAS",
    "BARANGSPEKKHUSUS",
    "BARANGVD",
    "BAHANBAKU",
    "BAHANBAKUTARIF",
    "BAHANBAKUDOKUMEN",
    "PUNGUTAN",
    "JAMINAN",
    "BANKDEVISA",
    "VERSI",
]


def filename_to_sheet_code(name: str) -> Optional[str]:
    m = re.match(r"^\d+_(.+)\.csv$", name.strip(), re.I)
    if not m:
        return None
    return m.group(1).upper()


def row_is_empty(row: list[str]) -> bool:
    return not any((c or "").strip() for c in row)


def parse_csv_file(path: Path) -> tuple[list[str], list[list[str]]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return [], []
    header = [h.strip().replace("\n", " ") for h in rows[0]]
    data_rows = rows[1:]
    return header, data_rows


def rows_to_cell_dicts(header: list[str], data_rows: list[list[str]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    ncols = len(header)
    for ri, row in enumerate(data_rows):
        if row_is_empty(row):
            continue
        cells: dict[str, Any] = {}
        for j in range(ncols):
            key = header[j] if j < len(header) else f"_col_{j}"
            val = row[j] if j < len(row) else ""
            cells[key] = val.strip() if isinstance(val, str) else val
        out.append(cells)
    return out


def load_folder_csvs(folder: Path) -> dict[str, list[dict[str, Any]]]:
    """Baca semua `NN_NAMA.csv`; nilai = list baris data (sel-sel sebagai dict)."""
    sheets: dict[str, list[dict[str, Any]]] = {}
    if not folder.is_dir():
        return sheets
    for p in sorted(folder.glob("*.csv")):
        if p.name.upper() == "README.MD":
            continue
        code = filename_to_sheet_code(p.name)
        if not code:
            continue
        header, data_rows = parse_csv_file(p)
        if not header:
            sheets[code] = []
            continue
        sheets[code] = rows_to_cell_dicts(header, data_rows)
    return sheets


def extract_nomor_dan_kode(sheets: dict[str, list[dict[str, Any]]]) -> Tuple[Optional[str], Optional[str]]:
    header_rows = sheets.get("HEADER") or []
    if not header_rows:
        return None, None
    first = header_rows[0]
    nomor = first.get("NOMOR AJU") or first.get("nomor_aju")
    kode = first.get("KODE DOKUMEN") or first.get("kode_dokumen")
    if nomor:
        nomor = str(nomor).strip()
    if kode:
        kode = str(kode).strip()
    return nomor, kode


def extract_versi(sheets: dict[str, list[dict[str, Any]]]) -> Optional[str]:
    rows = sheets.get("VERSI") or []
    if not rows:
        return None
    r0 = rows[0]
    for k, v in r0.items():
        if "VERSI" in k.upper() and v:
            return str(v).strip()
    return str(list(r0.values())[0]).strip() if r0 else None


def persist_declaration(
    db: Any,
    sheets: dict[str, list[dict[str, Any]]],
    source_label: Optional[str],
) -> Any:
    """Simpan ke DB: hapus lama dengan nomor AJU sama, insert baru (caller commit)."""
    from sqlalchemy import select

    from app.models import CustomsAjuSheetRow, CustomsDeclaration

    nomor, kode = extract_nomor_dan_kode(sheets)
    if not nomor:
        raise ValueError("NOMOR AJU tidak ditemukan di sheet HEADER")

    versi = extract_versi(sheets)
    existing = db.scalars(
        select(CustomsDeclaration).where(CustomsDeclaration.nomor_aju == nomor)
    ).first()
    if existing:
        db.delete(existing)
        db.flush()

    dec = CustomsDeclaration(
        nomor_aju=nomor,
        kode_dokumen=kode,
        source_label=source_label,
        versi_template=versi,
        meta_json={
            "sheet_codes_present": sorted(sheets.keys()),
            "row_counts": {k: len(v) for k, v in sheets.items()},
        },
    )
    db.add(dec)
    db.flush()

    for sheet_code in sorted(sheets.keys()):
        for ri, cells in enumerate(sheets[sheet_code]):
            db.add(
                CustomsAjuSheetRow(
                    declaration_id=dec.id,
                    sheet_code=sheet_code,
                    row_number=ri,
                    cells=cells,
                )
            )
    db.flush()
    db.refresh(dec)
    return dec


def declaration_to_api_dict(db: Any, declaration_id: int) -> dict[str, Any]:
    """Bangun struktur API: metadata + sheets terurut."""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.models import CustomsDeclaration

    dec = db.scalars(
        select(CustomsDeclaration)
        .options(selectinload(CustomsDeclaration.sheet_rows))
        .where(CustomsDeclaration.id == declaration_id)
    ).first()
    if not dec:
        return {}
    by_sheet: dict[str, list[dict[str, Any]]] = {}
    for row in sorted(dec.sheet_rows, key=lambda r: (r.sheet_code, r.row_number)):
        by_sheet.setdefault(row.sheet_code, []).append(row.cells)
    ordered: dict[str, list[dict[str, Any]]] = {}
    for c in SHEET_CODES_ORDER:
        if c in by_sheet:
            ordered[c] = by_sheet[c]
    for k in sorted(by_sheet.keys()):
        if k not in ordered:
            ordered[k] = by_sheet[k]
    return {
        "id": dec.id,
        "nomor_aju": dec.nomor_aju,
        "kode_dokumen": dec.kode_dokumen,
        "source_label": dec.source_label,
        "versi_template": dec.versi_template,
        "meta_json": dec.meta_json,
        "created_at": dec.created_at.isoformat() if dec.created_at else None,
        "updated_at": dec.updated_at.isoformat() if dec.updated_at else None,
        "sheets": ordered,
        "sheet_row_counts": {k: len(v) for k, v in by_sheet.items()},
    }
