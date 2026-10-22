"""Resolusi harga baris SO dari sheet List Harga Buyer (server-side, otoritatif)."""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.services.buyer_price_aliases import (
    canonical_price_block,
    emboss_is_special,
    extract_emboss_tokens,
    infer_price_block,
    customer_price_rules,
    is_outside_banten_factory,
    normalize_material_alias,
    split_material_and_thickness,
)
from app.services.buyer_price_import import list_to_api_dict
from app.services.buyer_price_period import select_buyer_price_list


def _norm(s: str | None) -> str:
    if s is None:
        return ""
    return re.sub(r"\s+", " ", str(s).strip().lower())


def _norm_alnum(s: str | None) -> str:
    raw = _norm(s)
    if not raw:
        return ""
    raw = raw.replace("&", " and ")
    raw = re.sub(r"[^a-z0-9.\-\s]", " ", raw)
    return re.sub(r"\s+", " ", raw).strip()


def _material_variants(material_name: str | None) -> list[str]:
    aliased = normalize_material_alias(material_name)
    base = _norm_alnum(aliased)
    if not base:
        return []
    out: set[str] = {base}
    raw = _norm_alnum(material_name)
    if raw:
        out.add(raw)
    # Hilangkan istilah umum yang sering membuat mismatch.
    stripped = re.sub(r"\b(map|leather|material|coated)\b", " ", base)
    stripped = re.sub(r"\s+", " ", stripped).strip()
    if stripped:
        out.add(stripped)
    # Buang suffix dalam kurung: "SPLIT SUEDE (MAP-SPLIT SUEDE)" -> "split suede".
    no_paren = re.sub(r"\(.*?\)", " ", base)
    no_paren = re.sub(r"\s+", " ", no_paren).strip()
    if no_paren:
        out.add(no_paren)
    return [x for x in out if x]


def _normalize_thickness_token(thickness_text: str | None) -> str:
    t = _norm_alnum(thickness_text)
    if not t:
        return ""
    t = re.sub(r"\bmm\b", "", t).strip()
    t = re.sub(r"\s*-\s*", "-", t)
    return t


def _thickness_variants(thickness_text: str | None) -> list[str]:
    t = _normalize_thickness_token(thickness_text)
    if not t:
        return []
    out: set[str] = {t}
    if "-" in t:
        parts = [p.strip() for p in t.split("-", 1)]
        if len(parts) == 2 and all(parts):
            out.add(f"{parts[0]} - {parts[1]}")
            out.add(f"{parts[0]}-{parts[1]} mm")
            out.add(f"{parts[0]} - {parts[1]} mm")
    return [x for x in out if x]


def _collect_price_keys(column_keys: list[str]) -> list[str]:
    std_price_labels = {
        "COLOR WHITE",
        "COLOR BLACK",
        "COLOR COLOR",
        "FLOURASENT",
        "METALIC",
        "EMBOSS",
        "SPESIAL EMBOSS",
    }
    out: list[str] = []
    for k in column_keys:
        if k is None:
            continue
        ks = str(k).strip()
        if re.search(r"price|harga", ks, re.I) or ks.upper() in std_price_labels:
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


def _row_block(row: dict[str, Any]) -> str:
    return canonical_price_block(row.get("COLOR"))


def _block_score(row_block: str, wanted: str) -> int:
    if not row_block:
        return 8
    if row_block == wanted:
        return 24
    fallbacks = {
        "OUTSIDE SPECIAL": ("SPECIAL", "OUTSIDE BANTEN", "COMMON"),
        "OUTSIDE BANTEN": ("COMMON",),
        "SPECIAL": ("COMMON",),
        "COMMON": (),
    }
    chain = fallbacks.get(wanted, ())
    if row_block in chain:
        return 6 if row_block == chain[0] else 2
    return 0


def _score_row(
    row: dict[str, Any],
    keys: list[str],
    price_key_set: set[str],
    *,
    material_name: str | None,
    color: str | None,
    style_article: str | None,
    thickness_text: str | None,
    emboss: str | None = None,
    wanted_block: str = "COMMON",
) -> int:
    row = dict(row)
    item_name, item_thick = split_material_and_thickness(row.get("ITEM"), row.get("THICKNESS"))
    row["ITEM"] = item_name
    if item_thick:
        row["THICKNESS"] = item_thick
    mat_variants = _material_variants(material_name)
    col = _norm_alnum(color)
    sty = _norm_alnum(style_article)
    th_variants = _thickness_variants(thickness_text)
    blob_parts: list[str] = []
    thick_cells: list[str] = []
    for k in keys:
        if k in price_key_set:
            continue
        cell = _norm_alnum(row.get(k))
        if not cell:
            continue
        blob_parts.append(cell)
        if re.search(r"thick|tebal|mm", str(k), re.I):
            thick_cells.append(cell)
    blob = " ".join(blob_parts)
    s = 0
    item_cell = _norm_alnum(row.get("ITEM") or row.get("item"))
    mat_exact = _norm_alnum(normalize_material_alias(material_name))
    if mat_exact and item_cell == mat_exact:
        s += 30
    if mat_variants:
        if any(m in blob for m in mat_variants):
            s += 12
        for part in blob_parts:
            if any(m in part or part in m for m in mat_variants):
                s += 6
                break
    if th_variants:
        matched_th = False
        if thick_cells:
            matched_th = any(tv in c or c in tv for tv in th_variants for c in thick_cells)
        else:
            matched_th = any(tv in blob for tv in th_variants)
        if matched_th:
            s += 10
    if sty and sty in blob:
        s += 5
    if col and col in blob:
        s += 4
    emboss_tokens = extract_emboss_tokens(emboss)
    if emboss_tokens:
        blob_tokens = extract_emboss_tokens(blob)
        if emboss_tokens & blob_tokens:
            s += 16
        elif emboss_is_special(emboss) and _row_block(row) in {"SPECIAL", "OUTSIDE SPECIAL"}:
            s += 4
    s += _block_score(_row_block(row), wanted_block)
    return s


def _optional_text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    return text or None


def _price_source(lst: Any | None, price_block: str | None) -> dict[str, Any]:
    """Keterangan list dan blok. Bukan bagian harga yang disimpan di baris SO."""
    start = getattr(lst, "period_start", None) if lst is not None else None
    end = getattr(lst, "period_end", None) if lst is not None else None
    title = None
    if lst is not None:
        title = _optional_text(getattr(lst, "title", None)) or _optional_text(
            getattr(lst, "period_label", None)
        )
    return {
        "list_title": title,
        "period_start": start if isinstance(start, date) else None,
        "period_end": end if isinstance(end, date) else None,
        "price_block": price_block,
    }


def _apply_customer_modifier(unit: Decimal, rule: dict, *, subtract: bool) -> tuple[Decimal, Decimal]:
    """Amount ditambah atau dikurangi. Persen dihitung dari harga saat ini."""
    kind = rule.get("type")
    value = Decimal(str(rule.get("value")))
    if kind == "percent":
        if value < -100 or value > 100:
            return unit, Decimal(0)
        delta = (unit * value / Decimal(100)).quantize(Decimal("0.0001"))
    else:
        delta = value.quantize(Decimal("0.0001"))
    if subtract:
        delta = -delta
    return (unit + delta).quantize(Decimal("0.0001")), delta


def resolve_unit_price_for_buyer(
    db: Session,
    buyer_code: str,
    *,
    material_name: Optional[str] = None,
    color: Optional[str] = None,
    style_article: Optional[str] = None,
    thickness_text: Optional[str] = None,
    color_family: Optional[str] = None,
    emboss: Optional[str] = None,
    factory_code: Optional[str] = None,
    as_of: Optional[date] = None,
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

    when = as_of or date.today()
    lst = select_buyer_price_list(db, code, when)
    if not lst:
        return {
            "unit_price": None,
            "matched": False,
            "price_column": None,
            "score": 0,
            "detail": f"List harga untuk buyer '{code}' pada tanggal {when.isoformat()} tidak ditemukan",
        }

    sheet = list_to_api_dict(db, lst.id)
    rows: list[dict[str, Any]] = sheet.get("rows") or []
    meta: dict[str, Any] = sheet.get("meta_json") or {}
    keys: list[str] = list(meta.get("column_keys") or [])
    if not keys and rows:
        keys = list(rows[0].keys())

    outside = is_outside_banten_factory(db, factory_code)
    wanted_block = infer_price_block(emboss=emboss, outside_banten=outside)
    source = _price_source(lst, wanted_block)

    price_keys = _collect_price_keys(keys)
    pk_set = set(price_keys)
    if not price_keys:
        return {
            "unit_price": None,
            "matched": False,
            "price_column": None,
            "score": 0,
            "detail": "Kolom harga tidak ditemukan di list buyer - import data gagal atau kolom tidak terdefinisi",
            **source,
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
            emboss=emboss,
            wanted_block=wanted_block,
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
            **source,
        }

    normalized_keys = {str(k).strip().upper(): str(k).strip() for k in keys}
    base_key = normalized_keys.get("COLOR WHITE")
    add_black_key = normalized_keys.get("COLOR BLACK")
    add_color_key = normalized_keys.get("COLOR COLOR")
    add_fluor_key = normalized_keys.get("FLOURASENT")
    add_metalic_key = normalized_keys.get("METALIC")
    add_emboss_key = normalized_keys.get("EMBOSS")
    add_special_emboss_key = normalized_keys.get("SPESIAL EMBOSS")

    unit: Decimal | None = None
    chosen_col = price_col
    color_text = _norm(color)
    base_price: Decimal | None = None
    addons: list[dict[str, Any]] = []

    def _apply_addon(total: Decimal, key: str, label: str, cell_key: str | None) -> Decimal:
        if not cell_key:
            return total
        amount = _parse_price_cell(best_row.get(cell_key)) or Decimal("0")
        addons.append({"key": key, "label": label, "amount": amount})
        return total + amount

    # New pricing matrix: COLOR WHITE is base; other columns are additive toppings.
    if base_key and best_row.get(base_key) not in (None, ""):
        base = _parse_price_cell(best_row.get(base_key))
        if base is not None:
            add_total = Decimal("0")
            cf = (color_family or "").strip().lower()
            if cf == "black":
                add_total = _apply_addon(add_total, "COLOR BLACK", "+ COLOR BLACK", add_black_key)
            if cf == "color":
                add_total = _apply_addon(add_total, "COLOR COLOR", "+ COLOR", add_color_key)
            if cf == "fluorescent":
                add_total = _apply_addon(add_total, "FLOURASENT", "FLOURASENT", add_fluor_key)
            if "metalic" in color_text or "metallic" in color_text:
                add_total = _apply_addon(add_total, "METALIC", "METALIC", add_metalic_key)
            if "spesial emboss" in color_text or "special emboss" in color_text:
                add_total = _apply_addon(add_total, "SPESIAL EMBOSS", "SPESIAL EMBOSS", add_special_emboss_key)
            elif "emboss" in color_text:
                add_total = _apply_addon(add_total, "EMBOSS", "EMBOSS", add_emboss_key)
            unit = base + add_total
            base_price = base
            chosen_col = "COLOR WHITE (+addons)"

    if unit is None:
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
            **source,
        }

    rules = customer_price_rules(db, factory_code)
    outside = rules.get("outside")
    if outside:
        unit, delta = _apply_customer_modifier(unit, outside, subtract=False)
        if delta:
            addons.append({"key": "OUTSIDE ADJUST", "label": "+ OUTSIDE", "amount": delta})
    discount = rules.get("discount")
    if discount:
        unit, delta = _apply_customer_modifier(unit, discount, subtract=True)
        if delta:
            addons.append({"key": "DISCOUNT MODIFIER", "label": "- DISKON", "amount": delta})

    return {
        "unit_price": unit,
        "base_price": base_price,
        "addons": addons,
        "matched": True,
        "price_column": chosen_col,
        "score": best_score,
        "detail": "ok",
        **source,
    }
