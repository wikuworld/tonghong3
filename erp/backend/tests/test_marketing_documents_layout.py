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
    assert "(FOC)" not in html
    foc = dict(_sj_ctx())
    foc["is_foc"] = True
    foc_html = render_sj_html(foc)
    assert "SURAT JALAN (DELIVERY SHEET) (FOC)" in foc_html
    assert "DELIVERY TO:" in html
    assert "QTY (S/F)" in html
    assert "P.O. NO." in html
    assert "RECEIVED BY" in html
    assert "APPROVED BY" in html
    assert "THI-M260911001" in html
    assert 'class="logo"' in html
    assert "data:image/png;base64," in html


def test_sj_dotmatrix_and_pdf():
    ctx = _sj_ctx()
    dm = render_sj_dotmatrix_html(ctx)
    assert "SURAT JALAN (DELIVERY SHEET)" in dm
    assert 'class="logo"' in dm
    foc = dict(ctx)
    foc["is_foc"] = True
    assert "SURAT JALAN (DELIVERY SHEET) (FOC)" in render_sj_dotmatrix_html(foc)
    assert "ITEM" in dm
    assert "window.print()" in dm
    pdf = render_sj_pdf(ctx)
    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 500


def test_invpl_pdf_has_signature_and_ctbc():
    html = render_invpl_html(_invpl_ctx())
    assert "INVOICE PACKING LIST" in html
    assert "AUTHORIZED SIGNATURE" in html
    assert "<b>BANK:</b>" in html
    assert "OUR ADVISING BANK" not in html
    assert "P.O. NO." in html
    assert "U. PRICE (USD)" in html
    assert "PIECES" in html
    assert "N.W. (KGS)" in html
    assert "CTBC" in html
    assert "A4 portrait" in html
    assert f"margin: {10}mm {12}mm" in html or "margin: 10mm 12mm" in html
    assert "logo-tonghong" in html or "data:image/png;base64," in html
    assert 'class="logo"' in html
    assert 'class="rule"' in html
    pdf = render_invpl_pdf(_invpl_ctx())
    assert pdf[:4] == b"%PDF"
    # text extraction not required; size sanity (logo makes PDF larger)
    assert len(pdf) > 500


def test_commercial_invoice_reuses_invpl_layout():
    from app.services.marketing_documents import render_commercial_invoice_html

    ctx = dict(_invpl_ctx())
    ctx["document_title"] = "COMMERCIAL INVOICE"
    html = render_commercial_invoice_html(ctx)
    assert "COMMERCIAL INVOICE" in html
    assert "AUTHORIZED SIGNATURE" in html
    assert "P.O. NO." in html
    assert "<b>BANK:</b>" in html


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


def test_packing_derived_weights_formula():
    from app.services.marketing_documents import packing_derived_weights

    nw, gw = packing_derived_weights(qty=Decimal("122"), rolls=2)
    assert nw == Decimal("13.42")  # 122 × 0.11
    assert gw == Decimal("14.02")  # 13.42 + 2 × 0.3
    nw2, gw2 = packing_derived_weights(
        qty=Decimal("100"), rolls=1, weight_net=Decimal("50"), weight_gross=Decimal("55")
    )
    assert nw2 == Decimal("50")
    assert gw2 == Decimal("55")
