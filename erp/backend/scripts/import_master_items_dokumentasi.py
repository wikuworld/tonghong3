#!/usr/bin/env python3
"""Impor master item PU / Suede / SubKon dari folder dokumentasi/master-items.

Usage:
  cd backend && PYTHONPATH=. python scripts/import_master_items_dokumentasi.py --dry-run
  cd backend && PYTHONPATH=. python scripts/import_master_items_dokumentasi.py --apply
  cd backend && PYTHONPATH=. python scripts/import_master_items_dokumentasi.py --apply --only subkon
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.services.pu_suede_master_items import (
    PU_SUEDE_SHEET,
    import_pu_suede_master_items,
    iter_pu_suede_rows_from_csv,
    iter_pu_suede_rows_from_xlsx,
)
from app.services.subkon_master_items import import_subkon_master_items, iter_subkon_rows_from_csv

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
DOC_DIR = ROOT / "dokumentasi" / "master-items"
DOCKER_DOC_DIR = BACKEND / "dokumentasi" / "master-items"
DEFAULT_DOC_DIR = DOCKER_DOC_DIR if DOCKER_DOC_DIR.exists() else DOC_DIR
DEFAULT_SUBKON_CSV = DEFAULT_DOC_DIR / "Sheet1-Table_1.csv"
DEFAULT_PU_SUEDE_XLSX = DEFAULT_DOC_DIR / "Master_List_Item_PU_Suede_Subcont.xlsx"
DEFAULT_PU_SUEDE_CSV = DEFAULT_DOC_DIR / "PUSUEDE-Table_1.csv"


def main() -> int:
    parser = argparse.ArgumentParser(description="Impor master item dari dokumentasi/master-items")
    parser.add_argument("--subkon-csv", type=Path, default=DEFAULT_SUBKON_CSV)
    parser.add_argument("--pu-suede-xlsx", type=Path, default=DEFAULT_PU_SUEDE_XLSX)
    parser.add_argument("--pu-suede-csv", type=Path, default=DEFAULT_PU_SUEDE_CSV)
    parser.add_argument("--pu-suede-sheet", default=PU_SUEDE_SHEET)
    parser.add_argument(
        "--only",
        choices=("all", "subkon", "pu-suede", "pu-suede-csv"),
        default="all",
        help="Pilih sumber impor",
    )
    parser.add_argument("--dry-run", action="store_true", help="Simulasi tanpa commit")
    parser.add_argument("--apply", action="store_true", help="Terapkan ke database")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        parser.error("Pilih --dry-run atau --apply")

    if args.only in ("all", "subkon") and not args.subkon_csv.exists():
        parser.error(f"CSV SubKon tidak ditemukan: {args.subkon_csv}")
    if args.only in ("all", "pu-suede") and not args.pu_suede_xlsx.exists():
        parser.error(f"File XLSX tidak ditemukan: {args.pu_suede_xlsx}")
    if args.only in ("all", "pu-suede-csv") and not args.pu_suede_csv.exists():
        parser.error(f"CSV PU/Suede tidak ditemukan: {args.pu_suede_csv}")

    db = SessionLocal()
    summary: dict[str, object] = {"dry_run": args.dry_run, "only": args.only}
    try:
        if args.only in ("all", "subkon"):
            subkon_result = import_subkon_master_items(
                db,
                iter_subkon_rows_from_csv(args.subkon_csv),
                dry_run=args.dry_run,
            )
            summary["subkon"] = subkon_result.to_dict()
            summary["subkon_csv"] = str(args.subkon_csv)

        if args.only in ("all", "pu-suede"):
            pu_suede_result = import_pu_suede_master_items(
                db,
                iter_pu_suede_rows_from_xlsx(args.pu_suede_xlsx, sheet_name=args.pu_suede_sheet),
                dry_run=args.dry_run,
            )
            summary["pu_suede"] = pu_suede_result.to_dict()
            summary["pu_suede_xlsx"] = str(args.pu_suede_xlsx)
            summary["pu_suede_sheet"] = args.pu_suede_sheet

        if args.only == "pu-suede-csv":
            pu_suede_csv_result = import_pu_suede_master_items(
                db,
                iter_pu_suede_rows_from_csv(args.pu_suede_csv),
                dry_run=args.dry_run,
            )
            summary["pu_suede_csv"] = pu_suede_csv_result.to_dict()
            summary["pu_suede_csv_path"] = str(args.pu_suede_csv)

        print(json.dumps(summary, indent=2, ensure_ascii=False))
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
