"""Urai tebal dan warna dari nama master kulit bila kolomnya masih kosong."""

from __future__ import annotations

import re

_MM_THEN_COLOR = re.compile(
    r"^(?P<head>.+?)(?:\s+|,\s*)(?P<thick>\d+\.\d+)\s*mm\s+(?P<color>[A-Za-z][A-Za-z \-]+)$",
    re.IGNORECASE,
)
_THICK_TAIL = re.compile(
    r"^(?P<head>.+?)(?:\s+|,\s*)(?P<thick>\d+\.\d+(?:\s*-\s*\d+\.\d+)?)\s*(?:mm)?$",
    re.IGNORECASE,
)
_HYPHEN_THICK = re.compile(r"^(?P<head>[0-9A-Za-z]{2,6})-(?P<thick>\d+\.\d+)$")
_CODE_TOKEN = re.compile(r"^(?=[0-9A-Z-]{2,6}$)(?=.*\d)[0-9A-Z-]+$")


def _clean_thickness(raw: str) -> str:
    return re.sub(r"\s+", "", raw or "")


def _color_from_head(head: str) -> str | None:
    text = (head or "").strip(" ,")
    if not text or not re.search(r"[A-Za-z]", text):
        return None
    if _CODE_TOKEN.match(text.upper()):
        return None
    return text


def kulit_spec_from_name(name: str | None) -> dict[str, str | None]:
    """Kembalikan tebal dan warna yang pasti. Keduanya None bila nama tidak terurai."""
    raw = (name or "").strip()
    empty = {"thickness": None, "color": None}
    if not raw:
        return empty
    colored = _MM_THEN_COLOR.match(raw)
    if colored:
        color = _color_from_head(colored.group("color"))
        return {"thickness": _clean_thickness(colored.group("thick")), "color": color}
    tail = _THICK_TAIL.match(raw)
    if tail:
        return {
            "thickness": _clean_thickness(tail.group("thick")),
            "color": _color_from_head(tail.group("head")),
        }
    hyphen = _HYPHEN_THICK.match(raw)
    if hyphen:
        return {
            "thickness": _clean_thickness(hyphen.group("thick")),
            "color": _color_from_head(hyphen.group("head")),
        }
    return empty
