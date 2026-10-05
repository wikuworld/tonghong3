"""Import katalog Master Item Raw Material (.xls) ke master MRP.

Sheet katalog: KULIT, KIMIA, RELEASE PAPER, LAINNYA.
Sheet Page1 (ledger stok) diimpor lewat import_page1_stock_ledger().
"""
from __future__ import annotations

import os
import re
from typing import Any

DEFAULT_XLS_PATH = os.environ.get(
    "MRP_RAW_MATERIAL_XLS",
    "/app/data/Master Item Raw Material.xls",
)

NAME_ALIASES = {
    "MPE-001-0001": "PE Film (1.75M)",
}

THICKNESS_SUFFIX = {
    "102": "1.02",
    "112": "1.12",
    "123": "1.23",
    "124": "1.24",
    "126": "1.26",
    "134": "1.34",
    "135": "1.35",
    "140": "1.40",
    "146": "1.46",
    "12": "1.2",
}

_TH_END = re.compile(r"^(?P<body>.+?)\s+(?P<th>\d+(?:\.\d+)?)\s*$")
_TH_MM = re.compile(
    r"(?P<th>\d+(?:\.\d+)?)\s*MM\b",
    re.IGNORECASE,
)
_COLOR_TAIL = re.compile(r"\b(BLACK|WHITE|GREY|GRAY|BROWN|RED|BLUE|TAN)\s*$", re.IGNORECASE)


def normalize_satuan(raw: str | None, default: str = "pcs") -> str:
    s = (raw or "").strip()
    if not s:
        return default
    key = s.lower()
    mapping = {
        "kg": "kg",
        "sf": "sf",
        "m": "meter",
        "meter": "meter",
        "roll": "roll",
        "pcs": "pcs",
        "yard": "yard",
    }
    return mapping.get(key, key)


def _cell_str(val: Any) -> str:
    if val is None:
        return ""
    if isinstance(val, float) and val == int(val):
        return str(int(val))
    return str(val).strip()


def parse_kulit_thickness_warna(kode: str, nama: str) -> tuple[str | None, str | None]:
    nama = (nama or "").strip()
    thickness = None
    warna = None

    m = _TH_END.match(nama)
    if m:
        thickness = m.group("th")
        warna = m.group("body").strip()
    else:
        mm = _TH_MM.search(nama)
        if mm:
            thickness = mm.group("th")
            warna_m = _COLOR_TAIL.search(nama)
            warna = warna_m.group(1).upper() if warna_m else nama
        else:
            warna = nama or None

    if not thickness:
        suf = kode.rsplit("-", 1)[-1] if "-" in kode else ""
        thickness = THICKNESS_SUFFIX.get(suf)

    if thickness:
        # normalize 1.2 -> 1.2mm, 1.02 -> 1.02mm
        t = thickness
        if not t.lower().endswith("mm"):
            t = f"{t}mm"
        thickness = t

    if warna:
        warna = re.sub(r"\s+", " ", warna).strip()
        # strip trailing comma junk
        warna = warna.rstrip(",").strip()

    return thickness, warna


def read_catalog_sheets(path: str) -> dict[str, list[dict[str, str]]]:
    import xlrd

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    book = xlrd.open_workbook(path)
    wanted = {
        "KULIT": "kulit",
        "KIMIA": "kimia",
        "RELEASE PAPER": "rp",
        "LAINNYA": "material",
    }
    out: dict[str, list[dict[str, str]]] = {v: [] for v in wanted.values()}

    for sheet_name, key in wanted.items():
        if sheet_name not in book.sheet_names():
            continue
        sh = book.sheet_by_name(sheet_name)
        if sh.nrows < 2:
            continue
        headers = [_cell_str(sh.cell_value(0, c)).upper() for c in range(sh.ncols)]
        try:
            i_kode = headers.index("KODE")
            i_nama = headers.index("NAMA")
            i_sat = headers.index("SAT") if "SAT" in headers else None
        except ValueError as e:
            raise ValueError(f"Sheet {sheet_name}: kolom KODE/NAMA wajib") from e

        for r in range(1, sh.nrows):
            kode = _cell_str(sh.cell_value(r, i_kode))
            nama = _cell_str(sh.cell_value(r, i_nama))
            if not kode:
                continue
            nama = NAME_ALIASES.get(kode, nama)
            sat = _cell_str(sh.cell_value(r, i_sat)) if i_sat is not None else ""
            out[key].append({"kode": kode, "nama": nama, "sat": sat})

    return out


def _count() -> dict[str, int]:
    return {"inserted": 0, "updated": 0}


def import_raw_material_masters(conn, path: str | None = None) -> dict:
    """Upsert katalog HANYA ke ERP raw_materials (tanpa mirror MRP)."""
    from erp_raw_materials import ensure_erp_material

    xls_path = path or DEFAULT_XLS_PATH
    catalogs = read_catalog_sheets(xls_path)
    stats = {
        "kulit": _count(),
        "kimia": _count(),
        "rp": _count(),
        "material": _count(),
    }
    skipped: list[str] = []
    erp_map = {"kulit": 0, "kimia": 0, "rp": 0, "material": 0}

    for row in catalogs["kulit"]:
        kode, nama = row["kode"], row["nama"]
        if not nama:
            skipped.append(f"kulit:{kode}:nama kosong")
            continue
        eid = ensure_erp_material(code=kode, name=nama, material_type="kulit", unit="sqft")
        if eid:
            stats["kulit"]["inserted"] += 1
            erp_map["kulit"] += 1

    for row in catalogs["kimia"]:
        kode, nama = row["kode"], row["nama"]
        if not nama:
            skipped.append(f"kimia:{kode}:nama kosong")
            continue
        satuan = normalize_satuan(row["sat"], "kg")
        eid = ensure_erp_material(code=kode, name=nama, material_type="kimia", unit=satuan)
        if eid:
            stats["kimia"]["inserted"] += 1
            erp_map["kimia"] += 1

    for row in catalogs["rp"]:
        kode, nama = row["kode"], row["nama"]
        if not nama:
            skipped.append(f"rp:{kode}:nama kosong")
            continue
        satuan = normalize_satuan(row["sat"], "meter")
        eid = ensure_erp_material(code=kode, name=nama, material_type="rp", unit=satuan)
        if eid:
            stats["rp"]["inserted"] += 1
            erp_map["rp"] += 1

    for row in catalogs["material"]:
        kode, nama = row["kode"], row["nama"]
        if not nama:
            skipped.append(f"material:{kode}:nama kosong")
            continue
        satuan = normalize_satuan(row["sat"], "pcs")
        eid = ensure_erp_material(
            code=kode, name=nama, material_type="material_lain", unit=satuan
        )
        if eid:
            stats["material"]["inserted"] += 1
            erp_map["material"] += 1

    return {
        "ok": True,
        "source": xls_path,
        "kulit": stats["kulit"],
        "kimia": stats["kimia"],
        "rp": stats["rp"],
        "material": stats["material"],
        "erp_mapped": erp_map,
        "skipped": skipped,
        "totals": {
            "kulit": len(catalogs["kulit"]),
            "kimia": len(catalogs["kimia"]),
            "rp": len(catalogs["rp"]),
            "material": len(catalogs["material"]),
        },
        "note": "ERP-only: tidak menulis mirror master_* MRP",
    }



def _find_page1_sheet(book):
    for name in book.sheet_names():
        key = name.strip().upper().replace(" ", "")
        if key in {"PAGE1", "PAGE01", "PAG1"} or name.strip().upper().startswith("PAGE1"):
            return name
    for name in book.sheet_names():
        if "PAGE" in name.upper() and "1" in name:
            return name
    return None


def import_page1_stock_ledger(conn, path: str | None = None) -> dict[str, Any]:
    """Import opening stock dari sheet Page1 ke tbl_stok_kimia_in / tbl_stok_rp_in.

    Heuristik kolom: KODE/CODE + QTY/STOCK/QTY_SISA (+ optional JENIS/TYPE).
    """
    import xlrd
    from datetime import date as _date
    from app import ensure_extended_tables, generate_code, init_db_tables

    xls_path = path or DEFAULT_XLS_PATH
    if not os.path.isfile(xls_path):
        raise FileNotFoundError(f"File tidak ditemukan: {xls_path}")

    init_db_tables()
    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    book = xlrd.open_workbook(xls_path)
    sheet_name = _find_page1_sheet(book)
    if not sheet_name:
        cur.close()
        return {
            "ok": False,
            "detail": "Sheet Page1 tidak ditemukan",
            "sheets": list(book.sheet_names()),
        }

    sh = book.sheet_by_name(sheet_name)
    if sh.nrows < 2:
        cur.close()
        return {"ok": True, "sheet": sheet_name, "inserted": 0, "skipped": ["sheet kosong"]}

    headers = [_cell_str(sh.cell_value(0, c)).upper() for c in range(sh.ncols)]

    def _idx(*names):
        for n in names:
            if n in headers:
                return headers.index(n)
        return None

    i_kode = _idx("KODE", "CODE", "ITEM CODE", "KODE BARANG")
    i_qty = _idx("QTY", "STOCK", "QTY_SISA", "QTY SISA", "ON HAND", "BALANCE")
    i_jenis = _idx("JENIS", "TYPE", "CATEGORY", "TIPE")
    i_nama = _idx("NAMA", "NAME", "DESKRIPSI", "DESCRIPTION")
    if i_kode is None or i_qty is None:
        cur.close()
        raise ValueError(f"Sheet {sheet_name}: butuh kolom KODE dan QTY/STOCK (ada: {headers})")

    inserted = 0
    skipped: list[str] = []
    today = _date.today().isoformat()

    for r in range(1, sh.nrows):
        kode = _cell_str(sh.cell_value(r, i_kode))
        if not kode:
            continue
        try:
            qty = float(sh.cell_value(r, i_qty) or 0)
        except (TypeError, ValueError):
            skipped.append(f"{kode}:qty invalid")
            continue
        if qty <= 0:
            skipped.append(f"{kode}:qty<=0")
            continue
        jenis = _cell_str(sh.cell_value(r, i_jenis)).upper() if i_jenis is not None else ""
        nama = _cell_str(sh.cell_value(r, i_nama)) if i_nama is not None else ""

        from erp_raw_materials import fetch_material_by_code

        # Prefer explicit type; else match kode against ERP raw_materials
        target = None
        mat = None
        if "RP" in jenis or "RELEASE" in jenis:
            target = "rp"
            mat = fetch_material_by_code(kode, material_type="rp")
        elif "KIMIA" in jenis or "CHEM" in jenis:
            target = "kimia"
            mat = fetch_material_by_code(kode, material_type="kimia")
        else:
            mat = fetch_material_by_code(kode, material_type="kimia")
            if mat:
                target = "kimia"
            else:
                mat = fetch_material_by_code(kode, material_type="rp")
                if mat:
                    target = "rp"

        if target == "kimia" and mat:
            kode_internal = generate_code("BC-K")
            cur.execute(
                "INSERT INTO tbl_stok_kimia_in "
                "(kode_internal, kimia_id, erp_material_id, kode_material, nama_material, "
                "qty, qty_sisa, satuan, tanggal_in, gudang) "
                "VALUES (%s,NULL,%s,%s,%s,%s,%s,%s,%s,'utama')",
                (
                    kode_internal,
                    mat["id"],
                    mat.get("code"),
                    mat.get("name") or nama,
                    qty,
                    qty,
                    mat.get("unit") or "kg",
                    today,
                ),
            )
            inserted += 1
        elif target == "rp" and mat:
            kode_internal = generate_code("BC-R")
            cur.execute(
                "INSERT INTO tbl_stok_rp_in "
                "(kode_internal, rp_id, erp_material_id, kode_material, nama_material, "
                "meter_roll, qty_sisa, tanggal_in, gudang) "
                "VALUES (%s,NULL,%s,%s,%s,%s,%s,%s,'utama')",
                (
                    kode_internal,
                    mat["id"],
                    mat.get("code"),
                    mat.get("name") or nama,
                    qty,
                    qty,
                    today,
                ),
            )
            inserted += 1
        else:
            skipped.append(f"{kode}:tidak match kimia/rp ERP ({nama or jenis or '-'})")

    conn.commit()
    cur.close()
    return {
        "ok": True,
        "source": xls_path,
        "sheet": sheet_name,
        "inserted": inserted,
        "skipped": skipped[:100],
        "skipped_count": len(skipped),
    }
