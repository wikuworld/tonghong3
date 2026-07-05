#!/usr/bin/env python3
"""Smoke test alur bisnis ERP: input PO, marketing flow, delivery, outstanding.

Menjalankan request HTTP ke API backend (live). Default: baca + buat PO draft smoke lalu hapus.

Usage:
  cd backend && PYTHONPATH=. python scripts/smoke_test_flows.py
  docker compose exec backend python scripts/smoke_test_flows.py
  docker compose exec backend python scripts/smoke_test_flows.py --verbose
  docker compose exec backend python scripts/smoke_test_flows.py --read-only
  docker compose exec backend python scripts/smoke_test_flows.py --only po_input
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Callable, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BACKEND = __import__("pathlib").Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

PREFIX = "/api/v1"
DEFAULT_BASE = os.environ.get("SMOKE_API_BASE", "http://127.0.0.1:8000").rstrip("/")
DEFAULT_USER = os.environ.get("SMOKE_USER", "admin")
DEFAULT_PASSWORD = os.environ.get("SMOKE_PASSWORD", "admin123")

Status = str  # pass | fail | skip


@dataclass
class CaseResult:
    case_id: str
    title: str
    status: Status
    message: str = ""
    detail: str = ""


@dataclass
class SmokeReport:
    results: list[CaseResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == "pass")

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == "fail")

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.status == "skip")


class ApiClient:
    def __init__(self, base_url: str, token: str = "") -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json_body: Any = None,
        timeout: int = 60,
    ) -> tuple[int, Any, str]:
        url = f"{self.base_url}{path}"
        if params:
            from urllib.parse import urlencode

            qs = urlencode({k: v for k, v in params.items() if v is not None})
            if qs:
                url = f"{url}?{qs}"
        data = None
        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
        req = Request(url, data=data, method=method.upper(), headers=self._headers())
        try:
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
                status = resp.status
        except HTTPError as exc:
            status = exc.code
            raw = exc.read().decode("utf-8", errors="replace")
        except URLError as exc:
            raise ConnectionError(str(exc)) from exc
        if not raw:
            return status, None, ""
        try:
            return status, json.loads(raw), raw
        except json.JSONDecodeError:
            return status, raw, raw

    def get(self, path: str, **kwargs: Any) -> tuple[int, Any, str]:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> tuple[int, Any, str]:
        return self.request("POST", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> tuple[int, Any, str]:
        return self.request("DELETE", path, **kwargs)


@dataclass
class FlowContext:
    client: ApiClient
    read_only: bool
    smoke_po_id: Optional[int] = None
    smoke_po_number: Optional[str] = None
    sample_po_id: Optional[int] = None
    sample_delivery_id: Optional[int] = None


def _expect_status(
    case_id: str,
    title: str,
    status: int,
    expected: int | set[int],
    *,
    detail: str = "",
    ok_message: str = "",
) -> CaseResult:
    ok_codes = expected if isinstance(expected, set) else {expected}
    if status in ok_codes:
        return CaseResult(case_id, title, "pass", ok_message or f"HTTP {status}")
    return CaseResult(case_id, title, "fail", f"HTTP {status}, expected {sorted(ok_codes)}", detail[:800])


def smoke_health(ctx: FlowContext) -> CaseResult:
    try:
        status, body, raw = ctx.client.get("/health")
    except ConnectionError as exc:
        return CaseResult("health", "Health check", "fail", str(exc))
    if status == 200 and (body is None or body == {} or body.get("status") in (None, "ok", "healthy")):
        return CaseResult("health", "Health check", "pass", f"HTTP {status}")
    return CaseResult("health", "Health check", "pass" if status == 200 else "fail", f"HTTP {status}", str(body or raw)[:400])


def smoke_login(base_url: str, username: str, password: str) -> tuple[Optional[ApiClient], CaseResult]:
    client = ApiClient(base_url)
    try:
        status, body, raw = client.post(
            f"{PREFIX}/auth/login",
            json_body={"username": username, "password": password},
        )
    except ConnectionError as exc:
        return None, CaseResult("auth_login", "Login admin", "fail", str(exc))
    if status != 200 or not isinstance(body, dict) or not body.get("access_token"):
        return None, CaseResult("auth_login", "Login admin", "fail", f"HTTP {status}", raw[:400])
    client.token = body["access_token"]
    return client, CaseResult("auth_login", "Login admin", "pass", f"user={username}")


def _pick_po_context(ctx: FlowContext) -> Optional[tuple[int, int, str]]:
    status, body, _ = ctx.client.get(f"{PREFIX}/customers/page", params={"limit": 30, "offset": 0})
    if status != 200 or not isinstance(body, dict):
        return None
    for customer in body.get("items") or []:
        cid = customer.get("id")
        if not cid:
            continue
        st, brands, _ = ctx.client.get(f"{PREFIX}/customers/{cid}/allowed-brands")
        if st != 200 or not brands:
            continue
        brand = brands[0]
        bid = brand.get("id")
        if not bid:
            continue
        st2, buyers, _ = ctx.client.get(f"{PREFIX}/masters/brands/{bid}/buyers")
        buyer = None
        if st2 == 200 and buyers:
            buyer = buyers[0].get("buyer_code")
        buyer = buyer or brand.get("code") or "NB"
        return int(cid), int(bid), str(buyer)
    return None


def smoke_po_preview_number(ctx: FlowContext) -> CaseResult:
    status, body, raw = ctx.client.get(
        f"{PREFIX}/po/next-number",
        params={"po_category": "production", "order_date": date.today().isoformat()},
    )
    if status == 200 and isinstance(body, dict) and body.get("po_number"):
        return CaseResult("po_preview_number", "Preview nomor PO/SO", "pass", body["po_number"])
    return _expect_status("po_preview_number", "Preview nomor PO/SO", status, 200, detail=raw, ok_message="")


def smoke_po_list(ctx: FlowContext) -> CaseResult:
    status, body, raw = ctx.client.get(f"{PREFIX}/po/page", params={"limit": 5, "offset": 0})
    if status != 200 or not isinstance(body, dict):
        return _expect_status("po_list", "Daftar PO (page)", status, 200, detail=raw)
    total = body.get("total", 0)
    items = body.get("items") or []
    if items and not ctx.sample_po_id:
        ctx.sample_po_id = items[0].get("id")
    return CaseResult("po_list", "Daftar PO (page)", "pass", f"{total} PO, sample id={ctx.sample_po_id}")


def smoke_po_input_write(ctx: FlowContext) -> CaseResult:
    if ctx.read_only:
        return CaseResult("po_input_write", "Input PO (create + detail)", "skip", "read-only mode")
    picked = _pick_po_context(ctx)
    if not picked:
        return CaseResult("po_input_write", "Input PO (create + detail)", "skip", "tidak ada customer+brand di DB")
    customer_id, brand_id, buyer = picked
    ref = f"SMOKE-{uuid.uuid4().hex[:10].upper()}"
    create_status, po, raw = ctx.client.post(
        f"{PREFIX}/po",
        json_body={
            "customer_id": customer_id,
            "brand_id": brand_id,
            "buyer": buyer,
            "po_category": "production",
            "status": "draft",
            "po_customer_ref": ref,
            "order_date": date.today().isoformat(),
            "remark": "Smoke test — auto cleanup",
        },
    )
    if create_status not in (200, 201) or not isinstance(po, dict) or not po.get("id"):
        return CaseResult("po_input_write", "Input PO (create + detail)", "fail", f"create HTTP {create_status}", raw[:600])
    po_id = int(po["id"])
    ctx.smoke_po_id = po_id
    ctx.smoke_po_number = po.get("po_number")

    detail_status, detail, detail_raw = ctx.client.post(
        f"{PREFIX}/po/{po_id}/details",
        json_body={
            "material_name": "COW SPORT",
            "color": "BLACK",
            "color_family": "black",
            "thickness_text": "1.2-1.4",
            "quantity_order": "100",
            "style_article": "SMOKE-TEST",
        },
    )
    if detail_status not in (200, 201):
        return CaseResult(
            "po_input_write",
            "Input PO (create + detail)",
            "fail",
            f"detail HTTP {detail_status} (PO {po_id} dibuat, belum dihapus)",
            detail_raw[:600],
        )

    list_status, details, _ = ctx.client.get(f"{PREFIX}/po/{po_id}/details")
    if list_status != 200 or not isinstance(details, list) or len(details) < 1:
        return CaseResult("po_input_write", "Input PO (create + detail)", "fail", "detail tidak terbaca setelah create")

    return CaseResult(
        "po_input_write",
        "Input PO (create + detail)",
        "pass",
        f"PO {ctx.smoke_po_number} id={po_id}, {len(details)} baris",
    )


def smoke_po_cleanup(ctx: FlowContext) -> CaseResult:
    if ctx.read_only or not ctx.smoke_po_id:
        return CaseResult("po_cleanup", "Cleanup PO smoke", "skip", "tidak ada PO smoke")
    status, body, raw = ctx.client.delete(f"{PREFIX}/po/{ctx.smoke_po_id}")
    if status == 200:
        ctx.smoke_po_id = None
        return CaseResult("po_cleanup", "Cleanup PO smoke", "pass", "PO smoke dihapus")
    if status in (400, 409):
        return CaseResult(
            "po_cleanup",
            "Cleanup PO smoke",
            "skip",
            f"PO {ctx.smoke_po_id} tidak bisa dihapus (HTTP {status}) — hapus manual bila perlu",
            raw[:400],
        )
    return CaseResult("po_cleanup", "Cleanup PO smoke", "fail", f"HTTP {status}", raw[:400])


def smoke_mkt_workflow_stages(ctx: FlowContext) -> CaseResult:
    status, body, raw = ctx.client.get(f"{PREFIX}/po/mkt-workflow-stages")
    if status == 200 and isinstance(body, dict) and body.get("stages"):
        stages = body["stages"]
        return CaseResult("mkt_workflow_stages", "Tahapan marketing workflow", "pass", f"{len(stages)} tahap")
    return _expect_status("mkt_workflow_stages", "Tahapan marketing workflow", status, 200, detail=raw)


def smoke_mkt_workflow_on_po(ctx: FlowContext) -> CaseResult:
    po_id = ctx.smoke_po_id or ctx.sample_po_id
    if not po_id:
        return CaseResult("mkt_workflow_po", "Status workflow pada PO", "skip", "tidak ada PO sample")
    status, body, raw = ctx.client.get(f"{PREFIX}/po/{po_id}")
    if status != 200 or not isinstance(body, dict):
        return _expect_status("mkt_workflow_po", "Status workflow pada PO", status, 200, detail=raw)
    stage = body.get("mkt_workflow_stage") or "input_system"
    return CaseResult("mkt_workflow_po", "Status workflow pada PO", "pass", f"PO {po_id} stage={stage}")


def smoke_marketing_outstanding(ctx: FlowContext) -> CaseResult:
    status, body, raw = ctx.client.get(
        f"{PREFIX}/marketing/outstanding-lines",
        params={"limit": 10, "skip": 0, "balance_filter": "all"},
    )
    if status != 200 or not isinstance(body, dict):
        return _expect_status("marketing_outstanding", "Outstanding marketing (saldo order)", status, 200, detail=raw)
    total = body.get("total", 0)
    rows = body.get("data") or []
    sample = rows[0] if rows else {}
    thi = sample.get("thi_order") or "-"
    no_po = sample.get("no_po") or "-"
    return CaseResult(
        "marketing_outstanding",
        "Outstanding marketing (saldo order)",
        "pass",
        f"{total} baris, contoh thi_order={thi}, no_po={no_po}",
    )


def smoke_marketing_outstanding_csv(ctx: FlowContext) -> CaseResult:
    status, body, raw = ctx.client.get(f"{PREFIX}/marketing/outstanding-lines.csv", params={"limit": 5})
    if status == 200 and isinstance(body, str) and "PO" in body.upper():
        return CaseResult("marketing_outstanding_csv", "Export outstanding CSV", "pass", f"{len(body.splitlines())} baris")
    if status == 200:
        return CaseResult("marketing_outstanding_csv", "Export outstanding CSV", "pass", "CSV OK")
    return _expect_status("marketing_outstanding_csv", "Export outstanding CSV", status, 200, detail=str(raw)[:400])


def smoke_marketing_delivery_lines(ctx: FlowContext) -> CaseResult:
    status, body, raw = ctx.client.get(
        f"{PREFIX}/marketing/delivery-lines",
        params={"limit": 10, "skip": 0},
    )
    if status != 200 or not isinstance(body, dict):
        return _expect_status("marketing_delivery_lines", "Delivery lines marketing", status, 200, detail=raw)
    total = body.get("total", 0)
    return CaseResult("marketing_delivery_lines", "Delivery lines marketing", "pass", f"{total} baris kiriman")


def smoke_marketing_delivery_planning(ctx: FlowContext) -> CaseResult:
    status, body, raw = ctx.client.get(f"{PREFIX}/marketing/delivery-planning", params={"limit": 5})
    if status == 200 and isinstance(body, dict):
        total = body.get("total", len(body.get("data") or []))
        return CaseResult("marketing_delivery_planning", "Perencanaan delivery marketing", "pass", f"{total} slot")
    return _expect_status("marketing_delivery_planning", "Perencanaan delivery marketing", status, 200, detail=raw)


def smoke_marketing_delivery_today(ctx: FlowContext) -> CaseResult:
    status, body, raw = ctx.client.get(f"{PREFIX}/marketing/delivery-today")
    if status == 200 and isinstance(body, dict):
        count = len(body.get("lines") or body.get("data") or [])
        return CaseResult("marketing_delivery_today", "Delivery hari ini", "pass", f"{count} baris")
    return _expect_status("marketing_delivery_today", "Delivery hari ini", status, 200, detail=raw)


def smoke_delivery_list(ctx: FlowContext) -> CaseResult:
    status, body, raw = ctx.client.get(f"{PREFIX}/delivery", params={"limit": 5})
    if status != 200 or not isinstance(body, list):
        return _expect_status("delivery_list", "Daftar delivery header", status, 200, detail=raw)
    if body and not ctx.sample_delivery_id:
        ctx.sample_delivery_id = body[0].get("id")
    return CaseResult(
        "delivery_list",
        "Daftar delivery header",
        "pass",
        f"{len(body)} header, sample id={ctx.sample_delivery_id}",
    )


def smoke_delivery_ready_shipments(ctx: FlowContext) -> CaseResult:
    status, body, raw = ctx.client.get(f"{PREFIX}/delivery-shipments/ready")
    if status == 200 and isinstance(body, list):
        return CaseResult("delivery_ready", "Baris siap kirim (packing→delivery)", "pass", f"{len(body)} baris")
    return _expect_status("delivery_ready", "Baris siap kirim (packing→delivery)", status, 200, detail=raw)


def smoke_delivery_details(ctx: FlowContext) -> CaseResult:
    if not ctx.sample_delivery_id:
        return CaseResult("delivery_details", "Detail delivery sample", "skip", "tidak ada delivery di DB")
    status, body, raw = ctx.client.get(f"{PREFIX}/delivery/{ctx.sample_delivery_id}/details")
    if status == 200 and isinstance(body, list):
        return CaseResult(
            "delivery_details",
            "Detail delivery sample",
            "pass",
            f"delivery {ctx.sample_delivery_id}: {len(body)} baris",
        )
    return _expect_status("delivery_details", "Detail delivery sample", status, 200, detail=raw)


def smoke_outstanding_materials(ctx: FlowContext) -> CaseResult:
    status, body, raw = ctx.client.get(f"{PREFIX}/workflow/outstanding-materials", params={"limit": 10})
    if status == 200 and isinstance(body, list):
        return CaseResult("outstanding_materials", "Outstanding materials (PPIC)", "pass", f"{len(body)} baris")
    return _expect_status("outstanding_materials", "Outstanding materials (PPIC)", status, 200, detail=raw)


FLOW_CASES: list[tuple[str, str, Callable[[FlowContext], CaseResult]]] = [
    ("health", "Health check", smoke_health),
    ("po_preview_number", "Preview nomor PO", smoke_po_preview_number),
    ("po_list", "Daftar PO", smoke_po_list),
    ("po_input_write", "Input PO", smoke_po_input_write),
    ("mkt_workflow_stages", "Tahapan MKT workflow", smoke_mkt_workflow_stages),
    ("mkt_workflow_po", "Workflow pada PO", smoke_mkt_workflow_on_po),
    ("marketing_outstanding", "Outstanding marketing", smoke_marketing_outstanding),
    ("marketing_outstanding_csv", "Export outstanding CSV", smoke_marketing_outstanding_csv),
    ("marketing_delivery_lines", "Delivery lines marketing", smoke_marketing_delivery_lines),
    ("marketing_delivery_planning", "Perencanaan delivery", smoke_marketing_delivery_planning),
    ("marketing_delivery_today", "Delivery hari ini", smoke_marketing_delivery_today),
    ("delivery_list", "Daftar delivery", smoke_delivery_list),
    ("delivery_ready", "Siap kirim", smoke_delivery_ready_shipments),
    ("delivery_details", "Detail delivery", smoke_delivery_details),
    ("outstanding_materials", "Outstanding materials", smoke_outstanding_materials),
    ("po_cleanup", "Cleanup PO smoke", smoke_po_cleanup),
]


def run_flows(
    *,
    base_url: str,
    username: str,
    password: str,
    only: set[str] | None,
    verbose: bool,
    read_only: bool,
) -> SmokeReport:
    report = SmokeReport()
    client, login_result = smoke_login(base_url, username, password)
    report.results.append(login_result)
    if not client:
        return report

    ctx = FlowContext(client=client, read_only=read_only)

    for case_id, title, runner in FLOW_CASES:
        if only and case_id not in only:
            continue
        try:
            result = runner(ctx)
        except Exception as exc:
            result = CaseResult(case_id, title, "fail", str(exc), traceback.format_exc())
        report.results.append(result)
        if verbose:
            icon = {"pass": "✓", "fail": "✗", "skip": "○"}[result.status]
            print(f"{icon} [{result.case_id}] {result.title}: {result.message}")
            if result.detail:
                print(result.detail)
                print()

    return report


def print_summary(report: SmokeReport) -> None:
    print("=" * 72)
    print("SMOKE TEST FLOWS — PO / Marketing / Delivery / Outstanding")
    print("=" * 72)
    for result in report.results:
        icon = {"pass": "PASS", "fail": "FAIL", "skip": "SKIP"}[result.status]
        print(f"[{icon:4}] {result.case_id:28} {result.message}")
    print("-" * 72)
    print(
        f"Total: {len(report.results)} | "
        f"PASS: {report.passed} | FAIL: {report.failed} | SKIP: {report.skipped}"
    )
    print("=" * 72)


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test alur PO, marketing, delivery, outstanding")
    parser.add_argument("--base-url", default=DEFAULT_BASE, help=f"Base API host (default: {DEFAULT_BASE})")
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument("--only", action="append", metavar="CASE_ID")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument(
        "--read-only",
        action="store_true",
        help="Hanya GET; tidak buat/hapus PO smoke",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    only = set(args.only) if args.only else None
    report = run_flows(
        base_url=args.base_url,
        username=args.user,
        password=args.password,
        only=only,
        verbose=args.verbose,
        read_only=args.read_only,
    )

    if args.json:
        print(
            json.dumps(
                {
                    "passed": report.passed,
                    "failed": report.failed,
                    "skipped": report.skipped,
                    "results": [r.__dict__ for r in report.results],
                },
                indent=2,
                ensure_ascii=False,
            )
        )
    else:
        print_summary(report)

    return 1 if report.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
