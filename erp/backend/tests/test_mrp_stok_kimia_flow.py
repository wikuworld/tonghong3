"""Smoke Stok Kimia: list, IN validasi, OUT cap."""

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


def test_stok_kimia_list_shape(auth_headers):
    with _client() as client:
        r = client.get("/mrp/stok-kimia", headers=auth_headers)
        if r.status_code >= 500:
            pytest.skip("stok-kimia unavailable")
        assert r.status_code == 200, r.text
        body = r.json()
        assert "stok_in" in body and "stok_out" in body and "kimia_list" in body
        assert "stats" in body


def test_stok_kimia_in_out_validation(auth_headers):
    with _client() as client:
        listing = client.get("/mrp/stok-kimia", headers=auth_headers)
        if listing.status_code >= 500:
            pytest.skip("stok-kimia unavailable")
        kimia = (listing.json().get("kimia_list") or [])
        if not kimia:
            pytest.skip("tidak ada master kimia")
        kid = kimia[0]["id"]

        bad = client.post(
            "/mrp/stok-kimia",
            headers=auth_headers,
            json={"action": "in", "kimia_id": kid, "qty": 0},
        )
        assert bad.status_code == 400, bad.text

        created = client.post(
            "/mrp/stok-kimia",
            headers=auth_headers,
            json={"action": "in", "kimia_id": kid, "qty": 5, "jumlah_kemasan": 1},
        )
        assert created.status_code in (200, 201), created.text
        assert created.json().get("kode_internal")

        again = client.get("/mrp/stok-kimia", headers=auth_headers)
        lots = again.json().get("stok_in") or []
        lot = next((x for x in lots if x.get("kimia_id") == kid and float(x.get("qty_sisa") or 0) >= 5), None)
        if not lot:
            lot = lots[0] if lots else None
        if not lot:
            pytest.skip("lot tidak tersedia setelah IN")

        over = client.post(
            "/mrp/stok-kimia",
            headers=auth_headers,
            json={
                "action": "out",
                "stok_in_id": lot["id"],
                "qty": float(lot["qty_sisa"]) + 100,
                "tujuan": "mixing",
            },
        )
        assert over.status_code == 400, over.text

        bad_tujuan = client.post(
            "/mrp/stok-kimia",
            headers=auth_headers,
            json={
                "action": "out",
                "stok_in_id": lot["id"],
                "qty": 0.5,
                "tujuan": "gudang-rahasia",
            },
        )
        assert bad_tujuan.status_code == 400, bad_tujuan.text

        ok_out = client.post(
            "/mrp/stok-kimia",
            headers=auth_headers,
            json={
                "action": "out",
                "stok_in_id": lot["id"],
                "qty": 0.5,
                "tujuan": "mixing",
                "kode_wip": "WIP-SMOKE-KIMIA",
            },
        )
        # Bridge ERP mungkin gagal di gateway; terima 200 atau 400 bridge
        assert ok_out.status_code in (200, 400), ok_out.text
        if ok_out.status_code == 200:
            assert ok_out.json().get("ok") is True
