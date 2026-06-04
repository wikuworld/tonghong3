"""HTTP integration tests for production router guards."""

from tests.http_fixtures import (
    assert_status,
    clear_api_overrides,
    clear_auth_user,
    make_api_client,
    set_auth_user,
)

_PREFIX = "/api/v1"


def test_production_list_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/production", 401)
    finally:
        clear_api_overrides()


def test_production_create_guest_forbidden():
    client = make_api_client()
    set_auth_user("guest")
    try:
        assert_status(client, "POST", f"{_PREFIX}/production", 403, {"po_id": 1})
    finally:
        clear_api_overrides()


def test_production_get_missing_404():
    client = make_api_client()
    set_auth_user("production")
    try:
        assert_status(client, "GET", f"{_PREFIX}/production/999", 404)
    finally:
        clear_api_overrides()


def test_production_details_missing_parent_404():
    client = make_api_client()
    set_auth_user("production")
    try:
        assert_status(client, "GET", f"{_PREFIX}/production/999/details", 404)
    finally:
        clear_api_overrides()
