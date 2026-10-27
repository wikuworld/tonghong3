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
    poh = SimpleNamespace(
        id=4, po_number="THIPM26090101", po_customer_ref="", po_category="prod"
    )

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
    # N.W/G.W dari formula packing bila belum ada berat: 12×0.11 / +2×0.3
    assert ctx["lines"][0]["nw"] == Decimal("1.32")
    assert ctx["lines"][0]["gw"] == Decimal("1.92")
    assert ctx["totals"]["nw"] == Decimal("1.32")
    assert ctx["totals"]["gw"] == Decimal("1.92")


def test_invpl_po_no_matches_sj_uses_customer_ref():
    """INVPL PO NO sama aturan SJ: po_customer_ref, bukan No. SO."""
    ph = PackingHeader(id=3, packing_number="MRP-FG-261021000014", source="mrp")
    dh = DeliveryHeader(id=9, packing_id=3, delivery_date=date(2026, 10, 21), customer_id=None)
    dd = SimpleNamespace(
        id=1,
        delivery_id=9,
        po_detail_id=11,
        production_detail_id=None,
        qty=Decimal("120"),
        qty_roll=3,
        qty_pcs=4,
        weight=None,
    )
    pod = SimpleNamespace(
        id=11,
        po_id=4,
        unit_price=Decimal("10"),
        color="ATOMIC VIOLET (55V)",
        master_item_id=None,
        material_name="VIRGIN HYDRO PU",
        style_article=None,
        thickness_text="1.2 - 1.4 mm",
        thickness_min=None,
        thickness_max=None,
    )
    poh = SimpleNamespace(
        id=4,
        po_number="THIPM26102104",
        po_customer_ref="test po cust",
        po_category="prod",
    )

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
    assert ctx["lines"][0]["po_no"] == "test po cust"
    assert ctx["lines"][0]["remark"] == "test po cust"
    assert poh.po_number == "THIPM26102104"
    assert poh.po_customer_ref == "test po cust"


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
    poh = SimpleNamespace(
        id=4, po_number="THIPM26090102", po_customer_ref="", po_category="prod"
    )

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


def test_invpl_nw_gw_from_packing_detail_weight_net():
    from app.models import PackingDetail

    ph = PackingHeader(id=3, packing_number="PK-W", source="erp")
    dh = DeliveryHeader(id=9, packing_id=3, delivery_date=date(2026, 9, 1), customer_id=None)
    pkd = SimpleNamespace(
        id=7,
        packing_id=3,
        production_detail_id=None,
        qty_packed=Decimal("100"),
        qty_roll=3,
        qty_pcs=6,
        weight_net=Decimal("40.50"),
    )
    dd = SimpleNamespace(
        id=1,
        delivery_id=9,
        po_detail_id=11,
        production_detail_id=None,
        packing_detail_id=7,
        qty=Decimal("100"),
        qty_roll=3,
        qty_pcs=6,
        weight=None,
    )
    pod = SimpleNamespace(
        id=11,
        po_id=4,
        unit_price=Decimal("1"),
        color="Black",
        master_item_id=None,
        material_name="PU",
        style_article=None,
        thickness_text=None,
        thickness_min=None,
        thickness_max=None,
    )
    poh = SimpleNamespace(
        id=4, po_number="THIPM26090103", po_customer_ref="", po_category="prod"
    )

    db = MagicMock()

    def _get(model, pk):
        if model is PackingHeader and pk == 3:
            return ph
        if model is DeliveryHeader and pk == 9:
            return dh
        if model is PackingDetail and pk == 7:
            return pkd
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
    assert ctx["lines"][0]["nw"] == Decimal("40.50")
    # G.W = N.W + rolls×0.3 bila gross packing belum ada
    assert ctx["lines"][0]["gw"] == Decimal("41.40")
    assert ctx["totals"]["nw"] == Decimal("40.50")
    assert ctx["totals"]["gw"] == Decimal("41.40")
