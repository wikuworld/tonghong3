# Master integrity checkpoints

Titik restore untuk roadmap struktur master data (GitHub tag + Alembic).
Ikuti: satu fase = satu PR → merge `main` → isi baris di bawah → `git tag db-master-fN`.

## Cara restore

```bash
# Batalkan fase terakhir (contoh F1)
git revert -m 1 <merge-commit-SHA>
docker compose exec backend alembic downgrade <revision_sebelum_fase>
docker compose restart backend
```

Lihat juga rencana: branch `feature/db-master-integrity-fN`, tag `db-master-fN`.

## Log checkpoint

| Fase | Tanggal | PR URL | Alembic revision (head fase) | Git tag | SHA | Catatan restore |
|------|---------|--------|------------------------------|---------|-----|-----------------|
| baseline | 2026-08-03 | — | `d8e9f0a1b2c3` + `k2l3m4n5o6p7` (merge `m0a1b2c3d4e5`) | — | — | Head `main` sebelum integrity; merge heads packing+marketing |
| F1 | 2026-08-03 | _(isi URL setelah PR merge)_ | `t1a2b3c4d5e6` | `db-master-f1` | _(SHA setelah merge)_ | `alembic downgrade s3t4u5v6w7x8` |
| F2 | 2026-08-03 | _(sama / epic PR)_ | `t2b3c4d5e6f7` | `db-master-f2` | | `alembic downgrade t1a2b3c4d5e6` |
| F3 | 2026-08-03 | | `t3c4d5e6f7g8` | `db-master-f3` | | `alembic downgrade t2b3c4d5e6f7` |
| F4 | 2026-08-03 | | `t4d5e6f7g8h9` | `db-master-f4` | | `alembic downgrade t3c4d5e6f7g8` |

> Catatan: implementasi di branch `feature/db-master-integrity-f1` membawa F1–F4 dalam satu PR agar gate smoke bisa diverifikasi end-to-end di dev. Tag `db-master-fN` dibuat **setelah merge ke main** (atau di SHA merge) sesuai konvensi restore.

## Revisi Alembic roadmap (dev)

| Fase | Revision ID | File |
|------|-------------|------|
| F1 | `t1a2b3c4d5e6` | `t1a2b3c4d5e6_master_integrity_f1.py` |
| F2 | `t2b3c4d5e6f7` | `t2b3c4d5e6f7_master_integrity_f2.py` |
| F3 | `t3c4d5e6f7g8` | `t3c4d5e6f7g8_master_integrity_f3.py` |
| F4 | `t4d5e6f7g8h9` | `t4d5e6f7g8h9_master_integrity_f4.py` |

## Smoke F1 (dev 2026-08-03)

- `UNIQUE brands.code` (`uq_brands_code`) OK
- Brand PUMA/REEBOK + maps OK; swatch PUMA/REEBOK `brand_id` null = **0**
- `buyer_codes` seed = 10; form-options pakai registry
- Audit: `docker compose exec backend python scripts/audit_master_integrity.py --json`
- Fluorescent non-GLOBAL `brand_id` null = **0**; `material_aliases` = 8
- Import: default **warn**; F4 `?reject_unknown_buyer=true` → 400

## Out of scope / ditunda

- Katalog `materials.id` (F4 opsional) — butuh keputusan bisnis rewrite wizard PO.
- Partial unique soft-delete — hanya setelah uji staging (lihat `master-soft-delete-policy.md`).
