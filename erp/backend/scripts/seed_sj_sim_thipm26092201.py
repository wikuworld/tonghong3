#!/usr/bin/env python3
"""Seed simulasi SJ→Invoice untuk SO THIPM26092201 (2 lot).

Menyiapkan:
- ERP: stage Outstanding, production+QC+packing done per lot
- MRP: packing finished + gudang FG in_stock per lot

Usage:
  cd erp/backend
  PYTHONPATH=. ../.venv/bin/python scripts/seed_sj_sim_thipm26092201.py
  # atau:
  PYTHONPATH=. .venv/bin/python scripts/seed_sj_sim_thipm26092201.py
"""

from __future__ import annotations

import os
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pymysql
from sqlalchemy import create_engine, select, text
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

from app.models import PoDetail, PoDetailDelivery, PoHeader  # noqa: E402
from app.services.delivery_shipment import list_ready_to_ship_for_po_details  # noqa: E402
from app.services.mrp_packing_bridge import ensure_erp_packing_from_mrp_finish  # noqa: E402
from app.services.mrp_production_bridge import upsert_production_mirror  # noqa: E402

PO_NUMBER = "THIPM26092201"
TARGET_LOTS = ("PUMAD002260922001", "PUMAD002260922002")


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


def _ensure_mrp_packing(
    cur,
    *,
    lot: str,
    qty: Decimal,
    customer: str,
    no_po: str,
    no_so: str,
    mrp_po_id: int,
    erp_production_id: int,
    erp_production_detail_id: int,
) -> tuple[int, str, str]:
    kode_wip = f"WIP-{lot}"[:30]
    kode_packing = f"PK-{lot[-12:]}"[:30]
    if len(kode_packing) < 8:
        kode_packing = f"PK-{lot}"[:30]

    cur.execute("SELECT id, status FROM tbl_packing WHERE kode_packing=%s LIMIT 1", (kode_packing,))
    existing = cur.fetchone()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if existing:
        packing_id = int(existing["id"])
        cur.execute(
            """
            UPDATE tbl_packing
            SET kode_wip=%s, no_po=%s, customer=%s, total_lembar=%s, total_ukuran=%s,
                status='finished', date_finished=%s,
                erp_production_id=%s, erp_production_detail_id=%s
            WHERE id=%s
            """,
            (
                kode_wip,
                no_po,
                customer,
                1,
                float(qty),
                now,
                erp_production_id,
                erp_production_detail_id,
                packing_id,
            ),
        )
    else:
        cur.execute(
            """
            INSERT INTO tbl_packing
              (kode_packing, kode_wip, no_po, customer, total_lembar, total_ukuran,
               status, date_created, date_finished, erp_production_id, erp_production_detail_id)
            VALUES (%s,%s,%s,%s,%s,%s,'finished',%s,%s,%s,%s)
            """,
            (
                kode_packing,
                kode_wip,
                no_po,
                customer,
                1,
                float(qty),
                now,
                now,
                erp_production_id,
                erp_production_detail_id,
            ),
        )
        packing_id = int(cur.lastrowid)

    cur.execute("DELETE FROM tbl_packing_po WHERE packing_id=%s", (packing_id,))
    cur.execute(
        """
        INSERT INTO tbl_packing_po (packing_id, po_id, no_po, no_so, qty_sq)
        VALUES (%s,%s,%s,%s,%s)
        """,
        (packing_id, mrp_po_id, no_po, no_so, float(qty)),
    )

    cur.execute("DELETE FROM tbl_packing_roll WHERE packing_id=%s", (packing_id,))
    cur.execute(
        """
        INSERT INTO tbl_packing_roll (packing_id, roll_no, lembar, ukuran, kode_packing)
        VALUES (%s,1,1,%s,%s)
        """,
        (packing_id, float(qty), kode_packing),
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
            (kode_packing, kode_wip, customer, float(qty), int(fg["id"])),
        )
        fg_id = int(fg["id"])
    else:
        cur.execute(
            """
            INSERT INTO tbl_gudang_fg
              (packing_id, kode_packing, kode_wip, customer, total_lembar, total_ukuran, status, date_in)
            VALUES (%s,%s,%s,%s,1,%s,'in_stock',%s)
            """,
            (packing_id, kode_packing, kode_wip, customer, float(qty), now),
        )
        fg_id = int(cur.lastrowid)

    return packing_id, kode_packing, kode_wip, fg_id


def main() -> int:
    url = os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL missing", file=sys.stderr)
        return 1

    eng = create_engine(url)
    Session = sessionmaker(bind=eng, autoflush=False, autocommit=False)
    db = Session()
    mrp = _mrp_conn()
    summary: list[dict] = []

    try:
        po = db.scalars(select(PoHeader).where(PoHeader.po_number == PO_NUMBER).limit(1)).first()
        if not po:
            print(f"PO {PO_NUMBER} tidak ditemukan", file=sys.stderr)
            return 1

        # Siapkan tahap Outstanding agar Buat SJ diizinkan
        po.mkt_workflow_stage = "in_outstanding"
        po.material_followup_done = True
        if (po.status or "").lower() == "confirmed":
            po.status = "production"
        db.flush()

        details = list(
            db.scalars(
                select(PoDetail)
                .where(PoDetail.po_id == po.id)
                .order_by(PoDetail.id.asc())
            ).all()
        )
        by_lot = {(d.thi_line_ref or "").strip(): d for d in details}
        missing = [lot for lot in TARGET_LOTS if lot not in by_lot]
        if missing:
            print(f"Lot tidak ketemu di ERP: {missing}", file=sys.stderr)
            return 1

        mcur = mrp.cursor()
        for lot in TARGET_LOTS:
            d = by_lot[lot]
            qty = Decimal(str(d.quantity_order or 0))
            if qty <= 0:
                qty = Decimal("1")

            if not (d.system_reference or "").strip():
                d.system_reference = lot

            # Rencana kirim 1 slot (mengisi kolom rencana di Outstanding)
            existing_slots = list(
                db.scalars(
                    select(PoDetailDelivery).where(PoDetailDelivery.po_detail_id == d.id)
                ).all()
            )
            if not existing_slots:
                db.add(
                    PoDetailDelivery(
                        po_detail_id=d.id,
                        sequence_no=1,
                        qty=qty,
                        delivery_date=d.line_etd or po.etd or date.today(),
                    )
                )
            db.flush()

            mcur.execute(
                "SELECT id, no_po, qty_order FROM tbl_master_po WHERE source_detail_id=%s LIMIT 1",
                (int(d.id),),
            )
            mpo = mcur.fetchone()
            if not mpo:
                print(f"MRP master_po untuk detail #{d.id} / {lot} tidak ada", file=sys.stderr)
                return 1
            mrp_po_id = int(mpo["id"])
            no_po_cust = (mpo.get("no_po") or po.po_customer_ref or "NO123").strip()
            customer = (po.customer_name_snapshot or "").strip() or "CUSTOMER"

            # Production mirror dulu (tanpa packing id), lalu packing MRP, lalu packing ERP
            kode_wip = f"WIP-{lot}"[:100]
            prod = upsert_production_mirror(
                db,
                source_detail_id=int(d.id),
                kode_wip=kode_wip,
                qty_planned=qty,
                qty_actual=qty,
                finish=True,
                actor="seed-sj-sim",
            )
            db.flush()

            packing_id, kode_packing, kode_wip_mrp, fg_id = _ensure_mrp_packing(
                mcur,
                lot=lot,
                qty=qty,
                customer=customer,
                no_po=no_po_cust,
                no_so=PO_NUMBER,
                mrp_po_id=mrp_po_id,
                erp_production_id=prod.production_id,
                erp_production_detail_id=prod.production_detail_id,
            )

            # Update mirror batch_number = mrp packing id
            from app.models import PackingHeader, ProductionDetail as PD

            pd_row = db.get(PD, prod.production_detail_id)
            if pd_row:
                pd_row.batch_number = str(packing_id)
            db.flush()

            erp_pack = ensure_erp_packing_from_mrp_finish(
                db,
                mrp_packing_id=packing_id,
                kode_packing=kode_packing,
                production_id=prod.production_id,
                lines=[(prod.production_detail_id, qty)],
                actor="seed-sj-sim",
                qty_roll=1,
            )
            pk = db.get(PackingHeader, erp_pack.packing_id)
            if pk:
                pk.mrp_fg_id = fg_id
            db.flush()

            mcur.execute(
                """
                UPDATE tbl_master_po
                SET qty_processed=%s, status='completed', lot_number=%s, no_so=%s
                WHERE id=%s
                """,
                (float(qty), lot, PO_NUMBER, mrp_po_id),
            )

            summary.append(
                {
                    "lot": lot,
                    "po_detail_id": int(d.id),
                    "qty": float(qty),
                    "erp_production_id": prod.production_id,
                    "erp_production_detail_id": prod.production_detail_id,
                    "erp_packing_id": erp_pack.packing_id,
                    "erp_packing_number": erp_pack.packing_number,
                    "mrp_packing_id": packing_id,
                    "kode_packing": kode_packing,
                    "kode_wip": kode_wip_mrp,
                    "mrp_fg_id": fg_id,
                }
            )

        db.commit()
        mrp.commit()

        # Verifikasi packing options siap SJ
        opts = list_ready_to_ship_for_po_details(db, [1, 2])
        print("OK seeded SJ simulation for", PO_NUMBER)
        for row in summary:
            print(
                f"  lot={row['lot']} qty={row['qty']} "
                f"erp_packing={row['erp_packing_number']}(#{row['erp_packing_id']}) "
                f"mrp_packing={row['kode_packing']}(#{row['mrp_packing_id']}) "
                f"fg=#{row['mrp_fg_id']}"
            )
        print(f"ready_to_ship_options={len(opts)}")
        for o in opts:
            print(
                f"  option lot={o.get('lot_no')} packing={o.get('packing_number')} "
                f"avail={o.get('qty_available')} po_detail_id={o.get('po_detail_id')}"
            )
        print(
            "\nLanjut di UI:\n"
            "1) Marketing Flow → Outstanding → centang 1 lot → Buat SJ dari Packing\n"
            "2) Ulangi untuk lot kedua (transaksi SJ terpisah)\n"
            "3) Delivery scan-out / sent → Invoice THIN otomatis"
        )
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
