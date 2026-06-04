"""HTTP integration tests for PO router guards and basic handler paths."""

from types import SimpleNamespace

from app.models import PoDetail

from tests.http_fixtures import (
    DummyDbSession,
    assert_status,
    clear_api_overrides,
    clear_auth_user,
    make_api_client,
    set_auth_user,
)

_PREFIX = "/api/v1"


def test_po_list_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/po", 401)
    finally:
        clear_api_overrides()


def test_po_create_guest_forbidden():
    client = make_api_client()
    set_auth_user("guest")
    try:
        assert_status(
            client,
            "POST",
            f"{_PREFIX}/po",
            403,
            {"po_category": "production", "customer_id": 1},
        )
    finally:
        clear_api_overrides()


def test_po_get_missing_returns_404():
    client = make_api_client()
    set_auth_user("marketing")
    try:
        assert_status(client, "GET", f"{_PREFIX}/po/999", 404)
    finally:
        clear_api_overrides()


def test_po_delete_non_admin_forbidden():
    client = make_api_client()
    set_auth_user("marketing")
    try:
        assert_status(client, "DELETE", f"{_PREFIX}/po/1", 403)
    finally:
        clear_api_overrides()


def test_po_workflow_advance_wrong_role():
    client = make_api_client()
    set_auth_user("warehouse")
    try:
        assert_status(client, "POST", f"{_PREFIX}/po/1/mkt-workflow/advance", 403)
    finally:
        clear_api_overrides()


def test_po_mkt_workflow_stages_ok():
    client = make_api_client()
    set_auth_user("marketing")
    try:
        resp = client.get(f"{_PREFIX}/po/mkt-workflow-stages")
        assert resp.status_code == 200
        body = resp.json()
        assert "stages" in body
        assert isinstance(body["stages"], list)
        assert len(body["stages"]) >= 1
    finally:
        clear_api_overrides()


def test_po_delivery_schedules_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/po-detail/1/delivery-schedules", 401)
    finally:
        clear_api_overrides()


def test_po_delivery_schedules_missing_detail_404():
    client = make_api_client()
    set_auth_user("marketing")
    try:
        assert_status(client, "GET", f"{_PREFIX}/po-detail/999/delivery-schedules", 404)
    finally:
        clear_api_overrides()


def test_po_delivery_schedules_returns_rows():
    schedule = SimpleNamespace(id=1, po_detail_id=5, sequence_no=1, qty=10, delivery_date=None)
    detail = SimpleNamespace(delivery_schedules=[schedule])

    def _get(model, obj_id):
        if model is PoDetail and obj_id == 5:
            return detail
        return None

    client = make_api_client(DummyDbSession(get_handler=_get))
    set_auth_user("marketing")
    try:
        resp = client.get(f"{_PREFIX}/po-detail/5/delivery-schedules")
        assert resp.status_code == 200
        assert resp.json()[0]["sequence_no"] == 1
    finally:
        clear_api_overrides()

