"""Tests for MKT workflow auto-sync and stuck-reason rules."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models import PoHeader
from app.services.mkt_workflow import (
    _po_ids_with_delivery,
    _stuck_reason_for_header,
    apply_mkt_stage,
    auto_advance_if_ready,
    get_stuck_reason,
    po_has_delivery_for_po,
    sync_mkt_workflow_auto_advance,
    validate_mkt_advance,
)


def test_in_outstanding_can_enter_followup_without_toggle():
    po = MagicMock(spec=PoHeader)
    po.mkt_workflow_stage = "in_outstanding"
    po.material_followup_done = False
    assert (
        _stuck_reason_for_header(
            po,
            has_ppic=True,
            ppic_complete=True,
            has_delivery=False,
            has_sj_invpl=False,
            has_invoice=False,
        )
        is None
    )


def test_material_followup_waits_for_delivery_not_toggle():
    po = MagicMock(spec=PoHeader)
    po.mkt_workflow_stage = "material_followup"
    po.material_followup_done = False
    flags = dict(
        has_ppic=True,
        ppic_complete=True,
        has_delivery=False,
        has_sj_invpl=False,
        has_invoice=False,
    )
    assert _stuck_reason_for_header(po, **flags) == "Delivery belum dibuat"
    flags["has_delivery"] = True
    assert _stuck_reason_for_header(po, **flags) is None


def test_with_ppic_not_stuck_without_assignment(db_session):
    po = MagicMock(spec=PoHeader)
    po.id = 1
    po.mkt_workflow_stage = "rekap_printed"
    po.status = "confirmed"
    po.rekap_printed_at = datetime.utcnow()
    po.material_followup_done = False
    db_session.get.return_value = po

    with patch("app.services.mkt_workflow.po_has_ppic_assignment", return_value=False):
        assert get_stuck_reason(db_session, 1) is None


def test_confirmed_input_system_not_stuck_without_rekap_print():
    po = MagicMock(spec=PoHeader)
    po.mkt_workflow_stage = "input_system"
    po.status = "confirmed"
    po.rekap_printed_at = None
    assert (
        _stuck_reason_for_header(
            po,
            has_ppic=False,
            ppic_complete=False,
            has_delivery=False,
            has_sj_invpl=False,
            has_invoice=False,
        )
        is None
    )


def test_draft_input_system_waits_for_confirm():
    po = MagicMock(spec=PoHeader)
    po.mkt_workflow_stage = "input_system"
    po.status = "draft"
    po.rekap_printed_at = None
    assert (
        _stuck_reason_for_header(
            po,
            has_ppic=False,
            ppic_complete=False,
            has_delivery=False,
            has_sj_invpl=False,
            has_invoice=False,
        )
        == "PO belum di-confirm"
    )


def test_validate_mkt_advance_uses_stuck_reason(db_session):
    po = MagicMock(spec=PoHeader)
    po.mkt_workflow_stage = "input_system"
    db_session.get.return_value = po

    with patch("app.services.mkt_workflow.get_stuck_reason", return_value="PO belum di-confirm"):
        with pytest.raises(HTTPException) as exc_info:
            validate_mkt_advance(db_session, po_id=1, target="rekap_printed")
        assert exc_info.value.status_code == 400
        assert "PO belum di-confirm" in exc_info.value.detail


def test_validate_allows_rekap_without_print_stamp(db_session):
    po = MagicMock(spec=PoHeader)
    po.id = 1
    po.mkt_workflow_stage = "input_system"
    po.status = "confirmed"
    po.rekap_printed_at = None
    db_session.get.return_value = po

    with patch("app.services.mkt_workflow.get_stuck_reason", return_value=None):
        validate_mkt_advance(db_session, po_id=1, target="rekap_printed")


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


def test_auto_advance_holds_in_outstanding_without_schedule(db_session):
    po = MagicMock(spec=PoHeader)
    po.id = 10
    po.mkt_workflow_stage = "in_outstanding"
    db_session.get.return_value = po

    with patch("app.services.mkt_workflow.get_stuck_reason", return_value=None):
        with patch("app.services.mkt_workflow.po_has_schedule_for_po", return_value=False):
            assert auto_advance_if_ready(db_session, 10) is None

    assert po.mkt_workflow_stage == "in_outstanding"


def test_auto_advance_from_outstanding_with_schedule(db_session):
    po = MagicMock(spec=PoHeader)
    po.id = 10
    po.mkt_workflow_stage = "in_outstanding"
    db_session.get.return_value = po

    with patch("app.services.mkt_workflow.get_stuck_reason", return_value=None):
        with patch("app.services.mkt_workflow.po_has_schedule_for_po", return_value=True):
            assert auto_advance_if_ready(db_session, 10) == "material_followup"

    assert po.mkt_workflow_stage == "material_followup"


def test_manual_advance_from_outstanding_without_schedule(db_session):
    po = MagicMock(spec=PoHeader)
    po.id = 10
    po.mkt_workflow_stage = "in_outstanding"
    db_session.get.return_value = po

    with patch("app.services.mkt_workflow.get_stuck_reason", return_value=None):
        validate_mkt_advance(db_session, 10, "material_followup")

    apply_mkt_stage(db_session, 10, "material_followup")
    assert po.mkt_workflow_stage == "material_followup"


def test_po_has_delivery_query_excludes_draft(db_session):
    db_session.scalars.return_value.first.return_value = None
    assert po_has_delivery_for_po(db_session, 1) is False
    stmt = db_session.scalars.call_args[0][0]
    compiled = str(stmt.compile(compile_kwargs={"literal_binds": True})).lower()
    assert "draft" in compiled
    assert "po_detail_id" in compiled


def test_po_ids_with_delivery_query_excludes_draft(db_session):
    db_session.scalars.return_value.all.return_value = []
    assert _po_ids_with_delivery(db_session, [1]) == set()
    stmt = db_session.scalars.call_args[0][0]
    compiled = str(stmt.compile(compile_kwargs={"literal_binds": True})).lower()
    assert "draft" in compiled
    assert "po_detail_id" in compiled


def test_direct_delivery_stmt_uses_po_detail_id():
    from app.services.mkt_workflow import _stmt_delivery_ids_via_direct

    compiled = str(
        _stmt_delivery_ids_via_direct(9, posted_only=True).compile(compile_kwargs={"literal_binds": True})
    ).lower()
    assert "po_detail_id" in compiled
    assert "draft" in compiled


def test_material_followup_draft_delivery_still_stuck():
    po = MagicMock(spec=PoHeader)
    po.mkt_workflow_stage = "material_followup"
    assert (
        _stuck_reason_for_header(
            po,
            has_ppic=True,
            ppic_complete=True,
            has_delivery=False,
            has_sj_invpl=False,
            has_invoice=False,
        )
        == "Delivery belum dibuat"
    )


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


def test_auto_advance_from_confirmed_stamps_rekap(db_session):
    po = MagicMock(spec=PoHeader)
    po.id = 11
    po.mkt_workflow_stage = "input_system"
    po.status = "confirmed"
    po.rekap_printed_at = None
    db_session.get.return_value = po

    with patch("app.services.mkt_workflow.get_stuck_reason", return_value=None):
        with patch("app.services.mkt_workflow.ensure_auto_ppic_handoff", return_value=True):
            assert auto_advance_if_ready(db_session, 11) == "rekap_printed"

    assert po.rekap_printed_at is not None
    assert po.mkt_workflow_stage == "rekap_printed"


def test_ensure_auto_ppic_handoff_without_user_still_ok(db_session):
    from app.services.mkt_workflow import ensure_auto_ppic_handoff

    po = MagicMock(spec=PoHeader)
    po.id = 12
    po.status = "confirmed"
    db_session.get.return_value = po
    db_session.scalars.return_value.first.return_value = None

    assert ensure_auto_ppic_handoff(db_session, 12) is True
    db_session.add.assert_not_called()


def test_sync_notifies_ppic_when_entering_outstanding(db_session):
    stages = iter(["rekap_printed", "with_ppic", "in_outstanding"])
    po = MagicMock(spec=PoHeader)
    po.id = 9
    po.po_number = "SO-9"
    db_session.get.return_value = po
    with patch(
        "app.services.mkt_workflow.auto_advance_if_ready",
        side_effect=lambda *_a, **_k: next(stages, None),
    ):
        with patch("app.services.audit.log_change"):
            with patch("app.services.mkt_workflow._notify_ppic_entered_outstanding") as notify:
                advanced = sync_mkt_workflow_auto_advance(db_session, 9, actor="tester")
    assert advanced == ["rekap_printed", "with_ppic", "in_outstanding"]
    notify.assert_called_once()


def test_sync_skip_ppic_notify_when_flag_false(db_session):
    stages = iter(["in_outstanding"])
    with patch(
        "app.services.mkt_workflow.auto_advance_if_ready",
        side_effect=lambda *_a, **_k: next(stages, None),
    ):
        with patch("app.services.audit.log_change"):
            with patch("app.services.mkt_workflow._notify_ppic_entered_outstanding") as notify:
                sync_mkt_workflow_auto_advance(db_session, 9, actor="tester", notify_ppic=False)
    notify.assert_not_called()
