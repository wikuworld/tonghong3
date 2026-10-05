"""Ekspor deklarasi AJU ke ZIP CSV (format Core Customs / BC 3.0)."""

from __future__ import annotations

import csv
import io
import zipfile
from typing import Any

from sqlalchemy.orm import Session

from app.services.customs_import import declaration_to_api_dict
from app.services.customs_templates import SHEET_EXPORT_FILENAMES


def _sheet_to_csv_bytes(header: list[str], rows: list[dict[str, Any]]) -> bytes:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(header)
    for row in rows:
        writer.writerow([row.get(k, "") for k in header])
    return buf.getvalue().encode("utf-8")


def export_declaration_zip(db: Session, declaration_id: int) -> tuple[bytes, str]:
    """Bangun ZIP berisi CSV per sheet; kembalikan (bytes, nama_file)."""
    detail = declaration_to_api_dict(db, declaration_id)
    if not detail:
        raise ValueError("Deklarasi tidak ditemukan")

    nomor = (detail.get("nomor_aju") or f"aju_{declaration_id}").strip()
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in nomor)[:48]
    zip_name = f"{safe_name}_bc30.zip"

    meta = detail.get("meta_json") or {}
    column_keys: dict[str, list[str]] = dict(meta.get("sheet_column_keys") or {})
    sheets: dict[str, list[dict[str, Any]]] = detail.get("sheets") or {}

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for sheet_code, filename in sorted(
            SHEET_EXPORT_FILENAMES.items(), key=lambda x: x[1]
        ):
            data_rows = sheets.get(sheet_code)
            if not data_rows:
                continue
            keys = column_keys.get(sheet_code)
            if not keys:
                key_set: set[str] = set()
                for r in data_rows:
                    key_set.update(r.keys())
                keys = sorted(key_set)
            csv_bytes = _sheet_to_csv_bytes(keys, data_rows)
            zf.writestr(filename, csv_bytes)

    return buf.getvalue(), zip_name
