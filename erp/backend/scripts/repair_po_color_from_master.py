#!/usr/bin/env python3
"""Isi kode warna baris PO dari master item dan lepas resep yang tidak sejalan.

Usage:
  python scripts/repair_po_color_from_master.py --report
  python scripts/repair_po_color_from_master.py --apply

Hanya baris yang punya master_item_id. Material, warna, emboss, tebal, qty,
dan nomor lot tidak diubah.
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

DEFAULT_ERP = "mysql+pymysql://uat_tonghong_erp:UatTonghongErp2026@127.0.0.1:3306/uat_tonghong_erp"


def _same(a, b) -> bool:
    return " ".join(str(a or "").split()).casefold() == " ".join(str(b or "").split()).casefold()


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


def _plan_row(row: dict) -> dict | None:
    master_code = str(row.get("master_code") or "").strip()
    ref = str(row.get("color_reference") or "").strip()
    changes: dict = {"po_detail_id": row["id"], "lot": row.get("thi_line_ref"), "item_code": row.get("item_code")}
    dirty = False
    if master_code and not _same(ref, master_code):
        changes["color_reference"] = master_code
        dirty = True
    recipe_id = row.get("color_swatch_recipe_id")
    if recipe_id:
        code_mismatch = bool(master_code) and not _same(row.get("recipe_code"), master_code)
        emboss_mismatch = not _same(row.get("recipe_emboss"), row.get("master_emboss"))
        if code_mismatch or emboss_mismatch:
            changes["detach_recipe_id"] = recipe_id
            changes["clear_color_standard"] = True
            changes["clear_backing"] = True
            dirty = True
        elif not str(row.get("color_standard") or "").strip() and str(row.get("recipe_standard") or "").strip():
            changes["color_standard"] = str(row.get("recipe_standard") or "").strip()
            dirty = True
    return changes if dirty else None


def _load(cur) -> list[dict]:
    cur.execute(
        "SELECT d.id, d.thi_line_ref, d.color_reference, d.color_standard, d.backing, "
        "d.color_swatch_recipe_id, mi.item_code, mi.color_code AS master_code, "
        "mi.emboss AS master_emboss, r.color_code AS recipe_code, r.emboss AS recipe_emboss, "
        "r.color_standard AS recipe_standard "
        "FROM po_details d "
        "JOIN master_items mi ON mi.id = d.master_item_id "
        "LEFT JOIN color_swatch_recipes r ON r.id = d.color_swatch_recipe_id "
        "WHERE d.master_item_id IS NOT NULL "
        "ORDER BY d.id"
    )
    return list(cur.fetchall())


def apply_plans(cur, plans: list[dict]) -> int:
    updated = 0
    for plan in plans:
        sets = []
        params = []
        if "color_reference" in plan:
            sets.append("color_reference=%s")
            params.append(plan["color_reference"])
        if "color_standard" in plan:
            sets.append("color_standard=%s")
            params.append(plan["color_standard"])
        if plan.get("detach_recipe_id"):
            sets.append("color_swatch_recipe_id=NULL")
            sets.append("color_standard=NULL")
            sets.append("backing=NULL")
        if not sets:
            continue
        params.append(plan["po_detail_id"])
        cur.execute(f"UPDATE po_details SET {', '.join(sets)} WHERE id=%s", params)
        updated += cur.rowcount
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Samakan kode warna baris PO dengan master item")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.report and not args.apply:
        parser.error("Pilih --report atau --apply")

    url = os.environ.get("ERP_DATABASE_URL") or os.environ.get("DATABASE_URL") or DEFAULT_ERP
    conn = _connect(url)
    try:
        with conn.cursor() as cur:
            plans = [p for row in _load(cur) if (p := _plan_row(row))]
        print(json.dumps({"changes": plans, "count": len(plans)}, indent=2, ensure_ascii=False))
        if args.apply and plans:
            with conn.cursor() as cur:
                updated = apply_plans(cur, plans)
            conn.commit()
            print(json.dumps({"applied_rows": updated}, ensure_ascii=False))
        elif args.apply:
            print(json.dumps({"applied_rows": 0}, ensure_ascii=False))
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
