from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    auth,
    buyer_prices,
    customs,
    customers,
    dashboard,
    delivery,
    documents,
    exchange_rates,
    invoice,
    marketing,
    masters,
    packing,
    po,
    production,
    qc,
    reports,
    sales_orders,
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
app.include_router(customers.router, prefix=_PREFIX)
app.include_router(wilayah.router, prefix=_PREFIX)
app.include_router(sales_orders.router, prefix=_PREFIX)
app.include_router(po.router, prefix=_PREFIX)
app.include_router(marketing.router, prefix=_PREFIX)
app.include_router(production.router, prefix=_PREFIX)
app.include_router(qc.router, prefix=_PREFIX)
app.include_router(packing.router, prefix=_PREFIX)
app.include_router(delivery.router, prefix=_PREFIX)
app.include_router(invoice.router, prefix=_PREFIX)
app.include_router(dashboard.router, prefix=_PREFIX)
app.include_router(exchange_rates.router, prefix=_PREFIX)
app.include_router(masters.router, prefix=_PREFIX)
app.include_router(reports.router, prefix=_PREFIX)
app.include_router(documents.router, prefix=_PREFIX)
app.include_router(customs.router, prefix=_PREFIX)
app.include_router(buyer_prices.router, prefix=_PREFIX)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
