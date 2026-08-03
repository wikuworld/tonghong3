"""Normalisasi dan impor master item kategori SubKon."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MasterItem
from app.services.thickness_format import canonical_thickness_range

SUBKON_CATEGORY = "SubKon"
EMPTY_MARKERS = {"", "-", "—", "–", "n/a", "na", "null", "none"}


@dataclass
class SubKonImportResult:
    imported: int
    inserted: int
    updated: int
    skipped: int

    def to_dict(self) -> dict[str, int]:
        return {
            "imported": self.imported,
            "inserted": self.inserted,
            "updated": self.updated,
            "skipped": self.skipped,
        }


def _clean_text(value: str | None) -> str | None:
    raw = str(value or "").strip()
    if raw.lower() in EMPTY_MARKERS:
        return None
    return raw


def _pick_row_value(row: dict[str, str | None], *keys: str) -> str | None:
    lower_map = {str(k).strip().lower(): v for k, v in row.items()}
    for key in keys:
        if key in row:
            val = row.get(key)
            if val is not None and str(val).strip():
                return str(val)
        lk = key.lower()
        if lk in lower_map:
            val = lower_map[lk]
            if val is not None and str(val).strip():
                return str(val)
    return None


def map_subkon_source_row(row: dict[str, str | None]) -> dict[str, str | None]:
    return {
        "item_code": _pick_row_value(row, "item_code", "KODE BARANG", "kode barang"),
        "thickness_range": _pick_row_value(row, "thickness_range", "thickness", "THICKNESS", "ketebalan"),
        "material_name": _pick_row_value(row, "material_name", "MATERIAL NAME", "material name"),
        "color": _pick_row_value(row, "color", "COLOR", "warna"),
        "emboss": _pick_row_value(row, "emboss", "EMBOSS"),
    }


def normalize_subkon_row(row: dict[str, str | None]) -> dict[str, str | None]:
    mapped = map_subkon_source_row(row) if any(
        k.lower() in {str(x).strip().lower() for x in row.keys()}
        for k in ("KODE BARANG", "MATERIAL NAME", "THICKNESS", "COLOR", "EMBOSS")
    ) else row
    thickness_raw = _clean_text(mapped.get("thickness_range") or mapped.get("thickness"))
    thickness = canonical_thickness_range(thickness_raw) if thickness_raw else None
    if thickness == "":
        thickness = None
    return {
        "category": SUBKON_CATEGORY,
        "item_code": _clean_text(mapped.get("item_code")),
        "material_name": _clean_text(mapped.get("material_name")),
        "thickness_range": thickness,
        "color": _clean_text(mapped.get("color")),
        "emboss": _clean_text(mapped.get("emboss")),
    }


def _detect_csv_delimiter(path: Path) -> str:
    with open(path, newline="", encoding="utf-8-sig") as f:
        first_line = f.readline()
    if first_line.count(";") >= first_line.count(","):
        return ";"
    return ","


def iter_subkon_rows_from_csv(path: Path) -> Iterable[dict[str, str | None]]:
    delimiter = _detect_csv_delimiter(path)
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f, delimiter=delimiter):
            yield normalize_subkon_row(row)


def iter_subkon_rows_from_bytes(content: bytes) -> Iterable[dict[str, str | None]]:
    text = content.decode("utf-8-sig", errors="ignore")
    for row in csv.DictReader(io.StringIO(text)):
        yield normalize_subkon_row(row)


def import_subkon_master_items(
    db: Session,
    rows: Iterable[dict[str, str | None]],
    *,
    dry_run: bool = False,
) -> SubKonImportResult:
    inserted = 0
    updated = 0
    skipped = 0
    seen_codes: set[str] = set()

    for item_data in rows:
        code = item_data.get("item_code")
        if not code:
            skipped += 1
            continue
        if code in seen_codes:
            skipped += 1
            continue
        seen_codes.add(code)

        existing = db.scalars(select(MasterItem).where(MasterItem.item_code == code)).first()
        if existing:
            changed = False
            for field in ("category", "material_name", "thickness_range", "color", "emboss"):
                val = item_data.get(field)
                if val is not None and getattr(existing, field) != val:
                    setattr(existing, field, val)
                    changed = True
            if changed:
                existing.updated_at = datetime.utcnow()
                updated += 1
            else:
                skipped += 1
            continue

        db.add(
            MasterItem(
                item_code=code,
                category=item_data.get("category"),
                material_name=item_data.get("material_name"),
                thickness_range=item_data.get("thickness_range"),
                color=item_data.get("color"),
                emboss=item_data.get("emboss"),
            )
        )
        inserted += 1

    if dry_run:
        db.rollback()
    else:
        db.commit()

    return SubKonImportResult(
        imported=inserted + updated,
        inserted=inserted,
        updated=updated,
        skipped=skipped,
    )
