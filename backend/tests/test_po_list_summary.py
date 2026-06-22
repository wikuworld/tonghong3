"""Unit tests for PO list summary helpers."""

from datetime import date
from types import SimpleNamespace

from app.services.po_list_summary import build_etd_display, build_material_hint


def test_build_material_hint_empty_po():
    assert build_material_hint(None, 0) is None


def test_build_material_hint_single_line():
    assert build_material_hint('ECO TECH COMFORT', 1) == 'ECO TECH COMFORT'


def test_build_material_hint_multi_line():
    assert build_material_hint('VIRGIN HYDRO PU', 5) == 'VIRGIN HYDRO PU +4'


def test_build_material_hint_no_material_name():
    assert build_material_hint(None, 2) is None
    assert build_material_hint('', 3) is None


def test_build_etd_display_from_header():
    assert build_etd_display(date(2026, 5, 12), []) == '2026-05-12'


def test_build_etd_display_from_delivery_schedule():
    detail = SimpleNamespace(
        line_etd=None,
        delivery_schedules=[SimpleNamespace(delivery_date=date(2026, 6, 5))],
    )
    assert build_etd_display(None, [detail]) == '2026-06-05'


def test_build_etd_display_multi_line_same_date():
    detail = SimpleNamespace(
        line_etd=date(2026, 5, 4),
        delivery_schedules=[],
    )
    rows = [detail, SimpleNamespace(line_etd=date(2026, 5, 4), delivery_schedules=[])]
    assert build_etd_display(None, rows) == '2026-05-04 +1'
