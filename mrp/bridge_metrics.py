"""Counter sederhana bridge stok MRP→ERP (in-process)."""

from __future__ import annotations

from threading import Lock
from typing import Any

_lock = Lock()
_counters: dict[str, int] = {
    "bridge_ok": 0,
    "bridge_fail": 0,
    "resolve_unmatched": 0,
    "out_rejected_missing_erp_id": 0,
}


def incr(name: str, n: int = 1) -> None:
    with _lock:
        _counters[name] = int(_counters.get(name, 0)) + int(n)


def snapshot() -> dict[str, Any]:
    with _lock:
        return dict(_counters)


def reset() -> None:
    with _lock:
        for k in list(_counters.keys()):
            _counters[k] = 0
