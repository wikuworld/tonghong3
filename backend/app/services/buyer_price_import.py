"""Impor folder CSV `LIST_HARGA_ALL_BUYER_extracted` → buyer_price_lists + baris JSON."""

from __future__ import annotations

import csv
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

PERIODE_RE = re.compile(
    r"PERIODE\s+(\d{4}/\d{2}/\d{2})\s*[-–]\s*(\d{4}/\d{2}/\d{2})",
    re.IGNORECASE,
)


def filename_to_buyer(name: str) -> Optional[str]:
    m = re.match(r"^\d+_(.+)\.csv$", name.strip(), re.I)
    if not m:
        return None
    return m.group(1).upper()


def parse_period_from_rows(rows: list[list[str]]) -> tuple[str, Optional[date], Optional[date]]:
    label = ""
    start_d = end_d = None
    for row in rows[:20]:
        line = ",".join(row)
        if "PERIODE" in line.upper():
            label = line.strip()
            m = PERIODE_RE.search(line)
            if m:
                try:
                    start_d = datetime.strptime(m.group(1), "%Y/%m/%d").date()
                    end_d = datetime.strptime(m.group(2), "%Y/%m/%d").date()
                except ValueError:
                    pass
            break
    return label, start_d, end_d


def row_nonempty(row: list[str]) -> bool:
    return any((c or "").strip() for c in row)


def _to_float(v: Any) -> Optional[float]:
    if v is None:
        return None
    s = str(v).strip().replace(",", "")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _fmt_num(v: Optional[float]) -> str:
    if v is None:
        return "0"
    # Simpan ringkas agar UI input-number tetap nyaman dibaca.
    if abs(v - int(v)) < 1e-9:
        return str(int(v))
    return f"{v:.6f}".rstrip("0").rstrip(".")


def normalize_buyer_cells(cells: dict[str, Any]) -> Optional[dict[str, Any]]:
    """
    Normalisasi berbagai format CSV buyer ke shape standar UI:
    ITEM, THICKNESS, COLOR, COLOR WHITE, COLOR BLACK, FLOURASENT, METALIC, EMBOSS, SPESIAL EMBOSS
    """
    upper = {str(k or "").strip().upper(): v for k, v in (cells or {}).items()}

    # Format "LIST HARGA ALL BUYER_extracted": MATERIAL NAME + PRICE + METALLIC/...
    if "MATERIAL NAME" in upper and "PRICE" in upper:
        item = str(upper.get("MATERIAL NAME") or "").strip()
        thickness = str(upper.get("THICKNESS") or "").strip()
        base = _to_float(upper.get("PRICE"))
        metallic_total = _to_float(upper.get("METALLIC/PEARLIZED/FLUORESCENT"))
        if not item or base is None:
            return None
        metallic_addon = 0.0
        if metallic_total is not None:
            metallic_addon = max(0.0, metallic_total - base)
        return {
            "ITEM": item,
            "THICKNESS": thickness,
            "COLOR": "",
            "COLOR WHITE": _fmt_num(base),
            "COLOR BLACK": "0",
            "FLOURASENT": "0",
            "METALIC": _fmt_num(metallic_addon),
            "EMBOSS": "0",
            "SPESIAL EMBOSS": "0",
        }

    # Sudah dalam format standar UI.
    if "ITEM" in upper and "COLOR WHITE" in upper:
        return {
            "ITEM": str(upper.get("ITEM") or "").strip(),
            "THICKNESS": str(upper.get("THICKNESS") or "").strip(),
            "COLOR": str(upper.get("COLOR") or "").strip(),
            "COLOR WHITE": str(upper.get("COLOR WHITE") or "0").strip() or "0",
            "COLOR BLACK": str(upper.get("COLOR BLACK") or "0").strip() or "0",
            "FLOURASENT": str(upper.get("FLOURASENT") or "0").strip() or "0",
            "METALIC": str(upper.get("METALIC") or "0").strip() or "0",
            "EMBOSS": str(upper.get("EMBOSS") or "0").strip() or "0",
            "SPESIAL EMBOSS": str(upper.get("SPESIAL EMBOSS") or "0").strip() or "0",
        }

    return None


def _extract_thickness(material_name: str) -> str:
    text = str(material_name or "").strip()
    m = re.search(r"(\d+(?:\.\d+)?\s*-\s*\d+(?:\.\d+)?)\s*MM?$", text, re.IGNORECASE)
    if not m:
        return ""
    return m.group(1).replace(" ", "")


def _first_numeric(values: list[str]) -> Optional[float]:
    for val in values:
        num = _to_float(val)
        if num is not None:
            return num
    return None


def parse_nike_block_rows(raw: list[list[str]], header_idx: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current: Optional[dict[str, Any]] = None

    def flush_current() -> None:
        nonlocal current
        if not current:
            return
        item = str(current.get("ITEM") or "").strip()
        if not item:
            current = None
            return
        white = _to_float(current.get("WHITE"))
        black = _to_float(current.get("BLACK"))
        color = _to_float(current.get("COLOR_RAW"))
        metallic = _to_float(current.get("METALLIC_RAW"))
        fluo = _to_float(current.get("FLUORESCENT_RAW"))

        base = white
        if base is None:
            for candidate in (black, color, metallic, fluo):
                if candidate is not None:
                    base = candidate
                    break
        if base is None:
            current = None
            return

        rows.append(
            {
                "ITEM": item,
                "THICKNESS": str(current.get("THICKNESS") or "").strip(),
                "COLOR": "",
                "COLOR WHITE": _fmt_num(base),
                "COLOR BLACK": _fmt_num(max(0.0, (black or base) - base) if black is not None else 0.0),
                "FLOURASENT": _fmt_num(max(0.0, (fluo or base) - base) if fluo is not None else 0.0),
                "METALIC": _fmt_num(max(0.0, (metallic or base) - base) if metallic is not None else 0.0),
                "EMBOSS": "0",
                "SPESIAL EMBOSS": "0",
            }
        )
        current = None

    for row in raw[header_idx + 1 :]:
        if not row_nonempty(row):
            continue
        no_val = (row[0] if len(row) > 0 else "").strip()
        material_cell = (row[1] if len(row) > 1 else "").strip()
        numeric = _first_numeric([row[i].strip() for i in range(2, min(len(row), 6))])

        # Baris awal item material.
        if no_val.isdigit() and material_cell:
            flush_current()
            current = {
                "ITEM": material_cell,
                "THICKNESS": _extract_thickness(material_cell),
            }
            continue

        # Baris breakdown warna di bawah item aktif.
        if current and not no_val and material_cell:
            label = material_cell.upper()
            if label == "WHITE":
                current["WHITE"] = numeric
            elif label == "BLACK":
                current["BLACK"] = numeric
            elif label == "COLOR":
                current["COLOR_RAW"] = numeric
            elif "METALLIC" in label or "PEARL" in label or "ANODIZED" in label:
                current["METALLIC_RAW"] = numeric
            elif "FLUORESCENT" in label:
                current["FLUORESCENT_RAW"] = numeric

    flush_current()
    return rows


def parse_price_block_rows(raw: list[list[str]], header_idx: int, headers: list[str]) -> Optional[list[dict[str, Any]]]:
    """
    Parser untuk format blok:
    - baris item utama: NO terisi (1,2,3...), MATERIAL NAME berisi nama material
    - baris turunan: NO kosong, MATERIAL NAME berisi WHITE/BLACK/COLOR/FLUORESCENT...
    """
    try:
        idx_no = next(i for i, h in enumerate(headers) if h.strip().upper() == "NO")
        idx_material = next(i for i, h in enumerate(headers) if h.strip().upper() == "MATERIAL NAME")
        idx_price = next(i for i, h in enumerate(headers) if h.strip().upper() == "PRICE")
    except StopIteration:
        return None

    idx_metallic: Optional[int] = None
    for i, h in enumerate(headers):
        up = h.strip().upper()
        if "METALLIC" in up or "PEARL" in up or "ANODIZED" in up:
            idx_metallic = i
            break

    def get_val(row: list[str], idx: int) -> str:
        return row[idx].strip() if idx < len(row) else ""

    # Deteksi apakah benar format blok warna.
    continuation_count = 0
    for row in raw[header_idx + 1 :]:
        if not row_nonempty(row):
            continue
        no_val = get_val(row, idx_no)
        mat = get_val(row, idx_material).upper()
        if (not no_val) and mat in {"WHITE", "BLACK", "COLOR", "FLUORESCENT"}:
            continuation_count += 1
            if continuation_count >= 2:
                break
    if continuation_count < 2:
        return None

    rows: list[dict[str, Any]] = []
    current: Optional[dict[str, Any]] = None

    def flush_current() -> None:
        nonlocal current
        if not current:
            return
        item = str(current.get("ITEM") or "").strip()
        if not item:
            current = None
            return

        white = _to_float(current.get("WHITE"))
        black = _to_float(current.get("BLACK"))
        fluo = _to_float(current.get("FLUORESCENT"))
        metallic_total = _to_float(current.get("METALLIC_TOTAL"))
        color_price = _to_float(current.get("COLOR_PRICE"))

        base = white
        if base is None:
            for candidate in (black, color_price, fluo, metallic_total):
                if candidate is not None:
                    base = candidate
                    break
        if base is None:
            current = None
            return

        metallic_ref = color_price if color_price is not None else base
        metallic_addon = 0.0
        if metallic_total is not None:
            metallic_addon = max(0.0, metallic_total - metallic_ref)

        rows.append(
            {
                "ITEM": item,
                "THICKNESS": str(current.get("THICKNESS") or "").strip(),
                "COLOR": "",
                "COLOR WHITE": _fmt_num(base),
                "COLOR BLACK": _fmt_num(max(0.0, (black or base) - base) if black is not None else 0.0),
                "FLOURASENT": _fmt_num(max(0.0, (fluo or base) - base) if fluo is not None else 0.0),
                "METALIC": _fmt_num(metallic_addon),
                "EMBOSS": "0",
                "SPESIAL EMBOSS": "0",
            }
        )
        current = None

    for row in raw[header_idx + 1 :]:
        if not row_nonempty(row):
            continue
        no_val = get_val(row, idx_no)
        material = get_val(row, idx_material)
        price_val = _to_float(get_val(row, idx_price))
        metallic_val = _to_float(get_val(row, idx_metallic)) if idx_metallic is not None else None
        material_up = material.upper()

        if no_val.isdigit() and material:
            flush_current()
            current = {"ITEM": material, "THICKNESS": _extract_thickness(material)}
            continue

        if current and not no_val and material:
            if material_up == "WHITE":
                current["WHITE"] = price_val
            elif material_up == "BLACK":
                current["BLACK"] = price_val
            elif material_up == "COLOR":
                current["COLOR_PRICE"] = price_val
                if metallic_val is not None:
                    current["METALLIC_TOTAL"] = metallic_val
            elif "FLUORESCENT" in material_up:
                current["FLUORESCENT"] = price_val
                if metallic_val is not None:
                    current["METALLIC_TOTAL"] = metallic_val
            elif any(x in material_up for x in ("METALLIC", "PEARL", "ANODIZED")):
                current["METALLIC_TOTAL"] = price_val

    flush_current()
    return rows


def parse_buyer_csv(path: Path) -> dict[str, Any]:
    with open(path, newline="", encoding="utf-8") as f:
        raw = list(csv.reader(f))
    title = (raw[0][0] if raw and raw[0] else "").strip()
    period_label, ps, pe = parse_period_from_rows(raw)

    header_idx: Optional[int] = None
    headers: list[str] = []
    for i, row in enumerate(raw):
        if not row:
            continue
        c0 = (row[0] or "").strip().upper()
        if c0 == "NO" or c0.startswith("NO"):
            header_idx = i
            headers = [(c or "").strip() for c in row]
            break

    data_rows: list[dict[str, Any]] = []
    if header_idx is not None:
        upper_headers = {h.strip().upper() for h in headers}
        if "PRICE COMMON" in upper_headers and "MATERIAL NAME" in upper_headers:
            data_rows = parse_nike_block_rows(raw, header_idx)
            return {
                "title": title,
                "period_label": period_label,
                "period_start": ps,
                "period_end": pe,
                "header_row_index": header_idx,
                "csv_line_count": len(raw),
                "data_rows": data_rows,
            }
        if "MATERIAL NAME" in upper_headers and "PRICE" in upper_headers:
            block_rows = parse_price_block_rows(raw, header_idx, headers)
            if block_rows is not None:
                return {
                    "title": title,
                    "period_label": period_label,
                    "period_start": ps,
                    "period_end": pe,
                    "header_row_index": header_idx,
                    "csv_line_count": len(raw),
                    "data_rows": block_rows,
                }
        for row in raw[header_idx + 1 :]:
            if not row_nonempty(row):
                continue
            d: dict[str, Any] = {}
            for k, h in enumerate(headers):
                key = h if h else f"_col{k}"
                val = row[k].strip() if k < len(row) else ""
                d[key] = val
            normalized = normalize_buyer_cells(d)
            if normalized is not None:
                data_rows.append(normalized)
    else:
        for row in raw:
            if not row_nonempty(row):
                continue
            normalized = normalize_buyer_cells(
                {f"col_{k}": row[k] if k < len(row) else "" for k in range(len(row))}
            )
            if normalized is not None:
                data_rows.append(normalized)

    return {
        "title": title,
        "period_label": period_label,
        "period_start": ps,
        "period_end": pe,
        "header_row_index": header_idx,
        "csv_line_count": len(raw),
        "data_rows": data_rows,
    }


def persist_buyer_folder(
    db: Any,
    folder: Path,
    source_label: Optional[str],
) -> list[Any]:
    """Satu `BuyerPriceList` per file buyer; hapus data lama dengan `buyer_code` sama."""
    from sqlalchemy import select

    from app.models import BuyerPriceList, BuyerPriceSheetRow

    if not folder.is_dir():
        raise ValueError(f"Bukan folder: {folder}")

    out: list[Any] = []
    for p in sorted(folder.glob("*.csv")):
        if p.name.upper() == "README.MD":
            continue
        buyer = filename_to_buyer(p.name)
        if not buyer:
            continue
        parsed = parse_buyer_csv(p)
        data_rows = parsed["data_rows"]

        existing = db.scalars(
            select(BuyerPriceList).where(BuyerPriceList.buyer_code == buyer)
        ).first()
        if existing:
            db.delete(existing)
            db.flush()

        lst = BuyerPriceList(
            buyer_code=buyer,
            title=parsed["title"] or None,
            period_label=parsed["period_label"] or None,
            period_start=parsed["period_start"],
            period_end=parsed["period_end"],
            currency="USD",
            meta_json={
                "filename": p.name,
                "source_label": source_label or folder.name,
                "header_row_index": parsed["header_row_index"],
                "csv_line_count": parsed["csv_line_count"],
                "data_row_count": len(data_rows),
            },
        )
        db.add(lst)
        db.flush()
        for ri, cells in enumerate(data_rows):
            db.add(BuyerPriceSheetRow(list_id=lst.id, row_number=ri, cells=cells))
        out.append(lst)
    db.flush()
    for o in out:
        db.refresh(o)
    return out


def list_to_api_dict(db: Any, list_id: int) -> dict[str, Any]:
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.models import BuyerPriceList, MasterItem

    row = db.scalars(
        select(BuyerPriceList)
        .options(selectinload(BuyerPriceList.rows))
        .where(BuyerPriceList.id == list_id)
    ).first()
    if not row:
        return {}
    lines = sorted(row.rows, key=lambda r: r.row_number)
    rows_out: list[dict[str, Any]] = []
    item_codes = {
        str((r.cells or {}).get("ITEM") or "").strip()
        for r in lines
        if isinstance(r.cells, dict) and str((r.cells or {}).get("ITEM") or "").strip()
    }
    item_codes = {x for x in item_codes if x}
    material_by_code: dict[str, str] = {}
    if item_codes:
        mats = db.execute(
            select(MasterItem.item_code, MasterItem.material_name).where(MasterItem.item_code.in_(item_codes))
        ).all()
        material_by_code = {
            str(code or "").strip(): str(material or "").strip()
            for code, material in mats
            if str(code or "").strip() and str(material or "").strip()
        }

    for line in lines:
        cells = dict(line.cells or {}) if isinstance(line.cells, dict) else {}
        item_val = str(cells.get("ITEM") or "").strip()
        if item_val in material_by_code:
            cells["ITEM"] = material_by_code[item_val]
        rows_out.append(cells)

    return {
        "id": row.id,
        "buyer_code": row.buyer_code,
        "title": row.title,
        "period_label": row.period_label,
        "period_start": row.period_start.isoformat() if row.period_start else None,
        "period_end": row.period_end.isoformat() if row.period_end else None,
        "currency": row.currency,
        "meta_json": row.meta_json,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "rows": rows_out,
        "row_count": len(lines),
    }
