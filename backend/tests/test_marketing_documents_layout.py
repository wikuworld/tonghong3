"""Smoke render Surat Jalan / INVPL layout."""

from datetime import date
from decimal import Decimal

from app.services.marketing_documents import (
    INVPL_BANK_DEFAULT,
    render_invpl_html,
    render_invpl_pdf,
    render_sj_dotmatrix_html,
    render_sj_html,
    render_sj_pdf,
)


def _sj_ctx():
    return {
        "delivery_number": "THI-M260911001",
        "delivery_date_fmt": "Sep 11, 2026",
        "customer_name": "ACME SHOES",
        "customer_address": "Jl. Contoh 1",
        "customer_tel": "021111",
        "customer_fax": "",
        "invoice_no": "THIN-M260911001",
        "bc_number": "",
        "vehicle_number": "B 1234 XX",
        "driver_name": "Budi",
        "lines": [
            {
                "no": 1,
                "item": "1.2-1.4MM GENERIC PU COATED LEATHER AR-20 RED",
                "po_no": "PO-1",
                "qty": Decimal("29.76"),
                "rolls": 180,
                "pcs": 1488,
            }
        ],
        "totals": {"qty": Decimal("29.76"), "rolls": 180, "pcs": 1488},
        "is_export": False,
    }


def _invpl_ctx():
    return {
        "packing_number": "PACK-1",
        "invoice_no": "THIN-M260911001",
        "doc_date_fmt": "Sep 11, 2026",
        "customer_name": "ACME",
        "customer_address": "Addr",
        "customer_phone_line": "TELP. NO. : 021",
        "is_export": False,
        "bill_to_block": "",
        "document_title": "INVOICE PACKING LIST",
        "description_line": "DESCRIPTION: SHOE MAKING MATERIAL (COW LEATHER)",
        "lines": [
            {
                "no": 1,
                "po_no": "PO-1",
                "item": "1.2-1.4MM MATERIAL",
                "color": "RED",
                "qty": Decimal("10"),
                "unit": "S/F",
                "unit_price": Decimal("1.38"),
                "amount": Decimal("13.80"),
                "rolls": 2,
                "pcs": 10,
                "nw": Decimal("5.0"),
                "gw": Decimal("5.5"),
                "remark": "",
            }
        ],
        "totals": {
            "qty": Decimal("10"),
            "amount": Decimal("13.80"),
            "rolls": 2,
            "pcs": 10,
            "nw": Decimal("5.0"),
            "gw": Decimal("5.5"),
        },
        "amount_in_words": "THIRTEEN UNITED STATES DOLLARS ONLY",
        "term_of_payment": "T/T 30 DAYS",
        "bank_name": INVPL_BANK_DEFAULT["bank_name"],
        "account_number": INVPL_BANK_DEFAULT["account_number"],
        "bank_address": INVPL_BANK_DEFAULT["bank_address"],
        "bank_phone": INVPL_BANK_DEFAULT["bank_phone"],
    }


def test_sj_html_layout_keys():
    html = render_sj_html(_sj_ctx())
    assert "SURAT JALAN (DELIVERY SHEET)" in html
    assert "DELIVERY TO:" in html
    assert "QTY (S/F)" in html
    assert "P.O. NO." in html
    assert "RECEIVED BY" in html
    assert "APPROVED BY" in html
    assert "THI-M260911001" in html


def test_sj_dotmatrix_and_pdf():
    ctx = _sj_ctx()
    dm = render_sj_dotmatrix_html(ctx)
    assert "SURAT JALAN (DELIVERY SHEET)" in dm
    assert "ITEM" in dm
    assert "window.print()" in dm
    pdf = render_sj_pdf(ctx)
    assert pdf[:4] == b"%PDF"


def test_invpl_pdf_has_signature_and_ctbc():
    html = render_invpl_html(_invpl_ctx())
    assert "INVOICE PACKING LIST" in html
    assert "Authorized signature" in html
    assert "ADVISING BANK" in html
    assert "CTBC" in html
    pdf = render_invpl_pdf(_invpl_ctx())
    assert pdf[:4] == b"%PDF"
    # text extraction not required; size sanity
    assert len(pdf) > 500


def test_invpl_foc_title():
    from app.services.marketing_documents import apply_invpl_foc_title, invpl_document_title

    assert invpl_document_title(foc=False) == "INVOICE PACKING LIST"
    assert invpl_document_title(foc=True) == "INVOICE PACKING LIST (FOC)"
    base = _invpl_ctx()
    plain_html = render_invpl_html(apply_invpl_foc_title(base, False))
    foc_html = render_invpl_html(apply_invpl_foc_title(base, True))
    assert "INVOICE PACKING LIST" in plain_html
    assert "INVOICE PACKING LIST (FOC)" not in plain_html
    assert "INVOICE PACKING LIST (FOC)" in foc_html
