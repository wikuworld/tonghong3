"""Scan packing list → delivery sent."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services import delivery_scan_out as scan


def test_resolve_packing_by_number():
    db = MagicMock()
    ph = SimpleNamespace(id=5, packing_number="PK-1")
    db.get.return_value = None

    class _S:
        def first(self):
            return ph

    db.scalars.return_value = _S()
    assert scan.resolve_packing_id(db, packing_number="PK-1") == 5


def test_resolve_requires_id_or_number():
    db = MagicMock()
    with pytest.raises(HTTPException) as exc:
        scan.resolve_packing_id(db)
    assert exc.value.status_code == 400


def test_scan_marks_draft_sent(monkeypatch):
    db = MagicMock()
    hdr = SimpleNamespace(id=10, status="draft", delivery_number="THI-1", packing_id=3)

    monkeypatch.setattr(scan, "resolve_packing_id", lambda *_a, **_k: 3)
    monkeypatch.setattr(scan, "delivery_ids_for_packing", lambda *_a, **_k: [10])
    db.get.return_value = hdr

    class _S:
        def first(self):
            return 1

    db.scalars.return_value = _S()
    monkeypatch.setattr("app.services.audit.log_change", lambda *a, **k: None)
    monkeypatch.setattr("app.services.mkt_workflow.sync_mkt_for_delivery", lambda *a, **k: None)
    monkeypatch.setattr(
        "app.services.notifications.create_notification_for_roles",
        lambda *a, **k: None,
    )

    result = scan.scan_packing_list_out(db, packing_id=3, actor="wh")
    assert result["marked_sent"] == [10]
    assert hdr.status == "sent"
    db.commit.assert_called_once()


def test_scan_idempotent_already_sent(monkeypatch):
    db = MagicMock()
    hdr = SimpleNamespace(id=10, status="sent", delivery_number="THI-1", packing_id=3)
    monkeypatch.setattr(scan, "resolve_packing_id", lambda *_a, **_k: 3)
    monkeypatch.setattr(scan, "delivery_ids_for_packing", lambda *_a, **_k: [10])
    db.get.return_value = hdr
    result = scan.scan_packing_list_out(db, packing_number="PK-1", actor="wh")
    assert result["already_sent"] == [10]
    assert result["marked_sent"] == []
