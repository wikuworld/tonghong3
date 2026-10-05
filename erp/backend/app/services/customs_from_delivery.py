"""Buat draft AJU BC 3.0 dari delivery dan tautkan ke delivery, PO, invoice."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    CustomsAjuSheetRow,
    CustomsDeclaration,
    Customer,
    DeliveryDetail,
    DeliveryHeader,
    Invoice,
    MasterItem,
    PackingHeader,
    PoDetail,
    PoHeader,
    ProductionDetail,
    ProductionOrder,
)
from app.timeutil import app_now
from app.services.customs_import import declaration_to_api_dict
from app.services.customs_templates import (
    DEFAULT_VERSI_TEMPLATE,
    EXPORTER_ADDRESS,
    EXPORTER_COUNTRY,
    EXPORTER_NAME,
    KODE_DOKUMEN_BC30_EKSPOR,
    KODE_ENTITAS_EKSPORTIR,
    KODE_ENTITAS_PEMILIK,
    KODE_ENTITAS_PENGIRIM,
    KODE_ENTITAS_PENJUAL,
    KODE_JENIS_IDENTITAS_NPWP16,
    build_entitas_row,
    build_row,
    draft_sheet_column_keys,
)


def generate_aju_number() -> str:
    """Nomor draft internal (26 digit CEISA diisi ulang saat submit ke portal)."""
    import random

    now = app_now()
    suffix = random.randint(1000, 9999)
    return f"TH{now.strftime('%y%m%d%H%M%S')}{suffix}"


def _fmt_date(d: Any) -> str:
    if d is None:
        return ""
    if hasattr(d, "isoformat"):
        return d.isoformat()
    return str(d)


def _fmt_num(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, Decimal):
        normalized = val.normalize()
        if normalized == normalized.to_integral_value():
            return str(int(normalized))
        return str(normalized)
    return str(val)


def _customer_country(customer: Customer | None) -> str:
    if not customer or not customer.country:
        return ""
    c = customer.country.strip().upper()
    if len(c) == 2:
        return c
    mapping = {
        "INDONESIA": "ID",
        "CHINA": "CN",
        "VIETNAM": "VN",
        "UNITED STATES": "US",
        "USA": "US",
    }
    return mapping.get(c, c[:2] if len(c) >= 2 else c)


def _gather_delivery_context(db: Session, delivery_id: int) -> dict[str, Any]:
    delivery = db.get(DeliveryHeader, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery tidak ditemukan")

    packing = db.get(PackingHeader, delivery.packing_id) if delivery.packing_id else None
    production: ProductionOrder | None = None
    po_header: PoHeader | None = None
    customer: Customer | None = None

    if packing and packing.production_id:
        production = db.get(ProductionOrder, packing.production_id)
        if production and production.po_id:
            po_header = db.get(PoHeader, production.po_id)
            if po_header and po_header.customer_id:
                customer = db.get(Customer, po_header.customer_id)
            elif delivery.customer_id:
                customer = db.get(Customer, delivery.customer_id)
    elif delivery.customer_id:
        customer = db.get(Customer, delivery.customer_id)

    delivery_details = list(
        db.scalars(select(DeliveryDetail).where(DeliveryDetail.delivery_id == delivery_id)).all()
    )

    items: list[dict[str, Any]] = []
    for idx, detail in enumerate(delivery_details, 1):
        production_detail: ProductionDetail | None = None
        po_detail: PoDetail | None = None
        master_item: MasterItem | None = None

        if detail.production_detail_id:
            production_detail = db.get(ProductionDetail, detail.production_detail_id)
            if production_detail and production_detail.po_detail_id:
                po_detail = db.get(PoDetail, production_detail.po_detail_id)
                if po_detail and po_detail.master_item_id:
                    master_item = db.get(MasterItem, po_detail.master_item_id)

        material_name = (po_detail.material_name or "").strip() if po_detail else ""
        color = (po_detail.color or "").strip() if po_detail else ""
        thickness = (po_detail.thickness_text or "").strip() if po_detail else ""
        emboss = (po_detail.emboss or "").strip() if po_detail else ""
        model = (po_detail.model or po_detail.style_article or "").strip() if po_detail else ""

        uraian_parts = [p for p in [material_name, thickness, color, emboss] if p]
        uraian = " / ".join(uraian_parts) if uraian_parts else f"Barang kirim #{idx}"

        lot_number = (production_detail.lot_number or "").strip() if production_detail else ""
        batch = (production_detail.batch_number or "").strip() if production_detail else ""
        qty = float(detail.qty) if detail.qty is not None else 0
        weight = float(detail.weight) if detail.weight is not None else None
        qty_roll = int(detail.qty_roll or 0)
        unit_price = float(po_detail.unit_price) if po_detail and po_detail.unit_price else None

        kode_barang = ""
        if master_item:
            kode_barang = (master_item.exim_material_code or master_item.item_code or "").strip()
        elif po_detail and po_detail.system_reference:
            kode_barang = po_detail.system_reference.strip()

        items.append(
            {
                "seri": idx,
                "uraian": uraian,
                "merek": lot_number or batch,
                "tipe": model or thickness,
                "ukuran": thickness,
                "spesifikasi": emboss,
                "qty": qty,
                "qty_roll": qty_roll,
                "netto": weight,
                "lot_number": lot_number,
                "kode_barang": kode_barang,
                "hs": "",
                "unit_price": unit_price,
            }
        )

    return {
        "delivery": delivery,
        "packing": packing,
        "production": production,
        "po_header": po_header,
        "customer": customer,
        "items": items,
        "delivery_details": delivery_details,
    }


def _build_header_row(
    nomor_aju: str,
    delivery: DeliveryHeader,
    customer: Customer | None,
) -> dict[str, str]:
    export_date = _fmt_date(delivery.delivery_date or app_now().date())
    kantor = ""
    if customer and customer.customs_office_code:
        kantor = customer.customs_office_code.strip()

    return build_row(
        "HEADER",
        {
            "NOMOR AJU": nomor_aju,
            "KODE DOKUMEN": KODE_DOKUMEN_BC30_EKSPOR,
            "KODE KANTOR EKSPOR": kantor,
            "KODE JENIS EKSPOR": "1",
            "KODE KATEGORI EKSPOR": "10",
            "KODE CARA DAGANG": "1",
            "KODE CARA BAYAR": "1",
            "KODE NEGARA TUJUAN": _customer_country(customer),
            "TANGGAL EKSPOR": export_date,
            "TANGGAL BERANGKAT": export_date,
            "FLAG CURAH": "2",
        },
    )


def _build_entitas_rows(
    nomor_aju: str,
    customer: Customer | None,
) -> list[dict[str, str]]:
    exporter_npwp = ""
    buyer_name = (customer.name or "").strip() if customer else ""
    buyer_addr = (customer.address or customer.billing_address or "").strip() if customer else ""
    buyer_tax = (customer.tax_id or "").strip() if customer else ""
    buyer_country = _customer_country(customer)

    rows = [
        build_entitas_row(
            nomor_aju,
            1,
            KODE_ENTITAS_EKSPORTIR,
            nomor_identitas=exporter_npwp,
            nama=EXPORTER_NAME,
            alamat=EXPORTER_ADDRESS,
            kode_negara=EXPORTER_COUNTRY,
            kode_jenis_identitas=KODE_JENIS_IDENTITAS_NPWP16,
        ),
        build_entitas_row(
            nomor_aju,
            2,
            KODE_ENTITAS_PEMILIK,
            nomor_identitas=exporter_npwp,
            nama=EXPORTER_NAME,
            alamat=EXPORTER_ADDRESS,
            kode_negara=EXPORTER_COUNTRY,
        ),
        build_entitas_row(
            nomor_aju,
            3,
            KODE_ENTITAS_PENGIRIM,
            nomor_identitas=exporter_npwp,
            nama=EXPORTER_NAME,
            alamat=EXPORTER_ADDRESS,
            kode_negara=EXPORTER_COUNTRY,
        ),
    ]
    if buyer_name:
        rows.append(
            build_entitas_row(
                nomor_aju,
                4,
                KODE_ENTITAS_PENJUAL,
                nomor_identitas=buyer_tax,
                nama=buyer_name,
                alamat=buyer_addr,
                kode_negara=buyer_country,
                kode_jenis_identitas=KODE_JENIS_IDENTITAS_NPWP16 if buyer_tax else "",
            )
        )
    return rows


def _build_barang_rows(nomor_aju: str, items: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in items:
        qty = item["qty"]
        unit_price = item.get("unit_price")
        fob = ""
        if unit_price is not None and qty:
            fob = _fmt_num(Decimal(str(unit_price)) * Decimal(str(qty)))

        rows.append(
            build_row(
                "BARANG",
                {
                    "NOMOR AJU": nomor_aju,
                    "SERI BARANG": str(item["seri"]),
                    "HS": item.get("hs") or "",
                    "KODE BARANG": item.get("kode_barang") or "",
                    "URAIAN": item["uraian"],
                    "MEREK": item.get("merek") or "",
                    "TIPE": item.get("tipe") or "",
                    "UKURAN": item.get("ukuran") or "",
                    "SPESIFIKASI LAIN": item.get("spesifikasi") or "",
                    "KODE SATUAN": "MTR",
                    "JUMLAH SATUAN": _fmt_num(qty),
                    "KODE KEMASAN": "ROLL" if item.get("qty_roll") else "PK",
                    "JUMLAH KEMASAN": _fmt_num(item.get("qty_roll") or 1),
                    "NETTO": _fmt_num(item.get("netto")),
                    "FOB": fob,
                    "HARGA SATUAN": _fmt_num(unit_price) if unit_price else "",
                    "KODE NEGARA ASAL": EXPORTER_COUNTRY,
                    "KODE KONDISI BARANG": "1",
                },
            )
        )
    return rows


def _build_kemasan_rows(nomor_aju: str, delivery_details: list[DeliveryDetail]) -> list[dict[str, str]]:
    total_roll = sum(int(d.qty_roll or 0) for d in delivery_details)
    total_pcs = sum(int(d.qty_pcs or 0) for d in delivery_details)
    rows: list[dict[str, str]] = []
    seri = 1
    if total_roll > 0:
        rows.append(
            build_row(
                "KEMASAN",
                {
                    "NOMOR AJU": nomor_aju,
                    "SERI": str(seri),
                    "KODE KEMASAN": "ROLL",
                    "JUMLAH KEMASAN": str(total_roll),
                },
            )
        )
        seri += 1
    if total_pcs > 0:
        rows.append(
            build_row(
                "KEMASAN",
                {
                    "NOMOR AJU": nomor_aju,
                    "SERI": str(seri),
                    "KODE KEMASAN": "PK",
                    "JUMLAH KEMASAN": str(total_pcs),
                },
            )
        )
    return rows


def _sync_invoice_nomor_aju(db: Session, delivery_id: int, nomor_aju: str) -> None:
    invoices = list(
        db.scalars(select(Invoice).where(Invoice.delivery_id == delivery_id)).all()
    )
    for inv in invoices:
        if not inv.nomor_aju:
            inv.nomor_aju = nomor_aju


def create_declaration_from_delivery(db: Session, delivery_id: int) -> dict[str, Any]:
    """Buat draft AJU BC 3.0, simpan sheet, tautkan delivery & PO."""
    ctx = _gather_delivery_context(db, delivery_id)
    delivery: DeliveryHeader = ctx["delivery"]
    po_header: PoHeader | None = ctx["po_header"]
    customer: Customer | None = ctx["customer"]
    items: list[dict[str, Any]] = ctx["items"]
    delivery_details: list[DeliveryDetail] = ctx["delivery_details"]

    if delivery.customs_declaration_id:
        existing = db.get(CustomsDeclaration, delivery.customs_declaration_id)
        if existing:
            out = declaration_to_api_dict(db, existing.id)
            out["already_linked"] = True
            out["delivery_id"] = delivery.id
            out["delivery_number"] = delivery.delivery_number
            return out

    nomor_aju = generate_aju_number()
    po_number = (po_header.po_number or str(po_header.id)) if po_header else ""

    header_row = _build_header_row(nomor_aju, delivery, customer)
    entitas_rows = _build_entitas_rows(nomor_aju, customer)
    barang_rows = _build_barang_rows(nomor_aju, items)
    kemasan_rows = _build_kemasan_rows(nomor_aju, delivery_details)
    versi_row = build_row("VERSI", {"VERSI": DEFAULT_VERSI_TEMPLATE})

    sheet_payloads: dict[str, list[dict[str, str]]] = {
        "HEADER": [header_row],
        "ENTITAS": entitas_rows,
        "BARANG": barang_rows,
        "VERSI": [versi_row],
    }
    if kemasan_rows:
        sheet_payloads["KEMASAN"] = kemasan_rows

    column_keys = draft_sheet_column_keys()
    row_counts = {k: len(v) for k, v in sheet_payloads.items()}

    dec = CustomsDeclaration(
        nomor_aju=nomor_aju,
        kode_dokumen=KODE_DOKUMEN_BC30_EKSPOR,
        source_label=f"Delivery {delivery.delivery_number or delivery.id}",
        versi_template=DEFAULT_VERSI_TEMPLATE,
        meta_json={
            "delivery_id": delivery.id,
            "delivery_number": delivery.delivery_number,
            "po_id": po_header.id if po_header else None,
            "po_number": po_number or None,
            "customer_id": customer.id if customer else delivery.customer_id,
            "customer_name": customer.name if customer else None,
            "generated_from": "delivery",
            "sheet_column_keys": column_keys,
            "row_counts": row_counts,
            "totals": {
                "qty": sum(float(i["qty"]) for i in items),
                "roll": sum(int(d.qty_roll or 0) for d in delivery_details),
                "pcs": sum(int(d.qty_pcs or 0) for d in delivery_details),
            },
        },
    )
    db.add(dec)
    db.flush()

    for sheet_code, rows in sheet_payloads.items():
        for ri, cells in enumerate(rows):
            db.add(
                CustomsAjuSheetRow(
                    declaration_id=dec.id,
                    sheet_code=sheet_code,
                    row_number=ri,
                    cells=cells,
                )
            )

    delivery.customs_declaration_id = dec.id
    if po_header and not po_header.customs_declaration_id:
        po_header.customs_declaration_id = dec.id

    _sync_invoice_nomor_aju(db, delivery.id, nomor_aju)

    db.commit()
    db.refresh(dec)

    out = declaration_to_api_dict(db, dec.id)
    out["already_linked"] = False
    out["delivery_id"] = delivery.id
    out["delivery_number"] = delivery.delivery_number
    out["customer_name"] = customer.name if customer else None
    out["po_number"] = po_number or None
    out["total_qty"] = sum(float(i["qty"]) for i in items)
    meta_totals = (dec.meta_json or {}).get("totals") or {}
    out["total_roll"] = meta_totals.get("roll", 0)
    out["total_pcs"] = meta_totals.get("pcs", 0)
    return out
