# Master Items - Excel Export/Import Implementation Plan

**Goal:** Add Excel export and import functionality for Master Items in the Tonghong project.

**Architecture:** Create utility module for Excel operations and add two endpoints to masters.py router. Frontend uses existing `fetchAuthenticatedDocument` for export (following existing pattern) and FormData POST for import.

**Tech Stack:** Python (FastAPI + openpyxl), Vue 3 + Element Plus

---

### Task 1: Install openpyxl

**Files:**
- Modify: `backend/requirements.txt`

- [ ] **Step 1: Check if openpyxl in requirements**

Run: `grep -i openpyxl /Users/wiranto/Projects/Tonghong/backend/requirements.txt 2>/dev/null || echo "NOT FOUND"`

If NOT FOUND, add it:
```bash
echo "openpyxl>=3.1.0" >> /Users/wiranto/Projects/Tonghong/backend/requirements.txt
```

- [ ] **Step 2: Install openpyxl**

Run: `pip install openpyxl`

---

### Task 2: Create Excel utility module

**Files:**
- Create: `backend/app/utils/__init__.py`
- Create: `backend/app/utils/excel_utils.py`

- [ ] **Step 1: Create utils directory and __init__.py**

Run: `mkdir -p /Users/wiranto/Projects/Tonghong/backend/app/utils && touch /Users/wiranto/Projects/Tonghong/backend/app/utils/__init__.py`

- [ ] **Step 2: Create excel_utils.py**

```python
import io
from openpyxl import Workbook, load_workbook


def export_to_excel(data: list[dict], columns: list[str], sheet_name: str = "Sheet1") -> bytes:
    """Export data to Excel format."""
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name

    headers = [col.replace("_", " ").title() for col in columns]
    for col, header in enumerate(headers, 1):
        ws.cell(row=1, column=col, value=header)

    for row_idx, item in enumerate(data, 2):
        for col_idx, col in enumerate(columns, 1):
            val = item.get(col, "")
            if hasattr(val, "isoformat"):
                val = val.isoformat()
            ws.cell(row=row_idx, column=col_idx, value=val if val is not None else "")

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def import_from_excel(file_content: bytes, columns: list[str]) -> list[dict]:
    """Import data from Excel format."""
    wb = load_workbook(io.BytesIO(file_content))
    ws = wb.active

    items = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0]:
            continue
        item = {}
        for i, col in enumerate(columns):
            val = row[i]
            if isinstance(val, (int, float)):
                item[col] = str(val) if val is not None else ""
            else:
                item[col] = str(val) if val is not None else ""
        items.append(item)

    return items
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/utils/
git commit -m "feat(masters): add excel export/import utilities"
```

---

### Task 3: Add export endpoint

**Files:**
- Modify: `backend/app/routers/masters.py:237-294`

- [ ] **Step 1: Add import at top of file**

After existing imports (line ~6):
```python
from fastapi.responses import StreamingResponse
```

- [ ] **Step 2: Add EXCEL_COLUMNS constant and export endpoint**

After line 294 (after delete_master_item function):

```python
EXCEL_COLUMNS = [
    "item_code", "thickness_mm", "thickness_range", "material_name",
    "emboss", "color", "softness", "color_reference", "backing",
    "quantity_order_default", "style_article", "model", "category", "exim_material_code"
]


@router.get("/masters/items/export")
async def export_master_items(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    from app.utils.excel_utils import export_to_excel

    items = db.scalars(select(MasterItem).order_by(MasterItem.item_code)).all()
    data = [
        {col: getattr(item, col, None) for col in EXCEL_COLUMNS}
        for item in items
    ]
    excel_content = export_to_excel(data, EXCEL_COLUMNS, "Master Items")
    return StreamingResponse(
        io.BytesIO(excel_content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=master_items.xlsx"}
    )
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/routers/masters.py
git commit -m "feat(masters): add /masters/items/export endpoint"
```

---

### Task 4: Add import endpoint

**Files:**
- Modify: `backend/app/routers/masters.py`

- [ ] **Step 1: Add import endpoint after export**

After the export endpoint (after line ~310):

```python
@router.post("/masters/items/import")
async def import_master_items(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user=Depends(require_roles("admin")),
):
    from decimal import Decimal
    from app.utils.excel_utils import import_from_excel

    content = await file.read()
    items = import_from_excel(content, EXCEL_COLUMNS)

    imported = 0
    errors = []

    for idx, item_data in enumerate(items):
        try:
            item_code = item_data.get("item_code", "").strip()
            if not item_code:
                errors.append(f"Row {idx + 2}: item_code is required")
                continue

            existing = db.scalars(
                select(MasterItem).where(MasterItem.item_code == item_code)
            ).first()

            if existing:
                for col in EXCEL_COLUMNS:
                    if col == "item_code":
                        continue
                    val = item_data.get(col)
                    if val and hasattr(existing, col):
                        if col == "thickness_mm" or col == "quantity_order_default":
                            try:
                                setattr(existing, col, Decimal(str(val)) if val else None)
                            except Exception:
                                setattr(existing, col, val)
                        else:
                            setattr(existing, col, val)
            else:
                new_item = MasterItem(item_code=item_code)
                for col in EXCEL_COLUMNS:
                    if col == "item_code":
                        continue
                    val = item_data.get(col)
                    if val and hasattr(new_item, col):
                        if col == "thickness_mm" or col == "quantity_order_default":
                            try:
                                setattr(new_item, col, Decimal(str(val)) if val else None)
                            except Exception:
                                setattr(new_item, col, val)
                        else:
                            setattr(new_item, col, val)
                db.add(new_item)

            imported += 1
        except Exception as e:
            errors.append(f"Row {idx + 2}: {str(e)}")

    db.commit()
    return {"imported": imported, "errors": errors if errors else None}
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/routers/masters.py
git commit -m "feat(masters): add /masters/items/import endpoint"
```

---

### Task 5: Add frontend API functions

**Files:**
- Modify: `frontend/src/api/client.js:351-366`

- [ ] **Step 1: Add export API function**

After `deleteMasterItem` function (line 366):

```javascript
export function masterItemsExportPath() {
  return '/masters/items/export'
}

export async function importMasterItems(file) {
  const fd = new FormData()
  fd.append('file', file)
  return apiFetch('/masters/items/import', { method: 'POST', body: fd })
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/api/client.js
git commit -m "feat(api): add masterItemsExportPath and importMasterItems"
```

---

### Task 6: Update MasterItemsPage.vue

**Files:**
- Modify: `frontend/src/views/admin/MasterItemsPage.vue`

- [ ] **Step 1: Add imports to script section**

Change line 123 from:
```javascript
import { createMasterItem, deleteMasterItem, listMasterItems, updateMasterItem } from '../../api/client'
```
To:
```javascript
import { createMasterItem, deleteMasterItem, listMasterItems, updateMasterItem, masterItemsExportPath, importMasterItems } from '../../api/client'
```

- [ ] **Step 2: Add buttons to template toolbar**

After line 5 (`<el-button type="primary" :icon="Plus" @click="openCreate">`):
```vue
<el-button @click="handleExport">{{ t('pages.masterItems.export') }}</el-button>
<el-button type="success" @click="openImportDialog">{{ t('pages.masterItems.import') }}</el-button>
```

- [ ] **Step 3: Add reactive data and functions**

After `const filteredRows = computed(...)` (line 260-264), add:
```javascript
const importDialogVisible = ref(false)
const importFile = ref(null)

function openImportDialog() {
  importDialogVisible.value = true
  importFile.value = null
}

function handleFileChange(file) {
  importFile.value = file.raw
}

async function handleExport() {
  try {
    const url = masterItemsExportPath()
    await fetchAuthenticatedDocument(url, { mode: 'download', downloadFallbackName: 'master_items.xlsx' })
    ElMessage.success(t('pages.masterItems.exportSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
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

- [ ] **Step 4: Add import dialog**

Before closing `</AdminSection>` tag (before line 114):
```vue
<el-dialog v-model="importDialogVisible" :title="t('pages.masterItems.importTitle')" width="400px" destroy-on-close>
  <el-upload
    ref="uploadRef"
    :auto-upload="false"
    :limit="1"
    accept=".xlsx,.xls"
    :on-change="handleFileChange"
  >
    <el-button type="primary">{{ t('pages.masterItems.selectFile') }}</el-button>
    <template #tip>
      <div class="el-upload__tip">File Excel (.xlsx, .xls)</div>
    </template>
  </el-upload>
  <template #footer>
    <el-button @click="importDialogVisible = false">{{ t('common.cancel') }}</el-button>
    <el-button type="primary" :disabled="!importFile" @click="handleImport">
      {{ t('pages.masterItems.doImport') }}
    </el-button>
  </template>
</el-dialog>
```

- [ ] **Step 5: Add ref for upload**

After line 123, add:
```javascript
const uploadRef = ref(null)
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/views/admin/MasterItemsPage.vue
git commit -m "feat(masterItems): add export/import buttons and dialog"
```

---

### Task 7: Add translations

**Files:**
- Find and modify the i18n locale files

- [ ] **Step 1: Find locale files**

Run: `find /Users/wiranto/Projects/Tonghong/frontend/src -name "*.json" | xargs grep -l "masterItems" 2>/dev/null`

- [ ] **Step 2: Add translations to each locale file**

Add to `pages.masterItems`:
```json
"export": "Export Excel",
"import": "Import Excel",
"importTitle": "Import Master Items",
"selectFile": "Select File",
"doImport": "Import",
"exportSuccess": "Export berhasil",
"importSuccess": "{count} item berhasil diimport"
```

- [ ] **Step 3: Commit**

---

## Verification

1. Start backend: `cd /Users/wiranto/Projects/Tonghong/backend && uvicorn app.main:app --reload`
2. Start frontend: `cd /Users/wiranto/Projects/Tonghong/frontend && npm run dev`
3. Login and navigate to Master Items
4. Click "Export Excel" - should download master_items.xlsx
5. Click "Import Excel" - should open dialog
6. Select a valid Excel file and click Import - items should appear in list

---

**Plan complete.** Two execution options:

1. **Subagent-Driven (recommended)** - Dispatch a fresh subagent per task, review between tasks
2. **Inline Execution** - Execute tasks in this session using executing-plans skill

**Which approach?**
