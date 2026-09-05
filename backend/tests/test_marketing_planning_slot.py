from decimal import Decimal
from types import SimpleNamespace

from app.routers.marketing import _planning_slot_ship_status, _po_q_matches


def test_planning_slot_ship_status_by_stage_and_balance():
    assert _planning_slot_ship_status("input_system", Decimal("0"), Decimal("2000")) == "too_early"
    assert _planning_slot_ship_status("with_ppic", Decimal("100"), Decimal("2000")) == "too_early"
    assert _planning_slot_ship_status("in_outstanding", Decimal("0"), Decimal("2000")) == "planned"
    assert _planning_slot_ship_status("material_followup", Decimal("500"), Decimal("2000")) == "partial"
    assert _planning_slot_ship_status("delivery_arranged", Decimal("2000"), Decimal("2000")) == "shipped"
    assert _planning_slot_ship_status("invoice_billing", Decimal("2100"), Decimal("2000")) == "shipped"


def test_planning_po_q_matches_so_or_customer_ref():
    header = SimpleNamespace(po_number="PS26082302", po_customer_ref="cvvv")
    assert _po_q_matches(header, "PS26082302") is True
    assert _po_q_matches(header, "cvvv") is True
    assert _po_q_matches(header, "tidak-ada") is False
