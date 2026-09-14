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


def _sql_no_so_from_master(alias: str = "pk") -> str:
    """Ambil No. SO dari master PO (no_po = PO customer)."""
    return (
        f"(SELECT po.no_so FROM tbl_master_po po "
        f"WHERE po.no_po = {alias}.no_po AND po.no_so IS NOT NULL AND po.no_so <> '' "
        f"ORDER BY po.id DESC LIMIT 1) AS no_so"
    )


def _parse_id_csv(raw: str | None) -> list[int]:
    out: list[int] = []
    for part in str(raw or "").split(","):
        part = part.strip()
        if part.isdigit():
            out.append(int(part))
    return out


# ---- health ----
@api.get("/health")
def health():
    try:
        from bridge_metrics import snapshot

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        conn.close()
        return jsonify(
            {
                "status": "ok",
                "database": "tonghong_mrp",
                "catalog_mode": "erp-only",
                "metrics": snapshot(),
            }
        )
    except Exception as e:
        return _err(f"db unavailable: {e}", 503)


# ---- palet / yl ----
@api.get("/palet/movements")
def palet_movements():
    direction = (request.args.get("direction") or "").strip().upper()
    q = (request.args.get("q") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    sql = (
        "SELECT m.*, (SELECT COUNT(*) FROM tbl_yl y WHERE y.kode_palet = m.kode_palet) AS jml_yl, "
        "(SELECT COALESCE(SUM(y.qty),0) FROM tbl_yl y WHERE y.kode_palet = m.kode_palet) AS qty_yl "
        "FROM tbl_palet_movement m WHERE 1=1"
    )
    params: list = []
    if direction in ("IN", "OUT"):
        sql += " AND m.direction=%s"
        params.append(direction)
    if q:
        like = f"%{q}%"
        sql += " AND (m.kode_palet LIKE %s OR IFNULL(m.keterangan,'') LIKE %s)"
        params.extend([like, like])
    sql += " ORDER BY m.created_at DESC LIMIT 200"
    cur.execute(sql, params)
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
    keterangan = (body.get("keterangan") or "").strip() or None
    items = body.get("items") or []

    cleaned = []
    for item in items:
        kode_yl = (item.get("kode_yl") or "").strip()
        if not kode_yl:
            continue
        try:
            qty = float(item.get("qty") or 0)
        except (TypeError, ValueError):
            return _err(f"Qty YL {kode_yl} harus angka")
        if qty <= 0:
            return _err(f"Qty YL {kode_yl} harus > 0")
        cleaned.append(
            {
                "kode_yl": kode_yl,
                "thickness": (item.get("thickness") or "").strip() or None,
                "warna": (item.get("warna") or "").strip() or None,
                "qty": qty,
            }
        )
    if not cleaned:
        return _err("Minimal satu YL dengan qty > 0")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "INSERT INTO tbl_palet_movement (kode_palet, direction, tanggal, keterangan) VALUES (%s,'IN',%s,%s)",
        (kode_palet, tanggal, keterangan),
    )
    for item in cleaned:
        cur.execute(
            "INSERT INTO tbl_yl (kode_yl, kode_palet, thickness, warna, qty) "
            "VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE thickness=%s, warna=%s, qty=%s",
            (
                item["kode_yl"],
                kode_palet,
                item["thickness"],
                item["warna"],
                item["qty"],
                item["thickness"],
                item["warna"],
                item["qty"],
            ),
        )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "kode_palet": kode_palet, "yl_count": len(cleaned)})


@api.post("/palet/out")
def palet_out():
    body = request.get_json(silent=True) or {}
    kode_palet = (body.get("kode_palet") or "").strip()
    if not kode_palet:
        return _err("kode_palet wajib")
    tanggal = body.get("tanggal") or date.today().isoformat()
    keterangan = (body.get("keterangan") or "").strip() or None
    clear_yl = body.get("clear_yl", True)
    if isinstance(clear_yl, str):
        clear_yl = clear_yl.lower() in ("1", "true", "yes")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS n FROM tbl_yl WHERE kode_palet=%s", (kode_palet,))
    n = int((cur.fetchone() or {}).get("n") or 0)
    if n == 0 and clear_yl:
        # Izinkan OUT kosong hanya jika pernah ada gerakan IN.
        cur.execute(
            "SELECT id FROM tbl_palet_movement WHERE kode_palet=%s AND direction='IN' LIMIT 1",
            (kode_palet,),
        )
        if not cur.fetchone():
            cur.close()
            conn.close()
            return _err("Palet tidak dikenal / belum pernah IN", 404)
    cur.execute(
        "INSERT INTO tbl_palet_movement (kode_palet, direction, tanggal, keterangan) VALUES (%s,'OUT',%s,%s)",
        (kode_palet, tanggal, keterangan),
    )
    yl_cleared = 0
    if clear_yl and n:
        cur.execute("DELETE FROM tbl_yl WHERE kode_palet=%s", (kode_palet,))
        yl_cleared = n
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "kode_palet": kode_palet, "yl_cleared": yl_cleared})


@api.get("/palet/<kode_palet>/yl")
def palet_yl(kode_palet):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM tbl_yl WHERE kode_palet = %s ORDER BY kode_yl",
        (kode_palet,),
    )
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.get("/yl")
def yl_list():
    q = (request.args.get("q") or "").strip()
    kode_palet = (request.args.get("kode_palet") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    sql = (
        "SELECT kode_yl, kode_palet, thickness, warna, qty, created_at FROM tbl_yl WHERE 1=1"
    )
    params: list = []
    if kode_palet:
        sql += " AND kode_palet=%s"
        params.append(kode_palet)
    if q:
        like = f"%{q}%"
        sql += (
            " AND (kode_yl LIKE %s OR kode_palet LIKE %s OR IFNULL(warna,'') LIKE %s "
            "OR IFNULL(thickness,'') LIKE %s)"
        )
        params.extend([like, like, like, like])
    sql += " ORDER BY kode_palet, kode_yl"
    cur.execute(sql, params)
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
    thickness = (body.get("thickness") or "").strip() or None
    warna = (body.get("warna") or "").strip() or None
    try:
        qty = float(body.get("qty") or 0)
    except (TypeError, ValueError):
        return _err("qty harus angka")
    if qty <= 0:
        return _err("qty harus > 0")
    tanggal = body.get("tanggal") or date.today().isoformat()
    keterangan = (body.get("keterangan") or "").strip() or None

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "INSERT INTO tbl_yl_movement (kode_yl, kode_palet, direction, thickness, warna, qty, tanggal, keterangan) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (kode_yl, kode_palet, direction, thickness, warna, qty, tanggal, keterangan),
    )
    if direction == "IN":
        cur.execute(
            "INSERT INTO tbl_yl (kode_yl, kode_palet, thickness, warna, qty) "
            "VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE thickness=%s, warna=%s, qty=qty+%s",
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
        stok = float(row["qty"] or 0)
        if qty > stok:
            conn.rollback()
            cur.close()
            conn.close()
            return _err(f"Qty OUT ({qty}) melebihi stok ({stok})")
        sisa = stok - qty
        if sisa <= 0:
            cur.execute("DELETE FROM tbl_yl WHERE id=%s", (row["id"],))
        else:
            cur.execute("UPDATE tbl_yl SET qty=%s WHERE id=%s", (sisa, row["id"]))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "kode_yl": kode_yl, "kode_palet": kode_palet, "direction": direction, "qty": qty})


# ---- masters ----
@api.get("/masters/erp")
def master_erp_list():
    """Sumber: tonghong.master_items (bukan salinan lokal master_erp)."""
    from erp_master_items import fetch_master_items, item_to_erp_shape

    try:
        limit = int(request.args.get("limit") or 500)
    except (TypeError, ValueError):
        limit = 500
    limit = max(1, min(limit, 2000))
    keyword = (request.args.get("keyword") or "").strip().lower()
    rows = fetch_master_items(limit=None if keyword else limit)
    out = []
    for r in rows:
        mapped = item_to_erp_shape(r)
        if keyword:
            blob = " ".join(
                str(mapped.get(k) or "")
                for k in (
                    "item_code",
                    "category",
                    "thickness",
                    "material_name",
                    "color",
                    "emboss",
                    "color_swatch",
                    "backer",
                )
            ).lower()
            if keyword not in blob:
                continue
        out.append(mapped)
        if len(out) >= limit:
            break
    return jsonify(out)


@api.get("/masters/erp/options")
def master_erp_options():
    from erp_master_items import options_payload

    return jsonify(options_payload())


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
    from erp_raw_materials import list_materials

    rows = list_materials("kulit")
    out = [
        {
            "id": r["id"],
            "erp_material_id": r["id"],
            "kode_kulit": r["code"],
            "nama_kulit": r["name"],
            "satuan": r.get("unit"),
            "source": "raw_materials",
        }
        for r in rows
    ]
    return jsonify(out)


@api.post("/masters/kulit")
def master_kulit_create():
    return _err(
        "Katalog kulit hanya di ERP Inventory (raw_materials). Tidak bisa create dari MRP.",
        403,
    )


@api.get("/masters/kimia")
def master_kimia_list():
    from erp_raw_materials import list_materials

    rows = list_materials("kimia")
    out = [
        {
            "id": r["id"],
            "erp_material_id": r["id"],
            "kode_kimia": r["code"],
            "kode_barang": r["code"],
            "nama_kimia": r["name"],
            "nama_barang": r["name"],
            "satuan": r.get("unit") or "kg",
            "source": "raw_materials",
        }
        for r in rows
    ]
    return jsonify(out)


@api.post("/masters/kimia")
def master_kimia_create():
    return _err(
        "Katalog kimia hanya di ERP Inventory (raw_materials). Tidak bisa create dari MRP.",
        403,
    )


@api.get("/masters/rp")
def master_rp_list():
    from erp_raw_materials import list_materials

    rows = list_materials("rp")
    out = [
        {
            "id": r["id"],
            "erp_material_id": r["id"],
            "kode_rp": r["code"],
            "nama_rp": r["name"],
            "nama_jenis": r["name"],
            "satuan": r.get("unit") or "meter",
            "source": "raw_materials",
        }
        for r in rows
    ]
    return jsonify(out)


@api.post("/masters/rp")
def master_rp_create():
    return _err(
        "Katalog RP hanya di ERP Inventory (raw_materials). Tidak bisa create dari MRP.",
        403,
    )


@api.get("/masters/treatment")
def master_treatment_list():
    from app import ensure_master_treatment

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_master_treatment(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_master_treatment ORDER BY jenis, nama_treatment, id")
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


def _qty_wip_by_source_detail_ids(cur, source_ids: list[int]) -> dict[int, float]:
    """QTY WIP = total ukuran persiapan proses yang sudah terbentuk (saved/completed)."""
    if not source_ids:
        return {}
    placeholders = ",".join(["%s"] * len(source_ids))
    cur.execute(
        f"SELECT po.source_detail_id, COALESCE(SUM(pk.total_size), 0) AS qty_wip "
        f"FROM tbl_master_po po "
        f"JOIN tbl_rencana_item_po rip ON rip.po_id = po.id "
        f"JOIN tbl_rencana_item i ON i.id = rip.item_id "
        f"JOIN tbl_persiapan_kulit pk ON pk.rencana_item_id = i.id "
        f"WHERE po.source_detail_id IN ({placeholders}) "
        f"AND pk.status IN ('started', 'saved', 'completed') "
        f"AND COALESCE(pk.kode_wip, '') <> '' "
        f"AND COALESCE(pk.total_size, 0) > 0 "
        f"GROUP BY po.source_detail_id",
        source_ids,
    )
    out: dict[int, float] = {}
    for row in cur.fetchall() or []:
        sid = row.get("source_detail_id")
        if sid is None:
            continue
        out[int(sid)] = float(row.get("qty_wip") or 0)
    return out


def _stock_wh_by_source_detail_ids(cur, source_ids: list[int]) -> dict[int, float]:
    """Stock WH = packing finished + surat jalan (erp_delivery_id) per baris PO ERP."""
    if not source_ids:
        return {}
    placeholders = ",".join(["%s"] * len(source_ids))
    cur.execute(
        f"SELECT sid.source_detail_id, COALESCE(SUM(sid.qty_sq), 0) AS stock_wh_qty "
        f"FROM ( "
        f"  SELECT po.source_detail_id, "
        f"    COALESCE(NULLIF(pp.qty_sq, 0), p.total_ukuran) AS qty_sq "
        f"  FROM tbl_packing p "
        f"  JOIN tbl_gudang_fg fg ON fg.packing_id = p.id "
        f"  JOIN tbl_packing_po pp ON pp.packing_id = p.id "
        f"  JOIN tbl_master_po po ON po.id = COALESCE(pp.po_id, ( "
        f"    SELECT id FROM tbl_master_po WHERE no_po = pp.no_po ORDER BY id DESC LIMIT 1 "
        f"  )) "
        f"  WHERE p.status = 'finished' "
        f"    AND fg.erp_delivery_id IS NOT NULL "
        f"    AND po.source_detail_id IN ({placeholders}) "
        f"  UNION ALL "
        f"  SELECT po.source_detail_id, p.total_ukuran AS qty_sq "
        f"  FROM tbl_packing p "
        f"  JOIN tbl_gudang_fg fg ON fg.packing_id = p.id "
        f"  JOIN tbl_rencana_item i ON i.kode_lot_wip = p.kode_wip "
        f"  JOIN tbl_rencana_item_po rip ON rip.item_id = i.id "
        f"  JOIN tbl_master_po po ON po.id = rip.po_id "
        f"  WHERE p.status = 'finished' "
        f"    AND fg.erp_delivery_id IS NOT NULL "
        f"    AND po.source_detail_id IN ({placeholders}) "
        f"    AND NOT EXISTS (SELECT 1 FROM tbl_packing_po x WHERE x.packing_id = p.id) "
        f") sid "
        f"WHERE sid.source_detail_id IS NOT NULL "
        f"GROUP BY sid.source_detail_id",
        (*source_ids, *source_ids),
    )
    out: dict[int, float] = {}
    for row in cur.fetchall() or []:
        sid = row.get("source_detail_id")
        if sid is None:
            continue
        out[int(sid)] = float(row.get("stock_wh_qty") or 0)
    return out


@api.get("/masters/po")
def master_po_list():
    from app import ensure_rencana_tables, ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    ensure_extended_tables(cur)
    conn.commit()
    source_ids = _parse_id_csv(request.args.get("source_detail_ids"))
    status = (request.args.get("status") or "").strip()
    if source_ids:
        placeholders = ",".join(["%s"] * len(source_ids))
        cur.execute(
            f"SELECT * FROM tbl_master_po WHERE source_detail_id IN ({placeholders}) "
            "ORDER BY no_po, item_name LIMIT 2000",
            source_ids,
        )
    elif status:
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
    if source_ids:
        wip_map = _qty_wip_by_source_detail_ids(cur, source_ids)
        stock_map = _stock_wh_by_source_detail_ids(cur, source_ids)
        for row in data:
            sid = row.get("source_detail_id")
            try:
                sid_i = int(sid)
            except (TypeError, ValueError):
                continue
            row["qty_wip"] = wip_map.get(sid_i, 0.0)
            row["stock_wh_qty"] = stock_map.get(sid_i, 0.0)
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
    cancelled_n = 0
    for item in items:
        source_detail_id = item.get("source_detail_id")
        try:
            source_detail_id = int(source_detail_id) if source_detail_id is not None else None
        except (TypeError, ValueError):
            source_detail_id = None
        want_cancel = bool(item.get("cancelled"))

        no_po = (item.get("no_po") or "").strip()
        item_name = (item.get("item_name") or "").strip()
        warna = (item.get("warna") or "").strip()
        tebal = (item.get("tebal") or "").strip()
        emboss = (item.get("emboss") or "").strip()

        existing = None
        if source_detail_id is not None:
            cur.execute(
                "SELECT id, qty_processed, status FROM tbl_master_po "
                "WHERE source_detail_id=%s LIMIT 1",
                (source_detail_id,),
            )
            existing = cur.fetchone()
        if not existing and no_po and item_name:
            cur.execute(
                "SELECT id, qty_processed, status FROM tbl_master_po "
                "WHERE no_po=%s AND item_name=%s AND COALESCE(warna,'')=%s "
                "AND COALESCE(tebal,'')=%s AND COALESCE(emboss,'')=%s LIMIT 1",
                (no_po, item_name, warna, tebal, emboss),
            )
            existing = cur.fetchone()

        # Cancel/delete dari ERP: tandai cancelled, jangan hapus (jaga qty_processed).
        if want_cancel:
            if existing:
                cur.execute(
                    "UPDATE tbl_master_po SET status='cancelled' WHERE id=%s",
                    (existing["id"],),
                )
                cancelled_n += 1
                updated += 1
            continue

        if not no_po or not item_name:
            continue
        no_so = (item.get("no_so") or "").strip() or None
        customer = (item.get("customer") or "").strip() or None
        try:
            erp_customer_id = (
                int(item["customer_id"]) if item.get("customer_id") is not None else None
            )
        except (TypeError, ValueError):
            erp_customer_id = None
        if erp_customer_id is None and customer:
            try:
                from erp_customers import resolve_customer

                resolved = resolve_customer(customer, create_if_missing=True)
                erp_customer_id = int(resolved["id"]) if resolved else None
                if resolved and resolved.get("name"):
                    customer = resolved["name"]
            except Exception:
                pass
        color_swatch = (item.get("color_swatch") or "").strip() or None
        lot_number = (item.get("lot_number") or "").strip() or None
        qty_order = float(item.get("qty_order") or item.get("sq_ft") or 0)
        sq_ft = float(item.get("sq_ft") or qty_order or 0)
        if item.get("qty_balance_erp") is not None:
            qty_balance_erp = float(item.get("qty_balance_erp") or 0)
        else:
            qty_balance_erp = qty_order

        if existing:
            qty_processed = float(existing.get("qty_processed") or 0)
            if qty_processed >= qty_order > 0:
                status = "completed"
            elif qty_processed > 0:
                status = "partial"
            else:
                status = "outstanding"
            cur.execute(
                "UPDATE tbl_master_po SET no_po=%s, no_so=%s, customer=%s, customer_id=%s, warna=%s, tebal=%s, emboss=%s, "
                "color_swatch=%s, source_detail_id=%s, lot_number=%s, sq_ft=%s, qty_order=%s, "
                "qty_balance_erp=%s, status=%s WHERE id=%s",
                (
                    no_po,
                    no_so,
                    customer,
                    erp_customer_id,
                    warna or None,
                    tebal or None,
                    emboss or None,
                    color_swatch,
                    source_detail_id,
                    lot_number,
                    sq_ft,
                    qty_order,
                    qty_balance_erp,
                    status,
                    existing["id"],
                ),
            )
            updated += 1
        else:
            cur.execute(
                "INSERT INTO tbl_master_po "
                "(no_po, no_so, customer, customer_id, item_name, warna, tebal, emboss, color_swatch, "
                "source_detail_id, lot_number, sq_ft, qty_order, qty_balance_erp, qty_processed, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,'outstanding')",
                (
                    no_po,
                    no_so,
                    customer,
                    erp_customer_id,
                    item_name,
                    warna or None,
                    tebal or None,
                    emboss or None,
                    color_swatch,
                    source_detail_id,
                    lot_number,
                    sq_ft,
                    qty_order,
                    qty_balance_erp,
                ),
            )
            inserted += 1

    from app import _recompute_all_master_po_qty_processed

    recompute = _recompute_all_master_po_qty_processed(cur)
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(
        {
            "ok": True,
            "inserted": inserted,
            "updated": updated,
            "cancelled": cancelled_n,
            "total": len(items),
            "recomputed": recompute.get("recomputed", 0),
        }
    )


@api.post("/masters/po/recompute-processed")
def master_po_recompute_processed():
    """Repair: qty_processed = SUM(qty_proses) dari alokasi rencana."""
    from app import _recompute_all_master_po_qty_processed, ensure_rencana_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    conn.commit()
    result = _recompute_all_master_po_qty_processed(cur)
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(result)


def _norm_spek_sql(col: str) -> str:
    """NULL / '' / '-' dianggap sama untuk match spek."""
    return f"COALESCE(NULLIF(NULLIF(TRIM({col}), ''), '-'), '-')"


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
        "SELECT r.id, r.kode_rencana, r.nama_rencana, r.tanggal_rencana, r.date_created, r.status, "
        "(SELECT COUNT(*) FROM tbl_rencana_item i WHERE i.rencana_id = r.id) AS jml_item, "
        "(SELECT COUNT(*) FROM tbl_rencana_item_po p "
        " JOIN tbl_rencana_item i ON i.id = p.item_id WHERE i.rencana_id = r.id) AS jml_po, "
        "(SELECT COALESCE(SUM(p.qty_proses), 0) FROM tbl_rencana_item_po p "
        " JOIN tbl_rencana_item i ON i.id = p.item_id WHERE i.rencana_id = r.id) AS total_qty_alokasi, "
        "(SELECT GROUP_CONCAT(DISTINCT i.nama_customer ORDER BY i.nama_customer SEPARATOR ', ') "
        " FROM tbl_rencana_item i "
        " "
        " WHERE i.rencana_id = r.id AND i.nama_customer IS NOT NULL AND i.nama_customer != '') AS customers, "
        "(SELECT GROUP_CONCAT(DISTINCT po.no_po ORDER BY po.no_po SEPARATOR ', ') "
        " FROM tbl_rencana_item_po p "
        " JOIN tbl_rencana_item i ON i.id = p.item_id "
        " JOIN tbl_master_po po ON po.id = p.po_id "
        " WHERE i.rencana_id = r.id) AS po_numbers "
        "FROM tbl_rencana_produksi r "
        "ORDER BY COALESCE(r.tanggal_rencana, r.date_created) DESC, r.id DESC"
    )
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(data)


@api.get("/rencana-produksi/<int:rencana_id>")
def rencana_detail(rencana_id: int):
    from app import ensure_extended_tables, ensure_rencana_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_rencana_produksi WHERE id = %s", (rencana_id,))
    rencana = cur.fetchone()
    if not rencana:
        cur.close()
        conn.close()
        return _err("Rencana tidak ditemukan", 404)
    cur.execute(
        "SELECT i.*, i.nama_customer, "
        "(SELECT COUNT(*) FROM tbl_rencana_item_po p WHERE p.item_id = i.id) AS jml_po, "
        "(SELECT COALESCE(SUM(p.qty_proses),0) FROM tbl_rencana_item_po p WHERE p.item_id = i.id) AS total_qty_so, "
        "(SELECT GROUP_CONCAT(DISTINCT COALESCE(NULLIF(po.no_so,''), po.no_po) ORDER BY po.no_po SEPARATOR ' / ') "
        " FROM tbl_rencana_item_po p JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = i.id) AS schedule_text, "
        "(SELECT GROUP_CONCAT(DISTINCT po.no_po ORDER BY po.no_po SEPARATOR ', ') "
        " FROM tbl_rencana_item_po p JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = i.id) AS po_numbers "
        "FROM tbl_rencana_item i "
        ""
        "WHERE i.rencana_id = %s ORDER BY i.urutan, i.id",
        (rencana_id,),
    )
    items = _rows(cur.fetchall())
    item_ids = [int(i["id"]) for i in items if i.get("id") is not None]
    allocations_by_item: dict[int, list] = {iid: [] for iid in item_ids}
    if item_ids:
        placeholders = ",".join(["%s"] * len(item_ids))
        cur.execute(
            f"SELECT p.id, p.item_id, p.po_id, p.qty_outstanding, p.qty_proses, "
            f"po.no_po, po.no_so, po.customer, po.item_name, po.tebal, po.warna, po.emboss, "
            f"po.color_swatch, po.qty_order, po.qty_processed, po.qty_balance_erp, "
            f"po.source_detail_id, po.lot_number, po.status AS po_status, "
            f"(po.qty_order - po.qty_processed) AS qty_sisa_alokasi "
            f"FROM tbl_rencana_item_po p "
            f"JOIN tbl_master_po po ON po.id = p.po_id "
            f"WHERE p.item_id IN ({placeholders}) "
            f"ORDER BY p.item_id, po.no_po, p.id",
            tuple(item_ids),
        )
        for row in _rows(cur.fetchall()):
            iid = int(row["item_id"])
            allocations_by_item.setdefault(iid, []).append(row)
        for rows in allocations_by_item.values():
            _attach_erp_lot_no(rows)
    for item in items:
        iid = int(item["id"])
        item["po_allocations"] = allocations_by_item.get(iid, [])

    summary = {
        "jml_item": len(items),
        "jml_po": sum(int(i.get("jml_po") or 0) for i in items),
        "total_qty_alokasi": sum(float(i.get("total_qty_so") or 0) for i in items),
        "customers": ", ".join(
            sorted(
                {
                    (i.get("nama_customer") or "").strip()
                    for i in items
                    if (i.get("nama_customer") or "").strip()
                }
            )
        ),
        "po_numbers": ", ".join(
            sorted(
                {
                    (i.get("po_numbers") or "").strip()
                    for i in items
                    if (i.get("po_numbers") or "").strip()
                }
            )
        ),
    }
    # Flatten unique PO numbers from allocations (cleaner than joining GROUP_CONCAT fragments)
    po_set: list[str] = []
    seen_po: set[str] = set()
    for item in items:
        for al in item.get("po_allocations") or []:
            no = (al.get("no_po") or "").strip()
            if no and no not in seen_po:
                seen_po.add(no)
                po_set.append(no)
    summary["po_numbers"] = ", ".join(po_set)

    cur.close()
    conn.close()
    return jsonify({"rencana": _row(rencana), "items": items, "summary": summary})


def _po_field_or_dash(value) -> str:
    text = (str(value) if value is not None else "").strip()
    return text or "-"


@api.post("/rencana-produksi")
def rencana_create():
    from app import (
        _ensure_customer_id,
        _recompute_master_po_qty_processed,
        _save_item_po_selections,
        ensure_extended_tables,
        ensure_rencana_tables,
        generate_code,
    )

    body = request.get_json(silent=True) or {}
    nama = (body.get("nama_rencana") or "").strip()
    tanggal = body.get("tanggal_rencana") or date.today().isoformat()
    po_lines = body.get("po_lines") or []
    items = body.get("items") or []
    if not nama:
        return _err("nama_rencana wajib")
    if not po_lines and not items:
        return _err("minimal satu po_lines atau items")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    ensure_extended_tables(cur)
    conn.commit()

    # Mode baru: spek item dari baris PO (1 PO = 1 item + alokasi).
    if po_lines:
        resolved = []
        seen_po: set[int] = set()
        for entry in po_lines:
            try:
                po_id = int(entry.get("po_id"))
            except (TypeError, ValueError):
                cur.close()
                conn.close()
                return _err("po_id tidak valid")
            if po_id in seen_po:
                cur.close()
                conn.close()
                return _err(f"po_id {po_id} duplikat dalam po_lines")
            seen_po.add(po_id)
            try:
                qty = float(entry.get("qty") or 0)
            except (TypeError, ValueError):
                cur.close()
                conn.close()
                return _err(f"qty tidak valid untuk po_id {po_id}")
            if qty <= 0:
                cur.close()
                conn.close()
                return _err(f"qty harus > 0 untuk po_id {po_id}")
            _recompute_master_po_qty_processed(cur, po_id)
            cur.execute("SELECT * FROM tbl_master_po WHERE id = %s", (po_id,))
            po = cur.fetchone()
            if not po:
                cur.close()
                conn.close()
                return _err(f"PO #{po_id} tidak ditemukan")
            status = (po.get("status") or "").strip()
            if status not in ("outstanding", "partial"):
                cur.close()
                conn.close()
                return _err(f"PO {po.get('no_po') or po_id} tidak dapat dialokasi (status={status})")
            outstanding = float(po.get("qty_order") or 0) - float(po.get("qty_processed") or 0)
            if qty > outstanding + 1e-9:
                cur.close()
                conn.close()
                return _err(
                    f"Qty {qty} melebihi sisa alokasi {outstanding} untuk PO {po.get('no_po') or po_id}"
                )
            material_name = (po.get("item_name") or "").strip()
            thickness = (po.get("tebal") or "").strip()
            color = (po.get("warna") or "").strip()
            if not material_name or not thickness or not color:
                cur.close()
                conn.close()
                return _err(
                    f"PO {po.get('no_po') or po_id} kurang spek (item/tebal/warna) untuk jadi item rencana"
                )
            customer_name = (po.get("customer") or "").strip() or "-"
            resolved.append(
                {
                    "po_id": po_id,
                    "qty": qty,
                    "thickness": thickness,
                    "material_name": material_name,
                    "color": color,
                    "emboss": _po_field_or_dash(po.get("emboss")),
                    "customer": customer_name,
                    "color_swatch": _po_field_or_dash(po.get("color_swatch")),
                }
            )

        kode_rencana = generate_code("RP")
        cur.execute(
            "INSERT INTO tbl_rencana_produksi "
            "(kode_rencana, kode_lot_wip, nama_rencana, tanggal_rencana, status) "
            "VALUES (%s, NULL, %s, %s, 'draft')",
            (kode_rencana, nama, tanggal),
        )
        rencana_id = cur.lastrowid
        for idx, item in enumerate(resolved, 1):
            from erp_master_items import lookup_backer

            backer = lookup_backer(
                material_name=item["material_name"],
                thickness=item["thickness"],
                color=item["color"],
                emboss=item.get("emboss"),
            )
            customer_id = _ensure_customer_id(cur, item["customer"])
            customer_nama = getattr(_ensure_customer_id, "last_name", None) or item["customer"]
            kode_item = generate_code("RPI")
            kode_wip = generate_code("WIP")
            cur.execute(
                "INSERT INTO tbl_rencana_item "
                "(rencana_id, kode_rencana_item, kode_lot_wip, customer_id, nama_customer, "
                "material_name, thickness, color, emboss, color_swatch, backer, keterangan, urutan) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    rencana_id,
                    kode_item,
                    kode_wip,
                    customer_id,
                    customer_nama,
                    item["material_name"],
                    item["thickness"],
                    item["color"],
                    item["emboss"],
                    item["color_swatch"],
                    backer,
                    None,
                    idx,
                ),
            )
            item_id = cur.lastrowid
            try:
                _save_item_po_selections(
                    cur, item_id, [{"po_id": item["po_id"], "qty": item["qty"]}]
                )
            except ValueError as exc:
                conn.rollback()
                cur.close()
                conn.close()
                return _err(str(exc))

        cur.execute("UPDATE tbl_rencana_produksi SET status='active' WHERE id=%s", (rencana_id,))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(
            {
                "id": rencana_id,
                "kode_rencana": kode_rencana,
                "ok": True,
                "items_created": len(resolved),
            }
        ), 201

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
                rencana_id,
                kode_item,
                kode_wip,
                customer_id,
                customer_nama,
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


@api.put("/rencana-produksi/<int:rencana_id>")
def rencana_update(rencana_id: int):
    from app import (
        _ensure_customer_id,
        _replace_item_po_selections,
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
    cur.execute("SELECT * FROM tbl_rencana_produksi WHERE id = %s", (rencana_id,))
    rencana = cur.fetchone()
    if not rencana:
        cur.close()
        conn.close()
        return _err("Rencana tidak ditemukan", 404)

    cur.execute(
        "UPDATE tbl_rencana_produksi SET nama_rencana=%s, tanggal_rencana=%s WHERE id=%s",
        (nama, tanggal, rencana_id),
    )

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
        keterangan = (item.get("keterangan") or "").strip() or None
        raw_item_id = item.get("id")
        item_id = None
        if raw_item_id is not None:
            try:
                item_id = int(raw_item_id)
            except (TypeError, ValueError):
                cur.close()
                conn.close()
                return _err("id item tidak valid")
            cur.execute(
                "SELECT id FROM tbl_rencana_item WHERE id=%s AND rencana_id=%s",
                (item_id, rencana_id),
            )
            if not cur.fetchone():
                cur.close()
                conn.close()
                return _err(f"Item #{item_id} tidak ditemukan pada rencana ini", 404)
            cur.execute(
                "UPDATE tbl_rencana_item SET "
                "customer_id=%s, nama_customer=%s, material_name=%s, thickness=%s, "
                "color=%s, emboss=%s, color_swatch=%s, backer=%s, keterangan=%s, urutan=%s "
                "WHERE id=%s",
                (
                    customer_id,
                    customer_nama,
                    material_name,
                    thickness,
                    color,
                    emboss,
                    color_swatch,
                    backer,
                    keterangan,
                    idx,
                    item_id,
                ),
            )
        else:
            kode_item = generate_code("RPI")
            kode_wip = generate_code("WIP")
            cur.execute(
                "INSERT INTO tbl_rencana_item "
                "(rencana_id, kode_rencana_item, kode_lot_wip, customer_id, nama_customer, "
                "material_name, thickness, color, emboss, color_swatch, backer, keterangan, urutan) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    rencana_id,
                    kode_item,
                    kode_wip,
                    customer_id,
                    customer_nama,
                    material_name,
                    thickness,
                    color,
                    emboss,
                    color_swatch,
                    backer,
                    keterangan,
                    idx,
                ),
            )
            item_id = cur.lastrowid

        pos = item.get("pos")
        if pos is not None:
            try:
                _replace_item_po_selections(cur, item_id, pos)
            except ValueError as exc:
                conn.rollback()
                cur.close()
                conn.close()
                return _err(str(exc))
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
    return jsonify({"id": rencana_id, "ok": True, "items_saved": saved})


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
def _insert_proses_ky_lines(cur, persiapan_id: int, ky_lines):
    if not ky_lines:
        return None
    if not isinstance(ky_lines, list):
        return _err("ky_lines harus berupa array")
    for line in ky_lines:
        kode_palet = (line.get("kode_palet") or "").strip()
        kode_yl = (line.get("kode_yl") or "").strip()
        try:
            target_qty = float(line.get("target_qty") if line.get("target_qty") is not None else line.get("qty") or 0)
        except (TypeError, ValueError):
            return _err(f"Qty KY {kode_yl or '-'} harus angka")
        if not kode_palet or not kode_yl:
            return _err("Kode KY/palet dan YL wajib diisi")
        if target_qty <= 0:
            return _err(f"Qty KY {kode_yl} harus > 0")
        cur.execute(
            "SELECT id, qty FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
            (kode_palet, kode_yl),
        )
        yl_row = cur.fetchone()
        if not yl_row:
            return _err(f"YL {kode_yl} tidak ada di palet {kode_palet}. Lakukan Palet IN dulu.", 404)
        if float(yl_row.get("qty") or 0) <= 0:
            return _err(f"Stok YL {kode_yl} kosong di palet {kode_palet}.")
        if target_qty > float(yl_row.get("qty") or 0):
            return _err(f"Qty KY {kode_yl} melebihi stok ({yl_row.get('qty')}).")
        tidak_ada_sisa = 1 if line.get("tidak_ada_sisa") in (True, 1, "1", "true", "True") else 0
        cur.execute(
            "INSERT INTO tbl_persiapan_ky (persiapan_id, kode_palet, kode_yl, target_qty, status, tidak_ada_sisa) "
            "VALUES (%s,%s,%s,%s,'planned',%s)",
            (persiapan_id, kode_palet, kode_yl, target_qty, tidak_ada_sisa),
        )
    return None


def _activate_next_planned_ky(cur, persiapan_id: int):
    cur.execute(
        "SELECT id FROM tbl_persiapan_ky WHERE persiapan_id=%s AND status='active' LIMIT 1",
        (persiapan_id,),
    )
    if cur.fetchone():
        return
    cur.execute(
        "SELECT id FROM tbl_persiapan_ky WHERE persiapan_id=%s AND status='planned' ORDER BY id LIMIT 1",
        (persiapan_id,),
    )
    planned = cur.fetchone()
    if planned:
        cur.execute("UPDATE tbl_persiapan_ky SET status='active' WHERE id=%s", (planned["id"],))


@api.get("/proses/scan-rencana")
def proses_scan_rencana():
    kode = (request.args.get("q") or "").strip()
    if not kode:
        return _err("Kode kosong")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT i.id, i.kode_rencana_item, i.kode_lot_wip, i.kode_kulit, i.material_name, "
        "i.thickness, i.color, i.emboss, i.color_swatch, r.kode_rencana, r.nama_rencana, "
        "r.tanggal_rencana, i.nama_customer "
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
        return _err("Rencana produksi tidak ditemukan", 404)
    cur.execute(
        "SELECT p.id AS po_link_id, po.id AS po_id, po.no_po, po.item_name, "
        "p.qty_outstanding, p.qty_proses "
        "FROM tbl_rencana_item_po p "
        "JOIN tbl_master_po po ON po.id = p.po_id "
        "WHERE p.item_id = %s ORDER BY po.no_po",
        (item["id"],),
    )
    item_material = (item.get("material_name") or "").strip()
    po_list = []
    for po in cur.fetchall():
        row = _row(po)
        po_material = (row.get("item_name") or "").strip()
        row["material_name"] = item_material or po_material or (item.get("kode_kulit") or "").strip()
        row["thickness"] = item.get("thickness")
        row["color"] = item.get("color")
        row["emboss"] = item.get("emboss")
        row["color_swatch"] = item.get("color_swatch")
        row["qty"] = row.get("qty_outstanding")
        po_list.append(row)
    out = _row(item)
    if not (out.get("material_name") or "").strip():
        out["material_name"] = (
            (po_list[0].get("material_name") if po_list else "")
            or (item.get("kode_kulit") or "").strip()
            or None
        )
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
        f"SELECT pk.*, {_sql_no_so_from_master('pk')} "
        "FROM tbl_persiapan_kulit pk ORDER BY pk.date_created DESC LIMIT 100"
    )
    persiapan_list = _rows(cur.fetchall())
    cur.execute(
        "SELECT i.id, i.kode_rencana_item, i.kode_lot_wip, i.material_name, i.kode_kulit, "
        "i.thickness, i.color, i.emboss, i.color_swatch, r.kode_rencana, r.nama_rencana, "
        "i.nama_customer "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        ""
        "WHERE r.status IN ('draft','active') AND i.kode_lot_wip IS NOT NULL "
        "ORDER BY r.date_created DESC"
    )
    rencana_items = _rows(cur.fetchall())
    cur.execute(
        "SELECT jenis, nama_treatment FROM tbl_master_treatment ORDER BY jenis, nama_treatment"
    )
    treatments = _rows(cur.fetchall())
    cur.execute(
        "SELECT DISTINCT y.kode_palet FROM tbl_yl y "
        "WHERE COALESCE(y.qty,0) > 0 ORDER BY y.kode_palet"
    )
    palet_options = [r["kode_palet"] for r in cur.fetchall() if r.get("kode_palet")]
    cur.close()
    conn.close()
    return jsonify(
        {
            "persiapan_list": persiapan_list,
            "rencana_items": rencana_items,
            "treatments": treatments,
            "palet_options": palet_options,
        }
    )


@api.get("/proses/next-wip")
def proses_next_wip():
    from app import preview_wip_persiapan_code

    return jsonify({"kode_wip": preview_wip_persiapan_code()})


@api.post("/proses")
def proses_create():
    from app import allocate_wip_persiapan_code, ensure_extended_tables, ensure_master_treatment, generate_code

    body = request.get_json(silent=True) or {}
    item_id = body.get("rencana_item_id")
    kode_scan = (body.get("kode_scan") or "").strip()
    treatment_jenis = (body.get("treatment_jenis") or "PU").strip()
    selected = body.get("treatment_list") or []
    if isinstance(selected, str):
        selected = [s.strip() for s in selected.split(",") if s.strip()]
    po_ids = body.get("po_ids") or []
    if isinstance(po_ids, str):
        po_ids = [x.strip() for x in po_ids.split(",") if x.strip()]
    po_ids = [int(x) for x in po_ids if str(x).strip().isdigit()]
    ky_lines = body.get("ky_lines") or []

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_master_treatment(cur)
    ensure_extended_tables(cur)
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
    if not selected:
        cur.close()
        conn.close()
        return _err("Pilih minimal satu treatment dari master.")

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
        "SELECT COUNT(*) AS cnt FROM tbl_rencana_item_po WHERE item_id = %s",
        (item_id,),
    )
    po_count = int((cur.fetchone() or {}).get("cnt") or 0)
    if po_count and not po_ids and not ky_lines:
        cur.close()
        conn.close()
        return _err("Pilih minimal satu baris PO / qty atau material KY untuk proses.")
    no_po = ""
    if po_ids:
        placeholders = ",".join(["%s"] * len(po_ids))
        cur.execute(
            f"SELECT po.no_po FROM tbl_rencana_item_po p "
            f"JOIN tbl_master_po po ON po.id = p.po_id "
            f"WHERE p.item_id = %s AND p.po_id IN ({placeholders}) ORDER BY po.no_po",
            (item_id, *po_ids),
        )
        no_po = ", ".join(r["no_po"] for r in cur.fetchall())
    elif po_count:
        cur.execute(
            "SELECT po.no_po FROM tbl_rencana_item_po p "
            "JOIN tbl_master_po po ON po.id = p.po_id WHERE p.item_id = %s LIMIT 1",
            (item_id,),
        )
        po_row = cur.fetchone()
        no_po = po_row["no_po"] if po_row else ""
    kode_proses = generate_code("PR")
    kode_wip = allocate_wip_persiapan_code(cur)
    treatment_list_str = ", ".join(selected)
    cur.execute(
        "INSERT INTO tbl_persiapan_kulit "
        "(kode_wip, kode_rencana, kode_proses, rencana_item_id, no_po, warna, tebal, emboss, "
        "treatment_jenis, treatment_list, status) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'draft')",
        (
            kode_wip,
            item["kode_rencana_item"],
            kode_proses,
            item_id,
            no_po,
            item["color"],
            item["thickness"],
            item["emboss"],
            treatment_jenis,
            treatment_list_str,
        ),
    )
    persiapan_id = cur.lastrowid
    ky_err = _insert_proses_ky_lines(cur, persiapan_id, ky_lines)
    if ky_err:
        conn.rollback()
        cur.close()
        conn.close()
        return ky_err
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": persiapan_id, "kode_proses": kode_proses, "kode_wip": kode_wip, "ok": True}), 201


@api.get("/proses/<int:persiapan_id>")
def proses_detail_api(persiapan_id: int):
    from app import ensure_extended_tables, ensure_master_treatment

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    ensure_master_treatment(cur)
    conn.commit()
    cur.execute(
        f"SELECT pk.*, {_sql_no_so_from_master('pk')} "
        "FROM tbl_persiapan_kulit pk WHERE pk.id = %s",
        (persiapan_id,),
    )
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
    cur.execute(
        f"SELECT pk.*, {_sql_no_so_from_master('pk')} "
        "FROM tbl_persiapan_kulit pk WHERE pk.id = %s",
        (persiapan_id,),
    )
    persiapan = cur.fetchone()
    if not persiapan:
        cur.close()
        conn.close()
        return _err("Data tidak ditemukan", 404)
    cur.execute(
        "SELECT kode_palet, kode_yl, target_qty, actual_qty, qty_consumed, status "
        "FROM tbl_persiapan_ky WHERE persiapan_id=%s ORDER BY id",
        (persiapan_id,),
    )
    ky_sessions = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(
        {
            "persiapan": _row(persiapan),
            "ky_sessions": ky_sessions,
            "title": "STIKER LOT WIP PRODUKSI",
        }
    )


@api.post("/proses/<int:persiapan_id>/actions")
def proses_actions(persiapan_id: int):
    from app import _consume_yl_for_ky_session, ensure_extended_tables

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

    status = (persiapan.get("status") or "").strip()
    locked = status in ("saved", "completed")

    def _need_started():
        if status != "started":
            return _err("Mulai proses (Start) dulu sebelum KY/ukur.")
        return None

    msg = "ok"
    try:
        if action == "start":
            if status not in ("draft", "started"):
                cur.close()
                conn.close()
                return _err(f"Tidak dapat Start dari status {status or '-'}")
            cur.execute(
                "UPDATE tbl_persiapan_kulit SET status='started' WHERE id=%s",
                (persiapan_id,),
            )
            _activate_next_planned_ky(cur, persiapan_id)
            msg = "Proses dimulai"

        elif action == "scan_ky":
            err = _need_started()
            if err:
                cur.close()
                conn.close()
                return err
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
                return _err("Kode KY/palet wajib diisi.")
            if not kode_yl:
                cur.close()
                conn.close()
                return _err("Kode YL wajib diisi agar stok bisa dikurangi saat selesai KY.")
            cur.execute(
                "SELECT id, qty FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
                (kode_palet, kode_yl),
            )
            yl_row = cur.fetchone()
            if not yl_row:
                cur.close()
                conn.close()
                return _err("KY/YL tidak ada di stok palet. Lakukan Palet IN dulu.", 404)
            if float(yl_row.get("qty") or 0) <= 0:
                cur.close()
                conn.close()
                return _err(f"Stok YL {kode_yl} kosong di palet {kode_palet}.")
            cur.execute(
                "INSERT INTO tbl_persiapan_ky (persiapan_id, kode_palet, kode_yl, target_qty, status) "
                "VALUES (%s,%s,%s,%s,'active')",
                (persiapan_id, kode_palet, kode_yl, target_qty),
            )
            cur.execute(
                "INSERT INTO tbl_persiapan_scan (persiapan_id, kode_palet, kode_yl) VALUES (%s,%s,%s)",
                (persiapan_id, kode_palet, kode_yl),
            )
            msg = f"KY {kode_palet} / YL {kode_yl} aktif"

        elif action == "add_ukur":
            err = _need_started()
            if err:
                cur.close()
                conn.close()
                return err
            ky_id = body.get("ky_id")
            size_val = float(body.get("size_val") or 0)
            if not ky_id or size_val <= 0:
                cur.close()
                conn.close()
                return _err("ky_id dan size_val (>0) wajib")
            cur.execute(
                "SELECT id, status FROM tbl_persiapan_ky WHERE id=%s AND persiapan_id=%s",
                (ky_id, persiapan_id),
            )
            ky_row = cur.fetchone()
            if not ky_row or ky_row.get("status") != "active":
                cur.close()
                conn.close()
                return _err("KY aktif tidak ditemukan")
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

        elif action == "activate_ky":
            err = _need_started()
            if err:
                cur.close()
                conn.close()
                return err
            ky_id = body.get("ky_id")
            if not ky_id:
                cur.close()
                conn.close()
                return _err("ky_id wajib")
            cur.execute(
                "SELECT id, status FROM tbl_persiapan_ky WHERE id=%s AND persiapan_id=%s",
                (ky_id, persiapan_id),
            )
            target_ky = cur.fetchone()
            if not target_ky:
                cur.close()
                conn.close()
                return _err("KY tidak ditemukan", 404)
            if target_ky.get("status") == "selesai":
                cur.close()
                conn.close()
                return _err("KY sudah selesai")
            if target_ky.get("status") != "active":
                cur.execute(
                    "UPDATE tbl_persiapan_ky SET status='planned' "
                    "WHERE persiapan_id=%s AND status='active' AND id<>%s",
                    (persiapan_id, ky_id),
                )
                cur.execute(
                    "UPDATE tbl_persiapan_ky SET status='active' WHERE id=%s",
                    (ky_id,),
                )
                msg = "KY diaktifkan"
            else:
                msg = "KY sudah aktif"

        elif action == "selesai_ky":
            err = _need_started()
            if err:
                cur.close()
                conn.close()
                return err
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
            if ky.get("status") != "active":
                cur.close()
                conn.close()
                return _err("KY sudah selesai")
            target = float(ky["target_qty"] or 0)
            actual = float(ky["actual_qty"] or 0)
            consumed = _consume_yl_for_ky_session(cur, ky, persiapan)
            selisih = actual - target
            cur.execute("UPDATE tbl_persiapan_ky SET status='selesai' WHERE id=%s", (ky_id,))
            _activate_next_planned_ky(cur, persiapan_id)
            if (
                persiapan.get("rencana_item_id")
                and selisih != 0
                and int(ky.get("tidak_ada_sisa") or 0) != 1
            ):
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
            msg = (
                f"KY selesai. Target: {target}, Aktual: {actual}, "
                f"stok YL OUT: {consumed}"
            )

        elif action == "scan":
            err = _need_started()
            if err:
                cur.close()
                conn.close()
                return err
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
            err = _need_started()
            if err:
                cur.close()
                conn.close()
                return err
            ukur_id = body.get("ukur_id")
            cur.execute(
                "SELECT u.size_val, u.ky_id, k.status AS ky_status, k.yl_consumed "
                "FROM tbl_persiapan_ukur u "
                "LEFT JOIN tbl_persiapan_ky k ON k.id = u.ky_id "
                "WHERE u.id=%s AND u.persiapan_id=%s",
                (ukur_id, persiapan_id),
            )
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return _err("Ukur tidak ditemukan", 404)
            if row.get("ky_status") == "selesai" or int(row.get("yl_consumed") or 0) == 1:
                cur.close()
                conn.close()
                return _err("Tidak dapat hapus ukur dari KY yang sudah selesai (stok sudah OUT)")
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
            if locked:
                cur.close()
                conn.close()
                return _err("Persiapan sudah selesai / tersimpan")
            if status != "started":
                cur.close()
                conn.close()
                return _err("Start proses dulu sebelum Simpan")
            cur.execute(
                "SELECT id FROM tbl_persiapan_ky WHERE persiapan_id=%s AND status='active' LIMIT 1",
                (persiapan_id,),
            )
            if cur.fetchone():
                cur.close()
                conn.close()
                return _err("Selesaikan KY aktif dulu sebelum Simpan")
            cur.execute(
                "SELECT COALESCE(total_size,0) AS tot FROM tbl_persiapan_kulit WHERE id=%s",
                (persiapan_id,),
            )
            tot = float((cur.fetchone() or {}).get("tot") or 0)
            if tot <= 0:
                cur.close()
                conn.close()
                return _err("Belum ada ukur (total size=0); tidak dapat menyelesaikan persiapan")
            # completed = siap packing/label; packing menerima saved|completed
            cur.execute(
                "UPDATE tbl_persiapan_kulit SET status='completed', date_saved=NOW() WHERE id=%s",
                (persiapan_id,),
            )
            msg = "Persiapan selesai (completed). Label siap dicetak; WIP bisa packing."

        elif action == "reprint":
            if status not in ("saved", "completed"):
                cur.close()
                conn.close()
                return _err("Reprint hanya setelah persiapan tersimpan/selesai")
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
    except ValueError as exc:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(exc))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "message": msg})


# ---- lab ----
@api.get("/lab/options")
def lab_options():
    from app import ensure_extended_tables, ensure_lab_tables, ensure_rencana_tables

    only_with_proses = (request.args.get("only_with_proses") or "0").strip() in (
        "1",
        "true",
        "yes",
    )

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_lab_tables(cur)
    ensure_rencana_tables(cur)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT ri.id, ri.kode_rencana_item, ri.kode_lot_wip, ri.kode_kulit, ri.color, ri.thickness, "
        "rp.nama_rencana, rp.tanggal_rencana, ri.nama_customer, "
        "pk.id AS persiapan_id, pk.kode_proses, pk.status AS persiapan_status, "
        "pk.treatment_jenis, pk.total_size "
        "FROM tbl_rencana_item ri "
        "JOIN tbl_rencana_produksi rp ON rp.id = ri.rencana_id "
        ""
        "LEFT JOIN tbl_persiapan_kulit pk ON pk.id = ("
        "  SELECT p2.id FROM tbl_persiapan_kulit p2 "
        "  WHERE p2.rencana_item_id = ri.id "
        "  ORDER BY FIELD(p2.status,'completed','saved','started','draft'), p2.id DESC "
        "  LIMIT 1"
        ") "
        "WHERE rp.status IN ('draft','active') "
        + (
            "AND pk.status IN ('started','saved','completed') "
            if only_with_proses
            else ""
        )
        + "ORDER BY "
        "CASE WHEN pk.status IN ('started','saved','completed') THEN 0 ELSE 1 END, "
        "rp.tanggal_rencana DESC, ri.urutan"
    )
    rencana_items = _rows(cur.fetchall())
    for it in rencana_items:
        st = (it.get("persiapan_status") or "").strip()
        it["has_proses"] = st in ("started", "saved", "completed")
    from erp_raw_materials import list_materials

    kimia_list = [
        {
            "kode_kimia": r["code"],
            "nama_kimia": r["name"],
            "satuan": r.get("unit") or "kg",
        }
        for r in list_materials("kimia")
        if (r.get("code") or "").strip()
    ]
    try:
        cur.execute("SELECT nama_resep FROM master_resep ORDER BY nama_resep")
        reseps = [r["nama_resep"] for r in cur.fetchall()]
    except Exception:
        reseps = []
    cur.close()
    conn.close()
    return jsonify(
        {
            "rencana_items": rencana_items,
            "kimia_list": kimia_list,
            "reseps": reseps,
            "gate": {
                "link_rpi_requires_proses": True,
                "allowed_persiapan_status": ["started", "saved", "completed"],
            },
        }
    )


@api.get("/lab")
def lab_list():
    from app import ensure_lab_tables, ensure_rencana_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_lab_tables(cur)
    ensure_rencana_tables(cur)
    conn.commit()
    # Pastikan kolom link RPI ada (install lama).
    from app import _col_names

    lab_cols = _col_names(cur, "tbl_lab_lot")
    if "rencana_item_id" not in lab_cols:
        cur.execute(
            "ALTER TABLE tbl_lab_lot ADD COLUMN rencana_item_id INT DEFAULT NULL"
        )
        conn.commit()

    cur.execute(
        "SELECT l.id AS lot_id, l.kode_lot_warna, l.nama_lot_warna, l.status, l.date_created, "
        "l.rencana_item_id, "
        "d.id AS detail_id, d.kode_kimia, d.nama_kimia, d.resep, d.satuan, d.qty, d.remarks, "
        "ri.kode_rencana_item, ri.kode_lot_wip, ri.color, ri.thickness, "
        "rp.nama_rencana, rp.tanggal_rencana, ri.nama_customer "
        "FROM tbl_lab_lot l "
        "JOIN tbl_lab_lot_detail d ON d.kode_lot_warna = l.kode_lot_warna "
        "LEFT JOIN tbl_rencana_item ri ON ri.id = l.rencana_item_id "
        "LEFT JOIN tbl_rencana_produksi rp ON rp.id = ri.rencana_id "
        ""
        "ORDER BY COALESCE(l.date_created, rp.tanggal_rencana) DESC, l.kode_lot_warna, d.id "
        "LIMIT 500"
    )
    flat = _rows(cur.fetchall())
    cur.close()
    conn.close()

    # Group per lot agar UI Vue tidak mengulang header.
    lots_map: dict[str, dict] = {}
    order: list[str] = []
    for row in flat:
        kode = row.get("kode_lot_warna") or ""
        if kode not in lots_map:
            order.append(kode)
            lots_map[kode] = {
                "lot_id": row.get("lot_id"),
                "kode_lot_warna": kode,
                "nama_lot_warna": row.get("nama_lot_warna"),
                "status": row.get("status"),
                "date_created": row.get("date_created"),
                "rencana_item_id": row.get("rencana_item_id"),
                "kode_rencana_item": row.get("kode_rencana_item"),
                "kode_lot_wip": row.get("kode_lot_wip"),
                "nama_customer": row.get("nama_customer"),
                "nama_rencana": row.get("nama_rencana"),
                "tanggal_rencana": row.get("tanggal_rencana"),
                "color": row.get("color"),
                "thickness": row.get("thickness"),
                "jml_kimia": 0,
                "total_qty": 0.0,
                "items": [],
            }
        lot = lots_map[kode]
        qty = float(row.get("qty") or 0)
        lot["jml_kimia"] += 1
        lot["total_qty"] += qty
        lot["items"].append(
            {
                "detail_id": row.get("detail_id"),
                "kode_kimia": row.get("kode_kimia"),
                "nama_kimia": row.get("nama_kimia"),
                "resep": row.get("resep"),
                "satuan": row.get("satuan"),
                "qty": row.get("qty"),
                "remarks": row.get("remarks"),
            }
        )

    lots = [lots_map[k] for k in order]
    return jsonify({"lots": lots, "flat": flat, "ok": True})


@api.post("/lab")
def lab_create():
    from app import (
        _col_names,
        ensure_extended_tables,
        ensure_lab_tables,
        ensure_rencana_tables,
        generate_code,
    )

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
    ensure_extended_tables(cur)
    conn.commit()
    # ensure rencana_item_id column
    lab_cols = _col_names(cur, "tbl_lab_lot")
    if "rencana_item_id" not in lab_cols:
        cur.execute(
            "ALTER TABLE tbl_lab_lot ADD COLUMN rencana_item_id INT DEFAULT NULL"
        )
        conn.commit()

    # Gate: link RPI hanya jika sudah ada Persiapan (Proses) started/saved/completed.
    if rencana_item_id is not None:
        try:
            rencana_item_id = int(rencana_item_id)
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("rencana_item_id tidak valid")
        cur.execute("SELECT id FROM tbl_rencana_item WHERE id=%s", (rencana_item_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return _err("Item rencana tidak ditemukan", 404)
        cur.execute(
            "SELECT id, kode_proses, status FROM tbl_persiapan_kulit "
            "WHERE rencana_item_id=%s AND status IN ('started','saved','completed') "
            "ORDER BY id DESC LIMIT 1",
            (rencana_item_id,),
        )
        prep = cur.fetchone()
        if not prep:
            cur.close()
            conn.close()
            return _err(
                "Link RPI memerlukan Persiapan (Proses) yang sudah di-Start. "
                "Buat/Start proses dulu, atau buat lot Lab tanpa link RPI."
            )

    kode_lot_warna = generate_code("LW")
    cur.execute(
        "INSERT INTO tbl_lab_lot (kode_lot_warna, nama_lot_warna, rencana_item_id) VALUES (%s, %s, %s)",
        (kode_lot_warna, nama_lot_warna, rencana_item_id),
    )
    for r in rows:
        kode_kimia = (r.get("kode_kimia") or "").strip()
        resep = (r.get("resep") or "").strip() or None
        satuan = (r.get("satuan") or "kg").strip() or "kg"
        try:
            qty = float(r.get("qty") or 0)
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err(f"Qty tidak valid untuk kimia {kode_kimia}")
        if qty <= 0:
            cur.close()
            conn.close()
            return _err(f"Qty harus > 0 untuk kimia {kode_kimia}")
        remarks = (r.get("remarks") or "").strip() or None
        from erp_raw_materials import fetch_material_by_code

        kimia = fetch_material_by_code(kode_kimia, material_type="kimia")
        if kimia and not (r.get("satuan") or "").strip():
            satuan = (kimia.get("unit") or satuan or "kg").strip() or "kg"
        cur.execute(
            "INSERT INTO tbl_lab_lot_detail "
            "(kode_lot_warna, kode_kimia, nama_kimia, resep, satuan, qty, remarks) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                kode_lot_warna,
                kode_kimia,
                (kimia.get("name") if kimia else kode_kimia),
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
def _erp_lot_nos_for_source_details(source_ids) -> dict[int, str]:
    """Lot No dari baris item SO ERP (po_details.thi_line_ref / system_reference)."""
    out: dict[int, str] = {}
    ids: list[int] = []
    seen: set[int] = set()
    for sid in source_ids or []:
        try:
            i = int(sid)
        except (TypeError, ValueError):
            continue
        if i and i not in seen:
            seen.add(i)
            ids.append(i)
    if not ids:
        return out
    try:
        from erp_customers import _connect

        erp = _connect()
        ecur = erp.cursor(dictionary=True)
        placeholders = ",".join(["%s"] * len(ids))
        ecur.execute(
            "SELECT pod.id, pod.thi_line_ref, pod.system_reference, "
            "(SELECT pd.lot_number FROM production_details pd "
            " WHERE pd.po_detail_id = pod.id ORDER BY pd.id DESC LIMIT 1) AS lot_number "
            f"FROM po_details pod WHERE pod.id IN ({placeholders})",
            tuple(ids),
        )
        for row in ecur.fetchall() or []:
            try:
                sid = int(row.get("id"))
            except (TypeError, ValueError):
                continue
            for key in ("thi_line_ref", "system_reference", "lot_number"):
                val = (row.get(key) or "").strip()
                if val:
                    out[sid] = val
                    break
        ecur.close()
        erp.close()
    except Exception:
        pass
    return out


def _erp_lot_no_for_source_detail(source_detail_id: int | None) -> str:
    """Lot No dari baris item SO ERP (po_details.thi_line_ref / system_reference)."""
    if not source_detail_id:
        return ""
    try:
        sid = int(source_detail_id)
    except (TypeError, ValueError):
        return ""
    return _erp_lot_nos_for_source_details([sid]).get(sid, "")


def _attach_erp_lot_no(rows: list) -> list:
    """Isi lot_no dari LOT NO baris SO (tbl_master_po.lot_number / thi_line_ref ERP)."""
    missing_ids = []
    for row in rows or []:
        stored = (row.get("lot_number") or row.get("lot_no") or "").strip()
        row["lot_no"] = stored
        if stored:
            continue
        sid = row.get("source_detail_id")
        try:
            sid_i = int(sid) if sid is not None else None
        except (TypeError, ValueError):
            sid_i = None
        if sid_i:
            missing_ids.append(sid_i)
    if missing_ids:
        lot_map = _erp_lot_nos_for_source_details(missing_ids)
        for row in rows or []:
            if (row.get("lot_no") or "").strip():
                continue
            sid = row.get("source_detail_id")
            try:
                sid_i = int(sid) if sid is not None else None
            except (TypeError, ValueError):
                sid_i = None
            row["lot_no"] = (lot_map.get(sid_i) or "").strip() if sid_i else ""
    return rows


def _packing_spec_for_wip(
    cur, kode_wip: str, no_po: str | None = None, rencana_item_id: int | None = None
) -> dict:
    """Ambil spek FG dari rencana item (+ PO) untuk packing list Tong Hong."""
    if rencana_item_id:
        where_sql = "i.id = %s"
        params: list = [int(rencana_item_id)]
    else:
        where_sql = "(i.kode_lot_wip = %s OR pk.kode_wip = %s)"
        params = [kode_wip, kode_wip]
    cur.execute(
        "SELECT i.kode_rencana_item, i.kode_lot_wip, i.thickness, i.color, i.emboss, "
        "i.color_swatch, i.backer, i.material_name, i.keterangan, "
        "i.nama_customer, "
        "po.no_po, po.no_so, po.item_name, po.source_detail_id, po.warna AS po_warna, po.tebal AS po_tebal, "
        "po.emboss AS po_emboss, po.color_swatch AS po_color_swatch "
        "FROM tbl_rencana_item i "
        "LEFT JOIN tbl_persiapan_kulit pk ON pk.rencana_item_id = i.id "
        "LEFT JOIN tbl_rencana_item_po rip ON rip.item_id = i.id "
        "LEFT JOIN tbl_master_po po ON po.id = rip.po_id "
        f"WHERE {where_sql} "
        "ORDER BY CASE WHEN po.no_po = %s THEN 0 ELSE 1 END, i.id "
        "LIMIT 1",
        (*params, no_po or ""),
    )
    row = cur.fetchone() or {}
    thickness = row.get("thickness") or row.get("po_tebal") or ""
    color = row.get("color") or row.get("po_warna") or ""
    emboss = row.get("emboss") or row.get("po_emboss") or ""
    swatch = row.get("color_swatch") or row.get("po_color_swatch") or ""
    description = row.get("item_name") or row.get("material_name") or ""
    if emboss and description and emboss.upper() not in description.upper():
        description = f"{description} ({emboss})" if description else emboss
    elif emboss and not description:
        description = emboss
    return {
        "description": description or "-",
        "thickness": thickness or "-",
        "color": color or "-",
        "softness": "-",
        "color_swatch": swatch or "-",
        "work_order": row.get("kode_lot_wip") or kode_wip or "-",
        "kode_rencana_item": row.get("kode_rencana_item") or "",
        "material_name": row.get("material_name") or "",
        "emboss": emboss or "",
        "backer": row.get("backer") or "",
        "customer_from_rencana": row.get("nama_customer") or "",
        "no_so": row.get("no_so") or "",
        "source_detail_id": row.get("source_detail_id"),
        "lot_no": _erp_lot_no_for_source_detail(row.get("source_detail_id"))
        or row.get("kode_lot_wip")
        or kode_wip
        or "-",
    }


def _packing_print_payload(cur, packing: dict) -> dict:
    cur.execute(
        "SELECT * FROM tbl_packing_roll WHERE packing_id = %s ORDER BY roll_no",
        (packing["id"],),
    )
    rolls = _rows(cur.fetchall())
    spec = _packing_spec_for_wip(cur, packing.get("kode_wip") or "", packing.get("no_po"))
    total_rolls = len(rolls)
    total_pieces = int(packing.get("total_lembar") or 0)
    if not total_pieces:
        total_pieces = sum(int(r.get("lembar") or 0) for r in rolls)
    total_qty = float(packing.get("total_ukuran") or 0)
    if not total_qty:
        total_qty = sum(float(r.get("ukuran") or 0) for r in rolls)
    header = {
        **_row(packing),
        "customer": packing.get("customer") or spec.get("customer_from_rencana") or "-",
        "description": spec["description"],
        "thickness": spec["thickness"],
        "color": spec["color"],
        "softness": packing.get("softness") or spec["softness"],
        "color_swatch": spec["color_swatch"],
        "work_order": spec["work_order"],
        "emboss": spec["emboss"],
        "backer": spec["backer"],
        "material_name": spec["material_name"],
        "kode_rencana_item": spec["kode_rencana_item"],
        "total_rolls": total_rolls,
        "total_pieces": total_pieces,
        "total_quantity": round(total_qty, 2),
        "qty_unit": "SF",
        "gross_weight": packing.get("gross_weight"),
        "net_weight": packing.get("net_weight"),
        "form_code": "QER-48-A/0",
        "company_name": "PT. TONG HONG TANNERY INDONESIA",
        "company_name_zh": "東崇皮革印尼有限公司",
    }
    return {"packing": header, "rolls": rolls, "spec": spec}


def _format_label_size_part(val: float) -> str:
    if abs(val - round(val)) < 1e-9:
        return str(int(round(val)))
    s = f"{val:.2f}".rstrip("0").rstrip(".")
    return s or "0"


def _parse_sizes_text(text: str | None) -> list[float]:
    if not text:
        return []
    out: list[float] = []
    for part in str(text).split("+"):
        part = part.strip()
        if not part:
            continue
        try:
            val = float(part)
        except (TypeError, ValueError):
            continue
        if val > 0:
            out.append(val)
    return out


def _fg_code_taken(cur, kode: str) -> bool:
    kode = (kode or "").strip()
    if not kode:
        return True
    cur.execute("SELECT 1 FROM tbl_packing WHERE kode_packing=%s LIMIT 1", (kode,))
    if cur.fetchone():
        return True
    from app import _col_names

    roll_cols = _col_names(cur, "tbl_packing_roll")
    if "kode_packing" in roll_cols:
        cur.execute(
            "SELECT 1 FROM tbl_packing_roll WHERE kode_packing=%s LIMIT 1", (kode,)
        )
        if cur.fetchone():
            return True
    return False


def _alloc_unique_fg_code(cur, max_try: int = 30) -> str:
    from app import generate_code

    for _ in range(max_try):
        kode = generate_code("FG")
        if not _fg_code_taken(cur, kode):
            return kode
    raise ValueError("Gagal generate kode packing FG unik")


def _backfill_roll_kode_packing(cur) -> None:
    from app import _col_names

    roll_cols = _col_names(cur, "tbl_packing_roll")
    if "kode_packing" not in roll_cols:
        return
    cur.execute(
        "SELECT id FROM tbl_packing_roll "
        "WHERE kode_packing IS NULL OR TRIM(kode_packing)='' "
        "ORDER BY packing_id, roll_no, id"
    )
    for row in cur.fetchall():
        kode = _alloc_unique_fg_code(cur)
        cur.execute(
            "UPDATE tbl_packing_roll SET kode_packing=%s WHERE id=%s",
            (kode, row["id"]),
        )


def _packing_roll_label_payload(
    packing: dict,
    roll: dict,
    spec: dict | None = None,
    sizes: list | None = None,
) -> dict:
    from datetime import date

    spec = spec or {}
    size_vals: list[float] = []
    for s in sizes or []:
        try:
            v = float(s)
        except (TypeError, ValueError):
            continue
        if v > 0:
            size_vals.append(v)
    sizes_text = "+".join(_format_label_size_part(v) for v in size_vals)
    if not sizes_text and roll.get("sizes_text"):
        sizes_text = str(roll.get("sizes_text") or "").strip()
        if sizes_text and not size_vals:
            size_vals = _parse_sizes_text(sizes_text)

    color = spec.get("color") or "-"
    swatch = (spec.get("color_swatch") or "").strip()
    if swatch and swatch not in str(color):
        color = f"{color} ({swatch})" if color and color != "-" else swatch

    lot_no = spec.get("lot_no") or spec.get("work_order") or packing.get("kode_wip") or "-"
    factory_code = spec.get("no_so") or packing.get("no_so") or packing.get("no_po") or "-"
    qty_unit = spec.get("qty_unit") or "SF"
    ukuran = float(roll.get("ukuran") or 0)
    qty_text = f"{int(ukuran) if ukuran == int(ukuran) else ukuran:g} {qty_unit}"
    roll_kode = (roll.get("kode_packing") or packing.get("kode_packing") or "").strip()

    return {
        "kode_packing": roll_kode,
        "kode_wip": packing.get("kode_wip"),
        "lot_no": lot_no,
        "roll_no": roll.get("roll_no"),
        "lembar": roll.get("lembar"),
        "ukuran": roll.get("ukuran"),
        "qty_text": qty_text,
        "remark": roll.get("remark") or "",
        "no_po": packing.get("no_po"),
        "no_so": factory_code,
        "factory_prod_code": factory_code,
        "customer": packing.get("customer") or spec.get("customer_from_rencana") or "-",
        "description": spec.get("description") or packing.get("description") or "-",
        "color": color or "-",
        "thickness": spec.get("thickness") or "-",
        "color_swatch": spec.get("color_swatch") or "",
        "emboss": spec.get("emboss") or "-",
        "softness": packing.get("softness") or spec.get("softness") or "SOFT",
        "mass_material": packing.get("softness") or spec.get("softness") or "SOFT",
        "gross_weight": packing.get("gross_weight"),
        "net_weight": packing.get("net_weight"),
        "work_order": lot_no,
        "qty_unit": qty_unit,
        "producing_date": date.today().isoformat(),
        "expiration_text": "1 年 (One Year)",
        "anti_moldy": "",
        "moisture": "",
        "sizes": size_vals,
        "sizes_text": sizes_text,
        "md_code": "ND",
        "company_name": "PT. TONG HONG TANNERY INDONESIA",
        "company_name_zh": "東崇皮革印尼有限公司",
    }


@api.get("/packing/pending-rpi")
def packing_pending_rpi():
    """RPI dengan persiapan selesai yang belum packing finished."""
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    _backfill_roll_kode_packing(cur)
    conn.commit()
    cur.execute(
        "SELECT i.id AS rencana_item_id, i.kode_rencana_item, i.kode_lot_wip, i.material_name, "
        "r.nama_rencana, i.keterangan, i.nama_customer, pk.kode_wip AS prep_kode_wip, "
        "pk.total_size AS prep_total_size, pk.status AS persiapan_status, "
        "po_line.no_po, po_line.no_so, po_line.po_id, po_line.source_detail_id, po_line.qty_rpi, "
        "COALESCE(prog.packing_id, 0) AS packing_id, prog.kode_packing, prog.packing_status, "
        "COALESCE(prog.qty_actual, 0) AS qty_actual, COALESCE(prog.next_roll_no, 1) AS next_roll_no "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        "JOIN tbl_persiapan_kulit pk ON pk.id = ( "
        "  SELECT p2.id FROM tbl_persiapan_kulit p2 "
        "  WHERE p2.rencana_item_id = i.id "
        "  AND p2.status IN ('started', 'saved', 'completed') "
        "  ORDER BY FIELD(p2.status, 'completed', 'saved', 'started'), p2.id DESC "
        "  LIMIT 1 "
        ") "
        "LEFT JOIN ( "
        "SELECT rip.item_id, po.no_po, po.no_so, po.id AS po_id, po.source_detail_id, "
        "  SUM(rip.qty_proses) AS qty_rpi "
        "  FROM tbl_rencana_item_po rip "
        "  JOIN tbl_master_po po ON po.id = rip.po_id "
        "  GROUP BY rip.item_id, po.no_po, po.no_so, po.id, po.source_detail_id "
        ") po_line ON po_line.item_id = i.id "
        "LEFT JOIN ( "
        "  SELECT p.kode_wip, p.id AS packing_id, p.kode_packing, p.status AS packing_status, "
        "  COALESCE(SUM(pr.ukuran), 0) AS qty_actual, "
        "  COALESCE(MAX(pr.roll_no), 0) + 1 AS next_roll_no "
        "  FROM tbl_packing p "
        "  LEFT JOIN tbl_packing_roll pr ON pr.packing_id = p.id "
        "  WHERE p.status = 'in_progress' "
        "  GROUP BY p.id, p.kode_wip, p.kode_packing, p.status "
        ") prog ON prog.kode_wip IN (i.kode_lot_wip, pk.kode_wip) "
        "WHERE NOT EXISTS ( "
        "  SELECT 1 FROM tbl_packing pf "
        "  WHERE pf.status = 'finished' "
        "  AND (pf.kode_wip = i.kode_lot_wip OR pf.kode_wip = pk.kode_wip) "
        ") "
        "ORDER BY i.kode_rencana_item, i.id"
    )
    rows = _rows(cur.fetchall())
    seen: set[int] = set()
    items = []
    for row in rows:
        rid = int(row.get("rencana_item_id") or 0)
        if not rid or rid in seen:
            continue
        seen.add(rid)
        deskripsi = (row.get("nama_rencana") or "").strip()
        if (row.get("keterangan") or "").strip():
            deskripsi = f"{deskripsi} · {row['keterangan']}".strip(" ·")
        row["deskripsi"] = deskripsi or row.get("nama_rencana") or "—"
        so_lot = _erp_lot_no_for_source_detail(row.get("source_detail_id"))
        row["lot_no"] = so_lot or row.get("kode_lot_wip") or row.get("prep_kode_wip")
        row["so_lot_no"] = so_lot
        row["kode_wip"] = row.get("prep_kode_wip") or row.get("kode_lot_wip")
        row["qty_rpi"] = float(row.get("qty_rpi") or row.get("prep_total_size") or 0)
        items.append(row)
    cur.close()
    conn.close()
    return jsonify(items)


@api.get("/packing/rpi/<int:rencana_item_id>/printed-rolls")
def packing_rpi_printed_rolls(rencana_item_id: int):
    """Roll yang sudah dicetak untuk satu baris RPI beserta kode packing per roll."""
    from app import ensure_extended_tables, _col_names

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    _backfill_roll_kode_packing(cur)
    conn.commit()
    cur.execute(
        "SELECT i.kode_lot_wip, pk.kode_wip AS prep_kode_wip "
        "FROM tbl_rencana_item i "
        "LEFT JOIN tbl_persiapan_kulit pk ON pk.rencana_item_id = i.id "
        "WHERE i.id = %s LIMIT 1",
        (rencana_item_id,),
    )
    item = cur.fetchone()
    if not item:
        cur.close()
        conn.close()
        return _err("Item RPI tidak ditemukan", 404)
    wip_codes = {
        (item.get("kode_lot_wip") or "").strip(),
        (item.get("prep_kode_wip") or "").strip(),
    }
    wip_codes.discard("")
    roll_cols = _col_names(cur, "tbl_packing_roll")
    has_kode = "kode_packing" in roll_cols
    has_sizes = "sizes_text" in roll_cols
    kode_sel = "pr.kode_packing" if has_kode else "NULL AS kode_packing"
    sizes_sel = "pr.sizes_text" if has_sizes else "NULL AS sizes_text"
    if wip_codes:
        placeholders = ",".join(["%s"] * len(wip_codes))
        cur.execute(
            f"SELECT pr.id, pr.roll_no, pr.lembar, pr.ukuran, pr.remark, pr.created_at, "
            f"{kode_sel}, {sizes_sel}, "
            "p.id AS packing_id, p.kode_packing AS session_kode_packing, p.status AS packing_status "
            "FROM tbl_packing p "
            "JOIN tbl_packing_roll pr ON pr.packing_id = p.id "
            f"WHERE p.rencana_item_id = %s OR p.kode_wip IN ({placeholders}) "
            "ORDER BY pr.created_at DESC, pr.roll_no DESC",
            (rencana_item_id, *sorted(wip_codes)),
        )
    else:
        cur.execute(
            f"SELECT pr.id, pr.roll_no, pr.lembar, pr.ukuran, pr.remark, pr.created_at, "
            f"{kode_sel}, {sizes_sel}, "
            "p.id AS packing_id, p.kode_packing AS session_kode_packing, p.status AS packing_status "
            "FROM tbl_packing p "
            "JOIN tbl_packing_roll pr ON pr.packing_id = p.id "
            "WHERE p.rencana_item_id = %s "
            "ORDER BY pr.created_at DESC, pr.roll_no DESC",
            (rencana_item_id,),
        )
    rows = _rows(cur.fetchall())
    for row in rows:
        row["kode_packing"] = (row.get("kode_packing") or "").strip()
        row["sizes"] = _parse_sizes_text(row.get("sizes_text"))
    cur.close()
    conn.close()
    return jsonify(rows)


@api.get("/packing/roll/<int:roll_id>/label")
def packing_roll_label_reprint(roll_id: int):
    """Payload label roll untuk cetak ulang."""
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_packing_roll WHERE id = %s", (roll_id,))
    roll = cur.fetchone()
    if not roll:
        cur.close()
        conn.close()
        return _err("Roll tidak ditemukan", 404)
    cur.execute("SELECT * FROM tbl_packing WHERE id = %s", (roll.get("packing_id"),))
    packing = cur.fetchone()
    if not packing:
        cur.close()
        conn.close()
        return _err("Packing tidak ditemukan", 404)
    roll_kode = (roll.get("kode_packing") or "").strip()
    if roll_kode:
        packing = dict(packing)
        packing["kode_packing"] = roll_kode
    sizes = _parse_sizes_text(roll.get("sizes_text"))
    spec = _packing_spec_for_wip(
        cur,
        packing.get("kode_wip") or "",
        packing.get("no_po"),
        packing.get("rencana_item_id"),
    )
    label = _packing_roll_label_payload(_row(packing), _row(roll), spec, sizes)
    cur.close()
    conn.close()
    return jsonify({"ok": True, "label": label, "reprint": True})


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
        "SELECT i.id AS item_id, po.id AS po_id, po.no_po, po.no_so, po.item_name, po.customer, "
        "p.qty_proses AS qty_sq "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_item_po p ON p.item_id = i.id "
        "JOIN tbl_master_po po ON po.id = p.po_id "
        "WHERE i.kode_lot_wip = %s",
        (kode_wip,),
    )
    po_list = _rows(cur.fetchall())
    # Ringkasan persiapan terbaru untuk UI scan.
    prep = wip_data[0] if wip_data else {}
    for row in wip_data:
        if (row.get("status") or "") == "completed":
            prep = row
            break
    cur.close()
    conn.close()
    return jsonify(
        {
            "kode_wip": kode_wip,
            "wip_data": wip_data,
            "po_list": po_list,
            "prep": {
                "kode_proses": prep.get("kode_proses"),
                "status": prep.get("status"),
                "warna": prep.get("warna"),
                "tebal": prep.get("tebal"),
                "emboss": prep.get("emboss"),
                "treatment_jenis": prep.get("treatment_jenis"),
                "treatment_list": prep.get("treatment_list"),
                "total_size": prep.get("total_size"),
                "no_po": prep.get("no_po"),
            },
        }
    )


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
    status = (request.args.get("status") or "").strip()
    if status in ("in_progress", "finished"):
        cur.execute(
            "SELECT * FROM tbl_packing WHERE status=%s ORDER BY date_created DESC LIMIT %s",
            (status, limit),
        )
    else:
        cur.execute(
            "SELECT * FROM tbl_packing ORDER BY date_created DESC LIMIT %s", (limit,)
        )
    data = _rows(cur.fetchall())
    for row in data:
        spec = _packing_spec_for_wip(
            cur,
            row.get("kode_wip") or "",
            row.get("no_po"),
            row.get("rencana_item_id"),
        )
        no_so = (spec.get("no_so") or "").strip()
        if not no_so:
            cur.execute(
                "SELECT no_so FROM tbl_packing_po WHERE packing_id = %s "
                "AND no_so IS NOT NULL AND no_so <> '' ORDER BY id LIMIT 1",
                (row.get("id"),),
            )
            po_row = cur.fetchone() or {}
            no_so = (po_row.get("no_so") or "").strip()
        row["no_so"] = no_so
        row["lot_no"] = (
            spec.get("lot_no")
            or row.get("kode_wip")
            or ""
        )
    cur.close()
    conn.close()
    return jsonify(data)


@api.post("/packing")
def packing_start():
    from app import ensure_extended_tables, generate_code

    body = request.get_json(silent=True) or {}
    rencana_item_id = body.get("rencana_item_id")
    kode_wip = (body.get("kode_wip") or "").strip()
    no_po = (body.get("no_po") or "").strip()
    no_so = (body.get("no_so") or "").strip()
    customer = (body.get("customer") or "").strip()
    qty_sq = body.get("qty_sq") or 0
    po_id = body.get("po_id")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    item_id_val = None
    if rencana_item_id is not None:
        try:
            item_id_val = int(rencana_item_id)
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("rencana_item_id tidak valid")
        cur.execute(
            "SELECT i.*, r.nama_rencana FROM tbl_rencana_item i "
            "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
            "WHERE i.id = %s",
            (item_id_val,),
        )
        item = cur.fetchone()
        if not item:
            cur.close()
            conn.close()
            return _err("Item RPI tidak ditemukan", 404)
        kode_wip = (item.get("kode_lot_wip") or "").strip()
        cur.execute(
            "SELECT po.id AS po_id, po.no_po, po.no_so, po.customer, p.qty_proses AS qty_sq "
            "FROM tbl_rencana_item_po p "
            "JOIN tbl_master_po po ON po.id = p.po_id "
            "WHERE p.item_id = %s ORDER BY p.id LIMIT 1",
            (item_id_val,),
        )
        po_row = cur.fetchone()
        if po_row:
            no_po = po_row.get("no_po") or no_po
            no_so = po_row.get("no_so") or no_so
            customer = po_row.get("customer") or customer
            qty_sq = po_row.get("qty_sq") or qty_sq
            po_id = po_row.get("po_id") or po_id
        cur.execute(
            "SELECT pk.kode_wip, pk.status FROM tbl_persiapan_kulit pk "
            "WHERE pk.rencana_item_id = %s "
            "AND pk.status IN ('started', 'saved', 'completed') "
            "ORDER BY FIELD(pk.status, 'completed', 'saved', 'started'), pk.id DESC "
            "LIMIT 1",
            (item_id_val,),
        )
        prep_row = cur.fetchone()
        if prep_row:
            kode_wip = (prep_row.get("kode_wip") or kode_wip).strip()

    if not kode_wip or not no_po:
        cur.close()
        conn.close()
        return _err("kode_wip dan no_po wajib")
    cur.execute(
        "SELECT id FROM tbl_persiapan_kulit "
        "WHERE kode_wip = %s AND status IN ('started', 'saved', 'completed') LIMIT 1",
        (kode_wip,),
    )
    if not cur.fetchone():
        cur.execute(
            "SELECT pk.id FROM tbl_persiapan_kulit pk "
            "JOIN tbl_rencana_item ri ON ri.id = pk.rencana_item_id "
            "WHERE ri.kode_lot_wip = %s AND pk.status IN ('started', 'saved', 'completed') "
            "LIMIT 1",
            (kode_wip,),
        )
        if not cur.fetchone():
            cur.close()
            conn.close()
            return _err("WIP tidak valid / persiapan belum dimulai", 404)

    # Hindari dobel packing in_progress untuk WIP+PO yang sama.
    cur.execute(
        "SELECT id, kode_packing FROM tbl_packing "
        "WHERE kode_wip=%s AND no_po=%s AND status='in_progress' "
        "ORDER BY id DESC LIMIT 1",
        (kode_wip, no_po),
    )
    existing = cur.fetchone()
    if existing:
        cur.execute(
            "SELECT COALESCE(MAX(roll_no), 0) + 1 AS nxt FROM tbl_packing_roll WHERE packing_id=%s",
            (existing["id"],),
        )
        next_roll = int((cur.fetchone() or {}).get("nxt") or 1)
        cur.close()
        conn.close()
        return jsonify(
            {
                "id": existing["id"],
                "kode_packing": existing["kode_packing"],
                "ok": True,
                "reused": True,
                "next_roll_no": next_roll,
                "message": "Packing in_progress sudah ada — dibuka ulang",
            }
        ), 200

    kode_packing = _alloc_unique_fg_code(cur)
    from app import _col_names

    packing_cols = _col_names(cur, "tbl_packing")
    if item_id_val is not None and "rencana_item_id" in packing_cols:
        cur.execute(
            "INSERT INTO tbl_packing "
            "(kode_packing, kode_wip, no_po, customer, status, rencana_item_id) "
            "VALUES (%s,%s,%s,%s,'in_progress',%s)",
            (kode_packing, kode_wip, no_po, customer, item_id_val),
        )
    else:
        cur.execute(
            "INSERT INTO tbl_packing (kode_packing, kode_wip, no_po, customer, status) "
            "VALUES (%s,%s,%s,%s,'in_progress')",
            (kode_packing, kode_wip, no_po, customer),
        )
    packing_id = cur.lastrowid
    po_id = body.get("po_id")
    try:
        po_id = int(po_id) if po_id is not None else None
    except (TypeError, ValueError):
        po_id = None
    if po_id is None and no_po:
        cur.execute(
            "SELECT id FROM tbl_master_po WHERE no_po=%s ORDER BY id DESC LIMIT 1",
            (no_po,),
        )
        row_po = cur.fetchone()
        if row_po:
            po_id = row_po["id"]
    cur.execute(
        "INSERT INTO tbl_packing_po (packing_id, po_id, no_po, no_so, qty_sq) "
        "VALUES (%s,%s,%s,%s,%s)",
        (packing_id, po_id, no_po, no_so, qty_sq),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(
        {
            "id": packing_id,
            "kode_packing": kode_packing,
            "kode_wip": kode_wip,
            "no_so": no_so,
            "next_roll_no": 1,
            "ok": True,
        }
    ), 201


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
    cur.execute(
        "SELECT pp.*, "
        "COALESCE(mp1.source_detail_id, mp2.source_detail_id) AS source_detail_id, "
        "COALESCE(mp1.item_name, mp2.item_name) AS item_name, "
        "COALESCE(mp1.warna, mp2.warna) AS warna "
        "FROM tbl_packing_po pp "
        "LEFT JOIN tbl_master_po mp1 ON mp1.id = pp.po_id "
        "LEFT JOIN tbl_master_po mp2 ON pp.po_id IS NULL AND mp2.id = ("
        "  SELECT id FROM tbl_master_po WHERE no_po = pp.no_po "
        "  ORDER BY id DESC LIMIT 1"
        ") "
        "WHERE pp.packing_id = %s",
        (packing_id,),
    )
    packing_pos = _rows(cur.fetchall())
    cur.execute(
        "SELECT i.id AS item_id, po.id AS po_id, po.source_detail_id, po.no_po, po.no_so, "
        "po.item_name, po.customer, p.qty_proses AS qty_sq "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_item_po p ON p.item_id = i.id "
        "JOIN tbl_master_po po ON po.id = p.po_id "
        "WHERE i.kode_lot_wip = %s",
        (packing["kode_wip"],),
    )
    available_pos = _rows(cur.fetchall())
    print_payload = _packing_print_payload(cur, packing)
    cur.close()
    conn.close()
    return jsonify(
        {
            "packing": print_payload["packing"],
            "rolls": rolls,
            "packing_pos": packing_pos,
            "available_pos": available_pos,
            "spec": print_payload.get("spec"),
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
    payload = _packing_print_payload(cur, packing)
    cur.close()
    conn.close()
    return jsonify(payload)


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
    if action == "update_header":
        if packing["status"] == "finished":
            cur.close()
            conn.close()
            return _err("Packing sudah finished")
        softness = body.get("softness")
        if softness is not None:
            softness = str(softness).strip() or None
        gw = body.get("gross_weight")
        nw = body.get("net_weight")
        gross_weight = float(gw) if gw not in (None, "") else None
        net_weight = float(nw) if nw not in (None, "") else None
        cur.execute(
            "UPDATE tbl_packing SET softness=%s, gross_weight=%s, net_weight=%s WHERE id=%s",
            (softness, gross_weight, net_weight, packing_id),
        )
        msg = "Header packing diperbarui"

    elif action == "add_roll":
        if packing["status"] == "finished":
            cur.close()
            conn.close()
            return _err("Packing sudah finished")
        lembar = int(body.get("lembar") or 1)
        ukuran = float(body.get("ukuran") or 0)
        remark = (body.get("remark") or "").strip() or None
        if lembar <= 0:
            cur.close()
            conn.close()
            return _err("Lembar/pieces harus > 0")
        if ukuran <= 0:
            cur.close()
            conn.close()
            return _err("Quantity (ukuran) harus > 0")
        cur.execute(
            "SELECT COALESCE(MAX(roll_no),0)+1 AS nxt FROM tbl_packing_roll WHERE packing_id=%s",
            (packing_id,),
        )
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
        msg = f"Roll #{roll_no} ditambahkan"

    elif action == "print_roll_label":
        if packing["status"] == "finished":
            cur.close()
            conn.close()
            return _err("Packing sudah finished")
        sizes = body.get("sizes") or []
        if not sizes:
            cur.close()
            conn.close()
            return _err("Tidak ada hasil pengukuran")
        parsed_sizes = []
        for s in sizes:
            try:
                val = float(s)
            except (TypeError, ValueError):
                continue
            if val > 0:
                parsed_sizes.append(val)
        if not parsed_sizes:
            cur.close()
            conn.close()
            return _err("Size pengukuran tidak valid")
        lembar = len(parsed_sizes)
        ukuran = sum(parsed_sizes)
        cur.execute(
            "SELECT COALESCE(MAX(roll_no),0)+1 AS nxt FROM tbl_packing_roll WHERE packing_id=%s",
            (packing_id,),
        )
        roll_no = int(cur.fetchone()["nxt"])
        remark = (body.get("remark") or "").strip() or None
        sizes_text = "+".join(_format_label_size_part(v) for v in parsed_sizes)
        from app import _col_names

        roll_kode = (packing.get("kode_packing") or "").strip()
        if not roll_kode:
            roll_kode = _alloc_unique_fg_code(cur)
        next_kode = _alloc_unique_fg_code(cur)
        roll_cols = _col_names(cur, "tbl_packing_roll")
        if "kode_packing" in roll_cols and "sizes_text" in roll_cols:
            cur.execute(
                "INSERT INTO tbl_packing_roll "
                "(packing_id, roll_no, lembar, ukuran, remark, kode_packing, sizes_text) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (packing_id, roll_no, lembar, ukuran, remark, roll_kode, sizes_text),
            )
        else:
            cur.execute(
                "INSERT INTO tbl_packing_roll (packing_id, roll_no, lembar, ukuran, remark) "
                "VALUES (%s,%s,%s,%s,%s)",
                (packing_id, roll_no, lembar, ukuran, remark),
            )
        cur.execute(
            "UPDATE tbl_packing SET total_lembar=total_lembar+%s, total_ukuran=total_ukuran+%s "
            "WHERE id=%s",
            (lembar, ukuran, packing_id),
        )
        cur.execute(
            "UPDATE tbl_packing SET kode_packing=%s WHERE id=%s",
            (next_kode, packing_id),
        )
        conn.commit()
        cur.execute("SELECT * FROM tbl_packing WHERE id=%s", (packing_id,))
        pkg = cur.fetchone()
        cur.execute(
            "SELECT * FROM tbl_packing_roll WHERE packing_id=%s AND roll_no=%s",
            (packing_id, roll_no),
        )
        roll_row = cur.fetchone()
        spec = _packing_spec_for_wip(
            cur,
            pkg.get("kode_wip") or "",
            pkg.get("no_po"),
            pkg.get("rencana_item_id"),
        )
        pkg_label = dict(pkg)
        pkg_label["kode_packing"] = roll_kode
        label = _packing_roll_label_payload(_row(pkg_label), _row(roll_row), spec, parsed_sizes)
        next_roll = roll_no + 1
        cur.close()
        conn.close()
        return jsonify(
            {
                "ok": True,
                "message": f"Label roll #{roll_no} siap cetak",
                "roll_no": roll_no,
                "roll_kode_packing": roll_kode,
                "next_roll_no": next_roll,
                "kode_packing": next_kode,
                "label": label,
            }
        )

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
        po_id = body.get("po_id")
        try:
            po_id = int(po_id) if po_id is not None else None
        except (TypeError, ValueError):
            po_id = None
        if not no_po:
            cur.close()
            conn.close()
            return _err("no_po wajib")
        if po_id is None:
            cur.execute(
                "SELECT id FROM tbl_master_po WHERE no_po=%s ORDER BY id DESC LIMIT 1",
                (no_po,),
            )
            row_po = cur.fetchone()
            if row_po:
                po_id = row_po["id"]
        cur.execute(
            "INSERT INTO tbl_packing_po (packing_id, po_id, no_po, no_so, qty_sq) "
            "VALUES (%s,%s,%s,%s,%s)",
            (packing_id, po_id, no_po, no_so, qty_sq),
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
                "SELECT COUNT(*) AS n FROM tbl_packing_roll WHERE packing_id=%s",
                (packing_id,),
            )
            n_roll = int((cur.fetchone() or {}).get("n") or 0)
            if n_roll <= 0:
                cur.close()
                conn.close()
                return _err("Tambah minimal satu roll sebelum Finish → Gudang FG")
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

    status = (request.args.get("status") or "").strip().lower()
    q = (request.args.get("q") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    sql = "SELECT * FROM tbl_gudang_fg WHERE 1=1"
    params: list = []
    if status in ("in_stock", "out"):
        sql += " AND status=%s"
        params.append(status)
    if q:
        like = f"%{q}%"
        sql += (
            " AND (kode_packing LIKE %s OR kode_wip LIKE %s OR customer LIKE %s "
            "OR IFNULL(erp_delivery_number,'') LIKE %s)"
        )
        params.extend([like, like, like, like])
    sql += " ORDER BY date_in DESC LIMIT 200"
    cur.execute(sql, params)
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
    cur.execute(
        "SELECT pp.*, "
        "COALESCE(mp1.source_detail_id, mp2.source_detail_id) AS source_detail_id, "
        "COALESCE(mp1.item_name, mp2.item_name) AS item_name "
        "FROM tbl_packing_po pp "
        "LEFT JOIN tbl_master_po mp1 ON mp1.id = pp.po_id "
        "LEFT JOIN tbl_master_po mp2 ON pp.po_id IS NULL AND mp2.id = ("
        "  SELECT id FROM tbl_master_po WHERE no_po = pp.no_po "
        "  ORDER BY id DESC LIMIT 1"
        ") "
        "WHERE pp.packing_id=%s",
        (fg["packing_id"],),
    )
    packing_pos = _rows(cur.fetchall())
    bridge_lines = []
    if packing:
        cur.execute(
            "SELECT po.source_detail_id, po.no_po, po.no_so, po.item_name, "
            "p.qty_proses AS qty_sq "
            "FROM tbl_rencana_item i "
            "JOIN tbl_rencana_item_po p ON p.item_id = i.id "
            "JOIN tbl_master_po po ON po.id = p.po_id "
            "WHERE i.kode_lot_wip = %s AND po.source_detail_id IS NOT NULL",
            (packing.get("kode_wip"),),
        )
        bridge_lines = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(
        {
            "fg": _row(fg),
            "packing": _row(packing),
            "rolls": rolls,
            "packing_pos": packing_pos,
            "bridge_lines": bridge_lines,
        }
    )


@api.post("/gudang-fg/out")
def gudang_fg_out():
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    kode_packing = (body.get("kode_packing") or "").strip()
    keterangan = (body.get("keterangan") or "").strip()
    if not kode_packing:
        return _err("kode_packing wajib")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT * FROM tbl_gudang_fg WHERE TRIM(kode_packing)=%s AND status='in_stock'",
        (kode_packing,),
    )
    fg = cur.fetchone()
    if not fg:
        cur.execute(
            "SELECT id, status FROM tbl_gudang_fg WHERE TRIM(kode_packing)=%s ORDER BY id DESC LIMIT 1",
            (kode_packing,),
        )
        existing = cur.fetchone()
        cur.close()
        conn.close()
        if existing and existing.get("status") == "out":
            return _err("Kode Packing List sudah OUT", 400)
        return _err("Kode Packing List tidak ditemukan di stok FG", 404)
    cur.execute(
        "UPDATE tbl_gudang_fg SET status='out', date_out=NOW(), keterangan_out=%s, "
        "bridge_status=NULL, bridge_error=NULL WHERE id=%s",
        (keterangan, fg["id"]),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "id": fg["id"], "kode_packing": kode_packing})


@api.post("/gudang-fg/<int:fg_id>/rollback-out")
def gudang_fg_rollback_out(fg_id: int):
    """Kembalikan FG ke in_stock jika bridge ERP gagal."""
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    reason = (body.get("reason") or "bridge failed")[:255]
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
    if fg.get("status") != "out":
        cur.close()
        conn.close()
        return jsonify({"ok": True, "id": fg_id, "status": fg.get("status"), "noop": True})
    cur.execute(
        "UPDATE tbl_gudang_fg SET status='in_stock', date_out=NULL, keterangan_out=NULL, "
        "erp_delivery_id=NULL, erp_delivery_number=NULL, "
        "bridge_status='failed', bridge_error=%s WHERE id=%s",
        (reason, fg_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "id": fg_id, "status": "in_stock"})


@api.post("/gudang-fg/<int:fg_id>/bridge-result")
def gudang_fg_bridge_result(fg_id: int):
    """Simpan hasil bridge Delivery ERP pada baris Gudang FG."""
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    delivery_id = body.get("delivery_id")
    delivery_number = (body.get("delivery_number") or "").strip() or None
    bridge_status = (body.get("bridge_status") or "ok").strip() or "ok"
    bridge_error = (body.get("bridge_error") or "").strip() or None
    try:
        delivery_id = int(delivery_id) if delivery_id is not None else None
    except (TypeError, ValueError):
        delivery_id = None

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT id FROM tbl_gudang_fg WHERE id=%s", (fg_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return _err("Data tidak ditemukan", 404)
    cur.execute(
        "UPDATE tbl_gudang_fg SET erp_delivery_id=%s, erp_delivery_number=%s, "
        "bridge_status=%s, bridge_error=%s WHERE id=%s",
        (delivery_id, delivery_number, bridge_status, bridge_error, fg_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(
        {
            "ok": True,
            "id": fg_id,
            "erp_delivery_id": delivery_id,
            "erp_delivery_number": delivery_number,
            "bridge_status": bridge_status,
        }
    )


# ---- P4: stok kimia / stok RP ----
@api.get("/stok-kimia")
def stok_kimia_list():
    from app import ensure_extended_tables

    include_empty = (request.args.get("all") or "").strip().lower() in ("1", "true", "yes")
    q = (request.args.get("q") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    sql_in = (
        "SELECT si.*, "
        "COALESCE(si.nama_material, '') AS nama_barang, "
        "COALESCE(si.kode_material, '') AS kode_barang, "
        "COALESCE(si.satuan, 'kg') AS satuan "
        "FROM tbl_stok_kimia_in si WHERE 1=1"
    )
    params_in: list = []
    if not include_empty:
        sql_in += " AND si.qty_sisa > 0"
    if q:
        like = f"%{q}%"
        sql_in += (
            " AND (si.kode_internal LIKE %s OR IFNULL(si.kode_material,'') LIKE %s "
            "OR IFNULL(si.nama_material,'') LIKE %s OR IFNULL(si.gudang,'') LIKE %s)"
        )
        params_in.extend([like, like, like, like])
    sql_in += " ORDER BY si.tanggal_in DESC, si.id DESC LIMIT 200"
    cur.execute(sql_in, params_in)
    stok_in = _rows(cur.fetchall())

    sql_out = (
        "SELECT so.*, COALESCE(so.nama_material, si.nama_material, '') AS nama_barang, "
        "COALESCE(so.kode_material, si.kode_material, '') AS kode_barang "
        "FROM tbl_stok_kimia_out so "
        "LEFT JOIN tbl_stok_kimia_in si ON si.id = so.stok_in_id WHERE 1=1"
    )
    params_out: list = []
    if q:
        like = f"%{q}%"
        sql_out += (
            " AND (IFNULL(so.nama_material,'') LIKE %s OR IFNULL(si.nama_material,'') LIKE %s "
            "OR IFNULL(so.kode_wip,'') LIKE %s OR IFNULL(so.tujuan,'') LIKE %s)"
        )
        params_out.extend([like, like, like, like])
    sql_out += " ORDER BY so.created_at DESC LIMIT 100"
    cur.execute(sql_out, params_out)
    stok_out = _rows(cur.fetchall())

    from erp_raw_materials import list_materials
    kimia_list = [
        {
            "id": r["id"],
            "kode_barang": r["code"],
            "nama_barang": r["name"],
            "satuan": r.get("unit") or "kg",
            "erp_material_id": r["id"],
        }
        for r in list_materials("kimia")
    ]
    cur.close()
    conn.close()
    return jsonify(
        {
            "stok_in": stok_in,
            "stok_out": stok_out,
            "kimia_list": kimia_list,
            "stats": {
                "lots": len(stok_in),
                "qty_sisa": round(sum(float(r.get("qty_sisa") or 0) for r in stok_in), 3),
                "out_rows": len(stok_out),
            },
        }
    )


@api.post("/stok-kimia")
def stok_kimia_action():
    from app import ensure_extended_tables, generate_code
    from datetime import timedelta

    body = request.get_json(silent=True) or {}
    action = (body.get("action") or "").strip().lower()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if action == "in":
        kimia_id = body.get("kimia_id")
        try:
            kimia_id = int(kimia_id) if kimia_id is not None else None
        except (TypeError, ValueError):
            kimia_id = None
        try:
            qty = float(body.get("qty") or 0)
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("qty harus angka")
        if not kimia_id:
            cur.close()
            conn.close()
            return _err("kimia_id wajib")
        if qty <= 0:
            cur.close()
            conn.close()
            return _err("qty harus > 0")
        try:
            jumlah_kemasan = int(body.get("jumlah_kemasan") or 0) or None
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("jumlah_kemasan harus angka")
        if jumlah_kemasan is not None and jumlah_kemasan < 0:
            cur.close()
            conn.close()
            return _err("jumlah_kemasan tidak boleh negatif")
        tanggal = body.get("tanggal") or date.today().isoformat()
        from erp_raw_materials import resolve_material

        mat = resolve_material(
            erp_material_id=kimia_id,
            code=(body.get("kode_kimia") or body.get("kode_barang") or None),
            material_type="kimia",
        )
        if not mat:
            cur.close()
            conn.close()
            return _err("Material kimia tidak ditemukan di ERP raw_materials", 404)
        erp_id = int(mat["id"])
        kode_internal = generate_code("BC-K")
        days = 365
        expired = date.today() + timedelta(days=days)
        satuan = (body.get("satuan") or mat.get("unit") or "kg")[:20]
        cur.execute(
            "INSERT INTO tbl_stok_kimia_in "
            "(kode_internal, kimia_id, erp_material_id, kode_material, nama_material, "
            "qty, qty_sisa, satuan, jumlah_kemasan, tanggal_in, expired_date, gudang) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'kimia')",
            (
                kode_internal,
                erp_id,
                erp_id,
                mat.get("code"),
                mat.get("name"),
                qty,
                qty,
                satuan,
                jumlah_kemasan,
                tanggal,
                expired,
            ),
        )
        new_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(
            {
                "ok": True,
                "id": new_id,
                "kode_internal": kode_internal,
                "qty": qty,
                "expired_date": expired.isoformat(),
                "erp_material_id": erp_id,
            }
        ), 201

    if action == "out":
        stok_in_id = body.get("stok_in_id")
        try:
            stok_in_id = int(stok_in_id) if stok_in_id is not None else None
        except (TypeError, ValueError):
            stok_in_id = None
        try:
            qty = float(body.get("qty") or 0)
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("qty harus angka")
        if not stok_in_id:
            cur.close()
            conn.close()
            return _err("stok_in_id wajib")
        if qty <= 0:
            cur.close()
            conn.close()
            return _err("qty harus > 0")
        try:
            jumlah_kemasan = int(body.get("jumlah_kemasan") or 0) or None
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("jumlah_kemasan harus angka")
        tujuan = (body.get("tujuan") or "mixing").strip().lower()
        if tujuan not in ("mixing", "produksi", "return"):
            cur.close()
            conn.close()
            return _err("tujuan harus mixing|produksi|return")
        kode_wip = (body.get("kode_wip") or "").strip() or None
        keterangan = (body.get("keterangan") or "").strip() or None
        tanggal = body.get("tanggal") or date.today().isoformat()
        cur.execute("SELECT * FROM tbl_stok_kimia_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok:
            cur.close()
            conn.close()
            return _err("Lot stok tidak ditemukan", 404)
        erp_id = stok.get("erp_material_id")
        if not erp_id:
            from bridge_metrics import incr

            incr("out_rejected_missing_erp_id")
            cur.close()
            conn.close()
            return _err("Lot belum ter-map erp_material_id — backfill / pilih material ERP")
        sisa = float(stok["qty_sisa"] or 0)
        if sisa <= 0:
            cur.close()
            conn.close()
            return _err("Lot sudah habis")
        if qty > sisa:
            cur.close()
            conn.close()
            return _err(f"Qty OUT ({qty}) melebihi sisa ({sisa})")
        cur.execute(
            "INSERT INTO tbl_stok_kimia_out "
            "(stok_in_id, kimia_id, erp_material_id, kode_material, nama_material, "
            "qty, jumlah_kemasan, tujuan, kode_wip, tanggal, keterangan) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                stok_in_id,
                stok.get("kimia_id") or erp_id,
                erp_id,
                stok.get("kode_material"),
                stok.get("nama_material"),
                qty,
                jumlah_kemasan,
                tujuan,
                kode_wip,
                tanggal,
                keterangan,
            ),
        )
        new_sisa = sisa - qty
        new_gudang = "mixing" if tujuan == "mixing" else (stok.get("gudang") or "kimia")
        cur.execute(
            "UPDATE tbl_stok_kimia_in SET qty_sisa=%s, gudang=%s WHERE id=%s",
            (new_sisa, new_gudang, stok_in_id),
        )
        out_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(
            {
                "ok": True,
                "out_id": out_id,
                "qty_sisa": new_sisa,
                "bridge": {
                    "material_type": "kimia",
                    "erp_material_id": erp_id,
                    "material_code": stok.get("kode_material"),
                    "material_name": stok.get("nama_material"),
                    "unit": stok.get("satuan") or "kg",
                    "qty": qty,
                    "mrp_ref": f"stok-kimia-out:{out_id}",
                },
            }
        )

    cur.close()
    conn.close()
    return _err("action harus in atau out")


@api.get("/stok-rp")
def stok_rp_list():
    from app import ensure_extended_tables

    include_empty = (request.args.get("all") or "").strip().lower() in ("1", "true", "yes")
    q = (request.args.get("q") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    sql_in = (
        "SELECT si.*, COALESCE(si.nama_material, '') AS nama_jenis, "
        "COALESCE(si.kode_material, '') AS kode_rp, 'meter' AS satuan "
        "FROM tbl_stok_rp_in si WHERE 1=1"
    )
    params_in: list = []
    if not include_empty:
        sql_in += " AND si.qty_sisa > 0"
    if q:
        like = f"%{q}%"
        sql_in += (
            " AND (si.kode_internal LIKE %s OR IFNULL(si.kode_material,'') LIKE %s "
            "OR IFNULL(si.nama_material,'') LIKE %s)"
        )
        params_in.extend([like, like, like])
    sql_in += " ORDER BY si.tanggal_in DESC, si.id DESC LIMIT 200"
    cur.execute(sql_in, params_in)
    stok_in = _rows(cur.fetchall())

    sql_out = (
        "SELECT so.*, COALESCE(so.nama_material, si.nama_material, '') AS nama_jenis, "
        "COALESCE(so.kode_material, si.kode_material, '') AS kode_rp "
        "FROM tbl_stok_rp_out so "
        "LEFT JOIN tbl_stok_rp_in si ON si.id = so.stok_in_id WHERE 1=1"
    )
    params_out: list = []
    if q:
        like = f"%{q}%"
        sql_out += (
            " AND (IFNULL(so.nama_material,'') LIKE %s OR IFNULL(si.nama_material,'') LIKE %s "
            "OR IFNULL(so.kode_wip,'') LIKE %s OR IFNULL(so.kode_material,'') LIKE %s)"
        )
        params_out.extend([like, like, like, like])
    sql_out += " ORDER BY so.created_at DESC LIMIT 100"
    cur.execute(sql_out, params_out)
    stok_out = _rows(cur.fetchall())

    from erp_raw_materials import list_materials

    rp_list = [
        {
            "id": r["id"],
            "kode_rp": r["code"],
            "nama_rp": r["name"],
            "satuan": r.get("unit") or "meter",
            "erp_material_id": r["id"],
        }
        for r in list_materials("rp")
    ]
    cur.close()
    conn.close()
    return jsonify(
        {
            "stok_in": stok_in,
            "stok_out": stok_out,
            "rp_list": rp_list,
            "stats": {
                "lots": len(stok_in),
                "qty_sisa": round(sum(float(r.get("qty_sisa") or 0) for r in stok_in), 3),
                "out_rows": len(stok_out),
            },
        }
    )


@api.post("/stok-rp")
def stok_rp_action():
    from app import ensure_extended_tables, generate_code

    body = request.get_json(silent=True) or {}
    action = (body.get("action") or "").strip().lower()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if action == "in":
        rp_id = body.get("rp_id")
        try:
            rp_id = int(rp_id) if rp_id is not None else None
        except (TypeError, ValueError):
            rp_id = None
        try:
            meter_roll = float(body.get("meter_roll") or body.get("qty") or 0)
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("meter_roll harus angka")
        if not rp_id:
            cur.close()
            conn.close()
            return _err("rp_id wajib")
        if meter_roll <= 0:
            cur.close()
            conn.close()
            return _err("meter_roll harus > 0")
        tanggal = body.get("tanggal") or date.today().isoformat()
        from erp_raw_materials import resolve_material

        mat = resolve_material(erp_material_id=rp_id, material_type="rp")
        if not mat:
            cur.close()
            conn.close()
            return _err("Material RP tidak ditemukan di ERP raw_materials", 404)
        erp_id = int(mat["id"])
        kode_internal = generate_code("BC-R")
        cur.execute(
            "INSERT INTO tbl_stok_rp_in "
            "(kode_internal, rp_id, erp_material_id, kode_material, nama_material, "
            "meter_roll, qty_sisa, tanggal_in) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                kode_internal,
                erp_id,
                erp_id,
                mat.get("code"),
                mat.get("name"),
                meter_roll,
                meter_roll,
                tanggal,
            ),
        )
        new_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(
            {
                "ok": True,
                "id": new_id,
                "kode_internal": kode_internal,
                "meter_roll": meter_roll,
                "erp_material_id": erp_id,
            }
        ), 201

    if action == "out":
        stok_in_id = body.get("stok_in_id")
        try:
            stok_in_id = int(stok_in_id) if stok_in_id is not None else None
        except (TypeError, ValueError):
            stok_in_id = None
        try:
            meter_roll = float(body.get("meter_roll") or body.get("qty") or 0)
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("meter_roll harus angka")
        if not stok_in_id:
            cur.close()
            conn.close()
            return _err("stok_in_id wajib")
        if meter_roll <= 0:
            cur.close()
            conn.close()
            return _err("meter_roll harus > 0")
        kode_wip = (body.get("kode_wip") or "").strip() or None
        keterangan = (body.get("keterangan") or "").strip() or None
        tanggal = body.get("tanggal") or date.today().isoformat()
        cur.execute("SELECT * FROM tbl_stok_rp_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok:
            cur.close()
            conn.close()
            return _err("Lot stok RP tidak ditemukan", 404)
        erp_id = stok.get("erp_material_id")
        if not erp_id:
            from bridge_metrics import incr

            incr("out_rejected_missing_erp_id")
            cur.close()
            conn.close()
            return _err("Lot RP belum ter-map erp_material_id")
        sisa = float(stok["qty_sisa"] or 0)
        if sisa <= 0:
            cur.close()
            conn.close()
            return _err("Lot RP sudah habis")
        if meter_roll > sisa:
            cur.close()
            conn.close()
            return _err(f"Meter OUT ({meter_roll}) melebihi sisa ({sisa})")
        cur.execute(
            "INSERT INTO tbl_stok_rp_out "
            "(stok_in_id, rp_id, erp_material_id, kode_material, nama_material, "
            "meter_roll, kode_wip, tanggal, keterangan) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                stok_in_id,
                stok.get("rp_id") or erp_id,
                erp_id,
                stok.get("kode_material"),
                stok.get("nama_material"),
                meter_roll,
                kode_wip,
                tanggal,
                keterangan,
            ),
        )
        new_sisa = sisa - meter_roll
        cur.execute(
            "UPDATE tbl_stok_rp_in SET qty_sisa=%s WHERE id=%s",
            (new_sisa, stok_in_id),
        )
        out_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(
            {
                "ok": True,
                "out_id": out_id,
                "qty_sisa": new_sisa,
                "bridge": {
                    "material_type": "rp",
                    "erp_material_id": erp_id,
                    "material_code": stok.get("kode_material"),
                    "material_name": stok.get("nama_material"),
                    "unit": "meter",
                    "qty": meter_roll,
                    "mrp_ref": f"stok-rp-out:{out_id}",
                },
            }
        )

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
    try:
        qty_digunakan = float(body.get("qty_digunakan") or 0)
    except (TypeError, ValueError):
        return _err("qty_digunakan harus angka")
    stok_in_id = body.get("stok_in_id")
    try:
        stok_in_id = int(stok_in_id) if stok_in_id not in (None, "") else None
    except (TypeError, ValueError):
        stok_in_id = None
    if not kode_wip or not kode_lot_warna:
        return _err("kode_wip dan kode_lot_warna wajib")
    if qty_digunakan <= 0:
        return _err("qty_digunakan harus > 0")
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
    bridge = None
    if stok_in_id:
        cur.execute("SELECT * FROM tbl_stok_kimia_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok:
            cur.close()
            conn.close()
            return _err("Lot stok kimia tidak ditemukan", 404)
        sisa = float(stok["qty_sisa"] or 0)
        if qty_digunakan > sisa:
            cur.close()
            conn.close()
            return _err(f"Stok kimia tidak cukup (sisa {sisa})", 400)
        cur.execute(
            "INSERT INTO tbl_stok_kimia_out (stok_in_id, kimia_id, qty, jumlah_kemasan, tujuan, kode_wip, tanggal) "
            "VALUES (%s,%s,%s,NULL,'produksi',%s,%s)",
            (stok_in_id, stok["kimia_id"], qty_digunakan, kode_wip, date.today().isoformat()),
        )
        cur.execute(
            "UPDATE tbl_stok_kimia_in SET qty_sisa=%s WHERE id=%s",
            (sisa - qty_digunakan, stok_in_id),
        )
        bridge = {
            "material_type": "kimia",
            "erp_material_id": stok.get("erp_material_id"),
            "material_code": stok.get("kode_material"),
            "material_name": stok.get("nama_material"),
            "unit": stok.get("satuan") or "kg",
            "qty": qty_digunakan,
            "mrp_ref": f"usage-color:{kode_lot_warna}",
        }
        if not bridge["erp_material_id"]:
            from bridge_metrics import incr

            incr("out_rejected_missing_erp_id")
            cur.close()
            conn.close()
            return _err("Lot kimia belum ter-map erp_material_id")
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
    return jsonify(
        {"ok": True, "id": new_id, "stok_deducted": bool(stok_in_id), "bridge": bridge}
    ), 201



@api.get("/usage-rp/scan-rp")
def usage_rp_scan():
    from erp_raw_materials import fetch_material_by_code

    kode = (request.args.get("q") or "").strip()
    if not kode:
        return _err("Kode kosong")
    mat = fetch_material_by_code(kode, material_type="rp")
    if not mat:
        return _err("Jenis RP tidak ditemukan di ERP", 404)
    return jsonify(
        {
            "kode_rp": mat["code"],
            "nama_jenis": mat["name"],
            "satuan": mat.get("unit") or "meter",
            "erp_material_id": mat["id"],
        }
    )


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
    from erp_raw_materials import fetch_material_by_code

    body = request.get_json(silent=True) or {}
    kode_wip = (body.get("kode_wip") or "").strip()
    jenis_scan = (body.get("jenis_rp") or body.get("kode_rp") or "").strip()
    try:
        qty_used = float(body.get("qty_used") or 0)
    except (TypeError, ValueError):
        return _err("qty_used harus angka")
    stok_in_id = body.get("stok_in_id")
    try:
        stok_in_id = int(stok_in_id) if stok_in_id not in (None, "") else None
    except (TypeError, ValueError):
        stok_in_id = None
    if not kode_wip or not jenis_scan:
        return _err("kode_wip dan jenis_rp wajib")
    if qty_used <= 0:
        return _err("qty_used harus > 0")
    mat = fetch_material_by_code(jenis_scan, material_type="rp")
    if not mat:
        return _err("Jenis RP tidak ditemukan di ERP", 404)
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    bridge = None
    if stok_in_id:
        cur.execute("SELECT * FROM tbl_stok_rp_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok:
            cur.close()
            conn.close()
            return _err("Lot stok RP tidak ditemukan", 404)
        if not stok.get("erp_material_id"):
            from bridge_metrics import incr

            incr("out_rejected_missing_erp_id")
            cur.close()
            conn.close()
            return _err("Lot RP belum ter-map erp_material_id")
        sisa = float(stok["qty_sisa"] or 0)
        if qty_used > sisa:
            cur.close()
            conn.close()
            return _err(f"Stok RP tidak cukup (sisa {sisa})", 400)
        cur.execute(
            "INSERT INTO tbl_stok_rp_out "
            "(stok_in_id, rp_id, erp_material_id, kode_material, nama_material, "
            "meter_roll, kode_wip, tanggal) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                stok_in_id,
                stok.get("rp_id"),
                stok.get("erp_material_id"),
                stok.get("kode_material"),
                stok.get("nama_material"),
                qty_used,
                kode_wip,
                date.today().isoformat(),
            ),
        )
        cur.execute(
            "UPDATE tbl_stok_rp_in SET qty_sisa = %s WHERE id=%s",
            (sisa - qty_used, stok_in_id),
        )
        bridge = {
            "material_type": "rp",
            "erp_material_id": stok.get("erp_material_id"),
            "material_code": stok.get("kode_material"),
            "material_name": stok.get("nama_material"),
            "unit": mat.get("unit") or "meter",
            "qty": qty_used,
            "mrp_ref": f"usage-rp:{jenis_scan}",
        }
    cur.execute(
        "INSERT INTO tbl_usage_rp (kode_wip, jenis_rp, qty_used, satuan) VALUES (%s,%s,%s,%s)",
        (
            kode_wip,
            mat.get("name") or jenis_scan,
            qty_used,
            body.get("satuan") or mat.get("unit") or "meter",
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(
        {"ok": True, "id": new_id, "stok_deducted": bool(stok_in_id), "bridge": bridge}
    ), 201


# ---- P5: material lain ----
@api.get("/masters/material-lain")
def master_material_lain_list():
    from erp_raw_materials import list_materials

    rows = list_materials("material_lain")
    out = [
        {
            "id": r["id"],
            "erp_material_id": r["id"],
            "kode_material": r["code"],
            "nama_material": r["name"],
            "satuan": r.get("unit") or "pcs",
            "source": "raw_materials",
        }
        for r in rows
    ]
    return jsonify(out)


@api.post("/masters/material-lain")
def master_material_lain_create():
    return _err(
        "Katalog material hanya di ERP Inventory (raw_materials). Tidak bisa create dari MRP.",
        403,
    )


@api.delete("/masters/material-lain/<int:material_id>")
def master_material_lain_delete(material_id: int):
    return _err("Hapus material hanya lewat ERP Inventory.", 403)


@api.get("/stok-material-lain")
def stok_material_lain_list():
    from app import ensure_extended_tables

    include_empty = (request.args.get("all") or "").strip().lower() in ("1", "true", "yes")
    q = (request.args.get("q") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    sql_in = (
        "SELECT si.*, COALESCE(si.kode_material,'') AS kode_material, "
        "COALESCE(si.nama_material,'') AS nama_material, "
        "COALESCE(si.satuan, 'pcs') AS satuan "
        "FROM tbl_stok_material_lain_in si WHERE 1=1"
    )
    params_in: list = []
    if not include_empty:
        sql_in += " AND si.qty_sisa > 0"
    if q:
        like = f"%{q}%"
        sql_in += (
            " AND (si.kode_internal LIKE %s OR IFNULL(si.kode_material,'') LIKE %s "
            "OR IFNULL(si.nama_material,'') LIKE %s)"
        )
        params_in.extend([like, like, like])
    sql_in += " ORDER BY si.tanggal_in DESC, si.id DESC LIMIT 200"
    cur.execute(sql_in, params_in)
    stok_in = _rows(cur.fetchall())

    sql_out = (
        "SELECT so.*, COALESCE(so.nama_material, si.nama_material,'') AS nama_material, "
        "COALESCE(so.kode_material, si.kode_material,'') AS kode_material "
        "FROM tbl_stok_material_lain_out so "
        "LEFT JOIN tbl_stok_material_lain_in si ON si.id = so.stok_in_id WHERE 1=1"
    )
    params_out: list = []
    if q:
        like = f"%{q}%"
        sql_out += (
            " AND (IFNULL(so.nama_material,'') LIKE %s OR IFNULL(so.kode_material,'') LIKE %s "
            "OR IFNULL(so.kode_wip,'') LIKE %s)"
        )
        params_out.extend([like, like, like])
    sql_out += " ORDER BY so.created_at DESC LIMIT 100"
    cur.execute(sql_out, params_out)
    stok_out = _rows(cur.fetchall())

    from erp_raw_materials import list_materials
    material_list = [
        {
            "id": r["id"],
            "kode_material": r["code"],
            "nama_material": r["name"],
            "satuan": r.get("unit") or "pcs",
            "erp_material_id": r["id"],
        }
        for r in list_materials("material_lain")
    ]
    cur.close()
    conn.close()
    return jsonify(
        {
            "stok_in": stok_in,
            "stok_out": stok_out,
            "material_list": material_list,
            "stats": {
                "lots": len(stok_in),
                "qty_sisa": round(sum(float(r.get("qty_sisa") or 0) for r in stok_in), 3),
                "out_rows": len(stok_out),
            },
        }
    )


@api.post("/stok-material-lain")
def stok_material_lain_action():
    from app import ensure_extended_tables, generate_code

    body = request.get_json(silent=True) or {}
    action = (body.get("action") or "").strip().lower()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if action == "in":
        material_id = body.get("material_id")
        try:
            material_id = int(material_id) if material_id is not None else None
        except (TypeError, ValueError):
            material_id = None
        try:
            qty = float(body.get("qty") or 0)
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("qty harus angka")
        if not material_id:
            cur.close()
            conn.close()
            return _err("material_id wajib")
        if qty <= 0:
            cur.close()
            conn.close()
            return _err("qty harus > 0")
        tanggal = body.get("tanggal") or date.today().isoformat()
        from erp_raw_materials import resolve_material

        mat = resolve_material(erp_material_id=material_id, material_type="material_lain")
        if not mat:
            cur.close()
            conn.close()
            return _err("Material tidak ditemukan di ERP raw_materials", 404)
        erp_id = int(mat["id"])
        kode_internal = generate_code("BC-M")
        satuan = (body.get("satuan") or mat.get("unit") or "pcs")[:20]
        cur.execute(
            "INSERT INTO tbl_stok_material_lain_in "
            "(kode_internal, material_id, erp_material_id, kode_material, nama_material, "
            "qty, qty_sisa, satuan, tanggal_in) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                kode_internal,
                None,
                erp_id,
                mat.get("code"),
                mat.get("name"),
                qty,
                qty,
                satuan,
                tanggal,
            ),
        )
        new_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(
            {
                "ok": True,
                "id": new_id,
                "kode_internal": kode_internal,
                "qty": qty,
                "erp_material_id": erp_id,
            }
        ), 201

    if action == "out":
        stok_in_id = body.get("stok_in_id")
        try:
            stok_in_id = int(stok_in_id) if stok_in_id is not None else None
        except (TypeError, ValueError):
            stok_in_id = None
        try:
            qty = float(body.get("qty") or 0)
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("qty harus angka")
        if not stok_in_id:
            cur.close()
            conn.close()
            return _err("stok_in_id wajib")
        if qty <= 0:
            cur.close()
            conn.close()
            return _err("qty harus > 0")
        tanggal = body.get("tanggal") or date.today().isoformat()
        kode_wip = (body.get("kode_wip") or "").strip() or None
        keterangan = (body.get("keterangan") or "").strip() or None
        cur.execute("SELECT * FROM tbl_stok_material_lain_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok:
            cur.close()
            conn.close()
            return _err("Lot stok tidak ditemukan", 404)
        erp_id = stok.get("erp_material_id")
        if not erp_id:
            from bridge_metrics import incr

            incr("out_rejected_missing_erp_id")
            cur.close()
            conn.close()
            return _err("Lot material belum ter-map erp_material_id")
        sisa = float(stok["qty_sisa"] or 0)
        if sisa <= 0:
            cur.close()
            conn.close()
            return _err("Lot sudah habis")
        if qty > sisa:
            cur.close()
            conn.close()
            return _err(f"Qty OUT ({qty}) melebihi sisa ({sisa})")
        cur.execute(
            "INSERT INTO tbl_stok_material_lain_out "
            "(stok_in_id, material_id, erp_material_id, kode_material, nama_material, "
            "qty, kode_wip, tanggal, keterangan) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                stok_in_id,
                stok.get("material_id") or erp_id,
                erp_id,
                stok.get("kode_material"),
                stok.get("nama_material"),
                qty,
                kode_wip,
                tanggal,
                keterangan,
            ),
        )
        new_sisa = sisa - qty
        cur.execute(
            "UPDATE tbl_stok_material_lain_in SET qty_sisa=%s WHERE id=%s",
            (new_sisa, stok_in_id),
        )
        out_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(
            {
                "ok": True,
                "out_id": out_id,
                "qty_sisa": new_sisa,
                "bridge": {
                    "material_type": "material_lain",
                    "erp_material_id": erp_id,
                    "material_code": stok.get("kode_material"),
                    "material_name": stok.get("nama_material"),
                    "unit": stok.get("satuan") or "pcs",
                    "qty": qty,
                    "mrp_ref": f"stok-material-lain-out:{out_id}",
                },
            }
        )

    cur.close()
    conn.close()
    return _err("action harus in atau out")


@api.get("/usage-material-lain/scan")
def usage_material_scan():
    from erp_raw_materials import fetch_material_by_code

    kode = (request.args.get("q") or "").strip()
    if not kode:
        return _err("Kode kosong")
    row = fetch_material_by_code(kode, material_type="material_lain")
    if not row:
        return _err("Material tidak ditemukan di ERP", 404)
    return jsonify(
        {
            "kode_material": row["code"],
            "nama_material": row["name"],
            "satuan": row.get("unit") or "pcs",
            "erp_material_id": row["id"],
        }
    )


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
    try:
        qty_used = float(body.get("qty_used") or 0)
    except (TypeError, ValueError):
        return _err("qty_used harus angka")
    if qty_used <= 0:
        return _err("qty_used harus > 0")
    stok_in_id = body.get("stok_in_id")
    try:
        stok_in_id = int(stok_in_id) if stok_in_id not in (None, "") else None
    except (TypeError, ValueError):
        stok_in_id = None
    satuan = (body.get("satuan") or "").strip() or None
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT nama_material, satuan FROM tbl_stok_material_lain_in WHERE kode_material=%s LIMIT 1",
        (kode_material,),
    )
    mat = cur.fetchone()
    if not mat:
        cur.close()
        conn.close()
        return _err("Material tidak ditemukan", 404)
    if stok_in_id:
        cur.execute("SELECT * FROM tbl_stok_material_lain_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok:
            cur.close()
            conn.close()
            return _err("Lot stok material tidak ditemukan", 404)
        sisa = float(stok["qty_sisa"] or 0)
        if qty_used > sisa:
            cur.close()
            conn.close()
            return _err(f"Stok material tidak cukup (sisa {sisa})", 400)
        cur.execute(
            "INSERT INTO tbl_stok_material_lain_out (stok_in_id, material_id, qty, kode_wip, tanggal) "
            "VALUES (%s,%s,%s,%s,%s)",
            (stok_in_id, stok["material_id"], qty_used, kode_wip, date.today().isoformat()),
        )
        cur.execute(
            "UPDATE tbl_stok_material_lain_in SET qty_sisa=%s WHERE id=%s",
            (sisa - qty_used, stok_in_id),
        )
    cur.execute(
        "INSERT INTO tbl_usage_material_lain (kode_wip, kode_material, nama_material, qty_used, satuan) "
        "VALUES (%s,%s,%s,%s,%s)",
        (
            kode_wip,
            kode_material,
            mat.get("nama_material"),
            qty_used,
            satuan or mat.get("satuan") or "pcs",
        ),
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({"ok": True, "id": new_id, "stok_deducted": bool(stok_in_id)}), 201


# ---- Debt: masters PUT/DELETE kulit/kimia/rp ----
@api.put("/masters/kulit/<int:kulit_id>")
def master_kulit_update(*args, **kwargs):
    return _err("Katalog hanya di ERP Inventory — tidak bisa ubah/hapus dari MRP.", 403)



@api.delete("/masters/kulit/<int:kulit_id>")
def master_kulit_delete(*args, **kwargs):
    return _err("Katalog hanya di ERP Inventory — tidak bisa ubah/hapus dari MRP.", 403)



@api.put("/masters/kimia/<int:kimia_id>")
def master_kimia_update(*args, **kwargs):
    return _err("Katalog hanya di ERP Inventory — tidak bisa ubah/hapus dari MRP.", 403)



@api.delete("/masters/kimia/<int:kimia_id>")
def master_kimia_delete(*args, **kwargs):
    return _err("Katalog hanya di ERP Inventory — tidak bisa ubah/hapus dari MRP.", 403)



@api.put("/masters/rp/<int:rp_id>")
def master_rp_update(*args, **kwargs):
    return _err("Katalog hanya di ERP Inventory — tidak bisa ubah/hapus dari MRP.", 403)



@api.delete("/masters/rp/<int:rp_id>")
def master_rp_delete(*args, **kwargs):
    return _err("Katalog hanya di ERP Inventory — tidak bisa ubah/hapus dari MRP.", 403)



@api.get("/erp/fields")
def erp_fields_api():
    from erp_master_items import fields_payload

    return jsonify(
        fields_payload(
            thickness=(request.args.get("thickness") or "").strip(),
            material_name=(request.args.get("material_name") or "").strip(),
            color=(request.args.get("color") or "").strip(),
        )
    )


@api.get("/erp/combination")
def erp_combination_api():
    from erp_master_items import combination_payload

    material_name = (request.args.get("material_name") or "").strip()
    color = (request.args.get("color") or "").strip()
    emboss = (request.args.get("emboss") or "").strip()
    thickness = (request.args.get("thickness") or "").strip()
    if not material_name or not color or not emboss:
        return _err("Material Name, Color, Emboss wajib")
    rows = combination_payload(
        material_name=material_name,
        color=color,
        emboss=emboss,
        thickness=thickness,
    )
    if not rows:
        return _err("Kombinasi tidak ditemukan di Master Item ERP", 404)
    return jsonify({"options": rows, "source": "master_items"})


@api.get("/rencana/po/by-combination")
def rencana_po_by_combination():
    from app import ensure_extended_tables
    from spek_match import filter_master_po_by_spek

    color = (request.args.get("color") or "").strip()
    emboss = (request.args.get("emboss") or "").strip()
    material_name = (request.args.get("material_name") or request.args.get("item_name") or "").strip()
    thickness = (request.args.get("thickness") or request.args.get("tebal") or "").strip()
    color_swatch = (request.args.get("color_swatch") or "").strip()
    if not material_name or not emboss or not thickness:
        return _err("Material, Emboss, dan Tebal wajib")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT id, no_po, no_so, customer, item_name, tebal, warna, emboss, color_swatch, "
        "sq_ft, qty_order, qty_processed, qty_balance_erp, source_detail_id, lot_number, "
        "(qty_order - qty_processed) AS qty_outstanding "
        "FROM tbl_master_po "
        "WHERE status IN ('outstanding','partial') "
        "ORDER BY no_po, item_name"
    )
    items = filter_master_po_by_spek(
        _rows(cur.fetchall()),
        material_name=material_name,
        thickness=thickness,
        color=color,
        emboss=emboss,
        color_swatch=color_swatch,
    )
    _attach_erp_lot_no(items)
    cur.close()
    conn.close()
    return jsonify(items)


@api.get("/rencana-produksi/<int:rencana_id>/print")
def rencana_print_api(rencana_id: int):
    from app import _make_rpi_barcode

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM tbl_rencana_produksi WHERE id = %s", (rencana_id,))
    rencana = cur.fetchone()
    if not rencana:
        cur.close()
        conn.close()
        return _err("Rencana tidak ditemukan", 404)
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
    items = _rows(cur.fetchall())
    for item in items:
        item["barcode"] = (
            item.get("kode_barcode")
            or item.get("kode_rencana_item")
            or _make_rpi_barcode(item.get("thickness"), item.get("emboss"), item.get("color"))
        )
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
        "SELECT i.*, i.nama_customer, r.nama_rencana, r.tanggal_rencana, r.kode_rencana "
        "FROM tbl_rencana_item i "
        ""
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
        return _err("Item tidak ditemukan", 404)
    barcode = item.get("kode_barcode") or item.get("kode_rencana_item") or _make_rpi_barcode(
        item.get("thickness"), item.get("emboss"), item.get("color")
    )
    return jsonify({"item": _row(item), "barcode": barcode})


@api.get("/rencana-produksi/item/<int:item_id>/list-po")
def rencana_item_list_po_get(item_id: int):
    from app import ensure_extended_tables, ensure_rencana_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    ensure_extended_tables(cur)
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
        cur.close()
        conn.close()
        return _err("Item rencana tidak ditemukan", 404)

    # Spek item: filter SO outstanding by Material + Emboss + Tebal (+ Warna jika ada).
    t_material = _po_field_or_dash(item.get("material_name"))
    t_warna = _po_field_or_dash(item.get("color"))
    t_emboss = _po_field_or_dash(item.get("emboss"))
    t_tebal = _po_field_or_dash(item.get("thickness"))

    from spek_match import filter_master_po_by_spek

    cur.execute(
        f"SELECT po.id, po.no_po, po.no_so, po.customer, po.item_name, po.tebal, po.warna, "
        f"po.emboss, po.color_swatch, po.sq_ft, po.qty_order, po.qty_processed, "
        f"po.qty_balance_erp, po.source_detail_id, po.lot_number, po.status, "
        f"(po.qty_order - po.qty_processed) AS qty_outstanding, "
        f"COALESCE(rip.qty_proses, 0) AS already_allocated_qty "
        f"FROM tbl_master_po po "
        f"LEFT JOIN tbl_rencana_item_po rip "
        f"  ON rip.po_id = po.id AND rip.item_id = %s "
        f"WHERE ("
        f"  po.status IN ('outstanding','partial') "
        f"  OR rip.id IS NOT NULL"
        f") "
        f"ORDER BY po.no_po, po.item_name",
        (item_id,),
    )
    raw_po_rows = _rows(cur.fetchall())
    po_list = filter_master_po_by_spek(
        raw_po_rows,
        material_name="" if t_material == "-" else t_material,
        thickness="" if t_tebal == "-" else t_tebal,
        color="" if t_warna == "-" else t_warna,
        emboss="" if t_emboss == "-" else t_emboss,
    )
    listed_ids = {int(p.get("id") or 0) for p in po_list if p.get("id")}
    for row in raw_po_rows:
        po_id = int(row.get("id") or 0)
        if not po_id or po_id in listed_ids:
            continue
        if float(row.get("already_allocated_qty") or 0) > 0:
            po_list.append(row)
            listed_ids.add(po_id)
    _attach_erp_lot_no(po_list)

    cur.execute(
        "SELECT p.id, p.item_id, p.po_id, p.qty_outstanding, p.qty_proses, "
        "po.no_po, po.no_so, po.customer, po.item_name, po.tebal, po.warna, po.emboss, "
        "po.color_swatch, po.qty_order, po.qty_processed, po.qty_balance_erp, "
        "po.source_detail_id, po.lot_number, po.status AS po_status, "
        "(po.qty_order - po.qty_processed) AS qty_sisa_alokasi, "
        "p.qty_proses AS already_allocated_qty "
        "FROM tbl_rencana_item_po p "
        "JOIN tbl_master_po po ON po.id = p.po_id "
        "WHERE p.item_id = %s "
        "ORDER BY po.no_po, p.id",
        (item_id,),
    )
    selected_po = _rows(cur.fetchall())
    _attach_erp_lot_no(selected_po)
    cur.close()
    conn.close()
    return jsonify({"item": _row(item), "po_list": po_list, "selected_po": selected_po})


@api.post("/rencana-produksi/item/<int:item_id>/list-po")
def rencana_item_list_po_save(item_id: int):
    from app import _replace_item_po_selections, ensure_rencana_tables

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
    try:
        _replace_item_po_selections(cur, item_id, po_data)
    except ValueError as exc:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(exc))
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
            SELECT DATE(p.date_created) AS tanggal, p.no_po,
                   (SELECT po.no_so FROM tbl_master_po po
                    WHERE po.no_po = p.no_po AND po.no_so IS NOT NULL AND po.no_so <> ''
                    ORDER BY po.id DESC LIMIT 1) AS no_so,
                   p.kode_packing AS kode_process,
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


# ---- Monitoring SO / Lot ----
_MONITOR_STATUS_RANK = (
    "rencana",
    "proses_draft",
    "proses_started",
    "proses_saved",
    "proses_completed",
    "lab",
    "usage",
    "checkpoint",
    "checkpoint_ok",
    "packing",
    "packing_finished",
    "gudang_fg",
    "gudang_fg_out",
)
_PREP_STATUS_RANK = {"draft": 1, "started": 2, "saved": 3, "completed": 4}
_PACKING_STATUS_RANK = {"in_progress": 1, "finished": 2}
_FG_STATUS_RANK = {"in_stock": 1, "out": 2}


def _monitoring_status_code(
    *,
    prep_status: str | None = None,
    has_lab: bool = False,
    has_usage: bool = False,
    checkpoint_result: str | None = None,
    packing_status: str | None = None,
    fg_status: str | None = None,
) -> str:
    code = "rencana"

    def bump(next_code: str):
        nonlocal code
        if _MONITOR_STATUS_RANK.index(next_code) > _MONITOR_STATUS_RANK.index(code):
            code = next_code

    prep = (prep_status or "").strip().lower()
    if prep == "completed":
        bump("proses_completed")
    elif prep == "saved":
        bump("proses_saved")
    elif prep == "started":
        bump("proses_started")
    elif prep:
        bump("proses_draft")
    if has_lab:
        bump("lab")
    if has_usage:
        bump("usage")
    result = (checkpoint_result or "").strip().upper()
    if result == "OK":
        bump("checkpoint_ok")
    elif result:
        bump("checkpoint")
    pack = (packing_status or "").strip().lower()
    if pack == "finished":
        bump("packing_finished")
    elif pack:
        bump("packing")
    fg = (fg_status or "").strip().lower()
    if fg == "out":
        bump("gudang_fg_out")
    elif fg:
        bump("gudang_fg")
    return code


def _sql_in(ids: list[int]) -> tuple[str, tuple]:
    clean: list[int] = []
    seen: set[int] = set()
    for x in ids or []:
        try:
            i = int(x)
        except (TypeError, ValueError):
            continue
        if i not in seen:
            seen.add(i)
            clean.append(i)
    if not clean:
        return "", ()
    return ",".join(["%s"] * len(clean)), tuple(clean)


def _furthest_status(values, rank_map: dict) -> str | None:
    best = None
    best_rank = -1
    for raw in values or []:
        key = (raw or "").strip().lower()
        rank = rank_map.get(key, 0)
        if rank > best_rank:
            best_rank = rank
            best = key
    return best


def _monitoring_row_from_bundle(item: dict, bundle: dict, lot_map: dict[int, str]) -> dict:
    pos = bundle.get("pos") or []
    so_vals = []
    po_vals = []
    source_ids = []
    for p in pos:
        so = (p.get("no_so") or "").strip()
        if so and so not in so_vals:
            so_vals.append(so)
        po = (p.get("no_po") or "").strip()
        if po and po not in po_vals:
            po_vals.append(po)
        sid = p.get("source_detail_id")
        try:
            sid_i = int(sid) if sid is not None else None
        except (TypeError, ValueError):
            sid_i = None
        if sid_i and sid_i not in source_ids:
            source_ids.append(sid_i)
    lot_no = ""
    for sid in source_ids:
        lot_no = (lot_map.get(sid) or "").strip()
        if lot_no:
            break
    if not lot_no:
        lot_no = (item.get("kode_lot_wip") or "").strip()
    prep_rows = bundle.get("prep") or []
    prep_status = _furthest_status([r.get("status") for r in prep_rows], _PREP_STATUS_RANK)
    qty_prep = 0.0
    wip_codes = []
    for r in prep_rows:
        qty_prep += float(r.get("total_size") or 0)
        wip = (r.get("kode_wip") or "").strip()
        if wip and wip not in wip_codes:
            wip_codes.append(wip)
    item_wip = (item.get("kode_lot_wip") or "").strip()
    if item_wip and item_wip not in wip_codes:
        wip_codes.append(item_wip)
    packing_rows = bundle.get("packing") or []
    packing_status = _furthest_status(
        [r.get("status") for r in packing_rows], _PACKING_STATUS_RANK
    )
    qty_fg = 0.0
    fg_measured = False
    for r in packing_rows:
        if (r.get("status") or "").strip().lower() == "finished":
            fg_measured = True
            qty_fg += float(r.get("total_ukuran") or 0)
    fg_rows = bundle.get("fg") or []
    fg_status = _furthest_status([r.get("status") for r in fg_rows], _FG_STATUS_RANK)
    if not fg_measured:
        for r in fg_rows:
            qty_fg += float(r.get("total_ukuran") or 0)
            if float(r.get("total_ukuran") or 0) > 0:
                fg_measured = True
    cp_rows = bundle.get("checkpoint") or []
    checkpoint_result = ""
    for r in cp_rows:
        res = (r.get("result") or "").strip().upper()
        if res == "OK":
            checkpoint_result = "OK"
            break
        if res and not checkpoint_result:
            checkpoint_result = res
    has_lab = bool(bundle.get("lab"))
    has_usage = bool(bundle.get("usage"))
    status_terakhir = _monitoring_status_code(
        prep_status=prep_status,
        has_lab=has_lab,
        has_usage=has_usage,
        checkpoint_result=checkpoint_result or None,
        packing_status=packing_status,
        fg_status=fg_status,
    )
    return {
        "rencana_item_id": item.get("id"),
        "kode_rencana": item.get("kode_rencana"),
        "kode_rencana_item": item.get("kode_rencana_item"),
        "kode_lot_wip": item.get("kode_lot_wip"),
        "nama_rencana": item.get("nama_rencana"),
        "nama_customer": item.get("nama_customer") or (pos[0].get("customer") if pos else None),
        "material_name": item.get("material_name"),
        "color": item.get("color"),
        "thickness": item.get("thickness"),
        "emboss": item.get("emboss"),
        "no_so": " / ".join(so_vals),
        "no_po": ", ".join(po_vals),
        "lot_no": lot_no,
        "source_detail_ids": source_ids,
        "kode_wip_list": wip_codes,
        "status_terakhir": status_terakhir,
        "total_qty_persiapan": qty_prep,
        "total_qty_fg": qty_fg if fg_measured else None,
        "fg_measured": fg_measured,
    }


def _monitoring_fetch_items(cur, item_id: int | None = None) -> list[dict]:
    sql = (
        "SELECT i.id, i.kode_rencana_item, i.kode_lot_wip, i.nama_customer, i.material_name, "
        "i.color, i.thickness, i.emboss, r.kode_rencana, r.nama_rencana, "
        "r.status AS rencana_status, r.tanggal_rencana, r.date_created "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
    )
    params: list = []
    if item_id is not None:
        sql += "WHERE i.id = %s "
        params.append(int(item_id))
    sql += "ORDER BY COALESCE(r.tanggal_rencana, r.date_created) DESC, i.id DESC"
    if item_id is None:
        sql += " LIMIT 500"
    cur.execute(sql, tuple(params))
    return _rows(cur.fetchall())


def _monitoring_attach(cur, items: list[dict], *, include_detail: bool = False) -> list[dict]:
    if not items:
        return []
    item_ids = [int(i["id"]) for i in items if i.get("id") is not None]
    rpi_by_id = {
        int(i["id"]): (i.get("kode_rencana_item") or "")
        for i in items
        if i.get("id") is not None
    }
    rpi_to_id = {v: k for k, v in rpi_by_id.items() if v}
    bundles: dict[int, dict] = {
        iid: {
            "pos": [],
            "prep": [],
            "packing": [],
            "fg": [],
            "checkpoint": [],
            "lab": [],
            "usage": [],
            "ky": [],
        }
        for iid in item_ids
    }
    in_sql, in_params = _sql_in(item_ids)

    cur.execute(
        f"SELECT p.item_id, po.no_so, po.no_po, po.source_detail_id, po.customer "
        f"FROM tbl_rencana_item_po p "
        f"JOIN tbl_master_po po ON po.id = p.po_id "
        f"WHERE p.item_id IN ({in_sql}) "
        f"ORDER BY p.item_id, po.no_so, po.no_po",
        in_params,
    )
    for row in _rows(cur.fetchall()):
        bundles[int(row["item_id"])]["pos"].append(row)

    rpi_codes = [c for c in rpi_by_id.values() if c]
    prep_sql = (
        "SELECT id, rencana_item_id, kode_wip, kode_rencana, kode_proses, status, "
        "checkpoint_status, total_size FROM tbl_persiapan_kulit WHERE rencana_item_id IN "
        f"({in_sql})"
    )
    prep_params = list(in_params)
    if rpi_codes:
        rpi_ph = ",".join(["%s"] * len(rpi_codes))
        prep_sql += f" OR (rencana_item_id IS NULL AND kode_rencana IN ({rpi_ph}))"
        prep_params.extend(rpi_codes)
    cur.execute(prep_sql, tuple(prep_params))
    wip_to_item: dict[str, int] = {}
    for raw in cur.fetchall() or []:
        row = _row(raw)
        iid = row.get("rencana_item_id")
        try:
            iid = int(iid) if iid is not None else None
        except (TypeError, ValueError):
            iid = None
        if iid not in bundles:
            iid = rpi_to_id.get((row.get("kode_rencana") or "").strip())
        if iid not in bundles:
            continue
        bundles[iid]["prep"].append(row)
        wip = (row.get("kode_wip") or "").strip()
        if wip:
            wip_to_item[wip] = iid
    for item in items:
        wip = (item.get("kode_lot_wip") or "").strip()
        if wip:
            wip_to_item[wip] = int(item["id"])

    wip_list = [w for w in wip_to_item.keys() if w]
    packing_ids: list[int] = []
    if wip_list or item_ids:
        pack_clauses = [f"rencana_item_id IN ({in_sql})"]
        pack_params = list(in_params)
        if wip_list:
            wip_ph = ",".join(["%s"] * len(wip_list))
            pack_clauses.append(f"kode_wip IN ({wip_ph})")
            pack_params.extend(wip_list)
        cur.execute(
            "SELECT id, rencana_item_id, kode_wip, kode_packing, status, total_ukuran, total_lembar "
            f"FROM tbl_packing WHERE {' OR '.join(pack_clauses)}",
            tuple(pack_params),
        )
        for raw in cur.fetchall() or []:
            row = _row(raw)
            iid = row.get("rencana_item_id")
            try:
                iid = int(iid) if iid is not None else None
            except (TypeError, ValueError):
                iid = None
            if iid not in bundles:
                iid = wip_to_item.get((row.get("kode_wip") or "").strip())
            if iid not in bundles:
                continue
            bundles[iid]["packing"].append(row)
            wip_to_item.setdefault((row.get("kode_wip") or "").strip(), iid)
            if row.get("id") is not None:
                packing_ids.append(int(row["id"]))

    wip_list = [w for w in wip_to_item.keys() if w]
    if wip_list or packing_ids:
        fg_clauses = []
        fg_params: list = []
        if wip_list:
            wip_ph = ",".join(["%s"] * len(wip_list))
            fg_clauses.append(f"kode_wip IN ({wip_ph})")
            fg_params.extend(wip_list)
        if packing_ids:
            pk_sql, pk_params = _sql_in(packing_ids)
            fg_clauses.append(f"packing_id IN ({pk_sql})")
            fg_params.extend(pk_params)
        cur.execute(
            "SELECT packing_id, kode_packing, kode_wip, status, total_ukuran "
            f"FROM tbl_gudang_fg WHERE {' OR '.join(fg_clauses)}",
            tuple(fg_params),
        )
        for raw in cur.fetchall() or []:
            row = _row(raw)
            iid = wip_to_item.get((row.get("kode_wip") or "").strip())
            if iid not in bundles:
                continue
            bundles[iid]["fg"].append(row)

    if wip_list:
        wip_ph = ",".join(["%s"] * len(wip_list))
        cur.execute(
            f"SELECT kode_wip, result, treatment, measured_at FROM tbl_checkpoint "
            f"WHERE kode_wip IN ({wip_ph}) ORDER BY id DESC",
            tuple(wip_list),
        )
        for raw in cur.fetchall() or []:
            row = _row(raw)
            iid = wip_to_item.get((row.get("kode_wip") or "").strip())
            if iid not in bundles:
                continue
            bundles[iid]["checkpoint"].append(row)
        cur.execute(
            f"SELECT kode_wip, kode_lot_warna, nama_warna, qty_pembuatan, qty_digunakan "
            f"FROM tbl_usage_color WHERE kode_wip IN ({wip_ph}) ORDER BY id",
            tuple(wip_list),
        )
        for raw in cur.fetchall() or []:
            row = _row(raw)
            iid = wip_to_item.get((row.get("kode_wip") or "").strip())
            if iid not in bundles:
                continue
            bundles[iid]["usage"].append(row)

    cur.execute(
        f"SELECT id, rencana_item_id, kode_lot_warna, nama_lot_warna, status "
        f"FROM tbl_lab_lot WHERE rencana_item_id IN ({in_sql})",
        in_params,
    )
    for raw in cur.fetchall() or []:
        row = _row(raw)
        try:
            iid = int(row.get("rencana_item_id"))
        except (TypeError, ValueError):
            continue
        if iid in bundles:
            bundles[iid]["lab"].append(row)

    if include_detail:
        prep_ids = [int(p["id"]) for b in bundles.values() for p in b["prep"] if p.get("id")]
        if prep_ids:
            ky_sql, ky_params = _sql_in(prep_ids)
            prep_by_id = {
                int(p["id"]): iid
                for iid, b in bundles.items()
                for p in b["prep"]
                if p.get("id") is not None
            }
            cur.execute(
                f"SELECT ky.*, pk.kode_proses, pk.kode_wip "
                f"FROM tbl_persiapan_ky ky "
                f"JOIN tbl_persiapan_kulit pk ON pk.id = ky.persiapan_id "
                f"WHERE ky.persiapan_id IN ({ky_sql}) "
                f"ORDER BY ky.created_at",
                ky_params,
            )
            for raw in cur.fetchall() or []:
                row = _row(raw)
                iid = prep_by_id.get(int(row["persiapan_id"]))
                if iid in bundles:
                    bundles[iid]["ky"].append(row)
        lot_codes = []
        for b in bundles.values():
            for u in b["usage"]:
                kode = (u.get("kode_lot_warna") or "").strip()
                if kode and kode not in lot_codes:
                    lot_codes.append(kode)
            for lab in b["lab"]:
                kode = (lab.get("kode_lot_warna") or "").strip()
                if kode and kode not in lot_codes:
                    lot_codes.append(kode)
        chem_by_lot: dict[str, list] = {}
        if lot_codes:
            lot_ph = ",".join(["%s"] * len(lot_codes))
            cur.execute(
                f"SELECT kode_lot_warna, kode_kimia, nama_kimia, resep, satuan, qty "
                f"FROM tbl_lab_lot_detail WHERE kode_lot_warna IN ({lot_ph}) ORDER BY id",
                tuple(lot_codes),
            )
            for raw in cur.fetchall() or []:
                row = _row(raw)
                kode = (row.get("kode_lot_warna") or "").strip()
                chem_by_lot.setdefault(kode, []).append(row)
        for iid, b in bundles.items():
            chemicals = []
            if b["usage"]:
                for u in b["usage"]:
                    kode = (u.get("kode_lot_warna") or "").strip()
                    qty_used = float(u.get("qty_digunakan") or 0)
                    qty_make = float(u.get("qty_pembuatan") or 0)
                    details = chem_by_lot.get(kode) or []
                    if details:
                        for d in details:
                            recipe_qty = float(d.get("qty") or 0)
                            used_qty = (
                                (recipe_qty / qty_make) * qty_used if qty_make > 0 else recipe_qty
                            )
                            used_qty = round(used_qty, 4)
                            chemicals.append(
                                {
                                    "kode_lot_warna": kode,
                                    "nama_warna": u.get("nama_warna"),
                                    "kode_kimia": d.get("kode_kimia"),
                                    "nama_kimia": d.get("nama_kimia"),
                                    "satuan": d.get("satuan") or "kg",
                                    "qty": used_qty,
                                    "qty_lot": qty_used,
                                }
                            )
                    else:
                        chemicals.append(
                            {
                                "kode_lot_warna": kode,
                                "nama_warna": u.get("nama_warna"),
                                "kode_kimia": None,
                                "nama_kimia": u.get("nama_warna"),
                                "satuan": "kg",
                                "qty": qty_used,
                                "qty_lot": qty_used,
                            }
                        )
            b["chemicals"] = chemicals

    source_ids = []
    for b in bundles.values():
        for p in b["pos"]:
            sid = p.get("source_detail_id")
            if sid is not None:
                source_ids.append(sid)
    lot_map = _erp_lot_nos_for_source_details(source_ids)
    out = []
    for item in items:
        iid = int(item["id"])
        row = _monitoring_row_from_bundle(item, bundles[iid], lot_map)
        if include_detail:
            row["ky"] = bundles[iid].get("ky") or []
            row["chemicals"] = bundles[iid].get("chemicals") or []
            row["persiapan"] = bundles[iid].get("prep") or []
            row["packing"] = bundles[iid].get("packing") or []
        out.append(row)
    return out


@api.get("/monitoring")
def monitoring_list():
    from app import ensure_extended_tables, ensure_lab_tables, ensure_rencana_tables

    q = (request.args.get("q") or "").strip().lower()
    status_f = (request.args.get("status") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    ensure_extended_tables(cur)
    ensure_lab_tables(cur)
    conn.commit()
    items = _monitoring_fetch_items(cur)
    rows = _monitoring_attach(cur, items, include_detail=False)
    cur.close()
    conn.close()
    if status_f:
        rows = [r for r in rows if r.get("status_terakhir") == status_f]
    if q:
        filtered = []
        for r in rows:
            blob = " ".join(
                str(r.get(k) or "")
                for k in (
                    "no_so",
                    "lot_no",
                    "status_terakhir",
                    "nama_customer",
                    "kode_rencana_item",
                    "kode_lot_wip",
                    "no_po",
                    "material_name",
                )
            ).lower()
            if q in blob:
                filtered.append(r)
        rows = filtered
    return jsonify(rows)


@api.get("/monitoring/<int:rencana_item_id>")
def monitoring_detail(rencana_item_id: int):
    from app import ensure_extended_tables, ensure_lab_tables, ensure_rencana_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    ensure_extended_tables(cur)
    ensure_lab_tables(cur)
    conn.commit()
    items = _monitoring_fetch_items(cur, item_id=rencana_item_id)
    if not items:
        cur.close()
        conn.close()
        return _err("Item rencana tidak ditemukan", 404)
    rows = _monitoring_attach(cur, items, include_detail=True)
    cur.close()
    conn.close()
    return jsonify(rows[0])


# ---- Integration: packing production mirror result ----
@api.post("/packing/<int:packing_id>/production-result")
def packing_production_result(packing_id: int):
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT id, kode_wip FROM tbl_packing WHERE id=%s", (packing_id,))
    pkg = cur.fetchone()
    if not pkg:
        cur.close()
        conn.close()
        return _err("Packing tidak ditemukan", 404)
    prod_id = body.get("erp_production_id")
    detail_id = body.get("erp_production_detail_id")
    try:
        prod_id = int(prod_id) if prod_id is not None else None
        detail_id = int(detail_id) if detail_id is not None else None
    except (TypeError, ValueError):
        prod_id = detail_id = None
    cur.execute(
        "UPDATE tbl_packing SET erp_production_id=%s, erp_production_detail_id=%s WHERE id=%s",
        (prod_id, detail_id, packing_id),
    )
    if pkg.get("kode_wip"):
        cur.execute(
            "UPDATE tbl_rencana_item SET erp_production_id=%s, erp_production_detail_id=%s "
            "WHERE kode_lot_wip=%s",
            (prod_id, detail_id, pkg["kode_wip"]),
        )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(
        {
            "ok": True,
            "packing_id": packing_id,
            "erp_production_id": prod_id,
            "erp_production_detail_id": detail_id,
        }
    )


@api.get("/packing/<int:packing_id>/bridge-context")
def packing_bridge_context(packing_id: int):
    """Konteks source_detail_id + qty untuk production mirror."""
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_packing WHERE id=%s", (packing_id,))
    packing = cur.fetchone()
    if not packing:
        cur.close()
        conn.close()
        return _err("Packing tidak ditemukan", 404)
    cur.execute(
        "SELECT po.source_detail_id, po.no_po, p.qty_proses AS qty_sq, po.id AS master_po_id "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_item_po p ON p.item_id = i.id "
        "JOIN tbl_master_po po ON po.id = p.po_id "
        "WHERE i.kode_lot_wip = %s AND po.source_detail_id IS NOT NULL "
        "ORDER BY p.id ASC LIMIT 1",
        (packing.get("kode_wip"),),
    )
    line = cur.fetchone()
    if not line:
        cur.execute(
            "SELECT COALESCE(mp1.source_detail_id, mp2.source_detail_id) AS source_detail_id, "
            "pp.no_po, pp.qty_sq, COALESCE(mp1.id, mp2.id) AS master_po_id "
            "FROM tbl_packing_po pp "
            "LEFT JOIN tbl_master_po mp1 ON mp1.id = pp.po_id "
            "LEFT JOIN tbl_master_po mp2 ON pp.po_id IS NULL AND mp2.id = ("
            "  SELECT id FROM tbl_master_po WHERE no_po = pp.no_po ORDER BY id DESC LIMIT 1"
            ") WHERE pp.packing_id=%s LIMIT 1",
            (packing_id,),
        )
        line = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(
        {
            "packing": _row(packing),
            "line": _row(line) if line else None,
        }
    )


# ---- Checkpoint QC ----
CHECKPOINT_QC_NAME = "QC"


def _resolve_checkpoint_treatment(cur, raw, *, allow_empty_as_qc=False):
    """Return nama treatment, False if invalid, None if empty and not allowed."""
    from app import ensure_master_treatment

    name = (raw or "").strip()
    if not name:
        return CHECKPOINT_QC_NAME if allow_empty_as_qc else None
    if name.upper() == CHECKPOINT_QC_NAME:
        return CHECKPOINT_QC_NAME
    ensure_master_treatment(cur)
    cur.execute(
        "SELECT nama_treatment FROM tbl_master_treatment WHERE nama_treatment=%s LIMIT 1",
        (name,),
    )
    row = cur.fetchone()
    if not row:
        return False
    return row.get("nama_treatment") if isinstance(row, dict) else row[0]


def _wip_plan_info(cur, kode_wip: str) -> dict:
    info = {
        "kode_rpi": None,
        "nama_rencana": None,
        "material_name": None,
        "emboss": None,
        "warna": None,
    }
    if not kode_wip:
        return info
    cur.execute(
        "SELECT kode_rencana, rencana_item_id, emboss, warna "
        "FROM tbl_persiapan_kulit WHERE kode_wip=%s "
        "ORDER BY FIELD(status,'completed','saved','started','draft'), id DESC LIMIT 1",
        (kode_wip,),
    )
    pk = cur.fetchone() or {}
    item = None
    item_id = pk.get("rencana_item_id")
    if item_id:
        cur.execute(
            "SELECT kode_rencana_item, material_name, emboss, color, rencana_id "
            "FROM tbl_rencana_item WHERE id=%s LIMIT 1",
            (item_id,),
        )
        item = cur.fetchone()
    if not item and pk.get("kode_rencana"):
        cur.execute(
            "SELECT kode_rencana_item, material_name, emboss, color, rencana_id "
            "FROM tbl_rencana_item WHERE kode_rencana_item=%s LIMIT 1",
            (pk.get("kode_rencana"),),
        )
        item = cur.fetchone()
    if not item:
        cur.execute(
            "SELECT kode_rencana_item, material_name, emboss, color, rencana_id "
            "FROM tbl_rencana_item WHERE kode_lot_wip=%s "
            "ORDER BY id DESC LIMIT 1",
            (kode_wip,),
        )
        item = cur.fetchone()
    item = item or {}
    nama = None
    rid = item.get("rencana_id")
    if rid:
        cur.execute(
            "SELECT nama_rencana FROM tbl_rencana_produksi WHERE id=%s LIMIT 1",
            (rid,),
        )
        rrow = cur.fetchone() or {}
        nama = rrow.get("nama_rencana")
    info["kode_rpi"] = item.get("kode_rencana_item") or pk.get("kode_rencana")
    info["nama_rencana"] = nama
    info["material_name"] = item.get("material_name")
    info["emboss"] = pk.get("emboss") or item.get("emboss")
    info["warna"] = pk.get("warna") or item.get("color")
    return info


def _attach_plan_info(cur, rows: list) -> list:
    cache: dict = {}
    out = []
    for row in rows:
        wip = (row or {}).get("kode_wip")
        if wip not in cache:
            cache[wip] = _wip_plan_info(cur, wip)
        merged = dict(row or {})
        merged.update(cache.get(wip) or {})
        out.append(merged)
    return out


@api.get("/checkpoint")
def checkpoint_list():
    from app import ensure_extended_tables

    result_f = (request.args.get("result") or "").strip().upper()
    treatment_f = (request.args.get("treatment") or "").strip()
    kode_wip = (request.args.get("kode_wip") or "").strip()
    q = (request.args.get("q") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    sql = "SELECT * FROM tbl_checkpoint WHERE 1=1"
    params: list = []
    if kode_wip:
        sql += " AND kode_wip=%s"
        params.append(kode_wip)
    if result_f in ("OK", "NG"):
        sql += " AND UPPER(IFNULL(result,''))=%s"
        params.append(result_f)
    if treatment_f:
        sql += " AND IFNULL(treatment,'')=%s"
        params.append(treatment_f)
    if q:
        like = f"%{q}%"
        sql += (
            " AND (kode_wip LIKE %s OR IFNULL(kode_packing,'') LIKE %s "
            "OR IFNULL(remark,'') LIKE %s OR IFNULL(result,'') LIKE %s "
            "OR IFNULL(treatment,'') LIKE %s)"
        )
        params.extend([like, like, like, like, like])
    sql += " ORDER BY measured_at DESC, id DESC LIMIT 200"
    cur.execute(sql, params)
    rows = _attach_plan_info(cur, _rows(cur.fetchall()))
    cur.close()
    conn.close()
    return jsonify(rows)


@api.get("/checkpoint/scan-wip")
def checkpoint_scan_wip():
    """Lookup WIP untuk form checkpoint (persiapan / packing / rencana)."""
    from app import ensure_extended_tables

    kode_wip = (request.args.get("q") or "").strip()
    if not kode_wip:
        return _err("Kode WIP kosong")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    cur.execute(
        "SELECT * FROM tbl_persiapan_kulit WHERE kode_wip=%s "
        "ORDER BY FIELD(status,'completed','saved','started','draft'), id DESC LIMIT 5",
        (kode_wip,),
    )
    prep_rows = _rows(cur.fetchall())
    prep = prep_rows[0] if prep_rows else None

    cur.execute(
        "SELECT id, kode_packing, no_po, customer, status, erp_production_detail_id, total_ukuran "
        "FROM tbl_packing WHERE kode_wip=%s ORDER BY id DESC LIMIT 5",
        (kode_wip,),
    )
    packing_rows = _rows(cur.fetchall())
    packing = None
    for p in packing_rows:
        if p.get("erp_production_detail_id"):
            packing = p
            break
    if packing is None and packing_rows:
        packing = packing_rows[0]

    cur.execute(
        "SELECT i.id, i.kode_rencana_item, i.kode_lot_wip, i.thickness, i.color, "
        "i.erp_production_detail_id, i.erp_production_id, i.nama_customer "
        "FROM tbl_rencana_item i "
        ""
        "WHERE i.kode_lot_wip=%s "
        "ORDER BY (i.erp_production_detail_id IS NULL), i.id DESC LIMIT 1",
        (kode_wip,),
    )
    rencana = cur.fetchone()

    if not prep and not packing and not rencana:
        cur.close()
        conn.close()
        return _err("WIP tidak ditemukan di shopfloor", 404)

    erp_pd = None
    for src in (packing, rencana, prep):
        if not src:
            continue
        sid = src.get("erp_production_detail_id")
        if sid:
            try:
                erp_pd = int(sid)
                break
            except (TypeError, ValueError):
                pass

    plan = _wip_plan_info(cur, kode_wip)
    cur.close()
    conn.close()
    return jsonify(
        {
            "ok": True,
            "kode_wip": kode_wip,
            "prep": _row(prep) if prep else None,
            "packing": _row(packing) if packing else None,
            "rencana": _row(rencana) if rencana else None,
            "kode_packing": (packing or {}).get("kode_packing"),
            "customer": (packing or {}).get("customer")
            or (rencana or {}).get("nama_customer"),
            "tebal_target": (prep or {}).get("tebal") or (rencana or {}).get("thickness"),
            "warna": plan.get("warna")
            or (prep or {}).get("warna")
            or (rencana or {}).get("color"),
            "erp_production_detail_id": erp_pd,
            "prep_status": (prep or {}).get("status"),
            "checkpoint_status": (prep or {}).get("checkpoint_status"),
            "treatment_jenis": (prep or {}).get("treatment_jenis"),
            "treatment_list": (prep or {}).get("treatment_list"),
            "kode_rpi": plan.get("kode_rpi"),
            "nama_rencana": plan.get("nama_rencana"),
            "material_name": plan.get("material_name"),
            "emboss": plan.get("emboss") or (prep or {}).get("emboss"),
        }
    )


@api.post("/checkpoint")
def checkpoint_create():
    from app import ensure_extended_tables, ensure_master_treatment

    body = request.get_json(silent=True) or {}
    kode_wip = (body.get("kode_wip") or "").strip()
    if not kode_wip:
        return _err("kode_wip wajib")
    result = (body.get("result") or "").strip().upper() or None

    thickness = body.get("thickness_actual")
    if thickness is not None and thickness != "":
        try:
            thickness = float(thickness)
        except (TypeError, ValueError):
            return _err("thickness_actual harus angka")
        if thickness <= 0:
            return _err("thickness_actual harus > 0")
    else:
        thickness = None

    softness = (body.get("softness_actual") or "").strip() or None
    remark = (body.get("remark") or "").strip() or None
    kode_packing = (body.get("kode_packing") or "").strip() or None
    erp_pd = body.get("erp_production_detail_id")
    try:
        erp_pd = int(erp_pd) if erp_pd is not None else None
    except (TypeError, ValueError):
        erp_pd = None

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    ensure_master_treatment(cur)
    conn.commit()

    treatment = _resolve_checkpoint_treatment(
        cur,
        body.get("treatment"),
        allow_empty_as_qc=result in ("OK", "NG"),
    )
    if treatment is None:
        cur.close()
        conn.close()
        return _err("Pilih treatment dari master atau QC")
    if treatment is False:
        cur.close()
        conn.close()
        return _err("Treatment tidak ada di Master Treatment MRP")

    is_qc = treatment == CHECKPOINT_QC_NAME
    if is_qc:
        if result not in ("OK", "NG"):
            cur.close()
            conn.close()
            return _err("result wajib OK atau NG")
        is_ok = body.get("is_ok")
        if is_ok is None:
            is_ok = 1 if result == "OK" else 0
        else:
            is_ok = 1 if is_ok in (True, 1, "1", "true", "True") else 0
    else:
        result = None
        is_ok = 1
        thickness = None
        softness = None

    # Validasi WIP ada di shopfloor (persiapan / packing / rencana).
    cur.execute(
        "SELECT 1 AS ok FROM tbl_persiapan_kulit WHERE kode_wip=%s LIMIT 1",
        (kode_wip,),
    )
    found = cur.fetchone()
    if not found:
        cur.execute("SELECT 1 AS ok FROM tbl_packing WHERE kode_wip=%s LIMIT 1", (kode_wip,))
        found = cur.fetchone()
    if not found:
        cur.execute(
            "SELECT 1 AS ok FROM tbl_rencana_item WHERE kode_lot_wip=%s LIMIT 1",
            (kode_wip,),
        )
        found = cur.fetchone()
    if not found:
        cur.close()
        conn.close()
        return _err("WIP tidak ditemukan di shopfloor", 404)

    if erp_pd is None:
        cur.execute(
            "SELECT erp_production_detail_id FROM tbl_packing "
            "WHERE kode_wip=%s AND erp_production_detail_id IS NOT NULL "
            "ORDER BY id DESC LIMIT 1",
            (kode_wip,),
        )
        row = cur.fetchone()
        if row:
            erp_pd = row.get("erp_production_detail_id")
        else:
            cur.execute(
                "SELECT erp_production_detail_id FROM tbl_rencana_item "
                "WHERE kode_lot_wip=%s AND erp_production_detail_id IS NOT NULL LIMIT 1",
                (kode_wip,),
            )
            row = cur.fetchone()
            if row:
                erp_pd = row.get("erp_production_detail_id")

    if not kode_packing:
        cur.execute(
            "SELECT kode_packing FROM tbl_packing WHERE kode_wip=%s "
            "ORDER BY FIELD(status,'finished','in_progress'), id DESC LIMIT 1",
            (kode_wip,),
        )
        prow = cur.fetchone()
        if prow:
            kode_packing = prow.get("kode_packing")

    cur.execute(
        "INSERT INTO tbl_checkpoint "
        "(kode_wip, kode_packing, checkpoint_type, treatment, thickness_actual, softness_actual, "
        "result, is_ok, remark, erp_production_detail_id) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            kode_wip,
            kode_packing,
            (body.get("checkpoint_type") or ("qc" if is_qc else "treatment"))[:50],
            treatment,
            thickness,
            softness,
            result,
            is_ok,
            remark,
            erp_pd,
        ),
    )
    new_id = cur.lastrowid
    cur.execute(
        "UPDATE tbl_persiapan_kulit SET checkpoint_status=%s WHERE kode_wip=%s",
        (treatment, kode_wip),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(
        {
            "ok": True,
            "id": new_id,
            "kode_wip": kode_wip,
            "kode_packing": kode_packing,
            "erp_production_detail_id": erp_pd,
            "treatment": treatment,
            "checkpoint_status": treatment,
            "result": result,
            "is_ok": bool(is_ok),
        }
    ), 201


@api.post("/checkpoint/<int:cp_id>/qc-result")
def checkpoint_qc_result(cp_id: int):
    body = request.get_json(silent=True) or {}
    qc_detail_id = body.get("erp_qc_detail_id")
    try:
        qc_detail_id = int(qc_detail_id) if qc_detail_id is not None else None
    except (TypeError, ValueError):
        return _err("erp_qc_detail_id wajib")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "UPDATE tbl_checkpoint SET erp_qc_detail_id=%s WHERE id=%s",
        (qc_detail_id, cp_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "id": cp_id, "erp_qc_detail_id": qc_detail_id})


# ---- Master map ERP material ----
@api.post("/masters/<master_type>/map-erp-material")
def master_map_erp_material(master_type):
    return _err("Endpoint map-erp-material dihapus — katalog langsung dari ERP raw_materials.", 410)



@api.post("/masters/erp/map-master-item")
def master_erp_map_item():
    return _err("master_erp lokal dihapus — pakai Master Item ERP.", 410)



@api.post("/masters/raw-materials/backfill-erp")
def masters_raw_materials_backfill_erp():
    return _err(
        "Backfill master_*→ERP dihapus — katalog sudah ERP-only (raw_materials).",
        410,
    )


@api.post("/masters/import/page1-stock")
def masters_import_page1_stock():
    from app import ensure_extended_tables
    from raw_material_import import import_page1_stock_ledger

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.close()
    try:
        result = import_page1_stock_ledger(conn)
    except FileNotFoundError as e:
        conn.close()
        return _err(str(e), 404)
    except Exception as e:
        conn.close()
        return _err(f"Import Page1 gagal: {e}", 400)
    conn.close()
    return jsonify(result)


# ---- Palet/YL: operasional-only acknowledgement (Fase 4) ----
@api.get("/palet/integration-status")
def palet_integration_status():
    return jsonify(
        {
            "ok": True,
            "mode": "operational_only",
            "detail": (
                "Palet/YL tetap SoR operasional di MRP; tidak diposting ke material_stocks ERP "
                "pada fase 2C (hanya kimia/RP + FG)."
            ),
        }
    )
