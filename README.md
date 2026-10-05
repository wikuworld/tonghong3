# Tonghong ERP & MRP

Sistem ERP ringan untuk alur **Sales/PO → Produksi → QC → Packing → Delivery → Invoice**, termasuk **flow Marketing (MKT)** dan ekspor laporan CSV.

## Fitur utama

- **PO / Sales Order**: input header + detail material, status PO, alur MKT (flowchart).
- **Production**: order produksi + detail lot.
- **QC**: validasi thickness & status OK/NG.
- **Packing**: menghubungkan Production + QC, wajib **done** sebelum Delivery.
- **Delivery + Surat Jalan**: delivery detail hanya untuk lot **QC OK**, status `sent` butuh minimal 1 detail.
- **Invoice**: berbasis delivery `sent`.
- **Marketing**:
  - **Outstanding (format marketing)**: baris PO yang belum selesai + filter balance, export CSV.
  - **Delivery list (format marketing)**: join delivery → produksi → PO (+ invoice bila ada), export CSV.
- **Reports (CSV)**: rekap PO harian, export sales orders & lines.
- **Customs (AJU)**: simpan data per sheet sebagai JSON cells (tidak ada kolom hilang).

## Terminologi: PO vs SO

- Di backend endpoint dan tabel masih menggunakan istilah **PO** (mis. `/po`, `po_headers`, `po_details`) untuk kompatibilitas historis.
- Secara proses bisnis, dokumen tersebut adalah **Sales Order (SO)** dari customer. Karena itu di UI label ditampilkan sebagai **SO** (mis. *No SO*).
- Jika suatu saat ada **Purchase Order vendor**, sebaiknya dibuat modul terpisah agar tidak rancu.

## Struktur repo (UAT)

- `erp/backend/`: FastAPI ERP (`tonghong-uat-erp-api` :8001)
- `erp/frontend/`: Vue ERP (`tonghong-uat-erp-ui` :8081)
- `mrp/backend/`: FastAPI MRP + shopfloor (`tonghong-uat-mrp-api` :8002)
- `mrp/frontend/`: Vue MRP + login (`tonghong-uat-mrp-ui` :8082)
- `tools/native/systemd/`: unit systemd UAT

## Menjalankan (systemd, server dev)

1. Salin env contoh:

```bash
cp .env.example .env
```

2. Pasang unit (sekali) lalu start:

```bash
./tools/stack-native.sh install
./tools/stack-native.sh start
```

Yang terjadi:
- MariaDB di port 3306
- Backend FastAPI di `${BACKEND_PORT:-8000}` — otomatis `alembic upgrade head`
- Flask MRP di `127.0.0.1:5010`
- Frontend Vite + HMR di `127.0.0.1:5173`
- Nginx proxy di `${WEB_PORT:-8080}` — UI + `/api`

URL:
- **UI + API**: `http://localhost:8080`
- **API langsung**: `http://localhost:8000/api/v1`
- **Swagger**: `http://localhost:8000/docs`
- **Healthcheck**: `http://localhost:8000/health`

Setelah ubah kode Python: `sudo systemctl restart tonghong-backend`

File Docker (`docker-compose.yml`, `Dockerfile`, dll.) diarsip di luar repo (`~/archives/docker-repo-*.tgz`), bukan cara jalan di server ini.

## Business process (ringkas)

Alur utama:

1. **Marketing** input PO (header + detail).
2. **Production** dibuat dari PO.
3. **QC** mengukur dan memberi status OK/NG.
4. **Packing** mengikat Production + QC, lalu status **done**.
5. **Delivery** dibuat dari Packing **done**, isi detail (hanya QC OK), lalu status `sent`.
6. **Invoice** dibuat dari Delivery `sent`.

Alur MKT (flowchart kantor) ada di `po_headers.mkt_workflow_stage`:

`input_system` → `rekap_printed` → `with_ppic` → `back_to_mkt` → `in_outstanding` → `material_followup` → `delivery_arranged` → `sj_invpl` → `invoice_billing`

Detail aturan bisnis: `backend/app/services/business_rules.py` dan Swagger `/docs`.

## Endpoint penting (ringkas)

Base: `/api/v1`

- **Marketing**
  - `GET /marketing/outstanding-lines?balance_filter=exclude_zero|all|positive_only`
  - `GET /marketing/outstanding-lines.csv?balance_filter=...`
  - `GET /marketing/delivery-lines`
  - `GET /marketing/delivery-lines.csv`
- **Reports**
  - `GET /reports/po-daily-recap.csv?date=YYYY-MM-DD`
- **Documents** (format marketing Tong Hong)
  - Surat jalan: `GET /documents/surat-jalan/{delivery_id}` (HTML), `GET /documents/surat-jalan/{delivery_id}/pdf`
  - INVPL: `GET /documents/invpl/{packing_id}` (HTML), `GET /documents/invpl/{packing_id}/pdf`, `GET /documents/invpl/{packing_id}/xlsx`

## Catatan pengembangan

- **Migrasi DB**: Alembic ada di `backend/alembic/versions/`.
- **CORS**: atur `CORS_ORIGINS` di `.env`.
- **Secrets**: jangan commit `.env`; repo menyediakan `.env.example`.
- Restart service: `./tools/stack-native.sh restart` atau `sudo systemctl restart tonghong-backend`.

