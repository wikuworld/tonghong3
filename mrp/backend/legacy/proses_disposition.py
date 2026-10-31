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


def parse_ukur_sizes(line: dict | None) -> list[float]:
    """Ambil daftar size pengukuran ulang dari body baris reject/retur.

    Menerima ``ukur_sizes`` (list angka) atau ``ukur_rows`` (list objek
    dengan ``size_val`` / ``size``). Angka non-positif diabaikan.
    """
    if not isinstance(line, dict):
        return []
    raw = line.get("ukur_sizes")
    if raw is None and line.get("ukur_rows") is not None:
        raw = line.get("ukur_rows")
    if not isinstance(raw, list):
        return []
    sizes: list[float] = []
    for item in raw:
        try:
            if isinstance(item, dict):
                val = float(item.get("size_val") or item.get("size") or 0)
            else:
                val = float(item or 0)
        except (TypeError, ValueError):
            continue
        if val > 0:
            sizes.append(round(val, 3))
    return sizes


def qty_from_ukur_sizes(sizes: list[float]) -> tuple[float, int]:
    """(total SF, jumlah lembar) dari hasil pengukuran ulang."""
    if not sizes:
        return 0.0, 0
    total = round(sum(float(s) for s in sizes), 3)
    return total, len(sizes)
