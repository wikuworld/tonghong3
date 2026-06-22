from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.routers.marketing import _delivery_detail_to_row


def test_delivery_row_system_no_is_so_and_po_number_is_customer_ref():
    dh = SimpleNamespace(
        id=1,
        delivery_number="THI-M260407013",
        delivery_date=date(2026, 4, 8),
        destination="",
        status="sent",
        packing_id=10,
        delivery_zone="",
    )
    dd = SimpleNamespace(
        id=100,
        qty=Decimal("1025.5"),
        qty_roll=6,
        qty_pcs=67,
        weight=Decimal("120"),
    )
    ph = SimpleNamespace(
        id=5,
        po_number="THIPM26030516",
        po_customer_ref="4501072445",
        order_date=date(2026, 3, 5),
        buyer="",
        brand_name_snapshot="NIKE",
        customer_name_snapshot="PT CHANGSHIN REKSA JAYA",
        customer_code="CS005",
        factory_code="CS005",
        po_category="production",
        order_type_label="Production",
    )
    pod = SimpleNamespace(
        thi_line_ref="PUMCS005260305001",
        system_reference="",
        material_name="VIRGIN HYDRO PU",
        thickness_text="1.2-1.4",
        color="ANTHRACITE (06F)",
        vir_softness_type="PU COATED(PU)",
        quantity_order=Decimal("1025"),
        unit_price=Decimal("1.21"),
        color_standard="FOLLOW CMP",
        color_reference="",
        emboss="AR-138 M",
        style_article="IQ0098-104",
        model="AIR MAX 90 MESH (GS)",
        detail_remark="",
    )

    row = _delivery_detail_to_row(dd, dh, None, pod, ph, None, None, None, None)

    assert row["system_no"] == "THIPM26030516"
    assert row["po_number"] == "4501072445"
    assert row["lot_no"] == "PUMCS005260305001"
    assert row["buyer"] == "NIKE"
    assert row["surat_jalan_no"] == "THI-C260407013"
