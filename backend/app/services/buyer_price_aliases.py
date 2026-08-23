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
}

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
