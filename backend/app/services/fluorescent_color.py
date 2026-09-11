"""Master fluorescent color — normalisasi & upsert import."""

from __future__ import annotations

import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FluorescentColorMaster
from app.timeutil import app_now

VALID_COLOR_CLASSES = frozenset({"fluorescent", "metallic"})


def normalize_buyer_code(value: str) -> str:
    return (value or "").strip().upper() or "GLOBAL"


def normalize_color_class(value: str | None) -> str:
    raw = (value or "fluorescent").strip().lower()
    return raw if raw in VALID_COLOR_CLASSES else "fluorescent"


def apply_fluorescent_fields(data: dict[str, Any]) -> dict[str, Any]:
    season_label = (data.get("season_label") or "").strip() or None
    color_code = (data.get("color_code") or "").strip() or None
    return {
        "buyer_code": normalize_buyer_code(data.get("buyer_code") or ""),
        "season_label": season_label,
        "season_year": data.get("season_year"),
        "season_type": (data.get("season_type") or "").strip() or None,
        "color_name": (data.get("color_name") or "").strip(),
        "color_code": color_code,
        "color_class": normalize_color_class(data.get("color_class")),
        "source_file": (data.get("source_file") or "").strip() or None,
        "is_active": bool(data.get("is_active", True)),
    }


def find_existing(
    db: Session,
    *,
    buyer_code: str,
    season_label: str | None,
    color_code: str | None,
    color_name: str,
    exclude_id: int | None = None,
) -> FluorescentColorMaster | None:
    stmt = select(FluorescentColorMaster).where(
        FluorescentColorMaster.buyer_code == buyer_code,
        FluorescentColorMaster.color_name == color_name,
    )
    if season_label:
        stmt = stmt.where(FluorescentColorMaster.season_label == season_label)
    else:
        stmt = stmt.where(FluorescentColorMaster.season_label.is_(None))
    if color_code:
        stmt = stmt.where(FluorescentColorMaster.color_code == color_code)
    else:
        stmt = stmt.where(FluorescentColorMaster.color_code.is_(None))
    if exclude_id is not None:
        stmt = stmt.where(FluorescentColorMaster.id != exclude_id)
    return db.scalars(stmt).first()


def upsert_fluorescent_rows(
    db: Session,
    rows: list[dict[str, Any]],
    *,
    reject_unknown_buyer: bool = False,
) -> dict[str, Any]:
    from app.models import Brand
    from app.services.buyer_registry import collect_unknown_buyer_codes
    from app.services.color_swatch import UnknownBuyerRejectError

    inserted = updated = 0
    warnings: list[str] = []
    seen_buyers: list[str] = []

    def _brand_id_for(buyer: str) -> int | None:
        if not buyer or buyer == "GLOBAL":
            return None
        b = db.scalars(select(Brand).where(Brand.code == buyer)).first()
        return b.id if b else None

    for raw in rows:
        data = apply_fluorescent_fields(raw)
        if not data["color_name"]:
            continue
        seen_buyers.append(data["buyer_code"])
        data["brand_id"] = _brand_id_for(data["buyer_code"])
        existing = find_existing(
            db,
            buyer_code=data["buyer_code"],
            season_label=data["season_label"],
            color_code=data["color_code"],
            color_name=data["color_name"],
        )
        if existing:
            existing.season_year = data.get("season_year")
            existing.season_type = data.get("season_type")
            existing.color_class = data["color_class"]
            if data.get("source_file"):
                existing.source_file = data["source_file"]
            existing.brand_id = data.get("brand_id")
            existing.is_active = True
            existing.updated_at = app_now()
            updated += 1
        else:
            db.add(FluorescentColorMaster(**data))
            inserted += 1
        db.flush()
    unknown = collect_unknown_buyer_codes(db, seen_buyers)
    if reject_unknown_buyer and unknown:
        db.rollback()
        raise UnknownBuyerRejectError(
            "buyer_code tidak ada di registry: " + ", ".join(unknown)
        )
    for u in unknown:
        warnings.append(f"buyer_code tidak ada di registry: {u}")
    db.commit()
    return {
        "inserted": inserted,
        "updated": updated,
        "total": len(rows),
        "warnings": warnings,
    }


def _load_import_module():
    script = Path(__file__).resolve().parents[1] / "scripts" / "import_fluorescent_colors.py"
    spec = importlib.util.spec_from_file_location("import_fluorescent_colors", script)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Script import tidak ditemukan: {script}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def gather_bundled_rows() -> list[dict[str, Any]]:
    """Muat baris dari CSV dokumentasi (sama seperti script import)."""
    from pathlib import Path

    imp = _load_import_module()
    dedup = imp.dedup
    load_nb = imp.load_nb
    load_adidas = imp.load_adidas
    load_global = imp.load_global
    load_ua = imp.load_ua

    root = Path(__file__).resolve().parents[2]
    dok_dir = root / "dokumentasi"
    if not dok_dir.is_dir():
        dok_dir = Path(__file__).resolve().parents[1] / "dokumentasi"

    nb = dok_dir / "Copy of NB Fluorescent color REV (from mr bob).csv"
    adidas = dok_dir / "adidas Metallic Fluorescent Colors till SS26.csv"
    global_file = next(dok_dir.glob("Fluorescent-*SPSU27.csv"), None)
    ua = dok_dir / "UA每季客人指定荧光色总汇FLOURESENT UA.csv"

    if not nb.is_file() or not adidas.is_file() or global_file is None:
        raise FileNotFoundError("File fluorescent NB/ADIDAS/GLOBAL tidak ditemukan di dokumentasi/")

    rows = dedup(load_nb(nb) + load_adidas(adidas) + load_global(global_file))
    if ua.is_file():
        rows = dedup(rows + load_ua(ua))
    for r in rows:
        r["source_file"] = r.get("source_file") or "fluorescent_csv_pack"
    return rows


def parse_fluorescent_upload(raw: bytes, filename: str) -> list[dict[str, Any]]:
    """Parse upload CSV fluorescent (format NB/ADIDAS/GLOBAL/UA atau generic)."""
    import csv
    import io
    import tempfile

    imp = _load_import_module()
    suffix = Path(filename).suffix or ".csv"
    path = Path(tempfile.mkstemp(suffix=suffix)[1])
    try:
        path.write_bytes(raw)
        merged: list[dict[str, Any]] = []
        for loader in (imp.load_nb, imp.load_adidas, imp.load_global, imp.load_ua):
            try:
                part = loader(path)
                if part:
                    merged.extend(part)
            except Exception:
                continue
        if merged:
            rows = imp.dedup(merged)
            for r in rows:
                r["source_file"] = filename
            return rows
    finally:
        path.unlink(missing_ok=True)

    text = raw.decode("utf-8-sig", errors="replace")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return []
    delim = ";" if ";" in lines[0] else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delim)
    out: list[dict[str, Any]] = []
    for row in reader:
        name = (row.get("color_name") or row.get("COLOR NAME") or row.get("Color Name") or "").strip()
        if not name:
            continue
        buyer = (row.get("buyer_code") or row.get("BUYER") or row.get("buyer") or "GLOBAL").strip()
        out.append(
            {
                "buyer_code": buyer,
                "season_label": (row.get("season_label") or row.get("season") or row.get("SEASON") or "").strip()
                or None,
                "color_name": name,
                "color_code": (row.get("color_code") or row.get("COLOR CODE") or row.get("code") or "").strip()
                or None,
                "color_class": (row.get("color_class") or row.get("class") or "fluorescent").strip(),
                "source_file": filename,
            }
        )
    return imp.dedup(out) if out else []
