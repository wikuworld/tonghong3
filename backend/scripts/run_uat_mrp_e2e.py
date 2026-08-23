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
REPORT_PATH = Path("/home/developer/project/dokumentasi/uat-mrp-sl043-hasil.md")


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
    rows = req("GET", "/mrp/masters/po", tok)
    if isinstance(rows, dict):
        rows = rows.get("items") or rows.get("data") or []
    hits = []
    for r in rows or []:
        if str(r.get("no_po") or "") != str(no_po):
            continue
        sid = r.get("source_detail_id")
        if sid is not None and int(sid) != int(source_detail_id):
            continue
        hits.append(r)
    if not hits:
        raise StepFail(
            "master PO MRP",
            f"tidak ketemu no_po={no_po} source_detail_id={source_detail_id}",
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
        return {
            "po_id": header["id"],
            "po_number": confirmed.get("po_number") or header.get("po_number"),
            "status": confirmed.get("status"),
            "detail_id": detail["id"],
            "unit_price": str(detail.get("unit_price")),
            "swatch_id": detail.get("color_swatch_recipe_id"),
            "color_standard": detail.get("color_standard"),
            "lot": detail.get("thi_line_ref") or detail.get("lot_number"),
        }

    out["m0"] = step(results, "M0 SO draft+confirm", m0)
    po_id = out["m0"]["po_id"]
    po_number = out["m0"]["po_number"]
    detail_id = out["m0"]["detail_id"]

    def m1():
        sync = req("POST", "/mrp/sync/po", prod, {})
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
            "sync": {k: sync.get(k) for k in ("ok", "synced", "count", "upserted") if k in sync}
            or sync,
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

    out["m1"] = step(results, "M1 sync PO MRP", m1)
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
        }

    out["m7"] = step(results, "M7 packing finish + FG in_stock", m7)
    kode_packing = out["m7"]["kode_packing"]

    def m8():
        out_data = req(
            "POST",
            "/mrp/gudang-fg/out",
            prod,
            {"kode_packing": kode_packing, "keterangan": "UAT MRP"},
        )
        fg_id = out_data.get("id")
        delivery_id = out_data.get("erp_delivery_id")
        if not delivery_id:
            raise StepFail("M8 delivery bridge", out_data)
        fg = req("GET", f"/mrp/gudang-fg/{fg_id}", prod)
        fg_row = fg.get("fg") or fg
        if str(fg_row.get("status") or "") != "out":
            raise StepFail("M8 FG masih in_stock", {"out": out_data, "fg": fg_row})
        delivery = req("GET", f"/delivery/{delivery_id}", mkt)
        po_on_del = delivery.get("po_number")
        return {
            "fg_id": fg_id,
            "fg_status": fg_row.get("status"),
            "kode_packing": kode_packing,
            "erp_delivery_id": delivery_id,
            "erp_delivery_number": out_data.get("erp_delivery_number") or delivery.get("delivery_number"),
            "erp_packing_id": out_data.get("erp_packing_id"),
            "delivery_status": delivery.get("status"),
            "delivery_po_number": po_on_del,
            "bridge_status": out_data.get("bridge_status"),
        }

    out["m8"] = step(results, "M8 FG OUT + Delivery ERP", m8)
    return out


def write_report(payload: dict, path: Path) -> None:
    lines = [
        "# Hasil UAT SO confirm + MRP sampai FG OUT",
        "",
        f"Waktu: {payload.get('ran_at')}",
        "Paket: SL043 · Nike · FG01854 · PINKSICLE 6FS · alokasi rencana 10",
        "Jalur: SO draft→confirm (tanpa Production/QC/Packing ERP) lalu MRP penuh termasuk FG OUT.",
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
                "erp_delivery_id",
                "erp_delivery_number",
                "delivery_status",
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
