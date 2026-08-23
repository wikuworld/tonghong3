# Status menu ERP vs MRP (sidebar)

Catatan singkat dual path — agar tidak bingung Production/QC/Packing muncul di dua tempat.

## Dual path

| Area | Peran |
|------|--------|
| **ERP** Production / QC / Packing | Buku/order ERP + bridge dari shopfloor (hint sidebar: *buku ERP*) |
| **MRP** Proses / Lab / Packing / Gudang FG / Checkpoint | Operasi shopfloor harian |

## Master katalog

Menu MRP Master (kecuali Treatment) = **lihat saja** dari ERP (`master_items` / `raw_materials`). CRUD di **Inventory** / Master Items.

## Disembunyikan dari sidebar (route tetap ada)

- Penawaran, Material Outstanding
- Harga Khusus, Harga Khusus Customer (API broken)
- Inventory Penerimaan
- Finance: Subcon / Mapping Akuntansi / Journal
- Dihapus UI: Customs, Kurs, Master Import ZIP

Lihat juga: [`dokumentasi/adr-erp-only-masters.md`](adr-erp-only-masters.md).
