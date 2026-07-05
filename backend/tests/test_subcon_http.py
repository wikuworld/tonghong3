"""HTTP integration tests for subcon invoice router guards."""

from tests.http_fixtures import (
    assert_status,
    clear_api_overrides,
    clear_auth_user,
    make_api_client,
    set_auth_user,
)

_PREFIX = "/api/v1"


def test_subcon_list_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/subcon-invoices", 401)
    finally:
        clear_api_overrides()


def test_subcon_create_guest_forbidden():
    client = make_api_client()
    set_auth_user("guest")
    try:
        assert_status(
            client,
            "POST",
            f"{_PREFIX}/subcon-invoices",
            403,
            {"po_id": 1, "invoice_type": "barang", "amount": 0},
        )
    finally:
        clear_api_overrides()


def test_subcon_get_missing_404():
    client = make_api_client()
    set_auth_user("finance")
    try:
        assert_status(client, "GET", f"{_PREFIX}/subcon-invoices/999", 404)
    finally:
        clear_api_overrides()


def test_subcon_generate_from_po_missing_404():
    client = make_api_client()
    set_auth_user("finance")
    try:
        assert_status(client, "POST", f"{_PREFIX}/subcon-invoices/generate-from-po/999", 404)
    finally:
        clear_api_overrides()
