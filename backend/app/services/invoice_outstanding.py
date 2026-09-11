"""Enrichment outstanding invoice + status AR."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models import DeliveryHeader, Invoice
from app.services.accounts_receivable_report import (
    enrich_invoice_out,
    invoice_balance,
    invoice_maturity,
)


def _dec(v: Any) -> Decimal:
    if v is None or v == "":
        return Decimal(0)
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal(0)


def invoice_deduction(inv: Invoice) -> Decimal:
    return _dec(inv.credit_note_amount) + _dec(inv.oia_export_usd)


def invoice_ar_status(inv: Invoice, *, today: date | None = None) -> str:
    """closed | overdue | not_overdue"""
    today = today or date.today()
    if invoice_balance(inv) <= 0:
        return "closed"
    maturity = invoice_maturity(inv)
    if maturity and maturity < today:
        return "overdue"
    return "not_overdue"


def sync_payment_status_from_balance(inv: Invoice) -> None:
    """Set payment_status paid/unpaid dari saldo."""
    if invoice_balance(inv) <= 0:
        inv.payment_status = "paid"
    elif (inv.payment_status or "").lower() == "paid":
        inv.payment_status = "unpaid"


def enrich_outstanding_invoice(db: Session, inv: Invoice, *, hide_po: bool = False) -> dict[str, Any]:
    data = enrich_invoice_out(inv, db)
    data["deduction_amount"] = float(invoice_deduction(inv))
    data["ar_status"] = invoice_ar_status(inv)
    maturity = invoice_maturity(inv)
    if maturity and not data.get("due_date"):
        data["due_date"] = maturity.isoformat()

    # Fallback Dokumen BC dari delivery bila invoice kosong
    bc_number = (inv.nopen or "").strip()
    bc_date = getattr(inv, "bc_date", None)
    if inv.delivery_id and (not bc_number or bc_date is None):
        dh = db.get(DeliveryHeader, int(inv.delivery_id))
        if dh:
            if not bc_number:
                bc_number = (dh.bc_number or "").strip()
            if bc_date is None:
                bc_date = dh.bc_date
    data["bc_number"] = bc_number or None
    data["bc_date"] = bc_date.isoformat() if bc_date else None
    # Alias tampilan list
    data["dokumen_bc"] = data["bc_number"]
    if hide_po:
        data["po_number"] = None
    return data


def filter_outstanding_rows(
    rows: list[dict[str, Any]],
    *,
    ar_status: Optional[str] = None,
    open_only: bool = False,
    customer_id: Optional[int] = None,
    q: Optional[str] = None,
) -> list[dict[str, Any]]:
    out = rows
    if open_only:
        out = [r for r in out if (r.get("ar_status") or "") != "closed"]
    if ar_status:
        key = ar_status.strip().lower().replace(" ", "_")
        # accept not-overdue / not_overdue
        key = key.replace("-", "_")
        out = [r for r in out if (r.get("ar_status") or "") == key]
    if customer_id is not None:
        out = [r for r in out if r.get("customer_id") == int(customer_id)]
    if q and str(q).strip():
        needle = str(q).strip().lower()
        filtered = []
        for r in out:
            hay = " ".join(
                str(r.get(k) or "")
                for k in (
                    "invoice_number",
                    "customer_name",
                    "po_number",
                    "tax_invoice_no",
                    "receipt_no",
                    "bc_number",
                    "nopen",
                    "nomor_aju",
                    "received_by",
                )
            ).lower()
            if needle in hay:
                filtered.append(r)
        out = filtered
    return out
