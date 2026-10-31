"""Auto-invoice THIN saat Surat Jalan dibuat."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models import DeliveryDetail, DeliveryHeader, Invoice
from app.services import delivery_auto_invoice as auto_inv
from app.services.business_rules import validate_invoice_against_delivery


class _Scalars:
    def __init__(self, rows):
        self._rows = rows

    def first(self):
        return self._rows[0] if self._rows else None

    def all(self):
        return list(self._rows)


class _Db:
    def __init__(self):
        self.added = []
        self._id = 50
        self.get_map = {}
        self.invoice_rows = []
        self.detail_rows = []

    def get(self, model, obj_id):
        return self.get_map.get((model, obj_id))

    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = self._id
            self._id += 1
        self.added.append(obj)
        if isinstance(obj, Invoice):
            self.invoice_rows.append(obj)

    def flush(self):
        return None

    def scalars(self, stmt):
        # Rough routing by stringified statement / called context
        text = str(stmt).lower()
        if "invoices" in text or "invoice" in text:
            return _Scalars(self.invoice_rows)
        if "delivery_details" in text or "deliverydetail" in text:
            return _Scalars(self.detail_rows)
        return _Scalars([])


def test_validate_allows_draft_when_flag_set():
    db = MagicMock()
    hdr = SimpleNamespace(id=1, status="draft", packing_id=9)
    detail = SimpleNamespace(id=1, delivery_id=1)
    db.get.return_value = hdr
    db.scalars.side_effect = [
        _Scalars([]),  # existing invoice
        _Scalars([detail]),  # details
    ]
    validate_invoice_against_delivery(db, 1, None, allow_draft=True)


def test_validate_rejects_draft_by_default():
    db = MagicMock()
    hdr = SimpleNamespace(id=1, status="draft", packing_id=9)
    db.get.return_value = hdr
    db.scalars.return_value = _Scalars([])
    with pytest.raises(HTTPException) as exc:
        validate_invoice_against_delivery(db, 1, None)
    assert exc.value.status_code == 400
    assert "sent" in str(exc.value.detail).lower()


def test_ensure_invoice_creates_thin(monkeypatch):
    from app.models import Customer

    db = _Db()
    delivery = SimpleNamespace(
        id=7,
        status="draft",
        packing_id=3,
        customer_id=11,
        delivery_date=date(2026, 9, 17),
    )
    cust = SimpleNamespace(
        id=11,
        name="PT TEST",
        address="Jl. A",
        phone="081",
        payment_terms="TT 30 days",
    )
    db.get_map[(DeliveryHeader, 7)] = delivery
    db.get_map[(Customer, 11)] = cust
    db.detail_rows = [SimpleNamespace(id=1, delivery_id=7)]

    monkeypatch.setattr(
        auto_inv,
        "ensure_invoice_for_delivery",
        auto_inv.ensure_invoice_for_delivery,
    )

    # Patch nested imports used inside ensure
    import app.services.delivery_auto_invoice as mod

    def _fake_validate(*_a, **_k):
        return None

    monkeypatch.setattr(
        "app.services.business_rules.validate_invoice_against_delivery",
        _fake_validate,
    )
    monkeypatch.setattr(
        "app.services.business_rules.po_id_from_delivery",
        lambda *_a, **_k: None,
    )
    monkeypatch.setattr(
        "app.services.business_rules.joined_po_numbers_for_delivery",
        lambda *_a, **_k: "SO-1",
    )
    monkeypatch.setattr(
        "app.services.document_numbers.allocate_invoice_number",
        lambda *_a, **_k: "THIN-M260917001",
    )
    monkeypatch.setattr("app.services.audit.log_change", lambda *a, **k: None)
    monkeypatch.setattr(
        "app.services.notifications.create_notification_for_roles",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "app.services.mkt_workflow.sync_invoice_billing_from_delivery",
        lambda *_a, **_k: None,
    )

    # Re-bind get for DeliveryHeader after imports inside function
    row = mod.ensure_invoice_for_delivery(db, 7, actor="tester")
    assert row is not None
    assert row.invoice_number == "THIN-M260917001"
    assert row.delivery_id == 7
    assert isinstance(row, Invoice)
    assert row.term_of_payment == "TT 30 days"
    assert row.due_date == date(2026, 10, 17)


def test_ensure_invoice_idempotent(monkeypatch):
    db = _Db()
    existing = Invoice(delivery_id=7, invoice_number="THIN-EXISTING")
    existing.id = 99
    db.invoice_rows = [existing]
    db.detail_rows = [SimpleNamespace(id=1, delivery_id=7)]
    db.get_map[(DeliveryHeader, 7)] = SimpleNamespace(
        id=7, status="draft", packing_id=1, customer_id=None, delivery_date=None
    )

    monkeypatch.setattr(
        "app.services.document_numbers.allocate_invoice_number",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("should not allocate")),
    )
    row = auto_inv.ensure_invoice_for_delivery(db, 7, actor="t")
    assert row is existing
    assert row.invoice_number == "THIN-EXISTING"


def test_ensure_skips_without_details():
    db = _Db()
    db.get_map[(DeliveryHeader, 7)] = SimpleNamespace(id=7, status="draft")
    db.detail_rows = []
    assert auto_inv.ensure_invoice_for_delivery(db, 7) is None
