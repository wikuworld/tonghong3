"""Unit tests for MKT workflow transitions and PO operations."""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from app.services.mkt_workflow import (
    MKT_STAGES_ORDER,
    mkt_stage_index,
    next_mkt_stage,
    prev_mkt_stage,
    validate_mkt_advance,
)
from app.models import PoHeader, SubconInvoice


class TestMktStageTransitions:
    def test_stages_have_correct_order(self):
        expected = [
            "input_system",
            "rekap_printed",
            "with_ppic",
            "back_to_mkt",
            "in_outstanding",
            "material_followup",
            "delivery_arranged",
            "sj_invpl",
            "invoice_billing",
        ]
        assert MKT_STAGES_ORDER == tuple(expected)

    def test_stage_index_returns_correct_position(self):
        assert mkt_stage_index("input_system") == 0
        assert mkt_stage_index("rekap_printed") == 1
        assert mkt_stage_index("invoice_billing") == 8

    def test_stage_index_unknown_returns_zero(self):
        assert mkt_stage_index("unknown_stage") == 0

    def test_stage_index_none_returns_zero(self):
        assert mkt_stage_index(None) == 0


class TestNextMktStage:
    def test_advance_workflow_validates_transitions(self, db_session):
        po = MagicMock(spec=PoHeader)
        po.mkt_workflow_stage = "input_system"
        db_session.get.return_value = po

        with pytest.raises(HTTPException) as exc_info:
            validate_mkt_advance(db_session, po_id=1, target="sj_invpl")
        assert exc_info.value.status_code == 400
        assert "Langkah MKT berikutnya harus" in exc_info.value.detail

    def test_cannot_skip_workflow_stages(self, db_session):
        po = MagicMock(spec=PoHeader)
        po.mkt_workflow_stage = "input_system"
        db_session.get.return_value = po

        with pytest.raises(HTTPException) as exc_info:
            validate_mkt_advance(db_session, po_id=1, target="in_outstanding")
        assert exc_info.value.status_code == 400

    def test_next_stage_from_input_system(self):
        assert next_mkt_stage("input_system") == "rekap_printed"

    def test_next_stage_from_final_returns_none(self):
        assert next_mkt_stage("invoice_billing") is None

    def test_next_stage_none_returns_second_stage(self):
        assert next_mkt_stage(None) == "rekap_printed"


class TestPrevMktStage:
    def test_rollback_workflow_to_previous_stage(self):
        assert prev_mkt_stage("rekap_printed") == "input_system"
        assert prev_mkt_stage("with_ppic") == "rekap_printed"

    def test_cannot_rollback_from_first_stage(self):
        assert prev_mkt_stage("input_system") is None

    def test_prev_stage_none_defaults_to_first(self):
        assert prev_mkt_stage(None) is None


class TestPoDeleteBlocked:
    def test_po_delete_blocked_with_active_invoices(self, db_session):
        po = MagicMock(spec=PoHeader)
        po.status = "completed"
        db_session.get.return_value = po

        subcon_invoice = MagicMock(spec=SubconInvoice)
        subcon_invoice.status = "sent"
        db_session.scalars.return_value.all.return_value = [subcon_invoice]

        with pytest.raises(HTTPException) as exc_info:
            validate_mkt_advance(db_session, po_id=1, target="invoice_billing")
        assert exc_info.value.status_code == 400


class TestWorkflowRollback:
    def test_rollback_from_rekap_printed_to_input_system(self):
        """Can rollback from rekap_printed to input_system."""
        assert prev_mkt_stage("rekap_printed") == "input_system"

    def test_rollback_from_with_ppic_to_rekap_printed(self):
        """Can rollback from with_ppic to rekap_printed."""
        assert prev_mkt_stage("with_ppic") == "rekap_printed"

    def test_rollback_from_back_to_mkt_to_with_ppic(self):
        """Can rollback from back_to_mkt to with_ppic."""
        assert prev_mkt_stage("back_to_mkt") == "with_ppic"

    def test_rollback_from_in_outstanding_to_back_to_mkt(self):
        """Can rollback from in_outstanding to back_to_mkt."""
        assert prev_mkt_stage("in_outstanding") == "back_to_mkt"

    def test_rollback_from_material_followup_to_in_outstanding(self):
        """Can rollback from material_followup to in_outstanding."""
        assert prev_mkt_stage("material_followup") == "in_outstanding"

    def test_rollback_from_delivery_arranged_to_material_followup(self):
        """Can rollback from delivery_arranged to material_followup."""
        assert prev_mkt_stage("delivery_arranged") == "material_followup"

    def test_rollback_from_sj_invpl_to_delivery_arranged(self):
        """Can rollback from sj_invpl to delivery_arranged."""
        assert prev_mkt_stage("sj_invpl") == "delivery_arranged"

    def test_rollback_from_invoice_billing_to_sj_invpl(self):
        """Can rollback from invoice_billing to sj_invpl."""
        assert prev_mkt_stage("invoice_billing") == "sj_invpl"

    def test_cannot_rollback_from_input_system(self):
        """Cannot rollback from input_system stage - already at first stage."""
        assert prev_mkt_stage("input_system") is None

    def test_rollback_blocked_for_first_stage_in_workflow(self):
        """First stage in workflow has no previous stage to rollback to."""
        first_stage = MKT_STAGES_ORDER[0]
        assert first_stage == "input_system"
        assert prev_mkt_stage(first_stage) is None

    def test_rollback_preserves_stage_order_integrity(self):
        """Each stage can only rollback to its immediate predecessor."""
        expected_pairs = [
            ("rekap_printed", "input_system"),
            ("with_ppic", "rekap_printed"),
            ("back_to_mkt", "with_ppic"),
            ("in_outstanding", "back_to_mkt"),
            ("material_followup", "in_outstanding"),
            ("delivery_arranged", "material_followup"),
            ("sj_invpl", "delivery_arranged"),
            ("invoice_billing", "sj_invpl"),
        ]
        for stage, expected_prev in expected_pairs:
            assert prev_mkt_stage(stage) == expected_prev, f"Rollback from {stage} should go to {expected_prev}"
