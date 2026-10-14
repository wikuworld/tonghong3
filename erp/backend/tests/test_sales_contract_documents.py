"""Sales Contract KPJB — multi SJ, kolom No. SJ, logo."""

from datetime import date
from decimal import Decimal
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.models import Customer, CustomerPic, DeliveryDetail, DeliveryHeader, PoDetail
from app.services.sales_contract_documents import (
    gather_sales_contract_ctx,
    render_sales_contract_docx,
    render_sales_contract_pdf,
)


def _make_db(*, headers, customer, details_by_delivery, pods):
    db = MagicMock()

    def scalars(stmt):
        result = MagicMock()
        entity = None
        try:
            entity = stmt.column_descriptions[0]["entity"]
        except Exception:
            entity = None
        text = str(stmt).lower()
        if entity is DeliveryDetail or "delivery_details" in text:
            found = None
            try:
                for crit in stmt._where_criteria:  # type: ignore[attr-defined]
                    right = getattr(crit, "right", None)
                    val = getattr(right, "value", None)
                    if val is not None and int(val) in details_by_delivery:
                        found = int(val)
                        break
            except Exception:
                found = None
            result.all.return_value = details_by_delivery.get(found, []) if found is not None else []
        elif entity is CustomerPic or "customer_pics" in text:
            result.all.return_value = []
        else:
            result.all.return_value = []
        return result

    db.scalars.side_effect = scalars
    header_map = {int(h.id): h for h in headers}

    def _get(model, pk):
        pk = int(pk)
        if model is DeliveryHeader:
            return header_map.get(pk)
        if model is Customer:
            return customer if customer and int(customer.id) == pk else None
        if model is PoDetail:
            return pods.get(pk)
        return None

    db.get.side_effect = _get
    return db


def test_gather_sales_contract_from_multi_sj_uses_sj_not_po():
    dh1 = SimpleNamespace(id=1, delivery_number="THI-M261001012", customer_id=9, delivery_date=date(2026, 10, 2))
    dh2 = SimpleNamespace(id=2, delivery_number="THI-M261001013", customer_id=9, delivery_date=date(2026, 10, 3))
    cust = SimpleNamespace(
        id=9,
        code="SC006",
        name="PT BUYER",
        address="JL. TEST",
        billing_address=None,
        tax_id="0211472683401000",
        contact_person="Buyer PIC",
        position="Manager",
        default_currency="USD",
    )
    pod = SimpleNamespace(
        id=10,
        material_name="Split Suede",
        thickness_text="1.2-1.4MM",
        color="BLACK",
        emboss="",
        unit_price=Decimal("1.33"),
    )
    dd1 = SimpleNamespace(id=1, po_detail_id=10, production_detail_id=None, qty=Decimal("100"))
    dd2 = SimpleNamespace(id=2, po_detail_id=10, production_detail_id=None, qty=Decimal("50"))
    db = _make_db(
        headers=[dh1, dh2],
        customer=cust,
        details_by_delivery={1: [dd1], 2: [dd2]},
        pods={10: pod},
    )

    ctx = gather_sales_contract_ctx(db, [1, 2])
    assert ctx["kontrak_no"] == "002/KPJB-THI/SC006/X/2026"
    assert [ln["sj"] for ln in ctx["lines"]] == ["THI-M261001012", "THI-M261001013"]
    assert ctx["total_qty"] == Decimal("150")
    assert "po" not in ctx["lines"][0]

    pdf = render_sales_contract_pdf(ctx)
    assert pdf[:4] == b"%PDF"
    docx = render_sales_contract_docx(ctx)
    assert docx[:2] == b"PK"


def test_gather_rejects_different_customers():
    dh1 = SimpleNamespace(id=1, delivery_number="A", customer_id=1, delivery_date=date(2026, 10, 1))
    dh2 = SimpleNamespace(id=2, delivery_number="B", customer_id=2, delivery_date=date(2026, 10, 1))
    cust = SimpleNamespace(
        id=1,
        code="A",
        name="A",
        address="",
        billing_address=None,
        tax_id=None,
        contact_person=None,
        position=None,
        default_currency="USD",
    )
    db = _make_db(headers=[dh1, dh2], customer=cust, details_by_delivery={1: [], 2: []}, pods={})
    with pytest.raises(ValueError, match="delivery_customer_mismatch"):
        gather_sales_contract_ctx(db, [1, 2])
