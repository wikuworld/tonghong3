"""Jadwal kirim dari POST /po/{id}/details datang sebagai dict setelah model_dump()."""

from datetime import date
from decimal import Decimal

from app.routers.po import _coerce_delivery_schedule_items, _validate_delivery_schedule_items
from app.schemas import DeliveryScheduleItem


def test_coerce_accepts_dict_and_model():
    items = _coerce_delivery_schedule_items(
        [
            {"sequence_no": 1, "qty": "12.5", "delivery_date": "2026-08-23"},
            DeliveryScheduleItem(sequence_no=2, qty=Decimal("3"), delivery_date=date(2026, 8, 24)),
        ]
    )
    assert [i.sequence_no for i in items] == [1, 2]
    assert items[0].qty == Decimal("12.5")
    _validate_delivery_schedule_items(items)
