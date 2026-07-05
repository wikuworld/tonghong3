# Phase 4: Workflow & Accounting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement marketing-PPIC workflow, subcon invoices, accounting mapping, and related workflow features.

**Architecture:** Backend models and services for workflow logic, new database tables, API endpoints, and frontend UI pages.

**Tech Stack:** Vue 3, Element Plus, FastAPI, SQLAlchemy, Alembic

---

## File Inventory

| File | Tasks |
|------|-------|
| `backend/app/models.py` | 4.1, 4.2, 4.3, 4.4, 4.5 |
| `backend/app/schemas.py` | 4.1, 4.2, 4.3, 4.4, 4.5 |
| `backend/app/routers/workflow.py` | 4.3, 4.4 |
| `backend/app/routers/accounting.py` | 4.5 |
| `backend/app/routers/subcon.py` | 4.2 |
| `backend/app/routers/customs.py` | 4.6 |
| `backend/alembic/versions/` | 4.1, 4.2, 4.3, 4.4, 4.5 |
| `frontend/src/views/admin/MarketingFlowPage.vue` | 4.3 |
| `frontend/src/views/admin/SubconInvoicePage.vue` | 4.2 |
| `frontend/src/views/admin/AccountingMappingsPage.vue` | 4.5 |
| `frontend/src/views/admin/CustomerBrandMappingPage.vue` | 4.1 |
| `frontend/src/api/client.js` | 4.1, 4.2, 4.3, 4.4, 4.5, 4.6 |
| `frontend/src/i18n/id.json` | all |
| `frontend/src/router/index.js` | all |

---

## Task 4.1: Customer-Brand Mapping

### Data Models

```python
class CustomerBrandMapping(Base):
    """Many-to-many mapping between customers and brands."""
    
    __tablename__ = "customer_brand_mappings"
    __table_args__ = (
        UniqueConstraint("customer_id", "brand_id", name="uq_customer_brand"),
    )
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("customers.id"))
    brand_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("brands.id"))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    
    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="brand_mappings")
    brand: Mapped[Optional["Brand"]] = relationship("Brand", back_populates="customer_mappings")


class BrandConstraint(Base):
    """Constraint: Customer hanya bisa pilih brand tertentu."""
    
    __tablename__ = "brand_constraints"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("customers.id"))
    allowed_brand_ids: Mapped[list] = mapped_column(JSON)  # [brand_id1, brand_id2]
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
```

### Implementation Steps

- [ ] **Step 1: Add models to models.py**
  - Add `CustomerBrandMapping` and `BrandConstraint` models
  - Add `brand_mappings` back_populates to Customer and Brand

- [ ] **Step 2: Add schemas**
  - CustomerBrandMappingCreate, CustomerBrandMappingUpdate, CustomerBrandMappingOut
  - BrandConstraintCreate, BrandConstraintUpdate, BrandConstraintOut

- [ ] **Step 3: Create migration**
  ```bash
  cd /Users/wiranto/Projects/Tonghong/backend && alembic revision --autogenerate -m "add_customer_brand_mappings"
  ```

- [ ] **Step 4: Create router** (`backend/app/routers/customers.py`)
  - GET/POST /customers/{id}/brand-mappings
  - DELETE /customers/{id}/brand-mappings/{mapping_id}
  - GET /customers/{id}/allowed-brands (returns constrained brands)

- [ ] **Step 5: Add API functions to client.js**

- [ ] **Step 6: Add translations**

- [ ] **Step 7: Create CustomerBrandMappingPage.vue**
  - Table showing current mappings
  - Add/remove brand associations
  - Set default brand

- [ ] **Step 8: Update PurchaseOrderPage.vue**
  - On customer change, fetch allowed brands
  - Filter brand dropdown based on constraints

---

## Task 4.2: Subcon Invoice

### Data Model

```python
class SubconInvoice(Base):
    """Invoice untuk PO Subcont - 2 jenis: barang dan jasa."""
    
    __tablename__ = "subcon_invoices"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    po_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("po_headers.id"))
    invoice_type: Mapped[str] = mapped_column(String(20))  # "barang" atau "jasa"
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100))
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, sent, paid
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    po: Mapped[Optional["PoHeader"]] = relationship("PoHeader", back_populates="subcon_invoices")
```

### Implementation Steps

- [ ] **Step 1: Add SubconInvoice model to models.py**
  - Add `subcon_invoices` back_populates to PoHeader

- [ ] **Step 2: Add schemas**
  - SubconInvoiceCreate, SubconInvoiceUpdate, SubconInvoiceOut
  - Include po_number in output via relationship

- [ ] **Step 3: Create migration**
  ```bash
  cd /Users/wiranto/Projects/Tonghong/backend && alembic revision --autogenerate -m "add_subcon_invoices"
  ```

- [ ] **Step 4: Create router** (`backend/app/routers/subcon.py`)
  - GET /subcon-invoices - list all (with optional po_id filter)
  - POST /subcon-invoices - create new
  - PUT /subcon-invoices/{id} - update
  - DELETE /subcon-invoices/{id} - soft delete
  - POST /subcon-invoices/generate-from-po/{po_id} - auto-generate both types

- [ ] **Step 5: Add API functions to client.js**

- [ ] **Step 6: Add translations**
  ```json
  "subconInvoice": {
    "title": "Invoice Subkon",
    "subtitle": "Kelola invoice barang dan jasa subkon",
    "invoiceType": "Tipe Invoice",
    "invoiceNumber": "No. Invoice",
    "poNumber": "No. PO",
    "amount": "Jumlah",
    "description": "Keterangan",
    "status": "Status",
    "barang": "Barang",
    "jasa": "Jasa",
    "draft": "Draft",
    "sent": "Terkirim",
    "paid": "Lunas"
  }
  ```

- [ ] **Step 7: Create SubconInvoicePage.vue**
  - Table with invoice list
  - Filter by PO, type, status
  - Create/Edit dialog with type selector
  - "Generate from PO" button for subcont POs

- [ ] **Step 8: Add route to router**

---

## Task 4.3: Marketing-PPIC Workflow

### User Department Field

```python
# Add to existing User model or create new field
department: Mapped[Optional[str]] = mapped_column(String(50))  # "marketing", "ppic", "qc", "admin"
```

### PPIC Assignment Model

```python
class PpicsAssignment(Base):
    """PO assignment to PPIC users."""
    
    __tablename__ = "ppic_assignments"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    po_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("po_headers.id"))
    ppic_user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, in_progress, completed
    notes: Mapped[Optional[str]] = mapped_column(Text)
    assigned_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    po: Mapped[Optional["PoHeader"]] = relationship("PoHeader")
    ppic_user: Mapped[Optional["User"]] = relationship("User")
```

### Implementation Steps

- [ ] **Step 1: Add PpicsAssignment model to models.py**
  - Add relationship to PoHeader

- [ ] **Step 2: Add schema**
  - PpicsAssignmentCreate, PpicsAssignmentUpdate, PpicsAssignmentOut

- [ ] **Step 3: Create migration**
  ```bash
  cd /Users/wiranto/Projects/Tonghong/backend && alembic revision --autogenerate -m "add_ppic_assignments"
  ```

- [ ] **Step 4: Create workflow router** (`backend/app/routers/workflow.py`)
  - POST /po/{po_id}/assign-to-ppic
  - GET /ppic/dashboard - list assigned POs for current user
  - PUT /ppic/assignments/{id}/status
  - GET /ppic/users - list PPIC users

- [ ] **Step 5: Add API functions to client.js**

- [ ] **Step 6: Add translations**

- [ ] **Step 7: Update MarketingFlowPage.vue**
  - Add "Assign to PPIC" button/action
  - Show PPIC assignment status

- [ ] **Step 8: Create PpicsDashboardPage.vue**
  - PPIC-specific dashboard
  - List assigned POs
  - Update assignment status
  - Add route for /admin/ppic-dashboard

---

## Task 4.4: Outstanding Materials

### Data Model

```python
class OutstandingMaterial(Base):
    """Track outstanding materials per PO detail."""
    
    __tablename__ = "outstanding_materials"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    po_detail_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("po_details.id"))
    material_name: Mapped[str] = mapped_column(String(255))
    total_qty: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    delivered_qty: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    balance_qty: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(20))  # pending, partial, fulfilled
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
```

### Implementation Steps

- [ ] **Step 1: Add OutstandingMaterial model**

- [ ] **Step 2: Add schemas**

- [ ] **Step 3: Create migration**

- [ ] **Step 4: Add endpoints to workflow router**
  - GET /outstanding-materials
  - POST /outstanding-materials/generate-from-po/{po_id}
  - PUT /outstanding-materials/{id}/deliver

- [ ] **Step 5: Add API functions to client.js**

- [ ] **Step 6: Add translations**
  ```json
  "outstandingMaterial": {
    "title": "Material Outstanding",
    "subtitle": "Tracking material yang belum terpenuhi",
    "materialName": "Nama Material",
    "totalQty": "Total Qty",
    "deliveredQty": "Sudah Terpenuhi",
    "balanceQty": "Sisa",
    "status": "Status",
    "pending": "Menunggu",
    "partial": "Sebagian",
    "fulfilled": "Tercukupi"
  }
  ```

- [ ] **Step 7: Create OutstandingMaterialsPage.vue**
  - Table with aggregation
  - Filter by customer, status
  - Update delivery progress

- [ ] **Step 8: Add route**

---

## Task 4.5: Accounting Mapping (COA)

### Data Model

```python
class AccountingMapping(Base):
    """Mapping transaksi ke Chart of Accounts."""
    
    __tablename__ = "accounting_mappings"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    transaction_type: Mapped[str] = mapped_column(String(50))  # po_created, invoice, payment
    status: Mapped[Optional[str]] = mapped_column(String(50))  # draft, confirmed, sent, paid
    coa_code: Mapped[str] = mapped_column(String(20))
    coa_name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
```

### Default Mappings (seed data)

| Transaction | Status | COA Code | COA Name |
|-------------|--------|----------|----------|
| po_created | draft | 1-1100 | Account Receivable |
| invoice | sent | 1-1200 | AR - Export |
| invoice | paid | 1-1300 | Cash/Bank |
| payment | - | 2-1000 | Cost of Goods Sold |

### Implementation Steps

- [ ] **Step 1: Add AccountingMapping model**

- [ ] **Step 2: Add schemas**

- [ ] **Step 3: Create migration with seed data**

- [ ] **Step 4: Create accounting router** (`backend/app/routers/accounting.py`)
  - GET /accounting-mappings
  - POST /accounting-mappings
  - PUT /accounting-mappings/{id}
  - DELETE /accounting-mappings/{id}
  - GET /accounting-mappings/resolve?transaction=&status=

- [ ] **Step 5: Add API functions to client.js**

- [ ] **Step 6: Add translations**
  ```json
  "accountingMapping": {
    "title": "Mapping Akuntansi",
    "subtitle": "Kelola mapping transaksi ke COA",
    "transactionType": "Tipe Transaksi",
    "coaCode": "Kode COA",
    "coaName": "Nama COA",
    "description": "Keterangan",
    "po_created": "PO Dibuat",
    "invoice": "Invoice",
    "payment": "Pembayaran"
  }
  ```

- [ ] **Step 7: Create AccountingMappingsPage.vue**
  - CRUD table
  - Transaction type dropdown
  - Status filter

- [ ] **Step 8: Add route**

---

## Task 4.6: Customs AJU Generator

### Implementation Steps

- [ ] **Step 1: Create customs router** (`backend/app/routers/customs.py`)
  - POST /customs/generate-from-delivery/{delivery_id}

- [ ] **Step 2: Add API function to client.js**

- [ ] **Step 3: Add translations**
  ```json
  "customs": {
    "generateAju": "Generate AJU",
    "ajuNumber": "Nomor AJU",
    "fromDelivery": "Dari Delivery"
  }
  ```

- [ ] **Step 4: Add button to DeliveryPage** (if exists)

---

## Summary

| Task | Description | Effort |
|------|-------------|--------|
| 4.1 | Customer-Brand Mapping | Medium |
| 4.2 | Subcon Invoice | Medium |
| 4.3 | Marketing-PPIC Workflow | High |
| 4.4 | Outstanding Materials | Medium |
| 4.5 | Accounting Mapping | Medium |
| 4.6 | Customs AJU Generator | Low |

**Total: 6 tasks**

---

## Plan complete and saved to `docs/superpowers/plans/2026-04-15-phase4-workflow-accounting-plan.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - Dispatch subagent per task for fast iteration

**2. Inline Execution** - Execute tasks sequentially in this session

**Which approach?**
