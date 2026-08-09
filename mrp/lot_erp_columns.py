"""Migrasi kolom lot ke erp_material_id + snapshot (ERP-only catalogs)."""

from __future__ import annotations

from typing import Any

import mysql.connector

from db import get_db_connection, root_db_config
import os

_ERP_DB = os.getenv("ERP_DB_NAME", "tonghong")


def _col_names(cur, table: str) -> set[str]:
    try:
        cur.execute(f"SHOW COLUMNS FROM {table}")
    except mysql.connector.Error:
        return set()
    return {r["Field"] if isinstance(r, dict) else r[0] for r in cur.fetchall()}


def _add_col(cur, table: str, ddl: str) -> None:
    cols = _col_names(cur, table)
    # ddl like: erp_material_id BIGINT DEFAULT NULL
    name = ddl.split()[0]
    if name not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


def ensure_lot_erp_columns(cur) -> None:
    """Pastikan lot/out punya erp_material_id + snapshot; lepas FK ke mirror master_*."""
    # Drop orphan FK ke mirror catalog (master sudah di-drop).
    for table, fk_name in (
        ("tbl_stok_kimia_in", "tbl_stok_kimia_in_ibfk_1"),
        ("tbl_stok_kimia_out", "tbl_stok_kimia_out_ibfk_2"),
        ("tbl_stok_rp_in", "tbl_stok_rp_in_ibfk_1"),
        ("tbl_stok_rp_out", "tbl_stok_rp_out_ibfk_2"),
        ("tbl_stok_material_lain_in", "tbl_stok_material_lain_in_ibfk_1"),
        ("tbl_stok_material_lain_out", "tbl_stok_material_lain_out_ibfk_2"),
    ):
        if not _col_names(cur, table):
            continue
        try:
            cur.execute(f"ALTER TABLE {table} DROP FOREIGN KEY {fk_name}")
        except mysql.connector.Error:
            pass

    # kimia in
    if _col_names(cur, "tbl_stok_kimia_in"):
        _add_col(cur, "tbl_stok_kimia_in", "erp_material_id BIGINT DEFAULT NULL")
        _add_col(cur, "tbl_stok_kimia_in", "kode_material VARCHAR(50) DEFAULT NULL")
        _add_col(cur, "tbl_stok_kimia_in", "nama_material VARCHAR(255) DEFAULT NULL")
        try:
            cur.execute("ALTER TABLE tbl_stok_kimia_in MODIFY kimia_id INT NULL")
        except mysql.connector.Error:
            pass
    if _col_names(cur, "tbl_stok_kimia_out"):
        _add_col(cur, "tbl_stok_kimia_out", "erp_material_id BIGINT DEFAULT NULL")
        _add_col(cur, "tbl_stok_kimia_out", "kode_material VARCHAR(50) DEFAULT NULL")
        _add_col(cur, "tbl_stok_kimia_out", "nama_material VARCHAR(255) DEFAULT NULL")
        try:
            cur.execute("ALTER TABLE tbl_stok_kimia_out MODIFY kimia_id INT NULL")
        except mysql.connector.Error:
            pass
    # rp in
    if _col_names(cur, "tbl_stok_rp_in"):
        _add_col(cur, "tbl_stok_rp_in", "erp_material_id BIGINT DEFAULT NULL")
        _add_col(cur, "tbl_stok_rp_in", "kode_material VARCHAR(50) DEFAULT NULL")
        _add_col(cur, "tbl_stok_rp_in", "nama_material VARCHAR(255) DEFAULT NULL")
        try:
            cur.execute("ALTER TABLE tbl_stok_rp_in MODIFY rp_id INT NULL")
        except mysql.connector.Error:
            pass
    if _col_names(cur, "tbl_stok_rp_out"):
        _add_col(cur, "tbl_stok_rp_out", "erp_material_id BIGINT DEFAULT NULL")
        _add_col(cur, "tbl_stok_rp_out", "kode_material VARCHAR(50) DEFAULT NULL")
        _add_col(cur, "tbl_stok_rp_out", "nama_material VARCHAR(255) DEFAULT NULL")
        try:
            cur.execute("ALTER TABLE tbl_stok_rp_out MODIFY rp_id INT NULL")
        except mysql.connector.Error:
            pass
    # material lain
    if _col_names(cur, "tbl_stok_material_lain_in"):
        _add_col(cur, "tbl_stok_material_lain_in", "erp_material_id BIGINT DEFAULT NULL")
        _add_col(cur, "tbl_stok_material_lain_in", "kode_material VARCHAR(50) DEFAULT NULL")
        _add_col(cur, "tbl_stok_material_lain_in", "nama_material VARCHAR(255) DEFAULT NULL")
        try:
            cur.execute("ALTER TABLE tbl_stok_material_lain_in MODIFY material_id INT NULL")
        except mysql.connector.Error:
            pass
    if _col_names(cur, "tbl_stok_material_lain_out"):
        _add_col(cur, "tbl_stok_material_lain_out", "erp_material_id BIGINT DEFAULT NULL")
        _add_col(cur, "tbl_stok_material_lain_out", "kode_material VARCHAR(50) DEFAULT NULL")
        _add_col(cur, "tbl_stok_material_lain_out", "nama_material VARCHAR(255) DEFAULT NULL")
        try:
            cur.execute("ALTER TABLE tbl_stok_material_lain_out MODIFY material_id INT NULL")
        except mysql.connector.Error:
            pass


def backfill_lot_erp_ids() -> dict[str, Any]:
    """Isi erp_material_id lot dari master_* lama (sekali jalan sebelum drop mirror)."""
    report: dict[str, Any] = {}
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    ensure_lot_erp_columns(cur)
    conn.commit()

    specs = [
        (
            "tbl_stok_kimia_in",
            "kimia_id",
            "master_kimia",
            "COALESCE(m.kode_kimia, m.kode_barang)",
            "COALESCE(m.nama_kimia, m.nama_barang)",
        ),
        (
            "tbl_stok_rp_in",
            "rp_id",
            "master_rp",
            "m.kode_rp",
            "COALESCE(m.nama_rp, m.nama_jenis)",
        ),
        (
            "tbl_stok_material_lain_in",
            "material_id",
            "master_material_lain",
            "m.kode_material",
            "m.nama_material",
        ),
    ]
    for table, fk, master, code_expr, name_expr in specs:
        if not _col_names(cur, table) or not _col_names(cur, master):
            report[table] = {"skipped": True}
            continue
        # Qualify master columns in COALESCE
        code_sql = code_expr if "." in code_expr else f"m.{code_expr}" if code_expr.count("(") == 0 else code_expr
        # from master.erp_material_id
        cur.execute(
            f"UPDATE {table} t "
            f"JOIN {master} m ON m.id = t.{fk} "
            f"SET t.erp_material_id = m.erp_material_id, "
            f"t.kode_material = COALESCE(t.kode_material, {code_expr}), "
            f"t.nama_material = COALESCE(t.nama_material, {name_expr}) "
            f"WHERE (t.erp_material_id IS NULL OR t.erp_material_id=0) "
            f"AND m.erp_material_id IS NOT NULL"
        )
        n1 = cur.rowcount
        # match by code to ERP if still null
        erp = root_db_config()
        erp["database"] = _ERP_DB
        econn = mysql.connector.connect(**erp)
        ecur = econn.cursor(dictionary=True)
        cur.execute(
            f"SELECT t.id, {code_expr} AS kode FROM {table} t "
            f"JOIN {master} m ON m.id = t.{fk} "
            f"WHERE t.erp_material_id IS NULL OR t.erp_material_id=0"
        )
        n2 = 0
        for row in cur.fetchall() or []:
            kode = (row.get("kode") or "").strip()
            if not kode:
                continue
            ecur.execute("SELECT id, code, name FROM raw_materials WHERE code=%s LIMIT 1", (kode,))
            hit = ecur.fetchone()
            if not hit:
                continue
            cur.execute(
                f"UPDATE {table} SET erp_material_id=%s, "
                f"kode_material=COALESCE(kode_material, %s), "
                f"nama_material=COALESCE(nama_material, %s) WHERE id=%s",
                (int(hit["id"]), hit.get("code"), hit.get("name"), row["id"]),
            )
            n2 += 1
        ecur.close()
        econn.close()
        report[table] = {"from_master_map": n1, "from_code_match": n2}
    conn.commit()
    cur.close()
    conn.close()
    return report


def drop_mirror_catalog_tables() -> list[str]:
    """Drop tabel mirror katalog MRP (setelah migrasi FK)."""
    dropped: list[str] = []
    conn = get_db_connection()
    cur = conn.cursor()
    for table in (
        "master_customer",
        "master_erp",
        "master_kulit",
        "master_kimia",
        "master_rp",
        "master_material_lain",
    ):
        try:
            cur.execute(f"DROP TABLE IF EXISTS {table}")
            dropped.append(table)
        except mysql.connector.Error:
            pass
    conn.commit()
    cur.close()
    conn.close()
    return dropped
