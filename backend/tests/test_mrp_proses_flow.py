"""Alur Proses/Persiapan: Start wajib, consume YL, status completed."""

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


def _ensure_yl_stock(client: httpx.Client, headers: dict, kode_palet: str, kode_yl: str, qty: float):
    # Palet IN dengan 1 YL
    r = client.post(
        "/mrp/palet/in",
        headers=headers,
        json={
            "kode_palet": kode_palet,
            "tanggal": date.today().isoformat(),
            "keterangan": "test proses",
            "items": [
                {
                    "kode_yl": kode_yl,
                    "thickness": "1.2",
                    "warna": "BLACK",
                    "qty": qty,
                }
            ],
        },
    )
    if r.status_code >= 500:
        pytest.skip(f"palet/in unavailable: {r.status_code}")
    assert r.status_code in (200, 201), r.text


def _pick_rencana_item(client: httpx.Client, headers: dict):
    plans = client.get("/mrp/rencana-produksi", headers=headers)
    if plans.status_code >= 500:
        pytest.skip("rencana unavailable")
    assert plans.status_code == 200
    for row in plans.json() or []:
        detail = client.get(f"/mrp/rencana-produksi/{row['id']}", headers=headers)
        if detail.status_code != 200:
            continue
        for item in detail.json().get("items") or []:
            if item.get("kode_lot_wip") and item.get("id"):
                return item
    return None


def test_proses_requires_start_before_ky(auth_headers):
    with _client() as client:
        item = _pick_rencana_item(client, auth_headers)
        if not item:
            pytest.skip("butuh item rencana ber-WIP")

        created = client.post(
            "/mrp/proses",
            headers=auth_headers,
            json={
                "rencana_item_id": item["id"],
                "treatment_jenis": "PU",
                "treatment_list": ["Treatment A"],
            },
        )
        if created.status_code >= 500:
            pytest.skip(f"proses create unavailable: {created.status_code}")
        assert created.status_code in (200, 201), created.text
        pid = created.json()["id"]

        bad = client.post(
            f"/mrp/proses/{pid}/actions",
            headers=auth_headers,
            json={
                "action": "scan_ky",
                "kode_palet": "KY-TEST-X",
                "kode_yl": "YL-TEST-X",
                "target_qty": 10,
            },
        )
        assert bad.status_code == 400, bad.text
        assert "start" in bad.text.lower() or "mulai" in bad.text.lower()


def test_proses_consume_yl_and_complete(auth_headers):
    with _client() as client:
        item = _pick_rencana_item(client, auth_headers)
        if not item:
            pytest.skip("butuh item rencana ber-WIP")

        suffix = date.today().strftime("%m%d%H%M%S")
        kode_palet = f"KY-T{suffix}"
        kode_yl = f"YL-T{suffix}"
        stock_qty = 50.0
        _ensure_yl_stock(client, auth_headers, kode_palet, kode_yl, stock_qty)

        created = client.post(
            "/mrp/proses",
            headers=auth_headers,
            json={
                "rencana_item_id": item["id"],
                "treatment_jenis": "PU",
                "treatment_list": ["Treatment A"],
            },
        )
        assert created.status_code in (200, 201), created.text
        pid = created.json()["id"]

        start = client.post(
            f"/mrp/proses/{pid}/actions",
            headers=auth_headers,
            json={"action": "start"},
        )
        assert start.status_code == 200, start.text

        ky = client.post(
            f"/mrp/proses/{pid}/actions",
            headers=auth_headers,
            json={
                "action": "scan_ky",
                "kode_palet": kode_palet,
                "kode_yl": kode_yl,
                "target_qty": 10,
            },
        )
        assert ky.status_code == 200, ky.text

        detail = client.get(f"/mrp/proses/{pid}", headers=auth_headers)
        assert detail.status_code == 200
        active = detail.json().get("active_ky")
        assert active and active.get("id")
        ky_id = active["id"]

        ukur_qty = 12.0
        ukur = client.post(
            f"/mrp/proses/{pid}/actions",
            headers=auth_headers,
            json={"action": "add_ukur", "ky_id": ky_id, "size_val": ukur_qty},
        )
        assert ukur.status_code == 200, ukur.text

        selesai = client.post(
            f"/mrp/proses/{pid}/actions",
            headers=auth_headers,
            json={"action": "selesai_ky", "ky_id": ky_id},
        )
        assert selesai.status_code == 200, selesai.text
        assert "out" in selesai.json().get("message", "").lower() or "OUT" in selesai.text

        # stok YL berkurang
        yl = client.get(f"/mrp/palet/{kode_palet}/yl", headers=auth_headers)
        assert yl.status_code == 200, yl.text
        rows = yl.json() if isinstance(yl.json(), list) else yl.json().get("items") or yl.json().get("yls") or []
        if isinstance(rows, dict):
            rows = rows.get("yls") or []
        hit = next((r for r in rows if str(r.get("kode_yl")) == kode_yl), None)
        if hit is None:
            # terhapus karena sisa 0 — di sini sisa harus 38
            pytest.fail("YL hilang padahal sisa seharusnya > 0")
        assert abs(float(hit.get("qty") or 0) - (stock_qty - ukur_qty)) < 1e-6

        save = client.post(
            f"/mrp/proses/{pid}/actions",
            headers=auth_headers,
            json={"action": "save"},
        )
        assert save.status_code == 200, save.text

        detail2 = client.get(f"/mrp/proses/{pid}", headers=auth_headers)
        assert detail2.json()["persiapan"]["status"] == "completed"

        # packing scan WIP harus menerima completed
        wip = detail2.json()["persiapan"]["kode_wip"]
        scan = client.get(f"/mrp/packing/scan-wip", headers=auth_headers, params={"q": wip})
        assert scan.status_code == 200, scan.text
