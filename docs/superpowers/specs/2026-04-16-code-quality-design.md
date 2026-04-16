# Code Quality Improvement Design

> **Date:** 2026-04-16  
> **Status:** Approved

## Goal

Improve code quality untuk Tonghong ERP dengan pendekatan incremental & safe - pecah file besar menjadi lebih kecil, organize logic, dan extract reusable code tanpa mengubah behavior existing.

## Architecture

**Frontend (Vue 3):**
- Extract composables untuk reusable logic (format, validation, API calls)
- Pecah `client.js` (965 lines) jadi domain-specific API modules
- Tambah folder `composables/` untuk shared Vue logic
- Tambah JSDoc comments untuk better documentation

**Backend (Python/FastAPI):**
- Pecah `schemas.py` (1139 lines) jadi domain-specific schema files
- Tambah type hints yang konsisten
- Organize models dengan better grouping
- Extract utility functions ke folder terpisah

## Tech Stack

- **Frontend:** Vue 3, Element Plus, Vite
- **Backend:** FastAPI, SQLAlchemy, Pydantic, Alembic
- **No new dependencies** - hanya reorganize existing code

---

## Frontend Design

### 1. Create Composables Folder

```
frontend/src/composables/
├── useFormatters.js        # formatCurrency, formatDate, formatNumber
├── useNotifications.js      # ElMessage wrappers
├── useConfirmDialog.js     # ElMessageBox confirm helpers
├── useApiState.js          # loading/error state management
└── usePagination.js        # pagination logic reuse
```

### 2. Extract API Modules

Pecah `client.js` jadi domain-specific modules:

```
frontend/src/api/
├── client.js              # Base apiFetch (keep as-is, small)
├── auth.js                # login, me, logout
├── customers.js           # Customer CRUD
├── invoices.js            # Invoice CRUD + related
├── deliveries.js          # Delivery CRUD + related
├── purchaseOrders.js      # PO CRUD + related
├── masters.js             # Brand, MasterItem, ExchangeRate
├── reports.js             # Report endpoints
├── inventory.js           # Stock, Material, Warehouse
└── index.js              # Re-export all untuk backward compat
```

### 3. Update Views to Use Composables

- Replace inline formatters dengan `useFormatters`
- Replace inline ElMessage dengan `useNotifications`
- Replace inline loading/error state dengan `useApiState`

---

## Backend Design

### 1. Schema Organization

Pecah `schemas.py` jadi files per domain:

```
backend/app/schemas/
├── __init__.py            # Re-export all schemas
├── base.py                # ORMBase, common mixins
├── customer.py            # Customer schemas
├── invoice.py             # Invoice schemas
├── delivery.py            # Delivery schemas
├── purchase_order.py      # PO schemas
├── master.py              # Brand, MasterItem, ExchangeRate
├── report.py              # Report schemas
├── inventory.py           # Stock, Material, Warehouse
└── common.py              # Pagination, Response wrappers
```

### 2. Model Organization

`models.py` tetap 1 file (SQLAlchemy require single module untuk migrations), tapi tambahkan region comments:

```python
# === CUSTOMER MODELS ===
# === INVOICE MODELS ===
# === DELIVERY MODELS ===
# === PURCHASE ORDER MODELS ===
# === MASTER DATA MODELS ===
# === INVENTORY MODELS ===
```

### 3. Add Type Hints

- Consistent Optional[T] instead of T | None
- Pydantic Field descriptions
- Better docstrings

---

## Implementation Order

### Phase 1: Frontend Composables
1. Create `composables/useFormatters.js`
2. Create `composables/useNotifications.js`
3. Create `composables/useConfirmDialog.js`
4. Create `composables/useApiState.js`
5. Update 3-5 views untuk use composables

### Phase 2: Frontend API Modules
1. Extract `auth.js` dari client.js
2. Extract `customers.js` dari client.js
3. Extract `invoices.js` dari client.js
4. Extract `deliveries.js` dan `purchaseOrders.js`
5. Extract `masters.js`, `reports.js`, `inventory.js`
6. Create `index.js` for backward compat
7. Update imports di views

### Phase 3: Backend Schema Organization
1. Create `schemas/` folder structure
2. Move customer schemas
3. Move invoice schemas
4. Move delivery schemas
5. Move PO schemas
6. Move master schemas
7. Move other schemas
8. Create `__init__.py` with re-exports
9. Update router imports

### Phase 4: Backend Model Comments
1. Add region comments ke models.py
2. Add type hints where missing

---

## Backward Compatibility

- API module exports di `index.js` mirroring original `client.js`
- Schema imports via `schemas/__init__.py`
- No behavior changes
- Incremental commits per phase

## Success Criteria

1. `client.js` < 200 lines
2. `schemas.py` < 300 lines (after split) or 1 file with clear regions
3. Composables folder exists with 4+ composables
4. API modules organized by domain
5. All existing functionality still works
