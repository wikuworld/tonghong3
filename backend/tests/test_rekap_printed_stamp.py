"""Unit tests for stamping rekap_printed_at on daily PO recap export."""

from datetime import datetime
from unittest.mock import MagicMock

from app.models import PoHeader
from app.services.mkt_workflow import stamp_rekap_printed_for_recap


def test_stamp_rekap_printed_sets_only_null_timestamps(db_session):
    h_new = MagicMock(spec=PoHeader)
    h_new.id = 1
    h_new.po_number = "SO-001"
    h_new.rekap_printed_at = None

    existing = datetime(2025, 6, 1, 10, 0, 0)
    h_done = MagicMock(spec=PoHeader)
    h_done.id = 2
    h_done.po_number = "SO-002"
    h_done.rekap_printed_at = existing

    count = stamp_rekap_printed_for_recap(db_session, [h_new, h_done], actor="marketing1")

    assert count == 1
    assert h_new.rekap_printed_at is not None
    assert h_done.rekap_printed_at == existing
    db_session.commit.assert_called_once()


def test_stamp_rekap_printed_no_commit_when_none_updated(db_session):
    h = MagicMock(spec=PoHeader)
    h.id = 3
    h.po_number = "SO-003"
    h.rekap_printed_at = datetime(2025, 6, 2, 8, 0, 0)

    count = stamp_rekap_printed_for_recap(db_session, [h])

    assert count == 0
    db_session.commit.assert_not_called()
