"""Smoke Checkpoint QC: list/filter, scan WIP, validasi create."""

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


def _any_wip(client, headers) -> str | None:
    proses = client.get("/mrp/proses", headers=headers)
    if proses.status_code == 200:
        for r in (proses.json() or {}).get("persiapan_list") or []:
            if r.get("kode_wip"):
                return r["kode_wip"]
    packing = client.get("/mrp/packing", headers=headers, params={"all": "1"})
    if packing.status_code == 200:
        for r in packing.json() or []:
            if r.get("kode_wip"):
                return r["kode_wip"]
    return None


def test_checkpoint_list_and_result_filter(auth_headers):
    with _client() as client:
        all_r = client.get("/mrp/checkpoint", headers=auth_headers)
        if all_r.status_code >= 500:
            pytest.skip("checkpoint unavailable")
        assert all_r.status_code == 200, all_r.text
        assert isinstance(all_r.json(), list)

        ok = client.get("/mrp/checkpoint", headers=auth_headers, params={"result": "OK"})
        assert ok.status_code == 200, ok.text
        for r in ok.json() or []:
            assert str(r.get("result") or "").upper() == "OK"

        wip = _any_wip(client, auth_headers)
        if wip:
            by_wip = client.get(
                "/mrp/checkpoint", headers=auth_headers, params={"kode_wip": wip}
            )
            assert by_wip.status_code == 200, by_wip.text
            for r in by_wip.json() or []:
                assert r.get("kode_wip") == wip
                assert "kode_rpi" in r
                assert "nama_rencana" in r
                assert "material_name" in r
                assert "emboss" in r
                assert "warna" in r


def test_checkpoint_scan_and_create(auth_headers):
    with _client() as client:
        wip = _any_wip(client, auth_headers)
        if not wip:
            pytest.skip("tidak ada WIP shopfloor")

        bad_scan = client.get(
            "/mrp/checkpoint/scan-wip",
            headers=auth_headers,
            params={"q": "WIP-TIDAK-ADA-XYZ"},
        )
        assert bad_scan.status_code == 404, bad_scan.text

        scan = client.get(
            "/mrp/checkpoint/scan-wip", headers=auth_headers, params={"q": wip}
        )
        assert scan.status_code == 200, scan.text
        body = scan.json()
        assert body.get("kode_wip") == wip

        bad_result = client.post(
            "/mrp/checkpoint",
            headers=auth_headers,
            json={"kode_wip": wip, "result": "MAYBE"},
        )
        assert bad_result.status_code == 400, bad_result.text

        bad_thick = client.post(
            "/mrp/checkpoint",
            headers=auth_headers,
            json={"kode_wip": wip, "result": "OK", "thickness_actual": 0},
        )
        assert bad_thick.status_code == 400, bad_thick.text

        created = client.post(
            "/mrp/checkpoint",
            headers=auth_headers,
            json={
                "kode_wip": wip,
                "result": "OK",
                "thickness_actual": 1.1,
                "softness_actual": "soft",
                "remark": "smoke checkpoint",
                "kode_packing": body.get("kode_packing"),
                "erp_production_detail_id": body.get("erp_production_detail_id"),
            },
        )
        assert created.status_code in (200, 201), created.text
        data = created.json()
        assert data.get("ok") is True
        assert data.get("kode_wip") == wip
        assert data.get("result") == "OK"
        assert str(data.get("treatment") or "").upper() == "QC"
        assert str(data.get("checkpoint_status") or "").upper() == "QC"


def _any_treatment(client, headers) -> str | None:
    mt = client.get("/mrp/masters/treatment", headers=headers)
    if mt.status_code != 200:
        return None
    rows = mt.json() or []
    if isinstance(rows, dict):
        rows = rows.get("items") or rows.get("treatments") or []
    for r in rows:
        name = str(r.get("nama_treatment") or "").strip()
        if name and name.upper() != "QC":
            return name
    return None


def test_checkpoint_treatment_updates_status(auth_headers):
    with _client() as client:
        wip = _any_wip(client, auth_headers)
        if not wip:
            pytest.skip("tidak ada WIP shopfloor")
        treatment = _any_treatment(client, auth_headers)
        if not treatment:
            pytest.skip("tidak ada master treatment")

        bad = client.post(
            "/mrp/checkpoint",
            headers=auth_headers,
            json={"kode_wip": wip, "treatment": "TREATMENT-TIDAK-ADA-XYZ"},
        )
        assert bad.status_code == 400, bad.text

        created = client.post(
            "/mrp/checkpoint",
            headers=auth_headers,
            json={"kode_wip": wip, "treatment": treatment, "remark": "smoke treatment"},
        )
        assert created.status_code in (200, 201), created.text
        data = created.json()
        assert data.get("ok") is True
        assert data.get("treatment") == treatment
        assert data.get("checkpoint_status") == treatment
        assert data.get("result") in (None, "")

        scan = client.get(
            "/mrp/checkpoint/scan-wip", headers=auth_headers, params={"q": wip}
        )
        assert scan.status_code == 200, scan.text
        assert scan.json().get("checkpoint_status") == treatment


def test_checkpoint_rejects_unknown_wip(auth_headers):
    with _client() as client:
        bad = client.post(
            "/mrp/checkpoint",
            headers=auth_headers,
            json={"kode_wip": "WIP-TIDAK-ADA-XYZ", "result": "OK"},
        )
        assert bad.status_code == 404, bad.text
        detail = bad.json().get("detail")
        assert isinstance(detail, str)
        assert "tidak ditemukan" in detail.lower()
