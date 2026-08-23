"""Smoke: GET /masters/color-links untuk 00A / BLACK (00A)."""

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


def test_color_links_00a(auth_headers):
    with _client() as client:
        r = client.get("/masters/color-links", params={"color_code": "00A"}, headers=auth_headers)
        if r.status_code == 404:
            pytest.skip("endpoint belum di-deploy")
        assert r.status_code == 200
        body = r.json()
        assert body["color_code"] == "00A"
        assert body["in_csi"] is True
        assert any(c["buyer_code"] == "NIKE" for c in body["csi"])
        assert body["swatch_count"] > 0


def test_color_links_from_item_text(auth_headers):
    with _client() as client:
        r = client.get("/masters/color-links", params={"color": "BLACK (00A)"}, headers=auth_headers)
        if r.status_code == 404:
            pytest.skip("endpoint belum di-deploy")
        assert r.status_code == 200
        body = r.json()
        assert body["color_code"] == "00A"
        assert body["item_label"] == "BLACK (00A)"
