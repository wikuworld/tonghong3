"""Tests for outstanding batch schedule / packing options helpers."""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.schemas import (
    DeliveryScheduleItem,
    OutstandingScheduleBatchIn,
    OutstandingScheduleLineIn,
    OutstandingShipBatchIn,
    OutstandingShipLineIn,
)
from app.services.outstanding_actions import apply_outstanding_schedule_batch, packing_options_for_details
from app.services.proforma_invoice_documents import gather_proforma_invoice_ctx_multi


def test_gather_proforma_multi_requires_same_customer(db_session):
    with patch(
        "app.services.proforma_invoice_documents.gather_proforma_invoice_ctx"
    ) as _gather:
        # first call for primary check via get, then per header
        pass

    h1 = MagicMock()
    h1.id = 1
    h1.customer_id = 10
    h2 = MagicMock()
    h2.id = 2
    h2.customer_id = 99

    def get_side(model, pid):
        return {1: h1, 2: h2}.get(pid)

    db_session.get.side_effect = get_side

    with pytest.raises(ValueError, match="customer_mismatch"):
        gather_proforma_invoice_ctx_multi(db_session, [1, 2])


def test_gather_proforma_multi_merges_lines(db_session):
    h1 = MagicMock()
    h1.id = 1
    h1.customer_id = 10
    h2 = MagicMock()
    h2.id = 2
    h2.customer_id = 10

    def get_side(model, pid):
        return {1: h1, 2: h2}.get(pid)

    db_session.get.side_effect = get_side

    ctx1 = {
        "po_number": "SO-1",
        "pi_number": "PI-1",
        "lines": [{"po_no": "SO-1", "item": "A"}],
        "total_qty": Decimal("2"),
        "total_amount": Decimal("10"),
        "customer_name": "C",
        "ship_address": "",
        "phone": "",
        "attn": "",
        "from_name": "X",
        "signature_name": "X",
        "po_list_label": "SO-1",
        "ex_factory_label": "SO-1",
        "payment_terms": "TT",
        "document_date": date.today(),
        "document_date_fmt": "2026-07-16",
        "unit": "SF",
        "po_detail_ids": [11],
    }
    ctx2 = {
        **ctx1,
        "po_number": "SO-2",
        "lines": [{"po_no": "SO-2", "item": "B"}],
        "total_qty": Decimal("3"),
        "total_amount": Decimal("15"),
        "po_detail_ids": [22],
    }

    with patch(
        "app.services.proforma_invoice_documents.gather_proforma_invoice_ctx",
        side_effect=[ctx1, ctx2],
    ):
        out = gather_proforma_invoice_ctx_multi(db_session, [1, 2])

    assert len(out["lines"]) == 2
    assert out["total_qty"] == Decimal("5")
    assert "SO-1" in out["po_number"]


def test_gather_proforma_filters_detail_ids(db_session):
    """Satu SO: hanya baris checklist yang masuk PI."""
    ph = MagicMock()
    ph.id = 5
    ph.po_number = "SO-5"
    ph.customer_id = None
    ph.customer_name_snapshot = "Cust"
    ph.delivery_address = ""
    ph.billing_address = ""
    ph.order_date = date(2026, 7, 15)
    ph.etd = None

    d1 = MagicMock()
    d1.id = 101
    d1.quantity_order = Decimal("10")
    d1.unit_price = Decimal("2")
    d1.material_name = "A"
    d1.emboss = ""
    d1.color = "BLK"
    d1.line_etd = None
    d1.thickness_text = "1.0"
    d1.thickness_mm = None

    d2 = MagicMock()
    d2.id = 102
    d2.quantity_order = Decimal("20")
    d2.unit_price = Decimal("3")
    d2.material_name = "B"
    d2.emboss = ""
    d2.color = "RED"
    d2.line_etd = None
    d2.thickness_text = "1.2"
    d2.thickness_mm = None

    db_session.get.side_effect = lambda model, pid: ph if pid == 5 else None
    db_session.scalars.return_value.all.return_value = [d1, d2]

    with (
        patch("app.services.proforma_invoice_documents._resolve_salesperson", return_value="S"),
        patch("app.services.proforma_invoice_documents._resolve_attn", return_value=""),
        patch("app.services.proforma_invoice_documents._resolve_payment_terms", return_value="TT"),
        patch("app.services.proforma_invoice_documents._build_pi_number", return_value="PI-5"),
        patch("app.services.proforma_invoice_documents._thickness_text", return_value="1.0"),
    ):
        from app.services.proforma_invoice_documents import gather_proforma_invoice_ctx

        out = gather_proforma_invoice_ctx(db_session, 5, po_detail_ids=[101])

    assert len(out["lines"]) == 1
    assert out["lines"][0]["item"] == "A"
    assert out["po_detail_ids"] == [101]
    assert out["total_qty"] == Decimal("10")


def test_schedule_batch_append(db_session):
    drow = MagicMock()
    drow.id = 7
    drow.quantity_order = Decimal("100")
    drow.line_etd = None
    db_session.get.return_value = drow
    db_session.scalars.return_value.all.return_value = []

    body = OutstandingScheduleBatchIn(
        mode="append",
        lines=[
            OutstandingScheduleLineIn(
                po_detail_id=7,
                delivery_date=date(2026, 8, 1),
                qty=Decimal("40"),
            )
        ],
    )

    with patch("app.services.outstanding_actions.log_change"):
        with patch("app.services.outstanding_actions.sync_mkt_workflow_auto_advance") as sync_mock:
            result = apply_outstanding_schedule_batch(db_session, body, actor="mkt")

    assert result["updated_count"] == 1
    assert result["po_detail_ids"] == [7]
    db_session.commit.assert_called()
    sync_mock.assert_not_called()


def test_schedule_batch_triggers_mkt_sync(db_session):
    drow = MagicMock()
    drow.id = 7
    drow.po_id = 3
    drow.quantity_order = Decimal("100")
    drow.line_etd = None
    db_session.get.return_value = drow
    db_session.scalars.return_value.all.return_value = []

    body = OutstandingScheduleBatchIn(
        mode="append",
        lines=[
            OutstandingScheduleLineIn(
                po_detail_id=7,
                delivery_date=date(2026, 8, 1),
                qty=Decimal("40"),
            )
        ],
    )

    with patch("app.services.outstanding_actions.log_change"):
        with patch("app.services.outstanding_actions.sync_mkt_workflow_auto_advance") as sync_mock:
            result = apply_outstanding_schedule_batch(db_session, body, actor="mkt")

    assert result["updated_count"] == 1
    sync_mock.assert_called_once_with(db_session, 3, actor="mkt")


def test_schedule_batch_rejects_over_order_qty(db_session):
    drow = MagicMock()
    drow.id = 7
    drow.quantity_order = Decimal("100")
    drow.line_etd = None
    db_session.get.return_value = drow

    existing = MagicMock()
    existing.sequence_no = 1
    existing.qty = Decimal("90")
    existing.delivery_date = date(2026, 7, 1)
    db_session.scalars.return_value.all.return_value = [existing]

    body = OutstandingScheduleBatchIn(
        mode="append",
        lines=[
            OutstandingScheduleLineIn(
                po_detail_id=7,
                delivery_date=date(2026, 8, 1),
                qty=Decimal("50"),
            )
        ],
    )

    with pytest.raises(HTTPException) as ei:
        apply_outstanding_schedule_batch(db_session, body, actor="mkt")
    assert ei.value.status_code == 400
    assert "melebihi qty order" in ei.value.detail


def test_validate_schedule_total_against_order_unit():
    from app.services.po_delivery_balance import validate_schedule_total_against_order

    db = MagicMock()
    pod = MagicMock()
    pod.quantity_order = Decimal("100")
    db.get.return_value = pod

    validate_schedule_total_against_order(
        db, 1, [DeliveryScheduleItem(sequence_no=1, qty=Decimal("40"), delivery_date=date(2026, 7, 1))]
    )

    with pytest.raises(HTTPException):
        validate_schedule_total_against_order(
            db,
            1,
            [
                DeliveryScheduleItem(sequence_no=1, qty=Decimal("60"), delivery_date=date(2026, 7, 1)),
                DeliveryScheduleItem(sequence_no=2, qty=Decimal("50"), delivery_date=date(2026, 7, 2)),
            ],
        )


def test_packing_options_forwards(db_session):
    with patch(
        "app.services.outstanding_actions.list_ready_to_ship_for_po_details",
        return_value=[{"po_detail_id": 1, "packing_id": 9}],
    ) as fn:
        rows = packing_options_for_details(db_session, [1, 2])
    fn.assert_called_once_with(db_session, [1, 2])
    assert rows[0]["packing_id"] == 9


def _stub_ship_stage(db_session, *, stage: str):
    from app.models import PoDetail, PoHeader

    drow = MagicMock()
    drow.id = 1
    drow.po_id = 10
    ph = MagicMock()
    ph.id = 10
    ph.po_number = "THIPM26071501"
    ph.mkt_workflow_stage = stage
    ph.customer_id = 1
    ph.brand_name_snapshot = "BRAND"
    ph.buyer = "BRAND"

    def get_side(model, pid):
        if model is PoDetail:
            return drow
        if model is PoHeader:
            return ph
        return MagicMock()

    db_session.get.side_effect = get_side


def test_ship_batch_rejects_null_qty(db_session):
    from app.services.outstanding_actions import apply_outstanding_ship_batch

    body = OutstandingShipBatchIn(
        lines=[
            OutstandingShipLineIn(
                po_detail_id=1,
                packing_id=9,
                production_detail_id=5,
                qty=None,
                delivery_date=date(2026, 7, 16),
            )
        ]
    )
    _stub_ship_stage(db_session, stage="in_outstanding")
    with (
        patch("app.services.outstanding_actions.require_packing_ready"),
        patch(
            "app.services.outstanding_actions.validate_same_customer_and_brand",
            return_value=(1, "BRAND"),
        ),
        patch("app.services.outstanding_actions._has_qc_ok", return_value=True),
        patch("app.services.outstanding_actions.allocate_surat_jalan_number", return_value="DEL-UAT"),
        patch("app.services.delivery_auto_invoice.ensure_invoice_for_delivery", return_value=None),
        patch("app.services.outstanding_actions.trigger_mrp_fg_out_for_packings"),
    ):
        with pytest.raises(HTTPException) as ei:
            apply_outstanding_ship_batch(db_session, body, actor="mkt")
    assert ei.value.status_code == 400
    assert "Qty" in ei.value.detail


def test_ship_batch_rejects_over_available(db_session):
    from app.services.outstanding_actions import apply_outstanding_ship_batch

    body = OutstandingShipBatchIn(
        lines=[
            OutstandingShipLineIn(
                po_detail_id=1,
                packing_id=9,
                production_detail_id=5,
                qty=Decimal("100"),
                delivery_date=date(2026, 7, 16),
            )
        ]
    )
    _stub_ship_stage(db_session, stage="in_outstanding")
    with (
        patch("app.services.outstanding_actions.require_packing_ready"),
        patch(
            "app.services.outstanding_actions.validate_same_customer_and_brand",
            return_value=(1, "BRAND"),
        ),
        patch("app.services.outstanding_actions._has_qc_ok", return_value=True),
        patch(
            "app.services.outstanding_actions.qty_available_for_packing_line",
            return_value=Decimal("40"),
        ),
        patch("app.services.outstanding_actions.allocate_surat_jalan_number", return_value="DEL-UAT"),
        patch("app.services.delivery_auto_invoice.ensure_invoice_for_delivery", return_value=None),
        patch("app.services.outstanding_actions.trigger_mrp_fg_out_for_packings"),
    ):
        with pytest.raises(HTTPException) as ei:
            apply_outstanding_ship_batch(db_session, body, actor="mkt")
    assert ei.value.status_code == 400
    assert "sisa packing" in ei.value.detail


def test_ship_batch_rejects_before_outstanding_stage(db_session):
    from app.services.outstanding_actions import apply_outstanding_ship_batch

    body = OutstandingShipBatchIn(
        lines=[
            OutstandingShipLineIn(
                po_detail_id=1,
                packing_id=9,
                production_detail_id=5,
                qty=Decimal("10"),
                delivery_date=date(2026, 7, 16),
            )
        ]
    )
    _stub_ship_stage(db_session, stage="rekap_printed")
    with pytest.raises(HTTPException) as ei:
        apply_outstanding_ship_batch(db_session, body, actor="mkt")
    assert ei.value.status_code == 400
    assert "Outstanding" in ei.value.detail


def test_ship_batch_partial_ok(db_session):
    from app.services.outstanding_actions import apply_outstanding_ship_batch

    body = OutstandingShipBatchIn(
        lines=[
            OutstandingShipLineIn(
                po_detail_id=1,
                packing_id=9,
                packing_detail_id=3,
                production_detail_id=5,
                qty=Decimal("10"),
                delivery_date=date(2026, 7, 16),
            )
        ]
    )
    hdr = MagicMock()
    hdr.id = 99
    hdr.delivery_number = "DEL-UAT"
    _stub_ship_stage(db_session, stage="in_outstanding")

    with (
        patch("app.services.outstanding_actions.require_packing_ready"),
        patch(
            "app.services.outstanding_actions.validate_same_customer_and_brand",
            return_value=(1, "BRAND"),
        ),
        patch("app.services.outstanding_actions._has_qc_ok", return_value=True),
        patch(
            "app.services.outstanding_actions.qty_available_for_packing_line",
            return_value=Decimal("40"),
        ),
        patch("app.services.outstanding_actions.validate_delivery_qty_against_po_balance"),
        patch("app.services.outstanding_actions.log_change"),
        patch("app.services.outstanding_actions.sync_mkt_for_delivery"),
        patch("app.services.outstanding_actions.allocate_surat_jalan_number", return_value="DEL-UAT"),
        patch("app.services.delivery_auto_invoice.ensure_invoice_for_delivery", return_value=None),
        patch("app.services.outstanding_actions.trigger_mrp_fg_out_for_packings"),
        patch("app.services.outstanding_actions.create_notification_for_roles"),
        patch("app.services.outstanding_actions.DeliveryHeader", return_value=hdr),
        patch("app.services.outstanding_actions.DeliveryDetail"),
    ):
        result = apply_outstanding_ship_batch(db_session, body, actor="mkt")

    assert result["ok"] is True
    assert result["delivery_count"] == 1
    assert result["delivery_ids"] == [99]
    assert result["delivery_numbers"] == ["DEL-UAT"]
    db_session.commit.assert_called()


def test_ship_batch_two_packings_same_customer_one_sj(db_session):
    from app.models import PoDetail, PoHeader
    from app.services.outstanding_actions import apply_outstanding_ship_batch

    d1 = MagicMock()
    d1.id = 1
    d1.po_id = 10
    d2 = MagicMock()
    d2.id = 2
    d2.po_id = 20
    ph1 = MagicMock()
    ph1.id = 10
    ph1.po_number = "SO-A"
    ph1.mkt_workflow_stage = "in_outstanding"
    ph1.customer_id = 1
    ph1.brand_name_snapshot = "BRAND"
    ph1.buyer = "BRAND"
    ph2 = MagicMock()
    ph2.id = 20
    ph2.po_number = "SO-B"
    ph2.mkt_workflow_stage = "in_outstanding"
    ph2.customer_id = 1
    ph2.brand_name_snapshot = "BRAND"
    ph2.buyer = "BRAND"

    def get_side(model, pid):
        from app.models import PackingDetail, PackingHeader, ProductionDetail

        if model is PoDetail:
            return {1: d1, 2: d2}.get(pid)
        if model is PoHeader:
            return {10: ph1, 20: ph2}.get(pid)
        if model is ProductionDetail:
            pd = MagicMock()
            pd.id = pid
            pd.po_detail_id = {5: 1, 6: 2}.get(pid)
            return pd
        if model is PackingDetail:
            pkd = MagicMock()
            pkd.id = pid
            pkd.qty_roll = 1
            pkd.qty_pcs = 1
            return pkd
        if model is PackingHeader:
            return MagicMock(id=pid)
        return MagicMock()

    db_session.get.side_effect = get_side
    # packing detail lookup via scalars().first()
    db_session.scalars.return_value.first.return_value = None
    hdr = MagicMock()
    hdr.id = 77
    hdr.delivery_number = "DEL-UAT"
    body = OutstandingShipBatchIn(
        lines=[
            OutstandingShipLineIn(
                po_detail_id=1,
                packing_id=9,
                packing_detail_id=3,
                production_detail_id=5,
                qty=Decimal("10"),
                delivery_date=date(2026, 7, 16),
            ),
            OutstandingShipLineIn(
                po_detail_id=2,
                packing_id=10,
                packing_detail_id=4,
                production_detail_id=6,
                qty=Decimal("8"),
                delivery_date=date(2026, 7, 16),
            ),
        ]
    )
    with (
        patch("app.services.outstanding_actions.require_packing_ready"),
        patch(
            "app.services.outstanding_actions.validate_same_customer_and_brand",
            return_value=(1, "BRAND"),
        ),
        patch("app.services.outstanding_actions._has_qc_ok", return_value=True),
        patch(
            "app.services.outstanding_actions.qty_available_for_packing_line",
            return_value=Decimal("40"),
        ),
        patch("app.services.outstanding_actions.validate_delivery_qty_against_po_balance"),
        patch("app.services.outstanding_actions.log_change"),
        patch("app.services.outstanding_actions.sync_mkt_for_delivery"),
        patch("app.services.outstanding_actions.allocate_surat_jalan_number", return_value="DEL-UAT"),
        patch("app.services.delivery_auto_invoice.ensure_invoice_for_delivery", return_value=None),
        patch("app.services.outstanding_actions.trigger_mrp_fg_out_for_packings"),
        patch("app.services.outstanding_actions.create_notification_for_roles"),
        patch("app.services.outstanding_actions.DeliveryHeader", return_value=hdr),
        patch("app.services.outstanding_actions.DeliveryDetail"),
    ):
        result = apply_outstanding_ship_batch(db_session, body, actor="mkt")

    assert result["ok"] is True
    assert result["delivery_count"] == 1
    assert result["delivery_ids"] == [77]
    assert result["delivery_numbers"] == ["DEL-UAT"]


def test_ship_batch_rejects_mixed_customers(db_session):
    from app.models import PoDetail, PoHeader
    from app.services.outstanding_actions import apply_outstanding_ship_batch

    d1 = MagicMock()
    d1.id = 1
    d1.po_id = 10
    d2 = MagicMock()
    d2.id = 2
    d2.po_id = 20
    ph1 = MagicMock()
    ph1.id = 10
    ph1.po_number = "SO-A"
    ph1.mkt_workflow_stage = "in_outstanding"
    ph1.customer_id = 1
    ph1.customer_name_snapshot = "PT ALPHA"
    ph1.brand_name_snapshot = "BRAND"
    ph1.buyer = "BRAND"
    ph2 = MagicMock()
    ph2.id = 20
    ph2.po_number = "SO-B"
    ph2.mkt_workflow_stage = "in_outstanding"
    ph2.customer_id = 2
    ph2.customer_name_snapshot = "PT BETA"
    ph2.brand_name_snapshot = "BRAND"
    ph2.buyer = "BRAND"

    def get_side(model, pid):
        if model is PoDetail:
            return {1: d1, 2: d2}.get(pid)
        if model is PoHeader:
            return {10: ph1, 20: ph2}.get(pid)
        return MagicMock()

    db_session.get.side_effect = get_side
    body = OutstandingShipBatchIn(
        lines=[
            OutstandingShipLineIn(
                po_detail_id=1,
                packing_id=9,
                packing_detail_id=3,
                production_detail_id=5,
                qty=Decimal("10"),
                delivery_date=date(2026, 7, 16),
            ),
            OutstandingShipLineIn(
                po_detail_id=2,
                packing_id=10,
                packing_detail_id=4,
                production_detail_id=6,
                qty=Decimal("8"),
                delivery_date=date(2026, 7, 16),
            ),
        ]
    )
    with pytest.raises(HTTPException) as ei:
        apply_outstanding_ship_batch(db_session, body, actor="mkt")
    assert ei.value.status_code == 400
    assert "satu customer" in ei.value.detail.lower()


def test_schedule_rejects_date_before_order(db_session):
    from app.models import PoDetail, PoHeader

    drow = MagicMock()
    drow.id = 1
    drow.po_id = 10
    drow.quantity_order = Decimal("100")
    drow.line_etd = date(2026, 8, 1)
    ph = MagicMock()
    ph.order_date = date(2026, 7, 10)

    def get_side(model, pid):
        if model is PoDetail and pid == 1:
            return drow
        if model is PoHeader and pid == 10:
            return ph
        return None

    db_session.get.side_effect = get_side
    db_session.scalars.return_value.all.return_value = []

    body = OutstandingScheduleBatchIn(
        mode="append",
        lines=[
            OutstandingScheduleLineIn(
                po_detail_id=1,
                qty=Decimal("10"),
                delivery_date=date(2026, 7, 1),
            )
        ],
    )
    with pytest.raises(HTTPException) as ei:
        apply_outstanding_schedule_batch(db_session, body, actor="mkt")
    assert ei.value.status_code == 400
    assert "sebelum tanggal order" in ei.value.detail


def test_ensure_unique_pi_number_suffix(db_session):
    from app.services.proforma_invoice_documents import _ensure_unique_pi_number

    existing = MagicMock()
    # first hit exists, second empty → -R2
    chain = [existing, None]

    def scalars_side(*_a, **_k):
        m = MagicMock()
        m.first.return_value = chain.pop(0) if chain else None
        return m

    db_session.scalars.side_effect = scalars_side
    assert _ensure_unique_pi_number(db_session, "001/PI/XX/PROD/I/2026") == "001/PI/XX/PROD/I/2026-R2"


def test_persist_proforma_invoice_record(db_session):
    from app.services.proforma_invoice_documents import persist_proforma_invoice_record

    ctx = {
        "pi_number": "001/PI/DEMO/PROD/VII/2026",
        "customer_id": 1,
        "customer_name": "Demo",
        "po_ids": [1],
        "po_detail_ids": [10, 11],
        "total_qty": Decimal("100"),
        "total_amount": Decimal("1000"),
    }
    with patch(
        "app.services.proforma_invoice_documents._ensure_unique_pi_number",
        return_value=ctx["pi_number"],
    ):
        row = persist_proforma_invoice_record(db_session, ctx, actor="mkt")
    db_session.add.assert_called()
    db_session.flush.assert_called()
    assert ctx["pi_number"] == "001/PI/DEMO/PROD/VII/2026"
    assert row is not None


def test_qty_available_returns_zero_if_packing_not_done(db_session):
    from app.services.delivery_shipment import qty_available_for_packing_line

    pk = MagicMock()
    pk.status = "draft"
    db_session.get.return_value = pk
    assert qty_available_for_packing_line(
        db_session, packing_id=1, production_detail_id=2
    ) == Decimal("0")
