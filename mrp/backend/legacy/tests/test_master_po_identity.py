"""Identitas packing/sync: po_id atau source_detail_id, bukan no_po LIMIT 1."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api_routes import (  # noqa: E402
    _resolve_master_po_for_packing,
    _sql_no_so_for_packing,
    _sql_no_so_from_master,
)


def test_resolve_without_ids_returns_none():
    cur = MagicMock()
    assert _resolve_master_po_for_packing(cur, {"no_po": "CUST-1", "kode_wip": "WIP-1"}) is None
    cur.execute.assert_not_called()


def test_resolve_by_po_id():
    cur = MagicMock()
    cur.fetchone.return_value = {"id": 4, "no_po": "CUST-1", "no_so": "SO-1", "source_detail_id": 11}
    row = _resolve_master_po_for_packing(cur, {"po_id": 4, "no_po": "OTHER"})
    assert row["id"] == 4
    sql = cur.execute.call_args[0][0]
    assert "WHERE id=%s" in sql
    assert cur.execute.call_args[0][1] == (4,)


def test_resolve_by_source_detail_id():
    cur = MagicMock()
    cur.fetchone.return_value = {"id": 9, "no_po": "CUST-2", "source_detail_id": 22}
    row = _resolve_master_po_for_packing(cur, {"source_detail_id": 22})
    assert row["source_detail_id"] == 22
    sql = cur.execute.call_args[0][0]
    assert "source_detail_id=%s" in sql
    assert "WHERE no_po" not in sql


def test_sql_no_so_from_wip_not_limit_1_by_no_po():
    sql = _sql_no_so_from_master("pk")
    assert "LIMIT 1" not in sql.upper()
    assert "kode_lot_wip" in sql
    assert "no_po =" not in sql


def test_sql_no_so_for_packing_uses_po_id():
    sql = _sql_no_so_for_packing("p")
    assert "tbl_packing_po" in sql
    assert "pp.po_id" in sql or "mp.id = pp.po_id" in sql
    assert "LIMIT 1" not in sql.upper()
    assert "kode_lot_wip" in sql
