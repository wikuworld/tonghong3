"""Update baris SO: marketing resolve ulang; admin boleh set harga."""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.routers.po import _apply_unit_price_on_update


def test_admin_keeps_client_unit_price():
    data = {"unit_price": Decimal("9.99"), "material_name": "GENERIC PU COATED"}
    _apply_unit_price_on_update(
        MagicMock(),
        SimpleNamespace(po_category="production", buyer="NIKE", factory_code="HW036"),
        SimpleNamespace(material_name="X"),
        data,
        SimpleNamespace(role="admin"),
    )
    assert data["unit_price"] == Decimal("9.99")


def test_marketing_qty_only_does_not_touch_price():
    data = {"quantity_order": Decimal("10"), "unit_price": Decimal("9.99")}
    _apply_unit_price_on_update(
        MagicMock(),
        SimpleNamespace(po_category="production", buyer="NIKE", factory_code="HW036"),
        SimpleNamespace(material_name="GENERIC PU COATED"),
        data,
        SimpleNamespace(role="marketing"),
    )
    assert "unit_price" not in data


def test_marketing_material_change_resolves_price(monkeypatch):
    data = {"material_name": "GENERIC PU COATED", "color_family": None, "unit_price": Decimal("9.99")}
    monkeypatch.setattr(
        "app.routers.po.resolve_unit_price_for_buyer",
        lambda *a, **k: {"unit_price": Decimal("1.13"), "matched": True},
    )
    _apply_unit_price_on_update(
        MagicMock(),
        SimpleNamespace(po_category="production", buyer="NIKE", factory_code="HW036"),
        SimpleNamespace(
            material_name="OLD",
            color=None,
            style_article=None,
            thickness_text=None,
            color_family=None,
            emboss=None,
        ),
        data,
        SimpleNamespace(role="marketing"),
    )
    assert data["unit_price"] == Decimal("1.13")


def _po():
    return SimpleNamespace(po_category="production", buyer="NB", factory_code="BI020", order_date=None)


def test_special_percent_and_nominal_use_list_price(monkeypatch):
    monkeypatch.setattr(
        "app.routers.po.resolve_unit_price_for_buyer",
        lambda *a, **k: {"unit_price": Decimal("2")},
    )
    percent = {
        "is_special_price": True,
        "discount_type": "percent",
        "discount_value": Decimal("-10"),
        "detail_remark": "season",
        "material_name": "PU",
        "unit_price": Decimal("9"),
    }
    _apply_unit_price_on_update(MagicMock(), _po(), None, percent, SimpleNamespace(role="marketing"))
    assert percent["list_unit_price"] == Decimal("2.0000")
    assert percent["unit_price"] == Decimal("1.8000")

    nominal = {
        "is_special_price": True,
        "discount_type": "nominal",
        "discount_value": Decimal("0.15"),
        "detail_remark": "season",
        "material_name": "PU",
    }
    _apply_unit_price_on_update(MagicMock(), _po(), None, nominal, SimpleNamespace(role="admin"))
    assert nominal["unit_price"] == Decimal("2.1500")


def test_special_price_requires_remark():
    with pytest.raises(HTTPException) as exc:
        _apply_unit_price_on_update(
            MagicMock(),
            _po(),
            None,
            {"is_special_price": True, "discount_type": "percent", "discount_value": Decimal("-5")},
            SimpleNamespace(role="marketing"),
        )
    assert exc.value.status_code == 400


def test_unchanged_special_line_is_not_recomputed(monkeypatch):
    def _boom(*_a, **_k):
        raise AssertionError("resolve tidak boleh dipanggil")

    monkeypatch.setattr("app.routers.po.resolve_unit_price_for_buyer", _boom)
    row = SimpleNamespace(
        is_special_price=True,
        discount_type="percent",
        discount_value=Decimal("-10"),
        material_name="PU",
        color=None,
        style_article=None,
        thickness_text=None,
        color_family=None,
        emboss=None,
        unit_price=Decimal("1.8000"),
        detail_remark="season",
    )
    data = {
        "is_special_price": True,
        "discount_type": "percent",
        "discount_value": Decimal("-10"),
        "material_name": "PU",
        "detail_remark": "season",
        "unit_price": Decimal("9"),
    }
    _apply_unit_price_on_update(MagicMock(), _po(), row, data, SimpleNamespace(role="marketing"))
    assert "unit_price" not in data


def test_spec_change_reapplies_stored_modifier(monkeypatch):
    monkeypatch.setattr(
        "app.routers.po.resolve_unit_price_for_buyer",
        lambda *a, **k: {"unit_price": Decimal("3")},
    )
    row = SimpleNamespace(
        is_special_price=True,
        discount_type="percent",
        discount_value=Decimal("-10"),
        material_name="OLD",
        color=None,
        style_article=None,
        thickness_text=None,
        color_family=None,
        emboss=None,
        detail_remark="season",
        unit_price=Decimal("1.8000"),
    )
    data = {"material_name": "GENERIC PU COATED", "unit_price": Decimal("9")}
    _apply_unit_price_on_update(MagicMock(), _po(), row, data, SimpleNamespace(role="marketing"))
    assert data["list_unit_price"] == Decimal("3.0000")
    assert data["unit_price"] == Decimal("2.7000")
    assert data["discount_value"] == Decimal("-10")


def test_subcont_keeps_client_price_for_marketing():
    data = {"unit_price": Decimal("2.00"), "material_name": "SPLIT SUEDE"}
    _apply_unit_price_on_update(
        MagicMock(),
        SimpleNamespace(po_category="subcont", buyer="NIKE", factory_code="HW036"),
        SimpleNamespace(material_name="SPLIT SUEDE"),
        data,
        SimpleNamespace(role="marketing"),
    )
    assert data["unit_price"] == Decimal("2.00")
