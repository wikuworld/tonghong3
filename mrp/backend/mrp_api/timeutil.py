"""Zona waktu aplikasi Tonghong MRP (default GMT+7 / Asia/Jakarta)."""

from __future__ import annotations

from datetime import date, datetime, timezone
from functools import lru_cache
from zoneinfo import ZoneInfo

from mrp_api.config import settings


@lru_cache(maxsize=1)
def app_zone() -> ZoneInfo:
    name = (settings.app_timezone or "Asia/Jakarta").strip() or "Asia/Jakarta"
    return ZoneInfo(name)


def app_now() -> datetime:
    return datetime.now(app_zone()).replace(tzinfo=None)


def app_today() -> date:
    return app_now().date()


def app_now_aware() -> datetime:
    return datetime.now(app_zone())


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def mariadb_time_zone_offset() -> str:
    now = app_now_aware()
    offset = now.utcoffset()
    if offset is None:
        return "+07:00"
    total = int(offset.total_seconds())
    sign = "+" if total >= 0 else "-"
    total = abs(total)
    hours, rem = divmod(total, 3600)
    minutes = rem // 60
    return f"{sign}{hours:02d}:{minutes:02d}"
