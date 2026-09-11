"""Unit tests: outstanding status + tanda terima numbering/render."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services.invoice_outstanding import invoice_ar_status, invoice_deduction
from app.services.tanda_terima_documents import (
    allocate_tanda_terima_number,
    render_tanda_terima_html,
    render_tanda_terima_pdf,
)


def test_invoice_ar_status_closed_when_balance_zero():
    inv = SimpleNamespace(
        total_amount=Decimal("100"),
        payment_amount=Decimal("100"),
        credit_note_amount=None,
        oia_export_usd=None,
        due_date=date(2026, 1, 1),
        payment_status="paid",
        term_of_payment=None,
        tax_invoice_date=None,
        invoice_date=date(2025, 12, 1),
    )
    assert invoice_ar_status(inv, today=date(2026, 9, 11)) == "closed"


def test_invoice_ar_status_overdue():
    inv = SimpleNamespace(
        total_amount=Decimal("100"),
        payment_amount=None,
        credit_note_amount=None,
        oia_export_usd=None,
        due_date=date(2026, 1, 1),
        payment_status="unpaid",
        term_of_payment=None,
        tax_invoice_date=None,
        invoice_date=date(2025, 12, 1),
    )
    assert invoice_ar_status(inv, today=date(2026, 9, 11)) == "overdue"


def test_invoice_deduction_sums_cn_and_oia():
    inv = SimpleNamespace(credit_note_amount=Decimal("10"), oia_export_usd=Decimal("5"))
    assert invoice_deduction(inv) == Decimal("15")


def test_allocate_tanda_terima_number_increments():
    db = MagicMock()
    db.scalars.return_value.all.return_value = ["001/09/2026", "NO. 055/09/2026", "bogus"]
    with patch("app.services.tanda_terima_documents.app_now") as now:
        now.return_value.date.return_value = date(2026, 9, 11)
        assert allocate_tanda_terima_number(db, on_date=date(2026, 9, 11)) == "056/09/2026"


def test_render_tanda_terima_html_and_pdf():
    ctx = {
        "document_title": "TANDA TERIMA DOKUMEN TAGIHAN",
        "receipt_no": "056/09/2026",
        "receipt_no_display": "NO. 056/09/2026",
        "customer_name": "PT SEJIN FASHION INDONESIA",
        "received_date_fmt": "September 9, 2026",
        "company_lines": ["PT. TONG HONG TANNERY INDONESIA"],
        "lines": [
            {
                "no": 1,
                "delivery_date_fmt": "08-Sep",
                "invoice_no": "THIN-C260908006",
                "qty_fmt": "805,40",
                "amount_fmt": "$ 1.234,00",
            }
        ],
        "total_amount_fmt": "$ 1.234,00",
    }
    html = render_tanda_terima_html(ctx)
    assert "TANDA TERIMA DOKUMEN TAGIHAN" in html
    assert "NO. 056/09/2026" in html
    assert "THIN-C260908006" in html
    pdf = render_tanda_terima_pdf(ctx)
    assert pdf[:4] == b"%PDF"


def test_gather_requires_same_customer():
    from app.services import tanda_terima_documents as mod

    inv1 = SimpleNamespace(id=1, customer_id=1, customer_name="A")
    inv2 = SimpleNamespace(id=2, customer_id=2, customer_name="B")
    db = MagicMock()
    db.scalars.return_value.all.return_value = [inv1, inv2]
    with pytest.raises(HTTPException) as ei:
        mod.gather_tanda_terima_ctx(db, [1, 2], stamp_invoices=False)
    assert ei.value.status_code == 400
