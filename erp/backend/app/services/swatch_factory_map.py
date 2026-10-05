"""Pemetaan factory_key color swatch → customer (kode pabrik ERP)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ColorSwatchRecipe, Customer
from app.services.color_swatch import (
    _compact_alnum,
    _strip_company_prefix,
    normalize_factory_key,
)

_COLOR_STD_CUSTOMER_RE = re.compile(r"^T[MS]([A-Z]{2}\d{3})", re.IGNORECASE)

# Kode tertanam di color_standard yang sudah tidak ada / typo di master customer
CUSTOMER_CODE_ALIASES: dict[str, str] = {
    "SD046": "SD047",
    "HW035": "HW036",
    "VF004": "VF050",
    "PY021": "PY028",
    "PG028": "PG021",
    "SC043": "SL043",
    "NS043": "NS016",
}

# Default factory_key CSV → kode customer (jika color_standard tidak punya petunjuk)
DEFAULT_FACTORY_CUSTOMER_CODE: dict[str, str] = {
    "ADIS": "AD002",
    "BIG": "BI020",
    "CHANGSHIN": "CS004",
    "CHANGSHIN RJ": "CS005",
    "CHANGSHIN INC": "CS006",
    "CHINGLUH": "CL017",
    "VICTORY/CHINGLUH": "VC005",
    "VICTORY": "VC005",
    "VICTORY FOOTWEAR": "VF050",
    "VICTORY/SCI": "VC005",
    "FENGTAY": "FT006",
    "FENGTAY (WEST)": "FT006",
    "FENGTAY WEST": "FT006",
    "FENGTAY (EAST)": "FT007",
    "FENGTAY EAST": "FT007",
    "FENGTAY (NORTH)": "FT008",
    "FENGTAY TW": "FT038",
    "NIKOMAS": "NS016",
    "NIKOMAS IY": "NS020",
    "POUYUEN": "PY028",
    "PCN G8": "PG021",
    "POUYUEN/SHOETOWN/PCN": "PG021",
    "PANARUB": "PA020",
    "METRO NB": "MP033",
    "METRO": "MP033",
    "ULTIMATE NOBLE": "MP034",
    "TAEKWANG": "TK027",
    "TAEKWANG KR": "TK028",
    "LONGRICH": "LR027",
    "LONGRICH UA": "LR026",
    "LONGRICH/YMUV": "LR026",
    "YMUV": "YC027",
    "DEANSHOES": "DS026",
    "DEANSHOES (UA)": "DS026",
    "KMK": "KM001",
    "PRATAMA": "PT012",
    "PRATAMA JX": "PT013",
    "PRATAMA JX 2": "PT015",
    "SHOETOWN": "SL043",
    "SHOETOWN CINA": "SL044",
    "SHOETOWN MUSTIKA": "SL045",
    "WEALTH VAST CO. LTD": "SL044",
    "PARKLAND": "PA009",
    "PARKLAND 1": "PA009",
    "PARKLAND 2": "PW010",
    "PARKLAND 3": "PA010",
    "PWI 2": "PW010",
    "GLOSTAR": "GS007",
    "GLOSTAR (ADS)": "GS009",
    "GLOSTAR (NB)": "PGS30",
    "HORNMING": "HI024",
    "HWASEUNG": "HW036",
    "HWASEUNG (HWP)": "HW036",
    "HWASEUNG HWP": "HW036",
    "SAI": "SD047",
    "SENGDAM": "SD048",
    "SENGDAM/SAI": "SD048",
    "SCI": "SC006",
    "SELALU CINTA INDONESIA": "SC006",
    "SMJ": "PT014",
    "SFI": "PW020",
    "SHT": "SH001",
    "SHYANG HUNG TAH": "SH001",
    "TAH SUNG HUNG": "TS001",
    "TAH SHUNG HUNG": "TS001",
    "TSH": "TS001",
    "DIAMOND": "DI024",
    "DIAMOND INTERNATIONAL": "DI024",
    "DPS": "DW001",
    "DWI PRIMA SENTOSA": "DW001",
    "YOUNG TREE": "YT001",
    "YOUNG TREE SOLO": "YT002",
    "VFI": "VF050",
}

# Normalisasi alias factory_key ke bentuk kanonik (CSV legacy)
CANONICAL_FACTORY_KEYS: dict[str, str] = {
    "FENGTAY WEST": "FENGTAY (WEST)",
    "FENGTAY EAST": "FENGTAY (EAST)",
    "TAH SHUNG HUNG": "TAH SUNG HUNG",
    "SHYANG HUNG TAH": "SHT",
    "HWASEUNG HWP": "HWASEUNG (HWP)",
    "SELALU CINTA INDONESIA": "SCI",
}


def extract_customer_code_from_color_standard(color_standard: str | None) -> str | None:
    if not color_standard or not str(color_standard).strip():
        return None
    m = _COLOR_STD_CUSTOMER_RE.match(str(color_standard).strip().upper())
    if not m:
        return None
    code = m.group(1).upper()
    return CUSTOMER_CODE_ALIASES.get(code, code)


def resolve_customer_code_for_swatch(
    factory_key: str | None,
    *,
    color_standard: str | None = None,
) -> str | None:
    """Tentukan kode customer ERP untuk satu baris swatch."""
    from_std = extract_customer_code_from_color_standard(color_standard)
    if from_std:
        return from_std

    fk = normalize_factory_key(factory_key)
    if not fk:
        return None

    if fk in DEFAULT_FACTORY_CUSTOMER_CODE:
        return DEFAULT_FACTORY_CUSTOMER_CODE[fk]

    # factory_key sama persis dengan kode customer (mis. AD002)
    if re.fullmatch(r"[A-Z]{2}\d{3}", fk):
        return fk

    return None


def _fuzzy_customer_id(db: Session, factory_key: str) -> int | None:
    fk = normalize_factory_key(factory_key)
    fk_compact = _compact_alnum(fk)
    if len(fk_compact) < 3:
        return None
    best: Customer | None = None
    best_score = 0
    for c in db.scalars(select(Customer).where(Customer.is_active.is_(True))).all():
        name_compact = _compact_alnum(_strip_company_prefix(c.name or ""))
        code_compact = _compact_alnum(c.code or "")
        score = 0
        if fk_compact == code_compact and code_compact:
            return int(c.id)
        if fk_compact in name_compact:
            score = len(fk_compact) + 10
        elif name_compact and name_compact in fk_compact:
            score = len(name_compact)
        if score > best_score:
            best_score = score
            best = c
    return int(best.id) if best and best_score >= 8 else None


def resolve_swatch_customer_id(
    db: Session,
    factory_key: str | None,
    *,
    color_standard: str | None = None,
) -> int | None:
    code = resolve_customer_code_for_swatch(factory_key, color_standard=color_standard)
    if code:
        cust = db.scalars(select(Customer).where(Customer.code.ilike(code)).limit(1)).first()
        if cust:
            return int(cust.id)
    if factory_key:
        return _fuzzy_customer_id(db, factory_key)
    return None


def _recipe_unique_key(row: ColorSwatchRecipe) -> tuple[str, str, str, str, str]:
    return (
        row.factory_key,
        row.buyer_code,
        row.color_code,
        row.material_name,
        row.emboss,
    )


@dataclass
class SwatchFactoryNormalizeResult:
    total: int = 0
    customer_linked: int = 0
    customer_unchanged: int = 0
    customer_unresolved: int = 0
    factory_key_renamed: int = 0
    factory_key_skipped_conflict: int = 0


def normalize_color_swatch_factory_links(
    db: Session,
    *,
    normalize_factory_keys: bool = True,
    dry_run: bool = False,
) -> SwatchFactoryNormalizeResult:
    """
    Sinkronkan customer_id & opsional normalisasi factory_key semua resep swatch.
    """
    result = SwatchFactoryNormalizeResult()
    rows = list(db.scalars(select(ColorSwatchRecipe)).all())
    result.total = len(rows)
    existing_keys = {_recipe_unique_key(r) for r in rows}

    for row in rows:
        target_customer_id = resolve_swatch_customer_id(
            db,
            row.factory_key,
            color_standard=row.color_standard,
        )
        if target_customer_id:
            if row.customer_id != target_customer_id:
                result.customer_linked += 1
                if not dry_run:
                    row.customer_id = target_customer_id
            else:
                result.customer_unchanged += 1
        else:
            result.customer_unresolved += 1

        if not normalize_factory_keys:
            continue

        canonical = CANONICAL_FACTORY_KEYS.get(normalize_factory_key(row.factory_key))
        if not canonical or canonical == row.factory_key:
            continue

        new_key = (
            row.factory_key,
            row.buyer_code,
            row.color_code,
            row.material_name,
            row.emboss,
        )
        candidate = (
            canonical,
            row.buyer_code,
            row.color_code,
            row.material_name,
            row.emboss,
        )
        if candidate in existing_keys and candidate != new_key:
            result.factory_key_skipped_conflict += 1
            continue

        if not dry_run:
            existing_keys.discard(new_key)
            row.factory_key = canonical
            existing_keys.add(candidate)
        result.factory_key_renamed += 1

    if not dry_run:
        db.commit()
    return result


def summarize_swatch_factory_coverage(db: Session) -> dict[str, Any]:
    rows = list(db.scalars(select(ColorSwatchRecipe).where(ColorSwatchRecipe.is_active.is_(True))).all())
    unresolved_fk: dict[str, int] = {}
    for row in rows:
        if row.customer_id:
            continue
        fk = row.factory_key
        unresolved_fk[fk] = unresolved_fk.get(fk, 0) + 1
    return {
        "active_total": len(rows),
        "with_customer_id": sum(1 for r in rows if r.customer_id),
        "without_customer_id": sum(1 for r in rows if not r.customer_id),
        "unresolved_by_factory_key": unresolved_fk,
    }
