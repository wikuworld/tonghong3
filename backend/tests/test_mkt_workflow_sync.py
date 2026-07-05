"""Tests for MKT workflow auto-sync and stuck-reason rules."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models import PoHeader
from app.services.mkt_workflow import (
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
