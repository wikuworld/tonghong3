#!/usr/bin/env python3
"""One-shot: cd mrp && .venv/bin/python scripts/import_raw_material_masters.py"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection
from raw_material_import import DEFAULT_XLS_PATH, import_raw_material_masters


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_XLS_PATH
    conn = get_db_connection()
    try:
        result = import_raw_material_masters(conn, path=path)
    finally:
        conn.close()
    print(result)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
