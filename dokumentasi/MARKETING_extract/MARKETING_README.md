# Ekstraksi MARKETING.xlsx

**File:** `MARKETING.xlsx`
**Jumlah sheet:** 9

## Daftar sheet

1. **SOP** — 2 baris × 19 kolom
2. **INPUT PO KE SYSTEM** — 35 baris × 1 kolom
3. **LAPORAN PO HARIAN** — 16 baris × 19 kolom
4. **DATA OUTSTANDING** — 26 baris × 36 kolom
5. **INVPL DAN SURAT JALAN** — 17 baris × 14 kolom
6. **DELIVERY LIST** — 18 baris × 24 kolom
7. **PI** — 0 baris × 0 kolom
8. **CUSTOMER INFO** — 14 baris × 3 kolom
9. **OUTSTANDING INVOICE** — 40 baris × 2 kolom

---

## Ringkasan isi

### SOP

**Teks / poin (urutan kemunculan, unik):**

- Harapan di sistem baru karena tidak ada print out rekap laporan maka ppic bisa langsung akses po tersebut di sistem

### INPUT PO KE SYSTEM

**Teks / poin (urutan kemunculan, unik):**

- 1. INPUT PO DI SISTEM YANG LAMA
- Sistem yang baru tolong untuk di lengkapi fitur seperti ini
- Request marketing
- 1. Harga tolong muncul secara otomatis dan tidak bisa di edit
- 2. Bisa copy paste untuk PO dengan item yang sama
- 3. Pengisian emboss tolong tidak diwajibkan karena ada beberapa material yang tidak wajib mengisi nama emboss
- 4. Nama material tolong di otomatiskan tapi ada kolom yang bisa di edit, karena kadang ada material subcont material baru yang belum pernah kita produksi sebelumnya
- 5. Apabila ada revisi warna, qty, thickness, ETD, color swatch,backing tolong agar ada history nya agar ppic mengetahui
- 6. Nomor Lot untuk material PU coated, Subcont, Return, Claim dan Suede diharapkan bisa dibedakan intialnya untuk memudahkan dalam pengecekan

### LAPORAN PO HARIAN

**Teks / poin (urutan kemunculan, unik):**

- LAPORAN PO HARIAN MARKETING
- Request marketing
- Next kami tidak akan print out contract review manually seperti ini, konfirmasi PO akan di confirm bu ona melalui akun system bu ona, dan ppic bisa kasih ETD langsung di sistem untuk saving paper.
- Tolong dimunculkan history revisian PO nya
- Setiap hari ada laporan received PO di grup WA, tolong dimunculkan di dashboard total qty terima PO setiap harinya
- Laporan harian PO dibedakan berdasarkan kategori nya yaitu sbb
- Revisi ….
- Production Order
- Sample
- Claim
- Subcont
- Return
- Repro/Short Lead Time PO

### DATA OUTSTANDING

**File CSV:** `MARKETING_extract/DATA_OUTSTANDING.csv` (22 baris data)

```
                  DATE    THI ORDER              CUSTOMER NAME BRAND ORDER TYPE                                       NO PO MATERIAL NAME THICKNESS  EMBOSS SOFTNESS TYPE                             COLOR SOFTNESS  QTY (S/F)\n  PRICE\n     COLOR S/W BACKING        MODEL      ARTICLE   RTA  REPLY ETD  STOCK WH  BALANCE          SYSTEM NO  REMARK    1st          Unnamed: 25  2nd Unnamed: 27  3rd Unnamed: 29  4th Unnamed: 31  5th Unnamed: 33  6th Unnamed: 35
0                  NaN          NaN                        NaN   NaN        NaN                                         NaN           NaN       NaN     NaN           NaN                               NaN      NaN          NaN      NaN           NaN      NaN         NaN          NaN   NaN        NaT       NaN      NaN                NaN     NaN    Qty                 Date  Qty        Date  Qty        Date  Qty        Date  Qty        Date  Qty        Date
1  2026-02-26 00:00:00   PS26022601                    GLOSTAR   N.B       PROD                                  4004365389   Split Suede   1.2-1.4     NaN          SOFT  BLACK CEMENT (008-24-00)          2.0-3.0        253.0     1.33  COLOR WINDOW        -         NaN          NaN  3/30 2026-03-30      35.8      0.0  MYCGS009260226001     NaN  217.2  2026-04-06 00:00:00  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN
2  2026-02-26 00:00:00   PS26022602                   METRO NB   N.B       PROD                    N2026025361NB/140151104C   Split Suede   1.4-1.6     NaN          SOFT    BLACK CEMENT (008-24-00)        2.0-3.0        810.0     1.33  COLOR WINDOW        -         NaN  UN480HGB-2E  3/30 2026-03-30     810.0      0.0  MYCMP033260226001     NaN    NaN                  NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN
3  2026-03-16 00:00:00    S26031601  PT SUKSES ABADI INDONESIA   N.B     SAMPLE  SAIDEV-26-0001113 ERP 0657/PO-SAI/III/2026   Split Suede   1.2-1.4     NaN          SOFT       BLACK (145-17-00)            2.0-3.0         30.0     1.33  COLOR WINDOW        -         NaN      W51580S   4/6 2026-04-06       NaN     30.0  SYCSD047260316003     NaN    NaN                  NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN
4  2026-04-02 00:00:00    S26040201  PT SUKSES ABADI INDONESIA   N.B     SAMPLE   SAIDEV-26-0001339 ERP 0045/PO-SAI/IV/2026   Split Suede   1.2-1.4     NaN          SOFT             BLACK (145-17-00)      2.0-3.0         60.0     1.33  COLOR WINDOW        -         NaN     G880R5X4  4/14 2026-04-14       NaN     60.0  SYCSD047260402001     NaN    NaN                  NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN
5  2026-03-13 00:00:00   PS26031304                   METRO NB   N.B      REPRO               N2026036955NBREPRO/135010034C   Split Suede   1.2-1.4     NaN          SOFT         BLACK (145-17-00)          2.0-3.0        225.0     1.33  COLOR WINDOW      NaN  U90604U4-D          NaN   4/1 2026-04-01     225.6     -0.6  MYCMP033260313002     NaN    NaN                  NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN
6  2026-03-17 00:00:00   PS26031707                   METRO NB   N.B      REPRO               N2026037261NBREPRO/135010233C   Split Suede   1.2-1.4     NaN          SOFT  NEW STONEWARE (034-62-06)         2.0-3.0        100.0     1.33  COLOR WINDOW        -         NaN          NaN  3/31 2026-03-31       NaN    100.0  MYCMP033260317001     NaN    NaN                  NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN
7  2026-03-31 00:00:00  PSC26033103             ULTIMATE NOBLE   N.B      CLAIM                 U2026010722NBFOC/135010132C   Split Suede   1.2-1.4     NaN          SOFT      SLATE GREY (000-55-00)        2.0-3.0        220.0     1.33  COLOR WINDOW        -         NaN          NaN  4/14 2026-04-14       NaN    220.0  BYCMP034260331001     NaN    NaN                  NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN  NaN         NaN
```

### INVPL DAN SURAT JALAN

**Teks / poin (urutan kemunculan, unik):**

- Request marketing untuk invoice packinglist
- Hilangkan PO nomor diatas dan tambahkan fitur PO Number di sebelah kiri Item material
- Untuk invoice customer export tolong tambahkan Bill To
- Untuk invoice customer export tambahkan kode material exim di sebelah kanan Item
- Keterangan lainnya yang ada di invoice ini harus muncul di sistem baru
- Munculkan fitur untuk download invpl secara PDF dan excel
- Request marketing untuk surat jalan
- Surat jalan tidak wajib di print out karena export tidak menggunakan surat jalan
- munculkan fitur untuk download sj secara PDF

### DELIVERY LIST

**File CSV:** `MARKETING_extract/DELIVERY_LIST.csv` (14 baris data)

```
            NO SJ            TGL KIRIM                                  FACTORY NAME      SYSTEM NO    PO DATE          PO NUMBER             LOT NO THICKNESS                  COLOR           TYPE                  MATERIAL NAME  QTY PO  UNIT PRICE  ROLL    PCS      SF   COLOR STD         EMBOSS   BUYER       STYLE                 MODEL       INV NUMBER  PI_NO                                REMARK
0  THI-C260318003  2026-04-08 00:00:00  PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA    PSC26030203 2026-03-02  POB/26/02/AD00447  BYCPH001260302001   1.4-1.6  CORE BLACK (A0QM)                 反毛  SPLIT SUEDE (MAP-SPLIT SUEDE)   200.0        1.22   2.0    9.0   205.2     CW 1030            NaN  ADIDAS         NaN                   NaN  THIN-C260318003    NaN  FOR REPLACEMENT CLAIM ADIDAS YIHFULL
1  THI-M260318013  2026-04-08 00:00:00  PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA     PS26030206 2026-03-02  POB/26/02/AD00442  MYCPH001260303001   1.4-1.6    CORE BLACK (A0QM)               反毛  SPLIT SUEDE (MAP-SPLIT SUEDE)   220.0        1.22   2.0   12.0   222.7     CW 1030            NaN  ADIDAS         NaN                   NaN  THIN-M260318013    NaN                                   NaN
2  THI-M260408001  2026-04-08 00:00:00  PT. PEI HAI INTERNATIONAL WIRATAMA INDONESIA     PS26030205 2026-03-02  POB/26/02/AD00443  MYCPH001260302001   1.4-1.6  CORE BLACK (A0QM)                 反毛  SPLIT SUEDE (MAP-SPLIT SUEDE)  3435.5        1.22  23.0  179.0  3436.5     CW 1030            NaN  ADIDAS         NaN                   NaN  THIN-M260408001    NaN                                   NaN
3  THI-M260407013  2026-04-08 00:00:00                      PT. CHANGSHIN REKSA JAYA  THIPM26022302 2026-02-23         4501067073  PUMCS005260223001   1.2-1.4       ANTHRACITE (06F)  PU COATED(PU)                VIRGIN HYDRO PU  1910.0        1.21  11.0  118.0  1844.6  FOLLOW CMP  AR-138 M / 圓材    NIKE  IQ0098-104  AIR MAX 90 MESH (GS)  THIN-M260407013    NaN                                   NaN
4  THI-M260407013  2026-04-08 00:00:00                      PT. CHANGSHIN REKSA JAYA  THIPM26030516 2026-03-05         4501072445  PUMCS005260305001   1.2-1.4       ANTHRACITE (06F)  PU COATED(PU)                VIRGIN HYDRO PU  1025.0        1.21   6.0   67.0  1025.5  FOLLOW CMP  AR-138 M / 圓材    NIKE  IQ0098-104  AIR MAX 90 MESH (GS)  THIN-M260407013    NaN                                   NaN
5  THI-M260407013  2026-04-08 00:00:00                      PT. CHANGSHIN REKSA JAYA  THIPM26030516 2026-03-05         4501072445  PUMCS005260305002   1.2-1.4       ANTHRACITE (06F)  PU COATED(PU)                VIRGIN HYDRO PU   529.0        1.21   2.0   14.0   205.8  FOLLOW CMP  AR-138 M / 圓材    NIKE  IQ0098-104  AIR MAX 90 MESH (GS)  THIN-M260407013    NaN                                   NaN
```

### PI

_Sheet kosong._

### CUSTOMER INFO

**Teks / poin (urutan kemunculan, unik):**

- Request Marketing
- Tambahkan list ini
- Jabatan
- NPWP
- No Skep KB
- Kode Kantor
- No Tlp
- Alamat email
- Alamat Bill To
- Term of Payment
- Kode customer tolong disamakan dengan sistem yang lama
- Alamat email untuk kirim outstanding payment secara otomatis dari sistem

### OUTSTANDING INVOICE

**Teks / poin (urutan kemunculan, unik):**

- REKAP OUTSTANDING INVOICE
- Request Marketing
- Tolong tambahkan filter jadi untuk PO nomor bisa dimunculkan dan bisa di hiden. Ketika PO number di hidden maka ini bisa untuk report secara ringkas hanya untuk nomor invoice, customer, qty, maturity (due date payment)
- Payment yang sudah lewat jatuh tempo secara otomatis di email dari sistem ke email yang ada di customer info
- Kolom faktur pajak, Faktur date, Tanda Terima, Received By dan received date, nopen dan no aju bisa di edit
- Munculkan dashboard untuk marketing yang handle invoice adalah invoice yang 1 minggu lagi due date tapi belum terbayarkan dan invoice yang sudah lewat pembayaran
- Setiap hari Rabu ada laporan invoice yang sudah jatuh tempo diharapkan bisa muncul di sistem untuk memudahkan laporan
- Contoh laporannya seperti ini :

