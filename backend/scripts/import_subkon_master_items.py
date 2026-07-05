#!/usr/bin/env python3
"""Impor master item SubKon dari CSV marketing.

Usage:
  cd backend && PYTHONPATH=. python scripts/import_subkon_master_items.py --dry-run
  cd backend && PYTHONPATH=. python scripts/import_subkon_master_items.py --apply
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.services.subkon_master_items import import_subkon_master_items, iter_subkon_rows_from_csv

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
DEFAULT_CSV = ROOT / "dokumentasi" / "Master_Data_extracted" / "01_Master_Item_SubKon.csv"
DOCKER_CSV = BACKEND / "dokumentasi" / "Master_Data_extracted" / "01_Master_Item_SubKon.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description="Impor master item kategori SubKon")
    parser.add_argument(
        "--csv",
        type=Path,
        default=DOCKER_CSV if DOCKER_CSV.exists() else DEFAULT_CSV,
        help="Path CSV SubKon",
    )
    parser.add_argument("--dry-run", action="store_true", help="Simulasi tanpa commit")
    parser.add_argument("--apply", action="store_true", help="Terapkan ke database")
    args = parser.parse_args()
    if not args.dry_run and not args.apply:
        parser.error("Pilih --dry-run atau --apply")
    if not args.csv.exists():
        parser.error(f"CSV tidak ditemukan: {args.csv}")

    db = SessionLocal()
    try:
        result = import_subkon_master_items(
            db,
            iter_subkon_rows_from_csv(args.csv),
            dry_run=args.dry_run,
        )
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
