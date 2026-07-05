# Dokumentasi referensi ERP

Folder ini di-mount read-only ke backend Docker (`/app/dokumentasi`).

## Master Item (PU, Suede, Subcont)

Letakkan file referensi di subfolder `master-items/`:

| File sumber | Nama di repo |
|-------------|--------------|
| `Sheet1-Table_1.csv` | `master-items/Sheet1-Table_1.csv` |
| `PU, SUEDE-Table_1.csv` | `master-items/PU_SUEDE-Table_1.csv` |
| `Master List Item PU, Suede, Subcont.xlsx` | `master-items/Master_List_Item_PU_Suede_Subcont.xlsx` |

## Upload dari Mac (contoh)

```bash
scp ~/Downloads/Sheet1-Table_1.csv developer@10.227.82.65:/home/developer/project/dokumentasi/master-items/
scp ~/Downloads/PU,\ SUEDE-Table_1.csv developer@10.227.82.65:/home/developer/project/dokumentasi/master-items/PU_SUEDE-Table_1.csv
scp ~/Downloads/Master\ List\ Item\ PU,\ Suede,\ Subcont.xlsx developer@10.227.82.65:/home/developer/project/dokumentasi/master-items/Master_List_Item_PU_Suede_Subcont.xlsx
```

Atau drag-and-drop ke folder `dokumentasi/master-items/` lewat Cursor / SFTP.
