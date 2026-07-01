"""Tests normalisasi nomor lot."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.lot_number_normalize import (
    is_legacy_lot_placeholder,
    normalize_lot_references,
    rewrite_subcont_lot_prefix,
)


def test_rewrite_subcont_lot_prefix():
    assert rewrite_subcont_lot_prefix("QYCMP033260305001") == "KYCMP033260305001"
    assert rewrite_subcont_lot_prefix("PURAD002260401001") == "PUKAD002260401001"
    assert rewrite_subcont_lot_prefix("MYCMP033260305001") is None
    assert rewrite_subcont_lot_prefix("QYCPA010260305001") == "KYCPA010260305001"
    assert rewrite_subcont_lot_prefix("") is None


def test_is_legacy_lot_placeholder():
    assert is_legacy_lot_placeholder("THI-") is True
    assert is_legacy_lot_placeholder("PU-2901") is True
    assert is_legacy_lot_placeholder("PUMAD002260605001") is False
    assert is_legacy_lot_placeholder("KYCMP033260305001") is False


def test_normalize_subcont_and_legacy_dry_run():
    subcont_detail = SimpleNamespace(
        id=1,
        po_id=10,
        thi_line_ref="QYCMP033260305001",
        system_reference="QYCMP033260305001",
    )
    legacy_detail = SimpleNamespace(
        id=2,
        po_id=11,
        thi_line_ref="PU-2901",
        system_reference="SYS-SO-202604-00001",
    )
    subcont_hdr = SimpleNamespace(po_category="subcont", po_number="SC-001", factory_code="MP033")
    prod_hdr = SimpleNamespace(po_category="production", po_number="SO-001", factory_code="AD002")

    db = MagicMock()
    db.execute.return_value.all.return_value = [
        (subcont_detail, subcont_hdr),
        (legacy_detail, prod_hdr),
    ]
    db.scalars.return_value.all.return_value = []

    result = normalize_lot_references(db, dry_run=True, clear_legacy_placeholders=True)
    assert result.subcont_prefix_updated == 1
    assert result.system_reference_updated == 1
    assert result.legacy_cleared == 1
    assert subcont_detail.thi_line_ref == "QYCMP033260305001"
    assert legacy_detail.thi_line_ref == "PU-2901"
    db.commit.assert_not_called()
