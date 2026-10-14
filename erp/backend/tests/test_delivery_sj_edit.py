"""Edit/hapus baris SJ draft dan nomor surat jalan manual."""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models import DeliveryDetail, DeliveryHeader, DocumentSequence, Invoice
from app.schemas import DeliveryDetailUpdate, DeliveryHeaderUpdate
from app.services.document_numbers import raise_floor_surat_jalan_sequence
from app.routers.delivery import delete_delivery_detail, update_delivery, update_delivery_detail


def _header(**kwargs):
    data = dict(
        id=5,
        status="draft",
        delivery_number="THI-M261014001",
        bc_number=None,
        bc_date=None,
        customs_declaration_id=None,
        packing_id=None,
    )
    data.update(kwargs)
    return SimpleNamespace(**data)


def _detail(**kwargs):
    data = dict(
        id=11,
        delivery_id=5,
        production_detail_id=21,
        qty=Decimal("10"),
        qty_roll=1,
        qty_pcs=2,
        returned_qty=None,
        weight=None,
        packing_detail_id=None,
        po_detail_id=None,
    )
    data.update(kwargs)
    return SimpleNamespace(**data)


def _user(role="admin"):
    return SimpleNamespace(username="tester", role=role)


def test_raise_floor_surat_jalan_sequence_bumps_counter():
    db = MagicMock()
    seq = SimpleNamespace(doc_type="THI-M", period="261014", last_value=2)
    db.scalars.return_value.first.return_value = seq
    raise_floor_surat_jalan_sequence(db, "THI-M261014010")
    assert seq.last_value == 10
    db.flush.assert_called()


def test_raise_floor_ignores_non_pattern():
    db = MagicMock()
    raise_floor_surat_jalan_sequence(db, "CUSTOM-SJ-1")
    db.scalars.assert_not_called()


def test_update_delivery_number_draft_ok():
    header = _header()
    db = MagicMock()
    db.get.return_value = header
    db.scalars.return_value.first.return_value = None
    with patch("app.routers.delivery.raise_floor_surat_jalan_sequence") as bump:
        with patch("app.routers.delivery.log_change"):
            out = update_delivery(
                5,
                DeliveryHeaderUpdate(delivery_number="THI-M261010001"),
                db,
                _user(),
            )
    assert out.delivery_number == "THI-M261010001"
    bump.assert_called_once()
    db.commit.assert_called()


def test_update_delivery_number_conflict_409():
    header = _header()
    other = _header(id=9, delivery_number="THI-M261010001")
    db = MagicMock()
    db.get.return_value = header
    db.scalars.return_value.first.return_value = other
    with pytest.raises(HTTPException) as exc:
        update_delivery(
            5,
            DeliveryHeaderUpdate(delivery_number="THI-M261010001"),
            db,
            _user(),
        )
    assert exc.value.status_code == 409
    assert header.delivery_number == "THI-M261014001"


def test_update_delivery_number_sent_rejected():
    header = _header(status="sent")
    db = MagicMock()
    db.get.return_value = header
    with pytest.raises(HTTPException) as exc:
        update_delivery(
            5,
            DeliveryHeaderUpdate(delivery_number="THI-M261010001"),
            db,
            _user(),
        )
    assert exc.value.status_code == 400
    assert "terkirim" in exc.value.detail.lower()


def test_update_delivery_detail_sent_rejected():
    detail = _detail()
    header = _header(status="sent")
    db = MagicMock()

    def get(model, pk):
        if model is DeliveryDetail:
            return detail
        if model is DeliveryHeader:
            return header
        return None

    db.get.side_effect = get
    with pytest.raises(HTTPException) as exc:
        update_delivery_detail(
            11,
            DeliveryDetailUpdate(qty=Decimal("8")),
            db,
            _user(),
            bypass_qc=False,
        )
    assert exc.value.status_code == 400
    assert "terkirim" in exc.value.detail.lower()


def test_delete_delivery_detail_draft_ok():
    detail = _detail()
    header = _header(status="draft")
    db = MagicMock()

    def get(model, pk):
        if model is DeliveryDetail and int(pk) == 11:
            return detail
        if model is DeliveryHeader and int(pk) == 5:
            return header
        return None

    db.get.side_effect = get
    # remaining lines after delete? first() for remaining -> None means empty
    # invoice lookup after sync: None
    db.scalars.return_value.first.return_value = None
    with patch("app.routers.delivery.log_change"):
        with patch("app.routers.delivery._sync_open_invoice_from_delivery") as sync:
            with patch("app.routers.delivery._void_open_invoice_if_no_lines") as void_fn:
                delete_delivery_detail(11, db, _user())
    db.delete.assert_called_once_with(detail)
    sync.assert_called_once_with(db, 5)
    void_fn.assert_called_once()
    db.commit.assert_called()


def test_delete_delivery_detail_sent_rejected():
    detail = _detail()
    header = _header(status="sent")
    db = MagicMock()

    def get(model, pk):
        if model is DeliveryDetail:
            return detail
        if model is DeliveryHeader:
            return header
        return None

    db.get.side_effect = get
    with pytest.raises(HTTPException) as exc:
        delete_delivery_detail(11, db, _user())
    assert exc.value.status_code == 400
    db.delete.assert_not_called()


def test_delete_delivery_detail_with_return_rejected():
    detail = _detail(returned_qty=Decimal("1"))
    header = _header(status="draft")
    db = MagicMock()

    def get(model, pk):
        if model is DeliveryDetail:
            return detail
        if model is DeliveryHeader:
            return header
        return None

    db.get.side_effect = get
    with pytest.raises(HTTPException) as exc:
        delete_delivery_detail(11, db, _user())
    assert exc.value.status_code == 400
    assert "retur" in exc.value.detail.lower()
