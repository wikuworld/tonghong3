"""Lookup relasi item ↔ CSI ↔ swatch lewat color_code (tanpa FK di item)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models import ColorSwatchRecipe, CsiColorMaster, FluorescentColorMaster
from app.services.color_code import (
    csi_color_label,
    extract_item_color_code,
    extract_item_color_qualifier,
)

OVERLAY_QUALIFIERS = frozenset({"FLUORESCENT", "PEARLIZED", "METALLIC", "METTALIC"})


def parse_color_link_query(
    color: str | None = None,
    color_code: str | None = None,
) -> tuple[str | None, str | None]:
    """Kembalikan (color_code, qualifier). Kode dari query atau extract `BLACK (00A)`."""
    code = (color_code or "").strip().upper() or extract_item_color_code(color)
    qualifier = extract_item_color_qualifier(color)
    return (code or None), qualifier


def _name_from_color_text(color: str | None) -> str:
    raw = (color or "").strip()
    if "(" in raw:
        return raw.split("(", 1)[0].strip()
    return raw


def serialize_color_links(
    *,
    color_code: str,
    color_qualifier: str | None,
    color_text: str | None,
    csi_rows: list[Any],
    swatch_rows: list[Any],
    fluorescent_rows: list[Any],
) -> dict[str, Any]:
    first_name = ""
    if csi_rows:
        first_name = (getattr(csi_rows[0], "color_name", None) or "").strip()
    if not first_name:
        first_name = _name_from_color_text(color_text)
    factories: list[str] = []
    seen_f: set[str] = set()
    for row in swatch_rows:
        fk = (getattr(row, "factory_key", None) or "").strip()
        if fk and fk not in seen_f:
            seen_f.add(fk)
            factories.append(fk)
    return {
        "color_code": color_code,
        "color_qualifier": color_qualifier,
        "item_label": csi_color_label(first_name, color_code),
        "in_csi": bool(csi_rows),
        "in_swatch": bool(swatch_rows),
        "csi": [
            {
                "id": int(row.id),
                "buyer_code": row.buyer_code,
                "color_code": row.color_code,
                "color_name": row.color_name,
                "label": csi_color_label(row.color_name, row.color_code),
            }
            for row in csi_rows
        ],
        "swatch_count": len(swatch_rows),
        "swatch_factories": factories[:8],
        "fluorescent": [
            {
                "id": int(row.id),
                "buyer_code": row.buyer_code,
                "color_code": row.color_code,
                "color_name": row.color_name,
                "season_label": row.season_label,
                "color_class": row.color_class,
            }
            for row in fluorescent_rows
        ],
    }


def lookup_color_links(
    db: Session,
    *,
    color: str | None = None,
    color_code: str | None = None,
) -> dict[str, Any]:
    code, qualifier = parse_color_link_query(color, color_code)
    if not code:
        return serialize_color_links(
            color_code="",
            color_qualifier=qualifier,
            color_text=color,
            csi_rows=[],
            swatch_rows=[],
            fluorescent_rows=[],
        )
    csi_rows = list(
        db.scalars(
            select(CsiColorMaster)
            .where(
                CsiColorMaster.is_active.is_(True),
                func.upper(func.trim(CsiColorMaster.color_code)) == code,
            )
            .order_by(CsiColorMaster.buyer_code.asc())
        ).all()
    )
    swatch_rows = list(
        db.scalars(
            select(ColorSwatchRecipe).where(
                ColorSwatchRecipe.is_active.is_(True),
                func.upper(func.trim(ColorSwatchRecipe.color_code)) == code,
            )
        ).all()
    )
    fluorescent_rows: list[Any] = []
    if qualifier and qualifier.upper() in OVERLAY_QUALIFIERS:
        fluorescent_rows = list(
            db.scalars(
                select(FluorescentColorMaster)
                .where(
                    FluorescentColorMaster.is_active.is_(True),
                    func.upper(func.trim(FluorescentColorMaster.color_code)) == code,
                )
                .order_by(FluorescentColorMaster.buyer_code.asc())
                .limit(20)
            ).all()
        )
    return serialize_color_links(
        color_code=code,
        color_qualifier=qualifier,
        color_text=color,
        csi_rows=csi_rows,
        swatch_rows=swatch_rows,
        fluorescent_rows=fluorescent_rows,
    )


def list_color_link_options(db: Session) -> list[dict[str, str]]:
    """Opsi unik NAMA (KODE) dari CSI aktif untuk dropdown item."""
    rows = list(
        db.scalars(
            select(CsiColorMaster)
            .where(CsiColorMaster.is_active.is_(True))
            .order_by(CsiColorMaster.color_name.asc(), CsiColorMaster.color_code.asc())
        ).all()
    )
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for row in rows:
        label = csi_color_label(row.color_name, row.color_code)
        key = label.upper()
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "label": label,
                "value": label,
                "color_code": (row.color_code or "").strip(),
                "color_name": (row.color_name or "").strip(),
            }
        )
    return out


def backfill_swatch_csi_exact(db: Session) -> dict[str, int]:
    """Hubungkan orphan swatch ke CSI exact (buyer, color_code). Tidak seed CSI baru."""
    result = db.execute(
        text(
            """
            UPDATE color_swatch_recipes s
            JOIN csi_color_masters c
              ON c.buyer_code = s.buyer_code
             AND UPPER(TRIM(c.color_code)) = UPPER(TRIM(s.color_code))
             AND c.is_active = 1
            SET s.csi_color_master_id = c.id
            WHERE s.csi_color_master_id IS NULL
            """
        )
    )
    db.flush()
    linked = int(result.rowcount or 0)
    orphan = int(
        db.scalar(
            select(func.count())
            .select_from(ColorSwatchRecipe)
            .where(
                ColorSwatchRecipe.is_active.is_(True),
                ColorSwatchRecipe.csi_color_master_id.is_(None),
            )
        )
        or 0
    )
    return {"linked": linked, "orphan_remaining": orphan}
