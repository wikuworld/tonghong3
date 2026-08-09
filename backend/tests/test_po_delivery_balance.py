"""Uji saldo kiriman vs qty order PO."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models import PoDetail, ProductionDetail
from app.services import po_delivery_balance as svc


def _mock_db(
    *,
    quantity_order=Decimal("100"),
    delivered_prod=Decimal("0"),
    delivered_direct=Decimal("0"),
    po_detail_id=10,
):
    db = MagicMock()
    pod = PoDetail(id=po_detail_id, quantity_order=quantity_order)
    pd = ProductionDetail(id=99, po_detail_id=po_detail_id)

    def get(model, pk):
        if model is PoDetail and pk == po_detail_id:
            return pod
        if model is ProductionDetail and pk == 99:
            return pd
        return None

    db.get.side_effect = get

    ones = iter([delivered_prod, delivered_direct])

    def _scalars(_stmt):
        result = MagicMock()
        result.one.side_effect = lambda: next(ones)
        return result

    db.scalars.side_effect = _scalars
    return db


def test_validate_delivery_qty_within_balance():
    db = _mock_db()
    svc.validate_delivery_qty_against_po_balance(
        db, production_detail_id=99, qty=Decimal("50")
    )


def test_validate_delivery_qty_exceeds_balance():
    db = _mock_db()
    with pytest.raises(HTTPException) as exc:
        svc.validate_delivery_qty_against_po_balance(
            db, production_detail_id=99, qty=Decimal("150")
        )
    assert exc.value.status_code == 400
    assert "melebihi saldo" in str(exc.value.detail).lower()


def test_remaining_po_detail_qty():
    db = _mock_db(delivered_prod=Decimal("30"), delivered_direct=Decimal("0"))
    remaining = svc.remaining_po_detail_qty(db, 10)
    assert remaining == Decimal("70")


def test_remaining_includes_direct_delivery():
    db = _mock_db(delivered_prod=Decimal("10"), delivered_direct=Decimal("20"))
    remaining = svc.remaining_po_detail_qty(db, 10)
    assert remaining == Decimal("70")
