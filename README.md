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

## Struktur repo

- `backend/`: FastAPI + SQLAlchemy + Alembic (MariaDB/MySQL)
- `frontend/`: Vue 3 + Vite + Element Plus (admin UI)
- `docker-compose.yml`: MariaDB + backend + web (Nginx) + profil dev untuk Vite HMR
- `api_flow_tonghong.md`: daftar endpoint & ringkasan business rules

## Menjalankan dengan Docker (disarankan)

1. Salin env contoh:

```bash
cp .env.example .env
```

Untuk deploy non-dev, set minimal:

```bash
APP_ENV=production
JWT_SECRET=<secret-kuat-minimal-32-karakter>
ADMIN_USERNAME=<admin-non-default>
ADMIN_PASSWORD=<password-kuat>
```

2. Jalankan:

```bash
docker compose up --build
```

Yang terjadi:
- MariaDB hidup di port `${MYSQL_PORT:-3306}`
- Backend FastAPI di `${BACKEND_PORT:-8000}` dan **otomatis menjalankan** `alembic upgrade head`
- Web (Nginx + build frontend) di `${WEB_PORT:-8080}`

URL:
- **Web**: `http://localhost:8080`
- **API**: `http://localhost:8000/api/v1`
- **Healthcheck**: `http://localhost:8000/health`

### Mode dev frontend (HMR)

Jika ingin Vite dev server:

```bash
docker compose --profile dev up --build frontend-dev
```

Frontend dev: `http://localhost:5173` (proxy API ke backend via `VITE_API_PROXY`).

## Menjalankan tanpa Docker (opsional)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# set DATABASE_URL sesuai lingkungan Anda
export DATABASE_URL='mysql+pymysql://tonghong:tonghong_secret@127.0.0.1:3306/tonghong'

alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

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

Detail aturan bisnis lebih lengkap ada di `api_flow_tonghong.md`.

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
- **CD GHCR**: set GitHub Actions secrets `JWT_SECRET`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` sebelum publish image.

