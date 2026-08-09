"""Import katalog Master Item Raw Material (.xls) ke master MRP.

Sheet yang diimpor: KULIT, KIMIA, RELEASE PAPER, LAINNYA.
Sheet Page1 (ledger stok) diabaikan.
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


def import_raw_material_masters(conn, path: str | None = None) -> dict[str, Any]:
    """Upsert katalog ke master_*; tidak menghapus baris yang tidak ada di file."""
    from app import ensure_extended_tables, init_db_tables

    xls_path = path or DEFAULT_XLS_PATH
    catalogs = read_catalog_sheets(xls_path)

    # Pastikan kolom master kulit/kimia/rp lengkap (seed vs schema baru).
    init_db_tables()

    cur = conn.cursor(dictionary=True)
    ensure_extended_tables(cur)
    conn.commit()

    stats = {
        "kulit": _count(),
        "kimia": _count(),
        "rp": _count(),
        "material": _count(),
    }
    skipped: list[str] = []

    for row in catalogs["kulit"]:
        kode, nama = row["kode"], row["nama"]
        if not nama:
            skipped.append(f"kulit:{kode}:nama kosong")
            continue
        thickness, warna = parse_kulit_thickness_warna(kode, nama)
        cur.execute("SELECT id FROM master_kulit WHERE kode_kulit=%s", (kode,))
        existing = cur.fetchone()
        if existing:
            cur.execute(
                "UPDATE master_kulit SET nama_kulit=%s, thickness=%s, warna=%s WHERE id=%s",
                (nama, thickness, warna, existing["id"]),
            )
            stats["kulit"]["updated"] += 1
        else:
            cur.execute(
                "INSERT INTO master_kulit (kode_kulit, nama_kulit, thickness, warna) "
                "VALUES (%s,%s,%s,%s)",
                (kode, nama, thickness, warna),
            )
            stats["kulit"]["inserted"] += 1

    for row in catalogs["kimia"]:
        kode, nama = row["kode"], row["nama"]
        if not nama:
            skipped.append(f"kimia:{kode}:nama kosong")
            continue
        satuan = normalize_satuan(row["sat"], "kg")
        cur.execute("SELECT id FROM master_kimia WHERE kode_barang=%s OR kode_kimia=%s", (kode, kode))
        existing = cur.fetchone()
        if existing:
            cur.execute(
                "UPDATE master_kimia SET nama_barang=%s, nama_kimia=%s, satuan=%s, "
                "kode_kimia=%s, kode_barang=%s WHERE id=%s",
                (nama, nama, satuan, kode, kode, existing["id"]),
            )
            stats["kimia"]["updated"] += 1
        else:
            cur.execute(
                "INSERT INTO master_kimia (kode_barang, nama_barang, satuan, expired_days, "
                "kode_kimia, nama_kimia) VALUES (%s,%s,%s,365,%s,%s)",
                (kode, nama, satuan, kode, nama),
            )
            stats["kimia"]["inserted"] += 1

    for row in catalogs["rp"]:
        kode, nama = row["kode"], row["nama"]
        if not nama:
            skipped.append(f"rp:{kode}:nama kosong")
            continue
        satuan = normalize_satuan(row["sat"], "meter")
        cur.execute("SELECT id FROM master_rp WHERE kode_rp=%s", (kode,))
        existing = cur.fetchone()
        if existing:
            cur.execute(
                "UPDATE master_rp SET nama_jenis=%s, nama_rp=%s, satuan=%s WHERE id=%s",
                (nama, nama, satuan, existing["id"]),
            )
            stats["rp"]["updated"] += 1
        else:
            cur.execute(
                "INSERT INTO master_rp (nama_jenis, satuan, kode_rp, nama_rp) VALUES (%s,%s,%s,%s)",
                (nama, satuan, kode, nama),
            )
            stats["rp"]["inserted"] += 1

    for row in catalogs["material"]:
        kode, nama = row["kode"], row["nama"]
        if not nama:
            skipped.append(f"material:{kode}:nama kosong")
            continue
        satuan = normalize_satuan(row["sat"], "pcs")
        cur.execute("SELECT id FROM master_material_lain WHERE kode_material=%s", (kode,))
        existing = cur.fetchone()
        if existing:
            cur.execute(
                "UPDATE master_material_lain SET nama_material=%s, satuan=%s WHERE id=%s",
                (nama, satuan, existing["id"]),
            )
            stats["material"]["updated"] += 1
        else:
            cur.execute(
                "INSERT INTO master_material_lain (kode_material, nama_material, satuan) "
                "VALUES (%s,%s,%s)",
                (kode, nama, satuan),
            )
            stats["material"]["inserted"] += 1

    conn.commit()
    cur.close()

    return {
        "ok": True,
        "source": xls_path,
        "kulit": stats["kulit"],
        "kimia": stats["kimia"],
        "rp": stats["rp"],
        "material": stats["material"],
        "skipped": skipped,
        "totals": {
            "kulit": len(catalogs["kulit"]),
            "kimia": len(catalogs["kimia"]),
            "rp": len(catalogs["rp"]),
            "material": len(catalogs["material"]),
        },
    }
