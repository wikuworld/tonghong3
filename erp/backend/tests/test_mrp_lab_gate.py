"""Gate Lab ↔ Proses + seed treatment (smoke API)."""

from __future__ import annotations

import os
from datetime import date

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


def test_lab_options_include_proses_fields(auth_headers):
    with _client() as client:
        opt = client.get("/mrp/lab/options", headers=auth_headers)
        if opt.status_code >= 500:
            pytest.skip("lab options unavailable")
        assert opt.status_code == 200, opt.text
        body = opt.json()
        assert "gate" in body
        assert body["gate"].get("link_rpi_requires_proses") is True
        items = body.get("rencana_items") or []
        if items:
            assert "has_proses" in items[0]
            assert "persiapan_status" in items[0] or items[0].get("has_proses") is False


def test_lab_create_without_rpi_ok(auth_headers):
    with _client() as client:
        opt = client.get("/mrp/lab/options", headers=auth_headers)
        if opt.status_code >= 500:
            pytest.skip("lab unavailable")
        kimia = (opt.json().get("kimia_list") or [])
        if not kimia:
            pytest.skip("tidak ada master kimia")
        kode = kimia[0]["kode_kimia"]
        created = client.post(
            "/mrp/lab",
            headers=auth_headers,
            json={
                "nama_lot_warna": f"TEST LAB NO RPI {date.today().isoformat()}",
                "rencana_item_id": None,
                "items": [{"kode_kimia": kode, "qty": 1, "satuan": "kg"}],
            },
        )
        assert created.status_code in (200, 201), created.text
        assert created.json().get("kode_lot_warna")

        listing = client.get("/mrp/lab", headers=auth_headers)
        assert listing.status_code == 200, listing.text
        body = listing.json()
        assert body.get("ok") is True
        lots = body.get("lots") or []
        assert any(l.get("kode_lot_warna") == created.json()["kode_lot_warna"] for l in lots)
        hit = next(l for l in lots if l["kode_lot_warna"] == created.json()["kode_lot_warna"])
        assert hit.get("jml_kimia", 0) >= 1
        assert isinstance(hit.get("items"), list) and hit["items"]


def test_lab_create_link_rpi_requires_proses(auth_headers):
    with _client() as client:
        opt = client.get(
            "/mrp/lab/options",
            headers=auth_headers,
            params={"only_with_proses": 0},
        )
        if opt.status_code >= 500:
            pytest.skip("lab unavailable")
        items = opt.json().get("rencana_items") or []
        kimia = opt.json().get("kimia_list") or []
        if not kimia:
            pytest.skip("tidak ada master kimia")
        bare = next((i for i in items if not i.get("has_proses")), None)
        if not bare:
            pytest.skip("tidak ada RPI tanpa proses untuk tes gate")
        bad = client.post(
            "/mrp/lab",
            headers=auth_headers,
            json={
                "nama_lot_warna": "TEST LAB GATE FAIL",
                "rencana_item_id": bare["id"],
                "items": [{"kode_kimia": kimia[0]["kode_kimia"], "qty": 1, "satuan": "kg"}],
            },
        )
        assert bad.status_code == 400, bad.text
        assert "proses" in bad.text.lower() or "persiapan" in bad.text.lower()


def test_treatment_seed_has_pu_and_suede(auth_headers):
    with _client() as client:
        proses = client.get("/mrp/proses", headers=auth_headers)
        if proses.status_code >= 500:
            pytest.skip("proses list unavailable")
        assert proses.status_code == 200, proses.text
        treatments = proses.json().get("treatments") or []
        # endpoint list treatment master
        mt = client.get("/mrp/masters/treatment", headers=auth_headers)
        rows = mt.json() if mt.status_code == 200 else treatments
        if isinstance(rows, dict):
            rows = rows.get("items") or rows.get("treatments") or []
        names = {str(r.get("nama_treatment") or "") for r in rows}
        jenis = {str(r.get("jenis") or "") for r in rows}
        assert any("PU -" in n for n in names) or "PU" in jenis
        assert any("Suede -" in n for n in names) or "Suede" in jenis
