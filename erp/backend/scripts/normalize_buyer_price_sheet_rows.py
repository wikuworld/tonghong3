#!/usr/bin/env python3
"""Rapikan baris list harga yang sudah tersimpan agar cocok dengan SO.

- Rentang ketebalan di nama ITEM dipindah ke THICKNESS.
- Nama yang punya alias diganti ke nama material SO.
- COLOR yang bukan blok Nike (COMMON / SPECIAL / OUTSIDE BANTEN / OUTSIDE SPECIAL) dikosongkan.

Usage:
  cd erp/backend && PYTHONPATH=. python scripts/normalize_buyer_price_sheet_rows.py --dry-run
  cd erp/backend && PYTHONPATH=. python scripts/normalize_buyer_price_sheet_rows.py --apply
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from app.db import SessionLocal
from app.models import BuyerPriceSheetRow
from app.services.buyer_price_aliases import normalize_sheet_cells


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    db = SessionLocal()
    changed = 0
    scanned = 0
    try:
        rows = list(db.scalars(select(BuyerPriceSheetRow).order_by(BuyerPriceSheetRow.id)).all())
        for row in rows:
            scanned += 1
            src = dict(row.cells or {})
            nxt = normalize_sheet_cells(src)
            if nxt == src:
                continue
            changed += 1
            if args.apply:
                row.cells = nxt
                flag_modified(row, "cells")
        if args.apply:
            db.commit()
        else:
            db.rollback()
    finally:
        db.close()
    mode = "applied" if args.apply else "dry-run"
    print(f"{mode}: scanned={scanned} changed={changed}")


if __name__ == "__main__":
    main()
