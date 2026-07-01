"""Tests lot number preview vs commit."""

from datetime import datetime
from unittest.mock import MagicMock

from app.models import LotSequence
from app.services.lot_numbers import _prefix_for, peek_lot_number


def _db_without_sequence() -> MagicMock:
    db = MagicMock()
    db.scalars.return_value.first.return_value = None
    return db


def test_peek_lot_number_does_not_increment():
    db = MagicMock()
    seq = LotSequence(prefix="PUM", factory_code="CS004", date_ymd="20260604", last_value=5)
    db.scalars.return_value.first.return_value = seq

    lot = peek_lot_number(
        db,
        po_category="production",
        factory_code="CS004",
        material_group="pu",
        at=datetime(2026, 6, 4, 12, 0, 0),
    )

    assert lot == "PUMCS004260604006"
    assert seq.last_value == 5


def test_prefix_return_and_subcont_suede_are_distinct():
    assert _prefix_for("suede", "return") == "QYC"
    assert _prefix_for("suede", "subcont") == "KYC"
    db = _db_without_sequence()
    ret = peek_lot_number(
        db,
        po_category="return",
        factory_code="PA010",
        material_group="suede",
        at=datetime(2026, 3, 5, 10, 0, 0),
    )
    sub = peek_lot_number(
        db,
        po_category="subcont",
        factory_code="MP033",
        material_group="suede",
        at=datetime(2026, 3, 5, 10, 0, 0),
    )
    assert ret == "QYCPA010260305001"
    assert sub == "KYCMP033260305001"


def test_prefix_return_and_subcont_pu_are_distinct():
    assert _prefix_for("pu", "return") == "PUR"
    assert _prefix_for("pu", "subcont") == "PUK"
    db = _db_without_sequence()
    ret = peek_lot_number(
        db,
        po_category="return",
        factory_code="AD002",
        material_group="pu",
        at=datetime(2026, 4, 1, 10, 0, 0),
    )
    sub = peek_lot_number(
        db,
        po_category="subcont",
        factory_code="AD002",
        material_group="pu",
        at=datetime(2026, 4, 1, 10, 0, 0),
    )
    assert ret == "PURAD002260401001"
    assert sub == "PUKAD002260401001"
