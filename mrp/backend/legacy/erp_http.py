"""Legacy helpers: ERP access selalu via HTTP API."""

from __future__ import annotations

from typing import Any


def erp_get(path: str, *, params: dict[str, Any] | None = None) -> Any:
    from mrp_api import erp_client

    return erp_client.get(path, params=params)


def erp_post(path: str, *, json: Any = None, params: dict[str, Any] | None = None) -> Any:
    from mrp_api import erp_client

    return erp_client.post(path, json=json, params=params)


def erp_put(path: str, *, json: Any = None, params: dict[str, Any] | None = None) -> Any:
    from mrp_api import erp_client

    return erp_client.put(path, json=json, params=params)
