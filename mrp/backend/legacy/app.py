from flask import Flask, request, redirect
from datetime import datetime, date
import mysql.connector
import os

from db import get_db_connection

app = Flask(__name__)
app.secret_key = os.getenv("MRP_SECRET_KEY", "change-me-dev-only")


def _redirect_mrp_ui(path: str):
    """HTML Flask shopfloor sudah diganti Vue — arahkan ke UI MRP."""
    base = (
        os.getenv("MRP_UI_ORIGIN")
        or os.getenv("VITE_MRP_UI_ORIGIN")
        or ""
    ).rstrip("/")
    target = f"{base}{path}" if base else path
    return redirect(target)


def generate_code(prefix):
    today = datetime.today().strftime("%y%m%d")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tbl_seq (name, last_val, prefix, date_key) VALUES (%s, 1, %s, %s) "
        "ON DUPLICATE KEY UPDATE last_val = IF(date_key = VALUES(date_key), last_val + 1, 1), "
        "date_key = VALUES(date_key)",
        (prefix, prefix, today),
    )
    conn.commit()
    cur.execute("SELECT last_val FROM tbl_seq WHERE name = %s", (prefix,))
    seq = cur.fetchone()[0]
    cur.close()
    conn.close()
    return f"{prefix}-{today}{seq:06d}"


WIP_PERSIAPAN_SEQ = "WIP-PERSIAPAN"


def _wip_persiapan_date_key() -> str:
    return datetime.today().strftime("%Y%m%d")


def preview_wip_persiapan_code(cur=None) -> str:
    """Preview kode WIP berikutnya tanpa mengonsumsi nomor urut."""
    today = _wip_persiapan_date_key()
    own_conn = cur is None
    if own_conn:
        conn = get_db_connection()
        cur = conn.cursor()
    cur.execute("SELECT last_val, date_key FROM tbl_seq WHERE name = %s", (WIP_PERSIAPAN_SEQ,))
    row = cur.fetchone()
    if row:
        if isinstance(row, dict):
            last_val = row.get("last_val")
            date_key = row.get("date_key")
        else:
            last_val, date_key = row[0], row[1]
        next_val = (int(last_val) + 1) if str(date_key) == today else 1
    else:
        next_val = 1
    if own_conn:
        cur.close()
        conn.close()
    return f"WIP-{today}-{next_val:05d}"


def allocate_wip_persiapan_code(cur=None) -> str:
    """Alokasikan kode WIP persiapan kulit; nomor urut naik saat commit."""
    today = _wip_persiapan_date_key()
    own_conn = cur is None
    if own_conn:
        conn = get_db_connection()
        cur = conn.cursor()
    cur.execute(
        "INSERT INTO tbl_seq (name, last_val, prefix, date_key) VALUES (%s, 1, %s, %s) "
        "ON DUPLICATE KEY UPDATE last_val = IF(date_key = VALUES(date_key), last_val + 1, 1), "
        "date_key = VALUES(date_key)",
        (WIP_PERSIAPAN_SEQ, "WIP", today),
    )
    cur.execute("SELECT last_val FROM tbl_seq WHERE name = %s", (WIP_PERSIAPAN_SEQ,))
    row = cur.fetchone()
    if row:
        if isinstance(row, dict):
            seq = int(row.get("last_val") or 1)
        else:
            seq = int(row[0])
    else:
        seq = 1
    if own_conn:
        conn.commit()
        cur.close()
        conn.close()
    return f"WIP-{today}-{seq:05d}"


def _col_names(cur, table):
    try:
        cur.execute(f"SHOW COLUMNS FROM {table}")
    except mysql.connector.Error:
        return set()
    rows = cur.fetchall()
    if rows and isinstance(rows[0], dict):
        return {r["Field"] for r in rows}
    return {r[0] for r in rows}


def _row_first(row):
    if isinstance(row, dict):
        return next(iter(row.values()))
    return row[0]


def ensure_rencana_tables(cur):
    # ERP-only: jangan CREATE master_customer (mirror). Snapshot di tbl_rencana_item.
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_rencana_item ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "rencana_id INT NOT NULL, "
        "kode_rencana_item VARCHAR(30) NOT NULL UNIQUE, "
        "kode_lot_wip VARCHAR(30) DEFAULT NULL, "
        "customer_id INT NOT NULL, "
        "kode_kulit VARCHAR(50) DEFAULT NULL, "
        "thickness VARCHAR(30) DEFAULT NULL, "
        "color VARCHAR(100) DEFAULT NULL, "
        "emboss VARCHAR(100) DEFAULT NULL, "
        "color_swatch VARCHAR(100) DEFAULT NULL, "
        "keterangan VARCHAR(255) DEFAULT NULL, "
        "urutan INT DEFAULT 1, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "INDEX idx_rencana_item (rencana_id))"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_rencana_item_po ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "item_id INT NOT NULL, "
        "po_id INT NOT NULL, "
        "qty_outstanding DECIMAL(12,2) DEFAULT 0, "
        "qty_proses DECIMAL(12,2) DEFAULT 0, "
        "INDEX idx_item_po (item_id))"
    )
    rp_cols = _col_names(cur, "tbl_rencana_produksi")
    if "tanggal_rencana" not in rp_cols:
        cur.execute("ALTER TABLE tbl_rencana_produksi ADD COLUMN tanggal_rencana DATE DEFAULT NULL")
    try:
        cur.execute("ALTER TABLE tbl_rencana_produksi MODIFY kode_lot_wip VARCHAR(30) NULL")
    except mysql.connector.Error:
        pass
    po_cols = _col_names(cur, "tbl_master_po")
    if "customer_id" not in po_cols:
        cur.execute("ALTER TABLE tbl_master_po ADD COLUMN customer_id INT DEFAULT NULL")
    lab_cols = _col_names(cur, "tbl_lab_lot")
    if "rencana_item_id" not in lab_cols:
        cur.execute("ALTER TABLE tbl_lab_lot ADD COLUMN rencana_item_id INT DEFAULT NULL")
    item_cols = _col_names(cur, "tbl_rencana_item")
    if item_cols and "nama_customer" not in item_cols:
        cur.execute(
            "ALTER TABLE tbl_rencana_item ADD COLUMN nama_customer VARCHAR(150) DEFAULT NULL "
            "AFTER customer_id"
        )
    if item_cols and "print_qty" not in item_cols:
        cur.execute(
            "ALTER TABLE tbl_rencana_item ADD COLUMN print_qty DECIMAL(12,2) DEFAULT NULL"
        )
    if item_cols and "print_schedule" not in item_cols:
        cur.execute(
            "ALTER TABLE tbl_rencana_item ADD COLUMN print_schedule VARCHAR(80) DEFAULT NULL"
        )
    if item_cols and "print_remarks" not in item_cols:
        cur.execute(
            "ALTER TABLE tbl_rencana_item ADD COLUMN print_remarks VARCHAR(255) DEFAULT NULL"
        )
    try:
        cur.execute(
            "UPDATE tbl_rencana_item i "
            ""
            "SET i.nama_customer = c.nama_customer "
            "WHERE (i.nama_customer IS NULL OR i.nama_customer='') "
            "AND c.nama_customer IS NOT NULL"
        )
    except Exception:
        pass
    try:
        from erp_customers import resolve_customer

        cur.execute(
            "SELECT DISTINCT customer FROM tbl_master_po "
            "WHERE customer IS NOT NULL AND customer != ''"
        )
        for row in cur.fetchall():
            nama = _row_first(row)
            resolved = resolve_customer(nama)
            if not resolved:
                continue
            cur.execute(
                "UPDATE tbl_master_po SET customer_id=%s WHERE customer=%s",
                (resolved["id"], nama),
            )
            cur.execute(
                "UPDATE tbl_rencana_item i "
                ""
                "SET i.customer_id=%s, i.nama_customer=%s "
                "WHERE mc.nama_customer=%s",
                (resolved["id"], resolved["name"], nama),
            )
            cur.execute(
                "UPDATE tbl_rencana_item SET customer_id=%s, nama_customer=%s "
                "WHERE nama_customer=%s",
                (resolved["id"], resolved["name"], nama),
            )
    except Exception:
        pass


def ensure_extended_tables(cur):
    # ERP-only catalogs: jangan CREATE master_erp / master_material_lain.
    try:
        from lot_erp_columns import ensure_lot_erp_columns
        ensure_lot_erp_columns(cur)
    except Exception:
        pass
    try:
        from dual_gudang import ensure_dual_gudang
        ensure_dual_gudang(cur)
    except Exception:
        pass
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_stok_material_lain_in ("
        "id INT AUTO_INCREMENT PRIMARY KEY, kode_internal VARCHAR(50) NOT NULL UNIQUE, "
        "material_id INT NOT NULL, qty DECIMAL(12,2) NOT NULL, qty_sisa DECIMAL(12,2) NOT NULL, "
        "satuan VARCHAR(20) DEFAULT 'pcs', tanggal_in DATE NOT NULL, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_stok_material_lain_out ("
        "id INT AUTO_INCREMENT PRIMARY KEY, stok_in_id INT DEFAULT NULL, material_id INT NOT NULL, "
        "qty DECIMAL(12,2) NOT NULL, kode_wip VARCHAR(30) DEFAULT NULL, tanggal DATE NOT NULL, "
        "keterangan VARCHAR(255) DEFAULT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_usage_material_lain ("
        "id INT AUTO_INCREMENT PRIMARY KEY, kode_wip VARCHAR(30) NOT NULL, "
        "kode_material VARCHAR(50) NOT NULL, nama_material VARCHAR(150) DEFAULT NULL, "
        "qty_used DECIMAL(12,2) DEFAULT 0, satuan VARCHAR(20) DEFAULT 'pcs', "
        "date_created DATETIME DEFAULT CURRENT_TIMESTAMP, INDEX idx_kode_wip (kode_wip))"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_packing_po ("
        "id INT AUTO_INCREMENT PRIMARY KEY, packing_id INT NOT NULL, po_id INT DEFAULT NULL, "
        "no_po VARCHAR(50) NOT NULL, no_so VARCHAR(50) DEFAULT NULL, "
        "qty_sq DECIMAL(12,2) DEFAULT 0)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_gudang_fg ("
        "id INT AUTO_INCREMENT PRIMARY KEY, packing_id INT NOT NULL UNIQUE, "
        "kode_packing VARCHAR(30) NOT NULL UNIQUE, kode_wip VARCHAR(30) NOT NULL, "
        "customer VARCHAR(150) DEFAULT NULL, total_lembar INT DEFAULT 0, "
        "total_ukuran DECIMAL(12,2) DEFAULT 0, status ENUM('in_stock','out') DEFAULT 'in_stock', "
        "date_in DATETIME DEFAULT CURRENT_TIMESTAMP, date_out DATETIME DEFAULT NULL, "
        "keterangan_out VARCHAR(255) DEFAULT NULL)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_persiapan_ky ("
        "id INT AUTO_INCREMENT PRIMARY KEY, persiapan_id INT NOT NULL, "
        "kode_palet VARCHAR(50) NOT NULL, kode_yl VARCHAR(50) DEFAULT NULL, "
        "target_qty DECIMAL(12,2) DEFAULT 0, actual_qty DECIMAL(12,2) DEFAULT 0, "
        "status ENUM('active','selesai') DEFAULT 'active', created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_kulit_lebih ("
        "id INT AUTO_INCREMENT PRIMARY KEY, rencana_item_id INT NOT NULL, "
        "persiapan_id INT DEFAULT NULL, ky_id INT DEFAULT NULL, "
        "kode_palet VARCHAR(50) DEFAULT NULL, kode_yl VARCHAR(50) DEFAULT NULL, "
        "target_qty DECIMAL(12,2) DEFAULT 0, actual_qty DECIMAL(12,2) DEFAULT 0, "
        "selisih DECIMAL(12,2) DEFAULT 0, keterangan VARCHAR(255) DEFAULT NULL, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, INDEX idx_rencana_item (rencana_item_id))"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_stock_sisa ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "sumber VARCHAR(20) NOT NULL COMMENT 'kimia|kulit|wip|fg', "
        "barcode VARCHAR(80) DEFAULT NULL, "
        "lot VARCHAR(80) DEFAULT NULL, "
        "qty DECIMAL(12,2) NOT NULL DEFAULT 0, "
        "status VARCHAR(20) NOT NULL DEFAULT 'open' "
        "COMMENT 'open|reserved|consumed|approved', "
        "po_id INT DEFAULT NULL, "
        "notes VARCHAR(255) DEFAULT NULL, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "INDEX idx_stock_sisa_status (status), "
        "INDEX idx_stock_sisa_sumber (sumber), "
        "INDEX idx_stock_sisa_barcode (barcode), "
        "INDEX idx_stock_sisa_po (po_id))"
    )
    sisa_cols = _col_names(cur, "tbl_stock_sisa")
    for col, ddl in (
        ("kode_rpi", "VARCHAR(30) DEFAULT NULL"),
        ("kode_wip", "VARCHAR(30) DEFAULT NULL"),
        ("material_name", "VARCHAR(200) DEFAULT NULL"),
        ("warna", "VARCHAR(100) DEFAULT NULL"),
        ("tebal", "VARCHAR(30) DEFAULT NULL"),
        ("treatment_jenis", "VARCHAR(20) DEFAULT NULL"),
    ):
        if col not in sisa_cols:
            cur.execute(f"ALTER TABLE tbl_stock_sisa ADD COLUMN {col} {ddl}")
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_stock_sisa_fg_assign ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "sisa_id INT NOT NULL, "
        "po_id INT NOT NULL, "
        "qty DECIMAL(12,2) NOT NULL, "
        "notes VARCHAR(255) DEFAULT NULL, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "INDEX idx_sisa_fg_assign_sisa (sisa_id), "
        "INDEX idx_sisa_fg_assign_po (po_id))"
    )
    packing_cols_sisa = _col_names(cur, "tbl_packing")
    if packing_cols_sisa and "stock_sisa_id" not in packing_cols_sisa:
        cur.execute("ALTER TABLE tbl_packing ADD COLUMN stock_sisa_id INT DEFAULT NULL")
    item_cols = _col_names(cur, "tbl_rencana_item")
    if "backer" not in item_cols:
        cur.execute("ALTER TABLE tbl_rencana_item ADD COLUMN backer VARCHAR(100) DEFAULT NULL")
    if "kode_barcode" not in item_cols:
        cur.execute("ALTER TABLE tbl_rencana_item ADD COLUMN kode_barcode VARCHAR(50) DEFAULT NULL")
    kimia_in_cols = _col_names(cur, "tbl_stok_kimia_in")
    if "jumlah_kemasan" not in kimia_in_cols:
        cur.execute("ALTER TABLE tbl_stok_kimia_in ADD COLUMN jumlah_kemasan INT DEFAULT NULL")
    if kimia_in_cols and "lot_number" not in kimia_in_cols:
        cur.execute(
            "ALTER TABLE tbl_stok_kimia_in ADD COLUMN lot_number VARCHAR(100) DEFAULT NULL"
        )
    rp_in_cols_lot = _col_names(cur, "tbl_stok_rp_in")
    if rp_in_cols_lot and "lot_number" not in rp_in_cols_lot:
        cur.execute(
            "ALTER TABLE tbl_stok_rp_in ADD COLUMN lot_number VARCHAR(100) DEFAULT NULL"
        )
    kimia_out_cols = _col_names(cur, "tbl_stok_kimia_out")
    if "jumlah_kemasan" not in kimia_out_cols:
        cur.execute("ALTER TABLE tbl_stok_kimia_out ADD COLUMN jumlah_kemasan INT DEFAULT NULL")
    ukur_cols = _col_names(cur, "tbl_persiapan_ukur")
    if "ky_id" not in ukur_cols:
        cur.execute("ALTER TABLE tbl_persiapan_ukur ADD COLUMN ky_id INT DEFAULT NULL")
    ky_cols = _col_names(cur, "tbl_persiapan_ky")
    if "yl_consumed" not in ky_cols:
        cur.execute(
            "ALTER TABLE tbl_persiapan_ky ADD COLUMN yl_consumed TINYINT(1) NOT NULL DEFAULT 0"
        )
    if "qty_consumed" not in ky_cols:
        cur.execute(
            "ALTER TABLE tbl_persiapan_ky ADD COLUMN qty_consumed DECIMAL(12,2) NOT NULL DEFAULT 0"
        )
    if "tidak_ada_sisa" not in ky_cols:
        cur.execute(
            "ALTER TABLE tbl_persiapan_ky ADD COLUMN tidak_ada_sisa TINYINT(1) NOT NULL DEFAULT 0"
        )
    cur.execute("SHOW COLUMNS FROM tbl_persiapan_ky LIKE 'status'")
    status_col = cur.fetchone()
    if status_col and "planned" not in str(status_col.get("Type") or ""):
        cur.execute(
            "ALTER TABLE tbl_persiapan_ky MODIFY status "
            "ENUM('planned','active','selesai') DEFAULT 'planned'"
        )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_proses_return ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "persiapan_id INT NOT NULL, "
        "ky_id INT DEFAULT NULL, "
        "kode_wip VARCHAR(30) NOT NULL, "
        "kode_palet VARCHAR(50) NOT NULL COMMENT 'KY lama', "
        "kode_yl_lama VARCHAR(50) NOT NULL, "
        "kode_yl_baru VARCHAR(55) NOT NULL COMMENT 'YL lama + -R', "
        "return_qty DECIMAL(12,2) NOT NULL DEFAULT 0, "
        "treatment_list TEXT DEFAULT NULL, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "INDEX idx_proses_return_wip (kode_wip), "
        "INDEX idx_proses_return_persiapan (persiapan_id), "
        "INDEX idx_proses_return_ky (ky_id))"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_gudang_mod ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "kode_mod VARCHAR(30) NOT NULL, "
        "persiapan_id INT NOT NULL, "
        "ky_id INT DEFAULT NULL, "
        "kode_wip VARCHAR(30) NOT NULL, "
        "kode_palet VARCHAR(50) NOT NULL COMMENT 'KY lama', "
        "kode_yl VARCHAR(50) NOT NULL, "
        "reject_qty DECIMAL(12,2) NOT NULL DEFAULT 0, "
        "treatment_list TEXT DEFAULT NULL, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "UNIQUE KEY uq_gudang_mod_kode (kode_mod), "
        "INDEX idx_gudang_mod_wip (kode_wip), "
        "INDEX idx_gudang_mod_persiapan (persiapan_id), "
        "INDEX idx_gudang_mod_ky (ky_id))"
    )
    mod_cols = _col_names(cur, "tbl_gudang_mod")
    if mod_cols and "reject_lembar" not in mod_cols:
        cur.execute(
            "ALTER TABLE tbl_gudang_mod ADD COLUMN reject_lembar INT NOT NULL DEFAULT 0 "
            "COMMENT 'Jumlah baris/lembar pengukuran'"
        )
    mod_cols = _col_names(cur, "tbl_gudang_mod")
    if mod_cols and "status" not in mod_cols:
        cur.execute(
            "ALTER TABLE tbl_gudang_mod ADD COLUMN status "
            "ENUM('in_stock','out') NOT NULL DEFAULT 'in_stock'"
        )
    if mod_cols and "consumed_persiapan_id" not in mod_cols:
        cur.execute(
            "ALTER TABLE tbl_gudang_mod ADD COLUMN consumed_persiapan_id INT DEFAULT NULL"
        )
    if mod_cols and "date_out" not in mod_cols:
        cur.execute("ALTER TABLE tbl_gudang_mod ADD COLUMN date_out DATETIME DEFAULT NULL")
    if mod_cols:
        cur.execute(
            "UPDATE tbl_gudang_mod SET status='in_stock' "
            "WHERE status IS NULL OR TRIM(status)=''"
        )
    ky_cols = _col_names(cur, "tbl_persiapan_ky")
    if ky_cols and "gudang_mod_id" not in ky_cols:
        cur.execute(
            "ALTER TABLE tbl_persiapan_ky ADD COLUMN gudang_mod_id INT DEFAULT NULL "
            "COMMENT 'Sumber stok Gudang MOD'"
        )
    pers_cols = _col_names(cur, "tbl_persiapan_kulit")
    if "rencana_item_id" not in pers_cols:
        cur.execute("ALTER TABLE tbl_persiapan_kulit ADD COLUMN rencana_item_id INT DEFAULT NULL")
    if pers_cols and "checkpoint_status" not in pers_cols:
        cur.execute(
            "ALTER TABLE tbl_persiapan_kulit ADD COLUMN checkpoint_status VARCHAR(100) DEFAULT NULL"
        )
    if pers_cols and "no_po" in pers_cols:
        cur.execute("SHOW COLUMNS FROM tbl_persiapan_kulit LIKE 'no_po'")
        no_po_col = cur.fetchone()
        no_po_type = ""
        if isinstance(no_po_col, dict):
            no_po_type = str(no_po_col.get("Type") or "").lower()
        elif no_po_col and len(no_po_col) > 1:
            no_po_type = str(no_po_col[1] or "").lower()
        if no_po_type.startswith("varchar("):
            try:
                width = int(no_po_type.split("(")[1].split(")")[0])
            except (IndexError, ValueError):
                width = 50
            if width < 500:
                cur.execute(
                    "ALTER TABLE tbl_persiapan_kulit MODIFY no_po VARCHAR(500) DEFAULT NULL"
                )
    # Legacy write path memakai status 'saved'; write path baru = 'completed'.
    # Gate packing/lab tetap menerima keduanya; normalisasi data lama sekali jalan.
    if pers_cols or _col_names(cur, "tbl_persiapan_kulit"):
        cur.execute(
            "UPDATE tbl_persiapan_kulit SET status='completed' "
            "WHERE status='saved'"
        )
        cur.execute("SHOW COLUMNS FROM tbl_persiapan_kulit LIKE 'status'")
        pers_status = cur.fetchone()
        if isinstance(pers_status, dict):
            pers_type = str(pers_status.get("Type") or "")
        elif pers_status:
            pers_type = str(pers_status[1] if len(pers_status) > 1 else "")
        else:
            pers_type = ""
        if pers_status and "voided" not in pers_type:
            cur.execute(
                "ALTER TABLE tbl_persiapan_kulit MODIFY status "
                "ENUM('draft','started','saved','completed','voided') DEFAULT 'draft'"
            )
    if "material_name" not in item_cols:
        cur.execute("ALTER TABLE tbl_rencana_item ADD COLUMN material_name VARCHAR(150) DEFAULT NULL")
    packing_cols = _col_names(cur, "tbl_packing")
    if packing_cols:
        if "softness" not in packing_cols:
            cur.execute("ALTER TABLE tbl_packing ADD COLUMN softness VARCHAR(50) DEFAULT NULL")
        if "gross_weight" not in packing_cols:
            cur.execute("ALTER TABLE tbl_packing ADD COLUMN gross_weight DECIMAL(12,2) DEFAULT NULL")
        if "net_weight" not in packing_cols:
            cur.execute("ALTER TABLE tbl_packing ADD COLUMN net_weight DECIMAL(12,2) DEFAULT NULL")
    roll_cols = _col_names(cur, "tbl_packing_roll")
    if roll_cols and "remark" not in roll_cols:
        cur.execute("ALTER TABLE tbl_packing_roll ADD COLUMN remark VARCHAR(255) DEFAULT NULL")
    if roll_cols:
        roll_cols = _col_names(cur, "tbl_packing_roll")
        if "kode_packing" not in roll_cols:
            cur.execute(
                "ALTER TABLE tbl_packing_roll ADD COLUMN kode_packing VARCHAR(30) DEFAULT NULL"
            )
        if "sizes_text" not in roll_cols:
            cur.execute(
                "ALTER TABLE tbl_packing_roll ADD COLUMN sizes_text VARCHAR(500) DEFAULT NULL"
            )
        roll_cols = _col_names(cur, "tbl_packing_roll")
        if "impactiva_grading" not in roll_cols:
            cur.execute(
                "ALTER TABLE tbl_packing_roll ADD COLUMN impactiva_grading VARCHAR(120) DEFAULT NULL"
            )
        if "moisture" not in roll_cols:
            cur.execute(
                "ALTER TABLE tbl_packing_roll ADD COLUMN moisture VARCHAR(40) DEFAULT NULL"
            )
    # ERP-only: jangan ALTER/seed master_erp / master_* mirror (sudah di-drop).
    po_cols_ext = _col_names(cur, "tbl_master_po")
    if "color_swatch" not in po_cols_ext:
        cur.execute("ALTER TABLE tbl_master_po ADD COLUMN color_swatch VARCHAR(100) DEFAULT NULL")
    if "source_detail_id" not in po_cols_ext:
        cur.execute("ALTER TABLE tbl_master_po ADD COLUMN source_detail_id INT DEFAULT NULL")
        try:
            cur.execute(
                "CREATE INDEX idx_master_po_source_detail ON tbl_master_po (source_detail_id)"
            )
        except mysql.connector.Error:
            pass
    if "qty_balance_erp" not in po_cols_ext:
        cur.execute(
            "ALTER TABLE tbl_master_po ADD COLUMN qty_balance_erp DECIMAL(12,2) DEFAULT NULL"
        )
    if "lot_number" not in po_cols_ext:
        cur.execute(
            "ALTER TABLE tbl_master_po ADD COLUMN lot_number VARCHAR(100) DEFAULT NULL"
        )
    packing_cols2 = _col_names(cur, "tbl_packing")
    if packing_cols2:
        if "erp_production_id" not in packing_cols2:
            cur.execute(
                "ALTER TABLE tbl_packing ADD COLUMN erp_production_id BIGINT DEFAULT NULL"
            )
        if "erp_production_detail_id" not in packing_cols2:
            cur.execute(
                "ALTER TABLE tbl_packing ADD COLUMN erp_production_detail_id BIGINT DEFAULT NULL"
            )
        if "rencana_item_id" not in packing_cols2:
            cur.execute(
                "ALTER TABLE tbl_packing ADD COLUMN rencana_item_id INT DEFAULT NULL"
            )
    item_cols2 = _col_names(cur, "tbl_rencana_item")
    if item_cols2:
        if "erp_production_id" not in item_cols2:
            cur.execute(
                "ALTER TABLE tbl_rencana_item ADD COLUMN erp_production_id BIGINT DEFAULT NULL"
            )
        if "erp_production_detail_id" not in item_cols2:
            cur.execute(
                "ALTER TABLE tbl_rencana_item ADD COLUMN erp_production_detail_id BIGINT DEFAULT NULL"
            )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_checkpoint ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "kode_wip VARCHAR(30) NOT NULL, "
        "kode_packing VARCHAR(30) DEFAULT NULL, "
        "checkpoint_type VARCHAR(50) DEFAULT 'inline', "
        "treatment VARCHAR(100) DEFAULT NULL, "
        "thickness_actual DECIMAL(10,3) DEFAULT NULL, "
        "softness_actual VARCHAR(100) DEFAULT NULL, "
        "result VARCHAR(16) DEFAULT NULL, "
        "is_ok TINYINT(1) DEFAULT NULL, "
        "remark VARCHAR(255) DEFAULT NULL, "
        "erp_production_detail_id BIGINT DEFAULT NULL, "
        "erp_qc_detail_id BIGINT DEFAULT NULL, "
        "measured_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "INDEX idx_checkpoint_wip (kode_wip))"
    )
    cp_cols = _col_names(cur, "tbl_checkpoint")
    if cp_cols and "treatment" not in cp_cols:
        cur.execute("ALTER TABLE tbl_checkpoint ADD COLUMN treatment VARCHAR(100) DEFAULT NULL")
    fg_cols = _col_names(cur, "tbl_gudang_fg")
    if fg_cols:
        if "erp_delivery_id" not in fg_cols:
            cur.execute(
                "ALTER TABLE tbl_gudang_fg ADD COLUMN erp_delivery_id BIGINT DEFAULT NULL"
            )
        if "erp_delivery_number" not in fg_cols:
            cur.execute(
                "ALTER TABLE tbl_gudang_fg ADD COLUMN erp_delivery_number VARCHAR(100) DEFAULT NULL"
            )
        if "bridge_status" not in fg_cols:
            cur.execute(
                "ALTER TABLE tbl_gudang_fg ADD COLUMN bridge_status VARCHAR(32) DEFAULT NULL"
            )
        if "bridge_error" not in fg_cols:
            cur.execute(
                "ALTER TABLE tbl_gudang_fg ADD COLUMN bridge_error VARCHAR(255) DEFAULT NULL"
            )


def _make_rpi_barcode(thickness, emboss, color):
    def short(val):
        if not val:
            return "NA"
        return "".join(c for c in val.upper() if c.isalnum())[:6]
    return f"RPI-{short(thickness)}-{short(emboss)}-{short(color)}"


def _ensure_master_treatment_body(cur):
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_master_treatment ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "jenis ENUM('PU','Suede') NOT NULL DEFAULT 'PU', "
        "nama_treatment VARCHAR(100) NOT NULL, "
        "is_active TINYINT(1) NOT NULL DEFAULT 1, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "UNIQUE KEY uk_nama_treatment (nama_treatment))"
    )
    cols = _col_names(cur, "tbl_master_treatment")
    if "created_at" not in cols:
        cur.execute(
            "ALTER TABLE tbl_master_treatment ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
    if "is_active" not in cols:
        cur.execute(
            "ALTER TABLE tbl_master_treatment ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1"
        )
    # Seed resmi PU / Suede untuk proses persiapan (UNIQUE nama_treatment).
    seeds = (
        ("PU", "PU - Degrease"),
        ("PU", "PU - Base Coat"),
        ("PU", "PU - Color Coat"),
        ("PU", "PU - Top Coat"),
        ("PU", "PU - Emboss / Press"),
        ("PU", "PU - Emboss"),
        ("Suede", "Suede - Buffing"),
        ("Suede", "Suede - Dyeing"),
        ("Suede", "Suede - Softener"),
        ("Suede", "Suede - Finishing Spray"),
    )
    for jenis, nama in seeds:
        cur.execute("SELECT id FROM tbl_master_treatment WHERE nama_treatment = %s", (nama,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO tbl_master_treatment (jenis, nama_treatment, is_active) VALUES (%s, %s, 1)",
                (jenis, nama),
            )
    # Nonaktifkan placeholder lama dari dump demo (tetap di DB agar history tidak hilang).
    for obsolete in (
        "Treatment A",
        "Treatment B",
        "Treatment C",
        "Treatment D",
        "Treatment Sueda A",
        "Emboss",
    ):
        cur.execute(
            "UPDATE tbl_master_treatment SET is_active=0 WHERE nama_treatment=%s AND is_active=1",
            (obsolete,),
        )


def ensure_master_treatment(cur=None):
    """Seed master treatment (koneksi sendiri + cursor buffered — hindari unread result / deadlock)."""
    del cur  # API lama tetap terima cursor request; tidak dipakai agar tidak bentrok dengan cursor caller.
    conn = get_db_connection()
    bcur = conn.cursor(dictionary=True, buffered=True)
    try:
        _ensure_master_treatment_body(bcur)
        conn.commit()
    finally:
        bcur.close()
        conn.close()


def ensure_lab_tables(cur):
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_lab_lot ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "kode_lot_warna VARCHAR(30) NOT NULL UNIQUE, "
        "nama_lot_warna VARCHAR(150) NOT NULL, "
        "status ENUM('active','used','expired') DEFAULT 'active', "
        "date_created DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "INDEX idx_kode_lot_warna (kode_lot_warna))"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_lab_lot_detail ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "kode_lot_warna VARCHAR(30) NOT NULL, "
        "kode_kimia VARCHAR(50) NOT NULL, "
        "nama_kimia VARCHAR(150) DEFAULT NULL, "
        "resep VARCHAR(150) DEFAULT NULL, "
        "satuan VARCHAR(20) DEFAULT 'kg', "
        "qty DECIMAL(12,2) DEFAULT 0, "
        "remarks TEXT DEFAULT NULL, "
        "INDEX idx_lot_detail (kode_lot_warna))"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_lab_lot_sisa ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "kode_lot_warna VARCHAR(30) NOT NULL, "
        "nama_lot_warna VARCHAR(150) DEFAULT NULL, "
        "qty_sisa DECIMAL(12,2) NOT NULL, "
        "notes TEXT DEFAULT NULL, "
        "status ENUM('open','mixed') NOT NULL DEFAULT 'open', "
        "date_created DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "INDEX idx_lab_sisa_lot (kode_lot_warna), "
        "INDEX idx_lab_sisa_date (date_created))"
    )
    sisa_cols = _col_names(cur, "tbl_lab_lot_sisa")
    if sisa_cols and "status" not in sisa_cols:
        cur.execute(
            "ALTER TABLE tbl_lab_lot_sisa "
            "ADD COLUMN status ENUM('open','mixed') NOT NULL DEFAULT 'open'"
        )


def init_db_tables():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS tbl_seq ("
            "name VARCHAR(30) PRIMARY KEY, last_val INT NOT NULL DEFAULT 0, "
            "prefix VARCHAR(10) DEFAULT '', date_key VARCHAR(8) DEFAULT '')"
        )
        # ERP-only: skip CREATE/ALTER master_kulit
        kulit_cols = set()
        # ERP-only: skip CREATE/ALTER master_rp & master_kimia (katalog di tonghong.raw_materials)
        cur.execute("SHOW INDEX FROM tbl_yl WHERE Key_name = 'uk_kode_yl'")
        if cur.fetchone():
            cur.execute("ALTER TABLE tbl_yl DROP INDEX uk_kode_yl")
        cur.execute("SHOW INDEX FROM tbl_yl WHERE Key_name = 'uk_palet_yl'")
        if not cur.fetchone():
            cur.execute("ALTER TABLE tbl_yl ADD UNIQUE KEY uk_palet_yl (kode_palet, kode_yl)")
        ensure_lab_tables(cur)
        ensure_rencana_tables(cur)
        ensure_master_treatment(cur)
        ensure_extended_tables(cur)
        conn.commit()
        cur.close()
        conn.close()
    except mysql.connector.Error:
        pass


init_db_tables()


def _master_po_alloc_status(qty_order: float, qty_processed: float, current_status: str | None = None) -> str:
    """Status alokasi plan di MRP (bukan status cancel ERP)."""
    status = (current_status or "").strip()
    if status == "cancelled":
        return "cancelled"
    if qty_processed >= qty_order > 0:
        return "completed"
    if qty_processed > 0:
        return "partial"
    return "outstanding"


def _recompute_master_po_qty_processed(cur, po_id) -> float:
    """Set qty_processed = alokasi rencana + assign gudang sisa FG; kembalikan nilai baru."""
    cur.execute(
        "SELECT COALESCE(SUM(qty_proses), 0) AS tot FROM tbl_rencana_item_po WHERE po_id = %s",
        (po_id,),
    )
    tot = float((cur.fetchone() or {}).get("tot") or 0)
    cur.execute(
        "SELECT COALESCE(SUM(qty), 0) AS tot FROM tbl_stock_sisa_fg_assign WHERE po_id = %s",
        (po_id,),
    )
    tot += float((cur.fetchone() or {}).get("tot") or 0)
    cur.execute(
        "SELECT id, qty_order, status FROM tbl_master_po WHERE id = %s",
        (po_id,),
    )
    po = cur.fetchone()
    if not po:
        return tot
    qty_order = float(po.get("qty_order") or 0)
    new_status = _master_po_alloc_status(qty_order, tot, po.get("status"))
    cur.execute(
        "UPDATE tbl_master_po SET qty_processed=%s, status=%s WHERE id=%s",
        (tot, new_status, po_id),
    )
    return tot


def _recompute_all_master_po_qty_processed(cur) -> dict:
    """Perbaiki seluruh qty_processed dari Σ alokasi (repair data historis)."""
    cur.execute("SELECT id FROM tbl_master_po")
    ids = [int(r["id"]) for r in (cur.fetchall() or []) if r.get("id") is not None]
    fixed = 0
    for po_id in ids:
        _recompute_master_po_qty_processed(cur, po_id)
        fixed += 1
    return {"ok": True, "recomputed": fixed}


def _release_item_po_selections(cur, item_id):
    """Hapus link alokasi item lalu recompute qty_processed master PO terdampak."""
    cur.execute(
        "SELECT DISTINCT po_id FROM tbl_rencana_item_po WHERE item_id = %s",
        (item_id,),
    )
    po_ids = [int(r["po_id"]) for r in (cur.fetchall() or []) if r.get("po_id") is not None]
    cur.execute("DELETE FROM tbl_rencana_item_po WHERE item_id = %s", (item_id,))
    for po_id in po_ids:
        _recompute_master_po_qty_processed(cur, po_id)


def _save_item_po_selections(cur, item_id, po_data):
    """Tambah alokasi PO ke item. Cap: qty <= order − Σ alokasi lain (via qty_processed)."""
    for entry in po_data:
        po_id = entry.get("po_id")
        qty = float(entry.get("qty") or 0)
        if not po_id or qty <= 0:
            continue
        po_id = int(po_id)
        # Pastikan angka master selaras sebelum cek sisa.
        _recompute_master_po_qty_processed(cur, po_id)
        cur.execute("SELECT * FROM tbl_master_po WHERE id = %s", (po_id,))
        po = cur.fetchone()
        if not po:
            raise ValueError(f"PO #{po_id} tidak ditemukan")
        status = (po.get("status") or "").strip()
        if status == "cancelled":
            raise ValueError(
                f"PO {po.get('no_po') or po_id} tidak dapat dialokasi (status=cancelled)"
            )
        qty_order = float(po.get("qty_order") or 0)
        qty_processed = float(po.get("qty_processed") or 0)
        qty_outstanding = qty_order - qty_processed
        if qty > qty_outstanding + 1e-9:
            raise ValueError(
                f"Qty {qty} melebihi sisa alokasi {qty_outstanding} "
                f"untuk PO {po.get('no_po') or po_id}"
            )
        cur.execute(
            "INSERT INTO tbl_rencana_item_po (item_id, po_id, qty_outstanding, qty_proses) "
            "VALUES (%s, %s, %s, %s)",
            (item_id, po_id, qty_outstanding, qty),
        )
        _recompute_master_po_qty_processed(cur, po_id)


def _replace_item_po_selections(cur, item_id, po_data):
    """Ganti alokasi PO item: release + recompute dulu, lalu tulis ulang."""
    _release_item_po_selections(cur, item_id)
    _save_item_po_selections(cur, item_id, po_data)


def _consume_yl_stock(
    cur,
    kode_palet: str,
    kode_yl: str,
    qty: float,
    tanggal=None,
    keterangan: str | None = None,
) -> float:
    """Kurangi stok YL + catat movement OUT. Kembalikan qty yang di-consume."""
    kode_palet = (kode_palet or "").strip()
    kode_yl = (kode_yl or "").strip()
    qty_out = float(qty or 0)
    if not kode_palet or not kode_yl:
        raise ValueError("kode_palet dan kode_yl wajib untuk consume stok")
    if qty_out <= 0:
        return 0.0
    cur.execute(
        "SELECT id, qty, thickness, warna FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
        (kode_palet, kode_yl),
    )
    row = cur.fetchone()
    if not row:
        raise ValueError(f"YL {kode_yl} tidak ada di stok palet {kode_palet}")
    stock = float(row.get("qty") or 0)
    if qty_out > stock + 1e-9:
        raise ValueError(
            f"Qty ukur {qty_out} melebihi stok YL {kode_yl} ({stock}) di palet {kode_palet}"
        )
    when = tanggal or date.today().isoformat()
    note = (keterangan or "").strip() or None
    cur.execute(
        "INSERT INTO tbl_yl_movement (kode_yl, kode_palet, direction, thickness, warna, qty, tanggal, keterangan) "
        "VALUES (%s,%s,'OUT',%s,%s,%s,%s,%s)",
        (
            kode_yl,
            kode_palet,
            row.get("thickness") or "",
            row.get("warna") or "",
            qty_out,
            when,
            note,
        ),
    )
    sisa = stock - qty_out
    if sisa <= 1e-9:
        cur.execute("DELETE FROM tbl_yl WHERE id=%s", (row["id"],))
    else:
        cur.execute("UPDATE tbl_yl SET qty=%s WHERE id=%s", (sisa, row["id"]))
    return qty_out


def _yl_spek_from_history(cur, kode_palet: str, kode_yl: str) -> tuple[str, str]:
    """Ambil thickness/warna terakhir dari movement (setelah OUT full, baris tbl_yl bisa hilang)."""
    cur.execute(
        "SELECT thickness, warna FROM tbl_yl_movement "
        "WHERE kode_palet=%s AND kode_yl=%s "
        "ORDER BY id DESC LIMIT 1",
        (kode_palet, kode_yl),
    )
    hist = cur.fetchone() or {}
    return (str(hist.get("thickness") or "").strip(), str(hist.get("warna") or "").strip())


def _return_yl_to_palet(
    cur,
    kode_palet,
    kode_yl,
    qty,
    *,
    keterangan=None,
    tanggal=None,
    thickness=None,
    warna=None,
) -> float:
    """Tambah/merge qty sisa kembali ke tbl_yl (IN) — lot digabung ke barcode YL yang sama."""
    kode_palet = (kode_palet or "").strip()
    kode_yl = (kode_yl or "").strip()
    qty_in = float(qty or 0)
    if not kode_palet or not kode_yl or qty_in <= 1e-9:
        return 0.0
    cur.execute(
        "SELECT id, qty, thickness, warna FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
        (kode_palet, kode_yl),
    )
    row = cur.fetchone()
    thickness = (
        str(thickness).strip()
        if thickness is not None
        else str((row or {}).get("thickness") or "").strip()
    )
    warna = (
        str(warna).strip() if warna is not None else str((row or {}).get("warna") or "").strip()
    )
    if not thickness and not warna:
        thickness, warna = _yl_spek_from_history(cur, kode_palet, kode_yl)
    when = tanggal or date.today().isoformat()
    note = (keterangan or "").strip() or None
    cur.execute(
        "INSERT INTO tbl_yl_movement (kode_yl, kode_palet, direction, thickness, warna, qty, tanggal, keterangan) "
        "VALUES (%s,%s,'IN',%s,%s,%s,%s,%s)",
        (kode_yl, kode_palet, thickness, warna, qty_in, when, note),
    )
    if row:
        cur.execute(
            "UPDATE tbl_yl SET qty=%s WHERE id=%s",
            (float(row.get("qty") or 0) + qty_in, row["id"]),
        )
    else:
        cur.execute(
            "INSERT INTO tbl_yl (kode_yl, kode_palet, thickness, warna, qty) "
            "VALUES (%s,%s,%s,%s,%s)",
            (kode_yl, kode_palet, thickness, warna, qty_in),
        )
    return qty_in


def _consume_yl_for_ky_session(cur, ky, persiapan=None) -> float:
    """Consume stok YL sesuai actual_qty sesi KY (idempotent via yl_consumed).

    Jika ada sisa alokasi (target > actual) dan bukan tidak_ada_sisa:
    OUT target lalu IN kembali (target-actual) agar sisa merge ke lot YL/palet.
    Net stok = −actual (sama seperti hanya OUT actual), dengan jejak IN/OUT eksplisit.
    """
    if not ky:
        raise ValueError("KY tidak ditemukan")
    if int(ky.get("gudang_mod_id") or 0):
        actual = float(ky.get("actual_qty") or 0)
        if int(ky.get("yl_consumed") or 0) == 1:
            return float(ky.get("qty_consumed") or 0)
        cur.execute(
            "UPDATE tbl_persiapan_ky SET yl_consumed=1, qty_consumed=%s WHERE id=%s",
            (actual, ky["id"]),
        )
        return actual
    if int(ky.get("yl_consumed") or 0) == 1:
        return float(ky.get("qty_consumed") or 0)
    actual = float(ky.get("actual_qty") or 0)
    target = float(ky.get("target_qty") or 0)
    if actual <= 0:
        raise ValueError("KY belum punya ukur (actual_qty=0); tambah ukur sebelum selesai")
    kode_yl = (ky.get("kode_yl") or "").strip()
    if not kode_yl:
        raise ValueError("KY tanpa kode YL tidak dapat mengurangi stok")
    kode_palet = ky.get("kode_palet")
    kode_wip = ((persiapan or {}).get("kode_wip") or "").strip()
    wip_ref = f" — WIP {kode_wip}" if kode_wip else ""
    tidak_ada_sisa = int(ky.get("tidak_ada_sisa") or 0) == 1
    cur.execute(
        "SELECT qty, thickness, warna FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
        (kode_palet, kode_yl),
    )
    stock_row = cur.fetchone()
    stock = float((stock_row or {}).get("qty") or 0)
    yl_thickness = str((stock_row or {}).get("thickness") or "").strip()
    yl_warna = str((stock_row or {}).get("warna") or "").strip()
    out_qty = actual
    return_sisa = False
    if not tidak_ada_sisa and target > actual + 1e-9 and stock + 1e-9 >= target:
        out_qty = target
        return_sisa = True
    consumed = _consume_yl_stock(
        cur,
        kode_palet,
        kode_yl,
        out_qty,
        keterangan=f"Keluar proses persiapan{wip_ref}",
    )
    total_consumed = consumed
    if tidak_ada_sisa:
        cur.execute(
            "SELECT qty FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
            (kode_palet, kode_yl),
        )
        remain_row = cur.fetchone()
        remainder = float((remain_row or {}).get("qty") or 0)
        if remainder > 1e-9:
            total_consumed += _consume_yl_stock(
                cur,
                kode_palet,
                kode_yl,
                remainder,
                keterangan=f"Adjustment tidak ada sisa{wip_ref}",
            )
    elif return_sisa:
        sisa_back = target - actual
        _return_yl_to_palet(
            cur,
            kode_palet,
            kode_yl,
            sisa_back,
            keterangan=f"Sisa KY dikembalikan ke palet{wip_ref}",
            thickness=yl_thickness or None,
            warna=yl_warna or None,
        )
        total_consumed = actual
    cur.execute(
        "UPDATE tbl_persiapan_ky SET yl_consumed=1, qty_consumed=%s WHERE id=%s",
        (total_consumed, ky["id"]),
    )
    return total_consumed


def _ensure_customer_id(cur, nama, erp_customer_id=None):
    """Return ERP customers.id; display name di _ensure_customer_id.last_name."""
    from erp_customers import ensure_customer_id

    cid, display = ensure_customer_id(nama, erp_customer_id=erp_customer_id)
    _ensure_customer_id.last_name = display
    return cid




# ==================== HTML UI retired → Vue SPA ====================
# Templates live removed; keep bookmarks working via _redirect_mrp_ui.


@app.route("/")
def index():
    return _redirect_mrp_ui("/admin/mrp/palet")


@app.route("/palet", methods=["GET", "POST"])
@app.route("/palet/<path:_rest>", methods=["GET", "POST"])
@app.route("/yl", methods=["GET", "POST"])
@app.route("/lot")
def redirect_palet(_rest=None):
    return _redirect_mrp_ui("/admin/mrp/palet")


@app.route("/rencana-produksi", methods=["GET", "POST"])
@app.route("/rencana-produksi/<path:_rest>", methods=["GET", "POST"])
def redirect_rencana(_rest=None):
    return _redirect_mrp_ui("/admin/mrp/rencana-produksi")


@app.route("/proses", methods=["GET", "POST"])
def proses():
    return _redirect_mrp_ui("/admin/mrp/proses")


@app.route("/proses/<int:persiapan_id>", methods=["GET", "POST"])
@app.route("/proses/<int:persiapan_id>/label")
def proses_detail(persiapan_id):
    return _redirect_mrp_ui(f"/admin/mrp/proses/{int(persiapan_id)}")


@app.route("/lab", methods=["GET", "POST"])
def lab():
    return _redirect_mrp_ui("/admin/mrp/lab")


@app.route("/usage")
@app.route("/usage-color", methods=["GET", "POST"])
@app.route("/usage-rp", methods=["GET", "POST"])
@app.route("/usage-material-lain", methods=["GET", "POST"])
def redirect_usage():
    return _redirect_mrp_ui("/admin/mrp/usage")


@app.route("/packing", methods=["GET", "POST"])
@app.route("/packing/history")
def redirect_packing_list():
    return _redirect_mrp_ui("/admin/mrp/packing")


@app.route("/packing/<int:packing_id>", methods=["GET", "POST"])
@app.route("/packing/<int:packing_id>/print")
def redirect_packing_detail(packing_id):
    return _redirect_mrp_ui(f"/admin/mrp/packing/{int(packing_id)}")


@app.route("/stok-kimia", methods=["GET", "POST"])
def redirect_stok_kimia():
    return _redirect_mrp_ui("/admin/mrp/stok-kimia")


@app.route("/stok-rp", methods=["GET", "POST"])
def redirect_stok_rp():
    return _redirect_mrp_ui("/admin/mrp/stok-rp")


@app.route("/stok-material-lain", methods=["GET", "POST"])
def redirect_stok_material_lain():
    return _redirect_mrp_ui("/admin/mrp/stok-material-lain")


@app.route("/report_packing")
def redirect_report_packing():
    return _redirect_mrp_ui("/admin/mrp/reports/packing")


@app.route("/report_persiapan")
def redirect_report_persiapan():
    return _redirect_mrp_ui("/admin/mrp/reports/persiapan")


@app.route("/report_selisih_wip")
def redirect_report_selisih_wip():
    return _redirect_mrp_ui("/admin/mrp/reports/selisih-wip")


@app.route("/master/kulit", methods=["GET", "POST"])
def redirect_master_kulit():
    return _redirect_mrp_ui("/admin/mrp/masters/kulit")


@app.route("/master/rp", methods=["GET", "POST"])
def redirect_master_rp():
    return _redirect_mrp_ui("/admin/mrp/masters/rp")


@app.route("/master/kimia", methods=["GET", "POST"])
def redirect_master_kimia():
    return _redirect_mrp_ui("/admin/mrp/masters/kimia")


@app.route("/master/treatment", methods=["GET", "POST"])
def redirect_master_treatment():
    return _redirect_mrp_ui("/admin/mrp/masters/treatment")


@app.route("/master/erp")
def redirect_master_erp():
    return _redirect_mrp_ui("/admin/mrp/masters/erp")


@app.route("/master/material-lain", methods=["GET", "POST"])
def redirect_master_material_lain():
    return _redirect_mrp_ui("/admin/mrp/masters/material-lain")


@app.route("/gudang-fg", methods=["GET", "POST"])
@app.route("/gudang-fg/<int:_fg_id>")
def redirect_gudang_fg(_fg_id=None):
    return _redirect_mrp_ui("/admin/mrp/gudang-fg")


@app.route("/checkpoint")
def checkpoint():
    return _redirect_mrp_ui("/admin/mrp/checkpoint")


@app.route("/init-db")
def init_db_route():
    from init_db import main
    try:
        main()
    except Exception:
        pass
    return _redirect_mrp_ui("/admin/mrp/palet")


from api_routes import api as mrp_api_blueprint

app.register_blueprint(mrp_api_blueprint)


@app.route("/admin")
@app.route("/admin/<path:subpath>")
def redirect_admin_to_vue(subpath=""):
    """UI Vue ada di WEB_PORT (8080), bukan di MRP Flask (5010)."""
    web_port = os.getenv("WEB_PORT", "8080")
    host = (request.host or "").split(":")[0] or "127.0.0.1"
    target = f"http://{host}:{web_port}/admin"
    if subpath:
        target = f"{target}/{subpath}"
    qs = request.query_string.decode()
    if qs:
        target = f"{target}?{qs}"
    return redirect(target, code=302)


if __name__ == "__main__":
    port = int(os.getenv("MRP_PORT", "5010"))
    debug = os.getenv("MRP_DEBUG", "0") == "1"
    app.run(debug=debug, port=port, host="0.0.0.0")
