# UAT — Label roll packing (meeting TongHong 17/9/26)

Tanggal catatan: 2026-09-19  
Modul: MRP Packing FG — cetak label roll

## Status

Layout label roll **diterima untuk UAT** dengan implementasi saat ini di:

- `mrp/frontend/src/utils/mrpPackingRollLabelPrint.js`
- API: `GET /api/mrp/packing/roll/{id}/label` + aksi `print_roll_label`

Sample fisik sticker TongHong **belum dilampirkan** di repo (`dokumentasi/`). Bila ada PDF/foto sample, simpan di folder ini dan bandingkan field-by-field.

## Field yang dicetak (layout sekarang)

| Area | Isi |
|------|-----|
| Brand | Logo `/logo-tonghong.png` + Tong Hong Tannery |
| Lot.No. | `lot_no` |
| Customer / Quantity | customer, qty SF |
| Packing No. / Gross | `kode_packing`, gross weight |
| Factory Prod.Code / Net | SO / factory code, net weight |
| Description / Mass | deskripsi, softness/mass |
| Color / Thickness | warna, tebal |
| Roll.No. + 張數 | nomor roll + lembar |
| Emboss / dates | emboss, producing, expiration |
| anti moldy / Moisture / Remark | sesuai payload |
| Barcode | CODE128 dari `kode_packing` |
| Sizes | rangkaian ukuran `a+b+c` |

Ukuran kertas: **100mm × 72mm**.

## Cara smoke-test UAT

1. Buka Packing FG → play sesi RPI (atau barang sisa approved).
2. START panel ukur → ADD beberapa size → CETAK LABEL ROLL.
3. Pastikan popup print tidak diblokir browser.
4. Cek barcode terbaca scanner (nilai = kode packing).
5. Reprint dari dialog history roll.

## Catatan defer

- Penyesuaian pixel-perfect vs sample fisik TongHong menunggu file sample.
- ERP frontend **tidak** menduplikasi route packing MRP; util label ada mirror di `erp/frontend` hanya jika dipakai gateway — tidak diubah di fase ini.
