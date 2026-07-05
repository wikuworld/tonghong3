"""Format nomor SO per kategori marketing."""

from datetime import date, datetime

from app.services.so_numbering import format_so_number, so_prefix_for_po


def test_so_prefix_production() -> None:
    assert so_prefix_for_po(po_category="production") == "PS"


def test_so_prefix_production_pu_coated() -> None:
    assert so_prefix_for_po(po_category="production", material_group="pu") == "THIPM"


def test_so_prefix_sample() -> None:
    assert so_prefix_for_po(po_category="sample") == "S"


def test_so_prefix_claim() -> None:
    assert so_prefix_for_po(po_category="claim") == "PSC"


def test_so_prefix_return_prod() -> None:
    assert so_prefix_for_po(po_category="return") == "PSR"


def test_so_prefix_return_sample() -> None:
    assert so_prefix_for_po(po_category="return", order_type_label="SAMPLE return") == "SR"


def test_so_number_format_examples() -> None:
    at = datetime(2026, 2, 26)
    assert format_so_number(prefix="PS", at=at, seq_value=1) == "PS26022601"
    assert format_so_number(prefix="THIPM", at=datetime(2026, 2, 23), seq_value=2) == "THIPM26022302"
    assert format_so_number(prefix="S", at=datetime(2025, 1, 10), seq_value=1) == "S25011001"
    assert format_so_number(prefix="PSC", at=datetime(2026, 3, 31), seq_value=3) == "PSC26033103"
    assert format_so_number(prefix="PSR", at=datetime(2026, 1, 6), seq_value=1) == "PSR26010601"
    assert format_so_number(prefix="SR", at=datetime(2026, 1, 6), seq_value=1) == "SR26010601"
