"""
Demo Script: Insert Data Korelasi Customer → Brand → Buyer → BuyerPrice → PO

Setup data untuk демонстрация alur:
1. Customers (PT yang membeli)
2. Brands (NIKE, ADIDAS, NB)
3. CustomerBrandMappings (Customer boleh pakai brand apa)
4. BrandBuyerMaps (Brand boleh pakai buyer code apa)
5. BuyerPriceLists + BuyerPriceSheetRows (sheet harga)
6. MasterItems (referensi material untuk autofill)
7. PO Headers + PO Details (dengan price resolution)

Run: cd backend && python -m scripts.demo_correlation_data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decimal import Decimal
from datetime import date

from sqlalchemy import select
from app.db import SessionLocal, engine
from app.models import (
    Customer,
    Brand,
    CustomerBrandMapping,
    BrandBuyerMap,
    BuyerPriceList,
    BuyerPriceSheetRow,
    MasterItem,
    PoHeader,
    PoDetail,
)
from app.services.buyer_price_resolve import resolve_unit_price_for_buyer


def clean_demo_data(db):
    """Hapus semua demo data yang sudah ada."""
    print("\n🧹 Membersihkan data demo sebelumnya...")
    
    # Hapus PO details dan headers
    db.query(PoDetail).filter(PoDetail.id > 0).delete()
    db.query(PoHeader).filter(PoHeader.id > 0).delete()
    
    # Hapus MasterItems
    db.query(MasterItem).filter(MasterItem.id > 0).delete()
    
    # Hapus BuyerPriceSheetRows
    db.query(BuyerPriceSheetRow).filter(BuyerPriceSheetRow.id > 0).delete()
    
    # Hapus BuyerPriceLists
    db.query(BuyerPriceList).filter(BuyerPriceList.id > 0).delete()
    
    # Hapus BrandBuyerMaps
    db.query(BrandBuyerMap).filter(BrandBuyerMap.id > 0).delete()
    
    # Hapus CustomerBrandMappings
    db.query(CustomerBrandMapping).filter(CustomerBrandMapping.id > 0).delete()
    
    # Hapus Brands
    db.query(Brand).filter(Brand.id > 0).delete()
    
    # Hapus Customers (kecuali id=1)
    db.query(Customer).filter(Customer.id > 1).delete()
    
    db.commit()
    print("   ✓ Data demo sebelumnya dihapus")


def create_customers(db):
    """1. Buat Customers."""
    print("\n📦 Step 1: Membuat Customers...")
    
    customers = [
        Customer(
            code="DEMO001",
            name="PT Tong Hong Tannery Indonesia",
            contact_person="Budi Santoso",
            email="budi@tonghong.com",
            phone="021-1234567",
            address="Jl. Industri Raya No. 1, Jakarta",
            is_export_customer=True,
        ),
        Customer(
            code="DEMO002",
            name="PT Bandung Leather Goods",
            contact_person="Siti Rahayu",
            email="siti@bandungleather.co.id",
            phone="022-7654321",
            address="Jl. Braga No. 88, Bandung",
            is_export_customer=False,
        ),
    ]
    
    for c in customers:
        existing = db.scalars(select(Customer).where(Customer.code == c.code)).first()
        if not existing:
            db.add(c)
    
    db.commit()
    
    result = db.scalars(select(Customer).where(Customer.code.in_(["DEMO001", "DEMO002"]))).all()
    for c in result:
        print(f"   ✓ Customer: {c.code} - {c.name} (ID: {c.id})")
    
    return result


def create_brands(db):
    """2. Buat Brands."""
    print("\n🏷️  Step 2: Membuat Brands...")
    
    brands = [
        Brand(code="NIKE", name="Nike Sportswear"),
        Brand(code="ADIDAS", name="Adidas Originals"),
        Brand(code="NB", name="New Balance"),
        Brand(code="UA", name="Under Armour"),
    ]
    
    for b in brands:
        existing = db.scalars(select(Brand).where(Brand.code == b.code)).first()
        if not existing:
            db.add(b)
    
    db.commit()
    
    result = db.scalars(select(Brand).where(Brand.code.in_(["NIKE", "ADIDAS", "NB", "UA"]))).all()
    for b in result:
        print(f"   ✓ Brand: {b.code} - {b.name} (ID: {b.id})")
    
    return result


def create_customer_brand_mappings(db, customers, brands):
    """3. Buat CustomerBrandMappings."""
    print("\n🔗 Step 3: Membuat Customer-Brand Mappings...")
    
    # DEMO001 boleh pakai NIKE, ADIDAS, NB
    # DEMO002 boleh pakai NB, UA
    mappings = [
        # Customer: PT Tong Hong (DEMO001)
        {"customer_code": "DEMO001", "brand_code": "NIKE", "is_default": True},
        {"customer_code": "DEMO001", "brand_code": "ADIDAS", "is_default": False},
        {"customer_code": "DEMO001", "brand_code": "NB", "is_default": False},
        # Customer: PT Bandung Leather (DEMO002)
        {"customer_code": "DEMO002", "brand_code": "NB", "is_default": True},
        {"customer_code": "DEMO002", "brand_code": "UA", "is_default": False},
    ]
    
    customer_map = {c.code: c for c in customers}
    brand_map = {b.code: b for b in brands}
    
    for m in mappings:
        customer = customer_map.get(m["customer_code"])
        brand = brand_map.get(m["brand_code"])
        if not customer or not brand:
            continue
        
        existing = db.scalars(
            select(CustomerBrandMapping).where(
                CustomerBrandMapping.customer_id == customer.id,
                CustomerBrandMapping.brand_id == brand.id,
            )
        ).first()
        
        if not existing:
            mapping = CustomerBrandMapping(
                customer_id=customer.id,
                brand_id=brand.id,
                is_default=m["is_default"],
            )
            db.add(mapping)
            print(f"   ✓ {customer.code} → {brand.code} (default: {m['is_default']})")
    
    db.commit()


def create_brand_buyer_maps(db, brands):
    """4. Buat BrandBuyerMaps."""
    print("\n📋 Step 4: Membuat Brand-Buyer Mappings...")
    
    # Setiap brand punya buyer code tertentu
    buyer_maps = [
        {"brand_code": "NIKE", "buyer_codes": ["NIKE"]},
        {"brand_code": "ADIDAS", "buyer_codes": ["ADI", "ADIDAS"]},
        {"brand_code": "NB", "buyer_codes": ["NB", "NBID"]},
        {"brand_code": "UA", "buyer_codes": ["UA"]},
    ]
    
    brand_map = {b.code: b for b in brands}
    
    for bm in buyer_maps:
        brand = brand_map.get(bm["brand_code"])
        if not brand:
            continue
        
        for buyer_code in bm["buyer_codes"]:
            existing = db.scalars(
                select(BrandBuyerMap).where(
                    BrandBuyerMap.brand_id == brand.id,
                    BrandBuyerMap.buyer_code == buyer_code,
                )
            ).first()
            
            if not existing:
                map_row = BrandBuyerMap(
                    brand_id=brand.id,
                    buyer_code=buyer_code,
                )
                db.add(map_row)
                print(f"   ✓ Brand {brand.code} → Buyer: {buyer_code}")
    
    db.commit()


def create_buyer_price_lists(db, brands):
    """5. Buat BuyerPriceLists + BuyerPriceSheetRows."""
    print("\n💰 Step 5: Membuat Buyer Price Lists + Sheet Rows...")
    
    brand_map = {b.code: b for b in brands}
    
    # Price list untuk NB (New Balance)
    nb_brand = brand_map.get("NB")
    if nb_brand:
        nb_list = BuyerPriceList(
            buyer_code="NB",
            currency="USD",
            title="New Balance Price List Q2 2026",
            period_label="Q2 2026",
            period_start=date(2026, 4, 1),
            period_end=date(2026, 6, 30),
            source_label="From NB Corporate Q2 2026",
            meta_json={"column_keys": ["NO", "ITEM", "THICKNESS", "PRICE", "PRICE_BLACK", "PRICE_FLUORESCENT"]},
        )
        db.add(nb_list)
        db.flush()
        
        nb_rows = [
            {"NO": "1", "ITEM": "COW SPORT", "THICKNESS": "1.2-1.4", "PRICE": "12.50", "PRICE_BLACK": "11.00", "PRICE_FLUORESCENT": "14.50"},
            {"NO": "2", "ITEM": "COW SPORT", "THICKNESS": "1.0-1.2", "PRICE": "11.50", "PRICE_BLACK": "10.00", "PRICE_FLUORESCENT": "13.50"},
            {"NO": "3", "ITEM": "SUEDE SPLIT", "THICKNESS": "0.9-1.1", "PRICE": "10.00", "PRICE_BLACK": "9.00", "PRICE_FLUORESCENT": "12.00"},
            {"NO": "4", "ITEM": "SUEDE SPLIT", "THICKNESS": "1.0-1.2", "PRICE": "10.50", "PRICE_BLACK": "9.50", "PRICE_FLUORESCENT": "12.50"},
            {"NO": "5", "ITEM": "PEBBLE EMBOSS", "THICKNESS": "1.0-1.2", "PRICE": "13.00", "PRICE_BLACK": "12.00", "PRICE_FLUORESCENT": "15.00"},
            {"NO": "6", "ITEM": "NUBUCK", "THICKNESS": "1.2-1.4", "PRICE": "14.00", "PRICE_BLACK": "13.00", "PRICE_FLUORESCENT": "16.00"},
        ]
        
        for i, cells in enumerate(nb_rows):
            row = BuyerPriceSheetRow(
                list_id=nb_list.id,
                row_number=i,
                cells=cells,
            )
            db.add(row)
        
        print(f"   ✓ BuyerPriceList: NB (ID: {nb_list.id}) dengan {len(nb_rows)} rows")
    
    # Price list untuk ADIDAS
    adidas_brand = brand_map.get("ADIDAS")
    if adidas_brand:
        adidas_list = BuyerPriceList(
            buyer_code="ADI",
            currency="USD",
            title="Adidas Price List April 2026",
            period_label="April 2026",
            period_start=date(2026, 4, 1),
            period_end=date(2026, 4, 30),
            source_label="From Adidas APAC Q2",
            meta_json={"column_keys": ["NO", "ITEM", "THICKNESS", "PRICE", "PRICE_BLACK", "PRICE_FLUORESCENT"]},
        )
        db.add(adidas_list)
        db.flush()
        
        adidas_rows = [
            {"NO": "1", "ITEM": "COW SPORT", "THICKNESS": "1.2-1.4", "PRICE": "13.00", "PRICE_BLACK": "12.00", "PRICE_FLUORESCENT": "15.00"},
            {"NO": "2", "ITEM": "SUEDE", "THICKNESS": "0.9-1.1", "PRICE": "11.00", "PRICE_BLACK": "10.00", "PRICE_FLUORESCENT": "13.00"},
            {"NO": "3", "ITEM": "NUBUCK", "THICKNESS": "1.2-1.4", "PRICE": "15.00", "PRICE_BLACK": "14.00", "PRICE_FLUORESCENT": "17.00"},
        ]
        
        for i, cells in enumerate(adidas_rows):
            row = BuyerPriceSheetRow(
                list_id=adidas_list.id,
                row_number=i,
                cells=cells,
            )
            db.add(row)
        
        print(f"   ✓ BuyerPriceList: ADI (ID: {adidas_list.id}) dengan {len(adidas_rows)} rows")
    
    db.commit()


def create_master_items(db):
    """6. Buat MasterItems."""
    print("\n📁 Step 6: Membuat Master Items...")
    
    items = [
        MasterItem(
            item_code="FG-NB-001",
            material_name="COW SPORT",
            thickness_mm=Decimal("1.3"),
            thickness_range="1.2-1.4",
            color="BLACK",
            emboss="SPORT",
            softness="Soft",
            color_reference="NB-BLK-CSPT-001",
            backing="PU COATED",
            quantity_order_default=Decimal("5000"),
            style_article="NB-2026-A",
            model="Classic 574",
            category="Sport",
            exim_material_code="4107.12.00",
        ),
        MasterItem(
            item_code="FG-NB-002",
            material_name="SUEDE SPLIT",
            thickness_mm=Decimal("1.0"),
            thickness_range="0.9-1.1",
            color="BLACK",
            emboss="NORMAL",
            softness="Extra Soft",
            color_reference="NB-BLK-SD-001",
            backing="NONE",
            quantity_order_default=Decimal("3000"),
            style_article="NB-2026-B",
            model="Fresh Foam",
            category="Running",
            exim_material_code="4107.12.00",
        ),
        MasterItem(
            item_code="FG-NB-003",
            material_name="PEBBLE EMBOSS",
            thickness_mm=Decimal("1.1"),
            thickness_range="1.0-1.2",
            color="BLACK",
            emboss="PEBBLE",
            softness="Soft",
            color_reference="NB-BLK-PB-001",
            backing="PU COATED",
            quantity_order_default=Decimal("4000"),
            style_article="NB-2026-C",
            model="Trail Running",
            category="Outdoor",
            exim_material_code="4107.12.00",
        ),
        MasterItem(
            item_code="FG-NB-004",
            material_name="NUBUCK",
            thickness_mm=Decimal("1.3"),
            thickness_range="1.2-1.4",
            color="BLACK",
            emboss="NUBUCK",
            softness="Medium",
            color_reference="NB-BLK-NB-001",
            backing="NONE",
            quantity_order_default=Decimal("2500"),
            style_article="NB-2026-D",
            model="Casual",
            category="Lifestyle",
            exim_material_code="4114.10.00",
        ),
        MasterItem(
            item_code="FG-NB-005",
            material_name="COW SPORT",
            thickness_mm=Decimal("1.3"),
            thickness_range="1.2-1.4",
            color="FLUO-YELLOW",
            emboss="SPORT",
            softness="Soft",
            color_reference="NB-FLUO-CSPT-001",
            backing="PU COATED",
            quantity_order_default=Decimal("2000"),
            style_article="NB-2026-E",
            model="Sport Performance",
            category="Sport",
            exim_material_code="4107.12.00",
        ),
        MasterItem(
            item_code="FG-AD-001",
            material_name="COW SPORT",
            thickness_mm=Decimal("1.3"),
            thickness_range="1.2-1.4",
            color="BLACK",
            emboss="SPORT",
            softness="Soft",
            color_reference="ADI-BLK-CSPT-001",
            backing="PU COATED",
            quantity_order_default=Decimal("6000"),
            style_article="ADI-2026-A",
            model="Ultraboost",
            category="Running",
            exim_material_code="4107.12.00",
        ),
        MasterItem(
            item_code="FG-AD-002",
            material_name="SUEDE",
            thickness_mm=Decimal("1.0"),
            thickness_range="0.9-1.1",
            color="BLACK",
            emboss="NORMAL",
            softness="Soft",
            color_reference="ADI-BLK-SD-001",
            backing="NONE",
            quantity_order_default=Decimal("3500"),
            style_article="ADI-2026-B",
            model="Stan Smith",
            category="Lifestyle",
            exim_material_code="4107.12.00",
        ),
    ]
    
    for item in items:
        existing = db.scalars(select(MasterItem).where(MasterItem.item_code == item.item_code)).first()
        if not existing:
            db.add(item)
            print(f"   ✓ MasterItem: {item.item_code} - {item.material_name} ({item.thickness_range})")
    
    db.commit()


def create_po_with_price_resolution(db, customers, brands):
    """7. Buat PO dengan price resolution."""
    print("\n📝 Step 7: Membuat PO dengan Price Resolution...")
    
    customer_map = {c.code: c for c in customers}
    brand_map = {b.code: b for b in brands}
    
    # PO 1: PT Tong Hong → NB → buyer NB
    customer1 = customer_map.get("DEMO001")
    nb_brand = brand_map.get("NB")
    
    if customer1 and nb_brand:
        po1 = PoHeader(
            customer_id=customer1.id,
            customer_code=customer1.code,
            brand_id=nb_brand.id,
            brand_name_snapshot=nb_brand.name,
            customer_name_snapshot=customer1.name,
            buyer="NB",
            order_date=date(2026, 4, 17),
            etd=date(2026, 5, 15),
            po_category="production",
            status="draft",
            remark="Demo PO untuk korelasi Customer-Brand-Buyer-Price",
        )
        db.add(po1)
        db.flush()
        
        # Detail 1: COW SPORT BLACK 1.2-1.4
        result1 = resolve_unit_price_for_buyer(
            db,
            buyer_code="NB",
            material_name="COW SPORT",
            color="BLACK",
            thickness_text="1.2-1.4",
            color_family="black",
        )
        
        detail1 = PoDetail(
            po_id=po1.id,
            material_name="COW SPORT",
            color="BLACK",
            color_family="black",
            thickness_text="1.2-1.4",
            thickness_min=Decimal("1.2"),
            thickness_max=Decimal("1.4"),
            quantity_order=Decimal("5000"),
            unit_price=result1.get("unit_price"),
            style_article="NB-2026-A",
            line_etd=date(2026, 5, 15),
            thi_line_ref="NB-001",
        )
        db.add(detail1)
        print(f"   ✓ PO1 Header: {po1.id} (Customer: {customer1.code}, Brand: {nb_brand.code}, Buyer: NB)")
        print(f"     └─ Detail 1: COW SPORT BLACK → Price: {result1.get('unit_price')} (matched: {result1.get('matched')}, score: {result1.get('score')})")
        
        # Detail 2: SUEDE SPLIT BLACK 0.9-1.1
        result2 = resolve_unit_price_for_buyer(
            db,
            buyer_code="NB",
            material_name="SUEDE SPLIT",
            color="BLACK",
            thickness_text="0.9-1.1",
            color_family="black",
        )
        
        detail2 = PoDetail(
            po_id=po1.id,
            material_name="SUEDE SPLIT",
            color="BLACK",
            color_family="black",
            thickness_text="0.9-1.1",
            thickness_min=Decimal("0.9"),
            thickness_max=Decimal("1.1"),
            quantity_order=Decimal("3000"),
            unit_price=result2.get("unit_price"),
            style_article="NB-2026-B",
            line_etd=date(2026, 5, 20),
            thi_line_ref="NB-002",
        )
        db.add(detail2)
        print(f"     └─ Detail 2: SUEDE SPLIT BLACK → Price: {result2.get('unit_price')} (matched: {result2.get('matched')}, score: {result2.get('score')})")
        
        # Detail 3: FLUORESCENT
        result3 = resolve_unit_price_for_buyer(
            db,
            buyer_code="NB",
            material_name="COW SPORT",
            color="FLUO-YELLOW",
            thickness_text="1.2-1.4",
            color_family="fluorescent",
        )
        
        detail3 = PoDetail(
            po_id=po1.id,
            material_name="COW SPORT",
            color="FLUO-YELLOW",
            color_family="fluorescent",
            thickness_text="1.2-1.4",
            thickness_min=Decimal("1.2"),
            thickness_max=Decimal("1.4"),
            quantity_order=Decimal("2000"),
            unit_price=result3.get("unit_price"),
            style_article="NB-2026-E",
            line_etd=date(2026, 5, 25),
            thi_line_ref="NB-003",
        )
        db.add(detail3)
        print(f"     └─ Detail 3: COW SPORT FLUORESCENT → Price: {result3.get('unit_price')} (matched: {result3.get('matched')}, score: {result3.get('score')})")
    
    # PO 2: PT Tong Hong → ADIDAS → buyer ADI
    adidas_brand = brand_map.get("ADIDAS")
    
    if customer1 and adidas_brand:
        po2 = PoHeader(
            customer_id=customer1.id,
            customer_code=customer1.code,
            brand_id=adidas_brand.id,
            brand_name_snapshot=adidas_brand.name,
            customer_name_snapshot=customer1.name,
            buyer="ADI",
            order_date=date(2026, 4, 17),
            etd=date(2026, 6, 1),
            po_category="production",
            status="draft",
            remark="Demo PO untuk Adidas",
        )
        db.add(po2)
        db.flush()
        
        result4 = resolve_unit_price_for_buyer(
            db,
            buyer_code="ADI",
            material_name="COW SPORT",
            color="BLACK",
            thickness_text="1.2-1.4",
            color_family="black",
        )
        
        detail4 = PoDetail(
            po_id=po2.id,
            material_name="COW SPORT",
            color="BLACK",
            color_family="black",
            thickness_text="1.2-1.4",
            thickness_min=Decimal("1.2"),
            thickness_max=Decimal("1.4"),
            quantity_order=Decimal("6000"),
            unit_price=result4.get("unit_price"),
            style_article="ADI-2026-A",
            line_etd=date(2026, 6, 1),
            thi_line_ref="ADI-001",
        )
        db.add(detail4)
        print(f"   ✓ PO2 Header: {po2.id} (Customer: {customer1.code}, Brand: {adidas_brand.code}, Buyer: ADI)")
        print(f"     └─ Detail: COW SPORT BLACK → Price: {result4.get('unit_price')} (matched: {result4.get('matched')}, score: {result4.get('score')})")
    
    db.commit()
    print("\n   ✓ Semua PO dan detail berhasil dibuat!")


def main():
    """Main function untuk insert demo data."""
    print("=" * 70)
    print("🎯 DEMO: Insert Data Korelasi Customer → Brand → Buyer → Price → PO")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        # Step 0: Clean existing demo data
        clean_demo_data(db)
        
        # Step 1: Create Customers
        customers = create_customers(db)
        
        # Step 2: Create Brands
        brands = create_brands(db)
        
        # Step 3: Create Customer-Brand Mappings
        create_customer_brand_mappings(db, customers, brands)
        
        # Step 4: Create Brand-Buyer Maps
        create_brand_buyer_maps(db, brands)
        
        # Step 5: Create Buyer Price Lists
        create_buyer_price_lists(db, brands)
        
        # Step 6: Create Master Items
        create_master_items(db)
        
        # Step 7: Create PO with Price Resolution
        create_po_with_price_resolution(db, customers, brands)
        
        print("\n" + "=" * 70)
        print("✅ SEMUA DATA DEMO BERHASIL DIINSERT!")
        print("=" * 70)
        print("\n📊 Summary:")
        print(f"   - Customers: 2 (DEMO001, DEMO002)")
        print(f"   - Brands: 4 (NIKE, ADIDAS, NB, UA)")
        print(f"   - Customer-Brand Mappings: 5")
        print(f"   - Brand-Buyer Maps: 6")
        print(f"   - Buyer Price Lists: 2 (NB, ADI)")
        print(f"   - Buyer Price Sheet Rows: 9")
        print(f"   - Master Items: 7")
        print(f"   - PO Headers: 2")
        print(f"   - PO Details: 4")
        print("\n💡 Test korelasi:")
        print("   1. Buka http://localhost:5173/admin/customers → Lihat Customer")
        print("   2. Buka http://localhost:5173/admin/brands → Lihat Brand")
        print("   3. Buka http://localhost:5173/admin/buyer-prices → Lihat Price List")
        print("   4. Buka http://localhost:5173/admin/po → Lihat PO dengan harga auto")
        print("   5. Buka http://localhost:5173/admin/master-items → Lihat Master Items")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
