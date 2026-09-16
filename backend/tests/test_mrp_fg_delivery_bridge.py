"""Uji bridge FG OUT MRP: taut SJ yang sudah ada, tidak membuat SJ baru."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models import (
    DeliveryHeader,
    PackingHeader,
    PoDetail,
    ProductionDetail,
)
from app.services import mrp_fg_delivery_bridge as bridge
from app.services import po_delivery_balance as bal


def test_sum_delivered_includes_direct_po_detail():
    db = MagicMock()
    # via_production then via_direct
    db.scalars.return_value.one.side_effect = [Decimal("10"), Decimal("25")]
    total = bal.sum_delivered_qty_for_po_detail(db, 7)
    assert total == Decimal("35")


def test_net_delivered_qty_expr_subtracts_returns():
    compiled = str(bal._net_delivered_qty_expr().compile())
    assert "returned_qty" in compiled.lower()


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


def test_resolve_production_prefers_wip_lot():
    db = MagicMock()
    pd = ProductionDetail(id=5, lot_number="WIP-A")
    db.scalars.return_value.first.return_value = pd
    got = bridge._resolve_production_detail_for_wip(
        db, kode_wip="WIP-A", erp_production_detail_id=99
    )
    assert got is pd
    db.get.assert_not_called()


def test_resolve_production_falls_back_to_stamp():
    db = MagicMock()
    db.scalars.return_value.first.return_value = None
    pd = ProductionDetail(id=8, lot_number="WIP-X")
    db.get.return_value = pd
    got = bridge._resolve_production_detail_for_wip(
        db, kode_wip="WIP-MISS", erp_production_detail_id=8
    )
    assert got is pd


def test_bridge_rejects_new_delivery():
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
    assert exc.value.status_code == 400
    assert "outstanding" in str(exc.value.detail).lower()


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


def test_bridge_does_not_create_stub_or_delivery():
    db = MagicMock()

    def _scalars(_stmt):
        result = MagicMock()
        result.first.return_value = None
        return result

    db.scalars.side_effect = _scalars
    added = []
    db.add.side_effect = added.append
    with pytest.raises(HTTPException) as exc:
        bridge.bridge_fg_out_to_delivery(
            db,
            mrp_fg_id=5,
            mrp_packing_id=4,
            kode_packing="FG-99",
            customer_name="Buyer",
            lines=[{"source_detail_id": 11, "qty_out": 10}],
            actor="tester",
        )
    assert exc.value.status_code == 400
    assert "outstanding" in str(exc.value.detail).lower()
    assert added == []


def test_set_delivery_mrp_fg_skips_when_another_sj_has_it():
    db = MagicMock()
    db.scalars.return_value.first.return_value = 10
    dh = DeliveryHeader(id=11, delivery_number="THI-NEW")
    dh.mrp_fg_id = None
    bridge._set_delivery_mrp_fg(db, dh, 9)
    assert dh.mrp_fg_id is None


def test_set_delivery_mrp_fg_assigns_when_free():
    db = MagicMock()
    db.scalars.return_value.first.return_value = None
    dh = DeliveryHeader(id=11, delivery_number="THI-NEW")
    dh.mrp_fg_id = None
    bridge._set_delivery_mrp_fg(db, dh, 9)
    assert dh.mrp_fg_id == 9
