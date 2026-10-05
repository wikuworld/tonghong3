"""Create paths auto-assign QC/DEL/INV numbers when blank; keep explicit numbers."""

from __future__ import annotations

from datetime import date
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.models import DeliveryHeader, Invoice, QcHeader
from app.routers import delivery as delivery_router
from app.routers import invoice as invoice_router
from app.routers import qc as qc_router
from app.schemas import (
    DeliveryFromPackingLinesIn,
    DeliveryHeaderCreate,
    InvoiceCreate,
    QcHeaderCreate,
)


class _RecordingDb:
    def __init__(self, *, get_map=None):
        self.get_map = get_map or {}
        self.added: list = []
        self._id = 100

    def get(self, model, obj_id):
        return self.get_map.get((model, obj_id))

    def add(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = self._id
            self._id += 1
        self.added.append(obj)

    def flush(self):
        return None

    def commit(self):
        return None

    def refresh(self, _obj):
        return None

    def scalars(self, _stmt):
        class _Empty:
            def first(self):
                return None

            def all(self):
                return []

        return _Empty()


@pytest.fixture
def user():
    return SimpleNamespace(username="tester", role="admin")


def test_qc_create_auto_number(monkeypatch, user):
    db = _RecordingDb()
    monkeypatch.setattr(qc_router, "next_number", lambda _db, doc, prefix: f"{prefix}-202609-00001")
    monkeypatch.setattr(qc_router, "log_change", lambda *a, **k: None)

    with pytest.raises(HTTPException) as exc:
        qc_router.create_qc_header(
            QcHeaderCreate(production_id=None, qc_date=date(2026, 9, 5)),
            db=db,
            user=user,
        )
    assert exc.value.status_code == 403
    assert "buku" in str(exc.value.detail).lower() or "mrp" in str(exc.value.detail).lower()


def test_qc_create_keeps_explicit_number(monkeypatch, user):
    db = _RecordingDb()
    monkeypatch.setattr(
        qc_router,
        "next_number",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("should not call next_number")),
    )
    monkeypatch.setattr(qc_router, "log_change", lambda *a, **k: None)

    with pytest.raises(HTTPException) as exc:
        qc_router.create_qc_header(
            QcHeaderCreate(qc_number="QC-CUSTOM-1", qc_date=date(2026, 9, 5)),
            db=db,
            user=user,
        )
    assert exc.value.status_code == 403


def test_delivery_create_auto_number(monkeypatch, user):
    db = _RecordingDb()
    monkeypatch.setattr(delivery_router, "require_packing_ready", lambda *_a, **_k: None)
    monkeypatch.setattr(
        delivery_router,
        "allocate_surat_jalan_number",
        lambda *_a, **_k: "DEL-202609-00007",
    )
    monkeypatch.setattr(delivery_router, "log_change", lambda *a, **k: None)
    monkeypatch.setattr(delivery_router, "po_numbers_from_delivery", lambda *_a, **_k: [])
    monkeypatch.setattr(
        "app.services.delivery_auto_invoice.ensure_invoice_for_delivery",
        lambda *_a, **_k: None,
    )

    row = delivery_router.create_delivery(
        DeliveryHeaderCreate(packing_id=1, status="draft"),
        db=db,
        user=user,
    )
    assert isinstance(row, DeliveryHeader)
    assert row.delivery_number == "DEL-202609-00007"


def test_delivery_create_keeps_explicit_number(monkeypatch, user):
    db = _RecordingDb()
    monkeypatch.setattr(delivery_router, "require_packing_ready", lambda *_a, **_k: None)
    monkeypatch.setattr(
        delivery_router,
        "allocate_surat_jalan_number",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("should not allocate")),
    )
    monkeypatch.setattr(delivery_router, "log_change", lambda *a, **k: None)
    monkeypatch.setattr(delivery_router, "po_numbers_from_delivery", lambda *_a, **_k: [])
    monkeypatch.setattr(
        "app.services.delivery_auto_invoice.ensure_invoice_for_delivery",
        lambda *_a, **_k: None,
    )

    row = delivery_router.create_delivery(
        DeliveryHeaderCreate(packing_id=1, delivery_number="DEL-CUSTOM", status="draft"),
        db=db,
        user=user,
    )
    assert row.delivery_number == "DEL-CUSTOM"


def test_delivery_from_packing_lines_auto_number(monkeypatch, user):
    db = _RecordingDb()
    monkeypatch.setattr(delivery_router, "require_packing_ready", lambda *_a, **_k: None)
    monkeypatch.setattr(
        delivery_router,
        "validate_same_customer_and_brand",
        lambda *_a, **_k: (10, "NIKE"),
    )
    monkeypatch.setattr(
        delivery_router,
        "allocate_surat_jalan_number",
        lambda *_a, **_k: "DEL-202609-00009",
    )
    monkeypatch.setattr(delivery_router, "_has_qc_ok", lambda *_a, **_k: True)
    monkeypatch.setattr(delivery_router, "qty_available_for_packing_line", lambda *a, **k: 100)
    monkeypatch.setattr(delivery_router, "validate_delivery_qty_against_po_balance", lambda *a, **k: None)
    monkeypatch.setattr(delivery_router, "log_change", lambda *a, **k: None)
    monkeypatch.setattr(delivery_router, "po_numbers_from_delivery", lambda *_a, **_k: [])
    monkeypatch.setattr(delivery_router, "sync_mkt_workflow_auto_advance", lambda *a, **k: None)
    monkeypatch.setattr(
        "app.services.delivery_auto_invoice.ensure_invoice_for_delivery",
        lambda *_a, **_k: None,
    )

    body = DeliveryFromPackingLinesIn(
        packing_id=1,
        customer_id=10,
        delivery_date=date(2026, 9, 5),
        delivery_type="production",
        lines=[{"production_detail_id": 5, "qty": 10}],
    )
    row = delivery_router.create_delivery_from_packing_lines(body, db=db, user=user)
    assert row.delivery_number == "DEL-202609-00009"


def test_invoice_create_auto_number(monkeypatch, user):
    delivery = SimpleNamespace(id=1, customer_id=10, packing_id=None, delivery_date=date(2026, 9, 5))
    db = _RecordingDb(get_map={(DeliveryHeader, 1): delivery})
    monkeypatch.setattr(invoice_router, "validate_invoice_against_delivery", lambda *_a, **_k: None)
    monkeypatch.setattr(
        invoice_router,
        "allocate_invoice_number",
        lambda *_a, **_k: "THIN-M260905001",
    )
    monkeypatch.setattr(invoice_router, "log_change", lambda *a, **k: None)
    monkeypatch.setattr(invoice_router, "create_notification_for_roles", lambda *a, **k: None)
    monkeypatch.setattr(invoice_router, "sync_invoice_billing_from_delivery", lambda *_a, **_k: None)
    monkeypatch.setattr(invoice_router, "po_id_from_delivery", lambda *_a, **_k: None)
    monkeypatch.setattr(invoice_router, "joined_po_numbers_for_delivery", lambda *_a, **_k: None)

    row = invoice_router.create_invoice(
        InvoiceCreate(delivery_id=1, invoice_date=date(2026, 9, 5)),
        db=db,
        user=user,
    )
    assert isinstance(row, Invoice)
    assert row.invoice_number == "THIN-M260905001"


def test_invoice_create_keeps_explicit_number(monkeypatch, user):
    delivery = SimpleNamespace(id=1, customer_id=10, packing_id=None)
    db = _RecordingDb(get_map={(DeliveryHeader, 1): delivery})
    monkeypatch.setattr(invoice_router, "validate_invoice_against_delivery", lambda *_a, **_k: None)
    monkeypatch.setattr(
        invoice_router,
        "allocate_invoice_number",
        lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("should not allocate")),
    )
    monkeypatch.setattr(invoice_router, "log_change", lambda *a, **k: None)
    monkeypatch.setattr(invoice_router, "create_notification_for_roles", lambda *a, **k: None)
    monkeypatch.setattr(invoice_router, "sync_invoice_billing_from_delivery", lambda *_a, **_k: None)
    monkeypatch.setattr(invoice_router, "po_id_from_delivery", lambda *_a, **_k: None)
    monkeypatch.setattr(invoice_router, "joined_po_numbers_for_delivery", lambda *_a, **_k: None)

    row = invoice_router.create_invoice(
        InvoiceCreate(delivery_id=1, invoice_number="INV-PO-CUSTOM", invoice_date=date(2026, 9, 5)),
        db=db,
        user=user,
    )
    assert row.invoice_number == "INV-PO-CUSTOM"
