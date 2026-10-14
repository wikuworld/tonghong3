"""Samakan identitas baris PO dengan master item yang ditautkan."""

from __future__ import annotations

import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import MasterItem

_WS = re.compile(r"\s+")
_THICKNESS_GAP = re.compile(r"\s*([-–])\s*")
_CODE_IN_PARENS = re.compile(r"\(([A-Za-z0-9][A-Za-z0-9._/\- ]{0,62})\)")


def _norm(value: str | None) -> str:
    return _WS.sub(" ", str(value or "").strip()).casefold()


def _norm_thickness(value: str | None) -> str:
    raw = _THICKNESS_GAP.sub(r"\1", str(value or "").strip()).replace("–", "-")
    return _WS.sub("", raw).casefold()


def _is_waiting_color_ref(value: str | None) -> bool:
    """Placeholder CS belum dari customer — tidak dibandingkan ke color_code master."""
    key = _WS.sub(" ", str(value or "").strip().upper()).replace(" ", "")
    return key in ("WAITINGC/S", "WAITINGCS", "WAITC/S", "WAITCS")


def po_line_uses_waiting_cs(
    color_reference: str | None,
    color_standard: str | None = None,
) -> bool:
    """Baris pakai opsi Waiting C/S — lewati validasi identitas/kode vs master item."""
    return _is_waiting_color_ref(color_reference) or _is_waiting_color_ref(color_standard)


def _color_code_token(value: str | None) -> str:
    """Samakan logika frontend: kode dari tanda kurung, atau string tanpa spasi."""
    raw = str(value or "").strip()
    if not raw:
        return ""
    m = _CODE_IN_PARENS.search(raw)
    if m:
        return str(m.group(1) or "").strip().casefold()
    if not _WS.search(raw):
        return raw.casefold()
    return raw.casefold()


def align_po_line_to_master_item(
    db: Session,
    *,
    master_item_id: int | None,
    material_name: str | None,
    color: str | None,
    emboss: str | None,
    thickness_text: str | None,
    color_reference: str | None,
    color_standard: str | None = None,
) -> str | None:
    """Tolak baris yang identitasnya beda dari master. Kode warna kosong diisi dari color_code."""
    if po_line_uses_waiting_cs(color_reference, color_standard):
        ref = str(color_reference or "").strip()
        if ref:
            return ref
        std = str(color_standard or "").strip()
        return std or None
    if master_item_id is None:
        return color_reference
    item = db.get(MasterItem, int(master_item_id))
    if item is None:
        raise HTTPException(status_code=400, detail="Master item tidak ditemukan")
    bad: list[str] = []
    if _norm(item.material_name) != _norm(material_name):
        bad.append("material")
    if _norm(item.color) != _norm(color):
        bad.append("warna")
    if _norm(item.emboss) != _norm(emboss):
        bad.append("emboss")
    if _norm_thickness(item.thickness_range) != _norm_thickness(thickness_text):
        bad.append("tebal")
    if bad:
        raise HTTPException(
            status_code=400,
            detail="Baris PO tidak sama dengan master item (" + ", ".join(bad) + ")",
        )
    code = str(item.color_code or "").strip()
    ref = str(color_reference or "").strip()
    if not code:
        return ref or None
    if not ref:
        return code
    if _color_code_token(ref) != _color_code_token(code):
        raise HTTPException(
            status_code=400,
            detail=f"Kode warna {ref} tidak sama dengan master item ({code})",
        )
    return code
