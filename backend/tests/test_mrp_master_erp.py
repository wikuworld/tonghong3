"""Smoke: MRP Master ERP memakai master_items Tonghong (bukan salinan lokal)."""

from __future__ import annotations

import os

import httpx
import pytest

BASE = os.environ.get("SMOKE_API_BASE", "http://127.0.0.1:8000/api/v1")


def _client():
    return httpx.Client(base_url=BASE, timeout=60.0)


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


def test_masters_erp_from_master_items(auth_headers):
    with _client() as client:
        r = client.get("/mrp/masters/erp", headers=auth_headers, params={"limit": 20})
        assert r.status_code == 200, r.text
        rows = r.json()
        assert isinstance(rows, list)
        assert rows, "master_items kosong?"
        row = rows[0]
        assert row.get("source") == "master_items"
        assert row.get("erp_master_item_id") or row.get("id")
        assert "material_name" in row
        assert "thickness" in row


def test_masters_erp_options_from_master_items(auth_headers):
    with _client() as client:
        r = client.get("/mrp/masters/erp/options", headers=auth_headers)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("source") == "master_items"
        assert isinstance(body.get("materials"), list)
        assert isinstance(body.get("thickness"), list)
        assert isinstance(body.get("colors"), list)
        assert body["materials"] or body["thickness"] or body["colors"]


def test_erp_fields_from_master_items(auth_headers):
    with _client() as client:
        opts = client.get("/mrp/masters/erp/options", headers=auth_headers)
        assert opts.status_code == 200
        materials = (opts.json() or {}).get("materials") or []
        if not materials:
            pytest.skip("tidak ada material")
        material = materials[0]
        r = client.get(
            "/mrp/erp/fields",
            headers=auth_headers,
            params={"material_name": material},
        )
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("source") == "master_items"
        assert isinstance(body.get("material_names"), list)
