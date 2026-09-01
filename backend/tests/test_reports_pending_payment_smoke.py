"""HTTP smoke tests for Pending Payment (Report Mr. Bob) API."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from openpyxl import load_workbook

from app.services.pending_payment_report import PENDING_PAYMENT_HEADERS
from tests.http_fixtures import (
    clear_api_overrides,
    clear_auth_user,
    make_api_client,
    set_auth_user,
)

_PREFIX = "/api/v1"


def _overdue_inv():
    return SimpleNamespace(
        id=1,
        customer_name="FENG TAY ENTERPRISE CO., LTD",
        tax_invoice_date=date(2026, 3, 30),
        invoice_date=date(2026, 3, 30),
        due_date=date(2026, 5, 30),
        term_of_payment="30",
        total_amount=Decimal("55.32"),
        payment_amount=None,
        payment_date=None,
        payment_remark="STILL WAITING FEEDBACK EMAIL",
        payment_status="unpaid",
        credit_note_amount=None,
        oia_export_usd=None,
    )


def _pp_db():
    db = MagicMock()
    db.scalars.return_value.all.return_value = [_overdue_inv()]
    return db


@pytest.fixture(autouse=True)
def _cleanup_overrides():
    yield
    clear_api_overrides()


def test_pending_payment_json_requires_auth():
    client = make_api_client(_pp_db())
    clear_auth_user()
    resp = client.get(f"{_PREFIX}/reports/pending-payment")
    assert resp.status_code == 401


def test_pending_payment_json_ok():
    client = make_api_client(_pp_db())
    set_auth_user("finance")
    resp = client.get(f"{_PREFIX}/reports/pending-payment", params={"as_of": "2026-08-28", "year": 2026})
    assert resp.status_code == 200
    body = resp.json()
    assert "Pending Payment 2026" in body["report_title"]
    assert body["summary"]["overdue_customer_count"] == 1
    feng = next(r for r in body["rows"] if r["customer"] == "FENG TAY ENTERPRISE CO., LTD")
    assert feng["amount_usd"] == 55.32


def test_pending_payment_xlsx_forbidden_marketing():
    client = make_api_client(_pp_db())
    set_auth_user("marketing")
    resp = client.get(f"{_PREFIX}/reports/pending-payment.xlsx")
    assert resp.status_code == 403


def test_pending_payment_xlsx_ok_finance():
    client = make_api_client(_pp_db())
    set_auth_user("finance")
    resp = client.get(f"{_PREFIX}/reports/pending-payment.xlsx", params={"as_of": "2026-08-28"})
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    wb = load_workbook(BytesIO(resp.content), read_only=True, data_only=True)
    headers = [wb.active.cell(row=3, column=c).value for c in range(1, 11)]
    assert headers == PENDING_PAYMENT_HEADERS
