from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from fastapi import HTTPException
import pytest

from app.routers.marketing import (
    _classify_line_material_group,
    _delivery_slots,
    _line_to_row,
    _normalize_material_group_filter,
    _passes_mkt_stage_min,
    _po_q_matches,
)


def test_outstanding_row_thi_order_uses_po_number_not_lot():
    header = SimpleNamespace(
        id=1,
        order_date=date(2026, 3, 5),
        po_number="SO-202603-00016",
        po_customer_ref="4501072445",
        brand_name_snapshot="NIKE",
        customer_name_snapshot="PT CHANGSHIN",
        customer_code="CS005",
        customer_id=5,
        factory_code="CS005",
        po_category="production",
        material_followup_remark="",
        material_followup_done=False,
        status="confirmed",
        mkt_workflow_stage="in_outstanding",
        order_type_label="Production",
        etd=date(2026, 4, 1),
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
    assert row["etd"] == "2026-04-01"
    assert row["production_status"] == "in_progress"
    assert row["followup_status"] == "belum"
    assert row["material_followup_remark_header"] == ""


def test_followup_status_dicatat_when_done_before_delivery():
    header = SimpleNamespace(
        id=2,
        order_date=date(2026, 3, 5),
        po_number="SO-2",
        po_customer_ref="PO-2",
        brand_name_snapshot="NIKE",
        customer_name_snapshot="PT X",
        customer_code="X1",
        customer_id=1,
        factory_code="X1",
        po_category="production",
        material_followup_remark="ok",
        material_followup_done=True,
        status="confirmed",
        mkt_workflow_stage="material_followup",
        order_type_label="Production",
    )
    detail = SimpleNamespace(
        id=20,
        thi_line_ref="LOT2",
        system_reference="",
        material_name="PU",
        thickness_text="1.2",
        emboss="",
        vir_softness_type="",
        color="BLACK",
        softness="",
        quantity_order=Decimal("10"),
        unit_price=Decimal("1"),
        color_reference="",
        color_standard="",
        backing="",
        model="",
        style_article="",
        rtd_text="",
        line_etd=None,
        stock_wh_qty=None,
        detail_remark="",
        marketing_outstanding_remark="",
        delivery_schedules=[],
    )
    row = _line_to_row(header, detail, Decimal("0"), Decimal("10"), "")
    assert row["followup_status"] == "dicatat"

    header.mkt_workflow_stage = "delivery_arranged"
    row2 = _line_to_row(header, detail, Decimal("0"), Decimal("10"), "")
    assert row2["followup_status"] == "selesai"


def test_delivery_slots_use_actual_sjs_not_single_plan():
    ln = SimpleNamespace(
        delivery_schedules=[
            SimpleNamespace(sequence_no=1, qty=Decimal("400"), delivery_date=date(2026, 9, 22)),
        ]
    )
    waves = [
        {"qty": Decimal("100"), "date": date(2026, 9, 14)},
        {"qty": Decimal("100"), "date": date(2026, 9, 22)},
        {"qty": Decimal("50"), "date": date(2026, 9, 25)},
    ]
    out = _delivery_slots(ln, actual_waves=waves)
    assert out["delivery_1_qty"] == "100"
    assert out["delivery_1_date"] == "2026-09-14"
    assert out["delivery_2_qty"] == "100"
    assert out["delivery_2_date"] == "2026-09-22"
    assert out["delivery_3_qty"] == "50"
    assert out["delivery_3_date"] == "2026-09-25"


def test_delivery_slots_empty_when_no_actual_even_if_plan_exists():
    """Rencana ada di plan_slots; delivery_N tidak diisi dari jadwal."""
    ln = SimpleNamespace(
        delivery_schedules=[
            SimpleNamespace(sequence_no=1, qty=Decimal("400"), delivery_date=date(2026, 9, 22)),
        ]
    )
    out = _delivery_slots(ln)
    assert out["delivery_1_qty"] == ""
    assert out["delivery_1_date"] == ""
    assert out["delivery_2_qty"] == ""
    assert out["delivery_2_date"] == ""


def test_delivery_slots_empty_waves_list():
    ln = SimpleNamespace(delivery_schedules=[])
    out = _delivery_slots(ln, actual_waves=[])
    assert out["delivery_1_qty"] == ""
    assert out["delivery_1_date"] == ""


def test_delivery_slots_use_actual_sjs_not_single_plan():
    ln = SimpleNamespace(
        delivery_schedules=[
            SimpleNamespace(sequence_no=1, qty=Decimal("400"), delivery_date=date(2026, 9, 22)),
        ]
    )
    waves = [
        {"qty": Decimal("100"), "date": date(2026, 9, 14)},
        {"qty": Decimal("100"), "date": date(2026, 9, 22)},
        {"qty": Decimal("50"), "date": date(2026, 9, 25)},
    ]
    out = _delivery_slots(ln, actual_waves=waves)
    assert out["delivery_1_qty"] == "100"
    assert out["delivery_1_date"] == "2026-09-14"
    assert out["delivery_2_qty"] == "100"
    assert out["delivery_2_date"] == "2026-09-22"
    assert out["delivery_3_qty"] == "50"
    assert out["delivery_3_date"] == "2026-09-25"


def test_delivery_slots_fall_back_to_plan_when_no_actual():
    ln = SimpleNamespace(
        delivery_schedules=[
            SimpleNamespace(sequence_no=1, qty=Decimal("400"), delivery_date=date(2026, 9, 22)),
        ]
    )
    out = _delivery_slots(ln)
    assert out["delivery_1_qty"] == "400"
    assert out["delivery_1_date"] == "2026-09-22"
    assert out["delivery_2_qty"] == ""
    assert out["delivery_2_date"] == ""


def test_normalize_material_group_filter():
    assert _normalize_material_group_filter(None) is None
    assert _normalize_material_group_filter("") is None
    assert _normalize_material_group_filter("PU") == "pu"
    assert _normalize_material_group_filter("Suide") == "suede"
    assert _normalize_material_group_filter("suede") == "suede"
    with pytest.raises(HTTPException) as exc:
        _normalize_material_group_filter("leather")
    assert exc.value.status_code == 400


def test_classify_line_material_group_from_name_and_master():
    header = SimpleNamespace(po_category="production")
    pu_line = SimpleNamespace(material_name="VIRGIN HYDRO PU", vir_softness_type="VIR SOFT")
    suede_line = SimpleNamespace(material_name="SPLIT SUEDE", vir_softness_type="")
    assert _classify_line_material_group(header, pu_line) == "pu"
    assert _classify_line_material_group(header, suede_line) == "suede"

    master_suede = SimpleNamespace(category="Suide")
    ambiguous = SimpleNamespace(material_name="ACTION LEATHER", vir_softness_type="")
    assert _classify_line_material_group(header, ambiguous, master_suede) == "suede"

    legacy = SimpleNamespace(po_category="suede")
    no_hint = SimpleNamespace(material_name="NUBUCK", vir_softness_type="")
    assert _classify_line_material_group(legacy, no_hint) == "suede"


def test_passes_mkt_stage_min_keeps_later_stages():
    assert _passes_mkt_stage_min("input_system", None) is True
    assert _passes_mkt_stage_min("input_system", "in_outstanding") is False
    assert _passes_mkt_stage_min("in_outstanding", "in_outstanding") is True
    assert _passes_mkt_stage_min("delivery_arranged", "in_outstanding") is True
    assert _passes_mkt_stage_min("invoice_billing", "in_outstanding") is True


def test_po_q_matches_so_number_or_customer_po():
    header = SimpleNamespace(po_number="PS26082302", po_customer_ref="cvvv")
    assert _po_q_matches(header, None) is True
    assert _po_q_matches(header, "") is True
    assert _po_q_matches(header, "PS26082302") is True
    assert _po_q_matches(header, "260823") is True
    assert _po_q_matches(header, "CVVV") is True
    assert _po_q_matches(header, "tidak-ada") is False
