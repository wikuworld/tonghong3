#!/usr/bin/env python3
"""Smoke test untuk semua skrip operasional di backend/scripts/.

Memverifikasi:
- modul dapat diimpor (syntax / dependency OK)
- CLI argparse merespons --help
- skrip dengan --dry-run jalan tanpa mutasi DB
- skrip impor dapat membaca sumber data (CSV/folder) bila tersedia
- koneksi database untuk skrip yang membutuhkan DB

Usage:
  cd backend && PYTHONPATH=. .venv/bin/python scripts/smoke_test.py
  cd backend && PYTHONPATH=. .venv/bin/python scripts/smoke_test.py --verbose
  cd backend && PYTHONPATH=. .venv/bin/python scripts/smoke_test.py --only normalize_lot_numbers
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import subprocess
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent if (BACKEND.parent / "docker-compose.yml").exists() else BACKEND
sys.path.insert(0, str(BACKEND))


def _dokumentasi_dir() -> Path:
    for candidate in (BACKEND / "dokumentasi", ROOT / "dokumentasi"):
        if candidate.is_dir():
            return candidate
    return BACKEND / "dokumentasi"


FIXTURES = Path(__file__).resolve().parent / "smoke_fixtures"


def _resolve_path(primary: Path, fixture_rel: str) -> tuple[Path, bool]:
    if primary.exists():
        return primary, False
    fixture = FIXTURES / fixture_rel
    if fixture.exists():
        return fixture, True
    return primary, False


def _resolve_dir(primary: Path, fixture_rel: str) -> tuple[Path, bool]:
    if primary.is_dir() and any(primary.glob("*")):
        return primary, False
    fixture = FIXTURES / fixture_rel
    if fixture.is_dir() and any(fixture.glob("*")):
        return fixture, True
    return primary, False


def _fluorescent_dir() -> tuple[Path, bool]:
    def _complete(base: Path) -> bool:
        nb = base / "Copy of NB Fluorescent color REV (from mr bob).csv"
        adidas = base / "adidas Metallic Fluorescent Colors till SS26.csv"
        global_file = next(base.glob("Fluorescent-*SPSU27.csv"), None)
        return nb.exists() and adidas.exists() and global_file is not None

    dok_dir = _dokumentasi_dir()
    if _complete(dok_dir):
        return dok_dir, False
    fixture_dir = FIXTURES / "fluorescent"
    if _complete(fixture_dir):
        return fixture_dir, True
    return dok_dir, False


Status = str  # "pass" | "fail" | "skip"


def _fixture_note(used_fixture: bool) -> str:
    return " [fixture]" if used_fixture else ""


@dataclass
class CaseResult:
    script_id: str
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


def _run(cmd: list[str], *, cwd: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(BACKEND))
    return subprocess.run(
        cmd,
        cwd=str(cwd or BACKEND),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _python(*args: str) -> list[str]:
    return [sys.executable, *args]


def _merge_output(proc: subprocess.CompletedProcess[str], limit: int = 800) -> str:
    text = (proc.stdout or "") + (proc.stderr or "")
    text = text.strip()
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def _db_ping() -> tuple[bool, str]:
    try:
        from sqlalchemy import text

        from app.db import SessionLocal

        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return True, "koneksi database OK"
        finally:
            db.close()
    except Exception as exc:
        return False, f"database tidak tersedia: {exc}"


def _runtime_ready() -> tuple[bool, str]:
    try:
        import sqlalchemy  # noqa: F401
    except ImportError:
        return False, "dependency backend belum terpasang — jalankan: cd backend && .venv/bin/python scripts/smoke_test.py"
    return True, "runtime OK"


def _import_module(module_name: str):
    ready, msg = _runtime_ready()
    if not ready:
        raise RuntimeError(msg)
    return importlib.import_module(module_name)


def _case_import(module_name: str, script_id: str, title: str) -> CaseResult:
    ready, msg = _runtime_ready()
    if not ready:
        return CaseResult(script_id, title, "skip", msg)
    try:
        mod = importlib.import_module(module_name)
        return CaseResult(script_id, title, "pass", f"import {module_name} OK", getattr(mod, "__doc__", "") or "")
    except Exception as exc:
        return CaseResult(script_id, title, "fail", f"gagal import {module_name}", str(exc))


def _case_cli_help(script_rel: str, script_id: str, title: str) -> CaseResult:
    ready, msg = _runtime_ready()
    if not ready:
        return CaseResult(script_id, title, "skip", msg)
    path = BACKEND / script_rel
    proc = _run(_python(str(path), "--help"))
    if proc.returncode == 0 and proc.stdout.strip():
        return CaseResult(script_id, title, "pass", "--help OK")
    return CaseResult(
        script_id,
        title,
        "fail",
        f"--help exit {proc.returncode}",
        _merge_output(proc),
    )


def _case_dry_run(script_rel: str, script_id: str, title: str, extra_args: list[str] | None = None) -> CaseResult:
    ok_db, db_msg = _db_ping()
    if not ok_db:
        return CaseResult(script_id, title, "skip", db_msg)

    path = BACKEND / script_rel
    proc = _run(_python(str(path), "--dry-run", *(extra_args or [])))
    if proc.returncode == 0:
        snippet = _merge_output(proc, 300)
        return CaseResult(script_id, title, "pass", "dry-run OK", snippet)
    return CaseResult(
        script_id,
        title,
        "fail",
        f"dry-run exit {proc.returncode}",
        _merge_output(proc),
    )


def smoke_normalize_lot_numbers() -> CaseResult:
    return _case_dry_run("scripts/normalize_lot_numbers.py", "normalize_lot_numbers", "Normalisasi nomor lot PO")


def smoke_normalize_color_swatch_factories() -> CaseResult:
    return _case_dry_run(
        "scripts/normalize_color_swatch_factories.py",
        "normalize_color_swatch_factories",
        "Normalisasi relasi factory color swatch",
    )


def _subkon_csv_path() -> Path:
    candidates = [
        BACKEND / "dokumentasi" / "Master_Data_extracted" / "01_Master_Item_SubKon.csv",
        ROOT / "dokumentasi" / "Master_Data_extracted" / "01_Master_Item_SubKon.csv",
        _dokumentasi_dir() / "master-items" / "Sheet1-Table_1.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def smoke_import_subkon_master_items() -> CaseResult:
    ready, msg = _runtime_ready()
    if not ready:
        return CaseResult("import_subkon_master_items", "Impor master item SubKon", "skip", msg)
    csv_path = _subkon_csv_path()
    if not csv_path.exists():
        return CaseResult(
            "import_subkon_master_items",
            "Impor master item SubKon",
            "skip",
            f"CSV tidak ada: {csv_path}",
        )
    return _case_dry_run("scripts/import_subkon_master_items.py", "import_subkon_master_items", "Impor master item SubKon", ["--csv", str(csv_path)])


def _master_items_subkon_csv() -> Path:
    return _dokumentasi_dir() / "master-items" / "Sheet1-Table_1.csv"


def smoke_import_master_items_dokumentasi() -> CaseResult:
    ready, msg = _runtime_ready()
    if not ready:
        return CaseResult("import_master_items_dokumentasi", "Impor master item dokumentasi", "skip", msg)
    subkon_csv = _master_items_subkon_csv()
    if not subkon_csv.exists():
        return CaseResult(
            "import_master_items_dokumentasi",
            "Impor master item dokumentasi",
            "skip",
            f"CSV SubKon tidak ada: {subkon_csv}",
        )
    return _case_dry_run(
        "scripts/import_master_items_dokumentasi.py",
        "import_master_items_dokumentasi",
        "Impor master item dokumentasi",
        ["--only", "subkon", "--subkon-csv", str(subkon_csv)],
    )


def smoke_fix_empty_po_numbers() -> CaseResult:
    ok_db, db_msg = _db_ping()
    if not ok_db:
        return CaseResult("fix_empty_po_numbers", "Perbaiki PO tanpa nomor", "skip", db_msg)
    try:
        from sqlalchemy import or_

        from app.db import SessionLocal
        from app.models import PoHeader

        db = SessionLocal()
        try:
            total = db.query(PoHeader).count()
            empty_number = db.query(PoHeader).filter(
                or_(PoHeader.po_number.is_(None), PoHeader.po_number == "")
            ).count()
            empty_ref = db.query(PoHeader).filter(
                or_(PoHeader.po_customer_ref.is_(None), PoHeader.po_customer_ref == "")
            ).count()
        finally:
            db.close()
        return CaseResult(
            "fix_empty_po_numbers",
            "Perbaiki PO tanpa nomor",
            "pass",
            f"read-only OK — {total} PO, {empty_number} tanpa po_number, {empty_ref} tanpa po_customer_ref",
        )
    except Exception as exc:
        return CaseResult("fix_empty_po_numbers", "Perbaiki PO tanpa nomor", "fail", str(exc), traceback.format_exc())


def _master_data_csv_dir() -> Path:
    default = ROOT.parent / "Master_Data_extracted"
    if BACKEND == ROOT:
        default = Path("/Master_Data_extracted")
    return Path(os.environ.get("MASTER_CSV_DIR", str(default)))


def smoke_import_master_data() -> CaseResult:
    ready, msg = _runtime_ready()
    if not ready:
        return CaseResult("import_master_data", "Impor Master_Data_extracted", "skip", msg)
    csv_dir, used_fixture = _resolve_dir(_master_data_csv_dir(), "Master_Data_extracted")
    if not csv_dir.is_dir():
        return CaseResult(
            "import_master_data",
            "Impor Master_Data_extracted",
            "skip",
            f"folder CSV tidak ada: {csv_dir}",
        )
    expected = ["01_Master_Item.csv"]
    found = [name for name in expected if (csv_dir / name).exists()]
    if not found:
        return CaseResult(
            "import_master_data",
            "Impor Master_Data_extracted",
            "skip",
            f"folder ada tapi file inti tidak ditemukan di {csv_dir}",
        )
    return CaseResult(
        "import_master_data",
        "Impor Master_Data_extracted",
        "pass",
        f"sumber data OK ({csv_dir}, {len(found)} file inti){_fixture_note(used_fixture)}",
    )


def smoke_import_fluorescent_colors() -> CaseResult:
    ready, msg = _runtime_ready()
    if not ready:
        return CaseResult("import_fluorescent_colors", "Impor master fluorescent color", "skip", msg)
    mod = _import_module("scripts.import_fluorescent_colors")
    dok_dir, used_fixture = _fluorescent_dir()
    nb = dok_dir / "Copy of NB Fluorescent color REV (from mr bob).csv"
    adidas = dok_dir / "adidas Metallic Fluorescent Colors till SS26.csv"
    global_file = next(dok_dir.glob("Fluorescent-*SPSU27.csv"), None)
    missing = [p.name for p in (nb, adidas) if not p.exists()]
    if global_file is None:
        missing.append("Fluorescent-*SPSU27.csv")
    if missing:
        return CaseResult(
            "import_fluorescent_colors",
            "Impor master fluorescent color",
            "skip",
            f"file CSV tidak lengkap di {dok_dir}: {', '.join(missing)}",
        )
    try:
        rows = mod.dedup(
            mod.load_nb(nb)
            + mod.load_adidas(adidas)
            + mod.load_global(global_file)
        )
        return CaseResult(
            "import_fluorescent_colors",
            "Impor master fluorescent color",
            "pass",
            f"parser OK — {len(rows)} baris unik{_fixture_note(used_fixture)}",
        )
    except Exception as exc:
        return CaseResult(
            "import_fluorescent_colors",
            "Impor master fluorescent color",
            "fail",
            str(exc),
            traceback.format_exc(),
        )


def smoke_import_factory_lokal() -> CaseResult:
    ready, msg = _runtime_ready()
    if not ready:
        return CaseResult("import_factory_lokal", "Impor LIST FACTORY-LOKAL", "skip", msg)
    primary = Path(os.environ.get("FACTORY_LOKAL_CSV", str(_dokumentasi_dir() / "LIST FACTORY-LOKAL.csv")))
    csv_path, used_fixture = _resolve_path(primary, "LIST FACTORY-LOKAL.csv")
    if not csv_path.exists():
        return CaseResult(
            "import_factory_lokal",
            "Impor LIST FACTORY-LOKAL",
            "skip",
            f"CSV tidak ada: {primary}",
        )
    try:
        import csv

        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter=";"))
        return CaseResult(
            "import_factory_lokal",
            "Impor LIST FACTORY-LOKAL",
            "pass",
            f"CSV OK — {len(rows)} baris ({csv_path.name}){_fixture_note(used_fixture)}",
        )
    except Exception as exc:
        return CaseResult("import_factory_lokal", "Impor LIST FACTORY-LOKAL", "fail", str(exc))


def smoke_import_factory_export() -> CaseResult:
    primary = Path("/tmp/LIST_FACTORY_EXPORT.csv")
    if not primary.exists():
        primary = _dokumentasi_dir() / "LIST FACTORY-EXPORT.csv"
    csv_path, used_fixture = _resolve_path(primary, "LIST FACTORY-EXPORT.csv")
    if not csv_path.exists():
        return CaseResult(
            "import_factory_export",
            "Impor LIST FACTORY-EXPORT",
            "skip",
            f"CSV tidak ada: {primary}",
        )
    try:
        import csv

        with open(csv_path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter=";"))
        return CaseResult(
            "import_factory_export",
            "Impor LIST FACTORY-EXPORT",
            "pass",
            f"CSV OK — {len(rows)} baris ({csv_path.name}){_fixture_note(used_fixture)}",
        )
    except Exception as exc:
        return CaseResult("import_factory_export", "Impor LIST FACTORY-EXPORT", "fail", str(exc))


def smoke_import_customs_aju_folder() -> CaseResult:
    ready, msg = _runtime_ready()
    if not ready:
        return CaseResult("import_customs_aju_folder", "Impor folder CSV customs AJU", "skip", msg)
    primary = ROOT.parent / "017_728_VICTORY_D_extracted"
    if BACKEND == ROOT:
        primary = Path("/017_728_VICTORY_D_extracted")
    folder, used_fixture = _resolve_dir(primary, "017_728_VICTORY_D_extracted")
    if not folder.is_dir():
        return CaseResult(
            "import_customs_aju_folder",
            "Impor folder CSV customs AJU",
            "skip",
            f"folder tidak ada: {primary}",
        )
    try:
        from app.services.customs_import import load_folder_csvs

        sheets = load_folder_csvs(folder)
        if not sheets:
            return CaseResult(
                "import_customs_aju_folder",
                "Impor folder CSV customs AJU",
                "fail",
                f"folder ada tapi tidak ada CSV: {folder}",
            )
        return CaseResult(
            "import_customs_aju_folder",
            "Impor folder CSV customs AJU",
            "pass",
            f"load_folder_csvs OK — {len(sheets)} sheet{_fixture_note(used_fixture)}",
        )
    except Exception as exc:
        return CaseResult(
            "import_customs_aju_folder",
            "Impor folder CSV customs AJU",
            "fail",
            str(exc),
            traceback.format_exc(),
        )


def smoke_import_buyer_price_folder() -> CaseResult:
    primary = ROOT / "LIST_HARGA_ALL_BUYER_extracted"
    if BACKEND == ROOT:
        primary = Path("/LIST_HARGA_ALL_BUYER_extracted")
    folder, used_fixture = _resolve_dir(primary, "LIST_HARGA_ALL_BUYER_extracted")
    if not folder.is_dir():
        return CaseResult(
            "import_buyer_price_folder",
            "Impor folder list harga buyer",
            "skip",
            f"folder tidak ada: {primary}",
        )
    csv_files = sorted(folder.glob("*.csv"))
    if not csv_files:
        return CaseResult(
            "import_buyer_price_folder",
            "Impor folder list harga buyer",
            "fail",
            f"folder ada tapi tidak ada CSV: {folder}",
        )
    try:
        from app.services.buyer_price_import import parse_buyer_csv

        parsed = parse_buyer_csv(csv_files[0])
        row_count = len(parsed.get("data_rows") or [])
        return CaseResult(
            "import_buyer_price_folder",
            "Impor folder list harga buyer",
            "pass",
            f"parse_buyer_csv OK — {len(csv_files)} file, {row_count} baris contoh{_fixture_note(used_fixture)}",
        )
    except Exception as exc:
        return CaseResult(
            "import_buyer_price_folder",
            "Impor folder list harga buyer",
            "fail",
            str(exc),
            traceback.format_exc(),
        )


def smoke_demo_correlation_data(*, allow_destructive: bool) -> CaseResult:
    ready, msg = _runtime_ready()
    if not ready:
        return CaseResult("demo_correlation_data", "Demo data korelasi Customer→PO", "skip", msg)
    _import_module("scripts.demo_correlation_data")
    ok_db, db_msg = _db_ping()
    if not ok_db:
        return CaseResult("demo_correlation_data", "Demo data korelasi Customer→PO", "skip", db_msg)
    extra = ["--reset-demo"] if allow_destructive else []
    proc = _run(_python("-m", "scripts.demo_correlation_data", *extra), timeout=300)
    if proc.returncode == 0:
        mode = "reset+upsert" if allow_destructive else "upsert idempotent"
        return CaseResult("demo_correlation_data", "Demo data korelasi Customer→PO", "pass", f"demo_correlation_data OK ({mode})")
    return CaseResult(
        "demo_correlation_data",
        "Demo data korelasi Customer→PO",
        "fail",
        f"exit {proc.returncode}",
        _merge_output(proc, 2000),
    )


@dataclass
class ScriptSpec:
    script_id: str
    title: str
    module_name: str | None = None
    cli_script: str | None = None
    runner: Callable[[], CaseResult] | None = None


SCRIPT_SPECS: list[ScriptSpec] = [
    ScriptSpec(
        "normalize_lot_numbers",
        "Normalisasi nomor lot PO",
        cli_script="scripts/normalize_lot_numbers.py",
        runner=smoke_normalize_lot_numbers,
    ),
    ScriptSpec(
        "normalize_color_swatch_factories",
        "Normalisasi factory color swatch",
        cli_script="scripts/normalize_color_swatch_factories.py",
        runner=smoke_normalize_color_swatch_factories,
    ),
    ScriptSpec(
        "import_subkon_master_items",
        "Impor master item SubKon",
        module_name="scripts.import_subkon_master_items",
        cli_script="scripts/import_subkon_master_items.py",
        runner=smoke_import_subkon_master_items,
    ),
    ScriptSpec(
        "import_master_items_dokumentasi",
        "Impor master item dokumentasi",
        module_name="scripts.import_master_items_dokumentasi",
        cli_script="scripts/import_master_items_dokumentasi.py",
        runner=smoke_import_master_items_dokumentasi,
    ),
    ScriptSpec(
        "fix_empty_po_numbers",
        "Perbaiki PO tanpa nomor",
        module_name="scripts.fix_empty_po_numbers",
        runner=smoke_fix_empty_po_numbers,
    ),
    ScriptSpec(
        "import_master_data",
        "Impor Master_Data_extracted",
        module_name="scripts.import_master_data",
        runner=smoke_import_master_data,
    ),
    ScriptSpec(
        "import_fluorescent_colors",
        "Impor fluorescent color",
        module_name="scripts.import_fluorescent_colors",
        runner=smoke_import_fluorescent_colors,
    ),
    ScriptSpec(
        "import_factory_lokal",
        "Impor factory lokal",
        module_name="scripts.import_factory_lokal",
        runner=smoke_import_factory_lokal,
    ),
    ScriptSpec(
        "import_factory_export",
        "Impor factory export",
        runner=smoke_import_factory_export,
    ),
    ScriptSpec(
        "import_customs_aju_folder",
        "Impor customs AJU",
        module_name="scripts.import_customs_aju_folder",
        runner=smoke_import_customs_aju_folder,
    ),
    ScriptSpec(
        "import_buyer_price_folder",
        "Impor buyer price folder",
        runner=smoke_import_buyer_price_folder,
    ),
    ScriptSpec(
        "demo_correlation_data",
        "Demo data korelasi Customer→PO",
        module_name="scripts.demo_correlation_data",
        runner=None,
    ),
]


def _merge_status(current: Status, new: Status) -> Status:
    priority = {"fail": 3, "skip": 2, "pass": 1}
    return new if priority[new] > priority[current] else current


OFFLINE_SCRIPT_IDS = frozenset({"import_factory_export", "import_buyer_price_folder"})


def _evaluate_script(spec: ScriptSpec, *, allow_destructive: bool) -> CaseResult:
    ready, runtime_msg = _runtime_ready()
    if not ready and spec.script_id not in OFFLINE_SCRIPT_IDS:
        return CaseResult(spec.script_id, spec.title, "skip", runtime_msg)

    status: Status = "pass"
    messages: list[str] = []
    details: list[str] = []

    if spec.module_name:
        import_result = _case_import(spec.module_name, spec.script_id, spec.title)
        status = _merge_status(status, import_result.status)
        if import_result.status != "pass":
            messages.append(import_result.message)

    if spec.cli_script:
        cli_result = _case_cli_help(spec.cli_script, spec.script_id, spec.title)
        status = _merge_status(status, cli_result.status)
        if cli_result.status != "pass":
            messages.append(f"CLI: {cli_result.message}")
            if cli_result.detail:
                details.append(cli_result.detail)

    if spec.script_id == "demo_correlation_data":
        feature_result = smoke_demo_correlation_data(allow_destructive=allow_destructive)
    elif spec.runner:
        try:
            feature_result = spec.runner()
        except Exception as exc:
            feature_result = CaseResult(spec.script_id, spec.title, "fail", str(exc), traceback.format_exc())
    else:
        feature_result = CaseResult(spec.script_id, spec.title, "skip", "tidak ada runner")

    status = _merge_status(status, feature_result.status)
    if feature_result.status == "pass":
        messages.insert(0, feature_result.message)
    elif feature_result.message:
        messages.append(feature_result.message)
    if feature_result.detail:
        details.append(feature_result.detail)

    if status == "pass" and not messages:
        messages.append("OK")

    unique_messages = list(dict.fromkeys(messages))

    return CaseResult(
        spec.script_id,
        spec.title,
        status,
        " | ".join(unique_messages),
        "\n".join(details),
    )


def run_smoke(*, only: set[str] | None, verbose: bool, allow_destructive: bool) -> SmokeReport:
    report = SmokeReport()

    db_ok, db_msg = _db_ping()
    if db_ok:
        report.results.append(CaseResult("database", "Koneksi database", "pass", db_msg))
    else:
        report.results.append(CaseResult("database", "Koneksi database", "skip", db_msg))

    for spec in SCRIPT_SPECS:
        if only and spec.script_id not in only:
            continue
        result = _evaluate_script(spec, allow_destructive=allow_destructive)
        report.results.append(result)
        if verbose:
            icon = {"pass": "✓", "fail": "✗", "skip": "○"}[result.status]
            print(f"{icon} [{result.script_id}] {result.title}: {result.message}")
            if result.detail:
                print(result.detail)
                print()

    return report


def print_summary(report: SmokeReport) -> None:
    print("=" * 72)
    print("SMOKE TEST — backend/scripts/")
    print("=" * 72)
    for result in report.results:
        icon = {"pass": "PASS", "fail": "FAIL", "skip": "SKIP"}[result.status]
        print(f"[{icon:4}] {result.script_id:32} {result.message}")
    print("-" * 72)
    print(
        f"Total: {len(report.results)} | "
        f"PASS: {report.passed} | FAIL: {report.failed} | SKIP: {report.skipped}"
    )
    print("=" * 72)


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test semua skrip backend/scripts/")
    parser.add_argument(
        "--only",
        action="append",
        metavar="SCRIPT_ID",
        help="Jalankan hanya skrip tertentu (bisa diulang)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Tampilkan detail per kasus")
    parser.add_argument(
        "--allow-destructive",
        action="store_true",
        help="Jalankan demo_correlation_data dengan --reset-demo (hapus data bertanda DEMO dulu)",
    )
    parser.add_argument("--json", action="store_true", help="Keluaran summary sebagai JSON")
    args = parser.parse_args()

    only = set(args.only) if args.only else None
    report = run_smoke(only=only, verbose=args.verbose, allow_destructive=args.allow_destructive)

    if args.json:
        payload = {
            "passed": report.passed,
            "failed": report.failed,
            "skipped": report.skipped,
            "results": [
                {
                    "script_id": r.script_id,
                    "title": r.title,
                    "status": r.status,
                    "message": r.message,
                    "detail": r.detail,
                }
                for r in report.results
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print_summary(report)

    return 1 if report.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
