"""HTTP integration tests for delivery router guards and validation."""

from types import SimpleNamespace

from app.models import DeliveryHeader

from tests.http_fixtures import (
    DummyDbSession,
    assert_status,
    clear_api_overrides,
    clear_auth_user,
    make_api_client,
    set_auth_user,
)

_PREFIX = "/api/v1"


def test_delivery_list_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/delivery", 401)
    finally:
        clear_api_overrides()


def test_delivery_create_guest_forbidden():
    client = make_api_client()
    set_auth_user("guest")
    try:
        assert_status(client, "POST", f"{_PREFIX}/delivery", 403, {"packing_id": 1})
    finally:
        clear_api_overrides()


def test_delivery_get_missing_404():
    client = make_api_client()
    set_auth_user("warehouse")
    try:
        assert_status(client, "GET", f"{_PREFIX}/delivery/999", 404)
    finally:
        clear_api_overrides()


def test_delivery_add_detail_no_qc_400():
    hdr = SimpleNamespace(id=1, status="draft")

    def _get(model, obj_id):
        if model is DeliveryHeader and obj_id == 1:
            return hdr
        return None

    db = DummyDbSession(get_handler=_get)
    client = make_api_client(db)
    set_auth_user("warehouse")
    try:
        assert_status(
            client,
            "POST",
            f"{_PREFIX}/delivery/1/details",
            400,
            {"production_detail_id": 10, "qty": 5},
        )
    finally:
        clear_api_overrides()


def test_delivery_add_detail_bypass_qc_non_admin_403():
    hdr = SimpleNamespace(id=1, status="draft")

    def _get(model, obj_id):
        if model is DeliveryHeader and obj_id == 1:
            return hdr
        return None

    client = make_api_client(DummyDbSession(get_handler=_get))
    set_auth_user("warehouse")
    try:
        assert_status(
            client,
            "POST",
            f"{_PREFIX}/delivery/1/details",
            403,
            {"production_detail_id": 10, "qty": 5},
            params={"bypass_qc": "true"},
        )
    finally:
        clear_api_overrides()


def test_delivery_mark_sj_printed_missing_404():
    client = make_api_client()
    set_auth_user("marketing")
    try:
        assert_status(client, "POST", f"{_PREFIX}/delivery/999/mark-surat-jalan-printed", 404)
    finally:
        clear_api_overrides()
