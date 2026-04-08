# Master Data CSV (selaras Tonghong API)

Header memakai **nama field** seperti di tabel/model backend (`snake_case`).

| File | Tabel / pemakaian |
|------|-------------------|
| `00_Master_Customer.csv` | **`customers`** — master eksplisit: `customer_code`, `customer_name`, `phone`, `address` (opsional). Diimpor **dulu** sebelum sinkron marketing. |
| `01_Master_Item.csv` | `master_items` — FG: `item_code`, `thickness_mm`, `material_name`, `emboss`, `color`, `category` |
| `02_Master_Harga.csv` | `master_prices` — matrix harga: `line_no`, kategori/tipe/nama material, `thickness_range`, harga USD per kolom warna, `remark`, `price_tier` |
| `03_Master_Data_Marketing.csv` | `po_headers` + `po_details` + `po_detail_deliveries` — satu baris = satu baris SO + jadwal kirim 1–12. Kolom wajib termasuk `customer_name_snapshot`. Kolom opsional: `customer_code` (kode bisnis per baris; jika diisi, dipakai saat sinkron customer). |

**Sinkron modul Customer:** skrip impor membaca **semua nama unik** `customer_name_snapshot` dari `03_…` dan meng-upsert ke tabel `customers`, sehingga daftar customer di UI **selaras dengan CSV** walaupun baris SO sudah pernah diimpor (PO duplikat tidak membuat ulang customer).

Impor:

`cd Tonghong/backend && PYTHONPATH=. python scripts/import_master_data.py`

Folder CSV default: `Projects/Master_Data_extracted` (di samping folder `Tonghong`).  
Docker: `-v /path/Master_Data_extracted:/csv` dan `-e MASTER_CSV_DIR=/csv`.

## Verifikasi (sinkron dengan backend)

- **48 kolom** pada `03_…`: semua key dipakai skrip impor (`backend/scripts/import_master_data.py`); migrasi DB `d4e5f6a7b8c0` (head Alembic).
- **Export CSV** `GET /api/v1/reports/sales-order-lines-export.csv` memuat kolom yang sama dengan baris marketing + `copied_from_detail_id` + `delivery_1…12` (qty + tanggal ISO).
- **Respons API** baris PO memuat `delivery_schedules[]` setelah create/update detail (muat relasi di `po.py`).
