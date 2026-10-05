"""Shared pagination + sort helpers for MRP Flask list endpoints."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence


def parse_page_args(args, *, default_page_size: int = 20, max_page_size: int = 200) -> dict[str, Any]:
    try:
        page = max(int(args.get("page") or 1), 1)
    except (TypeError, ValueError):
        page = 1
    try:
        raw = args.get("page_size") or args.get("limit") or default_page_size
        page_size = min(max(int(raw), 1), max_page_size)
    except (TypeError, ValueError):
        page_size = default_page_size
    try:
        offset = int(args.get("offset")) if args.get("offset") is not None else (page - 1) * page_size
        offset = max(offset, 0)
    except (TypeError, ValueError):
        offset = (page - 1) * page_size
    sort_by = (args.get("sort_by") or "").strip().lower() or None
    sort_dir = (args.get("sort_dir") or "desc").strip().lower()
    if sort_dir not in ("asc", "desc"):
        sort_dir = "desc"
    return {
        "page": page,
        "page_size": page_size,
        "offset": offset,
        "limit": page_size,
        "sort_by": sort_by,
        "sort_dir": sort_dir,
    }


def order_sql(
    sortable: Mapping[str, str],
    *,
    sort_by: Optional[str],
    sort_dir: str = "desc",
    default_sql: str = "id DESC",
) -> str:
    col = sortable.get((sort_by or "").strip().lower()) if sort_by else None
    if not col:
        return default_sql
    direction = "DESC" if (sort_dir or "desc").lower() == "desc" else "ASC"
    return f"{col} {direction}"


def page_payload(*, items: list, total: int, page: int, page_size: int, offset: int | None = None) -> dict:
    return {
        "items": items,
        "total": int(total),
        "page": int(page),
        "page_size": int(page_size),
        "limit": int(page_size),
        "offset": int(offset if offset is not None else (page - 1) * page_size),
    }


def sort_rows(
    items: Sequence[Mapping[str, Any]],
    *,
    sort_by: Optional[str],
    sort_dir: str = "desc",
    fields: Optional[Mapping[str, str]] = None,
) -> list:
    """Sort list of dicts by whitelist. ``fields`` maps sort_by → row key."""
    key = (sort_by or "").strip().lower()
    if not key:
        return list(items)
    field = fields.get(key) if fields is not None else key
    if fields is not None and not field:
        return list(items)
    if not field:
        return list(items)
    reverse = (sort_dir or "desc").lower() != "asc"

    def _key(row: Mapping[str, Any]):
        v = row.get(field)
        return (v is None, v)

    return sorted(items, key=_key, reverse=reverse)


def slice_page(
    items: Sequence[Any],
    *,
    page: int,
    page_size: int,
    offset: int | None = None,
) -> tuple[list, int]:
    total = len(items)
    off = int(offset if offset is not None else (page - 1) * page_size)
    off = max(off, 0)
    return list(items[off : off + page_size]), total
