# PO Form Enhancement Design

**Date:** 2026-04-15
**Project:** Tonghong ERP - PurchaseOrderPage.vue Enhancement
**Author:** AI Assistant

---

## 1. Overview

Meningkatkan PurchaseOrderPage.vue dengan fitur-fitur baru sesuai request marketing:
- Thickness dropdown preset
- ETD Schedule (multi-delivery)
- Billing/Delivery address terpisah
- Editable unit price
- Copy item dari PO lain

---

## 2. UI Changes

### 2.1 Thickness Dropdown Preset

**Location:** Form detail line, field thickness

**Change:** Ubah dari `el-input` ke `el-select` dengan preset options

```vue
<el-select v-model="formModel.thickness_text" class="w-full">
  <el-option label="1.0-1.2" value="1.0-1.2" />
  <el-option label="1.2-1.4" value="1.2-1.4" />
  <el-option label="1.4-1.6" value="1.4-1.6" />
  <el-option label="1.6-1.8" value="1.6-1.8" />
  <el-option label="Lainnya..." value="__custom__" />
</el-select>
```

**Note:** Jika user pilih "Lainnya...", show text input untuk custom value.

### 2.2 ETD Schedule (Multi-Delivery)

**Location:** Di bawah section material line, sebelum buttons

**UI:** Tabel dengan 12 kolom delivery

| # | Qty | Date |
|---|-----|------|
| 1st | [input] | [date picker] |
| 2nd | [input] | [date picker] |
| ... | ... | ... |
| 12th | [input] | [date picker] |

**Button:** "Auto-fill from ETD" - split qty evenly atau default dates

**Backend:** Simpan sebagai `delivery_schedules[]` JSON di detail line

### 2.3 Billing/Delivery Address

**Location:** Header section, Tambahkan setelah field lain

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

**Features:**
- Auto-fill dari customer master data
- User dapat override/edit manual
- Toggle "Same as billing" checkbox

### 2.4 Editable Unit Price

**Location:** Form detail line, field unit_price

**Change:** Ubah dari `readonly` ke editable dengan warning

```vue
<el-form-item :label="t('pages.po.unitPriceUsd')">
  <el-input 
    v-model.number="formModel.unit_price_override" 
    type="number"
    :controls="false"
  />
  <span class="mt-1 block text-xs text-amber-600">
    {{ t('pages.po.priceOverrideHint') }}
  </span>
</el-form-item>
```

**Logic:**
- Jika ada `unit_price_override`, gunakan itu
- Jika kosong, auto-resolve dari buyer price list
- Tampilkan indicator jika price berbeda dari auto-resolve

### 2.5 Copy Item dari PO Lain

**Location:** Di atas tabel draft lines

**UI:** 
```vue
<div class="flex items-center gap-2 mb-3">
  <el-button @click="openCopyItemDialog">
    {{ t('pages.po.copyItemFromOtherPo') }}
  </el-button>
</div>
```

**Dialog:**
- Search/filter PO yang ada
- Tampilkan detail lines dari PO tersebut
- Checkbox untuk pilih line(s)
- Button "Add Selected Lines"

---

## 3. Data Model Changes

### 3.1 PO Header - Tambah Field

```python
# Backend: app/models.py
class PoHeader(Base):
    # existing fields...
    billing_address: Optional[str] = None
    delivery_address: Optional[str] = None
```

### 3.2 PO Detail - Tambah Field

```python
# Backend: app/models.py
class PoDetail(Base):
    # existing fields...
    delivery_schedules: Optional[JSON] = None  # [{seq, qty, date}, ...]
    unit_price_override: Optional[float] = None
    copied_from_detail_id: Optional[int] = None
```

---

## 4. API Changes

### 4.1 PO Header Update
```
PUT /po/{id}
Body: {
  ...existing fields...,
  billing_address: string | null,
  delivery_address: string | null
}
```

### 4.2 PO Detail Create/Update
```
POST /po/{id}/details
PUT /po-detail/{id}
Body: {
  ...existing fields...,
  delivery_schedules: [{seq: 1, qty: 100, date: "2026-05-01"}, ...],
  unit_price_override: float | null
}
```

### 4.3 Copy Item dari PO
```
GET /po?customer_id={id}&status=any  # untuk list PO referensi
GET /po/{po_id}/details  # untuk get detail lines
```

---

## 5. Implementation Order

1. **Thickness dropdown** - Quick win, minimal change
2. **Billing/Delivery address** - Backend + Frontend
3. **Editable unit price** - Frontend + Backend
4. **ETD Schedule** - Complex, UI + Backend + API
5. **Copy item dari PO lain** - Dialog + API integration

---

## 6. Files to Modify

| File | Changes |
|------|---------|
| `frontend/src/views/admin/PurchaseOrderPage.vue` | Main UI enhancements |
| `frontend/src/i18n/id.json`, `en.json`, `zh.json` | Translation keys |
| `backend/app/models.py` | Add new fields |
| `backend/app/schemas/po.py` | Update Pydantic schemas |
| `backend/app/routers/po.py` | Handle new fields in CRUD |
| `backend/alembic/versions/` | Migration for new fields |

---

## 7. Migration Script

```python
# alembic revision
"""add_billing_delivery_addresses_and_etd_schedule"""

def upgrade():
    op.add_column('po_headers', sa.Column('billing_address', sa.Text, nullable=True))
    op.add_column('po_headers', sa.Column('delivery_address', sa.Text, nullable=True))
    op.add_column('po_details', sa.Column('delivery_schedules', sa.JSON, nullable=True))
    op.add_column('po_details', sa.Column('unit_price_override', sa.Float, nullable=True))

def downgrade():
    op.drop_column('po_details', 'unit_price_override')
    op.drop_column('po_details', 'delivery_schedules')
    op.drop_column('po_headers', 'delivery_address')
    op.drop_column('po_headers', 'billing_address')
```

---

## 8. i18n Keys

```json
{
  "pages": {
    "po": {
      "billingAddress": "Billing Address",
      "deliveryAddress": "Delivery Address",
      "etdSchedule": "ETD Schedule",
      "etdQty": "Qty",
      "etdDate": "Date",
      "priceOverrideHint": "Leave empty to auto-resolve from buyer price",
      "copyItemFromOtherPo": "Copy Item from Other PO",
      "selectItemsToCopy": "Select items to copy"
    }
  }
}
```
