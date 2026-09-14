"""Baca raw_materials Tonghong ERP — SSOT katalog bahan baku (tanpa mirror MRP)."""

from __future__ import annotations

import os
from typing import Any, Optional

import mysql.connector

from db import root_db_config

_ERP_DB = os.getenv("ERP_DB_NAME", "tonghong_erp")

_TYPE_ALIASES = {
    "kimia": "kimia",
    "rp": "rp",
    "material": "material_lain",
    "material_lain": "material_lain",
    "material-lain": "material_lain",
    "kulit": "kulit",
}


def _erp_connect():
    cfg = root_db_config()
    cfg["database"] = _ERP_DB
    return mysql.connector.connect(**cfg)


def normalize_material_type(material_type: str | None) -> str:
    raw = (material_type or "").strip().lower()
    return _TYPE_ALIASES.get(raw, raw)


def fetch_material(material_id: int) -> Optional[dict]:
    conn = _erp_connect()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT id, code, name, material_type, unit, is_active "
            "FROM raw_materials WHERE id=%s LIMIT 1",
            (int(material_id),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return _shape(row)
    finally:
        cur.close()
        conn.close()


def fetch_material_by_code(code: str, material_type: str | None = None) -> Optional[dict]:
    code = (code or "").strip()
    if not code:
        return None
    conn = _erp_connect()
    cur = conn.cursor(dictionary=True)
    try:
        if material_type:
            mt = normalize_material_type(material_type)
            cur.execute(
                "SELECT id, code, name, material_type, unit, is_active "
                "FROM raw_materials WHERE code=%s AND material_type=%s LIMIT 1",
                (code, mt),
            )
        else:
            cur.execute(
                "SELECT id, code, name, material_type, unit, is_active "
                "FROM raw_materials WHERE code=%s LIMIT 1",
                (code,),
            )
        row = cur.fetchone()
        return _shape(row) if row else None
    finally:
        cur.close()
        conn.close()


def list_materials(
    material_type: str | None = None,
    *,
    keyword: str | None = None,
    limit: int = 2000,
    active_only: bool = True,
) -> list[dict]:
    conn = _erp_connect()
    cur = conn.cursor(dictionary=True)
    try:
        where = ["1=1"]
        params: list[Any] = []
        if active_only:
            where.append("COALESCE(is_active, 1)=1")
        if material_type:
            where.append("material_type=%s")
            params.append(normalize_material_type(material_type))
        if keyword and keyword.strip():
            where.append("(code LIKE %s OR name LIKE %s)")
            q = f"%{keyword.strip()}%"
            params.extend([q, q])
        sql = (
            "SELECT id, code, name, material_type, unit, is_active "
            f"FROM raw_materials WHERE {' AND '.join(where)} "
            "ORDER BY code LIMIT %s"
        )
        params.append(max(1, min(int(limit), 5000)))
        cur.execute(sql, params)
        return [_shape(r) for r in (cur.fetchall() or [])]
    finally:
        cur.close()
        conn.close()


def resolve_material(
    *,
    erp_material_id: int | None = None,
    code: str | None = None,
    material_type: str | None = None,
) -> Optional[dict]:
    if erp_material_id:
        row = fetch_material(int(erp_material_id))
        if row and material_type:
            if normalize_material_type(row.get("material_type")) != normalize_material_type(
                material_type
            ):
                return None
        return row
    if code:
        return fetch_material_by_code(code, material_type=material_type)
    return None


def ensure_erp_material(
    *,
    code: str,
    name: str,
    material_type: str,
    unit: str = "kg",
) -> Optional[int]:
    """Upsert ke ERP raw_materials (impor). Tidak menulis tabel mirror MRP."""
    code = (code or "").strip()
    if not code:
        return None
    mt = normalize_material_type(material_type)
    conn = _erp_connect()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM raw_materials WHERE code=%s LIMIT 1", (code,))
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE raw_materials SET name=%s, material_type=%s, unit=%s, is_active=1 "
                "WHERE id=%s",
                ((name or code)[:255], mt[:50], (unit or "kg")[:20], int(row["id"])),
            )
            conn.commit()
            return int(row["id"])
        cur.execute(
            "INSERT INTO raw_materials (code, name, material_type, unit, is_active) "
            "VALUES (%s, %s, %s, %s, 1)",
            (code[:50], (name or code)[:255], mt[:50], (unit or "kg")[:20]),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        cur.close()
        conn.close()


def _shape(row: dict) -> dict:
    return {
        "id": int(row["id"]),
        "erp_material_id": int(row["id"]),
        "code": row.get("code"),
        "name": row.get("name"),
        "material_type": row.get("material_type"),
        "unit": row.get("unit") or "kg",
        "is_active": bool(row.get("is_active", True)),
        "source": "raw_materials",
        # alias kompat UI lama
        "kode": row.get("code"),
        "nama": row.get("name"),
        "satuan": row.get("unit") or "kg",
    }
