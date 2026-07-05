# Code Quality Improvement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve code quality dengan pendekatan incremental & safe - pecah file besar, extract reusable code, organize structure tanpa ubah behavior existing.

**Architecture:** Frontend Vue 3 - extract composables & organize API modules. Backend FastAPI - organize schemas & models. No new dependencies.

**Tech Stack:** Vue 3, Element Plus, FastAPI, SQLAlchemy, Pydantic

---

## Phase 1: Frontend Composables

### Task 1: Create useFormatters Composable

**Files:**
- Create: `frontend/src/composables/useFormatters.js`

- [ ] **Step 1: Create composables directory and useFormatters.js**

```javascript
// frontend/src/composables/useFormatters.js
import { useI18n } from 'vue-i18n'

export function useFormatters() {
  const { t } = useI18n()

  function formatCurrency(value, currency = 'IDR') {
    if (value == null) return '-'
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(value)
  }

  function formatNumber(value, decimals = 2) {
    if (value == null) return '-'
    return Number(value).toLocaleString('id-ID', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
  }

  function formatDate(dateStr, format = 'short') {
    if (!dateStr) return '-'
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return dateStr
    if (format === 'short') {
      return d.toLocaleDateString('id-ID', { year: 'numeric', month: 'short', day: 'numeric' })
    }
    return d.toLocaleDateString('id-ID')
  }

  return {
    formatCurrency,
    formatNumber,
    formatDate,
  }
}
```

- [ ] **Step 2: Export dari index.js (create if not exists)**

```javascript
// frontend/src/composables/index.js
export * from './useFormatters'
export * from './useNotifications'
export * from './useConfirmDialog'
export * from './useApiState'
```

- [ ] **Step 3: Commit**

```bash
cd /Users/wiranto/Projects/Tonghong
git add frontend/src/composables/
git commit -m "feat(composables): add useFormatters composable"
```

---

### Task 2: Create useNotifications Composable

**Files:**
- Create: `frontend/src/composables/useNotifications.js`

- [ ] **Step 1: Create useNotifications.js**

```javascript
// frontend/src/composables/useNotifications.js
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

export function useNotifications() {
  const { t } = useI18n()

  function notifySuccess(message = null) {
    ElMessage.success(message || t('common.saveSuccess'))
  }

  function notifyError(message = null) {
    ElMessage.error(message || t('common.errorGeneric'))
  }

  function notifyWarning(message) {
    ElMessage.warning(message)
  }

  function notifyInfo(message) {
    ElMessage.info(message)
  }

  return {
    notifySuccess,
    notifyError,
    notifyWarning,
    notifyInfo,
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/composables/useNotifications.js
git commit -m "feat(composables): add useNotifications composable"
```

---

### Task 3: Create useConfirmDialog Composable

**Files:**
- Create: `frontend/src/composables/useConfirmDialog.js`

- [ ] **Step 1: Create useConfirmDialog.js**

```javascript
// frontend/src/composables/useConfirmDialog.js
import { ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'

export function useConfirmDialog() {
  const { t } = useI18n()

  async function confirm(message, title = null) {
    try {
      await ElMessageBox.confirm(message, title || t('common.confirm'), {
        type: 'warning',
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
      })
      return true
    } catch {
      return false
    }
  }

  async function confirmDelete(itemName = '') {
    const msg = itemName
      ? t('common.deleteConfirmWithName', { name: itemName })
      : t('common.deleteConfirm')
    return confirm(msg)
  }

  return {
    confirm,
    confirmDelete,
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/composables/useConfirmDialog.js
git commit -m "feat(composables): add useConfirmDialog composable"
```

---

### Task 4: Create useApiState Composable

**Files:**
- Create: `frontend/src/composables/useApiState.js`

- [ ] **Step 1: Create useApiState.js**

```javascript
// frontend/src/composables/useApiState.js
import { ref } from 'vue'
import { useNotifications } from './useNotifications'

export function useApiState() {
  const loading = ref(false)
  const error = ref(null)
  const { notifyError } = useNotifications()

  async function execute(apiCall) {
    loading.value = true
    error.value = null
    try {
      const result = await apiCall()
      return result
    } catch (e) {
      error.value = e.message || String(e)
      notifyError(error.value)
      throw e
    } finally {
      loading.value = false
    }
  }

  function clearError() {
    error.value = null
  }

  return {
    loading,
    error,
    execute,
    clearError,
  }
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/composables/useApiState.js
git commit -m "feat(composables): add useApiState composable"
```

---

### Task 5: Update Sample Views to Use Composables

**Files:**
- Modify: `frontend/src/views/admin/BrandMasterPage.vue`
- Modify: `frontend/src/views/admin/ExchangeRatePage.vue`

- [ ] **Step 1: Update BrandMasterPage.vue untuk use composables**

Read the file first, then add imports and replace inline logic:

```javascript
// Add at top with other imports
import { useFormatters } from '../../composables/useFormatters'
import { useNotifications } from '../../composables/useNotifications'
import { useConfirmDialog } from '../../composables/useConfirmDialog'

// Add in setup()
const { formatCurrency } = useFormatters()
const { notifySuccess, notifyError } = useNotifications()
const { confirmDelete } = useConfirmDialog()

// Replace inline ElMessage calls with notifySuccess/notifyError
// Replace inline ElMessageBox.confirm with confirmDelete
```

- [ ] **Step 2: Test it works**

```bash
cd frontend && npm run lint
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/admin/BrandMasterPage.vue
git commit -m "refactor(BrandMasterPage): use composables for notifications"
```

---

## Phase 2: Frontend API Modules

### Task 6: Extract auth.js from client.js

**Files:**
- Modify: `frontend/src/api/client.js`
- Create: `frontend/src/api/auth.js`
- Create: `frontend/src/api/index.js`

- [ ] **Step 1: Create auth.js**

```javascript
// frontend/src/api/auth.js
import { apiFetch } from './client'

export function login(username, password) {
  return apiFetch('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) })
}

export function logout() {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user')
}

export function me() {
  return apiFetch('/auth/me')
}

export function getToken() {
  return localStorage.getItem('auth_token')
}

export function setToken(token) {
  localStorage.setItem('auth_token', token)
}
```

- [ ] **Step 2: Update client.js - remove auth functions**

Find and remove lines with login, me, logout functions from client.js

- [ ] **Step 3: Create index.js with re-exports**

```javascript
// frontend/src/api/index.js
export * from './auth'
export * from './client'

// Lazy exports untuk backward compat dengan nama asli
export { apiFetch } from './client'
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/api/auth.js frontend/src/api/index.js frontend/src/api/client.js
git commit -m "refactor(api): extract auth module from client.js"
```

---

### Task 7: Extract customers.js

**Files:**
- Create: `frontend/src/api/customers.js`
- Modify: `frontend/src/api/client.js`

- [ ] **Step 1: Find customer functions in client.js**

```bash
grep -n "customer" frontend/src/api/client.js | head -20
```

- [ ] **Step 2: Extract customer functions to customers.js**

```javascript
// frontend/src/api/customers.js
import { apiFetch } from './client'

export function listCustomers(params = {}) {
  const q = new URLSearchParams()
  if (params.keyword) q.set('keyword', params.keyword)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/customers${suffix}`)
}

export function getCustomer(id) {
  return apiFetch(`/customers/${id}`)
}

export function createCustomer(data) {
  return apiFetch('/customers', { method: 'POST', body: JSON.stringify(data) })
}

export function updateCustomer(id, data) {
  return apiFetch(`/customers/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export function deleteCustomer(id) {
  return apiFetch(`/customers/${id}`, { method: 'DELETE' })
}
```

- [ ] **Step 3: Remove extracted functions from client.js**

- [ ] **Step 4: Update index.js exports**

```javascript
export * from './customers'
```

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/customers.js frontend/src/api/index.js frontend/src/api/client.js
git commit -m "refactor(api): extract customers module"
```

---

### Task 8: Extract invoices.js

**Files:**
- Create: `frontend/src/api/invoices.js`
- Modify: `frontend/src/api/client.js`

- [ ] **Step 1: Find invoice functions in client.js**

```bash
grep -n "invoice" frontend/src/api/client.js | head -30
```

- [ ] **Step 2: Extract to invoices.js following same pattern as Task 7**

- [ ] **Step 3: Commit**

---

### Task 9: Extract deliveries.js

**Files:**
- Create: `frontend/src/api/deliveries.js`
- Modify: `frontend/src/api/client.js`

- [ ] **Step 1: Find delivery functions in client.js**

```bash
grep -n "delivery" frontend/src/api/client.js | head -30
```

- [ ] **Step 2: Extract to deliveries.js**

- [ ] **Step 3: Commit**

---

### Task 10: Extract purchaseOrders.js

**Files:**
- Create: `frontend/src/api/purchaseOrders.js`
- Modify: `frontend/src/api/client.js`

- [ ] **Step 1: Extract PO functions**

```bash
grep -n "po\|purchase" frontend/src/api/client.js | head -30
```

- [ ] **Step 2: Extract to purchaseOrders.js**

- [ ] **Step 3: Commit**

---

### Task 11: Extract remaining API modules

**Files:**
- Create: `frontend/src/api/masters.js` (Brand, MasterItem, ExchangeRate)
- Create: `frontend/src/api/reports.js`
- Create: `frontend/src/api/inventory.js`
- Modify: `frontend/src/api/index.js`

- [ ] **Step 1: Create masters.js**

```javascript
// frontend/src/api/masters.js
import { apiFetch } from './client'

// Brand
export function listBrands(params = {}) {
  const q = new URLSearchParams()
  if (params.keyword) q.set('keyword', params.keyword)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/brands${suffix}`)
}

export function createBrand(data) {
  return apiFetch('/brands', { method: 'POST', body: JSON.stringify(data) })
}

export function updateBrand(id, data) {
  return apiFetch(`/brands/${id}`, { method: 'PUT', body: JSON.stringify(data) })
}

export function deleteBrand(id) {
  return apiFetch(`/brands/${id}`, { method: 'DELETE' })
}

// Master Items
export function listMasterItems(params = {}) {
  const q = new URLSearchParams()
  if (params.keyword) q.set('keyword', params.keyword)
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch(`/master-items${suffix}`)
}

// Exchange Rates
export function listExchangeRates() {
  return apiFetch('/exchange-rates')
}
```

- [ ] **Step 2: Create reports.js and inventory.js**

- [ ] **Step 3: Update index.js dengan semua exports**

- [ ] **Step 4: Commit**

---

### Task 12: Final client.js cleanup

**Files:**
- Modify: `frontend/src/api/client.js`

- [ ] **Step 1: Clean up client.js - keep only base functions**

client.js should only contain:
- apiFetch (main function)
- fetchAuthenticatedDocument
- Any shared utilities

- [ ] **Step 2: Verify no functions lost**

```bash
# Check semua API exports
grep "^export" frontend/src/api/index.js
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/api/client.js
git commit -m "refactor(api): cleanup client.js, keep only base functions"
```

---

## Phase 3: Backend Schema Organization

### Task 13: Create schemas folder structure

**Files:**
- Create: `backend/app/schemas/__init__.py`
- Create: `backend/app/schemas/base.py`
- Create: `backend/app/schemas/common.py`

- [ ] **Step 1: Create base.py**

```python
# backend/app/schemas/base.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    """Base config untuk semua schemas - support ORM objects."""
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin:
    """Mixin untuk created_at/updated_at fields."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

- [ ] **Step 2: Create common.py**

```python
# backend/app/schemas/common.py
from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper."""
    data: List[T]
    total: int
    page: int
    page_size: int


class SuccessResponse(BaseModel):
    """Standard success response."""
    success: bool = True
    message: Optional[str] = None
```

- [ ] **Step 3: Create __init__.py**

```python
# backend/app/schemas/__init__.py
from .base import ORMBase, TimestampMixin
from .common import PaginatedResponse, SuccessResponse

__all__ = ['ORMBase', 'TimestampMixin', 'PaginatedResponse', 'SuccessResponse']
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/schemas/
git commit -m "refactor(schemas): create schemas folder structure"
```

---

### Task 14: Move customer schemas to separate file

**Files:**
- Create: `backend/app/schemas/customer.py`
- Modify: `backend/app/schemas/__init__.py`
- Modify: `backend/app/schemas.py`

- [ ] **Step 1: Extract customer schemas**

```python
# backend/app/schemas/customer.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CustomerBase(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    position: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    tax_id: Optional[str] = None
    skep_kb_number: Optional[str] = None
    customs_office_code: Optional[str] = None
    address: Optional[str] = None
    remark: Optional[str] = None
    is_export_customer: bool = False
    bill_to: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class CustomerOut(CustomerBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

- [ ] **Step 2: Update __init__.py**

```python
from .customer import CustomerCreate, CustomerUpdate, CustomerOut
```

- [ ] **Step 3: Remove customer schemas from schemas.py**

- [ ] **Step 4: Update imports di routers yang pakai customer schemas**

```bash
# Find files yang import dari schemas.py
grep -r "from.*schemas import" backend/app/routers/ | grep -i customer
```

- [ ] **Step 5: Commit**

---

### Task 15: Move invoice schemas to separate file

**Files:**
- Create: `backend/app/schemas/invoice.py`
- Modify: `backend/app/schemas/__init__.py`

- [ ] **Step 1: Extract invoice schemas**

```bash
# Find invoice class definitions in schemas.py
grep -n "^class Invoice" backend/app/schemas.py
```

- [ ] **Step 2: Extract to invoice.py**

- [ ] **Step 3: Update imports**

- [ ] **Step 4: Commit**

---

### Task 16: Move remaining schemas

**Files:**
- Create: `backend/app/schemas/delivery.py`
- Create: `backend/app/schemas/purchase_order.py`
- Create: `backend/app/schemas/master.py`
- Create: `backend/app/schemas/report.py`
- Create: `backend/app/schemas/inventory.py`

- [ ] **Step 1: Extract each domain schemas ke file terpisah**

- [ ] **Step 2: Update __init__.py dengan semua exports**

- [ ] **Step 3: Update router imports**

- [ ] **Step 4: Commit**

---

### Task 17: Final schemas.py cleanup

**Files:**
- Modify: `backend/app/schemas.py`

- [ ] **Step 1: Clean up schemas.py - keep only imports**

schemas.py should become a re-export module:

```python
"""Re-export semua schemas dari schemas/ folder."""
from .schemas import *

# Backward compatibility - re-export everything
from .schemas.base import ORMBase, TimestampMixin
from .schemas.common import PaginatedResponse, SuccessResponse
from .schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
# ... etc
```

- [ ] **Step 2: Verify imports still work**

```bash
cd backend && python -c "from app.schemas import *"
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/schemas.py
git commit -m "refactor(schemas): convert schemas.py to re-export module"
```

---

## Phase 4: Backend Model Comments

### Task 18: Add region comments to models.py

**Files:**
- Modify: `backend/app/models.py`

- [ ] **Step 1: Identify model regions**

```bash
grep -n "^class " backend/app/models.py | head -40
```

- [ ] **Step 2: Add region comments**

```python
# =============================================================================
# CUSTOMER MODELS
# =============================================================================


class Customer(Base):
    # ...


# =============================================================================
# INVOICE MODELS
# =============================================================================


class Invoice(Base):
    # ...
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/models.py
git commit -m "refactor(models): add region comments for organization"
```

---

## Verification Tasks

### Task 19: Run lint and tests

**Files:**
- None (verification only)

- [ ] **Step 1: Frontend lint**

```bash
cd frontend && npm run lint
```

- [ ] **Step 2: Backend lint**

```bash
cd backend && ruff check app/
```

- [ ] **Step 3: Verify imports work**

```bash
cd backend && python -c "from app.main import app; print('OK')"
```

- [ ] **Step 4: Commit verification task**

```bash
git commit -m "chore: verify code quality improvements pass linting"
```

---

## Summary

**Total Tasks:** 19

**Phase 1 (Tasks 1-5):** Frontend Composables - 5 tasks  
**Phase 2 (Tasks 6-12):** Frontend API Modules - 7 tasks  
**Phase 3 (Tasks 13-17):** Backend Schema Organization - 5 tasks  
**Phase 4 (Task 18):** Backend Model Comments - 1 task  
**Verification (Task 19):** Lint and test - 1 task

**Estimated Time:** 2-4 hours (incremental, safe approach)
