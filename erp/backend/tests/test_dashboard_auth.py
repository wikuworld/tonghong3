"""Dashboard endpoints require authentication."""

from __future__ import annotations

import inspect

from app.routers import dashboard as dashboard_router


def test_dashboard_summary_requires_auth():
    sig = inspect.signature(dashboard_router.dashboard_summary)
    assert "get_current_user" in str(sig)


def test_dashboard_invoice_summary_requires_auth():
    sig = inspect.signature(dashboard_router.invoice_summary)
    assert "get_current_user" in str(sig)
