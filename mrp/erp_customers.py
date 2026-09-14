"""Resolve customer dari Tonghong ERP (customers) — SSOT, bukan master_customer lokal."""

from __future__ import annotations

import re
from typing import Any, Optional

import mysql.connector

from db import root_db_config
import os

_ERP_DB = os.getenv("ERP_DB_NAME", "tonghong_erp")


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _connect():
    cfg = root_db_config()
    cfg["database"] = _ERP_DB
    return mysql.connector.connect(**cfg)


def _slug_code(nama: str) -> str:
    base = re.sub(r"[^A-Z0-9]+", "-", (nama or "CUST").upper()).strip("-")[:24] or "CUST"
    return f"MRP-{base}"


def resolve_customer(
    name_or_code: str | None,
    *,
    create_if_missing: bool | None = None,
) -> Optional[dict]:
    """
    Cari customers by name/code (case-insensitive).
    create_if_missing default dari env MRP_AUTO_CREATE_ERP_CUSTOMER (false di prod).
    """
    if create_if_missing is None:
        flag = (os.getenv("MRP_AUTO_CREATE_ERP_CUSTOMER") or "").strip().lower()
        if flag in {"1", "true", "yes", "on"}:
            create_if_missing = True
        elif flag in {"0", "false", "no", "off"}:
            create_if_missing = False
        else:
            # default: boleh di non-prod, tolak di production
            create_if_missing = (os.getenv("APP_ENV") or "dev").strip().lower() not in {
                "prod",
                "production",
            }
    raw = (name_or_code or "").strip()
    if not raw or raw == "-":
        return None
    conn = _connect()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT id, code, name FROM customers "
            "WHERE LOWER(TRIM(name)) = %s OR LOWER(TRIM(COALESCE(code,''))) = %s "
            "ORDER BY id LIMIT 1",
            (_norm(raw), _norm(raw)),
        )
        row = cur.fetchone()
        if row:
            return {
                "id": int(row["id"]),
                "code": row.get("code"),
                "name": (row.get("name") or raw).strip(),
            }
        if not create_if_missing:
            return None
        code = _slug_code(raw)
        # pastikan unik
        cur.execute("SELECT id FROM customers WHERE code=%s LIMIT 1", (code,))
        if cur.fetchone():
            code = f"{code}-{abs(hash(raw)) % 10000}"
        cur.execute(
            "INSERT INTO customers (code, name, is_active) VALUES (%s, %s, 1)",
            (code, raw[:255]),
        )
        conn.commit()
        return {"id": int(cur.lastrowid), "code": code, "name": raw[:255]}
    finally:
        cur.close()
        conn.close()


def fetch_customer(customer_id: int) -> Optional[dict]:
    conn = _connect()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT id, code, name FROM customers WHERE id=%s LIMIT 1",
            (int(customer_id),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return {"id": int(row["id"]), "code": row.get("code"), "name": row.get("name")}
    finally:
        cur.close()
        conn.close()


def list_customers(limit: int = 500) -> list[dict]:
    conn = _connect()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(
            "SELECT id, code, name FROM customers "
            "WHERE COALESCE(is_active, 1)=1 AND name IS NOT NULL AND TRIM(name)!='' "
            "ORDER BY name LIMIT %s",
            (int(limit),),
        )
        return [
            {"id": int(r["id"]), "code": r.get("code"), "name": r.get("name")}
            for r in (cur.fetchall() or [])
        ]
    finally:
        cur.close()
        conn.close()


def ensure_customer_id(nama: str | None, *, erp_customer_id: int | None = None) -> tuple[int, str]:
    """
    Return (erp_customer_id, display_name).
    Prefer erp_customer_id jika valid; else resolve by name (auto-create).
    """
    if erp_customer_id:
        row = fetch_customer(int(erp_customer_id))
        if row:
            return int(row["id"]), (row.get("name") or nama or "-").strip() or "-"
    resolved = resolve_customer(nama)  # hormati MRP_AUTO_CREATE_ERP_CUSTOMER / APP_ENV
    if not resolved:
        raise ValueError("Customer wajib (nama/kode) dan harus ada di Master Customer ERP")
    return int(resolved["id"]), resolved["name"]
