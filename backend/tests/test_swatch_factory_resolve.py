"""Tests resolve_swatch_factory_keys helpers."""

from app.services.color_swatch import _compact_alnum, _strip_company_prefix, normalize_factory_key


def test_compact_alnum():
    assert _compact_alnum("PT. CHANG SHIN") == "PTCHANGSHIN"
    assert _compact_alnum("CHANGSHIN") == "CHANGSHIN"


def test_strip_company_prefix():
    assert "CHANG SHIN" in _strip_company_prefix("PT. CHANG SHIN INDONESIA")


def test_normalize_factory_key():
    assert normalize_factory_key("  changshin  ") == "CHANGSHIN"
