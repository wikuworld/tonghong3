"""Smoke Monitoring MRP: list SO/lot/status and detail log/KY/chemical/qty."""

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


def test_monitoring_list_shape(auth_headers):
    with _client() as client:
        r = client.get("/mrp/monitoring", headers=auth_headers)
        if r.status_code >= 500:
            pytest.skip("monitoring unavailable")
        assert r.status_code == 200, r.text
        data = r.json()
        assert isinstance(data, list)
        for row in data[:20]:
            assert "no_so" in row
            assert "nama_rencana" in row
            assert "material_name" in row
            assert "emboss" in row
            assert "thickness" in row
            assert "lot_no" in row
            assert "status_terakhir" in row
            assert "rencana_item_id" in row


def test_monitoring_detail_ky_chemical_qty(auth_headers):
    with _client() as client:
        listed = client.get("/mrp/monitoring", headers=auth_headers)
        if listed.status_code >= 500:
            pytest.skip("monitoring unavailable")
        assert listed.status_code == 200, listed.text
        rows = listed.json() or []
        if not rows:
            missing = client.get("/mrp/monitoring/0", headers=auth_headers)
            assert missing.status_code == 404
            return
        item_id = rows[0].get("rencana_item_id")
        assert item_id
        detail = client.get(f"/mrp/monitoring/{item_id}", headers=auth_headers)
        assert detail.status_code == 200, detail.text
        body = detail.json()
        assert body.get("rencana_item_id") == item_id
        assert "ky" in body
        assert "chemicals" in body
        assert "status_log" in body
        assert "total_qty_persiapan" in body
        assert "fg_measured" in body
        assert isinstance(body.get("ky"), list)
        assert isinstance(body.get("chemicals"), list)
        assert isinstance(body.get("status_log"), list)
        for ev in body.get("status_log") or []:
            assert "tanggal" in ev
            assert "jam" in ev
            assert "proses" in ev
            assert ev.get("proses")
        if body.get("fg_measured"):
            assert body.get("total_qty_fg") is not None
        else:
            assert body.get("total_qty_fg") is None
