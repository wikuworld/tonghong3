"""Field komersial penerimaan material: supplier, harga, bentuk, skala."""

from __future__ import annotations


def parse_optional_text(value, *, limit: int = 255, label: str = "teks") -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    text = str(value).strip()
    if not text:
        return None, None
    if len(text) > limit:
        return None, f"{label} maksimal {limit} karakter"
    return text, None


def parse_unit_price(value) -> tuple[float | None, str | None]:
    if value is None or value == "":
        return None, None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None, "harga harus angka"
    if number < 0:
        return None, "harga tidak boleh negatif"
    return round(number, 4), None


def parse_erp_material_id(value) -> int | None:
    if value is None or value == "":
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def commercial_from_body(body: dict | None) -> tuple[dict | None, str | None]:
    body = body or {}
    supplier, err = parse_optional_text(body.get("supplier_name"), limit=255, label="nama supplier")
    if err:
        return None, err
    price, err = parse_unit_price(body.get("unit_price"))
    if err:
        return None, err
    return {"supplier_name": supplier, "unit_price": price}, None


YL_UPSERT_SQL = (
    "INSERT INTO tbl_yl (kode_yl, kode_palet, thickness, warna, qty, "
    "supplier_name, unit_price, bentuk_kulit, skala, erp_material_id) "
    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
    "ON DUPLICATE KEY UPDATE thickness=%s, warna=%s, qty=%s, "
    "supplier_name=%s, unit_price=%s, bentuk_kulit=%s, skala=%s, erp_material_id=%s"
)


def yl_upsert_params(item: dict, *, kode_palet: str, supplier_name: str | None) -> tuple:
    price, err = parse_unit_price(item.get("unit_price"))
    if err:
        raise ValueError(err)
    bentuk, err = parse_optional_text(item.get("bentuk_kulit"), limit=120, label="bentuk kulit")
    if err:
        raise ValueError(err)
    skala, err = parse_optional_text(item.get("skala"), limit=120, label="skala")
    if err:
        raise ValueError(err)
    line_supplier, err = parse_optional_text(
        item.get("supplier_name") if item.get("supplier_name") not in (None, "") else supplier_name,
        limit=255,
        label="nama supplier",
    )
    if err:
        raise ValueError(err)
    thickness = (item.get("thickness") or "").strip() or None
    warna = (item.get("warna") or "").strip() or None
    qty = float(item.get("qty") or 0)
    erp_id = parse_erp_material_id(item.get("erp_material_id"))
    written = (
        item.get("kode_yl"),
        kode_palet,
        thickness,
        warna,
        qty,
        line_supplier,
        price,
        bentuk,
        skala,
        erp_id,
    )
    return written + (thickness, warna, qty, line_supplier, price, bentuk, skala, erp_id)


KIMIA_IN_SQL = (
    "INSERT INTO tbl_stok_kimia_in "
    "(kode_internal, kimia_id, erp_material_id, kode_material, nama_material, "
    "qty, qty_sisa, satuan, jumlah_kemasan, tanggal_in, expired_date, gudang, lot_number, "
    "supplier_name, unit_price) "
    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
)

RP_IN_SQL = (
    "INSERT INTO tbl_stok_rp_in "
    "(kode_internal, rp_id, erp_material_id, kode_material, nama_material, "
    "meter_roll, qty_sisa, tanggal_in, gudang, lot_number, supplier_name, unit_price) "
    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
)

MATERIAL_LAIN_IN_SQL = (
    "INSERT INTO tbl_stok_material_lain_in "
    "(kode_internal, material_id, erp_material_id, kode_material, nama_material, "
    "qty, qty_sisa, satuan, tanggal_in, supplier_name, unit_price) "
    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
)
