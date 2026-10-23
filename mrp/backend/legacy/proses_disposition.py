"""Sisa ukur Reject/Return: alasan baris tidak bisa disimpan."""

from __future__ import annotations


def line_block_reason(
    *,
    measured: float,
    returned: float,
    rejected: float,
    remaining: float,
) -> str | None:
    if measured <= 1e-9:
        return "belum ada hasil ukur"
    if remaining > 1e-9:
        return None
    parts: list[str] = []
    if returned > 1e-9:
        parts.append("sudah diretur")
    if rejected > 1e-9:
        parts.append("sudah direject")
    if not parts:
        parts.append("sisa ukur habis")
    return " dan ".join(parts)
