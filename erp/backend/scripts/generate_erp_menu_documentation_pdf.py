#!/usr/bin/env python3
"""Generate PDF: menu ERP UI (8081) — nama, fungsi, tabel database."""

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
OUT_PDF = OUT_DIR / "ERP_Menu_Database_Reference.pdf"
PUBLIC_COPY = ROOT / "erp" / "frontend" / "public" / "ERP_Menu_Database_Reference.pdf"

# (Grup, Menu, Path, Fungsi, Tabel utama, Tabel pendukung)
ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "Umum",
        "Dashboard",
        "/admin/dashboard",
        "KPI operasional realtime: total SO, produksi berjalan, QC NG, kurs, tren, komposisi PO, Received PO PU/Suede, feed aktivitas.",
        "po_headers, po_details, production_orders, qc_details, delivery_headers, delivery_details, invoices, exchange_rates",
        "customers",
    ),
    (
        "Marketing",
        "Order Penjualan (SO)",
        "/admin/po",
        "Input/edit/hapus SO (header + detail), confirm, duplikasi, filter/monitoring status & alur MKT, ekspor CSV, cetak Sales Contract & Proforma Invoice (PDF/DOCX).",
        "po_headers, po_details, po_detail_deliveries, audit_logs, document_sequences, lot_sequences, proforma_invoice_records",
        "customers, customer_pics, brands, customer_brand_mappings, master_items, buyer_price_lists, buyer_price_sheet_rows, color_swatch_recipes, fluorescent_color_masters, notifications, ppic_assignments, production_details",
    ),
    (
        "Marketing",
        "Outstanding",
        "/admin/marketing-flow/outstanding",
        "Sisa kirim per baris SO (qty order − delivery). Atur rencana kirim, buat PI, buat SJ dari packing QC OK, lanjut/rollback tahap MKT, snapshot outstanding, ekspor Excel/CSV, cetak rekap PO.",
        "po_headers, po_details, po_detail_deliveries, marketing_outstanding_snapshots, packing_headers, packing_details, delivery_headers, delivery_details, proforma_invoice_records",
        "customers, master_items, production_details, invoices, invoice_details, ppic_assignments, audit_logs",
    ),
    (
        "Marketing",
        "Rencana Kirim",
        "/admin/marketing-flow/planning",
        "Pantauan jadwal slot kirim per baris SO (bukan tempat buat SJ). Filter rentang / hari ini / terlambat; tautan buka SJ di Delivery.",
        "po_headers, po_details, po_detail_deliveries, delivery_headers, delivery_details",
        "customers, packing_headers",
    ),
    (
        "Fulfillment",
        "Delivery",
        "/admin/delivery",
        "Daftar surat jalan: pantau draft/sent, scan-out gudang, tandai SJ tercetak, retur baris, buat SJ dari packing ERP, cetak SJ (HTML/PDF/dotmatrix), INVPL, Commercial Invoice, unduh Excel.",
        "delivery_headers, delivery_details, packing_headers, packing_details, po_headers, po_details",
        "customers, production_orders, production_details, qc_details, invoices",
    ),
    (
        "Fulfillment",
        "Invoice",
        "/admin/invoice",
        "Daftar invoice THIN (otomatis dari SJ) + tab outstanding AR. Buat/ubah invoice & detail, reminder, cetak tanda terima (HTML/PDF batch).",
        "invoices, invoice_details, delivery_headers, po_headers",
        "customers, document_sequences, notifications",
    ),
    (
        "Fulfillment",
        "Reports",
        "/admin/reports",
        "Laporan PO Harian Marketing (filter tanggal/customer/kategori), generate tampilan, cetak, ekspor CSV/XLSX (daily marketing, SO, baris SO). Termasuk ringkasan revisi ketebalan dari audit.",
        "po_headers, po_details, audit_logs",
        "customers, users",
    ),
    (
        "Buku MRP",
        "Production",
        "/admin/production",
        "Buku baca-saja: daftar production order & detail dari MRP. Operasi harian di MRP Rencana/Proses, bukan di sini.",
        "production_orders, production_details, po_headers, po_details",
        "—",
    ),
    (
        "Buku MRP",
        "Quality Control",
        "/admin/qc",
        "Buku baca-saja: daftar QC header/detail (OK/NG, tebal). Pencatatan operasional di MRP Checkpoint.",
        "qc_headers, qc_details, production_orders, production_details",
        "—",
    ),
    (
        "Buku MRP",
        "Packing",
        "/admin/packing",
        "Buku baca-saja + cetak: daftar packing, filter stub MRP, cetak INVPL (PDF/XLSX). Packing FG dan OUT di MRP Packing / Gudang FG.",
        "packing_headers, packing_details, po_headers, po_details, production_details",
        "delivery_headers, delivery_details, customers (saat cetak INVPL)",
    ),
    (
        "Master Data — Customer & Brand",
        "Customer",
        "/admin/customers",
        "CRUD master customer/consignee: identitas, PIC, NPWP, ekspor, terms, alamat, wilayah Indonesia (provinsi–kelurahan).",
        "customers, customer_pics",
        "po_headers, invoices, delivery_headers (cek relasi saat hapus); wilayah via API eksternal (bukan tabel DB)",
    ),
    (
        "Master Data — Customer & Brand",
        "Master Brand",
        "/admin/brands",
        "CRUD brand untuk input SO, hubungkan ke customer/PT, seed dari buyer, atur mapping buyer per brand.",
        "brands, brand_buyer_maps, customer_brand_mappings",
        "customers, po_headers (cek pemakaian saat hapus)",
    ),
    (
        "Master Data — Customer & Brand",
        "Mapping Customer-Brand",
        "/admin/customer-brand-mapping",
        "Relasi customer ↔ brand (termasuk default) dan batasan brand yang boleh dipilih customer.",
        "customer_brand_mappings, brand_constraints, customers, brands",
        "—",
    ),
    (
        "Master Data — Harga",
        "List Harga Buyer",
        "/admin/buyer-prices",
        "Master harga per buyer: metadata list + kelola baris sheet (COLOR WHITE sebagai base + adder warna/emboss). Impor ZIP/CSV, resolve harga ke SO.",
        "buyer_price_lists, buyer_price_sheet_rows",
        "master_items, po_headers (resolve harga), buyer_codes",
    ),
    (
        "Master Data — Item & Warna",
        "Master Item",
        "/admin/master-items",
        "CRUD referensi FG (kode, material, tebal, warna, emboss) untuk autofill SO. Impor/ekspor, tautan warna CSI/fluorescent/swatch.",
        "master_items, master_prices",
        "color_swatch_recipes, csi_color_masters, fluorescent_color_masters, po_details (cek pemakaian saat hapus)",
    ),
    (
        "Master Data — Item & Warna",
        "Master Color Swatch",
        "/admin/color-swatch",
        "CRUD resep warna per pabrik × buyer × material × emboss; impor CSV/bundled; opsi form dari CSI & master item; dipakai autofill warna wizard SO.",
        "color_swatch_recipes",
        "csi_color_masters, customers, master_items",
    ),
    (
        "Master Data — Item & Warna",
        "Master Fluorescent",
        "/admin/fluorescent-colors",
        "CRUD referensi warna fluorescent/metallic per buyer & season (validasi SO). Impor CSV/bundled.",
        "fluorescent_color_masters",
        "buyer_codes",
    ),
    (
        "Master Data — Item & Warna",
        "Master CSI",
        "/admin/csi-colors",
        "CRUD katalog warna resmi per buyer (CSI ALL BUYER). Impor bundled; dipakai form swatch dan cascade MRP.",
        "csi_color_masters",
        "buyer_codes, color_code_aliases",
    ),
    (
        "Master Data",
        "Data Intelligent",
        "/admin/data-intelligent",
        "Peta relasi master (customer–brand–buyer–item–CSI–swatch): ringkasan gap, perbaikan di web, unduh/unggah Excel, simpan mapping.",
        "customers, brands, brand_buyer_maps, buyer_codes, buyer_price_lists, customer_brand_mappings, master_items, material_aliases, csi_color_masters, fluorescent_color_masters, color_swatch_recipes",
        "—",
    ),
    (
        "System",
        "User & Role Access",
        "/admin/user-access",
        "Tab Users: buat/ubah user, role, status aktif, password. Tab Permission Matrix: modul × aksi per role (menu & tombol mengikuti matrix).",
        "users, role_permissions",
        "—",
    ),
    (
        "System",
        "Login",
        "/login",
        "Autentikasi akun ERP (JWT). Profil user & logout di header.",
        "users",
        "—",
    ),
    (
        "System",
        "Notifikasi (header)",
        "(ikon lonceng)",
        "Daftar notifikasi in-app, hitung belum dibaca, tandai dibaca / semua dibaca.",
        "notifications",
        "users",
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
        textColor=colors.HexColor("#334155"),
        spaceAfter=8,
    )
    cell = ParagraphStyle(
        "Cell",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        textColor=colors.black,
    )
    story = [
        Paragraph("Dokumentasi Menu ERP - Tonghong UAT", title_style),
        Paragraph(
            f"Base URL UI: http://10.227.82.65:8081 | Database ERP: uat_tonghong_erp | "
            f"API: /api/v1 (port 8001) | Dibuat: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            sub_style,
        ),
        Paragraph(
            "Kolom <b>Tabel utama</b> = tabel yang dibaca/ditulis langsung oleh fungsi menu. "
            "Kolom <b>Tabel pendukung</b> = lookup, relasi, atau tabel yang ikut tersentuh "
            "(cetak dokumen, validasi, hapus). Shopfloor (Rencana, Packing FG, stok) ada di MRP :8082.",
            sub_style,
        ),
    ]

    # Header baris tabel: string biasa (bukan Paragraph) agar FONTNAME/TEXTCOLOR TableStyle terbaca di semua viewer.
    table_data: list[list] = [
        ["Grup", "Menu", "Path", "Fungsi", "Tabel utama", "Tabel pendukung"],
    ]
    for grup, menu, pth, fungsi, utama, dukung in ROWS:
        table_data.append(
            [
                Paragraph(grup.replace("&", "&amp;"), cell),
                Paragraph(menu.replace("&", "&amp;"), cell),
                Paragraph(pth.replace("&", "&amp;"), cell),
                Paragraph(fungsi.replace("&", "&amp;"), cell),
                Paragraph(utama.replace("&", "&amp;"), cell),
                Paragraph(dukung.replace("&", "&amp;"), cell),
            ]
        )

    col_widths = [2.6 * cm, 3.2 * cm, 3.6 * cm, 5.8 * cm, 5.4 * cm, 5.0 * cm]
    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#0f172a")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "<b>Struktur sidebar ERP</b> (sesuai /admin): Dashboard | Marketing (SO, Outstanding) | "
            "Fulfillment (Delivery, Invoice, Reports) | Buku MRP (Production, QC, Packing) | "
            "Master Data (Customer &amp; Brand, Harga, Item &amp; Warna, Data Intelligent) | System (User &amp; Role Access). "
            "Rencana Kirim tersedia sebagai route terkait Outstanding.",
            sub_style,
        )
    )
    story.append(
        Paragraph(
            "<i>Catatan:</i> Beberapa halaman (Quotation, Subcon Invoice, Journal, Accounting Mapping, "
            "Inventory, Special Prices) ada di kode tetapi tidak tampil di sidebar ERP UAT :8081. "
            "Inventory &amp; shopfloor hidup di aplikasi MRP (port 8082).",
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
