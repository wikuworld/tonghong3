"""Smoke Palet/YL: IN validasi, OUT, YL qty cap."""

from __future__ import annotations

import os
import time

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


def test_palet_movements_filter(auth_headers):
    with _client() as client:
        all_r = client.get("/mrp/palet/movements", headers=auth_headers)
        if all_r.status_code >= 500:
            pytest.skip("palet unavailable")
        assert all_r.status_code == 200, all_r.text
        assert isinstance(all_r.json(), list)

        inn = client.get(
            "/mrp/palet/movements", headers=auth_headers, params={"direction": "IN"}
        )
        assert inn.status_code == 200, inn.text
        for r in inn.json() or []:
            assert r.get("direction") == "IN"


def test_palet_in_requires_yl_qty(auth_headers):
    with _client() as client:
        bad = client.post(
            "/mrp/palet/in",
            headers=auth_headers,
            json={"kode_palet": "KY-SMOKE-EMPTY", "items": []},
        )
        assert bad.status_code == 400, bad.text

        bad_qty = client.post(
            "/mrp/palet/in",
            headers=auth_headers,
            json={
                "kode_palet": "KY-SMOKE-EMPTY",
                "items": [{"kode_yl": "YL-X", "qty": 0}],
            },
        )
        assert bad_qty.status_code == 400, bad_qty.text


def test_palet_in_out_and_yl_cap(auth_headers):
    with _client() as client:
        suffix = str(int(time.time()))[-6:]
        kode_palet = f"KY-SMOKE-{suffix}"
        kode_yl = f"YL-SMOKE-{suffix}"

        created = client.post(
            "/mrp/palet/in",
            headers=auth_headers,
            json={
                "kode_palet": kode_palet,
                "keterangan": "smoke",
                "items": [
                    {
                        "kode_yl": kode_yl,
                        "thickness": "1.0",
                        "warna": "Black",
                        "qty": 10,
                    }
                ],
            },
        )
        assert created.status_code in (200, 201), created.text
        assert created.json().get("yl_count") == 1

        yl = client.get("/mrp/yl", headers=auth_headers, params={"kode_palet": kode_palet})
        assert yl.status_code == 200, yl.text
        rows = yl.json() or []
        assert any(r.get("kode_yl") == kode_yl for r in rows)

        over = client.post(
            "/mrp/yl/movement",
            headers=auth_headers,
            json={
                "kode_yl": kode_yl,
                "kode_palet": kode_palet,
                "direction": "OUT",
                "qty": 99,
            },
        )
        assert over.status_code == 400, over.text

        partial = client.post(
            "/mrp/yl/movement",
            headers=auth_headers,
            json={
                "kode_yl": kode_yl,
                "kode_palet": kode_palet,
                "direction": "OUT",
                "qty": 4,
            },
        )
        assert partial.status_code == 200, partial.text

        out = client.post(
            "/mrp/palet/out",
            headers=auth_headers,
            json={"kode_palet": kode_palet, "clear_yl": True, "keterangan": "smoke out"},
        )
        assert out.status_code == 200, out.text
        assert out.json().get("yl_cleared") >= 1

        unknown = client.post(
            "/mrp/palet/out",
            headers=auth_headers,
            json={"kode_palet": "KY-TIDAK-ADA-XYZ", "clear_yl": True},
        )
        assert unknown.status_code == 404, unknown.text
