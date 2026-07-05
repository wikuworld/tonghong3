"""Tests for delivery shipment / brand validation."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.delivery_shipment import (
    brand_key,
    lot_number_for_line,
    so_number_for_line,
    validate_same_customer_and_brand,
)


class _Ph:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _Pod:
    def __init__(self, **kw):
        self.__dict__.update(kw)


class _Pd:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def test_brand_key_prefers_snapshot():
    ph = _Ph(brand_name_snapshot="NIKE", buyer="ADIDAS")
    assert brand_key(ph) == "NIKE"


def test_lot_number_from_thi_line_ref():
    pod = _Pod(thi_line_ref="PUMSL044260611001", system_reference="")
    assert lot_number_for_line(pod, None) == "PUMSL044260611001"


def test_so_number_from_po_number():
    ph = _Ph(po_number="THIPM26022302")
    assert so_number_for_line(ph, None) == "THIPM26022302"


def test_validate_same_customer_and_brand_requires_rows():
    with pytest.raises(HTTPException) as exc:
        validate_same_customer_and_brand(MagicMock(), [])
    assert exc.value.status_code == 400
    assert "minimal satu" in exc.value.detail.lower()


def test_validate_same_customer_and_brand_rejects_mixed_brands():
    db = MagicMock()

    def fake_get(model, obj_id):
        from app.models import PoDetail, PoHeader, ProductionDetail

        if model is ProductionDetail:
            pd = MagicMock()
            pd.po_detail_id = obj_id
            return pd
        if model is PoDetail:
            pod = MagicMock()
            pod.po_id = obj_id
            return pod
        if model is PoHeader:
            ph = MagicMock()
            ph.id = obj_id
            ph.po_number = f"PO-{obj_id}"
            ph.customer_id = 1
            ph.brand_name_snapshot = "NIKE" if obj_id == 1 else "ADIDAS"
            ph.buyer = ph.brand_name_snapshot
            return ph
        return None

    db.get.side_effect = fake_get

    with pytest.raises(HTTPException) as exc:
        validate_same_customer_and_brand(db, [1, 2])
    assert exc.value.status_code == 400
    assert "brand" in exc.value.detail.lower()
