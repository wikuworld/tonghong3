"""Update baris SO: marketing resolve ulang; admin boleh set harga."""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

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
