"""Normalisasi nomor lot historis (prefix subcont, placeholder legacy, sequence)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LotSequence, PoDetail, PoHeader, ProductionDetail

# Prefix subcont lama (bersama retur) → prefix terpisah.
SUBCONT_LEGACY_LOT_PREFIX: dict[str, str] = {
    "QYC": "KYC",
    "PUR": "PUK",
}

# Placeholder lama di demo / input awal — kosongkan agar bisa generate ulang.
_LEGACY_PLACEHOLDER_RE = re.compile(
    r"^(THI-?|PU-\d{1,8})$",
    re.IGNORECASE,
)

_MARKETING_LOT_RE = re.compile(r"^[A-Z]{3}.+\d{6}\d{3}$")


@dataclass
class LotNormalizeResult:
    subcont_prefix_updated: int = 0
    system_reference_updated: int = 0
    production_lot_updated: int = 0
    legacy_cleared: int = 0
    sequences_upserted: int = 0
    skipped: int = 0
    samples: list[dict[str, Any]] = field(default_factory=list)
    dry_run: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "subcont_prefix_updated": self.subcont_prefix_updated,
            "system_reference_updated": self.system_reference_updated,
            "production_lot_updated": self.production_lot_updated,
            "legacy_cleared": self.legacy_cleared,
            "sequences_upserted": self.sequences_upserted,
            "skipped": self.skipped,
            "dry_run": self.dry_run,
            "samples": self.samples,
        }


def rewrite_subcont_lot_prefix(lot: str | None) -> str | None:
    """Ubah QYC→KYC atau PUR→PUK untuk lot subcont; None jika tidak perlu."""
    raw = (lot or "").strip()
    if not raw:
        return None
    for old, new in SUBCONT_LEGACY_LOT_PREFIX.items():
        if raw.startswith(old):
            return new + raw[len(old) :]
    return None


def is_legacy_lot_placeholder(lot: str | None) -> bool:
    raw = (lot or "").strip()
    if not raw:
        return False
    if _LEGACY_PLACEHOLDER_RE.match(raw):
        return True
    # Lot terlalu pendek / bukan format marketing 3+factory+6+3
    if not _MARKETING_LOT_RE.match(raw.upper()):
        if raw.upper().startswith(("MYC", "SYC", "BYC", "QYC", "KYC", "PUM", "PUS", "PUC", "PUR", "PUK")):
            return False
        if raw.startswith("PU-") or raw.startswith("THI"):
            return True
    return False


def _yymmdd_to_date_ymd(yymmdd: str) -> str | None:
    if len(yymmdd) != 6 or not yymmdd.isdigit():
        return None
    return f"20{yymmdd}"


def _parse_marketing_lot(lot: str, factory_code: str) -> tuple[str, str, int] | None:
    """Return (prefix, date_ymd, seq) bila lot cocok factory."""
    raw = (lot or "").strip()
    factory = (factory_code or "").strip()
    if len(raw) < 12 or not factory:
        return None
    prefix = raw[:3]
    if not raw.startswith(prefix + factory):
        return None
    tail = raw[3 + len(factory) :]
    if len(tail) != 9 or not tail.isdigit():
        return None
    date_ymd = _yymmdd_to_date_ymd(tail[:6])
    if not date_ymd:
        return None
    return prefix, date_ymd, int(tail[6:])


def _bump_lot_sequence(
    db: Session,
    *,
    prefix: str,
    factory_code: str,
    date_ymd: str,
    seq_value: int,
    dry_run: bool,
) -> bool:
    row = db.scalars(
        select(LotSequence).where(
            LotSequence.prefix == prefix,
            LotSequence.factory_code == factory_code,
            LotSequence.date_ymd == date_ymd,
        )
    ).first()
    if row is None:
        if not dry_run:
            db.add(
                LotSequence(
                    prefix=prefix,
                    factory_code=factory_code,
                    date_ymd=date_ymd,
                    last_value=seq_value,
                )
            )
        return True
    if seq_value > int(row.last_value or 0):
        if not dry_run:
            row.last_value = seq_value
        return True
    return False


def _record_sample(result: LotNormalizeResult, item: dict[str, Any]) -> None:
    if len(result.samples) < 25:
        result.samples.append(item)


def normalize_lot_references(
    db: Session,
    *,
    dry_run: bool = True,
    clear_legacy_placeholders: bool = True,
) -> LotNormalizeResult:
    """Selaraskan thi_line_ref / system_reference / production lot ke aturan prefix terbaru."""
    result = LotNormalizeResult(dry_run=dry_run)

    rows = db.execute(
        select(PoDetail, PoHeader)
        .join(PoHeader, PoDetail.po_id == PoHeader.id)
        .order_by(PoDetail.id.asc())
    ).all()

    for detail, header in rows:
        cat = (header.po_category or "production").strip().lower()
        factory = (header.factory_code or "").strip()
        old_thi = (detail.thi_line_ref or "").strip()
        sys_ref = (detail.system_reference or "").strip()
        thi = old_thi

        if cat == "subcont" and thi:
            new_thi = rewrite_subcont_lot_prefix(thi)
            if new_thi and new_thi != thi:
                _record_sample(
                    result,
                    {
                        "po_detail_id": detail.id,
                        "po_number": header.po_number,
                        "field": "thi_line_ref",
                        "before": thi,
                        "after": new_thi,
                    },
                )
                if not dry_run:
                    detail.thi_line_ref = new_thi
                result.subcont_prefix_updated += 1
                thi = new_thi

                if sys_ref and (sys_ref == old_thi or rewrite_subcont_lot_prefix(sys_ref)):
                    new_sys = rewrite_subcont_lot_prefix(sys_ref) or new_thi
                    if new_sys != sys_ref:
                        _record_sample(
                            result,
                            {
                                "po_detail_id": detail.id,
                                "po_number": header.po_number,
                                "field": "system_reference",
                                "before": sys_ref,
                                "after": new_sys,
                            },
                        )
                        if not dry_run:
                            detail.system_reference = new_sys
                        result.system_reference_updated += 1

                parsed = _parse_marketing_lot(new_thi, factory)
                if parsed:
                    prefix, date_ymd, seq = parsed
                    if _bump_lot_sequence(
                        db,
                        prefix=prefix,
                        factory_code=factory,
                        date_ymd=date_ymd,
                        seq_value=seq,
                        dry_run=dry_run,
                    ):
                        result.sequences_upserted += 1

        if clear_legacy_placeholders and thi and is_legacy_lot_placeholder(thi):
            _record_sample(
                result,
                {
                    "po_detail_id": detail.id,
                    "po_number": header.po_number,
                    "field": "thi_line_ref",
                    "before": thi,
                    "after": None,
                    "reason": "legacy_placeholder",
                },
            )
            if not dry_run:
                detail.thi_line_ref = None
            result.legacy_cleared += 1
            thi = ""

        if thi:
            prod_rows = db.scalars(
                select(ProductionDetail).where(ProductionDetail.po_detail_id == detail.id)
            ).all()
            current_thi = (detail.thi_line_ref or "").strip() if not dry_run else thi
            for prod in prod_rows:
                pl = (prod.lot_number or "").strip()
                if not pl:
                    continue
                new_pl: str | None = None
                if cat == "subcont":
                    new_pl = rewrite_subcont_lot_prefix(pl)
                if new_pl and new_pl != pl:
                    if not dry_run:
                        prod.lot_number = new_pl
                    result.production_lot_updated += 1
                elif current_thi and pl != current_thi and pl == old_thi:
                    if not dry_run:
                        prod.lot_number = current_thi
                    result.production_lot_updated += 1

    if not dry_run:
        db.commit()
    return result
