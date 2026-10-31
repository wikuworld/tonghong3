"""Periode list harga: tumpang tindih ditolak, resolver memilih tanggal."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.buyer_price_import import STANDARD_COLUMN_KEYS, build_price_cells
from app.services.buyer_price_period import assert_no_period_overlap, pick_price_list
from app.services.buyer_price_resolve import resolve_unit_price_for_buyer


def _list(**kwargs):
    data = {
        "id": 1,
        "brand_id": 1,
        "buyer_code": "NIKE",
        "period_label": None,
        "period_start": None,
        "period_end": None,
    }
    data.update(kwargs)
    return SimpleNamespace(**data)


def test_non_overlapping_periods_are_allowed():
    db = MagicMock()
    db.scalars.return_value.all.return_value = [
        _list(
            id=1,
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            period_label="2025",
        )
    ]
    assert_no_period_overlap(
        db,
        brand_id=1,
        buyer_code="NIKE",
        period_start=date(2026, 1, 1),
        period_end=date(2026, 12, 31),
        brand_label="Nike",
    )


def test_overlapping_periods_rejected_409():
    db = MagicMock()
    db.scalars.return_value.all.return_value = [
        _list(
            id=1,
            period_start=date(2025, 1, 1),
            period_end=date(2025, 12, 31),
            period_label="2025",
        )
    ]
    with pytest.raises(HTTPException) as exc:
        assert_no_period_overlap(
            db,
            brand_id=1,
            buyer_code="nike",
            period_start=date(2025, 6, 1),
            period_end=date(2026, 5, 31),
            brand_label="Nike",
        )
    assert exc.value.status_code == 409
    assert "Nike" in exc.value.detail
    assert "2025" in exc.value.detail


def test_pick_list_covering_as_of():
    early = _list(id=1, period_start=date(2025, 1, 1), period_end=date(2025, 12, 31))
    late = _list(id=2, period_start=date(2026, 1, 1), period_end=date(2026, 12, 31))
    chosen = pick_price_list([early, late], date(2026, 3, 1))
    assert chosen.id == 2


def test_pick_latest_start_when_ranges_both_cover():
    wide = _list(id=1, period_start=date(2026, 1, 1), period_end=date(2026, 12, 31))
    narrow = _list(id=2, period_start=date(2026, 6, 1), period_end=date(2026, 8, 31))
    chosen = pick_price_list([wide, narrow], date(2026, 7, 1))
    assert chosen.id == 2


def test_pick_prefers_po_brand_when_ranges_overlap():
    official = _list(
        id=25,
        brand_id=1,
        period_start=date(2026, 7, 1),
        period_end=date(2026, 12, 31),
    )
    trial = _list(
        id=41,
        brand_id=13,
        period_start=date(2026, 10, 1),
        period_end=date(2026, 10, 31),
    )
    when = date(2026, 10, 21)
    assert pick_price_list([official, trial], when, brand_id=1).id == 25
    assert pick_price_list([official, trial], when, brand_id=99).id == 41
    assert pick_price_list([official, trial], when).id == 41


def test_undated_list_is_fallback():
    dated = _list(id=1, period_start=date(2026, 1, 1), period_end=date(2026, 6, 30))
    legacy = _list(id=9, period_start=None, period_end=None)
    chosen = pick_price_list([dated, legacy], date(2026, 8, 1))
    assert chosen.id == 9


def _sheet(list_id: int):
    white = 1.11 if list_id == 1 else 9.0 if list_id == 9 else 2.22
    return {
        "rows": [
            build_price_cells(item="GENERIC PU COATED", block="COMMON", white=white),
        ],
        "meta_json": {"column_keys": list(STANDARD_COLUMN_KEYS)},
    }


def test_resolve_uses_list_covering_as_of(monkeypatch):
    early = _list(id=1, period_start=date(2025, 1, 1), period_end=date(2025, 12, 31))
    late = _list(id=2, period_start=date(2026, 1, 1), period_end=date(2026, 12, 31))
    db = MagicMock()
    db.scalars.return_value.all.return_value = [early, late]
    monkeypatch.setattr("app.services.buyer_price_resolve.list_to_api_dict", lambda _db, list_id: _sheet(list_id))
    monkeypatch.setattr("app.services.buyer_price_resolve.is_outside_banten_factory", lambda *_a, **_k: False)
    result = resolve_unit_price_for_buyer(
        db,
        "NIKE",
        material_name="GENERIC PU COATED",
        as_of=date(2026, 4, 1),
    )
    assert result["matched"] is True
    assert result["unit_price"] == Decimal("2.22")
    assert result["period_start"] == date(2026, 1, 1)
    assert result["period_end"] == date(2026, 12, 31)
    assert result["price_block"] == "COMMON"


def test_resolve_falls_back_to_undated_list(monkeypatch):
    dated = _list(id=1, period_start=date(2026, 1, 1), period_end=date(2026, 3, 31))
    legacy = _list(id=9, period_start=None, period_end=None)
    db = MagicMock()
    db.scalars.return_value.all.return_value = [dated, legacy]
    monkeypatch.setattr("app.services.buyer_price_resolve.list_to_api_dict", lambda _db, list_id: _sheet(list_id))
    monkeypatch.setattr("app.services.buyer_price_resolve.is_outside_banten_factory", lambda *_a, **_k: False)
    result = resolve_unit_price_for_buyer(
        db,
        "NIKE",
        material_name="GENERIC PU COATED",
        as_of=date(2026, 8, 1),
    )
    assert result["matched"] is True
    assert result["unit_price"] == Decimal("9")


def test_resolve_uses_brand_when_periods_overlap(monkeypatch):
    official = _list(
        id=25,
        brand_id=1,
        period_start=date(2026, 7, 1),
        period_end=date(2026, 12, 31),
    )
    trial = _list(
        id=41,
        brand_id=13,
        period_start=date(2026, 10, 1),
        period_end=date(2026, 10, 31),
    )
    db = MagicMock()
    db.scalars.return_value.all.return_value = [official, trial]

    def sheet(_db, list_id):
        white = 1.25 if list_id == 25 else 9.99
        return {
            "rows": [build_price_cells(item="GENERIC PU COATED", block="COMMON", white=white)],
            "meta_json": {"column_keys": list(STANDARD_COLUMN_KEYS)},
        }

    monkeypatch.setattr("app.services.buyer_price_resolve.list_to_api_dict", sheet)
    monkeypatch.setattr("app.services.buyer_price_resolve.is_outside_banten_factory", lambda *_a, **_k: False)
    result = resolve_unit_price_for_buyer(
        db,
        "NIKE",
        material_name="GENERIC PU COATED",
        as_of=date(2026, 10, 21),
        brand_id=1,
    )
    assert result["unit_price"] == Decimal("1.25")
    assert result["period_start"] == date(2026, 7, 1)
