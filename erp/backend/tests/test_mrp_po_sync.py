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
    assert mapped["lot_number"] is None
    assert "cancelled" not in mapped


def test_map_po_detail_no_po_falls_back_to_so_number():
    pod = _detail()
    pod.po.po_customer_ref = None
    mapped = sync.map_po_detail(pod)
    assert mapped["no_so"] == "PO-TEST-1"
    assert mapped["no_po"] == "PO-TEST-1"


def test_map_po_detail_includes_lot_from_thi_line_ref():
    pod = _detail()
    pod.thi_line_ref = "PUMTH26001260913004"
    mapped = sync.map_po_detail(pod)
    assert mapped["lot_number"] == "PUMTH26001260913004"


def test_map_po_detail_color_swatch_uses_factory_key():
    pod = _detail()
    recipe = MagicMock()
    recipe.factory_key = "NIKOMAS IY"
    recipe.color_code = "06B"
    recipe.color_name = "COOL GREY"
    pod.color_swatch_recipe = recipe
    pod.color_reference = "06B"
    mapped = sync.map_po_detail(pod)
    assert mapped["color_swatch"] == "NIKOMAS IY"


def test_map_po_detail_no_recipe_leaves_swatch_empty():
    pod = _detail()
    pod.color_reference = "06B"
    pod.color_standard = "TMN"
    mapped = sync.map_po_detail(pod)
    assert mapped["color_swatch"] is None


def test_map_po_detail_cancelled_header():
    mapped = sync.map_po_detail(_detail(status="cancelled"))
    assert mapped["cancelled"] is True


def test_sync_skips_draft_header(monkeypatch):
    db = MagicMock()
    pod = _detail(status="draft")
    monkeypatch.setattr(sync, "_load_details", lambda *a, **k: [pod])
    pushed = {}

    def _push(items, **kwargs):
        pushed["items"] = items
        return {"ok": True, "inserted": 0, "updated": 0, "total": len(items)}

    monkeypatch.setattr(sync, "_push_items", _push)
    result = sync.sync_po_details_to_mrp(db, detail_ids=[11], raise_on_error=True)
    assert result["ok"] is True
    assert pushed["items"] == []
    assert result["total"] == 0


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


def test_push_items_retries_then_succeeds(monkeypatch):
    calls = {"n": 0}

    class _Resp:
        status_code = 200
        content = b'{"ok":true,"updated":1}'

        def json(self):
            return {"ok": True, "updated": 1}

    class _Client:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, json=None):
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("transient")
            return _Resp()

    monkeypatch.setattr(sync.httpx, "Client", _Client)
    monkeypatch.setattr(sync.time, "sleep", lambda *_: None)
    out = sync._push_items([{"source_detail_id": 11}])
    assert out["ok"] is True
    assert out["attempts"] == 2
    assert calls["n"] == 2


def test_push_items_exhausts_retries(monkeypatch):
    class _Client:
        def __init__(self, *a, **k):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def post(self, url, json=None):
            raise RuntimeError("always down")

    monkeypatch.setattr(sync.httpx, "Client", _Client)
    monkeypatch.setattr(sync.time, "sleep", lambda *_: None)
    with pytest.raises(RuntimeError, match="always down"):
        sync._push_items([{"source_detail_id": 11}])

    db = MagicMock()
    monkeypatch.setattr(sync, "_load_details", lambda *a, **k: [_detail()])
    result = sync.try_sync_po_details_to_mrp(db, detail_ids=[11])
    assert result["ok"] is False
    assert result["attempts"] == sync._PUSH_MAX_ATTEMPTS
    assert "always down" in result["error"]


def test_sync_targeted_by_po_id(monkeypatch):
    db = MagicMock()
    pod = _detail(po_id=42, detail_id=99)
    seen = {}

    def _load(*a, **k):
        seen.update(k)
        return [pod]

    monkeypatch.setattr(sync, "_load_details", _load)

    def _push(items, **kwargs):
        return {"ok": True, "inserted": 0, "updated": 1, "total": len(items), "attempts": 1}

    monkeypatch.setattr(sync, "_push_items", _push)
    result = sync.sync_po_details_to_mrp(db, po_id=42, raise_on_error=True)
    assert result["ok"] is True
    assert seen.get("po_id") == 42


def test_gateway_sync_po_passes_po_id(monkeypatch):
    from app.routers import mrp_gateway as gw

    db = MagicMock()
    user = MagicMock()
    called = {}

    def _sync(db_arg, **kwargs):
        called.update(kwargs)
        return {"ok": True, "updated": 1, "attempts": 1}

    monkeypatch.setattr(gw, "sync_po_details_to_mrp", _sync)
    body = gw.MrpSyncPoIn(po_id=7)
    out = gw.sync_po_from_tonghong(body=body, _user=user, db=db)
    assert out["ok"] is True
    assert called.get("po_id") == 7
    assert called.get("raise_on_error") is True
    db.commit.assert_called()


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
        patch.object(po_router, "assert_po_detail_update_allowed"),
        patch.object(po_router, "try_sync_po_details_to_mrp", sync_mock),
        patch.object(po_router, "po_detail_audit_snapshot", return_value={}),
    ):
        out = po_router.update_po_detail(11, body, db, user)

    assert out is row
    db.commit.assert_called()
    sync_mock.assert_called_once_with(db, po_id=1, detail_ids=[11])


def test_update_po_confirm_rolls_back_when_sync_fails():
    from fastapi import HTTPException

    from app.routers import po as po_router
    from app.schemas import PoHeaderUpdate

    db = MagicMock()
    row = MagicMock()
    row.id = 42
    row.status = "draft"
    row.mkt_workflow_stage = "input_system"
    row.order_date = None
    row.customer_id = 1
    row.brand_id = 1
    row.buyer = "NB"
    row.po_customer_ref = "REF"
    row.po_number = "SO-42"
    db.get.return_value = row

    body = PoHeaderUpdate(status="confirmed")
    user = MagicMock(username="tester", role="admin")

    with (
        patch.object(po_router, "_validate_customer_brand_buyer"),
        patch.object(po_router, "_validate_po_customer_ref_unique"),
        patch.object(po_router, "apply_header_snapshots"),
        patch.object(po_router, "validate_po_status_transition"),
        patch.object(po_router, "_validate_po_has_details_for_confirm"),
        patch.object(po_router, "create_notification_for_roles"),
        patch.object(po_router, "log_change"),
        patch.object(po_router, "sync_mkt_workflow_auto_advance"),
        patch.object(
            po_router,
            "sync_po_details_to_mrp",
            return_value={"ok": False, "error": "down"},
        ),
    ):
        with pytest.raises(HTTPException) as exc:
            po_router.update_po(42, body, db, user)

    assert exc.value.status_code == 502
    assert "Confirm dibatalkan" in str(exc.value.detail)
    db.rollback.assert_called()
    db.commit.assert_not_called()


def test_mrp_write_forbidden_for_sales():
    from tests.http_fixtures import clear_api_overrides, make_api_client, set_auth_user

    client = make_api_client()
    set_auth_user("sales")
    try:
        resp = client.post("/api/v1/mrp/rencana-produksi", json={"nama_rencana": "x"})
        assert resp.status_code == 403
    finally:
        clear_api_overrides()
