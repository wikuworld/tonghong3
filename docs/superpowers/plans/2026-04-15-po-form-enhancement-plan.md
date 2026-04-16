# PO Form Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enhance PurchaseOrderPage.vue with thickness dropdown, ETD schedule, billing/delivery address, editable unit price, and copy item from other PO.

**Architecture:** Frontend-only changes with API integration. Backend model/schema updates for new fields. All features addable without breaking existing functionality.

**Tech Stack:** Vue 3, Element Plus, FastAPI, SQLAlchemy, Alembic

---

## File Inventory

| File | Action |
|------|--------|
| `frontend/src/views/admin/PurchaseOrderPage.vue` | Modify - main UI |
| `frontend/src/i18n/id.json` | Modify - translations |
| `frontend/src/api/client.js` | Modify - add copy item API |
| `backend/app/models.py` | Modify - add new fields |
| `backend/app/schemas/po.py` | Modify - update Pydantic schemas |
| `backend/app/routers/po.py` | Modify - handle new fields |
| `backend/alembic/versions/` | Create - migration |

---

## Task 1: Thickness Dropdown Preset

**Files:**
- Modify: `frontend/src/views/admin/PurchaseOrderPage.vue:298-301`

- [ ] **Step 1: Change thickness input to dropdown**

Replace lines 298-301 (thickness input) with:

```vue
<el-col :xs="24" :md="12">
  <el-form-item :label="t('common.thickness')">
    <el-select
      v-model="formModel.thickness_text"
      clearable
      filterable
      allow-create
      class="w-full"
      :placeholder="t('common.placeholder.thickness')"
    >
      <el-option label="1.0-1.2" value="1.0-1.2" />
      <el-option label="1.2-1.4" value="1.2-1.4" />
      <el-option label="1.4-1.6" value="1.4-1.6" />
      <el-option label="1.6-1.8" value="1.6-1.8" />
    </el-select>
  </el-form-item>
</el-col>
```

- [ ] **Step 2: Add translation for placeholder**

Add to `frontend/src/i18n/id.json`:
```json
"placeholder": {
  "thickness": "Pilih atau ketik ketebalan"
}
```

- [ ] **Step 3: Test the dropdown renders correctly**

Verify Element Plus `el-select` with `allow-create` allows both preset selection and custom input.

---

## Task 2: Billing/Delivery Address

**Files:**
- Modify: `backend/app/models.py` - PoHeader class
- Modify: `backend/app/schemas/po.py` - PoHeaderCreate/Update schemas
- Create: `backend/alembic/versions/xxxx_add_address_fields.py`
- Modify: `frontend/src/views/admin/PurchaseOrderPage.vue` - add form fields

- [ ] **Step 1: Add fields to backend model**

In `backend/app/models.py`, find `PoHeader` class, add after `remark` field:
```python
billing_address: Optional[str] = Field(None, sa_column=sa.Column(sa.Text))
delivery_address: Optional[str] = Field(None, sa.Column(sa.Text))
```

- [ ] **Step 2: Update Pydantic schemas**

In `backend/app/schemas/po.py`, add to `PoHeaderCreate` and `PoHeaderUpdate`:
```python
billing_address: Optional[str] = None
delivery_address: Optional[str] = None
```

- [ ] **Step 3: Create Alembic migration**

```bash
cd backend
alembic revision --autogenerate -m "add_billing_delivery_address"
```

- [ ] **Step 4: Add UI fields to PO dialog**

In `PurchaseOrderPage.vue`, add after line 249 (after remark field):

```vue
<el-col :xs="24" :md="12">
  <el-form-item :label="t('pages.po.billingAddress')">
    <el-input v-model="formModel.billing_address" type="textarea" :rows="2" />
  </el-form-item>
</el-col>
<el-col :xs="24" :md="12">
  <el-form-item :label="t('pages.po.deliveryAddress')">
    <el-input v-model="formModel.delivery_address" type="textarea" :rows="2" />
  </el-form-item>
</el-col>
```

- [ ] **Step 5: Update formModel reactive**

Add to `formModel` reactive object (around line 722):
```javascript
billing_address: '',
delivery_address: '',
```

- [ ] **Step 6: Update resetForm function**

Add to `resetForm` function (around line 858):
```javascript
formModel.billing_address = ''
formModel.delivery_address = ''
```

- [ ] **Step 7: Update openEditDialog**

Add loading of address fields (around line 1091-1092):
```javascript
formModel.remark = row.remark || ''
formModel.billing_address = row.billing_address || ''
formModel.delivery_address = row.delivery_address || ''
```

- [ ] **Step 8: Update submitForm header body**

Add to header object in `submitForm` (around line 1163):
```javascript
billing_address: formModel.billing_address?.trim() || undefined,
delivery_address: formModel.delivery_address?.trim() || undefined,
```

- [ ] **Step 9: Add translations**

Add to `frontend/src/i18n/id.json`:
```json
"pages": {
  "po": {
    "billingAddress": "Alamat Penagihan",
    "deliveryAddress": "Alamat Pengiriman"
  }
}
```

---

## Task 3: Editable Unit Price

**Files:**
- Modify: `frontend/src/views/admin/PurchaseOrderPage.vue` - make price editable

- [ ] **Step 1: Update unit price field to be editable**

Replace lines 378-383 (readonly price field) with:

```vue
<el-col :xs="24" :md="12">
  <el-form-item :label="t('pages.po.unitPriceUsd')">
    <el-input
      v-model.number="formModel.unit_price_input"
      type="number"
      :step="0.01"
      :controls="false"
      class="w-full"
    />
    <div class="mt-1 flex items-center gap-2">
      <span v-if="previewResolvedUnitPrice.value != null" class="text-xs text-slate-500">
        {{ t('pages.po.autoResolved') }}: {{ previewResolvedUnitPrice.value }}
      </span>
      <el-tag v-if="formModel.unit_price_input && previewResolvedUnitPrice.value != null && formModel.unit_price_input !== previewResolvedUnitPrice.value" size="small" type="warning">
        {{ t('pages.po.overridden') }}
      </el-tag>
    </div>
  </el-form-item>
</el-col>
```

- [ ] **Step 2: Add unit_price_input to formModel**

Add to `formModel` reactive:
```javascript
unit_price_input: null,
```

- [ ] **Step 3: Update onMasterItemChange to set unit_price_input**

Add to `onMasterItemChange` function:
```javascript
if (item && previewResolvedUnitPrice.value != null) {
  formModel.unit_price_input = previewResolvedUnitPrice.value
} else {
  formModel.unit_price_input = null
}
```

- [ ] **Step 4: Update buildCurrentDetailBody to use override price**

Modify function around line 982-997:

```javascript
async function buildCurrentDetailBody() {
  const body = {
    // ... existing fields ...
  }
  const b = (formModel.buyer || '').trim()
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
      // Use override if set, otherwise auto-resolve
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
  return body
}
```

- [ ] **Step 5: Add translations**

Add to `frontend/src/i18n/id.json`:
```json
"pages": {
  "po": {
    "autoResolved": "Auto:",
    "overridden": "Dioverride"
  }
}
```

---

## Task 4: ETD Schedule (Multi-Delivery)

**Files:**
- Modify: `backend/app/models.py` - PoDetail class
- Modify: `backend/app/schemas/po.py` - schemas
- Create: `backend/alembic/versions/xxxx_add_etd_schedule.py`
- Modify: `frontend/src/views/admin/PurchaseOrderPage.vue` - add schedule UI

- [ ] **Step 1: Add delivery_schedules to backend model**

In `backend/app/models.py`, find `PoDetail` class, add:
```python
delivery_schedules: Optional[dict] = Field(None, sa_column=sa.Column(sa.JSON))
```

- [ ] **Step 2: Update Pydantic schemas**

In `backend/app/schemas/po.py`, add to `PoDetailCreate`, `PoDetailUpdate`, `PoDetailOut`:
```python
delivery_schedules: Optional[dict] = None
```

- [ ] **Step 3: Create Alembic migration**

```bash
cd backend
alembic revision --autogenerate -m "add_delivery_schedules"
```

- [ ] **Step 4: Add ETD Schedule UI component**

In `PurchaseOrderPage.vue`, add after line 383 (after unit price field), before `</el-row>`:

```vue
<el-col :xs="24">
  <el-form-item :label="t('pages.po.etdSchedule')">
    <el-table :data="etdScheduleRows" border size="small" class="etd-schedule-table">
      <el-table-column :label="t('common.noLabel')" width="60" align="center">
        <template #default="{ $index }">{{ $index + 1 }}{{ ordinalSuffix($index + 1) }}</template>
      </el-table-column>
      <el-table-column :label="t('pages.po.etdQty')" width="120">
        <template #default="{ $index }">
          <el-input-number
            v-model="etdScheduleRows[$index].qty"
            :min="0"
            :controls="false"
            size="small"
            class="w-full"
          />
        </template>
      </el-table-column>
      <el-table-column :label="t('pages.po.etdDate')">
        <template #default="{ $index }">
          <el-date-picker
            v-model="etdScheduleRows[$index].date"
            type="date"
            size="small"
            class="w-full"
            value-format="YYYY-MM-DD"
          />
        </template>
      </el-table-column>
    </el-table>
    <div class="mt-2">
      <el-button size="small" @click="clearEtdSchedule">{{ t('common.clear') }}</el-button>
      <el-button size="small" type="primary" @click="autoFillEtdSchedule">{{ t('pages.po.autoFillFromEtd') }}</el-button>
    </div>
  </el-form-item>
</el-col>
```

- [ ] **Step 5: Add reactive data for ETD schedule**

Add to script section:
```javascript
const etdScheduleRows = ref([
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
])

function ordinalSuffix(index) {
  const j = index % 10
  const k = index % 100
  if (j === 1 && k !== 11) return 'st'
  if (j === 2 && k !== 12) return 'nd'
  if (j === 3 && k !== 13) return 'rd'
  return 'th'
}

function clearEtdSchedule() {
  etdScheduleRows.value = Array.from({ length: 12 }, () => ({ qty: null, date: '' }))
}

function autoFillEtdSchedule() {
  const qty = formModel.quantity_order ? Number(formModel.quantity_order) : 0
  if (!qty) return
  const eachQty = Math.floor(qty / 12)
  const remainder = qty % 12
  const baseDate = formModel.line_etd ? new Date(formModel.line_etd) : new Date()
  etdScheduleRows.value = Array.from({ length: 12 }, (_, i) => {
    const d = new Date(baseDate)
    d.setDate(d.getDate() + i * 7)
    return {
      qty: i < remainder ? eachQty + 1 : eachQty,
      date: i < remainder && i === 0 ? formModel.line_etd : d.toISOString().slice(0, 10)
    }
  })
}
```

- [ ] **Step 6: Update resetForm to clear ETD schedule**

Add to `resetForm`:
```javascript
clearEtdSchedule()
```

- [ ] **Step 7: Update buildCurrentDetailBody to include schedules**

Add to `buildCurrentDetailBody`:
```javascript
// Filter out empty rows
body.delivery_schedules = etdScheduleRows.value
  .filter(r => r.qty != null || r.date)
  .map((r, i) => ({ sequence_no: i + 1, qty: r.qty, delivery_date: r.date }))
```

- [ ] **Step 8: Add translations**

Add to `frontend/src/i18n/id.json`:
```json
"pages": {
  "po": {
    "etdSchedule": "Jadwal Pengiriman (ETD)",
    "etdQty": "Qty",
    "etdDate": "Tanggal",
    "autoFillFromEtd": "Auto-fill dari ETD"
  }
}
```

---

## Task 5: Copy Item dari PO Lain

**Files:**
- Modify: `frontend/src/api/client.js` - add copy item API
- Modify: `frontend/src/views/admin/PurchaseOrderPage.vue` - add copy dialog
- Add: CSS styles for dialog

- [ ] **Step 1: Add API function for fetching PO details**

In `frontend/src/api/client.js`, add:

```javascript
export async function listPoForCopy(params) {
  const searchParams = new URLSearchParams()
  if (params.customer_id) searchParams.set('customer_id', params.customer_id)
  searchParams.set('limit', '100')
  const res = await api.get(`/po?${searchParams.toString()}`)
  return res.data
}
```

- [ ] **Step 2: Add copy item dialog**

In `PurchaseOrderPage.vue`, add after line 547 (before closing `</AdminSection>`):

```vue
<el-dialog
  v-model="copyItemDialogVisible"
  :title="t('pages.po.copyItemFromOtherPo')"
  width="900px"
  destroy-on-close
  align-center
>
  <el-form label-position="top">
    <el-form-item :label="t('common.customer')">
      <el-select
        v-model="copyItemCustomerId"
        clearable
        filterable
        class="w-full"
        :placeholder="t('common.placeholder.customer')"
        @change="onCopyItemCustomerChange"
      >
        <el-option
          v-for="c in customers"
          :key="c.id"
          :label="customerOptionLabel(c)"
          :value="c.id"
        />
      </el-select>
    </el-form-item>
  </el-form>
  
  <el-table
    v-if="copyItemSourcePo"
    :data="copyItemSourcePo"
    border
    size="small"
    max-height="300"
    @selection-change="onCopyItemSelectionChange"
  >
    <el-table-column type="selection" width="55" />
    <el-table-column prop="po_number" :label="t('common.poNo')" width="150" />
    <el-table-column prop="material_name" :label="t('common.material')" min-width="160" />
    <el-table-column prop="thickness_text" :label="t('common.thickness')" width="100" />
    <el-table-column prop="color" :label="t('common.color')" width="100" />
    <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="100" />
  </el-table>
</el-dialog>
<template #footer>
  <div class="po-dialog-footer">
    <el-button @click="copyItemDialogVisible = false">{{ t('common.cancel') }}</el-button>
    <el-button type="primary" :disabled="!copyItemSelected.length" @click="addCopiedItems">
      {{ t('pages.po.addSelectedItems') }} ({{ copyItemSelected.length }})
    </el-button>
  </div>
</template>
```

- [ ] **Step 3: Add copy item reactive data**

Add to script:
```javascript
const copyItemDialogVisible = ref(false)
const copyItemCustomerId = ref(null)
const copyItemSourcePo = ref([])
const copyItemSelected = ref([])

async function openCopyItemDialog() {
  copyItemCustomerId.value = formModel.customer_id
  copyItemSelected.value = []
  copyItemSourcePo.value = []
  if (copyItemCustomerId.value) {
    await loadCopyItemSourcePos()
  }
  copyItemDialogVisible.value = true
}

async function loadCopyItemSourcePos() {
  if (!copyItemCustomerId.value) return
  try {
    const pos = await listPoForCopy({ customer_id: copyItemCustomerId.value })
    const allDetails = await Promise.all(
      pos.filter(p => p.id !== editingPoId.value).map(p => listPoDetails(p.id).catch(() => []))
    )
    copyItemSourcePo.value = allDetails.flat().map(d => ({
      ...d,
      source_po_number: pos.find(p => p.id === d.po_id)?.po_number
    }))
  } catch {
    copyItemSourcePo.value = []
  }
}

async function onCopyItemCustomerChange() {
  await loadCopyItemSourcePos()
}

function onCopyItemSelectionChange(selection) {
  copyItemSelected.value = selection
}

function addCopiedItems() {
  const newLines = copyItemSelected.value.map(d => ({
    ...d,
    id: undefined,
    copied_from_detail_id: d.id
  }))
  draftLines.value.push(...newLines)
  copyItemDialogVisible.value = false
  ElMessage.success(t('pages.po.itemsCopied', { count: newLines.length }))
}
```

- [ ] **Step 4: Add button to open copy dialog**

Add after line 388 (after copy line button):

```vue
<el-button :icon="DocumentCopy" @click="openCopyItemDialog">{{ t('pages.po.copyItemFromOtherPo') }}</el-button>
```

- [ ] **Step 5: Add translations**

Add to `frontend/src/i18n/id.json`:
```json
"pages": {
  "po": {
    "copyItemFromOtherPo": "Copy Item dari PO Lain",
    "addSelectedItems": "Tambah Item Terpilih",
    "itemsCopied": "{count} item berhasil disalin"
  }
}
```

---

## Summary

| Task | Effort | Description |
|------|--------|-------------|
| 1. Thickness Dropdown | Low | Quick UI change |
| 2. Billing/Delivery Address | Medium | Backend + Frontend |
| 3. Editable Unit Price | Low | UI change |
| 4. ETD Schedule | High | Complex table UI + Backend |
| 5. Copy Item dari PO | Medium | Dialog + API |

**Total: 5 tasks**

---

## Plan complete and saved to `docs/superpowers/plans/2026-04-15-po-form-enhancement-plan.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - Dispatch subagent per task for fast iteration

**2. Inline Execution** - Execute tasks sequentially in this session

**Which approach?**
