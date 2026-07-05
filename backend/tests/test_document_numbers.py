"""Nomor dokumen THI-/IN- mengikuti kategori PO."""

from app.models import PoHeader
from app.services.document_numbers import (
    category_letter_for_po,
    invoice_display_number,
    surat_jalan_display_number,
)


def test_sj_replaces_middle_letter_for_sample() -> None:
    ph = PoHeader(po_category="sample")
    assert surat_jalan_display_number("THI-C260318015", ph) == "THI-M260318015"


def test_invoice_replaces_middle_letter() -> None:
    ph = PoHeader(po_category="claim")
    assert invoice_display_number("IN-C26031801", ph) == "IN-L26031801"


def test_foc_in_order_type_label() -> None:
    ph = PoHeader(po_category="production", order_type_label="SAMPLE FOC")
    assert category_letter_for_po(ph) == "F"


def test_unmatched_pattern_unchanged() -> None:
    ph = PoHeader(po_category="production")
    assert surat_jalan_display_number("DN-123", ph) == "DN-123"
