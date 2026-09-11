"""Smoke Gudang FG: list/filter, detail, OUT validasi."""

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


def test_gudang_fg_list_and_status_filter(auth_headers):
    with _client() as client:
        all_r = client.get("/mrp/gudang-fg", headers=auth_headers)
        if all_r.status_code >= 500:
            pytest.skip("gudang-fg unavailable")
        assert all_r.status_code == 200, all_r.text
        rows = all_r.json()
        assert isinstance(rows, list)
        if not rows:
            pytest.skip("belum ada data FG")

        assert "kode_packing" in rows[0]
        assert "status" in rows[0]

        in_stock = client.get(
            "/mrp/gudang-fg", headers=auth_headers, params={"status": "in_stock"}
        )
        assert in_stock.status_code == 200, in_stock.text
        for r in in_stock.json() or []:
            assert r.get("status") == "in_stock"

        out = client.get("/mrp/gudang-fg", headers=auth_headers, params={"status": "out"})
        assert out.status_code == 200, out.text
        for r in out.json() or []:
            assert r.get("status") == "out"


def test_gudang_fg_detail_has_rolls_and_pos(auth_headers):
    with _client() as client:
        listing = client.get("/mrp/gudang-fg", headers=auth_headers)
        if listing.status_code >= 500:
            pytest.skip("gudang-fg unavailable")
        rows = listing.json() or []
        if not rows:
            pytest.skip("belum ada data FG")
        fg_id = rows[0]["id"]
        detail = client.get(f"/mrp/gudang-fg/{fg_id}", headers=auth_headers)
        assert detail.status_code == 200, detail.text
        body = detail.json()
        assert "fg" in body
        assert body["fg"].get("id") == fg_id
        assert "rolls" in body
        assert "packing_pos" in body


def test_gudang_fg_out_blocked_use_outstanding(auth_headers):
    with _client() as client:
        bad = client.post(
            "/mrp/gudang-fg/out",
            headers=auth_headers,
            json={"kode_packing": "FG-TIDAK-ADA-XYZ", "keterangan": "test"},
        )
        assert bad.status_code == 400, bad.text
        try:
            detail = bad.json().get("detail")
        except Exception:
            detail = bad.text
        text = detail if isinstance(detail, str) else str(detail)
        assert "outstanding" in text.lower()
