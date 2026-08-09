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
    cur.execute(f"SHOW COLUMNS FROM {table}")
    rows = cur.fetchall()
    if rows and isinstance(rows[0], dict):
        return {r["Field"] for r in rows}
    return {r[0] for r in rows}


def _row_first(row):
    if isinstance(row, dict):
        return next(iter(row.values()))
    return row[0]


def ensure_rencana_tables(cur):
    cur.execute(
        "CREATE TABLE IF NOT EXISTS master_customer ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "kode_customer VARCHAR(50) DEFAULT NULL, "
        "nama_customer VARCHAR(150) NOT NULL, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
        "INDEX idx_nama_customer (nama_customer))"
    )
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
    cur.execute("SELECT DISTINCT customer FROM tbl_master_po WHERE customer IS NOT NULL AND customer != ''")
    for row in cur.fetchall():
        nama = _row_first(row)
        cur.execute("SELECT id FROM master_customer WHERE nama_customer = %s", (nama,))
        if not cur.fetchone():
            kode = f"CUST-{nama[:20].upper().replace(' ', '-')}"
            cur.execute(
                "INSERT INTO master_customer (kode_customer, nama_customer) VALUES (%s, %s)",
                (kode, nama),
            )
    cur.execute(
        "UPDATE tbl_master_po p JOIN master_customer c ON c.nama_customer = p.customer "
        "SET p.customer_id = c.id WHERE p.customer_id IS NULL AND p.customer IS NOT NULL"
    )


def ensure_extended_tables(cur):
    cur.execute(
        "CREATE TABLE IF NOT EXISTS master_erp ("
        "id INT AUTO_INCREMENT PRIMARY KEY, thickness VARCHAR(30) NOT NULL, "
        "material_name VARCHAR(150) DEFAULT NULL, color VARCHAR(100) NOT NULL, "
        "emboss VARCHAR(100) NOT NULL, customer VARCHAR(150) DEFAULT NULL, "
        "color_swatch VARCHAR(100) DEFAULT NULL, backer VARCHAR(100) DEFAULT NULL, "
        "created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
    )
    cur.execute(
        "CREATE TABLE IF NOT EXISTS master_material_lain ("
        "id INT AUTO_INCREMENT PRIMARY KEY, kode_material VARCHAR(50) NOT NULL UNIQUE, "
        "nama_material VARCHAR(150) NOT NULL, deskripsi TEXT DEFAULT NULL, "
        "satuan VARCHAR(20) DEFAULT 'pcs', created_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
    )
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
    pers_cols = _col_names(cur, "tbl_persiapan_kulit")
    if "rencana_item_id" not in pers_cols:
        cur.execute("ALTER TABLE tbl_persiapan_kulit ADD COLUMN rencana_item_id INT DEFAULT NULL")
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
    erp_cols = _col_names(cur, "master_erp")
    if "material_name" not in erp_cols:
        cur.execute("ALTER TABLE master_erp ADD COLUMN material_name VARCHAR(150) DEFAULT NULL")
    if "customer" not in erp_cols:
        cur.execute("ALTER TABLE master_erp ADD COLUMN customer VARCHAR(150) DEFAULT NULL")
    try:
        cur.execute("ALTER TABLE master_erp DROP INDEX uk_erp_combo")
    except mysql.connector.Error:
        pass
    po_cols_ext = _col_names(cur, "tbl_master_po")
    if "color_swatch" not in po_cols_ext:
        cur.execute("ALTER TABLE tbl_master_po ADD COLUMN color_swatch VARCHAR(100) DEFAULT NULL")
    cur.execute(
        "UPDATE master_erp SET material_name = 'Standard Leather' "
        "WHERE material_name IS NULL OR material_name = ''"
    )
    cur.execute(
        "UPDATE master_erp e JOIN tbl_master_po p "
        "ON p.tebal = e.thickness AND p.warna = e.color AND p.emboss = e.emboss "
        "SET e.customer = p.customer WHERE e.customer IS NULL OR e.customer = ''"
    )
    cur.execute(
        "UPDATE tbl_master_po p JOIN master_erp e "
        "ON p.tebal = e.thickness AND p.warna = e.color AND p.emboss = e.emboss "
        "SET p.color_swatch = e.color_swatch WHERE p.color_swatch IS NULL OR p.color_swatch = ''"
    )
    erp_seeds = [
        ("1.0mm", "Standard Leather", "Brown", "Plain", "Customer A", "SW-BRN-01", "BK-PU-A"),
        ("1.0mm", "Standard Leather", "Brown", "Plain", "Customer A", "SW-BRN-01B", "WHITE"),
        ("1.0mm", "Standard Leather", "Black", "Emboss A", "Customer A", "SW-BLK-02", "BK-PU-B"),
        ("1.2mm", "Premium Leather", "Brown", "Plain", "Customer A", "SW-BRN-03", "BK-PU-A"),
        ("1.2mm", "Premium Leather", "Tan", "Emboss X", "Customer B", "SW-TAN-04", "BK-SUEDE-C"),
        ("1.4mm", "Premium Leather", "Red", "Emboss B", "Customer B", "SW-RED-05", "BK-PU-D"),
        ("1.4mm", "Premium Leather", "Maroon", "Emboss B", "Customer B", "SW-MAR-06", "BK-PU-D"),
        ("1.0mm", "Standard Leather", "Black", "Emboss A", "NIKOMAS", "SW-BLK-02", "BLACK"),
    ]
    for th, mat, co, em, cust, sw, bk in erp_seeds:
        cur.execute(
            "SELECT id FROM master_erp WHERE thickness=%s AND material_name=%s AND color=%s "
            "AND emboss=%s AND color_swatch=%s",
            (th, mat, co, em, sw),
        )
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO master_erp (thickness, material_name, color, emboss, customer, color_swatch, backer) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (th, mat, co, em, cust, sw, bk),
            )
    mat_seeds = [
        ("MAT-001", "Thread Nylon", "Benang jahit nylon", "roll"),
        ("MAT-002", "Label Tag", "Label produk", "pcs"),
        ("MAT-003", "Plastic Wrap", "Plastik pembungkus", "roll"),
    ]
    for km, nm, ds, sat in mat_seeds:
        cur.execute(
            "INSERT IGNORE INTO master_material_lain (kode_material, nama_material, deskripsi, satuan) "
            "VALUES (%s,%s,%s,%s)",
            (km, nm, ds, sat),
        )


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
    for nama in ("Treatment A", "Treatment B", "Treatment C", "Treatment D"):
        cur.execute("SELECT id FROM tbl_master_treatment WHERE nama_treatment = %s", (nama,))
        if not cur.fetchone():
            cur.execute(
                "INSERT INTO tbl_master_treatment (jenis, nama_treatment) VALUES ('PU', %s)",
                (nama,),
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
        cur.execute(
            "CREATE TABLE IF NOT EXISTS master_kulit ("
            "id INT AUTO_INCREMENT PRIMARY KEY, "
            "kode_kulit VARCHAR(50) NOT NULL UNIQUE, "
            "nama_kulit VARCHAR(150) DEFAULT NULL, "
            "thickness VARCHAR(30) DEFAULT NULL, "
            "warna VARCHAR(100) DEFAULT NULL, "
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
            "INDEX idx_kode_kulit (kode_kulit))"
        )
        cur.execute("SHOW COLUMNS FROM master_kulit")
        kulit_cols = {row[0] for row in cur.fetchall()}
        if "nama_kulit" not in kulit_cols:
            cur.execute("ALTER TABLE master_kulit ADD COLUMN nama_kulit VARCHAR(150) DEFAULT NULL AFTER kode_kulit")
        cur.execute(
            "CREATE TABLE IF NOT EXISTS master_rp ("
            "id INT AUTO_INCREMENT PRIMARY KEY, "
            "kode_rp VARCHAR(50) NOT NULL UNIQUE, "
            "nama_rp VARCHAR(150) NOT NULL, "
            "deskripsi TEXT DEFAULT NULL, "
            "satuan VARCHAR(20) DEFAULT 'meter', "
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
            "INDEX idx_kode_rp (kode_rp))"
        )
        cur.execute("SHOW COLUMNS FROM master_rp")
        rp_cols = {row[0] for row in cur.fetchall()}
        if "kode_rp" not in rp_cols:
            cur.execute("ALTER TABLE master_rp ADD COLUMN kode_rp VARCHAR(50) DEFAULT NULL")
        if "nama_rp" not in rp_cols:
            cur.execute("ALTER TABLE master_rp ADD COLUMN nama_rp VARCHAR(150) DEFAULT NULL")
        if "deskripsi" not in rp_cols:
            cur.execute("ALTER TABLE master_rp ADD COLUMN deskripsi TEXT DEFAULT NULL")
        if "created_at" not in rp_cols:
            cur.execute("ALTER TABLE master_rp ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        if "nama_jenis" in rp_cols:
            cur.execute(
                "UPDATE master_rp SET nama_rp = nama_jenis "
                "WHERE (nama_rp IS NULL OR nama_rp = '') AND nama_jenis IS NOT NULL"
            )
        cur.execute("SELECT id FROM master_rp WHERE kode_rp IS NULL OR kode_rp = ''")
        for (rp_id,) in cur.fetchall():
            cur.execute(
                "UPDATE master_rp SET kode_rp = %s WHERE id = %s",
                (f"RP-{rp_id:03d}", rp_id),
            )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS master_kimia ("
            "id INT AUTO_INCREMENT PRIMARY KEY, "
            "kode_kimia VARCHAR(50) NOT NULL UNIQUE, "
            "nama_kimia VARCHAR(150) NOT NULL, "
            "deskripsi TEXT DEFAULT NULL, "
            "satuan VARCHAR(20) DEFAULT 'kg', "
            "expired_days INT DEFAULT 365, "
            "created_at DATETIME DEFAULT CURRENT_TIMESTAMP, "
            "INDEX idx_kode_kimia (kode_kimia))"
        )
        cur.execute("SHOW COLUMNS FROM master_kimia")
        kimia_cols = {row[0] for row in cur.fetchall()}
        if "kode_kimia" not in kimia_cols:
            cur.execute("ALTER TABLE master_kimia ADD COLUMN kode_kimia VARCHAR(50) DEFAULT NULL")
        if "nama_kimia" not in kimia_cols:
            cur.execute("ALTER TABLE master_kimia ADD COLUMN nama_kimia VARCHAR(150) DEFAULT NULL")
        if "deskripsi" not in kimia_cols:
            cur.execute("ALTER TABLE master_kimia ADD COLUMN deskripsi TEXT DEFAULT NULL")
        if "created_at" not in kimia_cols:
            cur.execute("ALTER TABLE master_kimia ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        if "kode_barang" in kimia_cols:
            cur.execute(
                "UPDATE master_kimia SET kode_kimia = kode_barang "
                "WHERE (kode_kimia IS NULL OR kode_kimia = '') AND kode_barang IS NOT NULL"
            )
        if "nama_barang" in kimia_cols:
            cur.execute(
                "UPDATE master_kimia SET nama_kimia = nama_barang "
                "WHERE (nama_kimia IS NULL OR nama_kimia = '') AND nama_barang IS NOT NULL"
            )
        cur.execute("SELECT id FROM master_kimia WHERE kode_kimia IS NULL OR kode_kimia = ''")
        for (kimia_id,) in cur.fetchall():
            cur.execute(
                "UPDATE master_kimia SET kode_kimia = %s WHERE id = %s",
                (f"KIM-{kimia_id:03d}", kimia_id),
            )
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
    cur.execute(
        "SELECT kode_kulit, nama_kulit, thickness, warna FROM master_kulit ORDER BY kode_kulit"
    )
    kulit_list = cur.fetchall()
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
def _save_item_po_selections(cur, item_id, po_data):
    for entry in po_data:
        po_id = entry.get("po_id")
        qty = float(entry.get("qty") or 0)
        if not po_id or qty <= 0:
            continue
        cur.execute("SELECT * FROM tbl_master_po WHERE id = %s", (po_id,))
        po = cur.fetchone()
        if not po:
            continue
        qty_outstanding = float(po["qty_order"]) - float(po["qty_processed"])
        cur.execute(
            "INSERT INTO tbl_rencana_item_po (item_id, po_id, qty_outstanding, qty_proses) "
            "VALUES (%s, %s, %s, %s)",
            (item_id, po_id, qty_outstanding, qty),
        )
        new_processed = float(po["qty_processed"]) + qty
        status = "completed" if new_processed >= float(po["qty_order"]) else "partial"
        cur.execute(
            "UPDATE tbl_master_po SET qty_processed=%s, status=%s WHERE id=%s",
            (new_processed, status, po_id),
        )


def _ensure_customer_id(cur, nama):
    if not nama:
        cur.execute("SELECT id FROM master_customer ORDER BY id LIMIT 1")
        row = cur.fetchone()
        return row["id"] if row else 1
    cur.execute("SELECT id FROM master_customer WHERE nama_customer = %s", (nama,))
    row = cur.fetchone()
    if row:
        return row["id"]
    kode = f"CUST-{nama[:20].upper().replace(' ', '-')}"
    cur.execute(
        "INSERT INTO master_customer (kode_customer, nama_customer) VALUES (%s, %s)",
        (kode, nama),
    )
    return cur.lastrowid


@app.route("/api/erp/combination")
def api_erp_combination():
    material_name = request.args.get("material_name", "").strip()
    color = request.args.get("color", "").strip()
    emboss = request.args.get("emboss", "").strip()
    thickness = request.args.get("thickness", "").strip()
    if not material_name or not color or not emboss:
        return jsonify({"error": "Material Name, Color, Emboss wajib"}), 400
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    sql = (
        "SELECT thickness, material_name, color, emboss, customer, color_swatch, backer "
        "FROM master_erp WHERE material_name=%s AND color=%s AND emboss=%s"
    )
    params = [material_name, color, emboss]
    if thickness:
        sql += " AND thickness=%s"
        params.append(thickness)
    sql += " ORDER BY color_swatch"
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    if not rows:
        return jsonify({"error": "Kombinasi tidak ditemukan di master ERP"}), 404
    return jsonify({"options": rows})


@app.route("/api/erp/fields")
def api_erp_fields():
    thickness = request.args.get("thickness", "").strip()
    material_name = request.args.get("material_name", "").strip()
    color = request.args.get("color", "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    def distinct(col, where="", params=None):
        q = f"SELECT DISTINCT {col} AS v FROM master_erp WHERE {col} IS NOT NULL AND {col} != ''"
        if where:
            q += f" AND {where}"
        q += f" ORDER BY {col}"
        cur.execute(q, params or ())
        return [r["v"] for r in cur.fetchall()]

    where_parts, params = [], []
    if thickness:
        where_parts.append("thickness=%s")
        params.append(thickness)
    if material_name:
        where_parts.append("material_name=%s")
        params.append(material_name)
    if color:
        where_parts.append("color=%s")
        params.append(color)
    where = " AND ".join(where_parts) if where_parts else "1=1"

    result = {
        "thicknesses": distinct("thickness"),
        "material_names": distinct("material_name", where, params),
        "colors": distinct("color", where, params),
        "embosses": distinct("emboss", where, params),
        "customers": distinct("customer", where, params),
    }
    cur.close()
    conn.close()
    return jsonify(result)


@app.route("/api/erp/options")
def api_erp_options():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT DISTINCT thickness FROM master_erp ORDER BY thickness")
    thicknesses = [r["thickness"] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT color FROM master_erp ORDER BY color")
    colors = [r["color"] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT emboss FROM master_erp ORDER BY emboss")
    embosses = [r["emboss"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"thicknesses": thicknesses, "colors": colors, "embosses": embosses})


@app.route("/api/rencana/po/by-combination")
def api_po_by_combination():
    color = request.args.get("color", "").strip()
    emboss = request.args.get("emboss", "").strip()
    color_swatch = request.args.get("color_swatch", "").strip()
    if not color or not emboss or not color_swatch:
        return jsonify({"error": "Color, Emboss, Color Swatch wajib"}), 400
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT id, no_po, no_so, customer, item_name, sq_ft, qty_order, qty_processed, "
        "(qty_order - qty_processed) AS qty_outstanding "
        "FROM tbl_master_po "
        "WHERE warna = %s AND emboss = %s AND color_swatch = %s "
        "AND status IN ('outstanding','partial') "
        "ORDER BY no_po, item_name",
        (color, emboss, color_swatch),
    )
    items = cur.fetchall()
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
                    cur.execute(
                        "SELECT backer FROM master_erp "
                        "WHERE thickness=%s AND material_name=%s AND color=%s AND emboss=%s AND color_swatch=%s "
                        "LIMIT 1",
                        (thickness, material_name, color, emboss, color_swatch),
                    )
                    erp = cur.fetchone()
                    backer = (item.get("backer") or (erp["backer"] if erp else None))
                    customer_id = _ensure_customer_id(cur, customer_name)
                    kode_item = generate_code("RPI")
                    kode_wip = generate_code("WIP")
                    cur.execute(
                        "INSERT INTO tbl_rencana_item "
                        "(rencana_id, kode_rencana_item, kode_lot_wip, customer_id, "
                        "material_name, thickness, color, emboss, color_swatch, backer, keterangan, urutan) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (
                            rencana_id, kode_item, kode_wip, customer_id,
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

    cur.execute("SELECT DISTINCT thickness FROM master_erp ORDER BY thickness")
    erp_thickness = [r["thickness"] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT material_name FROM master_erp WHERE material_name IS NOT NULL ORDER BY material_name")
    erp_materials = [r["material_name"] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT color FROM master_erp ORDER BY color")
    erp_colors = [r["color"] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT emboss FROM master_erp ORDER BY emboss")
    erp_emboss = [r["emboss"] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT customer FROM master_erp WHERE customer IS NOT NULL ORDER BY customer")
    erp_customers = [r["customer"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template(
        "rencana_produksi_tambah.html",
        erp_thickness=erp_thickness,
        erp_materials=erp_materials,
        erp_colors=erp_colors,
        erp_emboss=erp_emboss,
        erp_customers=erp_customers,
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
        "SELECT i.*, c.nama_customer, "
        "(SELECT COUNT(*) FROM tbl_rencana_item_po p WHERE p.item_id = i.id) AS jml_po, "
        "(SELECT COALESCE(SUM(p.qty_proses),0) FROM tbl_rencana_item_po p WHERE p.item_id = i.id) AS total_qty_so, "
        "(SELECT GROUP_CONCAT(DISTINCT COALESCE(NULLIF(po.no_so,''), po.no_po) ORDER BY po.no_po SEPARATOR ' / ') "
        " FROM tbl_rencana_item_po p JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = i.id) AS schedule_text "
        "FROM tbl_rencana_item i "
        "LEFT JOIN master_customer c ON c.id = i.customer_id "
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
        "SELECT i.*, c.nama_customer, "
        "(SELECT COALESCE(SUM(p.qty_proses),0) FROM tbl_rencana_item_po p WHERE p.item_id = i.id) AS total_qty_so, "
        "(SELECT GROUP_CONCAT(DISTINCT COALESCE(NULLIF(po.no_so,''), po.no_po) ORDER BY po.no_po SEPARATOR ' / ') "
        " FROM tbl_rencana_item_po p JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = i.id) AS schedule_text "
        "FROM tbl_rencana_item i "
        "LEFT JOIN master_customer c ON c.id = i.customer_id "
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
        "SELECT i.*, c.nama_customer, r.nama_rencana, r.tanggal_rencana, r.kode_rencana "
        "FROM tbl_rencana_item i "
        "LEFT JOIN master_customer c ON c.id = i.customer_id "
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
        "SELECT i.*, c.nama_customer, r.nama_rencana "
        "FROM tbl_rencana_item i "
        "LEFT JOIN master_customer c ON c.id = i.customer_id "
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
        "SELECT i.*, c.nama_customer, r.nama_rencana, r.tanggal_rencana "
        "FROM tbl_rencana_item i "
        "JOIN master_customer c ON c.id = i.customer_id "
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
            cur.execute("DELETE FROM tbl_rencana_item_po WHERE item_id = %s", (item_id,))
            _save_item_po_selections(cur, item_id, po_data)
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
        "c.kode_customer, c.nama_customer "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        "JOIN master_customer c ON c.id = i.customer_id "
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
        "SELECT i.id, i.kode_rencana_item, i.kode_lot_wip, r.nama_rencana, c.nama_customer "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        "JOIN master_customer c ON c.id = i.customer_id "
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

        if action == "start":
            cur.execute("UPDATE tbl_persiapan_kulit SET status='started' WHERE id=%s", (persiapan_id,))

        elif action == "scan_ky":
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
            else:
                cur.execute(
                    "INSERT INTO tbl_persiapan_ky (persiapan_id, kode_palet, kode_yl, target_qty, status) "
                    "VALUES (%s,%s,%s,%s,'active')",
                    (persiapan_id, kode_palet, kode_yl or None, target_qty),
                )
                cur.execute(
                    "INSERT INTO tbl_persiapan_scan (persiapan_id, kode_palet, kode_yl) VALUES (%s,%s,%s)",
                    (persiapan_id, kode_palet, kode_yl or None),
                )
                flash(f"KY {kode_palet} aktif.", "success")

        elif action == "add_ukur":
            ky_id = request.form.get("ky_id")
            size_val = float(request.form.get("size_val") or 0)
            if ky_id and size_val:
                cur.execute(
                    "INSERT INTO tbl_persiapan_ukur (persiapan_id, ky_id, size_val) VALUES (%s,%s,%s)",
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
            ky_id = request.form.get("ky_id")
            cur.execute("SELECT * FROM tbl_persiapan_ky WHERE id=%s AND persiapan_id=%s", (ky_id, persiapan_id))
            ky = cur.fetchone()
            if ky:
                target = float(ky["target_qty"] or 0)
                actual = float(ky["actual_qty"] or 0)
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
                            persiapan["rencana_item_id"], persiapan_id, ky_id,
                            ky["kode_palet"], ky["kode_yl"],
                            target, actual, selisih,
                            "Kurang" if selisih < 0 else "Lebih",
                        ),
                    )
                flash(f"KY selesai. Target: {target}, Aktual: {actual}", "info")

        elif action == "scan":
            kode_palet = request.form.get("kode_palet", "").strip()
            kode_yl = request.form.get("kode_yl", "").strip()
            size_val = request.form.get("size_val")
            cur.execute(
                "INSERT INTO tbl_persiapan_scan (persiapan_id, kode_palet, kode_yl) VALUES (%s,%s,%s)",
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
            ukur_id = request.form.get("ukur_id")
            cur.execute("SELECT size_val, ky_id FROM tbl_persiapan_ukur WHERE id=%s AND persiapan_id=%s", (ukur_id, persiapan_id))
            row = cur.fetchone()
            if row:
                cur.execute("DELETE FROM tbl_persiapan_ukur WHERE id=%s", (ukur_id,))
                cur.execute(
                    "UPDATE tbl_persiapan_kulit SET total_size = GREATEST(total_size - %s, 0) WHERE id=%s",
                    (row["size_val"], persiapan_id),
                )
                if row.get("ky_id"):
                    cur.execute(
                        "UPDATE tbl_persiapan_ky SET actual_qty = GREATEST(actual_qty - %s, 0) WHERE id=%s",
                        (row["size_val"], row["ky_id"]),
                    )

        elif action == "save":
            cur.execute(
                "UPDATE tbl_persiapan_kulit SET status='saved', date_saved=NOW() WHERE id=%s",
                (persiapan_id,),
            )
            flash("Data tersimpan. Label siap dicetak.", "success")

        elif action == "reprint":
            cur.execute("SELECT COALESCE(MAX(reprint_ke),0)+1 AS nxt FROM tbl_persiapan_reprint WHERE persiapan_id=%s", (persiapan_id,))
            reprint_ke = cur.fetchone()["nxt"]
            cur.execute("INSERT INTO tbl_persiapan_reprint (persiapan_id, reprint_ke) VALUES (%s,%s)", (persiapan_id, reprint_ke))
            flash(f"Reprint ke-{reprint_ke} dicatat.", "info")

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
                    cur.execute(
                        "SELECT COALESCE(nama_kimia, nama_barang) AS nama_kimia "
                        "FROM master_kimia WHERE COALESCE(kode_kimia, kode_barang) = %s",
                        (kode_kimia.strip(),),
                    )
                    kimia = cur.fetchone()
                    cur.execute(
                        "INSERT INTO tbl_lab_lot_detail "
                        "(kode_lot_warna, kode_kimia, nama_kimia, resep, satuan, qty, remarks) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (
                            kode_lot_warna,
                            kode_kimia.strip(),
                            kimia["nama_kimia"] if kimia else kode_kimia.strip(),
                            resep.strip() or None,
                            satuan.strip() or "kg",
                            qty or 0,
                            remarks.strip() or None,
                        ),
                    )
                conn.commit()
                flash(f"Lot Warna {kode_lot_warna} berhasil dibuat.", "success")

    cur.execute(
        "SELECT l.kode_lot_warna, l.nama_lot_warna, l.status, l.date_created, l.rencana_item_id, "
        "d.kode_kimia, d.nama_kimia, d.resep, d.satuan, d.qty, d.remarks, "
        "ri.kode_rencana_item, rp.nama_rencana, rp.tanggal_rencana, c.nama_customer "
        "FROM tbl_lab_lot l "
        "JOIN tbl_lab_lot_detail d ON d.kode_lot_warna = l.kode_lot_warna "
        "LEFT JOIN tbl_rencana_item ri ON ri.id = l.rencana_item_id "
        "LEFT JOIN tbl_rencana_produksi rp ON rp.id = ri.rencana_id "
        "LEFT JOIN master_customer c ON c.id = ri.customer_id "
        "ORDER BY COALESCE(rp.tanggal_rencana, l.date_created) DESC, l.kode_lot_warna, d.id DESC LIMIT 200"
    )
    lab_list = cur.fetchall()
    cur.execute(
        "SELECT ri.id, ri.kode_rencana_item, ri.kode_kulit, ri.color, ri.thickness, "
        "rp.nama_rencana, rp.tanggal_rencana, c.nama_customer "
        "FROM tbl_rencana_item ri "
        "JOIN tbl_rencana_produksi rp ON rp.id = ri.rencana_id "
        "JOIN master_customer c ON c.id = ri.customer_id "
        "ORDER BY rp.tanggal_rencana DESC, ri.urutan"
    )
    rencana_items = cur.fetchall()
    cur.execute(
        "SELECT COALESCE(kode_kimia, kode_barang) AS kode_kimia, "
        "COALESCE(nama_kimia, nama_barang) AS nama_kimia, satuan "
        "FROM master_kimia ORDER BY kode_kimia"
    )
    kimia_list = cur.fetchall()
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
    kode = request.args.get("q", "").strip()
    if not kode:
        return jsonify({"error": "Kode kosong"}), 400
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT kode_rp, COALESCE(nama_rp, nama_jenis) AS nama_jenis, satuan "
        "FROM master_rp WHERE kode_rp = %s OR nama_rp = %s OR nama_jenis = %s LIMIT 1",
        (kode, kode, kode),
    )
    rp = cur.fetchone()
    cur.close()
    conn.close()
    if not rp:
        return jsonify({"error": "Jenis RP tidak ditemukan"}), 404
    return jsonify(rp)


@app.route("/usage-rp", methods=["GET", "POST"])
def usage_rp():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        kode_wip = request.form.get("kode_wip", "").strip()
        jenis_scan = request.form.get("jenis_rp", "").strip()
        cur.execute(
            "SELECT COALESCE(nama_rp, nama_jenis) AS nama_jenis, satuan "
            "FROM master_rp WHERE kode_rp = %s OR nama_rp = %s OR nama_jenis = %s LIMIT 1",
            (jenis_scan, jenis_scan, jenis_scan),
        )
        rp = cur.fetchone()
        if not rp:
            flash("Jenis RP tidak ditemukan.", "danger")
        else:
            cur.execute(
                "INSERT INTO tbl_usage_rp (kode_wip, jenis_rp, qty_used, satuan) VALUES (%s,%s,%s,%s)",
                (kode_wip, rp["nama_jenis"], request.form.get("qty_used") or 0,
                 request.form.get("satuan") or rp.get("satuan") or "meter"),
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
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "in":
            kimia_id = request.form.get("kimia_id")
            qty = float(request.form.get("qty") or 0)
            jumlah_kemasan = int(request.form.get("jumlah_kemasan") or 0) or None
            tanggal = request.form.get("tanggal") or date.today().isoformat()
            kode_internal = generate_code("BC-K")
            cur.execute("SELECT expired_days FROM master_kimia WHERE id=%s", (kimia_id,))
            kimia = cur.fetchone()
            expired = date.today() + timedelta(days=kimia["expired_days"] if kimia else 365)
            cur.execute(
                "INSERT INTO tbl_stok_kimia_in (kode_internal, kimia_id, qty, qty_sisa, jumlah_kemasan, tanggal_in, expired_date, gudang) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,'kimia')",
                (kode_internal, kimia_id, qty, qty, jumlah_kemasan, tanggal, expired),
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
            if stok and stok["qty_sisa"] >= qty:
                cur.execute(
                    "INSERT INTO tbl_stok_kimia_out (stok_in_id, kimia_id, qty, jumlah_kemasan, tujuan, kode_wip, tanggal) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (stok_in_id, stok["kimia_id"], qty, jumlah_kemasan, tujuan, kode_wip, tanggal),
                )
                new_sisa = float(stok["qty_sisa"]) - qty
                new_gudang = "mixing" if tujuan == "mixing" else stok["gudang"]
                cur.execute(
                    "UPDATE tbl_stok_kimia_in SET qty_sisa=%s, gudang=%s WHERE id=%s",
                    (new_sisa, new_gudang, stok_in_id),
                )
                flash("Stok Kimia OUT berhasil.", "success")
            else:
                flash("Stok tidak cukup.", "danger")

        conn.commit()

    cur.execute(
        "SELECT si.*, COALESCE(mk.nama_kimia, mk.nama_barang) AS nama_barang, "
        "COALESCE(mk.kode_kimia, mk.kode_barang) AS kode_barang FROM tbl_stok_kimia_in si "
        "JOIN master_kimia mk ON mk.id = si.kimia_id WHERE si.qty_sisa > 0 ORDER BY si.tanggal_in"
    )
    stok_in = cur.fetchall()
    cur.execute(
        "SELECT so.*, COALESCE(mk.nama_kimia, mk.nama_barang) AS nama_barang FROM tbl_stok_kimia_out so "
        "JOIN master_kimia mk ON mk.id = so.kimia_id ORDER BY so.created_at DESC LIMIT 50"
    )
    stok_out = cur.fetchall()
    cur.execute(
        "SELECT id, COALESCE(kode_kimia, kode_barang) AS kode_barang, "
        "COALESCE(nama_kimia, nama_barang) AS nama_barang, satuan "
        "FROM master_kimia ORDER BY COALESCE(nama_kimia, nama_barang)"
    )
    kimia_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("stok_kimia.html", stok_in=stok_in, stok_out=stok_out, kimia_list=kimia_list, today=date.today().isoformat())


# ==================== 10. STOK RP ====================
@app.route("/stok-rp", methods=["GET", "POST"])
def stok_rp():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "in":
            rp_id = request.form.get("rp_id")
            meter_roll = float(request.form.get("meter_roll") or 0)
            tanggal = request.form.get("tanggal") or date.today().isoformat()
            kode_internal = generate_code("BC-R")
            cur.execute(
                "INSERT INTO tbl_stok_rp_in (kode_internal, rp_id, meter_roll, qty_sisa, tanggal_in) VALUES (%s,%s,%s,%s,%s)",
                (kode_internal, rp_id, meter_roll, meter_roll, tanggal),
            )
            flash(f"Stok RP IN: {kode_internal}", "success")

        elif action == "out":
            stok_in_id = request.form.get("stok_in_id")
            meter_roll = float(request.form.get("meter_roll") or 0)
            kode_wip = request.form.get("kode_wip") or None
            tanggal = request.form.get("tanggal") or date.today().isoformat()

            cur.execute("SELECT * FROM tbl_stok_rp_in WHERE id=%s", (stok_in_id,))
            stok = cur.fetchone()
            if stok and float(stok["qty_sisa"]) >= meter_roll:
                cur.execute(
                    "INSERT INTO tbl_stok_rp_out (stok_in_id, rp_id, meter_roll, kode_wip, tanggal) VALUES (%s,%s,%s,%s,%s)",
                    (stok_in_id, stok["rp_id"], meter_roll, kode_wip, tanggal),
                )
                cur.execute(
                    "UPDATE tbl_stok_rp_in SET qty_sisa = qty_sisa - %s WHERE id=%s",
                    (meter_roll, stok_in_id),
                )
                flash("Stok RP OUT berhasil (FIFO).", "success")
            else:
                flash("Stok RP tidak cukup.", "danger")

        conn.commit()

    cur.execute(
        "SELECT si.*, COALESCE(mr.nama_rp, mr.nama_jenis) AS nama_jenis FROM tbl_stok_rp_in si "
        "JOIN master_rp mr ON mr.id = si.rp_id WHERE si.qty_sisa > 0 ORDER BY si.tanggal_in"
    )
    stok_in = cur.fetchall()
    cur.execute(
        "SELECT so.*, COALESCE(mr.nama_rp, mr.nama_jenis) AS nama_jenis FROM tbl_stok_rp_out so "
        "JOIN master_rp mr ON mr.id = so.rp_id ORDER BY so.created_at DESC LIMIT 50"
    )
    stok_out = cur.fetchall()
    cur.execute(
        "SELECT id, kode_rp, COALESCE(nama_rp, nama_jenis) AS nama_rp, deskripsi, satuan "
        "FROM master_rp ORDER BY kode_rp"
    )
    rp_list = cur.fetchall()
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


# ==================== MASTER KULIT ====================
@app.route("/master/kulit", methods=["GET", "POST"])
def master_kulit():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            kode_kulit = request.form.get("kode_kulit", "").strip()
            nama_kulit = request.form.get("nama_kulit", "").strip()
            thickness = request.form.get("thickness", "").strip() or None
            warna = request.form.get("warna", "").strip() or None
            if not kode_kulit or not nama_kulit:
                flash("Kode kulit dan nama kulit wajib diisi.", "danger")
            else:
                try:
                    cur.execute(
                        "INSERT INTO master_kulit (kode_kulit, nama_kulit, thickness, warna) VALUES (%s, %s, %s, %s)",
                        (kode_kulit, nama_kulit, thickness, warna),
                    )
                    conn.commit()
                    flash(f"Master kulit {kode_kulit} berhasil ditambahkan.", "success")
                except mysql.connector.IntegrityError:
                    flash(f"Kode kulit {kode_kulit} sudah ada.", "danger")

        elif action == "update":
            kulit_id = request.form.get("id")
            kode_kulit = request.form.get("kode_kulit", "").strip()
            nama_kulit = request.form.get("nama_kulit", "").strip()
            thickness = request.form.get("thickness", "").strip() or None
            warna = request.form.get("warna", "").strip() or None
            if not kode_kulit or not nama_kulit:
                flash("Kode kulit dan nama kulit wajib diisi.", "danger")
            else:
                try:
                    cur.execute(
                        "UPDATE master_kulit SET kode_kulit=%s, nama_kulit=%s, thickness=%s, warna=%s WHERE id=%s",
                        (kode_kulit, nama_kulit, thickness, warna, kulit_id),
                    )
                    conn.commit()
                    flash("Master kulit berhasil diperbarui.", "success")
                except mysql.connector.IntegrityError:
                    flash(f"Kode kulit {kode_kulit} sudah digunakan.", "danger")

        elif action == "delete":
            kulit_id = request.form.get("id")
            cur.execute("DELETE FROM master_kulit WHERE id=%s", (kulit_id,))
            conn.commit()
            flash("Master kulit berhasil dihapus.", "success")

    cur.execute("SELECT * FROM master_kulit ORDER BY kode_kulit")
    kulit_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("master_kulit.html", kulit_list=kulit_list)


@app.route("/master/rp", methods=["GET", "POST"])
def master_rp():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            kode_rp = request.form.get("kode_rp", "").strip()
            nama_rp = request.form.get("nama_rp", "").strip()
            deskripsi = request.form.get("deskripsi", "").strip() or None
            if not kode_rp or not nama_rp:
                flash("Kode RP dan Nama RP wajib diisi.", "danger")
            else:
                try:
                    cur.execute(
                        "INSERT INTO master_rp (kode_rp, nama_rp, deskripsi) VALUES (%s, %s, %s)",
                        (kode_rp, nama_rp, deskripsi),
                    )
                    conn.commit()
                    flash(f"Master RP {kode_rp} berhasil ditambahkan.", "success")
                except mysql.connector.IntegrityError:
                    flash(f"Kode RP {kode_rp} sudah ada.", "danger")

        elif action == "update":
            rp_id = request.form.get("id")
            kode_rp = request.form.get("kode_rp", "").strip()
            nama_rp = request.form.get("nama_rp", "").strip()
            deskripsi = request.form.get("deskripsi", "").strip() or None
            if not kode_rp or not nama_rp:
                flash("Kode RP dan Nama RP wajib diisi.", "danger")
            else:
                try:
                    cur.execute(
                        "UPDATE master_rp SET kode_rp=%s, nama_rp=%s, deskripsi=%s WHERE id=%s",
                        (kode_rp, nama_rp, deskripsi, rp_id),
                    )
                    conn.commit()
                    flash("Master RP berhasil diperbarui.", "success")
                except mysql.connector.IntegrityError:
                    flash(f"Kode RP {kode_rp} sudah digunakan.", "danger")

        elif action == "delete":
            rp_id = request.form.get("id")
            try:
                cur.execute("DELETE FROM master_rp WHERE id=%s", (rp_id,))
                conn.commit()
                flash("Master RP berhasil dihapus.", "success")
            except mysql.connector.Error:
                flash("Master RP tidak dapat dihapus karena masih digunakan di stok/usage.", "danger")

    cur.execute(
        "SELECT id, kode_rp, COALESCE(nama_rp, nama_jenis) AS nama_rp, deskripsi, created_at "
        "FROM master_rp ORDER BY kode_rp"
    )
    rp_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("master_rp.html", rp_list=rp_list)


@app.route("/master/kimia", methods=["GET", "POST"])
def master_kimia():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "create":
            kode_kimia = request.form.get("kode_kimia", "").strip()
            nama_kimia = request.form.get("nama_kimia", "").strip()
            deskripsi = request.form.get("deskripsi", "").strip() or None
            satuan = request.form.get("satuan", "kg").strip() or "kg"
            if not kode_kimia or not nama_kimia:
                flash("Kode kimia dan nama kimia wajib diisi.", "danger")
            else:
                try:
                    cur.execute(
                        "INSERT INTO master_kimia (kode_kimia, nama_kimia, deskripsi, satuan) "
                        "VALUES (%s, %s, %s, %s)",
                        (kode_kimia, nama_kimia, deskripsi, satuan),
                    )
                    conn.commit()
                    flash(f"Master kimia {kode_kimia} berhasil ditambahkan.", "success")
                except mysql.connector.IntegrityError:
                    flash(f"Kode kimia {kode_kimia} sudah ada.", "danger")

        elif action == "update":
            kimia_id = request.form.get("id")
            kode_kimia = request.form.get("kode_kimia", "").strip()
            nama_kimia = request.form.get("nama_kimia", "").strip()
            deskripsi = request.form.get("deskripsi", "").strip() or None
            satuan = request.form.get("satuan", "kg").strip() or "kg"
            if not kode_kimia or not nama_kimia:
                flash("Kode kimia dan nama kimia wajib diisi.", "danger")
            else:
                try:
                    cur.execute(
                        "UPDATE master_kimia SET kode_kimia=%s, nama_kimia=%s, deskripsi=%s, satuan=%s WHERE id=%s",
                        (kode_kimia, nama_kimia, deskripsi, satuan, kimia_id),
                    )
                    conn.commit()
                    flash("Master kimia berhasil diperbarui.", "success")
                except mysql.connector.IntegrityError:
                    flash(f"Kode kimia {kode_kimia} sudah digunakan.", "danger")

        elif action == "delete":
            kimia_id = request.form.get("id")
            try:
                cur.execute("DELETE FROM master_kimia WHERE id=%s", (kimia_id,))
                conn.commit()
                flash("Master kimia berhasil dihapus.", "success")
            except mysql.connector.Error:
                flash("Master kimia tidak dapat dihapus karena masih digunakan di stok.", "danger")

    cur.execute(
        "SELECT id, COALESCE(kode_kimia, kode_barang) AS kode_kimia, "
        "COALESCE(nama_kimia, nama_barang) AS nama_kimia, deskripsi, satuan, created_at "
        "FROM master_kimia ORDER BY kode_kimia"
    )
    kimia_list = cur.fetchall()
    cur.close()
    conn.close()
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


# ==================== MASTER ERP (dummy) ====================
@app.route("/master/erp")
def master_erp():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM master_erp ORDER BY thickness, color, emboss")
    erp_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("master_erp.html", erp_list=erp_list)


# ==================== MASTER MATERIAL LAIN ====================
@app.route("/master/material-lain", methods=["GET", "POST"])
def master_material_lain():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            kode = request.form.get("kode_material", "").strip()
            nama = request.form.get("nama_material", "").strip()
            deskripsi = request.form.get("deskripsi", "").strip() or None
            satuan = request.form.get("satuan", "pcs").strip() or "pcs"
            if kode and nama:
                try:
                    cur.execute(
                        "INSERT INTO master_material_lain (kode_material, nama_material, deskripsi, satuan) "
                        "VALUES (%s,%s,%s,%s)",
                        (kode, nama, deskripsi, satuan),
                    )
                    conn.commit()
                    flash(f"Material {kode} ditambahkan.", "success")
                except mysql.connector.IntegrityError:
                    flash("Kode material sudah ada.", "danger")
        elif action == "delete":
            cur.execute("DELETE FROM master_material_lain WHERE id=%s", (request.form.get("id"),))
            conn.commit()
            flash("Material dihapus.", "success")

    cur.execute("SELECT * FROM master_material_lain ORDER BY kode_material")
    material_list = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("master_material_lain.html", material_list=material_list)


# ==================== STOK MATERIAL LAIN ====================
@app.route("/stok-material-lain", methods=["GET", "POST"])
def stok_material_lain():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if request.method == "POST":
        action = request.form.get("action")
        if action == "in":
            material_id = request.form.get("material_id")
            qty = float(request.form.get("qty") or 0)
            tanggal = request.form.get("tanggal") or date.today().isoformat()
            kode_internal = generate_code("BC-M")
            cur.execute("SELECT satuan FROM master_material_lain WHERE id=%s", (material_id,))
            mat = cur.fetchone()
            cur.execute(
                "INSERT INTO tbl_stok_material_lain_in (kode_internal, material_id, qty, qty_sisa, satuan, tanggal_in) "
                "VALUES (%s,%s,%s,%s,%s,%s)",
                (kode_internal, material_id, qty, qty, mat["satuan"] if mat else "pcs", tanggal),
            )
            flash(f"Stok Material IN: {kode_internal}", "success")
        elif action == "out":
            stok_in_id = request.form.get("stok_in_id")
            qty = float(request.form.get("qty") or 0)
            tanggal = request.form.get("tanggal") or date.today().isoformat()
            kode_wip = request.form.get("kode_wip") or None
            cur.execute("SELECT * FROM tbl_stok_material_lain_in WHERE id=%s", (stok_in_id,))
            stok = cur.fetchone()
            if stok and stok["qty_sisa"] >= qty:
                cur.execute(
                    "INSERT INTO tbl_stok_material_lain_out (stok_in_id, material_id, qty, kode_wip, tanggal) "
                    "VALUES (%s,%s,%s,%s,%s)",
                    (stok_in_id, stok["material_id"], qty, kode_wip, tanggal),
                )
                cur.execute(
                    "UPDATE tbl_stok_material_lain_in SET qty_sisa=%s WHERE id=%s",
                    (float(stok["qty_sisa"]) - qty, stok_in_id),
                )
                flash("Stok Material OUT berhasil.", "success")
            else:
                flash("Stok tidak cukup.", "danger")
        conn.commit()

    cur.execute(
        "SELECT si.*, m.kode_material, m.nama_material FROM tbl_stok_material_lain_in si "
        "JOIN master_material_lain m ON m.id = si.material_id "
        "WHERE si.qty_sisa > 0 ORDER BY si.tanggal_in"
    )
    stok_in = cur.fetchall()
    cur.execute(
        "SELECT so.*, m.nama_material FROM tbl_stok_material_lain_out so "
        "JOIN master_material_lain m ON m.id = so.material_id ORDER BY so.created_at DESC LIMIT 50"
    )
    stok_out = cur.fetchall()
    cur.execute("SELECT id, kode_material, nama_material, satuan FROM master_material_lain ORDER BY kode_material")
    material_list = cur.fetchall()
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
    kode = request.args.get("q", "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT kode_material, nama_material, satuan FROM master_material_lain WHERE kode_material=%s",
        (kode,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return jsonify({"error": "Material tidak ditemukan"}), 404
    return jsonify(row)


@app.route("/usage-material-lain", methods=["GET", "POST"])
def usage_material_lain():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if request.method == "POST":
        kode_wip = request.form.get("kode_wip", "").strip()
        kode_material = request.form.get("kode_material", "").strip()
        qty_used = float(request.form.get("qty_used") or 0)
        satuan = request.form.get("satuan", "pcs")
        cur.execute("SELECT nama_material FROM master_material_lain WHERE kode_material=%s", (kode_material,))
        mat = cur.fetchone()
        cur.execute(
            "INSERT INTO tbl_usage_material_lain (kode_wip, kode_material, nama_material, qty_used, satuan) "
            "VALUES (%s,%s,%s,%s,%s)",
            (kode_wip, kode_material, mat["nama_material"] if mat else None, qty_used, satuan),
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
