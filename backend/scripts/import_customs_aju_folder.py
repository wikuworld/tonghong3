#!/usr/bin/env python3
"""
Impor folder CSV AJU (mis. 017_728_VICTORY_D_extracted) ke tabel customs_*.

  cd backend && PYTHONPATH=. python scripts/import_customs_aju_folder.py /path/to/017_728_VICTORY_D_extracted "017.728 VICTORY-D"

Default path (jika argumen tidak ada): ../../017_728_VICTORY_D_extracted relatif ke folder Projects.
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
DEFAULT_FOLDER = BACKEND.parent.parent / "017_728_VICTORY_D_extracted"

sys.path.insert(0, str(BACKEND))


def main() -> None:
    from app.db import SessionLocal
    from app.services.customs_import import load_folder_csvs, persist_declaration

    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_FOLDER
    label = sys.argv[2] if len(sys.argv) > 2 else folder.name

    if not folder.is_dir():
        print("Folder tidak ada:", folder)
        sys.exit(1)
    sheets = load_folder_csvs(folder)
    if not sheets:
        print("Tidak ada CSV.")
        sys.exit(1)
    db = SessionLocal()
    try:
        dec = persist_declaration(db, sheets, label)
        db.commit()
        print("OK id=", dec.id, "nomor_aju=", dec.nomor_aju)
    except Exception as e:
        db.rollback()
        print("Error:", e)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
