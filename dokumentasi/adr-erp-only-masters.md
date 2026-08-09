# ADR: Master data ERP-only (tanpa mirror MRP)

## Status

Accepted — 2026-08-10

## Context

MRP historically mirrored ERP catalogs (`master_customer`, `master_erp`, `master_kulit`, `master_kimia`, `master_rp`, `master_material_lain`). That caused double maintenance and ID drift.

## Decision

1. **System of Record** for catalogs is Tonghong ERP only:
   - `customers`, `master_items`, `raw_materials` (+ `material_stocks` for financial book).
2. **MRP must not CREATE or sync mirror catalog tables** for those domains.
3. Shopfloor **transaction** tables store `erp_*_id` plus denormalized code/name snapshots.
4. Dropdowns/lists resolve via root-DB read / gateway against ERP.
5. Operational SoR that stays in MRP: lot tables (`tbl_stok_*`), WIP/lab/proses/packing, treatment, resep names, palet/YL.
6. `tbl_master_po` remains as PO work-queue mirror (not a catalog master).

## Consequences

- Install/migrate paths stop creating catalog mirrors.
- After FK migration, mirror tables are dropped from `tonghong_mrp`.
- ERP master rows are never deleted by this migration.
- Auto-create of ERP customers from free-text is disabled in production (`MRP_AUTO_CREATE_ERP_CUSTOMER=false`).

## Grants (MRP DB user)

MRP app user needs **SELECT** (not DML) on Tonghong ERP tables:

- `tonghong.customers`
- `tonghong.raw_materials`
- `tonghong.master_items`

Write path for catalogs remains ERP Inventory / Customers UI (or impor yang menulis ke `raw_materials` saja).
