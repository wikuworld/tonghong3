---
name: tonghong-admin-page
description: Menambah atau mengubah halaman Vue di frontend/src/views/admin mengikuti pola Tonghong (AdminSection, tabel, dialog, i18n). Pakai saat membuat halaman /admin baru atau menyamakan UI dengan Customer/PO/Delivery.
---

# Halaman admin Tonghong

## Sebelum ngoding

1. Baca contoh yang sudah konsisten: `CustomersPage.vue`, `PurchaseOrderPage.vue`, atau `DeliveryPage.vue`.
2. Cek rule proyek: `.cursor/rules/tonghong-admin-vue.mdc` dan `tonghong-stack.mdc`.

## Struktur halaman

- Bungkus dengan `AdminSection`; judul/subtitle dari `t('pages.*')`.
- Toolbar di slot `#actions`: `el-input` pencarian + tombol sekunder + `el-button type="primary"` dengan ikon (`Plus`, `Download`, dll.).
- Panel filter: `div.filter-panel` + `filter-panel__title` + `el-form.filter-form`.
- Tabel: `class="admin-table"`, `border stripe size="small"`, kolom index, `empty-text`, aksi pakai ikon `link` + `el-tooltip`, hindari lebar tetap pada input toolbar (pakai class `*-toolbar-search`).

## Dialog & form

- `align-center`, `destroy-on-close` bila perlu; footer flex rata kanan (`*-dialog-footer`).
- Validasi form; string UI lewat i18n — tambahkan kunci di `frontend/src/i18n/index.js` untuk **id**, **en**, **zh**.

## Anti overlap

- Jangan set `width` besar pada search di scoped CSS; andalkan style global `style.css`.
- Tabel lebar: biarkan scroll di kontainer (body kartu sudah `overflow-x-auto`).

## Docker (production)

- Setelah ubah UI untuk image Nginx, ingatkan user: `docker compose up -d --build web`. Dev HMR: `docker compose --profile dev up frontend-dev` di port 5173.
