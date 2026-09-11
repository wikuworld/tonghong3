#!/usr/bin/env python3
"""UAT SO confirm + MRP shopfloor sampai FG OUT (SL043 / FG01854)."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlencode

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from run_uat_so_e2e import (  # noqa: E402
    PWD_DEMO,
    TODAY,
    StepFail,
    create_so_line,
    load_masters,
    login,
    req,
    step,
)

STAMP = datetime.now().strftime("%y%m%d%H%M")
QTY_RENCANA = 10.0
REPORT_PATH = Path(__file__).resolve().parents[2] / "dokumentasi" / "uat-mrp-sl043-hasil.md"


def qpath(path: str, **params) -> str:
    qs = urlencode({k: v for k, v in params.items() if v is not None}, quote_via=quote)
    return f"{path}?{qs}" if qs else path


def expect_http(fn, *, codes, step_name: str):
    try:
        out = fn()
        raise StepFail(step_name, {"unexpected_ok": out})
    except StepFail as e:
        detail = e.detail if isinstance(e.detail, dict) else {}
        http = detail.get("http")
        if http not in codes:
            raise StepFail(step_name, e.detail) from e
        return detail


def pick_pu_treatment(tok: str) -> str:
    rows = req("GET", "/mrp/masters/treatment", tok)
    if isinstance(rows, dict):
        rows = rows.get("items") or rows.get("treatments") or []
    pu = [
        r
        for r in (rows or [])
        if str(r.get("jenis") or "").upper() == "PU" and (r.get("nama_treatment") or "").strip()
    ]
    if not pu:
        raise StepFail("treatment PU", "tidak ada master treatment jenis PU")
    return str(pu[0]["nama_treatment"]).strip()


def find_master_po(tok: str, *, no_po: str, source_detail_id: int) -> dict:
    rows = req("GET", qpath("/mrp/masters/po", source_detail_ids=str(source_detail_id)), tok)
    if isinstance(rows, dict):
        rows = rows.get("items") or rows.get("data") or []
    hits = []
    for r in rows or []:
        sid = r.get("source_detail_id")
        if sid is None or int(sid) != int(source_detail_id):
            continue
        hits.append(r)
    if not hits:
        raise StepFail(
            "master PO MRP",
            f"tidak ketemu source_detail_id={source_detail_id} (no_po/so={no_po})",
        )
    return hits[0]


def run_flow(tokens: dict, masters: dict, results: list) -> dict:
    mkt = tokens["marketing"]
    prod = tokens["production"]
    out: dict = {}
    ref = f"UAT-MRP-SL043-{STAMP}"

    def m0():
        header, detail = create_so_line(mkt, masters, ref=ref, source="swatch")
        if (header.get("status") or "").lower() != "draft":
            raise StepFail("M0 draft", header)
        price = detail.get("unit_price")
        if price is None or abs(float(price) - 1.38) > 0.001:
            raise StepFail("M0 harga", {"unit_price": price, "expected": 1.38})
        if not detail.get("color_swatch_recipe_id"):
            raise StepFail("M0 swatch", detail)
        confirmed = req("PUT", f"/po/{header['id']}", mkt, {"status": "confirmed"})
        if (confirmed.get("status") or "").lower() != "confirmed":
            raise StepFail("M0 confirm", confirmed)
        mrp_sync = confirmed.get("mrp_sync") or {}
        return {
            "po_id": header["id"],
            "po_number": confirmed.get("po_number") or header.get("po_number"),
            "status": confirmed.get("status"),
            "detail_id": detail["id"],
            "unit_price": str(detail.get("unit_price")),
            "swatch_id": detail.get("color_swatch_recipe_id"),
            "color_standard": detail.get("color_standard"),
            "lot": detail.get("thi_line_ref") or detail.get("lot_number"),
            "mrp_sync_ok": mrp_sync.get("ok"),
            "mrp_sync_attempts": mrp_sync.get("attempts"),
        }

    out["m0"] = step(results, "M0 SO draft+confirm", m0)
    po_id = out["m0"]["po_id"]
    po_number = out["m0"]["po_number"]
    detail_id = out["m0"]["detail_id"]

    def m1():
        # Confirm sudah push ke MRP; jangan full sync manual kecuali baris belum muncul.
        sync = None
        try:
            row = find_master_po(prod, no_po=po_number, source_detail_id=detail_id)
        except StepFail:
            sync = req("POST", "/mrp/sync/po", prod, {"po_id": po_id})
            if sync.get("ok") is not True and not sync.get("synced"):
                if "ok" in sync and sync.get("ok") is False:
                    raise StepFail("M1 sync", sync)
            row = find_master_po(prod, no_po=po_number, source_detail_id=detail_id)
        status = str(row.get("status") or "")
        if status not in ("outstanding", "partial"):
            raise StepFail("M1 status", row)
        if not (row.get("item_name") and row.get("tebal") and row.get("warna")):
            raise StepFail("M1 spek", row)
        return {
            "sync": (
                {k: sync.get(k) for k in ("ok", "synced", "count", "upserted", "attempts") if k in sync}
                if isinstance(sync, dict)
                else {"via": "confirm"}
            ),
            "mrp_po_id": row["id"],
            "no_po": row.get("no_po"),
            "source_detail_id": row.get("source_detail_id"),
            "status": status,
            "qty_order": row.get("qty_order"),
            "qty_processed": row.get("qty_processed"),
            "item_name": row.get("item_name"),
            "tebal": row.get("tebal"),
            "warna": row.get("warna"),
        }

    out["m1"] = step(results, "M1 master PO setelah Confirm", m1)
    mrp_po_id = int(out["m1"]["mrp_po_id"])
    processed_before = float(out["m1"].get("qty_processed") or 0)

    def m2():
        created = req(
            "POST",
            "/mrp/rencana-produksi",
            prod,
            {
                "nama_rencana": f"UAT MRP SL043 {STAMP}",
                "tanggal_rencana": TODAY,
                "po_lines": [{"po_id": mrp_po_id, "qty": QTY_RENCANA}],
            },
        )
        if created.get("ok") is not True:
            raise StepFail("M2 create", created)
        rid = created["id"]
        detail = req("GET", f"/mrp/rencana-produksi/{rid}", prod)
        items = detail.get("items") or []
        if len(items) != 1:
            raise StepFail("M2 items", detail)
        item = items[0]
        if not item.get("kode_lot_wip"):
            raise StepFail("M2 WIP", item)
        rencana = detail.get("rencana") or detail
        status = str(rencana.get("status") or created.get("status") or "")
        row2 = find_master_po(prod, no_po=po_number, source_detail_id=detail_id)
        processed = float(row2.get("qty_processed") or 0)
        if processed + 1e-6 < processed_before + QTY_RENCANA:
            raise StepFail(
                "M2 qty_processed",
                {"before": processed_before, "after": processed, "expect_plus": QTY_RENCANA},
            )
        return {
            "rencana_id": rid,
            "status": status or "active",
            "item_id": item["id"],
            "kode_wip": item.get("kode_lot_wip"),
            "kode_rencana_item": item.get("kode_rencana_item"),
            "qty_processed": processed,
        }

    out["m2"] = step(results, "M2 rencana produksi", m2)
    rencana_item_id = out["m2"]["item_id"]
    kode_wip = out["m2"]["kode_wip"]

    kode_palet = f"KY-UAT-{STAMP}"
    kode_yl = f"YL-UAT-{STAMP}"

    def m3():
        palet = req(
            "POST",
            "/mrp/palet/in",
            prod,
            {
                "kode_palet": kode_palet,
                "tanggal": TODAY,
                "keterangan": "UAT MRP SL043",
                "items": [
                    {
                        "kode_yl": kode_yl,
                        "thickness": "1.2",
                        "warna": "PINKSICLE (6FS) FLUORESCENT",
                        "qty": 50,
                    }
                ],
            },
        )
        yl = req("GET", f"/mrp/palet/{quote(kode_palet, safe='')}/yl", prod)
        rows = yl if isinstance(yl, list) else (yl.get("items") or yl.get("yls") or [])
        hit = next((r for r in rows if str(r.get("kode_yl")) == kode_yl), None)
        if not hit:
            raise StepFail("M3 YL", {"palet": palet, "yl": yl})
        return {
            "kode_palet": kode_palet,
            "kode_yl": kode_yl,
            "qty": hit.get("qty"),
            "palet_ok": palet.get("ok", True),
        }

    out["m3"] = step(results, "M3 palet IN", m3)

    def m4():
        treatment = pick_pu_treatment(prod)
        created = req(
            "POST",
            "/mrp/proses",
            prod,
            {
                "rencana_item_id": rencana_item_id,
                "treatment_jenis": "PU",
                "treatment_list": [treatment],
            },
        )
        pid = created["id"]
        blocked = expect_http(
            lambda: req(
                "POST",
                f"/mrp/proses/{pid}/actions",
                prod,
                {
                    "action": "scan_ky",
                    "kode_palet": kode_palet,
                    "kode_yl": kode_yl,
                    "target_qty": QTY_RENCANA,
                },
            ),
            codes={400},
            step_name="M4 scan sebelum start",
        )
        req("POST", f"/mrp/proses/{pid}/actions", prod, {"action": "start"})
        ky = req(
            "POST",
            f"/mrp/proses/{pid}/actions",
            prod,
            {
                "action": "scan_ky",
                "kode_palet": kode_palet,
                "kode_yl": kode_yl,
                "target_qty": QTY_RENCANA,
            },
        )
        detail = req("GET", f"/mrp/proses/{pid}", prod)
        active = detail.get("active_ky") or {}
        ky_id = active.get("id") or ky.get("ky_id") or ky.get("id")
        if not ky_id:
            sessions = detail.get("ky_sessions") or []
            open_s = next((s for s in sessions if not s.get("date_out")), None)
            ky_id = (open_s or {}).get("id")
        if not ky_id:
            raise StepFail("M4 ky_id", {"scan": ky, "detail": detail})
        req(
            "POST",
            f"/mrp/proses/{pid}/actions",
            prod,
            {"action": "add_ukur", "ky_id": ky_id, "size_val": QTY_RENCANA},
        )
        req(
            "POST",
            f"/mrp/proses/{pid}/actions",
            prod,
            {"action": "selesai_ky", "ky_id": ky_id},
        )
        req("POST", f"/mrp/proses/{pid}/actions", prod, {"action": "save"})
        detail2 = req("GET", f"/mrp/proses/{pid}", prod)
        persiapan = detail2.get("persiapan") or {}
        status = str(persiapan.get("status") or "")
        if status not in ("completed", "saved"):
            raise StepFail("M4 status", persiapan)
        total = float(persiapan.get("total_size") or persiapan.get("total_ukuran") or 0)
        if total <= 0:
            raise StepFail("M4 total_size", persiapan)
        return {
            "proses_id": pid,
            "kode_proses": created.get("kode_proses") or persiapan.get("kode_proses"),
            "kode_wip": persiapan.get("kode_wip") or kode_wip,
            "status": status,
            "total_size": total,
            "treatment": treatment,
            "scan_before_start": blocked,
        }

    out["m4"] = step(results, "M4 proses PU", m4)
    kode_wip = out["m4"]["kode_wip"] or kode_wip

    def m5():
        opt = req("GET", "/mrp/lab/options", prod)
        kimia = opt.get("kimia_list") or []
        if not kimia:
            raise StepFail("M5 kimia", "kimia_list kosong")
        kode = kimia[0].get("kode_kimia")
        created = req(
            "POST",
            "/mrp/lab",
            prod,
            {
                "nama_lot_warna": f"UAT LAB SL043 {STAMP}",
                "rencana_item_id": rencana_item_id,
                "items": [{"kode_kimia": kode, "qty": 1, "satuan": "kg"}],
            },
        )
        kode_lot = created.get("kode_lot_warna")
        if not kode_lot:
            raise StepFail("M5 lot", created)
        return {
            "kode_lot_warna": kode_lot,
            "kode_kimia": kode,
            "nama_kimia": kimia[0].get("nama_kimia") or kimia[0].get("nama"),
        }

    out["m5"] = step(results, "M5 lab lot", m5)

    def m6():
        created = req(
            "POST",
            "/mrp/checkpoint",
            prod,
            {
                "kode_wip": kode_wip,
                "result": "OK",
                "thickness_actual": 1.1,
                "softness_actual": "soft",
                "remark": "UAT MRP SL043",
            },
        )
        if created.get("ok") is not True and created.get("result") != "OK":
            if not created.get("id"):
                raise StepFail("M6 checkpoint", created)
        result = str(created.get("result") or "OK").upper()
        if result != "OK":
            raise StepFail("M6 result", created)
        return {
            "checkpoint_id": created.get("id"),
            "kode_wip": created.get("kode_wip") or kode_wip,
            "result": result,
        }

    out["m6"] = step(results, "M6 checkpoint OK", m6)

    def m7():
        scan = req("GET", qpath("/mrp/packing/scan-wip", q=kode_wip), prod)
        pos = scan.get("po_list") or []
        po = next((p for p in pos if int(p.get("po_id") or 0) == mrp_po_id), pos[0] if pos else None)
        if not po:
            po = {
                "no_po": po_number,
                "no_so": po_number,
                "customer": masters["customer"].get("name") or "SL043",
                "qty_sq": QTY_RENCANA,
                "po_id": mrp_po_id,
            }
        started = req(
            "POST",
            "/mrp/packing",
            prod,
            {
                "kode_wip": kode_wip,
                "no_po": po.get("no_po") or po_number,
                "no_so": po.get("no_so") or "",
                "customer": po.get("customer") or masters["customer"].get("name") or "",
                "qty_sq": po.get("qty_sq") or QTY_RENCANA,
                "po_id": po.get("po_id") or mrp_po_id,
            },
        )
        packing_id = started["id"]
        kode_packing = started.get("kode_packing")
        req(
            "POST",
            f"/mrp/packing/{packing_id}/actions",
            prod,
            {"action": "add_roll", "lembar": 1, "ukuran": QTY_RENCANA},
        )
        finished = req(
            "POST",
            f"/mrp/packing/{packing_id}/actions",
            prod,
            {"action": "finish"},
        )
        detail = req("GET", f"/mrp/packing/{packing_id}", prod)
        packing = detail.get("packing") or detail
        status = str(packing.get("status") or "")
        kode_packing = packing.get("kode_packing") or kode_packing
        if status != "finished":
            raise StepFail("M7 status", {"finish": finished, "detail": detail})
        fgs = req("GET", qpath("/mrp/gudang-fg", status="in_stock"), prod)
        if isinstance(fgs, dict):
            fgs = fgs.get("items") or fgs.get("data") or []
        hit = next((r for r in (fgs or []) if str(r.get("kode_packing")) == str(kode_packing)), None)
        if not hit:
            raise StepFail("M7 FG in_stock", {"kode_packing": kode_packing, "fgs": fgs[:8] if isinstance(fgs, list) else fgs})
        erp_prod = finished.get("erp_production") or started.get("erp_production")
        return {
            "packing_id": packing_id,
            "kode_packing": kode_packing,
            "status": status,
            "fg_id": hit.get("id"),
            "fg_status": hit.get("status"),
            "erp_production": erp_prod,
            "erp_packing_id": (erp_prod or {}).get("packing_id"),
        }

    out["m7"] = step(results, "M7 packing finish + FG in_stock", m7)
    kode_packing = out["m7"]["kode_packing"]
    erp_packing_id = out["m7"].get("erp_packing_id")
    fg_id_in = out["m7"].get("fg_id")
    wh = tokens.get("warehouse") or mkt
    fin = tokens.get("finance") or mkt

    def m8():
        blocked = expect_http(
            lambda: req(
                "POST",
                "/mrp/gudang-fg/out",
                prod,
                {"kode_packing": kode_packing, "keterangan": "UAT mandiri"},
            ),
            codes={400},
            step_name="M8 FG OUT mandiri",
        )
        opts = req(
            "GET",
            qpath("/marketing/outstanding-packing-options", po_detail_ids=str(detail_id)),
            mkt,
        )
        data = opts.get("data") if isinstance(opts, dict) else opts
        if not data:
            raise StepFail("M8 packing options kosong", opts)
        line = next(
            (r for r in data if int(r.get("po_detail_id") or 0) == int(detail_id)),
            data[0],
        )
        qty = line.get("qty_available") or QTY_RENCANA
        ship = req(
            "POST",
            "/marketing/outstanding-ship-batch",
            mkt,
            {
                "lines": [
                    {
                        "po_detail_id": detail_id,
                        "packing_id": line["packing_id"],
                        "packing_detail_id": line.get("packing_detail_id"),
                        "production_detail_id": line["production_detail_id"],
                        "qty": qty,
                        "delivery_date": TODAY,
                    }
                ],
                "destination": "UAT MRP Outstanding",
            },
        )
        if int(ship.get("delivery_count") or 0) != 1:
            raise StepFail("M8 delivery_count", ship)
        numbers = ship.get("delivery_numbers") or []
        did = int(ship["delivery_ids"][0])
        delivery = req("GET", f"/delivery/{did}", mkt)
        dnum = (delivery.get("delivery_number") or (numbers[0] if numbers else "") or "").strip()
        if not dnum:
            raise StepFail("M8 delivery_number kosong", {"ship": ship, "delivery": delivery})
        fgs = req("GET", qpath("/mrp/gudang-fg", q=kode_packing), prod)
        if isinstance(fgs, dict):
            fgs = fgs.get("items") or fgs.get("data") or []
        hit = next((r for r in (fgs or []) if str(r.get("kode_packing")) == str(kode_packing)), None)
        if hit is None and fg_id_in:
            fg = req("GET", f"/mrp/gudang-fg/{fg_id_in}", prod)
            hit = fg.get("fg") or fg
        if str((hit or {}).get("status") or "") != "out":
            raise StepFail("M8 FG belum out", {"fg": hit, "ship": ship})
        return {
            "fg_out_blocked": blocked.get("http") if isinstance(blocked, dict) else 400,
            "option_packing_id": line.get("packing_id"),
            "production_detail_id": line.get("production_detail_id"),
            "delivery_id": did,
            "delivery_number": dnum,
            "delivery_status": delivery.get("status"),
            "fg_status": (hit or {}).get("status"),
            "fg_id": (hit or {}).get("id") or fg_id_in,
        }

    out["m8"] = step(results, "M8 Outstanding SJ + FG OUT", m8)
    delivery_id = out["m8"]["delivery_id"]
    packing_id = out["m8"].get("option_packing_id") or erp_packing_id

    def m9():
        sent = req("PUT", f"/delivery/{delivery_id}", wh, {"status": "sent"})
        if (sent.get("status") or "").lower() != "sent":
            raise StepFail("M9 sent", sent)
        if packing_id:
            req("POST", f"/packing/{int(packing_id)}/mark-invpl-printed", wh)
        req("POST", f"/delivery/{delivery_id}/mark-surat-jalan-printed", mkt)
        inv = req(
            "POST",
            "/invoice",
            fin,
            {
                "delivery_id": delivery_id,
                "customer_id": masters["customer"]["id"],
                "po_id": po_id,
                "po_number": po_number,
                "invoice_date": TODAY,
            },
        )
        invoice_number = inv.get("invoice_number")
        if not invoice_number:
            raise StepFail("M9 invoice_number", inv)
        rar = req(
            "GET",
            qpath(
                "/reports/accounts-receivable",
                payment_status="all",
                date_from=TODAY,
                date_to=TODAY,
            ),
            fin,
        )
        rar_rows = rar.get("rows") or []
        if not any(str(r.get("invoice_number") or "") == str(invoice_number) for r in rar_rows):
            raise StepFail("M9 RAR", {"invoice_number": invoice_number, "rar_count": len(rar_rows)})
        # Pending Payment = laporan tunggakan master (bukan daftar invoice baru); cukup health HTTP.
        pp = req("GET", "/reports/pending-payment", fin)
        if not isinstance(pp, dict):
            raise StepFail("M9 Pending Payment health", {"pp_type": type(pp).__name__})
        return {
            "delivery_status": sent.get("status"),
            "invoice_id": inv.get("id"),
            "invoice_number": invoice_number,
            "rar_hit": True,
            "pp_http_ok": True,
        }

    out["m9"] = step(results, "M9 sent + invoice + RAR", m9)

    def m10():
        blocked = expect_http(
            lambda: req(
                "POST",
                "/production",
                prod,
                {"po_id": po_id, "start_date": TODAY, "status": "planned"},
            ),
            codes={403},
            step_name="M10 ERP production",
        )
        return {"http": blocked.get("http"), "erp_shopfloor_blocked": True}

    out["m10"] = step(results, "M10 ERP production 403", m10)

    def m11():
        header2, detail2 = create_so_line(mkt, masters, ref=f"{ref}-B", source="swatch")
        confirmed2 = req("PUT", f"/po/{header2['id']}", mkt, {"status": "confirmed"})
        if (confirmed2.get("mkt_workflow_stage") or "") != "in_outstanding":
            raise StepFail("M11 confirm B", confirmed2)
        req("POST", "/mrp/sync/po", prod, {})
        row_b = find_master_po(prod, no_po=confirmed2.get("po_number") or header2.get("po_number"), source_detail_id=detail2["id"])
        created = req(
            "POST",
            "/mrp/rencana-produksi",
            prod,
            {
                "nama_rencana": f"UAT MRP SL043 {STAMP}B",
                "tanggal_rencana": TODAY,
                "po_lines": [{"po_id": row_b["id"], "qty": QTY_RENCANA}],
            },
        )
        if created.get("ok") is not True:
            raise StepFail("M11 rencana B", created)
        rid = created["id"]
        detail_r = req("GET", f"/mrp/rencana-produksi/{rid}", prod)
        item = (detail_r.get("items") or [None])[0]
        if not item or not item.get("kode_lot_wip"):
            raise StepFail("M11 WIP B", detail_r)
        kode_wip_b = item["kode_lot_wip"]
        kode_palet_b = f"KY-UAT-{STAMP}B"
        kode_yl_b = f"YL-UAT-{STAMP}B"
        req(
            "POST",
            "/mrp/palet/in",
            prod,
            {
                "kode_palet": kode_palet_b,
                "tanggal": TODAY,
                "keterangan": "UAT dual",
                "items": [
                    {
                        "kode_yl": kode_yl_b,
                        "thickness": "1.2",
                        "warna": "PINKSICLE (6FS) FLUORESCENT",
                        "qty": 50,
                    }
                ],
            },
        )
        treatment = pick_pu_treatment(prod)
        proses = req(
            "POST",
            "/mrp/proses",
            prod,
            {
                "rencana_item_id": item["id"],
                "treatment_jenis": "PU",
                "treatment_list": [treatment],
            },
        )
        pid = proses["id"]
        req("POST", f"/mrp/proses/{pid}/actions", prod, {"action": "start"})
        ky = req(
            "POST",
            f"/mrp/proses/{pid}/actions",
            prod,
            {
                "action": "scan_ky",
                "kode_palet": kode_palet_b,
                "kode_yl": kode_yl_b,
                "target_qty": QTY_RENCANA,
            },
        )
        detail_p = req("GET", f"/mrp/proses/{pid}", prod)
        active = detail_p.get("active_ky") or {}
        ky_id = active.get("id") or ky.get("ky_id") or ky.get("id")
        if not ky_id:
            sessions = detail_p.get("ky_sessions") or []
            open_s = next((s for s in sessions if not s.get("date_out")), None)
            ky_id = (open_s or {}).get("id")
        req("POST", f"/mrp/proses/{pid}/actions", prod, {"action": "add_ukur", "ky_id": ky_id, "size_val": QTY_RENCANA})
        req("POST", f"/mrp/proses/{pid}/actions", prod, {"action": "selesai_ky", "ky_id": ky_id})
        req("POST", f"/mrp/proses/{pid}/actions", prod, {"action": "save"})
        opt = req("GET", "/mrp/lab/options", prod)
        kimia = opt.get("kimia_list") or []
        if not kimia:
            raise StepFail("M11 kimia B", "kimia_list kosong")
        req(
            "POST",
            "/mrp/lab",
            prod,
            {
                "nama_lot_warna": f"UAT LAB SL043 {STAMP}B",
                "rencana_item_id": item["id"],
                "items": [{"kode_kimia": kimia[0].get("kode_kimia"), "qty": 1, "satuan": "kg"}],
            },
        )
        req(
            "POST",
            "/mrp/checkpoint",
            prod,
            {
                "kode_wip": kode_wip_b,
                "result": "OK",
                "thickness_actual": 1.1,
                "softness_actual": "soft",
                "remark": "UAT dual",
            },
        )
        scan = req("GET", qpath("/mrp/packing/scan-wip", q=kode_wip_b), prod)
        pos = scan.get("po_list") or []
        po_b = next((p for p in pos if int(p.get("po_id") or 0) == int(row_b["id"])), pos[0] if pos else None)
        if not po_b:
            po_b = {
                "no_po": confirmed2.get("po_number"),
                "qty_sq": QTY_RENCANA,
                "po_id": row_b["id"],
            }
        started = req(
            "POST",
            "/mrp/packing",
            prod,
            {
                "kode_wip": kode_wip_b,
                "customer": masters["customer"].get("name") or "",
                "no_po": po_b.get("no_po") or confirmed2.get("po_number"),
                "no_so": po_b.get("no_so") or "",
                "qty_sq": po_b.get("qty_sq") or QTY_RENCANA,
                "po_id": po_b.get("po_id") or row_b["id"],
                "source_detail_id": detail2["id"],
            },
        )
        packing_b = started["id"]
        req("POST", f"/mrp/packing/{packing_b}/actions", prod, {"action": "add_roll", "lembar": 1, "ukuran": QTY_RENCANA})
        req("POST", f"/mrp/packing/{packing_b}/actions", prod, {"action": "finish"})
        opts_b = req(
            "GET",
            qpath("/marketing/outstanding-packing-options", po_detail_ids=str(detail2["id"])),
            mkt,
        )
        data_b = opts_b.get("data") if isinstance(opts_b, dict) else opts_b
        if not data_b:
            raise StepFail("M11 packing options B", opts_b)
        line_b = data_b[0]
        header3, detail3 = create_so_line(mkt, masters, ref=f"{ref}-C", source="swatch")
        confirmed3 = req("PUT", f"/po/{header3['id']}", mkt, {"status": "confirmed"})
        req("POST", "/mrp/sync/po", prod, {})
        row_c = find_master_po(
            prod,
            no_po=confirmed3.get("po_number") or header3.get("po_number"),
            source_detail_id=detail3["id"],
        )
        created_c = req(
            "POST",
            "/mrp/rencana-produksi",
            prod,
            {
                "nama_rencana": f"UAT MRP SL043 {STAMP}C",
                "tanggal_rencana": TODAY,
                "po_lines": [{"po_id": row_c["id"], "qty": QTY_RENCANA}],
            },
        )
        if created_c.get("ok") is not True:
            raise StepFail("M11 rencana C", created_c)
        rid_c = created_c["id"]
        detail_c = req("GET", f"/mrp/rencana-produksi/{rid_c}", prod)
        item_c = (detail_c.get("items") or [None])[0]
        if not item_c or not item_c.get("kode_lot_wip"):
            raise StepFail("M11 WIP C", detail_c)
        kode_wip_c = item_c["kode_lot_wip"]
        kode_palet_c = f"KY-UAT-{STAMP}C"
        kode_yl_c = f"YL-UAT-{STAMP}C"
        req(
            "POST",
            "/mrp/palet/in",
            prod,
            {
                "kode_palet": kode_palet_c,
                "tanggal": TODAY,
                "keterangan": "UAT dual C",
                "items": [
                    {
                        "kode_yl": kode_yl_c,
                        "thickness": "1.2",
                        "warna": "PINKSICLE (6FS) FLUORESCENT",
                        "qty": 50,
                    }
                ],
            },
        )
        proses_c = req(
            "POST",
            "/mrp/proses",
            prod,
            {
                "rencana_item_id": item_c["id"],
                "treatment_jenis": "PU",
                "treatment_list": [treatment],
            },
        )
        pid_c = proses_c["id"]
        req("POST", f"/mrp/proses/{pid_c}/actions", prod, {"action": "start"})
        ky_c = req(
            "POST",
            f"/mrp/proses/{pid_c}/actions",
            prod,
            {
                "action": "scan_ky",
                "kode_palet": kode_palet_c,
                "kode_yl": kode_yl_c,
                "target_qty": QTY_RENCANA,
            },
        )
        detail_pc = req("GET", f"/mrp/proses/{pid_c}", prod)
        active_c = detail_pc.get("active_ky") or {}
        ky_id_c = active_c.get("id") or ky_c.get("ky_id") or ky_c.get("id")
        if not ky_id_c:
            sessions = detail_pc.get("ky_sessions") or []
            open_s = next((s for s in sessions if not s.get("date_out")), None)
            ky_id_c = (open_s or {}).get("id")
        req("POST", f"/mrp/proses/{pid_c}/actions", prod, {"action": "add_ukur", "ky_id": ky_id_c, "size_val": QTY_RENCANA})
        req("POST", f"/mrp/proses/{pid_c}/actions", prod, {"action": "selesai_ky", "ky_id": ky_id_c})
        req("POST", f"/mrp/proses/{pid_c}/actions", prod, {"action": "save"})
        req(
            "POST",
            "/mrp/lab",
            prod,
            {
                "nama_lot_warna": f"UAT LAB SL043 {STAMP}C",
                "rencana_item_id": item_c["id"],
                "items": [{"kode_kimia": kimia[0].get("kode_kimia"), "qty": 1, "satuan": "kg"}],
            },
        )
        req(
            "POST",
            "/mrp/checkpoint",
            prod,
            {
                "kode_wip": kode_wip_c,
                "result": "OK",
                "thickness_actual": 1.1,
                "softness_actual": "soft",
                "remark": "UAT dual C",
            },
        )
        scan_c = req("GET", qpath("/mrp/packing/scan-wip", q=kode_wip_c), prod)
        pos_c = scan_c.get("po_list") or []
        po_c = next((p for p in pos_c if int(p.get("po_id") or 0) == int(row_c["id"])), pos_c[0] if pos_c else None)
        if not po_c:
            po_c = {"no_po": confirmed3.get("po_number"), "qty_sq": QTY_RENCANA, "po_id": row_c["id"]}
        started_c = req(
            "POST",
            "/mrp/packing",
            prod,
            {
                "kode_wip": kode_wip_c,
                "customer": masters["customer"].get("name") or "",
                "no_po": po_c.get("no_po") or confirmed3.get("po_number"),
                "qty_sq": QTY_RENCANA,
                "po_id": po_c.get("po_id") or row_c["id"],
                "source_detail_id": detail3["id"],
            },
        )
        packing_c = started_c["id"]
        req("POST", f"/mrp/packing/{packing_c}/actions", prod, {"action": "add_roll", "lembar": 1, "ukuran": QTY_RENCANA})
        req("POST", f"/mrp/packing/{packing_c}/actions", prod, {"action": "finish"})
        opts_c = req(
            "GET",
            qpath("/marketing/outstanding-packing-options", po_detail_ids=f"{detail2['id']},{detail3['id']}"),
            mkt,
        )
        data_both = opts_c.get("data") if isinstance(opts_c, dict) else opts_c
        line2 = next((r for r in (data_both or []) if int(r.get("po_detail_id") or 0) == int(detail2["id"])), None)
        line3 = next((r for r in (data_both or []) if int(r.get("po_detail_id") or 0) == int(detail3["id"])), None)
        if not line2 or not line3:
            raise StepFail("M11 dual options", {"opts": opts_c, "d2": detail2["id"], "d3": detail3["id"]})
        ship2 = req(
            "POST",
            "/marketing/outstanding-ship-batch",
            mkt,
            {
                "lines": [
                    {
                        "po_detail_id": detail2["id"],
                        "packing_id": line2["packing_id"],
                        "packing_detail_id": line2.get("packing_detail_id"),
                        "production_detail_id": line2["production_detail_id"],
                        "qty": line2.get("qty_available") or QTY_RENCANA,
                        "delivery_date": TODAY,
                    },
                    {
                        "po_detail_id": detail3["id"],
                        "packing_id": line3["packing_id"],
                        "packing_detail_id": line3.get("packing_detail_id"),
                        "production_detail_id": line3["production_detail_id"],
                        "qty": line3.get("qty_available") or QTY_RENCANA,
                        "delivery_date": TODAY,
                    },
                ],
                "destination": "UAT dual SO",
            },
        )
        if int(ship2.get("delivery_count") or 0) != 1:
            raise StepFail("M11 dual SJ", ship2)
        did2 = int(ship2["delivery_ids"][0])
        dh2 = req("GET", f"/delivery/{did2}", mkt)
        return {
            "so_b": confirmed2.get("po_number"),
            "so_c": confirmed3.get("po_number"),
            "delivery_id": did2,
            "delivery_number": dh2.get("delivery_number"),
            "delivery_count": ship2.get("delivery_count"),
        }

    out["m11"] = step(results, "M11 dual SO 1 SJ", m11)
    return out


def write_report(payload: dict, path: Path) -> None:
    lines = [
        "# Hasil UAT SO confirm + MRP sampai Outstanding SJ + invoice",
        "",
        f"Waktu: {payload.get('ran_at')}",
        "Paket: SL043 · Nike · FG01854 · PINKSICLE 6FS · alokasi rencana 10",
        "Jalur: Confirm → Outstanding → MRP packing → Outstanding SJ → invoice / RAR.",
        "Catatan: Pending Payment = laporan tunggakan master (health check saja), bukan bukti invoice baru; bukti invoice baru = RAR.",
        "",
        "## Ringkasan langkah",
        "",
        "| Langkah | Hasil | Catatan |",
        "|---------|-------|---------|",
    ]
    for r in payload.get("steps") or []:
        mark = "LULUS" if r.get("ok") else "GAGAL"
        note = ""
        if r.get("ok") and isinstance(r.get("data"), dict):
            keys = (
                "po_number",
                "status",
                "unit_price",
                "mrp_po_id",
                "rencana_id",
                "kode_wip",
                "kode_proses",
                "kode_palet",
                "kode_lot_warna",
                "kode_packing",
                "fg_status",
                "delivery_id",
                "delivery_number",
                "invoice_number",
                "delivery_count",
                "result",
            )
            bits = [f"{k}={r['data'][k]}" for k in keys if r["data"].get(k) not in (None, "")]
            note = "; ".join(bits)
        elif not r.get("ok"):
            note = json.dumps(r.get("error"), ensure_ascii=False)[:280]
        lines.append(f"| {r['step']} | {mark} | {note} |")
    lines += [
        "",
        "## Dokumen",
        "",
        "```json",
        json.dumps(payload.get("flow") or {}, ensure_ascii=False, indent=2, default=str),
        "```",
        "",
    ]
    if payload.get("stop_reason"):
        lines += [
            "## Berhenti",
            "",
            "```json",
            json.dumps(payload["stop_reason"], ensure_ascii=False, indent=2, default=str),
            "```",
            "",
        ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    results: list = []
    payload = {"ran_at": datetime.now().isoformat(timespec="seconds"), "steps": results}
    try:
        tokens = {}
        for role, user in (
            ("marketing", "demo_marketing"),
            ("production", "demo_production"),
            ("warehouse", "demo_warehouse"),
            ("finance", "demo_finance"),
        ):
            tokens[role] = step(results, f"login {user}", lambda u=user: login(u, PWD_DEMO))
        masters = step(
            results,
            "muat master SL043/FG01854/swatch",
            lambda: load_masters(tokens["marketing"]),
        )
        payload["flow"] = run_flow(tokens, masters, results)
    except StepFail as e:
        payload["stopped"] = True
        payload["stop_reason"] = {e.step: e.detail}
    except Exception as e:
        payload["stopped"] = True
        payload["stop_reason"] = str(e)
        results.append({"step": "crash", "ok": False, "error": str(e)})
    write_report(payload, REPORT_PATH)
    print(
        json.dumps(
            {
                "ok": all(r.get("ok") for r in results),
                "report": str(REPORT_PATH),
                "steps": [(r["step"], r["ok"]) for r in results],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if all(r.get("ok") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
