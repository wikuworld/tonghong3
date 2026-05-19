"""Uji ringkas util filter tanggal untuk endpoint delivery-lines marketing."""

from datetime import date

from app.routers.marketing import _parse_iso_date_optional


def test_parse_iso_date_optional_accepts_none_and_blank():
    assert _parse_iso_date_optional(None) is None
    assert _parse_iso_date_optional("") is None
    assert _parse_iso_date_optional("   ") is None


def test_parse_iso_date_optional_parses_yyyy_mm_dd():
    assert _parse_iso_date_optional("2026-05-12") == date(2026, 5, 12)
    assert _parse_iso_date_optional("2026-05-12T00:00:00") == date(2026, 5, 12)
