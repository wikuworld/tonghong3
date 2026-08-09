"""Smoke: konsolidasi master ERP↔MRP (customer, raw materials, chemical drop)."""

from __future__ import annotations

import os

import httpx
import pytest

BASE = os.environ.get("SMOKE_API_BASE", "http://127.0.0.1:8000/api/v1")


def _client():
    return httpx.Client(base_url=BASE, timeout=120.0)


def _login(client: httpx.Client) -> str | None:
    for user, password in (
        ("demo_production", "TonghongDemo2026"),
        ("admin", "TonghongDemo2026"),
        ("admin", "admin123"),
    ):
        r = client.post("/auth/login", json={"username": user, "password": password})
        if r.status_code == 200 and r.json().get("access_token"):
            return r.json()["access_token"]
    return None


@pytest.fixture(scope="module")
def auth_headers():
    try:
        with _client() as client:
            token = _login(client)
    except httpx.HTTPError:
        pytest.skip("API tidak tersedia")
    if not token:
        pytest.skip("Login demo gagal")
    return {"Authorization": f"Bearer {token}"}


def test_customers_erp_list(auth_headers):
    with _client() as client:
        r = client.get("/customers", headers=auth_headers)
        assert r.status_code == 200, r.text
        rows = r.json()
        assert isinstance(rows, list)
        assert len(rows) >= 1


def test_raw_materials_backfill_erp_gone(auth_headers):
    """Endpoint backfill mirror→ERP dihapus (ERP-only)."""
    with _client() as client:
        r = client.post(
            "/mrp/masters/raw-materials/backfill-erp",
            headers=auth_headers,
            json={"dry_run": False},
        )
        assert r.status_code == 410, r.text


def test_masters_kimia_from_erp_raw_materials(auth_headers):
    with _client() as client:
        r = client.get("/mrp/masters/kimia", headers=auth_headers)
        assert r.status_code == 200, r.text
        rows = r.json()
        assert isinstance(rows, list)
        assert len(rows) >= 1
        assert rows[0].get("source") == "raw_materials"


def test_inventory_materials_after_backfill(auth_headers):
    with _client() as client:
        r = client.get("/inventory/materials", headers=auth_headers)
        assert r.status_code == 200, r.text
        rows = r.json()
        assert isinstance(rows, list)
        assert len(rows) > 3
