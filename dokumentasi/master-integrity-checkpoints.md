# Master integrity checkpoints

Titik restore untuk roadmap struktur master data (GitHub tag + Alembic).
Ikuti: satu fase = satu PR → merge `main` → isi baris di bawah → `git tag db-master-fN`.

## Cara restore

```bash
# Batalkan fase terakhir (contoh F1)
git revert -m 1 <merge-commit-SHA>
cd backend && .venv/bin/alembic downgrade <revision_sebelum_fase>
sudo systemctl restart tonghong-backend
```

Lihat juga rencana: branch `feature/db-master-integrity-fN`, tag `db-master-fN`.

## Log checkpoint

| Fase | Tanggal | PR URL | Alembic revision (head fase) | Git tag | SHA | Catatan restore |
|------|---------|--------|------------------------------|---------|-----|-----------------|
| baseline | 2026-08-03 | — | `d8e9f0a1b2c3` + `k2l3m4n5o6p7` (merge `m0a1b2c3d4e5`) | — | — | Head `main` sebelum integrity; merge heads packing+marketing |
| F1 | 2026-08-03 | https://github.com/wikuworld/tonghong/pull/20 | `t1a2b3c4d5e6` | `db-master-f1` | `184e9187163b` | `alembic downgrade s3t4u5v6w7x8` |
| F2 | 2026-08-03 | https://github.com/wikuworld/tonghong/pull/20 | `t2b3c4d5e6f7` | `db-master-f2` | `184e9187163b` | `alembic downgrade t1a2b3c4d5e6` |
| F3 | 2026-08-03 | https://github.com/wikuworld/tonghong/pull/20 | `t3c4d5e6f7g8` | `db-master-f3` | `184e9187163b` | `alembic downgrade t2b3c4d5e6f7` |
| F4 | 2026-08-03 | https://github.com/wikuworld/tonghong/pull/20 | `t4d5e6f7g8h9` | `db-master-f4` | `184e9187163b` | `alembic downgrade t3c4d5e6f7g8` |

> Catatan: implementasi di branch `feature/db-master-integrity-f1` membawa F1–F4 dalam satu PR agar gate smoke bisa diverifikasi end-to-end di dev. Tag `db-master-fN` dibuat **setelah merge ke main** (atau di SHA merge) sesuai konvensi restore.

## Revisi Alembic roadmap (dev)

| Fase | Revision ID | File |
|------|-------------|------|
| F1 | 2026-08-03 | https://github.com/wikuworld/tonghong/pull/20 | `t1a2b3c4d5e6` | `db-master-f1` | `184e9187163b` | `alembic downgrade s3t4u5v6w7x8` |
| F2 | 2026-08-03 | https://github.com/wikuworld/tonghong/pull/20 | `t2b3c4d5e6f7` | `db-master-f2` | `184e9187163b` | `alembic downgrade t1a2b3c4d5e6` |
| F3 | 2026-08-03 | https://github.com/wikuworld/tonghong/pull/20 | `t3c4d5e6f7g8` | `db-master-f3` | `184e9187163b` | `alembic downgrade t2b3c4d5e6f7` |
| F4 | 2026-08-03 | https://github.com/wikuworld/tonghong/pull/20 | `t4d5e6f7g8h9` | `db-master-f4` | `184e9187163b` | `alembic downgrade t3c4d5e6f7g8` |

## Smoke F1 (dev 2026-08-03)

- `UNIQUE brands.code` (`uq_brands_code`) OK
- Brand PUMA/REEBOK + maps OK; swatch PUMA/REEBOK `brand_id` null = **0**
- `buyer_codes` seed = 10; form-options pakai registry
- Audit: `cd backend && .venv/bin/python scripts/audit_master_integrity.py --json`
- Fluorescent non-GLOBAL `brand_id` null = **0**; `material_aliases` = 8
- Import: default **warn**; F4 `?reject_unknown_buyer=true` → 400

## Out of scope / ditunda

- Katalog `materials.id` (F4 opsional) — butuh keputusan bisnis rewrite wizard PO.
- Partial unique soft-delete — hanya setelah uji staging (lihat `master-soft-delete-policy.md`).
