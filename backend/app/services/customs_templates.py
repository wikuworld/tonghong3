"""Template kolom BC 3.0 / Core Customs (referensi CEISA 4.0 & ekstraksi AJU)."""

from __future__ import annotations

from typing import Any

# Urutan file ekspor: NN_SHEET.csv (sama folder ekstraksi Core Customs)
SHEET_EXPORT_FILENAMES: dict[str, str] = {
    "HEADER": "01_HEADER.csv",
    "ENTITAS": "02_ENTITAS.csv",
    "DOKUMEN": "03_DOKUMEN.csv",
    "PENGANGKUT": "04_PENGANGKUT.csv",
    "KEMASAN": "05_KEMASAN.csv",
    "KONTAINER": "06_KONTAINER.csv",
    "BARANG": "07_BARANG.csv",
    "BARANGTARIF": "08_BARANGTARIF.csv",
    "BARANGDOKUMEN": "09_BARANGDOKUMEN.csv",
    "BARANGENTITAS": "10_BARANGENTITAS.csv",
    "BARANGSPEKKHUSUS": "11_BARANGSPEKKHUSUS.csv",
    "BARANGVD": "12_BARANGVD.csv",
    "BAHANBAKU": "13_BAHANBAKU.csv",
    "BAHANBAKUTARIF": "14_BAHANBAKUTARIF.csv",
    "BAHANBAKUDOKUMEN": "15_BAHANBAKUDOKUMEN.csv",
    "PUNGUTAN": "16_PUNGUTAN.csv",
    "JAMINAN": "17_JAMINAN.csv",
    "BANKDEVISA": "18_BANKDEVISA.csv",
    "VERSI": "19_VERSI.csv",
}

# Kode dokumen PEB BC 3.0 (ekspor umum)
KODE_DOKUMEN_BC30_EKSPOR = "30"

# Referensi entitas CEISA (https://ceisa40.gitbook.io/pia-ceisa40/referensi/referensi-entitas)
KODE_ENTITAS_EKSPORTIR = "2"
KODE_ENTITAS_PEMILIK = "7"
KODE_ENTITAS_PENGIRIM = "9"
KODE_ENTITAS_PENJUAL = "10"

# NPWP 16 digit (kode jenis identitas CEISA)
KODE_JENIS_IDENTITAS_NPWP16 = "6"

# Eksportir internal (PT Tong Hong) — NPWP diisi manual di CEISA jika belum dikonfigurasi
EXPORTER_NAME = "PT. TONG HONG TANNERY INDONESIA"
EXPORTER_ADDRESS = (
    "Kawasan Industri Modern II JL. Modern Industri XIV/W-1, "
    "Ds. Barengkok Kec. Kibin Serang-Banten"
)
EXPORTER_COUNTRY = "ID"

SHEET_COLUMNS: dict[str, list[str]] = {
    "HEADER": [
        "NOMOR AJU",
        "KODE DOKUMEN",
        "KODE KANTOR",
        "KODE KANTOR BONGKAR",
        "KODE KANTOR PERIKSA",
        "KODE KANTOR TUJUAN",
        "KODE KANTOR EKSPOR",
        "KODE JENIS IMPOR",
        "KODE JENIS EKSPOR",
        "KODE JENIS TPB",
        "KODE JENIS PLB",
        "KODE JENIS PROSEDUR",
        "KODE TUJUAN PEMASUKAN",
        "KODE TUJUAN PENGIRIMAN",
        "KODE TUJUAN TPB",
        "KODE CARA DAGANG",
        "KODE CARA BAYAR",
        "KODE CARA BAYAR LAINNYA",
        "KODE GUDANG ASAL",
        "KODE GUDANG TUJUAN",
        "KODE JENIS KIRIM",
        "KODE JENIS PENGIRIMAN",
        "KODE KATEGORI EKSPOR",
        "KODE KATEGORI MASUK FTZ",
        "KODE KATEGORI KELUAR FTZ",
        "KODE KATEGORI BARANG FTZ",
        "KODE LOKASI",
        "KODE LOKASI BAYAR",
        "LOKASI ASAL",
        "LOKASI TUJUAN",
        "KODE DAERAH ASAL",
        "KODE GUDANG ASAL",
        "KODE GUDANG TUJUAN",
        "KODE NEGARA TUJUAN",
        "KODE TUTUP PU",
        "NOMOR BC11",
        "TANGGAL BC11",
        "NOMOR POS",
        "NOMOR SUB POS",
        "KODE PELABUHAN BONGKAR",
        "KODE PELABUHAN MUAT",
        "KODE PELABUHAN MUAT AKHIR",
        "KODE PELABUHAN TRANSIT",
        "KODE PELABUHAN TUJUAN",
        "KODE PELABUHAN EKSPOR",
        "KODE TPS",
        "TANGGAL BERANGKAT",
        "TANGGAL EKSPOR",
        "TANGGAL MASUK",
        "TANGGAL MUAT",
        "TANGGAL TIBA",
        "TANGGAL PERIKSA",
        "TEMPAT STUFFING",
        "TANGGAL STUFFING",
        "KODE TANDA PENGAMAN",
        "JUMLAH TANDA PENGAMAN",
        "FLAG CURAH",
        "FLAG",
    ],
    "ENTITAS": [
        "NOMOR AJU",
        "SERI",
        "KODE ENTITAS",
        "KODE JENIS IDENTITAS",
        "NOMOR IDENTITAS",
        "NAMA ENTITAS",
        "ALAMAT ENTITAS",
        "NIB ENTITAS",
        "KODE JENIS API",
        "KODE STATUS",
        "NOMOR IJIN ENTITAS",
        "TANGGAL IJIN ENTITAS",
        "KODE NEGARA",
        "NIPER ENTITAS",
    ],
    "DOKUMEN": [
        "NOMOR AJU",
        "SERI",
        "KODE DOKUMEN",
        "NOMOR DOKUMEN",
        "TANGGAL DOKUMEN",
        "KODE FASILITAS",
        "KODE IJIN",
    ],
    "PENGANGKUT": [
        "NOMOR AJU",
        "SERI",
        "KODE CARA ANGKUT",
        "NAMA PENGANGKUT",
        "NOMOR PENGANGKUT",
        "KODE BENDERA",
        "CALL SIGN",
        "FLAG ANGKUT PLB",
    ],
    "KEMASAN": [
        "NOMOR AJU",
        "SERI",
        "KODE KEMASAN",
        "JUMLAH KEMASAN",
        "MEREK",
    ],
    "KONTAINER": [
        "NOMOR AJU",
        "SERI",
        "NOMOR KONTINER",
        "KODE UKURAN KONTINER",
        "KODE JENIS KONTINER",
        "KODE TIPE KONTINER",
    ],
    "BARANG": [
        "NOMOR AJU",
        "SERI BARANG",
        "HS",
        "KODE BARANG",
        "URAIAN",
        "MEREK",
        "TIPE",
        "UKURAN",
        "SPESIFIKASI LAIN",
        "KODE SATUAN",
        "JUMLAH SATUAN",
        "KODE KEMASAN",
        "JUMLAH KEMASAN",
        "KODE DOKUMEN ASAL",
        "KODE KANTOR ASAL",
        "NOMOR DAFTAR ASAL",
        "TANGGAL DAFTAR ASAL",
        "NOMOR AJU ASAL",
        "SERI BARANG ASAL",
        "NETTO",
        "BRUTO",
        "VOLUME",
        "SALDO AWAL",
        "SALDO AKHIR",
        "JUMLAH REALISASI",
        "CIF",
        "CIF RUPIAH",
        "NDPBM",
        "FOB",
        "ASURANSI",
        "FREIGHT",
        "NILAI TAMBAH",
        "DISKON",
        "HARGA PENYERAHAN",
        "HARGA PEROLEHAN",
        "HARGA SATUAN",
        "HARGA EKSPOR",
        "HARGA PATOKAN",
        "NILAI BARANG",
        "NILAI JASA",
        "NILAI DANA SAWIT",
        "NILAI DEVISA",
        "PERSENTASE IMPOR",
        "KODE ASAL BARANG",
        "KODE DAERAH ASAL",
        "KODE GUNA BARANG",
        "KODE JENIS NILAI",
        "JATUH TEMPO ROYALTI",
        "KODE KATEGORI BARANG",
        "KODE KONDISI BARANG",
        "KODE NEGARA ASAL",
        "KODE PERHITUNGAN",
        "PERNYATAAN LARTAS",
        "FLAG 4 TAHUN",
        "SERI IZIN",
        "TAHUN PEMBUATAN",
        "KAPASITAS SILINDER",
        "KODE BKC",
        "KODE KOMODITI BKC",
        "KODE SUB KOMODITI BKC",
        "FLAG TIS",
        "ISI PER KEMASAN",
        "JUMLAH DILEKATKAN",
        "JUMLAH PITA CUKAI",
        "HJE CUKAI",
        "TARIF CUKAI",
    ],
    "VERSI": ["VERSI"],
}

# Versi template Core Customs / CEISA 4.0
DEFAULT_VERSI_TEMPLATE = "4.0"


def sheet_column_keys(sheet_code: str) -> list[str]:
    return list(SHEET_COLUMNS.get(sheet_code.upper(), []))


def empty_row(sheet_code: str) -> dict[str, str]:
    return {k: "" for k in sheet_column_keys(sheet_code)}


def build_row(sheet_code: str, values: dict[str, Any]) -> dict[str, str]:
    row = empty_row(sheet_code)
    for k, v in values.items():
        if k in row and v is not None and str(v).strip() != "":
            row[k] = str(v).strip()
    return row


def build_entitas_row(
    nomor_aju: str,
    seri: int,
    kode_entitas: str,
    *,
    nomor_identitas: str = "",
    nama: str = "",
    alamat: str = "",
    kode_negara: str = "",
    kode_jenis_identitas: str = KODE_JENIS_IDENTITAS_NPWP16,
) -> dict[str, str]:
    return build_row(
        "ENTITAS",
        {
            "NOMOR AJU": nomor_aju,
            "SERI": str(seri),
            "KODE ENTITAS": kode_entitas,
            "KODE JENIS IDENTITAS": kode_jenis_identitas,
            "NOMOR IDENTITAS": nomor_identitas,
            "NAMA ENTITAS": nama,
            "ALAMAT ENTITAS": alamat,
            "KODE NEGARA": kode_negara,
        },
    )


def draft_sheet_column_keys() -> dict[str, list[str]]:
    """Kolom yang dipakai draft generate-from-delivery."""
    return {
        code: sheet_column_keys(code)
        for code in ("HEADER", "ENTITAS", "KEMASAN", "BARANG", "VERSI")
    }
