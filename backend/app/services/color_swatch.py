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
from app.timeutil import app_now

# Buyer valid di sheet harga — selain ini di CSV diabaikan untuk buyer_code
_VALID_BUYERS = frozenset(
    {"NIKE", "ADIDAS", "NB", "UA", "PUMA", "REEBOK", "GLOBAL", "OIA", "OIA NIKE"}
)


def normalize_factory_key(raw: str | None) -> str:
    return re.sub(r"\s+", " ", (raw or "").strip()).upper()


_PAREN_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")
_PM_PREFIX_RE = re.compile(r"^\(PM\)\s*", re.IGNORECASE)
_EMBOSS_CODE_RE = re.compile(r"^([A-Z]{1,4}-\d+[A-Z]?)", re.IGNORECASE)
_MATERIAL_TRIM_SUFFIXES = (
    " coated leather",
    " coated",
    " leather",
    " split suede",
)


def normalize_swatch_color_name(text: str | None) -> str:
    """WOLF GREY (01V) → wolf grey"""
    s = re.sub(r"\s+", " ", (text or "").strip())
    s = _PAREN_SUFFIX_RE.sub("", s).strip()
    return s.lower()


def _extract_emboss_code_token(token: str) -> str | None:
    raw = (token or "").strip().upper()
    if not raw:
        return None
    m = _EMBOSS_CODE_RE.match(raw)
    if m:
        return m.group(1).upper()
    compact = re.sub(r"\s+", "", raw)
    m2 = _EMBOSS_CODE_RE.match(compact)
    return m2.group(1).upper() if m2 else None


def swatch_emboss_code(text: str | None) -> str:
    """AR-167 DM / R-8 M / UM-34T → kode dasar emboss (finish SM/M/DM diabaikan)."""
    s = re.sub(r"\s+", " ", (text or "").strip())
    s = _PAREN_SUFFIX_RE.sub("", s).strip()
    if not s:
        return ""
    for token in s.split():
        code = _extract_emboss_code_token(token)
        if code:
            return code
    code = _extract_emboss_code_token(s)
    return code or s.split()[0].upper()


def swatch_colors_match(a: str | None, b: str | None) -> bool:
    na = normalize_swatch_color_name(a)
    nb = normalize_swatch_color_name(b)
    if not na or not nb:
        return False
    return na == nb or na.startswith(nb) or nb.startswith(na)


def swatch_emboss_match(a: str | None, b: str | None) -> bool:
    ca = swatch_emboss_code(a)
    cb = swatch_emboss_code(b)
    if not ca or not cb:
        return False
    if ca == cb:
        return True
    # R-8M vs R-8, UM-34T vs UM-34 (jarang, tapi tetap longgar)
    return ca.startswith(cb) or cb.startswith(ca)


def normalize_swatch_material_name(text: str | None) -> str:
    """(PM) GENERIC PU COATED LEATHER → generic pu"""
    s = _PM_PREFIX_RE.sub("", (text or "").strip())
    s = re.sub(r"\s+", " ", s).strip().lower()
    for suffix in _MATERIAL_TRIM_SUFFIXES:
        if s.endswith(suffix):
            s = s[: -len(suffix)].strip()
    return s


def swatch_materials_match(a: str | None, b: str | None) -> bool:
    na = normalize_swatch_material_name(a)
    nb = normalize_swatch_material_name(b)
    if not na or not nb:
        return True
    return na == nb or na in nb or nb in na


def filter_swatch_recipes_by_dimensions(
    rows: list[ColorSwatchRecipe],
    *,
    material_name: str | None = None,
    color_name: str | None = None,
    emboss: str | None = None,
    db: Session | None = None,
) -> list[ColorSwatchRecipe]:
    """Filter resep setelah query DB — toleran suffix master item (warna/emboss)."""
    from app.services.material_aliases import resolve_canonical_material_name

    want_mat = resolve_canonical_material_name(db, material_name) if db else material_name
    out: list[ColorSwatchRecipe] = []
    for row in rows:
        row_mat = (
            resolve_canonical_material_name(db, row.material_name) if db else row.material_name
        )
        if want_mat and not swatch_materials_match(row_mat, want_mat):
            continue
        if color_name and not swatch_colors_match(row.color_name, color_name):
            continue
        if emboss and not swatch_emboss_match(row.emboss, emboss):
            continue
        out.append(row)
    return out


def _compact_alnum(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", (value or "").upper())


def _strip_company_prefix(name: str) -> str:
    return re.sub(
        r"^(PT\.?|CV\.?|TBK\.?|PD\.?|CO\.?|LTD\.?)\s+",
        "",
        (name or "").upper(),
        flags=re.IGNORECASE,
    ).strip()


def _customer_factory_tags(name_upper: str) -> list[str]:
    tags: list[str] = []
    for tag in ("WEST", "EAST", "NORTH", "SOUTH"):
        if tag in name_upper:
            tags.append(tag)
    if "REKSA JAYA" in name_upper:
        tags.append("RJ")
    if re.search(r"\bUA\b", name_upper) or name_upper.rstrip().endswith("-UA"):
        tags.append("UA")
    return tags


def _factory_key_match_score(
    rk_norm: str,
    *,
    name_upper: str,
    name_compact: str,
    hint: str,
    tags: list[str],
) -> int:
    rk_compact = _compact_alnum(rk_norm)
    if len(rk_compact) < 3:
        return 0
    score = 0
    if hint and rk_norm == hint:
        score += 100
    if rk_compact in name_compact:
        score += len(rk_compact) + 20
    elif rk_norm in name_upper:
        score += len(rk_compact) + 10
    for word in re.split(r"[\s/()]+", rk_norm):
        if len(word) >= 4 and word in name_upper:
            score += len(word)
    if hint:
        hint_compact = _compact_alnum(hint)
        if len(hint_compact) >= 3 and (
            rk_norm.startswith(hint + " ")
            or rk_norm.startswith(hint + "(")
            or rk_compact.startswith(hint_compact)
            or hint_compact in rk_compact
        ):
            score += 25
    for tag in tags:
        if tag in rk_norm:
            score += 35
    return score


def resolve_swatch_factory_keys(
    db: Session,
    *,
    factory_hint: str | None,
    customer_id: int | None = None,
) -> list[str]:
    """
    Kandidat factory_key untuk lookup swatch.
    Memetakan KODE SYSTEM (mis. CS004) ke semua varian nama pabrik di CSV
    (mis. FENGTAY, FENGTAY (WEST), CHANGSHIN RJ) via customer.
    """
    hint = normalize_factory_key(factory_hint)
    scored: list[tuple[int, str]] = []
    seen: set[str] = set()

    def add_scored(score: int, key: str | None) -> None:
        if not key:
            return
        k = normalize_factory_key(key)
        if not k or k in seen:
            return
        seen.add(k)
        scored.append((score, k))

    recipe_keys = list(
        db.scalars(
            select(ColorSwatchRecipe.factory_key)
            .where(ColorSwatchRecipe.is_active.is_(True))
            .distinct()
        ).all()
    )

    if hint:
        for rk in recipe_keys:
            if not rk:
                continue
            rk_norm = normalize_factory_key(rk)
            if rk_norm == hint:
                add_scored(100, rk_norm)
        if scored:
            scored.sort(key=lambda x: (-x[0], x[1]))
            return [k for _, k in scored]

    customer = db.get(Customer, customer_id) if customer_id else None
    if customer is None and hint:
        customer = db.scalars(select(Customer).where(Customer.code.ilike(hint)).limit(1)).first()

    if customer and (customer.name or "").strip():
        name_upper = _strip_company_prefix(customer.name or "")
        name_compact = _compact_alnum(name_upper)
        tags = _customer_factory_tags(name_upper)

        for rk in recipe_keys:
            if not rk:
                continue
            rk_norm = normalize_factory_key(rk)
            score = _factory_key_match_score(
                rk_norm,
                name_upper=name_upper,
                name_compact=name_compact,
                hint=hint,
                tags=tags,
            )
            if score >= 10:
                add_scored(score, rk_norm)

        words = [w for w in re.split(r"[\s.,()/]+", name_upper) if len(w) >= 3]
        for candidate in (
            _compact_alnum("".join(words[:2])),
            _compact_alnum(words[0]),
            _compact_alnum("".join(words[:3])),
        ):
            if len(candidate) < 4:
                continue
            for rk in recipe_keys:
                if _compact_alnum(normalize_factory_key(rk)) == candidate:
                    add_scored(15, rk)

    if hint:
        add_scored(5, hint)

    scored.sort(key=lambda x: (-x[0], x[1]))
    return [k for _, k in scored]


def normalize_buyer_code(raw: str | None) -> str:
    b = (raw or "").strip().upper()
    if b in {"WHITE", "BLACK", "GREY", "GRAY", "PINK", "YELLOW", "RED", "BLUE", "3MR", "3GU", "4AU"}:
        return ""
    return b


def parse_entered_date(raw: str | None) -> date | None:
    if not raw or not str(raw).strip():
        return None
    s = str(raw).strip()
    # DATA_CS_2026-07-28.csv memakai 22/Jan/26 — coba sebelum format numerik.
    for fmt in ("%d/%b/%y", "%d/%b/%Y", "%d-%b-%y", "%d-%b-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(s[:10] if len(s) > 10 else s, fmt).date()
        except ValueError:
            continue
    return None


def parse_csv_row(row: dict[str, str], source_file: str) -> dict[str, Any] | None:
    """Parse satu baris dictreader ke field recipe; None jika baris kosong."""
    # Lazy import: swatch_factory_map mengimpor normalize_factory_key dari modul ini.
    from app.services.swatch_factory_map import CANONICAL_FACTORY_KEYS

    code = (row.get("COLOR CODE") or row.get("color code") or "").strip()
    name = (row.get("COLOR NAME ") or row.get("COLOR NAME") or row.get("color name") or "").strip()
    if not code and not name:
        return None
    factory = normalize_factory_key(row.get("CUSTOMER") or row.get("customer"))
    factory = CANONICAL_FACTORY_KEYS.get(factory, factory)
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


def _resolve_customer_id(
    db: Session,
    factory_key: str,
    *,
    color_standard: str | None = None,
) -> int | None:
    from app.services.swatch_factory_map import resolve_swatch_customer_id

    return resolve_swatch_customer_id(
        db, factory_key, color_standard=color_standard
    )


def _resolve_brand_id(db: Session, buyer_code: str) -> int | None:
    b = buyer_code.strip().upper()
    brand = db.scalars(
        select(Brand).where((Brand.code.ilike(b)) | (Brand.name.ilike(b))).limit(1)
    ).first()
    return int(brand.id) if brand else None


class UnknownBuyerRejectError(ValueError):
    """Unknown buyer_code when reject_unknown_buyer=True."""


def _recipe_field(data: dict[str, Any] | ColorSwatchRecipe, name: str, default: str = "") -> str:
    if isinstance(data, dict):
        return str(data.get(name) or default)
    return str(getattr(data, name, None) or default)


def recipe_import_key(data: dict[str, Any] | ColorSwatchRecipe) -> tuple[str, str, str, str, str, str]:
    """Kunci upsert import — color_standard membedakan varian swatch pada dimensi sama."""
    return (
        _recipe_field(data, "factory_key"),
        _recipe_field(data, "buyer_code"),
        _recipe_field(data, "color_code"),
        _recipe_field(data, "material_name"),
        _recipe_field(data, "emboss"),
        _recipe_field(data, "color_standard"),
    )


def import_recipes(
    db: Session,
    recipes: list[dict[str, Any]],
    *,
    replace_inactive: bool = False,
    replace_inactive_scope: str = "global",
    reject_unknown_buyer: bool = False,
) -> dict[str, Any]:
    """Upsert recipes. Returns counts inserted, updated, skipped (+ warnings).

    replace_inactive_scope:
      - \"global\": soft-deactivate semua resep aktif yang kuncinya tidak ada di file
      - \"pair\": hanya orphan pada pasangan factory_key+buyer_code yang tersentuh file
    """
    from app.services.buyer_registry import collect_unknown_buyer_codes
    from app.services.material_aliases import material_missing_in_master_items

    inserted = 0
    updated = 0
    skipped = 0
    deactivated = 0
    warnings: list[str] = []
    imported_keys: set[tuple[str, str, str, str, str, str]] = set()
    customer_cache: dict[tuple[str, str | None], int | None] = {}
    brand_cache: dict[str, int | None] = {}
    buyers_seen: list[str] = [str(d.get("buyer_code") or "") for d in recipes]
    unknown_upfront = collect_unknown_buyer_codes(db, buyers_seen)
    if reject_unknown_buyer and unknown_upfront:
        raise UnknownBuyerRejectError(
            "buyer_code tidak ada di registry: " + ", ".join(unknown_upfront)
        )
    mats_warned: set[str] = set()

    for data in recipes:
        fk = data["factory_key"]
        buyer = data["buyer_code"]
        mat = data.get("material_name") or ""
        if mat and mat not in mats_warned and material_missing_in_master_items(db, mat):
            warnings.append(f"material tidak cocok master_items: {mat}")
            mats_warned.add(mat)
        imported_keys.add(recipe_import_key(data))
        cust_cache_key = (fk, data.get("color_standard"))
        if cust_cache_key not in customer_cache:
            customer_cache[cust_cache_key] = _resolve_customer_id(
                db, fk, color_standard=data.get("color_standard")
            )
        if buyer not in brand_cache:
            brand_cache[buyer] = _resolve_brand_id(db, buyer)

        existing = db.scalars(
            select(ColorSwatchRecipe).where(
                ColorSwatchRecipe.factory_key == fk,
                ColorSwatchRecipe.buyer_code == buyer,
                ColorSwatchRecipe.color_code == data["color_code"],
                ColorSwatchRecipe.material_name == data["material_name"],
                ColorSwatchRecipe.emboss == data["emboss"],
                ColorSwatchRecipe.color_standard == data.get("color_standard"),
            )
        ).first()

        if existing:
            existing.color_name = data["color_name"]
            existing.color_standard = data.get("color_standard")
            existing.backing = data.get("backing")
            existing.legacy_urut = data.get("legacy_urut")
            existing.entered_at = data.get("entered_at")
            existing.source_file = data.get("source_file")
            existing.customer_id = customer_cache[cust_cache_key]
            existing.brand_id = brand_cache[buyer]
            existing.is_active = True
            existing.updated_at = app_now()
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
                    customer_id=customer_cache[cust_cache_key],
                    brand_id=brand_cache[buyer],
                    is_active=True,
                )
            )
            inserted += 1
            db.flush()

    if replace_inactive and imported_keys:
        scope = (replace_inactive_scope or "global").strip().lower()
        if scope == "pair":
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
                    if recipe_import_key(recipe) not in imported_keys:
                        recipe.is_active = False
                        recipe.updated_at = app_now()
                        deactivated += 1
        else:
            # global: master hanya berisi isi file terbaru
            rows = db.scalars(
                select(ColorSwatchRecipe).where(ColorSwatchRecipe.is_active.is_(True))
            ).all()
            for recipe in rows:
                if recipe_import_key(recipe) not in imported_keys:
                    recipe.is_active = False
                    recipe.updated_at = app_now()
                    deactivated += 1

    db.commit()
    for u in collect_unknown_buyer_codes(db, buyers_seen):
        warnings.append(f"buyer_code tidak ada di registry: {u}")
    return {
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "deactivated": deactivated,
        "total": len(recipes),
        "warnings": warnings,
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
