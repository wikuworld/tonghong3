# Tonghong ERP - Comprehensive Enhancement Design

**Date:** 2026-04-15
**Project:** Tonghong ERP - Full Change Request Implementation
**Author:** AI Assistant

---

## Executive Summary

CR Tonghong mencakup 19 enhancement items yang tersebar di 11 modul. Dokumen ini membagi implementasi menjadi **4 phase** berdasarkan effort dan dependensi.

---

## Phase Breakdown

### Phase 1: Quick Wins (1-2 sprint)
Perubahan low-effort, minimal risk.

### Phase 2: Form Enhancements (2-3 sprint)
Form improvements dan UI enhancements.

### Phase 3: Pricing Engine (3-4 sprint)
Rule-based pricing system dengan kompleksitas tinggi.

### Phase 4: Workflow & Accounting (4+ sprint)
Marketing-PPIC workflow, accounting mapping, dan advanced features.

---

## Phase 1: Quick Wins

### 1.1 Customer - Field "Jabatan" (Position)

**Backend:**
```python
# models.py - Customer
position: Mapped[Optional[str]] = mapped_column(String(120))

# schemas.py
position: Optional[str] = None
```

**Frontend:** Tambah field di CustomersPage.vue form

### 1.2 PO - Dropdown Kategori: SubKon, Retur

**Status quo:** Kategori adalah dropdown dengan opsi production/sample/claim/return/subcont/suede

**Enhancement:** Tambah opsi yang lebih descriptive:
- SubKon (display) → subcont (value)
- Retur (display) → return (value)

**Frontend:** Update label di PO form:
```vue
<el-option :label="t('status.subkon')" value="subcont" />
<el-option :label="t('status.retur')" value="return" />
```

### 1.3 PO - SubKon/Retur → Harga Free Text

**Business Logic:**
```javascript
function handleCategoryChange(category) {
  if (category === 'subcont' || category === 'return') {
    // Disable auto-pricing, enable manual input
    formModel.autoPricingEnabled = false
    formModel.unit_price_input = null
  } else {
    // Enable auto-pricing
    formModel.autoPricingEnabled = true
  }
}
```

### 1.4 Exchange Rates - Tanggal Berlaku (Start-End)

**Backend:**
```python
# models.py - ExchangeRate
valid_from: Mapped[Optional[date]] = mapped_column(Date)
valid_to: Mapped[Optional[date]] = mapped_column(Date)

# schemas.py
valid_from: Optional[date] = None
valid_to: Optional[date] = None
```

**Frontend:** Tambah 2 field date picker di ExchangeRatePage

### 1.5 PO - Tampilkan "No PO Customer" di Table

**Frontend:** Tambah kolom di PurchaseOrderPage table:
```vue
<el-table-column prop="po_customer_ref" label="No. PO Customer" width="150" />
```

### 1.6 PO - Kelembutan (Softness) Dropdown

**Frontend:** Ubah softness input ke dropdown:
```vue
<el-select v-model="formModel.softness">
  <el-option label="Soft" value="Soft" />
  <el-option label="Medium" value="Medium" />
  <el-option label="Hard" value="Hard" />
  <!-- atau sesuai daftar dari database -->
</el-select>
```

### 1.7 PO - Remove Field Pabean (AJU)

**Backend:**
```python
# Hapus field dari model
# customs_declaration_id tetap ada tapi hidden di PO
```

**Frontend:**
- Hapus field customs_declaration_id dari PO form
- Pertahankan data existing di database ( jangan migrate drop)

---

## Phase 2: Form Enhancements

### 2.1 Master Items - Thickness Format Range

**Current:** `thickness_mm` (Decimal, single value)

**New:** `thickness_range` (String, format "1.2-1.4")

**Backend:**
```python
# models.py - MasterItem
thickness_range: Mapped[Optional[str]] = mapped_column(String(80))

# Parse helpers
def parse_thickness_range(range_str):
    """'1.2-1.4' -> (1.2, 1.4)"""
    if not range_str: return (None, None)
    parts = range_str.split('-')
    return (float(parts[0]), float(parts[1])) if len(parts) == 2 else (None, None)
```

**Frontend:** Text input dengan validation format "X.X-X.X"

### 2.2 Master Items - Export/Import Excel

**Backend API:**
```python
@router.post("/masters/items/export")
async def export_master_items():
    # Generate Excel from master_items table
    pass

@router.post("/masters/items/import")
async def import_master_items(file: UploadFile):
    # Parse Excel, validate, bulk insert/update
    pass
```

**Frontend:**
- Tombol "Export Excel" di MasterItemsPage
- Tombol "Import Excel" dengan file upload dialog
- Preview data sebelum import

### 2.3 Buyer Prices - Multi Currency

**Backend:**
```python
# models.py - BuyerPriceList
currency: Mapped[str] = mapped_column(String(3), default="USD")

# schemas.py
currency: str = "USD"
```

**Frontend:**
- Dropdown currency di buyer price header (USD, IDR, dll)
- Price display sesuai currency

### 2.4 Master Items - Color Standard Field

**Backend:**
```python
# models.py - MasterItem
color_standard: Mapped[Optional[str]] = mapped_column(String(255))

# schemas.py
color_standard: Optional[str] = None
```

### 2.5 Master Items - Model (Take Down)

**Backend:**
```python
# models.py - MasterItem
model_takedown: Mapped[Optional[str]] = mapped_column(String(100))
```

### 2.6 Invoice - Payment Detail

**Backend:**
```python
# models.py - Invoice
payment_date: Mapped[Optional[date]] = mapped_column(Date)
payment_bank_account: Mapped[Optional[str]] = mapped_column(String(100))
payment_proof_url: Mapped[Optional[str]] = mapped_column(String(500))  # File path
payment_status: Mapped[str] = mapped_column(String(20), default="unpaid")  # paid/unpaid

# schemas.py
payment_date: Optional[date] = None
payment_bank_account: Optional[str] = None
payment_proof_url: Optional[str] = None
payment_status: str = "unpaid"
```

**Frontend:**
- Tambah field di InvoicePage form
- File upload untuk bukti bayar
- Status badge (Paid/Unpaid)

---

## Phase 3: Pricing Engine

### 3.1 Pricing Logic - Special Price / Diskon

**New Model:**
```python
class SpecialPrice(Base):
    __tablename__ = "special_prices"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    buyer_code: Mapped[str] = mapped_column(String(32))
    material_pattern: Mapped[str] = mapped_column(String(255))  # regex atau exact match
    discount_type: Mapped[str] = mapped_column(String(20))  # "nominal" atau "percentage"
    discount_value: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    emboss_pattern: Mapped[Optional[str]] = mapped_column(String(100))
    color_pattern: Mapped[Optional[str]] = mapped_column(String(100))
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_to: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

**Pricing Algorithm:**
```python
def calculate_price(base_price, buyer_code, material, emboss, color):
    # 1. Get base price from buyer price list
    price = base_price
    
    # 2. Apply emboss surcharge
    if emboss_surcharge := get_emboss_surcharge(emboss):
        price += emboss_surcharge
    
    # 3. Apply special prices / discounts
    special = find_special_price(buyer_code, material, emboss, color)
    if special:
        if special.discount_type == "percentage":
            price = price * (1 - special.discount_value / 100)
        else:  # nominal
            price = price - special.discount_value
    
    return max(price, 0)
```

### 3.2 Pricing - Customer-Based

**Data Model:**
```python
class CustomerSpecialPrice(Base):
    __tablename__ = "customer_special_prices"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("customers.id"))
    buyer_code: Mapped[str] = mapped_column(String(32))
    price_override: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    discount_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_to: Mapped[Optional[date]] = mapped_column(Date)
```

### 3.3 Pricing - Bulk Update

**Backend API:**
```python
@router.post("/master-prices/bulk-update")
async def bulk_update_prices(items: list[PriceUpdateItem]):
    """
    items: [{"item_code": "123456", "buyer_code": "NB", "price": 1.33}, ...]
    """
    # Batch update via SQLAlchemy
    pass
```

**Frontend:**
- Halaman bulk update dengan table editor
- Upload CSV untuk mass update
- Preview changes sebelum apply

---

## Phase 4: Workflow & Accounting

### 4.1 Customer → Buyer → Brand Mapping

**Current:** Brand-Customer relationship via `Brand.customer_id`

**Enhanced Model:**
```python
class CustomerBrandMapping(Base):
    __tablename__ = "customer_brand_mappings"
    __table_args__ = (
        UniqueConstraint("customer_id", "brand_id", name="uq_customer_brand"),
    )
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("customers.id"))
    brand_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("brands.id"))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

class BrandConstraint(Base):
    """Constraint: Customer hanya bisa pilih brand tertentu"""
    __tablename__ = "brand_constraints"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("customers.id"))
    allowed_brand_ids: Mapped[list] = mapped_column(JSON)  # [brand_id1, brand_id2]
```

**Frontend - PO Form:**
```javascript
function onCustomerChange(customerId) {
  // Get allowed brands for this customer
  const allowedBrands = getAllowedBrands(customerId)
  
  // Filter brand dropdown
  formModel.allowedBrands = allowedBrands
  
  // Validate: jika brand selected tidak ada di allowed, reset
  if (!allowedBrands.includes(formModel.brand_id)) {
    formModel.brand_id = null
  }
}
```

### 4.2 Subcon Invoice - 2 Jenis Invoice

**Data Model:**
```python
class SubconInvoice(Base):
    __tablename__ = "subcon_invoices"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    po_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("po_headers.id"))
    invoice_type: Mapped[str] = mapped_column(String(20))  # "barang" atau "jasa"
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
```

**Frontend:**
- Saat create invoice untuk PO subcont, muncul dialog pilihan:
  - "Invoice Barang" - amount dari PO line prices
  - "Invoice Jasa" - amount manual (jasa processing)
- Generate 2 invoice numbers berbeda

### 4.3 Marketing → PPIC Workflow

**Workflow Stages:**
```
input_system → rekap_printed → with_ppic → assigned_to_ppic → 
back_to_mkt → in_outstanding → material_followup → 
delivery_arranged → sj_invpl → invoice_billing
```

**New Stage:** `assigned_to_ppic`

**PPIC User Role:**
```python
class User(Base):
    department: Mapped[Optional[str]] = mapped_column(String(50))  # "marketing", "ppic", "qc", "admin"
```

**Assignment Logic:**
```python
@router.post("/po/{po_id}/assign-to-ppic")
async def assign_to_ppic(po_id: int, ppic_user_id: int):
    po = db.query(PoHeader).get(po_id)
    po.mkt_workflow_stage = "assigned_to_ppic"
    po.assigned_ppic_user_id = ppic_user_id
    
    # Send notification to PPIC
    create_notification(
        user_id=ppic_user_id,
        title="New PO Assigned",
        message=f"PO {po.po_number} has been assigned to you",
        entity_type="po",
        entity_id=po_id
    )
```

**Frontend - PPIC Dashboard:**
- Halaman terpisah untuk PPIC
- List PO yang assigned
- Filter: pending, in_progress, completed

### 4.4 Outstanding Material

**Data Model:**
```python
class OutstandingMaterial(Base):
    __tablename__ = "outstanding_materials"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    po_detail_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("po_details.id"))
    material_name: Mapped[str] = mapped_column(String(255))
    total_qty: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    delivered_qty: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    balance_qty: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(20))  # pending, partial, fulfilled
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
```

**API:**
```python
@router.get("/outstanding-materials")
async def list_outstanding_materials(
    customer_id: Optional[int] = None,
    status: Optional[str] = None
):
    # Aggregate from PO details + delivery
    pass
```

### 4.5 Accounting Mapping (COA)

**Data Model:**
```python
class AccountingMapping(Base):
    __tablename__ = "accounting_mappings"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    transaction_type: Mapped[str] = mapped_column(String(50))  # po_created, invoice, payment, dll
    status: Mapped[str] = mapped_column(String(50))  # draft, confirmed, sent, paid, dll
    coa_code: Mapped[str] = mapped_column(String(20))
    coa_name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
```

**Default Mappings:**
| Transaction | Status | COA Code | COA Name |
|-------------|--------|----------|----------|
| PO Created | draft | 1-1100 | Account Receivable |
| Invoice | sent | 1-1200 | AR - Export |
| Invoice | paid | 1-1300 | Cash/Bank |
| Payment | - | 2-1000 | Cost of Goods Sold |

### 4.6 Customs - Generate AJU dari Delivery

**Backend Logic:**
```python
@router.post("/customs/generate-from-delivery/{delivery_id}")
async def generate_aju_from_delivery(delivery_id: int):
    delivery = db.query(DeliveryHeader).get(delivery_id)
    
    # Get related data
    packing = delivery.packing
    production = packing.production
    po = production.po_header
    
    # Generate AJU structure based on delivery data
    aju_data = {
        "nomor_aju": generate_aju_number(),
        "delivery_number": delivery.delivery_number,
        "customer_name": po.customer.name,
        "items": [],
        # ... other fields from delivery details
    }
    
    return aju_data
```

---

## Technical Architecture

### Database Migrations

**Migration Order:**
```
1. add_customer_position.py
2. add_exchange_rate_dates.py
3. add_invoice_payment_fields.py
4. add_special_prices.py
5. add_customer_brand_mappings.py
6. add_subcon_invoices.py
7. add_outstanding_materials.py
8. add_accounting_mappings.py
```

### API Structure

```
/api/v1/
├── customers/
│   └── {id}  (GET, PUT) - sudah ada, tambah field position
├── po/
│   ├── {id}  (GET, PUT) - sudah ada
│   └── assign-to-ppic  (POST) - NEW
├── master-items/
│   ├── export  (POST) - NEW
│   ├── import  (POST) - NEW
│   └── bulk-update  (POST) - NEW
├── buyer-prices/
│   └── resolve-unit-price  (POST) - enhance dengan diskon
├── special-prices/
│   ├── (GET, POST) - NEW
│   └── {id} (GET, PUT, DELETE) - NEW
├── subcon-invoices/
│   └── (GET, POST) - NEW
├── outstanding-materials/
│   └── (GET) - NEW
├── accounting-mappings/
│   └── (GET, POST) - NEW
├── customs/
│   └── generate-from-delivery/{id}  (POST) - NEW
└── exchange-rates/
    └── (GET, POST) - enhance dengan valid_from, valid_to
```

### File Changes Summary

| Phase | Files to Modify |
|-------|-----------------|
| 1 | models.py, schemas.py, 7 frontend pages, i18n |
| 2 | models.py, schemas.py, 5 frontend pages, new API endpoints |
| 3 | models.py, schemas.py, pricing service, new pages |
| 4 | models.py, schemas.py, workflow service, new pages |

---

## Implementation Order

### Phase 1 (Week 1-2)
1. Customer Jabatan field
2. PO Kategori labels (SubKon, Retur)
3. PO SubKon/Retur → free price
4. Exchange Rate start-end dates
5. PO table - No PO Customer column
6. PO Softness dropdown
7. Remove Pabean field from PO

### Phase 2 (Week 3-5)
1. Master Items thickness range format
2. Master Items export/import Excel
3. Buyer Prices multi-currency
4. Master Items color standard, model takedown
5. Invoice payment details

### Phase 3 (Week 6-9)
1. Special Prices table & API
2. Pricing engine service
3. Customer-based pricing
4. Bulk price update UI & API

### Phase 4 (Week 10-14)
1. Customer-Brand mapping
2. Brand constraints
3. PO form validation
4. Subcon Invoice generation
5. PPIC role & dashboard
6. PO assignment workflow
7. Outstanding materials
8. Accounting mappings
9. Customs AJU generator

---

## Risk Assessment

| Item | Risk | Mitigation |
|------|------|------------|
| Pricing engine complexity | High | Start with simple rules, iterate |
| Data migration | Medium | Test on staging first |
| Breaking existing PO flow | High | Maintain backward compatibility |
| PPIC workflow approval | Medium | Pilot with 1-2 users |

---

## Dependencies

```
Phase 1 → No dependencies
Phase 2 → Phase 1 (some shared models)
Phase 3 → Phase 2 (pricing UI builds on form enhancements)
Phase 4 → Phase 1, 2, 3 (full system integration)
```

---

## Open Questions

1. **Subcon Invoice Jasa** - Apakah ada formula untuk calculate jasa amount, atau fixed amount per PO?
2. **PPIC Users** - Berapa jumlah PPIC user yang diharapkan?
3. **Accounting COA** - Apakah ada existing COA codes yang harus diikuti?
4. **Special Price Combinations** - Bisa jelaskan kombinasi spesifik emboss/color yang affecting price?

---

## Next Steps

1. Review dan approval design document
2. Create detailed implementation plans per phase
3. Start Phase 1 implementation
4. Iteration based on user feedback
