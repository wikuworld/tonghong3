# Phase 1: Quick Wins Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement 7 low-effort enhancements across Customer, PO, and Exchange Rate modules.

**Architecture:** Backend model/schema changes + Frontend UI updates. Each task is independent and can be implemented in any order.

**Tech Stack:** Vue 3, Element Plus, FastAPI, SQLAlchemy, Alembic

---

## File Inventory

| File | Tasks |
|------|-------|
| `backend/app/models.py` | 1.1, 1.4 |
| `backend/app/schemas.py` | 1.1, 1.4 |
| `backend/alembic/versions/` | 1.1, 1.4 |
| `frontend/src/views/admin/CustomersPage.vue` | 1.1 |
| `frontend/src/views/admin/PurchaseOrderPage.vue` | 1.2, 1.3, 1.5, 1.6, 1.7 |
| `frontend/src/views/admin/ExchangeRatePage.vue` | 1.4 |
| `frontend/src/i18n/id.json` | 1.1, 1.2, 1.4, 1.6 |
| `frontend/src/i18n/en.json` | 1.1, 1.2, 1.4, 1.6 |

---

## Task 1.1: Customer - Field "Jabatan" (Position)

**Files:**
- Modify: `backend/app/models.py` - Customer class
- Modify: `backend/app/schemas.py` - CustomerCreate, CustomerUpdate, CustomerOut
- Create: `backend/alembic/versions/xxxx_add_customer_position.py`
- Modify: `frontend/src/views/admin/CustomersPage.vue`
- Modify: `frontend/src/i18n/id.json`

- [ ] **Step 1: Add field to Customer model**

In `backend/app/models.py`, find Customer class (line 29-54), add after `contact_person`:
```python
position: Mapped[Optional[str]] = mapped_column(String(120))
```

- [ ] **Step 2: Add field to Pydantic schemas**

In `backend/app/schemas.py`, add `position` field to:
- `CustomerCreate` (after contact_person)
- `CustomerUpdate` (after contact_person)
- `CustomerOut` (after contact_person)

```python
position: Optional[str] = None
```

- [ ] **Step 3: Create Alembic migration**

```bash
cd /Users/wiranto/Projects/Tonghong/backend
alembic revision --autogenerate -m "add_customer_position"
```

- [ ] **Step 4: Add field to CustomersPage.vue template**

Find where `contact_person` field is displayed (around line 169-173), add after it:
```vue
<el-col :xs="24" :sm="12">
  <el-form-item :label="t('pages.customers.fieldPosition')" prop="position">
    <el-input v-model="formModel.position" maxlength="120" clearable />
  </el-form-item>
</el-col>
```

Also add to detail view (around line 82-84):
```vue
<el-descriptions-item :label="t('pages.customers.fieldPosition')" :span="1">
  {{ detailRow.position || t('common.emptyValue') }}
</el-descriptions-item>
```

- [ ] **Step 5: Update formModel reactive**

Add to `formModel` reactive object (around line 453):
```javascript
position: '',
```

- [ ] **Step 6: Update resetFormModel function**

Add (around line 500):
```javascript
formModel.position = ''
```

- [ ] **Step 7: Update openEdit function**

Add loading of position (around line 625):
```javascript
formModel.position = row.position || ''
```

- [ ] **Step 8: Update submitForm payload**

Add to body object (around line 657):
```javascript
position: formModel.position.trim() || undefined,
```

- [ ] **Step 9: Add translations**

In `frontend/src/i18n/id.json`, add:
```json
"pages": {
  "customers": {
    "fieldPosition": "Jabatan"
  }
}
```

---

## Task 1.2: PO - Dropdown Kategori: SubKon, Retur

**Files:**
- Modify: `frontend/src/views/admin/PurchaseOrderPage.vue`
- Modify: `frontend/src/i18n/id.json`

- [ ] **Step 1: Update PO category dropdown labels**

Find the PO category dropdown (around line 203-212) and update labels:

```vue
<el-form-item :label="t('common.poCategory')">
  <el-select v-model="formModel.po_category" class="w-full" :placeholder="t('common.category')">
    <el-option :label="t('status.production')" value="production" />
    <el-option :label="t('status.subkon')" value="subcont" />
    <el-option :label="t('status.retur')" value="return" />
    <el-option :label="t('status.sample')" value="sample" />
    <el-option :label="t('status.claim')" value="claim" />
    <el-option :label="t('status.suede')" value="suede" />
  </el-select>
</el-form-item>
```

- [ ] **Step 2: Add translations**

In `frontend/src/i18n/id.json`:
```json
"status": {
  "subkon": "SubKon",
  "retur": "Retur"
}
```

In `frontend/src/i18n/en.json`:
```json
"status": {
  "subkon": "SubCon",
  "retur": "Return"
}
```

---

## Task 1.3: PO - SubKon/Retur → Harga Free Text

**Files:**
- Modify: `frontend/src/views/admin/PurchaseOrderPage.vue`

- [ ] **Step 1: Add autoPricingEnabled to formModel**

Add to `formModel` reactive (around line 722):
```javascript
autoPricingEnabled: true,
```

- [ ] **Step 2: Update resetForm**

Add (around line 888):
```javascript
formModel.autoPricingEnabled = true
```

- [ ] **Step 3: Add watcher for category changes**

Add after existing watchers (around line 856):
```javascript
watch(
  () => formModel.po_category,
  (newCategory) => {
    const isSubkonOrRetur = newCategory === 'subcont' || newCategory === 'return'
    formModel.autoPricingEnabled = !isSubkonOrRetur
    if (isSubkonOrRetur) {
      // Keep unit_price_input as manual input
      formModel.unit_price_input = null
    }
  }
)
```

- [ ] **Step 4: Update unit price field to disable auto-resolve**

Find the unit price field (added in previous enhancement) and add disable condition:

```vue
<el-input
  v-model.number="formModel.unit_price_input"
  type="number"
  :step="0.01"
  :controls="false"
  :disabled="!formModel.autoPricingEnabled && formModel.unit_price_input == null"
  class="w-full"
/>
```

Actually, since we made it editable, the field is already free text. The behavior should be:
- Normal category: auto-resolve price, but user can override
- Subkon/Retur: skip auto-resolve, manual input only

Update the buildCurrentDetailBody function (around line 982):

```javascript
async function buildCurrentDetailBody() {
  const body = {
    // ... existing field building ...
  }
  
  const b = (formModel.buyer || '').trim()
  const isFreePrice = formModel.po_category === 'subcont' || formModel.po_category === 'return'
  
  if (isFreePrice) {
    // Free text pricing - use manual input only
    if (formModel.unit_price_input != null) {
      body.unit_price = Number(formModel.unit_price_input)
    }
  } else {
    // Normal pricing - try auto-resolve
    if (b) {
      try {
        const r = await resolveBuyerUnitPrice({
          buyer_code: b,
          material_name: formModel.material_name || null,
          color: formModel.color || null,
          style_article: formModel.style_article || null,
          thickness_text: formModel.thickness_text || null,
          color_family: formModel.color_family || null,
        })
        if (formModel.unit_price_input != null) {
          body.unit_price = Number(formModel.unit_price_input)
        } else if (r.unit_price != null) {
          body.unit_price = Number(r.unit_price)
        }
      } catch {
        if (formModel.unit_price_input != null) {
          body.unit_price = Number(formModel.unit_price_input)
        }
      }
    } else if (formModel.unit_price_input != null) {
      body.unit_price = Number(formModel.unit_price_input)
    }
  }
  return body
}
```

---

## Task 1.4: Exchange Rates - Tanggal Berlaku (Start-End)

**Files:**
- Modify: `backend/app/models.py` - ExchangeRate class
- Modify: `backend/app/schemas.py` - ExchangeRate schemas
- Create: `backend/alembic/versions/xxxx_add_exchange_rate_dates.py`
- Modify: `frontend/src/views/admin/ExchangeRatePage.vue`
- Modify: `frontend/src/i18n/id.json`

- [ ] **Step 1: Add fields to ExchangeRate model**

In `backend/app/models.py`, find ExchangeRate class (line 511-521), add after `effective_date`:
```python
valid_from: Mapped[Optional[date]] = mapped_column(Date)
valid_to: Mapped[Optional[date]] = mapped_column(Date)
```

- [ ] **Step 2: Create Alembic migration**

```bash
cd /Users/wiranto/Projects/Tonghong/backend
alembic revision --autogenerate -m "add_exchange_rate_dates"
```

- [ ] **Step 3: Read ExchangeRatePage.vue to understand structure**

The file needs to be checked. If it exists, add the date fields to the form.

- [ ] **Step 4: Add date fields to form**

Add two date pickers for valid_from and valid_to:
```vue
<el-col :xs="24" :sm="8">
  <el-form-item :label="t('pages.exchangeRates.validFrom')">
    <el-date-picker
      v-model="formModel.valid_from"
      type="date"
      value-format="YYYY-MM-DD"
      class="w-full"
      clearable
    />
  </el-form-item>
</el-col>
<el-col :xs="24" :sm="8">
  <el-form-item :label="t('pages.exchangeRates.validTo')">
    <el-date-picker
      v-model="formModel.valid_to"
      type="date"
      value-format="YYYY-MM-DD"
      class="w-full"
      clearable
    />
  </el-form-item>
</el-col>
```

- [ ] **Step 5: Add translations**

In `frontend/src/i18n/id.json`:
```json
"pages": {
  "exchangeRates": {
    "validFrom": "Berlaku Dari",
    "validTo": "Berlaku Sampai"
  }
}
```

---

## Task 1.5: PO - Tampilkan "No PO Customer" di Table

**Files:**
- Modify: `frontend/src/views/admin/PurchaseOrderPage.vue`

- [ ] **Step 1: Add column to main table**

Find the PO table columns (around line 57-113), add after the po_number column:

```vue
<el-table-column prop="po_customer_ref" :label="t('pages.po.poCustomerRef')" min-width="140" show-overflow-tooltip />
```

---

## Task 1.6: PO - Kelembutan (Softness) Dropdown

**Files:**
- Modify: `frontend/src/views/admin/PurchaseOrderPage.vue`
- Modify: `frontend/src/i18n/id.json`

- [ ] **Step 1: Change softness input to dropdown**

Find the softness form item (around line 328-333) and replace:

```vue
<el-col :xs="24" :md="12">
  <el-form-item :label="t('common.softness')">
    <el-select v-model="formModel.softness" clearable filterable allow-create class="w-full">
      <el-option label="Soft" value="Soft" />
      <el-option label="Medium" value="Medium" />
      <el-option label="Hard" value="Hard" />
      <el-option label="Extra Soft" value="Extra Soft" />
      <el-option label="Super Soft" value="Super Soft" />
    </el-select>
  </el-form-item>
</el-col>
```

- [ ] **Step 2: Add translations**

In `frontend/src/i18n/id.json`:
```json
"common": {
  "softness": "Kelembutan"
}
```

---

## Task 1.7: PO - Remove Field Pabean (AJU) dari Form

**Files:**
- Modify: `frontend/src/views/admin/PurchaseOrderPage.vue`

- [ ] **Step 1: Remove customs_declaration_id from template**

Find the customs field (around line 185-200) and remove it. The field looks like:
```vue
<el-col :xs="24" :md="12">
  <el-form-item :label="`${t('menu.customs')} (${t('common.aju')})`">
    <el-select v-model="formModel.customs_declaration_id" ...>
      ...
    </el-select>
  </el-form-item>
</el-col>
```

Remove this entire block.

- [ ] **Step 2: Remove customs_declaration_id from formModel**

Find `formModel` reactive, remove:
```javascript
customs_declaration_id: null,
```

- [ ] **Step 3: Remove from resetForm**

Remove from resetForm function.

- [ ] **Step 4: Remove from openEditDialog**

Remove loading of customs_declaration_id.

- [ ] **Step 5: Remove from submitForm**

Remove from header body in submitForm.

- [ ] **Step 6: Remove import if not used elsewhere**

Check if `customsList` and `listCustomsDeclarations` are still needed. If not used, remove from imports.

**IMPORTANT:** Keep the data in database - do NOT create migration to drop the column. Just remove from UI.

---

## Summary

| Task | Description | Effort |
|------|-------------|--------|
| 1.1 | Customer Jabatan field | Low |
| 1.2 | PO Kategori labels (SubKon, Retur) | Low |
| 1.3 | PO SubKon/Retur → free price | Low |
| 1.4 | Exchange Rate start-end dates | Low |
| 1.5 | PO table - No PO Customer column | Low |
| 1.6 | PO Softness dropdown | Low |
| 1.7 | Remove Pabean field from PO | Low |

**Total: 7 tasks**

---

## Plan complete and saved to `docs/superpowers/plans/2026-04-15-phase1-quick-wins-plan.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - Dispatch subagent per task for fast iteration

**2. Inline Execution** - Execute tasks sequentially in this session

**Which approach?**
