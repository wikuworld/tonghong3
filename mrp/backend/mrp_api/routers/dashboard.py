from __future__ import annotations

from sqlalchemy import text

from fastapi import APIRouter, Depends

from mrp_api.db import engine
from mrp_api.models import MrpUser
from mrp_api.routers.auth import get_current_user

router = APIRouter(tags=["dashboard"])


def _scalar(sql: str, default=0):
    try:
        with engine.connect() as conn:
            val = conn.execute(text(sql)).scalar()
        return default if val is None else val
    except Exception:
        return default


def _rows(sql: str) -> list[dict]:
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            return [dict(row) for row in result.mappings()]
    except Exception:
        return []


@router.get("/dashboard/summary")
def dashboard_summary(_user: MrpUser = Depends(get_current_user)):
    return {
        "rencana_total": int(_scalar("SELECT COUNT(*) FROM tbl_rencana_produksi")),
        "rencana_active": int(
            _scalar("SELECT COUNT(*) FROM tbl_rencana_produksi WHERE status IN ('draft','active')")
        ),
        "po_outstanding": int(
            _scalar("SELECT COUNT(*) FROM tbl_master_po WHERE status IN ('outstanding','partial')")
        ),
        "proses_open": int(
            _scalar(
                "SELECT COUNT(*) FROM tbl_persiapan_kulit WHERE status IN ('draft','started','saved')"
            )
        ),
        "lab_lots": int(_scalar("SELECT COUNT(*) FROM tbl_lab_lot")),
        "packing_in_progress": int(
            _scalar("SELECT COUNT(*) FROM tbl_packing WHERE status='in_progress'")
        ),
        "packing_finished": int(
            _scalar("SELECT COUNT(*) FROM tbl_packing WHERE status='finished'")
        ),
        "fg_in_stock": int(
            _scalar("SELECT COUNT(*) FROM tbl_gudang_fg WHERE status='in_stock'")
        ),
        "stok_kimia_lots": int(
            _scalar("SELECT COUNT(*) FROM tbl_stok_kimia_in WHERE qty_sisa > 0")
        ),
        "stok_rp_lots": int(
            _scalar("SELECT COUNT(*) FROM tbl_stok_rp_in WHERE qty_sisa > 0")
        ),
        "recent_rencana": _rows(
            "SELECT id, kode_rencana, nama_rencana, status, tanggal_rencana "
            "FROM tbl_rencana_produksi ORDER BY id DESC LIMIT 8"
        ),
        "recent_packing": _rows(
            "SELECT id, kode_packing, customer, status, total_ukuran, date_created "
            "FROM tbl_packing ORDER BY id DESC LIMIT 8"
        ),
    }
