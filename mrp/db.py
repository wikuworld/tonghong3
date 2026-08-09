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
    }


def get_db_connection(**overrides):
    cfg = db_config()
    cfg.update(overrides)
    return mysql.connector.connect(**cfg)


def root_db_config() -> dict:
    """Root (or privileged) connection for bootstrap — no default database required."""
    return {
        "host": os.getenv("MRP_DB_HOST", "mariadb"),
        "port": int(os.getenv("MRP_DB_PORT", "3306")),
        "user": os.getenv("MRP_DB_ROOT_USER", "root"),
        "password": os.getenv("MYSQL_ROOT_PASSWORD", os.getenv("MRP_DB_ROOT_PASSWORD", "root")),
    }
