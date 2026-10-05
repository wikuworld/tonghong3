#!/usr/bin/env python3
"""Perbaiki lot PUMSL044260926001 dan laporkan baris SO lain yang resepnya tidak cocok.

Usage:
  python scripts/repair_lot_pumsl044260926001.py --report
  python scripts/repair_lot_pumsl044260926001.py --apply

--report hanya membaca. --apply mengembalikan kulit, membatalkan persiapan,
melepas alokasi MRP, dan mengosongkan resep yang tidak cocok pada lot ini.
Baris SO lain tidak diubah.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import pymysql
from pymysql.cursors import DictCursor

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.color_swatch import swatch_recipe_mismatch_fields

LOT = "PUMSL044260926001"
WIP = "WIP-20260926-00001"
RETURN_NOTE = f"Pengembalian perbaikan lot {LOT} — WIP {WIP}"
DEFAULT_ERP = "mysql+pymysql://uat_tonghong_erp:UatTonghongErp2026@127.0.0.1:3306/uat_tonghong_erp"
DEFAULT_MRP = "mysql+pymysql://uat_tonghong_mrp:UatTonghongMrp2026@127.0.0.1:3306/uat_tonghong_mrp"


def _connect(url: str):
    raw = url.replace("mysql+pymysql://", "mysql://").replace("mysql+mysqlconnector://", "mysql://")
    parsed = urlparse(raw)
    return pymysql.connect(
        host=parsed.hostname or "127.0.0.1",
        port=parsed.port or 3306,
        user=parsed.username or "",
        password=parsed.password or "",
        database=(parsed.path or "").lstrip("/"),
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
    )


def mismatched_lines(cur) -> list[dict]:
    cur.execute(
        "SELECT d.id, d.thi_line_ref, d.material_name, d.color, d.emboss, "
        "d.color_swatch_recipe_id, d.color_reference, d.color_standard, "
        "r.material_name AS recipe_material, r.color_name AS recipe_color, "
        "r.emboss AS recipe_emboss, r.color_standard AS recipe_standard, r.factory_key "
        "FROM po_details d "
        "JOIN color_swatch_recipes r ON r.id = d.color_swatch_recipe_id "
        "WHERE d.color_swatch_recipe_id IS NOT NULL "
        "ORDER BY d.id"
    )
    out = []
    for row in cur.fetchall():
        bad = swatch_recipe_mismatch_fields(
            recipe_material=row["recipe_material"],
            recipe_color=row["recipe_color"],
            recipe_emboss=row["recipe_emboss"],
            material_name=row["material_name"],
            color=row["color"],
            emboss=row["emboss"],
        )
        if not bad:
            continue
        out.append(
            {
                "po_detail_id": row["id"],
                "lot": row["thi_line_ref"],
                "mismatch": bad,
                "line_material": row["material_name"],
                "line_color": row["color"],
                "line_emboss": row["emboss"],
                "recipe_id": row["color_swatch_recipe_id"],
                "recipe_material": row["recipe_material"],
                "recipe_color": row["recipe_color"],
                "recipe_emboss": row["recipe_emboss"],
                "target_lot": (row["thi_line_ref"] or "") == LOT,
            }
        )
    return out


def _ensure_voided_status(cur) -> None:
    cur.execute("SHOW COLUMNS FROM tbl_persiapan_kulit LIKE 'status'")
    col = cur.fetchone()
    col_type = str((col or {}).get("Type") or "")
    if col and "voided" not in col_type:
        cur.execute(
            "ALTER TABLE tbl_persiapan_kulit MODIFY status "
            "ENUM('draft','started','saved','completed','voided') DEFAULT 'draft'"
        )


def _movement_attrs(cur, palet: str, yl: str) -> tuple[str, str]:
    cur.execute(
        "SELECT thickness, warna FROM tbl_yl_movement "
        "WHERE kode_palet=%s AND kode_yl=%s AND direction='OUT' "
        "AND keterangan LIKE %s ORDER BY id DESC LIMIT 1",
        (palet, yl, f"%{WIP}%"),
    )
    row = cur.fetchone() or {}
    return str(row.get("thickness") or ""), str(row.get("warna") or "")


def _return_yl(cur, palet: str, yl: str, qty: float, thickness: str, warna: str) -> bool:
    if qty <= 1e-9:
        return False
    cur.execute(
        "SELECT id FROM tbl_yl_movement "
        "WHERE kode_palet=%s AND kode_yl=%s AND direction='IN' AND keterangan=%s LIMIT 1",
        (palet, yl, RETURN_NOTE),
    )
    if cur.fetchone():
        return False
    cur.execute(
        "SELECT id, qty, thickness, warna FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
        (palet, yl),
    )
    row = cur.fetchone()
    use_thickness = str((row or {}).get("thickness") or thickness or "")
    use_warna = str((row or {}).get("warna") or warna or "")
    cur.execute(
        "INSERT INTO tbl_yl_movement "
        "(kode_yl, kode_palet, direction, thickness, warna, qty, tanggal, keterangan) "
        "VALUES (%s,%s,'IN',%s,%s,%s,CURDATE(),%s)",
        (yl, palet, use_thickness, use_warna, qty, RETURN_NOTE),
    )
    if row:
        cur.execute(
            "UPDATE tbl_yl SET qty=%s WHERE id=%s",
            (float(row.get("qty") or 0) + qty, row["id"]),
        )
    else:
        cur.execute(
            "INSERT INTO tbl_yl (kode_yl, kode_palet, thickness, warna, qty) VALUES (%s,%s,%s,%s,%s)",
            (yl, palet, use_thickness, use_warna, qty),
        )
    return True


def _recompute_po(cur, po_id: int) -> tuple[float, str]:
    cur.execute(
        "SELECT COALESCE(SUM(qty_proses), 0) AS tot FROM tbl_rencana_item_po WHERE po_id=%s",
        (po_id,),
    )
    tot = float((cur.fetchone() or {}).get("tot") or 0)
    cur.execute(
        "SELECT COALESCE(SUM(qty), 0) AS tot FROM tbl_stock_sisa_fg_assign WHERE po_id=%s",
        (po_id,),
    )
    tot += float((cur.fetchone() or {}).get("tot") or 0)
    cur.execute("SELECT qty_order, status FROM tbl_master_po WHERE id=%s", (po_id,))
    po = cur.fetchone()
    if not po:
        raise SystemExit(f"tbl_master_po id {po_id} tidak ditemukan")
    qty_order = float(po.get("qty_order") or 0)
    status = str(po.get("status") or "").strip()
    if status != "cancelled":
        if tot >= qty_order > 0:
            status = "completed"
        elif tot > 0:
            status = "partial"
        else:
            status = "outstanding"
    cur.execute(
        "UPDATE tbl_master_po SET qty_processed=%s, status=%s WHERE id=%s",
        (tot, status, po_id),
    )
    return tot, status


def apply_repair(erp, mrp) -> dict:
    with erp.cursor() as cur:
        cur.execute(
            "SELECT id, color_swatch_recipe_id, color_reference, color_standard "
            "FROM po_details WHERE thi_line_ref=%s",
            (LOT,),
        )
        detail = cur.fetchone()
    if not detail:
        raise SystemExit(f"Baris SO lot {LOT} tidak ditemukan")
    with mrp.cursor() as cur:
        cur.execute(
            "SELECT id, color_swatch, status, qty_processed FROM tbl_master_po WHERE lot_number=%s",
            (LOT,),
        )
        master = cur.fetchone()
        cur.execute(
            "SELECT id, status, total_size, rencana_item_id FROM tbl_persiapan_kulit WHERE kode_wip=%s",
            (WIP,),
        )
        persiapan = cur.fetchone()
    if not master:
        raise SystemExit(f"Master PO MRP lot {LOT} tidak ditemukan")
    if not persiapan:
        raise SystemExit(f"Persiapan WIP {WIP} tidak ditemukan")

    returned = []
    with mrp.cursor() as cur:
        _ensure_voided_status(cur)
        cur.execute(
            "SELECT id, kode_palet, kode_yl, qty_consumed, yl_consumed "
            "FROM tbl_persiapan_ky WHERE persiapan_id=%s",
            (persiapan["id"],),
        )
        for ky in cur.fetchall():
            if int(ky.get("yl_consumed") or 0) != 1:
                continue
            qty = float(ky.get("qty_consumed") or 0)
            palet = str(ky.get("kode_palet") or "").strip()
            yl = str(ky.get("kode_yl") or "").strip()
            thickness, warna = _movement_attrs(cur, palet, yl)
            if _return_yl(cur, palet, yl, qty, thickness, warna):
                returned.append({"palet": palet, "yl": yl, "qty": qty, "warna": warna, "tebal": thickness})
        cur.execute(
            "UPDATE tbl_persiapan_kulit SET status='voided', total_size=0, "
            "checkpoint_status=%s WHERE id=%s",
            (f"voided: kulit tidak cocok {LOT}", persiapan["id"]),
        )
        cur.execute("DELETE FROM tbl_rencana_item_po WHERE po_id=%s", (master["id"],))
        qty_processed, status = _recompute_po(cur, int(master["id"]))
        factory_key = None
    with erp.cursor() as cur:
        if detail.get("color_swatch_recipe_id"):
            cur.execute(
                "SELECT factory_key FROM color_swatch_recipes WHERE id=%s",
                (detail["color_swatch_recipe_id"],),
            )
            recipe = cur.fetchone()
            factory_key = (recipe or {}).get("factory_key")
        cur.execute(
            "UPDATE po_details SET color_swatch_recipe_id=NULL, color_reference=NULL, "
            "color_standard=NULL WHERE id=%s AND thi_line_ref=%s",
            (detail["id"], LOT),
        )
        cleared = cur.rowcount
    with mrp.cursor() as cur:
        if factory_key and str(master.get("color_swatch") or "").strip() == str(factory_key).strip():
            cur.execute(
                "UPDATE tbl_master_po SET color_swatch=NULL WHERE id=%s",
                (master["id"],),
            )
    mrp.commit()
    erp.commit()
    return {
        "lot": LOT,
        "po_detail_id": detail["id"],
        "mrp_po_id": master["id"],
        "persiapan_id": persiapan["id"],
        "returned": returned,
        "qty_processed": qty_processed,
        "mrp_status": status,
        "erp_line_fields_cleared": cleared,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Perbaikan data lot {LOT}")
    parser.add_argument("--report", action="store_true", help="Daftar baris yang resepnya tidak cocok")
    parser.add_argument("--apply", action="store_true", help="Terapkan perbaikan lot ini saja")
    args = parser.parse_args()
    if not args.report and not args.apply:
        parser.error("Pilih --report atau --apply")

    erp_url = os.environ.get("ERP_DATABASE_URL") or os.environ.get("DATABASE_URL") or DEFAULT_ERP
    mrp_url = os.environ.get("MRP_DATABASE_URL") or DEFAULT_MRP
    erp = _connect(erp_url)
    mrp = _connect(mrp_url)
    try:
        with erp.cursor() as cur:
            mismatches = mismatched_lines(cur)
        print(json.dumps({"mismatched_lines": mismatches, "count": len(mismatches)}, indent=2, ensure_ascii=False))
        if args.apply:
            result = apply_repair(erp, mrp)
            print(json.dumps({"applied": result}, indent=2, ensure_ascii=False))
    except Exception:
        erp.rollback()
        mrp.rollback()
        raise
    finally:
        erp.close()
        mrp.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
