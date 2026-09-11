from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, date, timedelta
import mysql.connector
import json
import os

from db import get_db_connection

app = Flask(__name__)
app.secret_key = os.getenv("MRP_SECRET_KEY", "change-me-dev-only")


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


_RENCANA_SCHEMA_READY = False
_EXTENDED_SCHEMA_READY = False


def ensure_rencana_tables(cur):
    global _RENCANA_SCHEMA_READY
    if _RENCANA_SCHEMA_READY:
        return
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
    _RENCANA_SCHEMA_READY = True


def ensure_extended_tables(cur):
    global _EXTENDED_SCHEMA_READY
    if _EXTENDED_SCHEMA_READY:
        return
    # ERP-only catalogs: jangan CREATE master_erp / master_material_lain.
    try:
        from lot_erp_columns import ensure_lot_erp_columns
        ensure_lot_erp_columns(cur)
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
    item_cols = _col_names(cur, "tbl_rencana_item")
    if "backer" not in item_cols:
        cur.execute("ALTER TABLE tbl_rencana_item ADD COLUMN backer VARCHAR(100) DEFAULT NULL")
    if "kode_barcode" not in item_cols:
        cur.execute("ALTER TABLE tbl_rencana_item ADD COLUMN kode_barcode VARCHAR(50) DEFAULT NULL")
    kimia_in_cols = _col_names(cur, "tbl_stok_kimia_in")
    if "jumlah_kemasan" not in kimia_in_cols:
        cur.execute("ALTER TABLE tbl_stok_kimia_in ADD COLUMN jumlah_kemasan INT DEFAULT NULL")
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
    pers_cols = _col_names(cur, "tbl_persiapan_kulit")
    if "rencana_item_id" not in pers_cols:
        cur.execute("ALTER TABLE tbl_persiapan_kulit ADD COLUMN rencana_item_id INT DEFAULT NULL")
    if pers_cols and "checkpoint_status" not in pers_cols:
        cur.execute(
            "ALTER TABLE tbl_persiapan_kulit ADD COLUMN checkpoint_status VARCHAR(100) DEFAULT NULL"
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
    idx_rows = []
    try:
        cur.execute("SHOW INDEX FROM tbl_master_po")
        raw_idx = cur.fetchall() or []
        idx_rows = []
        for r in raw_idx:
            if isinstance(r, dict):
                col = r.get("Column_name") or r.get("column_name")
                non_unique = r.get("Non_unique")
            else:
                col = r[4] if len(r) > 4 else None
                non_unique = r[1] if len(r) > 1 else None
            if col == "source_detail_id":
                idx_rows.append({"Non_unique": non_unique})
    except mysql.connector.Error:
        idx_rows = []
    has_unique = False
    for ix in idx_rows:
        if ix.get("Non_unique") == 0:
            has_unique = True
            break
    if not has_unique:
        try:
            cur.execute(
                "SELECT source_detail_id FROM tbl_master_po "
                "WHERE source_detail_id IS NOT NULL "
                "GROUP BY source_detail_id HAVING COUNT(*) > 1"
            )
            dup_sids = [
                r["source_detail_id"] if isinstance(r, dict) else r[0]
                for r in (cur.fetchall() or [])
            ]
            for sid in dup_sids:
                cur.execute(
                    "SELECT id FROM tbl_master_po WHERE source_detail_id=%s "
                    "ORDER BY qty_processed DESC, id ASC",
                    (sid,),
                )
                rows = cur.fetchall() or []
                for extra in rows[1:]:
                    extra_id = extra["id"] if isinstance(extra, dict) else extra[0]
                    cur.execute(
                        "UPDATE tbl_master_po SET status='cancelled', source_detail_id=NULL "
                        "WHERE id=%s",
                        (extra_id,),
                    )
            cur.execute(
                "CREATE UNIQUE INDEX uq_master_po_source_detail ON tbl_master_po (source_detail_id)"
            )
        except mysql.connector.Error:
            pass
    try:
        cur.execute("DROP TABLE IF EXISTS tbl_rencana_produksi_detail")
    except mysql.connector.Error:
        pass
    if "qty_balance_erp" not in po_cols_ext:
        cur.execute(
            "ALTER TABLE tbl_master_po ADD COLUMN qty_balance_erp DECIMAL(12,2) DEFAULT NULL"
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
    _EXTENDED_SCHEMA_READY = True


def _make_rpi_barcode(thickness, emboss, color):
    def short(val):
        if not val:
            return "NA"
        return "".join(c for c in val.upper() if c.isalnum())[:6]
    return f"RPI-{short(thickness)}-{short(emboss)}-{short(color)}"


def ensure_master_treatment(cur):
    cur.execute(
        "CREATE TABLE IF NOT EXISTS tbl_master_treatment ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "jenis ENUM('PU','Suede') NOT NULL DEFAULT 'PU', "
        "nama_treatment VARCHAR(100) NOT NULL, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "UNIQUE KEY uk_nama_treatment (nama_treatment))"
    )
    cols = _col_names(cur, "tbl_master_treatment")
    if "created_at" not in cols:
        cur.execute(
            "ALTER TABLE tbl_master_treatment ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
        )
    # Seed realistis PU / Suede (nama unik karena UNIQUE pada nama_treatment).
    seeds = (
        ("PU", "PU - Degrease"),
        ("PU", "PU - Base Coat"),
        ("PU", "PU - Color Coat"),
        ("PU", "PU - Top Coat"),
        ("PU", "PU - Emboss / Press"),
        ("Suede", "Suede - Buffing"),
        ("Suede", "Suede - Dyeing"),
        ("Suede", "Suede - Softener"),
        ("Suede", "Suede - Finishing Spray"),
    )
    for jenis, nama in seeds:
        cur.execute("SELECT id FROM tbl_master_treatment WHERE nama_treatment = %s", (nama,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO tbl_master_treatment (jenis, nama_treatment) VALUES (%s, %s)",
                (jenis, nama),
            )


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


@app.before_request
def _retire_flask_html_ui():
    path = request.path or "/"
    if path.startswith("/api/") or path.startswith("/static"):
        return None
    if path in ("/health", "/init-db"):
        return None
    return (
        "<!doctype html><meta charset='utf-8'><title>MRP UI dipindah</title>"
        "<p>Antarmuka shopfloor Flask sudah dinonaktifkan. "
        "Buka ERP Vue: "
        "<a href='http://127.0.0.1:8080/admin/mrp/rencana-produksi'>"
        "http://127.0.0.1:8080/admin/mrp/rencana-produksi</a>.</p>",
        410,
        {"Content-Type": "text/html; charset=utf-8"},
    )


@app.route("/")
def index():
    return redirect(url_for("palet"))


# ==================== 1. PALET IN/OUT (KY) ====================
@app.route("/palet", methods=["GET", "POST"])
def palet():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")
        kode_palet = request.form.get("kode_palet", "").strip()
        tanggal = request.form.get("tanggal") or date.today().isoformat()
        keterangan = request.form.get("keterangan", "")

        if action == "in":
            cur.execute(
                "INSERT INTO tbl_palet_movement (kode_palet, direction, tanggal, keterangan) VALUES (%s,'IN',%s,%s)",
                (kode_palet, tanggal, keterangan),
            )
            yl_list = zip(
                request.form.getlist("kode_yl[]"),
                request.form.getlist("thickness[]"),
                request.form.getlist("warna[]"),
                request.form.getlist("qty[]"),
            )
            for kode_yl, thickness, warna, qty in yl_list:
                if kode_yl.strip():
                    cur.execute(
                        "INSERT INTO tbl_yl (kode_yl, kode_palet, thickness, warna, qty) "
                        "VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE thickness=%s, warna=%s, qty=%s",
                        (kode_yl.strip(), kode_palet, thickness, warna, qty or 0, thickness, warna, qty or 0),
                    )
            flash(f"Palet {kode_palet} berhasil IN.", "success")
        conn.commit()

    cur.execute(
        "SELECT m.*, (SELECT COUNT(*) FROM tbl_yl y WHERE y.kode_palet = m.kode_palet) AS jml_yl "
        "FROM tbl_palet_movement m ORDER BY m.created_at DESC LIMIT 100"
    )
    movements = cur.fetchall()
    from erp_raw_materials import list_materials

    kulit_list = [
        {
            "kode_kulit": r["code"],
            "nama_kulit": r["name"],
            "thickness": None,
            "warna": None,
        }
        for r in list_materials("kulit")
    ]
    cur.close()
    conn.close()
    return render_template(
        "palet.html", movements=movements, kulit_list=kulit_list, today=date.today().isoformat()
    )


@app.route("/palet/<kode_palet>/barang/<kode_yl>/barcode")
def palet_barang_barcode(kode_palet, kode_yl):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM tbl_yl WHERE kode_palet = %s AND kode_yl = %s",
        (kode_palet, kode_yl),
    )
    barang = cur.fetchone()
    cur.close()
    conn.close()
    if not barang:
        flash("Barang tidak ditemukan.", "danger")
        return redirect(url_for("palet_yl_detail", kode_palet=kode_palet))
    return render_template(
        "palet_barang_barcode.html", kode_palet=kode_palet, barang=barang
    )


@app.route("/palet/<kode_palet>/yl")
def palet_yl_detail(kode_palet):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_yl WHERE kode_palet = %s", (kode_palet,))
    yls = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("palet_yl_detail.html", kode_palet=kode_palet, yls=yls)


# ==================== 2. YL IN/OUT (Gudang Palet) ====================
@app.route("/yl", methods=["GET", "POST"])
def yl():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")
        kode_yl = request.form.get("kode_yl", "").strip()
        kode_palet = request.form.get("kode_palet", "").strip()
        thickness = request.form.get("thickness", "")
        warna = request.form.get("warna", "")
        qty = request.form.get("qty") or 0
        tanggal = request.form.get("tanggal") or date.today().isoformat()
        direction = "IN" if action == "in" else "OUT"

        cur.execute(
            "INSERT INTO tbl_yl_movement (kode_yl, kode_palet, direction, thickness, warna, qty, tanggal) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (kode_yl, kode_palet, direction, thickness, warna, qty, tanggal),
        )
        if direction == "IN":
            cur.execute(
                "INSERT INTO tbl_yl (kode_yl, kode_palet, thickness, warna, qty) "
                "VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE thickness=%s, warna=%s, qty=%s",
                (kode_yl, kode_palet, thickness, warna, qty, thickness, warna, qty),
            )
        conn.commit()
        flash(f"YL {kode_yl} berhasil {direction}.", "success")

    cur.execute("SELECT * FROM tbl_yl_movement ORDER BY created_at DESC LIMIT 100")
    movements = cur.fetchall()
    cur.execute("SELECT DISTINCT kode_palet FROM tbl_yl ORDER BY kode_palet")
    palets = [r["kode_palet"] for r in cur.fetchall()]
    cur.execute("SELECT kode_yl, kode_palet, thickness, warna, qty FROM tbl_yl ORDER BY kode_palet, kode_yl")
    yl_master = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("yl.html", movements=movements, palets=palets, yl_master=yl_master, today=date.today().isoformat())


@app.route("/api/yl-by-palet/<kode_palet>")
def api_yl_by_palet(kode_palet):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_yl WHERE kode_palet = %s", (kode_palet,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)


# ==================== 3. RENCANA PRODUKSI ====================
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
    """Set qty_processed = SUM(qty_proses) alokasi aktif; kembalikan nilai baru."""
    cur.execute(
        "SELECT COALESCE(SUM(qty_proses), 0) AS tot FROM tbl_rencana_item_po WHERE po_id = %s",
        (po_id,),
    )
    tot = float((cur.fetchone() or {}).get("tot") or 0)
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
        if po.get("source_detail_id") is None:
            raise ValueError(
                f"PO {po.get('no_po') or po_id} belum terhubung ke baris SO ERP (source_detail_id)"
            )
        qty_order = float(po.get("qty_order") or 0)
        qty_processed = float(po.get("qty_processed") or 0)
        plan_left = qty_order - qty_processed
        cap = plan_left
        if po.get("qty_balance_erp") is not None:
            try:
                cap = min(plan_left, max(0.0, float(po.get("qty_balance_erp") or 0)))
            except (TypeError, ValueError):
                cap = plan_left
        if qty > cap + 1e-9:
            raise ValueError(
                f"Qty {qty} melebihi sisa rencana/kirim {cap} "
                f"untuk PO {po.get('no_po') or po_id}"
            )
        qty_outstanding = plan_left
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


def _consume_yl_stock(cur, kode_palet: str, kode_yl: str, qty: float, tanggal=None) -> float:
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
    cur.execute(
        "INSERT INTO tbl_yl_movement (kode_yl, kode_palet, direction, thickness, warna, qty, tanggal) "
        "VALUES (%s,%s,'OUT',%s,%s,%s,%s)",
        (
            kode_yl,
            kode_palet,
            row.get("thickness") or "",
            row.get("warna") or "",
            qty_out,
            when,
        ),
    )
    sisa = stock - qty_out
    if sisa <= 1e-9:
        cur.execute("DELETE FROM tbl_yl WHERE id=%s", (row["id"],))
    else:
        cur.execute("UPDATE tbl_yl SET qty=%s WHERE id=%s", (sisa, row["id"]))
    return qty_out


def _consume_yl_for_ky_session(cur, ky) -> float:
    """Consume stok YL sesuai actual_qty sesi KY (idempotent via yl_consumed)."""
    if not ky:
        raise ValueError("KY tidak ditemukan")
    if int(ky.get("yl_consumed") or 0) == 1:
        return float(ky.get("qty_consumed") or 0)
    actual = float(ky.get("actual_qty") or 0)
    if actual <= 0:
        raise ValueError("KY belum punya ukur (actual_qty=0); tambah ukur sebelum selesai")
    kode_yl = (ky.get("kode_yl") or "").strip()
    if not kode_yl:
        raise ValueError("KY tanpa kode YL tidak dapat mengurangi stok")
    consumed = _consume_yl_stock(cur, ky.get("kode_palet"), kode_yl, actual)
    cur.execute(
        "UPDATE tbl_persiapan_ky SET yl_consumed=1, qty_consumed=%s WHERE id=%s",
        (consumed, ky["id"]),
    )
    return consumed


def _ensure_customer_id(cur, nama, erp_customer_id=None):
    """Return ERP customers.id; display name di _ensure_customer_id.last_name."""
    from erp_customers import ensure_customer_id

    cid, display = ensure_customer_id(nama, erp_customer_id=erp_customer_id)
    _ensure_customer_id.last_name = display
    return cid


@app.route("/api/erp/combination")
def api_erp_combination():
    from erp_master_items import combination_payload

    material_name = request.args.get("material_name", "").strip()
    color = request.args.get("color", "").strip()
    emboss = request.args.get("emboss", "").strip()
    thickness = request.args.get("thickness", "").strip()
    if not material_name or not color or not emboss:
        return jsonify({"error": "Material Name, Color, Emboss wajib"}), 400
    rows = combination_payload(
        material_name=material_name,
        color=color,
        emboss=emboss,
        thickness=thickness,
    )
    if not rows:
        return jsonify({"error": "Kombinasi tidak ditemukan di Master Item ERP"}), 404
    return jsonify({"options": rows, "source": "master_items"})


@app.route("/api/erp/fields")
def api_erp_fields():
    from erp_master_items import fields_payload

    return jsonify(
        fields_payload(
            thickness=request.args.get("thickness", "").strip(),
            material_name=request.args.get("material_name", "").strip(),
            color=request.args.get("color", "").strip(),
        )
    )


@app.route("/api/erp/options")
def api_erp_options():
    from erp_master_items import options_payload

    opts = options_payload()
    return jsonify(
        {
            "thicknesses": opts.get("thickness") or [],
            "colors": opts.get("colors") or [],
            "embosses": opts.get("emboss") or [],
            "source": "master_items",
        }
    )


@app.route("/api/rencana/po/by-combination")
def api_po_by_combination():
    from erp_master_items import _norm, _thickness_matches

    color = request.args.get("color", "").strip()
    emboss = request.args.get("emboss", "").strip()
    thickness = (request.args.get("thickness") or request.args.get("tebal") or "").strip()
    color_swatch = request.args.get("color_swatch", "").strip()
    if not color or not emboss:
        return jsonify({"error": "Color dan Emboss wajib"}), 400
    if thickness:
        mode = "spek"
    elif color_swatch:
        mode = "swatch"
    else:
        return jsonify({"error": "Thickness atau Color Swatch wajib"}), 400
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, no_po, no_so, customer, item_name, tebal, warna, emboss, color_swatch, "
        "sq_ft, qty_order, qty_processed, "
        "(qty_order - qty_processed) AS qty_outstanding "
        "FROM tbl_master_po "
        "WHERE warna = %s AND emboss = %s "
        "AND status IN ('outstanding','partial') "
        "ORDER BY no_po, item_name",
        (color, emboss),
    )
    items = cur.fetchall()
    if mode == "spek":
        items = [i for i in items if _thickness_matches(i.get("tebal"), thickness)]
    if color_swatch:
        sw_norm = _norm(color_swatch)
        items = [
            i
            for i in items
            if _norm(i.get("color_swatch") or "") == sw_norm
        ]
    for item in items:
        item["qty_order"] = float(item["qty_order"] or 0)
        item["qty_outstanding"] = float(item["qty_outstanding"] or 0)
    cur.close()
    conn.close()
    return jsonify(items)


@app.route("/api/rencana/po/by-customer/<int:customer_id>")
def api_po_by_customer(customer_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, no_po, no_so, item_name, sq_ft, qty_order, qty_processed, "
        "(qty_order - qty_processed) AS qty_outstanding "
        "FROM tbl_master_po "
        "WHERE customer_id = %s AND status IN ('outstanding','partial') "
        "ORDER BY no_po, item_name",
        (customer_id,),
    )
    items = cur.fetchall()
    for item in items:
        item["qty_order"] = float(item["qty_order"] or 0)
        item["qty_outstanding"] = float(item["qty_outstanding"] or 0)
    cur.close()
    conn.close()
    return jsonify(items)


@app.route("/rencana-produksi")
def rencana_produksi():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT id, nama_rencana, tanggal_rencana, date_created, status "
        "FROM tbl_rencana_produksi ORDER BY COALESCE(tanggal_rencana, date_created) DESC, id DESC"
    )
    rencana_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("rencana_produksi.html", rencana_list=rencana_list)


@app.route("/rencana-produksi/tambah", methods=["GET", "POST"])
def rencana_produksi_tambah():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    ensure_extended_tables(cur)
    conn.commit()

    if request.method == "POST":
        nama = request.form.get("nama_rencana", "").strip()
        tanggal = request.form.get("tanggal_rencana") or date.today().isoformat()
        items_json = request.form.get("items_json", "[]")

        if not nama:
            flash("Nama Rencana Produksi wajib diisi.", "danger")
        else:
            try:
                items = json.loads(items_json)
            except json.JSONDecodeError:
                items = []
            if not items:
                flash("Minimal satu item harus diisi.", "danger")
            else:
                kode_rencana = generate_code("RP")
                cur.execute(
                    "INSERT INTO tbl_rencana_produksi "
                    "(kode_rencana, kode_lot_wip, nama_rencana, tanggal_rencana, status) "
                    "VALUES (%s, NULL, %s, %s, 'draft')",
                    (kode_rencana, nama, tanggal),
                )
                rencana_id = cur.lastrowid
                saved = 0
                for idx, item in enumerate(items, 1):
                    thickness = (item.get("thickness") or "").strip()
                    material_name = (item.get("material_name") or "").strip()
                    color = (item.get("color") or "").strip()
                    emboss = (item.get("emboss") or "").strip()
                    customer_name = (item.get("customer") or "").strip()
                    color_swatch = (item.get("color_swatch") or "").strip()
                    if not all([thickness, material_name, color, emboss, customer_name, color_swatch]):
                        continue
                    from erp_master_items import lookup_backer

                    backer = item.get("backer") or lookup_backer(
                        material_name=material_name,
                        thickness=thickness,
                        color=color,
                        emboss=emboss,
                    )
                    customer_id = _ensure_customer_id(cur, customer_name)
                    customer_nama = getattr(_ensure_customer_id, "last_name", None) or customer_name
                    kode_item = generate_code("RPI")
                    kode_wip = generate_code("WIP")
                    cur.execute(
                        "INSERT INTO tbl_rencana_item "
                        "(rencana_id, kode_rencana_item, kode_lot_wip, customer_id, nama_customer, "
                        "material_name, thickness, color, emboss, color_swatch, backer, keterangan, urutan) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (
                            rencana_id, kode_item, kode_wip, customer_id, customer_nama,
                            material_name, thickness, color, emboss, color_swatch, backer,
                            (item.get("keterangan") or "").strip() or None, idx,
                        ),
                    )
                    item_id = cur.lastrowid
                    pos = item.get("pos") or []
                    if pos:
                        _save_item_po_selections(cur, item_id, pos)
                    saved += 1
                if not saved:
                    conn.rollback()
                    flash("Tidak ada item valid. Lengkapi Thickness, Material, Color, Emboss, Customer, dan Color Swatch.", "danger")
                else:
                    cur.execute(
                        "UPDATE tbl_rencana_produksi SET status='active' WHERE id=%s",
                        (rencana_id,),
                    )
                    conn.commit()
                    flash(f"Rencana Produksi '{nama}' berhasil dibuat.", "success")
                    return redirect(url_for("rencana_produksi_detail", rencana_id=rencana_id))

    from erp_master_items import options_payload

    opts = options_payload()
    cur.close()
    conn.close()
    return render_template(
        "rencana_produksi_tambah.html",
        erp_thickness=opts.get("thickness") or [],
        erp_materials=opts.get("materials") or [],
        erp_colors=opts.get("colors") or [],
        erp_emboss=opts.get("emboss") or [],
        erp_customers=opts.get("customers") or [],
        today=date.today().isoformat(),
    )


@app.route("/rencana-produksi/daftar-wip")
def rencana_produksi_daftar():
    return redirect(url_for("rencana_produksi"))


@app.route("/rencana-produksi/<int:rencana_id>")
def rencana_produksi_detail(rencana_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_rencana_produksi WHERE id = %s", (rencana_id,))
    rencana = cur.fetchone()
    if not rencana:
        flash("Rencana produksi tidak ditemukan.", "danger")
        return redirect(url_for("rencana_produksi"))
    cur.execute(
        "SELECT i.*, i.nama_customer, "
        "(SELECT COUNT(*) FROM tbl_rencana_item_po p WHERE p.item_id = i.id) AS jml_po, "
        "(SELECT COALESCE(SUM(p.qty_proses),0) FROM tbl_rencana_item_po p WHERE p.item_id = i.id) AS total_qty_so, "
        "(SELECT GROUP_CONCAT(DISTINCT COALESCE(NULLIF(po.no_so,''), po.no_po) ORDER BY po.no_po SEPARATOR ' / ') "
        " FROM tbl_rencana_item_po p JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = i.id) AS schedule_text "
        "FROM tbl_rencana_item i "
        ""
        "WHERE i.rencana_id = %s ORDER BY i.urutan, i.id",
        (rencana_id,),
    )
    items = cur.fetchall()
    for item in items:
        if item.get("total_qty_so") is not None:
            item["total_qty_so"] = float(item["total_qty_so"])
    cur.close()
    conn.close()
    return render_template("rencana_produksi_detail.html", rencana=rencana, items=items)


@app.route("/rencana-produksi/<int:rencana_id>/print")
def rencana_produksi_print(rencana_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_rencana_produksi WHERE id = %s", (rencana_id,))
    rencana = cur.fetchone()
    if not rencana:
        flash("Rencana produksi tidak ditemukan.", "danger")
        return redirect(url_for("rencana_produksi"))
    cur.execute(
        "SELECT i.*, i.nama_customer, "
        "(SELECT COALESCE(SUM(p.qty_proses),0) FROM tbl_rencana_item_po p WHERE p.item_id = i.id) AS total_qty_so, "
        "(SELECT GROUP_CONCAT(DISTINCT COALESCE(NULLIF(po.no_so,''), po.no_po) ORDER BY po.no_po SEPARATOR ' / ') "
        " FROM tbl_rencana_item_po p JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = i.id) AS schedule_text "
        "FROM tbl_rencana_item i "
        ""
        "WHERE i.rencana_id = %s ORDER BY i.urutan, i.id",
        (rencana_id,),
    )
    items = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("rencana_produksi_print.html", rencana=rencana, items=items)


@app.route("/rencana-produksi/item/<int:item_id>")
def rencana_item_detail(item_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT i.*, i.nama_customer, r.nama_rencana, r.tanggal_rencana, r.kode_rencana "
        "FROM tbl_rencana_item i "
        ""
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        "WHERE i.id = %s",
        (item_id,),
    )
    item = cur.fetchone()
    if not item:
        flash("Item rencana tidak ditemukan.", "danger")
        return redirect(url_for("rencana_produksi"))
    cur.execute(
        "SELECT p.*, po.no_po, po.no_so, po.item_name FROM tbl_rencana_item_po p "
        "JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = %s",
        (item_id,),
    )
    selected_po = cur.fetchall()
    cur.execute(
        "SELECT kl.* FROM tbl_kulit_lebih kl WHERE kl.rencana_item_id = %s ORDER BY kl.created_at DESC",
        (item_id,),
    )
    kulit_lebih = cur.fetchall()
    cur.close()
    conn.close()
    return render_template(
        "rencana_item_detail.html",
        item=item,
        selected_po=selected_po,
        kulit_lebih=kulit_lebih,
    )


@app.route("/rencana-produksi/item/<int:item_id>/barcode")
def rencana_item_barcode(item_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT i.*, i.nama_customer, r.nama_rencana "
        "FROM tbl_rencana_item i "
        ""
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        "WHERE i.id = %s",
        (item_id,),
    )
    item = cur.fetchone()
    cur.close()
    conn.close()
    if not item:
        flash("Item tidak ditemukan.", "danger")
        return redirect(url_for("rencana_produksi"))
    return render_template("rencana_item_barcode.html", item=item)


@app.route("/rencana-produksi/item/<int:item_id>/list-po", methods=["GET", "POST"])
def rencana_item_list_po(item_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    conn.commit()

    cur.execute(
        "SELECT i.*, i.nama_customer, r.nama_rencana, r.tanggal_rencana "
        "FROM tbl_rencana_item i "
        ""
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        "WHERE i.id = %s",
        (item_id,),
    )
    item = cur.fetchone()
    if not item:
        flash("Item rencana tidak ditemukan.", "danger")
        return redirect(url_for("rencana_produksi"))

    if request.method == "POST":
        po_ids = request.form.getlist("po_id[]")
        qty_list = request.form.getlist("qty[]")
        po_data = [{"po_id": pid, "qty": qty} for pid, qty in zip(po_ids, qty_list) if pid]
        if po_data:
            try:
                _replace_item_po_selections(cur, item_id, po_data)
            except ValueError as exc:
                conn.rollback()
                flash(str(exc), "danger")
                return redirect(url_for("rencana_item_list_po", item_id=item_id))
            cur.execute(
                "UPDATE tbl_rencana_produksi SET status = 'active' WHERE id = %s",
                (item["rencana_id"],),
            )
            conn.commit()
            flash("PO berhasil disimpan.", "success")
        else:
            flash("Pilih minimal satu PO outstanding.", "danger")
        return redirect(url_for("rencana_produksi_detail", rencana_id=item["rencana_id"]))

    cur.execute(
        "SELECT id, no_po, no_so, item_name, sq_ft, qty_order, qty_processed, "
        "(qty_order - qty_processed) AS qty_outstanding "
        "FROM tbl_master_po "
        "WHERE tebal = %s AND warna = %s AND emboss = %s "
        "AND status IN ('outstanding','partial') "
        "ORDER BY no_po, item_name",
        (item["thickness"], item["color"], item["emboss"]),
    )
    po_list = cur.fetchall()
    cur.execute(
        "SELECT p.*, po.no_po, po.item_name FROM tbl_rencana_item_po p "
        "JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = %s",
        (item_id,),
    )
    selected_po = cur.fetchall()
    cur.close()
    conn.close()
    return render_template(
        "rencana_item_list_po.html",
        item=item,
        po_list=po_list,
        selected_po=selected_po,
    )


# ==================== 4. PERSIAPAN KULIT ====================
@app.route("/api/proses/rencana-scan")
def api_proses_rencana_scan():
    kode = request.args.get("q", "").strip()
    if not kode:
        return jsonify({"error": "Kode kosong"}), 400
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT i.id, i.kode_rencana_item, i.kode_lot_wip, i.kode_kulit, i.thickness, i.color, "
        "i.emboss, i.color_swatch, r.nama_rencana, r.tanggal_rencana, "
        "i.nama_customer "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        ""
        "WHERE i.kode_rencana_item = %s AND r.status IN ('draft','active')",
        (kode,),
    )
    item = cur.fetchone()
    if not item:
        cur.close()
        conn.close()
        return jsonify({"error": "Rencana produksi tidak ditemukan"}), 404
    cur.execute(
        "SELECT po.no_po, po.item_name, p.qty_outstanding, p.qty_proses "
        "FROM tbl_rencana_item_po p "
        "JOIN tbl_master_po po ON po.id = p.po_id "
        "WHERE p.item_id = %s ORDER BY po.no_po",
        (item["id"],),
    )
    po_list = cur.fetchall()
    for po in po_list:
        for key in ("qty_outstanding", "qty_proses"):
            if po.get(key) is not None:
                po[key] = float(po[key])
    item["po_list"] = po_list
    cur.close()
    conn.close()
    if item.get("tanggal_rencana"):
        item["tanggal_rencana"] = item["tanggal_rencana"].isoformat()
    return jsonify(item)


@app.route("/proses", methods=["GET", "POST"])
def proses():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            item_id = request.form.get("rencana_item_id")
            kode_scan = request.form.get("kode_scan", "").strip()
            if not item_id and kode_scan:
                cur.execute(
                    "SELECT i.id FROM tbl_rencana_item i "
                    "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
                    "WHERE i.kode_rencana_item = %s "
                    "AND r.status IN ('draft','active')",
                    (kode_scan,),
                )
                row = cur.fetchone()
                item_id = row["id"] if row else None
            if not item_id:
                flash("Ketik / scan kode RPI terlebih dahulu.", "danger")
                return redirect(url_for("proses"))
            cur.execute(
                "SELECT i.*, r.kode_rencana FROM tbl_rencana_item i "
                "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id WHERE i.id = %s",
                (item_id,),
            )
            item = cur.fetchone()
            if not item:
                flash("Item rencana tidak ditemukan.", "danger")
                return redirect(url_for("proses"))
            cur.execute(
                "SELECT no_po FROM tbl_rencana_item_po p "
                "JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = %s LIMIT 1",
                (item_id,),
            )
            po_row = cur.fetchone()
            kode_proses = generate_code("PR")
            selected_treatments = request.form.getlist("treatment_list[]")
            treatment_list_str = ", ".join(selected_treatments)
            treatment_jenis = request.form.get("treatment_jenis", "PU")
            if treatment_jenis not in ("PU", "Suede"):
                flash("Pilih jenis PU atau SUEDE.", "danger")
                return redirect(url_for("proses"))
            for tname in selected_treatments:
                cur.execute(
                    "SELECT id FROM tbl_master_treatment WHERE nama_treatment = %s AND jenis = %s",
                    (tname, treatment_jenis),
                )
                if not cur.fetchone():
                    flash(f"Treatment '{tname}' tidak sesuai jenis {treatment_jenis}.", "danger")
                    return redirect(url_for("proses"))
            cur.execute(
                "INSERT INTO tbl_persiapan_kulit "
                "(kode_wip, kode_rencana, kode_proses, rencana_item_id, no_po, warna, tebal, emboss, treatment_jenis, treatment_list, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'draft')",
                (
                    item["kode_lot_wip"], item["kode_rencana_item"], kode_proses, item_id,
                    po_row["no_po"] if po_row else "",
                    item["color"], item["thickness"], item["emboss"],
                    treatment_jenis, treatment_list_str,
                ),
            )
            persiapan_id = cur.lastrowid
            conn.commit()
            flash(f"Persiapan Kulit {kode_proses} dibuat.", "success")
            return redirect(url_for("proses_detail", persiapan_id=persiapan_id))

        elif action == "update":
            pid = request.form.get("persiapan_id")
            cur.execute(
                "UPDATE tbl_persiapan_kulit SET treatment_jenis=%s, treatment_list=%s WHERE id=%s",
                (request.form.get("treatment_jenis"),
                 request.form.get("treatment_list"), pid),
            )
            conn.commit()

    cur.execute(
        "SELECT i.id, i.kode_rencana_item, i.kode_lot_wip, r.nama_rencana, i.nama_customer "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        ""
        "WHERE r.status IN ('draft','active') AND i.kode_lot_wip IS NOT NULL "
        "ORDER BY r.date_created DESC"
    )
    rencana_list = cur.fetchall()
    cur.execute("SELECT * FROM tbl_persiapan_kulit ORDER BY date_created DESC LIMIT 50")
    persiapan_list = cur.fetchall()
    ensure_master_treatment(cur)
    conn.commit()
    cur.execute("SELECT jenis, nama_treatment FROM tbl_master_treatment ORDER BY jenis, nama_treatment")
    treatments = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("proses.html", rencana_list=rencana_list, persiapan_list=persiapan_list, treatments=treatments)


@app.route("/proses/<int:persiapan_id>", methods=["GET", "POST"])
def proses_detail(persiapan_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    cur.execute("SELECT * FROM tbl_persiapan_kulit WHERE id = %s", (persiapan_id,))
    persiapan = cur.fetchone()
    if not persiapan:
        flash("Data tidak ditemukan.", "danger")
        return redirect(url_for("proses"))

    if request.method == "POST":
        action = request.form.get("action")
        status = (persiapan.get("status") or "").strip()

        try:
            if action == "start":
                if status not in ("draft", "started"):
                    flash(f"Tidak dapat Start dari status {status or '-'}", "danger")
                else:
                    cur.execute(
                        "UPDATE tbl_persiapan_kulit SET status='started' WHERE id=%s",
                        (persiapan_id,),
                    )
                    flash("Proses dimulai.", "success")

            elif action == "scan_ky":
                if status != "started":
                    flash("Mulai proses (Start) dulu sebelum KY/ukur.", "warning")
                else:
                    kode_palet = request.form.get("kode_palet", "").strip()
                    kode_yl = request.form.get("kode_yl", "").strip()
                    target_qty = float(request.form.get("target_qty") or 0)
                    cur.execute(
                        "SELECT id FROM tbl_persiapan_ky WHERE persiapan_id=%s AND status='active'",
                        (persiapan_id,),
                    )
                    if cur.fetchone():
                        flash("Selesaikan KY aktif terlebih dahulu.", "warning")
                    elif not kode_palet:
                        flash("Kode KY wajib diisi.", "danger")
                    elif not kode_yl:
                        flash("Kode YL wajib diisi.", "danger")
                    else:
                        cur.execute(
                            "SELECT id, qty FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
                            (kode_palet, kode_yl),
                        )
                        yl_row = cur.fetchone()
                        if not yl_row or float(yl_row.get("qty") or 0) <= 0:
                            flash("KY/YL tidak ada / stok kosong. Palet IN dulu.", "danger")
                        else:
                            cur.execute(
                                "INSERT INTO tbl_persiapan_ky "
                                "(persiapan_id, kode_palet, kode_yl, target_qty, status) "
                                "VALUES (%s,%s,%s,%s,'active')",
                                (persiapan_id, kode_palet, kode_yl, target_qty),
                            )
                            cur.execute(
                                "INSERT INTO tbl_persiapan_scan "
                                "(persiapan_id, kode_palet, kode_yl) VALUES (%s,%s,%s)",
                                (persiapan_id, kode_palet, kode_yl),
                            )
                            flash(f"KY {kode_palet} / YL {kode_yl} aktif.", "success")

            elif action == "add_ukur":
                if status != "started":
                    flash("Mulai proses (Start) dulu sebelum KY/ukur.", "warning")
                else:
                    ky_id = request.form.get("ky_id")
                    size_val = float(request.form.get("size_val") or 0)
                    if ky_id and size_val > 0:
                        cur.execute(
                            "INSERT INTO tbl_persiapan_ukur "
                            "(persiapan_id, ky_id, size_val) VALUES (%s,%s,%s)",
                            (persiapan_id, ky_id, size_val),
                        )
                        cur.execute(
                            "UPDATE tbl_persiapan_kulit SET total_size = total_size + %s WHERE id=%s",
                            (size_val, persiapan_id),
                        )
                        cur.execute(
                            "UPDATE tbl_persiapan_ky SET actual_qty = actual_qty + %s WHERE id=%s",
                            (size_val, ky_id),
                        )

            elif action == "selesai_ky":
                if status != "started":
                    flash("Mulai proses (Start) dulu sebelum KY/ukur.", "warning")
                else:
                    ky_id = request.form.get("ky_id")
                    cur.execute(
                        "SELECT * FROM tbl_persiapan_ky WHERE id=%s AND persiapan_id=%s",
                        (ky_id, persiapan_id),
                    )
                    ky = cur.fetchone()
                    if not ky or ky.get("status") != "active":
                        flash("KY aktif tidak ditemukan.", "danger")
                    else:
                        target = float(ky["target_qty"] or 0)
                        actual = float(ky["actual_qty"] or 0)
                        consumed = _consume_yl_for_ky_session(cur, ky)
                        selisih = actual - target
                        cur.execute(
                            "UPDATE tbl_persiapan_ky SET status='selesai' WHERE id=%s",
                            (ky_id,),
                        )
                        if persiapan.get("rencana_item_id") and selisih != 0:
                            cur.execute(
                                "INSERT INTO tbl_kulit_lebih "
                                "(rencana_item_id, persiapan_id, ky_id, kode_palet, kode_yl, "
                                "target_qty, actual_qty, selisih, keterangan) "
                                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                (
                                    persiapan["rencana_item_id"],
                                    persiapan_id,
                                    ky_id,
                                    ky["kode_palet"],
                                    ky["kode_yl"],
                                    target,
                                    actual,
                                    selisih,
                                    "Kurang" if selisih < 0 else "Lebih",
                                ),
                            )
                        flash(
                            f"KY selesai. Target: {target}, Aktual: {actual}, OUT: {consumed}",
                            "info",
                        )

            elif action == "scan":
                if status != "started":
                    flash("Mulai proses (Start) dulu sebelum KY/ukur.", "warning")
                else:
                    kode_palet = request.form.get("kode_palet", "").strip()
                    kode_yl = request.form.get("kode_yl", "").strip()
                    size_val = request.form.get("size_val")
                    cur.execute(
                        "INSERT INTO tbl_persiapan_scan "
                        "(persiapan_id, kode_palet, kode_yl) VALUES (%s,%s,%s)",
                        (persiapan_id, kode_palet, kode_yl),
                    )
                    if size_val:
                        cur.execute(
                            "INSERT INTO tbl_persiapan_ukur (persiapan_id, size_val) VALUES (%s,%s)",
                            (persiapan_id, size_val),
                        )
                        cur.execute(
                            "UPDATE tbl_persiapan_kulit SET total_size = total_size + %s WHERE id=%s",
                            (float(size_val), persiapan_id),
                        )

            elif action == "delete_ukur":
                if status != "started":
                    flash("Mulai proses (Start) dulu sebelum KY/ukur.", "warning")
                else:
                    ukur_id = request.form.get("ukur_id")
                    cur.execute(
                        "SELECT u.size_val, u.ky_id, k.status AS ky_status, k.yl_consumed "
                        "FROM tbl_persiapan_ukur u "
                        "LEFT JOIN tbl_persiapan_ky k ON k.id = u.ky_id "
                        "WHERE u.id=%s AND u.persiapan_id=%s",
                        (ukur_id, persiapan_id),
                    )
                    row = cur.fetchone()
                    if row and (
                        row.get("ky_status") == "selesai"
                        or int(row.get("yl_consumed") or 0) == 1
                    ):
                        flash("Tidak dapat hapus ukur KY yang sudah selesai.", "danger")
                    elif row:
                        cur.execute("DELETE FROM tbl_persiapan_ukur WHERE id=%s", (ukur_id,))
                        cur.execute(
                            "UPDATE tbl_persiapan_kulit "
                            "SET total_size = GREATEST(total_size - %s, 0) WHERE id=%s",
                            (row["size_val"], persiapan_id),
                        )
                        if row.get("ky_id"):
                            cur.execute(
                                "UPDATE tbl_persiapan_ky "
                                "SET actual_qty = GREATEST(actual_qty - %s, 0) WHERE id=%s",
                                (row["size_val"], row["ky_id"]),
                            )

            elif action == "save":
                if status in ("saved", "completed"):
                    flash("Persiapan sudah selesai / tersimpan.", "warning")
                elif status != "started":
                    flash("Start proses dulu sebelum Simpan.", "warning")
                else:
                    cur.execute(
                        "SELECT id FROM tbl_persiapan_ky "
                        "WHERE persiapan_id=%s AND status='active' LIMIT 1",
                        (persiapan_id,),
                    )
                    if cur.fetchone():
                        flash("Selesaikan KY aktif dulu sebelum Simpan.", "warning")
                    elif float(persiapan.get("total_size") or 0) <= 0:
                        flash("Belum ada ukur (total size=0).", "danger")
                    else:
                        cur.execute(
                            "UPDATE tbl_persiapan_kulit "
                            "SET status='completed', date_saved=NOW() WHERE id=%s",
                            (persiapan_id,),
                        )
                        flash("Persiapan selesai (completed). Label siap dicetak.", "success")

            elif action == "reprint":
                if status not in ("saved", "completed"):
                    flash("Reprint hanya setelah persiapan tersimpan/selesai.", "warning")
                else:
                    cur.execute(
                        "SELECT COALESCE(MAX(reprint_ke),0)+1 AS nxt "
                        "FROM tbl_persiapan_reprint WHERE persiapan_id=%s",
                        (persiapan_id,),
                    )
                    reprint_ke = cur.fetchone()["nxt"]
                    cur.execute(
                        "INSERT INTO tbl_persiapan_reprint (persiapan_id, reprint_ke) VALUES (%s,%s)",
                        (persiapan_id, reprint_ke),
                    )
                    flash(f"Reprint ke-{reprint_ke} dicatat.", "info")
        except ValueError as exc:
            conn.rollback()
            flash(str(exc), "danger")
            cur.close()
            conn.close()
            return redirect(url_for("proses_detail", persiapan_id=persiapan_id))

        conn.commit()
        return redirect(url_for("proses_detail", persiapan_id=persiapan_id))
    cur.execute("SELECT * FROM tbl_persiapan_kulit WHERE id = %s", (persiapan_id,))
    persiapan = cur.fetchone()
    cur.execute("SELECT * FROM tbl_persiapan_scan WHERE persiapan_id = %s ORDER BY created_at", (persiapan_id,))
    scans = cur.fetchall()
    cur.execute("SELECT * FROM tbl_persiapan_ukur WHERE persiapan_id = %s ORDER BY created_at", (persiapan_id,))
    ukurs = cur.fetchall()
    cur.execute("SELECT * FROM tbl_persiapan_reprint WHERE persiapan_id = %s ORDER BY reprint_ke", (persiapan_id,))
    reprints = cur.fetchall()
    cur.execute(
        "SELECT * FROM tbl_persiapan_ky WHERE persiapan_id = %s ORDER BY created_at",
        (persiapan_id,),
    )
    ky_sessions = cur.fetchall()
    cur.execute(
        "SELECT id FROM tbl_persiapan_ky WHERE persiapan_id=%s AND status='active' LIMIT 1",
        (persiapan_id,),
    )
    active_ky = cur.fetchone()
    cur.execute("SELECT jenis, nama_treatment FROM tbl_master_treatment ORDER BY jenis, nama_treatment")
    treatments = cur.fetchall()
    cur.close()
    conn.close()
    return render_template(
        "proses_detail.html",
        persiapan=persiapan,
        scans=scans,
        ukurs=ukurs,
        reprints=reprints,
        ky_sessions=ky_sessions,
        active_ky=active_ky,
        treatments=treatments,
    )


@app.route("/proses/<int:persiapan_id>/label")
def proses_label(persiapan_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_persiapan_kulit WHERE id = %s", (persiapan_id,))
    persiapan = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("proses_label.html", persiapan=persiapan)


# ==================== 5. LAB (Mixing Color) ====================
@app.route("/lab", methods=["GET", "POST"])
def lab():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_lab_tables(cur)
    ensure_rencana_tables(cur)
    conn.commit()

    if request.method == "POST":
        nama_lot_warna = request.form.get("nama_lot_warna", "").strip()
        rencana_item_id = request.form.get("rencana_item_id") or None
        kode_kimia_list = request.form.getlist("kode_kimia[]")
        resep_list = request.form.getlist("resep[]")
        satuan_list = request.form.getlist("satuan[]")
        qty_list = request.form.getlist("qty[]")
        remarks_list = request.form.getlist("remarks[]")

        if not nama_lot_warna:
            flash("Nama Lot Warna wajib diisi.", "danger")
        else:
            rows = [
                (kode_kimia, resep, satuan, qty, remarks)
                for kode_kimia, resep, satuan, qty, remarks in zip(
                    kode_kimia_list, resep_list, satuan_list, qty_list, remarks_list
                )
                if kode_kimia.strip()
            ]
            if not rows:
                flash("Minimal satu chemical harus diisi.", "danger")
            else:
                kode_lot_warna = generate_code("LW")
                cur.execute(
                    "INSERT INTO tbl_lab_lot (kode_lot_warna, nama_lot_warna, rencana_item_id) VALUES (%s, %s, %s)",
                    (kode_lot_warna, nama_lot_warna, rencana_item_id),
                )
                for kode_kimia, resep, satuan, qty, remarks in rows:
                    from erp_raw_materials import fetch_material_by_code

                    mat = fetch_material_by_code(kode_kimia.strip(), material_type="kimia")
                    cur.execute(
                        "INSERT INTO tbl_lab_lot_detail "
                        "(kode_lot_warna, kode_kimia, nama_kimia, resep, satuan, qty, remarks) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (
                            kode_lot_warna,
                            kode_kimia.strip(),
                            (mat["name"] if mat else kode_kimia.strip()),
                            resep.strip() or None,
                            satuan.strip() or (mat.get("unit") if mat else "kg") or "kg",
                            qty or 0,
                            remarks.strip() or None,
                        ),
                    )
                conn.commit()
                flash(f"Lot Warna {kode_lot_warna} berhasil dibuat.", "success")

    cur.execute(
        "SELECT l.kode_lot_warna, l.nama_lot_warna, l.status, l.date_created, l.rencana_item_id, "
        "d.kode_kimia, d.nama_kimia, d.resep, d.satuan, d.qty, d.remarks, "
        "ri.kode_rencana_item, rp.nama_rencana, rp.tanggal_rencana, ri.nama_customer "
        "FROM tbl_lab_lot l "
        "JOIN tbl_lab_lot_detail d ON d.kode_lot_warna = l.kode_lot_warna "
        "LEFT JOIN tbl_rencana_item ri ON ri.id = l.rencana_item_id "
        "LEFT JOIN tbl_rencana_produksi rp ON rp.id = ri.rencana_id "
        ""
        "ORDER BY COALESCE(rp.tanggal_rencana, l.date_created) DESC, l.kode_lot_warna, d.id DESC LIMIT 200"
    )
    lab_list = cur.fetchall()
    cur.execute(
        "SELECT ri.id, ri.kode_rencana_item, ri.kode_kulit, ri.color, ri.thickness, "
        "rp.nama_rencana, rp.tanggal_rencana, ri.nama_customer "
        "FROM tbl_rencana_item ri "
        "JOIN tbl_rencana_produksi rp ON rp.id = ri.rencana_id "
        ""
        "ORDER BY rp.tanggal_rencana DESC, ri.urutan"
    )
    rencana_items = cur.fetchall()
    from erp_raw_materials import list_materials

    kimia_list = [
        {
            "kode_kimia": r["code"],
            "nama_kimia": r["name"],
            "satuan": r.get("unit") or "kg",
        }
        for r in list_materials("kimia")
    ]
    cur.execute("SELECT nama_resep FROM master_resep ORDER BY nama_resep")
    reseps = [r["nama_resep"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template(
        "lab.html", lab_list=lab_list, kimia_list=kimia_list, reseps=reseps, rencana_items=rencana_items
    )


# ==================== 6. USAGE COLOR ====================
@app.route("/api/usage-color/lot-scan")
def api_usage_color_lot_scan():
    kode = request.args.get("q", "").strip()
    if not kode:
        return jsonify({"error": "Kode kosong"}), 400
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT l.kode_lot_warna, l.nama_lot_warna, l.status, "
        "(SELECT COALESCE(SUM(d.qty), 0) FROM tbl_lab_lot_detail d "
        "WHERE d.kode_lot_warna = l.kode_lot_warna) AS qty_pembuatan "
        "FROM tbl_lab_lot l WHERE l.kode_lot_warna = %s",
        (kode,),
    )
    lot = cur.fetchone()
    cur.close()
    conn.close()
    if not lot:
        return jsonify({"error": "Kode lot warna tidak ditemukan"}), 404
    if lot.get("status") != "active":
        return jsonify({"error": "Lot warna tidak aktif"}), 400
    return jsonify(lot)


@app.route("/usage-color", methods=["GET", "POST"])
def usage_color():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        kode_wip = request.form.get("kode_wip", "").strip()
        kode_lot_warna = request.form.get("kode_lot_warna", "").strip()
        qty_digunakan = float(request.form.get("qty_digunakan") or 0)

        cur.execute("SELECT * FROM tbl_lab_lot WHERE kode_lot_warna = %s", (kode_lot_warna,))
        lot = cur.fetchone()
        if not lot:
            flash("Kode lot warna tidak ditemukan.", "danger")
        elif lot.get("status") != "active":
            flash("Lot warna tidak aktif.", "danger")
        else:
            cur.execute(
                "SELECT COALESCE(SUM(qty), 0) AS total_qty FROM tbl_lab_lot_detail WHERE kode_lot_warna = %s",
                (kode_lot_warna,),
            )
            total = cur.fetchone()
            cur.execute(
                "INSERT INTO tbl_usage_color (kode_wip, kode_lot_warna, nama_warna, qty_pembuatan, qty_digunakan) "
                "VALUES (%s,%s,%s,%s,%s)",
                (kode_wip, kode_lot_warna, lot["nama_lot_warna"], total["total_qty"], qty_digunakan),
            )
            conn.commit()
            flash("Usage Color berhasil disimpan.", "success")

    cur.execute("SELECT * FROM tbl_usage_color ORDER BY date_created DESC LIMIT 100")
    usage_list = cur.fetchall()
    cur.execute("SELECT DISTINCT kode_lot_wip AS kode_wip FROM tbl_rencana_produksi ORDER BY kode_lot_wip DESC")
    wip_list = [r["kode_wip"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template("usage_color.html", usage_list=usage_list, wip_list=wip_list)


# ==================== 7. USAGE RP (Laminating) ====================
@app.route("/api/usage-rp/rp-scan")
def api_usage_rp_rp_scan():
    from erp_raw_materials import fetch_material_by_code

    kode = request.args.get("q", "").strip()
    if not kode:
        return jsonify({"error": "Kode kosong"}), 400
    mat = fetch_material_by_code(kode, material_type="rp")
    if not mat:
        return jsonify({"error": "Jenis RP tidak ditemukan"}), 404
    return jsonify(
        {
            "kode_rp": mat["code"],
            "nama_jenis": mat["name"],
            "satuan": mat.get("unit") or "meter",
        }
    )


@app.route("/usage-rp", methods=["GET", "POST"])
def usage_rp():
    from erp_raw_materials import fetch_material_by_code

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        kode_wip = request.form.get("kode_wip", "").strip()
        jenis_scan = request.form.get("jenis_rp", "").strip()
        mat = fetch_material_by_code(jenis_scan, material_type="rp")
        if not mat:
            flash("Jenis RP tidak ditemukan.", "danger")
        else:
            cur.execute(
                "INSERT INTO tbl_usage_rp (kode_wip, jenis_rp, qty_used, satuan) VALUES (%s,%s,%s,%s)",
                (
                    kode_wip,
                    mat["name"],
                    request.form.get("qty_used") or 0,
                    request.form.get("satuan") or mat.get("unit") or "meter",
                ),
            )
            conn.commit()
            flash("Usage RP berhasil disimpan.", "success")

    cur.execute("SELECT * FROM tbl_usage_rp ORDER BY date_created DESC LIMIT 100")
    usage_list = cur.fetchall()
    cur.execute("SELECT DISTINCT kode_lot_wip AS kode_wip FROM tbl_rencana_produksi ORDER BY kode_lot_wip DESC")
    wip_list = [r["kode_wip"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template("usage_rp.html", usage_list=usage_list, wip_list=wip_list)


@app.route("/usage")
def usage():
    return redirect(url_for("usage_color"))


# ==================== 8. PACKING ====================
@app.route("/packing", methods=["GET", "POST"])
def packing():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "scan_wip":
            kode_wip = request.form.get("kode_wip", "").strip()
            cur.execute(
                "SELECT pk.* FROM tbl_persiapan_kulit pk "
                "WHERE pk.kode_wip = %s AND pk.status IN ('saved','completed')",
                (kode_wip,),
            )
            wip_data = cur.fetchall()
            cur.execute(
                "SELECT i.id AS item_id, po.no_po, po.no_so, po.item_name, po.customer, "
                "p.qty_proses AS qty_sq "
                "FROM tbl_rencana_item i "
                "JOIN tbl_rencana_item_po p ON p.item_id = i.id "
                "JOIN tbl_master_po po ON po.id = p.po_id "
                "WHERE i.kode_lot_wip = %s",
                (kode_wip,),
            )
            po_list = cur.fetchall()
            cur.close()
            conn.close()
            return render_template("packing.html", kode_wip=kode_wip, wip_data=wip_data, po_list=po_list, packing_list=[])

        elif action == "start_packing":
            kode_wip = request.form.get("kode_wip")
            no_po = request.form.get("no_po")
            no_so = request.form.get("no_so", "")
            customer = request.form.get("customer", "")
            kode_packing = generate_code("FG")
            cur.execute(
                "INSERT INTO tbl_packing (kode_packing, kode_wip, no_po, customer, status) VALUES (%s,%s,%s,%s,'in_progress')",
                (kode_packing, kode_wip, no_po, customer),
            )
            packing_id = cur.lastrowid
            cur.execute(
                "INSERT INTO tbl_packing_po (packing_id, no_po, no_so, qty_sq) VALUES (%s,%s,%s,%s)",
                (packing_id, no_po, no_so, request.form.get("qty_sq") or 0),
            )
            conn.commit()
            return redirect(url_for("packing_detail", packing_id=packing_id))

    cur.execute("SELECT * FROM tbl_packing ORDER BY date_created DESC LIMIT 50")
    packing_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("packing.html", packing_list=packing_list)


@app.route("/packing/<int:packing_id>", methods=["GET", "POST"])
def packing_detail(packing_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    cur.execute("SELECT * FROM tbl_packing WHERE id = %s", (packing_id,))
    packing = cur.fetchone()
    if not packing:
        flash("Packing tidak ditemukan.", "danger")
        return redirect(url_for("packing"))

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_header":
            softness = (request.form.get("softness") or "").strip() or None
            gw = request.form.get("gross_weight")
            nw = request.form.get("net_weight")
            gross_weight = float(gw) if gw not in (None, "") else None
            net_weight = float(nw) if nw not in (None, "") else None
            cur.execute(
                "UPDATE tbl_packing SET softness=%s, gross_weight=%s, net_weight=%s WHERE id=%s",
                (softness, gross_weight, net_weight, packing_id),
            )

        elif action == "add_roll":
            lembar = int(request.form.get("lembar") or 1)
            ukuran = float(request.form.get("ukuran") or 0)
            remark = (request.form.get("remark") or "").strip() or None
            cur.execute("SELECT COALESCE(MAX(roll_no),0)+1 AS nxt FROM tbl_packing_roll WHERE packing_id=%s", (packing_id,))
            roll_no = cur.fetchone()["nxt"]
            cur.execute(
                "INSERT INTO tbl_packing_roll (packing_id, roll_no, lembar, ukuran, remark) "
                "VALUES (%s,%s,%s,%s,%s)",
                (packing_id, roll_no, lembar, ukuran, remark),
            )
            cur.execute(
                "UPDATE tbl_packing SET total_lembar=total_lembar+%s, total_ukuran=total_ukuran+%s WHERE id=%s",
                (lembar, ukuran, packing_id),
            )

        elif action == "delete_roll":
            roll_id = request.form.get("roll_id")
            cur.execute("SELECT lembar, ukuran FROM tbl_packing_roll WHERE id=%s AND packing_id=%s", (roll_id, packing_id))
            roll = cur.fetchone()
            if roll:
                cur.execute("DELETE FROM tbl_packing_roll WHERE id=%s", (roll_id,))
                cur.execute(
                    "UPDATE tbl_packing SET total_lembar=GREATEST(total_lembar-%s,0), "
                    "total_ukuran=GREATEST(total_ukuran-%s,0) WHERE id=%s",
                    (roll["lembar"], roll["ukuran"], packing_id),
                )

        elif action == "add_po":
            no_po = request.form.get("no_po", "").strip()
            no_so = request.form.get("no_so", "").strip()
            qty_sq = float(request.form.get("qty_sq") or 0)
            if no_po:
                cur.execute(
                    "INSERT INTO tbl_packing_po (packing_id, no_po, no_so, qty_sq) VALUES (%s,%s,%s,%s)",
                    (packing_id, no_po, no_so, qty_sq),
                )

        elif action == "delete_po":
            po_row_id = request.form.get("po_row_id")
            cur.execute("DELETE FROM tbl_packing_po WHERE id=%s AND packing_id=%s", (po_row_id, packing_id))

        elif action == "finish":
            cur.execute(
                "UPDATE tbl_packing SET status='finished', date_finished=NOW() WHERE id=%s",
                (packing_id,),
            )
            cur.execute("SELECT * FROM tbl_packing WHERE id=%s", (packing_id,))
            pkg = cur.fetchone()
            cur.execute(
                "INSERT IGNORE INTO tbl_gudang_fg "
                "(packing_id, kode_packing, kode_wip, customer, total_lembar, total_ukuran, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,'in_stock')",
                (
                    packing_id, pkg["kode_packing"], pkg["kode_wip"], pkg["customer"],
                    pkg["total_lembar"], pkg["total_ukuran"],
                ),
            )
            flash("Finish Good selesai. Masuk Gudang FG.", "success")

        conn.commit()
        return redirect(url_for("packing_detail", packing_id=packing_id))

    cur.execute("SELECT * FROM tbl_packing WHERE id = %s", (packing_id,))
    packing = cur.fetchone()
    cur.execute("SELECT * FROM tbl_packing_roll WHERE packing_id = %s ORDER BY roll_no", (packing_id,))
    rolls = cur.fetchall()
    cur.execute("SELECT * FROM tbl_packing_po WHERE packing_id = %s", (packing_id,))
    packing_pos = cur.fetchall()
    cur.execute(
        "SELECT i.id AS item_id, po.no_po, po.no_so, po.item_name, po.customer, p.qty_proses AS qty_sq "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_item_po p ON p.item_id = i.id "
        "JOIN tbl_master_po po ON po.id = p.po_id "
        "WHERE i.kode_lot_wip = %s",
        (packing["kode_wip"],),
    )
    available_pos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template(
        "packing_detail.html",
        packing=packing,
        rolls=rolls,
        packing_pos=packing_pos,
        available_pos=available_pos,
    )


@app.route("/packing/<int:packing_id>/print")
def packing_print(packing_id):
    from api_routes import _packing_print_payload

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_packing WHERE id = %s", (packing_id,))
    packing = cur.fetchone()
    if not packing:
        cur.close()
        conn.close()
        return "Packing tidak ditemukan", 404
    payload = _packing_print_payload(cur, packing)
    cur.close()
    conn.close()
    return render_template(
        "packing_print.html",
        packing=payload["packing"],
        rolls=payload["rolls"],
    )


@app.route("/packing/history")
def packing_history():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_packing ORDER BY date_created DESC")
    packing_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("packing_history.html", packing_list=packing_list)


# ==================== 9. STOK KIMIA ====================
@app.route("/stok-kimia", methods=["GET", "POST"])
def stok_kimia():
    from erp_raw_materials import list_materials, resolve_material
    from lot_erp_columns import ensure_lot_erp_columns

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_lot_erp_columns(cur)
    conn.commit()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "in":
            kimia_id = request.form.get("kimia_id")
            qty = float(request.form.get("qty") or 0)
            jumlah_kemasan = int(request.form.get("jumlah_kemasan") or 0) or None
            tanggal = request.form.get("tanggal") or date.today().isoformat()
            kode_internal = generate_code("BC-K")
            mat = resolve_material(erp_material_id=int(kimia_id), material_type="kimia")
            if not mat:
                flash("Material kimia ERP tidak ditemukan.", "danger")
            else:
                expired = date.today() + timedelta(days=365)
                cur.execute(
                    "INSERT INTO tbl_stok_kimia_in "
                    "(kode_internal, kimia_id, erp_material_id, kode_material, nama_material, "
                    "qty, qty_sisa, jumlah_kemasan, tanggal_in, expired_date, gudang, satuan) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'kimia',%s)",
                    (
                        kode_internal,
                        mat["id"],
                        mat["id"],
                        mat["code"],
                        mat["name"],
                        qty,
                        qty,
                        jumlah_kemasan,
                        tanggal,
                        expired,
                        mat.get("unit") or "kg",
                    ),
                )
                flash(f"Stok Kimia IN: {kode_internal}", "success")

        elif action == "out":
            stok_in_id = request.form.get("stok_in_id")
            qty = float(request.form.get("qty") or 0)
            jumlah_kemasan = int(request.form.get("jumlah_kemasan") or 0) or None
            tujuan = request.form.get("tujuan", "mixing")
            kode_wip = request.form.get("kode_wip") or None
            tanggal = request.form.get("tanggal") or date.today().isoformat()

            cur.execute("SELECT * FROM tbl_stok_kimia_in WHERE id=%s", (stok_in_id,))
            stok = cur.fetchone()
            if not stok or float(stok["qty_sisa"]) < qty:
                flash("Stok tidak cukup.", "danger")
            elif not stok.get("erp_material_id"):
                flash("Lot belum ter-map erp_material_id.", "danger")
            else:
                cur.execute(
                    "INSERT INTO tbl_stok_kimia_out "
                    "(stok_in_id, kimia_id, erp_material_id, kode_material, nama_material, "
                    "qty, jumlah_kemasan, tujuan, kode_wip, tanggal) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        stok_in_id,
                        stok.get("kimia_id") or stok["erp_material_id"],
                        stok["erp_material_id"],
                        stok.get("kode_material"),
                        stok.get("nama_material"),
                        qty,
                        jumlah_kemasan,
                        tujuan,
                        kode_wip,
                        tanggal,
                    ),
                )
                new_sisa = float(stok["qty_sisa"]) - qty
                new_gudang = "mixing" if tujuan == "mixing" else stok["gudang"]
                cur.execute(
                    "UPDATE tbl_stok_kimia_in SET qty_sisa=%s, gudang=%s WHERE id=%s",
                    (new_sisa, new_gudang, stok_in_id),
                )
                flash("Stok Kimia OUT berhasil.", "success")

        conn.commit()

    cur.execute(
        "SELECT si.*, COALESCE(si.nama_material, '') AS nama_barang, "
        "COALESCE(si.kode_material, '') AS kode_barang "
        "FROM tbl_stok_kimia_in si WHERE si.qty_sisa > 0 ORDER BY si.tanggal_in"
    )
    stok_in = cur.fetchall()
    cur.execute(
        "SELECT so.*, COALESCE(so.nama_material, '') AS nama_barang "
        "FROM tbl_stok_kimia_out so ORDER BY so.created_at DESC LIMIT 50"
    )
    stok_out = cur.fetchall()
    kimia_list = [
        {
            "id": r["id"],
            "kode_barang": r["code"],
            "nama_barang": r["name"],
            "satuan": r.get("unit") or "kg",
        }
        for r in list_materials("kimia")
    ]
    cur.close()
    conn.close()
    return render_template(
        "stok_kimia.html",
        stok_in=stok_in,
        stok_out=stok_out,
        kimia_list=kimia_list,
        today=date.today().isoformat(),
    )


# ==================== 10. STOK RP ====================
@app.route("/stok-rp", methods=["GET", "POST"])
def stok_rp():
    from erp_raw_materials import list_materials, resolve_material
    from lot_erp_columns import ensure_lot_erp_columns

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_lot_erp_columns(cur)
    conn.commit()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "in":
            rp_id = request.form.get("rp_id")
            meter_roll = float(request.form.get("meter_roll") or 0)
            tanggal = request.form.get("tanggal") or date.today().isoformat()
            kode_internal = generate_code("BC-R")
            mat = resolve_material(erp_material_id=int(rp_id), material_type="rp")
            if not mat:
                flash("Material RP ERP tidak ditemukan.", "danger")
            else:
                cur.execute(
                    "INSERT INTO tbl_stok_rp_in "
                    "(kode_internal, rp_id, erp_material_id, kode_material, nama_material, "
                    "meter_roll, qty_sisa, tanggal_in) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        kode_internal,
                        mat["id"],
                        mat["id"],
                        mat["code"],
                        mat["name"],
                        meter_roll,
                        meter_roll,
                        tanggal,
                    ),
                )
                flash(f"Stok RP IN: {kode_internal}", "success")

        elif action == "out":
            stok_in_id = request.form.get("stok_in_id")
            meter_roll = float(request.form.get("meter_roll") or 0)
            kode_wip = request.form.get("kode_wip") or None
            tanggal = request.form.get("tanggal") or date.today().isoformat()

            cur.execute("SELECT * FROM tbl_stok_rp_in WHERE id=%s", (stok_in_id,))
            stok = cur.fetchone()
            if not stok or float(stok["qty_sisa"]) < meter_roll:
                flash("Stok RP tidak cukup.", "danger")
            elif not stok.get("erp_material_id"):
                flash("Lot RP belum ter-map erp_material_id.", "danger")
            else:
                cur.execute(
                    "INSERT INTO tbl_stok_rp_out "
                    "(stok_in_id, rp_id, erp_material_id, kode_material, nama_material, "
                    "meter_roll, kode_wip, tanggal) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        stok_in_id,
                        stok.get("rp_id") or stok["erp_material_id"],
                        stok["erp_material_id"],
                        stok.get("kode_material"),
                        stok.get("nama_material"),
                        meter_roll,
                        kode_wip,
                        tanggal,
                    ),
                )
                cur.execute(
                    "UPDATE tbl_stok_rp_in SET qty_sisa = qty_sisa - %s WHERE id=%s",
                    (meter_roll, stok_in_id),
                )
                flash("Stok RP OUT berhasil (FIFO).", "success")

        conn.commit()

    cur.execute(
        "SELECT si.*, COALESCE(si.nama_material, '') AS nama_jenis "
        "FROM tbl_stok_rp_in si WHERE si.qty_sisa > 0 ORDER BY si.tanggal_in"
    )
    stok_in = cur.fetchall()
    cur.execute(
        "SELECT so.*, COALESCE(so.nama_material, '') AS nama_jenis "
        "FROM tbl_stok_rp_out so ORDER BY so.created_at DESC LIMIT 50"
    )
    stok_out = cur.fetchall()
    rp_list = [
        {
            "id": r["id"],
            "kode_rp": r["code"],
            "nama_rp": r["name"],
            "deskripsi": None,
            "satuan": r.get("unit") or "meter",
        }
        for r in list_materials("rp")
    ]
    cur.close()
    conn.close()
    return render_template(
        "stok_rp.html",
        stok_in=stok_in,
        stok_out=stok_out,
        rp_list=rp_list,
        today=date.today().isoformat(),
    )


# ==================== REPORTS (existing) ====================
@app.route("/report_packing")
def report_packing():
    today = datetime.today().strftime("%Y-%m-%d")
    start_date = request.args.get("start_date", today)
    end_date = request.args.get("end_date", today)

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT DATE(p.date_created) AS tanggal, p.no_po, p.kode_packing AS kode_process,
                   COUNT(r.id) AS pack, SUM(r.lembar) AS qty, SUM(r.ukuran) AS size, p.status
            FROM tbl_packing p
            LEFT JOIN tbl_packing_roll r ON r.packing_id = p.id
            WHERE DATE(p.date_created) BETWEEN %s AND %s
            GROUP BY DATE(p.date_created), p.no_po, p.kode_packing, p.status
        """
        cur.execute(query, (start_date, end_date))
        report_data = cur.fetchall()
    except mysql.connector.Error:
        report_data = []

    total_all_lembar = sum(row.get("qty") or 0 for row in report_data)
    total_all_ukuran = sum(row.get("size") or 0 for row in report_data)
    total_all_pack = sum(row.get("pack") or 0 for row in report_data)

    cur.close()
    conn.close()
    return render_template(
        "report_packing.html",
        data=report_data,
        start_date=start_date,
        end_date=end_date,
        total_all_lembar=total_all_lembar,
        total_all_ukuran=total_all_ukuran,
        total_all_pack=total_all_pack,
    )


@app.route("/report_persiapan")
def report_persiapan():
    today = datetime.today().strftime("%Y-%m-%d")
    start_date = request.args.get("start_date", today)
    end_date = request.args.get("end_date", today)

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    try:
        query = """
            SELECT DATE(pk.date_created) AS tanggal, pk.kode_proses AS kode_proccess,
                   pk.no_po AS nama_barang, COUNT(u.id) AS total_lembar,
                   SUM(u.size_val) AS total_ukuran, pk.status AS status_terakhir
            FROM tbl_persiapan_kulit pk
            LEFT JOIN tbl_persiapan_ukur u ON u.persiapan_id = pk.id
            WHERE DATE(pk.date_created) BETWEEN %s AND %s
            GROUP BY pk.id
        """
        cur.execute(query, (start_date, end_date))
        report_data = cur.fetchall()
    except mysql.connector.Error:
        report_data = []

    total_all_lembar = sum(row.get("total_lembar") or 0 for row in report_data)
    total_all_ukuran = sum(row.get("total_ukuran") or 0 for row in report_data if row.get("total_ukuran"))

    cur.close()
    conn.close()
    return render_template(
        "report_persiapan.html",
        data=report_data,
        start_date=start_date,
        end_date=end_date,
        total_all_lembar=total_all_lembar,
        total_all_ukuran=total_all_ukuran,
    )


@app.route("/lot")
def lot():
    return redirect(url_for("palet"))


# ==================== MASTER KULIT / RP / KIMIA (read-only ERP) ====================
@app.route("/master/kulit", methods=["GET", "POST"])
def master_kulit():
    from erp_raw_materials import list_materials

    if request.method == "POST":
        flash("Katalog kulit dikelola di ERP Inventory (raw_materials).", "warning")
        return redirect(url_for("master_kulit"))
    kulit_list = [
        {
            "id": r["id"],
            "kode_kulit": r["code"],
            "nama_kulit": r["name"],
            "thickness": None,
            "warna": None,
        }
        for r in list_materials("kulit")
    ]
    return render_template("master_kulit.html", kulit_list=kulit_list)


@app.route("/master/rp", methods=["GET", "POST"])
def master_rp():
    from erp_raw_materials import list_materials

    if request.method == "POST":
        flash("Katalog RP dikelola di ERP Inventory (raw_materials).", "warning")
        return redirect(url_for("master_rp"))
    rp_list = [
        {
            "id": r["id"],
            "kode_rp": r["code"],
            "nama_rp": r["name"],
            "deskripsi": None,
            "created_at": None,
        }
        for r in list_materials("rp")
    ]
    return render_template("master_rp.html", rp_list=rp_list)


@app.route("/master/kimia", methods=["GET", "POST"])
def master_kimia():
    from erp_raw_materials import list_materials

    if request.method == "POST":
        flash("Katalog kimia dikelola di ERP Inventory (raw_materials).", "warning")
        return redirect(url_for("master_kimia"))
    kimia_list = [
        {
            "id": r["id"],
            "kode_kimia": r["code"],
            "nama_kimia": r["name"],
            "deskripsi": None,
            "satuan": r.get("unit") or "kg",
            "created_at": None,
        }
        for r in list_materials("kimia")
    ]
    return render_template("master_kimia.html", kimia_list=kimia_list)


@app.route("/master/treatment", methods=["GET", "POST"])
def master_treatment():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_master_treatment(cur)
    conn.commit()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            nama_treatment = request.form.get("nama_treatment", "").strip()
            jenis = request.form.get("jenis", "PU")
            if not nama_treatment:
                flash("Nama treatment wajib diisi.", "danger")
            else:
                try:
                    cur.execute(
                        "INSERT INTO tbl_master_treatment (jenis, nama_treatment) VALUES (%s, %s)",
                        (jenis, nama_treatment),
                    )
                    conn.commit()
                    flash(f"Master treatment {nama_treatment} berhasil ditambahkan.", "success")
                except mysql.connector.IntegrityError:
                    flash(f"Treatment {nama_treatment} sudah ada.", "danger")

        elif action == "update":
            treatment_id = request.form.get("id")
            nama_treatment = request.form.get("nama_treatment", "").strip()
            jenis = request.form.get("jenis", "PU")
            if not nama_treatment:
                flash("Nama treatment wajib diisi.", "danger")
            else:
                try:
                    cur.execute(
                        "UPDATE tbl_master_treatment SET jenis=%s, nama_treatment=%s WHERE id=%s",
                        (jenis, nama_treatment, treatment_id),
                    )
                    conn.commit()
                    flash("Master treatment berhasil diperbarui.", "success")
                except mysql.connector.IntegrityError:
                    flash(f"Treatment {nama_treatment} sudah digunakan.", "danger")

        elif action == "delete":
            treatment_id = request.form.get("id")
            cur.execute("DELETE FROM tbl_master_treatment WHERE id=%s", (treatment_id,))
            conn.commit()
            flash("Master treatment berhasil dihapus.", "success")

    cur.execute("SELECT * FROM tbl_master_treatment ORDER BY nama_treatment")
    treatment_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("master_treatment.html", treatment_list=treatment_list)


# ==================== MASTER ERP (= Master Item Tonghong) ====================
@app.route("/master/erp")
def master_erp():
    from erp_master_items import fetch_master_items, item_to_erp_shape

    erp_list = [item_to_erp_shape(r) for r in fetch_master_items(limit=2000)]
    return render_template("master_erp.html", erp_list=erp_list)


# ==================== MASTER MATERIAL LAIN (read-only ERP) ====================
@app.route("/master/material-lain", methods=["GET", "POST"])
def master_material_lain():
    from erp_raw_materials import list_materials

    if request.method == "POST":
        flash("Katalog material lain dikelola di ERP Inventory (raw_materials).", "warning")
        return redirect(url_for("master_material_lain"))
    material_list = [
        {
            "id": r["id"],
            "kode_material": r["code"],
            "nama_material": r["name"],
            "deskripsi": None,
            "satuan": r.get("unit") or "pcs",
        }
        for r in list_materials("material_lain")
    ]
    return render_template("master_material_lain.html", material_list=material_list)


# ==================== STOK MATERIAL LAIN ====================
@app.route("/stok-material-lain", methods=["GET", "POST"])
def stok_material_lain():
    from erp_raw_materials import list_materials, resolve_material
    from lot_erp_columns import ensure_lot_erp_columns

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    ensure_lot_erp_columns(cur)
    conn.commit()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "in":
            material_id = request.form.get("material_id")
            qty = float(request.form.get("qty") or 0)
            tanggal = request.form.get("tanggal") or date.today().isoformat()
            kode_internal = generate_code("BC-M")
            mat = resolve_material(erp_material_id=int(material_id), material_type="material_lain")
            if not mat:
                flash("Material ERP tidak ditemukan.", "danger")
            else:
                cur.execute(
                    "INSERT INTO tbl_stok_material_lain_in "
                    "(kode_internal, material_id, erp_material_id, kode_material, nama_material, "
                    "qty, qty_sisa, satuan, tanggal_in) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        kode_internal,
                        mat["id"],
                        mat["id"],
                        mat["code"],
                        mat["name"],
                        qty,
                        qty,
                        mat.get("unit") or "pcs",
                        tanggal,
                    ),
                )
                flash(f"Stok Material IN: {kode_internal}", "success")
        elif action == "out":
            stok_in_id = request.form.get("stok_in_id")
            qty = float(request.form.get("qty") or 0)
            tanggal = request.form.get("tanggal") or date.today().isoformat()
            kode_wip = request.form.get("kode_wip") or None
            cur.execute("SELECT * FROM tbl_stok_material_lain_in WHERE id=%s", (stok_in_id,))
            stok = cur.fetchone()
            if not stok or float(stok["qty_sisa"]) < qty:
                flash("Stok tidak cukup.", "danger")
            elif not stok.get("erp_material_id"):
                flash("Lot material belum ter-map erp_material_id.", "danger")
            else:
                cur.execute(
                    "INSERT INTO tbl_stok_material_lain_out "
                    "(stok_in_id, material_id, erp_material_id, kode_material, nama_material, "
                    "qty, kode_wip, tanggal) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        stok_in_id,
                        stok.get("material_id") or stok["erp_material_id"],
                        stok["erp_material_id"],
                        stok.get("kode_material"),
                        stok.get("nama_material"),
                        qty,
                        kode_wip,
                        tanggal,
                    ),
                )
                cur.execute(
                    "UPDATE tbl_stok_material_lain_in SET qty_sisa=%s WHERE id=%s",
                    (float(stok["qty_sisa"]) - qty, stok_in_id),
                )
                flash("Stok Material OUT berhasil.", "success")
        conn.commit()

    cur.execute(
        "SELECT si.*, COALESCE(si.kode_material, '') AS kode_material, "
        "COALESCE(si.nama_material, '') AS nama_material "
        "FROM tbl_stok_material_lain_in si WHERE si.qty_sisa > 0 ORDER BY si.tanggal_in"
    )
    stok_in = cur.fetchall()
    cur.execute(
        "SELECT so.*, COALESCE(so.nama_material, '') AS nama_material "
        "FROM tbl_stok_material_lain_out so ORDER BY so.created_at DESC LIMIT 50"
    )
    stok_out = cur.fetchall()
    material_list = [
        {
            "id": r["id"],
            "kode_material": r["code"],
            "nama_material": r["name"],
            "satuan": r.get("unit") or "pcs",
        }
        for r in list_materials("material_lain")
    ]
    cur.close()
    conn.close()
    return render_template(
        "stok_material_lain.html",
        stok_in=stok_in,
        stok_out=stok_out,
        material_list=material_list,
        today=date.today().isoformat(),
    )


# ==================== USAGE MATERIAL LAIN ====================
@app.route("/api/usage-material/scan")
def api_usage_material_scan():
    from erp_raw_materials import fetch_material_by_code

    kode = request.args.get("q", "").strip()
    mat = fetch_material_by_code(kode, material_type="material_lain")
    if not mat:
        return jsonify({"error": "Material tidak ditemukan"}), 404
    return jsonify(
        {
            "kode_material": mat["code"],
            "nama_material": mat["name"],
            "satuan": mat.get("unit") or "pcs",
        }
    )


@app.route("/usage-material-lain", methods=["GET", "POST"])
def usage_material_lain():
    from erp_raw_materials import fetch_material_by_code

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if request.method == "POST":
        kode_wip = request.form.get("kode_wip", "").strip()
        kode_material = request.form.get("kode_material", "").strip()
        qty_used = float(request.form.get("qty_used") or 0)
        satuan = request.form.get("satuan", "pcs")
        mat = fetch_material_by_code(kode_material, material_type="material_lain")
        cur.execute(
            "INSERT INTO tbl_usage_material_lain (kode_wip, kode_material, nama_material, qty_used, satuan) "
            "VALUES (%s,%s,%s,%s,%s)",
            (kode_wip, kode_material, mat["name"] if mat else None, qty_used, satuan),
        )
        conn.commit()
        flash("Usage material lain tersimpan.", "success")

    cur.execute("SELECT * FROM tbl_usage_material_lain ORDER BY date_created DESC LIMIT 100")
    usage_list = cur.fetchall()
    cur.execute(
        "SELECT DISTINCT kode_lot_wip FROM tbl_rencana_item WHERE kode_lot_wip IS NOT NULL ORDER BY kode_lot_wip DESC"
    )
    wip_list = [r["kode_lot_wip"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template("usage_material_lain.html", usage_list=usage_list, wip_list=wip_list)


# ==================== GUDANG FINISH GOOD ====================
@app.route("/gudang-fg", methods=["GET", "POST"])
def gudang_fg():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if request.method == "POST" and request.form.get("action") == "out":
        kode_packing = request.form.get("kode_packing", "").strip()
        keterangan = request.form.get("keterangan", "")
        cur.execute(
            "SELECT * FROM tbl_gudang_fg WHERE kode_packing=%s AND status='in_stock'",
            (kode_packing,),
        )
        fg = cur.fetchone()
        if fg:
            cur.execute(
                "UPDATE tbl_gudang_fg SET status='out', date_out=NOW(), keterangan_out=%s WHERE id=%s",
                (keterangan, fg["id"]),
            )
            conn.commit()
            flash(f"Packing List {kode_packing} OUT dari gudang.", "success")
        else:
            flash("Kode Packing List tidak ditemukan atau sudah OUT.", "danger")

    cur.execute(
        "SELECT * FROM tbl_gudang_fg ORDER BY date_in DESC LIMIT 100"
    )
    fg_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("gudang_fg.html", fg_list=fg_list)


@app.route("/gudang-fg/<int:fg_id>")
def gudang_fg_detail(fg_id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_gudang_fg WHERE id=%s", (fg_id,))
    fg = cur.fetchone()
    if not fg:
        flash("Data tidak ditemukan.", "danger")
        return redirect(url_for("gudang_fg"))
    cur.execute("SELECT * FROM tbl_packing WHERE id=%s", (fg["packing_id"],))
    packing = cur.fetchone()
    cur.execute("SELECT * FROM tbl_packing_roll WHERE packing_id=%s ORDER BY roll_no", (fg["packing_id"],))
    rolls = cur.fetchall()
    cur.execute("SELECT * FROM tbl_packing_po WHERE packing_id=%s", (fg["packing_id"],))
    packing_pos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("gudang_fg_detail.html", fg=fg, packing=packing, rolls=rolls, packing_pos=packing_pos)


@app.route("/checkpoint")
def checkpoint():
    return render_template("checkpoint.html")


@app.route("/init-db")
def init_db_route():
    from init_db import main
    try:
        main()
        flash("Database berhasil diinisialisasi.", "success")
    except Exception as e:
        flash(f"Gagal init DB: {e}", "danger")
    return redirect(url_for("palet"))


from api_routes import api as mrp_api_blueprint

app.register_blueprint(mrp_api_blueprint)


if __name__ == "__main__":
    port = int(os.getenv("MRP_PORT", "5010"))
    debug = os.getenv("MRP_DEBUG", "0") == "1"
    app.run(debug=debug, port=port, host="0.0.0.0")
