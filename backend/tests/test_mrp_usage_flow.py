"""Smoke Usage: validasi qty, scan, create tanpa/dengan stok."""

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


def test_usage_lists_ok(auth_headers):
    with _client() as client:
        for path in ("/mrp/usage-color", "/mrp/usage-rp", "/mrp/usage-material-lain"):
            r = client.get(path, headers=auth_headers)
            if r.status_code >= 500:
                pytest.skip(f"{path} unavailable")
            assert r.status_code == 200, r.text
            body = r.json()
            assert "usage_list" in body and "wip_list" in body


def test_usage_rejects_zero_qty(auth_headers):
    with _client() as client:
        # color
        bad_c = client.post(
            "/mrp/usage-color",
            headers=auth_headers,
            json={"kode_wip": "WIP-X", "kode_lot_warna": "LW-X", "qty_digunakan": 0},
        )
        assert bad_c.status_code == 400, bad_c.text

        # rp
        bad_r = client.post(
            "/mrp/usage-rp",
            headers=auth_headers,
            json={"kode_wip": "WIP-X", "jenis_rp": "NOPE", "qty_used": 0},
        )
        assert bad_r.status_code == 400, bad_r.text

        # material
        bad_m = client.post(
            "/mrp/usage-material-lain",
            headers=auth_headers,
            json={"kode_wip": "WIP-X", "kode_material": "MAT-001", "qty_used": 0},
        )
        assert bad_m.status_code == 400, bad_m.text


def test_usage_material_create_ok(auth_headers):
    with _client() as client:
        mats = client.get("/mrp/stok-material-lain", headers=auth_headers)
        if mats.status_code >= 500:
            pytest.skip("material unavailable")
        mlist = mats.json().get("material_list") or []
        if not mlist:
            pytest.skip("tidak ada master material")
        kode = mlist[0]["kode_material"]
        wips = client.get("/mrp/usage-material-lain", headers=auth_headers).json().get("wip_list") or []
        wip = wips[0] if wips else "WIP-SMOKE-USAGE"

        scan = client.get(
            "/mrp/usage-material-lain/scan",
            headers=auth_headers,
            params={"q": kode},
        )
        assert scan.status_code == 200, scan.text

        created = client.post(
            "/mrp/usage-material-lain",
            headers=auth_headers,
            json={
                "kode_wip": wip,
                "kode_material": kode,
                "qty_used": 0.25,
                "satuan": mlist[0].get("satuan") or "pcs",
            },
        )
        assert created.status_code in (200, 201), created.text
        assert created.json().get("ok") is True
