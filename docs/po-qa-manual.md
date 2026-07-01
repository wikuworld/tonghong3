# Manual QA — Modul PO (`/admin/po`)

Checklist per role setelah perubahan RBAC, delete guard, dan validasi confirm.

## Persiapan

- Akun uji: `admin`, `marketing`, `sales`, `ppic`, `finance` (view-only atau sesuai matrix)
- Minimal satu PO draft **dengan** baris detail dan satu **tanpa** baris detail

## Matrix yang diharapkan

| Aksi | admin | marketing | sales | ppic | finance |
|------|-------|-----------|-------|------|---------|
| Lihat list | ✅ | ✅ | ✅ | ✅ | ✅ |
| Buat PO | ✅ | ✅ | ✅ | ❌ | ❌ |
| Edit header / confirm | ✅ | ✅ | ✅ | ✅ | ❌* |
| Edit baris (harga) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Hapus PO | ✅ | ❌ | ❌ | ❌ | ❌ |
| Duplikasi PO | ✅ | ✅ | ✅ | ❌ | ❌ |
| Export CSV / dokumen | ✅ | ✅ | ✅ | ✅ | ✅ |

\* Finance: hanya update baris detail via API; tidak boleh simpan header wizard penuh.

## Skenario fungsional

1. **Filter** — status `completed` dan kategori PO memfilter hasil list.
2. **Quick confirm** — PO tanpa baris: frontend menolak; PO dengan baris: berhasil `confirmed`.
3. **Stuck reason** — kolom lengkap menampilkan teks terjemahan (bukan string mentah backend).
4. **Hapus PO** — draft kosong: admin berhasil; PO dengan production/invoice/delivery: ditolak dengan pesan jelas.
5. **No. PO customer duplikat** — simpan dua PO sama customer + ref sama: error 409.
6. **Deep link** — `?po_id=ID` membuka highlight; `?po_id=ID&edit=1` membuka wizard (jika `canUpdate`).

## Regresi wizard

1. Buat PO 3 langkah — customer → material → review → simpan.
2. Edit — revisi marketing, copy item, jadwal kirim 21 gelombang max.
3. Draft localStorage — tutup dialog, buka lagi, draft ter-restore.

## Performa (opsional)

- List 50+ PO: tidak terasa lambat berlebihan (batch stuck reason).
