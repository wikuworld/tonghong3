"""Alias nama material / kode customer + token emboss special untuk resolve harga."""

from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Customer

# File Excel vs nama master — jangan rewrite master_items.
MATERIAL_NAME_ALIASES = {
    "LACCATTO PATENT LEATHER": "LACCATO PATENT LEATHER",
    "LACCATTO PATENT LEATHER - EPM 5": "LACCATO PATENT LEATHER",
    "LACCATO PATENT LEATHER - EPM 5": "LACCATO PATENT LEATHER",
    "METAL LEATHER - PATENT": "METAL LEATHER-PATENT",
    "METAL LEATHER PATENT": "METAL LEATHER-PATENT",
    "PRINCESS LEATHER": "PRINCESS LEATHER",
    "(OIA) VIRGIN PU": "VIRGIN HYDRO PU",
    "VIRGIN PU": "VIRGIN HYDRO PU",
    "(PM) GENERIC PU COATED": "(PM) GENERIC PU COATED LEATHER",
}

NIKE_PRICE_BLOCKS = frozenset(
    {
        "COMMON",
        "SPECIAL",
        "OUTSIDE BANTEN",
        "OUTSIDE SPECIAL",
    }
)

_THICKNESS_RANGE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)")

# Kode di quotation vs kode ERP. AF001 belum ada master — tetap dinormalisasi.
CUSTOMER_CODE_ALIASES = {
    "HW035": "HW036",
    "HI-001": "HA001",
    "HI001": "HA001",
}

# Kode pabrik/customer di luar Banten (harga Nike Outside).
OUTSIDE_BANTEN_FACTORY_CODES = frozenset(
    {
        "BI020",  # Bintang Indokarya — Tegal
        "AF001",  # Aroma — Cirebon
    }
)

BANTEN_PROVINCE_CODE = "36"

SPECIAL_EMBOSS_TOKENS = frozenset(
    {
        "AR-140",
        "AR-169",
        "AR-172",
        "AR-176",
        "AR-185",
        "AR-20",
        "AR-216",
        "AR-80",
        "R-131",
        "R-231",
        "R-262",
        "R-102",
    }
)

_EMBOSS_TOKEN_RE = re.compile(r"\b([A-Z]{1,4}-?\d+[A-Z]?)\b", re.I)


def canonical_customer_code(code: str | None) -> str:
    raw = (code or "").strip().upper()
    if not raw:
        return ""
    return CUSTOMER_CODE_ALIASES.get(raw, raw)


def normalize_material_alias(name: str | None) -> str:
    raw = re.sub(r"^['\"]+", "", str(name or "").strip())
    raw = re.sub(r"\s+", " ", raw).strip()
    key = raw.upper()
    aliased = MATERIAL_NAME_ALIASES.get(key)
    return aliased or raw


def canonical_price_block(value: str | None) -> str:
    """Blok harga Nike. Warna produk dan teks lain dihitung sebagai blok kosong."""
    raw = re.sub(r"\s+", " ", str(value or "").strip()).upper()
    if raw in NIKE_PRICE_BLOCKS:
        return raw
    return ""


def split_material_and_thickness(name: str | None, thickness: str | None = "") -> tuple[str, str]:
    """Pisahkan rentang ketebalan dari nama item, lalu samakan nama ke alias SO."""
    raw = re.sub(r"\s+", " ", str(name or "").strip())
    thick = re.sub(r"\s+", "", str(thickness or "").strip())
    thick = re.sub(r"(?i)mm$", "", thick).strip()
    range_match = _THICKNESS_RANGE_RE.search(raw)
    if range_match:
        span = f"{range_match.group(1)}-{range_match.group(2)}"
        lead = range_match.group(1)
        if not thick or thick == lead or thick == span:
            thick = span
        raw = f"{raw[: range_match.start()]} {raw[range_match.end() :]}"
        raw = re.sub(r"\s+", " ", raw).strip(" -")
        raw = re.sub(r"(?i)\s*mm$", "", raw).strip(" -")
    elif thick:
        raw = re.sub(
            rf"(?i)(?:\s+{re.escape(thick)})(?:\s*mm)?\s*$",
            "",
            raw,
        ).strip()
    return normalize_material_alias(raw), thick


def normalize_sheet_cells(cells: dict | None) -> dict:
    """Rapikan satu baris sheet: nama material, rentang ketebalan, dan blok COLOR."""
    src = dict(cells or {})
    item, thick = split_material_and_thickness(src.get("ITEM"), src.get("THICKNESS"))
    src["ITEM"] = item
    src["THICKNESS"] = thick
    src["COLOR"] = canonical_price_block(src.get("COLOR"))
    return src


def extract_emboss_tokens(text: str | None) -> set[str]:
    out: set[str] = set()
    for m in _EMBOSS_TOKEN_RE.finditer(str(text or "").upper()):
        tok = m.group(1).upper()
        if not tok:
            continue
        if "-" not in tok and re.match(r"^[A-Z]+\d+", tok):
            tok = re.sub(r"^([A-Z]+)(\d)", r"\1-\2", tok)
        out.add(tok)
    return out


def emboss_is_special(emboss: str | None) -> bool:
    tokens = extract_emboss_tokens(emboss)
    return bool(tokens & SPECIAL_EMBOSS_TOKENS)


def is_outside_banten_factory(
    db: Session | None,
    factory_code: str | None,
) -> bool:
    code = canonical_customer_code(factory_code)
    if not code:
        return False
    if code in OUTSIDE_BANTEN_FACTORY_CODES:
        return True
    if db is None:
        return False
    row = db.scalars(select(Customer).where(Customer.code == code)).first()
    if not row:
        return False
    prov = str(row.wilayah_province_code or "").strip()
    if prov and prov != BANTEN_PROVINCE_CODE:
        return True
    blob = " ".join(
        str(x or "")
        for x in (row.city, row.address, row.billing_address)
    ).upper()
    if "BANTEN" in blob or "CIKANDE" in blob or "SERANG" in blob:
        return False
    return any(k in blob for k in ("CIREBON", "TEGAL", "JAWA TENGAH", "JAWA TIMUR"))


def infer_price_block(*, emboss: str | None, outside_banten: bool) -> str:
    special = emboss_is_special(emboss)
    if outside_banten:
        return "OUTSIDE SPECIAL" if special else "OUTSIDE BANTEN"
    return "SPECIAL" if special else "COMMON"
