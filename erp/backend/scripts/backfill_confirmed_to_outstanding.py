#!/usr/bin/env python3
"""Naikkan SO confirmed+ yang masih di input_system / rekap_printed / with_ppic ke Outstanding."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import SessionLocal  # noqa: E402
from app.services.mkt_workflow import backfill_confirmed_to_outstanding  # noqa: E402


def main() -> int:
    db = SessionLocal()
    try:
        moved = backfill_confirmed_to_outstanding(db, actor="backfill")
        print(f"moved={moved}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
