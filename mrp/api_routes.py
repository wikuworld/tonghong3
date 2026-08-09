"""JSON API for Tonghong Vue UI — mounted at /api/mrp."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from flask import Blueprint, jsonify, request

from db import get_db_connection

api = Blueprint("mrp_api", __name__, url_prefix="/api/mrp")


def _serialize(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _row(row: dict | None):
    if not row:
        return None
    return {k: _serialize(v) for k, v in row.items()}


def _rows(rows):
    return [_row(r) for r in rows]


def _err(message: str, status: int = 400):
    return jsonify({"detail": message}), status


# ---- health ----
@api.get("/health")
def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"status": "ok", "database": "tonghong_mrp"})
    except Exception as e:
        return _err(f"db unavailable: {e}", 503)


# ---- palet / yl ----
@api.get("/palet/movements")
def palet_movements():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT m.*, (SELECT COUNT(*) FROM tbl_yl y WHERE y.kode_palet = m.kode_palet) AS jml_yl "
        "FROM tbl_palet_movement m ORDER BY m.created_at DESC LIMIT 100"
    )
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.post("/palet/in")
def palet_in():
    body = request.get_json(silent=True) or {}
    kode_palet = (body.get("kode_palet") or "").strip()
    if not kode_palet:
        return _err("kode_palet wajib")
    tanggal = body.get("tanggal") or date.today().isoformat()
    keterangan = body.get("keterangan") or ""
    items = body.get("items") or []

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "INSERT INTO tbl_palet_movement (kode_palet, direction, tanggal, keterangan) VALUES (%s,'IN',%s,%s)",
        (kode_palet, tanggal, keterangan),
    )
    for item in items:
        kode_yl = (item.get("kode_yl") or "").strip()
        if not kode_yl:
            continue
        thickness = item.get("thickness") or ""
        warna = item.get("warna") or ""
        qty = item.get("qty") or 0
        cur.execute(
            "INSERT INTO tbl_yl (kode_yl, kode_palet, thickness, warna, qty) "
            "VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE thickness=%s, warna=%s, qty=%s",
            (kode_yl, kode_palet, thickness, warna, qty, thickness, warna, qty),
        )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "kode_palet": kode_palet})


@api.post("/palet/out")
def palet_out():
    body = request.get_json(silent=True) or {}
    kode_palet = (body.get("kode_palet") or "").strip()
    if not kode_palet:
        return _err("kode_palet wajib")
    tanggal = body.get("tanggal") or date.today().isoformat()
    keterangan = body.get("keterangan") or ""
    clear_yl = body.get("clear_yl", True)

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS n FROM tbl_yl WHERE kode_palet=%s", (kode_palet,))
    n = int((cur.fetchone() or {}).get("n") or 0)
    cur.execute(
        "INSERT INTO tbl_palet_movement (kode_palet, direction, tanggal, keterangan) VALUES (%s,'OUT',%s,%s)",
        (kode_palet, tanggal, keterangan),
    )
    if clear_yl:
        cur.execute("DELETE FROM tbl_yl WHERE kode_palet=%s", (kode_palet,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "kode_palet": kode_palet, "yl_cleared": n if clear_yl else 0})


@api.get("/palet/<kode_palet>/yl")
def palet_yl(kode_palet):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_yl WHERE kode_palet = %s", (kode_palet,))
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.get("/yl")
def yl_list():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT kode_yl, kode_palet, thickness, warna, qty, created_at FROM tbl_yl "
        "ORDER BY kode_palet, kode_yl"
    )
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.get("/yl/movements")
def yl_movements():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_yl_movement ORDER BY created_at DESC LIMIT 100")
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.post("/yl/movement")
def yl_movement_create():
    body = request.get_json(silent=True) or {}
    kode_yl = (body.get("kode_yl") or "").strip()
    kode_palet = (body.get("kode_palet") or "").strip()
    direction = (body.get("direction") or "IN").upper()
    if direction not in ("IN", "OUT"):
        return _err("direction harus IN atau OUT")
    if not kode_yl or not kode_palet:
        return _err("kode_yl dan kode_palet wajib")
    thickness = body.get("thickness") or ""
    warna = body.get("warna") or ""
    qty = body.get("qty") or 0
    tanggal = body.get("tanggal") or date.today().isoformat()

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
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
    else:
        cur.execute(
            "SELECT id, qty FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s",
            (kode_palet, kode_yl),
        )
        row = cur.fetchone()
        if not row:
            conn.rollback()
            cur.close()
            conn.close()
            return _err("YL tidak ditemukan di stok palet", 404)
        qty_out = float(qty or 0)
        sisa = float(row["qty"] or 0) - qty_out
        if sisa <= 0:
            cur.execute("DELETE FROM tbl_yl WHERE id=%s", (row["id"],))
        else:
            cur.execute("UPDATE tbl_yl SET qty=%s WHERE id=%s", (sisa, row["id"]))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True})


# ---- masters ----
@api.get("/masters/erp")
def master_erp_list():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM master_erp ORDER BY id DESC LIMIT 500")
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.get("/masters/erp/options")
def master_erp_options():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT DISTINCT thickness FROM master_erp WHERE thickness IS NOT NULL AND thickness!='' ORDER BY thickness")
    thickness = [r["thickness"] for r in cur.fetchall()]
    cur.execute(
        "SELECT DISTINCT material_name FROM master_erp "
        "WHERE material_name IS NOT NULL AND material_name!='' ORDER BY material_name"
    )
    materials = [r["material_name"] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT color FROM master_erp WHERE color IS NOT NULL AND color!='' ORDER BY color")
    colors = [r["color"] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT emboss FROM master_erp WHERE emboss IS NOT NULL AND emboss!='' ORDER BY emboss")
    emboss = [r["emboss"] for r in cur.fetchall()]
    cur.execute(
        "SELECT DISTINCT customer FROM master_erp WHERE customer IS NOT NULL AND customer!='' ORDER BY customer"
    )
    customers = [r["customer"] for r in cur.fetchall()]
    cur.execute(
        "SELECT DISTINCT color_swatch FROM master_erp "
        "WHERE color_swatch IS NOT NULL AND color_swatch!='' ORDER BY color_swatch"
    )
    color_swatch = [r["color_swatch"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(
        {
            "thickness": thickness,
            "materials": materials,
            "colors": colors,
            "emboss": emboss,
            "customers": customers,
            "color_swatch": color_swatch,
        }
    )


@api.post("/masters/import/raw-material")
def masters_import_raw_material():
    """Upsert katalog dari Master Item Raw Material.xls (KULIT/KIMIA/RP/LAINNYA)."""
    import os
    import tempfile

    from raw_material_import import DEFAULT_XLS_PATH, import_raw_material_masters

    tmp_path = None
    path = None
    upload = request.files.get("file")
    if upload and upload.filename:
        suffix = os.path.splitext(upload.filename)[1] or ".xls"
        fd, tmp_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        upload.save(tmp_path)
        path = tmp_path
    else:
        body = request.get_json(silent=True) or {}
        path = (body.get("path") or "").strip() or DEFAULT_XLS_PATH

    conn = get_db_connection()
    try:
        try:
            result = import_raw_material_masters(conn, path=path)
        except FileNotFoundError as e:
            return _err(str(e), 404)
        except Exception as e:
            conn.rollback()
            return _err(f"Import gagal: {e}", 400)
        return jsonify(result)
    finally:
        conn.close()
        if tmp_path and os.path.isfile(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass



@api.get("/masters/kulit")
def master_kulit_list():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM master_kulit ORDER BY kode_kulit")
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.post("/masters/kulit")
def master_kulit_create():
    body = request.get_json(silent=True) or {}
    kode = (body.get("kode_kulit") or "").strip()
    nama = (body.get("nama_kulit") or "").strip()
    if not kode or not nama:
        return _err("kode_kulit dan nama_kulit wajib")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO master_kulit (kode_kulit, nama_kulit, thickness, warna) VALUES (%s,%s,%s,%s)",
            (kode, nama, body.get("thickness") or None, body.get("warna") or None),
        )
        conn.commit()
        new_id = cur.lastrowid
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(e), 409)
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "ok": True}), 201


@api.get("/masters/kimia")
def master_kimia_list():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM master_kimia ORDER BY id")
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.post("/masters/kimia")
def master_kimia_create():
    body = request.get_json(silent=True) or {}
    kode = (body.get("kode_kimia") or body.get("kode_barang") or "").strip()
    nama = (body.get("nama_kimia") or body.get("nama_barang") or body.get("nama") or "").strip()
    if not kode or not nama:
        return _err("kode dan nama kimia wajib")
    satuan = body.get("satuan") or "kg"
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO master_kimia (kode_barang, nama_barang, satuan, kode_kimia, nama_kimia) "
            "VALUES (%s,%s,%s,%s,%s)",
            (kode, nama, satuan, kode, nama),
        )
        conn.commit()
        new_id = cur.lastrowid
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(e), 409)
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "ok": True}), 201


@api.get("/masters/rp")
def master_rp_list():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM master_rp ORDER BY kode_rp")
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.post("/masters/rp")
def master_rp_create():
    body = request.get_json(silent=True) or {}
    kode = (body.get("kode_rp") or "").strip()
    nama = (body.get("nama_rp") or body.get("nama_jenis") or "").strip()
    if not kode or not nama:
        return _err("kode_rp dan nama_rp wajib")
    deskripsi = body.get("deskripsi") or None
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO master_rp (nama_jenis, satuan, kode_rp, nama_rp, deskripsi) "
            "VALUES (%s,%s,%s,%s,%s)",
            (nama, body.get("satuan") or "meter", kode, nama, deskripsi),
        )
        conn.commit()
        new_id = cur.lastrowid
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(e), 409)
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "ok": True}), 201


@api.get("/masters/treatment")
def master_treatment_list():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_master_treatment ORDER BY id")
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.get("/masters/po")
def master_po_list():
    from app import ensure_rencana_tables, ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    ensure_extended_tables(cur)
    conn.commit()
    status = (request.args.get("status") or "").strip()
    if status:
        cur.execute(
            "SELECT * FROM tbl_master_po WHERE status=%s ORDER BY no_po, item_name LIMIT 500",
            (status,),
        )
    else:
        cur.execute(
            "SELECT * FROM tbl_master_po WHERE status IN ('outstanding','partial') "
            "ORDER BY no_po, item_name LIMIT 500"
        )
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.post("/masters/po/sync")
def master_po_sync():
    """Upsert PO lines from Tonghong. Never overwrite qty_processed."""
    from app import ensure_rencana_tables, ensure_extended_tables

    body = request.get_json(silent=True) or {}
    items = body.get("items") or []
    if not items:
        return _err("items kosong")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    ensure_extended_tables(cur)
    conn.commit()

    inserted = 0
    updated = 0
    for item in items:
        no_po = (item.get("no_po") or "").strip()
        item_name = (item.get("item_name") or "").strip()
        warna = (item.get("warna") or "").strip()
        tebal = (item.get("tebal") or "").strip()
        emboss = (item.get("emboss") or "").strip()
        if not no_po or not item_name:
            continue
        no_so = (item.get("no_so") or "").strip() or None
        customer = (item.get("customer") or "").strip() or None
        color_swatch = (item.get("color_swatch") or "").strip() or None
        qty_order = float(item.get("qty_order") or item.get("sq_ft") or 0)
        sq_ft = float(item.get("sq_ft") or qty_order or 0)

        cur.execute(
            "SELECT id, qty_processed, status FROM tbl_master_po "
            "WHERE no_po=%s AND item_name=%s AND COALESCE(warna,'')=%s "
            "AND COALESCE(tebal,'')=%s AND COALESCE(emboss,'')=%s LIMIT 1",
            (no_po, item_name, warna, tebal, emboss),
        )
        existing = cur.fetchone()

        if existing:
            qty_processed = float(existing.get("qty_processed") or 0)
            if qty_processed >= qty_order > 0:
                status = "completed"
            elif qty_processed > 0:
                status = "partial"
            else:
                status = "outstanding"
            cur.execute(
                "UPDATE tbl_master_po SET no_so=%s, customer=%s, warna=%s, tebal=%s, emboss=%s, "
                "color_swatch=%s, sq_ft=%s, qty_order=%s, status=%s WHERE id=%s",
                (
                    no_so,
                    customer,
                    warna or None,
                    tebal or None,
                    emboss or None,
                    color_swatch,
                    sq_ft,
                    qty_order,
                    status,
                    existing["id"],
                ),
            )
            updated += 1
        else:
            cur.execute(
                "INSERT INTO tbl_master_po "
                "(no_po, no_so, customer, item_name, warna, tebal, emboss, color_swatch, "
                "sq_ft, qty_order, qty_processed, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,'outstanding')",
                (
                    no_po,
                    no_so,
                    customer,
                    item_name,
                    warna or None,
                    tebal or None,
                    emboss or None,
                    color_swatch,
                    sq_ft,
                    qty_order,
                ),
            )
            inserted += 1

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "inserted": inserted, "updated": updated, "total": len(items)})


# ---- rencana produksi ----
@api.get("/rencana-produksi")
def rencana_list():
    # import helpers from app lazily to reuse ensure_* / generate_code
    from app import ensure_rencana_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT id, kode_rencana, nama_rencana, tanggal_rencana, date_created, status "
        "FROM tbl_rencana_produksi ORDER BY COALESCE(tanggal_rencana, date_created) DESC, id DESC"
    )
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.get("/rencana-produksi/<int:rencana_id>")
def rencana_detail(rencana_id: int):
    from app import ensure_rencana_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_rencana_produksi WHERE id = %s", (rencana_id,))
    rencana = cur.fetchone()
    if not rencana:
        cur.close()
        conn.close()
        return _err("Rencana tidak ditemukan", 404)
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
    items = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify({"rencana": _row(rencana), "items": items})


@api.post("/rencana-produksi")
def rencana_create():
    from app import (
        _ensure_customer_id,
        _save_item_po_selections,
        ensure_extended_tables,
        ensure_rencana_tables,
        generate_code,
    )

    body = request.get_json(silent=True) or {}
    nama = (body.get("nama_rencana") or "").strip()
    tanggal = body.get("tanggal_rencana") or date.today().isoformat()
    items = body.get("items") or []
    if not nama:
        return _err("nama_rencana wajib")
    if not items:
        return _err("minimal satu item")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    ensure_extended_tables(cur)
    conn.commit()

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
        backer = item.get("backer") or (erp["backer"] if erp else None)
        customer_id = _ensure_customer_id(cur, customer_name)
        kode_item = generate_code("RPI")
        kode_wip = generate_code("WIP")
        cur.execute(
            "INSERT INTO tbl_rencana_item "
            "(rencana_id, kode_rencana_item, kode_lot_wip, customer_id, "
            "material_name, thickness, color, emboss, color_swatch, backer, keterangan, urutan) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                rencana_id,
                kode_item,
                kode_wip,
                customer_id,
                material_name,
                thickness,
                color,
                emboss,
                color_swatch,
                backer,
                (item.get("keterangan") or "").strip() or None,
                idx,
            ),
        )
        item_id = cur.lastrowid
        pos = item.get("pos") or []
        if pos:
            _save_item_po_selections(cur, item_id, pos)
        saved += 1

    if not saved:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(
            "Tidak ada item valid. Lengkapi Thickness, Material, Color, Emboss, Customer, Color Swatch."
        )

    cur.execute("UPDATE tbl_rencana_produksi SET status='active' WHERE id=%s", (rencana_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": rencana_id, "kode_rencana": kode_rencana, "ok": True}), 201


# ---- master treatment CRUD ----
@api.post("/masters/treatment")
def master_treatment_create():
    from app import ensure_master_treatment

    body = request.get_json(silent=True) or {}
    nama = (body.get("nama_treatment") or "").strip()
    jenis = (body.get("jenis") or "PU").strip()
    if jenis not in ("PU", "Suede"):
        return _err("jenis harus PU atau Suede")
    if not nama:
        return _err("nama_treatment wajib")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_master_treatment(cur)
    conn.commit()
    try:
        cur.execute(
            "INSERT INTO tbl_master_treatment (jenis, nama_treatment) VALUES (%s, %s)",
            (jenis, nama),
        )
        conn.commit()
        new_id = cur.lastrowid
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(e), 409)
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "ok": True}), 201


@api.put("/masters/treatment/<int:treatment_id>")
def master_treatment_update(treatment_id: int):
    from app import ensure_master_treatment

    body = request.get_json(silent=True) or {}
    nama = (body.get("nama_treatment") or "").strip()
    jenis = (body.get("jenis") or "PU").strip()
    if jenis not in ("PU", "Suede"):
        return _err("jenis harus PU atau Suede")
    if not nama:
        return _err("nama_treatment wajib")
    conn = get_db_connection()
    cur = conn.cursor()
    ensure_master_treatment(cur)
    try:
        cur.execute(
            "UPDATE tbl_master_treatment SET jenis=%s, nama_treatment=%s WHERE id=%s",
            (jenis, nama, treatment_id),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(e), 409)
    cur.close()
    conn.close()
    return jsonify({"ok": True})


@api.delete("/masters/treatment/<int:treatment_id>")
def master_treatment_delete(treatment_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tbl_master_treatment WHERE id=%s", (treatment_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True})


# ---- proses / persiapan kulit ----
@api.get("/proses/scan-rencana")
def proses_scan_rencana():
    kode = (request.args.get("q") or "").strip()
    if not kode:
        return _err("Kode kosong")
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
        return _err("Rencana produksi tidak ditemukan", 404)
    cur.execute(
        "SELECT po.no_po, po.item_name, p.qty_outstanding, p.qty_proses "
        "FROM tbl_rencana_item_po p "
        "JOIN tbl_master_po po ON po.id = p.po_id "
        "WHERE p.item_id = %s ORDER BY po.no_po",
        (item["id"],),
    )
    po_list = _rows(cur.fetchall())
    out = _row(item)
    out["po_list"] = po_list
    cur.close()
    conn.close()
    return jsonify(out)


@api.get("/proses")
def proses_list():
    from app import ensure_master_treatment

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_master_treatment(cur)
    conn.commit()
    cur.execute(
        "SELECT * FROM tbl_persiapan_kulit ORDER BY date_created DESC LIMIT 100"
    )
    persiapan_list = _rows(cur.fetchall())
    cur.execute(
        "SELECT i.id, i.kode_rencana_item, i.kode_lot_wip, i.thickness, i.color, i.emboss, "
        "r.nama_rencana, c.nama_customer "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        "JOIN master_customer c ON c.id = i.customer_id "
        "WHERE r.status IN ('draft','active') AND i.kode_lot_wip IS NOT NULL "
        "ORDER BY r.date_created DESC"
    )
    rencana_items = _rows(cur.fetchall())
    cur.execute(
        "SELECT jenis, nama_treatment FROM tbl_master_treatment ORDER BY jenis, nama_treatment"
    )
    treatments = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(
        {
            "persiapan_list": persiapan_list,
            "rencana_items": rencana_items,
            "treatments": treatments,
        }
    )


@api.post("/proses")
def proses_create():
    from app import ensure_master_treatment, generate_code

    body = request.get_json(silent=True) or {}
    item_id = body.get("rencana_item_id")
    kode_scan = (body.get("kode_scan") or "").strip()
    treatment_jenis = (body.get("treatment_jenis") or "PU").strip()
    selected = body.get("treatment_list") or []
    if isinstance(selected, str):
        selected = [s.strip() for s in selected.split(",") if s.strip()]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_master_treatment(cur)
    conn.commit()

    if not item_id and kode_scan:
        cur.execute(
            "SELECT i.id FROM tbl_rencana_item i "
            "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
            "WHERE i.kode_rencana_item = %s AND r.status IN ('draft','active')",
            (kode_scan,),
        )
        row = cur.fetchone()
        item_id = row["id"] if row else None
    if not item_id:
        cur.close()
        conn.close()
        return _err("Ketik / scan kode RPI terlebih dahulu.")
    if treatment_jenis not in ("PU", "Suede"):
        cur.close()
        conn.close()
        return _err("Pilih jenis PU atau Suede.")

    cur.execute(
        "SELECT i.*, r.kode_rencana FROM tbl_rencana_item i "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id WHERE i.id = %s",
        (item_id,),
    )
    item = cur.fetchone()
    if not item:
        cur.close()
        conn.close()
        return _err("Item rencana tidak ditemukan", 404)

    for tname in selected:
        cur.execute(
            "SELECT id FROM tbl_master_treatment WHERE nama_treatment = %s AND jenis = %s",
            (tname, treatment_jenis),
        )
        if not cur.fetchone():
            cur.close()
            conn.close()
            return _err(f"Treatment '{tname}' tidak sesuai jenis {treatment_jenis}.")

    cur.execute(
        "SELECT no_po FROM tbl_rencana_item_po p "
        "JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = %s LIMIT 1",
        (item_id,),
    )
    po_row = cur.fetchone()
    kode_proses = generate_code("PR")
    treatment_list_str = ", ".join(selected)
    cur.execute(
        "INSERT INTO tbl_persiapan_kulit "
        "(kode_wip, kode_rencana, kode_proses, rencana_item_id, no_po, warna, tebal, emboss, "
        "treatment_jenis, treatment_list, status) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'draft')",
        (
            item["kode_lot_wip"],
            item["kode_rencana_item"],
            kode_proses,
            item_id,
            po_row["no_po"] if po_row else "",
            item["color"],
            item["thickness"],
            item["emboss"],
            treatment_jenis,
            treatment_list_str,
        ),
    )
    persiapan_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": persiapan_id, "kode_proses": kode_proses, "ok": True}), 201


@api.get("/proses/<int:persiapan_id>")
def proses_detail_api(persiapan_id: int):
    from app import ensure_extended_tables, ensure_master_treatment

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    ensure_master_treatment(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_persiapan_kulit WHERE id = %s", (persiapan_id,))
    persiapan = cur.fetchone()
    if not persiapan:
        cur.close()
        conn.close()
        return _err("Data tidak ditemukan", 404)
    cur.execute(
        "SELECT * FROM tbl_persiapan_scan WHERE persiapan_id = %s ORDER BY created_at",
        (persiapan_id,),
    )
    scans = _rows(cur.fetchall())
    cur.execute(
        "SELECT * FROM tbl_persiapan_ukur WHERE persiapan_id = %s ORDER BY created_at",
        (persiapan_id,),
    )
    ukurs = _rows(cur.fetchall())
    cur.execute(
        "SELECT * FROM tbl_persiapan_reprint WHERE persiapan_id = %s ORDER BY reprint_ke",
        (persiapan_id,),
    )
    reprints = _rows(cur.fetchall())
    cur.execute(
        "SELECT * FROM tbl_persiapan_ky WHERE persiapan_id = %s ORDER BY created_at",
        (persiapan_id,),
    )
    ky_sessions = _rows(cur.fetchall())
    cur.execute(
        "SELECT id FROM tbl_persiapan_ky WHERE persiapan_id=%s AND status='active' LIMIT 1",
        (persiapan_id,),
    )
    active_ky = cur.fetchone()
    cur.execute(
        "SELECT jenis, nama_treatment FROM tbl_master_treatment ORDER BY jenis, nama_treatment"
    )
    treatments = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(
        {
            "persiapan": _row(persiapan),
            "scans": scans,
            "ukurs": ukurs,
            "reprints": reprints,
            "ky_sessions": ky_sessions,
            "active_ky": _row(active_ky) if active_ky else None,
            "treatments": treatments,
        }
    )


@api.get("/proses/<int:persiapan_id>/label")
def proses_label_api(persiapan_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_persiapan_kulit WHERE id = %s", (persiapan_id,))
    persiapan = cur.fetchone()
    cur.close()
    conn.close()
    if not persiapan:
        return _err("Data tidak ditemukan", 404)
    return jsonify({"persiapan": _row(persiapan)})


@api.post("/proses/<int:persiapan_id>/actions")
def proses_actions(persiapan_id: int):
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    action = (body.get("action") or "").strip()
    if not action:
        return _err("action wajib")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_persiapan_kulit WHERE id = %s", (persiapan_id,))
    persiapan = cur.fetchone()
    if not persiapan:
        cur.close()
        conn.close()
        return _err("Data tidak ditemukan", 404)

    msg = "ok"
    if action == "start":
        cur.execute(
            "UPDATE tbl_persiapan_kulit SET status='started' WHERE id=%s", (persiapan_id,)
        )
        msg = "Proses dimulai"

    elif action == "scan_ky":
        kode_palet = (body.get("kode_palet") or "").strip()
        kode_yl = (body.get("kode_yl") or "").strip()
        target_qty = float(body.get("target_qty") or 0)
        cur.execute(
            "SELECT id FROM tbl_persiapan_ky WHERE persiapan_id=%s AND status='active'",
            (persiapan_id,),
        )
        if cur.fetchone():
            cur.close()
            conn.close()
            return _err("Selesaikan KY aktif terlebih dahulu.")
        if not kode_palet:
            cur.close()
            conn.close()
            return _err("Kode KY wajib diisi.")
        if kode_yl:
            cur.execute(
                "SELECT id FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
                (kode_palet, kode_yl),
            )
        else:
            cur.execute(
                "SELECT id FROM tbl_yl WHERE kode_palet=%s LIMIT 1",
                (kode_palet,),
            )
        if not cur.fetchone():
            cur.close()
            conn.close()
            return _err("KY/YL tidak ada di stok palet. Lakukan Palet IN dulu.", 404)
        cur.execute(
            "INSERT INTO tbl_persiapan_ky (persiapan_id, kode_palet, kode_yl, target_qty, status) "
            "VALUES (%s,%s,%s,%s,'active')",
            (persiapan_id, kode_palet, kode_yl or None, target_qty),
        )
        cur.execute(
            "INSERT INTO tbl_persiapan_scan (persiapan_id, kode_palet, kode_yl) VALUES (%s,%s,%s)",
            (persiapan_id, kode_palet, kode_yl or None),
        )
        msg = f"KY {kode_palet} aktif"

    elif action == "add_ukur":
        ky_id = body.get("ky_id")
        size_val = float(body.get("size_val") or 0)
        if not ky_id or not size_val:
            cur.close()
            conn.close()
            return _err("ky_id dan size_val wajib")
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
        msg = "Ukur ditambahkan"

    elif action == "selesai_ky":
        ky_id = body.get("ky_id")
        cur.execute(
            "SELECT * FROM tbl_persiapan_ky WHERE id=%s AND persiapan_id=%s",
            (ky_id, persiapan_id),
        )
        ky = cur.fetchone()
        if not ky:
            cur.close()
            conn.close()
            return _err("KY tidak ditemukan", 404)
        target = float(ky["target_qty"] or 0)
        actual = float(ky["actual_qty"] or 0)
        selisih = actual - target
        cur.execute("UPDATE tbl_persiapan_ky SET status='selesai' WHERE id=%s", (ky_id,))
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
        msg = f"KY selesai. Target: {target}, Aktual: {actual}"

    elif action == "scan":
        kode_palet = (body.get("kode_palet") or "").strip()
        kode_yl = (body.get("kode_yl") or "").strip()
        size_val = body.get("size_val")
        cur.execute(
            "INSERT INTO tbl_persiapan_scan (persiapan_id, kode_palet, kode_yl) VALUES (%s,%s,%s)",
            (persiapan_id, kode_palet, kode_yl),
        )
        if size_val:
            cur.execute(
                "INSERT INTO tbl_persiapan_ukur (persiapan_id, size_val) VALUES (%s,%s)",
                (persiapan_id, float(size_val)),
            )
            cur.execute(
                "UPDATE tbl_persiapan_kulit SET total_size = total_size + %s WHERE id=%s",
                (float(size_val), persiapan_id),
            )
        msg = "Scan tersimpan"

    elif action == "delete_ukur":
        ukur_id = body.get("ukur_id")
        cur.execute(
            "SELECT size_val, ky_id FROM tbl_persiapan_ukur WHERE id=%s AND persiapan_id=%s",
            (ukur_id, persiapan_id),
        )
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
        msg = "Ukur dihapus"

    elif action == "save":
        cur.execute(
            "UPDATE tbl_persiapan_kulit SET status='saved', date_saved=NOW() WHERE id=%s",
            (persiapan_id,),
        )
        msg = "Data tersimpan. Label siap dicetak."

    elif action == "reprint":
        cur.execute(
            "SELECT COALESCE(MAX(reprint_ke),0)+1 AS nxt FROM tbl_persiapan_reprint WHERE persiapan_id=%s",
            (persiapan_id,),
        )
        reprint_ke = cur.fetchone()["nxt"]
        cur.execute(
            "INSERT INTO tbl_persiapan_reprint (persiapan_id, reprint_ke) VALUES (%s,%s)",
            (persiapan_id, reprint_ke),
        )
        msg = f"Reprint ke-{reprint_ke} dicatat."

    else:
        cur.close()
        conn.close()
        return _err(f"action tidak dikenal: {action}")

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "message": msg})


# ---- lab ----
@api.get("/lab/options")
def lab_options():
    from app import ensure_lab_tables, ensure_rencana_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_lab_tables(cur)
    ensure_rencana_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT ri.id, ri.kode_rencana_item, ri.kode_kulit, ri.color, ri.thickness, "
        "rp.nama_rencana, rp.tanggal_rencana, c.nama_customer "
        "FROM tbl_rencana_item ri "
        "JOIN tbl_rencana_produksi rp ON rp.id = ri.rencana_id "
        "JOIN master_customer c ON c.id = ri.customer_id "
        "ORDER BY rp.tanggal_rencana DESC, ri.urutan"
    )
    rencana_items = _rows(cur.fetchall())
    cur.execute(
        "SELECT COALESCE(kode_kimia, kode_barang) AS kode_kimia, "
        "COALESCE(nama_kimia, nama_barang) AS nama_kimia, satuan "
        "FROM master_kimia ORDER BY kode_kimia"
    )
    kimia_list = _rows(cur.fetchall())
    try:
        cur.execute("SELECT nama_resep FROM master_resep ORDER BY nama_resep")
        reseps = [r["nama_resep"] for r in cur.fetchall()]
    except Exception:
        reseps = []
    cur.close()
    conn.close()
    return jsonify(
        {"rencana_items": rencana_items, "kimia_list": kimia_list, "reseps": reseps}
    )


@api.get("/lab")
def lab_list():
    from app import ensure_lab_tables, ensure_rencana_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_lab_tables(cur)
    ensure_rencana_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT l.kode_lot_warna, l.nama_lot_warna, l.status, l.date_created, l.rencana_item_id, "
        "d.kode_kimia, d.nama_kimia, d.resep, d.satuan, d.qty, d.remarks, "
        "ri.kode_rencana_item, rp.nama_rencana, rp.tanggal_rencana, c.nama_customer "
        "FROM tbl_lab_lot l "
        "JOIN tbl_lab_lot_detail d ON d.kode_lot_warna = l.kode_lot_warna "
        "LEFT JOIN tbl_rencana_item ri ON ri.id = l.rencana_item_id "
        "LEFT JOIN tbl_rencana_produksi rp ON rp.id = ri.rencana_id "
        "LEFT JOIN master_customer c ON c.id = ri.customer_id "
        "ORDER BY COALESCE(rp.tanggal_rencana, l.date_created) DESC, l.kode_lot_warna, d.id DESC "
        "LIMIT 200"
    )
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.post("/lab")
def lab_create():
    from app import ensure_lab_tables, ensure_rencana_tables, generate_code

    body = request.get_json(silent=True) or {}
    nama_lot_warna = (body.get("nama_lot_warna") or "").strip()
    rencana_item_id = body.get("rencana_item_id") or None
    rows_in = body.get("items") or []
    if not nama_lot_warna:
        return _err("Nama Lot Warna wajib diisi.")
    rows = [
        r
        for r in rows_in
        if (r.get("kode_kimia") or "").strip()
    ]
    if not rows:
        return _err("Minimal satu chemical harus diisi.")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_lab_tables(cur)
    ensure_rencana_tables(cur)
    conn.commit()
    # ensure rencana_item_id column
    from app import _col_names

    lab_cols = _col_names(cur, "tbl_lab_lot")
    if "rencana_item_id" not in lab_cols:
        cur.execute(
            "ALTER TABLE tbl_lab_lot ADD COLUMN rencana_item_id INT DEFAULT NULL"
        )
        conn.commit()

    kode_lot_warna = generate_code("LW")
    cur.execute(
        "INSERT INTO tbl_lab_lot (kode_lot_warna, nama_lot_warna, rencana_item_id) VALUES (%s, %s, %s)",
        (kode_lot_warna, nama_lot_warna, rencana_item_id),
    )
    for r in rows:
        kode_kimia = (r.get("kode_kimia") or "").strip()
        resep = (r.get("resep") or "").strip() or None
        satuan = (r.get("satuan") or "kg").strip() or "kg"
        qty = r.get("qty") or 0
        remarks = (r.get("remarks") or "").strip() or None
        cur.execute(
            "SELECT COALESCE(nama_kimia, nama_barang) AS nama_kimia "
            "FROM master_kimia WHERE COALESCE(kode_kimia, kode_barang) = %s",
            (kode_kimia,),
        )
        kimia = cur.fetchone()
        cur.execute(
            "INSERT INTO tbl_lab_lot_detail "
            "(kode_lot_warna, kode_kimia, nama_kimia, resep, satuan, qty, remarks) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                kode_lot_warna,
                kode_kimia,
                kimia["nama_kimia"] if kimia else kode_kimia,
                resep,
                satuan,
                qty,
                remarks,
            ),
        )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "kode_lot_warna": kode_lot_warna}), 201


# ---- packing FG ----
@api.get("/packing/scan-wip")
def packing_scan_wip():
    kode_wip = (request.args.get("q") or "").strip()
    if not kode_wip:
        return _err("Kode WIP kosong")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT pk.* FROM tbl_persiapan_kulit pk "
        "WHERE pk.kode_wip = %s AND pk.status IN ('saved','completed')",
        (kode_wip,),
    )
    wip_data = _rows(cur.fetchall())
    if not wip_data:
        cur.close()
        conn.close()
        return _err("WIP tidak ditemukan atau belum saved/completed", 404)
    cur.execute(
        "SELECT i.id AS item_id, po.no_po, po.no_so, po.item_name, po.customer, "
        "p.qty_proses AS qty_sq "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_item_po p ON p.item_id = i.id "
        "JOIN tbl_master_po po ON po.id = p.po_id "
        "WHERE i.kode_lot_wip = %s",
        (kode_wip,),
    )
    po_list = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify({"kode_wip": kode_wip, "wip_data": wip_data, "po_list": po_list})


@api.get("/packing/history")
def packing_history_api():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_packing ORDER BY date_created DESC")
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.get("/packing")
def packing_list():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    limit = 500 if request.args.get("all") in ("1", "true", "yes") else 100
    cur.execute(
        "SELECT * FROM tbl_packing ORDER BY date_created DESC LIMIT %s", (limit,)
    )
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.post("/packing")
def packing_start():
    from app import ensure_extended_tables, generate_code

    body = request.get_json(silent=True) or {}
    kode_wip = (body.get("kode_wip") or "").strip()
    no_po = (body.get("no_po") or "").strip()
    no_so = (body.get("no_so") or "").strip()
    customer = (body.get("customer") or "").strip()
    qty_sq = body.get("qty_sq") or 0
    if not kode_wip or not no_po:
        return _err("kode_wip dan no_po wajib")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT id FROM tbl_persiapan_kulit "
        "WHERE kode_wip = %s AND status IN ('saved','completed') LIMIT 1",
        (kode_wip,),
    )
    if not cur.fetchone():
        cur.close()
        conn.close()
        return _err("WIP tidak valid / belum saved", 404)

    kode_packing = generate_code("FG")
    cur.execute(
        "INSERT INTO tbl_packing (kode_packing, kode_wip, no_po, customer, status) "
        "VALUES (%s,%s,%s,%s,'in_progress')",
        (kode_packing, kode_wip, no_po, customer),
    )
    packing_id = cur.lastrowid
    cur.execute(
        "INSERT INTO tbl_packing_po (packing_id, no_po, no_so, qty_sq) VALUES (%s,%s,%s,%s)",
        (packing_id, no_po, no_so, qty_sq),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": packing_id, "kode_packing": kode_packing, "ok": True}), 201


@api.get("/packing/<int:packing_id>")
def packing_detail_api(packing_id: int):
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_packing WHERE id = %s", (packing_id,))
    packing = cur.fetchone()
    if not packing:
        cur.close()
        conn.close()
        return _err("Packing tidak ditemukan", 404)
    cur.execute(
        "SELECT * FROM tbl_packing_roll WHERE packing_id = %s ORDER BY roll_no",
        (packing_id,),
    )
    rolls = _rows(cur.fetchall())
    cur.execute("SELECT * FROM tbl_packing_po WHERE packing_id = %s", (packing_id,))
    packing_pos = _rows(cur.fetchall())
    cur.execute(
        "SELECT i.id AS item_id, po.no_po, po.no_so, po.item_name, po.customer, "
        "p.qty_proses AS qty_sq "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_item_po p ON p.item_id = i.id "
        "JOIN tbl_master_po po ON po.id = p.po_id "
        "WHERE i.kode_lot_wip = %s",
        (packing["kode_wip"],),
    )
    available_pos = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(
        {
            "packing": _row(packing),
            "rolls": rolls,
            "packing_pos": packing_pos,
            "available_pos": available_pos,
        }
    )


@api.get("/packing/<int:packing_id>/print")
def packing_print_api(packing_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_packing WHERE id = %s", (packing_id,))
    packing = cur.fetchone()
    if not packing:
        cur.close()
        conn.close()
        return _err("Packing tidak ditemukan", 404)
    cur.execute(
        "SELECT * FROM tbl_packing_roll WHERE packing_id = %s ORDER BY roll_no",
        (packing_id,),
    )
    rolls = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify({"packing": _row(packing), "rolls": rolls})


@api.post("/packing/<int:packing_id>/actions")
def packing_actions(packing_id: int):
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    action = (body.get("action") or "").strip()
    if not action:
        return _err("action wajib")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_packing WHERE id = %s", (packing_id,))
    packing = cur.fetchone()
    if not packing:
        cur.close()
        conn.close()
        return _err("Packing tidak ditemukan", 404)
    if packing["status"] == "finished" and action != "finish":
        # allow idempotent finish; block mutations after finished
        if action != "finish":
            cur.close()
            conn.close()
            return _err("Packing sudah finished")

    msg = "ok"
    if action == "add_roll":
        if packing["status"] == "finished":
            cur.close()
            conn.close()
            return _err("Packing sudah finished")
        lembar = int(body.get("lembar") or 1)
        ukuran = float(body.get("ukuran") or 0)
        cur.execute(
            "SELECT COALESCE(MAX(roll_no),0)+1 AS nxt FROM tbl_packing_roll WHERE packing_id=%s",
            (packing_id,),
        )
        roll_no = cur.fetchone()["nxt"]
        cur.execute(
            "INSERT INTO tbl_packing_roll (packing_id, roll_no, lembar, ukuran) VALUES (%s,%s,%s,%s)",
            (packing_id, roll_no, lembar, ukuran),
        )
        cur.execute(
            "UPDATE tbl_packing SET total_lembar=total_lembar+%s, total_ukuran=total_ukuran+%s WHERE id=%s",
            (lembar, ukuran, packing_id),
        )
        msg = f"Roll #{roll_no} ditambahkan"

    elif action == "delete_roll":
        if packing["status"] == "finished":
            cur.close()
            conn.close()
            return _err("Packing sudah finished")
        roll_id = body.get("roll_id")
        cur.execute(
            "SELECT lembar, ukuran FROM tbl_packing_roll WHERE id=%s AND packing_id=%s",
            (roll_id, packing_id),
        )
        roll = cur.fetchone()
        if roll:
            cur.execute("DELETE FROM tbl_packing_roll WHERE id=%s", (roll_id,))
            cur.execute(
                "UPDATE tbl_packing SET total_lembar=GREATEST(total_lembar-%s,0), "
                "total_ukuran=GREATEST(total_ukuran-%s,0) WHERE id=%s",
                (roll["lembar"], roll["ukuran"], packing_id),
            )
        msg = "Roll dihapus"

    elif action == "add_po":
        if packing["status"] == "finished":
            cur.close()
            conn.close()
            return _err("Packing sudah finished")
        no_po = (body.get("no_po") or "").strip()
        no_so = (body.get("no_so") or "").strip()
        qty_sq = float(body.get("qty_sq") or 0)
        if not no_po:
            cur.close()
            conn.close()
            return _err("no_po wajib")
        cur.execute(
            "INSERT INTO tbl_packing_po (packing_id, no_po, no_so, qty_sq) VALUES (%s,%s,%s,%s)",
            (packing_id, no_po, no_so, qty_sq),
        )
        msg = "PO ditambahkan"

    elif action == "delete_po":
        if packing["status"] == "finished":
            cur.close()
            conn.close()
            return _err("Packing sudah finished")
        po_row_id = body.get("po_row_id")
        cur.execute(
            "DELETE FROM tbl_packing_po WHERE id=%s AND packing_id=%s",
            (po_row_id, packing_id),
        )
        msg = "PO dihapus"

    elif action == "finish":
        if packing["status"] != "finished":
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
                packing_id,
                pkg["kode_packing"],
                pkg["kode_wip"],
                pkg["customer"],
                pkg["total_lembar"],
                pkg["total_ukuran"],
            ),
        )
        msg = "Finish Good selesai. Masuk Gudang FG."

    else:
        cur.close()
        conn.close()
        return _err(f"action tidak dikenal: {action}")

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "message": msg})


# ---- gudang FG ----
@api.get("/gudang-fg")
def gudang_fg_list():
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_gudang_fg ORDER BY date_in DESC LIMIT 100")
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.get("/gudang-fg/<int:fg_id>")
def gudang_fg_detail(fg_id: int):
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_gudang_fg WHERE id=%s", (fg_id,))
    fg = cur.fetchone()
    if not fg:
        cur.close()
        conn.close()
        return _err("Data tidak ditemukan", 404)
    cur.execute("SELECT * FROM tbl_packing WHERE id=%s", (fg["packing_id"],))
    packing = cur.fetchone()
    cur.execute(
        "SELECT * FROM tbl_packing_roll WHERE packing_id=%s ORDER BY roll_no",
        (fg["packing_id"],),
    )
    rolls = _rows(cur.fetchall())
    cur.execute("SELECT * FROM tbl_packing_po WHERE packing_id=%s", (fg["packing_id"],))
    packing_pos = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(
        {
            "fg": _row(fg),
            "packing": _row(packing),
            "rolls": rolls,
            "packing_pos": packing_pos,
        }
    )


@api.post("/gudang-fg/out")
def gudang_fg_out():
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    kode_packing = (body.get("kode_packing") or "").strip()
    keterangan = body.get("keterangan") or ""
    if not kode_packing:
        return _err("kode_packing wajib")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT * FROM tbl_gudang_fg WHERE kode_packing=%s AND status='in_stock'",
        (kode_packing,),
    )
    fg = cur.fetchone()
    if not fg:
        cur.close()
        conn.close()
        return _err("Kode Packing List tidak ditemukan atau sudah OUT", 404)
    cur.execute(
        "UPDATE tbl_gudang_fg SET status='out', date_out=NOW(), keterangan_out=%s WHERE id=%s",
        (keterangan, fg["id"]),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "id": fg["id"], "kode_packing": kode_packing})


# ---- P4: stok kimia / stok RP ----
@api.get("/stok-kimia")
def stok_kimia_list():
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT si.*, COALESCE(mk.nama_kimia, mk.nama_barang) AS nama_barang, "
        "COALESCE(mk.kode_kimia, mk.kode_barang) AS kode_barang FROM tbl_stok_kimia_in si "
        "JOIN master_kimia mk ON mk.id = si.kimia_id WHERE si.qty_sisa > 0 ORDER BY si.tanggal_in"
    )
    stok_in = _rows(cur.fetchall())
    cur.execute(
        "SELECT so.*, COALESCE(mk.nama_kimia, mk.nama_barang) AS nama_barang FROM tbl_stok_kimia_out so "
        "JOIN master_kimia mk ON mk.id = so.kimia_id ORDER BY so.created_at DESC LIMIT 50"
    )
    stok_out = _rows(cur.fetchall())
    cur.execute(
        "SELECT id, COALESCE(kode_kimia, kode_barang) AS kode_barang, "
        "COALESCE(nama_kimia, nama_barang) AS nama_barang, satuan "
        "FROM master_kimia ORDER BY COALESCE(nama_kimia, nama_barang)"
    )
    kimia_list = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify({"stok_in": stok_in, "stok_out": stok_out, "kimia_list": kimia_list})


@api.post("/stok-kimia")
def stok_kimia_action():
    from app import ensure_extended_tables, generate_code
    from datetime import timedelta

    body = request.get_json(silent=True) or {}
    action = (body.get("action") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if action == "in":
        kimia_id = body.get("kimia_id")
        qty = float(body.get("qty") or 0)
        if not kimia_id or qty <= 0:
            cur.close()
            conn.close()
            return _err("kimia_id dan qty wajib")
        jumlah_kemasan = int(body.get("jumlah_kemasan") or 0) or None
        tanggal = body.get("tanggal") or date.today().isoformat()
        kode_internal = generate_code("BC-K")
        cur.execute("SELECT expired_days FROM master_kimia WHERE id=%s", (kimia_id,))
        kimia = cur.fetchone()
        days = kimia["expired_days"] if kimia and kimia.get("expired_days") is not None else 365
        expired = date.today() + timedelta(days=int(days))
        cur.execute(
            "INSERT INTO tbl_stok_kimia_in (kode_internal, kimia_id, qty, qty_sisa, jumlah_kemasan, tanggal_in, expired_date, gudang) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,'kimia')",
            (kode_internal, kimia_id, qty, qty, jumlah_kemasan, tanggal, expired),
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True, "kode_internal": kode_internal}), 201

    if action == "out":
        stok_in_id = body.get("stok_in_id")
        qty = float(body.get("qty") or 0)
        if not stok_in_id or qty <= 0:
            cur.close()
            conn.close()
            return _err("stok_in_id dan qty wajib")
        jumlah_kemasan = int(body.get("jumlah_kemasan") or 0) or None
        tujuan = body.get("tujuan") or "mixing"
        kode_wip = body.get("kode_wip") or None
        tanggal = body.get("tanggal") or date.today().isoformat()
        cur.execute("SELECT * FROM tbl_stok_kimia_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok or float(stok["qty_sisa"]) < qty:
            cur.close()
            conn.close()
            return _err("Stok tidak cukup", 400)
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
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True})

    cur.close()
    conn.close()
    return _err("action harus in atau out")


@api.get("/stok-rp")
def stok_rp_list():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT si.*, COALESCE(mr.nama_rp, mr.nama_jenis) AS nama_jenis FROM tbl_stok_rp_in si "
        "JOIN master_rp mr ON mr.id = si.rp_id WHERE si.qty_sisa > 0 ORDER BY si.tanggal_in"
    )
    stok_in = _rows(cur.fetchall())
    cur.execute(
        "SELECT so.*, COALESCE(mr.nama_rp, mr.nama_jenis) AS nama_jenis FROM tbl_stok_rp_out so "
        "JOIN master_rp mr ON mr.id = so.rp_id ORDER BY so.created_at DESC LIMIT 50"
    )
    stok_out = _rows(cur.fetchall())
    cur.execute(
        "SELECT id, kode_rp, COALESCE(nama_rp, nama_jenis) AS nama_rp, deskripsi, satuan "
        "FROM master_rp ORDER BY kode_rp"
    )
    rp_list = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify({"stok_in": stok_in, "stok_out": stok_out, "rp_list": rp_list})


@api.post("/stok-rp")
def stok_rp_action():
    from app import generate_code

    body = request.get_json(silent=True) or {}
    action = (body.get("action") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if action == "in":
        rp_id = body.get("rp_id")
        meter_roll = float(body.get("meter_roll") or body.get("qty") or 0)
        if not rp_id or meter_roll <= 0:
            cur.close()
            conn.close()
            return _err("rp_id dan meter_roll wajib")
        tanggal = body.get("tanggal") or date.today().isoformat()
        kode_internal = generate_code("BC-R")
        cur.execute(
            "INSERT INTO tbl_stok_rp_in (kode_internal, rp_id, meter_roll, qty_sisa, tanggal_in) VALUES (%s,%s,%s,%s,%s)",
            (kode_internal, rp_id, meter_roll, meter_roll, tanggal),
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True, "kode_internal": kode_internal}), 201

    if action == "out":
        stok_in_id = body.get("stok_in_id")
        meter_roll = float(body.get("meter_roll") or body.get("qty") or 0)
        if not stok_in_id or meter_roll <= 0:
            cur.close()
            conn.close()
            return _err("stok_in_id dan meter_roll wajib")
        kode_wip = body.get("kode_wip") or None
        tanggal = body.get("tanggal") or date.today().isoformat()
        cur.execute("SELECT * FROM tbl_stok_rp_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok or float(stok["qty_sisa"]) < meter_roll:
            cur.close()
            conn.close()
            return _err("Stok RP tidak cukup", 400)
        cur.execute(
            "INSERT INTO tbl_stok_rp_out (stok_in_id, rp_id, meter_roll, kode_wip, tanggal) VALUES (%s,%s,%s,%s,%s)",
            (stok_in_id, stok["rp_id"], meter_roll, kode_wip, tanggal),
        )
        cur.execute(
            "UPDATE tbl_stok_rp_in SET qty_sisa = qty_sisa - %s WHERE id=%s",
            (meter_roll, stok_in_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True})

    cur.close()
    conn.close()
    return _err("action harus in atau out")


# ---- P4: usage color / rp ----
@api.get("/usage-color/scan-lot")
def usage_color_scan_lot():
    kode = (request.args.get("q") or "").strip()
    if not kode:
        return _err("Kode kosong")
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
        return _err("Kode lot warna tidak ditemukan", 404)
    if lot.get("status") != "active":
        return _err("Lot warna tidak aktif", 400)
    return jsonify(_row(lot))


@api.get("/usage-color")
def usage_color_list():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_usage_color ORDER BY date_created DESC LIMIT 100")
    usage_list = _rows(cur.fetchall())
    cur.execute(
        "SELECT DISTINCT kode_lot_wip AS kode_wip FROM tbl_rencana_item "
        "WHERE kode_lot_wip IS NOT NULL AND kode_lot_wip != '' "
        "ORDER BY kode_lot_wip DESC"
    )
    wip_list = [r["kode_wip"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"usage_list": usage_list, "wip_list": wip_list})


@api.post("/usage-color")
def usage_color_create():
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    kode_wip = (body.get("kode_wip") or "").strip()
    kode_lot_warna = (body.get("kode_lot_warna") or "").strip()
    qty_digunakan = float(body.get("qty_digunakan") or 0)
    stok_in_id = body.get("stok_in_id")
    if not kode_wip or not kode_lot_warna:
        return _err("kode_wip dan kode_lot_warna wajib")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_lab_lot WHERE kode_lot_warna = %s", (kode_lot_warna,))
    lot = cur.fetchone()
    if not lot:
        cur.close()
        conn.close()
        return _err("Kode lot warna tidak ditemukan", 404)
    if lot.get("status") != "active":
        cur.close()
        conn.close()
        return _err("Lot warna tidak aktif", 400)
    cur.execute(
        "SELECT COALESCE(SUM(qty), 0) AS total_qty FROM tbl_lab_lot_detail WHERE kode_lot_warna = %s",
        (kode_lot_warna,),
    )
    total = cur.fetchone()
    qty_pembuatan = float(total["total_qty"] or 0)
    if stok_in_id:
        cur.execute("SELECT * FROM tbl_stok_kimia_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok or float(stok["qty_sisa"]) < qty_digunakan:
            cur.close()
            conn.close()
            return _err("Stok kimia tidak cukup untuk usage", 400)
        cur.execute(
            "INSERT INTO tbl_stok_kimia_out (stok_in_id, kimia_id, qty, jumlah_kemasan, tujuan, kode_wip, tanggal) "
            "VALUES (%s,%s,%s,NULL,'produksi',%s,%s)",
            (stok_in_id, stok["kimia_id"], qty_digunakan, kode_wip, date.today().isoformat()),
        )
        cur.execute(
            "UPDATE tbl_stok_kimia_in SET qty_sisa=%s WHERE id=%s",
            (float(stok["qty_sisa"]) - qty_digunakan, stok_in_id),
        )
    cur.execute(
        "INSERT INTO tbl_usage_color (kode_wip, kode_lot_warna, nama_warna, qty_pembuatan, qty_digunakan) "
        "VALUES (%s,%s,%s,%s,%s)",
        (kode_wip, kode_lot_warna, lot["nama_lot_warna"], qty_pembuatan, qty_digunakan),
    )
    new_id = cur.lastrowid
    cur.execute(
        "SELECT COALESCE(SUM(qty_digunakan),0) AS used FROM tbl_usage_color WHERE kode_lot_warna=%s",
        (kode_lot_warna,),
    )
    used = float((cur.fetchone() or {}).get("used") or 0)
    if qty_pembuatan > 0 and used >= qty_pembuatan:
        cur.execute(
            "UPDATE tbl_lab_lot SET status='used' WHERE kode_lot_warna=%s",
            (kode_lot_warna,),
        )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "id": new_id, "stok_deducted": bool(stok_in_id)}), 201


@api.get("/usage-rp/scan-rp")
def usage_rp_scan():
    kode = (request.args.get("q") or "").strip()
    if not kode:
        return _err("Kode kosong")
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
        return _err("Jenis RP tidak ditemukan", 404)
    return jsonify(_row(rp))


@api.get("/usage-rp")
def usage_rp_list():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_usage_rp ORDER BY date_created DESC LIMIT 100")
    usage_list = _rows(cur.fetchall())
    cur.execute(
        "SELECT DISTINCT kode_lot_wip AS kode_wip FROM tbl_rencana_item "
        "WHERE kode_lot_wip IS NOT NULL AND kode_lot_wip != '' "
        "ORDER BY kode_lot_wip DESC"
    )
    wip_list = [r["kode_wip"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"usage_list": usage_list, "wip_list": wip_list})


@api.post("/usage-rp")
def usage_rp_create():
    body = request.get_json(silent=True) or {}
    kode_wip = (body.get("kode_wip") or "").strip()
    jenis_scan = (body.get("jenis_rp") or body.get("kode_rp") or "").strip()
    qty_used = float(body.get("qty_used") or 0)
    stok_in_id = body.get("stok_in_id")
    if not kode_wip or not jenis_scan:
        return _err("kode_wip dan jenis_rp wajib")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT COALESCE(nama_rp, nama_jenis) AS nama_jenis, satuan "
        "FROM master_rp WHERE kode_rp = %s OR nama_rp = %s OR nama_jenis = %s LIMIT 1",
        (jenis_scan, jenis_scan, jenis_scan),
    )
    rp = cur.fetchone()
    if not rp:
        cur.close()
        conn.close()
        return _err("Jenis RP tidak ditemukan", 404)
    if stok_in_id:
        cur.execute("SELECT * FROM tbl_stok_rp_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok or float(stok["qty_sisa"]) < qty_used:
            cur.close()
            conn.close()
            return _err("Stok RP tidak cukup untuk usage", 400)
        cur.execute(
            "INSERT INTO tbl_stok_rp_out (stok_in_id, rp_id, meter_roll, kode_wip, tanggal) VALUES (%s,%s,%s,%s,%s)",
            (stok_in_id, stok["rp_id"], qty_used, kode_wip, date.today().isoformat()),
        )
        cur.execute(
            "UPDATE tbl_stok_rp_in SET qty_sisa = qty_sisa - %s WHERE id=%s",
            (qty_used, stok_in_id),
        )
    cur.execute(
        "INSERT INTO tbl_usage_rp (kode_wip, jenis_rp, qty_used, satuan) VALUES (%s,%s,%s,%s)",
        (
            kode_wip,
            rp["nama_jenis"],
            qty_used,
            body.get("satuan") or rp.get("satuan") or "meter",
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({"ok": True, "id": new_id, "stok_deducted": bool(stok_in_id)}), 201


# ---- P5: material lain ----
@api.get("/masters/material-lain")
def master_material_lain_list():
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM master_material_lain ORDER BY kode_material")
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.post("/masters/material-lain")
def master_material_lain_create():
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    kode = (body.get("kode_material") or "").strip()
    nama = (body.get("nama_material") or "").strip()
    if not kode or not nama:
        return _err("kode_material dan nama_material wajib")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    try:
        cur.execute(
            "INSERT INTO master_material_lain (kode_material, nama_material, deskripsi, satuan) "
            "VALUES (%s,%s,%s,%s)",
            (kode, nama, body.get("deskripsi") or None, body.get("satuan") or "pcs"),
        )
        conn.commit()
        new_id = cur.lastrowid
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(e), 409)
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "ok": True}), 201


@api.delete("/masters/material-lain/<int:material_id>")
def master_material_lain_delete(material_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM master_material_lain WHERE id=%s", (material_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True})


@api.get("/stok-material-lain")
def stok_material_lain_list():
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT si.*, m.kode_material, m.nama_material FROM tbl_stok_material_lain_in si "
        "JOIN master_material_lain m ON m.id = si.material_id "
        "WHERE si.qty_sisa > 0 ORDER BY si.tanggal_in"
    )
    stok_in = _rows(cur.fetchall())
    cur.execute(
        "SELECT so.*, m.nama_material FROM tbl_stok_material_lain_out so "
        "JOIN master_material_lain m ON m.id = so.material_id ORDER BY so.created_at DESC LIMIT 50"
    )
    stok_out = _rows(cur.fetchall())
    cur.execute(
        "SELECT id, kode_material, nama_material, satuan FROM master_material_lain ORDER BY kode_material"
    )
    material_list = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify({"stok_in": stok_in, "stok_out": stok_out, "material_list": material_list})


@api.post("/stok-material-lain")
def stok_material_lain_action():
    from app import ensure_extended_tables, generate_code

    body = request.get_json(silent=True) or {}
    action = (body.get("action") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if action == "in":
        material_id = body.get("material_id")
        qty = float(body.get("qty") or 0)
        if not material_id or qty <= 0:
            cur.close()
            conn.close()
            return _err("material_id dan qty wajib")
        tanggal = body.get("tanggal") or date.today().isoformat()
        kode_internal = generate_code("BC-M")
        cur.execute("SELECT satuan FROM master_material_lain WHERE id=%s", (material_id,))
        mat = cur.fetchone()
        cur.execute(
            "INSERT INTO tbl_stok_material_lain_in (kode_internal, material_id, qty, qty_sisa, satuan, tanggal_in) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (kode_internal, material_id, qty, qty, mat["satuan"] if mat else "pcs", tanggal),
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True, "kode_internal": kode_internal}), 201

    if action == "out":
        stok_in_id = body.get("stok_in_id")
        qty = float(body.get("qty") or 0)
        if not stok_in_id or qty <= 0:
            cur.close()
            conn.close()
            return _err("stok_in_id dan qty wajib")
        tanggal = body.get("tanggal") or date.today().isoformat()
        kode_wip = body.get("kode_wip") or None
        cur.execute("SELECT * FROM tbl_stok_material_lain_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok or float(stok["qty_sisa"]) < qty:
            cur.close()
            conn.close()
            return _err("Stok tidak cukup", 400)
        cur.execute(
            "INSERT INTO tbl_stok_material_lain_out (stok_in_id, material_id, qty, kode_wip, tanggal) "
            "VALUES (%s,%s,%s,%s,%s)",
            (stok_in_id, stok["material_id"], qty, kode_wip, tanggal),
        )
        cur.execute(
            "UPDATE tbl_stok_material_lain_in SET qty_sisa=%s WHERE id=%s",
            (float(stok["qty_sisa"]) - qty, stok_in_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"ok": True})

    cur.close()
    conn.close()
    return _err("action harus in atau out")


@api.get("/usage-material-lain/scan")
def usage_material_scan():
    kode = (request.args.get("q") or "").strip()
    if not kode:
        return _err("Kode kosong")
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
        return _err("Material tidak ditemukan", 404)
    return jsonify(_row(row))


@api.get("/usage-material-lain")
def usage_material_list():
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_usage_material_lain ORDER BY date_created DESC LIMIT 100")
    usage_list = _rows(cur.fetchall())
    cur.execute(
        "SELECT DISTINCT kode_lot_wip FROM tbl_rencana_item "
        "WHERE kode_lot_wip IS NOT NULL ORDER BY kode_lot_wip DESC"
    )
    wip_list = [r["kode_lot_wip"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"usage_list": usage_list, "wip_list": wip_list})


@api.post("/usage-material-lain")
def usage_material_create():
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    kode_wip = (body.get("kode_wip") or "").strip()
    kode_material = (body.get("kode_material") or "").strip()
    if not kode_wip or not kode_material:
        return _err("kode_wip dan kode_material wajib")
    qty_used = float(body.get("qty_used") or 0)
    stok_in_id = body.get("stok_in_id")
    satuan = body.get("satuan") or "pcs"
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT nama_material, satuan FROM master_material_lain WHERE kode_material=%s",
        (kode_material,),
    )
    mat = cur.fetchone()
    if stok_in_id:
        cur.execute("SELECT * FROM tbl_stok_material_lain_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok or float(stok["qty_sisa"]) < qty_used:
            cur.close()
            conn.close()
            return _err("Stok material tidak cukup untuk usage", 400)
        cur.execute(
            "INSERT INTO tbl_stok_material_lain_out (stok_in_id, material_id, qty, kode_wip, tanggal) "
            "VALUES (%s,%s,%s,%s,%s)",
            (stok_in_id, stok["material_id"], qty_used, kode_wip, date.today().isoformat()),
        )
        cur.execute(
            "UPDATE tbl_stok_material_lain_in SET qty_sisa=%s WHERE id=%s",
            (float(stok["qty_sisa"]) - qty_used, stok_in_id),
        )
    cur.execute(
        "INSERT INTO tbl_usage_material_lain (kode_wip, kode_material, nama_material, qty_used, satuan) "
        "VALUES (%s,%s,%s,%s,%s)",
        (
            kode_wip,
            kode_material,
            mat["nama_material"] if mat else None,
            qty_used,
            body.get("satuan") or (mat["satuan"] if mat else satuan),
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({"ok": True, "id": new_id, "stok_deducted": bool(stok_in_id)}), 201


# ---- Debt: masters PUT/DELETE kulit/kimia/rp ----
@api.put("/masters/kulit/<int:kulit_id>")
def master_kulit_update(kulit_id: int):
    body = request.get_json(silent=True) or {}
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM master_kulit WHERE id=%s", (kulit_id,))
    existing = cur.fetchone()
    if not existing:
        cur.close()
        conn.close()
        return _err("Master kulit tidak ditemukan", 404)
    kode = (body.get("kode_kulit") or existing.get("kode_kulit") or "").strip()
    nama = (body.get("nama_kulit") or existing.get("nama_kulit") or "").strip()
    if not kode or not nama:
        cur.close()
        conn.close()
        return _err("kode_kulit dan nama_kulit wajib")
    thickness = body["thickness"] if "thickness" in body else existing.get("thickness")
    warna = body["warna"] if "warna" in body else existing.get("warna")
    try:
        cur.execute(
            "UPDATE master_kulit SET kode_kulit=%s, nama_kulit=%s, thickness=%s, warna=%s WHERE id=%s",
            (kode, nama, thickness or None, warna or None, kulit_id),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(e), 409)
    cur.close()
    conn.close()
    return jsonify({"ok": True})


@api.delete("/masters/kulit/<int:kulit_id>")
def master_kulit_delete(kulit_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM master_kulit WHERE id=%s", (kulit_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True})


@api.put("/masters/kimia/<int:kimia_id>")
def master_kimia_update(kimia_id: int):
    body = request.get_json(silent=True) or {}
    kode = (body.get("kode_kimia") or body.get("kode_barang") or "").strip()
    nama = (body.get("nama_kimia") or body.get("nama_barang") or "").strip()
    if not kode or not nama:
        return _err("kode dan nama kimia wajib")
    satuan = body.get("satuan") or "kg"
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE master_kimia SET kode_kimia=%s, nama_kimia=%s, kode_barang=%s, nama_barang=%s, "
            "deskripsi=%s, satuan=%s WHERE id=%s",
            (kode, nama, kode, nama, body.get("deskripsi") or None, satuan, kimia_id),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(e), 409)
    cur.close()
    conn.close()
    return jsonify({"ok": True})


@api.delete("/masters/kimia/<int:kimia_id>")
def master_kimia_delete(kimia_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM master_kimia WHERE id=%s", (kimia_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        cur.close()
        conn.close()
        return _err("Master kimia tidak dapat dihapus karena masih digunakan", 409)
    cur.close()
    conn.close()
    return jsonify({"ok": True})


@api.put("/masters/rp/<int:rp_id>")
def master_rp_update(rp_id: int):
    body = request.get_json(silent=True) or {}
    kode = (body.get("kode_rp") or "").strip()
    nama = (body.get("nama_rp") or body.get("nama_jenis") or "").strip()
    if not kode or not nama:
        return _err("kode_rp dan nama_rp wajib")
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE master_rp SET kode_rp=%s, nama_rp=%s, nama_jenis=%s, deskripsi=%s WHERE id=%s",
            (kode, nama, nama, body.get("deskripsi") or None, rp_id),
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(e), 409)
    cur.close()
    conn.close()
    return jsonify({"ok": True})


@api.delete("/masters/rp/<int:rp_id>")
def master_rp_delete(rp_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM master_rp WHERE id=%s", (rp_id,))
        conn.commit()
    except Exception:
        conn.rollback()
        cur.close()
        conn.close()
        return _err("Master RP tidak dapat dihapus karena masih digunakan", 409)
    cur.close()
    conn.close()
    return jsonify({"ok": True})


# ---- Debt: rencana item / PO / barcode / print + ERP helpers ----
@api.get("/erp/fields")
def erp_fields_api():
    thickness = (request.args.get("thickness") or "").strip()
    material_name = (request.args.get("material_name") or "").strip()
    color = (request.args.get("color") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    from app import ensure_extended_tables

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


@api.get("/erp/combination")
def erp_combination_api():
    from app import ensure_extended_tables

    material_name = (request.args.get("material_name") or "").strip()
    color = (request.args.get("color") or "").strip()
    emboss = (request.args.get("emboss") or "").strip()
    thickness = (request.args.get("thickness") or "").strip()
    if not material_name or not color or not emboss:
        return _err("Material Name, Color, Emboss wajib")
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
    rows = _rows(cur.fetchall())
    cur.close()
    conn.close()
    if not rows:
        return _err("Kombinasi tidak ditemukan di master ERP", 404)
    return jsonify({"options": rows})


@api.get("/rencana/po/by-combination")
def rencana_po_by_combination():
    color = (request.args.get("color") or "").strip()
    emboss = (request.args.get("emboss") or "").strip()
    color_swatch = (request.args.get("color_swatch") or "").strip()
    if not color or not emboss or not color_swatch:
        return _err("Color, Emboss, Color Swatch wajib")
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
    items = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(items)


@api.get("/rencana-produksi/<int:rencana_id>/print")
def rencana_print_api(rencana_id: int):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_rencana_produksi WHERE id = %s", (rencana_id,))
    rencana = cur.fetchone()
    if not rencana:
        cur.close()
        conn.close()
        return _err("Rencana tidak ditemukan", 404)
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
    items = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify({"rencana": _row(rencana), "items": items})


@api.get("/rencana-produksi/item/<int:item_id>")
def rencana_item_detail_api(item_id: int):
    from app import ensure_extended_tables

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
        cur.close()
        conn.close()
        return _err("Item rencana tidak ditemukan", 404)
    cur.execute(
        "SELECT p.*, po.no_po, po.no_so, po.item_name FROM tbl_rencana_item_po p "
        "JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = %s",
        (item_id,),
    )
    selected_po = _rows(cur.fetchall())
    cur.execute(
        "SELECT kl.* FROM tbl_kulit_lebih kl WHERE kl.rencana_item_id = %s ORDER BY kl.created_at DESC",
        (item_id,),
    )
    kulit_lebih = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify({"item": _row(item), "selected_po": selected_po, "kulit_lebih": kulit_lebih})


@api.get("/rencana-produksi/item/<int:item_id>/barcode")
def rencana_item_barcode_api(item_id: int):
    from app import _make_rpi_barcode

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
        return _err("Item tidak ditemukan", 404)
    barcode = item.get("kode_barcode") or item.get("kode_rencana_item") or _make_rpi_barcode(
        item.get("thickness"), item.get("emboss"), item.get("color")
    )
    return jsonify({"item": _row(item), "barcode": barcode})


@api.get("/rencana-produksi/item/<int:item_id>/list-po")
def rencana_item_list_po_get(item_id: int):
    from app import ensure_rencana_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT i.*, c.nama_customer, r.nama_rencana, r.tanggal_rencana "
        "FROM tbl_rencana_item i "
        "LEFT JOIN master_customer c ON c.id = i.customer_id "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        "WHERE i.id = %s",
        (item_id,),
    )
    item = cur.fetchone()
    if not item:
        cur.close()
        conn.close()
        return _err("Item rencana tidak ditemukan", 404)
    cur.execute(
        "SELECT id, no_po, no_so, item_name, sq_ft, qty_order, qty_processed, "
        "(qty_order - qty_processed) AS qty_outstanding "
        "FROM tbl_master_po "
        "WHERE tebal = %s AND warna = %s AND emboss = %s "
        "AND status IN ('outstanding','partial') "
        "ORDER BY no_po, item_name",
        (item["thickness"], item["color"], item["emboss"]),
    )
    po_list = _rows(cur.fetchall())
    cur.execute(
        "SELECT p.*, po.no_po, po.item_name FROM tbl_rencana_item_po p "
        "JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = %s",
        (item_id,),
    )
    selected_po = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify({"item": _row(item), "po_list": po_list, "selected_po": selected_po})


@api.post("/rencana-produksi/item/<int:item_id>/list-po")
def rencana_item_list_po_save(item_id: int):
    from app import _save_item_po_selections, ensure_rencana_tables

    body = request.get_json(silent=True) or {}
    po_data = body.get("pos") or body.get("po_data") or []
    if not po_data:
        return _err("Pilih minimal satu PO")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_rencana_item WHERE id=%s", (item_id,))
    item = cur.fetchone()
    if not item:
        cur.close()
        conn.close()
        return _err("Item rencana tidak ditemukan", 404)
    cur.execute("DELETE FROM tbl_rencana_item_po WHERE item_id = %s", (item_id,))
    _save_item_po_selections(cur, item_id, po_data)
    cur.execute(
        "UPDATE tbl_rencana_produksi SET status = 'active' WHERE id = %s",
        (item["rencana_id"],),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True})


# ---- P6: reports ----
@api.get("/reports/packing")
def report_packing_api():
    today = date.today().isoformat()
    start_date = request.args.get("start_date") or today
    end_date = request.args.get("end_date") or today
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT DATE(p.date_created) AS tanggal, p.no_po, p.kode_packing AS kode_process,
                   COUNT(r.id) AS pack, SUM(r.lembar) AS qty, SUM(r.ukuran) AS size, p.status
            FROM tbl_packing p
            LEFT JOIN tbl_packing_roll r ON r.packing_id = p.id
            WHERE DATE(p.date_created) BETWEEN %s AND %s
            GROUP BY DATE(p.date_created), p.no_po, p.kode_packing, p.status
            """,
            (start_date, end_date),
        )
        report_data = _rows(cur.fetchall())
    except Exception:
        report_data = []
    cur.close()
    conn.close()
    return jsonify(
        {
            "start_date": start_date,
            "end_date": end_date,
            "rows": report_data,
            "total_all_lembar": sum(r.get("qty") or 0 for r in report_data),
            "total_all_ukuran": sum(r.get("size") or 0 for r in report_data),
            "total_all_pack": sum(r.get("pack") or 0 for r in report_data),
        }
    )


@api.get("/reports/persiapan")
def report_persiapan_api():
    today = date.today().isoformat()
    start_date = request.args.get("start_date") or today
    end_date = request.args.get("end_date") or today
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT DATE(pk.date_created) AS tanggal, pk.kode_proses AS kode_proccess,
                   pk.no_po AS nama_barang, COUNT(u.id) AS total_lembar,
                   SUM(u.size_val) AS total_ukuran, pk.status AS status_terakhir
            FROM tbl_persiapan_kulit pk
            LEFT JOIN tbl_persiapan_ukur u ON u.persiapan_id = pk.id
            WHERE DATE(pk.date_created) BETWEEN %s AND %s
            GROUP BY pk.id
            """,
            (start_date, end_date),
        )
        report_data = _rows(cur.fetchall())
    except Exception:
        report_data = []
    cur.close()
    conn.close()
    return jsonify(
        {
            "start_date": start_date,
            "end_date": end_date,
            "rows": report_data,
            "total_all_lembar": sum(r.get("total_lembar") or 0 for r in report_data),
            "total_all_ukuran": sum(
                (r.get("total_ukuran") or 0) for r in report_data if r.get("total_ukuran")
            ),
        }
    )
