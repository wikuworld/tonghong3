"""Baca master_items Tonghong ERP dari MariaDB (sumber spek FG untuk MRP)."""

from __future__ import annotations

import os
import re
from typing import Any, Optional

from db import root_db_config
import mysql.connector

_ERP_DB = os.getenv("ERP_DB_NAME", "tonghong")

_RANGE_RE = re.compile(r"^\s*([\d.]+)\s*[-–]\s*([\d.]+)\s*$")


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _canonical_thickness(text: Any) -> str:
    raw = str(text or "").strip().replace("mm", "").strip()
    if not raw or raw in {"-", "—", "–"}:
        return ""
    m = _RANGE_RE.match(raw)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return raw


def _thickness_matches(row_thickness: Any, want: Any) -> bool:
    a = _canonical_thickness(row_thickness)
    b = _canonical_thickness(want)
    if not a or not b:
        return False
    return _norm(a) == _norm(b) or a.replace(" ", "") == b.replace(" ", "")


def _row_thickness(row: dict) -> str:
    tr = (row.get("thickness_range") or "").strip()
    if tr:
        return _canonical_thickness(tr)
    mm = row.get("thickness_mm")
    if mm is not None and str(mm).strip():
        return _canonical_thickness(mm)
    return ""


def _erp_connect():
    cfg = root_db_config()
    cfg["database"] = _ERP_DB
    return mysql.connector.connect(**cfg)


def fetch_master_items(limit: int | None = None) -> list[dict]:
    conn = _erp_connect()
    cur = conn.cursor(dictionary=True)
    sql = (
        "SELECT id, item_code, category, material_name, thickness_range, thickness_mm, "
        "color, emboss, color_reference, color_standard, backing "
        "FROM master_items ORDER BY item_code"
    )
    if limit:
        sql += f" LIMIT {int(limit)}"
    cur.execute(sql)
    rows = list(cur.fetchall() or [])
    cur.close()
    conn.close()
    return rows


def item_to_erp_shape(row: dict) -> dict:
    thickness = _row_thickness(row)
    return {
        "id": row["id"],
        "erp_master_item_id": row["id"],
        "item_code": row.get("item_code"),
        "category": row.get("category"),
        "thickness": thickness or None,
        "material_name": row.get("material_name"),
        "color": row.get("color"),
        "emboss": row.get("emboss"),
        "color_swatch": row.get("color_reference") or row.get("color_standard"),
        "backer": row.get("backing"),
        "customer": None,
        "source": "master_items",
    }


def _distinct(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for raw in values:
        v = (raw or "").strip()
        if not v:
            continue
        key = _norm(v)
        if key in seen:
            continue
        seen.add(key)
        out.append(v)
    return sorted(out, key=lambda s: s.lower())


def options_payload(rows: list[dict] | None = None) -> dict:
    rows = rows if rows is not None else fetch_master_items()
    return {
        "thickness": _distinct([_row_thickness(r) for r in rows]),
        "materials": _distinct([(r.get("material_name") or "") for r in rows]),
        "colors": _distinct([(r.get("color") or "") for r in rows]),
        "emboss": _distinct([(r.get("emboss") or "") for r in rows]),
        "customers": [],
        "color_swatch": _distinct(
            [(r.get("color_reference") or r.get("color_standard") or "") for r in rows]
        ),
        "categories": _distinct([(r.get("category") or "") for r in rows]),
        "source": "master_items",
    }


def fields_payload(
    *,
    thickness: str = "",
    material_name: str = "",
    color: str = "",
    rows: list[dict] | None = None,
) -> dict:
    rows = rows if rows is not None else fetch_master_items()
    filtered = rows
    if thickness.strip():
        filtered = [r for r in filtered if _thickness_matches(_row_thickness(r), thickness)]
    if material_name.strip():
        m = _norm(material_name)
        filtered = [r for r in filtered if _norm(r.get("material_name")) == m]
    if color.strip():
        c = _norm(color)
        filtered = [r for r in filtered if _norm(r.get("color")) == c]
    return {
        "thicknesses": _distinct([_row_thickness(r) for r in rows]),
        "material_names": _distinct([(r.get("material_name") or "") for r in filtered]),
        "colors": _distinct([(r.get("color") or "") for r in filtered]),
        "embosses": _distinct([(r.get("emboss") or "") for r in filtered]),
        "customers": [],
        "source": "master_items",
    }


def combination_payload(
    *,
    material_name: str,
    color: str,
    emboss: str,
    thickness: str = "",
    rows: list[dict] | None = None,
) -> list[dict]:
    rows = rows if rows is not None else fetch_master_items()
    m, c, e = _norm(material_name), _norm(color), _norm(emboss)
    hits = []
    for r in rows:
        if _norm(r.get("material_name")) != m:
            continue
        if _norm(r.get("color")) != c:
            continue
        if _norm(r.get("emboss")) != e:
            continue
        if thickness.strip() and not _thickness_matches(_row_thickness(r), thickness):
            continue
        hits.append(item_to_erp_shape(r))
    return hits


def lookup_backer(
    *,
    material_name: str,
    thickness: str,
    color: str,
    emboss: str | None = None,
) -> Optional[str]:
    """Resolve backing dari master_items (material + tebal + warna, opsional emboss)."""
    rows = fetch_master_items()
    m, c = _norm(material_name), _norm(color)
    hits = []
    for r in rows:
        if _norm(r.get("material_name")) != m:
            continue
        if not _thickness_matches(_row_thickness(r), thickness):
            continue
        if _norm(r.get("color")) != c:
            continue
        hits.append(r)
    if emboss and str(emboss).strip() and str(emboss).strip() != "-":
        e = _norm(emboss)
        narrowed = [r for r in hits if _norm(r.get("emboss")) == e]
        if narrowed:
            hits = narrowed
    for r in hits:
        b = (r.get("backing") or "").strip()
        if b:
            return b
    return None
