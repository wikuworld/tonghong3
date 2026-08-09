# Scan lanjutan master (di luar impor CSI/Nike/Adidas)
Generated from live DB.
| Label | Area | Temuan | n |
|-------|------|--------|---|
| `SOFT_DUP` | fluorescent same code multi-season | codes appearing in >1 row (usually multi-season — sah): showing top 20 | 20 |
| `CONTEXT_OK` | swatch same code multi-recipe | banyak resep per kode (factory/material beda) — sample top | 15 |
| `CONTEXT_OK` | csi per buyer | distribusi | 4057 |
| `CONTEXT_OK` | coverage | CSI=['ADIDAS', 'NB', 'NIKE', 'UA']; price=['ADIDAS', 'NB', 'NB01', 'NIKE', 'UA']; swatch=['ADIDAS', 'NB', 'NIKE', 'PUMA' | 0 |
| `CROSS_REF` | fluo codes not in CSI (per buyer) | bukan error — fluo punya season sendiri; hitung orphan vs CSI | 95 |
| `SOFT_DUP` | master_items same material_name | name groups with >1 row (top shown): query returned 15 in top slice | 57 |
