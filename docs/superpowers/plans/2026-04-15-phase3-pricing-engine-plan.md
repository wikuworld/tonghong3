# Phase 3: Pricing Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement rule-based pricing engine with special prices, discounts, customer-based pricing, and bulk update functionality.

**Architecture:** Backend service layer for pricing logic, new database models, API endpoints, and frontend UI for managing prices.

**Tech Stack:** Vue 3, Element Plus, FastAPI, SQLAlchemy, Alembic

---

## File Inventory

| File | Tasks |
|------|-------|
| `backend/app/models.py` | 3.1, 3.2 |
| `backend/app/schemas.py` | 3.1, 3.2 |
| `backend/app/services/pricing_service.py` | 3.3 |
| `backend/app/routers/pricing.py` | 3.1, 3.2, 3.3 |
| `backend/alembic/versions/` | 3.1, 3.2 |
| `frontend/src/views/admin/SpecialPricesPage.vue` | 3.1, 3.2 |
| `frontend/src/views/admin/BulkPriceUpdatePage.vue` | 3.3 |
| `frontend/src/api/client.js` | 3.1, 3.2, 3.3 |
| `frontend/src/i18n/id.json` | 3.1, 3.2, 3.3 |

---

## Task 3.1: Special Prices / Discounts

### Data Model

Create new table for special prices and discounts:

```python
class SpecialPrice(Base):
    __tablename__ = "special_prices"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    buyer_code: Mapped[str] = mapped_column(String(32))
    material_pattern: Mapped[Optional[str]] = mapped_column(String(255))  # regex or exact match
    emboss_pattern: Mapped[Optional[str]] = mapped_column(String(100))
    color_pattern: Mapped[Optional[str]] = mapped_column(String(100))
    discount_type: Mapped[str] = mapped_column(String(20))  # "nominal" or "percentage"
    discount_value: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_to: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
```

### Implementation Steps

- [ ] **Step 1: Add SpecialPrice model to models.py**

Add after existing models (around line 180):

```python
class SpecialPrice(Base):
    """Harga khusus/diskon per buyer untuk material tertentu."""
    
    __tablename__ = "special_prices"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    buyer_code: Mapped[str] = mapped_column(String(32))
    material_pattern: Mapped[Optional[str]] = mapped_column(String(255))
    emboss_pattern: Mapped[Optional[str]] = mapped_column(String(100))
    color_pattern: Mapped[Optional[str]] = mapped_column(String(100))
    discount_type: Mapped[str] = mapped_column(String(20))  # "nominal" or "percentage"
    discount_value: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_to: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
```

- [ ] **Step 2: Add Pydantic schemas**

In `schemas.py`, add:

```python
# --- Special Prices ---
class SpecialPriceCreate(BaseModel):
    buyer_code: str
    material_pattern: Optional[str] = None
    emboss_pattern: Optional[str] = None
    color_pattern: Optional[str] = None
    discount_type: str = "percentage"  # "nominal" or "percentage"
    discount_value: Decimal
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: bool = True

class SpecialPriceUpdate(BaseModel):
    buyer_code: Optional[str] = None
    material_pattern: Optional[str] = None
    emboss_pattern: Optional[str] = None
    color_pattern: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[Decimal] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: Optional[bool] = None

class SpecialPriceOut(ORMBase):
    id: int
    buyer_code: str
    material_pattern: Optional[str] = None
    emboss_pattern: Optional[str] = None
    color_pattern: Optional[str] = None
    discount_type: str
    discount_value: Decimal
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: bool
    created_at: Optional[datetime] = None
```

- [ ] **Step 3: Create Alembic migration**

```bash
cd /Users/wiranto/Projects/Tonghong/backend && alembic revision --autogenerate -m "add_special_prices"
```

- [ ] **Step 4: Create pricing router**

Create `backend/app/routers/pricing.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import SpecialPrice
from app.schemas import SpecialPriceCreate, SpecialPriceUpdate, SpecialPriceOut

router = APIRouter(prefix="/pricing", tags=["pricing"])

@router.get("/special-prices", response_model=list[SpecialPriceOut])
def list_special_prices(
    buyer_code: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(SpecialPrice).filter(SpecialPrice.is_active == True)
    if buyer_code:
        query = query.filter(SpecialPrice.buyer_code == buyer_code)
    return query.order_by(SpecialPrice.id.desc()).all()

@router.post("/special-prices", response_model=SpecialPriceOut)
def create_special_price(body: SpecialPriceCreate, db: Session = Depends(get_db)):
    row = SpecialPrice(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@router.put("/special-prices/{price_id}", response_model=SpecialPriceOut)
def update_special_price(price_id: int, body: SpecialPriceUpdate, db: Session = Depends(get_db)):
    row = db.query(SpecialPrice).get(price_id)
    if not row:
        raise HTTPException(404, "Special price not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row

@router.delete("/special-prices/{price_id}")
def delete_special_price(price_id: int, db: Session = Depends(get_db)):
    row = db.query(SpecialPrice).get(price_id)
    if not row:
        raise HTTPException(404, "Special price not found")
    row.is_active = False
    db.commit()
    return {"status": "deleted"}
```

- [ ] **Step 5: Register router in main.py**

Add to imports and router registration:

```python
from app.routers.pricing import router as pricing_router
app.include_router(pricing_router)
```

- [ ] **Step 6: Create SpecialPricesPage.vue**

Create `frontend/src/views/admin/SpecialPricesPage.vue`:

```vue
<template>
  <AdminSection :title="t('pages.specialPrices.title')" :subtitle="t('pages.specialPrices.subtitle')">
    <template #actions>
      <el-input v-model="keyword" :placeholder="t('pages.specialPrices.searchPlaceholder')" clearable />
      <el-button type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table :data="filteredRows" v-loading="loading" border stripe size="small">
      <el-table-column type="index" :label="t('common.noLabel')" width="56" />
      <el-table-column prop="buyer_code" :label="t('pages.specialPrices.buyerCode')" width="120" />
      <el-table-column prop="material_pattern" :label="t('pages.specialPrices.materialPattern')" min-width="160" />
      <el-table-column prop="emboss_pattern" :label="t('pages.specialPrices.embossPattern')" width="140" />
      <el-table-column prop="discount_type" :label="t('pages.specialPrices.discountType')" width="120">
        <template #default="{ row }">
          <el-tag :type="row.discount_type === 'percentage' ? 'primary' : 'success'">
            {{ t(`pages.specialPrices.${row.discount_type}`) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="discount_value" :label="t('pages.specialPrices.discountValue')" width="120">
        <template #default="{ row }">
          {{ row.discount_value }}{{ row.discount_type === 'percentage' ? '%' : '' }}
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="100" align="center">
        <template #default="{ row }">
          <el-button :icon="EditPen" link type="primary" @click="openEdit(row)" />
          <el-button :icon="Delete" link type="danger" @click="confirmDelete(row)" />
        </template>
      </el-table-column>
    </el-table>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="formVisible" :title="isEdit ? t('common.edit') : t('common.create')" width="600px" destroy-on-close>
      <el-form :model="form" label-position="top">
        <el-row :gutter="16">
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.specialPrices.buyerCode')" required>
              <el-input v-model="form.buyer_code" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.specialPrices.discountType')">
              <el-select v-model="form.discount_type" class="w-full">
                <el-option :label="t('pages.specialPrices.percentage')" value="percentage" />
                <el-option :label="t('pages.specialPrices.nominal')" value="nominal" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.specialPrices.discountValue')" required>
              <el-input-number v-model="form.discount_value" :min="0" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="t('pages.specialPrices.materialPattern')">
              <el-input v-model="form.material_pattern" placeholder="*PU* atau exact match" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.specialPrices.embossPattern')">
              <el-input v-model="form.emboss_pattern" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.specialPrices.colorPattern')">
              <el-input v-model="form.color_pattern" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="submitForm">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, EditPen, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import { listSpecialPrices, createSpecialPrice, updateSpecialPrice, deleteSpecialPrice } from '../../api/client'

const { t } = useI18n()

const loading = ref(false)
const rows = ref([])
const keyword = ref('')
const formVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)

const form = reactive({
  buyer_code: '',
  material_pattern: '',
  emboss_pattern: '',
  color_pattern: '',
  discount_type: 'percentage',
  discount_value: 0,
})

const filteredRows = computed(() => {
  if (!keyword.value) return rows.value
  const q = keyword.value.toLowerCase()
  return rows.value.filter(r => 
    r.buyer_code?.toLowerCase().includes(q) ||
    r.material_pattern?.toLowerCase().includes(q)
  )
})

async function load() {
  loading.value = true
  try {
    rows.value = await listSpecialPrices()
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(form, {
    buyer_code: '',
    material_pattern: '',
    emboss_pattern: '',
    color_pattern: '',
    discount_type: 'percentage',
    discount_value: 0,
  })
}

function openCreate() {
  isEdit.value = false
  editingId.value = null
  resetForm()
  formVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  editingId.value = row.id
  Object.assign(form, { ...row })
  formVisible.value = true
}

async function submitForm() {
  try {
    if (isEdit.value) {
      await updateSpecialPrice(editingId.value, form)
    } else {
      await createSpecialPrice(form)
    }
    ElMessage.success(t('common.save'))
    formVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(t('pages.specialPrices.deleteConfirm'), t('common.confirm'), { type: 'warning' })
    await deleteSpecialPrice(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

onMounted(load)
</script>
```

- [ ] **Step 7: Add API functions to client.js**

```javascript
export async function listSpecialPrices(params = {}) {
  const { data } = await api.get('/pricing/special-prices', { params })
  return data
}

export async function createSpecialPrice(body) {
  const { data } = await api.post('/pricing/special-prices', body)
  return data
}

export async function updateSpecialPrice(id, body) {
  const { data } = await api.put(`/pricing/special-prices/${id}`, body)
  return data
}

export async function deleteSpecialPrice(id) {
  await api.delete(`/pricing/special-prices/${id}`)
}
```

- [ ] **Step 8: Add translations**

```json
"pages": {
  "specialPrices": {
    "title": "Harga Khusus",
    "subtitle": "Kelola diskon dan harga khusus per buyer",
    "searchPlaceholder": "Cari buyer atau material",
    "buyerCode": "Buyer",
    "materialPattern": "Pattern Material",
    "embossPattern": "Pattern Emboss",
    "colorPattern": "Pattern Warna",
    "discountType": "Tipe Diskon",
    "discountValue": "Nilai",
    "percentage": "Persentase",
    "nominal": "Nominal",
    "deleteConfirm": "Hapus harga khusus ini?"
  }
}
```

---

## Task 3.2: Customer-Based Pricing

### Data Model

```python
class CustomerSpecialPrice(Base):
    __tablename__ = "customer_special_prices"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("customers.id"))
    buyer_code: Mapped[str] = mapped_column(String(32))
    material_pattern: Mapped[Optional[str]] = mapped_column(String(255))
    price_override: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    discount_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_to: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
```

### Implementation Steps

- [ ] **Step 1: Add CustomerSpecialPrice model**

Add to `models.py`:

```python
class CustomerSpecialPrice(Base):
    """Harga khusus per customer."""
    
    __tablename__ = "customer_special_prices"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("customers.id"))
    buyer_code: Mapped[str] = mapped_column(String(32))
    material_pattern: Mapped[Optional[str]] = mapped_column(String(255))
    price_override: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 4))
    discount_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    valid_from: Mapped[Optional[date]] = mapped_column(Date)
    valid_to: Mapped[Optional[date]] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)
    
    customer: Mapped[Optional["Customer"]] = relationship("Customer")
```

- [ ] **Step 2: Add schemas**

```python
class CustomerSpecialPriceCreate(BaseModel):
    customer_id: int
    buyer_code: str
    material_pattern: Optional[str] = None
    price_override: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None

class CustomerSpecialPriceUpdate(BaseModel):
    customer_id: Optional[int] = None
    buyer_code: Optional[str] = None
    material_pattern: Optional[str] = None
    price_override: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: Optional[bool] = None

class CustomerSpecialPriceOut(ORMBase):
    id: int
    customer_id: int
    buyer_code: str
    material_pattern: Optional[str] = None
    price_override: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    is_active: bool
```

- [ ] **Step 3: Create migration**

```bash
cd /Users/wiranto/Projects/Tonghong/backend && alembic revision --autogenerate -m "add_customer_special_prices"
```

- [ ] **Step 4: Add endpoints to pricing router**

```python
@router.get("/customer-prices", response_model=list[CustomerSpecialPriceOut])
def list_customer_prices(
    customer_id: int = None,
    db: Session = Depends(get_db)
):
    query = db.query(CustomerSpecialPrice).filter(CustomerSpecialPrice.is_active == True)
    if customer_id:
        query = query.filter(CustomerSpecialPrice.customer_id == customer_id)
    return query.order_by(CustomerSpecialPrice.id.desc()).all()

@router.post("/customer-prices", response_model=CustomerSpecialPriceOut)
def create_customer_price(body: CustomerSpecialPriceCreate, db: Session = Depends(get_db)):
    row = CustomerSpecialPrice(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@router.delete("/customer-prices/{price_id}")
def delete_customer_price(price_id: int, db: Session = Depends(get_db)):
    row = db.query(CustomerSpecialPrice).get(price_id)
    if not row:
        raise HTTPException(404, "Customer price not found")
    row.is_active = False
    db.commit()
    return {"status": "deleted"}
```

- [ ] **Step 5: Add API functions**

```javascript
export async function listCustomerPrices(params = {}) {
  const { data } = await api.get('/pricing/customer-prices', { params })
  return data
}

export async function createCustomerPrice(body) {
  const { data } = await api.post('/pricing/customer-prices', body)
  return data
}

export async function deleteCustomerPrice(id) {
  await api.delete(`/pricing/customer-prices/${id}`)
}
```

---

## Task 3.3: Bulk Price Update

### Implementation Steps

- [ ] **Step 1: Add bulk update endpoint**

Add to `pricing.py` router:

```python
from fastapi import UploadFile, File
import csv
import io

class PriceUpdateItem(BaseModel):
    buyer_code: str
    material_pattern: str
    new_price: Decimal

class BulkPriceUpdate(BaseModel):
    updates: list[PriceUpdateItem]

@router.post("/bulk-update", response_model=dict)
def bulk_update_prices(body: BulkPriceUpdate, db: Session = Depends(get_db)):
    """Update multiple prices at once."""
    updated = 0
    for item in body.updates:
        # Find matching buyer price list
        buyer_list = db.query(BuyerPriceList).filter(
            BuyerPriceList.buyer_code == item.buyer_code
        ).first()
        
        if buyer_list and buyer_list.rows:
            for row in buyer_list.rows:
                cells = row.cells or {}
                material = cells.get('ITEM', '') or cells.get('MATERIAL', '')
                if item.material_pattern.lower() in material.lower():
                    # Update price column
                    for price_col in ['PRICE', 'UOM', 'PRICE USD']:
                        if price_col in cells:
                            cells[price_col] = str(item.new_price)
                    row.cells = cells
                    updated += 1
    
    db.commit()
    return {"updated": updated}

@router.post("/bulk-update-csv")
async def bulk_update_prices_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Bulk update from CSV file."""
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    updated = 0
    for row in reader:
        buyer_code = row.get('buyer_code', '').strip()
        material_pattern = row.get('material_pattern', '').strip()
        new_price = row.get('new_price', '').strip()
        
        if not buyer_code or not material_pattern or not new_price:
            continue
        
        try:
            new_price_dec = Decimal(new_price)
        except:
            continue
        
        # Update logic (same as above)
        buyer_list = db.query(BuyerPriceList).filter(
            BuyerPriceList.buyer_code == buyer_code
        ).first()
        
        if buyer_list and buyer_list.rows:
            for bprow in buyer_list.rows:
                cells = bprow.cells or {}
                material = cells.get('ITEM', '') or cells.get('MATERIAL', '')
                if material_pattern.lower() in material.lower():
                    for price_col in ['PRICE', 'UOM', 'PRICE USD']:
                        if price_col in cells:
                            cells[price_col] = str(new_price_dec)
                    bprow.cells = cells
                    updated += 1
    
    db.commit()
    return {"updated": updated}
```

- [ ] **Step 2: Create BulkPriceUpdatePage.vue**

Create `frontend/src/views/admin/BulkPriceUpdatePage.vue`:

```vue
<template>
  <AdminSection :title="t('pages.bulkPriceUpdate.title')" :subtitle="t('pages.bulkPriceUpdate.subtitle')">
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="t('pages.bulkPriceUpdate.singleUpdate')" name="single">
        <el-form :model="singleForm" label-position="top" class="max-w-lg">
          <el-form-item :label="t('pages.bulkPriceUpdate.buyerCode')">
            <el-input v-model="singleForm.buyer_code" />
          </el-form-item>
          <el-form-item :label="t('pages.bulkPriceUpdate.materialPattern')">
            <el-input v-model="singleForm.material_pattern" />
          </el-form-item>
          <el-form-item :label="t('pages.bulkPriceUpdate.newPrice')">
            <el-input-number v-model="singleForm.new_price" :min="0" :precision="4" class="w-full" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="saving" @click="submitSingle">
              {{ t('pages.bulkPriceUpdate.update') }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.bulkPriceUpdate.csvUpload')" name="csv">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :limit="1"
          accept=".csv"
          :on-change="handleFileChange"
        >
          <el-button type="primary">{{ t('pages.bulkPriceUpdate.selectFile') }}</el-button>
        </el-upload>
        <div class="mt-4">
          <el-button type="success" :disabled="!csvFile" :loading="uploading" @click="submitCsv">
            {{ t('pages.bulkPriceUpdate.uploadAndUpdate') }}
          </el-button>
        </div>
        <div class="mt-4 text-xs text-slate-500">
          <p>{{ t('pages.bulkPriceUpdate.csvFormat') }}:</p>
          <code>buyer_code,material_pattern,new_price</code>
        </div>
      </el-tab-pane>
    </el-tabs>
  </AdminSection>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import { bulkUpdatePrices, bulkUpdatePricesCsv } from '../../api/client'

const { t } = useI18n()

const activeTab = ref('single')
const saving = ref(false)
const uploading = ref(false)
const csvFile = ref(null)
const uploadRef = ref(null)

const singleForm = reactive({
  buyer_code: '',
  material_pattern: '',
  new_price: 0,
})

async function submitSingle() {
  if (!singleForm.buyer_code || !singleForm.material_pattern) {
    ElMessage.warning(t('pages.bulkPriceUpdate.fillAllFields'))
    return
  }
  saving.value = true
  try {
    const result = await bulkUpdatePrices({
      updates: [{ ...singleForm }]
    })
    ElMessage.success(t('pages.bulkPriceUpdate.updatedCount', { count: result.updated }))
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    saving.value = false
  }
}

function handleFileChange(file) {
  csvFile.value = file.raw
}

async function submitCsv() {
  if (!csvFile.value) return
  uploading.value = true
  try {
    const result = await bulkUpdatePricesCsv(csvFile.value)
    ElMessage.success(t('pages.bulkPriceUpdate.updatedCount', { count: result.updated }))
    csvFile.value = null
    uploadRef.value?.clearFiles()
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    uploading.value = false
  }
}
</script>
```

- [ ] **Step 3: Add API functions**

```javascript
export async function bulkUpdatePrices(updates) {
  const { data } = await api.post('/pricing/bulk-update', { updates })
  return data
}

export async function bulkUpdatePricesCsv(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/pricing/bulk-update-csv', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return data
}
```

- [ ] **Step 4: Add translations**

```json
"pages": {
  "bulkPriceUpdate": {
    "title": "Update Harga Massal",
    "subtitle": "Update harga banyak item sekaligus",
    "singleUpdate": "Update Tunggal",
    "csvUpload": "Upload CSV",
    "buyerCode": "Buyer",
    "materialPattern": "Pattern Material",
    "newPrice": "Harga Baru",
    "update": "Update",
    "selectFile": "Pilih File CSV",
    "uploadAndUpdate": "Upload & Update",
    "csvFormat": "Format CSV:",
    "fillAllFields": "Lengkapi semua field",
    "updatedCount": "{count} item berhasil diupdate"
  }
}
```

---

## Summary

| Task | Description | Effort |
|------|-------------|--------|
| 3.1 | Special Prices / Discounts | High |
| 3.2 | Customer-Based Pricing | Medium |
| 3.3 | Bulk Price Update | Medium |

**Total: 3 tasks**

---

## Pricing Logic Flow

```
Input: buyer_code, material, emboss, color, customer_id
         │
         ▼
┌─────────────────────────────────────┐
│ 1. Get base price from Buyer Price  │
│    List                             │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 2. Check Special Prices             │
│    - Match buyer_code + patterns    │
│    - Check date validity            │
│    - Apply discount if found        │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ 3. Check Customer Special Prices    │
│    - Match customer_id + patterns   │
│    - Apply override/discount        │
└─────────────────────────────────────┘
         │
         ▼
    Final Price
```

---

## Plan complete and saved to `docs/superpowers/plans/2026-04-15-phase3-pricing-engine-plan.md`.

**Two execution options:**

**1. Subagent-Driven (recommended)** - Dispatch subagent per task for fast iteration

**2. Inline Execution** - Execute tasks sequentially in this session

**Which approach?**
