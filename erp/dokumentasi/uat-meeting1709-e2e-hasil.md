# Hasil E2E meeting TongHong 17/9 (DB-first + API)

Waktu: 2026-09-19T23:56:21
API: `http://127.0.0.1:8001/api/v1`
User orkestrator: `admin`

## Inventaris DB (Phase 0)

```json
{
  "ran_at": "2026-09-19T23:56:21",
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
        "username": "admini",
        "role": "admin",
        "is_active": 1
      },
      {
        "id": 10,
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
        "status": "sent",
        "packing_id": 8,
        "invoice_number": "THIN-M260914002"
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
    "po_outstanding": 10,
    "thin_invoices": 3
  },
  "mrp": {
    "ok": false,
    "error": "(1045, \"Access denied for user 'tonghong_mrp'@'127.0.0.1' (using password: NO)\")"
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
| M0 SO draft+confirm | LULUS |  | po_number=THIPM26091901 |
| M1 master PO setelah Confirm | GAGAL |  | {"color_swatch": "SHOETOWN", "created_at": "2026-09-19T21:39:26", "customer": "PT. SHOETOWN LIGUNG INDONESIA", "customer |

## Flow payload

```json
{}
```

## Berhenti

```json
{
  "M1 status": {
    "color_swatch": "SHOETOWN",
    "created_at": "2026-09-19T21:39:26",
    "customer": "PT. SHOETOWN LIGUNG INDONESIA",
    "customer_id": 28,
    "emboss": "AR-121",
    "id": 34,
    "item_name": "LACCATO PATENT LEATHER",
    "lot_number": "PUMSL043260919001",
    "no_po": "UAT-MRP-SL043-2609192356",
    "no_so": "THIPM26091901",
    "qty_balance_erp": 100.0,
    "qty_order": 100.0,
    "qty_processed": 9909090.0,
    "qty_wip": 40.0,
    "source_detail_id": 38,
    "sq_ft": 100.0,
    "status": "completed",
    "stock_wh_qty": 0.0,
    "tebal": "1.0 - 1.2",
    "warna": "PINKSICLE (6FS) FLUORESCENT"
  }
}
```

