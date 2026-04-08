#!/usr/bin/env python3
"""
Bangun ulang CSV master di Master_Data_extracted agar header = nama field API/DB (snake_case).
Jalankan dari repo root: python3 scripts/build_master_data_csv.py
"""

from __future__ import annotations

import csv
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT.parent / "Master_Data_extracted"
OUT = ROOT.parent / "Master_Data_extracted"


def q4(x: str | float | Decimal | None) -> str:
    if x is None or x == "" or x == "-":
        return ""
    try:
        d = Decimal(str(x)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        return format(d.normalize(), "f")
    except Exception:
        return str(x).strip()


def build_01() -> None:
    p = OUT / "01_Master_Item.csv"
    rows = []
    with open(SRC / "01_Master_Item.csv", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            code = (row.get("KODE BARANG") or row.get("item_code") or "").strip()
            if not code:
                continue
            rows.append(
                {
                    "item_code": code,
                    "thickness_mm": (row.get("THICKNESS") or row.get("thickness_mm") or "").strip(),
                    "material_name": (row.get("MATERIAL NAME") or row.get("material_name") or "").strip(),
                    "emboss": (row.get("EMBOSS") or row.get("emboss") or "").strip(),
                    "color": (row.get("COLOR") or row.get("color") or "").strip(),
                    "category": (row.get("CATEGORY") or row.get("category") or "").strip(),
                }
            )
    fields = ["item_code", "thickness_mm", "material_name", "emboss", "color", "category"]
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("Wrote", p, len(rows), "rows")


def build_02() -> None:
    raw_path = SRC / "02_Master_Harga.csv"
    with open(raw_path, newline="", encoding="utf-8") as f:
        first = f.readline()
        if "line_no" in first and "price_white_usd" in first:
            print("02_Master_Harga.csv already normalized, skip")
            return
        f.seek(0)
        lines = list(csv.reader(f))
    # Baris data mulai indeks 3 (setelah header + 2 baris subjudul)
    data_rows = []
    for line in lines[3:]:
        if not any(c.strip() for c in line):
            continue
        data_rows.append(line)

    out_rows: list[dict[str, str]] = []
    prev_cat = prev_type = prev_name = ""
    line_no = 0
    for line in data_rows:
        while len(line) < 11:
            line.append("")
        no_, cat, mtype, mname, thick, pw, pb, pc, pm, remark = (
            line[0],
            line[1],
            line[2],
            line[3],
            line[4],
            line[5],
            line[6],
            line[7],
            line[8],
            line[9],
        )
        if cat.strip():
            prev_cat = cat.strip()
        if mtype.strip():
            prev_type = mtype.strip()
        if mname.strip():
            prev_name = mname.strip()
        line_no += 1
        tier = ""
        rlow = (remark or "").lower()
        if "common" in rlow:
            tier = "Common"
        elif "special" in rlow:
            tier = "Special"
        out_rows.append(
            {
                "line_no": str(line_no),
                "material_category": prev_cat,
                "material_type": prev_type,
                "material_name": prev_name,
                "thickness_range": (thick or "").strip(),
                "price_white_usd": q4(pw),
                "price_black_usd": q4(pb),
                "price_color_usd": q4(pc),
                "price_metallic_usd": q4(pm) if str(pm).strip() != "-" else "",
                "remark": (remark or "").strip(),
                "price_tier": tier,
            }
        )

    fields = [
        "line_no",
        "material_category",
        "material_type",
        "material_name",
        "thickness_range",
        "price_white_usd",
        "price_black_usd",
        "price_color_usd",
        "price_metallic_usd",
        "remark",
        "price_tier",
    ]
    outp = OUT / "02_Master_Harga.csv"
    with open(outp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)
    print("Wrote", outp, len(out_rows), "rows")


def build_03() -> None:
    p = SRC / "03_Master_Data_Marketing.csv"
    with open(p, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if rows and rows[0] and rows[0][0] == "marketing_excel_date_serial":
        print("03_Master_Data_Marketing.csv already normalized, skip")
        return
    if len(rows) < 4:
        return
    header = [c.strip().replace("\n", "") for c in rows[1]]
    data = rows[3:]

    fieldnames = [
        "marketing_excel_date_serial",
        "thi_line_ref",
        "customer_name_snapshot",
        "brand_name_snapshot",
        "order_type_label",
        "po_customer_ref",
        "material_name",
        "thickness_text",
        "emboss",
        "vir_softness_type",
        "color",
        "softness",
        "quantity_order",
        "unit_price",
        "color_reference",
        "backing",
        "model",
        "style_article",
        "rtd_text",
        "etd_excel_serial",
        "stock_wh_qty",
        "balance_qty",
        "system_reference",
        "detail_remark",
    ]
    for i in range(1, 13):
        fieldnames.extend([f"delivery_{i}_qty", f"delivery_{i}_date"])

    outp = OUT / "03_Master_Data_Marketing.csv"
    with open(outp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in data:
            if not row or not any(c.strip() for c in row[:10]):
                continue
            while len(row) < 48:
                row.append("")
            d = {
                "marketing_excel_date_serial": row[0].strip(),
                "thi_line_ref": row[1].strip(),
                "customer_name_snapshot": row[2].strip(),
                "brand_name_snapshot": row[3].strip(),
                "order_type_label": row[4].strip(),
                "po_customer_ref": row[5].strip(),
                "material_name": row[6].strip(),
                "thickness_text": row[7].strip(),
                "emboss": row[8].strip(),
                "vir_softness_type": row[9].strip(),
                "color": row[10].strip(),
                "softness": row[11].strip(),
                "quantity_order": row[12].strip(),
                "unit_price": q4(row[13]) if row[13] else "",
                "color_reference": row[14].strip(),
                "backing": row[15].strip(),
                "model": row[16].strip(),
                "style_article": row[17].strip(),
                "rtd_text": row[18].strip(),
                "etd_excel_serial": row[19].strip(),
                "stock_wh_qty": row[20].strip(),
                "balance_qty": row[21].strip(),
                "system_reference": row[22].strip(),
                "detail_remark": row[23].strip(),
            }
            # delivery pairs cols 24..47
            for n in range(12):
                qi, di = 24 + n * 2, 25 + n * 2
                d[f"delivery_{n+1}_qty"] = row[qi].strip() if qi < len(row) else ""
                d[f"delivery_{n+1}_date"] = row[di].strip() if di < len(row) else ""
            w.writerow(d)
    print("Wrote", outp)


def main() -> None:
    if not SRC.exists():
        print("Missing", SRC)
        return
    build_01()
    build_02()
    build_03()
    readme = OUT / "README.md"
    readme.write_text(
        """# Master Data CSV (selaras Tonghong API)

Header memakai **nama field** seperti di tabel/model backend (`snake_case`).

| File | Tabel / pemakaian |
|------|-------------------|
| `01_Master_Item.csv` | `master_items` — FG: `item_code`, `thickness_mm`, `material_name`, `emboss`, `color`, `category` |
| `02_Master_Harga.csv` | `master_prices` — matrix harga: `line_no`, kategori/tipe/nama material, `thickness_range`, harga USD per kolom warna, `remark`, `price_tier` |
| `03_Master_Data_Marketing.csv` | `po_headers` + `po_details` + `po_detail_deliveries` — satu baris = satu baris SO + jadwal kirim 1–12 |

Impor: `cd Tonghong/backend && PYTHONPATH=. python scripts/import_master_data.py`  
Docker: mount CSV ke `/csv` dan set `MASTER_CSV_DIR=/csv`.

""",
        encoding="utf-8",
    )
    print("Updated", readme)


if __name__ == "__main__":
    main()
