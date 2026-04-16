"""Resolusi harga baris SO dari sheet List Harga Buyer (server-side, otoritatif)."""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import BuyerPriceList
from app.services.buyer_price_import import list_to_api_dict


def _norm(s: str | None) -> str:
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s).strip().lower())


def _collect_price_keys(column_keys: list[str]) -> list[str]:
    out: list[str] = []
    for k in column_keys:
        if k is None:
            continue
        ks = str(k).strip()
        if re.search(r"price|harga", ks, re.I):
            out.append(ks)
    return out


def _pick_price_column(price_keys: list[str], color_family: str | None) -> str | None:
    if not price_keys:
        return None
    cf = (color_family or "").strip().lower() or "color"
    if cf == "fluorescent":
        for k in price_keys:
            if re.search(r"fluores|metallic|pearl", str(k), re.I):
                return k
        return price_keys[-1]
    if cf == "black":
        for k in price_keys:
            if re.search(r"black", str(k), re.I):
                return k
        return price_keys[0]
    for k in price_keys:
        if re.match(r"^price$", str(k).strip(), re.I):
            return k
    for k in price_keys:
        if re.search(r"common|dasar|utama", str(k), re.I) and "special" not in str(k).lower():
            return k
    return price_keys[0]


def _parse_price_cell(val: Any) -> Decimal | None:
    if val is None:
        return None
    s = str(val).strip().replace(",", "")
    s = re.sub(r"[^\d.\-]", "", s)
    if not s:
        return None
    try:
        return Decimal(s)
    except Exception:
        return None


def _score_row(
    row: dict[str, Any],
    keys: list[str],
    price_key_set: set[str],
    *,
    material_name: str | None,
    color: str | None,
    style_article: str | None,
    thickness_text: str | None,
) -> int:
    mat = _norm(material_name)
    col = _norm(color)
    sty = _norm(style_article)
    th = _norm(thickness_text)
    blob_parts: list[str] = []
    thick_cells: list[str] = []
    for k in keys:
        if k in price_key_set:
            continue
        cell = _norm(row.get(k))
        if not cell:
            continue
        blob_parts.append(cell)
        if re.search(r"thick|tebal|mm", str(k), re.I):
            thick_cells.append(cell)
    blob = " ".join(blob_parts)
    s = 0
    if mat:
        if mat in blob:
            s += 12
        for part in blob_parts:
            if mat in part or part in mat:
                s += 6
                break
    if th:
        matched_th = any(th in c or c in th for c in thick_cells) if thick_cells else th in blob
        if matched_th:
            s += 10
    if sty and sty in blob:
        s += 5
    if col and col in blob:
        s += 4
    return s


def resolve_unit_price_for_buyer(
    db: Session,
    buyer_code: str,
    *,
    material_name: Optional[str] = None,
    color: Optional[str] = None,
    style_article: Optional[str] = None,
    thickness_text: Optional[str] = None,
    color_family: Optional[str] = None,
) -> dict[str, Any]:
    code = (buyer_code or "").strip().upper()
    if not code:
        return {
            "unit_price": None,
            "matched": False,
            "price_column": None,
            "score": 0,
            "detail": "buyer_code wajib diisi - tidak dapat mencari harga tanpa kode buyer",
        }

    lst = db.scalars(select(BuyerPriceList).where(BuyerPriceList.buyer_code == code)).first()
    if not lst:
        return {
            "unit_price": None,
            "matched": False,
            "price_column": None,
            "score": 0,
            "detail": f"List harga untuk buyer '{code}' tidak ditemukan - pastikan master buyer sudah diimport",
        }

    sheet = list_to_api_dict(db, lst.id)
    rows: list[dict[str, Any]] = sheet.get("rows") or []
    meta: dict[str, Any] = sheet.get("meta_json") or {}
    keys: list[str] = list(meta.get("column_keys") or [])
    if not keys and rows:
        keys = list(rows[0].keys())

    price_keys = _collect_price_keys(keys)
    pk_set = set(price_keys)
    if not price_keys:
        return {
            "unit_price": None,
            "matched": False,
            "price_column": None,
            "score": 0,
            "detail": "Kolom harga tidak ditemukan di list buyer - import data gagal atau kolom tidak terdefinisi",
        }

    price_col = _pick_price_column(price_keys, color_family)
    best_row: dict[str, Any] | None = None
    best_score = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        sc = _score_row(
            row,
            keys,
            pk_set,
            material_name=material_name,
            color=color,
            style_article=style_article,
            thickness_text=thickness_text,
        )
        if sc > best_score:
            best_score = sc
            best_row = row

    if best_score == 0 or not best_row:
        return {
            "unit_price": None,
            "matched": False,
            "price_column": price_col,
            "score": 0,
            "detail": f"Tidak ada baris yang cocok untuk material '{material_name or '-'}' dengan kriteria yang diberikan - cek nama material atau thickness",
        }

    unit: Decimal | None = None
    chosen_col = price_col
    if chosen_col:
        unit = _parse_price_cell(best_row.get(chosen_col))
    if unit is None:
        for pk in price_keys:
            unit = _parse_price_cell(best_row.get(pk))
            if unit is not None:
                chosen_col = pk
                break

    if unit is None:
        return {
            "unit_price": None,
            "matched": False,
            "price_column": chosen_col,
            "score": best_score,
            "detail": "Baris ditemukan tapi sel harga kosong - harga belum diinput untuk item ini",
        }

    return {
        "unit_price": unit,
        "matched": True,
        "price_column": chosen_col,
        "score": best_score,
        "detail": "ok",
    }
