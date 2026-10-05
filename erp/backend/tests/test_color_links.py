"""Unit: lookup item ↔ CSI ↔ swatch lewat kode warna."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.color_code import extract_item_color_code, extract_item_color_qualifier
from app.services.color_links import (
    OVERLAY_QUALIFIERS,
    backfill_swatch_csi_exact,
    parse_color_link_query,
    serialize_color_links,
)


def test_extract_black_00a():
    assert extract_item_color_code("BLACK (00A)") == "00A"
    assert extract_item_color_qualifier("BLACK (00A)") is None


def test_parse_query_from_item_text():
    code, qualifier = parse_color_link_query(color="BLACK (00A)")
    assert code == "00A"
    assert qualifier is None


def test_parse_query_prefers_explicit_code():
    code, qualifier = parse_color_link_query(color="BLACK (00A)", color_code="01V")
    assert code == "01V"


def test_parse_fluorescent_qualifier():
    code, qualifier = parse_color_link_query(color="UNIVERSITY RED (65N) FLUORESCENT")
    assert code == "65N"
    assert qualifier == "FLUORESCENT"
    assert qualifier in OVERLAY_QUALIFIERS


def test_serialize_00a_links():
    csi = [
        SimpleNamespace(id=1, buyer_code="NIKE", color_code="00A", color_name="BLACK"),
    ]
    swatches = [
        SimpleNamespace(factory_key="FENGTAY"),
        SimpleNamespace(factory_key="POUYUEN"),
        SimpleNamespace(factory_key="FENGTAY"),
    ]
    body = serialize_color_links(
        color_code="00A",
        color_qualifier=None,
        color_text="BLACK (00A)",
        csi_rows=csi,
        swatch_rows=swatches,
        fluorescent_rows=[],
    )
    assert body["item_label"] == "BLACK (00A)"
    assert body["in_csi"] is True
    assert body["in_swatch"] is True
    assert body["swatch_count"] == 3
    assert body["swatch_factories"] == ["FENGTAY", "POUYUEN"]
    assert body["csi"][0]["buyer_code"] == "NIKE"
    assert body["fluorescent"] == []


def test_serialize_empty_code_not_linked():
    body = serialize_color_links(
        color_code="",
        color_qualifier=None,
        color_text="0AJ/6CD",
        csi_rows=[],
        swatch_rows=[],
        fluorescent_rows=[],
    )
    assert body["in_csi"] is False
    assert body["in_swatch"] is False
    assert body["swatch_count"] == 0


def test_serialize_fluorescent_overlay():
    fluo = [
        SimpleNamespace(
            id=9,
            buyer_code="NIKE",
            color_code="65N",
            color_name="UNIVERSITY RED",
            season_label="SS26",
            color_class="fluorescent",
        )
    ]
    body = serialize_color_links(
        color_code="65N",
        color_qualifier="FLUORESCENT",
        color_text="UNIVERSITY RED (65N) FLUORESCENT",
        csi_rows=[],
        swatch_rows=[],
        fluorescent_rows=fluo,
    )
    assert body["color_qualifier"] == "FLUORESCENT"
    assert body["fluorescent"][0]["season_label"] == "SS26"


def test_backfill_exact_join_does_not_seed_csi():
    db = MagicMock()
    db.execute.return_value.rowcount = 3
    db.scalar.return_value = 471
    stats = backfill_swatch_csi_exact(db)
    assert stats["linked"] == 3
    assert stats["orphan_remaining"] == 471
    sql = str(db.execute.call_args[0][0])
    assert "JOIN csi_color_masters" in sql
    assert "csi_color_master_id IS NULL" in sql
    assert "INSERT" not in sql.upper()
