from dataclasses import dataclass

from fastapi.testclient import TestClient

from app.db import get_db
from app.main import app
from app.routers.auth import get_current_user


class _DummyDbSession:
    def get(self, _model, _id):
        return None


@dataclass
class _DummyUser:
    username: str
    role: str
    is_active: bool = True


def _override_db():
    yield _DummyDbSession()


def _make_client() -> TestClient:
    app.dependency_overrides[get_db] = _override_db
    return TestClient(app)


def _set_user(role: str, username: str = "tester") -> None:
    app.dependency_overrides[get_current_user] = lambda: _DummyUser(
        username=username,
        role=role,
    )


def _assert_status(client: TestClient, method: str, path: str, expected: int, payload=None) -> None:
    req = getattr(client, method.lower())
    resp = req(path, json=payload) if payload is not None else req(path)
    assert resp.status_code == expected, f"{method} {path} expected {expected}, got {resp.status_code}"


def test_admin_routes_require_auth_token():
    client = _make_client()
    app.dependency_overrides.pop(get_current_user, None)
    try:
        _assert_status(client, "GET", "/api/v1/customs/declarations", 401)
        _assert_status(client, "GET", "/api/v1/exchange-rates", 401)
        _assert_status(client, "GET", "/api/v1/buyer-prices/lists", 401)
    finally:
        app.dependency_overrides.clear()


def test_write_routes_reject_guest_role_with_403():
    client = _make_client()
    _set_user("guest")
    try:
        _assert_status(
            client,
            "POST",
            "/api/v1/customs/declarations",
            403,
            {"nomor_aju": "AJU-TEST-001"},
        )
        _assert_status(
            client,
            "POST",
            "/api/v1/buyer-prices/lists",
            403,
            {"buyer_code": "BYR001"},
        )
        _assert_status(
            client,
            "POST",
            "/api/v1/sales-orders",
            403,
            {"po_category": "production"},
        )
        _assert_status(
            client,
            "POST",
            "/api/v1/exchange-rates",
            403,
            {"idr_per_usd": "16000", "effective_date": "2026-04-08"},
        )
    finally:
        app.dependency_overrides.clear()


def test_allowed_roles_pass_guard_and_reach_handler_logic():
    client = _make_client()
    try:
        # Role valid harus lolos guard; dengan DB stub akan lanjut ke 404 (bukan 403).
        _set_user("exim", "exim-user")
        _assert_status(
            client,
            "PUT",
            "/api/v1/customs/declarations/1",
            404,
            {"kode_dokumen": "BC23"},
        )

        _set_user("marketing", "mkt-user")
        _assert_status(
            client,
            "PUT",
            "/api/v1/buyer-prices/lists/1",
            404,
            {"title": "Revisi April"},
        )

        _assert_status(
            client,
            "POST",
            "/api/v1/sales-orders/1/details",
            404,
            {},
        )
    finally:
        app.dependency_overrides.clear()

