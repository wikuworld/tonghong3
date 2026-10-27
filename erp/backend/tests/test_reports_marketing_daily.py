"""Unit tests for marketing daily report payload (revise audit + category buckets)."""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.routers.reports import (
    _build_marketing_daily_payload,
    _diff_po_line_audit,
    _normalize_po_category_bucket,
)


def test_diff_po_line_audit_detects_qty_change():
    before = {"po_id": 1, "quantity_order": 100, "thickness_text": "1.2 - 1.4"}
    after = {"po_id": 1, "quantity_order": 150, "thickness_text": "1.2 - 1.4"}
    changed, summary, old_vals, new_vals = _diff_po_line_audit(before, after)
    assert "quantity_order" in changed
    assert "thickness_text" not in changed
    assert "Qty" in summary
    assert "100" in old_vals and "150" in new_vals


def test_normalize_po_category_bucket():
    assert _normalize_po_category_bucket(None) == "production"
    assert _normalize_po_category_bucket("suede") == "production"
    assert _normalize_po_category_bucket("claim") == "claim"
    assert _normalize_po_category_bucket("subkon") == "subcont"
    assert _normalize_po_category_bucket("subcont") == "subcont"


def _header(**kwargs):
    defaults = {
        "id": 1,
        "po_number": "PS26082701",
        "po_customer_ref": "REF-1",
        "customer_name_snapshot": "PT TEST",
        "customer_code": "T001",
        "brand_name_snapshot": "NIKE",
        "order_type_label": None,
        "buyer": "NIKE",
        "order_date": date(2026, 8, 27),
        "created_at": datetime(2026, 8, 27, 8, 0, 0),
        "po_category": "production",
        "status": "confirmed",
        "details": [],
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _detail(**kwargs):
    defaults = {
        "id": 10,
        "po_id": 1,
        "copied_from_detail_id": None,
        "thi_line_ref": "LOT-001",
        "material_name": "ACTION PU",
        "thickness_text": "1.2 - 1.4",
        "thickness_min": None,
        "thickness_max": None,
        "emboss": "DE-7",
        "vir_softness_type": "",
        "color": "BLACK",
        "softness": "",
        "unit_price": Decimal("1.5"),
        "color_reference": "",
        "backing": "",
        "model": "",
        "style_article": "",
        "rtd_text": "",
        "detail_remark": "",
        "system_reference": "",
        "line_etd": None,
        "quantity_order": Decimal("100"),
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_claim_not_in_production_bucket():
    claim_h = _header(id=2, po_number="CL26082701", po_category="claim")
    claim_ln = _detail(id=20, po_id=2, material_name="CLAIM MAT")
    claim_h.details = [claim_ln]
    prod_h = _header(id=1, po_category="production")
    prod_ln = _detail(id=10, po_id=1)
    prod_h.details = [prod_ln]

    db = MagicMock()
    db.scalars.return_value.all.side_effect = [
        [prod_h, claim_h],  # headers
        [],  # audit logs
    ]
    db.get.return_value = None

    payload = _build_marketing_daily_payload(db, date(2026, 8, 27), date(2026, 8, 27), None, "order")
    assert len(payload["production_orders"]) == 1
    assert payload["production_orders"][0]["poNo"] == "PS26082701"
    assert len(payload["claim_orders"]) == 1
    assert payload["claim_orders"][0]["po_category"] == "claim"
    assert payload["samples"] == []
    assert payload["return_orders"] == []
    assert payload["subcont_orders"] == []


def test_revise_from_audit_qty_in_date_range():
    h = _header(id=5, po_number="PS26082601", order_date=date(2026, 8, 20))
    ln = _detail(id=50, po_id=5, quantity_order=Decimal("200"))
    h.details = [ln]

    audit = SimpleNamespace(
        id=99,
        entity_type="sales_order_line",
        entity_id=50,
        action="update",
        payload_before=json.dumps({"po_id": 5, "quantity_order": 100, "thickness_text": "1.0 - 1.2"}),
        payload_after=json.dumps({"po_id": 5, "quantity_order": 200, "thickness_text": "1.0 - 1.2"}),
        actor="demo_marketing",
        created_at=datetime(2026, 8, 27, 10, 30, 0),
    )

    db = MagicMock()
    # First scalars: headers; second: audit (inside _collect_revise_from_audit)
    db.scalars.return_value.all.side_effect = [
        [h],
        [audit],
    ]

    def _get(model, pk):
        if model.__name__ == "PoHeader" and pk == 5:
            return h
        if model.__name__ == "PoDetail" and pk == 50:
            return ln
        return None

    db.get.side_effect = _get

    # Order date filter would exclude this header (order 20 Agu), but revise uses audit date
    payload = _build_marketing_daily_payload(db, date(2026, 8, 27), date(2026, 8, 27), None, "order")
    assert payload["production_orders"] == []  # order_date outside range
    assert len(payload["revise_thickness"]) == 1
    rev = payload["revise_thickness"][0]
    assert rev["source"] == "audit"
    assert "quantity_order" in rev["changed_fields"]
    assert rev["actor"] == "demo_marketing"
    assert "Qty" in rev["change_summary"]
