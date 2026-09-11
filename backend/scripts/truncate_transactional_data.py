#!/usr/bin/env python3
"""Truncate data transaksi ERP (+ opsional MRP), master tetap utuh.

Default = analisis / dry-run (tampilkan jumlah baris). Hapus data hanya dengan
``--execute`` (dan konfirmasi, atau ``--yes``).

Master yang TIDAK disentuh (ERP):
  users, role_permissions, customers, customer_pics, brands,
  customer_brand_mappings, brand_constraints, buyer_codes, brand_buyer_maps,
  master_items, material_aliases, buyer_price_lists, buyer_price_sheet_rows,
  csi_color_masters, color_code_aliases, color_swatch_recipes,
  fluorescent_color_masters, warehouses, raw_materials, exchange_rates,
  accounting_mappings, alembic_version

Master yang TIDAK disentuh (MRP):
  tbl_master_treatment, master_resep

Sequence counter (document_sequences, lot_sequences, tbl_seq) di-reset agar
nomor SO/lot/kode shopfloor mulai ulang.

Contoh:
  cd backend && .venv/bin/python -m scripts.truncate_transactional_data
  cd backend && .venv/bin/python -m scripts.truncate_transactional_data --execute --yes
  cd backend && .venv/bin/python -m scripts.truncate_transactional_data --erp-only --execute --yes
  cd backend && .venv/bin/python -m scripts.truncate_transactional_data --mrp-only --execute --yes
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
sys.path.insert(0, str(ROOT))

# Muat .env proyek (systemd/native stack)
_ENV_FILE = PROJECT / ".env"
if _ENV_FILE.is_file():
    for _line in _ENV_FILE.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        os.environ.setdefault(_k.strip(), _v.strip())

from sqlalchemy import create_engine, inspect, text  # noqa: E402
from sqlalchemy.engine import Engine  # noqa: E402

from app.config import settings  # noqa: E402

# --- ERP: transaksi + sequence (boleh truncate) ---
ERP_TXN_TABLES: list[str] = [
    # dokumen hilir → hulu
    "invoice_details",
    "invoices",
    "delivery_details",
    "delivery_headers",
    "packing_details",
    "packing_headers",
    "qc_details",
    "qc_headers",
    "production_details",
    "production_orders",
        "ppic_assignments",
    "po_detail_deliveries",
    "po_details",
    "po_headers",
    "proforma_invoice_records",
    "marketing_outstanding_snapshots",
    "material_stocks",
    "customs_aju_sheet_rows",
    "customs_declarations",
        "notifications",
    "audit_logs",
    # counter nomor dokumen / lot
    "document_sequences",
    "lot_sequences",
]

ERP_MASTER_TABLES: list[str] = [
    "users",
    "role_permissions",
    "customers",
    "customer_pics",
    "brands",
    "customer_brand_mappings",
    "brand_constraints",
    "buyer_codes",
    "brand_buyer_maps",
    "master_items",
    "material_aliases",
    "buyer_price_lists",
    "buyer_price_sheet_rows",
    "csi_color_masters",
    "color_code_aliases",
    "color_swatch_recipes",
    "fluorescent_color_masters",
    "warehouses",
    "raw_materials",
    "exchange_rates",
        "alembic_version",
]

# --- MRP shopfloor: transaksi (+ seq); master treatment/resep tetap ---
MRP_TXN_TABLES: list[str] = [
    "tbl_packing_inbound_line",
    "tbl_packing_inbound",
    "tbl_packing_roll",
    "tbl_packing_po",
    "tbl_packing",
    "tbl_gudang_fg",
    "tbl_checkpoint",
    "tbl_usage_color",
    "tbl_usage_rp",
    "tbl_usage_material_lain",
    "tbl_lab_mixing",
    "tbl_lab_lot_detail",
    "tbl_lab_lot",
    "tbl_stok_kimia_out",
    "tbl_stok_rp_out",
    "tbl_stok_material_lain_out",
    "tbl_stok_kimia_in",
    "tbl_stok_rp_in",
    "tbl_stok_material_lain_in",
    "tbl_persiapan_scan",
    "tbl_persiapan_ukur",
    "tbl_persiapan_reprint",
    "tbl_persiapan_ky",
    "tbl_kulit_lebih",
    "tbl_persiapan_kulit",
    "tbl_yl_movement",
    "tbl_palet_movement",
    "tbl_yl",
    "tbl_rencana_item_po",
    "tbl_rencana_item",
    "tbl_rencana_produksi",
    "tbl_master_po",
    "tbl_seq",
]

MRP_MASTER_TABLES: list[str] = [
    "tbl_master_treatment",
    "master_resep",
]


def _mrp_engine() -> Engine:
    host = os.environ.get("MRP_DB_HOST", "127.0.0.1")
    port = os.environ.get("MRP_DB_PORT", "3306")
    user = os.environ.get("MRP_DB_USER", "tonghong_mrp")
    password = os.environ.get("MRP_DB_PASSWORD", "tonghong_mrp_secret")
    name = os.environ.get("MRP_DB_NAME", "tonghong_mrp")
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
    return create_engine(url, pool_pre_ping=True)


def _row_counts(eng: Engine, tables: list[str]) -> list[tuple[str, int | None]]:
    live = set(inspect(eng).get_table_names())
    out: list[tuple[str, int | None]] = []
    with eng.connect() as conn:
        for t in tables:
            if t not in live:
                out.append((t, None))
                continue
            n = conn.execute(text(f"SELECT COUNT(*) FROM `{t}`")).scalar()
            out.append((t, int(n or 0)))
    return out


def _print_section(title: str, rows: list[tuple[str, int | None]], *, only_nonempty: bool = False) -> int:
    print(f"\n=== {title} ===")
    total = 0
    for name, n in rows:
        if n is None:
            print(f"  {name:40} (tabel tidak ada)")
            continue
        if only_nonempty and n == 0:
            continue
        print(f"  {name:40} {n:>10}")
        total += n
    print(f"  {'TOTAL':40} {total:>10}")
    return total


def analyze(*, do_erp: bool, do_mrp: bool) -> None:
    print("Analisis data transaksi vs master (tidak mengubah data).")
    if do_erp:
        erp = create_engine(settings.database_url, pool_pre_ping=True)
        live = set(inspect(erp).get_table_names())
        classified = set(ERP_TXN_TABLES) | set(ERP_MASTER_TABLES)
        unknown = sorted(live - classified)
        print(f"\nERP DB: {settings.database_url.rsplit('@', 1)[-1]}")
        _print_section("ERP TRANSAKSI (+ sequence)", _row_counts(erp, ERP_TXN_TABLES))
        _print_section("ERP MASTER (aman — tidak di-truncate)", _row_counts(erp, ERP_MASTER_TABLES))
        if unknown:
            print("\nPERINGATAN — tabel ERP belum diklasifikasi:")
            for t in unknown:
                print(f"  - {t}")
        erp.dispose()

    if do_mrp:
        mrp = _mrp_engine()
        live = set(inspect(mrp).get_table_names())
        classified = set(MRP_TXN_TABLES) | set(MRP_MASTER_TABLES)
        unknown = sorted(live - classified)
        print(f"\nMRP DB: {os.environ.get('MRP_DB_NAME', 'tonghong_mrp')}")
        _print_section("MRP TRANSAKSI (+ seq)", _row_counts(mrp, MRP_TXN_TABLES))
        _print_section("MRP MASTER (aman — tidak di-truncate)", _row_counts(mrp, MRP_MASTER_TABLES))
        if unknown:
            print("\nPERINGATAN — tabel MRP belum diklasifikasi:")
            for t in unknown:
                print(f"  - {t}")
        mrp.dispose()


def _truncate_tables(eng: Engine, tables: list[str], label: str) -> int:
    live = set(inspect(eng).get_table_names())
    targets = [t for t in tables if t in live]
    skipped = [t for t in tables if t not in live]
    if skipped:
        print(f"  [{label}] lewati (tidak ada): {', '.join(skipped)}")
    if not targets:
        print(f"  [{label}] tidak ada tabel target")
        return 0

    # Hitungan sebelum hapus
    before = dict(_row_counts(eng, targets))
    total_before = sum(v or 0 for v in before.values())

    with eng.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        for t in targets:
            conn.execute(text(f"TRUNCATE TABLE `{t}`"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

    print(f"  [{label}] TRUNCATE {len(targets)} tabel ({total_before} baris sebelumnya)")
    for t in targets:
        n = before.get(t) or 0
        if n:
            print(f"    - {t}: {n} → 0")
    return len(targets)


def execute_truncate(*, do_erp: bool, do_mrp: bool) -> None:
    print("MENJALANKAN TRUNCATE data transaksi (master tetap)…")
    n = 0
    if do_erp:
        erp = create_engine(settings.database_url, pool_pre_ping=True)
        # Guard: jangan pernah truncate master
        live_master = [t for t in ERP_MASTER_TABLES if t in set(inspect(erp).get_table_names())]
        assert not set(ERP_TXN_TABLES) & set(ERP_MASTER_TABLES)
        n += _truncate_tables(erp, ERP_TXN_TABLES, "ERP")
        # verifikasi master masih ada
        counts = dict(_row_counts(erp, live_master))
        print("  [ERP] master tersisa (contoh):")
        for t in ("users", "customers", "master_items", "color_swatch_recipes", "alembic_version"):
            if t in counts and counts[t] is not None:
                print(f"    {t}: {counts[t]}")
        erp.dispose()

    if do_mrp:
        mrp = _mrp_engine()
        assert not set(MRP_TXN_TABLES) & set(MRP_MASTER_TABLES)
        n += _truncate_tables(mrp, MRP_TXN_TABLES, "MRP")
        counts = dict(_row_counts(mrp, MRP_MASTER_TABLES))
        print("  [MRP] master tersisa:")
        for t, c in counts.items():
            print(f"    {t}: {c}")
        mrp.dispose()

    print(f"\nSelesai. {n} tabel transaksi di-TRUNCATE.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Truncate data transaksi ERP/MRP; master data tidak dihapus.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Benar-benar truncate (tanpa flag ini hanya analisis).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Lewati prompt konfirmasi (wajib bersama --execute di non-interaktif).",
    )
    parser.add_argument("--erp-only", action="store_true", help="Hanya database ERP (tonghong).")
    parser.add_argument("--mrp-only", action="store_true", help="Hanya database MRP (tonghong_mrp).")
    args = parser.parse_args()

    if args.erp_only and args.mrp_only:
        print("Pilih salah satu: --erp-only atau --mrp-only", file=sys.stderr)
        return 2

    do_erp = not args.mrp_only
    do_mrp = not args.erp_only

    analyze(do_erp=do_erp, do_mrp=do_mrp)

    if not args.execute:
        print(
            "\nDry-run saja. Untuk menghapus data transaksi:\n"
            "  .venv/bin/python -m scripts.truncate_transactional_data --execute --yes",
        )
        return 0

    if not args.yes:
        try:
            ans = input(
                "\nKetik YES untuk truncate SEMUA data transaksi "
                f"({'ERP' if do_erp else ''}{'+' if do_erp and do_mrp else ''}{'MRP' if do_mrp else ''}): ",
            ).strip()
        except EOFError:
            ans = ""
        if ans != "YES":
            print("Dibatalkan.")
            return 1

    execute_truncate(do_erp=do_erp, do_mrp=do_mrp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
