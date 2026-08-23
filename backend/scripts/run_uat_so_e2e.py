#!/usr/bin/env python3
"""UAT SO SL043 / FG01854: draft → invoice + cabang B1/B2/B3."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path

BASE = "http://127.0.0.1:8000/api/v1"
PWD_DEMO = "TonghongDemo2026"
TODAY = date.today().isoformat()
STAMP = datetime.now().strftime("%y%m%d%H%M")


class StepFail(Exception):
    def __init__(self, step: str, detail):
        self.step = step
        self.detail = detail
        super().__init__(f"{step}: {detail}")


def req(method: str, path: str, token: str | None = None, body=None, timeout=60):
    data = None
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            raw = resp.read()
            if not raw:
                return {"_status": resp.status}
            return json.loads(raw.decode())
    except urllib.error.HTTPError as e:
        raw = e.read().decode(errors="replace")
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = raw
        raise StepFail(f"{method} {path}", {"http": e.code, "body": parsed}) from e


def login(username: str, password: str) -> str:
    out = req("POST", "/auth/login", body={"username": username, "password": password})
    tok = out.get("access_token")
    if not tok:
        raise StepFail("login", out)
    return tok


def step(results: list, name: str, fn):
    try:
        data = fn()
        results.append({"step": name, "ok": True, "data": data})
        return data
    except StepFail as e:
        results.append({"step": name, "ok": False, "error": e.detail})
        raise
    except Exception as e:
        results.append({"step": name, "ok": False, "error": str(e)})
        raise StepFail(name, str(e)) from e


def load_masters(tok: str) -> dict:
    customers = req("GET", "/customers?limit=500", tok)
    if isinstance(customers, dict):
        customers = customers.get("items") or customers.get("data") or []
    cust = next((c for c in customers if (c.get("code") or "").upper() == "SL043"), None)
    if not cust:
        raise StepFail("master customer", "SL043 tidak ada")

    brands = req("GET", "/masters/brands", tok)
    brand = next(
        (b for b in brands if (b.get("code") or b.get("name") or "").upper() in {"NIKE", "NK"}),
        None,
    )
    if not brand:
        brand = next((b for b in brands if "NIKE" in (b.get("name") or "").upper()), None)
    if not brand:
        raise StepFail("master brand", "Nike tidak ada")

    page = req("GET", "/masters/items/page?keyword=FG01854&limit=20", tok)
    items = page.get("items") if isinstance(page, dict) else page
    item = next((i for i in (items or []) if (i.get("item_code") or "") == "FG01854"), None)
    if not item:
        raise StepFail("master item", "FG01854 tidak ada")

    sw = req(
        "GET",
        "/masters/color-swatch-recipes/lookup?factory_key=SL043&customer_id="
        f"{cust['id']}&buyer_code=NIKE&material_name=VIRGIN%20HYDRO%20PU"
        "&color_name=PINKSICLE%20(6FS)%20FLUORESCENT&emboss=AR-33%20M&limit=20",
        tok,
    )
    recipe = None
    if isinstance(sw, list) and sw:
        recipe = next((r for r in sw if (r.get("color_code") or "").upper() == "6FS"), sw[0])
    return {"customer": cust, "brand": brand, "item": item, "swatch": recipe}


def create_so_line(tok: str, masters: dict, *, ref: str, source: str, price_special=False):
    c, b, it = masters["customer"], masters["brand"], masters["item"]
    sw = masters.get("swatch") or {}
    header = req(
        "POST",
        "/po",
        tok,
        {
            "customer_id": c["id"],
            "customer_code": c.get("code"),
            "brand_id": b["id"],
            "buyer": "NIKE",
            "po_category": "production",
            "factory_code": "SL043",
            "order_date": TODAY,
            "etd": TODAY,
            "status": "draft",
            "po_customer_ref": ref,
            "material_group": "pu",
            "customer_name_snapshot": c.get("name"),
            "brand_name_snapshot": b.get("name") or "Nike",
        },
    )
    detail_body = {
        "master_item_id": it["id"],
        "material_name": "VIRGIN HYDRO PU",
        "thickness_text": "1.0 - 1.2",
        "thickness_min": 1.0,
        "thickness_max": 1.2,
        "color": "PINKSICLE (6FS) FLUORESCENT",
        "color_family": "fluorescent",
        "emboss": "AR-33 M",
        "quantity_order": 100,
        "model": "UAT-MATRIX-01",
        "vir_softness_type": "Vir Soft",
    }
    if source == "swatch" and sw.get("id"):
        detail_body["color_swatch_recipe_id"] = sw["id"]
        detail_body["color_standard"] = sw.get("color_standard") or "TMSL0432020012901"
        detail_body["color_reference"] = sw.get("color_code") or "6FS"
    elif source == "csi":
        detail_body["color_standard"] = "CSI"
        detail_body["color_reference"] = "PINKSICLE (6FS)"
    elif source == "waiting":
        detail_body["color_standard"] = "WAITING C/S"
        detail_body["color_reference"] = "WAITING C/S"
    if price_special:
        detail_body["unit_price"] = 1.99
        detail_body["detail_remark"] = "UAT harga spesial"
    detail = req("POST", f"/po/{header['id']}/details", tok, detail_body)
    try:
        lot = req("POST", f"/po-detail/{detail['id']}/generate-lot", tok, {})
        detail = lot
    except StepFail:
        pass
    try:
        detail = req(
            "PUT",
            f"/po-detail/{detail['id']}",
            tok,
            {"color_family": detail_body.get("color_family") or "fluorescent"},
        )
    except StepFail:
        pass
    return header, detail


def run_happy(tokens: dict, masters: dict, results: list) -> dict:
    mkt, prod, qc, wh, fin, ppic = (
        tokens["marketing"],
        tokens["production"],
        tokens["qc"],
        tokens["warehouse"],
        tokens["finance"],
        tokens["ppic"],
    )
    ref = f"UAT-SL043-{STAMP}-A"

    def a1():
        h, d = create_so_line(mkt, masters, ref=ref, source="swatch")
        price = d.get("unit_price")
        return {
            "po_id": h["id"],
            "po_number": h.get("po_number"),
            "status": h.get("status"),
            "mkt": h.get("mkt_workflow_stage"),
            "detail_id": d["id"],
            "unit_price": price,
            "swatch_id": d.get("color_swatch_recipe_id"),
            "color_standard": d.get("color_standard"),
            "lot": d.get("lot_number") or d.get("system_reference"),
        }

    a1d = step(results, "A1 buat SO draft", a1)
    po_id = a1d["po_id"]

    def a2():
        h = req("PUT", f"/po/{po_id}", mkt, {"status": "confirmed"})
        return {"status": h.get("status"), "po_number": h.get("po_number")}

    a2d = step(results, "A2 confirm SO", a2)

    def a3():
        pr = req(
            "POST",
            "/production",
            prod,
            {"po_id": po_id, "start_date": TODAY, "status": "planned"},
        )
        pd = req(
            "POST",
            f"/production/{pr['id']}/details",
            prod,
            {
                "po_detail_id": a1d["detail_id"],
                "qty_planned": 100,
                "qty_actual": 100,
                "lot_number": a1d.get("lot"),
                "status": "pending",
            },
        )
        so = req("GET", f"/po/{po_id}", mkt)
        return {
            "production_id": pr["id"],
            "production_number": pr.get("production_number"),
            "production_detail_id": pd["id"],
            "so_status": so.get("status"),
        }

    a3d = step(results, "A3 production", a3)

    def a4():
        qh = req(
            "POST",
            "/qc",
            qc,
            {
                "production_id": a3d["production_id"],
                "po_id": po_id,
                "qc_date": TODAY,
                "operator_name": "UAT",
            },
        )
        qd = req(
            "POST",
            f"/qc/{qh['id']}/details",
            qc,
            {
                "production_detail_id": a3d["production_detail_id"],
                "result": "OK",
                "is_ok": True,
                "qty_checked": 100,
            },
        )
        return {
            "qc_id": qh["id"],
            "qc_number": qh.get("qc_number"),
            "qc_detail_id": qd["id"],
            "is_ok": qd.get("is_ok"),
        }

    a4d = step(results, "A4 QC OK", a4)

    def a5():
        pk = req(
            "POST",
            "/packing",
            wh,
            {
                "production_id": a3d["production_id"],
                "qc_header_id": a4d["qc_id"],
                "status": "draft",
            },
        )
        req(
            "POST",
            f"/packing/{pk['id']}/details/batch",
            wh,
            {
                "lines": [
                    {
                        "production_detail_id": a3d["production_detail_id"],
                        "qty_packed": 100,
                    }
                ]
            },
        )
        pk = req("PUT", f"/packing/{pk['id']}", wh, {"status": "done"})
        return {
            "packing_id": pk["id"],
            "packing_number": pk.get("packing_number"),
            "status": pk.get("status"),
        }

    a5d = step(results, "A5 packing done", a5)

    def a6():
        dh = req(
            "POST",
            "/delivery-shipments/from-packing-lines",
            wh,
            {
                "packing_id": a5d["packing_id"],
                "customer_id": masters["customer"]["id"],
                "delivery_date": TODAY,
                "delivery_type": "production",
                "lines": [
                    {
                        "production_detail_id": a3d["production_detail_id"],
                        "qty": 100,
                    }
                ],
            },
        )
        dh = req("PUT", f"/delivery/{dh['id']}", wh, {"status": "sent"})
        details = req("GET", f"/delivery/{dh['id']}/details", wh)
        return {
            "delivery_id": dh["id"],
            "delivery_number": dh.get("delivery_number"),
            "status": dh.get("status"),
            "detail_count": len(details) if isinstance(details, list) else 0,
        }

    a6d = step(results, "A6 delivery sent", a6)

    def a7():
        inv = req(
            "POST",
            "/invoice",
            fin,
            {
                "delivery_id": a6d["delivery_id"],
                "customer_id": masters["customer"]["id"],
                "po_id": po_id,
                "po_number": a2d.get("po_number") or a1d.get("po_number"),
                "invoice_date": TODAY,
            },
        )
        return {
            "invoice_id": inv["id"],
            "invoice_number": inv.get("invoice_number"),
            "po_number": inv.get("po_number"),
        }

    a7d = step(results, "A7 invoice", a7)

    def a8():
        req(
            "POST",
            "/reports/po-daily-recap/confirm-print",
            mkt,
            {"po_ids": [po_id], "report_date": TODAY},
        )
        so = req("GET", f"/po/{po_id}", mkt)
        stages = [so.get("mkt_workflow_stage")]

        ppic_user = req("GET", "/auth/me", ppic)
        if not ppic_user or not ppic_user.get("id"):
            raise StepFail("A8 ppic user", "demo_ppic /auth/me gagal")
        asg = req(
            "POST",
            f"/workflow/po/{po_id}/assign-to-ppic",
            ppic,
            {"po_id": po_id, "ppic_user_id": ppic_user["id"], "notes": "UAT"},
        )
        so = req("GET", f"/po/{po_id}", mkt)
        stages.append(so.get("mkt_workflow_stage"))

        req(
            "PUT",
            f"/workflow/ppic/assignments/{asg['id']}/status",
            ppic,
            {"status": "completed", "notes": "UAT complete"},
        )
        so = req("GET", f"/po/{po_id}", mkt)
        stages.append(so.get("mkt_workflow_stage"))

        req(
            "PUT",
            f"/po/{po_id}",
            mkt,
            {"material_followup_done": True, "material_followup_remark": "UAT follow-up OK"},
        )
        try:
            req("POST", f"/po/{po_id}/mkt-workflow/advance", mkt)
        except StepFail:
            pass
        so = req("GET", f"/po/{po_id}", mkt)
        stages.append(so.get("mkt_workflow_stage"))

        req("POST", f"/packing/{a5d['packing_id']}/mark-invpl-printed", wh)
        req("POST", f"/delivery/{a6d['delivery_id']}/mark-surat-jalan-printed", wh)
        try:
            req("POST", f"/po/{po_id}/mkt-workflow/advance", mkt)
        except StepFail:
            pass
        try:
            req("POST", f"/po/{po_id}/mkt-workflow/advance", mkt)
        except StepFail:
            pass
        so = req("GET", f"/po/{po_id}", mkt)
        stages.append(so.get("mkt_workflow_stage"))

        skip = None
        try:
            req("POST", f"/po/{po_id}/mkt-workflow/advance", mkt)
        except StepFail as e:
            skip = e.detail
        so = req("GET", f"/po/{po_id}", mkt)
        return {
            "final_stage": so.get("mkt_workflow_stage"),
            "stage_trace": stages,
            "skip_after_end": skip,
        }

    a8d = step(results, "A8 marketing flow", a8)
    return {"a1": a1d, "a2": a2d, "a3": a3d, "a4": a4d, "a5": a5d, "a6": a6d, "a7": a7d, "a8": a8d}


def run_branches(tokens: dict, masters: dict, results: list) -> dict:
    mkt = tokens["marketing"]
    out = {}

    def b1():
        h, d = create_so_line(mkt, masters, ref=f"UAT-SL043-{STAMP}-B1", source="csi")
        return {
            "po_id": h["id"],
            "po_number": h.get("po_number"),
            "color_standard": d.get("color_standard"),
            "swatch_id": d.get("color_swatch_recipe_id"),
            "color_reference": d.get("color_reference"),
        }

    out["B1"] = step(results, "B1 CSI", b1)

    def b2():
        h, d = create_so_line(mkt, masters, ref=f"UAT-SL043-{STAMP}-B2", source="waiting")
        return {
            "po_id": h["id"],
            "po_number": h.get("po_number"),
            "color_standard": d.get("color_standard"),
            "color_reference": d.get("color_reference"),
        }

    out["B2"] = step(results, "B2 Waiting C/S", b2)

    def b3():
        h, d = create_so_line(mkt, masters, ref=f"UAT-SL043-{STAMP}-B3", source="swatch")
        req("PUT", f"/po/{h['id']}", mkt, {"status": "confirmed"})
        pr = req("POST", "/production", tokens["production"], {"po_id": h["id"], "start_date": TODAY})
        pd = req(
            "POST",
            f"/production/{pr['id']}/details",
            tokens["production"],
            {"po_detail_id": d["id"], "qty_planned": 100, "qty_actual": 100},
        )
        qh = req(
            "POST",
            "/qc",
            tokens["qc"],
            {"production_id": pr["id"], "po_id": h["id"], "qc_date": TODAY},
        )
        req(
            "POST",
            f"/qc/{qh['id']}/details",
            tokens["qc"],
            {
                "production_detail_id": pd["id"],
                "result": "NG",
                "is_ok": False,
                "qty_checked": 100,
                "qty_reject": 100,
                "reject_reason": "UAT NG",
            },
        )
        pk = req(
            "POST",
            "/packing",
            tokens["warehouse"],
            {"production_id": pr["id"], "qc_header_id": qh["id"], "status": "draft"},
        )
        blocked = None
        try:
            req(
                "POST",
                f"/packing/{pk['id']}/details/batch",
                tokens["warehouse"],
                {"lines": [{"production_detail_id": pd["id"], "qty_packed": 100}]},
            )
            blocked = "UNEXPECTED_OK"
        except StepFail as e:
            blocked = e.detail
        return {
            "po_id": h["id"],
            "po_number": h.get("po_number"),
            "qc_id": qh["id"],
            "packing_blocked": blocked,
        }

    out["B3"] = step(results, "B3 QC NG blokir packing", b3)
    return out


def write_report(payload: dict, path: Path) -> None:
    lines = [
        "# Hasil UAT SO sampai selesai",
        "",
        f"Waktu: {payload.get('ran_at')}",
        f"Paket: SL043 · Nike · FG01854 · PINKSICLE 6FS · harga target 1.38",
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
                "production_number",
                "qc_number",
                "packing_number",
                "delivery_number",
                "invoice_number",
                "final_stage",
                "color_standard",
            )
            bits = [f"{k}={r['data'][k]}" for k in keys if r["data"].get(k) not in (None, "")]
            note = "; ".join(bits)
        elif not r.get("ok"):
            note = json.dumps(r.get("error"), ensure_ascii=False)[:240]
        lines.append(f"| {r['step']} | {mark} | {note} |")
    lines += ["", "## Dokumen happy path", "", "```json", json.dumps(payload.get("happy") or {}, ensure_ascii=False, indent=2), "```", ""]
    lines += ["## Cabang B", "", "```json", json.dumps(payload.get("branches") or {}, ensure_ascii=False, indent=2), "```", ""]
    if payload.get("stop_reason"):
        lines += ["## Berhenti", "", "```json", json.dumps(payload["stop_reason"], ensure_ascii=False, indent=2), "```", ""]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    results: list = []
    payload = {"ran_at": datetime.now().isoformat(timespec="seconds"), "steps": results}
    try:
        tokens = {}
        for role, user, pwd in (
            ("marketing", "demo_marketing", PWD_DEMO),
            ("production", "demo_production", PWD_DEMO),
            ("qc", "demo_qc", PWD_DEMO),
            ("warehouse", "demo_warehouse", PWD_DEMO),
            ("finance", "demo_finance", PWD_DEMO),
            ("ppic", "demo_ppic", PWD_DEMO),
        ):
            tokens[role] = step(results, f"login {user}", lambda u=user, p=pwd: login(u, p))
        results.append({"step": "login semua role", "ok": True, "data": list(tokens)})
        masters = step(results, "muat master SL043/FG01854/swatch", lambda: load_masters(tokens["marketing"]))
        payload["happy"] = run_happy(tokens, masters, results)
        payload["branches"] = run_branches(tokens, masters, results)
    except StepFail as e:
        payload["stopped"] = True
        payload["stop_reason"] = {e.step: e.detail}
    except Exception as e:
        payload["stopped"] = True
        payload["stop_reason"] = str(e)
        results.append({"step": "crash", "ok": False, "error": str(e)})
    out = Path("/home/developer/project/dokumentasi/uat-so-sl043-hasil.md")
    write_report(payload, out)
    print(json.dumps({"ok": all(r.get("ok") for r in results), "report": str(out), "steps": [(r["step"], r["ok"]) for r in results]}, ensure_ascii=False, indent=2))
    return 0 if all(r.get("ok") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
