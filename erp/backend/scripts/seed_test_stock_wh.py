#!/usr/bin/env python3
"""Isi stok WH dan qty terkait untuk SO yang sudah ada. Khusus testing UAT.

Outstanding membaca angka ini dari MRP, bukan dari kolom ERP yang kosong:

- STOCK WH  = packing ``finished`` yang tertaut ke baris SO
- QTY WIP   = persiapan kulit (started/saved/completed) dikurangi stok WH
- QTY RENCANA / SISA RENCANA = ``tbl_master_po.qty_processed``
- BALANCE   = qty order − qty terkirim (header delivery cancelled diabaikan)

Script ini:

- tidak mengubah packing / gudang FG yang sudah ada
- menambah baris bertanda ``TWH-`` hanya untuk baris SO yang stok WH-nya masih 0
- mengisi ``po_details.stock_wh_qty`` (netto, sudah dikurangi terkirim) dan ``balance_qty``

Baris tanpa stok: 40% order masuk gudang, 20% tetap WIP.
Baris yang sudah punya persiapan tapi belum masuk gudang: 40% persiapan jadi stok WH,
sisanya tetap tampil sebagai WIP.

Usage:
  cd erp/backend
  PYTHONPATH=. .venv/bin/python scripts/seed_test_stock_wh.py
  PYTHONPATH=. .venv/bin/python scripts/seed_test_stock_wh.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pymysql
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent
ROOT = BACKEND.parent.parent
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


def _load_dotenv() -> None:
    for f in (ROOT / ".env", BACKEND / ".env"):
        if not f.is_file():
            continue
        for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip() or line.strip().startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()

from app.models import PoDetail, PoHeader  # noqa: E402
from app.services.po_delivery_balance import (  # noqa: E402
    sum_delivered_qty_for_po_detail,
    sync_po_detail_balance_qty,
)

_SKIP_HEADER = frozenset({"draft", "completed", "cancelled", "canceled"})
_STOCK_RATIO = Decimal("0.40")
_WIP_RATIO = Decimal("0.20")
_Q = Decimal("0.01")


def _q(value: Decimal) -> Decimal:
    return value.quantize(_Q, rounding=ROUND_HALF_UP)


def _as_float_qty(value) -> float:
    try:
        return max(0.0, float(value or 0))
    except (TypeError, ValueError):
        return 0.0


def _mrp_conn():
    return pymysql.connect(
        host=os.environ.get("MRP_DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("MRP_DB_PORT", "3306")),
        user=os.environ.get("MRP_DB_USER", "uat_tonghong_mrp"),
        password=os.environ.get("MRP_DB_PASSWORD", ""),
        database=os.environ.get("MRP_DB_NAME", "uat_tonghong_mrp"),
        autocommit=False,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def _assign_stock_wh(packings, packing_po_rows, alloc_rows, source_ids: list[int]) -> dict[int, float]:
    """Salinan ringkas ``_assign_stock_wh_from_finished_packings`` di MRP."""
    wanted = {int(x) for x in source_ids}
    pos_by_packing: dict[int, list] = {}
    for pp in packing_po_rows:
        try:
            pid = int(pp.get("packing_id"))
        except (TypeError, ValueError):
            continue
        pos_by_packing.setdefault(pid, []).append(pp)

    allocs_by_item: dict[int, list] = {}
    alloc_by_po_id: dict[int, dict] = {}
    for alloc in alloc_rows:
        try:
            sid_i = int(alloc.get("source_detail_id"))
            item_id = int(alloc.get("item_id"))
        except (TypeError, ValueError):
            continue
        if sid_i not in wanted:
            continue
        allocs_by_item.setdefault(item_id, []).append(alloc)
        try:
            po_id = int(alloc.get("po_id"))
        except (TypeError, ValueError):
            po_id = None
        if po_id is not None:
            alloc_by_po_id[po_id] = alloc

    out: dict[int, float] = {}

    def _add(sid: int, qty: float) -> None:
        if sid in wanted and qty > 0:
            out[sid] = out.get(sid, 0.0) + qty

    def _unique_sids(allocs: list) -> list[int]:
        seen: list[int] = []
        for alloc in allocs:
            try:
                sid = int(alloc.get("source_detail_id"))
            except (TypeError, ValueError):
                continue
            if sid in wanted and sid not in seen:
                seen.append(sid)
        return seen

    for packing in packings:
        qty = _as_float_qty(packing.get("total_ukuran"))
        if qty <= 0:
            continue
        try:
            packing_id = int(packing.get("id"))
        except (TypeError, ValueError):
            packing_id = None
        try:
            item_id = int(packing.get("rencana_item_id"))
        except (TypeError, ValueError):
            item_id = None
        chosen = allocs_by_item.get(item_id, []) if item_id is not None else []
        sids = _unique_sids(chosen)
        if len(sids) == 1:
            _add(sids[0], qty)
            continue
        assigned = False
        for pp in pos_by_packing.get(packing_id, []) if packing_id is not None else []:
            try:
                po_id = int(pp.get("po_id"))
            except (TypeError, ValueError):
                continue
            alloc = alloc_by_po_id.get(po_id)
            if not alloc:
                continue
            try:
                sid = int(alloc.get("source_detail_id"))
            except (TypeError, ValueError):
                continue
            _add(sid, _as_float_qty(pp.get("qty_sq")) or qty)
            assigned = True
        if assigned or item_id is not None:
            continue
    return out


def _stock_wh_by_source(cur, source_ids: list[int]) -> dict[int, float]:
    if not source_ids:
        return {}
    cur.execute(
        "SELECT id, rencana_item_id, kode_wip, total_ukuran FROM tbl_packing WHERE status='finished'"
    )
    packings = list(cur.fetchall() or [])
    if not packings:
        return {}
    packing_ids = [int(p["id"]) for p in packings if p.get("id") is not None]
    packing_po_rows: list = []
    if packing_ids:
        ph = ",".join(["%s"] * len(packing_ids))
        cur.execute(
            f"SELECT packing_id, po_id, no_po, no_so, qty_sq FROM tbl_packing_po WHERE packing_id IN ({ph})",
            packing_ids,
        )
        packing_po_rows = list(cur.fetchall() or [])
    ph = ",".join(["%s"] * len(source_ids))
    cur.execute(
        f"""
        SELECT rip.item_id, rip.po_id, po.source_detail_id, i.kode_lot_wip
        FROM tbl_rencana_item_po rip
        JOIN tbl_master_po po ON po.id = rip.po_id
        JOIN tbl_rencana_item i ON i.id = rip.item_id
        WHERE po.source_detail_id IN ({ph})
        """,
        source_ids,
    )
    alloc_rows = list(cur.fetchall() or [])
    return _assign_stock_wh(packings, packing_po_rows, alloc_rows, source_ids)


def _persiapan_qty(cur, source_detail_id: int) -> float:
    cur.execute(
        """
        SELECT COALESCE(SUM(pk.total_size), 0) AS qty
        FROM tbl_master_po po
        JOIN tbl_rencana_item_po rip ON rip.po_id = po.id
        JOIN tbl_rencana_item i ON i.id = rip.item_id
        JOIN tbl_persiapan_kulit pk ON pk.rencana_item_id = i.id
        WHERE po.source_detail_id = %s
          AND pk.status IN ('started', 'saved', 'completed')
          AND COALESCE(pk.kode_wip, '') <> ''
          AND COALESCE(pk.total_size, 0) > 0
        """,
        (source_detail_id,),
    )
    row = cur.fetchone() or {}
    return _as_float_qty(row.get("qty"))


def _ensure_master_po(cur, header: PoHeader, detail: PoDetail) -> int:
    cur.execute(
        "SELECT id, qty_processed, qty_order, status FROM tbl_master_po WHERE source_detail_id=%s LIMIT 1",
        (int(detail.id),),
    )
    existing = cur.fetchone()
    if existing:
        return int(existing["id"])

    no_so = (header.po_number or "").strip()
    no_po = ((header.po_customer_ref or header.po_number or "").strip())[:50]
    item_name = ((detail.material_name or detail.style_article or f"LINE-{detail.id}").strip())[:200]
    customer = ((header.customer_name_snapshot or header.customer_code or "").strip())[:150] or None
    lot = ((detail.thi_line_ref or detail.system_reference or "").strip())[:100] or None
    qty = float(detail.quantity_order or 0)
    cur.execute(
        """
        INSERT INTO tbl_master_po
          (no_po, no_so, customer, customer_id, item_name, warna, tebal, emboss,
           sq_ft, qty_order, qty_processed, status, lot_number, source_detail_id, qty_balance_erp)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,'outstanding',%s,%s,%s)
        """,
        (
            no_po,
            no_so or None,
            customer,
            int(header.customer_id) if header.customer_id else None,
            item_name,
            ((detail.color or "").strip()[:100] or None),
            ((detail.thickness_text or "").strip()[:30] or None),
            ((detail.emboss or "").strip()[:100] or None),
            qty,
            qty,
            lot,
            int(detail.id),
            qty,
        ),
    )
    return int(cur.lastrowid)


def _ensure_test_plan(cur, *, detail_id: int, mrp_po_id: int, header: PoHeader, detail: PoDetail) -> int:
    kode_item = f"TWH-I-{detail_id}"[:30]
    cur.execute("SELECT id FROM tbl_rencana_item WHERE kode_rencana_item=%s LIMIT 1", (kode_item,))
    row = cur.fetchone()
    if row:
        return int(row["id"])

    kode_rencana = f"TWH-R-{detail_id}"[:30]
    kode_lot = f"TWH-L-{detail_id}"[:30]
    cur.execute("SELECT id FROM tbl_rencana_produksi WHERE kode_rencana=%s LIMIT 1", (kode_rencana,))
    rencana = cur.fetchone()
    if rencana:
        rencana_id = int(rencana["id"])
    else:
        cur.execute(
            """
            INSERT INTO tbl_rencana_produksi
              (kode_rencana, kode_lot_wip, nama_rencana, status, tanggal_rencana)
            VALUES (%s,%s,%s,'active',CURDATE())
            """,
            (kode_rencana, kode_lot, f"TEST STOCK WH {header.po_number or detail_id}"[:200]),
        )
        rencana_id = int(cur.lastrowid)

    customer_id = int(header.customer_id) if header.customer_id else 0
    customer = ((header.customer_name_snapshot or "").strip())[:150] or None
    cur.execute(
        """
        INSERT INTO tbl_rencana_item
          (rencana_id, kode_rencana_item, kode_lot_wip, customer_id, nama_customer,
           thickness, color, emboss, material_name, keterangan, urutan)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'seed test stock WH',1)
        """,
        (
            rencana_id,
            kode_item,
            kode_lot,
            customer_id,
            customer,
            ((detail.thickness_text or "").strip()[:30] or None),
            ((detail.color or "").strip()[:100] or None),
            ((detail.emboss or "").strip()[:100] or None),
            ((detail.material_name or "").strip())[:150] or None,
        ),
    )
    item_id = int(cur.lastrowid)
    cur.execute(
        """
        INSERT INTO tbl_rencana_item_po (item_id, po_id, qty_outstanding, qty_proses)
        VALUES (%s,%s,%s,0)
        """,
        (item_id, mrp_po_id, float(detail.quantity_order or 0)),
    )
    return item_id


def _ensure_packing(
    cur,
    *,
    detail_id: int,
    item_id: int,
    mrp_po_id: int,
    header: PoHeader,
    qty: Decimal,
) -> str:
    kode_packing = f"TWH-P-{detail_id}"[:30]
    kode_wip = f"TWH-WIP-{detail_id}"[:30]
    no_so = (header.po_number or "").strip()
    no_po = ((header.po_customer_ref or header.po_number or "").strip())[:50]
    customer = ((header.customer_name_snapshot or "").strip())[:150] or None
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    qty_f = float(qty)

    cur.execute("SELECT id FROM tbl_packing WHERE kode_packing=%s LIMIT 1", (kode_packing,))
    existing = cur.fetchone()
    if existing:
        packing_id = int(existing["id"])
        cur.execute(
            """
            UPDATE tbl_packing
            SET kode_wip=%s, no_po=%s, customer=%s, total_lembar=1, total_ukuran=%s,
                status='finished', date_finished=%s, rencana_item_id=%s
            WHERE id=%s
            """,
            (kode_wip, no_po, customer, qty_f, now, item_id, packing_id),
        )
    else:
        cur.execute(
            """
            INSERT INTO tbl_packing
              (kode_packing, kode_wip, no_po, customer, total_lembar, total_ukuran,
               status, date_created, date_finished, rencana_item_id)
            VALUES (%s,%s,%s,%s,1,%s,'finished',%s,%s,%s)
            """,
            (kode_packing, kode_wip, no_po, customer, qty_f, now, now, item_id),
        )
        packing_id = int(cur.lastrowid)

    cur.execute("DELETE FROM tbl_packing_po WHERE packing_id=%s", (packing_id,))
    cur.execute(
        "INSERT INTO tbl_packing_po (packing_id, po_id, no_po, no_so, qty_sq) VALUES (%s,%s,%s,%s,%s)",
        (packing_id, mrp_po_id, no_po, no_so, qty_f),
    )
    cur.execute("DELETE FROM tbl_packing_roll WHERE packing_id=%s", (packing_id,))
    cur.execute(
        """
        INSERT INTO tbl_packing_roll (packing_id, roll_no, lembar, ukuran, kode_packing, remark)
        VALUES (%s,1,1,%s,%s,'seed test stock WH')
        """,
        (packing_id, qty_f, kode_packing),
    )

    cur.execute("SELECT id FROM tbl_gudang_fg WHERE packing_id=%s LIMIT 1", (packing_id,))
    fg = cur.fetchone()
    if fg:
        cur.execute(
            """
            UPDATE tbl_gudang_fg
            SET kode_packing=%s, kode_wip=%s, customer=%s, total_lembar=1, total_ukuran=%s,
                status='in_stock', date_out=NULL, keterangan_out=NULL,
                erp_delivery_id=NULL, erp_delivery_number=NULL
            WHERE id=%s
            """,
            (kode_packing, kode_wip, customer, qty_f, int(fg["id"])),
        )
    else:
        cur.execute(
            """
            INSERT INTO tbl_gudang_fg
              (packing_id, kode_packing, kode_wip, customer, total_lembar, total_ukuran, status, date_in)
            VALUES (%s,%s,%s,%s,1,%s,'in_stock',%s)
            """,
            (packing_id, kode_packing, kode_wip, customer, qty_f, now),
        )
    return kode_packing


def _ensure_wip(cur, *, detail_id: int, item_id: int, header: PoHeader, qty: Decimal) -> None:
    if qty <= 0:
        return
    kode_proses = f"TWH-PR-{detail_id}"[:30]
    kode_wip = f"TWH-WIP-{detail_id}"[:30]
    kode_rencana = f"TWH-R-{detail_id}"[:30]
    no_po = ((header.po_customer_ref or header.po_number or "").strip())[:500]
    cur.execute("SELECT id FROM tbl_persiapan_kulit WHERE kode_proses=%s LIMIT 1", (kode_proses,))
    row = cur.fetchone()
    if row:
        cur.execute(
            """
            UPDATE tbl_persiapan_kulit
            SET kode_wip=%s, kode_rencana=%s, no_po=%s, total_size=%s,
                status='started', rencana_item_id=%s
            WHERE id=%s
            """,
            (kode_wip, kode_rencana, no_po, float(qty), item_id, int(row["id"])),
        )
        return
    cur.execute(
        """
        INSERT INTO tbl_persiapan_kulit
          (kode_wip, kode_rencana, kode_proses, no_po, total_size, status, rencana_item_id)
        VALUES (%s,%s,%s,%s,%s,'started',%s)
        """,
        (kode_wip, kode_rencana, kode_proses, no_po, float(qty), item_id),
    )


def _bump_processed(cur, mrp_po_id: int, order_qty: Decimal, processed_target: Decimal) -> None:
    cur.execute("SELECT qty_processed, qty_order FROM tbl_master_po WHERE id=%s", (mrp_po_id,))
    row = cur.fetchone() or {}
    current = Decimal(str(row.get("qty_processed") or 0))
    order = Decimal(str(row.get("qty_order") or order_qty or 0))
    if current > 0:
        return
    target = min(order, processed_target) if order > 0 else processed_target
    if target <= 0:
        status = "outstanding"
    elif order > 0 and target >= order:
        status = "completed"
    else:
        status = "partial"
    cur.execute(
        "UPDATE tbl_master_po SET qty_processed=%s, status=%s WHERE id=%s",
        (float(target), status, mrp_po_id),
    )


def _load_lines(db) -> list[tuple[PoHeader, PoDetail]]:
    headers = db.scalars(
        select(PoHeader).order_by(PoHeader.id.asc())
    ).all()
    out: list[tuple[PoHeader, PoDetail]] = []
    for header in headers:
        status = (header.status or "").strip().lower()
        if status in _SKIP_HEADER:
            continue
        details = db.scalars(
            select(PoDetail).where(PoDetail.po_id == header.id).order_by(PoDetail.id.asc())
        ).all()
        for detail in details:
            out.append((header, detail))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Isi stok WH testing untuk SO yang sudah ada")
    parser.add_argument("--dry-run", action="store_true", help="Hitung saja, jangan tulis database")
    args = parser.parse_args()

    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL missing", file=sys.stderr)
        return 1

    eng = create_engine(url)
    Session = sessionmaker(bind=eng, autoflush=False, autocommit=False)
    db = Session()
    mrp = _mrp_conn()
    try:
        lines = _load_lines(db)
        if not lines:
            print("Tidak ada baris SO aktif")
            return 0
        source_ids = [int(d.id) for _, d in lines]
        cur = mrp.cursor()

        before = _stock_wh_by_source(cur, source_ids)
        seeded: list[str] = []

        for header, detail in lines:
            detail_id = int(detail.id)
            order_qty = Decimal(str(detail.quantity_order or 0))
            if order_qty <= 0:
                continue
            if _as_float_qty(before.get(detail_id)) > 0:
                continue

            mrp_po_id = _ensure_master_po(cur, header, detail)
            item_id = _ensure_test_plan(
                cur, detail_id=detail_id, mrp_po_id=mrp_po_id, header=header, detail=detail
            )
            prepared = Decimal(str(_persiapan_qty(cur, detail_id)))
            if prepared > 0:
                stock_qty = _q(min(order_qty, prepared) * _STOCK_RATIO)
                wip_qty = Decimal("0")
            else:
                stock_qty = _q(order_qty * _STOCK_RATIO)
                wip_qty = _q(order_qty * _WIP_RATIO)
            if stock_qty <= 0:
                stock_qty = _q(min(order_qty, Decimal("1")))
            if not args.dry_run:
                kode = _ensure_packing(
                    cur,
                    detail_id=detail_id,
                    item_id=item_id,
                    mrp_po_id=mrp_po_id,
                    header=header,
                    qty=stock_qty,
                )
                if wip_qty > 0:
                    _ensure_wip(
                        cur,
                        detail_id=detail_id,
                        item_id=item_id,
                        header=header,
                        qty=stock_qty + wip_qty,
                    )
                _bump_processed(cur, mrp_po_id, order_qty, stock_qty + wip_qty)
            else:
                kode = f"TWH-P-{detail_id}"
            seeded.append(
                f"  {header.po_number} detail={detail_id} stock_wh={stock_qty} "
                f"wip_baru={wip_qty} packing={kode}"
            )

        after = _stock_wh_by_source(cur, source_ids) if not args.dry_run else before
        print(f"SO aktif: {len(lines)}")
        print(f"Baris yang diisi stok WH testing: {len(seeded)}")
        for line in seeded:
            print(line)

        print("\nKolom ERP (stock WH netto = packing finished − terkirim, balance = order − terkirim):")
        for header, detail in lines:
            detail_id = int(detail.id)
            delivered = sum_delivered_qty_for_po_detail(db, detail_id)
            gross = Decimal(str((after if not args.dry_run else before).get(detail_id, 0)))
            net = gross - delivered
            if net < 0:
                net = Decimal("0")
            net = _q(net)
            balance = sync_po_detail_balance_qty(db, detail_id)
            detail.stock_wh_qty = net
            print(
                f"  {header.po_number} detail={detail_id} "
                f"stock_wh={net} balance={balance} delivered={delivered} gross_mrp={_q(gross)}"
            )

        if args.dry_run:
            db.rollback()
            mrp.rollback()
            print("\nDry-run: tidak ada yang ditulis.")
            return 0

        db.commit()
        mrp.commit()
        print("\nTersimpan. Outstanding akan membaca stok WH ini dari MRP.")
        return 0
    except Exception:
        db.rollback()
        mrp.rollback()
        raise
    finally:
        db.close()
        mrp.close()


if __name__ == "__main__":
    raise SystemExit(main())
