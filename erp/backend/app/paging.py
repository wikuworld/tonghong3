"""Shared pagination + sort helpers for ERP list endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

from fastapi import Query
from sqlalchemy import Select, asc, desc


@dataclass(frozen=True)
class PageParams:
    page: int
    page_size: int
    offset: int
    limit: int
    sort_by: Optional[str]
    sort_dir: str  # asc|desc


def parse_page_params(
    *,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    skip: Optional[int] = None,
    sort_by: Optional[str] = None,
    sort_dir: Optional[str] = None,
    default_page_size: int = 20,
    max_page_size: int = 200,
) -> PageParams:
    """Normalize page/page_size or legacy limit/offset/skip into PageParams."""
    size = page_size if page_size is not None else limit
    if size is None:
        size = default_page_size
    try:
        size = int(size)
    except (TypeError, ValueError):
        size = default_page_size
    size = max(1, min(size, max_page_size))

    if page is not None:
        try:
            p = max(int(page), 1)
        except (TypeError, ValueError):
            p = 1
        off = (p - 1) * size
    elif offset is not None or skip is not None:
        raw_off = offset if offset is not None else skip
        try:
            off = max(int(raw_off or 0), 0)
        except (TypeError, ValueError):
            off = 0
        p = (off // size) + 1
    else:
        p = 1
        off = 0

    direction = (sort_dir or "desc").strip().lower()
    if direction not in ("asc", "desc"):
        direction = "desc"
    key = (sort_by or "").strip().lower() or None
    return PageParams(
        page=p,
        page_size=size,
        offset=off,
        limit=size,
        sort_by=key,
        sort_dir=direction,
    )


def page_query_deps(
    page: Optional[int] = Query(None, ge=1),
    page_size: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: Optional[int] = Query(None, ge=0),
    skip: Optional[int] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None),
    sort_dir: Optional[str] = Query(None),
) -> PageParams:
    return parse_page_params(
        page=page,
        page_size=page_size,
        limit=limit,
        offset=offset,
        skip=skip,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


def apply_sort(
    stmt: Select,
    *,
    sortable: Mapping[str, Any],
    sort_by: Optional[str],
    sort_dir: str = "desc",
    default_order: Sequence[Any] = (),
) -> Select:
    """Apply whitelist sort; fall back to default_order."""
    col = sortable.get((sort_by or "").strip().lower()) if sort_by else None
    if col is None:
        if default_order:
            return stmt.order_by(*default_order)
        return stmt
    primary = desc(col) if (sort_dir or "desc").lower() == "desc" else asc(col)
    return stmt.order_by(primary)


def page_dict(*, items: list, total: int, params: PageParams) -> dict[str, Any]:
    return {
        "items": items,
        "total": int(total),
        "page": params.page,
        "page_size": params.page_size,
        "limit": params.limit,
        "offset": params.offset,
    }


def sort_mapped_rows(
    rows: list,
    *,
    sortable: Mapping[str, str],
    sort_by: Optional[str],
    sort_dir: str = "desc",
) -> list:
    """In-memory whitelist sort for list[dict] (or objects with attributes)."""
    key_name = sortable.get((sort_by or "").strip().lower()) if sort_by else None
    if not key_name:
        return rows
    reverse = (sort_dir or "desc").lower() == "desc"

    def _val(row: Any) -> Any:
        if isinstance(row, Mapping):
            return row.get(key_name)
        return getattr(row, key_name, None)

    return sorted(rows, key=lambda r: (_val(r) is None, _val(r)), reverse=reverse)
