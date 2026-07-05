"""Tests color swatch import & parse."""

import io

from app.services.color_swatch import iter_csv_recipes, normalize_factory_key, parse_csv_row


def test_normalize_factory_key():
    assert normalize_factory_key("  nikomas  ") == "NIKOMAS"


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
