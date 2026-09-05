# Hasil UAT SO sampai selesai

Waktu: 2026-09-05T04:37:22
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
| A1 buat SO draft | LULUS | po_number=THIPM26090512; status=draft; swatch_id=1082; lot=PUMSL043260905021; color_standard=TMSL0432020012901 |
| A2 confirm SO | LULUS | po_number=THIPM26090512; status=confirmed |
| A8 MKT rekap+PPIC | LULUS |  |
| A3 production | LULUS | production_number=PRD-202609-00005 |
| A4 QC OK | LULUS | qc_number=QC-202609-00003 |
| A5 packing done | LULUS | status=done; packing_number=PACK-202609-00005 |
| A6 delivery sent | LULUS | status=sent; delivery_number=DEL-202609-00002 |
| A8 MKT SJ/INVPL | LULUS | pre_invoice_stage=sj_invpl |
| A7 invoice | LULUS | po_number=THIPM26090512; invoice_number=INV-202609-00002 |
| A8 marketing flow final | LULUS | pre_invoice_stage=sj_invpl; final_stage=invoice_billing |
| B1 CSI | LULUS | po_number=THIPM26090513; color_standard=CSI |
| B2 Waiting C/S | LULUS | po_number=THIPM26090514; color_standard=WAITING C/S |
| B3 QC NG blokir packing | LULUS | po_number=THIPM26090515 |

## Dokumen happy path

```json
{
  "a1": {
    "po_id": 47,
    "po_number": "THIPM26090512",
    "status": "draft",
    "mkt": "input_system",
    "detail_id": 65,
    "unit_price": null,
    "swatch_id": 1082,
    "color_standard": "TMSL0432020012901",
    "lot": "PUMSL043260905021"
  },
  "a2": {
    "status": "confirmed",
    "po_number": "THIPM26090512"
  },
  "a8_early": {
    "stage_trace": [
      "rekap_printed",
      "with_ppic",
      "in_outstanding",
      "material_followup"
    ],
    "post_ppic_stage": "material_followup"
  },
  "a3": {
    "production_id": 14,
    "production_number": "PRD-202609-00005",
    "production_detail_id": 15,
    "so_status": "production"
  },
  "a4": {
    "qc_id": 11,
    "qc_number": "QC-202609-00003",
    "qc_detail_id": 14,
    "is_ok": true
  },
  "a5": {
    "packing_id": 12,
    "packing_number": "PACK-202609-00005",
    "status": "done"
  },
  "a6": {
    "delivery_id": 9,
    "delivery_number": "DEL-202609-00002",
    "status": "sent",
    "detail_count": 1
  },
  "a8_pre": {
    "stage_trace": [
      "rekap_printed",
      "with_ppic",
      "in_outstanding",
      "material_followup",
      "sj_invpl"
    ],
    "pre_invoice_stage": "sj_invpl"
  },
  "a7": {
    "invoice_id": 5850,
    "invoice_number": "INV-202609-00002",
    "po_number": "THIPM26090512"
  },
  "a8": {
    "final_stage": "invoice_billing",
    "stage_trace": [
      "rekap_printed",
      "with_ppic",
      "in_outstanding",
      "material_followup",
      "sj_invpl",
      "invoice_billing"
    ],
    "pre_invoice_stage": "sj_invpl",
    "skip_after_end": {
      "http": 400,
      "body": {
        "detail": "PO sudah di tahap akhir alur MKT"
      }
    }
  }
}
```

## Cabang B

```json
{
  "B1": {
    "po_id": 48,
    "po_number": "THIPM26090513",
    "color_standard": "CSI",
    "swatch_id": null,
    "color_reference": "PINKSICLE (6FS)"
  },
  "B2": {
    "po_id": 49,
    "po_number": "THIPM26090514",
    "color_standard": "WAITING C/S",
    "color_reference": "WAITING C/S"
  },
  "B3": {
    "po_id": 50,
    "po_number": "THIPM26090515",
    "qc_id": 12,
    "packing_blocked": {
      "http": 400,
      "body": {
        "detail": "Production detail #16 belum QC OK"
      }
    }
  }
}
```

