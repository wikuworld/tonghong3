"""Baris PO harus ikut identitas dan kode warna master item."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.services.po_master_line import align_po_line_to_master_item


def _item(**kwargs):
    base = dict(
        material_name="ACTION LEATHER",
        color="CORE BLACK (A0QM)",
        emboss="AW-44 SG",
        thickness_range="1.2-1.4",
        color_code="A0QM",
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_empty_color_reference_filled_from_master_code():
    db = MagicMock()
    db.get.return_value = _item()
    assert (
        align_po_line_to_master_item(
            db,
            master_item_id=2032,
            material_name="ACTION LEATHER",
            color="CORE BLACK (A0QM)",
            emboss="AW-44 SG",
            thickness_text="1.2 - 1.4",
            color_reference=None,
        )
        == "A0QM"
    )


def test_wrong_color_reference_rejected():
    db = MagicMock()
    db.get.return_value = _item()
    with pytest.raises(HTTPException) as exc:
        align_po_line_to_master_item(
            db,
            master_item_id=2032,
            material_name="ACTION LEATHER",
            color="CORE BLACK (A0QM)",
            emboss="AW-44 SG",
            thickness_text="1.2 - 1.4",
            color_reference="6HV",
        )
    assert exc.value.status_code == 400


def test_csi_style_color_reference_accepted_when_code_matches():
    db = MagicMock()
    db.get.return_value = _item(color="COURT GREEN (3HK)", color_code="3HK")
    assert (
        align_po_line_to_master_item(
            db,
            master_item_id=2032,
            material_name="ACTION LEATHER",
            color="COURT GREEN (3HK)",
            emboss="AW-44 SG",
            thickness_text="1.2-1.4",
            color_reference="COURT GREEN (3HK)",
        )
        == "3HK"
    )


def test_waiting_cs_skips_all_master_identity_checks():
    db = MagicMock()
    db.get.return_value = _item(color_code="55V")
    assert (
        align_po_line_to_master_item(
            db,
            master_item_id=2032,
            material_name="WRONG MATERIAL",
            color="WRONG COLOR",
            emboss="WRONG EMBOSS",
            thickness_text="9.9-9.9",
            color_reference="WAITING C/S",
            color_standard="WAITING C/S",
        )
        == "WAITING C/S"
    )


def test_waiting_color_reference_allowed_without_master_code_match():
    db = MagicMock()
    db.get.return_value = _item(color_code="55V")
    assert (
        align_po_line_to_master_item(
            db,
            master_item_id=2032,
            material_name="ACTION LEATHER",
            color="CORE BLACK (A0QM)",
            emboss="AW-44 SG",
            thickness_text="1.2-1.4",
            color_reference="WAITING C/S",
        )
        == "WAITING C/S"
    )


def test_material_mismatch_rejected():
    db = MagicMock()
    db.get.return_value = _item()
    with pytest.raises(HTTPException) as exc:
        align_po_line_to_master_item(
            db,
            master_item_id=2032,
            material_name="GENERIC PU COATED LEATHER",
            color="CORE BLACK (A0QM)",
            emboss="AW-44 SG",
            thickness_text="1.2-1.4",
            color_reference="A0QM",
        )
    assert exc.value.status_code == 400
    assert "material" in exc.value.detail


def test_dateish_color_reference_replaced_with_master_code():
    """Created at Color Window (mis. 24/10/2024) tidak boleh dianggap kode warna."""
    db = MagicMock()
    db.get.return_value = _item(color="BLACK (145-17-00)", color_code="145-17-00")
    assert (
        align_po_line_to_master_item(
            db,
            master_item_id=32,
            material_name="ACTION LEATHER",
            color="BLACK (145-17-00)",
            emboss="AW-44 SG",
            thickness_text="1.2-1.4",
            color_reference="24/10/2024",
        )
        == "145-17-00"
    )


def test_color_window_label_kept_when_code_matches():
    db = MagicMock()
    db.get.return_value = _item(color="BLACK (145-17-00)", color_code="145-17-00")
    assert (
        align_po_line_to_master_item(
            db,
            master_item_id=32,
            material_name="ACTION LEATHER",
            color="BLACK (145-17-00)",
            emboss="AW-44 SG",
            thickness_text="1.2-1.4",
            color_reference="BLACK COLORO (145-17-00)",
            color_standard="COLOR WINDOW",
        )
        == "BLACK COLORO (145-17-00)"
    )


def test_color_window_does_not_reject_nonmatching_window_code():
    db = MagicMock()
    db.get.return_value = _item(color="BLACK (145-17-00)", color_code="145-17-00")
    assert (
        align_po_line_to_master_item(
            db,
            master_item_id=32,
            material_name="ACTION LEATHER",
            color="BLACK (145-17-00)",
            emboss="AW-44 SG",
            thickness_text="1.2-1.4",
            color_reference="BLACK COLORO (039-90-05)",
            color_standard="COLOR WINDOW",
        )
        == "BLACK COLORO (039-90-05)"
    )
