"""Addon harga buyer yang wajib diisi menurut flag master item."""

from __future__ import annotations

from typing import Any

# Flag master item → kunci sel sheet harga buyer.
ADDON_FLAGS: tuple[tuple[str, str], ...] = (
    ("flag_color_black", "COLOR BLACK"),
    ("flag_color", "COLOR COLOR"),
    ("flag_flourasent", "FLOURASENT"),
    ("flag_metalic", "METALIC"),
    ("flag_emboss", "EMBOSS"),
    ("flag_special_emboss", "SPESIAL EMBOSS"),
)


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _field(obj: Any, key: str) -> Any:
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def addon_price_filled(val: Any) -> bool:
    """Harga dasar: kosong dan nilai <= 0 belum diisi."""
    if val is None or val == "":
        return False
    try:
        return float(val) > 0
    except (TypeError, ValueError):
        return False


def addon_price_entered(val: Any) -> bool:
    """Addon flag: 0 sah. Hanya sel kosong yang belum diisi."""
    if val is None or val == "":
        return False
    try:
        return float(val) >= 0
    except (TypeError, ValueError):
        return False


def missing_addons_for_cells(cells: dict | None, items: list[Any]) -> list[str]:
    """Komponen wajib yang masih kosong untuk satu baris ITEM + THICKNESS."""
    data = cells if isinstance(cells, dict) else {}
    want_mat = _norm(data.get("ITEM"))
    want_thick = _norm(data.get("THICKNESS"))
    if not want_mat or not want_thick:
        return []
    missing: list[str] = []
    for flag, key in ADDON_FLAGS:
        required = False
        for item in items or []:
            if _norm(_field(item, "material_name")) != want_mat:
                continue
            if _norm(_field(item, "thickness_range")) != want_thick:
                continue
            if bool(_field(item, flag)):
                required = True
                break
        if required and not addon_price_entered(data.get(key)):
            missing.append(key)
    return missing


def missing_required_prices(cells: dict | None, items: list[Any] | None = None) -> list[str]:
    """Hanya COLOR WHITE yang wajib lebih dari 0. Flag addon boleh 0 dan tidak divalidasi."""
    del items
    data = cells if isinstance(cells, dict) else {}
    if not str(data.get("ITEM") or "").strip():
        return []
    if not addon_price_filled(data.get("COLOR WHITE")):
        return ["COLOR WHITE"]
    return []


def format_required_price_gaps(rows: list[Any], items: list[Any]) -> str:
    """Pesan validasi simpan. Kosong jika semua baris berisi ITEM sudah lengkap."""
    lines: list[str] = []
    for index, row in enumerate(rows or [], start=1):
        cells = row.cells if hasattr(row, "cells") else row
        missing = missing_required_prices(cells if isinstance(cells, dict) else {}, items)
        if not missing:
            continue
        item = str((cells or {}).get("ITEM") or "").strip()
        lines.append(f"Baris {index} ({item}): {', '.join(missing)} wajib diisi")
    return "\n".join(lines)


def missing_addons_for_sheet(rows: list[Any], items: list[Any]) -> list[str]:
    """Gabungan addon yang masih kurang di seluruh baris satu list harga."""
    seen: list[str] = []
    for row in rows or []:
        cells = row.cells if hasattr(row, "cells") else row
        for key in missing_addons_for_cells(cells, items):
            if key not in seen:
                seen.append(key)
    return seen
