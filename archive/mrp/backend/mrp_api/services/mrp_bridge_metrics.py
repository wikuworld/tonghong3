"""In-process counters for MRP stock bridge (ERP side)."""

from __future__ import annotations

from threading import Lock
from typing import Any

_lock = Lock()
_counters: dict[str, int] = {
    "bridge_ok": 0,
    "bridge_fail": 0,
    "unmatched_material": 0,
}


def incr(name: str, n: int = 1) -> None:
    with _lock:
        _counters[name] = int(_counters.get(name, 0)) + int(n)


def snapshot() -> dict[str, Any]:
    with _lock:
        return dict(_counters)
