"""Unit test template & export BC 3.0 customs."""

from __future__ import annotations

import io
import zipfile

from app.services.customs_templates import (
    KODE_DOKUMEN_BC30_EKSPOR,
    KODE_ENTITAS_EKSPORTIR,
    SHEET_COLUMNS,
    build_entitas_row,
    build_row,
    draft_sheet_column_keys,
    sheet_column_keys,
)


def test_barang_columns_match_ceisa_template():
    cols = sheet_column_keys("BARANG")
    assert "NOMOR AJU" in cols
    assert "HS" in cols
    assert "URAIAN" in cols
    assert "NETTO" in cols
    assert "FOB" in cols
    assert len(cols) >= 60


def test_build_row_fills_only_known_columns():
    row = build_row(
        "HEADER",
        {
            "NOMOR AJU": "TH2607011200001234",
            "KODE DOKUMEN": KODE_DOKUMEN_BC30_EKSPOR,
            "KODE JENIS EKSPOR": "1",
            "UNKNOWN": "skip",
        },
    )
    assert row["NOMOR AJU"] == "TH2607011200001234"
    assert row["KODE DOKUMEN"] == "30"
    assert row["KODE JENIS EKSPOR"] == "1"
    assert "UNKNOWN" not in row


def test_build_entitas_exporter():
    row = build_entitas_row(
        "AJU001",
        1,
        KODE_ENTITAS_EKSPORTIR,
        nama="PT. TONG HONG TANNERY INDONESIA",
        kode_negara="ID",
    )
    assert row["KODE ENTITAS"] == "2"
    assert row["NAMA ENTITAS"].startswith("PT. TONG HONG")


def test_draft_sheet_column_keys_subset():
    keys = draft_sheet_column_keys()
    assert set(keys.keys()) == {"HEADER", "ENTITAS", "KEMASAN", "BARANG", "VERSI"}
    for code, cols in keys.items():
        assert cols == SHEET_COLUMNS[code]


def test_export_zip_contains_numbered_csv(monkeypatch):
    from app.services import customs_export

    fake_detail = {
        "nomor_aju": "TEST-AJU-001",
        "meta_json": {
            "sheet_column_keys": {
                "HEADER": ["NOMOR AJU", "KODE DOKUMEN"],
                "VERSI": ["VERSI"],
            }
        },
        "sheets": {
            "HEADER": [{"NOMOR AJU": "TEST-AJU-001", "KODE DOKUMEN": "30"}],
            "VERSI": [{"VERSI": "4.0"}],
        },
    }

    class _Db:
        pass

    monkeypatch.setattr(
        customs_export,
        "declaration_to_api_dict",
        lambda db, decl_id: fake_detail if decl_id == 1 else {},
    )

    data, name = customs_export.export_declaration_zip(_Db(), 1)
    assert name.endswith("_bc30.zip")
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = set(zf.namelist())
        assert "01_HEADER.csv" in names
        assert "19_VERSI.csv" in names
        header = zf.read("01_HEADER.csv").decode("utf-8")
        assert "NOMOR AJU" in header
        assert "TEST-AJU-001" in header
