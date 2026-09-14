"""Unit tests: retur baris delivery → credit_note_amount invoice."""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models import DeliveryDetail, DeliveryHeader, PoDetail
from app.services import delivery_return as mod


def test_apply_delivery_line_return_credits_invoice():
    dd = SimpleNamespace(
        id=10,
        delivery_id=5,
        qty=Decimal("100"),
        returned_qty=None,
        po_detail_id=43,
        production_detail_id=None,
    )
    dh = SimpleNamespace(id=5, status="sent")
    pod = SimpleNamespace(id=43, unit_price=Decimal("2.50"))
    inv = SimpleNamespace(
        id=7,
        delivery_id=5,
        invoice_number="THIN-M260901001",
        total_amount=Decimal("250.00"),
        payment_amount=None,
        payment_status="unpaid",
        oia_export_usd=None,
        credit_note_amount=None,
        credit_note_date=None,
        credit_note_no=None,
    )
    invd = SimpleNamespace(
        id=70,
        invoice_id=7,
        qty=Decimal("100"),
        unit_price=Decimal("2.50"),
        amount=Decimal("250.00"),
        remark=None,
    )

    db = MagicMock()
    db.get.side_effect = lambda model, pk: {
        (DeliveryDetail, 10): dd,
        (DeliveryHeader, 5): dh,
        (PoDetail, 43): pod,
    }.get((model, pk))

    with (
        patch.object(mod, "_invoice_for_delivery", return_value=inv),
        patch.object(mod, "_matched_invoice_detail", return_value=invd),
        patch.object(mod, "resolve_po_detail_for_delivery_line", return_value=pod),
    ):
        out = mod.apply_delivery_line_return(db, detail_id=10, qty=Decimal("10"), remark="rusak")

    assert dd.returned_qty == Decimal("10")
    assert inv.credit_note_amount == Decimal("25.00")
    assert inv.credit_note_no == "CN-THIN-M260901001"
    assert inv.credit_note_date is not None
    assert invd.qty == Decimal("90")
    assert invd.amount == Decimal("225.00")
    assert out["credit_amount"] == 25.0
    assert out["remaining_returnable"] == 90.0
    assert "RETUR" in (invd.remark or "")


def test_apply_delivery_line_return_rejects_over_qty():
    dd = SimpleNamespace(
        id=10,
        delivery_id=5,
        qty=Decimal("20"),
        returned_qty=Decimal("15"),
        po_detail_id=None,
        production_detail_id=None,
    )
    dh = SimpleNamespace(id=5, status="sent")
    inv = SimpleNamespace(id=7, delivery_id=5)

    db = MagicMock()
    db.get.side_effect = lambda model, pk: {
        (DeliveryDetail, 10): dd,
        (DeliveryHeader, 5): dh,
    }.get((model, pk))

    with patch.object(mod, "_invoice_for_delivery", return_value=inv):
        with pytest.raises(HTTPException) as ei:
            mod.apply_delivery_line_return(db, detail_id=10, qty=Decimal("10"))
    assert ei.value.status_code == 400
    assert "melebihi" in (ei.value.detail or "").lower()


def test_apply_delivery_line_return_requires_invoice():
    dd = SimpleNamespace(
        id=10,
        delivery_id=5,
        qty=Decimal("20"),
        returned_qty=None,
        po_detail_id=43,
        production_detail_id=None,
    )
    dh = SimpleNamespace(id=5, status="sent")

    db = MagicMock()
    db.get.side_effect = lambda model, pk: {
        (DeliveryDetail, 10): dd,
        (DeliveryHeader, 5): dh,
    }.get((model, pk))

    with patch.object(mod, "_invoice_for_delivery", return_value=None):
        with pytest.raises(HTTPException) as ei:
            mod.apply_delivery_line_return(db, detail_id=10, qty=Decimal("5"))
    assert ei.value.status_code == 400
    assert "invoice" in (ei.value.detail or "").lower()


def test_apply_delivery_line_return_accumulates_credit_note():
    dd = SimpleNamespace(
        id=10,
        delivery_id=5,
        qty=Decimal("50"),
        returned_qty=Decimal("5"),
        po_detail_id=43,
        production_detail_id=None,
    )
    dh = SimpleNamespace(id=5, status="sent")
    pod = SimpleNamespace(id=43, unit_price=Decimal("10"))
    inv = SimpleNamespace(
        id=7,
        delivery_id=5,
        invoice_number="INV-1",
        total_amount=Decimal("500.00"),
        payment_amount=None,
        payment_status="unpaid",
        oia_export_usd=None,
        credit_note_amount=Decimal("50.00"),
        credit_note_date="2026-01-01",
        credit_note_no="CN-INV-1",
    )

    db = MagicMock()
    db.get.side_effect = lambda model, pk: {
        (DeliveryDetail, 10): dd,
        (DeliveryHeader, 5): dh,
    }.get((model, pk))

    with (
        patch.object(mod, "_invoice_for_delivery", return_value=inv),
        patch.object(mod, "_matched_invoice_detail", return_value=None),
        patch.object(mod, "resolve_po_detail_for_delivery_line", return_value=pod),
    ):
        out = mod.apply_delivery_line_return(db, detail_id=10, qty=Decimal("2"))

    assert dd.returned_qty == Decimal("7")
    assert inv.credit_note_amount == Decimal("70.00")
    assert inv.credit_note_no == "CN-INV-1"
    assert out["credit_amount"] == 20.0
    assert out["remaining_returnable"] == 43.0
