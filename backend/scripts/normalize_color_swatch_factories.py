#!/usr/bin/env python3
"""Normalisasi relasi factory_key color swatch → customer (pabrik ERP).

Usage:
  python scripts/normalize_color_swatch_factories.py --dry-run
  python scripts/normalize_color_swatch_factories.py --apply
  python scripts/normalize_color_swatch_factories.py --apply --no-rename-keys
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import SessionLocal
from app.services.swatch_factory_map import (
    normalize_color_swatch_factory_links,
    summarize_swatch_factory_coverage,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sinkronkan pabrik color swatch dengan master customer")
    parser.add_argument("--dry-run", action="store_true", help="Simulasi tanpa commit")
    parser.add_argument("--apply", action="store_true", help="Terapkan perubahan ke DB")
    parser.add_argument(
        "--no-rename-keys",
        action="store_true",
        help="Hanya set customer_id, jangan ubah factory_key",
    )
    args = parser.parse_args()
    if not args.dry_run and not args.apply:
        parser.error("Pilih --dry-run atau --apply")

    db = SessionLocal()
    try:
        before = summarize_swatch_factory_coverage(db)
        print("=== SEBELUM ===")
        print(json.dumps(before, indent=2, ensure_ascii=False))

        result = normalize_color_swatch_factory_links(
            db,
            normalize_factory_keys=not args.no_rename_keys,
            dry_run=args.dry_run,
        )
        print("\n=== HASIL ===")
        print(
            json.dumps(
                {
                    "total": result.total,
                    "customer_linked": result.customer_linked,
                    "customer_unchanged": result.customer_unchanged,
                    "customer_unresolved": result.customer_unresolved,
                    "factory_key_renamed": result.factory_key_renamed,
                    "factory_key_skipped_conflict": result.factory_key_skipped_conflict,
                    "dry_run": args.dry_run,
                },
                indent=2,
            )
        )

        if not args.dry_run:
            after = summarize_swatch_factory_coverage(db)
            print("\n=== SESUDAH ===")
            print(json.dumps(after, indent=2, ensure_ascii=False))
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
