"""P.O. NO. Surat Jalan memakai No. PO Customer dari SO."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.marketing_documents import gather_sj_rows, sj_po_no_from_header


def test_sj_po_no_prefers_customer_ref():
    poh = SimpleNamespace(po_customer_ref="4501072445", po_number="THIPM26101401")
    assert sj_po_no_from_header(poh) == "4501072445"


def test_sj_po_no_falls_back_to_internal_when_customer_empty():
    poh = SimpleNamespace(po_customer_ref="  ", po_number="THIPM26101401")
    assert sj_po_no_from_header(poh) == "THIPM26101401"
    assert sj_po_no_from_header(None) == ""


def test_gather_sj_rows_uses_customer_ref_via_po_detail_id():
    poh = SimpleNamespace(
        id=7,
        po_number="THIPM26101401",
        po_customer_ref="CUST-PO-7788",
        po_category="production",
        order_type_label=None,
    )
    pod = SimpleNamespace(
        id=3,
        po_id=7,
        master_item_id=None,
        material_name="ECO TECH",
        thickness_text="1.2-1.4",
        color="NAVY",
        emboss="R-102",
        detail_remark="",
        vir_softness_type="",
        soft_hardness="",
        color_family="",
        color_reference="",
        color_standard="",
        backing="",
        unit_price=None,
        quantity_order=None,
    )
    dd = SimpleNamespace(
        id=1,
        delivery_id=9,
        production_detail_id=None,
        po_detail_id=3,
        qty=1000,
        qty_roll=3,
        qty_pcs=3,
        weight=None,
    )
    dh = SimpleNamespace(
        id=9,
        customer_id=1,
        delivery_number="THI-M261014002",
        delivery_date=None,
        destination="",
        vehicle_number="",
        driver_name="",
        bc_number="",
        bc_date=None,
    )
    cust = SimpleNamespace(name="PT ADIS", address="Jl.", phone="", fax="", is_export_customer=False)

    db = MagicMock()

    def get_side(model, key):
        name = getattr(model, "__name__", str(model))
        if "DeliveryHeader" in name and key == 9:
            return dh
        if "Customer" in name and key == 1:
            return cust
        if "PoDetail" in name and key == 3:
            return pod
        if "PoHeader" in name and key == 7:
            return poh
        return None

    db.get.side_effect = get_side

    def scalars(stmt):
        result = MagicMock()
        text = str(stmt).lower()
        if "invoice" in text:
            result.first.return_value = None
            result.all.return_value = []
        else:
            result.all.return_value = [dd]
            result.first.return_value = dd
        return result

    db.scalars.side_effect = scalars

    ctx = gather_sj_rows(db, 9)
    assert ctx["lines"][0]["po_no"] == "CUST-PO-7788"
