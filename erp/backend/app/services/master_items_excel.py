"""Export/import Excel master items — upsert by item_code, update parsial, anti-duplikat."""

from __future__ import annotations

import io
from dataclasses import asdict, dataclass, field
from typing import Any

from openpyxl import Workbook, load_workbook
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import MasterItem
from app.services.color_code import apply_item_color_extract
from app.timeutil import app_now

EXPORT_COLUMNS = [
    "category",
    "item_code",
    "material_name",
    "thickness_range",
    "color",
    "emboss",
    "flag_color_black",
    "flag_color",
    "flag_flourasent",
    "flag_metalic",
    "flag_emboss",
    "flag_special_emboss",
]

FLAG_COLUMNS = [
    "flag_color_black",
    "flag_color",
    "flag_flourasent",
    "flag_metalic",
    "flag_emboss",
    "flag_special_emboss",
]

CATEGORY_ALIAS = {
    "pu": "PU",
    "suide": "Suede",
    "suede": "Suede",
    "subkon": "SubKon",
    "subcont": "SubKon",
    "subcontract": "SubKon",
}

@dataclass
class ImportErrorRow:
    row: int
    item_code: str | None
    reason: str


@dataclass
class MasterItemsImportResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    total_rows: int = 0
    errors: list[ImportErrorRow] = field(default_factory=list)

    @property
    def imported(self) -> int:
        """Kompatibilitas: baris yang benar-benar mengubah data."""
        return self.created + self.updated

    def to_dict(self) -> dict[str, Any]:
        return {
            "created": self.created,
            "updated": self.updated,
            "skipped": self.skipped,
            "total_rows": self.total_rows,
            "imported": self.imported,
            "errors": [asdict(e) for e in self.errors],
        }


def _normalize_header(raw: Any) -> str:
    s = str(raw or "").strip().lower().replace(" ", "_").replace("-", "_")
    while "__" in s:
        s = s.replace("__", "_")
    return s


def _cell_str(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()


def parse_flag_cell(raw: Any) -> bool | None:
    """None jika kosong (jangan ubah data lama). ValueError jika bukan ya/tidak."""
    s = _cell_str(raw).lower()
    if not s:
        return None
    if s in {"1", "true", "yes", "y", "ya"}:
        return True
    if s in {"0", "false", "no", "n", "tidak"}:
        return False
    raise ValueError("flag_invalid")


def normalize_category(raw: str | None) -> str | None:
    """None jika kosong; ValueError jika tidak valid."""
    s = _cell_str(raw)
    if not s:
        return None
    out = CATEGORY_ALIAS.get(s.lower())
    if not out:
        raise ValueError("category_invalid")
    return out


def export_master_items_xlsx(db: Session) -> bytes:
    """Header snake_case (item_code, …) agar round-trip stabil."""
    items = list(db.scalars(select(MasterItem).order_by(MasterItem.item_code)).all())
    wb = Workbook()
    ws = wb.active
    ws.title = "Master Items"
    for col_idx, col in enumerate(EXPORT_COLUMNS, 1):
        ws.cell(row=1, column=col_idx, value=col)
    for row_idx, item in enumerate(items, 2):
        for col_idx, col in enumerate(EXPORT_COLUMNS, 1):
            val = getattr(item, col, None)
            if col in FLAG_COLUMNS:
                ws.cell(row=row_idx, column=col_idx, value="true" if bool(val) else "false")
            else:
                ws.cell(row=row_idx, column=col_idx, value="" if val is None else str(val))
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


def export_master_items_template_xlsx() -> bytes:
    """Template kosong hanya header."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Master Items"
    for col_idx, col in enumerate(EXPORT_COLUMNS, 1):
        ws.cell(row=1, column=col_idx, value=col)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


def _parse_rows_from_excel(content: bytes) -> tuple[list[dict[str, str]], list[ImportErrorRow]]:
    """Baca sheet aktif; map kolom by nama header (normalize)."""
    wb = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    ws = wb.active
    rows_iter = ws.iter_rows(values_only=True)
    try:
        header_row = next(rows_iter)
    except StopIteration:
        return [], [ImportErrorRow(row=1, item_code=None, reason="File Excel kosong")]

    # Terima snake_case baru + judul lama ("Item Code" → item_code)
    title_to_key = {
        c: c for c in EXPORT_COLUMNS
    }
    for c in EXPORT_COLUMNS:
        title_to_key[_normalize_header(c.replace("_", " ").title())] = c

    col_map: dict[int, str] = {}
    for idx, cell in enumerate(header_row):
        key = _normalize_header(cell)
        mapped = title_to_key.get(key)
        if mapped and mapped not in col_map.values():
            col_map[idx] = mapped

    if "item_code" not in col_map.values():
        return [], [
            ImportErrorRow(
                row=1,
                item_code=None,
                reason="Header wajib memuat kolom item_code (dan kolom master item lainnya)",
            )
        ]

    parsed: list[dict[str, str]] = []
    parse_errors: list[ImportErrorRow] = []
    for excel_row_num, row in enumerate(rows_iter, start=2):
        if row is None or all(c is None or str(c).strip() == "" for c in row):
            continue
        item: dict[str, str] = {c: "" for c in EXPORT_COLUMNS}
        for idx, key in col_map.items():
            if idx < len(row):
                item[key] = _cell_str(row[idx])
        # Skip fully empty after map
        if not any(item.get(c) for c in EXPORT_COLUMNS):
            continue
        item["_row"] = str(excel_row_num)  # type: ignore[assignment]
        parsed.append(item)
    return parsed, parse_errors


def _values_equal(a: Any, b: Any) -> bool:
    return _cell_str(a) == _cell_str(b)


def import_master_items_xlsx(db: Session, content: bytes) -> MasterItemsImportResult:
    result = MasterItemsImportResult()
    rows, parse_errors = _parse_rows_from_excel(content)
    result.errors.extend(parse_errors)
    if parse_errors and not rows:
        return result

    # Preload existing by item_code for fewer queries
    existing_all = list(db.scalars(select(MasterItem)).all())
    by_code: dict[str, MasterItem] = {
        (m.item_code or "").strip(): m for m in existing_all if (m.item_code or "").strip()
    }
    seen_in_file: set[str] = set()

    for item in rows:
        result.total_rows += 1
        excel_row = int(item.pop("_row", "0") or 0)
        code = _cell_str(item.get("item_code"))
        if not code:
            result.skipped += 1
            result.errors.append(
                ImportErrorRow(row=excel_row, item_code=None, reason="item_code wajib diisi")
            )
            continue

        category_raw = item.get("category")
        category_norm: str | None = None
        if _cell_str(category_raw):
            try:
                category_norm = normalize_category(category_raw)
            except ValueError:
                result.skipped += 1
                result.errors.append(
                    ImportErrorRow(
                        row=excel_row,
                        item_code=code,
                        reason="category harus salah satu: PU, Suede, SubKon",
                    )
                )
                continue

        # Build patch: only non-empty cells
        patch: dict[str, str] = {}
        if category_norm is not None:
            patch["category"] = category_norm
        for f in ("material_name", "thickness_range", "color", "emboss"):
            val = _cell_str(item.get(f))
            if val:
                patch[f] = val

        flag_patch: dict[str, bool] = {}
        try:
            for f in FLAG_COLUMNS:
                parsed = parse_flag_cell(item.get(f, ""))
                if parsed is not None:
                    flag_patch[f] = parsed
        except ValueError:
            result.skipped += 1
            result.errors.append(
                ImportErrorRow(
                    row=excel_row,
                    item_code=code,
                    reason="flag addon harus true/false (atau kosong)",
                )
            )
            continue

        existing = by_code.get(code)
        if existing is None and code in seen_in_file:
            # Same new code appears again in file before flush — treat as update of session object
            existing = by_code.get(code)

        if existing is None:
            if "category" not in patch:
                result.skipped += 1
                result.errors.append(
                    ImportErrorRow(
                        row=excel_row,
                        item_code=code,
                        reason="category wajib diisi untuk item baru",
                    )
                )
                continue
            row = MasterItem(item_code=code)
            for k, v in patch.items():
                setattr(row, k, v)
            for f in FLAG_COLUMNS:
                setattr(row, f, flag_patch.get(f, False))
            if "color" in patch:
                apply_item_color_extract(row)
            row.updated_at = app_now()
            db.add(row)
            db.flush()
            by_code[code] = row
            seen_in_file.add(code)
            result.created += 1
            continue

        # Update existing — partial
        changed = False
        color_changed = False
        for k, v in patch.items():
            if not _values_equal(getattr(existing, k, None), v):
                setattr(existing, k, v)
                changed = True
                if k == "color":
                    color_changed = True
        for k, v in flag_patch.items():
            if bool(getattr(existing, k, False)) != v:
                setattr(existing, k, v)
                changed = True
        if color_changed:
            apply_item_color_extract(existing)
        if changed:
            existing.updated_at = app_now()
            result.updated += 1
        else:
            result.skipped += 1
        by_code[code] = existing
        seen_in_file.add(code)

    return result
