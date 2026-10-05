"""HTTP integration tests for marketing router guards."""

from tests.http_fixtures import (
    assert_status,
    clear_api_overrides,
    clear_auth_user,
    make_api_client,
    set_auth_user,
)

_PREFIX = "/api/v1"


def test_marketing_outstanding_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/marketing/outstanding-lines", 401)
    finally:
        clear_api_overrides()


def test_marketing_outstanding_csv_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/marketing/outstanding-lines.csv", 401)
    finally:
        clear_api_overrides()


def test_marketing_delivery_lines_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/marketing/delivery-lines", 401)
    finally:
        clear_api_overrides()


def test_marketing_snapshot_create_guest_forbidden():
    client = make_api_client()
    set_auth_user("guest")
    try:
        assert_status(client, "POST", f"{_PREFIX}/marketing/outstanding-snapshots", 403, {})
    finally:
        clear_api_overrides()


def test_marketing_snapshot_get_missing_404():
    client = make_api_client()
    set_auth_user("marketing")
    try:
        assert_status(client, "GET", f"{_PREFIX}/marketing/outstanding-snapshots/999", 404)
    finally:
        clear_api_overrides()
