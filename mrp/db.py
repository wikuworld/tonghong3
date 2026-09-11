"""Shared DB config for MRP service — reads Docker/env defaults."""
from __future__ import annotations

import os

import mysql.connector


def db_config() -> dict:
    return {
        "host": os.getenv("MRP_DB_HOST", "mariadb"),
        "port": int(os.getenv("MRP_DB_PORT", "3306")),
        "user": os.getenv("MRP_DB_USER", "tonghong_mrp"),
        "password": os.getenv("MRP_DB_PASSWORD", "tonghong_mrp_secret"),
        "database": os.getenv("MRP_DB_NAME", "tonghong_mrp"),
        "connection_timeout": int(os.getenv("MRP_DB_CONNECT_TIMEOUT", "10")),
        # Autocommit: tanpa ini, SELECT/SHOW di transaksi terbuka menahan
        # metadata lock sampai commit — satu koneksi Sleep cukup menggantung DDL ensure_*.
        "autocommit": True,
    }


def get_db_connection(**overrides):
    cfg = db_config()
    cfg.update(overrides)
    conn = mysql.connector.connect(**cfg)
    # ensure_*_tables() menjalankan DDL idempoten di hampir setiap request. Dengan
    # lock_wait_timeout default (1 hari) satu koneksi idle-in-transaction cukup
    # untuk menggantung request selamanya.
    lock_wait = int(os.getenv("MRP_DB_LOCK_WAIT_TIMEOUT", "5"))
    cur = conn.cursor()
    cur.execute(
        "SET SESSION lock_wait_timeout=%s, innodb_lock_wait_timeout=%s",
        (lock_wait, lock_wait),
    )
    cur.close()
    return conn


def root_db_config() -> dict:
    """Root (or privileged) connection for bootstrap — no default database required."""
    return {
        "host": os.getenv("MRP_DB_HOST", "mariadb"),
        "port": int(os.getenv("MRP_DB_PORT", "3306")),
        "user": os.getenv("MRP_DB_ROOT_USER", "root"),
        "password": os.getenv("MYSQL_ROOT_PASSWORD", os.getenv("MRP_DB_ROOT_PASSWORD", "root")),
    }


def erp_db_config() -> dict:
    """Koneksi baca katalog ERP (raw_materials / customers / master_items).

    Jangan pakai root: di MariaDB native, root@127.0.0.1 memakai unix_socket auth
    dan gagal lewat TCP (error 1698 Access denied).
    """
    host = os.getenv("ERP_DB_HOST") or os.getenv("MRP_DB_HOST") or "127.0.0.1"
    port = int(os.getenv("ERP_DB_PORT") or os.getenv("MRP_DB_PORT") or os.getenv("MYSQL_PORT") or "3306")
    user = (os.getenv("ERP_DB_USER") or os.getenv("MYSQL_USER") or "tonghong").strip()
    password = os.getenv("ERP_DB_PASSWORD") or os.getenv("MYSQL_PASSWORD") or "tonghong_secret"
    database = os.getenv("ERP_DB_NAME") or os.getenv("MYSQL_DATABASE") or "tonghong"
    if not user or user == "root":
        # Guard: jangan pernah jatuh ke root untuk baca katalog ERP.
        user = "tonghong"
        password = os.getenv("ERP_DB_PASSWORD") or os.getenv("MYSQL_PASSWORD") or "tonghong_secret"
    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "connection_timeout": int(os.getenv("MRP_DB_CONNECT_TIMEOUT", "10")),
        "autocommit": True,
    }
