# Hasil UAT SO sampai selesai

Waktu: 2026-08-17T05:58:58
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
| A1 buat SO draft | LULUS | po_number=THIPM26081701; status=draft; color_standard=TMSL0432020012901; unit_price=1.38; lot=PUMSL043260817002 |
| A2 confirm SO | LULUS | po_number=THIPM26081701; status=confirmed |
| A3 production | LULUS | production_number=PRD-202608-00002 |
| A4 QC OK | LULUS |  |
| A5 packing done | LULUS | status=done; packing_number=PACK-202608-00003 |
| A6 delivery sent | LULUS | status=sent |
| A7 invoice | LULUS | po_number=THIPM26081701 |
| A8 marketing flow | LULUS | final_stage=invoice_billing |
| B1 CSI | LULUS | po_number=THIPM26081702; color_standard=CSI |
| B2 Waiting C/S | LULUS | po_number=THIPM26081703; color_standard=WAITING C/S |
| B3 QC NG blokir packing | LULUS | po_number=THIPM26081704 |

## Dokumen happy path

```json
{
  "a1": {
    "po_id": 19,
    "po_number": "THIPM26081701",
    "status": "draft",
    "mkt": "input_system",
    "detail_id": 35,
    "unit_price": "1.3800",
    "swatch_id": 1082,
    "color_standard": "TMSL0432020012901",
    "lot": "PUMSL043260817002"
  },
  "a2": {
    "status": "confirmed",
    "po_number": "THIPM26081701"
  },
  "a3": {
    "production_id": 4,
    "production_number": "PRD-202608-00002",
    "production_detail_id": 7,
    "so_status": "production"
  },
  "a4": {
    "qc_id": 3,
    "qc_number": null,
    "qc_detail_id": 6,
    "is_ok": true
  },
  "a5": {
    "packing_id": 4,
    "packing_number": "PACK-202608-00003",
    "status": "done"
  },
  "a6": {
    "delivery_id": 4,
    "delivery_number": null,
    "status": "sent",
    "detail_count": 1
  },
  "a7": {
    "invoice_id": 1,
    "invoice_number": null,
    "po_number": "THIPM26081701"
  },
  "a8": {
    "final_stage": "invoice_billing",
    "stage_trace": [
      "invoice_billing",
      "invoice_billing",
      "invoice_billing",
      "invoice_billing",
      "invoice_billing"
    ],
    "skip_after_end": {
      "http": 400,
      "body": {
        "detail": "PO sudah di tahap akhir alur MKT"
      }
    }
  }
}
```

Catatan A1: `POST /po/{id}/details` belum memanggil resolve harga (hanya `PUT` yang resolve). Setelah `PUT` spek yang sama, `unit_price` tersimpan **1.3800**. Lot THI = `PUMSL043260817002`. Runner UAT sekarang ikut `PUT` setelah create baris.

UAT dijalankan lewat API (`backend/scripts/run_uat_so_e2e.py` → `http://127.0.0.1:8000/api/v1`) dengan akun demo per role, bukan klik wizard UI. Alur dan payload sama dengan paket SL043 / FG01854.

## Cabang B

```json
{
  "B1": {
    "po_id": 20,
    "po_number": "THIPM26081702",
    "color_standard": "CSI",
    "swatch_id": null,
    "color_reference": "PINKSICLE (6FS)"
  },
  "B2": {
    "po_id": 21,
    "po_number": "THIPM26081703",
    "color_standard": "WAITING C/S",
    "color_reference": "WAITING C/S"
  },
  "B3": {
    "po_id": 22,
    "po_number": "THIPM26081704",
    "qc_id": 4,
    "packing_blocked": {
      "http": 400,
      "body": {
        "detail": "Production detail #8 belum QC OK"
      }
    }
  }
}
```

