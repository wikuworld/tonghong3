"""Identitas kulit pada label reject Gudang MOD."""

from __future__ import annotations


def _label_text(value) -> str:
    return str(value or "").strip()


def _yl_spek_for_label(cur, kode_palet: str, kode_yl: str) -> tuple[str, str]:
    """Thickness dan warna kulit dari stok YL, atau movement bila baris stok sudah hilang."""
    kode_palet = _label_text(kode_palet)
    kode_yl = _label_text(kode_yl)
    if not kode_palet or not kode_yl:
        return "", ""
    cur.execute(
        "SELECT thickness, warna FROM tbl_yl WHERE kode_palet=%s AND kode_yl=%s LIMIT 1",
        (kode_palet, kode_yl),
    )
    row = cur.fetchone() or {}
    thickness = _label_text(row.get("thickness"))
    warna = _label_text(row.get("warna"))
    if thickness or warna:
        return thickness, warna
    cur.execute(
        "SELECT thickness, warna FROM tbl_yl_movement "
        "WHERE kode_palet=%s AND kode_yl=%s "
        "ORDER BY id DESC LIMIT 1",
        (kode_palet, kode_yl),
    )
    hist = cur.fetchone() or {}
    return _label_text(hist.get("thickness")), _label_text(hist.get("warna"))


def _mod_label_identity(cur, row: dict) -> dict:
    """Nama material, warna backing, dan thickness kulit yang dipakai sebelum reject."""
    has_rencana = row.get("rencana_item_id") not in (None, "", 0)
    material = _label_text(row.get("rencana_material_name"))
    thickness = _label_text(row.get("rencana_thickness"))
    backer = _label_text(row.get("rencana_backer"))
    if not has_rencana:
        yl_thickness, yl_warna = _yl_spek_for_label(
            cur, row.get("kode_palet"), row.get("kode_yl")
        )
        if not thickness:
            thickness = yl_thickness
        if not backer:
            backer = yl_warna
    return {
        "material_name": material,
        "thickness": thickness,
        "backer": backer,
    }
