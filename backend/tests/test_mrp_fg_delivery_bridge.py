"""Uji bridge FG OUT MRP → Delivery draft + saldo PO langsung."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models import DeliveryDetail, DeliveryHeader, PackingHeader, PoDetail, PoHeader
from app.services import mrp_fg_delivery_bridge as bridge
from app.services import po_delivery_balance as bal


def test_sum_delivered_includes_direct_po_detail():
    db = MagicMock()
    # via_production then via_direct
    db.scalars.return_value.one.side_effect = [Decimal("10"), Decimal("25")]
    total = bal.sum_delivered_qty_for_po_detail(db, 7)
    assert total == Decimal("35")


def test_validate_delivery_qty_with_po_detail_id():
    db = MagicMock()
    pod = PoDetail(id=7, quantity_order=Decimal("100"))
    db.get.side_effect = lambda model, pk: pod if model is PoDetail and pk == 7 else None
    db.scalars.return_value.one.side_effect = [Decimal("0"), Decimal("0")]
    bal.validate_delivery_qty_against_po_balance(db, po_detail_id=7, qty=Decimal("40"))

    db.scalars.return_value.one.side_effect = [Decimal("80"), Decimal("0")]
    with pytest.raises(HTTPException) as exc:
        bal.validate_delivery_qty_against_po_balance(db, po_detail_id=7, qty=Decimal("40"))
    assert exc.value.status_code == 400


def test_bridge_rejects_empty_lines():
    db = MagicMock()
    db.scalars.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        bridge.bridge_fg_out_to_delivery(
            db,
            mrp_fg_id=1,
            mrp_packing_id=2,
            kode_packing="FG-1",
            customer_name="Acme",
            lines=[],
        )
    assert "source_detail_id" in str(exc.value.detail).lower() or "sync po" in str(exc.value.detail).lower()


def test_bridge_idempotent_returns_existing():
    db = MagicMock()
    existing = DeliveryHeader(id=99, delivery_number="DEL-1", packing_id=50, mrp_fg_id=3)
    pk = PackingHeader(id=50, packing_number="MRP-FG-1", mrp_fg_id=3)
    db.scalars.return_value.first.return_value = existing
    db.get.return_value = pk
    result = bridge.bridge_fg_out_to_delivery(
        db,
        mrp_fg_id=3,
        mrp_packing_id=2,
        kode_packing="FG-1",
        customer_name="Acme",
        lines=[{"source_detail_id": 1, "qty_out": 10}],
    )
    assert result.created is False
    assert result.delivery_id == 99
    assert result.delivery_number == "DEL-1"


def test_bridge_creates_stub_and_delivery(monkeypatch):
    db = MagicMock()

    def _scalars(stmt):
        result = MagicMock()
        result.first.return_value = None
        result.one.return_value = Decimal("0")
        return result

    db.scalars.side_effect = _scalars

    ph = PoHeader(id=1, po_number="PO-1", customer_id=9, status="confirmed")
    pod = PoDetail(id=11, po_id=1, quantity_order=Decimal("500"), balance_qty=Decimal("500"))

    def _get(model, pk):
        if model is PoDetail and pk == 11:
            return pod
        if model is PoHeader and pk == 1:
            return ph
        return None

    db.get.side_effect = _get

    nums = iter(["PACK-X", "DEL-X"])

    monkeypatch.setattr(bridge, "next_number", lambda *_a, **_k: next(nums))
    monkeypatch.setattr(bridge, "log_change", lambda *a, **k: None)
    monkeypatch.setattr(bridge, "validate_delivery_qty_against_po_balance", lambda *a, **k: None)
    monkeypatch.setattr(bridge, "sync_po_detail_balance_qty", lambda *a, **k: Decimal("490"))

    added = []

    def _add(obj):
        added.append(obj)
        if isinstance(obj, PackingHeader):
            obj.id = 70
        if isinstance(obj, DeliveryHeader):
            obj.id = 80
        if isinstance(obj, DeliveryDetail):
            obj.id = 90

    db.add.side_effect = _add

    result = bridge.bridge_fg_out_to_delivery(
        db,
        mrp_fg_id=5,
        mrp_packing_id=4,
        kode_packing="FG-99",
        customer_name="Buyer",
        lines=[{"source_detail_id": 11, "qty_out": 10}],
        actor="tester",
    )
    assert result.created is True
    assert result.delivery_id == 80
    assert result.packing_id == 70
    assert any(isinstance(x, PackingHeader) and x.source == "mrp" for x in added)
    assert any(isinstance(x, DeliveryHeader) and x.status == "draft" for x in added)
    assert any(
        isinstance(x, DeliveryDetail) and x.po_detail_id == 11 and x.qty == Decimal("10")
        for x in added
    )
