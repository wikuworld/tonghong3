"""Shared DB config for MRP service — reads project .env / process env."""
from __future__ import annotations

import os
from pathlib import Path

import mysql.connector

# legacy/db.py → project_uat/.env (bukan mrp/backend/.env)
_ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"


def _load_root_env() -> None:
    """Load /tonghong/.env into os.environ if not already set (jalan tanpa Docker)."""
    if not _ROOT_ENV.is_file():
        return
    for raw in _ROOT_ENV.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = val


_load_root_env()

_DEFAULT_HOST = "202.10.48.75"
_DEFAULT_USER = "root"
_DEFAULT_PASSWORD = "Developer2026!"


def db_config() -> dict:
    return {
        "host": os.getenv("MRP_DB_HOST") or os.getenv("MYSQL_HOST", _DEFAULT_HOST),
        "port": int(os.getenv("MRP_DB_PORT") or os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MRP_DB_USER") or os.getenv("MYSQL_USER", _DEFAULT_USER),
        "password": os.getenv("MRP_DB_PASSWORD")
        or os.getenv("MYSQL_PASSWORD", _DEFAULT_PASSWORD),
        "database": os.getenv("MRP_DB_NAME", "tonghong_mrp"),
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci",
    }


def get_db_connection(**overrides):
    cfg = db_config()
    cfg.update(overrides)
    return mysql.connector.connect(**cfg)


def root_db_config() -> dict:
    """Root (or privileged) connection for bootstrap — no default database required."""
    return {
        "host": os.getenv("MRP_DB_HOST") or os.getenv("MYSQL_HOST", _DEFAULT_HOST),
        "port": int(os.getenv("MRP_DB_PORT") or os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MRP_DB_ROOT_USER") or os.getenv("MYSQL_USER", _DEFAULT_USER),
        "password": os.getenv("MYSQL_ROOT_PASSWORD")
        or os.getenv("MRP_DB_ROOT_PASSWORD")
        or os.getenv("MYSQL_PASSWORD", _DEFAULT_PASSWORD),
    }
