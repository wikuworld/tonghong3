#!/usr/bin/env python3
"""Isi raw_materials.thickness dan color dari nama kulit yang polanya pasti.

Hanya kolom yang masih kosong. Baris yang sudah terisi tidak ditimpa.
Token kode pendek (01V, 2CT) tidak dijadikan warna.

Usage:
  cd erp/backend
  PYTHONPATH=. .venv/bin/python scripts/backfill_kulit_thickness_color.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_PROJECT = ROOT.parent.parent if (ROOT.parent.parent / ".env").is_file() else ROOT.parent
for _env in (ROOT / ".env", _PROJECT / ".env"):
    if not _env.is_file():
        continue
    for _line in _env.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not _line.strip() or _line.strip().startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        key = _k.strip()
        if key in ("DATABASE_URL",) or key not in __import__("os").environ:
            __import__("os").environ[key] = _v.strip().strip('"').strip("'")

from sqlalchemy import select  # noqa: E402

from app.db import SessionLocal  # noqa: E402
from app.models import RawMaterial  # noqa: E402
from app.services.kulit_name_spec import kulit_spec_from_name  # noqa: E402


def _blank(value) -> bool:
    return value is None or str(value).strip() == ""


def main() -> int:
    db = SessionLocal()
    updated = 0
    skipped = 0
    try:
        rows = db.scalars(
            select(RawMaterial).where(RawMaterial.material_type == "kulit").order_by(RawMaterial.code)
        ).all()
        for row in rows:
            spec = kulit_spec_from_name(row.name)
            changed = False
            if _blank(row.thickness) and spec["thickness"]:
                row.thickness = spec["thickness"]
                changed = True
            if _blank(row.color) and spec["color"]:
                row.color = spec["color"]
                changed = True
            if changed:
                updated += 1
            else:
                skipped += 1
        db.commit()
    finally:
        db.close()
    print(f"kulit diperbarui={updated} dilewati={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
