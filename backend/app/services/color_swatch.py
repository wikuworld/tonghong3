"""Import & normalisasi master color swatch (CSV legacy)."""

from __future__ import annotations

import csv
import io
import re
from datetime import date, datetime
from typing import Any, BinaryIO, TextIO

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Brand, ColorSwatchRecipe, Customer

# Buyer valid di sheet harga — selain ini di CSV diabaikan untuk buyer_code
_VALID_BUYERS = frozenset(
    {"NIKE", "ADIDAS", "NB", "UA", "PUMA", "REEBOK", "GLOBAL", "OIA", "OIA NIKE"}
)


def normalize_factory_key(raw: str | None) -> str:
    return re.sub(r"\s+", " ", (raw or "").strip()).upper()


def _compact_alnum(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (value or "").upper())


def _strip_company_prefix(name: str) -> str:
    return re.sub(
        r"^(PT\.?|CV\.?|TBK\.?|PD\.?|CO\.?|LTD\.?)\s+",
        "",
        (name or "").upper(),
        flags=re.IGNORECASE,
    ).strip()


def resolve_swatch_factory_keys(
    db: Session,
    *,
    factory_hint: str | None,
    customer_id: int | None = None,
) -> list[str]:
    """
    Kandidat factory_key untuk lookup swatch.
    Memetakan KODE SYSTEM (mis. CS004) ke nama pabrik di CSV (mis. CHANGSHIN) via customer.
    """
    hint = normalize_factory_key(factory_hint)
    out: list[str] = []
    seen: set[str] = set()

    def add(key: str | None) -> None:
        if not key:
            return
        k = normalize_factory_key(key)
        if k and k not in seen:
            seen.add(k)
            out.append(k)

    if hint:
        exact = db.scalar(
            select(ColorSwatchRecipe.factory_key)
            .where(
                ColorSwatchRecipe.is_active.is_(True),
                ColorSwatchRecipe.factory_key == hint,
            )
            .limit(1)
        )
        if exact:
            add(exact)
            return out

    customer = db.get(Customer, customer_id) if customer_id else None
    if customer is None and hint:
        customer = db.scalars(select(Customer).where(Customer.code.ilike(hint)).limit(1)).first()

    if customer and (customer.name or "").strip():
        name_upper = _strip_company_prefix(customer.name or "")
        name_compact = _compact_alnum(name_upper)
        recipe_keys = list(
            db.scalars(
                select(ColorSwatchRecipe.factory_key)
                .where(ColorSwatchRecipe.is_active.is_(True))
                .distinct()
            ).all()
        )
        best_key: str | None = None
        best_score = 0
        for rk in recipe_keys:
            if not rk:
                continue
            rk_norm = normalize_factory_key(rk)
            rk_compact = _compact_alnum(rk_norm)
            if len(rk_compact) < 4:
                continue
            score = 0
            if rk_compact in name_compact:
                score = len(rk_compact) + 20
            elif rk_norm in name_upper:
                score = len(rk_compact) + 10
            if score > best_score:
                best_score = score
                best_key = rk_norm
        if best_key and best_score >= 10:
            add(best_key)

        words = [w for w in re.split(r"[\s.,()/]+", name_upper) if len(w) >= 3]
        if words:
            for candidate in (
                _compact_alnum("".join(words[:2])),
                _compact_alnum(words[0]),
                _compact_alnum("".join(words[:3])),
            ):
                if len(candidate) < 4:
                    continue
                for rk in recipe_keys:
                    if _compact_alnum(normalize_factory_key(rk)) == candidate:
                        add(rk)
                        break

    if hint:
        add(hint)
    return out


def normalize_buyer_code(raw: str | None) -> str:
    b = (raw or "").strip().upper()
    if b in {"WHITE", "BLACK", "GREY", "GRAY", "PINK", "YELLOW", "RED", "BLUE", "3MR", "3GU", "4AU"}:
        return ""
    return b


def parse_entered_date(raw: str | None) -> date | None:
    if not raw or not str(raw).strip():
        return None
    s = str(raw).strip()
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(s[:10] if len(s) > 10 else s, fmt).date()
        except ValueError:
            continue
    return None


def parse_csv_row(row: dict[str, str], source_file: str) -> dict[str, Any] | None:
    """Parse satu baris dictreader ke field recipe; None jika baris kosong."""
    code = (row.get("COLOR CODE") or row.get("color code") or "").strip()
    name = (row.get("COLOR NAME ") or row.get("COLOR NAME") or row.get("color name") or "").strip()
    if not code and not name:
        return None
    factory = normalize_factory_key(row.get("CUSTOMER") or row.get("customer"))
    buyer = normalize_buyer_code(row.get("BRAND") or row.get("brand"))
    if not factory or not buyer:
        return None
    if buyer not in _VALID_BUYERS:
        return None
    material = (row.get("MATERIAL") or row.get("material") or "").strip()
    if not material:
        return None
    return {
        "factory_key": factory,
        "buyer_code": buyer,
        "color_code": code,
        "color_name": name or code,
        "emboss": (row.get("EMBOS") or row.get("emboss") or "").strip(),
        "color_standard": (row.get("COLOR SWATCH") or row.get("color swatch") or "").strip() or None,
        "backing": (row.get("BACKING") or row.get("backing") or "").strip() or None,
        "material_name": material,
        "legacy_urut": (row.get("NO URUT") or row.get("no urut") or "").strip() or None,
        "entered_at": parse_entered_date(row.get("TGGL MASUK") or row.get("tggl masuk")),
        "source_file": source_file,
    }


def iter_csv_recipes(stream: TextIO | BinaryIO, source_file: str) -> list[dict[str, Any]]:
    if hasattr(stream, "read"):
        text = stream.read()
        if isinstance(text, bytes):
            text = text.decode("utf-8-sig", errors="replace")
    else:
        text = str(stream)
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    out: list[dict[str, Any]] = []
    for row in reader:
        parsed = parse_csv_row(row, source_file)
        if parsed:
            out.append(parsed)
    return out


def _resolve_customer_id(db: Session, factory_key: str) -> int | None:
    fk = normalize_factory_key(factory_key)
    if not fk:
        return None
    cust = db.scalars(select(Customer).where(Customer.code.ilike(fk)).limit(1)).first()
    if cust:
        return int(cust.id)
    cust = db.scalars(select(Customer).where(Customer.name.ilike(fk)).limit(1)).first()
    if cust:
        return int(cust.id)
    like = f"%{fk}%"
    cust = db.scalars(select(Customer).where(Customer.name.ilike(like)).limit(1)).first()
    if cust:
        return int(cust.id)
    fk_compact = _compact_alnum(fk)
    if len(fk_compact) < 4:
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


def _resolve_brand_id(db: Session, buyer_code: str) -> int | None:
    b = buyer_code.strip().upper()
    brand = db.scalars(
        select(Brand).where((Brand.code.ilike(b)) | (Brand.name.ilike(b))).limit(1)
    ).first()
    return int(brand.id) if brand else None


def import_recipes(
    db: Session,
    recipes: list[dict[str, Any]],
    *,
    replace_inactive: bool = False,
) -> dict[str, int]:
    """Upsert recipes. Returns counts inserted, updated, skipped."""
    inserted = 0
    updated = 0
    skipped = 0
    deactivated = 0
    imported_keys: set[tuple[str, str, str, str, str]] = set()
    customer_cache: dict[str, int | None] = {}
    brand_cache: dict[str, int | None] = {}

    for data in recipes:
        fk = data["factory_key"]
        buyer = data["buyer_code"]
        imported_keys.add(
            (fk, buyer, data["color_code"], data["material_name"], data["emboss"])
        )
        if fk not in customer_cache:
            customer_cache[fk] = _resolve_customer_id(db, fk)
        if buyer not in brand_cache:
            brand_cache[buyer] = _resolve_brand_id(db, buyer)

        existing = db.scalars(
            select(ColorSwatchRecipe).where(
                ColorSwatchRecipe.factory_key == fk,
                ColorSwatchRecipe.buyer_code == buyer,
                ColorSwatchRecipe.color_code == data["color_code"],
                ColorSwatchRecipe.material_name == data["material_name"],
                ColorSwatchRecipe.emboss == data["emboss"],
            )
        ).first()

        if existing:
            existing.color_name = data["color_name"]
            existing.color_standard = data.get("color_standard")
            existing.backing = data.get("backing")
            existing.legacy_urut = data.get("legacy_urut")
            existing.entered_at = data.get("entered_at")
            existing.source_file = data.get("source_file")
            existing.customer_id = customer_cache[fk]
            existing.brand_id = brand_cache[buyer]
            existing.is_active = True
            existing.updated_at = datetime.utcnow()
            updated += 1
            db.flush()
        else:
            db.add(
                ColorSwatchRecipe(
                    factory_key=fk,
                    buyer_code=buyer,
                    color_code=data["color_code"],
                    color_name=data["color_name"],
                    emboss=data["emboss"],
                    color_standard=data.get("color_standard"),
                    backing=data.get("backing"),
                    material_name=data["material_name"],
                    legacy_urut=data.get("legacy_urut"),
                    entered_at=data.get("entered_at"),
                    source_file=data.get("source_file"),
                    customer_id=customer_cache[fk],
                    brand_id=brand_cache[buyer],
                    is_active=True,
                )
            )
            inserted += 1
            db.flush()

    if replace_inactive and imported_keys:
        touched_pairs = {(d["factory_key"], d["buyer_code"]) for d in recipes}
        for fk, buyer in touched_pairs:
            rows = db.scalars(
                select(ColorSwatchRecipe).where(
                    ColorSwatchRecipe.factory_key == fk,
                    ColorSwatchRecipe.buyer_code == buyer,
                    ColorSwatchRecipe.is_active.is_(True),
                )
            ).all()
            for recipe in rows:
                rk = (
                    recipe.factory_key,
                    recipe.buyer_code,
                    recipe.color_code,
                    recipe.material_name,
                    recipe.emboss,
                )
                if rk not in imported_keys:
                    recipe.is_active = False
                    recipe.updated_at = datetime.utcnow()
                    deactivated += 1

    db.commit()
    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "deactivated": deactivated,
        "total": len(recipes),
    }


def recipe_to_po_fill(recipe: ColorSwatchRecipe) -> dict[str, Any]:
    """Payload untuk mengisi baris PO dari satu resep swatch."""
    return {
        "color": recipe.color_name,
        "color_reference": recipe.color_code or None,
        "color_standard": recipe.color_standard,
        "emboss": recipe.emboss,
        "backing": recipe.backing,
        "material_name": recipe.material_name,
        "thi_line_ref": recipe.legacy_urut,
        "color_swatch_recipe_id": recipe.id,
    }
