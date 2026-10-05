"""Export Excel BC 2.7 dari delivery — field ada diisi, belum ada = need feed."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from openpyxl import load_workbook
from io import BytesIO

from app.models import (
    Customer,
    DeliveryDetail,
    DeliveryHeader,
    ExchangeRate,
    Invoice,
    MasterItem,
    PoDetail,
)
from app.services.delivery_customs_bc27_xlsx import (
    NEED_FEED,
    generate_nomor_aju,
    render_delivery_customs_bc27_xlsx,
)


def _scalars_side_effect(delivery_details, invoices, rates):
    def _scalars(stmt):
        result = MagicMock()
        entity = None
        try:
            entity = stmt.column_descriptions[0]["entity"]
        except Exception:
            entity = None
        text = str(stmt)
        if entity is DeliveryDetail or "delivery_details" in text:
            result.all.return_value = delivery_details
        elif entity is Invoice or "invoices" in text:
            result.all.return_value = invoices
        elif entity is ExchangeRate or "exchange_rates" in text:
            result.all.return_value = rates
        else:
            result.all.return_value = []
        return result

    return _scalars


def test_generate_nomor_aju_format():
    assert generate_nomor_aju(date(2026, 10, 2), 4407) == "000027TOP41720261002004407"


def test_render_bc27_fills_known_and_marks_need_feed():
    dh = SimpleNamespace(
        id=4407,
        delivery_number="THI-M261001012",
        customer_id=9,
        delivery_date=date(2026, 10, 2),
        driver_name="Budi",
        vehicle_number="B 1234 XX",
        packing_id=None,
    )
    cust = SimpleNamespace(
        id=9,
        name="SELALU CINTA INDONESIA",
        address="JL. LINGKAR SELATAN",
        billing_address=None,
        tax_id="0729241489505000000000",
        skep_kb_number="193/WBC.10/2020",
        customs_office_code="060800",
        default_currency="USD",
        reference_quotation="002/KPJB-THI/SC006/X/2026",
    )
    pod = SimpleNamespace(
        id=1,
        master_item_id=2,
        material_name="VIRGIN HYDRO PU LEATHER",
        thickness_text="1.2-1.4MM",
        color="BLACK (00A)",
        emboss="R-8 M",
        unit_price=Decimal("1.20"),
        system_reference=None,
    )
    master = SimpleNamespace(id=2, item_code="FG00071", exim_material_code=None)
    dd = SimpleNamespace(
        id=1,
        po_detail_id=1,
        production_detail_id=None,
        packing_detail_id=None,
        qty=Decimal("100"),
        qty_roll=10,
        qty_pcs=0,
        weight=Decimal("12.5"),
    )
    inv = SimpleNamespace(
        id=3,
        invoice_number="THIN-M261001012",
        invoice_date=date(2026, 10, 2),
        delivery_id=4407,
    )
    rate = SimpleNamespace(idr_per_usd=Decimal("17863"), effective_date=date(2026, 10, 1))

    db = MagicMock()
    db.scalars.side_effect = _scalars_side_effect([dd], [inv], [rate])

    def _get(model, pk):
        if model is DeliveryHeader and int(pk) == 4407:
            return dh
        if model is Customer and int(pk) == 9:
            return cust
        if model is PoDetail and int(pk) == 1:
            return pod
        if model is MasterItem and int(pk) == 2:
            return master
        return None

    db.get.side_effect = _get

    data, name = render_delivery_customs_bc27_xlsx(db, 4407)
    assert name.endswith("_bc27.xlsx")
    assert data[:2] == b"PK"

    wb = load_workbook(BytesIO(data))
    assert "HEADER" in wb.sheetnames
    assert "BARANG" in wb.sheetnames
    assert "BAHANBAKU" in wb.sheetnames

    header = {wb["HEADER"].cell(1, c).value: wb["HEADER"].cell(2, c).value for c in range(1, wb["HEADER"].max_column + 1)}
    assert header["NOMOR AJU"] == "000027TOP41720261002004407"
    assert header["KODE DOKUMEN"] == "27"
    assert header["KODE KANTOR TUJUAN"] == "060800"
    assert header["CIF"] == 120.0
    assert header["NDPBM"] == 17863.0
    assert header["NOMOR DAFTAR"] == NEED_FEED

    barang_hs_col = None
    for c in range(1, wb["BARANG"].max_column + 1):
        if wb["BARANG"].cell(1, c).value == "HS":
            barang_hs_col = c
            break
    assert barang_hs_col is not None
    assert wb["BARANG"].cell(2, barang_hs_col).value == NEED_FEED

    kode_col = None
    for c in range(1, wb["BARANG"].max_column + 1):
        if wb["BARANG"].cell(1, c).value == "KODE BARANG":
            kode_col = c
            break
    assert wb["BARANG"].cell(2, kode_col).value == "FG00071"

    bb_hs = None
    for c in range(1, wb["BAHANBAKU"].max_column + 1):
        if wb["BAHANBAKU"].cell(1, c).value == "HS":
            bb_hs = c
            break
    assert wb["BAHANBAKU"].cell(2, bb_hs).value == NEED_FEED
