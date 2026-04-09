import inspect

from fastapi.params import Query
from fastapi.routing import APIRoute

from app import main
from app.routers import buyer_prices, customs, exchange_rates, sales_orders


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

