"""HTTP integration tests for invoice router guards."""

from tests.http_fixtures import (
    assert_status,
    clear_api_overrides,
    clear_auth_user,
    make_api_client,
    set_auth_user,
)

_PREFIX = "/api/v1"


def test_invoice_list_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/invoice", 401)
    finally:
        clear_api_overrides()


def test_invoice_create_guest_forbidden():
    client = make_api_client()
    set_auth_user("guest")
    try:
        assert_status(client, "POST", f"{_PREFIX}/invoice", 403, {"delivery_id": 1})
    finally:
        clear_api_overrides()


def test_invoice_get_missing_404():
    client = make_api_client()
    set_auth_user("finance")
    try:
        assert_status(client, "GET", f"{_PREFIX}/invoice/999", 404)
    finally:
        clear_api_overrides()
