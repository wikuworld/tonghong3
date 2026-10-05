"""HTTP integration tests for invoice router guards and outstanding workbench."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from tests.http_fixtures import (
    DummyDbSession,
    assert_status,
    clear_api_overrides,
    clear_auth_user,
    make_api_client,
    set_auth_user,
)

_PREFIX = "/api/v1"


def test_invoice_list_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/invoice", 401)
    finally:
        clear_api_overrides()


def test_invoice_create_guest_forbidden():
    client = make_api_client()
    set_auth_user("guest")
    try:
        assert_status(client, "POST", f"{_PREFIX}/invoice", 403, {"delivery_id": 1})
    finally:
        clear_api_overrides()


def test_invoice_get_missing_404():
    client = make_api_client()
    set_auth_user("finance")
    try:
        assert_status(client, "GET", f"{_PREFIX}/invoice/999", 404)
    finally:
        clear_api_overrides()


def _invoice_ns(**kw):
    data = dict(
        id=1,
        delivery_id=None,
        customer_id=1,
        po_id=None,
        invoice_number="THIN-C260913001",
        packing_list_number=None,
        po_number="PS26091301",
        customer_name="PT SEJIN FASHION INDONESIA",
        customer_address=None,
        customer_phone=None,
        invoice_date=date(2026, 9, 1),
        description=None,
        term_of_payment="T/T 30 DAYS",
        bank_name=None,
        account_number=None,
        bank_address=None,
        bank_phone=None,
        total_amount=Decimal("1000.00"),
        total_in_words=None,
        due_date=date(2026, 1, 1),
        tax_invoice_no="010.001-26.00000001",
        tax_invoice_date=date(2026, 9, 1),
        receipt_no=None,
        received_by="Budi",
        received_date=date(2026, 9, 10),
        nopen="BC-260908",
        nomor_aju="AJU-1",
        bc_date=date(2026, 9, 8),
        payment_date=None,
        payment_bank_account=None,
        payment_proof_url=None,
        payment_status="unpaid",
        payment_amount=None,
        payment_remark=None,
        credit_note_no=None,
        credit_note_date=None,
        credit_note_amount=Decimal("10.00"),
        oia_export_usd=Decimal("5.00"),
        created_at=None,
    )
    data.update(kw)
    return SimpleNamespace(**data)


class _InvoiceDb(DummyDbSession):
    def __init__(self, invoices, qty=12.5):
        super().__init__()
        self.invoices = list(invoices)
        self.qty = qty

    def scalars(self, _stmt):
        invoices = self.invoices

        class _R:
            def all(self_inner):
                return list(invoices)

            def first(self_inner):
                return invoices[0] if invoices else None

        return _R()

    def scalar(self, _stmt):
        return self.qty

    def get(self, _model, _obj_id):
        return None

    def add(self, _obj):
        return None

    def commit(self):
        return None


def test_invoice_outstanding_returns_ar_fields():
    overdue = _invoice_ns()
    client = make_api_client(_InvoiceDb([overdue]))
    set_auth_user("finance")
    try:
        resp = client.get(f"{_PREFIX}/invoice/outstanding")
        assert resp.status_code == 200, resp.text
        rows = resp.json()
        assert len(rows) == 1
        row = rows[0]
        assert row["ar_status"] == "overdue"
        assert row["deduction_amount"] == 15.0
        assert row["qty_total"] == 12.5
        assert row["dokumen_bc"] == "BC-260908"
        assert row["bc_date"] == "2026-09-08"
        assert row["received_by"] == "Budi"
        assert row["received_date"] == "2026-09-10"
    finally:
        clear_api_overrides()


def test_invoice_outstanding_filter_ar_status_and_q():
    overdue = _invoice_ns(id=1, invoice_number="THIN-OVERDUE", due_date=date(2026, 1, 1))
    current = _invoice_ns(
        id=2,
        invoice_number="THIN-CURRENT",
        due_date=date(2026, 12, 31),
        nopen="NOPEN-XYZ",
        received_by="Sari",
        credit_note_amount=None,
        oia_export_usd=None,
    )
    closed = _invoice_ns(
        id=3,
        invoice_number="THIN-CLOSED",
        due_date=date(2026, 1, 1),
        payment_amount=Decimal("1000.00"),
        payment_status="paid",
        credit_note_amount=None,
        oia_export_usd=None,
    )
    client = make_api_client(_InvoiceDb([overdue, current, closed]))
    set_auth_user("finance")
    try:
        overdue_resp = client.get(f"{_PREFIX}/invoice/outstanding", params={"ar_status": "overdue"})
        assert overdue_resp.status_code == 200, overdue_resp.text
        overdue_rows = overdue_resp.json()
        assert [r["invoice_number"] for r in overdue_rows] == ["THIN-OVERDUE"]

        q_resp = client.get(
            f"{_PREFIX}/invoice/outstanding", params={"q": "CURRENT", "open_only": False}
        )
        assert q_resp.status_code == 200, q_resp.text
        q_rows = q_resp.json()
        assert [r["invoice_number"] for r in q_rows] == ["THIN-CURRENT"]
        assert q_rows[0]["ar_status"] == "not_overdue"
    finally:
        clear_api_overrides()


def test_tanda_terima_batch_rejects_mixed_customers():
    inv1 = _invoice_ns(id=1, customer_id=1, customer_name="A")
    inv2 = _invoice_ns(id=2, customer_id=2, customer_name="B")
    client = make_api_client(_InvoiceDb([inv1, inv2]))
    set_auth_user("finance")
    try:
        with patch("app.routers.documents.log_change"):
            resp = client.post(
                f"{_PREFIX}/documents/tanda-terima/batch/html",
                json={
                    "invoice_ids": [1, 2],
                    "stamp_invoices": False,
                    "receipt_no": "001/09/2026",
                },
            )
        assert resp.status_code == 400, resp.text
        assert "customer" in resp.text.lower()
    finally:
        clear_api_overrides()


def test_tanda_terima_batch_html_title():
    inv = _invoice_ns()
    client = make_api_client(_InvoiceDb([inv]))
    set_auth_user("finance")
    try:
        with patch("app.routers.documents.log_change"):
            resp = client.post(
                f"{_PREFIX}/documents/tanda-terima/batch/html",
                json={
                    "invoice_ids": [1],
                    "stamp_invoices": False,
                    "receipt_no": "056/09/2026",
                    "received_by": "Budi",
                    "received_date": "2026-09-10",
                },
            )
        assert resp.status_code == 200, resp.text
        assert "TANDA TERIMA DOKUMEN TAGIHAN" in resp.text
        assert "THIN-C260913001" in resp.text
    finally:
        clear_api_overrides()
