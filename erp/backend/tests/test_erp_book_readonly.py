"""Path A Production/QC/Packing write is blocked — buku baca-saja."""

from tests.http_fixtures import (
    assert_status,
    clear_api_overrides,
    make_api_client,
    set_auth_user,
)

_PREFIX = "/api/v1"


def test_production_create_admin_forbidden():
    client = make_api_client()
    set_auth_user("admin")
    try:
        resp = client.post(f"{_PREFIX}/production", json={"po_id": 1})
        assert resp.status_code == 403, resp.text
        detail = str((resp.json() or {}).get("detail") or "")
        assert "buku baca-saja" in detail.lower() or "hanya di mrp" in detail.lower()
    finally:
        clear_api_overrides()


def test_qc_create_admin_forbidden():
    client = make_api_client()
    set_auth_user("admin")
    try:
        assert_status(client, "POST", f"{_PREFIX}/qc", 403, {})
    finally:
        clear_api_overrides()


def test_packing_create_warehouse_forbidden():
    client = make_api_client()
    set_auth_user("warehouse")
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
