"""HTTP integration tests for packing router guards."""

from tests.http_fixtures import (
    assert_status,
    clear_api_overrides,
    clear_auth_user,
    make_api_client,
    set_auth_user,
)

_PREFIX = "/api/v1"


def test_packing_list_requires_auth():
    client = make_api_client()
    clear_auth_user()
    try:
        assert_status(client, "GET", f"{_PREFIX}/packing", 401)
    finally:
        clear_api_overrides()


def test_packing_create_guest_forbidden():
    client = make_api_client()
    set_auth_user("guest")
    try:
        assert_status(
            client,
            "POST",
            f"{_PREFIX}/packing",
            403,
            {"production_id": 1, "qc_header_id": 1},
        )
    finally:
        clear_api_overrides()
