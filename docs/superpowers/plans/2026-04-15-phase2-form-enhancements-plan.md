# Phase 2: Form Enhancements Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement 5 medium-effort enhancements across Master Items, Buyer Prices, and Invoice modules.

**Architecture:** Backend model/schema changes + Frontend UI + Export/Import functionality.

**Tech Stack:** Vue 3, Element Plus, FastAPI, SQLAlchemy, Alembic, openpyxl

---

## File Inventory

| File | Tasks |
|------|-------|
| `backend/app/models.py` | 2.1, 2.3, 2.4, 2.5 |
| `backend/app/schemas.py` | 2.1, 2.3, 2.4, 2.5 |
| `backend/app/routers/master_items.py` | 2.2 |
| `backend/app/routers/invoices.py` | 2.5 |
| `frontend/src/views/admin/MasterItemsPage.vue` | 2.1, 2.4 |
| `frontend/src/views/admin/BuyerPricePage.vue` | 2.3 |
| `frontend/src/views/admin/InvoicePage.vue` | 2.5 |
| `frontend/src/i18n/id.json` | 2.1, 2.3, 2.4, 2.5 |

---

## Task 2.1: Master Items - Thickness Format Range

**Files:**
- Modify: `backend/app/models.py` - MasterItem class
- Modify: `backend/app/schemas.py` - MasterItem schemas
- Create: `backend/alembic/versions/xxxx_add_thickness_range.py`
- Modify: `frontend/src/views/admin/MasterItemsPage.vue`

- [ ] **Step 1: Add thickness_range field to MasterItem model**

In `backend/app/models.py`, find MasterItem class (line 57-82), add after `thickness_mm`:
```python
thickness_range: Mapped[Optional[str]] = mapped_column(String(80))
```

- [ ] **Step 2: Update Pydantic schemas**

In `backend/app/schemas.py`, add `thickness_range` to:
- `MasterItemCreate` (after thickness_mm)
- `MasterItemOut` (after thickness_mm)

```python
thickness_range: Optional[str] = None
```

- [ ] **Step 3: Create Alembic migration**

```bash
cd /Users/wiranto/Projects/Tonghong/backend && alembic revision --autogenerate -m "add_thickness_range"
```

- [ ] **Step 4: Update MasterItemsPage.vue form**

Find the thickness field (around line 47-49). Replace the single value input with range format:

Current:
```vue
<el-col :xs="24" :md="12">
  <el-form-item :label="t('common.thickness')">
    <el-input v-model="form.thickness_mm" type="number" step="0.001" />
  </el-form-item>
</el-col>
```

Replace with:
```vue
<el-col :xs="24" :md="12">
  <el-form-item :label="t('common.thickness')">
    <el-input 
      v-model="form.thickness_range" 
      placeholder="1.2-1.4"
      clearable
    />
  </el-form-item>
</el-col>
```

Also keep thickness_mm as hidden for backward compatibility, or update to store min/max:

```vue
<!-- Hidden fields for min/max if needed -->
<input type="hidden" v-model="form.thickness_min" />
<input type="hidden" v-model="form.thickness_max" />
```

- [ ] **Step 5: Update formModel reactive**

Add to form object (around line 130):
```javascript
thickness_range: '',
```

- [ ] **Step 6: Update resetForm**

Add (around line 157):
```javascript
form.thickness_range = ''
```

- [ ] **Step 7: Update openEdit**

Add loading (around line 185):
```javascript
form.thickness_range = row.thickness_range || ''
```

- [ ] **Step 8: Update submit payload**

Add to payload (around line 208):
```javascript
thickness_range: form.thickness_range || undefined,
```

- [ ] **Step 9: Add translations**

In `frontend/src/i18n/id.json`:
```json
"pages": {
  "masterItems": {
    "thicknessRangeHint": "Format: 1.2-1.4"
  }
}
```

---

## Task 2.2: Master Items - Export/Import Excel

**Files:**
- Modify: `backend/app/routers/master_items.py` - Add export/import endpoints
- Create: `backend/app/services/excel_service.py` - Excel processing
- Modify: `frontend/src/views/admin/MasterItemsPage.vue` - Add buttons
- Modify: `frontend/src/api/client.js` - Add API functions

- [ ] **Step 1: Read existing master_items router**

Read `/Users/wiranto/Projects/Tonghong/backend/app/routers/master_items.py` to understand structure.

- [ ] **Step 2: Create Excel service**

Create `backend/app/services/excel_service.py`:
```python
from openpyxl import Workbook, load_workbook
from typing import BinaryIO
import io

def export_master_items(items: list[dict]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Master Items"
    
    headers = ["item_code", "material_name", "thickness_range", "color", "emboss", "softness", "color_reference", "backing", "style_article", "model", "category", "exim_material_code"]
    
    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header.replace("_", " ").title())
    
    for row, item in enumerate(items, 2):
        for col, header in enumerate(headers, 1):
            ws.cell(row=row, column=col, value=item.get(header, ""))
    
    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

def import_master_items(file_content: bytes) -> list[dict]:
    wb = load_workbook(io.BytesIO(file_content))
    ws = wb.active
    
    headers = [cell.value for cell in ws[1]]
    
    items = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:  # Skip empty rows
            continue
        item = {headers[i]: str(row[i]) if row[i] is not None else "" for i in range(len(headers))}
        items.append(item)
    
    return items
```

- [ ] **Step 3: Add export endpoint to router**

```python
@router.get("/export")
async def export_master_items():
    from app.services.excel_service import export_master_items
    from app.db import SessionLocal
    from app.models import MasterItem
    
    db = SessionLocal()
    try:
        items = db.query(MasterItem).all()
        data = [row_to_dict(item) for item in items]
        excel_content = export_master_items(data)
        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            io.BytesIO(excel_content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=master_items.xlsx"}
        )
    finally:
        db.close()
```

- [ ] **Step 4: Add import endpoint to router**

```python
from fastapi import UploadFile, File

@router.post("/import")
async def import_master_items(file: UploadFile = File(...)):
    from app.services.excel_service import import_master_items
    from app.db import SessionLocal
    from app.models import MasterItem
    
    content = await file.read()
    items = import_master_items(content)
    
    db = SessionLocal()
    try:
        imported = 0
        for item_data in items:
            existing = db.query(MasterItem).filter(MasterItem.item_code == item_data.get("item_code")).first()
            if existing:
                for key, value in item_data.items():
                    if hasattr(existing, key) and value:
                        setattr(existing, key, value)
            else:
                new_item = MasterItem(**item_data)
                db.add(new_item)
            imported += 1
        
        db.commit()
        return {"imported": imported, "items": items}
    finally:
        db.close()
```

- [ ] **Step 5: Add API functions to frontend client.js**

```javascript
export async function exportMasterItems() {
  const response = await api.get('/master-items/export', { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', 'master_items.xlsx')
  document.body.appendChild(link)
  link.click()
  link.remove()
}

export async function importMasterItems(file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/master-items/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}
```

- [ ] **Step 6: Update MasterItemsPage.vue**

Add buttons in toolbar (around line 5):
```vue
<el-button @click="handleExport">{{ t('pages.masterItems.export') }}</el-button>
<el-button type="success" @click="openImportDialog">{{ t('pages.masterItems.import') }}</el-button>
```

Add import dialog:
```vue
<el-dialog v-model="importDialogVisible" :title="t('pages.masterItems.importTitle')" width="500px">
  <el-upload
    ref="uploadRef"
    :auto-upload="false"
    :limit="1"
    accept=".xlsx,.xls"
    :on-change="handleFileChange"
  >
    <el-button type="primary">{{ t('pages.masterItems.selectFile') }}</el-button>
  </el-upload>
  <template #footer>
    <el-button @click="importDialogVisible = false">{{ t('common.cancel') }}</el-button>
    <el-button type="primary" :disabled="!importFile" @click="handleImport">
      {{ t('pages.masterItems.import') }}
    </el-button>
  </template>
</el-dialog>
```

Add reactive data and functions:
```javascript
const importDialogVisible = ref(false)
const importFile = ref(null)
const uploadRef = ref(null)

function openImportDialog() {
  importDialogVisible.value = true
  importFile.value = null
}

function handleFileChange(file) {
  importFile.value = file.raw
}

async function handleExport() {
  await exportMasterItems()
  ElMessage.success(t('pages.masterItems.exportSuccess'))
}

async function handleImport() {
  if (!importFile.value) return
  try {
    const result = await importMasterItems(importFile.value)
    ElMessage.success(t('pages.masterItems.importSuccess', { count: result.imported }))
    importDialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}
```

- [ ] **Step 7: Add translations**

```json
"pages": {
  "masterItems": {
    "export": "Export Excel",
    "import": "Import Excel",
    "importTitle": "Import Master Items",
    "selectFile": "Pilih File",
    "exportSuccess": "Export berhasil",
    "importSuccess": "{count} item berhasil diimport"
  }
}
```

---

## Task 2.3: Buyer Prices - Multi Currency

**Files:**
- Modify: `backend/app/models.py` - BuyerPriceList class
- Modify: `backend/app/schemas.py` - BuyerPriceList schemas
- Create: `backend/alembic/versions/xxxx_add_currency.py`
- Modify: `frontend/src/views/admin/BuyerPricePage.vue`

- [ ] **Step 1: Add currency field to BuyerPriceList model**

In `backend/app/models.py`, find BuyerPriceList class (line 146-167), add after `buyer_code`:
```python
currency: Mapped[str] = mapped_column(String(3), default="USD")
```

- [ ] **Step 2: Create Alembic migration**

```bash
cd /Users/wiranto/Projects/Tonghong/backend && alembic revision --autogenerate -m "add_buyer_price_currency"
```

- [ ] **Step 3: Update Pydantic schemas**

In `backend/app/schemas.py`, add to BuyerPriceListCreate and BuyerPriceListUpdate:
```python
currency: str = "USD"
```

- [ ] **Step 4: Update BuyerPricePage.vue**

Find the header form (around line 93-133). Add currency dropdown after buyer_code field or in header section:

```vue
<el-col :xs="24" :sm="12">
  <el-form-item :label="t('pages.buyerPrices.currency')">
    <el-select v-model="headerForm.currency" class="w-full">
      <el-option label="USD" value="USD" />
      <el-option label="IDR" value="IDR" />
      <el-option label="EUR" value="EUR" />
    </el-select>
  </el-form-item>
</el-col>
```

Update headerForm reactive:
```javascript
currency: 'USD',
```

- [ ] **Step 5: Add translations**

```json
"pages": {
  "buyerPrices": {
    "currency": "Mata Uang"
  }
}
```

---

## Task 2.4: Master Items - Color Standard, Model (Take Down)

**Files:**
- Modify: `backend/app/models.py` - MasterItem class
- Modify: `backend/app/schemas.py` - MasterItem schemas
- Create: `backend/alembic/versions/xxxx_add_color_standard.py`
- Modify: `frontend/src/views/admin/MasterItemsPage.vue`

- [ ] **Step 1: Add new fields to MasterItem model**

In `backend/app/models.py`, find MasterItem class, add after `color_reference`:
```python
color_standard: Mapped[Optional[str]] = mapped_column(String(255))
model_takedown: Mapped[Optional[str]] = mapped_column(String(100))
```

- [ ] **Step 2: Create Alembic migration**

```bash
cd /Users/wiranto/Projects/Tonghong/backend && alembic revision --autogenerate -m "add_color_standard_model_takedown"
```

- [ ] **Step 3: Update Pydantic schemas**

In `backend/app/schemas.py`, add to MasterItemCreate and MasterItemOut:
```python
color_standard: Optional[str] = None
model_takedown: Optional[str] = None
```

- [ ] **Step 4: Update MasterItemsPage.vue form**

Add after color_reference field:
```vue
<el-col :xs="24" :md="12">
  <el-form-item :label="t('pages.masterItems.colorStandard')">
    <el-input v-model="form.color_standard" maxlength="255" />
  </el-form-item>
</el-col>
<el-col :xs="24" :md="12">
  <el-form-item :label="t('pages.masterItems.modelTakedown')">
    <el-input v-model="form.model_takedown" maxlength="100" />
  </el-form-item>
</el-col>
```

- [ ] **Step 5: Update form reactive and functions**

Add to form object:
```javascript
color_standard: '',
model_takedown: '',
```

Update resetForm, openEdit, submit as before.

- [ ] **Step 6: Add translations**

```json
"pages": {
  "masterItems": {
    "colorStandard": "Color Standard",
    "modelTakedown": "Model (Take Down)"
  }
}
```

---

## Task 2.5: Invoice - Payment Detail

**Files:**
- Modify: `backend/app/models.py` - Invoice class
- Modify: `backend/app/schemas.py` - Invoice schemas
- Create: `backend/alembic/versions/xxxx_add_invoice_payment.py`
- Modify: `frontend/src/views/admin/InvoicePage.vue`

- [ ] **Step 1: Add payment fields to Invoice model**

In `backend/app/models.py`, find Invoice class (line 457-489), add after `nomor_aju`:
```python
payment_date: Mapped[Optional[date]] = mapped_column(Date)
payment_bank_account: Mapped[Optional[str]] = mapped_column(String(100))
payment_proof_url: Mapped[Optional[str]] = mapped_column(String(500))
payment_status: Mapped[str] = mapped_column(String(20), default="unpaid")
```

- [ ] **Step 2: Create Alembic migration**

```bash
cd /Users/wiranto/Projects/Tonghong/backend && alembic revision --autogenerate -m "add_invoice_payment_fields"
```

- [ ] **Step 3: Update Pydantic schemas**

In `backend/app/schemas.py`, add to InvoiceCreate, InvoiceUpdate, InvoiceOut:
```python
payment_date: Optional[date] = None
payment_bank_account: Optional[str] = None
payment_proof_url: Optional[str] = None
payment_status: str = "unpaid"
```

- [ ] **Step 4: Read InvoicePage.vue**

First read `/Users/wiranto/Projects/Tonghong/frontend/src/views/admin/InvoicePage.vue` to understand structure.

- [ ] **Step 5: Add payment fields to form**

Add in the form section:
```vue
<el-col :xs="24" :md="12">
  <el-form-item :label="t('pages.invoice.paymentStatus')">
    <el-select v-model="form.payment_status" class="w-full">
      <el-option :label="t('pages.invoice.unpaid')" value="unpaid" />
      <el-option :label="t('pages.invoice.paid')" value="paid" />
    </el-select>
  </el-form-item>
</el-col>
<el-col :xs="24" :md="12">
  <el-form-item :label="t('pages.invoice.paymentDate')">
    <el-date-picker
      v-model="form.payment_date"
      type="date"
      value-format="YYYY-MM-DD"
      class="w-full"
      clearable
    />
  </el-form-item>
</el-col>
<el-col :xs="24" :md="12">
  <el-form-item :label="t('pages.invoice.paymentBankAccount')">
    <el-input v-model="form.payment_bank_account" maxlength="100" />
  </el-form-item>
</el-col>
<el-col :xs="24" :md="12">
  <el-form-item :label="t('pages.invoice.paymentProof')">
    <el-input v-model="form.payment_proof_url" maxlength="500" placeholder="URL atau path file" />
  </el-form-item>
</el-col>
```

- [ ] **Step 6: Update reactive, resetForm, openEdit, submit**

Add to form reactive:
```javascript
payment_date: '',
payment_bank_account: '',
payment_proof_url: '',
payment_status: 'unpaid',
```

- [ ] **Step 7: Add table column for payment status**

Find the table columns and add after status or relevant column:
```vue
<el-table-column :label="t('pages.invoice.paymentStatus')" width="120">
  <template #default="{ row }">
    <el-tag :type="row.payment_status === 'paid' ? 'success' : 'warning'">
      {{ t(`pages.invoice.${row.payment_status}`) }}
    </el-tag>
  </template>
</el-table-column>
```

- [ ] **Step 8: Add translations**

```json
"pages": {
  "invoice": {
    "paymentStatus": "Status Pembayaran",
    "paymentDate": "Tanggal Transfer",
    "paymentBankAccount": "Rekening Bank",
    "paymentProof": "Bukti Bayar",
    "unpaid": "Belum Bayar",
    "paid": "Lunas"
  }
}
```

---

## Summary

| Task | Description | Effort |
|------|-------------|--------|
| 2.1 | Master Items thickness range (1.2-1.4) | Medium |
| 2.2 | Master Items export/import Excel | Medium |
| 2.3 | Buyer Prices multi-currency | Medium |
| 2.4 | Master Items color standard, model takedown | Medium |
| 2.5 | Invoice payment details | Medium |

**Total: 5 tasks**

---

## Dependencies

- Task 2.2 (Excel) requires openpyxl: `pip install openpyxl`
- All tasks are independent except 2.4 can be done after 2.1

---

## Plan complete and saved to `docs/superpowers/plans/2026-04-15-phase2-form-enhancements-plan.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - Dispatch subagent per task for fast iteration

**2. Inline Execution** - Execute tasks sequentially in this session

**Which approach?**
