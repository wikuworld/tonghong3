# Kontrak list: pagination + sorting (ERP / MRP)

## Query params

| Param | Keterangan |
|-------|------------|
| `page` | 1-based (default `1`) |
| `page_size` | default `20`, max `200` |
| `limit` / `offset` | alias legacy (`offset = (page-1)*page_size`) |
| `skip` / `limit` | alias marketing |
| `sort_by` | nama kolom (whitelist per endpoint) |
| `sort_dir` | `asc` atau `desc` (default biasanya `desc` untuk tanggal) |

## Response

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20
}
```

Endpoint lama yang masih mengembalikan `limit`/`offset` di body boleh menyertakan keduanya bersama `page`/`page_size`.

## UI

- `el-pagination` + `sortable="custom"` + refetch server saat page/size/sort berubah
- Nomor urut: `(page - 1) * pageSize + index + 1`
- Default sort: tanggal/id terbaru (`desc`) kecuali master katalog (kode/nama `asc`)

## Whitelist sort

Hanya kolom yang di-whitelist di backend yang diterima. `sort_by` tidak dikenal → fallback default order endpoint.
