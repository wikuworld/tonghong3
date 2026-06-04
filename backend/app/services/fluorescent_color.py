"""Master fluorescent color — normalisasi & upsert import."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FluorescentColorMaster

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


def upsert_fluorescent_rows(db: Session, rows: list[dict[str, Any]]) -> dict[str, int]:
    inserted = updated = 0
    for raw in rows:
        data = apply_fluorescent_fields(raw)
        if not data["color_name"]:
            continue
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
            existing.is_active = True
            updated += 1
        else:
            db.add(FluorescentColorMaster(**data))
            inserted += 1
        db.flush()
    db.commit()
    return {"inserted": inserted, "updated": updated, "total": len(rows)}


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
