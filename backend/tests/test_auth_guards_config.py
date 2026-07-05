import inspect

from fastapi.params import Query
from fastapi.routing import APIRoute

from app import main
from app.routers import (
    accounting,
    buyer_prices,
    customs,
    delivery,
    exchange_rates,
    invoice,
    journal,
    marketing,
    masters,
    packing,
    po,
    pricing,
    production,
    qc,
    sales_orders,
    subcon,
    workflow,
    wilayah,
)


def _get_route(router, path: str, method: str) -> APIRoute:
    for r in router.routes:
        if isinstance(r, APIRoute) and r.path == path and method.upper() in r.methods:
            return r
    raise AssertionError(f"Route tidak ditemukan: {method} {path}")


def _has_dep(route: APIRoute, dep_name: str) -> bool:
    return any((getattr(d.call, "__name__", "") == dep_name) for d in route.dependant.dependencies)


def test_sales_orders_and_details_require_auth_and_role_guards():
    # Read endpoints: minimal harus login.
    for path, method in [
        ("/sales-orders", "GET"),
        ("/sales-orders/{so_id}", "GET"),
    ]:
        route = _get_route(sales_orders.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    # Write endpoints: harus memakai require_roles (closure _dep).
    for path, method in [
        ("/sales-orders", "POST"),
        ("/sales-orders/{so_id}", "PUT"),
        ("/sales-orders/{so_id}", "DELETE"),
        ("/sales-orders/{so_id}/details", "POST"),
        ("/sales-order-details/{detail_id}", "PUT"),
        ("/sales-order-details/{detail_id}", "DELETE"),
    ]:
        route = _get_route(sales_orders.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_exchange_rates_require_auth_and_role_guards():
    for path, method in [
        ("/exchange-rates", "GET"),
        ("/exchange-rates/latest", "GET"),
    ]:
        route = _get_route(exchange_rates.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    route = _get_route(exchange_rates.router, "/exchange-rates", "POST")
    assert _has_dep(route, "_dep"), "POST /exchange-rates harus pakai require_roles"


def test_buyer_prices_require_auth_and_role_guards():
    for path, method in [
        ("/buyer-prices/lists", "GET"),
        ("/buyer-prices/lists/{list_id}", "GET"),
        ("/buyer-prices/by-buyer/{buyer_code}", "GET"),
    ]:
        route = _get_route(buyer_prices.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    route = _get_route(buyer_prices.router, "/buyer-prices/resolve-unit-price", "POST")
    assert _has_dep(route, "get_current_user"), "POST /buyer-prices/resolve-unit-price harus pakai get_current_user"

    for path, method in [
        ("/buyer-prices/lists", "POST"),
        ("/buyer-prices/lists/{list_id}", "PUT"),
        ("/buyer-prices/lists/{list_id}/sheet", "PUT"),
        ("/buyer-prices/lists/{list_id}", "DELETE"),
        ("/buyer-prices/import-upload", "POST"),
        ("/buyer-prices/import-zip", "POST"),
    ]:
        route = _get_route(buyer_prices.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_customs_require_auth_and_role_guards_and_limit_bounds():
    for path, method in [
        ("/customs/declarations", "GET"),
        ("/customs/declarations/{declaration_id}", "GET"),
        ("/customs/declarations/by-nomor/{nomor_aju}", "GET"),
    ]:
        route = _get_route(customs.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    for path, method in [
        ("/customs/declarations", "POST"),
        ("/customs/declarations/{declaration_id}", "PUT"),
        ("/customs/declarations/{declaration_id}/sheets-data", "PUT"),
        ("/customs/declarations/{declaration_id}", "DELETE"),
        ("/customs/declarations/import-upload", "POST"),
        ("/customs/declarations/import-zip", "POST"),
    ]:
        route = _get_route(customs.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"

    sig = inspect.signature(customs.list_declarations)
    limit_default = sig.parameters["limit"].default
    assert isinstance(limit_default, Query)
    ge_values = [getattr(m, "ge", None) for m in getattr(limit_default, "metadata", [])]
    le_values = [getattr(m, "le", None) for m in getattr(limit_default, "metadata", [])]
    assert 1 in ge_values
    assert 1000 in le_values


def test_po_router_require_auth_and_role_guards():
    for path, method in [
        ("/po", "GET"),
        ("/po/page", "GET"),
        ("/po/material-hints", "GET"),
        ("/po/mkt-workflow-stages", "GET"),
        ("/po/next-number", "GET"),
        ("/po/{po_id}", "GET"),
    ]:
        route = _get_route(po.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    route = _get_route(po.router, "/po-detail/{detail_id}/delivery-schedules", "GET")
    assert _has_dep(route, "get_current_user"), "GET delivery-schedules harus pakai get_current_user"

    for path, method in [
        ("/po", "POST"),
        ("/po/{po_id}", "DELETE"),
        ("/po/{po_id}/mkt-workflow/advance", "POST"),
        ("/po/{po_id}/details", "POST"),
    ]:
        route = _get_route(po.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_delivery_router_require_auth_and_role_guards():
    for path, method in [
        ("/delivery", "GET"),
        ("/delivery/{delivery_id}", "GET"),
        ("/delivery/{delivery_id}/details", "GET"),
    ]:
        route = _get_route(delivery.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    for path, method in [
        ("/delivery", "POST"),
        ("/delivery/{delivery_id}", "PUT"),
        ("/delivery/{delivery_id}/details", "POST"),
        ("/delivery/{delivery_id}/mark-surat-jalan-printed", "POST"),
    ]:
        route = _get_route(delivery.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_subcon_router_require_auth_and_role_guards():
    for path, method in [
        ("/subcon-invoices", "GET"),
        ("/subcon-invoices/{invoice_id}", "GET"),
    ]:
        route = _get_route(subcon.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    for path, method in [
        ("/subcon-invoices", "POST"),
        ("/subcon-invoices/{invoice_id}", "PUT"),
        ("/subcon-invoices/{invoice_id}", "DELETE"),
        ("/subcon-invoices/generate-from-po/{po_id}", "POST"),
    ]:
        route = _get_route(subcon.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_marketing_router_require_auth_and_role_guards():
    for path, method in [
        ("/marketing/outstanding-lines", "GET"),
        ("/marketing/outstanding-lines.csv", "GET"),
        ("/marketing/delivery-lines", "GET"),
        ("/marketing/delivery-planning", "GET"),
        ("/marketing/delivery-today", "GET"),
        ("/marketing/outstanding-snapshots", "GET"),
        ("/marketing/outstanding-snapshots/{snapshot_id}", "GET"),
    ]:
        route = _get_route(marketing.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    for path, method in [
        ("/marketing/outstanding-snapshots", "POST"),
    ]:
        route = _get_route(marketing.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_production_router_require_auth_and_role_guards():
    for path, method in [
        ("/production", "GET"),
        ("/production/{production_id}", "GET"),
        ("/production/{production_id}/details", "GET"),
    ]:
        route = _get_route(production.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    for path, method in [
        ("/production", "POST"),
        ("/production/{production_id}/details", "POST"),
        ("/production-detail/{detail_id}", "PUT"),
    ]:
        route = _get_route(production.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_qc_router_require_auth_and_role_guards():
    for path, method in [
        ("/qc", "GET"),
        ("/qc/{qc_id}", "GET"),
        ("/qc/{qc_id}/details", "GET"),
    ]:
        route = _get_route(qc.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    for path, method in [
        ("/qc", "POST"),
        ("/qc/{qc_id}/details", "POST"),
        ("/qc-detail/{detail_id}", "PUT"),
    ]:
        route = _get_route(qc.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_packing_router_require_auth_and_role_guards():
    for path, method in [
        ("/packing", "GET"),
        ("/packing/{packing_id}", "GET"),
    ]:
        route = _get_route(packing.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    for path, method in [
        ("/packing", "POST"),
        ("/packing/{packing_id}", "PUT"),
        ("/packing/{packing_id}/details", "POST"),
        ("/packing/{packing_id}/mark-invpl-printed", "POST"),
    ]:
        route = _get_route(packing.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_invoice_router_require_auth_and_role_guards():
    for path, method in [
        ("/invoice", "GET"),
        ("/invoice/outstanding", "GET"),
        ("/invoice/{invoice_id}", "GET"),
        ("/invoice/{invoice_id}/details", "GET"),
    ]:
        route = _get_route(invoice.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    for path, method in [
        ("/invoice", "POST"),
        ("/invoice/{invoice_id}", "PUT"),
        ("/invoice/{invoice_id}/details", "POST"),
        ("/invoice/backfill-fks", "POST"),
    ]:
        route = _get_route(invoice.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_pricing_router_require_auth_and_role_guards():
    for path, method in [
        ("/pricing/special-prices", "GET"),
        ("/pricing/customer-prices", "GET"),
    ]:
        route = _get_route(pricing.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    for path, method in [
        ("/pricing/special-prices", "POST"),
        ("/pricing/special-prices/{price_id}", "PUT"),
        ("/pricing/customer-prices", "POST"),
        ("/pricing/customer-prices/{price_id}", "PUT"),
        ("/pricing/bulk-update", "POST"),
        ("/pricing/bulk-update-csv", "POST"),
    ]:
        route = _get_route(pricing.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"

    for path, method in [
        ("/pricing/special-prices/{price_id}", "DELETE"),
        ("/pricing/customer-prices/{price_id}", "DELETE"),
    ]:
        route = _get_route(pricing.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_accounting_router_require_auth_and_role_guards():
    for path, method in [
        ("/accounting/mappings", "GET"),
        ("/accounting/mappings/resolve", "GET"),
    ]:
        route = _get_route(accounting.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    for path, method in [
        ("/accounting/mappings", "POST"),
        ("/accounting/mappings/{mapping_id}", "PUT"),
        ("/accounting/mappings/{mapping_id}", "DELETE"),
    ]:
        route = _get_route(accounting.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_journal_router_require_auth_and_role_guards():
    for path, method in [
        ("/journal/entries", "GET"),
        ("/journal/entries/trial-balance", "GET"),
    ]:
        route = _get_route(journal.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    route = _get_route(journal.router, "/journal/entries/generate-from-transaction", "POST")
    assert _has_dep(route, "_dep"), "POST generate-from-transaction harus pakai require_roles"


def test_wilayah_router_requires_auth():
    for path, method in [
        ("/wilayah/provinces", "GET"),
        ("/wilayah/regencies/{province_code}", "GET"),
        ("/wilayah/districts/{regency_code}", "GET"),
        ("/wilayah/villages/{district_code}", "GET"),
    ]:
        route = _get_route(wilayah.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"


def test_workflow_router_require_auth_and_role_guards():
    for path, method in [
        ("/workflow/outstanding-materials", "GET"),
        ("/workflow/ppic/dashboard", "GET"),
        ("/workflow/ppic/users", "GET"),
        ("/workflow/po/{po_id}/ppic-assignment", "GET"),
    ]:
        route = _get_route(workflow.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    for path, method in [
        ("/workflow/po/{po_id}/assign-to-ppic", "POST"),
        ("/workflow/outstanding-materials", "POST"),
        ("/workflow/outstanding-materials/{material_id}", "PUT"),
        ("/workflow/outstanding-materials/{material_id}", "DELETE"),
        ("/workflow/outstanding-materials/generate-from-po/{po_id}", "POST"),
        ("/workflow/outstanding-materials/{material_id}/deliver", "PUT"),
        ("/workflow/ppic/assignments/{assignment_id}/status", "PUT"),
    ]:
        route = _get_route(workflow.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_masters_router_require_auth_and_role_guards():
    for path, method in [
        ("/masters/brands", "GET"),
        ("/masters/items", "GET"),
        ("/masters/fluorescent-colors", "GET"),
        ("/masters/prices", "GET"),
    ]:
        route = _get_route(masters.router, path, method)
        assert _has_dep(route, "get_current_user"), f"{method} {path} harus pakai get_current_user"

    for path, method in [
        ("/masters/brands", "POST"),
        ("/masters/items", "POST"),
        ("/masters/items/import", "POST"),
        ("/masters/import-zip", "POST"),
        ("/masters/fluorescent-colors", "POST"),
    ]:
        route = _get_route(masters.router, path, method)
        assert _has_dep(route, "_dep"), f"{method} {path} harus pakai require_roles"


def test_startup_hardening_rejects_any_default_auth_in_non_dev_env():
    old_app_env = main.settings.app_env
    old_jwt_secret = main.settings.jwt_secret
    old_admin_username = main.settings.admin_username
    old_admin_password = main.settings.admin_password
    try:
        main.settings.app_env = "production"
        main.settings.jwt_secret = "this-is-a-very-strong-secret-value-12345"

        # Case 1: username default -> harus ditolak.
        main.settings.admin_username = "admin"
        main.settings.admin_password = "A_secure_password_123"
        try:
            main._bootstrap_admin()
            assert False, "Startup harus gagal jika ADMIN_USERNAME masih default"
        except RuntimeError:
            pass

        # Case 2: password default -> harus ditolak.
        main.settings.admin_username = "supervisor"
        main.settings.admin_password = "admin123"
        try:
            main._bootstrap_admin()
            assert False, "Startup harus gagal jika ADMIN_PASSWORD masih default"
        except RuntimeError:
            pass
    finally:
        main.settings.app_env = old_app_env
        main.settings.jwt_secret = old_jwt_secret
        main.settings.admin_username = old_admin_username
        main.settings.admin_password = old_admin_password


def test_startup_hardening_rejects_default_jwt_secret_in_non_dev_env():
    old_app_env = main.settings.app_env
    old_jwt_secret = main.settings.jwt_secret
    old_admin_username = main.settings.admin_username
    old_admin_password = main.settings.admin_password
    try:
        main.settings.app_env = "production"
        main.settings.jwt_secret = "dev-secret-change-me"
        main.settings.admin_username = "secure-admin"
        main.settings.admin_password = "Very_secure_password_123"

        try:
            main._bootstrap_admin()
            assert False, "Startup harus gagal jika JWT_SECRET masih default"
        except RuntimeError:
            pass
    finally:
        main.settings.app_env = old_app_env
        main.settings.jwt_secret = old_jwt_secret
        main.settings.admin_username = old_admin_username
        main.settings.admin_password = old_admin_password

