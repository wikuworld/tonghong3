#!/usr/bin/env python3
"""Impor katalog CSI dari dokumentasi/CSI ALL BUYER.xlsx (upsert, tidak hapus)."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))

from app.db import SessionLocal
from app.services.csi_color import parse_csi_workbook, upsert_csi_rows


def default_workbook() -> Path:
    for base in (ROOT / "dokumentasi", BACKEND / "dokumentasi", Path("/app/dokumentasi")):
        path = base / "CSI ALL BUYER.xlsx"
        if path.is_file():
            return path
    raise FileNotFoundError("CSI ALL BUYER.xlsx tidak ditemukan di dokumentasi/")


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_workbook()
    rows = parse_csi_workbook(path)
    if not rows:
        raise SystemExit("Tidak ada baris CSI valid")
    db = SessionLocal()
    try:
        stats = upsert_csi_rows(db, rows)
        db.commit()
        print(f"CSI import {path.name}: inserted={stats['inserted']} updated={stats['updated']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
