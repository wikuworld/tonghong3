"""Aturan pecahan repack FG. Tidak menyentuh database."""

from __future__ import annotations


def validate_repack_lines(lines, total_lembar, total_ukuran):
    """Return (None, parsed) atau (pesan, None).

    Jumlah lembar harus sama persis. Jumlah ukuran boleh selisih sampai 0,01.
    """
    if not isinstance(lines, list) or not lines:
        return "Minimal satu baris repack", None
    try:
        lembar_target = int(total_lembar or 0)
    except (TypeError, ValueError):
        return "Lembar FG lama tidak valid", None
    try:
        ukuran_target = round(float(total_ukuran or 0), 2)
    except (TypeError, ValueError):
        return "Ukuran FG lama tidak valid", None
    parsed = []
    lembar_sum = 0
    ukuran_sum = 0.0
    for index, line in enumerate(lines, start=1):
        line = line or {}
        try:
            lembar = int(line.get("lembar"))
        except (TypeError, ValueError):
            return f"Baris {index}: lembar harus bilangan bulat", None
        if lembar <= 0:
            return f"Baris {index}: lembar harus > 0", None
        try:
            ukuran = round(float(line.get("ukuran")), 2)
        except (TypeError, ValueError):
            return f"Baris {index}: ukuran harus angka", None
        if ukuran <= 0:
            return f"Baris {index}: ukuran harus > 0", None
        lembar_sum += lembar
        ukuran_sum = round(ukuran_sum + ukuran, 2)
        parsed.append({"lembar": lembar, "ukuran": ukuran})
    if lembar_sum != lembar_target:
        return "Jumlah lembar baru harus sama dengan FG lama", None
    if abs(ukuran_sum - ukuran_target) > 0.01:
        return "Jumlah ukuran baru harus sama dengan FG lama", None
    return None, parsed
