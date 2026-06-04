"""Generator nomor lot sesuai format marketing (prefix+factory+YYMMDD+seq)."""

from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LotSequence, MasterItem, PoDetail, PoHeader


def _material_group_from_detail(db: Session, detail: PoDetail) -> str:
    """Return 'suede' or 'pu'. Raise 400 bila tidak bisa ditentukan."""
    if detail.master_item_id:
        mi = db.get(MasterItem, detail.master_item_id)
        cat = (mi.category or "").strip().lower() if mi else ""
        # di validator MasterItem: PU, Suide, SubKon
        if cat in {"suide", "suede"}:
            return "suede"
        if cat in {"pu"}:
            return "pu"
    # fallback heuristik
    vt = (detail.vir_softness_type or "").strip().lower()
    if "pu" in vt:
        return "pu"
    mn = (detail.material_name or "").strip().lower()
    if "suede" in mn or "suide" in mn:
        return "suede"
    if "pu" in mn:
        return "pu"
    raise HTTPException(status_code=400, detail="Material group tidak bisa ditentukan (butuh master item PU/Suide).")


def _prefix_for(group: str, po_category: str) -> str:
    c = (po_category or "production").strip().lower()
    if group == "suede":
        return {
            "production": "MYC",
            "sample": "SYC",
            "claim": "BYC",
            "return": "QYC",
            "subcont": "QYC",
            "suede": "MYC",
        }.get(c, "MYC")
    if group == "pu":
        return {
            "production": "PUM",
            "sample": "PUS",
            "claim": "PUC",
            "return": "PUR",
            "subcont": "PUR",
            "suede": "PUM",
        }.get(c, "PUM")
    raise HTTPException(status_code=400, detail="Material group tidak valid.")


def _material_group_from_inputs(
    db: Session,
    *,
    master_item_id: int | None,
    material_name: str | None,
    vir_softness_type: str | None,
) -> str:
    if master_item_id:
        mi = db.get(MasterItem, master_item_id)
        cat = (mi.category or "").strip().lower() if mi else ""
        if cat in {"suide", "suede"}:
            return "suede"
        if cat in {"pu"}:
            return "pu"
    vt = (vir_softness_type or "").strip().lower()
    if "pu" in vt:
        return "pu"
    mn = (material_name or "").strip().lower()
    if "suede" in mn or "suide" in mn:
        return "suede"
    if "pu" in mn:
        return "pu"
    raise HTTPException(status_code=400, detail="Material group tidak bisa ditentukan (butuh master item PU/Suide).")


def _lot_number_format(
    *,
    prefix: str,
    factory: str,
    date_yymmdd: str,
    seq_value: int,
) -> str:
    return f"{prefix}{factory}{date_yymmdd}{seq_value:03d}"


def peek_lot_number(
    db: Session,
    *,
    po_category: str,
    factory_code: str,
    material_group: str,
    at: datetime | None = None,
) -> str:
    """Preview nomor lot berikutnya tanpa menaikkan sequence (untuk draft UI)."""
    now = at or datetime.now()
    date_ymd = now.strftime("%Y%m%d")
    date_yymmdd = now.strftime("%y%m%d")
    prefix = _prefix_for(material_group, po_category)
    factory = (factory_code or "").strip()
    if not factory:
        raise HTTPException(status_code=400, detail="Factory code PO belum diisi.")
    seq = db.scalars(
        select(LotSequence).where(
            LotSequence.prefix == prefix,
            LotSequence.factory_code == factory,
            LotSequence.date_ymd == date_ymd,
        )
    ).first()
    n = (int(seq.last_value) + 1) if seq else 1
    return _lot_number_format(prefix=prefix, factory=factory, date_yymmdd=date_yymmdd, seq_value=n)


def generate_lot_number(
    db: Session,
    *,
    po_category: str,
    factory_code: str,
    material_group: str,
    at: datetime | None = None,
) -> str:
    now = at or datetime.now()
    date_ymd = now.strftime("%Y%m%d")
    date_yymmdd = now.strftime("%y%m%d")

    prefix = _prefix_for(material_group, po_category)
    factory = (factory_code or "").strip()
    if not factory:
        raise HTTPException(status_code=400, detail="Factory code PO belum diisi.")

    seq = db.scalars(
        select(LotSequence)
        .where(
            LotSequence.prefix == prefix,
            LotSequence.factory_code == factory,
            LotSequence.date_ymd == date_ymd,
        )
        .with_for_update()
    ).first()
    if seq is None:
        seq = LotSequence(prefix=prefix, factory_code=factory, date_ymd=date_ymd, last_value=1)
        db.add(seq)
        db.flush()
        n = 1
    else:
        seq.last_value += 1
        n = int(seq.last_value)
        db.flush()

    return _lot_number_format(prefix=prefix, factory=factory, date_yymmdd=date_yymmdd, seq_value=n)


def generate_po_detail_lot_number(db: Session, detail_id: int, *, at: datetime | None = None) -> str:
    detail = db.get(PoDetail, detail_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Detail PO tidak ditemukan")
    po = db.get(PoHeader, detail.po_id) if detail.po_id else None
    if not po:
        raise HTTPException(status_code=404, detail="PO tidak ditemukan")
    factory = (po.factory_code or "").strip()
    if not factory:
        raise HTTPException(status_code=400, detail="Factory code PO belum diisi.")

    now = at or datetime.now()
    group = _material_group_from_detail(db, detail)
    return generate_lot_number(db, po_category=po.po_category, factory_code=factory, material_group=group, at=now)

