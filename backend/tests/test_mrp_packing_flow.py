"""Smoke Packing: scan WIP, validasi roll, finish butuh roll."""

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


def _ready_wip(client, headers):
    proses = client.get("/mrp/proses", headers=headers)
    if proses.status_code >= 500:
        return None
    rows = (proses.json() or {}).get("persiapan_list") or []
    for r in rows:
        if str(r.get("status")) in ("saved", "completed") and r.get("kode_wip"):
            return r["kode_wip"]
    return None


def test_packing_scan_returns_prep_and_po_id(auth_headers):
    with _client() as client:
        wip = _ready_wip(client, auth_headers)
        if not wip:
            pytest.skip("tidak ada WIP ready packing")
        scan = client.get("/mrp/packing/scan-wip", headers=auth_headers, params={"q": wip})
        assert scan.status_code == 200, scan.text
        body = scan.json()
        assert body.get("kode_wip") == wip
        assert "prep" in body
        assert body["prep"].get("status") in ("saved", "completed")
        pos = body.get("po_list") or []
        if pos:
            assert "po_id" in pos[0] or pos[0].get("no_po")


def test_packing_rejects_empty_roll_and_finish_without_roll(auth_headers):
    with _client() as client:
        wip = _ready_wip(client, auth_headers)
        if not wip:
            pytest.skip("tidak ada WIP ready packing")
        scan = client.get("/mrp/packing/scan-wip", headers=auth_headers, params={"q": wip})
        assert scan.status_code == 200, scan.text
        pos = scan.json().get("po_list") or []
        if not pos:
            pytest.skip("WIP tanpa PO")
        po = pos[0]
        started = client.post(
            "/mrp/packing",
            headers=auth_headers,
            json={
                "kode_wip": wip,
                "no_po": po["no_po"],
                "no_so": po.get("no_so") or "",
                "customer": po.get("customer") or "",
                "qty_sq": po.get("qty_sq") or 0,
                "po_id": po.get("po_id"),
            },
        )
        assert started.status_code in (200, 201), started.text
        pid = started.json()["id"]

        bad_roll = client.post(
            f"/mrp/packing/{pid}/actions",
            headers=auth_headers,
            json={"action": "add_roll", "lembar": 1, "ukuran": 0},
        )
        assert bad_roll.status_code == 400, bad_roll.text

        bad_finish = client.post(
            f"/mrp/packing/{pid}/actions",
            headers=auth_headers,
            json={"action": "finish"},
        )
        # Jika packing sudah punya roll dari reuse in_progress, finish bisa lolos —
        # pastikan minimal error mengandung roll ATAU status already finished path.
        detail = client.get(f"/mrp/packing/{pid}", headers=auth_headers)
        rolls = (detail.json() or {}).get("rolls") or []
        if not rolls:
            assert bad_finish.status_code == 400, bad_finish.text
            assert "roll" in bad_finish.text.lower()
        else:
            assert bad_finish.status_code == 200, bad_finish.text
