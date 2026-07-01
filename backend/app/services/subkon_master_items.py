"""Normalisasi dan impor master item kategori SubKon."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
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


def normalize_subkon_row(row: dict[str, str | None]) -> dict[str, str | None]:
    thickness_raw = _clean_text(row.get("thickness_range") or row.get("thickness"))
    thickness = canonical_thickness_range(thickness_raw) if thickness_raw else None
    if thickness == "":
        thickness = None
    return {
        "category": SUBKON_CATEGORY,
        "item_code": _clean_text(row.get("item_code")),
        "material_name": _clean_text(row.get("material_name")),
        "thickness_range": thickness,
        "color": _clean_text(row.get("color")),
        "emboss": _clean_text(row.get("emboss")),
    }


def iter_subkon_rows_from_csv(path: Path) -> Iterable[dict[str, str | None]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
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

    for item_data in rows:
        code = item_data.get("item_code")
        if not code:
            skipped += 1
            continue

        existing = db.scalars(select(MasterItem).where(MasterItem.item_code == code)).first()
        if existing:
            changed = False
            for field in ("category", "material_name", "thickness_range", "color", "emboss"):
                val = item_data.get(field)
                if val is not None and getattr(existing, field) != val:
                    setattr(existing, field, val)
                    changed = True
            if changed:
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
