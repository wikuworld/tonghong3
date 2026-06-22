"""Unit tests for Proforma Invoice document generation."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from app.services import proforma_invoice_documents as pi


class _FakeScalarResult:
    def __init__(self, value):
        self._value = value

    def all(self):
        return self._value


class _FakeDb:
    def __init__(self, ph, details, cust=None, salesperson=None, pic=None, seq=1):
        self._ph = ph
        self._details = details
        self._cust = cust
        self._salesperson = salesperson
        self._pic = pic
        self._seq = seq
        self._scalar_calls = 0

    def get(self, model, pk):
        name = getattr(model, "__name__", "")
        if name == "PoHeader" and pk == self._ph.id:
            return self._ph
        if name == "Customer" and self._cust and pk == self._cust.id:
            return self._cust
        return None

    def scalars(self, _stmt):
        return _FakeScalarResult(self._details)

    def scalar(self, _stmt):
        self._scalar_calls += 1
        if self._scalar_calls == 1 and self._salesperson is not None:
            return self._salesperson
        if self._pic is not None and self._scalar_calls == 2:
            return self._pic
        return self._seq


def _sample_po():
    ph = SimpleNamespace(
        id=17,
        po_number="SFI-PRB-UO-260220-0017",
        customer_id=1,
        customer_code="SFI",
        buyer="SFI",
        order_date=date(2026, 2, 24),
        etd=date(2026, 3, 13),
        delivery_address="Jl. Raya Pati - Kudus Km 7",
        billing_address=None,
        po_category="suede",
        order_type_label=None,
        customer_name_snapshot="PT SEJIN FASHION INDONESIA",
    )
    detail = SimpleNamespace(
        id=1,
        material_name="Split Suede",
        thickness_text="1.2-1.4",
        thickness_min=None,
        thickness_max=None,
        emboss="",
        color="BLACK 145-17-00",
        quantity_order=Decimal("1692.15"),
        unit_price=Decimal("1.33"),
        line_etd=date(2026, 3, 13),
    )
    cust = SimpleNamespace(
        id=1,
        name="PT SEJIN FASHION INDONESIA",
        address="Jl. Raya Pati - Kudus Km 7",
        phone="(0295) 4105610",
        contact_person="DWI ANJAR",
        payment_terms="BY T/T 30 DAYS",
    )
    return ph, [detail], cust


def test_gather_proforma_invoice_ctx_maps_po_lines():
    ph, details, cust = _sample_po()
    db = _FakeDb(ph, details, cust=cust, salesperson="KRISTINA", pic=None)
    ctx = pi.gather_proforma_invoice_ctx(db, ph.id)
    assert ctx["po_number"] == ph.po_number
    assert ctx["customer_name"] == cust.name
    assert ctx["from_name"] == "KRISTINA"
    assert ctx["attn"] == "DWI ANJAR"
    assert len(ctx["lines"]) == 1
    line = ctx["lines"][0]
    assert line["item"] == "Split Suede"
    assert line["thickness"] == "1.2-1.4"
    assert line["color"] == "BLACK 145-17-00"
    assert line["qty"] == Decimal("1692.15")
    assert line["amount"] == Decimal("2250.56")
    assert line["etd"] == "3-13"
    assert "PI/SFI" in ctx["pi_number"]


def test_render_proforma_invoice_pdf_and_docx_produce_bytes():
    ph, details, cust = _sample_po()
    db = _FakeDb(ph, details, cust=cust, salesperson="KRISTINA")
    ctx = pi.gather_proforma_invoice_ctx(db, ph.id)
    pdf = pi.render_proforma_invoice_pdf(ctx)
    docx = pi.render_proforma_invoice_docx(ctx)
    assert pdf[:4] == b"%PDF"
    assert docx[:2] == b"PK"
