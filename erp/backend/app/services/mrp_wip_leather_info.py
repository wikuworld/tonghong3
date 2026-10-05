"""Ambil warna kulit + tanggal masuk pabrik dari MRP per kode WIP (lot)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _mrp_base() -> str:
    return (settings.mrp_upstream_url or "http://127.0.0.1:8002").rstrip("/")


def fetch_wip_leather_info(kode_wips: list[str]) -> dict[str, dict[str, Any]]:
    """Map kode_wip → {warna_kulit, tanggal_masuk_pabrik}. Gagal jaringan → {}."""
    codes = []
    seen: set[str] = set()
    for raw in kode_wips or []:
        w = (raw or "").strip()
        if not w or w in seen:
            continue
        seen.add(w)
        codes.append(w)
    if not codes:
        return {}

    base = _mrp_base()
    timeout = max(float(settings.mrp_sync_timeout_seconds or 8.0), 15.0)
    out: dict[str, dict[str, Any]] = {}
    # batch in chunks to keep query string short
    chunk_size = 80
    try:
        with httpx.Client(timeout=timeout) as client:
            for i in range(0, len(codes), chunk_size):
                chunk = codes[i : i + chunk_size]
                r = client.get(
                    f"{base}/api/mrp/wip-leather-info",
                    params={"kode_wip": ",".join(chunk)},
                )
                if r.status_code != 200:
                    logger.warning(
                        "MRP wip-leather-info status=%s body=%s",
                        r.status_code,
                        (r.text or "")[:200],
                    )
                    continue
                body = r.json() if r.content else {}
                items = body.get("items") if isinstance(body, dict) else None
                if not isinstance(items, list):
                    continue
                for it in items:
                    if not isinstance(it, dict):
                        continue
                    key = str(it.get("kode_wip") or "").strip()
                    if not key:
                        continue
                    out[key] = {
                        "warna_kulit": (it.get("warna_kulit") or "").strip(),
                        "tanggal_masuk_pabrik": (
                            str(it.get("tanggal_masuk_pabrik") or "").strip()[:10] or None
                        ),
                    }
    except httpx.HTTPError as exc:
        logger.warning("MRP wip-leather-info unavailable: %s", exc)
    return out


def enrich_delivery_rows_with_leather(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Isi leather_color + leather_in_date pada baris delivery list (lot_no = kode WIP)."""
    if not rows:
        return rows
    lots = [str(r.get("lot_no") or "").strip() for r in rows]
    info = fetch_wip_leather_info(lots)
    for r in rows:
        lot = str(r.get("lot_no") or "").strip()
        meta = info.get(lot) or {}
        r["leather_color"] = meta.get("warna_kulit") or ""
        r["leather_in_date"] = meta.get("tanggal_masuk_pabrik") or ""
    return rows
