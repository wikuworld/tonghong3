"""
Fix Script: Generate po_number and po_customer_ref for empty PO records

Usage: cd backend && python -m scripts.fix_empty_po_numbers
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models import PoHeader
from app.services.numbering import next_number


def fix_empty_po_numbers():
    db = SessionLocal()
    
    try:
        # Find all PO with empty po_number
        empty_po_numbers = db.query(PoHeader).filter(
            (PoHeader.po_number == None) | (PoHeader.po_number == '')
        ).all()
        
        print(f"\n📋 Found {len(empty_po_numbers)} PO with empty po_number")
        
        for po in empty_po_numbers:
            old_po_number = po.po_number
            new_po_number = next_number(db, "SO", "SO")
            po.po_number = new_po_number
            print(f"   ✓ PO ID {po.id}: '{old_po_number}' → '{new_po_number}'")
        
        db.commit()
        print(f"\n✅ Fixed {len(empty_po_numbers)} PO numbers")
        
        # Find all PO with empty po_customer_ref
        empty_customer_refs = db.query(PoHeader).filter(
            (PoHeader.po_customer_ref == None) | (PoHeader.po_customer_ref == '')
        ).all()
        
        print(f"\n📋 Found {len(empty_customer_refs)} PO with empty po_customer_ref")
        
        for po in empty_customer_refs:
            old_ref = po.po_customer_ref
            # Generate default customer ref: PO-{po_number}
            if po.po_number:
                po.po_customer_ref = f"PO-{po.po_number}"
            else:
                po.po_customer_ref = f"PO-{po.id}"
            print(f"   ✓ PO ID {po.id}: '{old_ref}' → '{po.po_customer_ref}'")
        
        db.commit()
        print(f"\n✅ Fixed {len(empty_customer_refs)} PO customer references")
        
        # Summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        
        total = db.query(PoHeader).count()
        with_po_number = db.query(PoHeader).filter(
            (PoHeader.po_number != None) & (PoHeader.po_number != '')
        ).count()
        with_customer_ref = db.query(PoHeader).filter(
            (PoHeader.po_customer_ref != None) & (PoHeader.po_customer_ref != '')
        ).count()
        
        print(f"Total PO: {total}")
        print(f"With po_number: {with_po_number}")
        print(f"With po_customer_ref: {with_customer_ref}")
        print(f"Still empty po_number: {total - with_po_number}")
        print(f"Still empty po_customer_ref: {total - with_customer_ref}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    fix_empty_po_numbers()
