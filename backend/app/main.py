from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    accounting,
    audit,
    auth,
    buyer_prices,
    color_swatch,
    customs,
    customers,
    dashboard,
    delivery,
    documents,
    exchange_rates,
    invoice,
    inventory,
    journal,
    marketing,
    masters,
    notifications,
    permissions,
    packing,
    po,
    pricing,
    production,
    quotations,
    qc,
    reports,
    sales_orders,
    subcon,
    workflow,
    wilayah,
)

app = FastAPI(title="Tonghong API", version="1.0.0", description="Sales · Produksi · ERP (CR)")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=_PREFIX)
app.include_router(audit.router, prefix=_PREFIX)
app.include_router(customers.router, prefix=_PREFIX)
app.include_router(wilayah.router, prefix=_PREFIX)
app.include_router(sales_orders.router, prefix=_PREFIX)
app.include_router(po.router, prefix=_PREFIX)
app.include_router(quotations.router, prefix=_PREFIX)
app.include_router(subcon.router, prefix=_PREFIX)
app.include_router(marketing.router, prefix=_PREFIX)
app.include_router(production.router, prefix=_PREFIX)
app.include_router(qc.router, prefix=_PREFIX)
app.include_router(packing.router, prefix=_PREFIX)
app.include_router(delivery.router, prefix=_PREFIX)
app.include_router(invoice.router, prefix=_PREFIX)
app.include_router(dashboard.router, prefix=_PREFIX)
app.include_router(exchange_rates.router, prefix=_PREFIX)
app.include_router(masters.router, prefix=_PREFIX)
app.include_router(color_swatch.router, prefix=_PREFIX)
app.include_router(notifications.router, prefix=_PREFIX)
app.include_router(permissions.router, prefix=_PREFIX)
app.include_router(reports.router, prefix=_PREFIX)
app.include_router(documents.router, prefix=_PREFIX)
app.include_router(customs.router, prefix=_PREFIX)
app.include_router(buyer_prices.router, prefix=_PREFIX)
app.include_router(pricing.router, prefix=_PREFIX)
app.include_router(workflow.router, prefix=_PREFIX)
app.include_router(accounting.router, prefix=_PREFIX)
app.include_router(inventory.router, prefix=_PREFIX)
app.include_router(journal.router, prefix=_PREFIX)


@app.on_event("startup")
def _bootstrap_admin() -> None:
    non_dev_env = str(settings.app_env or "dev").strip().lower() not in {
        "dev",
        "local",
        "development",
        "test",
    }
    if non_dev_env and (
        settings.jwt_secret == "dev-secret-change-me"
        or (
            settings.admin_username == "admin"
            or settings.admin_password == "admin123"
        )
    ):
        raise RuntimeError(
            "Unsafe auth defaults detected for non-dev environment. "
            "Please override JWT secret and bootstrap admin credentials."
        )

    # buat user admin default jika belum ada (lihat `settings.admin_*`)
    try:
        from app.routers.auth import ensure_bootstrap_admin
        from app.routers.permissions import ensure_default_permissions
        from app.db import SessionLocal

        ensure_bootstrap_admin()
        db = SessionLocal()
        try:
            ensure_default_permissions(db)
        finally:
            db.close()
    except Exception:
        # jangan gagal startup hanya karena bootstrap (mis. DB belum siap)
        return


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
