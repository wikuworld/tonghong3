"""Unit tests: MRP erp_client + inventory write block."""

from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient


def test_erp_client_resolve_customer_maps_response():
    from mrp_api import erp_client

    fake = {"id": 7, "code": "ACME", "name": "Acme Corp"}
    with patch.object(erp_client, "get", return_value=fake) as mock_get:
        row = erp_client.resolve_customer("Acme", create=False)
        assert row == fake
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == "/customers/resolve"
        assert kwargs["params"]["q"] == "Acme"
        assert kwargs["params"]["create"] is False


def test_erp_client_list_materials_passes_filters():
    from mrp_api import erp_client

    with patch.object(erp_client, "get", return_value=[{"id": 1, "code": "K1"}]) as mock_get:
        rows = erp_client.list_materials(material_type="kimia", code="K1", limit=10)
        assert len(rows) == 1
        params = mock_get.call_args.kwargs["params"]
        assert params["material_type"] == "kimia"
        assert params["code"] == "K1"


def test_erp_client_po_detail_mrp_lines_by_lots():
    from mrp_api import erp_client

    with patch.object(
        erp_client,
        "get",
        return_value={
            "lines": {
                "PUMTH26001260929010": {
                    "source_detail_id": "99",
                    "material_name": "VIRGIN HYDRO PU",
                    "lot_ref": "PUMTH26001260929010",
                    "no_so": "THIPM26092905",
                    "no_po": "PO-THIPM26092905",
                }
            }
        },
    ):
        out = erp_client.po_detail_mrp_lines_by_lots(["PUMTH26001260929010"])
        assert out["PUMTH26001260929010"]["material_name"] == "VIRGIN HYDRO PU"


def test_erp_client_po_detail_mrp_lines():
    from mrp_api import erp_client

    with patch.object(
        erp_client,
        "get",
        return_value={
            "lines": {
                "35": {
                    "material_name": "VIRGIN HYDRO PU",
                    "lot_ref": "PUMTH26001260929010",
                    "no_so": "THIPM26092905",
                    "no_po": "PO-THIPM26092905",
                }
            }
        },
    ):
        out = erp_client.po_detail_mrp_lines([35])
        assert out[35]["material_name"] == "VIRGIN HYDRO PU"
        assert out[35]["lot_ref"] == "PUMTH26001260929010"


def test_erp_client_po_detail_lot_refs():
    from mrp_api import erp_client

    with patch.object(
        erp_client, "get", return_value={"refs": {"11": "LOT-A", "12": "LOT-B"}}
    ):
        out = erp_client.po_detail_lot_refs([11, 12])
        assert out[11] == "LOT-A"
        assert out[12] == "LOT-B"


def test_mrp_inventory_write_blocked():
    from mrp_api.main import app as mrp_app
    from mrp_api.models import MrpUser
    from mrp_api.routers import auth as mrp_auth

    def _fake_user():
        return MrpUser(
            id=1,
            username="admin",
            password_hash="!",
            role="admin",
            is_active=True,
        )

    mrp_app.dependency_overrides[mrp_auth.get_current_user] = _fake_user
    client = TestClient(mrp_app)
    try:
        r = client.post(
            "/api/v1/inventory/warehouses",
            json={"code": "X", "name": "X"},
        )
        assert r.status_code == 403
    finally:
        mrp_app.dependency_overrides.clear()
