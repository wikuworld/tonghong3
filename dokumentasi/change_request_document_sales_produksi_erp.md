# CHANGE REQUEST DOCUMENT (CR)

**Project:** Sistem Sales, Produksi & ERP  
**Tanggal:** 02 April 2026  
**Requestor:** Business / Marketing / Operasional  

---

## 1. BACKGROUND

Saat ini proses bisnis masih banyak menggunakan **Excel manual**, yang menyebabkan:
- Data tidak konsisten (SO, produksi, QC, delivery)
- Sulit melakukan tracking (over production, reject, status produksi)
- Tidak ada audit trail perubahan data
- Monitoring oleh marketing terbatas (tidak real-time)
- Integrasi ke sistem lain (Bea Cukai, Zahir) belum optimal

Diperlukan pengembangan sistem terintegrasi untuk:
- Sales Order
- Produksi
- QC
- Packing & Delivery
- Reporting & Dashboard

---

## 2. OBJECTIVE

- Mengganti proses manual (Excel) menjadi sistem terpusat  
- Meningkatkan **visibility & traceability** end-to-end  
- Menyediakan **real-time monitoring** untuk marketing  
- Mengurangi human error  
- Mendukung integrasi ke ERP / sistem eksternal  

---

## 3. SCOPE OF CHANGE

### 3.1 Master Data Enhancement
- Penambahan master:
  - Customer (multi PIC, versioning)
  - Brand (multi per customer)
  - Buyer (kategori: OIA, Direct, Regular)
  - Material + atribut (ketebalan, warna, emboss, dll)
  - Master harga dengan approval  

---

### 3.2 Sales Order (SO) Revamp
- Rename:
  - PO → Sales Order (SO)
- Fitur:
  - Multi item dalam 1 SO
  - Item sama dengan ETD berbeda
  - Copy item
  - Auto pricing dari master harga
  - Billing & Delivery address terpisah
  - Remark tersimpan dan tampil di dokumen  

---

### 3.3 Production Module
- Generate nomor produksi otomatis (running number)
- Link ke Sales Order
- Tracking status produksi
- Audit log perubahan data
- Monitoring oleh marketing  

---

### 3.4 Finished Goods & Over Production
- Tracking berdasarkan **lot number**
- Identifikasi kelebihan produksi
- Trace ke SO asal
- Validasi input agar tidak ada produksi tanpa referensi SO  

---

### 3.5 Quality Control (QC) Module
- QC record auto-generate dari produksi
- Pencatatan:
  - Qty checked
  - Qty reject
  - Reason reject
- Reject dapat:
  - diukur ulang / ditimbang
- Data reject visible ke marketing  

---

### 3.6 Packing & Delivery
- Modul baru:
  - Packing monitoring
  - Delivery tracking
- Flow:
  **QC → Packing → Delivery**
- Generate dokumen:
  - Surat jalan (dot matrix)
  - Dokumen A4  

---

### 3.7 Dashboard & Monitoring
- Dashboard per role (marketing, admin, dll)
- Widget:
  - Status produksi
  - Outstanding SO
  - QC rate
  - Delivery status
  - Kurs USD  

---

### 3.8 Exchange Rate (Kurs)
- Input oleh user EXIM
- Menggunakan **effective date**
- Digunakan untuk invoice
- Widget kurs di dashboard  

---

### 3.9 Contract Management
- Generate kontrak dari multiple invoice
- PIC dapat dipilih
- Customer memiliki multiple PIC  

---

### 3.10 Reporting & Export
- Laporan dinamis (filterable)
- Export CSV:
  - SO
  - Item
  - Qty
  - Status
- Mengurangi ketergantungan Excel  

---

### 3.11 User & Access Control
- Role:
  - Admin
  - Operator
  - Supervisor
  - Marketing
  - EXIM  
- Dashboard dan akses berbasis role  

---

### 3.12 Integration
- Integrasi dengan:
  - Bea Cukai (BC)
  - Zahir  
- Export data standar (CSV/API)

---

## 4. BUSINESS PROCESS FLOW (TO-BE)

```
Sales Order (SO)
        ↓
Production Order
        ↓
Quality Control (QC)
        ↓
Packing
        ↓
Delivery
```

---

## 5. FUNCTIONAL REQUIREMENTS (HIGHLIGHT)

- Auto numbering (SO & Production)
- Approval workflow (harga)
- Audit log (mandatory)
- Multi item per SO
- Over production tracking
- Reject tracking
- Real-time dashboard
- Dynamic reporting  

---

## 6. NON-FUNCTIONAL REQUIREMENTS

- Bilingual (Indonesia & English)
- Printable format:
  - A4
  - Dot Matrix
- Role-based access control
- Modular architecture (MRP & ERP bisa dipisah)
- Data consistency & integrity  

---

## 7. IMPACT ANALYSIS

### Positive Impact
- Efisiensi operasional meningkat  
- Monitoring real-time  
- Data lebih akurat  
- Mengurangi kesalahan manual  

### Potential Risks
- Perubahan proses kerja (user adaptation)  
- Kebutuhan training user  
- Data migration dari Excel  

---

## 8. ASSUMPTIONS

- Semua transaksi berbasis SO (PO tidak digunakan lagi)  
- Currency utama: USD  
- User EXIM bertanggung jawab atas kurs  
- Semua produksi harus refer ke SO  

---

## 9. DEPENDENCIES

- Master data harus lengkap sebelum go-live  
- Approval flow harga harus disepakati  
- Template dokumen (invoice, surat jalan, kontrak)  

---

## 10. OPEN ISSUES

1. Definisi reject:
   - weight-based atau dimension-based?  
2. Apakah perlu multi currency selain USD?  
3. Level approval harga (single / multi-level)?  
4. Detail integrasi ke Bea Cukai & Zahir (API vs CSV)?  

---

## 11. PRIORITY

**HIGH PRIORITY:**
- Sales Order
- Production
- QC
- Dashboard

**MEDIUM:**
- Contract
- Integration

**LOW:**
- Advanced analytics  

---

## 12. APPROVAL

| Role | Nama | Tanggal | Tanda Tangan |
|------|------|--------|-------------|
| Requestor |  |  |  |
| IT / Dev Lead |  |  |  |
| Business Owner |  |  |  |

