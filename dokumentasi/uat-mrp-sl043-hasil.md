# Hasil UAT SO confirm + MRP sampai Outstanding SJ + invoice

Waktu: 2026-09-10T23:38:23
Paket: SL043 · Nike · FG01854 · PINKSICLE 6FS · alokasi rencana 10
Jalur: Confirm → Outstanding → MRP packing → Outstanding SJ → invoice / RAR.
Catatan: Pending Payment = laporan tunggakan master (health check saja), bukan bukti invoice baru; bukti invoice baru = RAR.

## Ringkasan langkah

| Langkah | Hasil | Catatan |
|---------|-------|---------|
| login demo_marketing | LULUS |  |
| login demo_production | LULUS |  |
| login demo_warehouse | LULUS |  |
| login demo_finance | LULUS |  |
| muat master SL043/FG01854/swatch | LULUS |  |
| M0 SO draft+confirm | LULUS | po_number=THIPM26091006; status=confirmed; unit_price=1.3800 |
| M1 sync PO MRP | LULUS | status=outstanding; mrp_po_id=10 |
| M2 rencana produksi | LULUS | status=active; rencana_id=6; kode_wip=WIP-260910000001 |
| M3 palet IN | LULUS | kode_palet=KY-UAT-2609102338 |
| M4 proses PU | LULUS | status=completed; kode_wip=WIP-260910000001; kode_proses=PR-260910000001 |
| M5 lab lot | LULUS | kode_lot_warna=LW-260910000001 |
| M6 checkpoint OK | LULUS | kode_wip=WIP-260910000001; result=OK |
| M7 packing finish + FG in_stock | LULUS | status=finished; kode_packing=FG-260910000001; fg_status=in_stock |
| M8 Outstanding SJ + FG OUT | LULUS | fg_status=out; delivery_id=1; delivery_number=DEL-202609-00001 |
| M9 sent + invoice + RAR | LULUS | invoice_number=INV-202609-00001 |
| M10 ERP production 403 | LULUS |  |
| M11 dual SO 1 SJ | LULUS | delivery_id=2; delivery_number=DEL-202609-00002; delivery_count=1 |

## Dokumen

```json
{
  "m0": {
    "po_id": 10,
    "po_number": "THIPM26091006",
    "status": "confirmed",
    "detail_id": 11,
    "unit_price": "1.3800",
    "swatch_id": 1082,
    "color_standard": "TMSL0432020012901",
    "lot": "PUMSL043260910012"
  },
  "m1": {
    "sync": {
      "ok": true
    },
    "mrp_po_id": 10,
    "no_po": "UAT-MRP-SL043-2609102338",
    "source_detail_id": 11,
    "status": "outstanding",
    "qty_order": 100.0,
    "qty_processed": 0.0,
    "item_name": "VIRGIN HYDRO PU",
    "tebal": "1.0 - 1.2",
    "warna": "PINKSICLE (6FS) FLUORESCENT"
  },
  "m2": {
    "rencana_id": 6,
    "status": "active",
    "item_id": 2,
    "kode_wip": "WIP-260910000001",
    "kode_rencana_item": "RPI-260910000001",
    "qty_processed": 10.0
  },
  "m3": {
    "kode_palet": "KY-UAT-2609102338",
    "kode_yl": "YL-UAT-2609102338",
    "qty": 50.0,
    "palet_ok": true
  },
  "m4": {
    "proses_id": 4,
    "kode_proses": "PR-260910000001",
    "kode_wip": "WIP-260910000001",
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
    "kode_lot_warna": "LW-260910000001",
    "kode_kimia": "GAPCHEM1786268682",
    "nama_kimia": "Gap Chem"
  },
  "m6": {
    "checkpoint_id": 1,
    "kode_wip": "WIP-260910000001",
    "result": "OK"
  },
  "m7": {
    "packing_id": 1,
    "kode_packing": "FG-260910000001",
    "status": "finished",
    "fg_id": 1,
    "fg_status": "in_stock",
    "erp_production": {
      "production_id": 1,
      "production_detail_id": 1,
      "production_number": "MRP-PRD-202609-00001",
      "finished": true,
      "line_count": 1,
      "packing_id": 1,
      "packing_number": "MRP-FG-260910000001",
      "qc_header_id": 1
    },
    "erp_packing_id": 1
  },
  "m8": {
    "fg_out_blocked": 400,
    "option_packing_id": 1,
    "production_detail_id": 1,
    "delivery_id": 1,
    "delivery_number": "DEL-202609-00001",
    "delivery_status": "draft",
    "fg_status": "out",
    "fg_id": 1
  },
  "m9": {
    "delivery_status": "sent",
    "invoice_id": 1,
    "invoice_number": "INV-202609-00001",
    "rar_hit": true,
    "pp_http_ok": true
  },
  "m10": {
    "http": 403,
    "erp_shopfloor_blocked": true
  },
  "m11": {
    "so_b": "THIPM26091007",
    "so_c": "THIPM26091008",
    "delivery_id": 2,
    "delivery_number": "DEL-202609-00002",
    "delivery_count": 1
  }
}
```

