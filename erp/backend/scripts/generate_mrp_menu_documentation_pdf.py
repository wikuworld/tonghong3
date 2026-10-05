#!/usr/bin/env python3
"""Generate PDF: menu MRP UI (8082) — nama, fungsi, tabel database."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[3]  # project_uat
OUT_DIR = ROOT / "docs"
OUT_PDF = OUT_DIR / "MRP_Menu_Database_Reference.pdf"
PUBLIC_COPY = ROOT / "mrp" / "frontend" / "public" / "MRP_Menu_Database_Reference.pdf"

# (Grup, Menu, Path, Fungsi, Tabel MRP, Tabel ERP / catatan)
ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "Umum",
        "Dashboard",
        "/admin/dashboard",
        "Ringkasan operasi: rencana aktif, PO outstanding, proses terbuka, lab, packing, FG, stok kimia/RP.",
        "tbl_rencana_produksi, tbl_master_po, tbl_persiapan_kulit, tbl_lab_lot, tbl_packing, tbl_gudang_fg, tbl_stok_kimia_in, tbl_stok_rp_in",
        "—",
    ),
    (
        "Alur (Flow)",
        "Rencana Produksi (MRP)",
        "/admin/mrp/rencana-produksi",
        "Buat RPI, alokasi baris SO outstanding ke item rencana; sync PO dari ERP; cetak rencana.",
        "tbl_rencana_produksi, tbl_rencana_item, tbl_rencana_item_po, tbl_master_po, tbl_seq",
        "po_headers, po_details (via sync → tbl_master_po); baca lot/material: API ERP po-details",
    ),
    (
        "Alur (Flow)",
        "Proses / Persiapan (MRP)",
        "/admin/mrp/proses",
        "Persiapan kulit per WIP: scan palet/YL, ukur, treatment, selesai KY, return sisa.",
        "tbl_persiapan_kulit, tbl_persiapan_scan, tbl_persiapan_ukur, tbl_persiapan_reprint, tbl_persiapan_ky, tbl_kulit_lebih, tbl_proses_return, tbl_rencana_item, tbl_rencana_item_po, tbl_master_po, tbl_palet_movement, tbl_yl, tbl_yl_movement",
        "—",
    ),
    (
        "Alur (Flow)",
        "Lab Lot Warna (MRP)",
        "/admin/mrp/lab",
        "Lot warna lab, detail kimia per lot, mixing, sisa lot.",
        "tbl_lab_lot, tbl_lab_lot_detail, tbl_lab_mixing, tbl_lab_lot_sisa, tbl_stok_kimia_in/out (consumption)",
        "raw_materials (kimia, read via API ERP)",
    ),
    (
        "Alur (Flow)",
        "Packing FG (MRP)",
        "/admin/mrp/packing",
        "Packing finish good per WIP/RPI: roll, PO line, selesai → FG.",
        "tbl_packing, tbl_packing_roll, tbl_packing_po, tbl_packing_inbound, tbl_packing_inbound_line, tbl_rencana_item, tbl_master_po, tbl_seq",
        "po_details (source_detail_id di tbl_master_po / bridge ERP packing)",
    ),
    (
        "Alur (Flow)",
        "Gudang FG (MRP)",
        "/admin/mrp/gudang-fg",
        "Stok FG in/out, tie ke packing & surat jalan ERP.",
        "tbl_gudang_fg, tbl_packing, tbl_packing_roll, tbl_master_po",
        "delivery_headers, delivery_details (OUT / bridge SJ)",
    ),
    (
        "Alur (Flow)",
        "Gudang MOD (MRP)",
        "/admin/mrp/gudang-mod",
        "Material on demand / reject MOD, konsumsi ke proses.",
        "tbl_gudang_mod, tbl_persiapan_kulit",
        "—",
    ),
    (
        "Alur (Flow)",
        "Gudang Sisa (MRP)",
        "/admin/mrp/gudang-sisa",
        "Barang sisa / stock sisa, assign ke SO, packing dari sisa.",
        "tbl_stock_sisa, tbl_stock_sisa_fg_assign, tbl_packing (mode sisa)",
        "tbl_master_po (po_id assign)",
    ),
    (
        "Alur (Flow)",
        "Checkpoint (MRP)",
        "/admin/mrp/checkpoint",
        "Checkpoint QC proses (status per persiapan).",
        "tbl_checkpoint, tbl_persiapan_kulit, tbl_master_treatment",
        "—",
    ),
    (
        "Alur (Flow)",
        "Monitoring (MRP)",
        "/admin/mrp/monitoring",
        "Timeline status RPI → proses → lab → packing → FG.",
        "tbl_rencana_item, tbl_rencana_produksi, tbl_persiapan_kulit, tbl_lab_lot, tbl_packing, tbl_gudang_fg, tbl_checkpoint, tbl_master_po",
        "—",
    ),
    (
        "Material & Stok",
        "Stok Crust (MRP)",
        "/admin/mrp/palet",
        "Master palet (KY), YL, mutasi IN/OUT.",
        "tbl_palet_movement, tbl_yl, tbl_yl_movement",
        "—",
    ),
    (
        "Material & Stok",
        "Stok Kimia (MRP)",
        "/admin/mrp/stok-kimia",
        "Penerimaan & pengeluaran stok kimia (FIFO lot).",
        "tbl_stok_kimia_in, tbl_stok_kimia_out",
        "raw_materials (katalog kimia via API ERP)",
    ),
    (
        "Material & Stok",
        "Stok RP (MRP)",
        "/admin/mrp/stok-rp",
        "Penerimaan & pengeluaran resin powder.",
        "tbl_stok_rp_in, tbl_stok_rp_out",
        "raw_materials (RP via API ERP)",
    ),
    (
        "Material & Stok",
        "Stok Material Lain (MRP)",
        "/admin/mrp/stok-material-lain",
        "Stok material lain (non kimia/RP standar).",
        "tbl_stok_material_lain_in, tbl_stok_material_lain_out",
        "raw_materials (via API ERP)",
    ),
    (
        "Material & Stok",
        "Usage (MRP)",
        "/admin/mrp/usage",
        "Pencatatan pemakaian lot warna, RP, material lain ke proses.",
        "tbl_usage_color, tbl_usage_rp, tbl_usage_material_lain, tbl_lab_lot, tbl_stok_*",
        "—",
    ),
    (
        "Master Data",
        "Inventory (Material / Stok / Gudang)",
        "/admin/inventory",
        "Katalog & stok gudang ERP (proxy dari MRP UI).",
        "—",
        "raw_materials, material_stocks, warehouses",
    ),
    (
        "Master Data",
        "Master Item (MRP)",
        "/admin/mrp/masters/erp",
        "Lihat master item FG/spec dari ERP (read-only).",
        "—",
        "master_items, master_prices (API ERP)",
    ),
    (
        "Master Data",
        "Master Kulit (MRP)",
        "/admin/mrp/masters/kulit",
        "Kelola material kulit (ERP inventory).",
        "—",
        "raw_materials (material_type kulit)",
    ),
    (
        "Master Data",
        "Master Kimia (MRP)",
        "/admin/mrp/masters/kimia",
        "Lihat katalog kimia ERP (read-only di MRP).",
        "—",
        "raw_materials (kimia)",
    ),
    (
        "Master Data",
        "Master RP (MRP)",
        "/admin/mrp/masters/rp",
        "Lihat katalog RP ERP (read-only).",
        "—",
        "raw_materials (RP)",
    ),
    (
        "Master Data",
        "Master Treatment (MRP)",
        "/admin/mrp/masters/treatment",
        "Daftar treatment PU/Suede untuk persiapan.",
        "tbl_master_treatment",
        "—",
    ),
    (
        "Master Data",
        "Master Material Lain (MRP)",
        "/admin/mrp/masters/material-lain",
        "Lihat material lain di ERP (read-only).",
        "—",
        "raw_materials",
    ),
    (
        "Laporan",
        "Report Packing (MRP)",
        "/admin/mrp/reports/packing",
        "Rekap packing per tanggal: roll, lembar, ukuran (SF).",
        "tbl_packing, tbl_packing_roll, tbl_master_po",
        "—",
    ),
    (
        "Laporan",
        "Report Persiapan (MRP)",
        "/admin/mrp/reports/persiapan",
        "Rekap persiapan kulit: lembar & total ukuran per proses.",
        "tbl_persiapan_kulit, tbl_persiapan_ukur",
        "—",
    ),
    (
        "Laporan",
        "Report Selisih WIP (MRP)",
        "/admin/mrp/reports/selisih-wip",
        "Banding qty WIP persiapan vs qty aktual packing roll.",
        "tbl_persiapan_kulit, tbl_rencana_item, tbl_packing, tbl_packing_roll",
        "—",
    ),
    (
        "Sistem",
        "Login / User MRP",
        "/login",
        "Autentikasi pengguna MRP & hak akses menu.",
        "mrp_users, mrp_role_permissions",
        "—",
    ),
    (
        "Sistem",
        "Resep (internal)",
        "(lab / master)",
        "Referensi resep lab.",
        "master_resep",
        "—",
    ),
]


def build_pdf(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(path),
        pagesize=landscape(A4),
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.2 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=6,
    )
    sub_style = ParagraphStyle(
        "Sub",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        spaceAfter=12,
    )
    cell = ParagraphStyle(
        "Cell",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
    )
    story = [
        Paragraph("Dokumentasi Menu MRP - Tonghong UAT", title_style),
        Paragraph(
            f"Base URL UI: http://10.227.82.65:8082 · Database MRP: uat_tonghong_mrp · "
            f"ERP via HTTP API (uat_tonghong_erp) · Dibuat: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            sub_style,
        ),
        Paragraph(
            "Kolom <b>Tabel MRP</b> = tabel MariaDB shopfloor. Kolom <b>Tabel ERP</b> = tabel ERP atau "
            "akses read/sync lewat API (tidak selalu SQL langsung dari MRP).",
            sub_style,
        ),
    ]

    # Baris header pakai string biasa + style tabel (Paragraph + TEXTCOLOR table sering bentrok).
    table_data: list[list] = [
        ["Grup", "Menu", "Path", "Fungsi", "Tabel MRP", "Tabel ERP / integrasi"],
    ]
    for grup, menu, pth, fungsi, mrp, erp in ROWS:
        table_data.append(
            [
                Paragraph(grup, cell),
                Paragraph(menu, cell),
                Paragraph(pth.replace("&", "&amp;"), cell),
                Paragraph(fungsi.replace("&", "&amp;"), cell),
                Paragraph(mrp.replace("&", "&amp;"), cell),
                Paragraph(erp.replace("&", "&amp;"), cell),
            ]
        )

    col_widths = [2.2 * cm, 3.2 * cm, 3.5 * cm, 5.5 * cm, 5.8 * cm, 5.3 * cm]
    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#cbd5e1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, 0), 6),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 1), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "<i>Catatan:</i> Modul ERP (Sales Order, Delivery, dll.) dapat muncul di sidebar jika "
            "di-enable; di deployment UAT ini fokus shopfloor MRP di port 8082.",
            sub_style,
        )
    )
    doc.build(story)


def main() -> int:
    build_pdf(OUT_PDF)
    if PUBLIC_COPY.parent.is_dir():
        PUBLIC_COPY.write_bytes(OUT_PDF.read_bytes())
        print(f"Salin ke UI: {PUBLIC_COPY}")
    print(f"PDF: {OUT_PDF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
