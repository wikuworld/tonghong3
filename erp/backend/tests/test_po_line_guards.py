"""Kunci edit baris SO yang sudah produksi / WIP."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models import PoDetail
from app.services.po_line_guards import (
    assert_po_detail_not_in_wip,
    assert_po_detail_update_allowed,
    attach_po_line_locks,
    po_detail_lock_state,
)


def _row(**kwargs):
    row = MagicMock(spec=PoDetail)
    row.id = 7
    row.material_name = "PU"
    row.color = "BLACK"
    row.thi_line_ref = "LOT-1"
    row.quantity_order = Decimal("100")
    row.master_item_id = 3
    for k, v in kwargs.items():
        setattr(row, k, v)
    return row


def test_lock_when_production_exists(db_session):
    db_session.scalars.return_value.first.return_value = 99
    locked, reason = po_detail_lock_state(db_session, 7, alloc={})
    assert locked is True
    assert "produksi" in reason


def test_lock_when_mrp_wip(db_session):
    db_session.scalars.return_value.first.return_value = None
    locked, reason = po_detail_lock_state(
        db_session, 7, alloc={"mrp_qty_wip": "12", "mrp_qty_processed": ""}
    )
    assert locked is True
    assert "WIP" in reason


def test_not_locked_when_unsynced(db_session):
    db_session.scalars.return_value.first.return_value = None
    locked, reason = po_detail_lock_state(db_session, 7, alloc={"mrp_qty_wip": "", "mrp_qty_processed": ""})
    assert locked is False
    assert reason is None


def test_update_blocks_identity_when_locked(db_session):
    row = _row()
    with patch("app.services.po_line_guards.po_detail_lock_state", return_value=(True, "locked")):
        with pytest.raises(HTTPException) as exc:
            assert_po_detail_update_allowed(db_session, row, {"color": "RED"})
        assert exc.value.status_code == 400


def test_update_allows_remark_when_locked(db_session):
    row = _row()
    with patch("app.services.po_line_guards.po_detail_lock_state", return_value=(True, "locked")):
        with patch("app.services.po_line_guards.qty_floor_for_po_detail", return_value=Decimal("10")):
            assert_po_detail_update_allowed(db_session, row, {"detail_remark": "ok"})


def test_update_blocks_qty_below_floor(db_session):
    row = _row()
    with patch("app.services.po_line_guards.po_detail_lock_state", return_value=(True, "locked")):
        with patch("app.services.po_line_guards.qty_floor_for_po_detail", return_value=Decimal("80")):
            with pytest.raises(HTTPException) as exc:
                assert_po_detail_update_allowed(db_session, row, {"quantity_order": Decimal("50")})
            assert "80" in exc.value.detail


def test_delete_blocked_when_wip(db_session):
    with patch("app.services.po_line_guards.po_detail_lock_state", return_value=(True, "Baris sudah masuk WIP")):
        with pytest.raises(HTTPException):
            assert_po_detail_not_in_wip(db_session, 7)


def test_attach_locks_sets_flags(db_session):
    a = _row()
    a.id = 1
    b = _row()
    b.id = 2
    db_session.scalars.return_value.all.return_value = [1]
    with patch(
        "app.services.po_line_guards.fetch_mrp_alloc_by_detail_ids",
        return_value={2: {"mrp_qty_wip": "5", "mrp_qty_processed": ""}},
    ):
        attach_po_line_locks(db_session, [a, b])
    assert a.line_locked is True
    assert b.line_locked is True
