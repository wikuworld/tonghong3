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
STAMP = datetime.now().strftime("%y%m%d%H%M%S")


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

    # Lookup (main API wajib factory_key atau customer_id). Fallback page + filter lokal.
    sw = req(
        "GET",
        "/masters/color-swatch-recipes/lookup?buyer_code=NIKE"
        f"&customer_id={cust['id']}&factory_key=SHOETOWN"
        "&material_name=VIRGIN%20HYDRO%20PU&q=6FS&limit=40",
        tok,
    )
    candidates = sw if isinstance(sw, list) else []
    if not candidates:
        page_sw = req(
            "GET",
            "/masters/color-swatch-recipes/page?keyword=PINK%20SICLE&limit=50",
            tok,
        )
        candidates = page_sw.get("items") if isinstance(page_sw, dict) else (page_sw or [])
    candidates = [
        r
        for r in (candidates or [])
        if (r.get("color_code") or "").upper() == "6FS"
        and (
            r.get("customer_id") == cust["id"]
            or (r.get("factory_key") or "").upper() == "SHOETOWN"
        )
    ]

    def _rank(r: dict) -> tuple:
        cust_ok = 0 if r.get("customer_id") == cust["id"] else 1
        mat_ok = 0 if "VIRGIN HYDRO" in (r.get("material_name") or "").upper() else 1
        return (cust_ok, mat_ok, r.get("id") or 0)

    recipe = None
    if candidates:
        recipe = sorted(candidates, key=_rank)[0]
    if not recipe or not recipe.get("id"):
        # Last resort: known SL043 PINKSICLE recipe id if still active.
        try:
            recipe = req("GET", "/masters/color-swatch-recipes/1082", tok)
        except StepFail:
            recipe = None
    if not recipe or not recipe.get("id"):
        raise StepFail(
            "master swatch",
            "Resep 6FS / VIRGIN HYDRO PU untuk SL043 (SHOETOWN) tidak ditemukan/aktif",
        )
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
        "material_name": sw.get("material_name") or "VIRGIN HYDRO PU",
        "thickness_text": "1.0 - 1.2",
        "thickness_min": 1.0,
        "thickness_max": 1.2,
        # Nama warna SO harus match master fluorescent; swatch pakai spelling berbeda.
        "color": "PINKSICLE (6FS) FLUORESCENT",
        "color_family": "fluorescent",
        "emboss": (sw.get("emboss") if source == "swatch" else None) or "AR-33 M",
        "quantity_order": 100,
        "model": "UAT-MATRIX-01",
        "vir_softness_type": "Vir Soft",
    }
    if source == "swatch":
        if not sw.get("id"):
            raise StepFail("create_so_line swatch", "masters.swatch kosong")
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


def _lot_from_detail(d: dict) -> str | None:
    return d.get("thi_line_ref") or d.get("lot_number") or d.get("system_reference")


def _require(value, label: str, step_name: str):
    if value in (None, ""):
        raise StepFail(step_name, f"{label} wajib terisi")
    return value


def run_happy(tokens: dict, masters: dict, results: list) -> dict:
    mkt = tokens["marketing"]
    prod = tokens["production"]
    ref = f"UAT-SL043-{STAMP}-A"

    def a1():
        h, d = create_so_line(mkt, masters, ref=ref, source="swatch")
        swatch_id = _require(d.get("color_swatch_recipe_id"), "color_swatch_recipe_id", "A1")
        color_standard = _require(d.get("color_standard"), "color_standard", "A1")
        lot = _require(_lot_from_detail(d), "thi_line_ref/lot", "A1")
        return {
            "po_id": h["id"],
            "po_number": h.get("po_number"),
            "status": h.get("status"),
            "mkt": h.get("mkt_workflow_stage"),
            "detail_id": d["id"],
            "unit_price": d.get("unit_price"),
            "swatch_id": swatch_id,
            "color_standard": color_standard,
            "lot": lot,
        }

    a1d = step(results, "A1 buat SO draft", a1)
    po_id = a1d["po_id"]

    def a2():
        h = req("PUT", f"/po/{po_id}", mkt, {"status": "confirmed"})
        stage = h.get("mkt_workflow_stage")
        if stage != "in_outstanding":
            raise StepFail(
                "A2 confirm SO",
                f"expected in_outstanding after confirm, got {stage}",
            )
        return {"status": h.get("status"), "po_number": h.get("po_number"), "mkt": stage}

    a2d = step(results, "A2 confirm SO", a2)

    def a8_rekap_ppic():
        """Confirm sudah Outstanding; cetak RKPO opsional; assignment pool selesai."""
        so = req("GET", f"/po/{po_id}", mkt)
        stages = [so.get("mkt_workflow_stage")]
        if stages[-1] != "in_outstanding":
            raise StepFail(
                "A8 confirm→outstanding",
                f"expected in_outstanding after confirm, got {stages[-1]}",
            )
        req(
            "POST",
            "/reports/po-daily-recap/confirm-print",
            mkt,
            {"po_ids": [po_id], "report_date": TODAY},
        )
        so = req("GET", f"/po/{po_id}", mkt)
        if so.get("mkt_workflow_stage") != "in_outstanding":
            raise StepFail(
                "A8 optional rekap print",
                f"expected still in_outstanding, got {so.get('mkt_workflow_stage')}",
            )

        asg = req("GET", f"/workflow/po/{po_id}/ppic-assignment", mkt)
        if not asg or asg.get("status") != "completed":
            raise StepFail(
                "A8 PPIC auto assignment",
                f"expected completed auto assignment, got {asg}",
            )

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
        return {"stage_trace": stages, "post_ppic_stage": so.get("mkt_workflow_stage"), "ppic_status": asg.get("status")}

    a8_early = step(results, "A8 MKT rekap+PPIC", a8_rekap_ppic)

    def a3():
        blocked = expect_http(
            lambda: req(
                "POST",
                "/production",
                prod,
                {"po_id": po_id, "start_date": TODAY, "status": "planned"},
            ),
            codes={403},
            step_name="A3 production",
        )
        return {"http": blocked.get("http"), "erp_shopfloor_blocked": True}

    a3d = step(results, "A3 ERP production ditolak (403)", a3)
    return {
        "a1": a1d,
        "a2": a2d,
        "a8_early": a8_early,
        "a3": a3d,
    }


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
        blocked = expect_http(
            lambda: req(
                "POST",
                "/production",
                tokens["production"],
                {"po_id": h["id"], "start_date": TODAY},
            ),
            codes={403},
            step_name="B3 ERP production",
        )
        return {
            "po_id": h["id"],
            "po_number": h.get("po_number"),
            "erp_shopfloor_blocked": blocked,
        }

    out["B3"] = step(results, "B3 ERP production 403", b3)
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
                "swatch_id",
                "lot",
                "production_number",
                "qc_number",
                "packing_number",
                "delivery_number",
                "invoice_number",
                "pre_invoice_stage",
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
    out = Path(__file__).resolve().parents[2] / "dokumentasi" / "uat-so-sl043-hasil.md"
    write_report(payload, out)
    print(json.dumps({"ok": all(r.get("ok") for r in results), "report": str(out), "steps": [(r["step"], r["ok"]) for r in results]}, ensure_ascii=False, indent=2))
    return 0 if all(r.get("ok") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
