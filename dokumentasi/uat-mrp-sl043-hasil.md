# Hasil UAT SO confirm + MRP sampai FG OUT

Waktu: 2026-08-17T06:16:39
Paket: SL043 · Nike · FG01854 · PINKSICLE 6FS · alokasi rencana 10
Jalur: SO draft→confirm (tanpa Production/QC/Packing ERP) lalu MRP penuh termasuk FG OUT.

## Ringkasan langkah

| Langkah | Hasil | Catatan |
|---------|-------|---------|
| login demo_marketing | LULUS |  |
| login demo_production | LULUS |  |
| muat master SL043/FG01854/swatch | LULUS |  |
| M0 SO draft+confirm | LULUS | po_number=THIPM26081705; status=confirmed; unit_price=1.3800 |
| M1 sync PO MRP | LULUS | status=outstanding; mrp_po_id=24 |
| M2 rencana produksi | LULUS | status=active; rencana_id=29; kode_wip=WIP-260817000001 |
| M3 palet IN | LULUS | kode_palet=KY-UAT-2608170616 |
| M4 proses PU | LULUS | status=completed; kode_wip=WIP-260817000001; kode_proses=PR-260817000001 |
| M5 lab lot | LULUS | kode_lot_warna=LW-260817000001 |
| M6 checkpoint OK | LULUS | kode_wip=WIP-260817000001; result=OK |
| M7 packing finish + FG in_stock | LULUS | status=finished; kode_packing=FG-260817000001; fg_status=in_stock |
| M8 FG OUT + Delivery ERP | LULUS | kode_packing=FG-260817000001; fg_status=out; erp_delivery_id=5; erp_delivery_number=DEL-202608-00003; delivery_status=draft |

## Dokumen

```json
{
  "m0": {
    "po_id": 23,
    "po_number": "THIPM26081705",
    "status": "confirmed",
    "detail_id": 39,
    "unit_price": "1.3800",
    "swatch_id": 1082,
    "color_standard": "TMSL0432020012901",
    "lot": "PUMSL043260817010"
  },
  "m1": {
    "sync": {
      "ok": true
    },
    "mrp_po_id": 24,
    "no_po": "THIPM26081705",
    "source_detail_id": 39,
    "status": "outstanding",
    "qty_order": 100.0,
    "qty_processed": 0.0,
    "item_name": "VIRGIN HYDRO PU",
    "tebal": "1.0 - 1.2",
    "warna": "PINKSICLE (6FS) FLUORESCENT"
  },
  "m2": {
    "rencana_id": 29,
    "status": "active",
    "item_id": 35,
    "kode_wip": "WIP-260817000001",
    "kode_rencana_item": "RPI-260817000001",
    "qty_processed": 10.0
  },
  "m3": {
    "kode_palet": "KY-UAT-2608170616",
    "kode_yl": "YL-UAT-2608170616",
    "qty": 50.0,
    "palet_ok": true
  },
  "m4": {
    "proses_id": 9,
    "kode_proses": "PR-260817000001",
    "kode_wip": "WIP-260817000001",
    "status": "completed",
    "total_size": 10.0,
    "treatment": "Emboss",
    "scan_before_start": {
      "http": 400,
      "body": {
        "detail": "Mulai proses (Start) dulu sebelum KY/ukur."
      }
    }
  },
  "m5": {
    "kode_lot_warna": "LW-260817000001",
    "kode_kimia": "GAPCHEM1786268682",
    "nama_kimia": "Gap Chem"
  },
  "m6": {
    "checkpoint_id": 5,
    "kode_wip": "WIP-260817000001",
    "result": "OK"
  },
  "m7": {
    "packing_id": 7,
    "kode_packing": "FG-260817000001",
    "status": "finished",
    "fg_id": 5,
    "fg_status": "in_stock",
    "erp_production": {
      "production_id": 6,
      "production_detail_id": 9,
      "production_number": "MRP-PRD-202608-00004",
      "finished": true
    }
  },
  "m8": {
    "fg_id": 5,
    "fg_status": "out",
    "kode_packing": "FG-260817000001",
    "erp_delivery_id": 5,
    "erp_delivery_number": "DEL-202608-00003",
    "erp_packing_id": 6,
    "delivery_status": "draft",
    "delivery_po_number": null,
    "bridge_status": "ok"
  }
}
```

