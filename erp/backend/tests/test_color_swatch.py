"""Tests color swatch import & parse."""

import io
from datetime import date

from app.services.color_swatch import (
    iter_csv_recipes,
    normalize_factory_key,
    parse_csv_row,
    parse_entered_date,
    suggest_next_color_standard,
)


def test_normalize_factory_key():
    assert normalize_factory_key("  nikomas  ") == "NIKOMAS"


def test_parse_entered_date_month_name():
    assert parse_entered_date("22/Jan/26") == date(2026, 1, 22)
    assert parse_entered_date("13/May/2026") == date(2026, 5, 13)
    assert parse_entered_date("12-01-2019") == date(2019, 1, 12)


def test_parse_csv_row_valid():
    row = {
        "CUSTOMER": "NIKOMAS",
        "COLOR CODE": "ADBD",
        "COLOR NAME ": "METAL GREY",
        "EMBOS": "DE-73",
        "COLOR SWATCH": "SCOTDIC",
        "BACKING": "WHITE",
        "NO URUT": "A589",
        "BRAND": "ADIDAS",
        "MATERIAL": "PU COATED LEATHER",
        "TGGL MASUK": "12-01-2019",
    }
    parsed = parse_csv_row(row, "test.csv")
    assert parsed is not None
    assert parsed["factory_key"] == "NIKOMAS"
    assert parsed["buyer_code"] == "ADIDAS"
    assert parsed["color_code"] == "ADBD"


def test_parse_csv_row_canonical_factory_and_data_cs_date():
    row = {
        "CUSTOMER": "HWASEUNG HWP",
        "COLOR CODE": "C123",
        "COLOR NAME": "WOLF GREY",
        "EMBOS": "DE-7",
        "COLOR SWATCH": "TMHW036-WG",
        "BACKING": "WHITE",
        "NO URUT": "1",
        "BRAND": "NIKE",
        "MATERIAL": "METAL SHIFT LEATHER",
        "TGGL MASUK": "22/Jan/26",
    }
    parsed = parse_csv_row(row, "DATA_CS_2026-07-28.csv")
    assert parsed is not None
    assert parsed["factory_key"] == "HWASEUNG (HWP)"
    assert parsed["color_standard"] == "TMHW036-WG"
    assert parsed["entered_at"] == date(2026, 1, 22)
    assert parsed["material_name"] == "METAL SHIFT LEATHER"


def test_parse_csv_row_skips_empty():
    assert parse_csv_row({"CUSTOMER": "", "COLOR CODE": "", "BRAND": "NIKE"}, "x") is None


def test_iter_csv_minimal():
    csv_text = (
        "CUSTOMER;COLOR CODE;COLOR NAME ;EMBOS;COLOR SWATCH;BACKING;NO URUT;BRAND;MATERIAL;TGGL MASUK\n"
        "NIKOMAS;X1;RED;DE-7;SCOTDIC;WHITE;A1;ADIDAS;PU COATED LEATHER;01-01-2020\n"
    )
    rows = iter_csv_recipes(io.StringIO(csv_text), "t.csv")
    assert len(rows) == 1
    assert rows[0]["color_code"] == "X1"


class _FakeScalars:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class _FakeDb:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self, _stmt):
        return _FakeScalars(self._rows)


def test_suggest_next_color_standard_increments_seq():
    db = _FakeDb(["TMSL0432026100301", "TMSL0432026100302", "OTHER"])
    assert (
        suggest_next_color_standard(db, customer_code="SL043", on_date=date(2026, 10, 3))
        == "TMSL0432026100303"
    )


def test_suggest_next_color_standard_starts_at_01():
    db = _FakeDb([])
    assert (
        suggest_next_color_standard(db, customer_code="SL043", on_date=date(2026, 10, 3))
        == "TMSL0432026100301"
    )
