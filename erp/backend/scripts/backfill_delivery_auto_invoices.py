#!/usr/bin/env python3
"""Backfill invoice THIN untuk delivery yang belum punya invoice (SJ lama sebelum auto-invoice).

Usage:
  cd erp/backend
  PYTHONPATH=. .venv/bin/python scripts/backfill_delivery_auto_invoices.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Pastikan .env project/UAT di-load sebelum SessionLocal (sama DB dengan uvicorn).
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

from app.db import SessionLocal  # noqa: E402
from app.models import DeliveryDetail, DeliveryHeader, Invoice  # noqa: E402
from app.services.delivery_auto_invoice import ensure_invoice_for_delivery  # noqa: E402
from sqlalchemy import select  # noqa: E402


def main() -> int:
    db = SessionLocal()
    created = 0
    skipped_existing = 0
    skipped_no_detail = 0
    errors: list[str] = []
    try:
        deliveries = db.scalars(select(DeliveryHeader).order_by(DeliveryHeader.id)).all()
        for hdr in deliveries:
            existing = db.scalars(
                select(Invoice.id).where(Invoice.delivery_id == int(hdr.id)).limit(1)
            ).first()
            if existing:
                skipped_existing += 1
                continue
            has_detail = db.scalars(
                select(DeliveryDetail.id).where(DeliveryDetail.delivery_id == int(hdr.id)).limit(1)
            ).first()
            if not has_detail:
                skipped_no_detail += 1
                print(f"skip delivery #{hdr.id} {hdr.delivery_number}: no details")
                continue
            try:
                inv = ensure_invoice_for_delivery(
                    db, int(hdr.id), actor="backfill-thin", allow_draft=True
                )
                db.commit()
                if inv:
                    created += 1
                    print(
                        f"ok delivery #{hdr.id} {hdr.delivery_number} → {inv.invoice_number}"
                    )
                else:
                    skipped_no_detail += 1
                    print(f"skip delivery #{hdr.id} {hdr.delivery_number}: ensure returned None")
            except Exception as exc:  # noqa: BLE001
                db.rollback()
                msg = f"fail delivery #{hdr.id} {hdr.delivery_number}: {exc}"
                errors.append(msg)
                print(msg)
        print(
            f"summary created={created} skipped_existing={skipped_existing} "
            f"skipped_no_detail={skipped_no_detail} errors={len(errors)}"
        )
        return 1 if errors else 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
