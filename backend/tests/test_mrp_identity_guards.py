"""Guardrail: identitas SO–MRP hanya source_detail_id, bukan merge spek."""

from pathlib import Path

from app.models import PoHeader
from app.services.po_list_summary import attach_mrp_sync_errors

ROOT = Path(__file__).resolve().parents[2]
API_ROUTES = (ROOT / "mrp" / "api_routes.py").read_text(encoding="utf-8")
FG_BRIDGE = (ROOT / "backend" / "app" / "services" / "mrp_fg_delivery_bridge.py").read_text(
    encoding="utf-8"
)


def test_master_po_sync_looks_up_by_source_detail_only():
    assert "WHERE source_detail_id=%s LIMIT 1" in API_ROUTES
    assert "no_po=%s AND item_name=%s AND warna=%s" not in API_ROUTES
    assert "source_detail_id wajib; sync tidak boleh merge spek" in API_ROUTES


def test_packing_resolve_does_not_use_no_po_limit_1():
    assert "Wajib po_id (tbl_master_po.id) atau source_detail_id" in API_ROUTES
    assert "WHERE no_po=%s ORDER BY id DESC LIMIT 1" not in API_ROUTES


def test_packing_report_no_so_not_limit_1_by_no_po():
    assert "WHERE po.no_po = p.no_po AND po.no_so IS NOT NULL" not in API_ROUTES
    assert "def _sql_no_so_for_packing" in API_ROUTES
    assert "tbl_packing_po" in API_ROUTES


def test_packing_bridge_context_returns_all_lines():
    assert '"lines": lines' in API_ROUTES
    assert "ORDER BY p.id ASC" in API_ROUTES


def test_fg_out_does_not_create_delivery():
    assert "FG_OUT_MUST_USE_OUTSTANDING" in FG_BRIDGE
    assert "create_from_mrp_fg_out" not in FG_BRIDGE
    assert "ProductionDetail.lot_number == wip" in FG_BRIDGE
    assert "ORDER BY ProductionDetail.id DESC" not in FG_BRIDGE


def test_attach_mrp_sync_error_badge():
    po = PoHeader(id=7, po_number="THI-1")
    db = type("DB", (), {})()

    class Q:
        def filter(self, *a, **k):
            return self

        def order_by(self, *a, **k):
            return self

        def all(self):
            return [(7, "upstream down", 99)]

    db.query = lambda *a, **k: Q()
    attach_mrp_sync_errors(db, [po])
    assert po.mrp_sync_error == "upstream down"
