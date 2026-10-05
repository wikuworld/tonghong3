"""Unit tests for dual warehouse (utama|lapangan) mapping."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dual_gudang import (  # noqa: E402
    GUDANG_LAPANGAN,
    GUDANG_UTAMA,
    gudang_match_sql,
    is_utama_to_lapangan_out,
    normalize_gudang,
    parse_gudang_filter,
    should_spawn_lapangan_transfer_lot,
)


def test_normalize_legacy_kimia_mixing():
    assert normalize_gudang("kimia") == GUDANG_UTAMA
    assert normalize_gudang("mixing") == GUDANG_LAPANGAN
    assert normalize_gudang("KIMIA") == GUDANG_UTAMA
    assert normalize_gudang("Mixing") == GUDANG_LAPANGAN


def test_normalize_canonical():
    assert normalize_gudang("utama") == GUDANG_UTAMA
    assert normalize_gudang("lapangan") == GUDANG_LAPANGAN
    assert normalize_gudang(None) == GUDANG_UTAMA
    assert normalize_gudang("") == GUDANG_UTAMA


def test_parse_gudang_filter():
    assert parse_gudang_filter("utama") == GUDANG_UTAMA
    assert parse_gudang_filter("mixing") == GUDANG_LAPANGAN
    assert parse_gudang_filter("all") is None
    assert parse_gudang_filter(None) is None
    assert parse_gudang_filter("") is None


def test_is_utama_to_lapangan_out():
    assert is_utama_to_lapangan_out(from_gudang=GUDANG_UTAMA, tujuan="lapangan")
    assert is_utama_to_lapangan_out(from_gudang=GUDANG_UTAMA, tujuan="mixing")
    assert not is_utama_to_lapangan_out(from_gudang=GUDANG_UTAMA, tujuan="produksi")
    assert not is_utama_to_lapangan_out(from_gudang=GUDANG_LAPANGAN, tujuan="lapangan")
    assert should_spawn_lapangan_transfer_lot(
        from_gudang=GUDANG_UTAMA, tujuan="lapangan", new_sisa=0
    )


def test_gudang_match_sql():
    clause, params = gudang_match_sql("si.gudang", GUDANG_LAPANGAN)
    assert "si.gudang IN" in clause
    assert params == [GUDANG_LAPANGAN, "mixing"]
    clause_u, params_u = gudang_match_sql("si.gudang", GUDANG_UTAMA)
    assert "kimia" in params_u
    assert "utama" in params_u
