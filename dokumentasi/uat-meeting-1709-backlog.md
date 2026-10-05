# UAT / status — backlog meeting TongHong 17/9/26

Tanggal implementasi kode: 2026-09-19 (UAT).

## Ringkasan fase

| Fase | Item | Status |
|------|------|--------|
| 1 | Invoice THIN otomatis saat buat SJ | DONE |
| 2 | Scan packing list → delivery `sent` | DONE |
| 3 | Dual gudang Kimia/RP (utama + lapangan) | DONE |
| 4 | Stock sisa (menu, packing, SO+PPIC, kimia barcode, kulit→KY, label roll note) | DONE |

## Smoke singkat

1. Buat SJ dari outstanding/packing → cek `invoices.invoice_number` berawalan `THIN-`.
2. Di Delivery, scan packing number/ID → status SJ jadi `sent`.
3. Stok Kimia/RP: tab Utama vs Lapangan; Lab hanya baca lapangan.
4. Menu MRP Gudang Sisa + tab info di Packing FG; packing mode barang sisa (approved).

## Catatan

- Sample sticker fisik TongHong belum ada di repo — lihat `uat-label-roll-meeting-1709.md`.
- Ajukan SO dari sisa membutuhkan role yang boleh create PO + alur PPIC.
