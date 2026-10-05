"""Unit tests: ERP service token (X-Internal-Api-Key) auth."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_service_api_key_authenticates(monkeypatch):
    from app.config import settings
    from app.main import app
    from app.routers.auth import SERVICE_MRP_USERNAME

    monkeypatch.setattr(settings, "erp_service_token", "test-token-xyz")
    client = TestClient(app)
    r = client.get("/api/v1/auth/me", headers={"X-Internal-Api-Key": "test-token-xyz"})
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == SERVICE_MRP_USERNAME
    assert body["role"] == "ppic"


def test_service_api_key_rejects_bad_token(monkeypatch):
    from app.config import settings
    from app.main import app

    monkeypatch.setattr(settings, "erp_service_token", "test-token-xyz")
    client = TestClient(app)
    r = client.get("/api/v1/auth/me", headers={"X-Internal-Api-Key": "wrong"})
    assert r.status_code == 401


def test_materials_filter_accepted(monkeypatch):
    """Smoke: materials list accepts material_type/code query (auth via service key)."""
    from app.config import settings
    from app.main import app

    monkeypatch.setattr(settings, "erp_service_token", "test-token-xyz")
    client = TestClient(app)
    r = client.get(
        "/api/v1/inventory/materials",
        params={"material_type": "kimia", "code": "NOPE", "limit": 5},
        headers={"X-Internal-Api-Key": "test-token-xyz"},
    )
    # 200 with empty list, or 500 if DB down — auth must not be 401/403
    assert r.status_code != 401
    assert r.status_code != 403


def test_customers_resolve_route_exists(monkeypatch):
    from app.config import settings
    from app.main import app

    monkeypatch.setattr(settings, "erp_service_token", "test-token-xyz")
    client = TestClient(app)
    r = client.get(
        "/api/v1/customers/resolve",
        params={"q": "__nonexistent_customer_xyz__"},
        headers={"X-Internal-Api-Key": "test-token-xyz"},
    )
    assert r.status_code != 401
    assert r.status_code != 404  # route exists; body may be null
    assert r.status_code in (200, 500)


def test_po_details_lot_refs_route(monkeypatch):
    from app.config import settings
    from app.main import app

    monkeypatch.setattr(settings, "erp_service_token", "test-token-xyz")
    client = TestClient(app)
    r = client.get(
        "/api/v1/po-details/lot-refs",
        params={"ids": "1,2"},
        headers={"X-Internal-Api-Key": "test-token-xyz"},
    )
    assert r.status_code != 401
    assert r.status_code != 404
