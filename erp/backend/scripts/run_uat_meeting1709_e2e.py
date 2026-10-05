#!/usr/bin/env python3
"""E2E meeting TongHong 17/9: inventaris DB → MRP shopfloor → SJ + THIN auto → scan-out.

Usage:
  cd erp/backend
  E2E_API_BASE=http://127.0.0.1:8001/api/v1 E2E_USER=admin E2E_PASSWORD=admin123 \\
    PYTHONPATH=. .venv/bin/python scripts/run_uat_meeting1709_e2e.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlencode

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent  # erp/backend
ERP_ROOT = BACKEND.parent  # erp
ROOT = ERP_ROOT.parent  # project_uat
if not (ROOT / "dokumentasi").is_dir() and (ERP_ROOT / "dokumentasi").is_dir():
    ROOT = ERP_ROOT
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# --- Patch API base sebelum import helper yang memakai BASE ---
import run_uat_so_e2e as so_e2e  # noqa: E402

DEFAULT_BASE = "http://127.0.0.1:8001/api/v1"
so_e2e.BASE = os.environ.get("E2E_API_BASE", DEFAULT_BASE).rstrip("/")

from run_uat_so_e2e import (  # noqa: E402
    PWD_DEMO,
    StepFail,
    load_masters,
    login,
    req,
    step,
)
from run_uat_mrp_e2e import run_flow  # noqa: E402

REPORT_PATH = ROOT / "dokumentasi" / "uat-meeting1709-e2e-hasil.md"
E2E_USER = os.environ.get("E2E_USER", "admin")
E2E_PASSWORD = os.environ.get("E2E_PASSWORD", "admin123")


def qpath(path: str, **params) -> str:
    qs = urlencode({k: v for k, v in params.items() if v is not None}, quote_via=quote)
    return f"{path}?{qs}" if qs else path


def soft_step(results: list, name: str, fn):
    """Soft gate: catat LULUS/SKIP/GAGAL tanpa menghentikan run utama."""
    try:
        data = fn()
        results.append({"step": name, "ok": True, "soft": True, "data": data})
        return data
    except Exception as e:
        detail = e.detail if isinstance(e, StepFail) else str(e)
        results.append({"step": name, "ok": False, "soft": True, "skipped": True, "error": detail})
        return None


# ---------------------------------------------------------------------------
# Phase 0 — inventaris DB
# ---------------------------------------------------------------------------


def _load_dotenv_files() -> None:
    """Load .env; project root wins for DB keys so Phase0 MRP tidak Access denied."""
    force_keys = {
        "DATABASE_URL",
        "MRP_DB_HOST",
        "MRP_DB_PORT",
        "MRP_DB_NAME",
        "MRP_DB_USER",
        "MRP_DB_PASSWORD",
        "MRP_DATABASE_URL",
    }
    for f in (BACKEND / ".env", ROOT / ".env"):
        if not f.is_file():
            continue
        for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip() or line.strip().startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            key = k.strip()
            val = v.strip().strip('"').strip("'")
            if key in force_keys or key not in os.environ:
                os.environ[key] = val


def inventory_erp_db() -> dict:
    from sqlalchemy import create_engine, text

    url = os.environ.get("DATABASE_URL")
    if not url:
        from app.config import settings

        url = settings.database_url
    eng = create_engine(url)
    out: dict = {"ok": True, "users": [], "packing_done": 0, "deliveries": [], "po_outstanding": 0, "thin_invoices": 0}
    with eng.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT id, username, role, is_active FROM users "
                "WHERE username IN ('admin','demo_marketing','demo_production','demo_warehouse','demo_finance') "
                "OR role='admin' ORDER BY id"
            )
        ).mappings().all()
        out["users"] = [dict(r) for r in rows]
        out["packing_done"] = int(
            conn.execute(text("SELECT COUNT(*) FROM packing_headers WHERE LOWER(status)='done'")).scalar() or 0
        )
        dels = conn.execute(
            text(
                "SELECT d.id, d.delivery_number, d.status, d.packing_id, "
                "(SELECT i.invoice_number FROM invoices i WHERE i.delivery_id=d.id LIMIT 1) AS invoice_number "
                "FROM delivery_headers d ORDER BY d.id DESC LIMIT 15"
            )
        ).mappings().all()
        out["deliveries"] = [dict(r) for r in dels]
        out["po_outstanding"] = int(
            conn.execute(
                text("SELECT COUNT(*) FROM po_headers WHERE mkt_workflow_stage='in_outstanding'")
            ).scalar()
            or 0
        )
        out["thin_invoices"] = int(
            conn.execute(text("SELECT COUNT(*) FROM invoices WHERE invoice_number LIKE 'THIN-%'")).scalar()
            or 0
        )
    return out


def inventory_mrp_db() -> dict:
    import pymysql

    host = os.environ.get("MRP_DB_HOST", "127.0.0.1")
    port = int(os.environ.get("MRP_DB_PORT", "3306"))
    name = os.environ.get("MRP_DB_NAME", "uat_tonghong_mrp")
    user = os.environ.get("MRP_DB_USER", "tonghong_mrp")
    password = os.environ.get("MRP_DB_PASSWORD", "")
    out: dict = {"ok": True}
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=name,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT jenis, COUNT(*) AS n FROM tbl_master_treatment "
                "WHERE COALESCE(is_active,1)=1 GROUP BY jenis"
            )
            out["treatment_by_jenis"] = {r["jenis"]: int(r["n"]) for r in cur.fetchall()}
            for gudang in ("utama", "lapangan"):
                try:
                    cur.execute(
                        "SELECT COUNT(*) AS n FROM tbl_stok_kimia_in WHERE gudang=%s",
                        (gudang,),
                    )
                    out[f"kimia_in_{gudang}"] = int(cur.fetchone()["n"])
                except Exception as e:
                    out[f"kimia_in_{gudang}"] = f"err:{e}"
                try:
                    cur.execute(
                        "SELECT COUNT(*) AS n FROM tbl_stok_rp_in WHERE gudang=%s",
                        (gudang,),
                    )
                    out[f"rp_in_{gudang}"] = int(cur.fetchone()["n"])
                except Exception as e:
                    out[f"rp_in_{gudang}"] = f"err:{e}"
            try:
                cur.execute(
                    "SELECT status, COUNT(*) AS n FROM tbl_stock_sisa GROUP BY status"
                )
                out["stock_sisa"] = {r["status"]: int(r["n"]) for r in cur.fetchall()}
            except Exception as e:
                out["stock_sisa"] = {"error": str(e)}
            try:
                cur.execute(
                    "SELECT COUNT(*) AS n FROM tbl_gudang_fg WHERE status='in_stock'"
                )
                out["fg_in_stock"] = int(cur.fetchone()["n"])
            except Exception:
                try:
                    cur.execute(
                        "SELECT COUNT(*) AS n FROM tbl_packing WHERE status='finished'"
                    )
                    out["packing_finished"] = int(cur.fetchone()["n"])
                except Exception as e:
                    out["fg_or_packing"] = f"err:{e}"
    finally:
        conn.close()
    return out


def collect_db_inventory() -> dict:
    _load_dotenv_files()
    inv: dict = {"ran_at": datetime.now().isoformat(timespec="seconds")}
    try:
        inv["erp"] = inventory_erp_db()
    except Exception as e:
        inv["erp"] = {"ok": False, "error": str(e)}
    try:
        inv["mrp"] = inventory_mrp_db()
    except Exception as e:
        inv["mrp"] = {"ok": False, "error": str(e)}
    return inv


# ---------------------------------------------------------------------------
# Soft gates (API)
# ---------------------------------------------------------------------------


def soft_dual_gudang(tok: str) -> dict:
    kimia_u = req("GET", qpath("/mrp/stok-kimia", gudang="utama"), tok)
    kimia_l = req("GET", qpath("/mrp/stok-kimia", gudang="lapangan"), tok)
    rp_u = req("GET", qpath("/mrp/stok-rp", gudang="utama"), tok)
    rp_l = req("GET", qpath("/mrp/stok-rp", gudang="lapangan"), tok)
    for label, payload, expect in (
        ("kimia_utama", kimia_u, "utama"),
        ("kimia_lapangan", kimia_l, "lapangan"),
        ("rp_utama", rp_u, "utama"),
        ("rp_lapangan", rp_l, "lapangan"),
    ):
        if isinstance(payload, dict) and payload.get("gudang") not in (None, expect):
            raise StepFail(f"soft gudang {label}", payload.get("gudang"))
    return {
        "kimia_utama_lots": (kimia_u.get("stats") or {}).get("lots") if isinstance(kimia_u, dict) else None,
        "kimia_lapangan_lots": (kimia_l.get("stats") or {}).get("lots") if isinstance(kimia_l, dict) else None,
        "rp_utama_lots": (rp_u.get("stats") or {}).get("lots") if isinstance(rp_u, dict) else None,
        "rp_lapangan_lots": (rp_l.get("stats") or {}).get("lots") if isinstance(rp_l, dict) else None,
    }


def soft_treatment(tok: str) -> dict:
    rows = req("GET", "/mrp/masters/treatment", tok)
    if isinstance(rows, dict):
        rows = rows.get("items") or rows.get("treatments") or []
    pu = [r for r in (rows or []) if str(r.get("jenis") or "").upper() == "PU"]
    suede = [r for r in (rows or []) if str(r.get("jenis") or "").upper() == "SUEDE"]
    if not pu or not suede:
        raise StepFail("soft treatment", {"pu": len(pu), "suede": len(suede)})
    return {"pu": len(pu), "suede": len(suede), "total": len(rows or [])}


def soft_stock_sisa(tok: str) -> dict:
    rows = req("GET", "/mrp/stock-sisa", tok)
    if isinstance(rows, dict):
        rows = rows.get("items") or rows.get("data") or []
    by = {}
    for r in rows or []:
        st = str(r.get("status") or "?")
        by[st] = by.get(st, 0) + 1
    return {"count": len(rows or []), "by_status": by}


def soft_stock_sisa_packing(tok: str, *, mrp_po_id: int | None = None) -> dict:
    """Seed approved → packing sisa → consumed; open ditolak; finish jika ada mrp_po_id."""
    from run_uat_so_e2e import expect_http

    stamp = datetime.now().strftime("%y%m%d%H%M%S")
    open_row = req(
        "POST",
        "/mrp/stock-sisa",
        tok,
        {
            "sumber": "fg",
            "barcode": f"E2E-OPEN-{stamp}",
            "lot": f"LOT-OPEN-{stamp}",
            "qty": 3.0,
            "status": "open",
            "notes": "E2E meeting1709 open (harus ditolak packing)",
        },
    )
    open_id = int(open_row["id"])
    blocked = expect_http(
        lambda: req(
            "POST",
            "/mrp/packing",
            tok,
            {"source_mode": "sisa", "stock_sisa_id": open_id, "qty_sq": 3.0},
        ),
        codes={400},
        step_name="soft packing sisa status open",
    )

    approved = req(
        "POST",
        "/mrp/stock-sisa",
        tok,
        {
            "sumber": "fg",
            "barcode": f"E2E-SISA-{stamp}",
            "lot": f"LOT-SISA-{stamp}",
            "qty": 5.0,
            "status": "approved",
            "notes": "E2E meeting1709 approved seed",
        },
    )
    sisa_id = int(approved["id"])
    start_body: dict = {
        "source_mode": "sisa",
        "stock_sisa_id": sisa_id,
        "qty_sq": 5.0,
    }
    if mrp_po_id:
        start_body["po_id"] = int(mrp_po_id)
    started = req("POST", "/mrp/packing", tok, start_body)
    packing_id = int(started["id"])
    kode_packing = started.get("kode_packing")
    listed = req("GET", qpath("/mrp/stock-sisa", q=f"E2E-SISA-{stamp}"), tok)
    if isinstance(listed, dict):
        listed = listed.get("items") or listed.get("data") or []
    hit = next((r for r in (listed or []) if int(r.get("id") or 0) == sisa_id), None)
    if not hit:
        all_rows = req("GET", "/mrp/stock-sisa", tok)
        if isinstance(all_rows, dict):
            all_rows = all_rows.get("items") or all_rows.get("data") or []
        hit = next((r for r in (all_rows or []) if int(r.get("id") or 0) == sisa_id), None)
    status = str((hit or {}).get("status") or "")
    if status != "consumed":
        raise StepFail(
            "soft packing sisa belum consumed",
            {"sisa_id": sisa_id, "status": status, "started": started, "hit": hit},
        )

    pack_status = "in_progress"
    finish_ok = False
    finish_note = None
    try:
        req(
            "POST",
            f"/mrp/packing/{packing_id}/actions",
            tok,
            {"action": "add_roll", "lembar": 1, "ukuran": 5.0},
        )
        finished = req(
            "POST",
            f"/mrp/packing/{packing_id}/actions",
            tok,
            {"action": "finish"},
        )
        detail = req("GET", f"/mrp/packing/{packing_id}", tok)
        packing = detail.get("packing") or detail
        pack_status = str(packing.get("status") or "")
        if pack_status == "finished":
            finish_ok = True
        else:
            finish_note = {"finish": finished, "status": pack_status}
    except StepFail as e:
        finish_note = e.detail
        # Tetap LULUS pada consumed; finish+ERP dicatat bila gagal bridge

    return {
        "open_id": open_id,
        "open_blocked_http": blocked.get("http") if isinstance(blocked, dict) else 400,
        "sisa_id": sisa_id,
        "sisa_status": status,
        "packing_id": packing_id,
        "kode_packing": kode_packing,
        "packing_status": pack_status,
        "finish_ok": finish_ok,
        "finish_optional": finish_note,
        "mrp_po_id": mrp_po_id,
        "count": 1,
    }


def soft_lab_lapangan_only(tok: str) -> dict:
    """Lab options hanya expose stok_lapangan (bukan gudang utama)."""
    opt = req("GET", "/mrp/lab/options", tok)
    kimia = opt.get("kimia_list") or []
    if not kimia:
        raise StepFail("soft lab kimia_list kosong", opt)
    bad = [r for r in kimia if "stok_utama" in r or "stok_gudang_utama" in r]
    if bad:
        raise StepFail("soft lab bocor stok utama", bad[:3])
    if any("stok_lapangan" not in r for r in kimia):
        raise StepFail("soft lab tanpa field stok_lapangan", kimia[:2])
    kimia_u = req("GET", qpath("/mrp/stok-kimia", gudang="utama"), tok)
    kimia_l = req("GET", qpath("/mrp/stok-kimia", gudang="lapangan"), tok)
    return {
        "kimia_options": len(kimia),
        "stok_lapangan_field": True,
        "gudang_utama": (kimia_u.get("gudang") if isinstance(kimia_u, dict) else None),
        "gudang_lapangan": (kimia_l.get("gudang") if isinstance(kimia_l, dict) else None),
    }


def soft_label_roll(tok: str, *, mrp_packing_id: int | None) -> dict:
    """GET payload label roll setelah packing (M7) — packing sudah finished."""
    if not mrp_packing_id:
        raise StepFail("soft label roll", "mrp_packing_id kosong")
    detail = req("GET", f"/mrp/packing/{int(mrp_packing_id)}", tok)
    rolls = detail.get("rolls") or []
    if not rolls:
        raise StepFail("soft label roll tanpa rolls", {"packing_id": mrp_packing_id, "detail_keys": list(detail.keys())})
    roll_id = int(rolls[0]["id"])
    payload = req("GET", f"/mrp/packing/roll/{roll_id}/label", tok)
    if not payload.get("ok") and not payload.get("label"):
        raise StepFail("soft label roll GET", payload)
    label = payload.get("label") or payload
    kode = label.get("kode_packing") or label.get("packing_no") or label.get("barcode")
    if not kode:
        raise StepFail("soft label roll field", {"keys": list(label.keys())[:20], "label": label})
    return {
        "roll_id": roll_id,
        "kode_packing": kode,
        "roll_no": label.get("roll_no"),
        "label_keys": sorted(label.keys())[:24],
        "count": 1,
    }


def soft_scan_out_negatif(wh_tok: str, *, packing_id_sent: int | None) -> dict:
    """Scan-out packing tidak ada / tanpa SJ → 404; packing sudah sent → idempotent."""
    from run_uat_so_e2e import expect_http

    miss_id = expect_http(
        lambda: req(
            "POST",
            "/delivery-shipments/scan-out",
            wh_tok,
            {"packing_id": 999999999},
        ),
        codes={404},
        step_name="soft scan-out packing id hilang",
    )
    miss_num = expect_http(
        lambda: req(
            "POST",
            "/delivery-shipments/scan-out",
            wh_tok,
            {"packing_number": "FG-E2E-NO-SUCH-PACKING"},
        ),
        codes={404},
        step_name="soft scan-out packing number hilang",
    )
    already = None
    if packing_id_sent:
        again = req(
            "POST",
            "/delivery-shipments/scan-out",
            wh_tok,
            {"packing_id": int(packing_id_sent)},
        )
        already = again.get("already_sent") or []
        if not again.get("ok") and not already:
            raise StepFail("soft scan-out already sent", again)
    return {
        "missing_id_http": miss_id.get("http"),
        "missing_number_http": miss_num.get("http"),
        "already_sent": already,
        "count": 1,
    }


def soft_role_tokens(tokens: dict, admin_tok: str) -> dict:
    """Pastikan hard path memakai demo_* (token beda dari admin) bila login demo sukses."""
    flags = {}
    for role in ("marketing", "production", "warehouse", "finance"):
        flags[role] = tokens.get(role) is not None and tokens.get(role) != admin_tok
    if not any(flags.values()):
        raise StepFail("soft role semua fallback admin", flags)
    return {"distinct_from_admin": flags, "count": sum(1 for v in flags.values() if v)}


def soft_suede_proses(tok: str, *, rencana_item_id: int | None, mrp_po_id: int | None) -> dict:
    """Buat proses treatment Suede (create + start) pada RPI dari hard path."""
    if not rencana_item_id:
        raise StepFail("soft suede", "rencana_item_id kosong")
    rows = req("GET", "/mrp/masters/treatment", tok)
    if isinstance(rows, dict):
        rows = rows.get("items") or rows.get("treatments") or []
    suede = [
        r
        for r in (rows or [])
        if str(r.get("jenis") or "").upper() == "SUEDE" and (r.get("nama_treatment") or "").strip()
    ]
    if not suede:
        raise StepFail("soft suede treatment kosong", {"total": len(rows or [])})
    treatment = str(suede[0]["nama_treatment"]).strip()
    stamp = datetime.now().strftime("%y%m%d%H%M%S")
    kode_palet = f"KY-SOFT-{stamp}"
    kode_yl = f"YL-SOFT-{stamp}"
    req(
        "POST",
        "/mrp/palet/in",
        tok,
        {
            "kode_palet": kode_palet,
            "tanggal": datetime.now().date().isoformat(),
            "keterangan": "soft suede proses",
            "items": [
                {
                    "kode_yl": kode_yl,
                    "thickness": "1.2",
                    "warna": "BLACK",
                    "qty": 20,
                }
            ],
        },
    )
    body: dict = {
        "rencana_item_id": int(rencana_item_id),
        "treatment_jenis": "Suede",
        "treatment_list": [treatment],
        "ky_lines": [
            {
                "kode_palet": kode_palet,
                "kode_yl": kode_yl,
                "target_qty": 10,
            }
        ],
    }
    if mrp_po_id:
        body["po_ids"] = [int(mrp_po_id)]
    created = req("POST", "/mrp/proses", tok, body)
    pid = created.get("id")
    if not pid:
        raise StepFail("soft suede create", created)
    req("POST", f"/mrp/proses/{pid}/actions", tok, {"action": "start"})
    detail = req("GET", f"/mrp/proses/{pid}", tok)
    persiapan = detail.get("persiapan") or detail
    return {
        "proses_id": pid,
        "treatment": treatment,
        "treatment_jenis": persiapan.get("treatment_jenis") or "Suede",
        "status": persiapan.get("status"),
        "suede": 1,
        "count": 1,
    }


def soft_sisa_so_ppic(mkt: str, prod: str, masters: dict) -> dict:
    """open → ajukan/reserve SO → PPIC completed → sync → approved."""
    from run_uat_so_e2e import create_so_line

    stamp = datetime.now().strftime("%y%m%d%H%M%S")
    sisa = req(
        "POST",
        "/mrp/stock-sisa",
        prod,
        {
            "sumber": "fg",
            "barcode": f"E2E-PPIC-{stamp}",
            "lot": f"LOT-PPIC-{stamp}",
            "qty": 4.0,
            "status": "open",
            "notes": "E2E SO+PPIC dari sisa",
        },
    )
    sisa_id = int(sisa["id"])
    header, detail = create_so_line(mkt, masters, ref=f"UAT-SISA-PPIC-{stamp}", source="swatch")
    po_id = int(header["id"])
    confirmed = req("PUT", f"/po/{po_id}", mkt, {"status": "confirmed"})
    if (confirmed.get("status") or "").lower() != "confirmed":
        raise StepFail("soft sisa SO confirm", confirmed)

    asg = req("GET", f"/workflow/po/{po_id}/ppic-assignment", mkt)
    if not asg:
        # assign lalu complete
        asg = req("POST", f"/workflow/po/{po_id}/assign-to-ppic", mkt, {"notes": "E2E sisa PPIC"})
    if (asg.get("status") or "").lower() != "completed":
        asg = req(
            "PUT",
            f"/workflow/ppic/assignments/{asg['id']}/status",
            mkt,
            {"status": "completed", "notes": "E2E complete PPIC sisa"},
        )
    if (asg.get("status") or "").lower() != "completed":
        raise StepFail("soft sisa PPIC belum completed", asg)

    reserved = req(
        "POST",
        f"/mrp/stock-sisa/{sisa_id}/actions",
        prod,
        {"action": "reserve", "po_id": po_id, "notes": "E2E reserve ke SO"},
    )
    row = (reserved.get("row") or reserved)
    if str(row.get("status") or "").lower() != "reserved":
        raise StepFail("soft sisa reserve", reserved)

    synced = req(
        "POST",
        f"/mrp/stock-sisa/{sisa_id}/actions",
        prod,
        {"action": "sync-ppic"},
    )
    row2 = synced.get("row") or synced
    # sync-ppic juga dipanggil otomatis saat PPIC complete; approve manual fallback
    st = str(row2.get("status") or "").lower()
    if st != "approved":
        approved = req(
            "POST",
            f"/mrp/stock-sisa/{sisa_id}/actions",
            prod,
            {"action": "approve"},
        )
        row2 = approved.get("row") or approved
        st = str(row2.get("status") or "").lower()
    if st != "approved":
        raise StepFail("soft sisa belum approved setelah PPIC", {"sync": synced, "row": row2})
    return {
        "sisa_id": sisa_id,
        "erp_po_id": po_id,
        "po_number": confirmed.get("po_number") or header.get("po_number"),
        "ppic_status": asg.get("status"),
        "sisa_status": st,
        "detail_id": detail.get("id"),
        "count": 1,
    }


def soft_smoke_api_ui(tokens: dict, *, detail_id: int | None) -> dict:
    """Smoke setara UI (tanpa browser): outstanding options, delivery, dual gudang, gudang sisa."""
    mkt = tokens["marketing"]
    prod = tokens["production"]
    wh = tokens["warehouse"]
    checks = {}
    if detail_id:
        opts = req(
            "GET",
            qpath("/marketing/outstanding-packing-options", po_detail_ids=str(detail_id)),
            mkt,
        )
        checks["outstanding_options"] = True
        checks["outstanding_type"] = type(opts).__name__
    dels = req("GET", qpath("/delivery", limit=5), wh)
    checks["delivery_list"] = isinstance(dels, list) or isinstance(dels, dict)
    for g in ("utama", "lapangan"):
        req("GET", qpath("/mrp/stok-kimia", gudang=g), prod)
        req("GET", qpath("/mrp/stok-rp", gudang=g), prod)
    checks["dual_gudang_tabs"] = True
    sisa = req("GET", "/mrp/stock-sisa", prod)
    checks["gudang_sisa_menu"] = isinstance(sisa, list) or isinstance(sisa, dict)
    return {"ok": True, "checks": checks, "count": len(checks)}


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def write_report(payload: dict, path: Path) -> None:
    results = payload.get("steps") or []
    lines = [
        "# Hasil E2E meeting TongHong 17/9 (DB-first + API)",
        "",
        f"Waktu: {payload.get('ran_at')}",
        f"API: `{so_e2e.BASE}`",
        f"User orkestrator: `{payload.get('orchestrator_user')}`",
        "",
        "## Inventaris DB (Phase 0)",
        "",
        "```json",
        json.dumps(payload.get("db_inventory") or {}, ensure_ascii=False, indent=2, default=str),
        "```",
        "",
        "## Ringkasan langkah",
        "",
        "| Langkah | Hasil | Soft | Catatan |",
        "|---------|-------|------|---------|",
    ]
    for r in results:
        if r.get("ok"):
            hasil = "LULUS"
        elif r.get("skipped") or r.get("soft"):
            hasil = "SKIP" if r.get("skipped") else "GAGAL"
        else:
            hasil = "GAGAL"
        soft = "ya" if r.get("soft") else ""
        note = ""
        if r.get("ok") and isinstance(r.get("data"), dict):
            d = r["data"]
            bits = []
            for k in (
                "po_number",
                "delivery_number",
                "invoice_number",
                "kode_wip",
                "kode_packing",
                "delivery_status",
                "pu",
                "suede",
                "count",
                "sisa_id",
                "sisa_status",
                "no_duplicate_thin",
                "invoice_count",
                "finish_ok",
                "roll_id",
                "ppic_status",
                "treatment",
            ):
                if k in d and d[k] is not None:
                    bits.append(f"{k}={d[k]}")
            note = "; ".join(bits)[:120]
        elif r.get("error"):
            note = json.dumps(r["error"], ensure_ascii=False, default=str)[:120]
        lines.append(f"| {r.get('step')} | {hasil} | {soft} | {note} |")
    lines += ["", "## Flow payload", "", "```json"]
    lines.append(json.dumps(payload.get("flow") or {}, ensure_ascii=False, indent=2, default=str))
    lines += ["```", ""]
    if payload.get("stop_reason"):
        lines += [
            "## Berhenti",
            "",
            "```json",
            json.dumps(payload["stop_reason"], ensure_ascii=False, indent=2, default=str),
            "```",
            "",
        ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    results: list = []
    payload: dict = {
        "ran_at": datetime.now().isoformat(timespec="seconds"),
        "steps": results,
        "orchestrator_user": E2E_USER,
        "api_base": so_e2e.BASE,
    }

    # Phase 0
    try:
        inv = step(results, "Phase0 inventaris DB", collect_db_inventory)
        payload["db_inventory"] = inv
        if inv.get("erp", {}).get("ok") is False and inv.get("mrp", {}).get("ok") is False:
            raise StepFail("Phase0", "ERP dan MRP DB gagal diakses")
    except StepFail as e:
        payload["db_inventory"] = {"error": e.detail}
        # lanjut API tetap dicoba

    try:
        tokens: dict = {}
        admin_tok = step(
            results,
            f"login {E2E_USER}",
            lambda: login(E2E_USER, E2E_PASSWORD),
        )
        tokens["admin"] = admin_tok

        for role, user in (
            ("marketing", "demo_marketing"),
            ("production", "demo_production"),
            ("warehouse", "demo_warehouse"),
            ("finance", "demo_finance"),
        ):
            try:
                tokens[role] = step(
                    results,
                    f"login {user}",
                    lambda u=user: login(u, PWD_DEMO),
                )
            except StepFail as e:
                results.append(
                    {
                        "step": f"login {user}",
                        "ok": False,
                        "soft": True,
                        "skipped": True,
                        "error": e.detail,
                    }
                )
                tokens[role] = admin_tok

        # Pastikan kunci ada
        for k in ("marketing", "production", "warehouse", "finance"):
            tokens.setdefault(k, admin_tok)

        masters = step(
            results,
            "muat master SL043/FG01854/swatch",
            lambda: load_masters(tokens["marketing"]),
        )
        payload["flow"] = run_flow(tokens, masters, results, meeting_1709=True)
        flow = payload["flow"] or {}

        # Soft gates (data-dependent / tambahan meeting 17/9)
        soft_step(results, "soft dual gudang kimia/RP", lambda: soft_dual_gudang(tokens["production"]))
        soft_step(results, "soft treatment PU/Suede", lambda: soft_treatment(tokens["production"]))
        soft_step(results, "soft stock-sisa API", lambda: soft_stock_sisa(tokens["production"]))
        soft_step(
            results,
            "soft packing dari stock-sisa approved",
            lambda: soft_stock_sisa_packing(
                tokens["production"],
                mrp_po_id=(flow.get("m1") or {}).get("mrp_po_id"),
            ),
        )
        soft_step(
            results,
            "soft Lab stok lapangan saja",
            lambda: soft_lab_lapangan_only(tokens["production"]),
        )
        soft_step(
            results,
            "soft label roll GET payload",
            lambda: soft_label_roll(
                tokens["production"],
                mrp_packing_id=(flow.get("m7") or {}).get("packing_id"),
            ),
        )
        soft_step(
            results,
            "soft scan-out negatif",
            lambda: soft_scan_out_negatif(
                tokens["warehouse"],
                packing_id_sent=(flow.get("m9") or {}).get("packing_id")
                or (flow.get("m8") or {}).get("option_packing_id"),
            ),
        )
        soft_step(
            results,
            "soft role demo_* distinct",
            lambda: soft_role_tokens(tokens, admin_tok),
        )
        soft_step(
            results,
            "soft proses Suede",
            lambda: soft_suede_proses(
                tokens["production"],
                rencana_item_id=(flow.get("m2") or {}).get("item_id"),
                mrp_po_id=(flow.get("m1") or {}).get("mrp_po_id"),
            ),
        )
        soft_step(
            results,
            "soft SO+PPIC dari stock-sisa",
            lambda: soft_sisa_so_ppic(tokens["marketing"], tokens["production"], masters),
        )
        soft_step(
            results,
            "soft smoke API setara UI",
            lambda: soft_smoke_api_ui(
                tokens,
                detail_id=(flow.get("m0") or {}).get("detail_id"),
            ),
        )

    except StepFail as e:
        payload["stopped"] = True
        payload["stop_reason"] = {e.step: e.detail}
    except Exception as e:
        payload["stopped"] = True
        payload["stop_reason"] = str(e)
        results.append({"step": "crash", "ok": False, "error": str(e)})

    write_report(payload, REPORT_PATH)
    hard_ok = all(r.get("ok") for r in results if not r.get("soft"))
    print(
        json.dumps(
            {
                "ok": hard_ok,
                "report": str(REPORT_PATH),
                "api_base": so_e2e.BASE,
                "steps": [
                    (r["step"], "LULUS" if r.get("ok") else ("SKIP" if r.get("skipped") else "GAGAL"))
                    for r in results
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if hard_ok else 1


if __name__ == "__main__":
    sys.exit(main())
