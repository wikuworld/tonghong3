"""Uji packing MRP finish → packing ERP done + QC, tanpa Delivery."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

from fastapi import HTTPException
import pytest

from app.models import PackingDetail, PackingHeader, ProductionDetail, QcDetail, QcHeader
from app.services import mrp_packing_bridge as bridge


def test_kode_packing_strips_mrp_prefix():
    pk = PackingHeader(packing_number="MRP-FG-99")
    assert bridge.kode_packing_from_erp(pk) == "FG-99"
    pk2 = PackingHeader(packing_number="PACK-1")
    assert bridge.kode_packing_from_erp(pk) == "FG-99"
    assert bridge.kode_packing_from_erp(pk2) == "PACK-1"


def test_ensure_rejects_empty_lines():
    db = MagicMock()
    with pytest.raises(HTTPException) as exc:
        bridge.ensure_erp_packing_from_mrp_finish(
            db,
            mrp_packing_id=1,
            kode_packing="FG-1",
            production_id=2,
            lines=[],
        )
    assert exc.value.status_code == 400


def test_ensure_creates_packing_and_qc(monkeypatch):
    db = MagicMock()

    def _scalars(_stmt):
        result = MagicMock()
        result.first.return_value = None
        return result

    db.scalars.side_effect = _scalars
    pd = ProductionDetail(id=11, qty_actual=Decimal("10"), qty_planned=Decimal("10"))

    def _get(model, pk):
        if model is ProductionDetail and pk == 11:
            return pd
        return None

    db.get.side_effect = _get
    nums = iter(["QC-X", "PACK-X"])
    monkeypatch.setattr(bridge, "next_number", lambda *_a, **_k: next(nums))
    monkeypatch.setattr(bridge, "log_change", lambda *a, **k: None)

    added = []

    def _add(obj):
        added.append(obj)
        if isinstance(obj, PackingHeader):
            obj.id = 70
        if isinstance(obj, QcHeader):
            obj.id = 80
        if isinstance(obj, QcDetail):
            obj.id = 81
        if isinstance(obj, PackingDetail):
            obj.id = 90

    db.add.side_effect = _add

    result = bridge.ensure_erp_packing_from_mrp_finish(
        db,
        mrp_packing_id=4,
        kode_packing="FG-99",
        production_id=5,
        lines=[(11, 10)],
        actor="tester",
    )
    assert result.created is True
    assert result.packing_id == 70
    assert result.production_id == 5
    pk = next(x for x in added if isinstance(x, PackingHeader))
    assert pk.source == "mrp"
    assert pk.status == "done"
    assert pk.production_id == 5
    assert pk.mrp_packing_id == 4
    assert pk.mrp_fg_id is None
    assert any(isinstance(x, QcDetail) and x.is_ok is True for x in added)
    assert any(isinstance(x, PackingDetail) and x.production_detail_id == 11 for x in added)
    assert not any(type(x).__name__ == "DeliveryHeader" for x in added)
