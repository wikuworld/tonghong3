"""HTTP-level smoke for color swatch lookup (global per buyer)."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.db import get_db
from app.main import app
from app.routers.auth import get_current_user


def _override_user():
    return MagicMock(username="admin", role="admin")


def _fake_recipe(**kwargs):
    defaults = {
        "id": 1,
        "factory_key": "NIKOMAS",
        "customer_id": None,
        "buyer_code": "NIKE",
        "brand_id": None,
        "csi_color_master_id": None,
        "color_code": "01V",
        "color_name": "WOLF GREY",
        "emboss": "DE-7",
        "color_standard": "SCOTDIC",
        "backing": "WHITE",
        "material_name": "VIRGIN HYDRO PU",
        "legacy_urut": None,
        "entered_at": None,
        "source_file": None,
        "is_active": True,
        "created_at": None,
        "updated_at": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_lookup_swatch_without_factory_ok():
    """SO boleh lookup hanya dengan buyer_code — tanpa factory/customer."""
    fake_row = _fake_recipe()
    db = MagicMock()
    db.scalars.return_value.all.return_value = [fake_row]
    db.get.return_value = None

    app.dependency_overrides[get_current_user] = _override_user
    app.dependency_overrides[get_db] = lambda: db
    try:
        client = TestClient(app)
        with patch(
            "app.routers.color_swatch.filter_swatch_recipes_by_dimensions",
            side_effect=lambda rows, **kwargs: rows,
        ), patch(
            "app.routers.color_swatch._recipe_to_out",
            side_effect=lambda _db, recipe: {
                "id": recipe.id,
                "factory_key": recipe.factory_key,
                "buyer_code": recipe.buyer_code,
                "color_code": recipe.color_code,
                "color_name": recipe.color_name,
                "emboss": recipe.emboss,
                "material_name": recipe.material_name,
                "is_active": True,
            },
        ):
            # Endpoint returns ORM rows; FastAPI serializes via response_model.
            # Patch response path: call endpoint logic indirectly via client —
            # ColorSwatchRecipeOut.from_attributes on SimpleNamespace works if all fields set.
            r = client.get(
                "/api/v1/masters/color-swatch-recipes/lookup",
                params={"buyer_code": "NIKE", "limit": 10},
            )
        assert r.status_code == 200, r.text
        body = r.json()
        assert isinstance(body, list)
        assert len(body) == 1
        assert body[0]["factory_key"] == "NIKOMAS"
        assert body[0]["buyer_code"] == "NIKE"
    finally:
        app.dependency_overrides.clear()
