from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.routers.marketing import _line_to_row


def test_outstanding_row_thi_order_uses_po_number_not_lot():
    header = SimpleNamespace(
        id=1,
        order_date=date(2026, 3, 5),
        po_number="SO-202603-00016",
        po_customer_ref="4501072445",
        brand_name_snapshot="NIKE",
        customer_name_snapshot="PT CHANGSHIN",
        customer_code="CS005",
        factory_code="CS005",
        po_category="production",
        material_followup_remark="",
        material_followup_done=False,
        status="confirmed",
        mkt_workflow_stage="in_outstanding",
        order_type_label="Production",
    )
    detail = SimpleNamespace(
        id=10,
        thi_line_ref="PUMCS005260305001",
        system_reference="",
        material_name="VIRGIN HYDRO PU",
        thickness_text="1.2-1.4",
        emboss="AR-138 M",
        vir_softness_type="VIR SOFT",
        color="ANTHRACITE (06F)",
        softness="2.8-3.2",
        quantity_order=Decimal("1025"),
        unit_price=Decimal("1.21"),
        color_reference="",
        color_standard="FOLLOW CMP",
        backing="",
        model="IQ0098-104",
        style_article="",
        rtd_text="",
        line_etd=None,
        stock_wh_qty=None,
        detail_remark="",
        marketing_outstanding_remark="",
        delivery_schedules=[],
    )

    row = _line_to_row(header, detail, Decimal("0"), Decimal("1025"), "in_progress")

    assert row["thi_order"] == "SO-202603-00016"
    assert row["no_po"] == "4501072445"
    assert row["po_customer_ref"] == "4501072445"
    assert row["system_reference"] == "PUMCS005260305001"
