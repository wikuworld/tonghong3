"""Unit tests for MKT workflow transitions and PO operations."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models import PoHeader
from app.services.mkt_workflow import (
    MKT_STAGES_ORDER,
    mkt_stage_index,
    next_mkt_stage,
    normalize_mkt_stage,
    prev_mkt_stage,
    validate_mkt_advance,
    validate_mkt_rollback,
)


class TestMktStageTransitions:
    def test_stages_have_correct_order(self):
        expected = [
            "input_system",
            "rekap_printed",
            "with_ppic",
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
        assert mkt_stage_index("invoice_billing") == 7

    def test_back_to_mkt_alias_maps_to_in_outstanding(self):
        assert normalize_mkt_stage("back_to_mkt") == "in_outstanding"
        assert mkt_stage_index("back_to_mkt") == mkt_stage_index("in_outstanding")

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

    def test_next_after_with_ppic_is_in_outstanding(self):
        assert next_mkt_stage("with_ppic") == "in_outstanding"

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

    def test_in_outstanding_rolls_back_to_with_ppic(self):
        assert prev_mkt_stage("in_outstanding") == "with_ppic"
        assert prev_mkt_stage("back_to_mkt") == "with_ppic"



class TestWorkflowRollback:
    def test_rollback_pairs(self):
        expected_pairs = [
            ("rekap_printed", "input_system"),
            ("with_ppic", "rekap_printed"),
            ("in_outstanding", "with_ppic"),
            ("material_followup", "in_outstanding"),
            ("delivery_arranged", "material_followup"),
            ("sj_invpl", "delivery_arranged"),
            ("invoice_billing", "sj_invpl"),
        ]
        for stage, expected_prev in expected_pairs:
            assert prev_mkt_stage(stage) == expected_prev

    def test_cannot_rollback_from_input_system(self):
        assert prev_mkt_stage("input_system") is None

    def test_validate_rollback_requires_reason(self, db_session):
        po = MagicMock(spec=PoHeader)
        po.mkt_workflow_stage = "with_ppic"
        db_session.get.return_value = po
        with pytest.raises(HTTPException) as exc:
            validate_mkt_rollback(db_session, 1, reason="abc")
        assert exc.value.status_code == 400
        assert "Alasan rollback" in exc.value.detail

    def test_validate_rollback_blocks_locked_stage(self, db_session):
        po = MagicMock(spec=PoHeader)
        po.mkt_workflow_stage = "delivery_arranged"
        db_session.get.return_value = po
        with pytest.raises(HTTPException) as exc:
            validate_mkt_rollback(db_session, 1, reason="salah tahap admin")
        assert "terkunci" in exc.value.detail

    def test_validate_rollback_blocks_when_delivery_exists(self, db_session):
        po = MagicMock(spec=PoHeader)
        po.mkt_workflow_stage = "material_followup"
        db_session.get.return_value = po
        with patch("app.services.mkt_workflow.po_has_invoice_for_po", return_value=False):
            with patch("app.services.mkt_workflow.po_has_delivery_for_po", return_value=True):
                with pytest.raises(HTTPException) as exc:
                    validate_mkt_rollback(db_session, 1, reason="koreksi tahap admin")
        assert "delivery" in exc.value.detail.lower()

    def test_validate_rollback_ok(self, db_session):
        po = MagicMock(spec=PoHeader)
        po.mkt_workflow_stage = "in_outstanding"
        db_session.get.return_value = po
        with patch("app.services.mkt_workflow.po_has_invoice_for_po", return_value=False):
            with patch("app.services.mkt_workflow.po_has_delivery_for_po", return_value=False):
                prev, reason = validate_mkt_rollback(db_session, 1, reason="koreksi tahap admin")
        assert prev == "with_ppic"
        assert reason == "koreksi tahap admin"
