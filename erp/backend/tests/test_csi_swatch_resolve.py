"""Tes resolve CSI ke field swatch — salin dari CSI, orphan tetap NULL."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.csi_color import apply_csi_to_swatch_fields, resolve_csi_by_buyer_code


def test_apply_csi_copies_code_and_name_when_empty():
    csi = SimpleNamespace(id=9, is_active=True, color_code="01V", color_name="WOLF GREY")
    db = MagicMock()
    db.get.return_value = csi
    csi_id, code, name = apply_csi_to_swatch_fields(
        db,
        csi_id=9,
        buyer_code="NIKE",
        color_code="",
        color_name="",
    )
    assert csi_id == 9
    assert code == "01V"
    assert name == "WOLF GREY"


def test_apply_csi_keeps_manual_override():
    csi = SimpleNamespace(id=9, is_active=True, color_code="01V", color_name="WOLF GREY")
    db = MagicMock()
    db.get.return_value = csi
    csi_id, code, name = apply_csi_to_swatch_fields(
        db,
        csi_id=9,
        buyer_code="NIKE",
        color_code="xx",
        color_name="yy",
    )
    assert csi_id == 9
    assert code == "xx"
    assert name == "yy"


def test_apply_csi_resolve_by_buyer_code():
    csi = SimpleNamespace(id=4, is_active=True, color_code="00A", color_name="BLACK")
    db = MagicMock()
    db.get.return_value = None
    db.scalars.return_value.first.return_value = csi
    csi_id, code, name = apply_csi_to_swatch_fields(
        db,
        csi_id=None,
        buyer_code="NIKE",
        color_code="00A",
        color_name="BLACK ANODIZED",
    )
    assert csi_id == 4
    assert code == "00A"
    assert name == "BLACK ANODIZED"


def test_orphan_puma_stays_unlinked():
    db = MagicMock()
    db.get.return_value = None
    db.scalars.return_value.first.return_value = None
    csi_id, code, name = apply_csi_to_swatch_fields(
        db,
        csi_id=None,
        buyer_code="PUMA",
        color_code="123",
        color_name="RED",
    )
    assert csi_id is None
    assert code == "123"
    assert name == "RED"
    assert resolve_csi_by_buyer_code(db, "PUMA", "123") is None
