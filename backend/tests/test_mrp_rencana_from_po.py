"""Integrasi create rencana dari po_lines (lewati jika stack MRP tidak hidup)."""

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


def test_create_rencana_from_po_lines(auth_headers):
    with _client() as client:
        sync = client.post("/mrp/sync/po", headers=auth_headers, json={})
        if sync.status_code >= 500:
            pytest.skip(f"MRP sync unavailable: {sync.status_code}")
        assert sync.status_code == 200, sync.text
        assert sync.json().get("ok") is True

        masters = client.get("/mrp/masters/po", headers=auth_headers)
        assert masters.status_code == 200, masters.text
        rows = masters.json()
        candidates = []
        for r in rows:
            if str(r.get("status") or "") not in ("outstanding", "partial"):
                continue
            outstanding = float(r.get("qty_order") or 0) - float(r.get("qty_processed") or 0)
            if outstanding <= 0:
                continue
            if not (r.get("item_name") and r.get("tebal") and r.get("warna")):
                continue
            candidates.append((r, outstanding))
        assert candidates, "tidak ada PO allocatable untuk tes"

        sample, outstanding = candidates[0]
        qty = min(1.0, outstanding)
        processed_before = float(sample.get("qty_processed") or 0)

        created = client.post(
            "/mrp/rencana-produksi",
            headers=auth_headers,
            json={
                "nama_rencana": f"TEST FROM PO {date.today().isoformat()}",
                "tanggal_rencana": date.today().isoformat(),
                "po_lines": [{"po_id": sample["id"], "qty": qty}],
            },
        )
        assert created.status_code == 201, created.text
        body = created.json()
        assert body.get("ok") is True
        rid = body["id"]

        detail = client.get(f"/mrp/rencana-produksi/{rid}", headers=auth_headers)
        assert detail.status_code == 200, detail.text
        items = detail.json().get("items") or []
        assert len(items) == 1
        item = items[0]
        assert item.get("material_name") == sample.get("item_name")
        assert item.get("thickness") == sample.get("tebal")
        assert item.get("color") == sample.get("warna")
        assert int(item.get("jml_po") or 0) >= 1

        po_dlg = client.get(
            f"/mrp/rencana-produksi/item/{item['id']}/list-po",
            headers=auth_headers,
        )
        assert po_dlg.status_code == 200, po_dlg.text
        selected = po_dlg.json().get("selected_po") or []
        assert selected, "PO harus sudah teralokasi saat create"
        assert any(int(s.get("po_id") or 0) == int(sample["id"]) for s in selected)

        masters2 = client.get("/mrp/masters/po", headers=auth_headers)
        row2 = next(r for r in masters2.json() if r["id"] == sample["id"])
        assert float(row2.get("qty_processed") or 0) >= processed_before + qty - 1e-6


def test_create_rencana_rejects_qty_over_outstanding(auth_headers):
    with _client() as client:
        sync = client.post("/mrp/sync/po", headers=auth_headers, json={})
        if sync.status_code >= 500:
            pytest.skip(f"MRP sync unavailable: {sync.status_code}")
        masters = client.get("/mrp/masters/po", headers=auth_headers)
        rows = masters.json()
        sample = None
        outstanding = 0.0
        for r in rows:
            if str(r.get("status") or "") not in ("outstanding", "partial"):
                continue
            outstanding = float(r.get("qty_order") or 0) - float(r.get("qty_processed") or 0)
            if outstanding > 0 and r.get("item_name") and r.get("tebal") and r.get("warna"):
                sample = r
                break
        assert sample is not None

        bad = client.post(
            "/mrp/rencana-produksi",
            headers=auth_headers,
            json={
                "nama_rencana": "TEST OVER QTY",
                "tanggal_rencana": date.today().isoformat(),
                "po_lines": [{"po_id": sample["id"], "qty": outstanding + 1000}],
            },
        )
        assert bad.status_code == 400, bad.text
        detail = bad.json().get("detail") or bad.text
        assert "melebihi" in str(detail).lower() or "sisa" in str(detail).lower()


def test_replace_po_allocation_does_not_double_qty_processed(auth_headers):
    """Re-save alokasi PO harus rollback dulu — qty_processed tidak dobel."""
    with _client() as client:
        sync = client.post("/mrp/sync/po", headers=auth_headers, json={})
        if sync.status_code >= 500:
            pytest.skip(f"MRP sync unavailable: {sync.status_code}")

        masters = client.get("/mrp/masters/po", headers=auth_headers)
        sample = None
        outstanding = 0.0
        for r in masters.json():
            if str(r.get("status") or "") not in ("outstanding", "partial"):
                continue
            outstanding = float(r.get("qty_order") or 0) - float(r.get("qty_processed") or 0)
            if outstanding >= 2 and r.get("item_name") and r.get("tebal") and r.get("warna"):
                sample = r
                break
        if not sample:
            pytest.skip("butuh PO outstanding >= 2 untuk tes replace")

        processed_before = float(sample.get("qty_processed") or 0)
        qty = 1.0
        created = client.post(
            "/mrp/rencana-produksi",
            headers=auth_headers,
            json={
                "nama_rencana": f"TEST REPLACE PO {date.today().isoformat()}",
                "tanggal_rencana": date.today().isoformat(),
                "po_lines": [{"po_id": sample["id"], "qty": qty}],
            },
        )
        assert created.status_code == 201, created.text
        rid = created.json()["id"]
        detail = client.get(f"/mrp/rencana-produksi/{rid}", headers=auth_headers)
        item_id = detail.json()["items"][0]["id"]

        after_create = client.get("/mrp/masters/po", headers=auth_headers)
        row_mid = next(r for r in after_create.json() if r["id"] == sample["id"])
        assert abs(float(row_mid.get("qty_processed") or 0) - (processed_before + qty)) < 1e-6

        # Simpan ulang qty yang sama — tidak boleh jadi +2
        again = client.post(
            f"/mrp/rencana-produksi/item/{item_id}/list-po",
            headers=auth_headers,
            json={"pos": [{"po_id": sample["id"], "qty": qty}]},
        )
        assert again.status_code == 200, again.text

        after_replace = client.get("/mrp/masters/po", headers=auth_headers)
        row_end = next(r for r in after_replace.json() if r["id"] == sample["id"])
        assert abs(float(row_end.get("qty_processed") or 0) - (processed_before + qty)) < 1e-6

        # Ubah qty 1 → 2
        change = client.post(
            f"/mrp/rencana-produksi/item/{item_id}/list-po",
            headers=auth_headers,
            json={"pos": [{"po_id": sample["id"], "qty": 2.0}]},
        )
        assert change.status_code == 200, change.text
        after_change = client.get("/mrp/masters/po", headers=auth_headers)
        row_chg = next(r for r in after_change.json() if r["id"] == sample["id"])
        assert abs(float(row_chg.get("qty_processed") or 0) - (processed_before + 2.0)) < 1e-6


def test_recompute_processed_matches_sum_allocations(auth_headers):
    with _client() as client:
        sync = client.post("/mrp/sync/po", headers=auth_headers, json={})
        if sync.status_code >= 500:
            pytest.skip(f"MRP sync unavailable: {sync.status_code}")

        recompute = client.post("/mrp/masters/po/recompute-processed", headers=auth_headers)
        if recompute.status_code == 404:
            pytest.skip("endpoint recompute belum tersedia di upstream")
        assert recompute.status_code == 200, recompute.text
        body = recompute.json()
        assert body.get("ok") is True
        assert int(body.get("recomputed") or 0) >= 0

        masters = client.get("/mrp/masters/po", headers=auth_headers)
        assert masters.status_code == 200
        # Ambil satu rencana yang punya alokasi, cek qty_processed selaras
        plans = client.get("/mrp/rencana-produksi", headers=auth_headers)
        assert plans.status_code == 200
        plan_rows = plans.json() or []
        if not plan_rows:
            pytest.skip("tidak ada rencana untuk verifikasi recompute")
        rid = plan_rows[0]["id"]
        detail = client.get(f"/mrp/rencana-produksi/{rid}", headers=auth_headers)
        assert detail.status_code == 200
        by_po: dict[int, float] = {}
        for item in detail.json().get("items") or []:
            for al in item.get("po_allocations") or []:
                pid = int(al["po_id"])
                by_po[pid] = by_po.get(pid, 0.0) + float(al.get("qty_proses") or 0)
        if not by_po:
            pytest.skip("rencana tanpa alokasi")
        masters_map = {int(r["id"]): r for r in masters.json()}
        for pid, qty_sum in by_po.items():
            row = masters_map.get(pid)
            assert row is not None, f"master PO {pid} hilang"
            # Σ alokasi di rencana ini <= qty_processed global (boleh lebih besar dari rencana lain)
            assert float(row.get("qty_processed") or 0) + 1e-6 >= qty_sum


def test_list_po_matches_emboss_dash_vs_null(auth_headers):
    """Item emboss '-' harus menemukan master emboss NULL/''/'-'."""
    with _client() as client:
        sync = client.post("/mrp/sync/po", headers=auth_headers, json={})
        if sync.status_code >= 500:
            pytest.skip(f"MRP sync unavailable: {sync.status_code}")

        masters = client.get("/mrp/masters/po", headers=auth_headers)
        assert masters.status_code == 200
        sample = None
        outstanding = 0.0
        for r in masters.json():
            if str(r.get("status") or "") not in ("outstanding", "partial"):
                continue
            outstanding = float(r.get("qty_order") or 0) - float(r.get("qty_processed") or 0)
            emb = r.get("emboss")
            emb_empty = emb is None or str(emb).strip() in ("", "-")
            if outstanding >= 1 and r.get("item_name") and r.get("tebal") and r.get("warna") and emb_empty:
                sample = r
                break
        if not sample:
            pytest.skip("butuh PO dengan emboss kosong/null/-")

        created = client.post(
            "/mrp/rencana-produksi",
            headers=auth_headers,
            json={
                "nama_rencana": f"TEST EMBOS DASH {date.today().isoformat()}",
                "tanggal_rencana": date.today().isoformat(),
                "po_lines": [{"po_id": sample["id"], "qty": min(1.0, outstanding)}],
            },
        )
        assert created.status_code == 201, created.text
        rid = created.json()["id"]
        detail = client.get(f"/mrp/rencana-produksi/{rid}", headers=auth_headers)
        item = detail.json()["items"][0]
        assert (item.get("emboss") or "").strip() in ("", "-")

        po_dlg = client.get(
            f"/mrp/rencana-produksi/item/{item['id']}/list-po",
            headers=auth_headers,
        )
        assert po_dlg.status_code == 200, po_dlg.text
        payload = po_dlg.json()
        po_list = payload.get("po_list") or []
        assert any(int(p.get("id") or 0) == int(sample["id"]) for p in po_list)
        hit = next(p for p in po_list if int(p["id"]) == int(sample["id"]))
        assert "already_allocated_qty" in hit
        assert "qty_balance_erp" in hit
        assert "qty_order" in hit
        assert float(hit.get("already_allocated_qty") or 0) >= min(1.0, outstanding) - 1e-6

        # Re-save qty sama — completed/partial tetap bisa dipertahankan
        again = client.post(
            f"/mrp/rencana-produksi/item/{item['id']}/list-po",
            headers=auth_headers,
            json={"pos": [{"po_id": sample["id"], "qty": min(1.0, outstanding)}]},
        )
        assert again.status_code == 200, again.text


def test_save_po_rejects_overbook_across_plans(auth_headers):
    with _client() as client:
        sync = client.post("/mrp/sync/po", headers=auth_headers, json={})
        if sync.status_code >= 500:
            pytest.skip(f"MRP sync unavailable: {sync.status_code}")
        client.post("/mrp/masters/po/recompute-processed", headers=auth_headers)

        masters = client.get("/mrp/masters/po", headers=auth_headers)
        sample = None
        outstanding = 0.0
        for r in masters.json():
            if str(r.get("status") or "") not in ("outstanding", "partial"):
                continue
            outstanding = float(r.get("qty_order") or 0) - float(r.get("qty_processed") or 0)
            if outstanding >= 1 and r.get("item_name") and r.get("tebal") and r.get("warna"):
                sample = r
                break
        if not sample:
            pytest.skip("tidak ada PO outstanding")

        qty = min(1.0, outstanding)
        created = client.post(
            "/mrp/rencana-produksi",
            headers=auth_headers,
            json={
                "nama_rencana": f"TEST OVERBOOK {date.today().isoformat()}",
                "tanggal_rencana": date.today().isoformat(),
                "po_lines": [{"po_id": sample["id"], "qty": qty}],
            },
        )
        assert created.status_code == 201, created.text
        rid = created.json()["id"]
        detail = client.get(f"/mrp/rencana-produksi/{rid}", headers=auth_headers)
        item_id = detail.json()["items"][0]["id"]

        # Coba alokasi melebihi sisa (setelah release item ini, sisa = order - alokasi_lain)
        # Karena replace melepaskan dulu, overbook harus memakai qty > qty_order
        over = client.post(
            f"/mrp/rencana-produksi/item/{item_id}/list-po",
            headers=auth_headers,
            json={
                "pos": [
                    {
                        "po_id": sample["id"],
                        "qty": float(sample.get("qty_order") or 0) + 1000,
                    }
                ]
            },
        )
        assert over.status_code == 400, over.text
