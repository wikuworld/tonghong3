"""Unit tests for PO list summary helpers."""

from datetime import date
from types import SimpleNamespace

from app.services.po_list_summary import build_etd_display, build_material_hint, build_reply_etd_display


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


def test_build_reply_etd_display_empty():
    assert build_reply_etd_display([]) is None
    assert build_reply_etd_display([SimpleNamespace(line_etd=None)]) is None


def test_build_reply_etd_display_single():
    assert build_reply_etd_display([SimpleNamespace(line_etd=date(2026, 7, 1))]) == '2026-07-01'


def test_build_reply_etd_display_multi_dates():
    rows = [
        SimpleNamespace(line_etd=date(2026, 7, 1)),
        SimpleNamespace(line_etd=date(2026, 7, 15)),
    ]
    assert build_reply_etd_display(rows) == '2026-07-01, 2026-07-15'


def test_build_reply_etd_display_same_date_multi_lines():
    rows = [
        SimpleNamespace(line_etd=date(2026, 9, 29)),
        SimpleNamespace(line_etd=date(2026, 9, 29)),
    ]
    assert build_reply_etd_display(rows) == '2026-09-29'


def test_build_reply_etd_display_ignores_delivery_schedule():
    detail = SimpleNamespace(
        line_etd=None,
        delivery_schedules=[SimpleNamespace(delivery_date=date(2026, 6, 5))],
    )
    assert build_reply_etd_display([detail]) is None


def test_build_lot_hint_unique_lots():
    from app.services.po_list_summary import build_lot_hint

    rows = [
        SimpleNamespace(thi_line_ref='LOT-A', system_reference=None),
        SimpleNamespace(thi_line_ref='LOT-B', system_reference=None),
        SimpleNamespace(thi_line_ref='LOT-A', system_reference=None),
        SimpleNamespace(thi_line_ref='', system_reference=''),
    ]
    assert build_lot_hint(rows) == 'LOT-A, LOT-B'


def test_build_lot_hint_prefers_thi_over_system_reference():
    from app.services.po_list_summary import build_lot_hint

    rows = [
        SimpleNamespace(thi_line_ref='PUMAD002260922001', system_reference=None),
        SimpleNamespace(thi_line_ref='', system_reference='SYS-ONLY'),
    ]
    assert build_lot_hint(rows) == 'PUMAD002260922001, SYS-ONLY'


def test_build_lot_hint_empty():
    from app.services.po_list_summary import build_lot_hint

    assert build_lot_hint([]) is None
    assert build_lot_hint([SimpleNamespace(thi_line_ref=None, system_reference=None)]) is None
