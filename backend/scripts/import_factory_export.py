#!/usr/bin/env python3
"""
Import LIST FACTORY-EXPORT.csv ke tabel master:
- customers (is_export_customer=true)
- brands
- customer_brand_mappings
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from sqlalchemy import select

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.db import SessionLocal
from app.models import Brand, Customer, CustomerBrandMapping

CSV_PATH = Path("/tmp/LIST_FACTORY_EXPORT.csv")


def norm(s: str | None) -> str:
    return (s or "").strip()


def norm_buyer(raw: str) -> str:
    token = re.sub(r"\s+", " ", raw.upper()).strip(" ,.;")
    if token == "OIA":
        return "OIA NIKE"
    return token


def get_or_create_brand(session, buyer_name: str) -> Brand:
    row = session.scalars(select(Brand).where(Brand.name == buyer_name)).first()
    if row:
        return row
    row = session.scalars(select(Brand).where(Brand.code == buyer_name)).first()
    if row:
        if not row.name:
            row.name = buyer_name
        return row
    row = Brand(code=buyer_name, name=buyer_name)
    session.add(row)
    session.flush()
    return row


def main() -> None:
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV tidak ditemukan: {CSV_PATH}")

    session = SessionLocal()
    touched = inserted = map_inserted = brand_inserted = 0
    try:
        known_customers = {int(x) for x in session.scalars(select(Customer.id)).all()}
        known_brands = {int(x) for x in session.scalars(select(Brand.id)).all()}
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter=";"):
                code = norm(row.get("KODE SYSTEM"))
                name = norm(row.get("NAMA"))
                buyer = norm_buyer(norm(row.get("BUYER")))
                if not code or not name or not buyer:
                    continue
                if code.upper() == "NOTE":
                    continue

                customer = session.scalars(select(Customer).where(Customer.code == code)).first()
                if customer is None:
                    customer = session.scalars(select(Customer).where(Customer.name == name)).first()

                ship_addr = norm(row.get("ALAMAT PADA INVOICE/ALAMAT PENGIRIMAN"))
                bill_to = norm(row.get("BILL TO"))
                bill_addr = norm(row.get("ALAMAT BILL TO"))
                attn = norm(row.get("ATTN"))
                country = norm(row.get("NEGARA"))
                phone = norm(row.get("TELEPHONE"))
                bill_phone = norm(row.get("TLP BILL TO"))
                email = norm(row.get("EMAIL BILL TO"))
                final_phone = phone or bill_phone or None
                final_address = ship_addr or bill_addr or None
                billing_address = bill_addr or ship_addr or None
                contact = attn or None
                remark_parts = []
                if bill_to:
                    remark_parts.append(f"Bill To: {bill_to}")
                remark = " | ".join(remark_parts) if remark_parts else None

                if customer is None:
                    customer = Customer(
                        code=code,
                        name=name,
                        country=country or None,
                        address=final_address,
                        billing_address=billing_address,
                        contact_person=contact,
                        phone=final_phone,
                        email=email or None,
                        remark=remark,
                        is_active=True,
                        is_export_customer=True,
                    )
                    session.add(customer)
                    session.flush()
                else:
                    customer.code = code or customer.code
                    customer.name = name
                    customer.country = country or customer.country
                    customer.address = final_address or customer.address
                    customer.billing_address = billing_address or customer.billing_address
                    customer.contact_person = contact or customer.contact_person
                    customer.phone = final_phone or customer.phone
                    customer.email = email or customer.email
                    customer.remark = remark or customer.remark
                    customer.is_export_customer = True
                    customer.is_active = True
                    session.flush()

                touched += 1
                if customer.id not in known_customers:
                    inserted += 1
                    known_customers.add(int(customer.id))

                brand = get_or_create_brand(session, buyer)
                if brand.id not in known_brands:
                    brand_inserted += 1
                    known_brands.add(int(brand.id))
                exists = session.scalars(
                    select(CustomerBrandMapping).where(
                        CustomerBrandMapping.customer_id == customer.id,
                        CustomerBrandMapping.brand_id == brand.id,
                    )
                ).first()
                if not exists:
                    session.add(
                        CustomerBrandMapping(
                            customer_id=customer.id,
                            brand_id=brand.id,
                            is_default=False,
                        )
                    )
                    map_inserted += 1

        session.commit()
        print(f"CSV: {CSV_PATH}")
        print(f"Customers touched: {touched}")
        print(f"Customers inserted: {inserted}")
        print(f"Brands inserted: {brand_inserted}")
        print(f"Customer-Brand mappings inserted: {map_inserted}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
