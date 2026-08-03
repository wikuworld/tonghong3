"""Tests for MKT workflow auto-sync and stuck-reason rules."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models import PoHeader
from app.services.mkt_workflow import (
    apply_mkt_stage,
    get_stuck_reason,
    sync_mkt_workflow_auto_advance,
    validate_mkt_advance,
)


def test_with_ppic_stuck_only_requires_assignment(db_session):
    po = MagicMock(spec=PoHeader)
    po.id = 1
    po.mkt_workflow_stage = "rekap_printed"
    po.status = "confirmed"
    po.rekap_printed_at = datetime.utcnow()
    po.material_followup_done = False
    db_session.get.return_value = po

    with patch("app.services.mkt_workflow.po_has_ppic_assignment", return_value=False):
        assert get_stuck_reason(db_session, 1) == "Belum di-assign ke PPIC"

    with patch("app.services.mkt_workflow.po_has_ppic_assignment", return_value=True):
        with patch("app.services.mkt_workflow.po_ppic_is_complete", return_value=False):
            assert get_stuck_reason(db_session, 1) is None


def test_validate_mkt_advance_uses_stuck_reason(db_session):
    po = MagicMock(spec=PoHeader)
    po.mkt_workflow_stage = "input_system"
    db_session.get.return_value = po

    with patch("app.services.mkt_workflow.get_stuck_reason", return_value="PO belum di-confirm"):
        with pytest.raises(HTTPException) as exc_info:
            validate_mkt_advance(db_session, po_id=1, target="rekap_printed")
        assert exc_info.value.status_code == 400
        assert "PO belum di-confirm" in exc_info.value.detail


def test_validate_blocks_rekap_without_print_stamp(db_session):
    po = MagicMock(spec=PoHeader)
    po.id = 1
    po.mkt_workflow_stage = "input_system"
    po.status = "confirmed"
    po.rekap_printed_at = None
    db_session.get.return_value = po

    with patch("app.services.mkt_workflow.get_stuck_reason", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            validate_mkt_advance(db_session, po_id=1, target="rekap_printed")
        assert "rekap" in str(exc_info.value.detail).lower()


def test_apply_mkt_stage_does_not_auto_stamp_rekap(db_session):
    po = MagicMock(spec=PoHeader)
    po.id = 1
    po.mkt_workflow_stage = "input_system"
    po.rekap_printed_at = None
    db_session.get.return_value = po

    apply_mkt_stage(db_session, 1, "rekap_printed")

    assert po.mkt_workflow_stage == "rekap_printed"
    assert po.rekap_printed_at is None


def test_sync_auto_advance_chain(db_session):
    po = MagicMock(spec=PoHeader)
    po.id = 5
    po.mkt_workflow_stage = "input_system"
    po.rekap_printed_at = datetime.utcnow()
    po.status = "confirmed"
    db_session.get.return_value = po

    stages = iter(["rekap_printed", None])

    with patch("app.services.mkt_workflow.auto_advance_if_ready", side_effect=lambda *_a, **_k: next(stages)):
        with patch("app.services.audit.log_change"):
            advanced = sync_mkt_workflow_auto_advance(db_session, 5, actor="tester")

    assert advanced == ["rekap_printed"]


def test_sync_stop_at_stage(db_session):
    stages = iter(["rekap_printed", "with_ppic", "in_outstanding"])
    with patch(
        "app.services.mkt_workflow.auto_advance_if_ready",
        side_effect=lambda *_a, **_k: next(stages, None),
    ):
        with patch("app.services.audit.log_change"):
            advanced = sync_mkt_workflow_auto_advance(
                db_session, 9, actor="tester", stop_at_stage="rekap_printed"
            )
    assert advanced == ["rekap_printed"]


def test_invalidate_ppic_on_rollback_before_with_ppic(db_session):
    from app.services.mkt_workflow import invalidate_ppic_assignments_for_rollback

    a = MagicMock()
    a.status = "completed"
    a.completed_at = datetime.utcnow()
    a.notes = "ok"
    db_session.scalars.return_value.all.return_value = [a]

    invalidate_ppic_assignments_for_rollback(db_session, 1, "rekap_printed")

    assert a.status == "cancelled"
    assert a.completed_at is None


def test_invalidate_ppic_reopens_when_back_to_with_ppic(db_session):
    from app.services.mkt_workflow import invalidate_ppic_assignments_for_rollback

    a = MagicMock()
    a.status = "completed"
    a.completed_at = datetime.utcnow()
    a.notes = ""
    db_session.scalars.return_value.all.return_value = [a]

    invalidate_ppic_assignments_for_rollback(db_session, 1, "with_ppic")

    assert a.status == "pending"
    assert a.completed_at is None
