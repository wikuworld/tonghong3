"""INVPL memakai delivery_details jika packing_details kosong (stub MRP)."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models import DeliveryHeader, PackingHeader, PoDetail, PoHeader
from app.services.marketing_documents import gather_invpl_rows


def test_invpl_from_delivery_details_when_packing_empty():
    ph = PackingHeader(id=3, packing_number="MRP-FG-1", source="mrp")
    dh = DeliveryHeader(id=9, packing_id=3, delivery_date=date(2026, 9, 1), customer_id=None)
    dd = SimpleNamespace(
        id=1,
        delivery_id=9,
        po_detail_id=11,
        production_detail_id=None,
        qty=Decimal("12"),
        qty_roll=2,
        qty_pcs=None,
        weight=None,
    )
    pod = SimpleNamespace(
        id=11,
        po_id=4,
        unit_price=Decimal("1.5"),
        color="Black",
        master_item_id=None,
        material_name="PVC",
        style_article=None,
        thickness_text=None,
        thickness_min=None,
        thickness_max=None,
    )
    poh = SimpleNamespace(id=4, po_number="THIPM26090101", po_category="prod")

    db = MagicMock()

    def _get(model, pk):
        if model is PackingHeader and pk == 3:
            return ph
        if model is DeliveryHeader and pk == 9:
            return dh
        if model is PoDetail and pk == 11:
            return pod
        if model is PoHeader and pk == 4:
            return poh
        return None

    db.get.side_effect = _get

    firsts = iter([None])

    def _scalars(_stmt):
        result = MagicMock()
        result.all.return_value = [dd]
        result.first.side_effect = lambda: next(firsts, None)
        return result

    db.scalars.side_effect = _scalars

    ctx = gather_invpl_rows(db, 3, delivery_id=9)
    assert ctx["lines"]
    assert ctx["lines"][0]["qty"] == Decimal("12")
    assert ctx["lines"][0]["po_no"] == "THIPM26090101"
    assert ctx["totals"]["qty"] == Decimal("12")


def test_invpl_from_delivery_ignores_packing_mismatch():
    ph = PackingHeader(id=3, packing_number="PK-A", source="mrp")
    dh = DeliveryHeader(id=9, packing_id=99, delivery_date=date(2026, 9, 1), customer_id=None)
    dd = SimpleNamespace(
        id=1,
        delivery_id=9,
        po_detail_id=11,
        production_detail_id=None,
        qty=Decimal("5"),
        qty_roll=1,
        qty_pcs=None,
        weight=None,
    )
    pod = SimpleNamespace(
        id=11,
        po_id=4,
        unit_price=Decimal("2"),
        color="Red",
        master_item_id=None,
        material_name="PU",
        style_article=None,
        thickness_text=None,
        thickness_min=None,
        thickness_max=None,
    )
    poh = SimpleNamespace(id=4, po_number="THIPM26090102", po_category="prod")

    db = MagicMock()

    def _get(model, pk):
        if model is PackingHeader and pk == 3:
            return ph
        if model is DeliveryHeader and pk == 9:
            return dh
        if model is PoDetail and pk == 11:
            return pod
        if model is PoHeader and pk == 4:
            return poh
        return None

    db.get.side_effect = _get
    firsts = iter([None])

    def _scalars(_stmt):
        result = MagicMock()
        result.all.return_value = [dd]
        result.first.side_effect = lambda: next(firsts, None)
        return result

    db.scalars.side_effect = _scalars
    ctx = gather_invpl_rows(db, 3, delivery_id=9)
    assert ctx["lines"][0]["qty"] == Decimal("5")
    assert ctx["packing_number"] == "PK-A"
