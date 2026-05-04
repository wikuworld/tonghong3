#!/usr/bin/env python3
"""
Import LIST FACTORY-LOKAL.csv ke tabel master:
- customers
- brands
- customer_brand_mappings

Jalankan (di container backend-dev):
  python scripts/import_factory_lokal.py

Opsional override path:
  FACTORY_LOKAL_CSV=/app/dokumentasi/LIST FACTORY-LOKAL.csv python scripts/import_factory_lokal.py
"""

from __future__ import annotations

import csv
import os
import re
import sys
from pathlib import Path

from sqlalchemy import select

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.db import SessionLocal
from app.models import Brand, Customer, CustomerBrandMapping


DEFAULT_CSV = Path("/app/dokumentasi/LIST FACTORY-LOKAL.csv")
CSV_PATH = Path(os.environ.get("FACTORY_LOKAL_CSV", str(DEFAULT_CSV)))


def _clean(text: str | None) -> str:
    if text is None:
        return ""
    return str(text).strip()


def _norm_buyer_token(text: str) -> str:
    token = re.sub(r"\s+", " ", text.upper()).strip(" ,.;")
    return token


def _split_buyers(raw: str | None) -> list[str]:
    if not raw:
        return []
    out: list[str] = []
    for part in str(raw).split(","):
        token = _norm_buyer_token(part)
        if token and token not in out:
            out.append(token)
    return out


def _pick_tax_id(row: dict[str, str]) -> str | None:
    npwp_baru = _clean(row.get("NPWP baru"))
    npwp = _clean(row.get("NPWP"))
    if npwp_baru and npwp_baru.upper() != "CLOSE":
        return npwp_baru
    if npwp and npwp.upper() != "CLOSE":
        return npwp
    return None


def _pick_customer_address(row: dict[str, str]) -> tuple[str | None, str | None]:
    addr_npwp = _clean(row.get("ALAMAT PADA NPWP"))
    addr_inv = _clean(row.get("ALAMAT PADA INVOICE"))
    # Di aplikasi saat ini address utama kita pakai alamat invoice.
    address = addr_inv or addr_npwp or None
    billing_address = addr_npwp or addr_inv or None
    return address, billing_address


def _upsert_customer(session, row: dict[str, str]) -> Customer | None:
    code = _clean(row.get("KODE SYSTEM")) or None
    name = _clean(row.get("NAMA")) or None
    if not name:
        return None

    customer = None
    if code:
        customer = session.scalars(select(Customer).where(Customer.code == code)).first()
    if customer is None:
        customer = session.scalars(select(Customer).where(Customer.name == name)).first()

    tax_id = _pick_tax_id(row)
    address, billing_address = _pick_customer_address(row)

    kppbc = _clean(row.get("KPPBC"))
    kode_customs = _clean(row.get("KODE"))
    no_izin = _clean(row.get("NO. IZIN"))
    nitku = _clean(row.get("NITKU"))
    note_parts = []
    if kppbc:
        note_parts.append(f"KPPBC: {kppbc}")
    if kode_customs:
        note_parts.append(f"Kode Bea Cukai: {kode_customs}")
    if no_izin:
        note_parts.append(f"No Izin: {no_izin}")
    if nitku and nitku.upper() != "CLOSE":
        note_parts.append(f"NITKU: {nitku}")
    remark = " | ".join(note_parts) if note_parts else None

    if customer is None:
        customer = Customer(
            code=code,
            name=name,
            tax_id=tax_id,
            customs_office_code=kode_customs or None,
            address=address,
            billing_address=billing_address,
            remark=remark,
            is_active=True,
            is_export_customer=False,
        )
        session.add(customer)
        session.flush()
        return customer

    customer.code = code or customer.code
    customer.name = name
    customer.tax_id = tax_id
    customer.customs_office_code = kode_customs or customer.customs_office_code
    customer.address = address or customer.address
    customer.billing_address = billing_address or customer.billing_address
    customer.remark = remark or customer.remark
    customer.is_active = True
    return customer


def _get_or_create_brand(session, buyer_name: str) -> Brand:
    brand = session.scalars(select(Brand).where(Brand.name == buyer_name)).first()
    if brand:
        return brand
    brand = session.scalars(select(Brand).where(Brand.code == buyer_name)).first()
    if brand:
        if not brand.name:
            brand.name = buyer_name
        return brand
    brand = Brand(code=buyer_name, name=buyer_name)
    session.add(brand)
    session.flush()
    return brand


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV tidak ditemukan: {CSV_PATH}")

    session = SessionLocal()
    inserted_customers = 0
    touched_customers = 0
    inserted_brands = 0
    inserted_mappings = 0
    try:
        existing_customer_ids = {c.id for c in session.scalars(select(Customer.id)).all()}
        existing_brand_ids = {b.id for b in session.scalars(select(Brand.id)).all()}

        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                customer = _upsert_customer(session, row)
                if customer is None:
                    continue
                touched_customers += 1
                if customer.id not in existing_customer_ids:
                    inserted_customers += 1
                    existing_customer_ids.add(customer.id)

                buyer_tokens = _split_buyers(row.get("BUYER"))
                for buyer in buyer_tokens:
                    brand = _get_or_create_brand(session, buyer)
                    if brand.id not in existing_brand_ids:
                        inserted_brands += 1
                        existing_brand_ids.add(brand.id)
                    exists = session.scalars(
                        select(CustomerBrandMapping).where(
                            CustomerBrandMapping.customer_id == customer.id,
                            CustomerBrandMapping.brand_id == brand.id,
                        )
                    ).first()
                    if exists:
                        continue
                    session.add(
                        CustomerBrandMapping(
                            customer_id=customer.id,
                            brand_id=brand.id,
                            is_default=False,
                        )
                    )
                    inserted_mappings += 1

        session.commit()
        print(f"CSV: {CSV_PATH}")
        print(f"Customers touched: {touched_customers}")
        print(f"Customers inserted: {inserted_customers}")
        print(f"Brands inserted: {inserted_brands}")
        print(f"Customer-Brand mappings inserted: {inserted_mappings}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
