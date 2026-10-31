"""Unit tests for accounts receivable (RAR) report."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.accounts_receivable_report import (
    RAR_HEADERS,
    invoice_balance,
    invoice_remark,
    invoice_to_rar_row,
    parse_payment_term_days,
    payment_term_days_for_due,
    render_rar_xlsx,
    resolve_invoice_payment_terms,
)


def _inv(**kwargs):
    defaults = {
        "id": 1,
        "tax_invoice_no": "07002600001575917",
        "customer_name": "PT TEST",
        "tax_invoice_date": date(2026, 1, 5),
        "invoice_date": date(2026, 1, 5),
        "receipt_no": "002/01/2025",
        "received_by": "SETO",
        "received_date": date(2026, 1, 5),
        "term_of_payment": "30",
        "due_date": date(2026, 2, 4),
        "total_amount": Decimal("6871.94"),
        "invoice_number": "THIN-M251229010",
        "po_number": "PO-TEST",
        "payment_amount": Decimal("6871.94"),
        "payment_date": date(2026, 3, 2),
        "payment_remark": None,
        "payment_status": "paid",
        "nopen": "000.192",
        "nomor_aju": "00002721147220260105000013",
        "credit_note_no": None,
        "credit_note_date": None,
        "credit_note_amount": None,
        "oia_export_usd": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_parse_payment_term_days():
    assert parse_payment_term_days("30") == 30
    assert parse_payment_term_days("T/T 60 days") == 60
    assert parse_payment_term_days("") is None


def test_payment_term_days_for_due_advance():
    assert payment_term_days_for_due("TT in advance") == 0
    assert payment_term_days_for_due("TT 30 days") == 30
    assert payment_term_days_for_due("") is None


def test_resolve_invoice_payment_terms_from_customer():
    term, due = resolve_invoice_payment_terms(
        customer_payment_terms="TT 30 days",
        term_of_payment=None,
        due_date=None,
        base_date=date(2026, 1, 1),
    )
    assert term == "TT 30 days"
    assert due == date(2026, 1, 31)


def test_resolve_invoice_payment_terms_respects_explicit():
    term, due = resolve_invoice_payment_terms(
        customer_payment_terms="TT 60 days",
        term_of_payment="TT 90 days",
        due_date=date(2026, 3, 1),
        base_date=date(2026, 1, 1),
    )
    assert term == "TT 90 days"
    assert due == date(2026, 3, 1)


def test_invoice_remark_finish_payment():
    inv = _inv()
    assert invoice_remark(inv) == "FINISH PAYMENT"


def test_invoice_remark_not_yet():
    inv = _inv(payment_amount=None, payment_date=None, payment_status="unpaid")
    assert invoice_remark(inv) == "NOT YET"


def test_partial_payment_balance():
    inv = _inv(payment_amount=Decimal("6165"), payment_status="paid", total_amount=Decimal("7089.75"))
    assert invoice_balance(inv) == Decimal("924.75")
    assert invoice_remark(inv) == "NOT YET"


def test_credit_note_reduces_balance():
    inv = _inv(
        payment_amount=Decimal("1000"),
        credit_note_amount=Decimal("200"),
        total_amount=Decimal("1500"),
        payment_status="unpaid",
    )
    assert invoice_balance(inv) == Decimal("300")


def test_invoice_to_rar_row_columns():
    inv = _inv()
    row = invoice_to_rar_row(inv, seq=1, qty=Decimal("6087.6"))
    assert row["tax_invoice_no"] == "07002600001575917"
    assert row["remark"] == "FINISH PAYMENT"
    assert row["qty"] == 6087.6


def test_render_rar_xlsx_has_headers():
    payload = {
        "year": 2026,
        "report_title": "RECAPITULATION ACCOUNT RECEIVABLE 2026",
        "summary": {"qty_total": 1, "amount_faktur_usd": 100, "amount_payment_usd": 100},
        "rar_rows": [invoice_to_rar_row(_inv(), seq=1, qty=Decimal("1"))],
    }
    data = render_rar_xlsx(payload)
    assert len(data) > 500
    assert len(RAR_HEADERS) == 24


def test_build_rar_payload_with_db(monkeypatch):
    from app.services import accounts_receivable_report as mod

    inv = _inv()
    db = MagicMock()
    db.scalars.return_value.all.return_value = [inv]
    db.scalar.return_value = Decimal("100")

    payload = mod.build_rar_payload(db, year=2026)
    assert payload["summary"]["count"] == 1
    assert payload["rows"][0]["customer_name"] == "PT TEST"
