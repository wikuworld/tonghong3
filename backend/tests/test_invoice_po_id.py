"""Resolver po_id invoice: jalur MRP (po_detail_id) dan packing klasik."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models import DeliveryHeader, PackingHeader, PoDetail, PoHeader, ProductionDetail, ProductionOrder
from app.services.business_rules import po_id_from_delivery


def test_po_id_from_mrp_delivery_via_po_detail_id():
    db = MagicMock()
    dd = SimpleNamespace(po_detail_id=43, production_detail_id=None)
    pod = SimpleNamespace(id=43, po_id=27)
    hdr = SimpleNamespace(packing_id=7)

    db.scalars.return_value.all.return_value = [dd]
    db.get.side_effect = lambda model, pk: {
        (PoDetail, 43): pod,
        (DeliveryHeader, 6): hdr,
        (PackingHeader, 7): SimpleNamespace(production_id=None),
    }.get((model, pk))

    assert po_id_from_delivery(db, 6) == 27


def test_po_id_from_classic_packing_production():
    db = MagicMock()
    db.scalars.return_value.all.return_value = []
    hdr = SimpleNamespace(packing_id=3)
    packing = SimpleNamespace(production_id=9)
    production = SimpleNamespace(po_id=27)

    db.get.side_effect = lambda model, pk: {
        (DeliveryHeader, 6): hdr,
        (PackingHeader, 3): packing,
        (ProductionOrder, 9): production,
    }.get((model, pk))

    assert po_id_from_delivery(db, 6) == 27


def test_po_id_from_production_detail_when_no_direct_po_detail():
    db = MagicMock()
    dd = SimpleNamespace(po_detail_id=None, production_detail_id=10)
    pd = SimpleNamespace(id=10, po_detail_id=43)
    pod = SimpleNamespace(id=43, po_id=27)
    hdr = SimpleNamespace(packing_id=None)

    db.scalars.return_value.all.return_value = [dd]
    db.get.side_effect = lambda model, pk: {
        (ProductionDetail, 10): pd,
        (PoDetail, 43): pod,
        (DeliveryHeader, 6): hdr,
    }.get((model, pk))

    assert po_id_from_delivery(db, 6) == 27


def test_resolve_delivery_line_prefers_direct_po_detail():
    from app.routers.delivery import _resolve_delivery_line_masters

    db = MagicMock()
    dd = SimpleNamespace(po_detail_id=43, production_detail_id=None)
    pod = SimpleNamespace(id=43, po_id=27)
    ph = SimpleNamespace(id=27, po_number="PS26082302", po_customer_ref="cvvv")
    db.get.side_effect = lambda model, pk: {
        (PoDetail, 43): pod,
        (PoHeader, 27): ph,
    }.get((model, pk))

    pd, got_pod, got_ph = _resolve_delivery_line_masters(db, dd)
    assert pd is None
    assert got_pod is pod
    assert got_ph is ph


def test_po_id_none_when_no_chain():
    db = MagicMock()
    db.scalars.return_value.all.return_value = []
    db.get.return_value = None
    assert po_id_from_delivery(db, 99) is None
