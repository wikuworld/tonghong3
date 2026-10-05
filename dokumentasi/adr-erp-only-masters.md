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
4. Dropdowns/lists resolve via **ERP HTTP API** (`ERP_API_URL` + service token), not cross-DB SQL.
5. Operational SoR that stays in MRP: lot tables (`tbl_stok_*`), WIP/lab/proses/packing, treatment, resep names, palet/YL.
6. `tbl_master_po` remains as PO work-queue mirror (not a catalog master); filled by **ERP→MRP push** only. MRP reconcile (`POST /api/v1/mrp/sync/po` di sisi MRP) meminta ERP push ulang via service token — bukan pull SQL.

## Consequences

- Install/migrate paths stop creating catalog mirrors.
- After FK migration, mirror tables are dropped from `tonghong_mrp`.
- ERP master rows are never deleted by this migration.
- Auto-create of ERP customers from free-text is disabled in production (`MRP_AUTO_CREATE_ERP_CUSTOMER=false`).

## Grants (MRP DB user)

MRP app user **tidak** punya akses ke database ERP.
Katalog (`customers`, `raw_materials`, `master_items`) hanya via HTTP
(`ERP_API_URL` + `X-Internal-Api-Key` / `ERP_SERVICE_TOKEN`).
Tidak ada jalur SQL lintas-DB / rollback.
