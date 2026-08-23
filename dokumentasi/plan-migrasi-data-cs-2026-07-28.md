# Plan: migrasi data Color Swatch `DATA CS 2026-07-28(1).xlsx`

Sumber: `dokumentasi/DATA CS 2026-07-28(1).xlsx` (904 baris, 1 sheet).
Target: tabel `color_swatch_recipes` (DB existing 3.047 resep aktif).

## Batasan

- Tidak mengubah kode aplikasi (parser, import, router, frontend).
- Hanya penyesuaian data di MariaDB.
- Tidak menonaktifkan resep yang tidak ada di Excel (file ini subset).
- Tidak insert near-duplicate (kunci unik exact-string akan menganggap ejaan beda sebagai baris baru).

## Temuan ringkas

Excel memakai kolom yang sama dengan import existing (`CUSTOMER`, `COLOR CODE`, `COLOR NAME`, `EMBOS`, `COLOR SWATCH`, `BACKING`, `NO URUT`, `BRAND`, `MATERIAL`, `TGGL MASUK`). Semua 904 baris lolos parser; buyer valid (NIKE, UA, NB, ADIDAS).

Matching ke DB:

| Cara | Hasil |
|---|---|
| Kunci persis (pabrik+buyer+kode+material+emboss) | 418 |
| Material + emboss dinormalisasi | +446 |
| Pabrik + buyer + kode warna | 900 / 904 |
| Terlihat baru | 4 — ternyata alias ejaan (`10126C`→`10162C`, `430-A`→`430`, `49R`→`49R 1A`) |

Import upsert existing **tidak dipakai**: akan insert ~486 duplikat.

## Strategi data

1. Parse Excel dengan parser existing (dipakai di memori, tidak diubah).
2. Duplikat di Excel (33 kunci sama): baris terakhir yang menang.
3. Cari resep DB dengan urutan:
   - kunci persis
   - pabrik + buyer + kode + material ternormalisasi + kode emboss
   - prefix `color_standard` + pabrik + buyer
   - alias kode yang sudah diketahui
4. Satu baris DB hanya dipakai sekali.
5. Jika ketemu: **UPDATE field non-kunci** dari Excel (data user menang):
   - `color_name`, `color_standard`, `backing`, `legacy_urut`, `entered_at`, `source_file`
   - `source_file` = `DATA CS 2026-07-28(1).xlsx`
6. **Kunci unik tidak diubah** (`factory_key`, `buyer_code`, `color_code`, `material_name`, `emboss`) supaya tidak bentrok constraint dan tidak merusak import CSV berikutnya.
7. Jika tidak ketemu setelah semua langkah: INSERT resep baru + resolve `customer_id` / `brand_id` / CSI lewat helper existing.
8. Alias kode Excel yang beda ejaan dicatat di `color_code_aliases` (data saja) agar kode user tetap ketemu CSI.
9. PO yang sudah terikat (2 resep / 6 baris) tidak disentuh kecuali kebetulan match; kunci unik mereka tetap.

## Yang tidak dilakukan

- `replace_inactive` / hapus resep di luar Excel (~2.000 baris lain tetap aktif).
- Ubah `backend/app/services/color_swatch.py` atau endpoint import.
- Commit perubahan kode.

## Verifikasi setelah apply

- Hitung `source_file = DATA CS 2026-07-28(1).xlsx` = jumlah baris Excel yang ter-update/insert.
- Total `color_swatch_recipes` naik hanya sebesar insert murni (perkiraan 0).
- Unique key tetap unik; PO `color_swatch_recipe_id` masih valid.
- 4 alias ejaan ter-match, bukan baris baru.

## Hasil apply (2026-08-23)

- Update 871 resep (33 duplikat Excel digabung, last-wins). Insert 0.
- Total tetap 3.047 aktif; unique key tetap 3.047.
- Match: exact 401, norm 432, color_standard 38.
- Alias baru di `color_code_aliases`: `UA/10126C`, `UA/430-A` → CSI 430, `NIKE/49R` → CSI 49R.
- PO tetap valid (6 baris / 2 resep). Resep 2815 (WEALTH VAST / 6CV) ter-update nama → `HYPER PINK FLUORESCENT` (match benar, kode swatch sama).
