from __future__ import annotations

from starlette.middleware.wsgi import WSGIMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from mrp_api.config import settings
from mrp_api.db import ensure_identity_tables
from mrp_api.flask_wsgi import load_flask_app
from mrp_api.routers import auth, compat, dashboard, erp_catalog, inventory
from mrp_api.routers.auth import ensure_seed_users


class MrpV1RewriteMiddleware:
    """Vue MRP memanggil /api/v1/mrp/*; handler Flask tetap di /api/mrp/*."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            path = scope.get("path") or ""
            if path == "/api/v1/mrp" or path.startswith("/api/v1/mrp/"):
                new_path = "/api/mrp" + path[len("/api/v1/mrp") :]
                scope = dict(scope)
                scope["path"] = new_path
                if "raw_path" in scope:
                    scope["raw_path"] = new_path.encode("utf-8")
        await self.app(scope, receive, send)


app = FastAPI(
    title="Tonghong MRP API",
    version="1.0.0",
    description="Tonghong MRP API",
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(MrpV1RewriteMiddleware)

_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=_PREFIX)
app.include_router(compat.router, prefix=_PREFIX)
app.include_router(dashboard.router, prefix=_PREFIX)
app.include_router(inventory.router, prefix=_PREFIX)
app.include_router(erp_catalog.router, prefix=_PREFIX)


@app.get("/health")
def health():
    return {"status": "ok", "service": "tonghong-mrp", "stack": "fastapi"}


@app.get("/api/v1/health")
def health_v1():
    return {"status": "ok", "service": "tonghong-mrp", "stack": "fastapi"}


@app.on_event("startup")
def _bootstrap() -> None:
    ensure_identity_tables()
    ensure_seed_users()


app.mount("/", WSGIMiddleware(load_flask_app()))
