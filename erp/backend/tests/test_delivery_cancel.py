"""Soft-delete delivery: flag is_deleted, invoice void, qty, dan tahap marketing."""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models import DeliveryHeader, Invoice
from app.schemas import DeliveryHeaderUpdate
from app.services import delivery_cancel as cancel_mod
from app.services.delivery_scan_out import _mark_deliveries_sent
from app.services.delivery_shipment import sum_delivered_qty
from app.services.invoice_outstanding import exclude_voided_invoices
from app.services.mkt_workflow import reconcile_po_stage_after_delivery_cancel
from app.services.po_delivery_balance import sum_delivered_qty_for_po_detail
from app.routers.delivery import update_delivery


def _header(**kwargs):
    data = dict(
        id=5,
        status="draft",
        delivery_number="SJ-1",
        bc_number=None,
        bc_date=None,
        customs_declaration_id=None,
        packing_id=None,
        cancel_reason=None,
        cancelled_at=None,
        cancelled_by=None,
        is_deleted=False,
        deleted_at=None,
        deleted_by=None,
        delete_reason=None,
    )
    data.update(kwargs)
    return SimpleNamespace(**data)


def _invoice(**kwargs):
    data = dict(
        id=7,
        delivery_id=5,
        payment_status="unpaid",
        payment_amount=None,
        credit_note_no=None,
        credit_note_amount=None,
        voided_at=None,
        void_reason=None,
    )
    data.update(kwargs)
    return SimpleNamespace(**data)


def _db(header, invoice=None):
    db = MagicMock()

    def get(model, pk):
        if model is DeliveryHeader and int(pk) == int(header.id):
            return header
        return None

    db.get.side_effect = get
    db.scalars.return_value.first.return_value = invoice
    return db


def _soft_delete(db, header, *, role="admin", reason="salah buat"):
    with patch("app.services.delivery_cancel.po_ids_from_delivery", return_value=set()):
        return cancel_mod.soft_delete_delivery(
            db,
            header.id,
            reason=reason,
            actor="tester",
            role=role,
        )


def test_soft_delete_draft_sets_flag_keeps_status_and_second_call_rejected():
    header = _header()
    db = _db(header)
    _soft_delete(db, header)
    assert header.is_deleted is True
    assert header.status == "draft"
    assert header.delete_reason == "salah buat"
    assert header.deleted_by == "tester"
    assert header.deleted_at is not None
    assert header.cancel_reason == "salah buat"
    db.commit.assert_called()

    with pytest.raises(HTTPException) as exc:
        _soft_delete(db, header)
    assert exc.value.status_code == 400
    assert "sudah dihapus" in exc.value.detail.lower()


def test_cancel_alias_calls_soft_delete():
    header = _header()
    db = _db(header)
    with patch("app.services.delivery_cancel.po_ids_from_delivery", return_value=set()):
        cancel_mod.cancel_delivery(
            db, header.id, reason="alias", actor="tester", role="admin"
        )
    assert header.is_deleted is True
    assert header.status == "draft"


def test_soft_delete_sent_is_rejected():
    header = _header(status="sent")
    db = _db(header, invoice=None)
    with pytest.raises(HTTPException) as exc:
        _soft_delete(db, header, role="warehouse")
    assert exc.value.status_code == 400
    assert "terkirim" in exc.value.detail.lower()
    assert header.is_deleted is False
    assert header.status == "sent"


def test_soft_delete_draft_unpaid_invoice_voids_for_admin():
    header = _header(status="draft")
    inv = _invoice()
    db = _db(header, inv)
    _soft_delete(db, header, role="admin")
    assert header.is_deleted is True
    assert header.status == "draft"
    assert inv.voided_at is not None
    assert inv.void_reason == "salah buat"


def test_warehouse_cannot_delete_when_invoice_exists():
    header = _header(status="draft")
    inv = _invoice()
    db = _db(header, inv)
    with pytest.raises(HTTPException) as exc:
        _soft_delete(db, header, role="warehouse")
    assert exc.value.status_code == 403
    assert header.is_deleted is False
    assert header.status == "draft"
    assert inv.voided_at is None


def test_soft_delete_rejects_paid_invoice():
    header = _header(status="draft")
    db = _db(header, _invoice(payment_status="paid"))
    with pytest.raises(HTTPException) as exc:
        _soft_delete(db, header, role="admin")
    assert exc.value.status_code == 400
    assert "retur" in exc.value.detail.lower()
    assert header.is_deleted is False
    assert header.status == "draft"


def test_soft_delete_rejects_payment_amount():
    header = _header(status="draft")
    db = _db(header, _invoice(payment_amount=Decimal("10")))
    with pytest.raises(HTTPException) as exc:
        _soft_delete(db, header, role="finance")
    assert exc.value.status_code == 400
    assert header.is_deleted is False
    assert header.status == "draft"


def test_soft_delete_rejects_bc_number():
    header = _header(status="draft", bc_number="BC-9")
    db = _db(header)
    with pytest.raises(HTTPException) as exc:
        _soft_delete(db, header)
    assert exc.value.status_code == 400
    assert "bc" in exc.value.detail.lower()
    assert header.is_deleted is False
    assert header.status == "draft"


def test_soft_delete_rejects_credit_note():
    header = _header(status="draft")
    db = _db(header, _invoice(credit_note_no="CN-1", credit_note_amount=Decimal("5")))
    with pytest.raises(HTTPException) as exc:
        _soft_delete(db, header, role="admin")
    assert exc.value.status_code == 400
    assert header.is_deleted is False
    assert header.status == "draft"


def test_scan_out_skips_deleted():
    header = SimpleNamespace(id=1, status="draft", delivery_number="SJ-1", is_deleted=True)
    db = MagicMock()
    db.get.return_value = header
    out = _mark_deliveries_sent(db, [1], actor="tester", action="scan_out")
    assert out["skipped"] == [{"delivery_id": 1, "reason": "deleted"}]
    assert out["marked_sent"] == []
    assert header.status == "draft"


def test_scan_out_skips_legacy_cancelled():
    header = SimpleNamespace(id=1, status="cancelled", delivery_number="SJ-1", is_deleted=False)
    db = MagicMock()
    db.get.return_value = header
    out = _mark_deliveries_sent(db, [1], actor="tester", action="scan_out")
    assert out["skipped"] == [{"delivery_id": 1, "reason": "deleted"}]
    assert out["marked_sent"] == []
    assert header.status == "cancelled"


def test_sum_delivered_qty_excludes_deleted_header():
    captured = []
    db = MagicMock()
    db.scalar.side_effect = lambda stmt: captured.append(stmt) or Decimal(0)
    assert sum_delivered_qty(db, 9) == Decimal(0)
    sql = str(captured[0].compile(compile_kwargs={"literal_binds": True})).lower()
    assert "is_deleted" in sql
    assert "cancelled" in sql
    assert "canceled" in sql


def test_po_balance_excludes_deleted_header():
    captured = []
    db = MagicMock()

    def scalars(stmt):
        captured.append(stmt)
        result = MagicMock()
        result.one.return_value = Decimal(0)
        return result

    db.scalars.side_effect = scalars
    assert sum_delivered_qty_for_po_detail(db, 7) == Decimal(0)
    assert len(captured) == 2
    for stmt in captured:
        sql = str(stmt.compile(compile_kwargs={"literal_binds": True})).lower()
        assert "is_deleted" in sql
        assert "cancelled" in sql


def test_outstanding_query_excludes_voided_invoice():
    stmt = exclude_voided_invoices(Invoice.__table__.select())
    assert "voided_at" in str(stmt).lower()


def test_put_status_cancelled_is_rejected():
    header = _header()
    db = _db(header)
    user = SimpleNamespace(username="admin", role="admin")
    with pytest.raises(HTTPException) as exc:
        update_delivery(header.id, DeliveryHeaderUpdate(status="cancelled"), db, user)
    assert exc.value.status_code == 400
    assert header.status == "draft"
    assert header.is_deleted is False


def test_reconcile_lowers_stage_when_no_other_sent():
    po = SimpleNamespace(id=3, mkt_workflow_stage="invoice_billing")
    db = MagicMock()
    with patch("app.services.mkt_workflow.po_has_posted_delivery", return_value=False):
        changed = reconcile_po_stage_after_delivery_cancel(
            db, po, actor="tester", exclude_delivery_id=5
        )
    assert changed is True
    assert po.mkt_workflow_stage == "material_followup"


def test_reconcile_keeps_stage_when_other_sent_exists():
    po = SimpleNamespace(id=3, mkt_workflow_stage="sj_invpl")
    db = MagicMock()
    with patch("app.services.mkt_workflow.po_has_posted_delivery", return_value=True):
        changed = reconcile_po_stage_after_delivery_cancel(
            db, po, actor="tester", exclude_delivery_id=5
        )
    assert changed is False
    assert po.mkt_workflow_stage == "sj_invpl"
