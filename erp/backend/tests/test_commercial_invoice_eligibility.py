"""CI boleh dicetak tanpa menandai INVPL (sejajar SJ)."""

from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.models import DeliveryHeader, PackingHeader
from app.services.marketing_documents import commercial_invoice_eligibility


def _db(hdr, *, packing=None, details=None):
    db = MagicMock()
    detail_rows = details if details is not None else [SimpleNamespace(id=1)]
    db.scalars.return_value.all.return_value = detail_rows

    def _get(model, pk):
        if model is DeliveryHeader and int(pk) == int(hdr.id):
            return hdr
        if model is PackingHeader and packing is not None and int(pk) == int(packing.id):
            return packing
        return None

    db.get.side_effect = _get
    return db


def test_ci_allowed_outtown_without_invpl_mark():
    today = date.today()
    hdr = SimpleNamespace(
        id=10,
        packing_id=3,
        delivery_date=today,
        delivery_zone="outtown",
    )
    packing = SimpleNamespace(id=3, invpl_printed_at=None)
    ok, code = commercial_invoice_eligibility(_db(hdr, packing=packing), 10)
    assert ok is True
    assert code == ""


def test_ci_allowed_multi_packing_delivery_without_header_packing():
    today = date.today()
    hdr = SimpleNamespace(
        id=11,
        packing_id=None,
        delivery_date=today,
        delivery_zone="outtown",
    )
    details = [SimpleNamespace(id=1, packing_detail_id=9)]
    ok, code = commercial_invoice_eligibility(_db(hdr, details=details), 11)
    assert ok is True
    assert code == ""


def test_ci_local_still_waits_h_plus_1():
    today = date.today()
    hdr = SimpleNamespace(
        id=12,
        packing_id=3,
        delivery_date=today,
        delivery_zone="local",
    )
    packing = SimpleNamespace(id=3, invpl_printed_at=None)
    ok, code = commercial_invoice_eligibility(_db(hdr, packing=packing), 12)
    assert ok is False
    assert code == "local_wait_h_plus_1"


def test_ci_local_ok_on_h_plus_1():
    today = date.today()
    hdr = SimpleNamespace(
        id=13,
        packing_id=3,
        delivery_date=today - timedelta(days=1),
        delivery_zone="local",
    )
    packing = SimpleNamespace(id=3, invpl_printed_at=None)
    ok, code = commercial_invoice_eligibility(_db(hdr, packing=packing), 13)
    assert ok is True
    assert code == ""
