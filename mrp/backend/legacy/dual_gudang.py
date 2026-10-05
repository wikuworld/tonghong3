"""Dual warehouse helpers: utama | lapangan (legacy kimia|mixing → utama|lapangan)."""

from __future__ import annotations

GUDANG_UTAMA = "utama"
GUDANG_LAPANGAN = "lapangan"
LEGACY_UTAMA = ("kimia", "utama", "")
LEGACY_LAPANGAN = ("mixing", "lapangan")


def normalize_gudang(value, default: str = GUDANG_UTAMA) -> str:
    """Map legacy/current warehouse labels to utama|lapangan."""
    v = (value if value is not None else "").strip().lower()
    if v in LEGACY_LAPANGAN:
        return GUDANG_LAPANGAN
    if v in LEGACY_UTAMA:
        return GUDANG_UTAMA
    if v in (GUDANG_UTAMA, GUDANG_LAPANGAN):
        return v
    return default if default in (GUDANG_UTAMA, GUDANG_LAPANGAN) else GUDANG_UTAMA


def parse_gudang_filter(raw) -> str | None:
    """Return utama|lapangan from query/body, or None if absent/invalid."""
    if raw is None:
        return None
    v = str(raw).strip().lower()
    if not v or v in ("all", "*", "any"):
        return None
    return normalize_gudang(v)


def is_utama_to_lapangan_out(*, from_gudang: str, tujuan: str) -> bool:
    """OUT dari gudang utama dengan tujuan lapangan → transfer ke gudang lapangan."""
    return (
        from_gudang == GUDANG_UTAMA
        and (tujuan or "").strip().lower() in ("lapangan", "mixing")
    )


def should_spawn_lapangan_transfer_lot(
    *, from_gudang: str, tujuan: str, new_sisa: float = 0
) -> bool:
    """Alias backward-compat — transfer lapangan tidak bergantung sisa di utama."""
    return is_utama_to_lapangan_out(from_gudang=from_gudang, tujuan=tujuan)


def gudang_match_sql(column: str, gudang: str) -> tuple[str, list]:
    """SQL predicate + params for canonical gudang, including legacy kimia/mixing."""
    g = normalize_gudang(gudang)
    col = column.strip() or "gudang"
    if g == GUDANG_LAPANGAN:
        return f"{col} IN (%s, %s)", [GUDANG_LAPANGAN, "mixing"]
    return (
        f"({col} IN (%s, %s) OR {col} IS NULL OR {col} = '')",
        [GUDANG_UTAMA, "kimia"],
    )


def _col_names(cur, table: str) -> set[str]:
    try:
        cur.execute(f"SHOW COLUMNS FROM {table}")
    except Exception:
        return set()
    rows = cur.fetchall() or []
    if rows and isinstance(rows[0], dict):
        return {r["Field"] for r in rows}
    return {r[0] for r in rows}


def _col_type(cur, table: str, column: str) -> str:
    try:
        cur.execute(f"SHOW COLUMNS FROM {table} LIKE %s", (column,))
    except Exception:
        return ""
    row = cur.fetchone()
    if not row:
        return ""
    if isinstance(row, dict):
        return str(row.get("Type") or "")
    # Field, Type, ...
    return str(row[1] if len(row) > 1 else "")


def ensure_dual_gudang(cur) -> None:
    """
    Ensure kimia/RP stock use gudang utama|lapangan.
    Migrates legacy kimia→utama, mixing→lapangan via ALTER + UPDATE.
    """
    kimia_cols = _col_names(cur, "tbl_stok_kimia_in")
    if kimia_cols and "gudang" in kimia_cols:
        gtype = _col_type(cur, "tbl_stok_kimia_in", "gudang").lower()
        # Widen ENUM (or leave VARCHAR) so legacy + new values coexist during migrate.
        if "enum" in gtype and "utama" not in gtype:
            try:
                cur.execute(
                    "ALTER TABLE tbl_stok_kimia_in MODIFY gudang "
                    "ENUM('kimia','mixing','utama','lapangan') DEFAULT 'utama'"
                )
            except Exception:
                pass
        try:
            cur.execute(
                "UPDATE tbl_stok_kimia_in SET gudang='utama' "
                "WHERE gudang IS NULL OR gudang='' OR gudang='kimia'"
            )
            cur.execute(
                "UPDATE tbl_stok_kimia_in SET gudang='lapangan' WHERE gudang='mixing'"
            )
        except Exception:
            pass
        gtype2 = _col_type(cur, "tbl_stok_kimia_in", "gudang").lower()
        if "enum" in gtype2 and "kimia" in gtype2:
            try:
                cur.execute(
                    "ALTER TABLE tbl_stok_kimia_in MODIFY gudang "
                    "ENUM('utama','lapangan') DEFAULT 'utama'"
                )
            except Exception:
                pass

    out_cols = _col_names(cur, "tbl_stok_kimia_out")
    if out_cols and "tujuan" in out_cols:
        ttype = _col_type(cur, "tbl_stok_kimia_out", "tujuan").lower()
        if "enum" in ttype and "lapangan" not in ttype:
            try:
                cur.execute(
                    "ALTER TABLE tbl_stok_kimia_out MODIFY tujuan "
                    "ENUM('mixing','produksi','return','lapangan','keluar') NOT NULL"
                )
            except Exception:
                pass
        try:
            cur.execute(
                "UPDATE tbl_stok_kimia_out SET tujuan='lapangan' WHERE tujuan='mixing'"
            )
        except Exception:
            pass

    rp_in_cols = _col_names(cur, "tbl_stok_rp_in")
    if rp_in_cols and "gudang" not in rp_in_cols:
        try:
            cur.execute(
                "ALTER TABLE tbl_stok_rp_in ADD COLUMN gudang "
                "VARCHAR(20) NOT NULL DEFAULT 'utama'"
            )
        except Exception:
            pass
        rp_in_cols = _col_names(cur, "tbl_stok_rp_in")
    if rp_in_cols and "gudang" in rp_in_cols:
        try:
            cur.execute(
                "UPDATE tbl_stok_rp_in SET gudang='utama' "
                "WHERE gudang IS NULL OR gudang='' OR gudang='kimia'"
            )
            cur.execute(
                "UPDATE tbl_stok_rp_in SET gudang='lapangan' WHERE gudang='mixing'"
            )
        except Exception:
            pass

    rp_out_cols = _col_names(cur, "tbl_stok_rp_out")
    if rp_out_cols and "gudang" not in rp_out_cols:
        try:
            cur.execute(
                "ALTER TABLE tbl_stok_rp_out ADD COLUMN gudang "
                "VARCHAR(20) DEFAULT NULL"
            )
        except Exception:
            pass
    if rp_out_cols and "tujuan" not in rp_out_cols:
        try:
            cur.execute(
                "ALTER TABLE tbl_stok_rp_out ADD COLUMN tujuan "
                "VARCHAR(20) DEFAULT NULL"
            )
        except Exception:
            pass
