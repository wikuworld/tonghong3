#!/usr/bin/env python3
"""Normalisasi nomor lot PO (prefix subcont + placeholder legacy).

Usage:
  python scripts/normalize_lot_numbers.py --dry-run
  python scripts/normalize_lot_numbers.py --apply
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.services.lot_number_normalize import normalize_lot_references


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalisasi thi_line_ref / lot production")
    parser.add_argument("--dry-run", action="store_true", help="Simulasi tanpa commit")
    parser.add_argument("--apply", action="store_true", help="Terapkan ke database")
    parser.add_argument(
        "--keep-legacy",
        action="store_true",
        help="Jangan kosongkan placeholder THI- / PU-xxxx",
    )
    args = parser.parse_args()
    if not args.dry_run and not args.apply:
        parser.error("Pilih --dry-run atau --apply")

    db = SessionLocal()
    try:
        result = normalize_lot_references(
            db,
            dry_run=args.dry_run,
            clear_legacy_placeholders=not args.keep_legacy,
        )
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
