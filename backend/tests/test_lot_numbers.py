"""Tests lot number preview vs commit."""

from datetime import datetime
from unittest.mock import MagicMock

from app.models import LotSequence
from app.services.lot_numbers import peek_lot_number


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
