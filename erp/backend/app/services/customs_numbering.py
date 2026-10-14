"""Nomor AJU BC 2.7 & nomor kontrak KPJB."""

from __future__ import annotations

from datetime import date

ROMAN_MONTHS = {
    1: "I",
    2: "II",
    3: "III",
    4: "IV",
    5: "V",
    6: "VI",
    7: "VII",
    8: "VIII",
    9: "IX",
    10: "X",
    11: "XI",
    12: "XII",
}


def normalize_aju_seq(raw: str | int | None) -> str:
    """Wajib 6 digit (xxxxxx pada NOMOR AJU)."""
    s = "".join(ch for ch in str(raw or "").strip() if ch.isdigit())
    if len(s) != 6:
        raise ValueError("aju_seq_invalid")
    return s


def kontrak_seq_from_date(on_date: date) -> str:
    """xxx otomatis: '0' + tanggal (hari, 2 digit). Contoh tgl 2 → 002."""
    return f"0{on_date.day:02d}"


def generate_nomor_aju(on_date: date, aju_seq: str | int) -> str:
    """format: 000027TOP417yyyymmddxxxxxx"""
    seq = normalize_aju_seq(aju_seq)
    return f"000027TOP417{on_date.strftime('%Y%m%d')}{seq}"


def generate_nomor_kontrak(customer_code: str | None, on_date: date) -> str:
    """format: xxx/KPJB-THI/kodecustomer/m(romawi)/yyyy

    xxx otomatis dari tanggal (0 + dd). Contoh: 002/KPJB-THI/SC006/X/2026
    """
    seq = kontrak_seq_from_date(on_date)
    code = (customer_code or "").strip().upper() or "XXXXX"
    roman = ROMAN_MONTHS.get(int(on_date.month), str(on_date.month))
    return f"{seq}/KPJB-THI/{code}/{roman}/{on_date.year}"
