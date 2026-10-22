"""JSON API for Tonghong Vue UI — mounted at /api/mrp."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import mysql.connector
from flask import Blueprint, jsonify, request

from db import get_db_connection
from mod_label import _mod_label_identity
from mrp_api.paging import order_sql, page_payload, parse_page_args, slice_page, sort_rows

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
    pg = parse_page_args(request.args, default_page_size=50)
    order = order_sql(
        {
            "created_at": "m.created_at",
            "tanggal": "m.tanggal",
            "kode_palet": "m.kode_palet",
            "direction": "m.direction",
            "id": "m.id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="m.created_at DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    where = " WHERE 1=1"
    params: list = []
    if direction in ("IN", "OUT"):
        where += " AND m.direction=%s"
        params.append(direction)
    if q:
        like = f"%{q}%"
        where += " AND (m.kode_palet LIKE %s OR IFNULL(m.keterangan,'') LIKE %s)"
        params.extend([like, like])
    cur.execute(f"SELECT COUNT(*) AS c FROM tbl_palet_movement m{where}", params)
    total = int((cur.fetchone() or {}).get("c") or 0)
    sql = (
        "SELECT m.*, (SELECT COUNT(*) FROM tbl_yl y WHERE y.kode_palet = m.kode_palet) AS jml_yl, "
        "(SELECT COALESCE(SUM(y.qty),0) FROM tbl_yl y WHERE y.kode_palet = m.kode_palet) AS qty_yl "
        f"FROM tbl_palet_movement m{where} ORDER BY {order} LIMIT %s OFFSET %s"
    )
    cur.execute(sql, params + [pg["page_size"], pg["offset"]])
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(
        page_payload(
            items=data,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


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


def _yl_spek_used(cur, kode_palet: str, kode_yl: str) -> bool:
    cur.execute(
        "SELECT id FROM tbl_persiapan_ky WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
        (kode_palet, kode_yl),
    )
    if cur.fetchone():
        return True
    cur.execute(
        "SELECT id FROM tbl_yl_movement WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
        (kode_palet, kode_yl),
    )
    return cur.fetchone() is not None


def _yl_delete_block_reason(cur, kode_palet: str, kode_yl: str) -> str | None:
    if _yl_spek_used(cur, kode_palet, kode_yl):
        return "YL sudah dipakai proses atau punya riwayat movement. Tidak bisa dihapus."
    cur.execute(
        "SELECT id FROM tbl_kulit_lebih WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
        (kode_palet, kode_yl),
    )
    if cur.fetchone():
        return "YL sudah tercatat sebagai kulit lebih. Tidak bisa dihapus."
    return None


def _yl_body_pair(body):
    kode_palet = (body.get("kode_palet") or "").strip()
    kode_yl = (body.get("kode_yl") or "").strip()
    if not kode_palet or not kode_yl:
        return None, None, "kode_palet dan kode_yl wajib"
    return kode_palet, kode_yl, None


@api.put("/palet/yl")
def palet_yl_update():
    body = request.get_json(silent=True) or {}
    kode_palet, kode_yl, err = _yl_body_pair(body)
    if err:
        return _err(err)
    thickness = (body.get("thickness") or "").strip()
    warna = (body.get("warna") or "").strip()
    try:
        qty = round(float(body.get("qty")), 3)
    except (TypeError, ValueError):
        return _err("qty harus angka")
    if qty <= 0:
        return _err("qty harus > 0")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    from app import ensure_extended_tables
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT * FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1 FOR UPDATE",
        (kode_palet, kode_yl),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return _err("YL tidak ditemukan di stok palet", 404)
    reserved = _yl_reserved_qty(cur, kode_palet, kode_yl)
    if qty + 1e-9 < reserved:
        cur.close()
        conn.close()
        return _err(f"Qty baru di bawah reservasi proses ({reserved})")
    spek_changed = (
        str(row.get("thickness") or "").strip() != thickness
        or str(row.get("warna") or "").strip() != warna
    )
    if spek_changed and _yl_spek_used(cur, kode_palet, kode_yl):
        cur.close()
        conn.close()
        return _err("Tebal dan warna terkunci karena YL sudah dipakai proses atau punya riwayat movement")
    cur.execute(
        "UPDATE tbl_yl SET thickness=%s, warna=%s, qty=%s WHERE id=%s",
        (thickness or None, warna or None, qty, row["id"]),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "kode_palet": kode_palet, "kode_yl": kode_yl, "qty": qty})


@api.delete("/palet/yl")
def palet_yl_delete():
    body = request.get_json(silent=True) or {}
    kode_palet, kode_yl, err = _yl_body_pair(body)
    if err:
        return _err(err)
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    from app import ensure_extended_tables
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT id FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1 FOR UPDATE",
        (kode_palet, kode_yl),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return _err("YL tidak ditemukan di stok palet", 404)
    reason = _yl_delete_block_reason(cur, kode_palet, kode_yl)
    if reason:
        cur.close()
        conn.close()
        return _err(reason)
    cur.execute("DELETE FROM tbl_yl WHERE id=%s", (row["id"],))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "kode_palet": kode_palet, "kode_yl": kode_yl, "deleted": True})


@api.get("/palet/<kode_palet>/yl")
def palet_yl(kode_palet):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM tbl_yl WHERE kode_palet = %s ORDER BY kode_yl",
        (kode_palet,),
    )
    rows = _rows(cur.fetchall())
    data = []
    for row in rows:
        stock = float(row.get("qty") or 0)
        available = _yl_available_qty(cur, kode_palet, row.get("kode_yl") or "")
        reserved = max(stock - available, 0.0)
        data.append({**row, "reserved_qty": reserved, "available_qty": available})
    cur.close()
    conn.close()
    return jsonify(data)


@api.get("/yl")
def yl_list():
    q = (request.args.get("q") or "").strip()
    kode_palet = (request.args.get("kode_palet") or "").strip()
    pg = parse_page_args(request.args, default_page_size=200)
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    where = " WHERE 1=1"
    params: list = []
    if kode_palet:
        where += " AND kode_palet=%s"
        params.append(kode_palet)
    if q:
        like = f"%{q}%"
        where += (
            " AND (kode_yl LIKE %s OR kode_palet LIKE %s OR IFNULL(warna,'') LIKE %s "
            "OR IFNULL(thickness,'') LIKE %s)"
        )
        params.extend([like, like, like, like])
    cur.execute(f"SELECT COUNT(*) AS c FROM tbl_yl{where}", params)
    total = int((cur.fetchone() or {}).get("c") or 0)
    order = order_sql(
        {
            "kode_yl": "kode_yl",
            "kode_palet": "kode_palet",
            "thickness": "thickness",
            "warna": "warna",
            "qty": "qty",
            "created_at": "created_at",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="kode_palet ASC, kode_yl ASC",
    )
    sql = (
        f"SELECT kode_yl, kode_palet, thickness, warna, qty, created_at FROM tbl_yl{where}"
        f" ORDER BY {order} LIMIT %s OFFSET %s"
    )
    cur.execute(sql, params + [pg["page_size"], pg["offset"]])
    data = _rows(cur.fetchall())
    for row in data:
        palet = row.get("kode_palet") or ""
        yl_code = row.get("kode_yl") or ""
        stock = float(row.get("qty") or 0)
        available = _yl_available_qty(cur, palet, yl_code)
        row["reserved_qty"] = round(max(stock - available, 0.0), 3)
        row["spek_locked"] = _yl_spek_used(cur, palet, yl_code)
    cur.close()
    conn.close()
    return jsonify(
        page_payload(
            items=data,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


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


@api.get("/masters/erp/page")
def master_erp_page():
    """Pagination Master Item ERP untuk UI Vue MRP."""
    from erp_master_items import fetch_master_items_page, item_to_erp_shape, master_item_stats

    pg = parse_page_args(request.args, default_page_size=50)
    keyword = (request.args.get("keyword") or "").strip() or None
    category = (request.args.get("category") or "").strip() or None
    rows, total = fetch_master_items_page(
        limit=pg["page_size"],
        offset=pg["offset"],
        keyword=keyword,
        category=category,
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
    )
    payload = page_payload(
        items=[item_to_erp_shape(r) for r in rows],
        total=total,
        page=pg["page"],
        page_size=pg["page_size"],
        offset=pg["offset"],
    )
    payload["stats"] = master_item_stats()
    return jsonify(payload)


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




def _normalize_kulit_leather_type(raw: str | None) -> str | None:
    s = (raw or "").strip().upper()
    if not s:
        return None
    if s in ("SUIDE", "SUEDE"):
        return "SUEDE"
    if s == "PU":
        return "PU"
    return None


def _kulit_row_out(row: dict) -> dict:
    lt = _normalize_kulit_leather_type(row.get("leather_type") or row.get("type"))
    return {
        "id": row.get("id"),
        "erp_material_id": row.get("id"),
        "kode_kulit": row.get("code") or row.get("kode_kulit"),
        "nama_kulit": row.get("name") or row.get("nama_kulit"),
        "satuan": row.get("unit") or row.get("satuan"),
        "type": lt,
        "leather_type": lt,
        "thickness": row.get("thickness"),
        "color": row.get("color"),
        "warna": row.get("color") or row.get("warna"),
        "source": "raw_materials",
    }


def _parse_kulit_write_body(body: dict) -> tuple[dict, str | None]:
    body = body or {}
    code = (body.get("kode_kulit") or body.get("code") or "").strip()
    name = (body.get("nama_kulit") or body.get("name") or "").strip()
    if not code:
        return {}, "Kode kulit wajib"
    if not name:
        return {}, "Nama kulit wajib"
    unit = (body.get("satuan") or body.get("unit") or "sqft").strip() or "sqft"
    thickness = (body.get("thickness") or "").strip() or None
    color = (body.get("color") or body.get("warna") or "").strip() or None
    leather_type = _normalize_kulit_leather_type(
        body.get("type") or body.get("leather_type") or body.get("kulit_type")
    )
    if not leather_type:
        return {}, "Type kulit wajib (PU atau SUEDE)"
    payload = {
        "code": code,
        "name": name,
        "material_type": "kulit",
        "unit": unit,
        "thickness": thickness,
        "color": color,
        "leather_type": leather_type,
        "min_stock": None,
        "cost_price": None,
    }
    return payload, None


def _erp_kulit_material(material_id: int):
    from erp_raw_materials import fetch_material, normalize_material_type

    row = fetch_material(int(material_id))
    if not row:
        return None, "Material kulit tidak ditemukan"
    if normalize_material_type(row.get("material_type")) != "kulit":
        return None, "Bukan material tipe kulit"
    return row, None


@api.get("/masters/kulit")
def master_kulit_list():
    from erp_raw_materials import list_materials

    pg = parse_page_args(request.args, default_page_size=50)
    rows = list_materials("kulit")
    out = [_kulit_row_out(r) for r in rows]
    out = sort_rows(
        out,
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        fields={
            "kode_kulit": "kode_kulit",
            "nama_kulit": "nama_kulit",
            "type": "type",
            "id": "id",
            "code": "kode_kulit",
        },
    )
    page_items, total = slice_page(out, page=pg["page"], page_size=pg["page_size"], offset=pg["offset"])
    return jsonify(
        page_payload(
            items=page_items,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


@api.post("/masters/kulit")
def master_kulit_create():
    from mrp_api import erp_client

    body = request.get_json(silent=True) or {}
    payload, err = _parse_kulit_write_body(body)
    if err:
        return _err(err)
    payload["is_active"] = True
    try:
        row = erp_client.create_material(payload)
    except erp_client.ErpApiError as exc:
        code = exc.status_code or 502
        if code == 409:
            return _err("Kode kulit sudah ada", 409)
        return _err(str(exc), code if 400 <= code < 600 else 400)
    return jsonify(_kulit_row_out(row)), 201


@api.get("/masters/kimia")
def master_kimia_list():
    from erp_raw_materials import list_materials, material_ukuran

    pg = parse_page_args(request.args, default_page_size=50)
    rows = list_materials("kimia")
    out = []
    for r in rows:
        ukuran = material_ukuran(r)
        out.append(
            {
                "id": r["id"],
                "erp_material_id": r["id"],
                "kode_kimia": r["code"],
                "kode_barang": r["code"],
                "nama_kimia": r["name"],
                "nama_barang": r["name"],
                "satuan": r.get("unit") or "kg",
                "size": ukuran or None,
                "ukuran": ukuran or None,
                "source": "raw_materials",
            }
        )
    out = sort_rows(
        out,
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        fields={
            "kode_kimia": "kode_kimia",
            "kode_barang": "kode_barang",
            "nama_kimia": "nama_kimia",
            "nama_barang": "nama_barang",
            "id": "id",
        },
    )
    page_items, total = slice_page(out, page=pg["page"], page_size=pg["page_size"], offset=pg["offset"])
    return jsonify(
        page_payload(
            items=page_items,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


@api.get("/masters/kimia/<int:kimia_id>")
def master_kimia_get(kimia_id: int):
    from erp_raw_materials import material_ukuran, resolve_material

    mat = resolve_material(erp_material_id=kimia_id, material_type="kimia")
    if not mat:
        return _err("Material kimia tidak ditemukan", 404)
    ukuran = material_ukuran(mat)
    return jsonify(
        {
            "id": mat["id"],
            "erp_material_id": mat["id"],
            "kode_kimia": mat.get("code"),
            "kode_barang": mat.get("code"),
            "nama_kimia": mat.get("name"),
            "nama_barang": mat.get("name"),
            "satuan": mat.get("unit") or "kg",
            "size": ukuran or None,
            "ukuran": ukuran or None,
            "source": "raw_materials",
        }
    )


@api.post("/masters/kimia")
def master_kimia_create():
    return _err(
        "Katalog kimia hanya di ERP Inventory (raw_materials). Tidak bisa create dari MRP.",
        403,
    )


@api.get("/masters/rp")
def master_rp_list():
    from erp_raw_materials import list_materials

    pg = parse_page_args(request.args, default_page_size=50)
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
    out = sort_rows(
        out,
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        fields={"kode_rp": "kode_rp", "nama_rp": "nama_rp", "nama_jenis": "nama_jenis", "id": "id"},
    )
    page_items, total = slice_page(out, page=pg["page"], page_size=pg["page_size"], offset=pg["offset"])
    return jsonify(
        page_payload(
            items=page_items,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


@api.post("/masters/rp")
def master_rp_create():
    return _err(
        "Katalog RP hanya di ERP Inventory (raw_materials). Tidak bisa create dari MRP.",
        403,
    )


@api.get("/masters/treatment")
def master_treatment_list():
    from app import ensure_master_treatment

    pg = parse_page_args(request.args, default_page_size=50)
    order = order_sql(
        {
            "jenis": "jenis",
            "nama_treatment": "nama_treatment",
            "created_at": "created_at",
            "id": "id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="jenis, nama_treatment, id",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_master_treatment(cur)
    conn.commit()
    cur.execute(
        "SELECT COUNT(*) AS c FROM tbl_master_treatment WHERE COALESCE(is_active, 1)=1"
    )
    total = int((cur.fetchone() or {}).get("c") or 0)
    cur.execute(
        "SELECT * FROM tbl_master_treatment "
        "WHERE COALESCE(is_active, 1)=1 "
        f"ORDER BY {order} LIMIT %s OFFSET %s",
        (pg["page_size"], pg["offset"]),
    )
    data = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(
        page_payload(
            items=data,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


def _qty_wip_by_source_detail_ids(cur, source_ids: list[int]) -> dict[int, float]:
    """QTY WIP mentah = total ukuran persiapan (started/saved/completed).

    Caller mengurangi Stock WH agar mutual exclusive di outstanding.
    """
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


def _as_float_qty(value) -> float:
    try:
        return max(0.0, float(value or 0))
    except (TypeError, ValueError):
        return 0.0


def _assign_stock_wh_from_finished_packings(
    packings: list,
    packing_po_rows: list,
    alloc_rows: list,
    source_ids: list[int],
) -> dict[int, float]:
    """Stock WH packing finished per baris SO (source_detail_id).

    Utamakan packing.rencana_item_id → alokasi RPI (lot SO). packing_po.po_id
    sering salah karena lookup no_po ORDER BY id DESC (baris SO lain di PO yang sama).
    Qty belum dikurangi terkirim — itu dihitung di outstanding ERP.
    """
    wanted = {int(x) for x in source_ids if x is not None}
    if not wanted:
        return {}

    pos_by_packing: dict[int, list] = {}
    for pp in packing_po_rows or []:
        try:
            pid = int(pp.get("packing_id"))
        except (TypeError, ValueError):
            continue
        pos_by_packing.setdefault(pid, []).append(pp)

    allocs_by_item: dict[int, list] = {}
    allocs_by_wip: dict[str, list] = {}
    alloc_by_po_id: dict[int, dict] = {}
    for alloc in alloc_rows or []:
        sid = alloc.get("source_detail_id")
        try:
            sid_i = int(sid)
        except (TypeError, ValueError):
            continue
        if sid_i not in wanted:
            continue
        try:
            item_id = int(alloc.get("item_id"))
        except (TypeError, ValueError):
            continue
        allocs_by_item.setdefault(item_id, []).append(alloc)
        wip = str(alloc.get("kode_lot_wip") or alloc.get("prep_kode_wip") or "").strip()
        if wip:
            allocs_by_wip.setdefault(wip, []).append(alloc)
        try:
            po_id = int(alloc.get("po_id"))
        except (TypeError, ValueError):
            po_id = None
        if po_id is not None:
            alloc_by_po_id[po_id] = alloc

    out: dict[int, float] = {}

    def _add(sid: int, qty: float) -> None:
        if sid not in wanted or qty <= 0:
            return
        out[sid] = out.get(sid, 0.0) + qty

    def _unique_sids(allocs: list) -> list[int]:
        seen: list[int] = []
        for alloc in allocs:
            try:
                sid = int(alloc.get("source_detail_id"))
            except (TypeError, ValueError):
                continue
            if sid in wanted and sid not in seen:
                seen.append(sid)
        return seen

    for packing in packings or []:
        qty = _as_float_qty(packing.get("total_ukuran"))
        if qty <= 0:
            continue
        try:
            packing_id = int(packing.get("id"))
        except (TypeError, ValueError):
            packing_id = None
        chosen: list = []
        try:
            item_id = int(packing.get("rencana_item_id"))
        except (TypeError, ValueError):
            item_id = None
        if item_id is not None:
            chosen = allocs_by_item.get(item_id, [])
        if not chosen:
            wip = str(packing.get("kode_wip") or "").strip()
            if wip:
                chosen = allocs_by_wip.get(wip, [])
        sids = _unique_sids(chosen)
        if len(sids) == 1:
            _add(sids[0], qty)
            continue
        assigned = False
        for pp in pos_by_packing.get(packing_id, []) if packing_id is not None else []:
            try:
                po_id = int(pp.get("po_id"))
            except (TypeError, ValueError):
                continue
            alloc = alloc_by_po_id.get(po_id)
            if not alloc:
                continue
            try:
                sid = int(alloc.get("source_detail_id"))
            except (TypeError, ValueError):
                continue
            split_qty = _as_float_qty(pp.get("qty_sq")) or qty
            _add(sid, split_qty)
            assigned = True
        if assigned or item_id is not None:
            continue

    return out


def _stock_wh_by_source_detail_ids(cur, source_ids: list[int]) -> dict[int, float]:
    """Stock WH = qty packing finished/in_progress (sudah diukur) per baris SO ERP."""
    if not source_ids:
        return {}
    from app import _col_names

    packing_cols = _col_names(cur, "tbl_packing")
    packing_fields = ["id", "kode_wip", "total_ukuran"]
    if "rencana_item_id" in packing_cols:
        packing_fields.insert(1, "rencana_item_id")
    cur.execute(
        f"SELECT {', '.join(packing_fields)} FROM tbl_packing "
        "WHERE status IN ('finished','in_progress') AND COALESCE(total_ukuran,0) > 0"
    )
    packings = list(cur.fetchall() or [])
    if not packings:
        return {}
    packing_ids = [int(p["id"]) for p in packings if p.get("id") is not None]
    packing_po_rows: list = []
    if packing_ids:
        pp_ph = ",".join(["%s"] * len(packing_ids))
        cur.execute(
            f"SELECT packing_id, po_id, no_po, no_so, qty_sq "
            f"FROM tbl_packing_po WHERE packing_id IN ({pp_ph})",
            packing_ids,
        )
        packing_po_rows = list(cur.fetchall() or [])
    placeholders = ",".join(["%s"] * len(source_ids))
    cur.execute(
        f"SELECT rip.item_id, rip.po_id, po.source_detail_id, po.lot_number, po.no_so, "
        f"i.kode_lot_wip, pk.kode_wip AS prep_kode_wip "
        f"FROM tbl_rencana_item_po rip "
        f"JOIN tbl_master_po po ON po.id = rip.po_id "
        f"JOIN tbl_rencana_item i ON i.id = rip.item_id "
        f"LEFT JOIN tbl_persiapan_kulit pk ON pk.rencana_item_id = i.id "
        f"WHERE po.source_detail_id IN ({placeholders})",
        source_ids,
    )
    alloc_rows = list(cur.fetchall() or [])
    return _assign_stock_wh_from_finished_packings(
        packings, packing_po_rows, alloc_rows, source_ids
    )


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
            # Mutual exclusive: WIP kosong jika sudah masuk Stock WH.
            wip_raw = wip_map.get(sid_i, 0.0)
            wh = stock_map.get(sid_i, 0.0)
            row["stock_wh_qty"] = wh
            row["qty_wip"] = max(0.0, float(wip_raw) - float(wh))
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
                "UPDATE tbl_master_po SET no_po=%s, no_so=%s, customer=%s, customer_id=%s, item_name=%s, "
                "warna=%s, tebal=%s, emboss=%s, color_swatch=%s, source_detail_id=%s, lot_number=%s, sq_ft=%s, "
                "qty_order=%s, qty_balance_erp=%s, status=%s WHERE id=%s",
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


@api.post("/sync/po")
def sync_po_from_erp():
    """Minta ERP push ulang SO → MRP (reconcile/retry). Tidak ada pull SQL.

    UI MRP memanggil endpoint ini; MRP meneruskan ke ERP POST /api/v1/mrp/sync/po
    (service token), lalu ERP yang push ke /api/mrp/masters/po/sync.
    """
    body = request.get_json(silent=True) or {}
    po_id = None
    if body.get("po_id") is not None and str(body.get("po_id")).strip() != "":
        try:
            po_id = int(body["po_id"])
        except (TypeError, ValueError):
            return _err("po_id tidak valid")
    try:
        from mrp_api import erp_client

        data = erp_client.request_po_sync(po_id=po_id)
    except Exception as exc:
        status = getattr(exc, "status_code", None) or 502
        return _err(f"ERP sync PO gagal: {exc}", int(status) if int(status) >= 400 else 502)
    if not isinstance(data, dict):
        data = {"ok": True, "raw": data}
    data.setdefault("ok", True)
    data["via"] = "erp_push"
    return jsonify(data)


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

    pg = parse_page_args(request.args, default_page_size=20)
    page, page_size, offset = pg["page"], pg["page_size"], pg["offset"]
    order = order_sql(
        {
            "tanggal_rencana": "COALESCE(r.tanggal_rencana, r.date_created)",
            "tanggal": "COALESCE(r.tanggal_rencana, r.date_created)",
            "kode_rencana": "r.kode_rencana",
            "status": "r.status",
            "date_created": "r.date_created",
            "id": "r.id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="COALESCE(r.tanggal_rencana, r.date_created) DESC, r.id DESC",
    )

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    conn.commit()
    cur.execute("SELECT COUNT(*) AS c FROM tbl_rencana_produksi")
    total = int((cur.fetchone() or {}).get("c") or 0)

    cur.execute(
        "SELECT r.id, r.kode_rencana, r.nama_rencana, r.tanggal_rencana, r.date_created, r.status "
        "FROM tbl_rencana_produksi r "
        f"ORDER BY {order} "
        "LIMIT %s OFFSET %s",
        (page_size, offset),
    )
    headers = _rows(cur.fetchall())
    if not headers:
        cur.close()
        conn.close()
        return jsonify(page_payload(items=[], total=total, page=page, page_size=page_size, offset=offset))

    ids = [int(r["id"]) for r in headers if r.get("id") is not None]
    placeholders = ",".join(["%s"] * len(ids))
    cur.execute(
        f"SELECT i.rencana_id, "
        f"  COUNT(DISTINCT i.id) AS jml_item, "
        f"  COUNT(p.id) AS jml_po, "
        f"  COALESCE(SUM(p.qty_proses), 0) AS total_qty_alokasi, "
        f"  GROUP_CONCAT(DISTINCT NULLIF(i.nama_customer, '') ORDER BY i.nama_customer SEPARATOR ', ') AS customers, "
        f"  GROUP_CONCAT(DISTINCT po.no_po ORDER BY po.no_po SEPARATOR ', ') AS po_numbers "
        f"FROM tbl_rencana_item i "
        f"LEFT JOIN tbl_rencana_item_po p ON p.item_id = i.id "
        f"LEFT JOIN tbl_master_po po ON po.id = p.po_id "
        f"WHERE i.rencana_id IN ({placeholders}) "
        f"GROUP BY i.rencana_id",
        tuple(ids),
    )
    agg_by_id = {int(r["rencana_id"]): r for r in _rows(cur.fetchall()) if r.get("rencana_id") is not None}
    data = []
    for row in headers:
        rid = int(row["id"])
        agg = agg_by_id.get(rid) or {}
        data.append(
            {
                **row,
                "jml_item": int(agg.get("jml_item") or 0),
                "jml_po": int(agg.get("jml_po") or 0),
                "total_qty_alokasi": float(agg.get("total_qty_alokasi") or 0),
                "customers": agg.get("customers"),
                "po_numbers": agg.get("po_numbers"),
            }
        )
    cur.close()
    conn.close()
    return jsonify(page_payload(items=data, total=total, page=page, page_size=page_size, offset=offset))


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
        relinked = 0
        for rows in allocations_by_item.values():
            _hydrate_master_po_rows_from_erp(rows)
            relinked += _relink_rencana_allocations_by_erp_lot(cur, rows)
        if relinked:
            conn.commit()
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


def _rencana_spek_key(material_name, color, emboss, thickness) -> tuple[str, str, str, str]:
    return (
        (material_name or "").strip().lower(),
        (color or "").strip().lower(),
        (emboss or "").strip().lower(),
        (thickness or "").strip().lower(),
    )


def _merge_rencana_po_entries(entries: list) -> list[dict]:
    """Gabung alokasi PO; qty untuk po_id sama dijumlahkan."""
    merged: dict[int, float] = {}
    for entry in entries or []:
        try:
            po_id = int(entry.get("po_id"))
        except (TypeError, ValueError):
            continue
        try:
            qty = float(entry.get("qty") or 0)
        except (TypeError, ValueError):
            continue
        if po_id <= 0 or qty <= 0:
            continue
        merged[po_id] = merged.get(po_id, 0.0) + qty
    return [{"po_id": pid, "qty": qty} for pid, qty in merged.items()]


def _merge_rencana_customers(names: list[str]) -> str:
    seen: set[str] = set()
    ordered: list[str] = []
    for raw in names:
        for part in str(raw or "").replace(";", ",").split(","):
            name = part.strip()
            if not name:
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            ordered.append(name)
    return ", ".join(ordered) if ordered else "-"


def _group_rencana_create_items(raw_items: list) -> list[dict]:
    """Satu RPI per kombinasi material + warna + emboss + tebal (urutan kemunculan pertama)."""
    groups: dict[tuple[str, str, str, str], dict] = {}
    order: list[tuple[str, str, str, str]] = []
    for item in raw_items or []:
        material_name = (item.get("material_name") or "").strip()
        color = (item.get("color") or "").strip()
        emboss = (item.get("emboss") or "").strip()
        thickness = (item.get("thickness") or "").strip()
        customer_name = (item.get("customer") or item.get("customer_name") or "").strip()
        if not all([thickness, material_name, color, emboss]):
            continue
        key = _rencana_spek_key(material_name, color, emboss, thickness)
        if key not in groups:
            groups[key] = {
                "material_name": material_name,
                "color": color,
                "emboss": emboss,
                "thickness": thickness,
                "color_swatch": (item.get("color_swatch") or "").strip() or None,
                "backer": (item.get("backer") or "").strip() or None,
                "keterangan": (item.get("keterangan") or "").strip() or None,
                "pos": [],
                "_customers": [],
            }
            order.append(key)
        bucket = groups[key]
        if customer_name:
            bucket["_customers"].append(customer_name)
        if not bucket.get("color_swatch") and (item.get("color_swatch") or "").strip():
            bucket["color_swatch"] = (item.get("color_swatch") or "").strip()
        if not bucket.get("backer") and (item.get("backer") or "").strip():
            bucket["backer"] = (item.get("backer") or "").strip()
        ket = (item.get("keterangan") or "").strip()
        if ket:
            prev = (bucket.get("keterangan") or "").strip()
            bucket["keterangan"] = ket if not prev else f"{prev}; {ket}"
        if item.get("po_id") is not None:
            bucket["pos"].append({"po_id": item.get("po_id"), "qty": item.get("qty")})
        bucket["pos"].extend(item.get("pos") or [])

    out: list[dict] = []
    for key in order:
        g = groups[key]
        g["customer"] = _merge_rencana_customers(g.pop("_customers", []))
        g["pos"] = _merge_rencana_po_entries(g["pos"])
        out.append(g)
    return out


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

        grouped = _group_rencana_create_items(resolved)
        if not grouped:
            cur.close()
            conn.close()
            return _err("Tidak ada item valid setelah penggabungan spek")

        kode_rencana = generate_code("RP")
        cur.execute(
            "INSERT INTO tbl_rencana_produksi "
            "(kode_rencana, kode_lot_wip, nama_rencana, tanggal_rencana, status) "
            "VALUES (%s, NULL, %s, %s, 'draft')",
            (kode_rencana, nama, tanggal),
        )
        rencana_id = cur.lastrowid
        for idx, item in enumerate(grouped, 1):
            from erp_master_items import lookup_backer

            backer = item.get("backer") or lookup_backer(
                material_name=item["material_name"],
                thickness=item["thickness"],
                color=item["color"],
                emboss=item.get("emboss"),
            )
            customer_nama = item.get("customer") or "-"
            customer_primary = customer_nama.split(",")[0].strip() or customer_nama
            customer_id = _ensure_customer_id(cur, customer_primary)
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
                    item.get("color_swatch"),
                    backer,
                    item.get("keterangan"),
                    idx,
                ),
            )
            item_id = cur.lastrowid
            try:
                _save_item_po_selections(cur, item_id, item.get("pos") or [])
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
                "items_created": len(grouped),
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
    grouped_items = _group_rencana_create_items(items)
    saved = 0
    for idx, item in enumerate(grouped_items, 1):
        customer_nama = (item.get("customer") or "").strip()
        if not customer_nama:
            continue
        from erp_master_items import lookup_backer

        backer = item.get("backer") or lookup_backer(
            material_name=item["material_name"],
            thickness=item["thickness"],
            color=item["color"],
            emboss=item["emboss"],
        )
        customer_primary = customer_nama.split(",")[0].strip() or customer_nama
        customer_id = _ensure_customer_id(cur, customer_primary)
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
                item.get("color_swatch"),
                backer,
                item.get("keterangan"),
                idx,
            ),
        )
        item_id = cur.lastrowid
        pos = item.get("pos") or []
        if pos:
            try:
                _save_item_po_selections(cur, item_id, pos)
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
            "Tidak ada item valid. Lengkapi Thickness, Material, Color, Emboss, dan Customer."
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
        color_swatch = (item.get("color_swatch") or "").strip() or None
        if not all([thickness, material_name, color, emboss, customer_name]):
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
            "Tidak ada item valid. Lengkapi Thickness, Material, Color, Emboss, dan Customer."
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
            "SELECT id FROM tbl_master_treatment WHERE nama_treatment=%s LIMIT 1",
            (nama,),
        )
        existing = cur.fetchone()
        if existing:
            cur.execute(
                "UPDATE tbl_master_treatment SET jenis=%s, is_active=1 WHERE id=%s",
                (jenis, existing["id"]),
            )
            new_id = existing["id"]
        else:
            cur.execute(
                "INSERT INTO tbl_master_treatment (jenis, nama_treatment, is_active) VALUES (%s, %s, 1)",
                (jenis, nama),
            )
            new_id = cur.lastrowid
        conn.commit()
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
            "UPDATE tbl_master_treatment SET jenis=%s, nama_treatment=%s, is_active=1 WHERE id=%s",
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
    from app import ensure_master_treatment

    conn = get_db_connection()
    cur = conn.cursor()
    ensure_master_treatment(cur)
    # Soft-delete: proses/checkpoint hanya menampilkan treatment aktif.
    cur.execute(
        "UPDATE tbl_master_treatment SET is_active=0 WHERE id=%s",
        (treatment_id,),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True})


# ---- proses / persiapan kulit ----
def _yl_stock_qty(cur, kode_palet: str, kode_yl: str) -> float:
    cur.execute(
        "SELECT qty FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
        (kode_palet, kode_yl),
    )
    row = cur.fetchone()
    return float((row or {}).get("qty") or 0)


def _yl_reserved_qty(cur, kode_palet: str, kode_yl: str, *, exclude_ky_id=None) -> float:
    """Jumlah target KY planned/active yang belum consume (reservasi soft)."""
    sql = (
        "SELECT COALESCE(SUM(target_qty),0) AS reserved "
        "FROM tbl_persiapan_ky "
        "WHERE kode_palet=%s AND kode_yl=%s AND status IN ('planned','active') "
        "AND COALESCE(yl_consumed,0)=0"
    )
    params: list = [kode_palet, kode_yl]
    if exclude_ky_id:
        sql += " AND id<>%s"
        params.append(int(exclude_ky_id))
    cur.execute(sql, params)
    return float((cur.fetchone() or {}).get("reserved") or 0)


def _yl_available_qty(cur, kode_palet: str, kode_yl: str, *, exclude_ky_id=None) -> float:
    stock = _yl_stock_qty(cur, kode_palet, kode_yl)
    reserved = _yl_reserved_qty(cur, kode_palet, kode_yl, exclude_ky_id=exclude_ky_id)
    avail = stock - reserved
    return avail if avail > 0 else 0.0


def _persiapan_has_ky_yl(cur, persiapan_id: int, kode_palet: str, kode_yl: str) -> bool:
    cur.execute(
        "SELECT id FROM tbl_persiapan_ky "
        "WHERE persiapan_id=%s AND kode_palet=%s AND kode_yl=%s LIMIT 1",
        (persiapan_id, kode_palet, kode_yl),
    )
    return cur.fetchone() is not None


def _gudang_mod_take_for_proses(cur, mod_id: int, persiapan_id: int) -> dict:
    cur.execute("SELECT * FROM tbl_gudang_mod WHERE id=%s FOR UPDATE", (int(mod_id),))
    mod = cur.fetchone()
    if not mod:
        raise ValueError("Barang MOD tidak ditemukan")
    status = (mod.get("status") or "in_stock").strip().lower()
    if status != "in_stock":
        raise ValueError(f"MOD {mod.get('kode_mod')} sudah OUT / tidak tersedia")
    cur.execute(
        "UPDATE tbl_gudang_mod SET status='out', consumed_persiapan_id=%s, date_out=NOW() "
        "WHERE id=%s",
        (persiapan_id, int(mod_id)),
    )
    return mod


def _insert_proses_ky_lines(cur, persiapan_id: int, ky_lines):
    if not ky_lines:
        return None
    if not isinstance(ky_lines, list):
        return _err("ky_lines harus berupa array")
    seen_yl = set()
    seen_mod = set()
    for line in ky_lines:
        gudang_mod_id = line.get("gudang_mod_id")
        try:
            target_qty = float(
                line.get("target_qty") if line.get("target_qty") is not None else line.get("qty") or 0
            )
        except (TypeError, ValueError):
            return _err("Qty KY harus angka")
        if target_qty <= 0:
            return _err("Qty KY harus > 0")
        tidak_ada_sisa = 1 if line.get("tidak_ada_sisa") in (True, 1, "1", "true", "True") else 0

        if gudang_mod_id:
            try:
                mod_id = int(gudang_mod_id)
            except (TypeError, ValueError):
                return _err("gudang_mod_id tidak valid")
            if mod_id in seen_mod:
                return _err("MOD duplikat pada daftar proses")
            seen_mod.add(mod_id)
            cur.execute(
                "SELECT 1 FROM tbl_persiapan_ky WHERE persiapan_id=%s AND gudang_mod_id=%s LIMIT 1",
                (persiapan_id, mod_id),
            )
            if cur.fetchone():
                return _err("MOD sudah dipakai di proses ini")
            try:
                mod = _gudang_mod_take_for_proses(cur, mod_id, persiapan_id)
            except ValueError as exc:
                return _err(str(exc))
            kode_palet = (mod.get("kode_palet") or "").strip()
            kode_yl = (mod.get("kode_yl") or "").strip()
            mod_sf = float(mod.get("reject_qty") or 0)
            if not kode_palet or not kode_yl:
                return _err("Data MOD tidak lengkap (KY/YL)")
            if abs(target_qty - mod_sf) > 1e-9:
                return _err(
                    f"Qty proses MOD {mod.get('kode_mod')} harus {mod_sf:.2f} SF (sesuai stok MOD)"
                )
            cur.execute(
                "INSERT INTO tbl_persiapan_ky "
                "(persiapan_id, kode_palet, kode_yl, target_qty, status, tidak_ada_sisa, gudang_mod_id) "
                "VALUES (%s,%s,%s,%s,'planned',%s,%s)",
                (persiapan_id, kode_palet, kode_yl, target_qty, tidak_ada_sisa, mod_id),
            )
            continue

        kode_palet = (line.get("kode_palet") or "").strip()
        kode_yl = (line.get("kode_yl") or "").strip()
        if not kode_palet or not kode_yl:
            return _err("Kode KY/palet dan YL wajib diisi")
        key = (kode_palet, kode_yl)
        if key in seen_yl or _persiapan_has_ky_yl(cur, persiapan_id, kode_palet, kode_yl):
            return _err(
                f"YL {kode_yl} di palet {kode_palet} sudah ada di proses ini. "
                "Pilih YL lain atau selesaikan yang sudah ada."
            )
        seen_yl.add(key)
        avail = _yl_available_qty(cur, kode_palet, kode_yl)
        if avail <= 0:
            stock = _yl_stock_qty(cur, kode_palet, kode_yl)
            if stock <= 0:
                return _err(f"Stok YL {kode_yl} kosong di palet {kode_palet}.")
            return _err(
                f"YL {kode_yl} di palet {kode_palet} sudah dialokasikan proses lain "
                f"(stok {stock}, tersedia {avail})."
            )
        if target_qty > avail + 1e-9:
            return _err(
                f"Qty KY {kode_yl} melebihi stok tersedia ({avail})."
            )
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


def _find_rencana_items_by_scan(cur, kode: str):
    """Cari item rencana by RPI, WIP lot, atau kode RP (status draft/active)."""
    cur.execute(
        "SELECT i.id, i.kode_rencana_item, i.kode_lot_wip, i.kode_kulit, i.material_name, "
        "i.thickness, i.color, i.emboss, i.color_swatch, r.kode_rencana, r.nama_rencana, "
        "r.tanggal_rencana, i.nama_customer "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        "WHERE r.status IN ('draft','active') AND ("
        "  i.kode_rencana_item = %s OR i.kode_lot_wip = %s OR r.kode_rencana = %s"
        ") ORDER BY i.urutan, i.id",
        (kode, kode, kode),
    )
    return cur.fetchall() or []


@api.get("/proses/rencana-search")
def proses_rencana_search():
    """Autocomplete RPI / RP / WIP untuk form buat proses."""
    q = (request.args.get("q") or "").strip()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    base_sql = (
        "SELECT i.id, i.kode_rencana_item, i.kode_lot_wip, r.kode_rencana, r.nama_rencana, "
        "r.tanggal_rencana "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        "WHERE r.status IN ('draft','active') "
    )
    if not q:
        cur.execute(base_sql + "ORDER BY r.date_created DESC, i.urutan, i.id LIMIT 50")
    else:
        like = f"%{q}%"
        cur.execute(
            base_sql
            + "AND (i.kode_rencana_item LIKE %s OR i.kode_lot_wip LIKE %s OR "
            "r.kode_rencana LIKE %s OR r.nama_rencana LIKE %s) "
            "ORDER BY i.kode_rencana_item, i.id LIMIT 30",
            (like, like, like, like),
        )
    items = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify({"items": items})


@api.get("/proses/scan-rencana")
def proses_scan_rencana():
    kode = (request.args.get("q") or "").strip()
    if not kode:
        return _err("Kode kosong")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    matches = _find_rencana_items_by_scan(cur, kode)
    if not matches:
        cur.close()
        conn.close()
        return _err("Rencana produksi tidak ditemukan", 404)
    if len(matches) > 1:
        cur.close()
        conn.close()
        return _err(
            "Kode RP punya beberapa item. Scan RPI / WIP, atau pilih item di daftar.",
            400,
        )
    item = matches[0]
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

    pg = parse_page_args(request.args, default_page_size=20)
    order = order_sql(
        {
            "date_created": "pk.date_created",
            "kode_proses": "pk.kode_proses",
            "kode_wip": "pk.kode_wip",
            "status": "pk.status",
            "id": "pk.id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="pk.date_created DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_master_treatment(cur)
    conn.commit()
    cur.execute("SELECT COUNT(*) AS c FROM tbl_persiapan_kulit")
    total = int((cur.fetchone() or {}).get("c") or 0)
    cur.execute(
        f"SELECT pk.*, {_sql_no_so_from_master('pk')} "
        f"FROM tbl_persiapan_kulit pk ORDER BY {order} LIMIT %s OFFSET %s",
        (pg["page_size"], pg["offset"]),
    )
    persiapan_list = _rows(cur.fetchall())
    cur.execute(
        "SELECT i.id, i.kode_rencana_item, i.kode_lot_wip, i.material_name, i.kode_kulit, "
        "i.thickness, i.color, i.emboss, i.color_swatch, r.kode_rencana, r.nama_rencana, "
        "r.tanggal_rencana, i.nama_customer "
        "FROM tbl_rencana_item i "
        "JOIN tbl_rencana_produksi r ON r.id = i.rencana_id "
        "WHERE r.status IN ('draft','active') AND i.kode_lot_wip IS NOT NULL "
        "ORDER BY r.date_created DESC"
    )
    rencana_items = _rows(cur.fetchall())
    cur.execute(
        "SELECT jenis, nama_treatment FROM tbl_master_treatment "
        "WHERE COALESCE(is_active, 1)=1 ORDER BY jenis, nama_treatment"
    )
    treatments = _rows(cur.fetchall())
    cur.execute(
        "SELECT DISTINCT y.kode_palet FROM tbl_yl y "
        "WHERE COALESCE(y.qty,0) > 0 ORDER BY y.kode_palet"
    )
    palet_options = [r["kode_palet"] for r in cur.fetchall() if r.get("kode_palet")]
    cur.close()
    conn.close()
    payload = page_payload(
        items=persiapan_list,
        total=total,
        page=pg["page"],
        page_size=pg["page_size"],
        offset=pg["offset"],
    )
    payload.update(
        {
            "persiapan_list": persiapan_list,
            "rencana_items": rencana_items,
            "treatments": treatments,
            "palet_options": palet_options,
        }
    )
    return jsonify(payload)


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
        matches = _find_rencana_items_by_scan(cur, kode_scan)
        if len(matches) > 1:
            cur.close()
            conn.close()
            return _err(
                "Kode RP punya beberapa item. Scan RPI / WIP, atau pilih item di daftar.",
            )
        item_id = matches[0]["id"] if matches else None
    if not item_id:
        cur.close()
        conn.close()
        return _err("Ketik / scan kode RP, RPI, atau WIP terlebih dahulu.")
    if treatment_jenis not in ("PU", "Suede"):
        cur.close()
        conn.close()
        return _err("Pilih jenis PU atau Suede.")
    if not isinstance(ky_lines, list) or not ky_lines:
        cur.close()
        conn.close()
        return _err("Pilih minimal satu material KY sebelum menyimpan.")

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
    if po_count and not po_ids:
        cur.close()
        conn.close()
        return _err("Pilih minimal satu baris PO / qty untuk proses.")
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
        if not no_po:
            cur.close()
            conn.close()
            return _err("PO yang dipilih tidak valid untuk item rencana ini.")
    if len(no_po) > 500:
        cur.close()
        conn.close()
        return _err(
            "Gabungan nomor PO terlalu panjang (maks. 500 karakter). Kurangi jumlah baris PO yang dipilih."
        )
    treatment_list_str = ", ".join(selected)
    try:
        kode_proses = generate_code("PR")
        kode_wip = allocate_wip_persiapan_code(cur)
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
    except mysql.connector.Error as exc:
        conn.rollback()
        cur.close()
        conn.close()
        errno = getattr(exc, "errno", None)
        if errno == 1406:
            return _err(
                "Gabungan nomor PO terlalu panjang untuk kolom database. "
                "Kurangi PO yang dipilih atau minta admin menjalankan migrasi MRP terbaru."
            )
        if errno == 1205:
            return _err("Database sibuk (lock timeout). Tunggu sebentar lalu coba Simpan lagi.")
        return _err(f"Gagal menyimpan persiapan: {exc}", 500)
    cur.close()
    conn.close()
    return jsonify({"id": persiapan_id, "kode_proses": kode_proses, "kode_wip": kode_wip, "ok": True}), 201


def _returned_qty_for_ky(cur, ky_id: int) -> float:
    cur.execute(
        "SELECT COALESCE(SUM(return_qty),0) AS total FROM tbl_proses_return WHERE ky_id=%s",
        (ky_id,),
    )
    return float((cur.fetchone() or {}).get("total") or 0)


def _rejected_qty_for_ky(cur, ky_id: int) -> float:
    cur.execute(
        "SELECT COALESCE(SUM(reject_qty),0) AS total FROM tbl_gudang_mod WHERE ky_id=%s",
        (ky_id,),
    )
    return float((cur.fetchone() or {}).get("total") or 0)


def _ky_measured_actual(cur, persiapan_id: int, ky_id: int, actual_qty) -> float:
    actual = float(actual_qty or 0)
    if actual <= 0:
        cur.execute(
            "SELECT COALESCE(SUM(size_val),0) AS total FROM tbl_persiapan_ukur "
            "WHERE persiapan_id=%s AND ky_id=%s",
            (persiapan_id, ky_id),
        )
        actual = float((cur.fetchone() or {}).get("total") or 0)
    return actual


def _remaining_measurable_qty(cur, persiapan_id: int, ky_id: int, ky_row: dict) -> float:
    actual = _ky_measured_actual(cur, persiapan_id, int(ky_id), ky_row.get("actual_qty"))
    returned = _returned_qty_for_ky(cur, int(ky_id))
    rejected = _rejected_qty_for_ky(cur, int(ky_id))
    return round(actual - returned - rejected, 3)


def _ky_ukur_lembar_count(cur, persiapan_id: int, ky_id: int) -> int:
    cur.execute(
        "SELECT COUNT(*) AS c FROM tbl_persiapan_ukur "
        "WHERE persiapan_id=%s AND ky_id=%s",
        (persiapan_id, ky_id),
    )
    return int((cur.fetchone() or {}).get("c") or 0)


def _new_yl_return_code(kode_yl_lama: str) -> str:
    kode = (kode_yl_lama or "").strip()
    if kode.endswith("-R"):
        return kode
    return f"{kode}-R"


@api.get("/proses/return/lookup")
def proses_return_lookup():
    from app import ensure_extended_tables

    kode_wip = (request.args.get("wip") or request.args.get("kode_wip") or "").strip()
    if not kode_wip:
        return _err("Input WIP wajib")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        f"SELECT pk.*, {_sql_no_so_from_master('pk')} "
        "FROM tbl_persiapan_kulit pk WHERE pk.kode_wip=%s ORDER BY pk.id DESC LIMIT 1",
        (kode_wip,),
    )
    persiapan = cur.fetchone()
    if not persiapan:
        cur.close()
        conn.close()
        return _err(f"WIP {kode_wip} tidak ditemukan", 404)
    persiapan_id = int(persiapan["id"])
    cur.execute(
        "SELECT id, kode_palet, kode_yl, target_qty, actual_qty, status "
        "FROM tbl_persiapan_ky WHERE persiapan_id=%s ORDER BY id",
        (persiapan_id,),
    )
    lines = []
    for ky in cur.fetchall():
        ky_id = int(ky["id"])
        actual = _ky_measured_actual(cur, persiapan_id, ky_id, ky.get("actual_qty"))
        if actual <= 0:
            continue
        remaining = _remaining_measurable_qty(cur, persiapan_id, ky_id, ky)
        if remaining <= 1e-9:
            continue
        returned = _returned_qty_for_ky(cur, ky_id)
        lines.append(
            {
                "ky_id": ky_id,
                "kode_palet": ky.get("kode_palet"),
                "kode_yl": ky.get("kode_yl"),
                "measured_qty": actual,
                "returned_qty": returned,
                "return_qty": remaining,
                "kode_yl_baru": _new_yl_return_code(ky.get("kode_yl") or ""),
            }
        )
    cur.close()
    conn.close()
    if not lines:
        return _err("Tidak ada YL terukur yang bisa diretur untuk WIP ini", 400)
    return jsonify(
        {
            "persiapan": _row(persiapan),
            "lines": lines,
        }
    )


@api.get("/proses/return")
def proses_return_list():
    from app import ensure_extended_tables

    pg = parse_page_args(request.args, default_page_size=20)
    order = order_sql(
        {
            "date_created": "pr.created_at",
            "kode_wip": "pr.kode_wip",
            "kode_yl_lama": "pr.kode_yl_lama",
            "id": "pr.id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="pr.created_at DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT COUNT(*) AS c FROM tbl_proses_return")
    total = int((cur.fetchone() or {}).get("c") or 0)
    cur.execute(
        f"SELECT pr.*, pk.kode_proses, pk.treatment_jenis "
        f"FROM tbl_proses_return pr "
        f"LEFT JOIN tbl_persiapan_kulit pk ON pk.id = pr.persiapan_id "
        f"ORDER BY {order} LIMIT %s OFFSET %s",
        (pg["page_size"], pg["offset"]),
    )
    items = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(
        page_payload(
            items=items,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


@api.post("/proses/return")
def proses_return_create():
    from app import _return_yl_to_palet, ensure_extended_tables

    body = request.get_json(silent=True) or {}
    kode_wip = (body.get("kode_wip") or body.get("wip") or "").strip()
    lines = body.get("lines") or []
    if not kode_wip:
        return _err("Input WIP wajib")
    if not isinstance(lines, list) or not lines:
        return _err("Pilih minimal satu baris YL untuk diretur")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT * FROM tbl_persiapan_kulit WHERE kode_wip=%s ORDER BY id DESC LIMIT 1",
        (kode_wip,),
    )
    persiapan = cur.fetchone()
    if not persiapan:
        cur.close()
        conn.close()
        return _err(f"WIP {kode_wip} tidak ditemukan", 404)
    persiapan_id = int(persiapan["id"])
    treatment_list = (persiapan.get("treatment_list") or "").strip()
    created = []

    try:
        for line in lines:
            ky_id = line.get("ky_id")
            if not ky_id:
                cur.close()
                conn.close()
                return _err("ky_id wajib di setiap baris")
            try:
                return_qty = float(line.get("return_qty") or 0)
            except (TypeError, ValueError):
                cur.close()
                conn.close()
                return _err("Qty retur harus angka")
            if return_qty <= 0:
                continue
            cur.execute(
                "SELECT * FROM tbl_persiapan_ky WHERE id=%s AND persiapan_id=%s",
                (int(ky_id), persiapan_id),
            )
            ky = cur.fetchone()
            if not ky:
                cur.close()
                conn.close()
                return _err(f"Sesi KY #{ky_id} tidak valid untuk WIP ini", 400)
            remaining = _remaining_measurable_qty(cur, persiapan_id, int(ky_id), ky)
            if return_qty > remaining + 1e-9:
                cur.close()
                conn.close()
                return _err(
                    f"Qty retur YL {ky.get('kode_yl')} melebihi sisa ({remaining:.2f})"
                )
            kode_palet = (ky.get("kode_palet") or "").strip()
            kode_yl_lama = (ky.get("kode_yl") or "").strip()
            if not kode_palet or not kode_yl_lama:
                cur.close()
                conn.close()
                return _err("KY/ YL tidak lengkap pada sesi proses")
            kode_yl_baru = _new_yl_return_code(kode_yl_lama)
            cur.execute(
                "SELECT thickness, warna FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
                (kode_palet, kode_yl_lama),
            )
            old_yl_meta = cur.fetchone() or {}
            ret_thickness = (old_yl_meta.get("thickness") or "").strip()
            ret_warna = (old_yl_meta.get("warna") or "").strip()
            if not ret_thickness and not ret_warna:
                from app import _yl_spek_from_history

                ret_thickness, ret_warna = _yl_spek_from_history(cur, kode_palet, kode_yl_lama)
            wip_ref = f" — retur WIP {kode_wip}"
            _return_yl_to_palet(
                cur,
                kode_palet,
                kode_yl_baru,
                return_qty,
                keterangan=f"Retur proses dari {kode_yl_lama}{wip_ref}",
                thickness=ret_thickness or None,
                warna=ret_warna or None,
            )
            cur.execute(
                "INSERT INTO tbl_proses_return "
                "(persiapan_id, ky_id, kode_wip, kode_palet, kode_yl_lama, kode_yl_baru, "
                "return_qty, treatment_list) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    persiapan_id,
                    int(ky_id),
                    kode_wip,
                    kode_palet,
                    kode_yl_lama,
                    kode_yl_baru,
                    return_qty,
                    treatment_list or None,
                ),
            )
            created.append(
                {
                    "id": cur.lastrowid,
                    "kode_palet": kode_palet,
                    "kode_yl_lama": kode_yl_lama,
                    "kode_yl_baru": kode_yl_baru,
                    "return_qty": return_qty,
                }
            )
        if not created:
            conn.rollback()
            cur.close()
            conn.close()
            return _err("Qty retur harus > 0 pada minimal satu baris")
        conn.commit()
    except ValueError as exc:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(exc))
    except Exception as exc:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(exc) or "Gagal menyimpan retur")
    cur.close()
    conn.close()
    return jsonify({"ok": True, "items": created}), 201


@api.get("/proses/return/<int:return_id>/label")
def proses_return_label_api(return_id: int):
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_proses_return WHERE id=%s", (return_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return _err("Data retur tidak ditemukan", 404)
    cur.close()
    conn.close()
    return jsonify(
        {
            "return": _row(row),
            "title": "LABEL RETUR KULIT",
        }
    )


@api.get("/proses/reject/lookup")
def proses_reject_lookup():
    from app import ensure_extended_tables

    kode_wip = (request.args.get("wip") or request.args.get("kode_wip") or "").strip()
    if not kode_wip:
        return _err("Input WIP wajib")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        f"SELECT pk.*, {_sql_no_so_from_master('pk')} "
        "FROM tbl_persiapan_kulit pk WHERE pk.kode_wip=%s ORDER BY pk.id DESC LIMIT 1",
        (kode_wip,),
    )
    persiapan = cur.fetchone()
    if not persiapan:
        cur.close()
        conn.close()
        return _err(f"WIP {kode_wip} tidak ditemukan", 404)
    persiapan_id = int(persiapan["id"])
    cur.execute(
        "SELECT id, kode_palet, kode_yl, target_qty, actual_qty, status "
        "FROM tbl_persiapan_ky WHERE persiapan_id=%s ORDER BY id",
        (persiapan_id,),
    )
    lines = []
    for ky in cur.fetchall():
        ky_id = int(ky["id"])
        actual = _ky_measured_actual(cur, persiapan_id, ky_id, ky.get("actual_qty"))
        if actual <= 0:
            continue
        remaining = _remaining_measurable_qty(cur, persiapan_id, ky_id, ky)
        if remaining <= 1e-9:
            continue
        lembar = _ky_ukur_lembar_count(cur, persiapan_id, ky_id)
        lines.append(
            {
                "ky_id": ky_id,
                "kode_palet": ky.get("kode_palet"),
                "kode_yl": ky.get("kode_yl"),
                "reject_sf": remaining,
                "lembar_qty": lembar,
                "reject_qty": remaining,
            }
        )
    cur.close()
    conn.close()
    if not lines:
        return _err("Tidak ada YL terukur yang bisa direject untuk WIP ini", 400)
    return jsonify(
        {
            "persiapan": _row(persiapan),
            "lines": lines,
        }
    )


@api.post("/proses/reject")
def proses_reject_create():
    from app import ensure_extended_tables, generate_code

    body = request.get_json(silent=True) or {}
    kode_wip = (body.get("kode_wip") or body.get("wip") or "").strip()
    lines = body.get("lines") or []
    if not kode_wip:
        return _err("Input WIP wajib")
    if not isinstance(lines, list) or not lines:
        return _err("Pilih minimal satu baris YL untuk direject")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT * FROM tbl_persiapan_kulit WHERE kode_wip=%s ORDER BY id DESC LIMIT 1",
        (kode_wip,),
    )
    persiapan = cur.fetchone()
    if not persiapan:
        cur.close()
        conn.close()
        return _err(f"WIP {kode_wip} tidak ditemukan", 404)
    persiapan_id = int(persiapan["id"])
    treatment_list = (persiapan.get("treatment_list") or "").strip()
    created = []

    try:
        for line in lines:
            ky_id = line.get("ky_id")
            if not ky_id:
                cur.close()
                conn.close()
                return _err("ky_id wajib di setiap baris")
            cur.execute(
                "SELECT * FROM tbl_persiapan_ky WHERE id=%s AND persiapan_id=%s",
                (int(ky_id), persiapan_id),
            )
            ky = cur.fetchone()
            if not ky:
                cur.close()
                conn.close()
                return _err(f"Sesi KY #{ky_id} tidak valid untuk WIP ini", 400)
            remaining = _remaining_measurable_qty(cur, persiapan_id, int(ky_id), ky)
            if remaining <= 1e-9:
                continue
            reject_qty = remaining
            lembar_qty = _ky_ukur_lembar_count(cur, persiapan_id, int(ky_id))
            kode_palet = (ky.get("kode_palet") or "").strip()
            kode_yl = (ky.get("kode_yl") or "").strip()
            if not kode_palet or not kode_yl:
                cur.close()
                conn.close()
                return _err("KY/ YL tidak lengkap pada sesi proses")
            kode_mod = generate_code("MOD")
            cur.execute(
                "INSERT INTO tbl_gudang_mod "
                "(kode_mod, persiapan_id, ky_id, kode_wip, kode_palet, kode_yl, "
                "reject_qty, reject_lembar, treatment_list, status) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'in_stock')",
                (
                    kode_mod,
                    persiapan_id,
                    int(ky_id),
                    kode_wip,
                    kode_palet,
                    kode_yl,
                    reject_qty,
                    lembar_qty,
                    treatment_list or None,
                ),
            )
            created.append(
                {
                    "id": cur.lastrowid,
                    "kode_mod": kode_mod,
                    "kode_palet": kode_palet,
                    "kode_yl": kode_yl,
                    "reject_qty": reject_qty,
                    "reject_lembar": lembar_qty,
                }
            )
        if not created:
            conn.rollback()
            cur.close()
            conn.close()
            return _err("Tidak ada YL terukur yang bisa direject")
        conn.commit()
    except Exception as exc:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(exc) or "Gagal menyimpan reject")
    cur.close()
    conn.close()
    return jsonify({"ok": True, "items": created}), 201


@api.get("/gudang-mod")
def gudang_mod_list():
    from app import ensure_extended_tables

    q = (request.args.get("q") or "").strip()
    status = (request.args.get("status") or "").strip().lower()
    pg = parse_page_args(request.args, default_page_size=20)
    order = order_sql(
        {
            "date_created": "gm.created_at",
            "kode_mod": "gm.kode_mod",
            "kode_wip": "gm.kode_wip",
            "kode_yl": "gm.kode_yl",
            "id": "gm.id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="gm.created_at DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    where = " WHERE 1=1"
    params: list = []
    if status in ("in_stock", "out"):
        where += " AND gm.status=%s"
        params.append(status)
    if q:
        like = f"%{q}%"
        where += (
            " AND (gm.kode_mod LIKE %s OR gm.kode_wip LIKE %s OR gm.kode_yl LIKE %s "
            "OR gm.kode_palet LIKE %s)"
        )
        params.extend([like, like, like, like])
    cur.execute(f"SELECT COUNT(*) AS c FROM tbl_gudang_mod gm{where}", params)
    total = int((cur.fetchone() or {}).get("c") or 0)
    cur.execute(
        f"SELECT gm.*, pk.kode_proses, pk.treatment_jenis, "
        f"y.thickness AS yl_thickness, y.warna AS yl_warna "
        f"FROM tbl_gudang_mod gm "
        f"LEFT JOIN tbl_persiapan_kulit pk ON pk.id = gm.persiapan_id "
        f"LEFT JOIN tbl_yl y ON y.kode_palet=gm.kode_palet AND y.kode_yl=gm.kode_yl "
        f"{where} ORDER BY {order} LIMIT %s OFFSET %s",
        params + [pg["page_size"], pg["offset"]],
    )
    items = _rows(cur.fetchall())
    cur.close()
    conn.close()
    return jsonify(
        page_payload(
            items=items,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


@api.get("/gudang-mod/<int:mod_id>/label")
def gudang_mod_label_api(mod_id: int):
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT gm.*, pk.kode_proses, pk.treatment_jenis, pk.rencana_item_id, "
        "i.material_name AS rencana_material_name, i.thickness AS rencana_thickness, "
        "i.backer AS rencana_backer "
        "FROM tbl_gudang_mod gm "
        "LEFT JOIN tbl_persiapan_kulit pk ON pk.id = gm.persiapan_id "
        "LEFT JOIN tbl_rencana_item i ON i.id = pk.rencana_item_id "
        "WHERE gm.id=%s",
        (mod_id,),
    )
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return _err("Data MOD tidak ditemukan", 404)
    identity = _mod_label_identity(cur, row)
    cur.close()
    conn.close()
    payload = _row(row) or {}
    for key in (
        "rencana_item_id",
        "rencana_material_name",
        "rencana_thickness",
        "rencana_backer",
    ):
        payload.pop(key, None)
    payload.update(identity)
    return jsonify(
        {
            "mod": payload,
            "title": "LABEL REJECT KULIT",
        }
    )


def _rpi_allocations_for_item(cur, item_id: int) -> list:
    cur.execute(
        "SELECT p.id AS rip_id, p.po_id AS po_id, p.qty_proses AS qty_rpi, "
        "po.no_so, po.no_po, po.source_detail_id, po.lot_number, po.item_name, "
        "po.warna AS po_warna, po.emboss AS po_emboss, "
        "i.material_name, i.color, i.emboss "
        "FROM tbl_rencana_item_po p "
        "JOIN tbl_master_po po ON po.id = p.po_id "
        "JOIN tbl_rencana_item i ON i.id = p.item_id "
        "WHERE p.item_id = %s ORDER BY po.no_so, po.no_po, p.id",
        (int(item_id),),
    )
    rows = _rows(cur.fetchall())
    _attach_erp_lot_no(rows)
    for row in rows:
        mat = (row.get("material_name") or row.get("item_name") or "").strip()
        row["material_name"] = mat or "—"
        row["color"] = (row.get("color") or row.get("po_warna") or "").strip() or "—"
        row["emboss"] = (row.get("emboss") or row.get("po_emboss") or "").strip() or "—"
    return rows


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
        "SELECT jenis, nama_treatment FROM tbl_master_treatment "
        "WHERE COALESCE(is_active, 1)=1 ORDER BY jenis, nama_treatment"
    )
    treatments = _rows(cur.fetchall())
    rpi_allocations = []
    rid = persiapan.get("rencana_item_id")
    if rid:
        try:
            rpi_allocations = _rpi_allocations_for_item(cur, int(rid))
        except (TypeError, ValueError):
            rpi_allocations = []
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
            "rpi_allocations": rpi_allocations,
        }
    )


@api.post("/proses/<int:persiapan_id>/change-lot")
def proses_change_lot(persiapan_id: int):
    """Ganti alokasi PO (lot SO) pada RPI proses ini ke baris PO / lot baru."""
    from app import _replace_item_po_selections, ensure_rencana_tables

    body = request.get_json(silent=True) or {}
    try:
        rip_id = int(body.get("rip_id") or 0)
    except (TypeError, ValueError):
        return _err("rip_id tidak valid")
    try:
        new_po_id = int(body.get("new_po_id") or 0)
    except (TypeError, ValueError):
        return _err("new_po_id tidak valid")
    if rip_id <= 0 or new_po_id <= 0:
        return _err("rip_id dan new_po_id wajib")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_persiapan_kulit WHERE id=%s", (persiapan_id,))
    persiapan = cur.fetchone()
    if not persiapan:
        cur.close()
        conn.close()
        return _err("Data tidak ditemukan", 404)
    item_id = persiapan.get("rencana_item_id")
    if not item_id:
        cur.close()
        conn.close()
        return _err("Persiapan tidak terhubung ke item RPI")
    try:
        item_id = int(item_id)
    except (TypeError, ValueError):
        cur.close()
        conn.close()
        return _err("rencana_item_id tidak valid")

    cur.execute(
        "SELECT id, po_id, qty_proses FROM tbl_rencana_item_po WHERE id=%s AND item_id=%s",
        (rip_id, item_id),
    )
    target = cur.fetchone()
    if not target:
        cur.close()
        conn.close()
        return _err("Alokasi PO tidak ditemukan pada RPI ini", 404)
    old_po_id = int(target.get("po_id") or 0)
    qty = float(target.get("qty_proses") or 0)
    if qty <= 0:
        cur.close()
        conn.close()
        return _err("Qty RPI alokasi tidak valid")
    if old_po_id == new_po_id:
        cur.close()
        conn.close()
        return jsonify({"ok": True, "message": "Lot tidak berubah"})

    cur.execute(
        "SELECT p.id, p.po_id, p.qty_proses FROM tbl_rencana_item_po p WHERE p.item_id=%s ORDER BY p.id",
        (item_id,),
    )
    allocs = _rows(cur.fetchall())
    po_data = []
    replaced = False
    for row in allocs:
        if int(row.get("id") or 0) == rip_id:
            po_data.append({"po_id": new_po_id, "qty": qty})
            replaced = True
        else:
            po_data.append({"po_id": int(row["po_id"]), "qty": float(row.get("qty_proses") or 0)})
    if not replaced:
        cur.close()
        conn.close()
        return _err("Alokasi PO tidak ditemukan", 404)

    try:
        _replace_item_po_selections(cur, item_id, po_data)
    except ValueError as exc:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(exc))

    conn.commit()
    new_lot = ""
    cur.execute("SELECT source_detail_id, lot_number FROM tbl_master_po WHERE id=%s", (new_po_id,))
    po_row = cur.fetchone() or {}
    new_lot = (po_row.get("lot_number") or "").strip()
    if not new_lot and po_row.get("source_detail_id"):
        new_lot = _erp_lot_no_for_source_detail(po_row.get("source_detail_id"))
    rpi_allocations = _rpi_allocations_for_item(cur, item_id)
    cur.close()
    conn.close()
    return jsonify(
        {
            "ok": True,
            "lot_no": new_lot,
            "rpi_allocations": rpi_allocations,
            "message": "Lot number diperbarui",
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
    cur.execute(
        "SELECT COUNT(*) AS c FROM tbl_persiapan_ukur WHERE persiapan_id=%s",
        (persiapan_id,),
    )
    persiapan["jml_pcs"] = int((cur.fetchone() or {}).get("c") or 0)
    cur.close()
    conn.close()
    return jsonify(
        {
            "persiapan": _row(persiapan),
            "ky_sessions": ky_sessions,
            "title": "STIKER LOT WIP PRODUKSI",
        }
    )


def _rencana_spek(cur, persiapan) -> tuple[str, str]:
    warna = str((persiapan or {}).get("warna") or "")
    tebal = str((persiapan or {}).get("tebal") or "")
    rid = (persiapan or {}).get("rencana_item_id")
    if rid:
        cur.execute(
            "SELECT color, thickness FROM tbl_rencana_item WHERE id=%s",
            (rid,),
        )
        item = cur.fetchone()
        if item:
            if str(item.get("color") or "").strip():
                warna = str(item.get("color") or "")
            if str(item.get("thickness") or "").strip():
                tebal = str(item.get("thickness") or "")
    return warna, tebal


def _yl_spek_error(cur, persiapan, kode_palet: str, kode_yl: str) -> str | None:
    from spek_match import yl_spek_reject_reason

    cur.execute(
        "SELECT thickness, warna FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
        ((kode_palet or "").strip(), (kode_yl or "").strip()),
    )
    yl = cur.fetchone()
    if not yl:
        return None
    warna, tebal = _rencana_spek(cur, persiapan)
    return yl_spek_reject_reason(
        yl_warna=yl.get("warna"),
        yl_tebal=yl.get("thickness"),
        rencana_warna=warna,
        rencana_tebal=tebal,
        require_color_match=False,
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
            if status == "voided":
                cur.close()
                conn.close()
                return _err("Persiapan sudah dibatalkan dan tidak dapat dimulai lagi.")
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
            if target_qty <= 0:
                cur.close()
                conn.close()
                return _err("Qty KY harus > 0.")
            if _persiapan_has_ky_yl(cur, persiapan_id, kode_palet, kode_yl):
                cur.close()
                conn.close()
                return _err(
                    f"YL {kode_yl} di palet {kode_palet} sudah ada di proses ini. "
                    "Pilih YL lain atau selesaikan yang sudah ada."
                )
            avail = _yl_available_qty(cur, kode_palet, kode_yl)
            if avail <= 0:
                cur.close()
                conn.close()
                stock = _yl_stock_qty(cur, kode_palet, kode_yl)
                if stock <= 0:
                    return _err(f"Stok YL {kode_yl} kosong di palet {kode_palet}.")
                return _err(
                    f"YL {kode_yl} sudah dialokasikan proses lain "
                    f"(stok {stock}, tersedia {avail})."
                )
            if target_qty > avail + 1e-9:
                cur.close()
                conn.close()
                return _err(f"Qty KY melebihi stok tersedia ({avail}).")
            spek_err = _yl_spek_error(cur, persiapan, kode_palet, kode_yl)
            if spek_err:
                cur.close()
                conn.close()
                return _err(spek_err)
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
                "SELECT id, status, kode_palet, kode_yl, actual_qty, target_qty, gudang_mod_id "
                "FROM tbl_persiapan_ky WHERE id=%s AND persiapan_id=%s",
                (ky_id, persiapan_id),
            )
            ky_row = cur.fetchone()
            if not ky_row or ky_row.get("status") != "active":
                cur.close()
                conn.close()
                return _err("KY aktif tidak ditemukan")
            new_actual = float(ky_row.get("actual_qty") or 0) + size_val
            if int(ky_row.get("gudang_mod_id") or 0):
                mod_cap = float(ky_row.get("target_qty") or 0)
                if new_actual > mod_cap + 1e-9:
                    cur.close()
                    conn.close()
                    return _err(
                        f"Total ukur {new_actual} melebihi SF MOD ({mod_cap})."
                    )
            else:
                stock = _yl_stock_qty(cur, ky_row["kode_palet"], ky_row["kode_yl"])
                # Ukur tidak boleh melebihi stok fisik yang masih ada di palet.
                if new_actual > stock + 1e-9:
                    cur.close()
                    conn.close()
                    return _err(
                        f"Total ukur {new_actual} melebihi stok YL ({stock}) di palet {ky_row['kode_palet']}."
                    )
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
            skip_spek = body.get("skip_spek_check") in (True, 1, "1", "true", "True")
            if not skip_spek:
                spek_err = _yl_spek_error(
                    cur, persiapan, ky.get("kode_palet") or "", ky.get("kode_yl") or ""
                )
                if spek_err:
                    cur.close()
                    conn.close()
                    return _err(spek_err)
            target = float(ky["target_qty"] or 0)
            actual = float(ky["actual_qty"] or 0)
            consumed = _consume_yl_for_ky_session(cur, ky, persiapan)
            selisih = actual - target
            cur.execute("UPDATE tbl_persiapan_ky SET status='selesai' WHERE id=%s", (ky_id,))
            _activate_next_planned_ky(cur, persiapan_id)
            from_mod = int(ky.get("gudang_mod_id") or 0)
            if (
                not from_mod
                and persiapan.get("rencana_item_id")
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
            # Catat sisa kulit ke gudang sisa bila ada alokasi tak terpakai
            if (
                not from_mod
                and int(ky.get("tidak_ada_sisa") or 0) != 1
                and target > actual + 1e-9
            ):
                sisa_qty = round(target - actual, 3)
                cur.execute(
                    "INSERT INTO tbl_stock_sisa "
                    "(sumber, barcode, lot, qty, status, notes) "
                    "VALUES ('kulit', %s, %s, %s, 'open', %s)",
                    (
                        ky.get("kode_yl"),
                        ky.get("kode_palet"),
                        sisa_qty,
                        f"Sisa KY #{ky_id} dikembalikan ke palet",
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
def _lab_sisa_consume(cur, *, lab_sisa_id: int, qty: float) -> None:
    """Kurangi qty sisa lot warna (tab Sisa) saat dipakai sebagai bahan lot baru."""
    cur.execute(
        "SELECT id, kode_lot_warna, qty_sisa, status FROM tbl_lab_lot_sisa "
        "WHERE id=%s FOR UPDATE",
        (lab_sisa_id,),
    )
    row = cur.fetchone()
    if not row or (row.get("status") or "open") != "open":
        raise ValueError("Sisa lot warna tidak valid atau sudah Mixed")
    avail = float(row.get("qty_sisa") or 0)
    if qty > avail + 1e-9:
        kode = (row.get("kode_lot_warna") or "").strip() or str(lab_sisa_id)
        raise ValueError(
            f"Qty melebihi sisa lot warna {kode} (butuh {qty}, tersedia {avail})"
        )
    new_qty = round(avail - qty, 3)
    if new_qty <= 0:
        cur.execute(
            "UPDATE tbl_lab_lot_sisa SET qty_sisa=0, status='mixed' WHERE id=%s",
            (lab_sisa_id,),
        )
    else:
        cur.execute(
            "UPDATE tbl_lab_lot_sisa SET qty_sisa=%s WHERE id=%s",
            (new_qty, lab_sisa_id),
        )


def _lw_base_from_rpi(kode_rencana_item: str) -> str:
    s = (kode_rencana_item or "").strip()
    if not s:
        return "LW"
    upper = s.upper()
    if upper.startswith("RPI-"):
        return "LW-" + s[4:]
    if upper.startswith("RPI"):
        rest = s[3:].lstrip("-")
        return f"LW-{rest}" if rest else "LW"
    return f"LW-{s}"


def _next_lw_kode(cur, kode_rencana_item: str) -> str:
    base = _lw_base_from_rpi(kode_rencana_item)
    cur.execute(
        "SELECT kode_lot_warna FROM tbl_lab_lot "
        "WHERE kode_lot_warna = %s OR kode_lot_warna LIKE %s",
        (base, f"{base}-%"),
    )
    max_seq = 0
    for row in cur.fetchall() or []:
        kode = (row.get("kode_lot_warna") or "").strip()
        if kode == base:
            max_seq = max(max_seq, 1)
            continue
        prefix = base + "-"
        if kode.startswith(prefix):
            tail = kode[len(prefix) :]
            if tail.isdigit():
                max_seq = max(max_seq, int(tail))
    return f"{base}-{max_seq + 1}"


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
        "ri.emboss, ri.color_swatch, ri.keterangan, "
        "rp.nama_rencana, rp.tanggal_rencana, ri.nama_customer, "
        "(SELECT COALESCE(SUM(p.qty_proses), 0) FROM tbl_rencana_item_po p WHERE p.item_id = ri.id) "
        "AS total_qty_so, "
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
    from dual_gudang import GUDANG_LAPANGAN

    kimia_rows = [
        r for r in list_materials("kimia") if (r.get("code") or "").strip()
    ]
    stok_by_code: dict[str, float] = {}
    if kimia_rows:
        try:
            cur.execute(
                "SELECT kode_material, COALESCE(SUM(qty_sisa), 0) AS qty "
                "FROM tbl_stok_kimia_in "
                "WHERE gudang=%s AND qty_sisa > 0 AND kode_material IS NOT NULL "
                "GROUP BY kode_material",
                (GUDANG_LAPANGAN,),
            )
            for row in cur.fetchall() or []:
                kode = (row.get("kode_material") or "").strip()
                if kode:
                    stok_by_code[kode] = float(row.get("qty") or 0)
        except Exception:
            stok_by_code = {}
    kimia_list = [
        {
            "kode_kimia": r["code"],
            "nama_kimia": r["name"],
            "satuan": r.get("unit") or "kg",
            "erp_material_id": r.get("id"),
            "stok_lapangan": round(stok_by_code.get((r["code"] or "").strip(), 0.0), 3),
        }
        for r in kimia_rows
    ]
    kimia_stock_lots: list[dict] = []
    try:
        cur.execute(
            "SELECT id, kode_internal, kode_material, nama_material, lot_number, "
            "qty_sisa, satuan, gudang, erp_material_id, kimia_id "
            "FROM tbl_stok_kimia_in "
            "WHERE gudang=%s AND qty_sisa > 0 "
            "ORDER BY tanggal_in ASC, id ASC",
            (GUDANG_LAPANGAN,),
        )
        for row in cur.fetchall() or []:
            kimia_stock_lots.append(
                {
                    "stok_in_id": row.get("id"),
                    "kode_internal": row.get("kode_internal"),
                    "kode_kimia": row.get("kode_material"),
                    "nama_kimia": row.get("nama_material"),
                    "lot_number": row.get("lot_number"),
                    "qty_sisa": round(float(row.get("qty_sisa") or 0), 3),
                    "satuan": row.get("satuan") or "kg",
                    "gudang": row.get("gudang"),
                }
            )
    except Exception:
        kimia_stock_lots = []
    lab_lot_sisa_picks: list[dict] = []
    try:
        cur.execute(
            "SELECT id, kode_lot_warna, nama_lot_warna, qty_sisa, notes "
            "FROM tbl_lab_lot_sisa "
            "WHERE COALESCE(status, 'open') = 'open' AND qty_sisa > 0 "
            "ORDER BY date_created ASC, id ASC"
        )
        for row in cur.fetchall() or []:
            kode = (row.get("kode_lot_warna") or "").strip()
            if not kode:
                continue
            nama = (row.get("nama_lot_warna") or kode).strip()
            lab_lot_sisa_picks.append(
                {
                    "source": "lab_sisa",
                    "lab_sisa_id": row.get("id"),
                    "kode_kimia": kode,
                    "nama_kimia": nama,
                    "lot_number": kode,
                    "qty_sisa": round(float(row.get("qty_sisa") or 0), 3),
                    "satuan": "kg",
                }
            )
    except Exception:
        lab_lot_sisa_picks = []
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
            "kimia_stock_lots": kimia_stock_lots,
            "lab_lot_sisa_picks": lab_lot_sisa_picks,
            "reseps": reseps,
            "gate": {
                "link_rpi_requires_proses": True,
                "rpi_required": True,
                "allowed_persiapan_status": ["started", "saved", "completed"],
            },
        }
    )


def _lab_group_lots(flat: list[dict]) -> list[dict]:
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
                "emboss": row.get("emboss"),
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
    return [lots_map[k] for k in order]


@api.get("/lab")
def lab_list():
    from app import ensure_lab_tables, ensure_rencana_tables

    tab = (request.args.get("tab") or "utama").strip().lower()
    pg = parse_page_args(request.args, default_page_size=20)

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_lab_tables(cur)
    ensure_rencana_tables(cur)
    conn.commit()
    from app import _col_names

    lab_cols = _col_names(cur, "tbl_lab_lot")
    if "rencana_item_id" not in lab_cols:
        cur.execute(
            "ALTER TABLE tbl_lab_lot ADD COLUMN rencana_item_id INT DEFAULT NULL"
        )
        conn.commit()

    if tab == "sisa":
        order = order_sql(
            {
                "date_created": "s.date_created",
                "kode_lot_warna": "s.kode_lot_warna",
                "qty_sisa": "s.qty_sisa",
                "id": "s.id",
            },
            sort_by=pg["sort_by"],
            sort_dir=pg["sort_dir"],
            default_sql="s.date_created DESC",
        )
        cur.execute(
            "SELECT COUNT(*) AS c FROM tbl_lab_lot_sisa "
            "WHERE COALESCE(status, 'open') = 'open'"
        )
        total = int((cur.fetchone() or {}).get("c") or 0)
        cur.execute(
            f"SELECT s.id, s.kode_lot_warna, s.nama_lot_warna, s.qty_sisa, s.notes, "
            f"s.status, s.date_created, "
            f"l.status AS lot_status, ri.kode_rencana_item, ri.kode_lot_wip, ri.color, ri.nama_customer "
            f"FROM tbl_lab_lot_sisa s "
            f"LEFT JOIN tbl_lab_lot l ON l.kode_lot_warna = s.kode_lot_warna "
            f"LEFT JOIN tbl_rencana_item ri ON ri.id = l.rencana_item_id "
            f"WHERE COALESCE(s.status, 'open') = 'open' "
            f"ORDER BY {order} LIMIT %s OFFSET %s",
            (pg["page_size"], pg["offset"]),
        )
        items = _rows(cur.fetchall())
        cur.close()
        conn.close()
        payload = page_payload(
            items=items,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
        payload.update({"lots": items, "tab": tab, "ok": True})
        return jsonify(payload)

    status = "active" if tab == "utama" else "used" if tab == "terpakai" else "active"
    cur.execute(
        "SELECT l.id AS lot_id, l.kode_lot_warna, l.nama_lot_warna, l.status, l.date_created, "
        "l.rencana_item_id, "
        "d.id AS detail_id, d.kode_kimia, d.nama_kimia, d.resep, d.satuan, d.qty, d.remarks, "
        "ri.kode_rencana_item, ri.kode_lot_wip, ri.color, ri.thickness, ri.emboss, "
        "rp.nama_rencana, rp.tanggal_rencana, ri.nama_customer "
        "FROM tbl_lab_lot l "
        "JOIN tbl_lab_lot_detail d ON d.kode_lot_warna = l.kode_lot_warna "
        "LEFT JOIN tbl_rencana_item ri ON ri.id = l.rencana_item_id "
        "LEFT JOIN tbl_rencana_produksi rp ON rp.id = ri.rencana_id "
        "WHERE l.status = %s "
        "ORDER BY COALESCE(l.date_created, rp.tanggal_rencana) DESC, l.kode_lot_warna, d.id "
        "LIMIT 500",
        (status,),
    )
    flat = _rows(cur.fetchall())
    cur.close()
    conn.close()

    lots = _lab_group_lots(flat)
    lots = sort_rows(
        lots,
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        fields={
            "date_created": "date_created",
            "kode_lot_warna": "kode_lot_warna",
            "status": "status",
            "tanggal_rencana": "tanggal_rencana",
            "id": "lot_id",
        },
    )
    page_lots, total = slice_page(lots, page=pg["page"], page_size=pg["page_size"], offset=pg["offset"])
    payload = page_payload(
        items=page_lots,
        total=total,
        page=pg["page"],
        page_size=pg["page_size"],
        offset=pg["offset"],
    )
    payload.update({"lots": page_lots, "flat": flat, "tab": tab, "ok": True})
    return jsonify(payload)


@api.post("/lab/sisa")
def lab_sisa_create():
    from app import ensure_lab_tables

    body = request.get_json(silent=True) or {}
    kode_lot_warna = (body.get("kode_lot_warna") or body.get("lot_no") or "").strip()
    notes = (body.get("notes") or "").strip() or None
    try:
        qty_sisa = float(body.get("qty_sisa") or body.get("qty") or 0)
    except (TypeError, ValueError):
        return _err("qty_sisa harus angka")
    if not kode_lot_warna:
        return _err("LOT NO wajib")
    if qty_sisa <= 0:
        return _err("qty_sisa harus > 0")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_lab_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_lab_lot WHERE kode_lot_warna = %s", (kode_lot_warna,))
    lot = cur.fetchone()
    if not lot:
        cur.close()
        conn.close()
        return _err("Lot warna tidak ditemukan", 404)
    lot_status = (lot.get("status") or "").strip()
    if lot_status not in ("active", "used"):
        cur.close()
        conn.close()
        return _err("Lot harus ada di tab Utama atau Terpakai")

    cur.execute(
        "INSERT INTO tbl_lab_lot_sisa (kode_lot_warna, nama_lot_warna, qty_sisa, notes, status) "
        "VALUES (%s, %s, %s, %s, 'open')",
        (kode_lot_warna, lot.get("nama_lot_warna"), qty_sisa, notes),
    )
    new_id = cur.lastrowid
    conn.commit()
    cur.execute(
        "SELECT s.id, s.kode_lot_warna, s.nama_lot_warna, s.qty_sisa, s.notes, s.date_created, "
        "l.status AS lot_status, ri.kode_rencana_item, ri.kode_lot_wip, ri.color, ri.nama_customer "
        "FROM tbl_lab_lot_sisa s "
        "LEFT JOIN tbl_lab_lot l ON l.kode_lot_warna = s.kode_lot_warna "
        "LEFT JOIN tbl_rencana_item ri ON ri.id = l.rencana_item_id "
        "WHERE s.id = %s",
        (new_id,),
    )
    row = _row(cur.fetchone())
    cur.close()
    conn.close()
    return jsonify({"ok": True, "id": new_id, "item": row}), 201


@api.post("/lab/sisa/<int:sisa_id>/mixed")
def lab_sisa_mixed(sisa_id):
    """Tandai sisa sudah dicampur sehingga tidak lagi tampil di tab Sisa."""
    from app import ensure_lab_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_lab_tables(cur)
    conn.commit()
    cur.execute("SELECT id, status, kode_lot_warna FROM tbl_lab_lot_sisa WHERE id=%s", (sisa_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return _err("Catatan sisa tidak ditemukan", 404)
    if (row.get("status") or "open") == "mixed":
        cur.close()
        conn.close()
        return _err("Sisa ini sudah Mixed")
    cur.execute("UPDATE tbl_lab_lot_sisa SET status='mixed' WHERE id=%s", (sisa_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(
        {
            "ok": True,
            "id": sisa_id,
            "status": "mixed",
            "kode_lot_warna": row.get("kode_lot_warna"),
        }
    )


@api.post("/lab")
def lab_create():
    from app import (
        _col_names,
        ensure_extended_tables,
        ensure_lab_tables,
        ensure_rencana_tables,
    )

    body = request.get_json(silent=True) or {}
    rencana_item_id = body.get("rencana_item_id") or None
    lots_in = body.get("lots") or body.get("color_lots") or []
    # Legacy single-lot payload (nama + items flat).
    if not lots_in and (body.get("nama_lot_warna") or body.get("items")):
        lots_in = [
            {
                "nama_lot_warna": body.get("nama_lot_warna"),
                "catatan": body.get("catatan") or body.get("notes"),
                "items": body.get("items") or [],
            }
        ]
    if not rencana_item_id:
        return _err("Item rencana (RPI) wajib dipilih.")
    if not lots_in:
        return _err("Minimal satu baris lot warna (Nama Lot Warna) harus ditambahkan.")

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

    try:
        rencana_item_id = int(rencana_item_id)
    except (TypeError, ValueError):
        cur.close()
        conn.close()
        return _err("rencana_item_id tidak valid")
    cur.execute(
        "SELECT id, kode_rencana_item, kode_lot_wip FROM tbl_rencana_item WHERE id=%s",
        (rencana_item_id,),
    )
    ri_row = cur.fetchone()
    if not ri_row:
        cur.close()
        conn.close()
        return _err("Item rencana tidak ditemukan", 404)
    kode_rencana_item = (ri_row.get("kode_rencana_item") or "").strip()
    kode_wip = (ri_row.get("kode_lot_wip") or "").strip() or None
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
            "RPI memerlukan Persiapan (Proses) yang sudah di-Start. Buat/Start proses dulu."
        )

    from erp_raw_materials import fetch_material_by_code
    from dual_gudang import GUDANG_LAPANGAN

    lots_prepared: list[dict] = []
    for lot_idx, lot_in in enumerate(lots_in):
        nama_lot_warna = (lot_in.get("nama_lot_warna") or "").strip()
        if not nama_lot_warna:
            cur.close()
            conn.close()
            return _err(f"Nama Lot Warna wajib (baris {lot_idx + 1}).")
        catatan = (lot_in.get("catatan") or lot_in.get("notes") or "").strip() or None
        rows_in = lot_in.get("items") or []
        rows = [
            r
            for r in rows_in
            if r.get("lab_sisa_id") not in (None, "")
            or (r.get("kode_kimia") or "").strip()
        ]
        if not rows:
            cur.close()
            conn.close()
            return _err(f"Minimal satu bahan kimia untuk lot \"{nama_lot_warna}\".")
        prepared_items = []
        for r in rows:
            lab_sisa_id = r.get("lab_sisa_id")
            try:
                lab_sisa_id = (
                    int(lab_sisa_id) if lab_sisa_id not in (None, "") else None
                )
            except (TypeError, ValueError):
                lab_sisa_id = None
            kode_kimia = (r.get("kode_kimia") or "").strip()
            lot_number = (r.get("lot_number") or "").strip() or None
            stok_in_id = r.get("stok_in_id")
            try:
                stok_in_id = int(stok_in_id) if stok_in_id not in (None, "") else None
            except (TypeError, ValueError):
                stok_in_id = None
            satuan = (r.get("satuan") or "kg").strip() or "kg"
            try:
                qty = float(r.get("qty") or 0)
            except (TypeError, ValueError):
                cur.close()
                conn.close()
                return _err(f"Qty tidak valid untuk kimia {kode_kimia or 'sisa lot'}")
            if qty <= 0:
                cur.close()
                conn.close()
                return _err(f"Qty harus > 0 untuk kimia {kode_kimia or 'sisa lot'}")
            line_remarks = (r.get("remarks") or "").strip()
            if lab_sisa_id:
                cur.execute(
                    "SELECT id, kode_lot_warna, nama_lot_warna, qty_sisa, status "
                    "FROM tbl_lab_lot_sisa WHERE id=%s",
                    (lab_sisa_id,),
                )
                sisa_row = cur.fetchone()
                if not sisa_row or (sisa_row.get("status") or "open") != "open":
                    cur.close()
                    conn.close()
                    return _err("Sisa lot warna tidak valid atau sudah Mixed", 400)
                kode_kimia = (sisa_row.get("kode_lot_warna") or kode_kimia or "").strip()
                if not kode_kimia:
                    cur.close()
                    conn.close()
                    return _err("Kode sisa lot warna kosong", 400)
                lot_number = kode_kimia
                avail = float(sisa_row.get("qty_sisa") or 0)
                if qty > avail:
                    cur.close()
                    conn.close()
                    return _err(
                        f"Qty melebihi sisa lot warna {kode_kimia} "
                        f"(butuh {qty}, tersedia {avail})",
                        400,
                    )
                nama_sisa = (sisa_row.get("nama_lot_warna") or kode_kimia).strip()
                sisa_note = "Bahan: sisa lot warna"
                line_remarks = (
                    f"{line_remarks} · {sisa_note}".strip(" ·")
                    if line_remarks
                    else sisa_note
                )
                prepared_items.append(
                    {
                        "kode_kimia": kode_kimia,
                        "code_match": kode_kimia,
                        "nama_kimia": nama_sisa,
                        "resep": (r.get("resep") or "").strip() or None,
                        "satuan": satuan,
                        "qty": qty,
                        "remarks": line_remarks or None,
                        "stok_in_id": None,
                        "lab_sisa_id": lab_sisa_id,
                        "lot_number": lot_number,
                    }
                )
                continue
            if not kode_kimia:
                cur.close()
                conn.close()
                return _err("Kode kimia wajib untuk bahan stok lapangan")
            if lot_number:
                lot_note = f"Lot No: {lot_number}"
                line_remarks = f"{line_remarks} · {lot_note}".strip(" ·") if line_remarks else lot_note
            kimia = fetch_material_by_code(kode_kimia, material_type="kimia")
            if kimia and not (r.get("satuan") or "").strip():
                satuan = (kimia.get("unit") or satuan or "kg").strip() or "kg"
            code_match = (kimia.get("code") if kimia else kode_kimia) or kode_kimia
            if stok_in_id:
                cur.execute(
                    "SELECT * FROM tbl_stok_kimia_in WHERE id=%s AND gudang=%s AND qty_sisa > 0",
                    (stok_in_id, GUDANG_LAPANGAN),
                )
                stock_lot = cur.fetchone()
                if not stock_lot:
                    cur.close()
                    conn.close()
                    return _err(f"Lot stok kimia tidak valid untuk {kode_kimia}", 400)
                sk = (stock_lot.get("kode_material") or "").strip()
                if sk not in (kode_kimia, code_match):
                    cur.close()
                    conn.close()
                    return _err(f"Lot stok tidak cocok dengan kimia {kode_kimia}", 400)
                avail = float(stock_lot.get("qty_sisa") or 0)
                if qty > avail:
                    cur.close()
                    conn.close()
                    return _err(
                        f"Qty melebihi sisa lot {lot_number or stock_lot.get('kode_internal')} "
                        f"({kode_kimia}: butuh {qty}, tersedia {avail})",
                        400,
                    )
            else:
                cur.execute(
                    "SELECT COALESCE(SUM(qty_sisa), 0) AS qty "
                    "FROM tbl_stok_kimia_in "
                    "WHERE gudang=%s AND qty_sisa > 0 AND ("
                    "  kode_material=%s OR kode_material=%s"
                    ")",
                    (GUDANG_LAPANGAN, kode_kimia, code_match),
                )
                avail = float((cur.fetchone() or {}).get("qty") or 0)
                if qty > avail:
                    cur.close()
                    conn.close()
                    return _err(
                        f"Stok lapangan tidak cukup untuk {kode_kimia} "
                        f"(butuh {qty}, tersedia {avail})",
                        400,
                    )
            prepared_items.append(
                {
                    "kode_kimia": kode_kimia,
                    "code_match": code_match,
                    "nama_kimia": (kimia.get("name") if kimia else kode_kimia),
                    "resep": (r.get("resep") or "").strip() or None,
                    "satuan": satuan,
                    "qty": qty,
                    "remarks": line_remarks or None,
                    "stok_in_id": stok_in_id,
                    "lab_sisa_id": None,
                    "lot_number": lot_number,
                }
            )
        lots_prepared.append(
            {
                "nama_lot_warna": nama_lot_warna,
                "catatan": catatan,
                "items": prepared_items,
            }
        )

    tanggal = date.today().isoformat()
    created_kodes: list[str] = []
    stok_outs: list[dict] = []
    try:
        for lot in lots_prepared:
            kode_lot_warna = _next_lw_kode(cur, kode_rencana_item)
            created_kodes.append(kode_lot_warna)
            catatan = lot.get("catatan")
            cur.execute(
                "INSERT INTO tbl_lab_lot (kode_lot_warna, nama_lot_warna, rencana_item_id) "
                "VALUES (%s, %s, %s)",
                (kode_lot_warna, lot["nama_lot_warna"], rencana_item_id),
            )
            for row in lot["items"]:
                detail_remarks = row["remarks"]
                if catatan:
                    detail_remarks = (
                        f"{catatan} · {detail_remarks}".strip(" ·")
                        if detail_remarks
                        else catatan
                    )
                cur.execute(
                    "INSERT INTO tbl_lab_lot_detail "
                    "(kode_lot_warna, kode_kimia, nama_kimia, resep, satuan, qty, remarks) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (
                        kode_lot_warna,
                        row["kode_kimia"],
                        row["nama_kimia"],
                        row["resep"],
                        row["satuan"],
                        row["qty"],
                        detail_remarks,
                    ),
                )
            lab_note = f"Lab lot {kode_lot_warna}"
            for row in lot["items"]:
                if row.get("lab_sisa_id"):
                    _lab_sisa_consume(
                        cur,
                        lab_sisa_id=int(row["lab_sisa_id"]),
                        qty=float(row["qty"]),
                    )
                    continue
                stok_outs.extend(
                    _kimia_consume_lapangan_fifo(
                        cur,
                        kode_kimia=row["kode_kimia"],
                        code_match=row.get("code_match") or row["kode_kimia"],
                        qty_needed=float(row["qty"]),
                        kode_wip=kode_wip,
                        keterangan=lab_note,
                        tanggal=tanggal,
                        stok_in_id=row.get("stok_in_id"),
                    )
                )
    except ValueError as exc:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(exc), 400)

    conn.commit()
    cur.close()
    conn.close()
    primary = created_kodes[0] if created_kodes else None
    return jsonify(
        {
            "ok": True,
            "kode_lot_warna": primary,
            "kode_lot_warna_list": created_kodes,
            "stok_outs": stok_outs,
            "stok_deducted": bool(stok_outs),
        }
    ), 201


# ---- packing FG ----
def _erp_lot_nos_for_source_details(source_ids) -> dict[int, str]:
    """Lot No dari baris item SO ERP via HTTP API."""
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
        from mrp_api import erp_client

        return erp_client.po_detail_lot_refs(ids)
    except Exception:
        return out


def _attach_so_remark(spec: dict | None) -> dict:
    spec = dict(spec or {})
    if not (spec.get("so_remark") or "").strip():
        spec["so_remark"] = _so_remark_for_source_detail(spec.get("source_detail_id"))
    return spec


def _so_remark_for_source_detail(source_detail_id) -> str:
    """Remark baris SO (po_details.detail_remark) via snapshot HTTP ERP."""
    if not source_detail_id:
        return ""
    try:
        sid = int(source_detail_id)
    except (TypeError, ValueError):
        return ""
    if not sid:
        return ""
    try:
        from mrp_api import erp_client

        line = (erp_client.po_detail_mrp_lines([sid]) or {}).get(sid) or {}
        return (line.get("detail_remark") or "").strip()
    except Exception:
        return ""


def _erp_lot_no_for_source_detail(source_detail_id: int | None) -> str:
    """Lot No dari baris item SO ERP (po_details.thi_line_ref / system_reference)."""
    if not source_detail_id:
        return ""
    try:
        sid = int(source_detail_id)
    except (TypeError, ValueError):
        return ""
    return _erp_lot_nos_for_source_details([sid]).get(sid, "")


def _apply_erp_line_snap_to_row(row: dict, snap: dict | None) -> None:
    if not row or not isinstance(snap, dict):
        return
    mat = (snap.get("material_name") or "").strip()
    if mat:
        row["item_name"] = mat
    lot = (snap.get("lot_ref") or "").strip()
    if lot:
        row["lot_no"] = lot
        row["lot_number"] = lot
    no_so = (snap.get("no_so") or "").strip()
    if no_so:
        row["no_so"] = no_so
    no_po = (snap.get("no_po") or "").strip()
    if no_po:
        row["no_po"] = no_po
    sid_raw = snap.get("source_detail_id")
    try:
        sid_i = int(sid_raw) if sid_raw is not None else None
    except (TypeError, ValueError):
        sid_i = None
    if sid_i:
        row["source_detail_id"] = sid_i


def _hydrate_master_po_rows_from_erp(rows: list) -> list:
    """Lot No ERP menang atas cache tbl_master_po (material + referensi SO)."""
    if not rows:
        return rows
    _attach_erp_lot_no(rows)
    ids: list[int] = []
    lots: list[str] = []
    seen_id: set[int] = set()
    seen_lot: set[str] = set()
    for row in rows:
        sid = row.get("source_detail_id")
        try:
            sid_i = int(sid) if sid is not None else None
        except (TypeError, ValueError):
            sid_i = None
        if sid_i and sid_i not in seen_id:
            seen_id.add(sid_i)
            ids.append(sid_i)
        lot = (row.get("lot_no") or row.get("lot_number") or "").strip()
        if lot and lot not in seen_lot:
            seen_lot.add(lot)
            lots.append(lot)
    by_id: dict[int, dict[str, str]] = {}
    by_lot: dict[str, dict[str, str]] = {}
    try:
        from mrp_api import erp_client

        if ids:
            by_id = erp_client.po_detail_mrp_lines(ids)
        if lots:
            by_lot = erp_client.po_detail_mrp_lines_by_lots(lots)
    except Exception:
        by_id = {}
        by_lot = {}
    for row in rows:
        lot = (row.get("lot_no") or row.get("lot_number") or "").strip()
        snap = by_lot.get(lot) if lot else None
        if not snap:
            sid = row.get("source_detail_id")
            try:
                sid_i = int(sid) if sid is not None else None
            except (TypeError, ValueError):
                sid_i = None
            if sid_i:
                snap = by_id.get(sid_i)
        _apply_erp_line_snap_to_row(row, snap)
    return rows


def _relink_rencana_allocations_by_erp_lot(cur, alloc_rows: list) -> int:
    """Perbaiki po_id alokasi jika Lot No ERP → source_detail_id berbeda dari cache master_po."""
    if not alloc_rows:
        return 0
    lots: list[str] = []
    seen: set[str] = set()
    for row in alloc_rows:
        lot = (row.get("lot_no") or row.get("lot_number") or "").strip()
        if lot and lot not in seen:
            seen.add(lot)
            lots.append(lot)
    if not lots:
        return 0
    try:
        from mrp_api import erp_client

        by_lot = erp_client.po_detail_mrp_lines_by_lots(lots)
    except Exception:
        return 0
    fixed = 0
    for row in alloc_rows:
        lot = (row.get("lot_no") or row.get("lot_number") or "").strip()
        snap = by_lot.get(lot) if lot else None
        if not snap:
            continue
        try:
            erp_sid = int(snap.get("source_detail_id") or 0)
        except (TypeError, ValueError):
            erp_sid = 0
        if not erp_sid:
            continue
        try:
            cur_sid = int(row.get("source_detail_id") or 0)
        except (TypeError, ValueError):
            cur_sid = 0
        if erp_sid == cur_sid:
            _apply_erp_line_snap_to_row(row, snap)
            continue
        cur.execute(
            "SELECT id FROM tbl_master_po WHERE source_detail_id=%s LIMIT 1",
            (erp_sid,),
        )
        hit = cur.fetchone()
        if not hit:
            _apply_erp_line_snap_to_row(row, snap)
            continue
        new_po_id = int(hit["id"])
        old_po_id = int(row.get("po_id") or 0)
        rip_id = row.get("id")
        if new_po_id and new_po_id != old_po_id and rip_id:
            cur.execute(
                "UPDATE tbl_rencana_item_po SET po_id=%s WHERE id=%s",
                (new_po_id, int(rip_id)),
            )
            row["po_id"] = new_po_id
            fixed += 1
        row["source_detail_id"] = erp_sid
        _apply_erp_line_snap_to_row(row, snap)
        cur.execute(
            "UPDATE tbl_master_po SET item_name=%s, lot_number=%s, no_so=%s, no_po=%s, "
            "source_detail_id=%s WHERE id=%s",
            (
                (snap.get("material_name") or row.get("item_name") or "").strip() or None,
                (snap.get("lot_ref") or lot or "").strip() or None,
                (snap.get("no_so") or "").strip() or None,
                (snap.get("no_po") or "").strip() or None,
                erp_sid,
                new_po_id,
            ),
        )
    return fixed


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
    cur.execute("SELECT 1 FROM tbl_gudang_fg WHERE TRIM(kode_packing)=%s LIMIT 1", (kode,))
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
    if swatch == "-":
        swatch = ""
    if swatch and swatch not in str(color):
        color = f"{color} ({swatch})" if color and color != "-" else swatch

    lot_no = spec.get("lot_no") or spec.get("work_order") or packing.get("kode_wip") or "-"
    factory_code = spec.get("no_so") or packing.get("no_so") or packing.get("no_po") or "-"
    qty_unit = spec.get("qty_unit") or "SF"
    ukuran = float(roll.get("ukuran") or 0)
    qty_text = f"{int(ukuran) if ukuran == int(ukuran) else ukuran:g} {qty_unit}"
    roll_kode = (roll.get("kode_packing") or packing.get("kode_packing") or "").strip()
    produced = roll.get("created_at")
    if produced:
        producing_date = str(produced)[:10]
    else:
        producing_date = date.today().isoformat()
    material_name = (spec.get("material_name") or "").strip()
    if not material_name or material_name == "-":
        material_name = (spec.get("description") or packing.get("description") or "-").strip() or "-"

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
        "material_name": material_name,
        "color": color or "-",
        "thickness": spec.get("thickness") or "-",
        "color_swatch": spec.get("color_swatch") or "",
        "emboss": spec.get("emboss") or "-",
        "so_remark": (spec.get("so_remark") or "").strip(),
        "impactiva_grading": (roll.get("impactiva_grading") or "").strip(),
        "moisture": (roll.get("moisture") or "").strip(),
        "softness": packing.get("softness") or spec.get("softness") or "SOFT",
        "mass_material": packing.get("softness") or spec.get("softness") or "SOFT",
        "gross_weight": packing.get("gross_weight"),
        "net_weight": packing.get("net_weight"),
        "work_order": lot_no,
        "qty_unit": qty_unit,
        "producing_date": producing_date,
        "expiration_text": "1 年 (One Year)",
        "anti_moldy": "TCMTB",
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
        "  SELECT p.kode_wip, p.no_po, p.id AS packing_id, p.kode_packing, p.status AS packing_status, "
        "  COALESCE(SUM(pr.ukuran), 0) AS qty_actual, "
        "  COALESCE(MAX(pr.roll_no), 0) + 1 AS next_roll_no "
        "  FROM tbl_packing p "
        "  LEFT JOIN tbl_packing_roll pr ON pr.packing_id = p.id "
        "  WHERE p.status = 'in_progress' "
        "  GROUP BY p.id, p.kode_wip, p.no_po, p.kode_packing, p.status "
        ") prog ON prog.kode_wip IN (i.kode_lot_wip, pk.kode_wip) "
        "  AND (po_line.no_po IS NULL OR po_line.no_po = '' OR prog.no_po = po_line.no_po) "
        "WHERE ( "
        "  po_line.po_id IS NULL "
        "  OR NOT EXISTS ( "
        "    SELECT 1 FROM tbl_packing pf "
        "    WHERE pf.status = 'finished' "
        "    AND (pf.kode_wip = pk.kode_wip OR pf.kode_wip = i.kode_lot_wip) "
        "    AND pf.no_po = po_line.no_po "
        "  ) "
        ") "
        "ORDER BY i.kode_rencana_item, po_line.no_po, i.id"
    )
    rows = _rows(cur.fetchall())
    seen: set[tuple[int, int]] = set()
    items = []
    for row in rows:
        rid = int(row.get("rencana_item_id") or 0)
        if not rid:
            continue
        try:
            po_key = int(row.get("po_id") or 0)
        except (TypeError, ValueError):
            po_key = 0
        dedupe_key = (rid, po_key)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        deskripsi = (row.get("nama_rencana") or "").strip()
        if (row.get("keterangan") or "").strip():
            deskripsi = f"{deskripsi} · {row['keterangan']}".strip(" ·")
        row["deskripsi"] = deskripsi or row.get("nama_rencana") or "—"
        so_lot = _erp_lot_no_for_source_detail(row.get("source_detail_id"))
        row["lot_no"] = so_lot or row.get("kode_lot_wip") or row.get("prep_kode_wip")
        row["so_lot_no"] = so_lot
        row["kode_wip"] = row.get("prep_kode_wip") or row.get("kode_lot_wip")
        row["qty_rpi"] = float(row.get("qty_rpi") or 0)
        row["qty_wip"] = float(row.get("prep_total_size") or 0)
        row["qty_sisa_fg"] = _packing_fg_sisa_qty(
            cur,
            rencana_item_id=rid,
            kode_wip=(row.get("kode_wip") or "").strip(),
        )
        items.append(row)
    cur.close()
    conn.close()
    return jsonify(items)


@api.post("/packing/ukur-sisa")
def packing_ukur_sisa():
    """Simpan hasil pengukuran sisa packing ke Gudang Sisa, sumber FG."""
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    try:
        rencana_item_id = int(body.get("rencana_item_id") or 0)
    except (TypeError, ValueError):
        return _err("rencana_item_id tidak valid")
    if rencana_item_id <= 0:
        return _err("rencana_item_id wajib")

    sizes = []
    for raw in body.get("sizes") or []:
        try:
            size = float(raw)
        except (TypeError, ValueError):
            return _err("ukuran harus angka")
        if size <= 0:
            return _err("ukuran harus > 0")
        sizes.append(size)
    if sizes:
        qty = round(sum(sizes), 2)
    else:
        try:
            qty = float(body.get("qty") or 0)
        except (TypeError, ValueError):
            return _err("qty harus angka")
    if qty <= 0:
        return _err("qty harus > 0")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT i.kode_rencana_item, i.kode_lot_wip, i.material_name, i.color, i.thickness, "
        "pk.kode_wip AS prep_kode_wip, pk.warna AS prep_warna, pk.tebal AS prep_tebal, "
        "pk.treatment_jenis "
        "FROM tbl_rencana_item i "
        "LEFT JOIN tbl_persiapan_kulit pk ON pk.id = ( "
        "  SELECT p2.id FROM tbl_persiapan_kulit p2 "
        "  WHERE p2.rencana_item_id = i.id "
        "  AND p2.status IN ('started', 'saved', 'completed') "
        "  ORDER BY FIELD(p2.status, 'completed', 'saved', 'started'), p2.id DESC "
        "  LIMIT 1 "
        ") "
        "WHERE i.id = %s",
        (rencana_item_id,),
    )
    item = cur.fetchone()
    if not item:
        cur.close()
        conn.close()
        return _err("Item RPI tidak ditemukan", 404)

    material_name = (item.get("material_name") or "").strip() or None
    warna = (item.get("color") or item.get("prep_warna") or "").strip() or None
    tebal = (item.get("thickness") or item.get("prep_tebal") or "").strip() or None
    treatment = (item.get("treatment_jenis") or "").strip()
    if treatment not in ("PU", "Suede"):
        treatment = None
    kode_rpi = (item.get("kode_rencana_item") or "").strip() or None
    kode_wip = (item.get("prep_kode_wip") or item.get("kode_lot_wip") or "").strip() or None
    if not material_name or not warna or not tebal:
        cur.close()
        conn.close()
        return _err("FG sisa wajib punya Material, Warna, dan Tebal dari RPI")

    notes = (body.get("notes") or "").strip() or "Pengukuran sisa packing"
    fg_code = _latest_fg_roll_code_for_wip(cur, kode_wip or "") or (kode_wip or "")
    cur.execute(
        "INSERT INTO tbl_stock_sisa "
        "(sumber, barcode, lot, qty, status, notes, kode_rpi, kode_wip, "
        "material_name, warna, tebal, treatment_jenis) "
        "VALUES ('fg', %s, %s, %s, 'open', %s, %s, %s, %s, %s, %s, %s)",
        (
            fg_code,
            fg_code,
            qty,
            notes,
            kode_rpi,
            kode_wip,
            material_name,
            warna,
            tebal,
            treatment,
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    cur.execute("SELECT * FROM tbl_stock_sisa WHERE id=%s", (new_id,))
    row = _enrich_stock_sisa_fg_row(cur, cur.fetchone())
    cur.close()
    conn.close()
    return jsonify({"ok": True, "id": new_id, "qty": qty, "item": _row(row)}), 201


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
    spec = _attach_so_remark(
        _packing_spec_for_wip(
            cur,
            packing.get("kode_wip") or "",
            packing.get("no_po"),
            packing.get("rencana_item_id"),
        )
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
    pg = parse_page_args(request.args, default_page_size=20)
    # Legacy ``all=1`` kept for callers that still request a wide dump.
    if request.args.get("all") in ("1", "true", "yes") and request.args.get("page") is None:
        pg["page_size"] = min(500, 500)
        pg["limit"] = pg["page_size"]
        pg["offset"] = 0
        pg["page"] = 1
    status = (request.args.get("status") or "").strip()
    where = " WHERE 1=1"
    params: list = []
    if status in ("in_progress", "finished"):
        where += " AND status=%s"
        params.append(status)
    order = order_sql(
        {
            "date_created": "date_created",
            "kode_packing": "kode_packing",
            "kode_wip": "kode_wip",
            "status": "status",
            "id": "id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="date_created DESC",
    )
    cur.execute(f"SELECT COUNT(*) AS c FROM tbl_packing{where}", params)
    total = int((cur.fetchone() or {}).get("c") or 0)
    cur.execute(
        f"SELECT * FROM tbl_packing{where} ORDER BY {order} LIMIT %s OFFSET %s",
        params + [pg["page_size"], pg["offset"]],
    )
    data = _rows(cur.fetchall())
    fg_status_by_packing: dict = {}
    packing_ids = [r.get("id") for r in data if r.get("id") is not None]
    if packing_ids:
        placeholders = ",".join(["%s"] * len(packing_ids))
        cur.execute(
            "SELECT gf.packing_id, gf.status FROM tbl_gudang_fg gf "
            f"INNER JOIN ("
            f"  SELECT packing_id, MAX(id) AS mid FROM tbl_gudang_fg "
            f"  WHERE packing_id IN ({placeholders}) GROUP BY packing_id"
            f") latest ON latest.mid = gf.id",
            packing_ids,
        )
        for fg in cur.fetchall() or []:
            fg_status_by_packing[fg.get("packing_id")] = (fg.get("status") or "").strip()
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
        fg_status = fg_status_by_packing.get(row.get("id")) or ""
        row["fg_status"] = fg_status or None
        # Finished boleh dikoreksi selama FG belum OUT (termasuk jika baris FG belum ada).
        row["can_correct"] = bool(
            row.get("status") == "in_progress"
            or (
                row.get("status") == "finished"
                and fg_status not in ("out", "repacked")
            )
        )
    cur.close()
    conn.close()
    return jsonify(
        page_payload(
            items=data,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


@api.post("/packing")
def packing_start():
    from app import ensure_extended_tables, generate_code

    body = request.get_json(silent=True) or {}
    rencana_item_id = body.get("rencana_item_id")
    stock_sisa_id = body.get("stock_sisa_id")
    source_mode = (body.get("source_mode") or "").strip().lower()
    kode_wip = (body.get("kode_wip") or "").strip()
    no_po = (body.get("no_po") or "").strip()
    no_so = (body.get("no_so") or "").strip()
    customer = (body.get("customer") or "").strip()
    qty_sq = body.get("qty_sq") or 0
    po_id = body.get("po_id")
    sisa_mode = bool(stock_sisa_id) or source_mode in ("sisa", "barang_sisa", "stock_sisa")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    sisa_id_val = None
    item_id_val = None

    if sisa_mode:
        try:
            sisa_id_val = int(stock_sisa_id) if stock_sisa_id is not None else None
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("stock_sisa_id tidak valid")
        if not sisa_id_val:
            cur.close()
            conn.close()
            return _err("stock_sisa_id wajib untuk packing barang sisa")
        cur.execute("SELECT * FROM tbl_stock_sisa WHERE id=%s", (sisa_id_val,))
        sisa = cur.fetchone()
        if not sisa:
            cur.close()
            conn.close()
            return _err("Stock sisa tidak ditemukan", 404)
        if (sisa.get("status") or "").strip().lower() != "approved":
            cur.close()
            conn.close()
            return _err("Hanya stock sisa berstatus approved yang bisa di-packing")
        kode_wip = kode_wip or f"SISA-{sisa_id_val}"
        if sisa.get("po_id") and not po_id:
            po_id = sisa["po_id"]
        if not no_po:
            no_po = f"SISA-{sisa_id_val}"
        if sisa.get("po_id") and (not no_so or no_po.startswith("SISA-")):
            try:
                from erp_http import erp_get

                po = erp_get(f"/po/{int(sisa['po_id'])}")
                if isinstance(po, dict):
                    no_so = no_so or (po.get("po_number") or "").strip()
                    customer = customer or (po.get("customer_name_snapshot") or "")
                    if no_po.startswith("SISA-"):
                        no_po = (
                            po.get("po_customer_ref") or po.get("po_number") or no_po
                        )
            except Exception:
                pass
        qty_sq = qty_sq or float(sisa.get("qty") or 0)
    else:
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
            try:
                po_id_int = int(po_id) if po_id is not None else None
            except (TypeError, ValueError):
                po_id_int = None
            if po_id_int:
                cur.execute(
                    "SELECT po.id AS po_id, po.no_po, po.no_so, po.customer, p.qty_proses AS qty_sq "
                    "FROM tbl_rencana_item_po p "
                    "JOIN tbl_master_po po ON po.id = p.po_id "
                    "WHERE p.item_id = %s AND po.id = %s LIMIT 1",
                    (item_id_val, po_id_int),
                )
            else:
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

    if not kode_wip or not no_po:
        cur.close()
        conn.close()
        return _err("kode_wip dan no_po wajib")

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
    cols = ["kode_packing", "kode_wip", "no_po", "customer", "status"]
    vals: list = [kode_packing, kode_wip, no_po, customer, "in_progress"]
    if item_id_val is not None and "rencana_item_id" in packing_cols:
        cols.append("rencana_item_id")
        vals.append(item_id_val)
    if sisa_id_val is not None and "stock_sisa_id" in packing_cols:
        cols.append("stock_sisa_id")
        vals.append(sisa_id_val)
    placeholders = ",".join(["%s"] * len(vals))
    cur.execute(
        f"INSERT INTO tbl_packing ({', '.join(cols)}) VALUES ({placeholders})",
        tuple(vals),
    )
    packing_id = cur.lastrowid
    try:
        po_id = int(po_id) if po_id is not None else None
    except (TypeError, ValueError):
        po_id = None
    if po_id is None:
        raw_po = body.get("po_id")
        try:
            po_id = int(raw_po) if raw_po is not None else None
        except (TypeError, ValueError):
            po_id = None
    if po_id is None and item_id_val is not None:
        cur.execute(
            "SELECT po_id FROM tbl_rencana_item_po WHERE item_id=%s ORDER BY id LIMIT 1",
            (item_id_val,),
        )
        row_po = cur.fetchone() or {}
        po_id = row_po.get("po_id")
    cur.execute(
        "INSERT INTO tbl_packing_po (packing_id, po_id, no_po, no_so, qty_sq) "
        "VALUES (%s,%s,%s,%s,%s)",
        (packing_id, po_id, no_po, no_so, qty_sq),
    )
    if sisa_id_val is not None:
        cur.execute(
            "UPDATE tbl_stock_sisa SET status='consumed' WHERE id=%s AND status='approved'",
            (sisa_id_val,),
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
            "stock_sisa_id": sisa_id_val,
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
    packing_out = dict(print_payload["packing"])
    packing_out["qty_actual"] = _packing_roll_qty_actual(cur, packing_id)
    cap = _packing_wip_qty_limit(cur, packing)
    if cap is not None:
        packing_out["qty_wip"] = cap[0]
    packing_out["qty_sisa_fg"] = _packing_fg_sisa_qty(
        cur,
        rencana_item_id=packing.get("rencana_item_id"),
        kode_wip=(packing.get("kode_wip") or "").strip(),
    )
    fg_row = _fg_row_for_packing(cur, packing_id)
    fg_status = (fg_row.get("status") or "") if fg_row else ""
    packing_out["fg_id"] = fg_row.get("id") if fg_row else None
    packing_out["fg_status"] = fg_status or None
    # Finished boleh dikoreksi selama FG belum OUT (termasuk jika baris FG belum ada).
    packing_out["can_correct"] = bool(
        packing.get("status") == "in_progress"
        or (packing.get("status") == "finished" and fg_status != "out")
    )
    cur.close()
    conn.close()
    return jsonify(
        {
            "packing": packing_out,
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


def _packing_fg_sisa_qty(cur, *, rencana_item_id, kode_wip: str) -> float:
    """Total qty sisa FG (pengukuran sisa packing) untuk WIP/RPI."""
    kode_wip = (kode_wip or "").strip()
    kode_rpi = None
    if rencana_item_id:
        cur.execute(
            "SELECT kode_rencana_item FROM tbl_rencana_item WHERE id=%s LIMIT 1",
            (int(rencana_item_id),),
        )
        row = cur.fetchone()
        kode_rpi = (row.get("kode_rencana_item") or "").strip() if row else None
    clauses = ["sumber = 'fg'", "COALESCE(status,'open') IN ('open','approved')"]
    params: list = []
    if kode_rpi and kode_wip:
        clauses.append("(kode_rpi = %s OR kode_wip = %s)")
        params.extend([kode_rpi, kode_wip])
    elif kode_wip:
        clauses.append("kode_wip = %s")
        params.append(kode_wip)
    elif kode_rpi:
        clauses.append("kode_rpi = %s")
        params.append(kode_rpi)
    else:
        return 0.0
    cur.execute(
        f"SELECT COALESCE(SUM(qty), 0) AS q FROM tbl_stock_sisa WHERE {' AND '.join(clauses)}",
        tuple(params),
    )
    return round(float((cur.fetchone() or {}).get("q") or 0), 2)


def _packing_roll_qty_actual(cur, packing_id: int) -> float:
    cur.execute(
        "SELECT COALESCE(SUM(ukuran), 0) AS qty FROM tbl_packing_roll WHERE packing_id=%s",
        (int(packing_id),),
    )
    return round(float((cur.fetchone() or {}).get("qty") or 0), 2)


def _packing_wip_qty_limit(cur, packing) -> tuple[float, float] | None:
    """Qty WIP persiapan dan Qty Actual roll in-progress. None untuk packing barang sisa."""
    if packing.get("stock_sisa_id"):
        return None
    rencana_item_id = packing.get("rencana_item_id")
    kode_wip = (packing.get("kode_wip") or "").strip()
    prep = None
    if rencana_item_id:
        cur.execute(
            "SELECT total_size FROM tbl_persiapan_kulit "
            "WHERE rencana_item_id=%s AND status IN ('started','saved','completed') "
            "ORDER BY FIELD(status,'completed','saved','started'), id DESC LIMIT 1",
            (rencana_item_id,),
        )
        prep = cur.fetchone()
    if not prep and kode_wip:
        cur.execute(
            "SELECT total_size FROM tbl_persiapan_kulit "
            "WHERE kode_wip=%s AND status IN ('started','saved','completed') "
            "ORDER BY FIELD(status,'completed','saved','started'), id DESC LIMIT 1",
            (kode_wip,),
        )
        prep = cur.fetchone()
    qty_wip = round(float((prep or {}).get("total_size") or 0), 2)
    qty_actual = 0.0
    if kode_wip:
        cur.execute(
            "SELECT COALESCE(SUM(pr.ukuran), 0) AS qty "
            "FROM tbl_packing p "
            "LEFT JOIN tbl_packing_roll pr ON pr.packing_id = p.id "
            "WHERE p.status = 'in_progress' AND p.kode_wip = %s",
            (kode_wip,),
        )
        qty_actual = round(float((cur.fetchone() or {}).get("qty") or 0), 2)
    return qty_wip, qty_actual


_PACKING_FINISHED_CORRECT_ACTIONS = frozenset(
    {"update_header", "add_roll", "delete_roll", "add_po", "delete_po"}
)


def _fg_row_for_packing(cur, packing_id: int, *, lock: bool = False):
    sql = "SELECT * FROM tbl_gudang_fg WHERE packing_id=%s ORDER BY id DESC LIMIT 1"
    if lock:
        sql += " FOR UPDATE"
    cur.execute(sql, (packing_id,))
    return cur.fetchone()


def _fg_roll_locked_reason(cur, packing_id: int) -> str | None:
    fg = _fg_row_for_packing(cur, packing_id)
    if not fg:
        return None
    status = (fg.get("status") or "").strip()
    if status == "out":
        return "Gudang FG sudah OUT — tidak bisa diedit"
    if status == "repacked":
        return "Gudang FG sudah di-repack — tidak bisa diedit"
    if fg.get("erp_delivery_id"):
        return (
            "Surat jalan sudah menempel. Roll tidak bisa diubah "
            "sampai kaitan surat jalan dilepas."
        )
    return None


def _packing_finished_mutation_error(cur, packing, action: str):
    """None if mutation allowed; error message if blocked.

    Finished packing may still be corrected while Gudang FG is not OUT
    (including when the FG row is missing and will be upserted on sync).
    """
    if (packing.get("status") or "") != "finished":
        return None
    if action == "finish":
        return None
    if action not in _PACKING_FINISHED_CORRECT_ACTIONS:
        return "Packing sudah finished"
    return _fg_roll_locked_reason(cur, packing["id"])


def _sync_gudang_fg_from_packing(cur, packing_id: int) -> None:
    """Buat atau segarkan satu baris FG. Kode FG tidak ikut kode header yang maju."""
    cur.execute("SELECT * FROM tbl_packing WHERE id=%s", (packing_id,))
    pkg = cur.fetchone()
    if not pkg:
        return
    fg = _fg_row_for_packing(cur, packing_id, lock=True)
    if fg and (fg.get("status") or "") in ("out", "repacked"):
        return
    cur.execute(
        "SELECT COUNT(*) AS n, COALESCE(SUM(lembar),0) AS lembar, "
        "COALESCE(SUM(ukuran),0) AS ukuran "
        "FROM tbl_packing_roll WHERE packing_id=%s",
        (packing_id,),
    )
    totals = cur.fetchone() or {}
    n_roll = int(totals.get("n") or 0)
    lembar = int(totals.get("lembar") or 0)
    ukuran = round(float(totals.get("ukuran") or 0), 2)
    if n_roll <= 0:
        if (
            fg
            and (fg.get("status") or "") == "in_stock"
            and not fg.get("erp_delivery_id")
        ):
            cur.execute(
                "DELETE FROM tbl_gudang_fg WHERE id=%s AND status='in_stock'",
                (fg["id"],),
            )
        return
    if fg and (fg.get("status") or "") == "in_stock":
        cur.execute(
            "UPDATE tbl_gudang_fg SET kode_wip=%s, customer=%s, "
            "total_lembar=%s, total_ukuran=%s "
            "WHERE id=%s AND status='in_stock'",
            (
                pkg.get("kode_wip"),
                pkg.get("customer"),
                lembar,
                ukuran,
                fg["id"],
            ),
        )
        return
    kode = (pkg.get("kode_packing") or "").strip()
    if not kode or _fg_kode_used_by_other(cur, kode, packing_id):
        kode = _alloc_unique_fg_code(cur)
    cur.execute(
        "INSERT INTO tbl_gudang_fg "
        "(packing_id, kode_packing, kode_wip, customer, total_lembar, total_ukuran, status) "
        "VALUES (%s,%s,%s,%s,%s,%s,'in_stock')",
        (
            packing_id,
            kode,
            pkg.get("kode_wip"),
            pkg.get("customer"),
            lembar,
            ukuran,
        ),
    )


def _fg_kode_used_by_other(cur, kode: str, packing_id: int) -> bool:
    cur.execute(
        "SELECT id FROM tbl_gudang_fg WHERE TRIM(kode_packing)=%s AND packing_id<>%s LIMIT 1",
        ((kode or "").strip(), int(packing_id)),
    )
    return cur.fetchone() is not None


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
    finished_err = _packing_finished_mutation_error(cur, packing, action)
    if finished_err:
        cur.close()
        conn.close()
        return _err(finished_err)

    msg = "ok"
    sync_fg = False
    if action == "update_header":
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
        sync_fg = packing["status"] == "finished"

    elif action == "add_roll":
        locked = _fg_roll_locked_reason(cur, packing_id)
        if locked:
            cur.close()
            conn.close()
            return _err(locked)
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
        sync_fg = True

    elif action == "print_roll_label":
        locked = _fg_roll_locked_reason(cur, packing_id)
        if locked:
            cur.close()
            conn.close()
            return _err(locked)
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
        ukuran = round(sum(parsed_sizes), 2)
        overage_warn = None
        cap = _packing_wip_qty_limit(cur, packing)
        if cap is not None:
            qty_wip, qty_actual = cap
            projected = round(ukuran + qty_actual, 2)
            if projected > qty_wip + 1e-9:
                overage_warn = {
                    "ukuran": ukuran,
                    "qty_actual": qty_actual,
                    "qty_wip": qty_wip,
                    "projected": projected,
                    "overage": round(projected - qty_wip, 2),
                }
        cur.execute(
            "SELECT COALESCE(MAX(roll_no),0)+1 AS nxt FROM tbl_packing_roll WHERE packing_id=%s",
            (packing_id,),
        )
        roll_no = int(cur.fetchone()["nxt"])
        remark = (body.get("remark") or "").strip() or None
        impactiva = (body.get("impactiva_grading") or "").strip() or None
        moisture = (body.get("moisture") or "").strip() or None
        sizes_text = "+".join(_format_label_size_part(v) for v in parsed_sizes)
        from app import _col_names

        roll_kode = (packing.get("kode_packing") or "").strip()
        if not roll_kode:
            roll_kode = _alloc_unique_fg_code(cur)
        next_kode = _alloc_unique_fg_code(cur)
        roll_cols = _col_names(cur, "tbl_packing_roll")
        if "kode_packing" in roll_cols and "sizes_text" in roll_cols:
            grade_cols = "impactiva_grading" in roll_cols and "moisture" in roll_cols
            if grade_cols:
                cur.execute(
                    "INSERT INTO tbl_packing_roll "
                    "(packing_id, roll_no, lembar, ukuran, remark, kode_packing, sizes_text, "
                    "impactiva_grading, moisture) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                        packing_id,
                        roll_no,
                        lembar,
                        ukuran,
                        remark,
                        roll_kode,
                        sizes_text,
                        impactiva,
                        moisture,
                    ),
                )
            else:
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
        _sync_gudang_fg_from_packing(cur, packing_id)
        conn.commit()
        cur.execute("SELECT * FROM tbl_packing WHERE id=%s", (packing_id,))
        pkg = cur.fetchone()
        cur.execute(
            "SELECT * FROM tbl_packing_roll WHERE packing_id=%s AND roll_no=%s",
            (packing_id, roll_no),
        )
        roll_row = cur.fetchone()
        spec = _attach_so_remark(
            _packing_spec_for_wip(
                cur,
                pkg.get("kode_wip") or "",
                pkg.get("no_po"),
                pkg.get("rencana_item_id"),
            )
        )
        pkg_label = dict(pkg)
        pkg_label["kode_packing"] = roll_kode
        label = _packing_roll_label_payload(_row(pkg_label), _row(roll_row), spec, parsed_sizes)
        next_roll = roll_no + 1
        cur.close()
        conn.close()
        payload = {
            "ok": True,
            "message": f"Label roll #{roll_no} siap cetak",
            "roll_no": roll_no,
            "roll_kode_packing": roll_kode,
            "next_roll_no": next_roll,
            "kode_packing": next_kode,
            "label": label,
        }
        if overage_warn:
            payload["wip_overage"] = overage_warn
            payload["warning"] = (
                f"Qty packing ({overage_warn['projected']}) melebihi Qty WIP "
                f"({overage_warn['qty_wip']}) sebanyak {overage_warn['overage']}."
            )
        return jsonify(payload)

    elif action == "delete_roll":
        locked = _fg_roll_locked_reason(cur, packing_id)
        if locked:
            cur.close()
            conn.close()
            return _err(locked)
        roll_id = body.get("roll_id")
        if packing["status"] == "finished":
            cur.execute(
                "SELECT COUNT(*) AS n FROM tbl_packing_roll WHERE packing_id=%s",
                (packing_id,),
            )
            n_roll = int((cur.fetchone() or {}).get("n") or 0)
            if n_roll <= 1:
                cur.close()
                conn.close()
                return _err("Packing finished harus menyisakan minimal satu roll")
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
        sync_fg = True

    elif action == "add_po":
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
            raw_sid = body.get("source_detail_id")
            try:
                sid = int(raw_sid) if raw_sid is not None else None
            except (TypeError, ValueError):
                sid = None
            if sid is not None:
                cur.execute(
                    "SELECT id FROM tbl_master_po WHERE source_detail_id=%s LIMIT 1",
                    (sid,),
                )
                row_po = cur.fetchone() or {}
                po_id = row_po.get("id")
            if po_id is None and packing.get("rencana_item_id"):
                cur.execute(
                    "SELECT po_id FROM tbl_rencana_item_po WHERE item_id=%s ORDER BY id LIMIT 1",
                    (packing.get("rencana_item_id"),),
                )
                row_po = cur.fetchone() or {}
                po_id = row_po.get("po_id")
        cur.execute(
            "INSERT INTO tbl_packing_po (packing_id, po_id, no_po, no_so, qty_sq) "
            "VALUES (%s,%s,%s,%s,%s)",
            (packing_id, po_id, no_po, no_so, qty_sq),
        )
        msg = "PO ditambahkan"

    elif action == "delete_po":
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
            # Qty Actual boleh melebihi Qty WIP; warning kelebihan ditangani di UI.
            cur.execute(
                "UPDATE tbl_packing SET status='finished', date_finished=NOW() WHERE id=%s",
                (packing_id,),
            )
        msg = "Finish Good selesai. Masuk Gudang FG."
        sync_fg = True

    else:
        cur.close()
        conn.close()
        return _err(f"action tidak dikenal: {action}")

    if sync_fg:
        _sync_gudang_fg_from_packing(cur, packing_id)

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "message": msg})


# ---- stock sisa / gudang sisa ----
_STOCK_SISA_SUMBER = ("kimia", "kulit", "wip", "fg")
_STOCK_SISA_STATUS = ("open", "reserved", "consumed", "approved")


def _looks_like_fg_packing_code(code: str) -> bool:
    return (code or "").strip().upper().startswith("FG")


def _latest_fg_roll_code_for_wip(cur, kode_wip: str) -> str:
    kode_wip = (kode_wip or "").strip()
    if not kode_wip:
        return ""
    cur.execute(
        "SELECT pr.kode_packing FROM tbl_packing_roll pr "
        "INNER JOIN tbl_packing p ON p.id = pr.packing_id "
        "WHERE TRIM(p.kode_wip) = %s AND TRIM(COALESCE(pr.kode_packing, '')) <> '' "
        "ORDER BY pr.id DESC LIMIT 1",
        (kode_wip,),
    )
    row = cur.fetchone()
    if row and row.get("kode_packing"):
        return str(row["kode_packing"]).strip()
    return ""


def _fg_packing_display_code(cur, row: dict) -> str:
    """Kode packing FG (FGxxx) untuk baris stock sisa FG."""
    row = row or {}
    for raw in (row.get("barcode"), row.get("lot")):
        c = (raw or "").strip()
        if _looks_like_fg_packing_code(c):
            return c
    kode_wip = (row.get("kode_wip") or "").strip()
    roll_code = _latest_fg_roll_code_for_wip(cur, kode_wip) if kode_wip else ""
    if roll_code:
        return roll_code
    resolved = _resolve_fg_sisa_from_packing(
        cur, row.get("barcode") or row.get("lot") or kode_wip
    )
    kp = (resolved.get("kode_packing") or "").strip()
    if _looks_like_fg_packing_code(kp):
        return kp
    return roll_code or kp or ""


def _resolve_fg_sisa_from_packing(cur, barcode: str) -> dict:
    code = (barcode or "").strip()
    if not code:
        return {}
    cur.execute(
        "SELECT p.kode_wip, p.kode_packing, p.rencana_item_id, "
        "ri.kode_rencana_item, ri.material_name, ri.color, ri.thickness, "
        "pk.treatment_jenis "
        "FROM tbl_packing p "
        "LEFT JOIN tbl_persiapan_kulit pk ON pk.kode_wip = p.kode_wip "
        "LEFT JOIN tbl_rencana_item ri ON ri.id = COALESCE(p.rencana_item_id, pk.rencana_item_id) "
        "WHERE TRIM(p.kode_packing) = %s OR TRIM(p.kode_wip) = %s "
        "ORDER BY p.id DESC LIMIT 1",
        (code, code),
    )
    row = cur.fetchone()
    if not row:
        cur.execute(
            "SELECT gf.kode_wip, gf.kode_packing, p.rencana_item_id, "
            "ri.kode_rencana_item, ri.material_name, ri.color, ri.thickness, "
            "pk.treatment_jenis "
            "FROM tbl_gudang_fg gf "
            "LEFT JOIN tbl_packing p ON p.id = gf.packing_id "
            "LEFT JOIN tbl_persiapan_kulit pk ON pk.kode_wip = gf.kode_wip "
            "LEFT JOIN tbl_rencana_item ri ON ri.id = COALESCE(p.rencana_item_id, pk.rencana_item_id) "
            "WHERE TRIM(gf.kode_packing) = %s "
            "ORDER BY gf.id DESC LIMIT 1",
            (code,),
        )
        row = cur.fetchone()
    if not row:
        return {}
    kode_wip = (row.get("kode_wip") or "").strip()
    kode_packing = (row.get("kode_packing") or "").strip()
    if not _looks_like_fg_packing_code(kode_packing) and kode_wip:
        kode_packing = _latest_fg_roll_code_for_wip(cur, kode_wip) or kode_packing
    return {
        "kode_wip": row.get("kode_wip"),
        "kode_rpi": row.get("kode_rencana_item"),
        "kode_packing": kode_packing,
        "material_name": row.get("material_name"),
        "warna": row.get("color"),
        "tebal": row.get("thickness"),
        "treatment_jenis": row.get("treatment_jenis"),
    }


def _merge_fg_sisa_fields(row: dict, resolved: dict) -> dict:
    out = dict(row or {})
    for key in (
        "kode_rpi",
        "kode_wip",
        "kode_packing",
        "material_name",
        "warna",
        "tebal",
        "treatment_jenis",
    ):
        if not (out.get(key) or "").strip() and resolved.get(key):
            out[key] = resolved.get(key)
    return out


def _enrich_stock_sisa_fg_row(cur, row: dict) -> dict:
    if (row or {}).get("sumber") != "fg":
        return row
    resolved = _resolve_fg_sisa_from_packing(cur, row.get("barcode") or row.get("lot"))
    out = _merge_fg_sisa_fields(row, resolved)
    out["kode_packing"] = _fg_packing_display_code(cur, out)
    return out


def _fg_sisa_outstanding_po_rows(cur, row: dict) -> list[dict]:
    from spek_match import filter_master_po_by_spek

    material = (row.get("material_name") or "").strip()
    warna = (row.get("warna") or "").strip()
    tebal = (row.get("tebal") or "").strip()
    if not material or not warna or not tebal:
        return []
    cur.execute(
        "SELECT id, no_po, no_so, customer, item_name, tebal, warna, emboss, color_swatch, "
        "sq_ft, qty_order, qty_processed, qty_balance_erp, source_detail_id, lot_number, status, "
        "(qty_order - qty_processed) AS qty_outstanding "
        "FROM tbl_master_po "
        "WHERE status IN ('outstanding','partial') "
        "ORDER BY no_po, item_name LIMIT 500"
    )
    items = filter_master_po_by_spek(
        _rows(cur.fetchall()),
        material_name=material,
        thickness=tebal,
        color=warna,
    )
    for item in items:
        item["qty_outstanding"] = max(
            0.0,
            float(item.get("qty_order") or 0) - float(item.get("qty_processed") or 0),
        )
    return [it for it in items if float(it.get("qty_outstanding") or 0) > 1e-9]


@api.get("/stock-sisa/<int:sisa_id>/fg-outstanding-so")
@api.get("/gudang-sisa/<int:sisa_id>/fg-outstanding-so")
def stock_sisa_fg_outstanding_so(sisa_id: int):
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_stock_sisa WHERE id=%s", (sisa_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return _err("Stock sisa tidak ditemukan", 404)
    if row.get("sumber") != "fg":
        cur.close()
        conn.close()
        return _err("Hanya untuk stock sisa FG")
    row = _enrich_stock_sisa_fg_row(cur, row)
    items = _fg_sisa_outstanding_po_rows(cur, row)
    cur.close()
    conn.close()
    return jsonify(
        {
            "ok": True,
            "sisa": _row(row),
            "items": items,
            "spec": {
                "material_name": row.get("material_name"),
                "warna": row.get("warna"),
                "tebal": row.get("tebal"),
                "treatment_jenis": row.get("treatment_jenis"),
            },
        }
    )


@api.get("/stock-sisa")
@api.get("/gudang-sisa")
def stock_sisa_list():
    from app import ensure_extended_tables

    status = (request.args.get("status") or "").strip().lower()
    sumber = (request.args.get("sumber") or "").strip().lower()
    q = (request.args.get("q") or "").strip()
    pg = parse_page_args(request.args, default_page_size=20)
    order = order_sql(
        {
            "created_at": "created_at",
            "barcode": "barcode",
            "lot": "lot",
            "status": "status",
            "sumber": "sumber",
            "id": "id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="created_at DESC, id DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    where = " WHERE 1=1"
    params: list = []
    if status in _STOCK_SISA_STATUS:
        where += " AND status=%s"
        params.append(status)
    if sumber in _STOCK_SISA_SUMBER:
        where += " AND sumber=%s"
        params.append(sumber)
    if q:
        like = f"%{q}%"
        where += (
            " AND (IFNULL(barcode,'') LIKE %s OR IFNULL(lot,'') LIKE %s "
            "OR IFNULL(notes,'') LIKE %s OR IFNULL(sumber,'') LIKE %s)"
        )
        params.extend([like, like, like, like])
    cur.execute(f"SELECT COUNT(*) AS c FROM tbl_stock_sisa{where}", params)
    total = int((cur.fetchone() or {}).get("c") or 0)
    cur.execute(
        f"SELECT * FROM tbl_stock_sisa{where} ORDER BY {order} LIMIT %s OFFSET %s",
        params + [pg["page_size"], pg["offset"]],
    )
    data = _rows(cur.fetchall())
    if sumber == "fg":
        data = [_enrich_stock_sisa_fg_row(cur, row) for row in data]
    cur.close()
    conn.close()
    return jsonify(
        page_payload(
            items=data,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


@api.post("/stock-sisa")
@api.post("/gudang-sisa")
def stock_sisa_create():
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    sumber = (body.get("sumber") or "").strip().lower()
    if sumber not in _STOCK_SISA_SUMBER:
        return _err("sumber harus kimia|kulit|wip|fg")
    try:
        qty = float(body.get("qty") or 0)
    except (TypeError, ValueError):
        return _err("qty harus angka")
    if qty <= 0:
        return _err("qty harus > 0")
    barcode = (body.get("barcode") or "").strip() or None
    lot = (body.get("lot") or "").strip() or None
    notes = (body.get("notes") or "").strip() or None
    status = (body.get("status") or "open").strip().lower()
    if status not in _STOCK_SISA_STATUS:
        return _err("status tidak valid")
    po_id = body.get("po_id")
    try:
        po_id = int(po_id) if po_id is not None else None
    except (TypeError, ValueError):
        return _err("po_id tidak valid")

    kode_rpi = (body.get("kode_rpi") or "").strip() or None
    kode_wip = (body.get("kode_wip") or "").strip() or None
    material_name = (body.get("material_name") or "").strip() or None
    warna = (body.get("warna") or body.get("color") or "").strip() or None
    tebal = (body.get("tebal") or body.get("thickness") or "").strip() or None
    treatment_jenis = (body.get("treatment_jenis") or body.get("jenis") or "").strip() or None
    if treatment_jenis and treatment_jenis not in ("PU", "Suede"):
        return _err("treatment_jenis harus PU atau Suede")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    if sumber == "fg":
        resolved = _resolve_fg_sisa_from_packing(cur, barcode or lot or "")
        merged = _merge_fg_sisa_fields(
            {
                "kode_rpi": kode_rpi,
                "kode_wip": kode_wip,
                "material_name": material_name,
                "warna": warna,
                "tebal": tebal,
                "treatment_jenis": treatment_jenis,
            },
            resolved,
        )
        kode_rpi = merged.get("kode_rpi")
        kode_wip = merged.get("kode_wip")
        material_name = merged.get("material_name")
        warna = merged.get("warna")
        tebal = merged.get("tebal")
        treatment_jenis = merged.get("treatment_jenis")
        if not material_name or not warna or not tebal:
            cur.close()
            conn.close()
            return _err("FG sisa wajib punya Material, Warna, dan Tebal (isi manual atau scan kode packing)")

    cur.execute(
        "INSERT INTO tbl_stock_sisa "
        "(sumber, barcode, lot, qty, status, po_id, notes, kode_rpi, kode_wip, "
        "material_name, warna, tebal, treatment_jenis) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            sumber,
            barcode,
            lot,
            qty,
            status,
            po_id,
            notes,
            kode_rpi,
            kode_wip,
            material_name,
            warna,
            tebal,
            treatment_jenis,
        ),
    )
    new_id = cur.lastrowid
    conn.commit()
    cur.execute("SELECT * FROM tbl_stock_sisa WHERE id=%s", (new_id,))
    row = _enrich_stock_sisa_fg_row(cur, cur.fetchone())
    cur.close()
    conn.close()
    return jsonify(_row(row)), 201


@api.put("/stock-sisa/<int:sisa_id>")
@api.put("/gudang-sisa/<int:sisa_id>")
def stock_sisa_update(sisa_id: int):
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    cur.execute("SELECT * FROM tbl_stock_sisa WHERE id=%s", (sisa_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return _err("Stock sisa tidak ditemukan", 404)

    sumber = row.get("sumber")
    if "sumber" in body:
        sumber = (body.get("sumber") or "").strip().lower()
        if sumber not in _STOCK_SISA_SUMBER:
            cur.close()
            conn.close()
            return _err("sumber harus kimia|kulit|wip|fg")
    status = row.get("status")
    if "status" in body:
        status = (body.get("status") or "").strip().lower()
        if status not in _STOCK_SISA_STATUS:
            cur.close()
            conn.close()
            return _err("status tidak valid")
    qty = row.get("qty")
    if "qty" in body:
        try:
            qty = float(body.get("qty") or 0)
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("qty harus angka")
        if qty <= 0:
            cur.close()
            conn.close()
            return _err("qty harus > 0")
    barcode = row.get("barcode")
    if "barcode" in body:
        barcode = (body.get("barcode") or "").strip() or None
    lot = row.get("lot")
    if "lot" in body:
        lot = (body.get("lot") or "").strip() or None
    notes = row.get("notes")
    if "notes" in body:
        notes = (body.get("notes") or "").strip() or None
    po_id = row.get("po_id")
    if "po_id" in body:
        try:
            po_id = int(body.get("po_id")) if body.get("po_id") is not None else None
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("po_id tidak valid")

    cur.execute(
        "UPDATE tbl_stock_sisa SET sumber=%s, barcode=%s, lot=%s, qty=%s, "
        "status=%s, po_id=%s, notes=%s WHERE id=%s",
        (sumber, barcode, lot, qty, status, po_id, notes, sisa_id),
    )
    conn.commit()
    cur.execute("SELECT * FROM tbl_stock_sisa WHERE id=%s", (sisa_id,))
    updated = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(_row(updated))


@api.post("/stock-sisa/<int:sisa_id>/actions")
@api.post("/gudang-sisa/<int:sisa_id>/actions")
def stock_sisa_actions(sisa_id: int):
    """Actions: reserve (Ajukan SO), approve, sync-ppic, consume."""
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    action = (body.get("action") or "").strip().lower()
    if not action:
        return _err("action wajib")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    cur.execute("SELECT * FROM tbl_stock_sisa WHERE id=%s", (sisa_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return _err("Stock sisa tidak ditemukan", 404)

    msg = "ok"
    if action in ("ajukan-so", "reserve"):
        if (row.get("status") or "").lower() not in ("open", "reserved"):
            cur.close()
            conn.close()
            return _err("Hanya status open/reserved yang bisa diajukan SO")
        po_id = body.get("po_id")
        try:
            po_id = int(po_id) if po_id is not None else None
        except (TypeError, ValueError):
            po_id = None
        # Jika po_id belum ada, coba buat draft SO via ERP (butuh role marketing di service token → fallback).
        if not po_id:
            try:
                from erp_http import erp_post

                notes = (body.get("notes") or row.get("notes") or "").strip()
                payload = {
                    "status": "draft",
                    "po_category": "production",
                    "customer_name_snapshot": (body.get("customer_name") or "STOCK SISA").strip(),
                    "po_customer_ref": f"SISA-{sisa_id}",
                    "order_type_label": "stock-sisa",
                }
                if body.get("customer_id"):
                    payload["customer_id"] = int(body["customer_id"])
                created = erp_post("/po", json=payload)
                if isinstance(created, dict) and created.get("id"):
                    po_id = int(created["id"])
                    # Confirm + assign PPIC bila memungkinkan
                    try:
                        from erp_http import erp_put, erp_post as erp_post2

                        erp_put(f"/po/{po_id}", json={"status": "confirmed"})
                        erp_post2(
                            f"/workflow/po/{po_id}/assign-to-ppic",
                            json={"notes": notes or f"Ajukan SO dari stock sisa #{sisa_id}"},
                        )
                    except Exception:
                        pass
            except Exception as exc:
                cur.close()
                conn.close()
                return _err(
                    f"Buat SO gagal ({exc}). Kirim po_id dari UI setelah createPo + assign PPIC."
                )
        if not po_id:
            cur.close()
            conn.close()
            return _err("po_id wajib (atau buat SO dulu di ERP)")
        notes = (body.get("notes") or row.get("notes") or "").strip() or None
        cur.execute(
            "UPDATE tbl_stock_sisa SET status='reserved', po_id=%s, notes=%s WHERE id=%s",
            (po_id, notes, sisa_id),
        )
        msg = f"Stock sisa reserved ke PO #{po_id}"

    elif action == "approve":
        cur.execute(
            "UPDATE tbl_stock_sisa SET status='approved' WHERE id=%s",
            (sisa_id,),
        )
        msg = "Stock sisa approved — siap packing ulang"

    elif action == "sync-ppic":
        po_id = row.get("po_id")
        if not po_id:
            cur.close()
            conn.close()
            return _err("Belum ada po_id untuk sync PPIC")
        try:
            from erp_http import erp_get

            assignment = erp_get(f"/workflow/po/{int(po_id)}/ppic-assignment")
        except Exception as exc:
            cur.close()
            conn.close()
            return _err(f"Gagal cek PPIC assignment: {exc}")
        st = ""
        if isinstance(assignment, dict):
            st = (assignment.get("status") or "").strip().lower()
        if st == "completed":
            cur.execute(
                "UPDATE tbl_stock_sisa SET status='approved' WHERE id=%s AND status='reserved'",
                (sisa_id,),
            )
            msg = "PPIC completed → stock sisa approved"
        else:
            msg = f"PPIC status={st or 'none'} — belum approved"

    elif action == "consume":
        cur.execute(
            "UPDATE tbl_stock_sisa SET status='consumed' WHERE id=%s",
            (sisa_id,),
        )
        msg = "Stock sisa consumed"

    elif action in ("assign-so-fg", "assign_so_fg"):
        from app import _recompute_master_po_qty_processed

        if row.get("sumber") != "fg":
            cur.close()
            conn.close()
            return _err("Assign SO hanya untuk stock sisa FG")
        if (row.get("status") or "").lower() == "consumed":
            cur.close()
            conn.close()
            return _err("Stock sisa FG sudah habis")
        row = _enrich_stock_sisa_fg_row(cur, row)
        try:
            po_id = int(body.get("po_id"))
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("po_id wajib")
        try:
            assign_qty = float(body.get("qty") or 0)
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("qty harus angka")
        if assign_qty <= 0:
            cur.close()
            conn.close()
            return _err("qty harus > 0")
        sisa_qty = float(row.get("qty") or 0)
        if assign_qty > sisa_qty + 1e-9:
            cur.close()
            conn.close()
            return _err(f"Qty assign ({assign_qty}) melebihi sisa stok ({sisa_qty})")
        matches = _fg_sisa_outstanding_po_rows(cur, row)
        match_ids = {int(m.get("id") or 0) for m in matches}
        if po_id not in match_ids:
            cur.close()
            conn.close()
            return _err("SO tidak outstanding atau spek tidak cocok (Material/Warna/Tebal)")
        cur.execute("SELECT * FROM tbl_master_po WHERE id=%s", (po_id,))
        po = cur.fetchone()
        if not po:
            cur.close()
            conn.close()
            return _err("SO tidak ditemukan", 404)
        outstanding = float(po.get("qty_order") or 0) - float(po.get("qty_processed") or 0)
        if assign_qty > outstanding + 1e-9:
            cur.close()
            conn.close()
            return _err(f"Qty melebihi outstanding SO ({outstanding})")
        notes = (body.get("notes") or "").strip() or None
        cur.execute(
            "INSERT INTO tbl_stock_sisa_fg_assign (sisa_id, po_id, qty, notes) "
            "VALUES (%s,%s,%s,%s)",
            (sisa_id, po_id, assign_qty, notes),
        )
        assign_id = cur.lastrowid
        new_qty = round(sisa_qty - assign_qty, 3)
        new_status = "consumed" if new_qty <= 1e-9 else "open"
        cur.execute(
            "UPDATE tbl_stock_sisa SET qty=%s, status=%s WHERE id=%s",
            (max(0.0, new_qty), new_status, sisa_id),
        )
        new_processed = _recompute_master_po_qty_processed(cur, po_id)
        msg = (
            f"Assign {assign_qty} ke SO {po.get('no_po') or po_id} — "
            f"terkirim (qty_processed={new_processed})"
        )
        row = dict(row)
        row["qty"] = max(0.0, new_qty)
        row["status"] = new_status
        conn.commit()
        cur.execute("SELECT * FROM tbl_stock_sisa WHERE id=%s", (sisa_id,))
        updated = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify(
            {
                "ok": True,
                "message": msg,
                "row": _row(updated),
                "assign_id": assign_id,
                "po_id": po_id,
                "qty_assigned": assign_qty,
                "qty_processed": new_processed,
            }
        )

    else:
        cur.close()
        conn.close()
        return _err("action harus ajukan-so|reserve|approve|sync-ppic|consume|assign-so-fg")

    conn.commit()
    cur.execute("SELECT * FROM tbl_stock_sisa WHERE id=%s", (sisa_id,))
    updated = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "message": msg, "row": _row(updated)})


@api.post("/stock-sisa/sync-ppic")
@api.post("/gudang-sisa/sync-ppic")
def stock_sisa_sync_ppic_all():
    """Bulk: reserved + po_id → approved bila PPIC assignment completed."""
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    cur.execute(
        "SELECT id, po_id FROM tbl_stock_sisa WHERE status='reserved' AND po_id IS NOT NULL"
    )
    rows = cur.fetchall() or []
    approved = 0
    try:
        from erp_http import erp_get
    except Exception:
        cur.close()
        conn.close()
        return _err("erp_http tidak tersedia")
    for r in rows:
        try:
            assignment = erp_get(f"/workflow/po/{int(r['po_id'])}/ppic-assignment")
            st = (assignment.get("status") or "").strip().lower() if isinstance(assignment, dict) else ""
            if st == "completed":
                cur.execute(
                    "UPDATE tbl_stock_sisa SET status='approved' WHERE id=%s AND status='reserved'",
                    (r["id"],),
                )
                approved += 1
        except Exception:
            continue
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "checked": len(rows), "approved": approved})


# ---- gudang FG ----
def _enrich_gudang_fg_rows(cur, rows: list) -> list:
    """Isi lot/SO/spek/kode barang/roll_count pada baris Gudang FG (enrich saat baca)."""
    if not rows:
        return rows
    packing_ids: list[int] = []
    seen_pid: set[int] = set()
    for row in rows:
        try:
            pid = int(row.get("packing_id"))
        except (TypeError, ValueError):
            continue
        if pid and pid not in seen_pid:
            seen_pid.add(pid)
            packing_ids.append(pid)

    packing_by_id: dict[int, dict] = {}
    roll_count_by_pid: dict[int, int] = {}
    if packing_ids:
        ph = ",".join(["%s"] * len(packing_ids))
        cur.execute(f"SELECT * FROM tbl_packing WHERE id IN ({ph})", packing_ids)
        for pkg in cur.fetchall() or []:
            try:
                packing_by_id[int(pkg["id"])] = pkg
            except (TypeError, ValueError, KeyError):
                continue
        cur.execute(
            f"SELECT packing_id, COUNT(*) AS n FROM tbl_packing_roll "
            f"WHERE packing_id IN ({ph}) GROUP BY packing_id",
            packing_ids,
        )
        for rr in cur.fetchall() or []:
            try:
                roll_count_by_pid[int(rr["packing_id"])] = int(rr.get("n") or 0)
            except (TypeError, ValueError, KeyError):
                continue

    source_ids: list[int] = []
    specs_by_pid: dict[int, dict] = {}
    for pid, pkg in packing_by_id.items():
        rencana_id = pkg.get("rencana_item_id")
        try:
            rencana_id = int(rencana_id) if rencana_id is not None else None
        except (TypeError, ValueError):
            rencana_id = None
        spec = _packing_spec_for_wip(
            cur,
            pkg.get("kode_wip") or "",
            pkg.get("no_po"),
            rencana_id,
        )
        specs_by_pid[pid] = spec
        sid = spec.get("source_detail_id")
        try:
            sid_i = int(sid) if sid is not None else None
        except (TypeError, ValueError):
            sid_i = None
        if sid_i and sid_i not in source_ids:
            source_ids.append(sid_i)

    item_code_by_sid: dict[int, str] = {}
    if source_ids:
        try:
            from mrp_api import erp_client

            lines = erp_client.po_detail_mrp_lines(source_ids) or {}
            for sid, snap in lines.items():
                try:
                    sid_i = int(sid)
                except (TypeError, ValueError):
                    continue
                if isinstance(snap, dict):
                    code = (snap.get("item_code") or "").strip()
                    if code:
                        item_code_by_sid[sid_i] = code
        except Exception:
            pass

    for row in rows:
        try:
            pid = int(row.get("packing_id"))
        except (TypeError, ValueError):
            pid = None
        spec = specs_by_pid.get(pid) if pid is not None else None
        row["roll_count"] = roll_count_by_pid.get(pid, 0) if pid is not None else 0
        if not spec:
            row.setdefault("lot_no", "")
            row.setdefault("no_so", "")
            row.setdefault("thickness", "")
            row.setdefault("material_name", "")
            row.setdefault("emboss", "")
            row.setdefault("color", "")
            row.setdefault("kode_barang", "")
            continue
        lot = (spec.get("lot_no") or "").strip()
        if lot in ("-",):
            lot = ""
        row["lot_no"] = lot
        row["no_so"] = (spec.get("no_so") or "").strip()
        thick = (spec.get("thickness") or "").strip()
        row["thickness"] = "" if thick in ("", "-") else thick
        row["material_name"] = (spec.get("material_name") or "").strip()
        row["emboss"] = (spec.get("emboss") or "").strip()
        color = (spec.get("color") or "").strip()
        row["color"] = "" if color in ("", "-") else color
        if not (row.get("customer") or "").strip():
            cust = (spec.get("customer_from_rencana") or "").strip()
            if cust:
                row["customer"] = cust
        kode_barang = ""
        sid = spec.get("source_detail_id")
        try:
            sid_i = int(sid) if sid is not None else None
        except (TypeError, ValueError):
            sid_i = None
        if sid_i is not None:
            kode_barang = item_code_by_sid.get(sid_i, "")
        row["kode_barang"] = kode_barang
        row["source_detail_id"] = sid_i
    return rows


@api.get("/gudang-fg")
def gudang_fg_list():
    from app import ensure_extended_tables

    status = (request.args.get("status") or "").strip().lower()
    q = (request.args.get("q") or "").strip()
    pg = parse_page_args(request.args, default_page_size=20)
    order = order_sql(
        {
            "date_in": "gf.date_in",
            "kode_packing": "gf.kode_packing",
            "kode_wip": "gf.kode_wip",
            "status": "gf.status",
            "customer": "gf.customer",
            "id": "gf.id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="gf.date_in DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    from_sql = (
        " FROM tbl_gudang_fg gf "
        "LEFT JOIN tbl_packing p ON p.id = gf.packing_id"
    )
    where = " WHERE 1=1"
    params: list = []
    if status in ("in_stock", "out", "repacked"):
        where += " AND gf.status=%s"
        params.append(status)
    if q:
        like = f"%{q}%"
        where += (
            " AND (gf.kode_packing LIKE %s OR gf.kode_wip LIKE %s OR gf.customer LIKE %s "
            "OR IFNULL(gf.erp_delivery_number,'') LIKE %s OR IFNULL(gf.notes,'') LIKE %s)"
        )
        params.extend([like, like, like, like, like])
    cur.execute(f"SELECT COUNT(*) AS c{from_sql}{where}", params)
    total = int((cur.fetchone() or {}).get("c") or 0)
    cur.execute(
        f"SELECT gf.*, p.status AS packing_status{from_sql}{where} "
        f"ORDER BY {order} LIMIT %s OFFSET %s",
        params + [pg["page_size"], pg["offset"]],
    )
    data = _enrich_gudang_fg_rows(cur, _rows(cur.fetchall()))
    if q:
        qq = q.lower()

        def _match_enrich(row: dict) -> bool:
            blob = " ".join(
                str(row.get(k) or "")
                for k in (
                    "kode_packing",
                    "kode_wip",
                    "customer",
                    "erp_delivery_number",
                    "notes",
                    "lot_no",
                    "no_so",
                    "material_name",
                    "emboss",
                    "color",
                    "thickness",
                    "kode_barang",
                )
            ).lower()
            return qq in blob

        # Page sudah difilter SQL; filter tambahan untuk field enrich di halaman ini.
        data = [r for r in data if _match_enrich(r)]
    cur.close()
    conn.close()
    return jsonify(
        page_payload(
            items=data,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


def _sj_rolls_for_fg(cur, fg: dict) -> list[dict]:
    packing_id = fg.get("packing_id")
    packing_rolls: list[dict] = []
    if packing_id:
        cur.execute(
            "SELECT * FROM tbl_packing_roll WHERE packing_id=%s ORDER BY roll_no, id",
            (int(packing_id),),
        )
        packing_rolls = _rows(cur.fetchall())
    return _sj_rolls_from_packing(fg, packing_rolls)


def _sj_rolls_from_packing(fg: dict, packing_rolls: list | None) -> list[dict]:
    fg_status = (fg.get("status") or "").strip()
    already = fg_status == "out"
    packing_kode = (fg.get("kode_packing") or "").strip()
    out: list[dict] = []
    for r in packing_rolls or []:
        kode_fg = (r.get("kode_packing") or packing_kode or "").strip()
        out.append(
            {
                "roll_id": r.get("id"),
                "fg_id": fg.get("id"),
                "kode_fg": kode_fg,
                "kode_packing": kode_fg,
                "packing_kode": packing_kode,
                "roll_no": r.get("roll_no"),
                "lembar": r.get("lembar"),
                "ukuran": r.get("ukuran"),
                "fg_status": fg_status,
                "scanned": already,
            }
        )
    if not out and packing_kode:
        out.append(
            {
                "roll_id": None,
                "fg_id": fg.get("id"),
                "kode_fg": packing_kode,
                "kode_packing": packing_kode,
                "packing_kode": packing_kode,
                "roll_no": 1,
                "lembar": fg.get("total_lembar"),
                "ukuran": fg.get("total_ukuran"),
                "fg_status": fg_status,
                "scanned": already,
            }
        )
    return out


@api.get("/gudang-fg/surat-jalan/pending")
def gudang_fg_surat_jalan_pending():
    """Customer + SJ yang masih punya FG in_stock (belum diproses OUT)."""
    from app import ensure_extended_tables

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT gf.customer AS customer, "
        "gf.erp_delivery_number AS delivery_number, "
        "gf.erp_delivery_id AS delivery_id, "
        "COUNT(DISTINCT gf.id) AS fg_count, "
        "COUNT(pr.id) AS roll_count "
        "FROM tbl_gudang_fg gf "
        "LEFT JOIN tbl_packing_roll pr ON pr.packing_id = gf.packing_id "
        "WHERE gf.status='in_stock' "
        "AND TRIM(IFNULL(gf.erp_delivery_number,'')) <> '' "
        "GROUP BY gf.customer, gf.erp_delivery_number, gf.erp_delivery_id "
        "ORDER BY gf.customer ASC, gf.erp_delivery_number ASC"
    )
    rows = _rows(cur.fetchall())
    cur.close()
    conn.close()

    grouped: dict[str, dict] = {}
    for row in rows:
        customer = (row.get("customer") or "").strip() or "—"
        bucket = grouped.setdefault(
            customer,
            {"customer": customer, "deliveries": []},
        )
        bucket["deliveries"].append(
            {
                "delivery_number": row.get("delivery_number"),
                "delivery_id": row.get("delivery_id"),
                "fg_count": int(row.get("fg_count") or 0),
                "roll_count": int(row.get("roll_count") or 0) or int(row.get("fg_count") or 0),
            }
        )
    return jsonify({"customers": list(grouped.values())})


@api.get("/gudang-fg/surat-jalan")
def gudang_fg_surat_jalan_lookup():
    """Daftar FG + roll yang terhubung ke nomor surat jalan ERP."""
    from app import ensure_extended_tables

    delivery_number = (
        (request.args.get("q") or request.args.get("delivery_number") or "").strip()
    )
    if not delivery_number:
        return _err("Nomor surat jalan wajib")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT * FROM tbl_gudang_fg "
        "WHERE LOWER(TRIM(IFNULL(erp_delivery_number,''))) = LOWER(%s) "
        "ORDER BY kode_packing ASC",
        (delivery_number,),
    )
    rows = _rows(cur.fetchall())
    rolls: list[dict] = []
    for fg in rows:
        rolls.extend(_sj_rolls_for_fg(cur, fg))
    cur.close()
    conn.close()
    if not rows:
        return _err(f"Surat jalan {delivery_number!r} tidak punya FG terdaftar", 404)
    delivery_id = next(
        (r.get("erp_delivery_id") for r in rows if r.get("erp_delivery_id") is not None),
        None,
    )
    customer = next((r.get("customer") for r in rows if (r.get("customer") or "").strip()), "")
    return jsonify(
        {
            "delivery_number": delivery_number,
            "delivery_id": delivery_id,
            "customer": customer,
            "items": rows,
            "rolls": rolls,
        }
    )


@api.post("/gudang-fg/surat-jalan/out")
def gudang_fg_surat_jalan_out():
    """OUT batch FG setelah scan surat jalan + verifikasi packing."""
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    delivery_number = (body.get("delivery_number") or "").strip()
    fg_ids_raw = body.get("fg_ids") or []
    keterangan = (body.get("keterangan") or "").strip()
    if not delivery_number:
        return _err("delivery_number wajib")
    if not isinstance(fg_ids_raw, list) or not fg_ids_raw:
        return _err("fg_ids wajib (array id FG)")

    fg_ids: list[int] = []
    for raw in fg_ids_raw:
        try:
            fg_ids.append(int(raw))
        except (TypeError, ValueError):
            continue
    if not fg_ids:
        return _err("fg_ids tidak valid")

    note = keterangan or f"Scan SJ {delivery_number}"
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    placeholders = ",".join(["%s"] * len(fg_ids))
    cur.execute(
        f"SELECT * FROM tbl_gudang_fg WHERE id IN ({placeholders})",
        fg_ids,
    )
    rows = {int(r["id"]): r for r in (cur.fetchall() or [])}
    missing = [fid for fid in fg_ids if fid not in rows]
    if missing:
        cur.close()
        conn.close()
        return _err(f"FG tidak ditemukan: {missing}", 404)

    for fid in fg_ids:
        row = rows[fid]
        sj = (row.get("erp_delivery_number") or "").strip()
        if sj and sj.lower() != delivery_number.lower():
            cur.close()
            conn.close()
            return _err(
                f"FG {row.get('kode_packing')} tidak termasuk SJ {delivery_number}",
                400,
            )

    out_ids: list[int] = []
    skipped: list[dict] = []
    for fid in fg_ids:
        row = rows[fid]
        if row.get("status") == "out":
            skipped.append({"id": fid, "kode_packing": row.get("kode_packing"), "reason": "already_out"})
            continue
        if row.get("status") != "in_stock":
            skipped.append({"id": fid, "kode_packing": row.get("kode_packing"), "reason": "invalid_status"})
            continue
        blocked = _fg_packing_not_finished(cur, row)
        if blocked:
            cur.close()
            conn.close()
            return _err(blocked)
        cur.execute(
            "UPDATE tbl_gudang_fg SET status='out', date_out=NOW(), keterangan_out=%s "
            "WHERE id=%s AND status='in_stock'",
            (note[:255], fid),
        )
        if cur.rowcount:
            out_ids.append(fid)

    conn.commit()
    cur.close()
    conn.close()
    return jsonify(
        {
            "ok": True,
            "delivery_number": delivery_number,
            "out_count": len(out_ids),
            "out_ids": out_ids,
            "skipped": skipped,
        }
    )


def _packing_pos_for_packing_id(cur, packing_id: int) -> list:
    cur.execute(
        "SELECT pp.*, "
        "COALESCE(mp1.source_detail_id, mp2.source_detail_id) AS source_detail_id, "
        "COALESCE(mp1.item_name, mp2.item_name) AS item_name, "
        "COALESCE(mp1.lot_number, mp2.lot_number) AS lot_number "
        "FROM tbl_packing_po pp "
        "LEFT JOIN tbl_master_po mp1 ON mp1.id = pp.po_id "
        "LEFT JOIN tbl_master_po mp2 ON pp.po_id IS NULL AND mp2.id = ("
        "  SELECT id FROM tbl_master_po WHERE no_po = pp.no_po "
        "  ORDER BY id DESC LIMIT 1"
        ") "
        "WHERE pp.packing_id=%s",
        (packing_id,),
    )
    return _attach_erp_lot_no(_rows(cur.fetchall()))


def _lot_tags_for_packing(cur, packing_id: int, kode_wip: str | None = None) -> set[str]:
    tags: set[str] = set()
    wip = (kode_wip or "").strip()
    if not wip and packing_id:
        cur.execute("SELECT kode_wip FROM tbl_packing WHERE id=%s", (packing_id,))
        row = cur.fetchone() or {}
        wip = (row.get("kode_wip") or "").strip()
    if wip:
        tags.add(wip.lower())
    for pp in _packing_pos_for_packing_id(cur, packing_id):
        for key in ("lot_no", "lot_number"):
            v = (pp.get(key) or "").strip()
            if v:
                tags.add(v.lower())
    return tags


def _lot_no_matches_packing(cur, packing_id: int, kode_wip: str | None, lot_no: str) -> bool:
    needle = (lot_no or "").strip().lower()
    if not needle:
        return True
    return needle in _lot_tags_for_packing(cur, packing_id, kode_wip)


def _parse_wip_csv(raw: str | None) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for part in str(raw or "").split(","):
        w = part.strip()
        if not w or w in seen:
            continue
        seen.add(w)
        out.append(w)
    return out[:200]


def _leather_info_for_wip(cur, kode_wip: str) -> dict:
    """Warna kulit + tanggal masuk pabrik (YL/palet IN) untuk satu kode WIP."""
    wip = (kode_wip or "").strip()
    if not wip:
        return {"kode_wip": "", "warna_kulit": "", "tanggal_masuk_pabrik": None}

    pairs: list[tuple[str, str]] = []
    seen_pair: set[tuple[str, str]] = set()

    def _add(palet: str | None, yl: str | None) -> None:
        p = (palet or "").strip()
        y = (yl or "").strip()
        if not p and not y:
            return
        key = (p, y)
        if key in seen_pair:
            return
        seen_pair.add(key)
        pairs.append(key)

    cur.execute(
        "SELECT kode_palet, kode_yl FROM tbl_gudang_mod WHERE kode_wip=%s",
        (wip,),
    )
    for r in cur.fetchall() or []:
        _add(r.get("kode_palet"), r.get("kode_yl"))

    cur.execute(
        "SELECT ps.kode_palet, ps.kode_yl "
        "FROM tbl_persiapan_kulit pk "
        "JOIN tbl_persiapan_scan ps ON ps.persiapan_id = pk.id "
        "WHERE pk.kode_wip=%s",
        (wip,),
    )
    for r in cur.fetchall() or []:
        _add(r.get("kode_palet"), r.get("kode_yl"))

    like = f"%{wip}%"
    cur.execute(
        "SELECT kode_palet, kode_yl FROM tbl_yl_movement "
        "WHERE direction='OUT' AND IFNULL(keterangan,'') LIKE %s",
        (like,),
    )
    for r in cur.fetchall() or []:
        _add(r.get("kode_palet"), r.get("kode_yl"))

    warna = ""
    tgl_masuk = None
    for palet, yl in pairs:
        if not warna and yl:
            if palet:
                cur.execute(
                    "SELECT warna FROM tbl_yl WHERE kode_yl=%s AND kode_palet=%s "
                    "AND IFNULL(warna,'')<>'' ORDER BY id DESC LIMIT 1",
                    (yl, palet),
                )
            else:
                cur.execute(
                    "SELECT warna FROM tbl_yl WHERE kode_yl=%s "
                    "AND IFNULL(warna,'')<>'' ORDER BY id DESC LIMIT 1",
                    (yl,),
                )
            row = cur.fetchone() or {}
            warna = (row.get("warna") or "").strip()
            if not warna:
                cur.execute(
                    "SELECT warna FROM tbl_yl_movement WHERE kode_yl=%s "
                    "AND IFNULL(warna,'')<>'' ORDER BY id ASC LIMIT 1",
                    (yl,),
                )
                row = cur.fetchone() or {}
                warna = (row.get("warna") or "").strip()

        candidates: list = []
        if yl:
            cur.execute(
                "SELECT MIN(tanggal) AS t FROM tbl_yl_movement "
                "WHERE direction='IN' AND kode_yl=%s",
                (yl,),
            )
            candidates.append((cur.fetchone() or {}).get("t"))
        if palet:
            cur.execute(
                "SELECT MIN(tanggal) AS t FROM tbl_palet_movement "
                "WHERE direction='IN' AND kode_palet=%s",
                (palet,),
            )
            candidates.append((cur.fetchone() or {}).get("t"))
            if yl:
                cur.execute(
                    "SELECT MIN(tanggal) AS t FROM tbl_yl_movement "
                    "WHERE direction='IN' AND kode_palet=%s AND kode_yl=%s",
                    (palet, yl),
                )
                candidates.append((cur.fetchone() or {}).get("t"))
        for t in candidates:
            if t is None:
                continue
            if tgl_masuk is None or t < tgl_masuk:
                tgl_masuk = t

    return {
        "kode_wip": wip,
        "warna_kulit": warna,
        "tanggal_masuk_pabrik": _serialize(tgl_masuk) if tgl_masuk is not None else None,
    }


@api.get("/wip-leather-info")
def wip_leather_info():
    """Batch: warna kulit + tanggal masuk pabrik per kode WIP (untuk daftar Delivery ERP)."""
    from app import ensure_extended_tables

    codes = _parse_wip_csv(request.args.get("kode_wip") or request.args.get("lots"))
    if not codes:
        return jsonify({"items": [], "total": 0})
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    items = [_leather_info_for_wip(cur, w) for w in codes]
    cur.close()
    conn.close()
    return jsonify({"items": items, "total": len(items)})


@api.get("/gudang-fg/by-lot")
def gudang_fg_by_lot():
    """Daftar FG in_stock/out whose packing PO lot matches lot_no (marketing outstanding ship)."""
    from app import ensure_extended_tables

    lot_no = (request.args.get("lot_no") or request.args.get("lot") or "").strip()
    if not lot_no:
        return _err("lot_no wajib")
    status = (request.args.get("status") or "in_stock").strip().lower()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    where = " WHERE 1=1"
    params: list = []
    if status in ("in_stock", "out", "repacked"):
        where += " AND status=%s"
        params.append(status)
    cur.execute(f"SELECT * FROM tbl_gudang_fg{where} ORDER BY kode_packing ASC", params)
    rows = _rows(cur.fetchall())
    matched = []
    for fg in rows:
        pid = fg.get("packing_id")
        if not pid:
            continue
        if _lot_no_matches_packing(cur, int(pid), fg.get("kode_wip"), lot_no):
            matched.append(_row(fg))
    cur.close()
    conn.close()
    return jsonify(matched)


@api.get("/gudang-fg/packing-by-delivery-lot")
def gudang_fg_packing_by_delivery_lot():
    """FG + roll/PO packing untuk SJ ERP, difilter lot no baris outstanding."""
    from app import ensure_extended_tables

    delivery_number = (
        (request.args.get("delivery_number") or request.args.get("q") or "").strip()
    )
    lot_no = (request.args.get("lot_no") or request.args.get("lot") or "").strip()
    if not delivery_number:
        return _err("Nomor surat jalan wajib")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute(
        "SELECT * FROM tbl_gudang_fg "
        "WHERE LOWER(TRIM(IFNULL(erp_delivery_number,''))) = LOWER(%s) "
        "ORDER BY kode_packing ASC",
        (delivery_number,),
    )
    fg_rows = _rows(cur.fetchall())
    items: list[dict[str, Any]] = []
    for fg in fg_rows:
        packing_id = fg.get("packing_id")
        if not packing_id:
            continue
        if not _lot_no_matches_packing(
            cur, int(packing_id), fg.get("kode_wip"), lot_no
        ):
            continue
        cur.execute(
            "SELECT * FROM tbl_packing_roll WHERE packing_id=%s ORDER BY roll_no",
            (packing_id,),
        )
        rolls = _rows(cur.fetchall())
        packing_pos = _packing_pos_for_packing_id(cur, int(packing_id))
        items.append(
            {
                "fg": _row(fg),
                "rolls": rolls,
                "packing_pos": packing_pos,
            }
        )
    cur.close()
    conn.close()
    if not fg_rows:
        return _err(f"Surat jalan {delivery_number!r} tidak punya FG terdaftar", 404)
    if lot_no and not items:
        return _err(
            f"Tidak ada packing list FG untuk lot {lot_no!r} pada surat jalan ini",
            404,
        )
    return jsonify(
        {
            "delivery_number": delivery_number,
            "lot_no": lot_no,
            "items": items,
        }
    )


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
    if packing:
        fg["packing_status"] = packing.get("status")
    enriched = _enrich_gudang_fg_rows(cur, [_row(fg)])
    fg_out = enriched[0] if enriched else _row(fg)
    cur.execute(
        "SELECT * FROM tbl_packing_roll WHERE packing_id=%s ORDER BY roll_no",
        (fg["packing_id"],),
    )
    rolls = _rows(cur.fetchall())
    cur.execute(
        "SELECT pp.*, "
        "COALESCE(mp1.source_detail_id, mp2.source_detail_id) AS source_detail_id, "
        "COALESCE(mp1.item_name, mp2.item_name) AS item_name, "
        "COALESCE(mp1.lot_number, mp2.lot_number) AS lot_number "
        "FROM tbl_packing_po pp "
        "LEFT JOIN tbl_master_po mp1 ON mp1.id = pp.po_id "
        "LEFT JOIN tbl_master_po mp2 ON pp.po_id IS NULL AND mp2.id = ("
        "  SELECT id FROM tbl_master_po WHERE no_po = pp.no_po "
        "  ORDER BY id DESC LIMIT 1"
        ") "
        "WHERE pp.packing_id=%s",
        (fg["packing_id"],),
    )
    packing_pos = _attach_erp_lot_no(_rows(cur.fetchall()))
    bridge_lines = []
    if packing:
        cur.execute(
            "SELECT po.source_detail_id, po.no_po, po.no_so, po.item_name, po.lot_number, "
            "p.qty_proses AS qty_sq "
            "FROM tbl_rencana_item i "
            "JOIN tbl_rencana_item_po p ON p.item_id = i.id "
            "JOIN tbl_master_po po ON po.id = p.po_id "
            "WHERE i.kode_lot_wip = %s AND po.source_detail_id IS NOT NULL",
            (packing.get("kode_wip"),),
        )
        bridge_lines = _attach_erp_lot_no(_rows(cur.fetchall()))
    cur.close()
    conn.close()
    return jsonify(
        {
            "fg": fg_out,
            "packing": _row(packing),
            "rolls": rolls,
            "packing_pos": packing_pos,
            "bridge_lines": bridge_lines,
        }
    )


@api.post("/gudang-fg/<int:fg_id>/notes")
def gudang_fg_notes(fg_id: int):
    """Simpan notes manual pada baris stok FG."""
    from app import ensure_extended_tables

    body = request.get_json(silent=True) or {}
    notes_raw = body.get("notes")
    notes = (notes_raw if notes_raw is not None else "").strip() or None

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT id FROM tbl_gudang_fg WHERE id=%s", (fg_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return _err("Data tidak ditemukan", 404)
    cur.execute("UPDATE tbl_gudang_fg SET notes=%s WHERE id=%s", (notes, fg_id))
    conn.commit()
    cur.execute("SELECT * FROM tbl_gudang_fg WHERE id=%s", (fg_id,))
    fg = cur.fetchone()
    enriched = _enrich_gudang_fg_rows(cur, [_row(fg)])
    cur.close()
    conn.close()
    return jsonify({"ok": True, "fg": enriched[0] if enriched else _row(fg)})


def _fg_packing_not_finished(cur, fg) -> str | None:
    """Pesan bila FG belum boleh keluar fisik. None bila packing sudah finished."""
    kode = fg.get("kode_packing") or ""
    if (fg.get("status") or "") == "repacked":
        return f"FG {kode} sudah di-repack"
    packing_id = fg.get("packing_id")
    if not packing_id:
        return "Packing belum selesai"
    cur.execute("SELECT status FROM tbl_packing WHERE id=%s", (int(packing_id),))
    pkg = cur.fetchone()
    if not pkg or (pkg.get("status") or "") != "finished":
        return "Packing belum selesai"
    return None


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
    blocked = _fg_packing_not_finished(cur, fg)
    if blocked:
        cur.close()
        conn.close()
        return _err(blocked)
    cur.execute(
        "UPDATE tbl_gudang_fg SET status='out', date_out=NOW(), keterangan_out=%s, "
        "bridge_status=NULL, bridge_error=NULL WHERE id=%s",
        (keterangan, fg["id"]),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "id": fg["id"], "kode_packing": kode_packing})


def _repack_child_packing(cur, src: dict, kode: str, lembar: int, ukuran: float) -> int:
    from app import _col_names

    cols = set(_col_names(cur, "tbl_packing"))
    no_po = (src.get("no_po") or "").strip() or "-"
    fields = [
        "kode_packing",
        "kode_wip",
        "no_po",
        "customer",
        "status",
        "total_lembar",
        "total_ukuran",
    ]
    vals = [
        kode,
        src.get("kode_wip") or "",
        no_po,
        src.get("customer"),
        "finished",
        int(lembar),
        ukuran,
    ]
    if "rencana_item_id" in cols:
        fields.append("rencana_item_id")
        vals.append(src.get("rencana_item_id"))
    placeholders = ",".join(["%s"] * len(vals))
    date_sql = ", date_finished" if "date_finished" in cols else ""
    date_val = ", NOW()" if "date_finished" in cols else ""
    cur.execute(
        f"INSERT INTO tbl_packing ({', '.join(fields)}{date_sql}) "
        f"VALUES ({placeholders}{date_val})",
        tuple(vals),
    )
    new_id = cur.lastrowid
    cur.execute("SELECT * FROM tbl_packing_po WHERE packing_id=%s", (src["id"],))
    for po in cur.fetchall() or []:
        cur.execute(
            "INSERT INTO tbl_packing_po (packing_id, po_id, no_po, no_so, qty_sq) "
            "VALUES (%s,%s,%s,%s,%s)",
            (
                new_id,
                po.get("po_id"),
                po.get("no_po") or no_po,
                po.get("no_so"),
                po.get("qty_sq") or 0,
            ),
        )
    roll_cols = set(_col_names(cur, "tbl_packing_roll"))
    if "kode_packing" in roll_cols:
        cur.execute(
            "INSERT INTO tbl_packing_roll (packing_id, roll_no, lembar, ukuran, kode_packing) "
            "VALUES (%s,1,%s,%s,%s)",
            (new_id, int(lembar), ukuran, kode),
        )
    else:
        cur.execute(
            "INSERT INTO tbl_packing_roll (packing_id, roll_no, lembar, ukuran) "
            "VALUES (%s,1,%s,%s)",
            (new_id, int(lembar), ukuran),
        )
    return int(new_id)


@api.post("/gudang-fg/<int:fg_id>/repack")
def gudang_fg_repack(fg_id: int):
    from app import ensure_extended_tables
    from fg_repack_rules import validate_repack_lines

    body = request.get_json(silent=True) or {}
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT * FROM tbl_gudang_fg WHERE id=%s FOR UPDATE", (fg_id,))
    fg = cur.fetchone()
    if not fg:
        cur.close()
        conn.close()
        return _err("Data tidak ditemukan", 404)
    if (fg.get("status") or "") != "in_stock":
        cur.close()
        conn.close()
        return _err("Hanya FG in stock yang bisa di-repack")
    if fg.get("erp_delivery_id"):
        cur.close()
        conn.close()
        return _err(
            "Surat jalan sudah menempel. Repack ditolak sampai kaitan surat jalan dilepas."
        )
    blocked = _fg_packing_not_finished(cur, fg)
    if blocked:
        cur.close()
        conn.close()
        return _err(blocked)
    err, lines = validate_repack_lines(
        body.get("lines"), fg.get("total_lembar"), fg.get("total_ukuran")
    )
    if err:
        cur.close()
        conn.close()
        return _err(err)
    cur.execute("SELECT * FROM tbl_packing WHERE id=%s FOR UPDATE", (fg["packing_id"],))
    src = cur.fetchone()
    if not src:
        cur.close()
        conn.close()
        return _err("Packing sumber tidak ditemukan", 404)
    created = []
    for line in lines:
        kode = _alloc_unique_fg_code(cur)
        new_packing_id = _repack_child_packing(
            cur, src, kode, line["lembar"], line["ukuran"]
        )
        cur.execute(
            "INSERT INTO tbl_gudang_fg "
            "(packing_id, kode_packing, kode_wip, customer, total_lembar, total_ukuran, "
            "status, repacked_from_id) "
            "VALUES (%s,%s,%s,%s,%s,%s,'in_stock',%s)",
            (
                new_packing_id,
                kode,
                src.get("kode_wip"),
                src.get("customer"),
                line["lembar"],
                line["ukuran"],
                fg_id,
            ),
        )
        created.append(
            {
                "id": cur.lastrowid,
                "packing_id": new_packing_id,
                "kode_packing": kode,
                "lembar": line["lembar"],
                "ukuran": line["ukuran"],
            }
        )
    cur.execute(
        "UPDATE tbl_gudang_fg SET status='repacked' WHERE id=%s AND status='in_stock'",
        (fg_id,),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, "id": fg_id, "status": "repacked", "created": created})


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
    from dual_gudang import gudang_match_sql, normalize_gudang, parse_gudang_filter

    include_empty = (request.args.get("all") or "").strip().lower() in ("1", "true", "yes")
    q = (request.args.get("q") or "").strip()
    kode_f = (request.args.get("kode") or "").strip()
    gudang_f = parse_gudang_filter(request.args.get("gudang"))
    history_mode = bool(kode_f)
    pg = parse_page_args(request.args, default_page_size=20)
    order_in = order_sql(
        {
            "tanggal_in": "si.tanggal_in",
            "kode_internal": "si.kode_internal",
            "kode_material": "si.kode_material",
            "id": "si.id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="si.tanggal_in DESC, si.id DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    where_in = ""
    params_in: list = []
    if not include_empty:
        where_in += " AND si.qty_sisa > 0"
    if gudang_f:
        gudang_clause, gudang_params = gudang_match_sql("si.gudang", gudang_f)
        where_in += f" AND {gudang_clause}"
        params_in.extend(gudang_params)
    if kode_f:
        where_in += " AND si.kode_material = %s"
        params_in.append(kode_f)
    if q:
        like = f"%{q}%"
        where_in += (
            " AND (si.kode_internal LIKE %s OR IFNULL(si.kode_material,'') LIKE %s "
            "OR IFNULL(si.nama_material,'') LIKE %s OR IFNULL(si.gudang,'') LIKE %s "
            "OR IFNULL(si.lot_number,'') LIKE %s)"
        )
        params_in.extend([like, like, like, like, like])

    summary_where = where_in
    summary_params = list(params_in)
    if not history_mode:
        summary_where += " AND COALESCE(NULLIF(TRIM(si.kode_material), ''), '') <> ''"
        cur.execute(
            f"SELECT COALESCE(si.kode_material, '') AS kode_barang, "
            f"MAX(COALESCE(si.nama_material, '')) AS nama_barang, "
            f"MAX(COALESCE(si.satuan, 'kg')) AS satuan, "
            f"COUNT(*) AS lot_count, "
            f"COALESCE(SUM(si.qty_sisa), 0) AS qty_sisa, "
            f"COALESCE(SUM(si.qty), 0) AS qty_in "
            f"FROM tbl_stok_kimia_in si WHERE 1=1{summary_where} "
            f"GROUP BY COALESCE(si.kode_material, '') "
            f"ORDER BY kode_barang",
            summary_params,
        )
        summary = _rows(cur.fetchall())
        for row in summary:
            row["qty_sisa"] = round(float(row.get("qty_sisa") or 0), 3)
            row["qty_in"] = round(float(row.get("qty_in") or 0), 3)
            row["lot_count"] = int(row.get("lot_count") or 0)
    else:
        summary = []

    cur.execute(
        f"SELECT COUNT(*) AS c, COALESCE(SUM(si.qty_sisa), 0) AS qty_sisa "
        f"FROM tbl_stok_kimia_in si WHERE 1=1{where_in}",
        params_in,
    )
    agg = cur.fetchone() or {}
    total_in = int(agg.get("c") or 0)
    total_qty_sisa = round(float(agg.get("qty_sisa") or 0), 3)
    sql_in = (
        "SELECT si.*, "
        "COALESCE(si.nama_material, '') AS nama_barang, "
        "COALESCE(si.kode_material, '') AS kode_barang, "
        "COALESCE(si.satuan, 'kg') AS satuan "
        f"FROM tbl_stok_kimia_in si WHERE 1=1{where_in} "
        f"ORDER BY {order_in} LIMIT %s OFFSET %s"
    )
    in_limit = 500 if history_mode else pg["page_size"]
    in_offset = 0 if history_mode else pg["offset"]
    cur.execute(sql_in, params_in + [in_limit, in_offset])
    stok_in = _rows(cur.fetchall())
    for row in stok_in:
        row["gudang"] = normalize_gudang(row.get("gudang"))

    sql_out = (
        "SELECT so.*, COALESCE(so.nama_material, si.nama_material, '') AS nama_barang, "
        "COALESCE(so.kode_material, si.kode_material, '') AS kode_barang, "
        "COALESCE(si.kode_internal, '') AS kode_internal "
        "FROM tbl_stok_kimia_out so "
        "LEFT JOIN tbl_stok_kimia_in si ON si.id = so.stok_in_id WHERE 1=1"
    )
    params_out: list = []
    if gudang_f:
        gudang_clause, gudang_params = gudang_match_sql("si.gudang", gudang_f)
        sql_out += f" AND {gudang_clause}"
        params_out.extend(gudang_params)
    if kode_f:
        sql_out += " AND COALESCE(so.kode_material, si.kode_material) = %s"
        params_out.append(kode_f)
    if q:
        like = f"%{q}%"
        sql_out += (
            " AND (IFNULL(so.nama_material,'') LIKE %s OR IFNULL(si.nama_material,'') LIKE %s "
            "OR IFNULL(so.kode_wip,'') LIKE %s OR IFNULL(so.tujuan,'') LIKE %s)"
        )
        params_out.extend([like, like, like, like])
    out_limit = 500 if history_mode else pg["page_size"]
    sql_out += " ORDER BY so.created_at DESC LIMIT %s"
    cur.execute(sql_out, params_out + [out_limit])
    stok_out = _rows(cur.fetchall())

    from erp_raw_materials import list_materials, material_ukuran
    kimia_list = []
    for r in list_materials("kimia"):
        ukuran = material_ukuran(r)
        kimia_list.append(
            {
                "id": r["id"],
                "kode_barang": r["code"],
                "nama_barang": r["name"],
                "satuan": r.get("unit") or "kg",
                "size": ukuran or None,
                "ukuran": ukuran or None,
                "erp_material_id": r["id"],
            }
        )
    cur.close()
    conn.close()
    payload = page_payload(
        items=stok_in,
        total=total_in,
        page=pg["page"],
        page_size=pg["page_size"],
        offset=pg["offset"],
    )
    payload.update(
        {
            "stok_in": stok_in,
            "stok_out": stok_out,
            "summary": summary,
            "kimia_list": kimia_list,
            "gudang": gudang_f,
            "kode": kode_f or None,
            "stats": {
                "lots": total_in,
                "qty_sisa": total_qty_sisa,
                "out_rows": len(stok_out),
            },
        }
    )
    return jsonify(payload)


def _stok_kimia_parse_out_body(body, *, tujuan_default: str):
    try:
        qty = float(body.get("qty") or 0)
    except (TypeError, ValueError):
        return None, _err("qty harus angka")
    if qty <= 0:
        return None, _err("qty harus > 0")
    try:
        jumlah_kemasan = int(body.get("jumlah_kemasan") or 0) or None
    except (TypeError, ValueError):
        return None, _err("jumlah_kemasan harus angka")
    tujuan = (body.get("tujuan") or tujuan_default).strip().lower()
    if tujuan == "mixing":
        tujuan = "lapangan"
    allowed = ("produksi", "return", "lapangan", "keluar")
    if tujuan not in allowed:
        return None, _err("tujuan harus produksi|return|lapangan|keluar")
    ctx = {
        "qty": qty,
        "jumlah_kemasan": jumlah_kemasan,
        "tujuan": tujuan,
        "kode_wip": (body.get("kode_wip") or "").strip() or None,
        "keterangan": (body.get("keterangan") or "").strip() or None,
        "tanggal": body.get("tanggal") or date.today().isoformat(),
    }
    return ctx, None


def _stok_kimia_apply_out_on_lot(cur, stok_in_id: int, qty: float, ctx: dict, *, from_gudang: str) -> dict:
    from dual_gudang import GUDANG_LAPANGAN, is_utama_to_lapangan_out, normalize_gudang

    cur.execute("SELECT * FROM tbl_stok_kimia_in WHERE id=%s FOR UPDATE", (int(stok_in_id),))
    stok = cur.fetchone()
    if not stok:
        raise ValueError("Lot stok tidak ditemukan")
    cur_gudang = normalize_gudang(stok.get("gudang"))
    if cur_gudang != from_gudang:
        raise ValueError(f"Lot ini di gudang {cur_gudang}; aksi ini hanya untuk gudang {from_gudang}")
    erp_id = stok.get("erp_material_id")
    if not erp_id:
        from bridge_metrics import incr

        incr("out_rejected_missing_erp_id")
        raise ValueError("Lot belum ter-map erp_material_id — backfill / pilih material ERP")
    sisa = float(stok["qty_sisa"] or 0)
    if sisa <= 0:
        raise ValueError("Lot sudah habis")
    if qty > sisa + 1e-9:
        raise ValueError(f"Qty OUT ({qty}) melebihi sisa ({sisa})")
    tujuan = ctx["tujuan"]
    tanggal = ctx["tanggal"]
    jumlah_kemasan = ctx["jumlah_kemasan"]
    cur.execute(
        "INSERT INTO tbl_stok_kimia_out "
        "(stok_in_id, kimia_id, erp_material_id, kode_material, nama_material, "
        "qty, jumlah_kemasan, tujuan, kode_wip, tanggal, keterangan) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            int(stok_in_id),
            stok.get("kimia_id") or erp_id,
            erp_id,
            stok.get("kode_material"),
            stok.get("nama_material"),
            qty,
            jumlah_kemasan,
            tujuan,
            ctx["kode_wip"],
            tanggal,
            ctx["keterangan"],
        ),
    )
    out_id = cur.lastrowid
    new_sisa = round(sisa - qty, 3)
    cur.execute(
        "UPDATE tbl_stok_kimia_in SET qty_sisa=%s, gudang=%s WHERE id=%s",
        (new_sisa, cur_gudang, int(stok_in_id)),
    )
    lapangan_lot = None
    bridge = None
    if is_utama_to_lapangan_out(from_gudang=from_gudang, tujuan=tujuan):
        from app import generate_code

        kode_internal = generate_code("BC-K")
        cur.execute(
            "INSERT INTO tbl_stok_kimia_in "
            "(kode_internal, kimia_id, erp_material_id, kode_material, nama_material, "
            "qty, qty_sisa, satuan, jumlah_kemasan, tanggal_in, expired_date, gudang, lot_number) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                kode_internal,
                stok.get("kimia_id") or erp_id,
                erp_id,
                stok.get("kode_material"),
                stok.get("nama_material"),
                qty,
                qty,
                stok.get("satuan") or "kg",
                jumlah_kemasan,
                tanggal,
                stok.get("expired_date"),
                GUDANG_LAPANGAN,
                stok.get("lot_number"),
            ),
        )
        lapangan_lot = {
            "id": cur.lastrowid,
            "kode_internal": kode_internal,
            "qty_sisa": qty,
            "gudang": GUDANG_LAPANGAN,
        }
    elif not is_utama_to_lapangan_out(from_gudang=from_gudang, tujuan=tujuan):
        bridge = {
            "material_type": "kimia",
            "erp_material_id": erp_id,
            "material_code": stok.get("kode_material"),
            "material_name": stok.get("nama_material"),
            "unit": stok.get("satuan") or "kg",
            "qty": qty,
            "mrp_ref": f"stok-kimia-out:{out_id}",
        }
    return {
        "out_id": out_id,
        "qty_sisa": new_sisa,
        "gudang": cur_gudang,
        "tujuan": tujuan,
        "lapangan_lot": lapangan_lot,
        "bridge": bridge,
        "fifo_line": {
            "stok_in_id": int(stok_in_id),
            "kode_internal": stok.get("kode_internal"),
            "lot_number": stok.get("lot_number"),
            "qty": qty,
        },
    }


def _stok_kimia_fifo_out(cur, conn, body, *, erp_material_id: int, from_gudang: str, tujuan_default: str):
    from dual_gudang import gudang_match_sql

    ctx, err = _stok_kimia_parse_out_body(body, tujuan_default=tujuan_default)
    if err:
        cur.close()
        conn.close()
        return err
    qty_total = float(ctx["qty"])
    gudang_clause, gudang_params = gudang_match_sql("si.gudang", from_gudang)
    cur.execute(
        f"SELECT si.id FROM tbl_stok_kimia_in si "
        f"WHERE si.erp_material_id=%s AND si.qty_sisa > 0 AND {gudang_clause} "
        f"ORDER BY si.tanggal_in ASC, si.id ASC",
        (int(erp_material_id), *gudang_params),
    )
    lot_ids = [int(r["id"]) for r in cur.fetchall()]
    if not lot_ids:
        cur.close()
        conn.close()
        return _err("Tidak ada lot stok aktif untuk kimia ini")
    remaining = qty_total
    out_ids: list[int] = []
    fifo_lines: list[dict] = []
    lapangan_lots: list[dict] = []
    bridges: list[dict] = []
    last_meta: dict = {}
    try:
        for lot_id in lot_ids:
            if remaining <= 1e-9:
                break
            cur.execute(
                "SELECT qty_sisa FROM tbl_stok_kimia_in WHERE id=%s FOR UPDATE",
                (lot_id,),
            )
            row = cur.fetchone()
            if not row:
                continue
            sisa = float(row.get("qty_sisa") or 0)
            if sisa <= 1e-9:
                continue
            take = min(remaining, sisa)
            part = _stok_kimia_apply_out_on_lot(cur, lot_id, take, ctx, from_gudang=from_gudang)
            out_ids.append(int(part["out_id"]))
            fifo_lines.append(part["fifo_line"])
            if part.get("lapangan_lot"):
                lapangan_lots.append(part["lapangan_lot"])
            if part.get("bridge"):
                bridges.append(part["bridge"])
            last_meta = part
            remaining = round(remaining - take, 3)
        if remaining > 1e-9:
            conn.rollback()
            cur.close()
            conn.close()
            return _err(f"Stok FIFO tidak cukup (kurang {remaining:.3f})")
        conn.commit()
    except ValueError as exc:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(exc))
    cur.close()
    conn.close()
    payload = {
        "ok": True,
        "fifo": True,
        "out_ids": out_ids,
        "out_id": out_ids[-1] if out_ids else None,
        "fifo_lines": fifo_lines,
        "qty": qty_total,
        "qty_sisa": last_meta.get("qty_sisa"),
        "gudang": last_meta.get("gudang"),
        "tujuan": ctx["tujuan"],
    }
    if len(bridges) == 1:
        payload["bridge"] = bridges[0]
    elif bridges:
        payload["bridges"] = bridges
    if lapangan_lots:
        payload["lapangan_lot"] = lapangan_lots[-1]
        payload["lapangan_lots"] = lapangan_lots
    return jsonify(payload)


def _stok_kimia_do_out(cur, conn, body, *, from_gudang: str, tujuan_default: str):
    """Shared OUT / out_lapangan for kimia. Returns (jsonify_response) or (_err)."""
    stok_in_id = body.get("stok_in_id")
    try:
        stok_in_id = int(stok_in_id) if stok_in_id is not None else None
    except (TypeError, ValueError):
        stok_in_id = None
    kimia_id = body.get("kimia_id") or body.get("erp_material_id")
    try:
        kimia_id = int(kimia_id) if kimia_id is not None else None
    except (TypeError, ValueError):
        kimia_id = None
    use_fifo = body.get("fifo") in (True, 1, "1", "true", "True") or (
        not stok_in_id and kimia_id
    )
    if use_fifo and kimia_id:
        return _stok_kimia_fifo_out(
            cur, conn, body, erp_material_id=int(kimia_id), from_gudang=from_gudang, tujuan_default=tujuan_default
        )
    ctx, err = _stok_kimia_parse_out_body(body, tujuan_default=tujuan_default)
    if err:
        cur.close()
        conn.close()
        return err
    if not stok_in_id:
        cur.close()
        conn.close()
        return _err("Pilih kimia (FIFO) atau lot stok")
    try:
        result = _stok_kimia_apply_out_on_lot(
            cur, int(stok_in_id), float(ctx["qty"]), ctx, from_gudang=from_gudang
        )
        conn.commit()
    except ValueError as exc:
        conn.rollback()
        cur.close()
        conn.close()
        return _err(str(exc))
    cur.close()
    conn.close()
    payload = {
        "ok": True,
        "out_id": result["out_id"],
        "qty_sisa": result["qty_sisa"],
        "gudang": result["gudang"],
        "tujuan": result["tujuan"],
    }
    if result.get("bridge"):
        payload["bridge"] = result["bridge"]
    if result.get("lapangan_lot"):
        payload["lapangan_lot"] = result["lapangan_lot"]
    return jsonify(payload)


_STOCK_LOT_KIND = {
    "kimia": {
        "table": "tbl_stok_kimia_in",
        "out_table": "tbl_stok_kimia_out",
        "qty_in": "qty",
        "qty_out": "qty",
        "usage_table": "tbl_usage_color",
        "block_lapangan": True,
        "lot": True,
        "satuan": True,
        "kemasan": True,
        "expired": True,
    },
    "rp": {
        "table": "tbl_stok_rp_in",
        "out_table": "tbl_stok_rp_out",
        "qty_in": "meter_roll",
        "qty_out": "meter_roll",
        "usage_table": "tbl_usage_rp",
        "block_lapangan": True,
        "lot": True,
        "satuan": False,
        "kemasan": False,
        "expired": False,
    },
    "material_lain": {
        "table": "tbl_stok_material_lain_in",
        "out_table": "tbl_stok_material_lain_out",
        "qty_in": "qty",
        "qty_out": "qty",
        "usage_table": "tbl_usage_material_lain",
        "block_lapangan": False,
        "lot": False,
        "satuan": True,
        "kemasan": False,
        "expired": False,
    },
}


def _stock_lot_id(body):
    raw = body.get("id") or body.get("stok_in_id")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _stock_lot_out_stats(cur, spec, stok_in_id: int) -> dict:
    kemasan_sql = "COALESCE(SUM(jumlah_kemasan),0)" if spec["kemasan"] else "0"
    cur.execute(
        f"SELECT COALESCE(SUM({spec['qty_out']}),0) AS issued, COUNT(*) AS n, "
        f"{kemasan_sql} AS kemasan FROM {spec['out_table']} WHERE stok_in_id=%s",
        (int(stok_in_id),),
    )
    row = cur.fetchone() or {}
    return {
        "issued": round(float(row.get("issued") or 0), 3),
        "n": int(row.get("n") or 0),
        "kemasan": int(float(row.get("kemasan") or 0)),
    }


def _stock_lot_has_sisa_note(cur, kode_internal: str) -> bool:
    from app import _col_names

    cols = _col_names(cur, "tbl_stock_sisa")
    if not cols or "barcode" not in cols or not kode_internal:
        return False
    cur.execute(
        "SELECT id FROM tbl_stock_sisa WHERE barcode=%s LIMIT 1",
        (kode_internal,),
    )
    return cur.fetchone() is not None


def _stock_lot_has_usage(cur, spec, stok_in_id: int) -> bool:
    from app import _col_names

    cols = _col_names(cur, spec["usage_table"])
    if not cols or "stok_in_id" not in cols:
        return False
    cur.execute(
        f"SELECT id FROM {spec['usage_table']} WHERE stok_in_id=%s LIMIT 1",
        (int(stok_in_id),),
    )
    return cur.fetchone() is not None


def _stock_lot_mutate(cur, body, kind: str):
    """Return (payload, None) atau (None, pesan). Pemanggil yang commit."""
    from dual_gudang import normalize_gudang
    from stock_lot_rules import (
        parse_date_text,
        parse_kemasan,
        parse_positive_qty,
        validate_lot_delete,
        validate_lot_update,
    )

    spec = _STOCK_LOT_KIND[kind]
    action = (body.get("action") or "").strip().lower()
    lot_id = _stock_lot_id(body)
    if not lot_id:
        return None, "id lot wajib"
    cur.execute(
        f"SELECT * FROM {spec['table']} WHERE id=%s FOR UPDATE",
        (lot_id,),
    )
    lot = cur.fetchone()
    if not lot:
        return None, "Lot tidak ditemukan"
    stats = _stock_lot_out_stats(cur, spec, lot_id)
    qty_col = spec["qty_in"]
    if action == "delete":
        gudang = normalize_gudang(lot.get("gudang")) if spec["block_lapangan"] else None
        err = validate_lot_delete(
            out_count=stats["n"],
            gudang=gudang,
            has_sisa_note=_stock_lot_has_sisa_note(cur, lot.get("kode_internal") or ""),
            has_usage=_stock_lot_has_usage(cur, spec, lot_id),
            block_lapangan=spec["block_lapangan"],
        )
        if err:
            return None, err
        cur.execute(f"DELETE FROM {spec['table']} WHERE id=%s", (lot_id,))
        return {"ok": True, "id": lot_id, "deleted": True}, None

    if action != "update":
        return None, "action harus update|delete"

    qty_new, err = parse_positive_qty(body.get("qty") if "qty" in body else body.get("meter_roll"))
    if err:
        return None, err
    tanggal, err = parse_date_text(body.get("tanggal") or body.get("tanggal_in"))
    if err:
        return None, err
    lot_number = (body.get("lot_number") or body.get("lot_no") or "")
    if spec["lot"]:
        lot_number = str(lot_number).strip()
    satuan = str(body.get("satuan") or lot.get("satuan") or "").strip()
    kemasan_new = None
    if spec["kemasan"]:
        kemasan_new, err = parse_kemasan(body.get("jumlah_kemasan"))
        if err:
            return None, err
    expired_text = ""
    if spec["expired"]:
        expired_text, err = parse_date_text(
            body.get("expired_date"), required=False, label="tanggal kedaluwarsa"
        )
        if err:
            return None, err

    def _d(value):
        if value is None or value == "":
            return ""
        if hasattr(value, "isoformat"):
            return value.isoformat()[:10]
        return str(value)[:10]

    locked_changed = False
    if _d(lot.get("tanggal_in")) != tanggal:
        locked_changed = True
    if spec["lot"] and str(lot.get("lot_number") or "").strip() != str(lot_number).strip():
        locked_changed = True
    if spec["satuan"] and str(lot.get("satuan") or "").strip() != satuan:
        locked_changed = True
    if spec["kemasan"]:
        current_kemasan = lot.get("jumlah_kemasan")
        current_kemasan = int(current_kemasan) if current_kemasan not in (None, "") else None
        if current_kemasan != kemasan_new:
            locked_changed = True
    if spec["expired"] and _d(lot.get("expired_date")) != expired_text:
        locked_changed = True

    err = validate_lot_update(
        qty_new=qty_new,
        issued=stats["issued"],
        qty_book=lot.get(qty_col) or 0,
        qty_sisa_book=lot.get("qty_sisa") or 0,
        out_count=stats["n"],
        locked_changed=locked_changed,
        kemasan_new=kemasan_new,
        kemasan_issued=stats["kemasan"],
        satuan=satuan,
        lot_number=lot_number,
        check_satuan=spec["satuan"],
        check_lot=spec["lot"],
        check_kemasan=spec["kemasan"],
    )
    if err:
        return None, err
    qty_sisa = round(float(qty_new) - float(stats["issued"]), 3)
    sets = [f"{qty_col}=%s", "qty_sisa=%s", "tanggal_in=%s"]
    params = [qty_new, qty_sisa, tanggal]
    if spec["lot"]:
        sets.append("lot_number=%s")
        params.append(lot_number or None)
    if spec["satuan"]:
        sets.append("satuan=%s")
        params.append(satuan[:20])
    if spec["kemasan"]:
        sets.append("jumlah_kemasan=%s")
        params.append(kemasan_new)
    if spec["expired"]:
        sets.append("expired_date=%s")
        params.append(expired_text or None)
    params.append(lot_id)
    cur.execute(
        f"UPDATE {spec['table']} SET {', '.join(sets)} WHERE id=%s",
        tuple(params),
    )
    return {
        "ok": True,
        "id": lot_id,
        "qty": qty_new,
        "qty_sisa": qty_sisa,
        "meter_roll": qty_new if kind == "rp" else None,
    }, None


@api.post("/stok-kimia")
def stok_kimia_action():
    from app import ensure_extended_tables, generate_code
    from datetime import timedelta
    from dual_gudang import GUDANG_LAPANGAN, GUDANG_UTAMA, normalize_gudang

    body = request.get_json(silent=True) or {}
    action = (body.get("action") or "").strip().lower()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if action in ("update", "delete"):
        payload, err = _stock_lot_mutate(cur, body, "kimia")
        if err:
            cur.close()
            conn.close()
            return _err(err)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(payload)

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
        lot_number = (body.get("lot_number") or body.get("lot_no") or "").strip() or None
        gudang = normalize_gudang(body.get("gudang"), default=GUDANG_UTAMA)
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
            "qty, qty_sisa, satuan, jumlah_kemasan, tanggal_in, expired_date, gudang, lot_number) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
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
                gudang,
                lot_number,
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
                "gudang": gudang,
                "expired_date": expired.isoformat(),
                "erp_material_id": erp_id,
            }
        ), 201

    if action == "sisa":
        # Input sisa kimia: tambah qty ke lot BC-K yang sudah ada (jangan generate barcode baru).
        barcode = (body.get("barcode") or body.get("kode_internal") or "").strip()
        try:
            qty = float(body.get("qty") or 0)
        except (TypeError, ValueError):
            cur.close()
            conn.close()
            return _err("qty harus angka")
        if not barcode:
            cur.close()
            conn.close()
            return _err("barcode / kode_internal wajib")
        if qty <= 0:
            cur.close()
            conn.close()
            return _err("qty harus > 0")
        notes = (body.get("notes") or body.get("keterangan") or "").strip() or None
        cur.execute(
            "SELECT * FROM tbl_stok_kimia_in WHERE kode_internal=%s LIMIT 1",
            (barcode,),
        )
        stok = cur.fetchone()
        if not stok:
            cur.close()
            conn.close()
            return _err(f"Lot kimia {barcode} tidak ditemukan", 404)
        new_sisa = float(stok.get("qty_sisa") or 0) + qty
        new_qty = float(stok.get("qty") or 0) + qty
        cur.execute(
            "UPDATE tbl_stok_kimia_in SET qty_sisa=%s, qty=%s WHERE id=%s",
            (new_sisa, new_qty, stok["id"]),
        )
        record_sisa = body.get("record_stock_sisa", True)
        sisa_id = None
        if record_sisa not in (False, 0, "0", "false", "False"):
            cur.execute(
                "INSERT INTO tbl_stock_sisa "
                "(sumber, barcode, lot, qty, status, notes) "
                "VALUES ('kimia', %s, %s, %s, 'open', %s)",
                (
                    barcode,
                    stok.get("kode_material") or stok.get("nama_material"),
                    qty,
                    notes or f"Sisa kimia ke {barcode}",
                ),
            )
            sisa_id = cur.lastrowid
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(
            {
                "ok": True,
                "id": stok["id"],
                "kode_internal": barcode,
                "qty_added": qty,
                "qty_sisa": new_sisa,
                "stock_sisa_id": sisa_id,
            }
        )

    if action == "out":
        return _stok_kimia_do_out(
            cur, conn, body, from_gudang=GUDANG_UTAMA, tujuan_default="produksi"
        )

    if action == "out_lapangan":
        body = dict(body)
        if not (body.get("tujuan") or "").strip():
            body["tujuan"] = "keluar"
        return _stok_kimia_do_out(
            cur, conn, body, from_gudang=GUDANG_LAPANGAN, tujuan_default="keluar"
        )

    cur.close()
    conn.close()
    return _err("action harus in|out|out_lapangan|sisa|update|delete")


@api.get("/stok-rp")
def stok_rp_list():
    from app import ensure_extended_tables
    from dual_gudang import gudang_match_sql, normalize_gudang, parse_gudang_filter

    include_empty = (request.args.get("all") or "").strip().lower() in ("1", "true", "yes")
    q = (request.args.get("q") or "").strip()
    kode_f = (request.args.get("kode") or "").strip()
    gudang_f = parse_gudang_filter(request.args.get("gudang"))
    history_mode = bool(kode_f)
    pg = parse_page_args(request.args, default_page_size=20)
    order_in = order_sql(
        {
            "tanggal_in": "si.tanggal_in",
            "kode_internal": "si.kode_internal",
            "kode_material": "si.kode_material",
            "id": "si.id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="si.tanggal_in DESC, si.id DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    where_in = ""
    params_in: list = []
    if not include_empty:
        where_in += " AND si.qty_sisa > 0"
    if gudang_f:
        gudang_clause, gudang_params = gudang_match_sql("si.gudang", gudang_f)
        where_in += f" AND {gudang_clause}"
        params_in.extend(gudang_params)
    if kode_f:
        where_in += " AND si.kode_material = %s"
        params_in.append(kode_f)
    if q:
        like = f"%{q}%"
        where_in += (
            " AND (si.kode_internal LIKE %s OR IFNULL(si.kode_material,'') LIKE %s "
            "OR IFNULL(si.nama_material,'') LIKE %s OR IFNULL(si.gudang,'') LIKE %s "
            "OR IFNULL(si.lot_number,'') LIKE %s)"
        )
        params_in.extend([like, like, like, like, like])

    summary_where = where_in
    summary_params = list(params_in)
    if not history_mode:
        summary_where += " AND COALESCE(NULLIF(TRIM(si.kode_material), ''), '') <> ''"
        cur.execute(
            f"SELECT COALESCE(si.kode_material, '') AS kode_barang, "
            f"MAX(COALESCE(si.nama_material, '')) AS nama_barang, "
            f"'meter' AS satuan, "
            f"COUNT(*) AS lot_count, "
            f"COALESCE(SUM(si.qty_sisa), 0) AS qty_sisa, "
            f"COALESCE(SUM(si.meter_roll), 0) AS qty_in "
            f"FROM tbl_stok_rp_in si WHERE 1=1{summary_where} "
            f"GROUP BY COALESCE(si.kode_material, '') "
            f"ORDER BY kode_barang",
            summary_params,
        )
        summary = _rows(cur.fetchall())
        for row in summary:
            row["qty_sisa"] = round(float(row.get("qty_sisa") or 0), 3)
            row["qty_in"] = round(float(row.get("qty_in") or 0), 3)
            row["lot_count"] = int(row.get("lot_count") or 0)
    else:
        summary = []

    cur.execute(
        f"SELECT COUNT(*) AS c, COALESCE(SUM(si.qty_sisa), 0) AS qty_sisa "
        f"FROM tbl_stok_rp_in si WHERE 1=1{where_in}",
        params_in,
    )
    agg = cur.fetchone() or {}
    total_in = int(agg.get("c") or 0)
    total_qty_sisa = round(float(agg.get("qty_sisa") or 0), 3)
    sql_in = (
        "SELECT si.*, COALESCE(si.nama_material, '') AS nama_jenis, "
        "COALESCE(si.kode_material, '') AS kode_rp, 'meter' AS satuan "
        f"FROM tbl_stok_rp_in si WHERE 1=1{where_in} "
        f"ORDER BY {order_in} LIMIT %s OFFSET %s"
    )
    in_limit = 500 if history_mode else pg["page_size"]
    in_offset = 0 if history_mode else pg["offset"]
    cur.execute(sql_in, params_in + [in_limit, in_offset])
    stok_in = _rows(cur.fetchall())
    for row in stok_in:
        row["gudang"] = normalize_gudang(row.get("gudang"))

    sql_out = (
        "SELECT so.*, COALESCE(so.nama_material, si.nama_material, '') AS nama_jenis, "
        "COALESCE(so.kode_material, si.kode_material, '') AS kode_rp, "
        "COALESCE(si.kode_internal, '') AS kode_internal "
        "FROM tbl_stok_rp_out so "
        "LEFT JOIN tbl_stok_rp_in si ON si.id = so.stok_in_id WHERE 1=1"
    )
    params_out: list = []
    if gudang_f:
        gudang_clause, gudang_params = gudang_match_sql("IFNULL(so.gudang, si.gudang)", gudang_f)
        sql_out += f" AND {gudang_clause}"
        params_out.extend(gudang_params)
    if kode_f:
        sql_out += " AND COALESCE(so.kode_material, si.kode_material) = %s"
        params_out.append(kode_f)
    if q:
        like = f"%{q}%"
        sql_out += (
            " AND (IFNULL(so.nama_material,'') LIKE %s OR IFNULL(si.nama_material,'') LIKE %s "
            "OR IFNULL(so.kode_wip,'') LIKE %s OR IFNULL(so.kode_material,'') LIKE %s)"
        )
        params_out.extend([like, like, like, like])
    out_limit = 500 if history_mode else pg["page_size"]
    sql_out += " ORDER BY so.created_at DESC LIMIT %s"
    cur.execute(sql_out, params_out + [out_limit])
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
    payload = page_payload(
        items=stok_in,
        total=total_in,
        page=pg["page"],
        page_size=pg["page_size"],
        offset=pg["offset"],
    )
    payload.update(
        {
            "stok_in": stok_in,
            "stok_out": stok_out,
            "summary": summary,
            "rp_list": rp_list,
            "gudang": gudang_f,
            "kode": kode_f or None,
            "stats": {
                "lots": total_in,
                "qty_sisa": total_qty_sisa,
                "out_rows": len(stok_out),
            },
        }
    )
    return jsonify(payload)


def _kimia_consume_lapangan_fifo(
    cur,
    *,
    kode_kimia: str,
    code_match: str,
    qty_needed: float,
    kode_wip: str | None,
    keterangan: str,
    tanggal: str,
    stok_in_id: int | None = None,
) -> list[dict]:
    """Potong stok kimia gudang lapangan (FIFO) dan catat OUT produksi."""
    from dual_gudang import GUDANG_LAPANGAN

    remaining = float(qty_needed)
    if remaining <= 0:
        return []

    if stok_in_id:
        cur.execute(
            "SELECT * FROM tbl_stok_kimia_in WHERE id=%s AND gudang=%s AND qty_sisa > 0",
            (int(stok_in_id), GUDANG_LAPANGAN),
        )
        preferred = cur.fetchone()
        if not preferred:
            raise ValueError(f"Lot stok kimia #{stok_in_id} tidak tersedia")
        lots = [preferred]
    else:
        cur.execute(
            "SELECT * FROM tbl_stok_kimia_in "
            "WHERE gudang=%s AND qty_sisa > 0 AND ("
            "  kode_material=%s OR kode_material=%s"
            ") ORDER BY tanggal_in ASC, id ASC",
            (GUDANG_LAPANGAN, kode_kimia, code_match),
        )
        lots = cur.fetchall() or []
    outs: list[dict] = []
    for lot in lots:
        if remaining <= 1e-9:
            break
        sisa = float(lot.get("qty_sisa") or 0)
        if sisa <= 0:
            continue
        take = min(sisa, remaining)
        erp_id = lot.get("erp_material_id")
        cur.execute(
            "INSERT INTO tbl_stok_kimia_out "
            "(stok_in_id, kimia_id, erp_material_id, kode_material, nama_material, "
            "qty, jumlah_kemasan, tujuan, kode_wip, tanggal, keterangan) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                lot["id"],
                lot.get("kimia_id") or erp_id,
                erp_id,
                lot.get("kode_material"),
                lot.get("nama_material"),
                take,
                None,
                "produksi",
                kode_wip,
                tanggal,
                keterangan,
            ),
        )
        out_id = cur.lastrowid
        cur.execute(
            "UPDATE tbl_stok_kimia_in SET qty_sisa=%s WHERE id=%s",
            (round(sisa - take, 3), lot["id"]),
        )
        outs.append(
            {
                "out_id": out_id,
                "stok_in_id": lot["id"],
                "kode_internal": lot.get("kode_internal"),
                "kode_kimia": lot.get("kode_material") or kode_kimia,
                "qty": take,
            }
        )
        remaining = round(remaining - take, 3)

    if remaining > 1e-6:
        raise ValueError(
            f"Stok lapangan tidak cukup untuk {kode_kimia} "
            f"(butuh {qty_needed}, kurang {remaining})"
        )
    return outs


def _stok_rp_do_out(cur, conn, body, *, from_gudang: str, tujuan_default: str):
    from dual_gudang import GUDANG_LAPANGAN, GUDANG_UTAMA, normalize_gudang
    from app import _col_names

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
    tujuan = (body.get("tujuan") or tujuan_default).strip().lower()
    if tujuan == "mixing":
        tujuan = "lapangan"
    kode_wip = (body.get("kode_wip") or "").strip() or None
    keterangan = (body.get("keterangan") or "").strip() or None
    tanggal = body.get("tanggal") or date.today().isoformat()
    cur.execute("SELECT * FROM tbl_stok_rp_in WHERE id=%s", (stok_in_id,))
    stok = cur.fetchone()
    if not stok:
        cur.close()
        conn.close()
        return _err("Lot stok RP tidak ditemukan", 404)
    cur_gudang = normalize_gudang(stok.get("gudang"))
    if cur_gudang != from_gudang:
        cur.close()
        conn.close()
        return _err(
            f"Lot RP di gudang {cur_gudang}; aksi ini hanya untuk gudang {from_gudang}"
        )
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
    out_cols = _col_names(cur, "tbl_stok_rp_out")
    cols = [
        "stok_in_id",
        "rp_id",
        "erp_material_id",
        "kode_material",
        "nama_material",
        "meter_roll",
        "kode_wip",
        "tanggal",
        "keterangan",
    ]
    vals = [
        stok_in_id,
        stok.get("rp_id") or erp_id,
        erp_id,
        stok.get("kode_material"),
        stok.get("nama_material"),
        meter_roll,
        kode_wip,
        tanggal,
        keterangan,
    ]
    if "gudang" in out_cols:
        cols.append("gudang")
        vals.append(from_gudang)
    if "tujuan" in out_cols:
        cols.append("tujuan")
        vals.append(tujuan)
    ph = ",".join(["%s"] * len(cols))
    cur.execute(
        f"INSERT INTO tbl_stok_rp_out ({', '.join(cols)}) VALUES ({ph})",
        tuple(vals),
    )
    out_id = cur.lastrowid
    new_sisa = sisa - meter_roll
    new_gudang = cur_gudang
    lapangan_lot = None
    from dual_gudang import GUDANG_LAPANGAN, is_utama_to_lapangan_out

    cur.execute(
        "UPDATE tbl_stok_rp_in SET qty_sisa=%s, gudang=%s WHERE id=%s",
        (new_sisa, new_gudang, stok_in_id),
    )

    if is_utama_to_lapangan_out(from_gudang=from_gudang, tujuan=tujuan):
        from app import generate_code

        kode_internal = generate_code("BC-R")
        cur.execute(
            "INSERT INTO tbl_stok_rp_in "
            "(kode_internal, rp_id, erp_material_id, kode_material, nama_material, "
            "meter_roll, qty_sisa, tanggal_in, gudang, lot_number) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                kode_internal,
                stok.get("rp_id") or erp_id,
                erp_id,
                stok.get("kode_material"),
                stok.get("nama_material"),
                meter_roll,
                meter_roll,
                tanggal,
                GUDANG_LAPANGAN,
                stok.get("lot_number"),
            ),
        )
        lapangan_lot = {
            "id": cur.lastrowid,
            "kode_internal": kode_internal,
            "qty_sisa": meter_roll,
            "gudang": GUDANG_LAPANGAN,
        }
    conn.commit()
    cur.close()
    conn.close()
    payload = {
        "ok": True,
        "out_id": out_id,
        "qty_sisa": new_sisa,
        "gudang": new_gudang,
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
    if lapangan_lot:
        payload["lapangan_lot"] = lapangan_lot
    return jsonify(payload)


@api.post("/stok-rp")
def stok_rp_action():
    from app import ensure_extended_tables, generate_code
    from dual_gudang import GUDANG_LAPANGAN, GUDANG_UTAMA, normalize_gudang

    body = request.get_json(silent=True) or {}
    action = (body.get("action") or "").strip().lower()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if action in ("update", "delete"):
        payload, err = _stock_lot_mutate(cur, body, "rp")
        if err:
            cur.close()
            conn.close()
            return _err(err)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(payload)

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
        lot_number = (body.get("lot_number") or body.get("lot_no") or "").strip() or None
        gudang = normalize_gudang(body.get("gudang"), default=GUDANG_UTAMA)
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
            "meter_roll, qty_sisa, tanggal_in, gudang, lot_number) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                kode_internal,
                erp_id,
                erp_id,
                mat.get("code"),
                mat.get("name"),
                meter_roll,
                meter_roll,
                tanggal,
                gudang,
                lot_number,
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
                "lot_number": lot_number,
                "meter_roll": meter_roll,
                "gudang": gudang,
                "erp_material_id": erp_id,
            }
        ), 201

    if action == "out":
        body = dict(body)
        if not (body.get("tujuan") or "").strip():
            body["tujuan"] = "produksi"
        return _stok_rp_do_out(
            cur, conn, body, from_gudang=GUDANG_UTAMA, tujuan_default="produksi"
        )

    if action == "out_lapangan":
        body = dict(body)
        if not (body.get("tujuan") or "").strip():
            body["tujuan"] = "keluar"
        return _stok_rp_do_out(
            cur, conn, body, from_gudang=GUDANG_LAPANGAN, tujuan_default="keluar"
        )

    cur.close()
    conn.close()
    return _err("action harus in|out|out_lapangan|update|delete")


_USAGE_KIND = {
    "color": {
        "table": "tbl_usage_color",
        "qty": "qty_digunakan",
        "in_table": "tbl_stok_kimia_in",
        "out_table": "tbl_stok_kimia_out",
        "out_qty": "qty",
    },
    "rp": {
        "table": "tbl_usage_rp",
        "qty": "qty_used",
        "in_table": "tbl_stok_rp_in",
        "out_table": "tbl_stok_rp_out",
        "out_qty": "meter_roll",
    },
    "material_lain": {
        "table": "tbl_usage_material_lain",
        "qty": "qty_used",
        "in_table": "tbl_stok_material_lain_in",
        "out_table": "tbl_stok_material_lain_out",
        "out_qty": "qty",
    },
}


def _sync_color_lot_status(cur, kode_lot_warna: str):
    cur.execute(
        "SELECT status FROM tbl_lab_lot WHERE kode_lot_warna=%s",
        (kode_lot_warna,),
    )
    lot = cur.fetchone()
    if not lot:
        return
    cur.execute(
        "SELECT COALESCE(SUM(qty),0) AS total_qty FROM tbl_lab_lot_detail WHERE kode_lot_warna=%s",
        (kode_lot_warna,),
    )
    pembuatan = float((cur.fetchone() or {}).get("total_qty") or 0)
    cur.execute(
        "SELECT COALESCE(SUM(qty_digunakan),0) AS used FROM tbl_usage_color WHERE kode_lot_warna=%s",
        (kode_lot_warna,),
    )
    used = float((cur.fetchone() or {}).get("used") or 0)
    status = (lot.get("status") or "").strip()
    if status == "used" and used + 0.001 < pembuatan:
        cur.execute(
            "UPDATE tbl_lab_lot SET status='active' WHERE kode_lot_warna=%s",
            (kode_lot_warna,),
        )
    elif status == "active" and pembuatan > 0 and used + 0.001 >= pembuatan:
        cur.execute(
            "UPDATE tbl_lab_lot SET status='used' WHERE kode_lot_warna=%s",
            (kode_lot_warna,),
        )


def _usage_mutate(cur, kind: str, usage_id: int, body, *, delete: bool):
    from stock_lot_rules import parse_positive_qty

    spec = _USAGE_KIND[kind]
    cur.execute(
        f"SELECT * FROM {spec['table']} WHERE id=%s FOR UPDATE",
        (int(usage_id),),
    )
    row = cur.fetchone()
    if not row:
        return None, "Pemakaian tidak ditemukan"
    in_id = row.get("stok_in_id")
    out_id = row.get("stok_out_id")
    if not in_id or not out_id:
        return None, "Pemakaian tanpa jejak lot tidak bisa diubah atau dihapus"
    cur.execute(
        f"SELECT * FROM {spec['out_table']} WHERE id=%s FOR UPDATE",
        (int(out_id),),
    )
    out = cur.fetchone()
    if not out or int(out.get("stok_in_id") or 0) != int(in_id):
        return None, "Jejak keluar tidak milik lot pemakaian ini"
    cur.execute(
        f"SELECT * FROM {spec['in_table']} WHERE id=%s FOR UPDATE",
        (int(in_id),),
    )
    lot = cur.fetchone()
    if not lot:
        return None, "Lot stok tidak ditemukan"
    old_qty = round(float(row.get(spec["qty"]) or 0), 3)
    out_qty = round(float(out.get(spec["out_qty"]) or 0), 3)
    if abs(old_qty - out_qty) > 0.001:
        return None, "Qty pemakaian tidak cocok dengan baris keluar. Data tidak diubah."
    if delete:
        new_qty = 0.0
    else:
        raw_qty = body.get("qty")
        if raw_qty in (None, ""):
            raw_qty = body.get(spec["qty"])
        new_qty, err = parse_positive_qty(raw_qty)
        if err:
            return None, err
        if kind == "color":
            kode_lot = row.get("kode_lot_warna") or ""
            cur.execute(
                "SELECT COALESCE(SUM(qty),0) AS total_qty FROM tbl_lab_lot_detail WHERE kode_lot_warna=%s",
                (kode_lot,),
            )
            pembuatan = float((cur.fetchone() or {}).get("total_qty") or 0)
            cur.execute(
                "SELECT COALESCE(SUM(qty_digunakan),0) AS used FROM tbl_usage_color "
                "WHERE kode_lot_warna=%s AND id<>%s",
                (kode_lot, int(usage_id)),
            )
            other = float((cur.fetchone() or {}).get("used") or 0)
            if pembuatan > 0 and other + new_qty > pembuatan + 0.001:
                return None, f"Qty melebihi sisa lot warna ({round(pembuatan - other, 3)})"
    delta = round(new_qty - old_qty, 3)
    sisa = round(float(lot.get("qty_sisa") or 0), 3)
    if delta > sisa + 0.001:
        return None, "Kenaikan qty melebihi sisa lot"
    new_sisa = round(sisa - delta, 3)
    cur.execute(
        f"UPDATE {spec['in_table']} SET qty_sisa=%s WHERE id=%s",
        (new_sisa, int(in_id)),
    )
    if delete:
        cur.execute(f"DELETE FROM {spec['out_table']} WHERE id=%s", (int(out_id),))
        cur.execute(f"DELETE FROM {spec['table']} WHERE id=%s", (int(usage_id),))
    else:
        cur.execute(
            f"UPDATE {spec['out_table']} SET {spec['out_qty']}=%s WHERE id=%s",
            (new_qty, int(out_id)),
        )
        cur.execute(
            f"UPDATE {spec['table']} SET {spec['qty']}=%s WHERE id=%s",
            (new_qty, int(usage_id)),
        )
    if kind == "color":
        _sync_color_lot_status(cur, row.get("kode_lot_warna") or "")
    return {"ok": True, "id": int(usage_id), "deleted": delete, "qty": new_qty, "qty_sisa": new_sisa}, None


def _usage_mutate_response(kind: str, usage_id: int, *, delete: bool):
    from app import ensure_extended_tables

    body = {} if delete else (request.get_json(silent=True) or {})
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    payload, err = _usage_mutate(cur, kind, usage_id, body, delete=delete)
    if err:
        conn.rollback()
        cur.close()
        conn.close()
        code = 404 if "tidak ditemukan" in err else 400
        return _err(err, code)
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(payload)


@api.put("/usage-color/<int:usage_id>")
def usage_color_update(usage_id: int):
    return _usage_mutate_response("color", usage_id, delete=False)


@api.delete("/usage-color/<int:usage_id>")
def usage_color_delete(usage_id: int):
    return _usage_mutate_response("color", usage_id, delete=True)


@api.put("/usage-rp/<int:usage_id>")
def usage_rp_update(usage_id: int):
    return _usage_mutate_response("rp", usage_id, delete=False)


@api.delete("/usage-rp/<int:usage_id>")
def usage_rp_delete(usage_id: int):
    return _usage_mutate_response("rp", usage_id, delete=True)


@api.put("/usage-material-lain/<int:usage_id>")
def usage_material_update(usage_id: int):
    return _usage_mutate_response("material_lain", usage_id, delete=False)


@api.delete("/usage-material-lain/<int:usage_id>")
def usage_material_delete(usage_id: int):
    return _usage_mutate_response("material_lain", usage_id, delete=True)


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
    pg = parse_page_args(request.args, default_page_size=20)
    order = order_sql(
        {
            "date_created": "date_created",
            "kode_wip": "kode_wip",
            "kode_lot_warna": "kode_lot_warna",
            "id": "id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="date_created DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS c FROM tbl_usage_color")
    total = int((cur.fetchone() or {}).get("c") or 0)
    cur.execute(
        f"SELECT * FROM tbl_usage_color ORDER BY {order} LIMIT %s OFFSET %s",
        (pg["page_size"], pg["offset"]),
    )
    usage_list = _rows(cur.fetchall())
    cur.execute(
        "SELECT DISTINCT kode_lot_wip AS kode_wip FROM tbl_rencana_item "
        "WHERE kode_lot_wip IS NOT NULL AND kode_lot_wip != '' "
        "ORDER BY kode_lot_wip DESC"
    )
    wip_list = [r["kode_wip"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    payload = page_payload(
        items=usage_list,
        total=total,
        page=pg["page"],
        page_size=pg["page_size"],
        offset=pg["offset"],
    )
    payload.update({"usage_list": usage_list, "wip_list": wip_list})
    return jsonify(payload)


@api.post("/usage-color")
def usage_color_create():
    body = request.get_json(silent=True) or {}
    kode_wip = (body.get("kode_wip") or "").strip()
    kode_lot_warna = (body.get("kode_lot_warna") or "").strip()
    qty_digunakan = body.get("qty_digunakan")
    stok_in_id = body.get("stok_in_id")
    try:
        stok_in_id = int(stok_in_id) if stok_in_id not in (None, "") else None
    except (TypeError, ValueError):
        stok_in_id = None
    if qty_digunakan not in (None, ""):
        try:
            qty_digunakan = float(qty_digunakan)
        except (TypeError, ValueError):
            return _err("qty_digunakan harus angka")
        if qty_digunakan <= 0:
            return _err("qty_digunakan harus > 0")
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    payload, err = _apply_usage_color(
        cur,
        kode_wip=kode_wip,
        kode_lot_warna=kode_lot_warna,
        qty_digunakan=qty_digunakan,
        stok_in_id=stok_in_id,
    )
    if err:
        cur.close()
        conn.close()
        code = 404 if "tidak ditemukan" in err else 400
        return _err(err, code)
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"ok": True, **payload}), 201



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
    pg = parse_page_args(request.args, default_page_size=20)
    order = order_sql(
        {
            "date_created": "date_created",
            "kode_wip": "kode_wip",
            "jenis_rp": "jenis_rp",
            "id": "id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="date_created DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS c FROM tbl_usage_rp")
    total = int((cur.fetchone() or {}).get("c") or 0)
    cur.execute(
        f"SELECT * FROM tbl_usage_rp ORDER BY {order} LIMIT %s OFFSET %s",
        (pg["page_size"], pg["offset"]),
    )
    usage_list = _rows(cur.fetchall())
    cur.execute(
        "SELECT DISTINCT kode_lot_wip AS kode_wip FROM tbl_rencana_item "
        "WHERE kode_lot_wip IS NOT NULL AND kode_lot_wip != '' "
        "ORDER BY kode_lot_wip DESC"
    )
    wip_list = [r["kode_wip"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    payload = page_payload(
        items=usage_list,
        total=total,
        page=pg["page"],
        page_size=pg["page_size"],
        offset=pg["offset"],
    )
    payload.update({"usage_list": usage_list, "wip_list": wip_list})
    return jsonify(payload)


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
    from app import ensure_extended_tables
    ensure_extended_tables(cur)
    conn.commit()
    bridge = None
    stock_out_id = None
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
        stock_out_id = cur.lastrowid
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
        "INSERT INTO tbl_usage_rp (kode_wip, jenis_rp, qty_used, satuan, stok_in_id, stok_out_id) "
        "VALUES (%s,%s,%s,%s,%s,%s)",
        (
            kode_wip,
            mat.get("name") or jenis_scan,
            qty_used,
            body.get("satuan") or mat.get("unit") or "meter",
            stok_in_id,
            stock_out_id,
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

    pg = parse_page_args(request.args, default_page_size=50)
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
    out = sort_rows(
        out,
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        fields={"kode_material": "kode_material", "nama_material": "nama_material", "id": "id"},
    )
    page_items, total = slice_page(out, page=pg["page"], page_size=pg["page_size"], offset=pg["offset"])
    return jsonify(
        page_payload(
            items=page_items,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


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
    pg = parse_page_args(request.args, default_page_size=20)
    order_in = order_sql(
        {
            "tanggal_in": "si.tanggal_in",
            "kode_internal": "si.kode_internal",
            "kode_material": "si.kode_material",
            "id": "si.id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="si.tanggal_in DESC, si.id DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    where_in = ""
    params_in: list = []
    if not include_empty:
        where_in += " AND si.qty_sisa > 0"
    if q:
        like = f"%{q}%"
        where_in += (
            " AND (si.kode_internal LIKE %s OR IFNULL(si.kode_material,'') LIKE %s "
            "OR IFNULL(si.nama_material,'') LIKE %s)"
        )
        params_in.extend([like, like, like])
    cur.execute(
        f"SELECT COUNT(*) AS c FROM tbl_stok_material_lain_in si WHERE 1=1{where_in}",
        params_in,
    )
    total_in = int((cur.fetchone() or {}).get("c") or 0)
    sql_in = (
        "SELECT si.*, COALESCE(si.kode_material,'') AS kode_material, "
        "COALESCE(si.nama_material,'') AS nama_material, "
        "COALESCE(si.satuan, 'pcs') AS satuan "
        f"FROM tbl_stok_material_lain_in si WHERE 1=1{where_in} "
        f"ORDER BY {order_in} LIMIT %s OFFSET %s"
    )
    cur.execute(sql_in, params_in + [pg["page_size"], pg["offset"]])
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
    sql_out += " ORDER BY so.created_at DESC LIMIT %s"
    cur.execute(sql_out, params_out + [pg["page_size"]])
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
    payload = page_payload(
        items=stok_in,
        total=total_in,
        page=pg["page"],
        page_size=pg["page_size"],
        offset=pg["offset"],
    )
    payload.update(
        {
            "stok_in": stok_in,
            "stok_out": stok_out,
            "material_list": material_list,
            "stats": {
                "lots": total_in,
                "qty_sisa": round(sum(float(r.get("qty_sisa") or 0) for r in stok_in), 3),
                "out_rows": len(stok_out),
            },
        }
    )
    return jsonify(payload)


@api.post("/stok-material-lain")
def stok_material_lain_action():
    from app import ensure_extended_tables, generate_code

    body = request.get_json(silent=True) or {}
    action = (body.get("action") or "").strip().lower()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    if action in ("update", "delete"):
        payload, err = _stock_lot_mutate(cur, body, "material_lain")
        if err:
            cur.close()
            conn.close()
            return _err(err)
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(payload)

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
    return _err("action harus in|out|update|delete")


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

    pg = parse_page_args(request.args, default_page_size=20)
    order = order_sql(
        {
            "date_created": "date_created",
            "kode_wip": "kode_wip",
            "kode_material": "kode_material",
            "id": "id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="date_created DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    cur.execute("SELECT COUNT(*) AS c FROM tbl_usage_material_lain")
    total = int((cur.fetchone() or {}).get("c") or 0)
    cur.execute(
        f"SELECT * FROM tbl_usage_material_lain ORDER BY {order} LIMIT %s OFFSET %s",
        (pg["page_size"], pg["offset"]),
    )
    usage_list = _rows(cur.fetchall())
    cur.execute(
        "SELECT DISTINCT kode_lot_wip FROM tbl_rencana_item "
        "WHERE kode_lot_wip IS NOT NULL ORDER BY kode_lot_wip DESC"
    )
    wip_list = [r["kode_lot_wip"] for r in cur.fetchall()]
    cur.close()
    conn.close()
    payload = page_payload(
        items=usage_list,
        total=total,
        page=pg["page"],
        page_size=pg["page_size"],
        offset=pg["offset"],
    )
    payload.update({"usage_list": usage_list, "wip_list": wip_list})
    return jsonify(payload)


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
    stock_out_id = None
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
        stock_out_id = cur.lastrowid
        cur.execute(
            "UPDATE tbl_stok_material_lain_in SET qty_sisa=%s WHERE id=%s",
            (sisa - qty_used, stok_in_id),
        )
    cur.execute(
        "INSERT INTO tbl_usage_material_lain "
        "(kode_wip, kode_material, nama_material, qty_used, satuan, stok_in_id, stok_out_id) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (
            kode_wip,
            kode_material,
            mat.get("nama_material"),
            qty_used,
            satuan or mat.get("satuan") or "pcs",
            stok_in_id,
            stock_out_id,
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
    from mrp_api import erp_client

    _, err = _erp_kulit_material(kulit_id)
    if err:
        return _err(err, 404)
    body = request.get_json(silent=True) or {}
    payload, err = _parse_kulit_write_body(body)
    if err:
        return _err(err)
    try:
        row = erp_client.update_material(kulit_id, payload)
    except erp_client.ErpApiError as exc:
        code = exc.status_code or 502
        return _err(str(exc), code if 400 <= code < 600 else 400)
    return jsonify(_kulit_row_out(row))


@api.delete("/masters/kulit/<int:kulit_id>")
def master_kulit_delete(kulit_id: int):
    from mrp_api import erp_client

    _, err = _erp_kulit_material(kulit_id)
    if err:
        return _err(err, 404)
    try:
        row = erp_client.update_material(kulit_id, {"is_active": False})
    except erp_client.ErpApiError as exc:
        code = exc.status_code or 502
        return _err(str(exc), code if 400 <= code < 600 else 400)
    return jsonify({"ok": True, "id": kulit_id, "item": _kulit_row_out(row)})



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
    """Daftar SO outstanding/partial untuk alokasi rencana.

    Semua filter opsional. Tanpa spek → list master PO siap alokasi (SO-first).
    Dengan spek → cocokkan toleran lewat spek_match.
    """
    from app import ensure_extended_tables
    from spek_match import filter_master_po_by_spek

    color = (request.args.get("color") or "").strip()
    emboss = (request.args.get("emboss") or "").strip()
    material_name = (request.args.get("material_name") or request.args.get("item_name") or "").strip()
    thickness = (request.args.get("thickness") or request.args.get("tebal") or "").strip()
    color_swatch = (request.args.get("color_swatch") or "").strip()
    customer = (request.args.get("customer") or "").strip()
    q = (request.args.get("q") or request.args.get("keyword") or "").strip()
    no_so = (request.args.get("no_so") or "").strip()
    no_po = (request.args.get("no_po") or "").strip()
    try:
        limit = min(max(int(request.args.get("limit") or 1000), 1), 2000)
    except (TypeError, ValueError):
        limit = 1000

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    sql = (
        "SELECT id, no_po, no_so, customer, item_name, tebal, warna, emboss, color_swatch, "
        "sq_ft, qty_order, qty_processed, qty_balance_erp, source_detail_id, lot_number, "
        "(qty_order - qty_processed) AS qty_outstanding "
        "FROM tbl_master_po "
        "WHERE status IN ('outstanding','partial') "
    )
    params: list = []
    if customer:
        sql += "AND customer LIKE %s "
        params.append(f"%{customer}%")
    if no_so:
        sql += "AND COALESCE(no_so, '') LIKE %s "
        params.append(f"%{no_so}%")
    if no_po:
        sql += "AND COALESCE(no_po, '') LIKE %s "
        params.append(f"%{no_po}%")
    if q:
        like = f"%{q}%"
        sql += (
            "AND ("
            "COALESCE(no_po,'') LIKE %s OR COALESCE(no_so,'') LIKE %s "
            "OR COALESCE(customer,'') LIKE %s OR COALESCE(item_name,'') LIKE %s "
            "OR COALESCE(lot_number,'') LIKE %s OR COALESCE(warna,'') LIKE %s "
            "OR COALESCE(emboss,'') LIKE %s OR COALESCE(tebal,'') LIKE %s "
            "OR COALESCE(color_swatch,'') LIKE %s"
            ") "
        )
        params.extend([like] * 9)
    sql += "ORDER BY no_po, item_name LIMIT %s"
    params.append(limit)

    cur.execute(sql, params)
    items = filter_master_po_by_spek(
        _rows(cur.fetchall()),
        material_name=material_name,
        thickness=thickness,
        color=color,
        emboss=emboss,
        color_swatch=color_swatch,
    )
    _hydrate_master_po_rows_from_erp(items)
    cur.close()
    conn.close()
    return jsonify(items)


@api.put("/rencana-produksi/item/<int:item_id>/print-fields")
def rencana_item_print_fields(item_id: int):
    """Qty, schedule, dan remarks untuk cetak rencana. Tidak mengubah alokasi SO."""
    from app import ensure_rencana_tables

    body = request.get_json(silent=True) or {}
    qty_raw = body.get("print_qty")
    print_qty = None
    if qty_raw not in (None, ""):
        try:
            print_qty = round(float(qty_raw), 2)
        except (TypeError, ValueError):
            return _err("print_qty tidak valid")
        if print_qty < 0:
            return _err("print_qty tidak valid")
    schedule = (body.get("print_schedule") or "").strip() or None
    remarks = (body.get("print_remarks") or "").strip() or None

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_rencana_tables(cur)
    conn.commit()
    cur.execute("SELECT id FROM tbl_rencana_item WHERE id=%s", (item_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        return _err("Item rencana tidak ditemukan", 404)
    cur.execute(
        "UPDATE tbl_rencana_item SET print_qty=%s, print_schedule=%s, print_remarks=%s WHERE id=%s",
        (print_qty, schedule, remarks, item_id),
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(
        {
            "ok": True,
            "id": item_id,
            "print_qty": print_qty,
            "print_schedule": schedule or "",
            "print_remarks": remarks or "",
        }
    )


@api.get("/rencana-produksi/<int:rencana_id>/print")
def rencana_print_api(rencana_id: int):
    from app import _make_rpi_barcode, ensure_rencana_tables

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
    _hydrate_master_po_rows_from_erp(po_list)

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
    _hydrate_master_po_rows_from_erp(selected_po)
    relinked = _relink_rencana_allocations_by_erp_lot(cur, selected_po)
    if relinked:
        conn.commit()
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
    pg = parse_page_args(request.args, default_page_size=50)
    totals = {
        "total_all_lembar": sum(r.get("qty") or 0 for r in report_data),
        "total_all_ukuran": sum(r.get("size") or 0 for r in report_data),
        "total_all_pack": sum(r.get("pack") or 0 for r in report_data),
    }
    report_data = sort_rows(
        report_data,
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        fields={
            "tanggal": "tanggal",
            "no_po": "no_po",
            "no_so": "no_so",
            "kode_process": "kode_process",
            "status": "status",
        },
    )
    page_rows, total = slice_page(
        report_data, page=pg["page"], page_size=pg["page_size"], offset=pg["offset"]
    )
    payload = page_payload(
        items=page_rows,
        total=total,
        page=pg["page"],
        page_size=pg["page_size"],
        offset=pg["offset"],
    )
    payload.update(
        {
            "start_date": start_date,
            "end_date": end_date,
            "rows": page_rows,
            **totals,
        }
    )
    return jsonify(payload)


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
            SELECT DATE(pk.date_created) AS tanggal,
                   pk.kode_proses AS kode_proses,
                   pk.kode_proses AS kode_proccess,
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
    pg = parse_page_args(request.args, default_page_size=50)
    totals = {
        "total_all_lembar": sum(r.get("total_lembar") or 0 for r in report_data),
        "total_all_ukuran": sum(
            (r.get("total_ukuran") or 0) for r in report_data if r.get("total_ukuran")
        ),
    }
    report_data = sort_rows(
        report_data,
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        fields={
            "tanggal": "tanggal",
            "kode_proses": "kode_proses",
            "kode_proccess": "kode_proses",
            "nama_barang": "nama_barang",
            "status_terakhir": "status_terakhir",
        },
    )
    page_rows, total = slice_page(
        report_data, page=pg["page"], page_size=pg["page_size"], offset=pg["offset"]
    )
    payload = page_payload(
        items=page_rows,
        total=total,
        page=pg["page"],
        page_size=pg["page_size"],
        offset=pg["offset"],
    )
    payload.update(
        {
            "start_date": start_date,
            "end_date": end_date,
            "rows": page_rows,
            **totals,
        }
    )
    return jsonify(payload)


@api.get("/reports/selisih-wip")
def report_selisih_wip_api():
    """Per WIP: qty persiapan (total_size) vs total roll packing (ukuran)."""
    today = date.today().isoformat()
    start_date = request.args.get("start_date") or today
    end_date = request.args.get("end_date") or today
    q = (request.args.get("q") or "").strip().lower()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            """
            SELECT pk.kode_wip,
                   COALESCE(NULLIF(TRIM(ri.material_name), ''), '—') AS nama_material,
                   COALESCE(NULLIF(TRIM(ri.thickness), ''), NULLIF(TRIM(pk.tebal), ''), '—') AS thickness,
                   COALESCE(NULLIF(TRIM(ri.emboss), ''), NULLIF(TRIM(pk.emboss), ''), '—') AS emboss,
                   COALESCE(NULLIF(TRIM(ri.color), ''), NULLIF(TRIM(pk.warna), ''), '—') AS warna,
                   COALESCE(pk.total_size, 0) AS qty_wip,
                   COALESCE(pack.qty_actual, 0) AS qty_actual,
                   DATE(pk.date_created) AS tanggal
            FROM tbl_persiapan_kulit pk
            LEFT JOIN tbl_rencana_item ri ON ri.id = pk.rencana_item_id
            LEFT JOIN (
                SELECT p.kode_wip, COALESCE(SUM(pr.ukuran), 0) AS qty_actual
                FROM tbl_packing p
                LEFT JOIN tbl_packing_roll pr ON pr.packing_id = p.id
                WHERE COALESCE(p.kode_wip, '') <> ''
                GROUP BY p.kode_wip
            ) pack ON pack.kode_wip = pk.kode_wip
            WHERE pk.status IN ('started', 'saved', 'completed')
              AND DATE(pk.date_created) BETWEEN %s AND %s
            ORDER BY pk.date_created DESC, pk.id DESC
            """,
            (start_date, end_date),
        )
        report_data = _rows(cur.fetchall())
    except Exception:
        report_data = []
    cur.close()
    conn.close()

    for row in report_data:
        qty_wip = round(float(row.get("qty_wip") or 0), 2)
        qty_actual = round(float(row.get("qty_actual") or 0), 2)
        selisih = round(qty_actual - qty_wip, 2)
        if qty_wip > 1e-9:
            selisih_pct = round((selisih / qty_wip) * 100.0, 2)
        else:
            selisih_pct = 0.0 if abs(selisih) < 1e-9 else None
        row["qty_wip"] = qty_wip
        row["qty_actual"] = qty_actual
        row["selisih_qty"] = selisih
        row["selisih_pct"] = selisih_pct

    if q:
        def _match(r):
            blob = " ".join(
                str(r.get(k) or "")
                for k in (
                    "kode_wip",
                    "nama_material",
                    "thickness",
                    "emboss",
                    "warna",
                )
            ).lower()
            return q in blob

        report_data = [r for r in report_data if _match(r)]

    pg = parse_page_args(request.args, default_page_size=50)
    totals = {
        "total_qty_wip": round(sum(r.get("qty_wip") or 0 for r in report_data), 2),
        "total_qty_actual": round(sum(r.get("qty_actual") or 0 for r in report_data), 2),
        "total_selisih_qty": round(sum(r.get("selisih_qty") or 0 for r in report_data), 2),
    }
    report_data = sort_rows(
        report_data,
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        fields={
            "tanggal": "tanggal",
            "kode_wip": "kode_wip",
            "nama_material": "nama_material",
            "thickness": "thickness",
            "emboss": "emboss",
            "warna": "warna",
            "qty_wip": "qty_wip",
            "qty_actual": "qty_actual",
            "selisih_qty": "selisih_qty",
            "selisih_pct": "selisih_pct",
        },
    )
    page_rows, total = slice_page(
        report_data, page=pg["page"], page_size=pg["page_size"], offset=pg["offset"]
    )
    payload = page_payload(
        items=page_rows,
        total=total,
        page=pg["page"],
        page_size=pg["page_size"],
        offset=pg["offset"],
    )
    payload.update(
        {
            "start_date": start_date,
            "end_date": end_date,
            "rows": page_rows,
            **totals,
        }
    )
    return jsonify(payload)


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


def _monitoring_parse_dt(value):
    if value is None or value == "":
        return None, False
    if isinstance(value, datetime):
        return value, True
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day), False
    s = str(value).strip()
    if not s:
        return None, False
    s = s.replace("Z", "")
    if "T" in s or " " in s:
        try:
            return datetime.fromisoformat(s[:19]), True
        except ValueError:
            pass
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d"), False
    except ValueError:
        return None, False


def _monitoring_log_entry(value, proses: str, keterangan: str | None = None) -> dict | None:
    dt, has_time = _monitoring_parse_dt(value)
    if dt is None:
        return None
    entry = {
        "at": dt.strftime("%Y-%m-%d %H:%M:%S") if has_time else dt.strftime("%Y-%m-%d"),
        "tanggal": dt.strftime("%Y-%m-%d"),
        "jam": dt.strftime("%H:%M:%S") if has_time else None,
        "proses": proses,
    }
    note = (keterangan or "").strip() if keterangan is not None else ""
    if note:
        entry["keterangan"] = note
    return entry


def _monitoring_status_log(item: dict, bundle: dict) -> list[dict]:
    logs: list[dict] = []

    def add(value, proses: str, keterangan: str | None = None):
        entry = _monitoring_log_entry(value, proses, keterangan)
        if entry:
            logs.append(entry)

    add(
        item.get("date_created") or item.get("item_created_at") or item.get("tanggal_rencana"),
        "rencana",
        item.get("kode_rencana") or item.get("kode_rencana_item"),
    )
    for row in bundle.get("prep") or []:
        status = (row.get("status") or "").strip().lower()
        created = row.get("date_created")
        saved = row.get("date_saved")
        kode = row.get("kode_proses")
        if status == "completed":
            if saved:
                add(created, "proses_started", kode)
                add(saved, "proses_completed", kode)
            else:
                add(created, "proses_completed", kode)
        elif status == "saved":
            if saved:
                add(created, "proses_started", kode)
                add(saved, "proses_saved", kode)
            else:
                add(created, "proses_saved", kode)
        elif status == "started":
            add(created, "proses_started", kode)
        elif status:
            add(created, "proses_draft", kode)
    for row in bundle.get("lab") or []:
        add(row.get("date_created"), "lab", row.get("kode_lot_warna"))
    for row in bundle.get("usage") or []:
        add(row.get("date_created"), "usage", row.get("kode_lot_warna"))
    for row in bundle.get("checkpoint") or []:
        result = (row.get("result") or "").strip().upper()
        proses = "checkpoint_ok" if result == "OK" else "checkpoint"
        add(
            row.get("measured_at") or row.get("created_at"),
            proses,
            result or row.get("treatment"),
        )
    for row in bundle.get("packing") or []:
        status = (row.get("status") or "").strip().lower()
        created = row.get("date_created")
        finished = row.get("date_finished")
        kode = row.get("kode_packing")
        if status == "finished":
            if finished:
                add(created, "packing", kode)
                add(finished, "packing_finished", kode)
            else:
                add(created, "packing_finished", kode)
        elif status:
            add(created, "packing", kode)
    for row in bundle.get("fg") or []:
        status = (row.get("status") or "").strip().lower()
        date_in = row.get("date_in")
        date_out = row.get("date_out")
        kode = row.get("kode_packing")
        if status == "out":
            if date_out:
                add(date_in, "gudang_fg", kode)
                add(date_out, "gudang_fg_out", kode)
            else:
                add(date_in or date_out, "gudang_fg_out", kode)
        elif status:
            add(date_in, "gudang_fg", kode)

    rank = {code: i for i, code in enumerate(_MONITOR_STATUS_RANK)}
    logs.sort(key=lambda e: (e.get("at") or "", rank.get(e.get("proses") or "", 99)))
    return logs


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
        "i.color, i.thickness, i.emboss, i.created_at AS item_created_at, "
        "r.kode_rencana, r.nama_rencana, "
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
        "checkpoint_status, total_size, date_created, date_saved FROM tbl_persiapan_kulit WHERE rencana_item_id IN "
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
            "SELECT id, rencana_item_id, kode_wip, kode_packing, status, total_ukuran, total_lembar, "
            "date_created, date_finished "
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
            "SELECT packing_id, kode_packing, kode_wip, status, total_ukuran, date_in, date_out "
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
            f"SELECT kode_wip, result, treatment, measured_at, created_at FROM tbl_checkpoint "
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
            f"SELECT kode_wip, kode_lot_warna, nama_warna, qty_pembuatan, qty_digunakan, date_created "
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
        f"SELECT id, rencana_item_id, kode_lot_warna, nama_lot_warna, status, date_created "
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
            row["status_log"] = _monitoring_status_log(item, bundles[iid])
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
                    "nama_rencana",
                    "lot_no",
                    "status_terakhir",
                    "nama_customer",
                    "kode_rencana_item",
                    "kode_lot_wip",
                    "no_po",
                    "material_name",
                    "emboss",
                    "thickness",
                )
            ).lower()
            if q in blob:
                filtered.append(r)
        rows = filtered
    pg = parse_page_args(request.args, default_page_size=20)
    rows = sort_rows(
        rows,
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        fields={
            "no_so": "no_so",
            "nama_rencana": "nama_rencana",
            "lot_no": "lot_no",
            "status_terakhir": "status_terakhir",
            "material_name": "material_name",
            "kode_lot_wip": "kode_lot_wip",
            "id": "rencana_item_id",
        },
    )
    page_rows, total = slice_page(rows, page=pg["page"], page_size=pg["page_size"], offset=pg["offset"])
    return jsonify(
        page_payload(
            items=page_rows,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


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
    cur.execute(
        "SELECT COUNT(*) AS n FROM tbl_packing_roll WHERE packing_id=%s",
        (packing_id,),
    )
    n_roll = int((cur.fetchone() or {}).get("n") or 0)
    packing_out = _row(packing) or {}
    packing_out["qty_roll"] = n_roll
    packing_out["total_rolls"] = n_roll
    if line:
        line = dict(line)
        line["qty_roll"] = n_roll
    cur.close()
    conn.close()
    return jsonify(
        {
            "packing": packing_out,
            "line": _row(line) if line else None,
        }
    )


# ---- Checkpoint QC ----
CHECKPOINT_QC_NAME = "QC"
CHECKPOINT_USAGE_COLOR_NAME = "Penggunaan Lot Warna"


def _parse_treatment_list(raw) -> list[str]:
    if isinstance(raw, list):
        return [str(s).strip() for s in raw if str(s).strip()]
    return [s.strip() for s in str(raw or "").split(",") if s.strip()]


def _checkpoint_allowed_treatments(cur, kode_wip: str) -> list[str]:
    """Treatment yang dicentang saat proses persiapan untuk WIP ini."""
    cur.execute(
        "SELECT treatment_list FROM tbl_persiapan_kulit WHERE kode_wip=%s "
        "ORDER BY FIELD(status,'completed','saved','started','draft'), id DESC LIMIT 1",
        (kode_wip,),
    )
    row = cur.fetchone()
    return _parse_treatment_list(row.get("treatment_list") if row else "")


def _checkpoint_active_lab_lots(cur, kode_wip: str) -> list[dict]:
    """Lot warna aktif dari Lab; lot terkait WIP diutamakan."""
    cur.execute(
        "SELECT l.kode_lot_warna, l.nama_lot_warna, l.status, l.date_created, "
        "ri.kode_lot_wip, ri.color, ri.nama_customer, "
        "(SELECT COALESCE(SUM(d.qty), 0) FROM tbl_lab_lot_detail d "
        "WHERE d.kode_lot_warna = l.kode_lot_warna) AS qty_pembuatan, "
        "(SELECT COALESCE(SUM(u.qty_digunakan), 0) FROM tbl_usage_color u "
        "WHERE u.kode_lot_warna = l.kode_lot_warna) AS qty_used "
        "FROM tbl_lab_lot l "
        "LEFT JOIN tbl_rencana_item ri ON ri.id = l.rencana_item_id "
        "WHERE l.status = 'active' "
        "ORDER BY (ri.kode_lot_wip = %s) DESC, l.date_created DESC, l.kode_lot_warna DESC",
        (kode_wip,),
    )
    lots = []
    for row in _rows(cur.fetchall()):
        qty_pembuatan = float(row.get("qty_pembuatan") or 0)
        qty_used = float(row.get("qty_used") or 0)
        qty_sisa = max(0.0, qty_pembuatan - qty_used)
        lots.append(
            {
                **row,
                "qty_pembuatan": qty_pembuatan,
                "qty_used": qty_used,
                "qty_sisa": qty_sisa,
            }
        )
    return lots


def _apply_usage_color(
    cur,
    *,
    kode_wip: str,
    kode_lot_warna: str,
    qty_digunakan=None,
    stok_in_id=None,
    mark_used: bool = False,
):
    """Catat penggunaan lot warna. Return (payload, None) atau (None, pesan_error)."""
    from app import ensure_extended_tables

    ensure_extended_tables(cur)
    kode_wip = (kode_wip or "").strip()
    kode_lot_warna = (kode_lot_warna or "").strip()
    if not kode_wip or not kode_lot_warna:
        return None, "kode_wip dan kode_lot_warna wajib"

    cur.execute("SELECT * FROM tbl_lab_lot WHERE kode_lot_warna = %s", (kode_lot_warna,))
    lot = cur.fetchone()
    if not lot:
        return None, "Kode lot warna tidak ditemukan"
    if lot.get("status") != "active":
        return None, "Lot warna tidak aktif"

    cur.execute(
        "SELECT COALESCE(SUM(qty), 0) AS total_qty FROM tbl_lab_lot_detail "
        "WHERE kode_lot_warna = %s",
        (kode_lot_warna,),
    )
    qty_pembuatan = float((cur.fetchone() or {}).get("total_qty") or 0)
    cur.execute(
        "SELECT COALESCE(SUM(qty_digunakan), 0) AS used FROM tbl_usage_color "
        "WHERE kode_lot_warna = %s",
        (kode_lot_warna,),
    )
    qty_already_used = float((cur.fetchone() or {}).get("used") or 0)
    qty_sisa = max(0.0, qty_pembuatan - qty_already_used)

    if qty_digunakan is None or qty_digunakan == "":
        qty_digunakan = qty_sisa if qty_sisa > 0 else qty_pembuatan
    else:
        try:
            qty_digunakan = float(qty_digunakan)
        except (TypeError, ValueError):
            return None, "qty_digunakan harus angka"
    if qty_digunakan <= 0:
        return None, "qty_digunakan harus > 0"
    if qty_pembuatan > 0 and qty_digunakan > qty_sisa + 1e-9:
        return None, f"Qty melebihi sisa lot ({qty_sisa})"

    bridge = None
    stock_out_id = None
    if stok_in_id:
        from dual_gudang import GUDANG_LAPANGAN, normalize_gudang

        try:
            stok_in_id = int(stok_in_id)
        except (TypeError, ValueError):
            return None, "stok_in_id tidak valid"
        cur.execute("SELECT * FROM tbl_stok_kimia_in WHERE id=%s", (stok_in_id,))
        stok = cur.fetchone()
        if not stok:
            return None, "Lot stok kimia tidak ditemukan"
        if normalize_gudang(stok.get("gudang")) != GUDANG_LAPANGAN:
            return None, "Usage color hanya boleh dari gudang lapangan"
        sisa = float(stok["qty_sisa"] or 0)
        if qty_digunakan > sisa:
            return None, f"Stok kimia tidak cukup (sisa {sisa})"
        cur.execute(
            "INSERT INTO tbl_stok_kimia_out (stok_in_id, kimia_id, qty, jumlah_kemasan, tujuan, kode_wip, tanggal) "
            "VALUES (%s,%s,%s,NULL,'produksi',%s,%s)",
            (stok_in_id, stok["kimia_id"], qty_digunakan, kode_wip, date.today().isoformat()),
        )
        stock_out_id = cur.lastrowid
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
            return None, "Lot kimia belum ter-map erp_material_id"

    cur.execute(
        "INSERT INTO tbl_usage_color "
        "(kode_wip, kode_lot_warna, nama_warna, qty_pembuatan, qty_digunakan, stok_in_id, stok_out_id) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (
            kode_wip,
            kode_lot_warna,
            lot["nama_lot_warna"],
            qty_pembuatan,
            qty_digunakan,
            stok_in_id,
            stock_out_id,
        ),
    )
    new_id = cur.lastrowid

    lot_status = lot.get("status")
    if mark_used:
        cur.execute(
            "UPDATE tbl_lab_lot SET status='used' WHERE kode_lot_warna=%s",
            (kode_lot_warna,),
        )
        lot_status = "used"
    else:
        cur.execute(
            "SELECT COALESCE(SUM(qty_digunakan), 0) AS used FROM tbl_usage_color "
            "WHERE kode_lot_warna = %s",
            (kode_lot_warna,),
        )
        used = float((cur.fetchone() or {}).get("used") or 0)
        if qty_pembuatan > 0 and used >= qty_pembuatan:
            cur.execute(
                "UPDATE tbl_lab_lot SET status='used' WHERE kode_lot_warna=%s",
                (kode_lot_warna,),
            )
            lot_status = "used"

    return (
        {
            "id": new_id,
            "kode_lot_warna": kode_lot_warna,
            "qty_digunakan": qty_digunakan,
            "qty_pembuatan": qty_pembuatan,
            "lot_status": lot_status,
            "stok_deducted": bool(stok_in_id),
            "bridge": bridge,
        },
        None,
    )


def _resolve_checkpoint_treatment(cur, raw, *, allow_empty_as_qc=False):
    """Return nama treatment, False if invalid, None if empty and not allowed."""
    from app import ensure_master_treatment

    name = (raw or "").strip()
    if not name:
        return CHECKPOINT_QC_NAME if allow_empty_as_qc else None
    if name.upper() == CHECKPOINT_QC_NAME:
        return CHECKPOINT_QC_NAME
    if name == CHECKPOINT_USAGE_COLOR_NAME:
        return CHECKPOINT_USAGE_COLOR_NAME
    ensure_master_treatment(cur)
    cur.execute(
        "SELECT nama_treatment FROM tbl_master_treatment "
        "WHERE nama_treatment=%s AND COALESCE(is_active, 1)=1 LIMIT 1",
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
    pg = parse_page_args(request.args, default_page_size=20)
    order = order_sql(
        {
            "measured_at": "measured_at",
            "kode_wip": "kode_wip",
            "result": "result",
            "treatment": "treatment",
            "id": "id",
        },
        sort_by=pg["sort_by"],
        sort_dir=pg["sort_dir"],
        default_sql="measured_at DESC, id DESC",
    )
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()
    where = " WHERE 1=1"
    params: list = []
    if kode_wip:
        where += " AND kode_wip=%s"
        params.append(kode_wip)
    if result_f in ("OK", "NG"):
        where += " AND UPPER(IFNULL(result,''))=%s"
        params.append(result_f)
    if treatment_f:
        where += " AND IFNULL(treatment,'')=%s"
        params.append(treatment_f)
    if q:
        like = f"%{q}%"
        where += (
            " AND (kode_wip LIKE %s OR IFNULL(kode_packing,'') LIKE %s "
            "OR IFNULL(remark,'') LIKE %s OR IFNULL(result,'') LIKE %s "
            "OR IFNULL(treatment,'') LIKE %s)"
        )
        params.extend([like, like, like, like, like])
    cur.execute(f"SELECT COUNT(*) AS c FROM tbl_checkpoint{where}", params)
    total = int((cur.fetchone() or {}).get("c") or 0)
    cur.execute(
        f"SELECT * FROM tbl_checkpoint{where} ORDER BY {order} LIMIT %s OFFSET %s",
        params + [pg["page_size"], pg["offset"]],
    )
    rows = _attach_plan_info(cur, _rows(cur.fetchall()))
    cur.close()
    conn.close()
    return jsonify(
        page_payload(
            items=rows,
            total=total,
            page=pg["page"],
            page_size=pg["page_size"],
            offset=pg["offset"],
        )
    )


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
        return _err("WIP tidak ditemukan di MRP", 404)

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
    treatment_allowed = _parse_treatment_list((prep or {}).get("treatment_list"))
    from app import ensure_extended_tables, ensure_lab_tables

    ensure_extended_tables(cur)
    ensure_lab_tables(cur)
    conn.commit()
    lab_lots = _checkpoint_active_lab_lots(cur, kode_wip)
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
            "treatment_allowed": treatment_allowed,
            "lab_lots": lab_lots,
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
    is_usage_color = treatment == CHECKPOINT_USAGE_COLOR_NAME
    usage_color_result = None
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
    elif is_usage_color:
        kode_lot_warna = (body.get("kode_lot_warna") or "").strip()
        if not kode_lot_warna:
            cur.close()
            conn.close()
            return _err("Pilih lot warna dari Lab")
        usage_color_result, err = _apply_usage_color(
            cur,
            kode_wip=kode_wip,
            kode_lot_warna=kode_lot_warna,
            qty_digunakan=body.get("qty_digunakan"),
            mark_used=True,
        )
        if err:
            cur.close()
            conn.close()
            code = 404 if "tidak ditemukan" in err else 400
            return _err(err, code)
        lot_label = kode_lot_warna
        if remark:
            remark = f"{remark} · {lot_label}"
        else:
            remark = lot_label
        result = None
        is_ok = 1
        thickness = None
        softness = None
    else:
        allowed = _checkpoint_allowed_treatments(cur, kode_wip)
        if not allowed:
            cur.close()
            conn.close()
            return _err(
                "Belum ada treatment dari proses persiapan untuk WIP ini. "
                "Centang treatment di Proses Persiapan dulu."
            )
        if treatment not in allowed:
            cur.close()
            conn.close()
            return _err(
                f"Treatment '{treatment}' tidak termasuk rencana persiapan "
                f"({', '.join(allowed)})"
            )
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
        return _err("WIP tidak ditemukan di MRP", 404)

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

    cp_type = body.get("checkpoint_type") or (
        "qc" if is_qc else ("usage_color" if is_usage_color else "treatment")
    )
    cur.execute(
        "INSERT INTO tbl_checkpoint "
        "(kode_wip, kode_packing, checkpoint_type, treatment, thickness_actual, softness_actual, "
        "result, is_ok, remark, erp_production_detail_id) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (
            kode_wip,
            kode_packing,
            cp_type[:50],
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
    resp = {
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
    if usage_color_result:
        resp["usage_color"] = usage_color_result
    return jsonify(resp), 201


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
