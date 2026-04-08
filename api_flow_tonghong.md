# API FLOW - TONG HONG SYSTEM

## Base URL
/api/v1/

---

# 1. AUTH (OPTIONAL)
POST /auth/login
POST /auth/logout

---

# 2. CUSTOMER

GET /customers
POST /customers
GET /customers/{id}
PUT /customers/{id}
DELETE /customers/{id}

---

# 3. PO (PURCHASE ORDER)

## Header
GET /po
POST /po
GET /po/{id}
GET /po/{po_id}/details — daftar baris PO (`PoDetailOut[]`)
PUT /po/{id}
DELETE /po/{id}

## Detail
POST /po/{id}/details
PUT /po-detail/{id}
DELETE /po-detail/{id}

---

# 4. PRODUCTION

POST /production
GET /production
GET /production/{id}
GET /production/{production_id}/details — baris production (lot)

POST /production/{id}/details
PUT /production-detail/{id}

---

# 5. QC (MEASUREMENT)

## Header
POST /qc
GET /qc
GET /qc/{id}
GET /qc/{qc_id}/details — baris pengukuran QC

## Detail
POST /qc/{id}/details
PUT /qc-detail/{id}

## RULE:
- thickness_actual must be between min & max
- if OK → is_ok = true
- only is_ok = true can go to delivery

---

# 6. DELIVERY

## Header
POST /delivery — body wajib `packing_id`; packing harus status **done**
GET /delivery
PUT /delivery/{id} — ubah status (mis. **sent**); jika ganti `packing_id`, packing baru juga harus **done**
GET /delivery/{id}
GET /delivery/{delivery_id}/details

## Detail
POST /delivery/{id}/details — hanya baris production detail yang sudah **QC OK**
PUT /delivery-detail/{id}

## RULE:
- Hanya data QC OK pada detail delivery
- Status **sent** hanya jika sudah ada minimal satu baris detail

---

# 6b. PACKING

POST /packing — wajib `production_id` + `qc_header_id` (QC harus untuk production yang sama)
PUT /packing/{id} — mis. set status **done** (wajib sebelum buat delivery)
GET /packing
GET /packing/{id}

---

# 7. INVOICE

POST /invoice — wajib `delivery_id`; delivery harus **sent**, punya **packing_id**, minimal satu detail; `po_number` opsional harus cocok dengan SO di rantai delivery jika diisi
GET /invoice
GET /invoice/{id}
GET /invoice/{invoice_id}/details

POST /invoice/{id}/details

---

# 8. FLOW SUMMARY

PO → Production → QC → **Packing (done)** → **Delivery (+ detail)** → **Delivery sent** → Invoice (FK `delivery_id`)

---

# 8b. ALUR MKT (FLOWCHART KANTOR — 100% DI SISTEM)

Tahapan berurutan di `po_headers.mkt_workflow_stage` (naik satu per satu lewat API):

`input_system` → `rekap_printed` → `with_ppic` → `back_to_mkt` → `in_outstanding` → `material_followup` → `delivery_arranged` → `sj_invpl` → `invoice_billing`

- **GET /po/mkt-workflow-stages** — daftar urutan tahap
- **GET /po?mkt_workflow_stage=...** — filter board
- **POST /po/{id}/mkt-workflow/advance** — maju ke tahap berikut (dengan validasi)
- **GET /reports/po-daily-recap.csv?date=YYYY-MM-DD** — rekap PO hari ini (order_date atau tanggal input)
- **GET /documents/surat-jalan/{delivery_id}** — HTML cetak Surat Jalan
- **GET /documents/invpl/{packing_id}** — HTML cetak INVPL
- **POST /delivery/{id}/mark-surat-jalan-printed** — tandai SJ sudah dicetak
- **POST /packing/{id}/mark-invpl-printed** — tandai INVPL sudah dicetak
- **PUT /po/{id}** — `material_followup_remark`, `material_followup_done` (wajib sebelum ke *delivery_arranged*)
- Setelah **POST /invoice**, PO pada delivery tersebut otomatis ke `invoice_billing` jika belum

---

# 9. IMPORTANT BUSINESS RULES

1. Transisi status PO dibatasi (draft → confirmed → production → completed; lihat backend `validate_po_status_transition`)
2. Production harus ada sebelum QC bermakna; QC OK sebelum baris delivery
3. Packing menghubungkan production + QC; delivery membutuhkan packing **done**
4. Invoice membutuhkan delivery **sent** + minimal satu detail; kolom `invoices.delivery_id` (FK)
5. Data invoice tetap snapshot teks (nama pelanggan, dll.); tautan ke delivery untuk audit alur
6. Alur MKT (§8b) melengkapi flowchart kantor: PPIC/MKT/outstanding/material/SJ/INVPL sebelum invoice penagihan

---

# 10. CR — DASHBOARD & MASTER (Sales / Produksi)

## Dashboard (ringkasan KPI)
GET /dashboard/summary
- Mengembalikan `counts` (SO, SO open, production, delivery, QC reject lines) dan `exchange_rate` terbaru (jika ada).

## Sales Order (alias domain untuk PO; nomor SO = `po_number` di DB)
GET /sales-orders
POST /sales-orders
GET /sales-orders/{so_id}
PUT /sales-orders/{so_id}
DELETE /sales-orders/{so_id}
POST /sales-orders/{so_id}/details
PUT /sales-order-details/{detail_id}
DELETE /sales-order-details/{detail_id}

## Kurs USD/IDR (EXIM)
GET /exchange-rates
POST /exchange-rates
GET /exchange-rates/latest

## Packing (antara QC dan Delivery)
GET /packing
POST /packing
GET /packing/{packing_id}
POST /packing/{packing_id}/details

## Master: Brand & Customer PIC
GET /masters/brands
POST /masters/brands
PUT /masters/brands/{brand_id}
DELETE /masters/brands/{brand_id}
GET /masters/customer-pics
POST /masters/customer-pics
DELETE /masters/customer-pics/{pic_id}

## Master: Item FG & matrix harga (sheet Excel)
GET /masters/items
POST /masters/items
GET /masters/prices

Field tambahan **PO / baris SO** (sinkron dengan CSV `03_Master_Data_Marketing.csv`):
- Header: `marketing_excel_date_serial`, `po_customer_ref`, `order_type_label`, `brand_name_snapshot`, `customer_name_snapshot`
- Baris: `master_item_id`, `thi_line_ref`, `thickness_text`, `emboss`, `vir_softness_type`, `rtd_text`, `etd_excel_serial`, `stock_wh_qty`, `balance_qty`, `system_reference`, `detail_remark`, plus `delivery_schedules[]` (1–12: `sequence_no`, `qty`, `delivery_date`)

## Laporan export CSV
GET /reports/sales-orders-export.csv (termasuk kolom marketing header)
GET /reports/sales-order-lines-export.csv (baris SO + `copied_from_detail_id` + `delivery_1_qty` … `delivery_12_date`)

## Pabean — AJU (Core Customs / VICTORY-D, lengkap per sheet)

Tabel `customs_declarations` + `customs_aju_sheet_rows` menyimpan **setiap sel** per baris sebagai JSON (`cells`), sehingga **tidak ada kolom yang terlewat** dibanding CSV asli.

GET /customs/declarations
GET /customs/declarations/{id} — detail + `sheets` { SHEET_CODE: [ {kolom: nilai}, ... ] }
GET /customs/declarations/by-nomor/{nomor_aju}
DELETE /customs/declarations/{id}
POST /customs/declarations/import-upload — form-data: `files` (banyak `NN_*.csv`), optional `source_label`
POST /customs/declarations/import-zip — form-data: `file` (ZIP berisi CSV), optional `source_label`

**PO:** field `customs_declaration_id` (opsional) di `po_headers` menaut ke `customs_declarations.id`.

Impor CLI: `cd backend && PYTHONPATH=. python scripts/import_customs_aju_folder.py /path/ke/017_728_VICTORY_D_extracted`

## List harga buyer (Excel → CSV per sheet: `01_NB.csv`, …)

Tabel `buyer_price_lists` + `buyer_price_sheet_rows` — tiap baris `cells` JSON (format kolom berbeda per buyer).

GET /buyer-prices/lists
GET /buyer-prices/lists/{id} — detail + `rows`: [ { kolom: nilai }, … ]
GET /buyer-prices/by-buyer/{buyer_code}
DELETE /buyer-prices/lists/{id}
POST /buyer-prices/import-upload — form-data: `files` (banyak `NN_*.csv`), optional `source_label`
POST /buyer-prices/import-zip — form-data: `file` (ZIP berisi CSV), optional `source_label`

Impor CLI: `cd backend && PYTHONPATH=. python scripts/import_buyer_price_folder.py /path/ke/LIST_HARGA_ALL_BUYER_extracted`

---

# END
