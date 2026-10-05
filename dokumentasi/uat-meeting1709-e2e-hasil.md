# Hasil E2E meeting TongHong 17/9 (DB-first + API)

Waktu: 2026-09-20T00:11:32
API: `http://127.0.0.1:8001/api/v1`
User orkestrator: `admin`

## Inventaris DB (Phase 0)

```json
{
  "ran_at": "2026-09-20T00:11:32",
  "erp": {
    "ok": true,
    "users": [
      {
        "id": 1,
        "username": "Cre@tiv3",
        "role": "admin",
        "is_active": 1
      },
      {
        "id": 3,
        "username": "demo_marketing",
        "role": "marketing",
        "is_active": 1
      },
      {
        "id": 5,
        "username": "demo_production",
        "role": "production",
        "is_active": 1
      },
      {
        "id": 7,
        "username": "demo_warehouse",
        "role": "warehouse",
        "is_active": 1
      },
      {
        "id": 8,
        "username": "demo_finance",
        "role": "finance",
        "is_active": 1
      },
      {
        "id": 9,
        "username": "admin",
        "role": "admin",
        "is_active": 1
      }
    ],
    "packing_done": 9,
    "deliveries": [
      {
        "id": 6,
        "delivery_number": "THI-M260914002",
        "status": "draft",
        "packing_id": 8,
        "invoice_number": null
      },
      {
        "id": 5,
        "delivery_number": "THI-M260914001",
        "status": "sent",
        "packing_id": 7,
        "invoice_number": "THIN-M260914001"
      },
      {
        "id": 4,
        "delivery_number": "THI-M260913002",
        "status": "draft",
        "packing_id": 5,
        "invoice_number": null
      },
      {
        "id": 3,
        "delivery_number": "THI-M260913001",
        "status": "sent",
        "packing_id": 4,
        "invoice_number": "THIN-M260913001"
      },
      {
        "id": 2,
        "delivery_number": "DEL-202609-00002",
        "status": "draft",
        "packing_id": 2,
        "invoice_number": null
      },
      {
        "id": 1,
        "delivery_number": "DEL-202609-00001",
        "status": "sent",
        "packing_id": 1,
        "invoice_number": "INV-202609-00001"
      }
    ],
    "po_outstanding": 12,
    "thin_invoices": 2
  },
  "mrp": {
    "ok": true,
    "treatment_by_jenis": {
      "PU": 6,
      "Suede": 4
    },
    "kimia_in_utama": 0,
    "rp_in_utama": 2,
    "kimia_in_lapangan": 2,
    "rp_in_lapangan": 0,
    "stock_sisa": {
      "consumed": 2,
      "open": 2
    },
    "fg_in_stock": 2
  }
}
```

## Ringkasan langkah

| Langkah | Hasil | Soft | Catatan |
|---------|-------|------|---------|
| Phase0 inventaris DB | LULUS |  |  |
| login admin | LULUS |  |  |
| login demo_marketing | LULUS |  |  |
| login demo_production | LULUS |  |  |
| login demo_warehouse | LULUS |  |  |
| login demo_finance | LULUS |  |  |
| muat master SL043/FG01854/swatch | LULUS |  |  |
| M0 SO draft+confirm | LULUS |  | po_number=THIPM26092003 |
| M1 master PO setelah Confirm | LULUS |  |  |
| M2 rencana produksi | LULUS |  | kode_wip=WIP-260920000003 |
| M3 palet IN | LULUS |  |  |
| M4 proses PU | LULUS |  | kode_wip=WIP-20260920-00003; treatment=PU - Base Coat |
| M5 lab lot | LULUS |  |  |
| M6 checkpoint OK | LULUS |  | kode_wip=WIP-20260920-00003 |
| M7 packing finish + FG in_stock | LULUS |  | kode_packing=FG-260920000005 |
| M8 Outstanding SJ + FG OUT | LULUS |  | delivery_number=THI-M260920003; delivery_status=draft |
| M8b auto invoice THIN dari SJ | LULUS |  | invoice_number=THIN-M260920003; no_duplicate_thin=True; invoice_count=1 |
| M9 scan-out packing → sent | LULUS |  | invoice_number=THIN-M260920003; delivery_status=sent |
| soft dual gudang kimia/RP | LULUS | ya |  |
| soft treatment PU/Suede | LULUS | ya | pu=6; suede=4 |
| soft stock-sisa API | LULUS | ya | count=4 |
| soft packing dari stock-sisa approved | LULUS | ya | kode_packing=FG-260920000006; count=1; sisa_id=6; sisa_status=consumed; finish_ok=True |
| soft Lab stok lapangan saja | LULUS | ya |  |
| soft label roll GET payload | LULUS | ya | kode_packing=FG-260920000005; count=1; roll_id=15 |
| soft scan-out negatif | LULUS | ya | count=1 |
| soft role demo_* distinct | LULUS | ya | count=4 |
| soft proses Suede | LULUS | ya | suede=1; count=1; treatment=Suede - Buffing |
| soft SO+PPIC dari stock-sisa | LULUS | ya | po_number=THIPM26092004; count=1; sisa_id=7; sisa_status=approved; ppic_status=completed |
| soft smoke API setara UI | LULUS | ya | count=5 |

## Flow payload

```json
{
  "m0": {
    "po_id": 40,
    "po_number": "THIPM26092003",
    "status": "confirmed",
    "detail_id": 43,
    "unit_price": "1.3800",
    "swatch_id": 1082,
    "color_standard": "TMSL0432020012901",
    "lot": "PUMSL043260920006",
    "mrp_sync_ok": true,
    "mrp_sync_attempts": 1
  },
  "m1": {
    "sync": {
      "via": "confirm"
    },
    "mrp_po_id": 39,
    "no_po": "UAT-MRP-SL043-2609200011",
    "source_detail_id": 43,
    "status": "outstanding",
    "qty_order": 100.0,
    "qty_processed": 0.0,
    "item_name": "VIRGIN HYDRO PU",
    "tebal": "1.0 - 1.2",
    "warna": "PINKSICLE (6FS) FLUORESCENT"
  },
  "m2": {
    "rencana_id": 48,
    "status": "active",
    "item_id": 47,
    "kode_wip": "WIP-260920000003",
    "kode_rencana_item": "RPI-260920000003",
    "qty_processed": 10.0
  },
  "m3": {
    "kode_palet": "KY-UAT-2609200011",
    "kode_yl": "YL-UAT-2609200011",
    "qty": 50.0,
    "palet_ok": true
  },
  "m4": {
    "proses_id": 46,
    "kode_proses": "PR-260920000003",
    "kode_wip": "WIP-20260920-00003",
    "status": "completed",
    "total_size": 10.0,
    "treatment": "PU - Base Coat",
    "scan_before_start": {
      "http": 400,
      "body": {
        "detail": "Mulai proses (Start) dulu sebelum KY/ukur."
      }
    }
  },
  "m5": {
    "kode_lot_warna": "LW-260920000003",
    "kode_kimia": "GAPCHEM1786268682",
    "nama_kimia": "Gap Chem"
  },
  "m6": {
    "checkpoint_id": 21,
    "kode_wip": "WIP-20260920-00003",
    "result": "OK"
  },
  "m7": {
    "packing_id": 19,
    "kode_packing": "FG-260920000005",
    "status": "finished",
    "fg_id": 15,
    "fg_status": "in_stock",
    "erp_production": {
      "production_id": 14,
      "production_detail_id": 14,
      "production_number": "MRP-PRD-202609-00014",
      "finished": true,
      "line_count": 1,
      "packing_id": 13,
      "packing_number": "MRP-FG-260920000005",
      "qc_header_id": 14
    },
    "erp_packing_id": 13
  },
  "m8": {
    "fg_out_blocked": 400,
    "option_packing_id": 13,
    "production_detail_id": 14,
    "delivery_id": 10,
    "delivery_number": "THI-M260920003",
    "delivery_status": "draft",
    "fg_status": "out",
    "fg_id": 15
  },
  "m8b": {
    "invoice_id": 8,
    "invoice_number": "THIN-M260920003",
    "delivery_id": 10,
    "auto_from_sj": true,
    "invoice_count": 1,
    "no_duplicate_thin": true,
    "manual_post_blocked": 400
  },
  "m9": {
    "delivery_status": "sent",
    "packing_id": 13,
    "scan": {
      "ok": true,
      "packing_id": 13,
      "marked_sent": [
        10
      ],
      "already_sent": [],
      "skipped": [],
      "message": "Packing #13: 1 SJ ditandai sent"
    },
    "scan_idempotent": {
      "ok": true,
      "packing_id": 13,
      "marked_sent": [],
      "already_sent": [
        10
      ],
      "skipped": [],
      "message": "Packing #13: 0 SJ ditandai sent, 1 sudah sent"
    },
    "invoice_id": 8,
    "invoice_number": "THIN-M260920003"
  }
}
```

