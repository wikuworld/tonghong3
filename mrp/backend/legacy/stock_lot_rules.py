"""Aturan edit/hapus lot stok kimia, RP, dan material lain."""

EPS = 0.001


def round3(value) -> float:
    return round(float(value), 3)


def _date_text(value) -> str:
    if value is None or value == "":
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()[:10]
    return str(value)[:10]


def _text(value) -> str:
    return str(value or "").strip()


def parse_positive_qty(raw, label="qty"):
    try:
        qty = round3(raw)
    except (TypeError, ValueError):
        return None, f"{label} harus angka"
    if qty <= 0:
        return None, f"{label} harus > 0"
    return qty, None


def parse_date_text(raw, *, required=True, label="tanggal"):
    text = _date_text(raw)
    if not text:
        if required:
            return None, f"{label} wajib"
        return "", None
    try:
        from datetime import date

        date.fromisoformat(text)
    except ValueError:
        return None, f"{label} tidak valid"
    return text, None


def booked_issued(qty, qty_sisa) -> float:
    return round3(float(qty) - float(qty_sisa))


def totals_mismatch(qty, qty_sisa, issued) -> bool:
    return abs(booked_issued(qty, qty_sisa) - round3(issued)) > EPS


def parse_kemasan(raw):
    if raw in (None, ""):
        return None, None
    try:
        number = float(raw)
    except (TypeError, ValueError):
        return None, "jumlah kemasan harus angka"
    if not number.is_integer() or number < 0:
        return None, "jumlah kemasan harus bilangan bulat >= 0"
    return int(number), None


def validate_lot_update(
    *,
    qty_new,
    issued,
    qty_book,
    qty_sisa_book,
    out_count,
    locked_changed,
    kemasan_new=None,
    kemasan_issued=0,
    satuan=None,
    lot_number=None,
    check_satuan=False,
    check_lot=False,
    check_kemasan=False,
):
    if totals_mismatch(qty_book, qty_sisa_book, issued):
        return "Qty lot tidak cocok dengan jumlah keluar. Data tidak diubah."
    qty, err = parse_positive_qty(qty_new)
    if err:
        return err
    if qty + EPS < round3(issued):
        return "Qty baru lebih kecil dari jumlah yang sudah keluar"
    if int(out_count or 0) > 0 and locked_changed:
        return "Setelah ada keluar, hanya qty yang boleh diubah"
    if check_kemasan and kemasan_new is not None and kemasan_new < int(kemasan_issued or 0):
        return "Jumlah kemasan lebih kecil dari kemasan yang sudah keluar"
    if check_satuan:
        unit = _text(satuan)
        if not unit or len(unit) > 20:
            return "Satuan wajib, maksimal 20 karakter"
    if check_lot and len(_text(lot_number)) > 100:
        return "Nomor lot maksimal 100 karakter"
    return None


def validate_lot_delete(*, out_count, gudang, has_sisa_note, has_usage, block_lapangan=True):
    if int(out_count or 0) > 0:
        return "Lot sudah pernah keluar. Tidak bisa dihapus."
    if block_lapangan and _text(gudang).lower() == "lapangan":
        return "Lot gudang lapangan tidak bisa dihapus."
    if has_sisa_note:
        return "Lot punya catatan sisa. Tidak bisa dihapus."
    if has_usage:
        return "Lot sudah dipakai pada pemakaian. Tidak bisa dihapus."
    return None
