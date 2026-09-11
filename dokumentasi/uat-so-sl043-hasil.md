# Hasil UAT SO sampai selesai

Waktu: 2026-09-10T23:37:05
Paket: SL043 · Nike · FG01854 · PINKSICLE 6FS · harga target 1.38

## Ringkasan langkah

| Langkah | Hasil | Catatan |
|---------|-------|---------|
| login demo_marketing | LULUS |  |
| login demo_production | LULUS |  |
| login demo_qc | LULUS |  |
| login demo_warehouse | LULUS |  |
| login demo_finance | LULUS |  |
| login demo_ppic | LULUS |  |
| login semua role | LULUS |  |
| muat master SL043/FG01854/swatch | LULUS |  |
| A1 buat SO draft | LULUS | po_number=THIPM26091001; status=draft; unit_price=1.3800; swatch_id=1082; lot=PUMSL043260910002; color_standard=TMSL0432020012901 |
| A2 confirm SO | LULUS | po_number=THIPM26091001; status=confirmed |
| A8 MKT rekap+PPIC | LULUS |  |
| A3 ERP production ditolak (403) | LULUS |  |
| B1 CSI | LULUS | po_number=THIPM26091002; color_standard=CSI |
| B2 Waiting C/S | LULUS | po_number=THIPM26091003; color_standard=WAITING C/S |
| B3 ERP production 403 | LULUS | po_number=THIPM26091004 |

## Dokumen happy path

```json
{
  "a1": {
    "po_id": 5,
    "po_number": "THIPM26091001",
    "status": "draft",
    "mkt": "input_system",
    "detail_id": 6,
    "unit_price": "1.3800",
    "swatch_id": 1082,
    "color_standard": "TMSL0432020012901",
    "lot": "PUMSL043260910002"
  },
  "a2": {
    "status": "confirmed",
    "po_number": "THIPM26091001",
    "mkt": "in_outstanding"
  },
  "a8_early": {
    "stage_trace": [
      "in_outstanding",
      "material_followup"
    ],
    "post_ppic_stage": "material_followup",
    "ppic_status": "completed"
  },
  "a3": {
    "http": 403,
    "erp_shopfloor_blocked": true
  }
}
```

## Cabang B

```json
{
  "B1": {
    "po_id": 6,
    "po_number": "THIPM26091002",
    "color_standard": "CSI",
    "swatch_id": null,
    "color_reference": "PINKSICLE (6FS)"
  },
  "B2": {
    "po_id": 7,
    "po_number": "THIPM26091003",
    "color_standard": "WAITING C/S",
    "color_reference": "WAITING C/S"
  },
  "B3": {
    "po_id": 8,
    "po_number": "THIPM26091004",
    "erp_shopfloor_blocked": {
      "http": 403,
      "body": {
        "detail": "Operasi shopfloor hanya di MRP. Halaman Production/QC/Packing adalah buku baca-saja."
      }
    }
  }
}
```

