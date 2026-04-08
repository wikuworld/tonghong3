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
        for row in raw[header_idx + 1 :]:
            if not row_nonempty(row):
                continue
            d: dict[str, Any] = {}
            for k, h in enumerate(headers):
                key = h if h else f"_col{k}"
                val = row[k].strip() if k < len(row) else ""
                d[key] = val
            data_rows.append(d)
    else:
        for row in raw:
            if not row_nonempty(row):
                continue
            data_rows.append(
                {f"col_{k}": row[k] if k < len(row) else "" for k in range(len(row))}
            )

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
            source_label=source_label or folder.name,
            meta_json={
                "filename": p.name,
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

    from app.models import BuyerPriceList

    row = db.scalars(
        select(BuyerPriceList)
        .options(selectinload(BuyerPriceList.rows))
        .where(BuyerPriceList.id == list_id)
    ).first()
    if not row:
        return {}
    lines = sorted(row.rows, key=lambda r: r.row_number)
    return {
        "id": row.id,
        "buyer_code": row.buyer_code,
        "title": row.title,
        "period_label": row.period_label,
        "period_start": row.period_start.isoformat() if row.period_start else None,
        "period_end": row.period_end.isoformat() if row.period_end else None,
        "source_label": row.source_label,
        "meta_json": row.meta_json,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "rows": [r.cells for r in lines],
        "row_count": len(lines),
    }
