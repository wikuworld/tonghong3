# Catatan UAT — backfill & data bersih (2026-09-20)

## Invoice THIN untuk SJ lama

Sebelum meeting 17/9, beberapa delivery draft tidak punya invoice. Sudah di-backfill:

| Delivery | Nomor SJ | Invoice |
|----------|----------|---------|
| 2 | DEL-202609-00002 | THIN-M260910001 |
| 4 | THI-M260913002 | THIN-M260913002 |
| 6 | THI-M260914002 | THIN-M260914002 |

Skrip ulang (idempotent):

```bash
cd erp/backend
PYTHONPATH=. .venv/bin/python scripts/backfill_delivery_auto_invoices.py
```

## Data MRP kotor

`tbl_master_po` id 34 (`UAT-MRP-SL043-2609192356`) punya `qty_processed` ~9.9 juta dari alokasi rencana rusak.
Sudah di-clamp:

- `tbl_rencana_item_po` id 65/66 → `qty_proses=0`
- master PO 34 → `qty_processed=0`, `status=outstanding`

## Dokumentasi

`dokumentasi/mrp-peta-fungsi.md` diperbarui: invoice THIN otomatis (bukan manual).
