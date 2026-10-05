#!/usr/bin/env python3
"""Generate sample RAR + Pending Payment XLSX from real DB data."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import SessionLocal
from app.services.accounts_receivable_report import build_rar_payload, render_rar_xlsx
from app.services.pending_payment_report import build_pending_payment_payload, render_pending_payment_xlsx

OUT_DIR = Path(__file__).resolve().parents[2] / "dokumentasi" / "sample-reports"

RAR_CASES = [
    ("RAR_2026_full", {"year": 2026, "payment_status": "all"}),
    ("RAR_2026_unpaid", {"year": 2026, "payment_status": "unpaid"}),
    ("RAR_2026_paid", {"year": 2026, "payment_status": "paid"}),
    ("RAR_2026_Q1", {"year": 2026, "date_from": date(2026, 1, 1), "date_to": date(2026, 3, 31), "payment_status": "all"}),
    ("RAR_2026_Q2_unpaid", {"year": 2026, "date_from": date(2026, 4, 1), "date_to": date(2026, 6, 30), "payment_status": "unpaid"}),
]

PP_CASES = [
    ("PP_20260807", date(2026, 8, 7)),
    ("PP_20260814", date(2026, 8, 14)),
    ("PP_20260818", date(2026, 8, 18)),
    ("PP_20260828", date(2026, 8, 28)),
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    db = SessionLocal()
    try:
        for name, kwargs in RAR_CASES:
            payload = build_rar_payload(db, **kwargs)
            data = render_rar_xlsx(payload)
            path = OUT_DIR / f"{name}.xlsx"
            path.write_bytes(data)
            summary = payload.get("summary") or {}
            manifest.append(
                {
                    "type": "rar",
                    "file": path.name,
                    "params": {k: (v.isoformat() if isinstance(v, date) else v) for k, v in kwargs.items()},
                    "count": summary.get("count", 0),
                    "amount_faktur_usd": summary.get("amount_faktur_usd", 0),
                    "not_yet_count": summary.get("not_yet_count", 0),
                }
            )
            print(f"RAR  {path.name}: {summary.get('count', 0)} faktur")

        for name, as_of in PP_CASES:
            payload = build_pending_payment_payload(db, as_of=as_of, year=2026)
            data = render_pending_payment_xlsx(payload)
            path = OUT_DIR / f"{name}.xlsx"
            path.write_bytes(data)
            summary = payload.get("summary") or {}
            manifest.append(
                {
                    "type": "pending_payment",
                    "file": path.name,
                    "as_of": as_of.isoformat(),
                    "overdue_customers": summary.get("overdue_customer_count", 0),
                    "overdue_invoices": summary.get("overdue_invoice_count", 0),
                    "amount_usd_total": summary.get("amount_usd_total", 0),
                }
            )
            print(
                f"PP   {path.name}: {summary.get('overdue_customer_count', 0)} customer, "
                f"USD {summary.get('amount_usd_total', 0):,.2f}"
            )
    finally:
        db.close()

    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nOutput: {OUT_DIR} ({len(manifest)} files + manifest.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
