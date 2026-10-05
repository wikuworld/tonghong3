#!/usr/bin/env python3
"""
Import master fluorescent colors dari dokumen:
- Copy of NB Fluorescent color REV (from mr bob).csv
- adidas Metallic Fluorescent Colors till SS26.csv
- Fluorescent- Master List of All Leather & Synthetic as of SPSU27.csv
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from sqlalchemy import delete, select

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))

from app.db import SessionLocal
from app.models import FluorescentColorMaster


def _clean(s: str | None) -> str:
    return (s or "").strip()


def _norm_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _season_parts(raw: str) -> tuple[str | None, int | None]:
    v = _norm_spaces(raw).upper()
    if not v:
        return None, None
    m_year = re.search(r"(20\d{2})", v)
    year = int(m_year.group(1)) if m_year else None
    season_type = None
    if any(x in v for x in ("SS", "SP/SU", "SPSU", "SP")):
        season_type = "SS"
    elif any(x in v for x in ("FW", "FA/HO", "FAHO", "HO", "Q3", "Q4")):
        season_type = "FW"
    elif "Q1" in v or "Q2" in v:
        season_type = "SS"
    return season_type, year


def load_nb(path: Path) -> list[dict]:
    out: list[dict] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f, delimiter=";"):
            if len(row) < 5:
                continue
            name = _norm_spaces(_clean(row[1]))
            code = _norm_spaces(_clean(row[2]))
            season = _norm_spaces(_clean(row[3]))
            remark = _clean(row[4]).lower()
            if not name or name.lower() == "color name":
                continue
            if "fluorescent" not in remark and "metallic" not in remark:
                continue
            season_type, season_year = _season_parts(season)
            color_class = "metallic" if "metallic" in remark else "fluorescent"
            out.append(
                {
                    "buyer_code": "NB",
                    "season_label": season or None,
                    "season_type": season_type,
                    "season_year": season_year,
                    "color_name": name,
                    "color_code": code or None,
                    "color_class": color_class,
                }
            )
    return out


def load_adidas(path: Path) -> list[dict]:
    out: list[dict] = []
    current_season = ""
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f, delimiter=";"):
            if len(row) < 3:
                continue
            s0 = _norm_spaces(_clean(row[0]))
            name = _norm_spaces(_clean(row[1]))
            code = _norm_spaces(_clean(row[2]))
            if s0 and s0.lower() != "season":
                current_season = s0
            if not name or name.lower() == "color name":
                continue
            if "no fluorescent color" in code.lower():
                continue
            season_type, season_year = _season_parts(current_season)
            color_class = "metallic" if "metallic" in current_season.lower() else "fluorescent"
            out.append(
                {
                    "buyer_code": "ADIDAS",
                    "season_label": current_season or None,
                    "season_type": season_type,
                    "season_year": season_year,
                    "color_name": name,
                    "color_code": code or None,
                    "color_class": color_class,
                }
            )
    return out


def load_global(path: Path) -> list[dict]:
    out: list[dict] = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f, delimiter=";"):
            if len(row) < 5:
                continue
            code = _norm_spaces(_clean(row[1]))
            name = _norm_spaces(_clean(row[2]))
            season = _norm_spaces(_clean(row[3]))
            remark = _clean(row[4]).lower()
            if not name or name.lower() == "color name":
                continue
            if "fluorescent" not in remark and "metallic" not in remark:
                continue
            season_type, season_year = _season_parts(season)
            color_class = "metallic" if "metallic" in remark else "fluorescent"
            out.append(
                {
                    "buyer_code": "GLOBAL",
                    "season_label": season or None,
                    "season_type": season_type,
                    "season_year": season_year,
                    "color_name": name,
                    "color_code": code or None,
                    "color_class": color_class,
                }
            )
    return out


def load_ua(path: Path) -> list[dict]:
    out: list[dict] = []
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f, delimiter=";"))
    if not rows:
        return out
    for header_idx, header in enumerate(rows):
        if not any("fluorescent" in _clean(x).lower() for x in header):
            continue
        for col_idx, season_cell in enumerate(header):
            season = _norm_spaces(_clean(season_cell))
            if not season or "fluorescent" not in season.lower():
                continue
            season_type, season_year = _season_parts(season)
            for r in rows[header_idx + 1 :]:
                if col_idx >= len(r):
                    continue
                name_raw = _norm_spaces(_clean(r[col_idx]))
                if not name_raw:
                    if all(not _clean(c) for c in r):
                        break
                    continue
                m = re.search(r"\s+([0-9A-Za-z\-]+)$", name_raw)
                code = m.group(1) if m else None
                out.append(
                    {
                        "buyer_code": "UA",
                        "season_label": season,
                        "season_type": season_type,
                        "season_year": season_year,
                        "color_name": name_raw,
                        "color_code": code,
                        "color_class": "fluorescent",
                    }
                )
    return out


def dedup(rows: list[dict]) -> list[dict]:
    seen: set[tuple] = set()
    out: list[dict] = []
    for r in rows:
        key = (
            r["buyer_code"],
            r.get("season_label") or "",
            (r.get("color_code") or "").upper(),
            r["color_name"].upper(),
            r["color_class"],
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def main() -> None:
    doc_dirs = [ROOT / "dokumentasi", BACKEND / "dokumentasi"]
    dok_dir = next((d for d in doc_dirs if d.exists()), ROOT / "dokumentasi")
    nb = dok_dir / "Copy of NB Fluorescent color REV (from mr bob).csv"
    adidas = dok_dir / "adidas Metallic Fluorescent Colors till SS26.csv"
    global_file = None
    for p in dok_dir.glob("Fluorescent-*SPSU27.csv"):
        global_file = p
        break
    if not global_file:
        raise FileNotFoundError("File Fluorescent Master SPSU27 tidak ditemukan")
    if not nb.exists() or not adidas.exists():
        raise FileNotFoundError("File NB/ADIDAS fluorescent tidak ditemukan")
    ua = dok_dir / "UA每季客人指定荧光色总汇FLOURESENT UA.csv"

    rows = dedup(
        load_nb(nb)
        + load_adidas(adidas)
        + load_global(global_file)
        + (load_ua(ua) if ua.exists() else [])
    )

    db = SessionLocal()
    try:
        db.execute(delete(FluorescentColorMaster))
        db.flush()
        for r in rows:
            db.add(
                FluorescentColorMaster(
                    buyer_code=r["buyer_code"],
                    season_label=r["season_label"],
                    season_type=r["season_type"],
                    season_year=r["season_year"],
                    color_name=r["color_name"],
                    color_code=r["color_code"],
                    color_class=r["color_class"],
                    source_file="fluorescent_csv_pack",
                    is_active=True,
                )
            )
        db.commit()
        total = db.scalar(select(FluorescentColorMaster).count()) if False else len(rows)
        print("Imported fluorescent colors:", total)
        for buyer in ("NB", "ADIDAS", "UA", "GLOBAL"):
            cnt = db.scalar(
                select(FluorescentColorMaster)
                .where(FluorescentColorMaster.buyer_code == buyer)
                .count()
            ) if False else sum(1 for x in rows if x["buyer_code"] == buyer)
            print(f"- {buyer}: {cnt}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

