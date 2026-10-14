"""Unit: material group inference untuk lot SubKon."""

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.models import MasterItem
from app.services.lot_numbers import infer_material_group


def _master_item(**kwargs) -> MasterItem:
    return MasterItem(id=1, item_code="SUB0001", **kwargs)


def test_subkon_suede_material_maps_to_suede_group():
    mi = _master_item(category="SubKon", material_name="SPLIT SUEDE")
    assert infer_material_group(master_item=mi) == "suede"


def test_subkon_action_leather_maps_to_pu_group():
    mi = _master_item(category="SubKon", material_name="PRO ACTION LEATHER")
    assert infer_material_group(master_item=mi) == "pu"


def test_subkon_cow_leather_maps_to_suede_group():
    mi = _master_item(category="SubKon", material_name="COW LEATHER")
    assert infer_material_group(master_item=mi) == "suede"


def test_existing_pu_and_suide_categories_unchanged():
    assert infer_material_group(master_item=_master_item(category="PU", material_name="VIRGIN HYDRO PU")) == "pu"
    assert infer_material_group(master_item=_master_item(category="Suede", material_name="SPLIT SUEDE")) == "suede"


def test_fallback_by_material_name_without_master_item():
    assert infer_material_group(material_name="HI SUEDE") == "suede"
    assert infer_material_group(material_name="VIRGIN HYDRO PU") == "pu"


def test_unknown_material_raises():
    with pytest.raises(HTTPException) as exc:
        infer_material_group(material_name="UNKNOWN FABRIC")
    assert exc.value.status_code == 400


def test_subkon_detail_with_master_item():
    mi = _master_item(category="SubKon", material_name="EMBOSSED SUEDE")
    db = MagicMock()
    db.get.return_value = mi
    from app.models import PoDetail
    from app.services.lot_numbers import _material_group_from_detail

    detail = PoDetail(id=1, master_item_id=1, material_name="EMBOSSED SUEDE")
    assert _material_group_from_detail(db, detail) == "suede"
