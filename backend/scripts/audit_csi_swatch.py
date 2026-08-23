#!/usr/bin/env python3
"""Laporan selisih CSI ↔ swatch ↔ alias (bukan rewrite)."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from sqlalchemy import func, select

from app.db import SessionLocal
from app.models import ColorCodeAlias, ColorSwatchRecipe, CsiColorMaster


def main() -> None:
    db = SessionLocal()
    try:
        csi_n = int(db.scalar(select(func.count(CsiColorMaster.id)).where(CsiColorMaster.is_active.is_(True))) or 0)
        sw_n = int(db.scalar(select(func.count(ColorSwatchRecipe.id)).where(ColorSwatchRecipe.is_active.is_(True))) or 0)
        linked = int(
            db.scalar(
                select(func.count(ColorSwatchRecipe.id)).where(
                    ColorSwatchRecipe.is_active.is_(True),
                    ColorSwatchRecipe.csi_color_master_id.is_not(None),
                )
            )
            or 0
        )
        orphan = sw_n - linked
        pending = int(
            db.scalar(
                select(func.count(ColorCodeAlias.id)).where(ColorCodeAlias.steward_status == "pending")
            )
            or 0
        )
        print(f"csi_active={csi_n} swatch_active={sw_n} linked={linked} orphan={orphan} alias_pending={pending}")
        rows = db.execute(
            select(ColorSwatchRecipe.buyer_code, func.count(ColorSwatchRecipe.id))
            .where(
                ColorSwatchRecipe.is_active.is_(True),
                ColorSwatchRecipe.csi_color_master_id.is_(None),
            )
            .group_by(ColorSwatchRecipe.buyer_code)
            .order_by(func.count(ColorSwatchRecipe.id).desc())
        ).all()
        for buyer, n in rows:
            print(f"orphan_buyer {buyer}={n}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
