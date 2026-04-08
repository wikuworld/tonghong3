#!/usr/bin/env python3
"""
Impor folder CSV list harga buyer (mis. LIST_HARGA_ALL_BUYER_extracted) ke `buyer_price_lists`.

  cd backend && PYTHONPATH=. python scripts/import_buyer_price_folder.py /path/to/LIST_HARGA_ALL_BUYER_extracted "LABEL_SUMBER"

Default path (jika argumen tidak ada): ../../LIST_HARGA_ALL_BUYER_extracted relatif ke folder backend.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
DEFAULT_FOLDER = BACKEND.parent / "LIST_HARGA_ALL_BUYER_extracted"

sys.path.insert(0, str(BACKEND))


def main() -> None:
    from app.db import SessionLocal
    from app.services.buyer_price_import import persist_buyer_folder

    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FOLDER
    label = sys.argv[2] if len(sys.argv) > 2 else folder.name

    if not folder.is_dir():
        print("Folder tidak ada:", folder)
        sys.exit(1)

    db = SessionLocal()
    try:
        lst = persist_buyer_folder(db, folder, label)
        db.commit()
        for x in lst:
            print("OK id=", x.id, "buyer_code=", x.buyer_code, "rows=", x.meta_json.get("data_row_count") if x.meta_json else "?")
    except Exception as e:
        db.rollback()
        print("Error:", e)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
