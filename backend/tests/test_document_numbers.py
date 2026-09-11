"""Nomor dokumen THI-/THIN- mengikuti kategori PO."""

from datetime import date
from unittest.mock import MagicMock

from app.models import DocumentSequence, PoHeader
from app.services.document_numbers import (
    allocate_invoice_number,
    allocate_surat_jalan_number,
    category_code_for_po,
    category_letter_for_po,
    invoice_display_number,
    surat_jalan_display_number,
)


def test_category_codes() -> None:
    assert category_code_for_po(PoHeader(po_category="production")) == "M"
    assert category_code_for_po(PoHeader(po_category="sample")) == "MD"
    assert category_code_for_po(PoHeader(po_category="claim")) == "C"
    assert category_code_for_po(PoHeader(po_category="return")) == "R"
    assert category_code_for_po(PoHeader(po_category="subcont")) == "T"
    assert category_code_for_po(PoHeader(po_category="suede")) == "M"


def test_foc_follows_sample() -> None:
    ph = PoHeader(po_category="production", order_type_label="SAMPLE FOC")
    assert category_letter_for_po(ph) == "MD"


def test_sj_normalizes_code_for_production() -> None:
    ph = PoHeader(po_category="production")
    assert surat_jalan_display_number("THI-C260318015", ph) == "THI-M260318015"


def test_sj_sample_md() -> None:
    ph = PoHeader(po_category="sample")
    assert surat_jalan_display_number("THI-M260318015", ph) == "THI-MD260318015"


def test_invoice_thin_prefix() -> None:
    ph = PoHeader(po_category="claim")
    assert invoice_display_number("IN-C26031801", ph) == "THIN-C26031801"
    assert invoice_display_number("THIN-M260318001", ph) == "THIN-C260318001"


def test_legacy_del_inv_remap() -> None:
    ph = PoHeader(po_category="production")
    assert (
        surat_jalan_display_number("DEL-202609-00001", ph, doc_date=date(2026, 9, 10))
        == "THI-M260910001"
    )
    assert (
        invoice_display_number("INV-202609-00007", ph, doc_date=date(2026, 9, 11))
        == "THIN-M260911007"
    )


def test_unmatched_pattern_unchanged() -> None:
    ph = PoHeader(po_category="production")
    assert surat_jalan_display_number("DN-123", ph) == "DN-123"


def test_allocate_sj_and_invoice_format() -> None:
    db = MagicMock()
    db.scalars.return_value.first.return_value = None

    def add(obj):
        if isinstance(obj, DocumentSequence):
            obj.last_value = 1

    db.add.side_effect = add
    ph = PoHeader(po_category="sample")
    sj = allocate_surat_jalan_number(db, po=ph, on_date=date(2026, 9, 11))
    inv = allocate_invoice_number(db, po=ph, on_date=date(2026, 9, 11))
    assert sj == "THI-MD260911001"
    assert inv == "THIN-MD260911001"
