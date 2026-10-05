"""Resolve customer dari Tonghong ERP via HTTP API — SSOT."""

from __future__ import annotations

import os
from typing import Any, Optional


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _auto_create_default() -> bool:
    flag = (os.getenv("MRP_AUTO_CREATE_ERP_CUSTOMER") or "").strip().lower()
    if flag in {"1", "true", "yes", "on"}:
        return True
    if flag in {"0", "false", "no", "off"}:
        return False
    return (os.getenv("APP_ENV") or "dev").strip().lower() not in {"prod", "production"}


def resolve_customer(
    name_or_code: str | None,
    *,
    create_if_missing: bool | None = None,
) -> Optional[dict]:
    if create_if_missing is None:
        create_if_missing = _auto_create_default()
    raw = (name_or_code or "").strip()
    if not raw or raw == "-":
        return None

    from mrp_api import erp_client

    try:
        row = erp_client.resolve_customer(raw, create=bool(create_if_missing))
    except erp_client.ErpApiError:
        return None
    if not row:
        return None
    return {
        "id": int(row["id"]),
        "code": row.get("code"),
        "name": (row.get("name") or raw).strip(),
    }


def fetch_customer(customer_id: int) -> Optional[dict]:
    from mrp_api import erp_client

    try:
        row = erp_client.get_customer(int(customer_id))
    except erp_client.ErpApiError:
        return None
    if not row:
        return None
    return {"id": int(row["id"]), "code": row.get("code"), "name": row.get("name")}


def list_customers(limit: int = 500) -> list[dict]:
    from mrp_api import erp_client

    rows = erp_client.list_customers(limit=int(limit))
    return [
        {"id": int(r["id"]), "code": r.get("code"), "name": r.get("name")}
        for r in rows
        if (r.get("name") or "").strip()
    ]


def ensure_customer_id(nama: str | None, *, erp_customer_id: int | None = None) -> tuple[int, str]:
    if erp_customer_id:
        row = fetch_customer(int(erp_customer_id))
        if row:
            return int(row["id"]), (row.get("name") or nama or "-").strip() or "-"
    resolved = resolve_customer(nama)
    if not resolved:
        raise ValueError("Customer wajib (nama/kode) dan harus ada di Master Customer ERP")
    return int(resolved["id"]), resolved["name"]
