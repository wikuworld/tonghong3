# Seed `tonghong_mrp`

Dump historis. **Jangan** dipakai untuk recreate katalog mirror MRP.

## ERP-only (2026-08)

Katalog SoR: `tonghong.customers`, `tonghong.master_items`, `tonghong.raw_materials`.

Tabel mirror berikut **tidak** lagi dibuat/di-seed:

- `master_customer`
- `master_erp`
- `master_kulit`
- `master_kimia`
- `master_rp`
- `master_material_lain`
- `master_chemical` (legacy)

Install baru: ikuti `mrp/schema.sql` + `ensure_*` (tanpa CREATE mirror). Lot memakai `erp_material_id` + snapshot.

`tonghong_mrp.sql` disimpan sebagai artefak legacy; blok CREATE mirror sudah dikomentari / dinonaktifkan.
