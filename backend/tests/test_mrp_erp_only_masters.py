"""Kontrak ERP-only: katalog MRP dari raw_materials; mirror tables hilang; OUT butuh erp id."""

from __future__ import annotations

import os

import httpx
import pytest

BASE = os.environ.get("SMOKE_API_BASE", "http://127.0.0.1:8000/api/v1")


def _client():
    return httpx.Client(base_url=BASE, timeout=90.0)


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


def test_masters_kimia_from_erp(auth_headers):
    with _client() as client:
        r = client.get("/mrp/masters/kimia", headers=auth_headers)
        assert r.status_code == 200, r.text
        rows = r.json()
        assert isinstance(rows, list)
        assert rows, "raw_materials kimia kosong?"
        assert rows[0].get("source") == "raw_materials"
        assert rows[0].get("erp_material_id") or rows[0].get("id")


def test_masters_create_forbidden(auth_headers):
    with _client() as client:
        r = client.post(
            "/mrp/masters/kimia",
            headers=auth_headers,
            json={"kode_kimia": "X-TEST", "nama_kimia": "Should Fail"},
        )
        assert r.status_code == 403, r.text


def test_stok_kimia_list_without_mirror(auth_headers):
    with _client() as client:
        r = client.get("/mrp/stok-kimia", headers=auth_headers)
        assert r.status_code == 200, r.text
        body = r.json()
        assert "stok_in" in body
        assert "kimia_list" in body
        assert isinstance(body["kimia_list"], list)


def test_customers_erp_still_intact(auth_headers):
    with _client() as client:
        r = client.get("/customers", headers=auth_headers)
        assert r.status_code == 200, r.text
        assert len(r.json()) >= 1


def test_inventory_materials_intact(auth_headers):
    with _client() as client:
        r = client.get("/inventory/materials", headers=auth_headers)
        assert r.status_code == 200, r.text
        assert len(r.json()) > 10


def test_map_endpoints_gone(auth_headers):
    with _client() as client:
        r = client.post("/mrp/masters/erp/map-master-item", headers=auth_headers, json={})
        assert r.status_code == 410, r.text
        r2 = client.post(
            "/mrp/masters/raw-materials/backfill-erp",
            headers=auth_headers,
            json={"dry_run": True},
        )
        assert r2.status_code == 410, r2.text


def test_stok_kimia_out_rejects_missing_lot(auth_headers):
    with _client() as client:
        r = client.post(
            "/mrp/stok-kimia",
            headers=auth_headers,
            json={"action": "out", "stok_in_id": 99999999, "qty": 1},
        )
        assert r.status_code in (400, 404), r.text


def test_mrp_health_erp_only_metrics(auth_headers):
    with _client() as client:
        r = client.get("/mrp/health", headers=auth_headers)
        assert r.status_code == 200, r.text
        body = r.json()
        assert body.get("catalog_mode") == "erp-only"
        assert "metrics" in body
        assert "out_rejected_missing_erp_id" in body["metrics"]


def test_bridge_reject_unknown_material(auth_headers):
    with _client() as client:
        r = client.post(
            "/mrp/bridge/stock-issue",
            headers=auth_headers,
            json={
                "erp_material_id": 999999999,
                "material_type": "kimia",
                "qty": 0.01,
                "mrp_ref": "test-unmatched",
            },
        )
        assert r.status_code == 400, r.text
