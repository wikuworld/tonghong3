# Color Swatch — perilaku SO & impor (2026-08)

## Lookup SO
- Endpoint `GET /masters/color-swatch-recipes/lookup` hanya **wajib `buyer_code`**.
- `factory_key` / `customer_id` opsional dan **tidak memfilter** hasil (diterima agar FE lama tidak 422).
- Hasil = semua resep `is_active` untuk buyer itu (lintas pabrik). Label opsi menampilkan `factory_key`.

## Impor master = Excel/CSV terbaru
- `import-csv` / `import-bundled` default: `replace_inactive=true`, `replace_inactive_scope=global`.
- Setelah upsert, resep aktif yang **tidak ada di file** di-`is_active=False`.
- Scope `pair` tetap tersedia (orphan hanya per factory+buyer yang tersentuh file).

## Label UI
- Material PU → grup **Color Swatch**.
- Material Suede (`category`/`nama` mengandung suede/suide) → grup **Color Window**.
- Sumber data tetap tabel `color_swatch_recipes`.
