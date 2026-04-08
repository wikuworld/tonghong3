# Review layout halaman admin

Periksa file Vue admin yang sedang dibuka atau yang saya sebutkan:

1. Toolbar tidak memaksa overflow: input pencarian memakai class `*-toolbar-search`, tombol bisa wrap (`flex-wrap`).
2. Tabel punya `empty-text` i18n, kolom aksi tidak menindih konten — jika perlu scroll horizontal, pastikan kontainer benar.
3. Dialog punya footer terpisah dan tidak memotong konten di layar kecil.
4. Semua teks UI lewat `t(...)` dengan kunci di `id` / `en` / `zh`.

Sebutkan file yang perlu diubah dan terapkan perbaikan minimal.
