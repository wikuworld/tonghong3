#!/usr/bin/env python3
"""Backfill tbl_persiapan_kulit.status saved → completed (idempotent).

Usage (from mrp/backend/legacy):
  python scripts/backfill_persiapan_saved_to_completed.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import get_db_connection  # noqa: E402


def main() -> int:
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS c FROM tbl_persiapan_kulit WHERE status='saved'")
    before = int((cur.fetchone() or {}).get("c") or 0)
    cur.execute("UPDATE tbl_persiapan_kulit SET status='completed' WHERE status='saved'")
    conn.commit()
    print(f"updated={cur.rowcount} had_saved={before}")
    cur.close()
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
