"""Uji auto-sync PO ERP → MRP."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.models import PoDetail, PoHeader
from app.services import mrp_po_sync as sync


def _detail(status="confirmed", detail_id=11, po_id=1):
    ph = PoHeader(
        id=po_id,
        po_number="PO-TEST-1",
        po_customer_ref="CUST-1",
        customer_name_snapshot="Acme",
        status=status,
    )
    pod = PoDetail(
        id=detail_id,
        po_id=po_id,
        material_name="PVC",
        color="Black",
        quantity_order=Decimal("100"),
        balance_qty=Decimal("80"),
    )
    pod.po = ph
    pod.color_swatch_recipe = None
    return pod


def test_map_po_detail_includes_balance_and_source():
    mapped = sync.map_po_detail(_detail())
    assert mapped["source_detail_id"] == 11
    assert mapped["qty_order"] == 100.0
    assert mapped["qty_balance_erp"] == 80.0
    assert mapped["no_so"] == "PO-TEST-1"
    assert mapped["no_po"] == "CUST-1"
    assert "cancelled" not in mapped


def test_map_po_detail_no_po_falls_back_to_so_number():
    pod = _detail()
    pod.po.po_customer_ref = None
    mapped = sync.map_po_detail(pod)
    assert mapped["no_so"] == "PO-TEST-1"
    assert mapped["no_po"] == "PO-TEST-1"


def test_map_po_detail_cancelled_header():
    mapped = sync.map_po_detail(_detail(status="cancelled"))
    assert mapped["cancelled"] is True


def test_sync_incremental_by_detail_id(monkeypatch):
    db = MagicMock()
    pod = _detail()

    monkeypatch.setattr(sync, "_load_details", lambda *a, **k: [pod])

    pushed = {}

    def _push(items, **kwargs):
        pushed["items"] = items
        return {"ok": True, "inserted": 0, "updated": 1, "total": len(items)}

    monkeypatch.setattr(sync, "_push_items", _push)

    result = sync.sync_po_details_to_mrp(db, detail_ids=[11], raise_on_error=True)
    assert result["ok"] is True
    assert result["updated"] == 1
    assert pushed["items"][0]["source_detail_id"] == 11
    assert pushed["items"][0]["qty_balance_erp"] == 80.0
    assert pushed["items"][0]["no_so"] == "PO-TEST-1"
    assert pushed["items"][0]["no_po"] == "CUST-1"


def test_sync_orphan_cancelled_detail_ids(monkeypatch):
    db = MagicMock()
    monkeypatch.setattr(sync, "_load_details", lambda *a, **k: [])

    pushed = {}

    def _push(items, **kwargs):
        pushed["items"] = items
        return {"ok": True, "inserted": 0, "updated": 1, "total": len(items)}

    monkeypatch.setattr(sync, "_push_items", _push)

    result = sync.try_sync_po_details_to_mrp(db, cancelled_detail_ids=[99])
    assert result["ok"] is True
    assert pushed["items"] == [{"source_detail_id": 99, "cancelled": True}]


def test_sync_upstream_error_best_effort(monkeypatch):
    db = MagicMock()
    monkeypatch.setattr(sync, "_load_details", lambda *a, **k: [_detail()])
    monkeypatch.setattr(
        sync,
        "_push_items",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("MRP down")),
    )

    result = sync.try_sync_po_details_to_mrp(db, detail_ids=[11])
    assert result["ok"] is False
    assert "MRP down" in result["error"]


def test_sync_upstream_error_raises_when_requested(monkeypatch):
    db = MagicMock()
    monkeypatch.setattr(sync, "_load_details", lambda *a, **k: [_detail()])
    monkeypatch.setattr(
        sync,
        "_push_items",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("MRP down")),
    )

    with pytest.raises(RuntimeError, match="MRP down"):
        sync.sync_po_details_to_mrp(db, detail_ids=[11], raise_on_error=True)


def test_update_po_detail_calls_sync_after_commit_and_survives_sync_failure():
    """Hook: setelah commit, sync dipanggil; kegagalan sync tidak gagalkan PO."""
    from app.routers import po as po_router

    db = MagicMock()
    row = _detail()
    db.get.side_effect = lambda model, pk: row if model is PoDetail else row.po

    body = MagicMock()
    body.model_dump.return_value = {"quantity_order": Decimal("120")}
    user = MagicMock(username="tester", role="admin")
    sync_mock = MagicMock(return_value={"ok": False, "error": "down"})

    with (
        patch.object(po_router, "log_change"),
        patch.object(po_router, "mark_po_item_revised"),
        patch.object(po_router, "_detail_loaded", return_value=row),
        patch.object(po_router, "_validate_fluorescent_color_master"),
        patch.object(po_router, "try_sync_po_details_to_mrp", sync_mock),
        patch.object(po_router, "po_detail_audit_snapshot", return_value={}),
    ):
        out = po_router.update_po_detail(11, body, db, user)

    assert out is row
    db.commit.assert_called()
    sync_mock.assert_called_once_with(db, detail_ids=[11])
