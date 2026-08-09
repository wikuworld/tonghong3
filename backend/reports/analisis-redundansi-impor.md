# Analisis Redundansi Data Impor

Generated: `2026-08-05T17:09:20.942160+00:00`

## Ringkasan temuan per label

### HARD_DUP (0)
- _(kosong)_

### LEGACY (0)
- _(kosong)_

### SOFT_DUP (1)
- **csi_color_masters**: Nama warna sama dengan >1 color_code (dari sumber Excel, biasanya sah) _(count=26)_
  - `{"buyer": "ADIDAS", "name": "Blast Purple F13", "codes_n": 2, "codes": "A6EP | A6F9"}`
  - `{"buyer": "ADIDAS", "name": "Core RedS17", "codes_n": 2, "codes": "A9N1 | A9N2"}`
  - `{"buyer": "ADIDAS", "name": "WHITE", "codes_n": 2, "codes": "001A | 01F7"}`
  - `{"buyer": "NB", "name": "AQUAMARINE", "codes_n": 2, "codes": "NB0600102 | NB0904545"}`
  - `{"buyer": "NB", "name": "CLAY", "codes_n": 2, "codes": "NB0301054 | NB0303573"}`

### ARTEFACT (1)
- **buyer_price:NIKE**: Baris OUTSIDE BANTEN terimpor: 4 (sesuai aturan: hanya yang punya W) _(count=4)_
  - `{"item": "VIRGIN HYDRO PU", "white": "1.15"}`
  - `{"item": "GENERIC PU COATED", "white": "1.15"}`
  - `{"item": "ECO TECH COMFORT", "white": "1.28"}`
  - `{"item": "H.P ECO TECH COMFORT", "white": "1.28"}`

### CROSS_REF (2)
- **csi ∩ color_swatch**: Kode CSI yang juga dipakai swatch (peran berbeda: katalog vs resep) _(count=743)_
  - `{"buyer": "ADIDAS", "code": "002A", "csi_name": "BRIGHT YELLOW", "factory": "NIKOMAS", "material": "SEMI FULL GRAIN"}`
  - `{"buyer": "ADIDAS", "code": "002A", "csi_name": "BRIGHT YELLOW", "factory": "NIKOMAS", "material": "SOFT PU COATED LEATHER"}`
  - `{"buyer": "ADIDAS", "code": "003A", "csi_name": "YELLOW", "factory": "NIKOMAS", "material": "SEMI FULL GRAIN"}`
  - `{"buyer": "ADIDAS", "code": "014A", "csi_name": "COLLEGIATE RED", "factory": "NIKOMAS", "material": "SOFT PU COATED LEATHER"}`
  - `{"buyer": "ADIDAS", "code": "020A", "csi_name": "GREEN", "factory": "PANARUB", "material": "PU COATED LEATHER"}`
- **csi ∩ fluorescent**: Kode CSI yang juga ada di fluorescent master _(count=196)_
  - `{"buyer": "ADIDAS", "rows": 100}`
  - `{"buyer": "NB", "rows": 7}`
  - `{"buyer": "UA", "rows": 89}`

### CONTEXT_OK (12)
- **csi_color_masters**: Tidak ada HARD_DUP pada (buyer_code, color_code) — unique key sehat _(count=0)_
- **csi_color_masters**: Near-duplicate code setelah normalize spasi: tidak ada _(count=0)_
- **buyer_price:ADIDAS**: Tidak ada duplikat (ITEM, COLOR/block, THICKNESS) — 17 baris _(count=0)_
- **buyer_price:NB**: Tidak ada duplikat (ITEM, COLOR/block, THICKNESS) — 9 baris _(count=0)_
- **buyer_price:NB01**: Tidak ada duplikat (ITEM, COLOR/block, THICKNESS) — 3 baris _(count=0)_
- **buyer_price:NIKE**: Tidak ada duplikat (ITEM, COLOR/block, THICKNESS) — 39 baris _(count=0)_
- **buyer_price:UA**: Tidak ada duplikat (ITEM, COLOR/block, THICKNESS) — 7 baris _(count=0)_
- **buyer_price:NIKE**: ITEM di >1 blok (COMMON/SPECIAL/OUTSIDE): 7 — harga beda = sah _(count=7)_
  - `{"item": "(OIA) VIRGIN PU 1.0-1.2", "blocks": {"COMMON": "1.19", "SPECIAL": "1.32"}}`
  - `{"item": "(OIA) VIRGIN PU 1.2-1.4", "blocks": {"COMMON": "1.5", "SPECIAL": "1.63"}}`
  - `{"item": "(OIA) VIRGIN PU 1.4-1.6", "blocks": {"COMMON": "1.23", "SPECIAL": "1.36"}}`
  - `{"item": "ECO TECH COMFORT", "blocks": {"COMMON": "1.26", "SPECIAL": "1.36", "OUTSIDE BANTEN": "1.28"}}`
  - `{"item": "GENERIC PU COATED", "blocks": {"COMMON": "1.13", "SPECIAL": "1.23", "OUTSIDE BANTEN": "1.15"}}`
- **buyer_price:NIKE**: Tidak ada ITEM multi-blok dengan harga WHITE identik antar blok _(count=0)_
- **buyer_price:ADIDAS**: Addon negatif: tidak ada _(count=0)_
- **color_swatch_recipes**: Duplikat kunci resep: tidak ada _(count=0)_
- **swatch FOLLOW CSI* orphan**: Swatch ber-standard CSI yang color_code tidak ada di csi_color_masters: 0 _(count=0)_

## Counts

```json
{
  "csi": {
    "total": 4057,
    "active": 4057,
    "by_buyer": [
      {
        "buyer_code": "ADIDAS",
        "rows": 1149,
        "distinct_codes": 1149,
        "distinct_names": 1146
      },
      {
        "buyer_code": "NB",
        "rows": 798,
        "distinct_codes": 798,
        "distinct_names": 789
      },
      {
        "buyer_code": "NIKE",
        "rows": 1425,
        "distinct_codes": 1425,
        "distinct_names": 1412
      },
      {
        "buyer_code": "UA",
        "rows": 685,
        "distinct_codes": 685,
        "distinct_names": 684
      }
    ]
  },
  "csi_soft_dup_by_buyer": [
    {
      "buyer_code": "ADIDAS",
      "name_groups": 3,
      "rows": 6
    },
    {
      "buyer_code": "NB",
      "name_groups": 9,
      "rows": 18
    },
    {
      "buyer_code": "NIKE",
      "name_groups": 13,
      "rows": 26
    },
    {
      "buyer_code": "UA",
      "name_groups": 1,
      "rows": 2
    }
  ],
  "buyer_price_lists": [
    {
      "id": 23,
      "buyer_code": "ADIDAS",
      "title": "QUOTATION ADIDAS FW26 (FEB-JUL 2026)",
      "period_label": "PERIODE 2026/02/01 - 2026/07/31",
      "period_start": "2026-02-01",
      "period_end": "2026-07-31",
      "rows": 17,
      "meta_preview": "{\"source_file\": \"1._QUOTATION_ADIDAS_FW26_FEB-JUL_2026_ (1).xlsx\", \"kind\": \"adidas_quotation\", \"canonical_sheet\": \"ADCI\", \"data_row_count\": 17, \"column_keys\": ["
    },
    {
      "id": 13,
      "buyer_code": "NB",
      "title": "LIST HARGA NB MATERIAL",
      "period_label": "PERIODE 2026/03/01 - 2026/09/30,,,,",
      "period_start": "2026-03-01",
      "period_end": "2026-09-30",
      "rows": 9,
      "meta_preview": "{\"filename\": \"01_NB.csv\", \"source_label\": \"LIST_HARGA_ALL_BUYER_extracted\", \"header_row_index\": 3, \"csv_line_count\": 17, \"data_row_count\": 9}"
    },
    {
      "id": 17,
      "buyer_code": "NB01",
      "title": "NB Periode 04 Mei 2026 - 04 mei 2027",
      "period_label": "NB Periode 04 Mei 2026 - 04 mei 2027",
      "period_start": "2026-05-04",
      "period_end": "2027-03-04",
      "rows": 3,
      "meta_preview": "{\"column_keys\": [\"ITEM\", \"THICKNESS\", \"COLOR\", \"COLOR WHITE\", \"COLOR BLACK\", \"FLOURASENT\", \"METALIC\", \"EMBOSS\", \"SPESIAL EMBOSS\"]}"
    },
    {
      "id": 22,
      "buyer_code": "NIKE",
      "title": "UPDATE PRICE NIKE (JUL-DES 2026)",
      "period_label": "JUL-DES 2026",
      "period_start": "2026-07-01",
      "period_end": "2026-12-31",
      "rows": 39,
      "meta_preview": "{\"source_file\": \"HARGA_TEMPEL_NIKE_JUL_-_DES_2026_UPDATE (1).xlsx\", \"kind\": \"nike_tempel\", \"notes\": [\"SPECIAL DIRECT: AR-140, AR-169, AR-172, AR-176, AR-185, AR"
    },
    {
      "id": 16,
      "buyer_code": "UA",
      "title": "LIST HARGA MATERIAL UA",
      "period_label": "PERIODE 2026/02/01 - 2026/07/31,,,,,",
      "period_start": "2026-02-01",
      "period_end": "2026-07-31",
      "rows": 7,
      "meta_preview": "{\"filename\": \"04_UA.csv\", \"source_label\": \"LIST_HARGA_ALL_BUYER_extracted\", \"header_row_index\": 3, \"csv_line_count\": 39, \"data_row_count\": 7}"
    }
  ],
  "color_swatch_active": 3047,
  "csi_swatch_overlap": [
    {
      "buyer_code": "ADIDAS",
      "overlap_codes": 202
    },
    {
      "buyer_code": "NB",
      "overlap_codes": 19
    },
    {
      "buyer_code": "NIKE",
      "overlap_codes": 414
    },
    {
      "buyer_code": "UA",
      "overlap_codes": 108
    }
  ],
  "csi_fluo_overlap": [
    {
      "buyer_code": "ADIDAS",
      "rows": 100
    },
    {
      "buyer_code": "NB",
      "rows": 7
    },
    {
      "buyer_code": "UA",
      "rows": 89
    }
  ],
  "swatch_follow_csi": {
    "total": 91,
    "orphan_code_not_in_csi": 0
  }
}
```

## Rekomendasi

- **P0**: Tidak ada HARD_DUP pada CSI / Nike / Adidas hasil impor musim — tidak perlu cleanup duplikat unik.
- **P1**: ARTEFACT: baris OUTSIDE BANTEN / orphan swatch FOLLOW CSI — dokumentasikan atau perketat parser; bukan error data ganda.
- **P2**: SOFT_DUP CSI (nama sama, kode beda) biarkan — sesuai sumber Excel; jangan merge otomatis.
- **P2**: CROSS_REF CSI∩swatch/fluorescent adalah overlap peran (katalog vs resep vs fluo) — jangan hapus salah satu sisi.
