"""Export Excel bea cukai BC 2.7 (pengeluaran KB/TPB) dari delivery.

Format mengacu lampiran `dokumentasi/000027TOP41720261002004407.xlsx`.
Field yang ada di ERP diisi dari data; yang belum punya sumber ditandai `need feed`.
"""

from __future__ import annotations

from copy import copy
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from pathlib import Path
from typing import Any

from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Customer,
    DeliveryDetail,
    DeliveryHeader,
    ExchangeRate,
    Invoice,
    MasterItem,
    PackingDetail,
    PoDetail,
    ProductionDetail,
)
from app.timeutil import app_now

NEED_FEED = "need feed"

# Identitas perusahaan (isi tetap dari template contoh AJU).
TH_NAME = "TONG HONG TANNERY INDONESIA"
TH_ADDRESS = (
    "KAWASAN INDUSTRI MODERN CIKANDE JL MODERN INDUSTRI XIV, NO. W1, "
    "BARENGKOK, KIBIN, KAB. SERANG, BANTEN, 42185"
)
TH_NPWP = "0211472683401000000000"
TH_NIB = "8120104992265"
TH_SKEP = "KM-86/WBC.07/2019"
TH_SKEP_DATE = "04-16-2019 00:00:00"
TH_KODE_KANTOR = "050400"
TH_KOTA_PERNYATAAN = "SERANG"
TH_NAMA_PERNYATAAN = "CHIU PO HAO"
TH_JABATAN_PERNYATAAN = "DIREKTUR"
TH_KODE_JENIS_API = "02"
TH_KODE_STATUS = "LAINNYA"

KODE_DOKUMEN_BC27 = "27"
KODE_DOK_INVOICE = "380"
KODE_DOK_SJ = "630"
KODE_DOK_KONTRAK = "315"
KODE_SATUAN_FTK = "FTK"
KODE_KEMASAN_RO = "RO"
VERSI_TEMPLATE = "1.3"

SHEET_ORDER = [
    "HEADER",
    "ENTITAS",
    "DOKUMEN",
    "PENGANGKUT",
    "KEMASAN",
    "KONTAINER",
    "KOMPONENBIAYA",
    "BARANG",
    "BARANGTARIF",
    "BARANGDOKUMEN",
    "BARANGENTITAS",
    "BARANGSPEKKHUSUS",
    "BARANGVD",
    "BAHANBAKU",
    "BAHANBAKUTARIF",
    "BAHANBAKUDOKUMEN",
    "PUNGUTAN",
    "JAMINAN",
    "BANKDEVISA",
    "VERSI",
    "RESPON",
]


def _template_candidates() -> list[Path]:
    here = Path(__file__).resolve()
    return [
        here.parents[3] / "dokumentasi" / "000027TOP41720261002004407.xlsx",
        here.parents[2] / "dokumentasi" / "000027TOP41720261002004407.xlsx",
        Path("/app/dokumentasi/000027TOP41720261002004407.xlsx"),
        Path("/home/developer/project_uat/dokumentasi/000027TOP41720261002004407.xlsx"),
    ]


def resolve_bc27_template_path() -> Path | None:
    for p in _template_candidates():
        if p.is_file():
            return p
    return None


def _dec(val: Any) -> Decimal:
    if val is None or val == "":
        return Decimal("0")
    if isinstance(val, Decimal):
        return val
    return Decimal(str(val))


def _money2(val: Decimal) -> Decimal:
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _fmt_date(d: date | datetime | None) -> str:
    if d is None:
        return NEED_FEED
    if isinstance(d, datetime):
        d = d.date()
    return d.isoformat()


def _or_feed(val: Any, *, zero_ok: bool = False) -> Any:
    if val is None:
        return NEED_FEED
    if isinstance(val, str):
        s = val.strip()
        return s if s else NEED_FEED
    if isinstance(val, (int, float, Decimal)):
        if not zero_ok and val == 0:
            return NEED_FEED
        if isinstance(val, Decimal):
            return float(val) if val != val.to_integral_value() else int(val)
        return val
    return val


def _header_map(ws: Worksheet) -> dict[str, list[int]]:
    """Kolom 1-based per nama header (dukung nama duplikat)."""
    out: dict[str, list[int]] = {}
    for c in range(1, (ws.max_column or 0) + 1):
        name = ws.cell(1, c).value
        if name is None:
            continue
        key = str(name).strip()
        if not key:
            continue
        out.setdefault(key, []).append(c)
    return out


def _clear_data_rows(ws: Worksheet) -> None:
    if ws.max_row and ws.max_row > 1:
        ws.delete_rows(2, ws.max_row - 1)


def _write_row(ws: Worksheet, row_idx: int, headers: dict[str, list[int]], values: dict[str, Any]) -> None:
    used: dict[str, int] = {}
    for key, val in values.items():
        cols = headers.get(key) or []
        if not cols:
            continue
        occ = used.get(key, 0)
        if occ >= len(cols):
            continue
        ws.cell(row_idx, cols[occ], val)
        used[key] = occ + 1


def _append_row(ws: Worksheet, headers: dict[str, list[int]], values: dict[str, Any]) -> None:
    _write_row(ws, (ws.max_row or 1) + 1, headers, values)


def _copy_sheet_headers(src: Worksheet, dst: Worksheet) -> None:
    for c in range(1, (src.max_column or 0) + 1):
        src_cell = src.cell(1, c)
        dst_cell = dst.cell(1, c)
        dst_cell.value = src_cell.value
        if src_cell.has_style:
            dst_cell.font = copy(src_cell.font)
            dst_cell.fill = copy(src_cell.fill)
            dst_cell.border = copy(src_cell.border)
            dst_cell.alignment = copy(src_cell.alignment)
            dst_cell.number_format = src_cell.number_format


def _blank_workbook_from_template(template: Path) -> Any:
    src = load_workbook(template)
    wb = Workbook()
    # remove default
    default = wb.active
    wb.remove(default)
    for name in SHEET_ORDER:
        if name not in src.sheetnames:
            ws = wb.create_sheet(name)
            continue
        src_ws = src[name]
        ws = wb.create_sheet(name)
        _copy_sheet_headers(src_ws, ws)
    # any extra sheets from template
    for name in src.sheetnames:
        if name not in wb.sheetnames:
            ws = wb.create_sheet(name)
            _copy_sheet_headers(src[name], ws)
    src.close()
    return wb


def generate_nomor_aju(on_date: date, delivery_id: int) -> str:
    """format: 000027TOP417yyyymmddxxxxxx"""
    return f"000027TOP417{on_date.strftime('%Y%m%d')}{int(delivery_id) % 1_000_000:06d}"


def _latest_kurs(db: Session, on_date: date | None = None) -> Decimal | None:
    q = select(ExchangeRate).order_by(ExchangeRate.effective_date.desc())
    rows = list(db.scalars(q).all())
    if not rows:
        return None
    if on_date is None:
        return _dec(rows[0].idr_per_usd)
    for r in rows:
        if r.effective_date and r.effective_date <= on_date:
            return _dec(r.idr_per_usd)
    return _dec(rows[0].idr_per_usd)


def _item_uraian(pod: PoDetail | None) -> str:
    if not pod:
        return NEED_FEED
    from app.services.thickness_format import display_po_thickness_mm

    thick = display_po_thickness_mm(pod)
    rest = " ".join(
        p
        for p in [
            (pod.material_name or "").strip(),
            (pod.emboss or "").strip(),
            (pod.color or "").strip(),
        ]
        if p
    )
    if thick and rest:
        return f"{thick} {rest}".strip()
    return rest or thick or NEED_FEED


def _gather_lines(db: Session, delivery_id: int) -> list[dict[str, Any]]:
    details = list(
        db.scalars(
            select(DeliveryDetail)
            .where(DeliveryDetail.delivery_id == delivery_id)
            .order_by(DeliveryDetail.id.asc())
        ).all()
    )
    lines: list[dict[str, Any]] = []
    for idx, dd in enumerate(details, 1):
        pod: PoDetail | None = None
        master: MasterItem | None = None
        pd: ProductionDetail | None = None
        if dd.po_detail_id:
            pod = db.get(PoDetail, int(dd.po_detail_id))
        if dd.production_detail_id:
            pd = db.get(ProductionDetail, int(dd.production_detail_id))
            if pod is None and pd and pd.po_detail_id:
                pod = db.get(PoDetail, int(pd.po_detail_id))
        if pod and pod.master_item_id:
            master = db.get(MasterItem, int(pod.master_item_id))

        qty = _dec(dd.qty)
        unit_price = _dec(pod.unit_price) if pod and pod.unit_price is not None else None
        amount = _money2(qty * unit_price) if unit_price is not None else None

        nw = _dec(dd.weight) if dd.weight is not None else None
        if nw is None and dd.packing_detail_id:
            pkd = db.get(PackingDetail, int(dd.packing_detail_id))
            if pkd and pkd.weight_net is not None:
                nw = _dec(pkd.weight_net)

        kode_barang = ""
        if master:
            kode_barang = (master.item_code or master.exim_material_code or "").strip()
        if not kode_barang and pod and pod.system_reference:
            kode_barang = pod.system_reference.strip()

        lines.append(
            {
                "seri": idx,
                "uraian": _item_uraian(pod),
                "kode_barang": kode_barang or NEED_FEED,
                "hs": NEED_FEED,
                "qty": qty,
                "qty_roll": int(dd.qty_roll or 0),
                "qty_pcs": int(dd.qty_pcs or 0),
                "nw": nw,
                "gw": nw,
                "amount": amount,
                "unit_price": unit_price,
            }
        )
    return lines


def build_bc27_workbook(db: Session, delivery_id: int) -> tuple[Any, str]:
    dh = db.get(DeliveryHeader, delivery_id)
    if not dh:
        raise ValueError("delivery_not_found")

    customer = db.get(Customer, dh.customer_id) if dh.customer_id else None
    invoices = list(
        db.scalars(
            select(Invoice).where(Invoice.delivery_id == delivery_id).order_by(Invoice.id.asc())
        ).all()
    )
    lines = _gather_lines(db, delivery_id)
    dday = dh.delivery_date or app_now().date()
    nomor_aju = generate_nomor_aju(dday, int(dh.id))
    kurs = _latest_kurs(db, dday)

    total_cif = sum((ln["amount"] or Decimal("0") for ln in lines), Decimal("0"))
    total_nw = sum((ln["nw"] or Decimal("0") for ln in lines), Decimal("0"))
    total_gw = sum((ln["gw"] or Decimal("0") for ln in lines), Decimal("0"))
    total_roll = sum(int(ln["qty_roll"] or 0) for ln in lines)
    if total_gw <= 0 and total_nw > 0:
        total_gw = total_nw

    cif_idr = _money2(total_cif * kurs) if kurs is not None else None
    ppn = _money2(cif_idr * Decimal("0.11")) if cif_idr is not None else None

    template = resolve_bc27_template_path()
    if template:
        wb = _blank_workbook_from_template(template)
    else:
        wb = Workbook()
        default = wb.active
        wb.remove(default)
        for name in SHEET_ORDER:
            wb.create_sheet(name)

    # --- HEADER ---
    ws = wb["HEADER"]
    hmap = _header_map(ws)
    if not hmap:
        # fallback minimal headers if template missing
        for i, col in enumerate(
            [
                "NOMOR AJU",
                "KODE DOKUMEN",
                "KODE KANTOR",
                "KODE KANTOR TUJUAN",
                "KODE JENIS TPB",
                "KODE TUJUAN PENGIRIMAN",
                "KODE TUJUAN TPB",
                "CIF",
                "HARGA_PENYERAHAN",
                "NDPBM",
                "DASAR PENGENAAN PAJAK",
                "BRUTO",
                "NETTO",
                "KOTA PERNYATAAN",
                "TANGGAL PERNYATAAN",
                "NAMA PERNYATAAN",
                "JABATAN PERNYATAAN",
                "KODE VALUTA",
                "NOMOR DAFTAR",
                "TANGGAL DAFTAR",
                "PPN PAJAK",
                "PPNBM PAJAK",
                "TARIF PPN PAJAK",
            ],
            1,
        ):
            ws.cell(1, i, col)
        hmap = _header_map(ws)

    kantor_tujuan = (customer.customs_office_code or "").strip() if customer else ""
    valuta = "USD"
    if customer and (customer.default_currency or "").strip():
        valuta = customer.default_currency.strip().upper()

    header_vals: dict[str, Any] = {
        "NOMOR AJU": nomor_aju,
        "KODE DOKUMEN": KODE_DOKUMEN_BC27,
        "KODE KANTOR": TH_KODE_KANTOR,
        "KODE KANTOR TUJUAN": _or_feed(kantor_tujuan),
        "KODE JENIS TPB": "1",
        "KODE TUJUAN PENGIRIMAN": "1",
        "KODE TUJUAN TPB": "1",
        "ASURANSI": 0,
        "NILAI BARANG": 0,
        "FREIGHT": 0,
        "FOB": 0,
        "BIAYA TAMBAHAN": 0,
        "BIAYA PENGURANG": 0,
        "VD": 0,
        "CIF": float(total_cif) if total_cif else NEED_FEED,
        "HARGA_PENYERAHAN": float(cif_idr) if cif_idr is not None else NEED_FEED,
        "NDPBM": float(kurs) if kurs is not None else NEED_FEED,
        "DASAR PENGENAAN PAJAK": float(cif_idr) if cif_idr is not None else NEED_FEED,
        "UANG MUKA": 0,
        "BRUTO": float(total_gw) if total_gw else NEED_FEED,
        "NETTO": float(total_nw) if total_nw else NEED_FEED,
        "VOLUME": 0,
        "KOTA PERNYATAAN": TH_KOTA_PERNYATAAN,
        "TANGGAL PERNYATAAN": _fmt_date(dday),
        "NAMA PERNYATAAN": TH_NAMA_PERNYATAAN,
        "JABATAN PERNYATAAN": TH_JABATAN_PERNYATAAN,
        "KODE VALUTA": valuta,
        "NOMOR DAFTAR": NEED_FEED,
        "TANGGAL DAFTAR": NEED_FEED,
        "PPN PAJAK": float(ppn) if ppn is not None else NEED_FEED,
        "PPNBM PAJAK": 0,
        "TARIF PPN PAJAK": 11,
    }
    _append_row(ws, hmap, header_vals)

    # --- ENTITAS ---
    ws = wb["ENTITAS"]
    emap = _header_map(ws)
    # 7 & 3: Tong Hong; 8: customer
    _append_row(
        ws,
        emap,
        {
            "NOMOR AJU": nomor_aju,
            "SERI": 7,
            "KODE ENTITAS": "7",
            "KODE JENIS IDENTITAS": "6",
            "NOMOR IDENTITAS": TH_NPWP,
            "NAMA ENTITAS": TH_NAME,
            "ALAMAT ENTITAS": TH_ADDRESS,
            "KODE JENIS API": TH_KODE_JENIS_API,
            "KODE STATUS": TH_KODE_STATUS,
        },
    )
    _append_row(
        ws,
        emap,
        {
            "NOMOR AJU": nomor_aju,
            "SERI": 3,
            "KODE ENTITAS": "3",
            "KODE JENIS IDENTITAS": "6",
            "NOMOR IDENTITAS": TH_NPWP,
            "NAMA ENTITAS": TH_NAME,
            "ALAMAT ENTITAS": TH_ADDRESS,
            "NIB ENTITAS": TH_NIB,
            "KODE JENIS API": TH_KODE_JENIS_API,
            "KODE STATUS": TH_KODE_STATUS,
            "NOMOR IJIN ENTITAS": TH_SKEP,
            "TANGGAL IJIN ENTITAS": TH_SKEP_DATE,
        },
    )
    cust_name = (customer.name or "").strip() if customer else ""
    cust_addr = ""
    if customer:
        cust_addr = (customer.address or customer.billing_address or "").strip()
    cust_tax = (customer.tax_id or "").strip() if customer else ""
    cust_skep = (customer.skep_kb_number or "").strip() if customer else ""
    _append_row(
        ws,
        emap,
        {
            "NOMOR AJU": nomor_aju,
            "SERI": 8,
            "KODE ENTITAS": "8",
            "KODE JENIS IDENTITAS": "6",
            "NOMOR IDENTITAS": _or_feed(cust_tax),
            "NAMA ENTITAS": _or_feed(cust_name),
            "ALAMAT ENTITAS": _or_feed(cust_addr),
            "KODE JENIS API": TH_KODE_JENIS_API,
            "KODE STATUS": TH_KODE_STATUS,
            "NOMOR IJIN ENTITAS": _or_feed(cust_skep),
            "TANGGAL IJIN ENTITAS": NEED_FEED,
        },
    )

    # --- DOKUMEN ---
    ws = wb["DOKUMEN"]
    dmap = _header_map(ws)
    seri = 1
    if invoices:
        for inv in invoices:
            _append_row(
                ws,
                dmap,
                {
                    "NOMOR AJU": nomor_aju,
                    "SERI": seri,
                    "KODE DOKUMEN": KODE_DOK_INVOICE,
                    "NOMOR DOKUMEN": _or_feed(inv.invoice_number),
                    "TANGGAL DOKUMEN": _fmt_date(inv.invoice_date or dday),
                },
            )
            seri += 1
    else:
        _append_row(
            ws,
            dmap,
            {
                "NOMOR AJU": nomor_aju,
                "SERI": seri,
                "KODE DOKUMEN": KODE_DOK_INVOICE,
                "NOMOR DOKUMEN": NEED_FEED,
                "TANGGAL DOKUMEN": _fmt_date(dday),
            },
        )
        seri += 1

    _append_row(
        ws,
        dmap,
        {
            "NOMOR AJU": nomor_aju,
            "SERI": seri,
            "KODE DOKUMEN": KODE_DOK_SJ,
            "NOMOR DOKUMEN": _or_feed(dh.delivery_number),
            "TANGGAL DOKUMEN": _fmt_date(dday),
        },
    )
    seri += 1

    kontrak = ""
    if customer and (customer.reference_quotation or "").strip():
        kontrak = customer.reference_quotation.strip()
    _append_row(
        ws,
        dmap,
        {
            "NOMOR AJU": nomor_aju,
            "SERI": seri,
            "KODE DOKUMEN": KODE_DOK_KONTRAK,
            "NOMOR DOKUMEN": _or_feed(kontrak),
            "TANGGAL DOKUMEN": _fmt_date(dday),
        },
    )

    # --- PENGANGKUT ---
    ws = wb["PENGANGKUT"]
    pmap = _header_map(ws)
    _append_row(
        ws,
        pmap,
        {
            "NOMOR AJU": nomor_aju,
            "SERI": 1,
            "KODE CARA ANGKUT": NEED_FEED,
            "NAMA PENGANGKUT": (dh.driver_name or "").strip() or "-",
            "NOMOR PENGANGKUT": (dh.vehicle_number or "").strip() or "-",
        },
    )

    # --- KEMASAN ---
    ws = wb["KEMASAN"]
    kmap = _header_map(ws)
    _append_row(
        ws,
        kmap,
        {
            "NOMOR AJU": nomor_aju,
            "SERI": 1,
            "KODE KEMASAN": KODE_KEMASAN_RO,
            "JUMLAH KEMASAN": total_roll if total_roll > 0 else NEED_FEED,
        },
    )

    # empty-header-only sheets already cleared via blank workbook

    # --- BARANG ---
    ws = wb["BARANG"]
    bmap = _header_map(ws)
    for ln in lines:
        amt = ln["amount"]
        amt_idr = _money2(amt * kurs) if amt is not None and kurs is not None else None
        _append_row(
            ws,
            bmap,
            {
                "NOMOR AJU": nomor_aju,
                "SERI BARANG": ln["seri"],
                "HS": NEED_FEED,
                "KODE BARANG": ln["kode_barang"],
                "URAIAN": ln["uraian"],
                "MEREK": "-",
                "TIPE": "-",
                "UKURAN": "-",
                "SPESIFIKASI LAIN": "-",
                "KODE SATUAN": KODE_SATUAN_FTK,
                "JUMLAH SATUAN": float(ln["qty"]) if ln["qty"] else NEED_FEED,
                "NETTO": float(ln["nw"]) if ln["nw"] is not None else NEED_FEED,
                "CIF": float(amt) if amt is not None else NEED_FEED,
                "CIF RUPIAH": float(amt_idr) if amt_idr is not None else NEED_FEED,
                "NDPBM": float(kurs) if kurs is not None else NEED_FEED,
                "FOB": 0,
                "NILAI TAMBAH": 0,
                "DISKON": 0,
                "HARGA PENYERAHAN": float(amt_idr) if amt_idr is not None else NEED_FEED,
                "HARGA PEROLEHAN": 0,
                "HARGA EKSPOR": 0,
                "NILAI BARANG": 0,
                "NILAI JASA": 0,
            },
        )

    # --- BAHANBAKU (belum ada BOM di ERP) ---
    ws = wb["BAHANBAKU"]
    bbmap = _header_map(ws)
    for ln in lines:
        _append_row(
            ws,
            bbmap,
            {
                "NOMOR AJU": nomor_aju,
                "SERI BARANG": ln["seri"],
                "SERI BAHAN BAKU": 1,
                "KODE ASAL BAHAN BAKU": "0",
                "HS": NEED_FEED,
                "KODE BARANG": NEED_FEED,
                "URAIAN": NEED_FEED,
                "MEREK": "-",
                "TIPE": "-",
                "UKURAN": "-",
                "SPESIFIKASI LAIN": "-",
                "KODE SATUAN": KODE_SATUAN_FTK,
                "JUMLAH SATUAN": float(ln["qty"]) if ln["qty"] else NEED_FEED,
                "KODE DOKUMEN ASAL": "23",
                "KODE KANTOR ASAL": TH_KODE_KANTOR,
                "NDPBM": float(kurs) if kurs is not None else NEED_FEED,
                "HARGA PENYERAHAN": 0,
                "HARGA PEROLEHAN": 0,
                "NILAI JASA": 0,
                "SERI IZIN": 0,
            },
        )

    # --- BAHANBAKUTARIF: BM / PPH / PPN per barang (qty dari invoice) ---
    ws = wb["BAHANBAKUTARIF"]
    btmap = _header_map(ws)
    tarif_rows = [
        ("BM", "1", 0, "6", 100),
        ("PPH", "1", 2.5, "6", 100),
        ("PPN", "1", 11, "6", 100),
    ]
    for ln in lines:
        qty = float(ln["qty"]) if ln["qty"] else NEED_FEED
        for kode_pungutan, kode_tarif, tarif, kode_fas, tarif_fas in tarif_rows:
            _append_row(
                ws,
                btmap,
                {
                    "NOMOR AJU": nomor_aju,
                    "SERI BARANG": ln["seri"],
                    "SERI BAHAN BAKU": 1,
                    "KODE ASAL BAHAN BAKU": "0",
                    "KODE PUNGUTAN": kode_pungutan,
                    "KODE TARIF": kode_tarif,
                    "TARIF": tarif,
                    "KODE FASILITAS": kode_fas,
                    "TARIF FASILITAS": tarif_fas,
                    "NILAI BAYAR": 0,
                    "NILAI SUDAH DILUNASI": 0,
                    "KODE SATUAN": KODE_SATUAN_FTK,
                    "JUMLAH SATUAN": qty,
                },
            )

    # --- VERSI ---
    ws = wb["VERSI"]
    if ws.max_row < 1 or ws.cell(1, 1).value is None:
        ws.cell(1, 1, "VERSI")
    if ws.max_row >= 2:
        ws.cell(2, 1, VERSI_TEMPLATE)
    else:
        ws.cell(2, 1, VERSI_TEMPLATE)

    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in nomor_aju)[:48]
    filename = f"{safe}_bc27.xlsx"
    return wb, filename


def render_delivery_customs_bc27_xlsx(db: Session, delivery_id: int) -> tuple[bytes, str]:
    wb, filename = build_bc27_workbook(db, delivery_id)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue(), filename
