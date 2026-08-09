"""Uji production mirror + stock issue bridge MRP→ERP."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models import (
    MaterialStock,
    PoDetail,
    PoHeader,
    ProductionDetail,
    ProductionOrder,
    RawMaterial,
    Warehouse,
)
from app.services import mrp_production_bridge as prod
from app.services import mrp_stock_bridge as stock


def test_production_mirror_idempotent_by_lot(monkeypatch):
    db = MagicMock()
    ph = PoHeader(id=1, po_number="PO-1", status="confirmed")
    pod = PoDetail(id=11, po_id=1, quantity_order=Decimal("100"))
    existing_pd = ProductionDetail(
        id=50, production_id=9, po_detail_id=11, lot_number="WIP-1", qty_planned=Decimal("10")
    )
    existing_pr = ProductionOrder(id=9, po_id=1, production_number="MRP-PRD-1", status="in_progress")

    def _get(model, pk):
        if model is PoDetail and pk == 11:
            return pod
        if model is PoHeader and pk == 1:
            return ph
        if model is ProductionOrder and pk == 9:
            return existing_pr
        return None

    db.get.side_effect = _get
    db.scalars.return_value.first.return_value = existing_pd
    monkeypatch.setattr(prod, "log_change", lambda *a, **k: None)

    result = prod.upsert_production_mirror(
        db,
        source_detail_id=11,
        kode_wip="WIP-1",
        qty_actual=Decimal("12"),
        finish=True,
        actor="t",
    )
    assert result.production_detail_id == 50
    assert result.finished is True
    assert existing_pd.status == "completed"


def test_production_mirror_requires_wip():
    db = MagicMock()
    with pytest.raises(HTTPException):
        prod.upsert_production_mirror(db, source_detail_id=1, kode_wip="")


def test_stock_issue_decrements_existing_stock(monkeypatch):
    db = MagicMock()
    mat = RawMaterial(id=7, code="K-1", name="Kimia", material_type="kimia", unit="kg")
    wh = Warehouse(id=3, code="SHOPFLOOR", name="Shop")
    st = MaterialStock(
        id=1, material_id=7, warehouse_id=3, current_stock=Decimal("10"), reserved_stock=Decimal("0")
    )

    db.get.side_effect = lambda model, pk: mat if model is RawMaterial and pk == 7 else None

    firsts = iter([wh, st])

    def _scalars(_stmt):
        r = MagicMock()
        r.first.side_effect = lambda: next(firsts)
        return r

    db.scalars.side_effect = _scalars
    monkeypatch.setattr(stock, "log_change", lambda *a, **k: None)
    monkeypatch.setattr(stock.settings, "mrp_shopfloor_warehouse_code", "SHOPFLOOR", raising=False)

    result = stock.issue_stock_from_mrp(
        db,
        erp_material_id=7,
        qty=Decimal("2.5"),
        actor="t",
    )
    assert result.qty == Decimal("2.5")
    assert result.stock_after == Decimal("7.5")
    assert st.current_stock == Decimal("7.5")
