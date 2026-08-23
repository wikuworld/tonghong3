#!/usr/bin/env python3
"""Isi ulang list harga ADIDAS + NIKE dari workbook resmi di dokumentasi/."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))


def _default_doc() -> Path:
    for candidate in (
        BACKEND / "dokumentasi",
        Path("/app/dokumentasi"),
        BACKEND.parent / "dokumentasi",
    ):
        if candidate.is_dir():
            return candidate
    return BACKEND.parent / "dokumentasi"


def main() -> None:
    from app.db import SessionLocal
    from app.services.buyer_price_import import persist_official_buyer_workbooks

    doc = Path(sys.argv[1]) if len(sys.argv) > 1 else _default_doc()
    if not doc.is_dir():
        print("Folder dokumentasi tidak ada:", doc)
        sys.exit(1)

    db = SessionLocal()
    try:
        lists = persist_official_buyer_workbooks(db, doc)
        db.commit()
        if not lists:
            print("Tidak ada workbook Adidas/Nike yang ditemukan")
            sys.exit(1)
        for lst in lists:
            meta = lst.meta_json or {}
            print(
                "OK",
                lst.buyer_code,
                "id=",
                lst.id,
                "rows=",
                meta.get("data_row_count"),
                "src=",
                meta.get("source_file"),
            )
    except Exception as exc:
        db.rollback()
        print("Error:", exc)
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
