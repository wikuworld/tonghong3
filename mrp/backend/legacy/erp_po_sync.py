"""PO sync: ERP push is SoR. MRP tidak pull SQL dari DB ERP."""

from __future__ import annotations

from typing import Optional


def pull_po_items(*, po_id: Optional[int] = None, limit: int = 2000) -> list[dict]:
    """Tidak dipakai lagi. Sync PO hanya ERP→MRP push (POST /api/v1/mrp/sync/po di ERP)."""
    return []
