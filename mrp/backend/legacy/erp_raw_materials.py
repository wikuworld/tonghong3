"""Baca raw_materials Tonghong ERP via HTTP API — SSOT katalog bahan baku."""

from __future__ import annotations

from typing import Optional


_TYPE_ALIASES = {
    "kimia": "kimia",
    "rp": "rp",
    "material": "material_lain",
    "material_lain": "material_lain",
    "material-lain": "material_lain",
    "kulit": "kulit",
}


def normalize_material_type(material_type: str | None) -> str:
    raw = (material_type or "").strip().lower()
    return _TYPE_ALIASES.get(raw, raw)


def material_ukuran(row: dict | None) -> str:
    if not row:
        return ""
    for key in ("ukuran", "size"):
        val = row.get(key)
        if val is None or val == "":
            continue
        return str(val).strip()
    return ""


def _shape(row: dict) -> dict:
    ukuran = material_ukuran(row)
    return {
        "id": int(row["id"]),
        "erp_material_id": int(row["id"]),
        "code": row.get("code"),
        "name": row.get("name"),
        "material_type": row.get("material_type"),
        "unit": row.get("unit") or "kg",
        "size": ukuran or None,
        "ukuran": ukuran or None,
        "thickness": row.get("thickness"),
        "color": row.get("color"),
        "leather_type": row.get("leather_type"),
        "is_active": bool(row.get("is_active", True)),
        "source": "raw_materials",
        "kode": row.get("code"),
        "nama": row.get("name"),
        "satuan": row.get("unit") or "kg",
    }


def fetch_material(material_id: int) -> Optional[dict]:
    from mrp_api import erp_client

    try:
        row = erp_client.get_material(int(material_id))
    except erp_client.ErpApiError:
        return None
    return _shape(row) if row else None


def fetch_material_by_code(code: str, material_type: str | None = None) -> Optional[dict]:
    code = (code or "").strip()
    if not code:
        return None
    from mrp_api import erp_client

    rows = erp_client.list_materials(
        material_type=normalize_material_type(material_type) if material_type else None,
        code=code,
        active_only=False,
        limit=5,
    )
    if not rows:
        return None
    return _shape(rows[0])


def list_materials(
    material_type: str | None = None,
    *,
    keyword: str | None = None,
    limit: int = 2000,
    active_only: bool = True,
) -> list[dict]:
    from mrp_api import erp_client

    rows = erp_client.list_materials(
        material_type=normalize_material_type(material_type) if material_type else None,
        q=keyword,
        active_only=active_only,
        limit=max(1, min(int(limit), 5000)),
    )
    return [_shape(r) for r in rows]


def resolve_material(
    *,
    erp_material_id: int | None = None,
    code: str | None = None,
    material_type: str | None = None,
) -> Optional[dict]:
    if erp_material_id:
        row = fetch_material(int(erp_material_id))
        if row and material_type:
            if normalize_material_type(row.get("material_type")) != normalize_material_type(
                material_type
            ):
                return None
        return row
    if code:
        return fetch_material_by_code(code, material_type=material_type)
    return None


def ensure_erp_material(
    *,
    code: str,
    name: str,
    material_type: str,
    unit: str = "kg",
) -> Optional[int]:
    """Upsert katalog via ERP HTTP API (bukan SQL lintas-DB)."""
    code = (code or "").strip()
    if not code:
        return None
    mt = normalize_material_type(material_type)
    from mrp_api import erp_client

    existing = fetch_material_by_code(code, material_type=None)
    if existing:
        try:
            row = erp_client.upsert_material(
                code=code, name=name or code, material_type=mt, unit=unit or "kg"
            )
            return int(row["id"]) if row else int(existing["id"])
        except erp_client.ErpApiError:
            return int(existing["id"])
    try:
        row = erp_client.upsert_material(
            code=code, name=name or code, material_type=mt, unit=unit or "kg"
        )
        return int(row["id"]) if row else None
    except erp_client.ErpApiError:
        return None
