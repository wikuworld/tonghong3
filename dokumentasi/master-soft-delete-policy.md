# Soft-delete policy — Color Swatch & Fluorescent

## Perilaku

| Master | Delete API | Efek |
|--------|------------|------|
| Color Swatch | Soft (`is_active=false`) | Baris tetap; unique key tetap terisi |
| Fluorescent | Soft (`is_active=false`) | Sama |
| Master Item / Brand / Customer | Hard (diblok jika masih direferensikan) | — |

## PO / dokumen

- `po_details.color_swatch_recipe_id` boleh tetap menunjuk resep `is_active=0` (historis).
- Lookup / picker UI hanya menampilkan `is_active=1`.
- Jangan cascade-null FK saat soft-delete.

## Unique + re-import

- Soft-delete **tidak** membebaskan unique key → import ulang kombinasi sama akan **update** baris existing (upsert), bukan insert baru.
- Partial unique `WHERE is_active=1` **belum** diterapkan (perlu uji staging). Lihat roadmap F3.

## Checkpoint

Lihat [master-integrity-checkpoints.md](./master-integrity-checkpoints.md).
