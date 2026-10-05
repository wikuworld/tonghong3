"""Readonly audit report: master integrity (orphan / mismatch)."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# Allow `python scripts/audit_master_integrity.py` inside container
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sqlalchemy import func, select, text

from app.db import SessionLocal
from app.models import (
    Brand,
    ColorSwatchRecipe,
    FluorescentColorMaster,
    MasterItem,
)
from app.services.color_swatch import normalize_swatch_material_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit master integrity")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    db = SessionLocal()
    report: dict = {}

    report["swatch_active"] = db.scalar(
        select(func.count()).select_from(ColorSwatchRecipe).where(ColorSwatchRecipe.is_active.is_(True))
    )
    report["swatch_brand_id_null"] = db.scalar(
        select(func.count())
        .select_from(ColorSwatchRecipe)
        .where(ColorSwatchRecipe.is_active.is_(True), ColorSwatchRecipe.brand_id.is_(None))
    )
    report["swatch_customer_id_null"] = db.scalar(
        select(func.count())
        .select_from(ColorSwatchRecipe)
        .where(ColorSwatchRecipe.is_active.is_(True), ColorSwatchRecipe.customer_id.is_(None))
    )
    report["fluoro_brand_id_null"] = db.scalar(
        select(func.count())
        .select_from(FluorescentColorMaster)
        .where(
            FluorescentColorMaster.is_active.is_(True),
            FluorescentColorMaster.brand_id.is_(None),
            FluorescentColorMaster.buyer_code != "GLOBAL",
        )
    )

    brand_codes = {
        str(c).strip().upper()
        for c in db.scalars(select(Brand.code)).all()
        if c
    }
    swatch_buyers = db.execute(
        text(
            """
            SELECT buyer_code, COUNT(*) c FROM color_swatch_recipes
            WHERE is_active=1 GROUP BY buyer_code
            """
        )
    ).fetchall()
    report["swatch_buyers_missing_brand"] = [
        {"buyer_code": b, "count": int(c)}
        for b, c in swatch_buyers
        if b and str(b).upper() not in brand_codes and str(b).upper() != "GLOBAL"
    ]

    item_norms = set()
    for m in db.scalars(select(MasterItem.material_name)).all():
        n = normalize_swatch_material_name(m)
        if n:
            item_norms.add(n)
    missing = Counter()
    for m, cnt in db.execute(
        text(
            """
            SELECT material_name, COUNT(*) FROM color_swatch_recipes
            WHERE is_active=1 GROUP BY material_name
            """
        )
    ):
        n = normalize_swatch_material_name(m)
        if n and n not in item_norms:
            missing[n] += int(cnt)
    report["swatch_material_norm_missing_top"] = [
        {"norm": k, "count": v} for k, v in missing.most_common(20)
    ]

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        for k, v in report.items():
            print(f"{k}: {v}")
    db.close()


if __name__ == "__main__":
    main()
