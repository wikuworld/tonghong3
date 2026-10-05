"""Unit tests master integrity helpers."""

from app.services.buyer_registry import _HARDCODE
from app.services.material_aliases import _norm_key


def test_buyer_hardcode_includes_puma_reebok():
    assert "PUMA" in _HARDCODE
    assert "REEBOK" in _HARDCODE
    assert "GLOBAL" in _HARDCODE


def test_material_alias_norm_key():
    assert _norm_key("  pm  generic ") == "PM GENERIC"
