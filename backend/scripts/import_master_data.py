#!/usr/bin/env python3
"""
Impor CSV dari Master_Data_extracted ke MariaDB.

  cd backend && PYTHONPATH=. python scripts/import_master_data.py

CSV: ../../Master_Data_extracted/ (folder `Projects` di samping repo Tonghong).
Override: env MASTER_CSV_DIR=/path/to/Master_Data_extracted
"""

from __future__ import annotations

import csv
import os
import re
import sys
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
TONGHONG_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = TONGHONG_ROOT.parent / "Master_Data_extracted"
CSV_DIR = Path(os.environ.get("MASTER_CSV_DIR", str(DEFAULT_CSV)))

sys.path.insert(0, str(BACKEND))


def excel_serial_to_date(serial: str | None) -> date | None:
    if not serial or not str(serial).strip():
        return None
    try:
        n = int(float(serial))
    except (ValueError, TypeError):
        return None
    base = date(1899, 12, 30)
    return base + timedelta(days=n)


def parse_thickness_range(text: str | None) -> tuple[Decimal | None, Decimal | None]:
    if not text or not str(text).strip():
        return None, None
    m = re.match(
        r"^\s*([\d.]+)\s*[-–]\s*([\d.]+)\s*$",
        str(text).strip(),
    )
    if not m:
        return None, None
    try:
        return Decimal(m.group(1)), Decimal(m.group(2))
    except (InvalidOperation, ValueError):
        return None, None


def dec(val: str | None) -> Decimal | None:
    if val is None or str(val).strip() == "":
        return None
    try:
        return Decimal(str(val).strip())
    except InvalidOperation:
        return None


def import_items(session) -> int:
    from app.models import MasterItem

    path = CSV_DIR / "01_Master_Item.csv"
    if not path.exists():
        print("Skip items:", path)
        return 0
    n = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = (row.get("item_code") or "").strip()
            if not code:
                continue
            existing = session.query(MasterItem).filter_by(item_code=code).first()
            if existing:
                continue
            t = dec(row.get("thickness_mm"))
            session.add(
                MasterItem(
                    item_code=code,
                    thickness_mm=t,
                    material_name=(row.get("material_name") or "").strip() or None,
                    emboss=(row.get("emboss") or "").strip() or None,
                    color=(row.get("color") or "").strip() or None,
                    category=(row.get("category") or "").strip() or None,
                )
            )
            n += 1
    session.commit()
    print("master_items inserted:", n)
    return n


def import_prices(session) -> int:
    from sqlalchemy import delete

    from app.models import MasterPrice

    path = CSV_DIR / "02_Master_Harga.csv"
    if not path.exists():
        print("Skip prices:", path)
        return 0
    session.execute(delete(MasterPrice))
    session.commit()
    n = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            session.add(
                MasterPrice(
                    line_no=int(row["line_no"]) if row.get("line_no") else None,
                    material_category=row.get("material_category") or None,
                    material_type=row.get("material_type") or None,
                    material_name=row.get("material_name") or None,
                    thickness_range=row.get("thickness_range") or None,
                    price_white_usd=dec(row.get("price_white_usd")),
                    price_black_usd=dec(row.get("price_black_usd")),
                    price_color_usd=dec(row.get("price_color_usd")),
                    price_metallic_usd=dec(row.get("price_metallic_usd")),
                    remark=row.get("remark") or None,
                    price_tier=row.get("price_tier") or None,
                )
            )
            n += 1
    session.commit()
    print("master_prices inserted:", n)
    return n


def _unique_customer_code(session, base: str) -> str:
    from app.models import Customer

    code = (base or "CUST")[:50]
    n = 0
    while session.query(Customer).filter(Customer.code == code).first():
        n += 1
        code = f"{(base or 'CUST')[:40]}_{n}"[:50]
    return code


def upsert_customer_by_name(
    session,
    name: str,
    *,
    code: str | None = None,
    phone: str | None = None,
    address: str | None = None,
):
    """
    Selaraskan baris `customers` dengan CSV:
    - cocokkan dulu by `name` (sama persis dengan customer_name_snapshot di marketing).
    - jika ada `code` dan belum dipakai customer lain, set / perbarui.
    - `phone` / `address` hanya ditimpa jika nilai argumen tidak None (string kosong = hapus field).
    """
    from app.models import Customer

    name = (name or "").strip()
    if not name:
        return None

    row = session.query(Customer).filter(Customer.name == name).first()
    if row is None and code:
        cs = (code or "").strip()[:50]
        oc = session.query(Customer).filter(Customer.code == cs).first()
        if oc:
            oc.name = name
            row = oc

    if row is None:
        want_code = (code or "").strip()[:50] if code else None
        if want_code:
            taken = session.query(Customer).filter(Customer.code == want_code).first()
            if taken:
                want_code = None
        if not want_code:
            base = re.sub(r"[^\w\-]+", "_", name)[:48] or "CUST"
            want_code = _unique_customer_code(session, base)
        row = Customer(
            name=name,
            code=want_code,
            phone=phone if phone is not None else None,
            address=address if address is not None else None,
        )
        session.add(row)
        session.flush()
        return row

    if code:
        c = (code or "").strip()[:50]
        if c and row.code != c:
            taken = session.query(Customer).filter(Customer.code == c, Customer.id != row.id).first()
            if not taken:
                row.code = c
    if phone is not None:
        row.phone = phone.strip() if phone.strip() else None
    if address is not None:
        row.address = address.strip() if address.strip() else None
    session.flush()
    return row


def get_or_create_customer(session, name: str):
    """Kompatibel impor marketing: pastikan customer ada by nama snapshot."""
    return upsert_customer_by_name(session, name)


def import_customers_master(session) -> int:
    """File opsional: `00_Master_Customer.csv` — kolom disarankan: customer_code, customer_name, phone, address."""
    path = CSV_DIR / "00_Master_Customer.csv"
    if not path.exists():
        print("Skip 00 customer master:", path)
        return 0
    n = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = (row.get("customer_code") or row.get("code") or "").strip() or None
            name = (row.get("customer_name") or row.get("name") or "").strip()
            if not name:
                continue
            phone = row.get("phone")
            phone = phone.strip() if phone and str(phone).strip() else None
            addr = row.get("address")
            addr = addr.strip() if addr and str(addr).strip() else None
            upsert_customer_by_name(session, name, code=code, phone=phone, address=addr)
            n += 1
    session.commit()
    print("customers upserted from 00_Master_Customer.csv:", n)
    return n


def sync_customers_from_marketing(session) -> int:
    """
    Baca semua nilai unik `customer_name_snapshot` dari `03_Master_Data_Marketing.csv`
    (dan `customer_code` jika kolom opsional ada) agar modul Customer di UI selaras dengan CSV
    meskipun baris SO sudah pernah diimpor (impor marketing melewatkan PO duplikat).
    """
    path = CSV_DIR / "03_Master_Data_Marketing.csv"
    if not path.exists():
        print("Skip sync customers from marketing:", path)
        return 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        if "customer_name_snapshot" not in fields:
            print("Skip sync customers: kolom customer_name_snapshot tidak ada")
            return 0
        has_cc = "customer_code" in fields
        by_name: dict[str, str | None] = {}
        for row in reader:
            name = (row.get("customer_name_snapshot") or "").strip()
            if not name:
                continue
            cc = (row.get("customer_code") or "").strip() or None if has_cc else None
            if name not in by_name:
                by_name[name] = cc
            elif cc and not by_name[name]:
                by_name[name] = cc
    n = 0
    for name in sorted(by_name.keys()):
        upsert_customer_by_name(session, name, code=by_name[name])
        n += 1
    session.commit()
    print("customers synced from marketing (distinct names):", n)
    return n


def import_marketing(session) -> int:
    from app.models import PoDetail, PoDetailDelivery, PoHeader

    path = CSV_DIR / "03_Master_Data_Marketing.csv"
    if not path.exists():
        print("Skip marketing:", path)
        return 0
    n = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            thi = (row.get("thi_line_ref") or "").strip()
            if not thi:
                continue
            if session.query(PoHeader).filter(PoHeader.po_number == thi).first():
                continue
            cust_name = row.get("customer_name_snapshot") or ""
            cust = get_or_create_customer(session, cust_name)
            mes = row.get("marketing_excel_date_serial") or ""
            mes_int = None
            if str(mes).strip():
                try:
                    mes_int = int(float(mes))
                except (ValueError, TypeError):
                    mes_int = None
            hdr = PoHeader(
                po_number=thi,
                customer_id=cust.id if cust else None,
                customer_name_snapshot=cust_name.strip() or None,
                brand_name_snapshot=(row.get("brand_name_snapshot") or "").strip() or None,
                order_type_label=(row.get("order_type_label") or "").strip() or None,
                po_customer_ref=(row.get("po_customer_ref") or "").strip() or None,
                marketing_excel_date_serial=mes_int,
                status="draft",
                po_category="production",
            )
            session.add(hdr)
            session.flush()
            tmin, tmax = parse_thickness_range(row.get("thickness_text"))
            etd_ser = row.get("etd_excel_serial") or ""
            etd_int = None
            if str(etd_ser).strip():
                try:
                    etd_int = int(float(etd_ser))
                except (ValueError, TypeError):
                    etd_int = None
            line_etd = excel_serial_to_date(str(etd_ser)) if etd_ser else None
            det = PoDetail(
                po_id=hdr.id,
                thi_line_ref=thi,
                material_name=(row.get("material_name") or "").strip() or None,
                thickness_text=(row.get("thickness_text") or "").strip() or None,
                thickness_min=tmin,
                thickness_max=tmax,
                emboss=(row.get("emboss") or "").strip() or None,
                vir_softness_type=(row.get("vir_softness_type") or "").strip() or None,
                color=(row.get("color") or "").strip() or None,
                softness=(row.get("softness") or "").strip() or None,
                quantity_order=dec(row.get("quantity_order")),
                unit_price=dec(row.get("unit_price")),
                color_reference=(row.get("color_reference") or "").strip() or None,
                backing=(row.get("backing") or "").strip() or None,
                model=(row.get("model") or "").strip() or None,
                style_article=(row.get("style_article") or "").strip() or None,
                rtd_text=(row.get("rtd_text") or "").strip() or None,
                etd_excel_serial=etd_int,
                line_etd=line_etd,
                stock_wh_qty=dec(row.get("stock_wh_qty")),
                balance_qty=dec(row.get("balance_qty")),
                system_reference=(row.get("system_reference") or "").strip() or None,
                detail_remark=(row.get("detail_remark") or "").strip() or None,
            )
            session.add(det)
            session.flush()
            for seq in range(1, 13):
                qk = f"delivery_{seq}_qty"
                dk = f"delivery_{seq}_date"
                qv = dec(row.get(qk))
                ds = (row.get(dk) or "").strip()
                ddate = excel_serial_to_date(ds) if ds else None
                if qv is not None or ddate is not None:
                    session.add(
                        PoDetailDelivery(
                            po_detail_id=det.id,
                            sequence_no=seq,
                            qty=qv,
                            delivery_date=ddate,
                        )
                    )
            n += 1
    session.commit()
    print("marketing SO lines inserted:", n)
    return n


def main() -> None:
    from app.db import SessionLocal

    if not CSV_DIR.is_dir():
        print("Folder tidak ada:", CSV_DIR)
        print("Set MASTER_CSV_DIR atau letakkan Master_Data_extracted di", DEFAULT_CSV)
        sys.exit(1)
    print("CSV_DIR:", CSV_DIR)
    session = SessionLocal()
    try:
        import_customers_master(session)
        sync_customers_from_marketing(session)
        import_items(session)
        import_prices(session)
        import_marketing(session)
    finally:
        session.close()


if __name__ == "__main__":
    main()
