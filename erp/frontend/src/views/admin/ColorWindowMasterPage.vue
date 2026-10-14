<template>
  <AdminSection :title="t('pages.colorWindow.title')" :subtitle="t('pages.colorWindow.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        clearable
        :placeholder="t('pages.colorWindow.searchPlaceholder')"
        class="cw-toolbar-search"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canView" :icon="Download" @click="handleExport">{{ t('pages.colorWindow.export') }}</el-button>
      <el-button v-if="canCreate" type="success" :icon="Upload" @click="openImportDialog">{{ t('pages.colorWindow.import') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.colorWindow.listSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.colorWindow.listSubtitle') }}</p>
        </div>
      </div>

      <div class="filter-panel cw-filter-panel">
        <p class="filter-panel__title">{{ t('common.filter') }}</p>
        <el-select
          v-model="filterBrand"
          clearable
          filterable
          class="cw-filter-brand"
          :placeholder="t('pages.colorWindow.brandFilter')"
        >
          <el-option v-for="b in formOptions.brand_codes" :key="b" :label="b" :value="b" />
        </el-select>
      </div>

      <p class="admin-scroll-hint">{{ t('pages.colorWindow.scrollHint') }}</p>

      <div class="admin-table-scroll">
        <el-table
          :data="rows"
          v-loading="loading"
          border
          stripe
          size="small"
          class="admin-table"
          table-layout="fixed"
          max-height="52vh"
          :empty-text="t('pages.colorWindow.tableEmpty')"
          @sort-change="onSortChange"
        >
          <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
          <el-table-column prop="color_code" :label="t('pages.colorWindow.colCode')" width="140" show-overflow-tooltip sortable="custom" />
          <el-table-column prop="color_name" :label="t('common.color')" min-width="200" show-overflow-tooltip sortable="custom" />
          <el-table-column prop="brand_code" :label="t('pages.colorWindow.brandFilter')" width="110" align="center" sortable="custom">
            <template #default="{ row }">
              <el-tag size="small" effect="plain" type="info">{{ row.brand_code || '—' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="remark" :label="t('common.remark')" min-width="160" show-overflow-tooltip />
          <el-table-column prop="created_at" :label="t('pages.colorWindow.colCreatedAt')" width="148" align="center" sortable="custom">
            <template #default="{ row }">{{ formatAuditDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column prop="updated_at" :label="t('pages.colorWindow.colUpdatedAt')" width="148" align="center" sortable="custom">
            <template #default="{ row }">{{ formatAuditDateTime(row.updated_at) }}</template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="88" fixed="right" align="center">
            <template #default="{ row }">
              <AdminTableActions
                :show-edit="canUpdate"
                :show-delete="canDelete"
                @edit="openEdit(row)"
                @delete="remove(row)"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="cw-pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          size="small"
          background
          layout="total, sizes, prev, pager, next"
          :total="total"
          :page-sizes="[20, 50, 100, 200]"
        />
      </div>
    </div>

    <el-dialog v-model="importDialogVisible" :title="t('pages.colorWindow.importTitle')" width="640px" destroy-on-close align-center>
      <p class="cw-import-sub">{{ t('pages.colorWindow.importSub') }}</p>
      <p class="cw-import-hint">{{ t('pages.colorWindow.importHint') }}</p>
      <ul class="cw-import-cols">
        <li>{{ t('pages.colorWindow.importColsRequired') }}</li>
        <li>{{ t('pages.colorWindow.importColsOptional') }}</li>
      </ul>
      <div class="cw-import-actions">
        <el-button :icon="Download" @click="downloadImportTemplate">{{ t('pages.colorWindow.downloadTemplate') }}</el-button>
      </div>
      <p class="cw-import-panel-title">{{ t('pages.colorWindow.importPanelTitle') }}</p>
      <el-upload
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleImportFile"
      >
        <el-button type="primary">{{ t('pages.colorWindow.selectFile') }}</el-button>
      </el-upload>
      <div v-if="importResult" class="cw-import-result">
        <p>
          {{
            t('pages.colorWindow.importResultSummary', {
              created: importResult.created || 0,
              updated: importResult.updated || 0,
              skipped: importResult.skipped || 0,
            })
          }}
        </p>
        <ul v-if="importResult.errors?.length" class="cw-import-errors">
          <li v-for="(err, idx) in importResult.errors.slice(0, 8)" :key="idx">
            {{ t('pages.colorWindow.importErrorRow', { row: err.row, code: err.color_code || '—', reason: err.reason }) }}
          </li>
          <li v-if="importResult.errors.length > 8">
            {{ t('pages.colorWindow.importErrorMore', { n: importResult.errors.length - 8 }) }}
          </li>
        </ul>
      </div>
      <template #footer>
        <el-button @click="importDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :disabled="!importFile || importing" :loading="importing" @click="handleImport">
          {{ t('pages.colorWindow.doImport') }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="formVisible" width="560px" destroy-on-close align-center @closed="resetForm">
      <template #header>
        <div>
          <h3 class="cw-dialog-title">
            {{ editId ? t('pages.colorWindow.editTitle') : t('pages.colorWindow.createTitle') }}
          </h3>
          <p class="cw-dialog-sub">{{ t('pages.colorWindow.dialogFormSub') }}</p>
        </div>
      </template>
      <el-form label-position="top" @submit.prevent>
        <el-form-item :label="t('pages.colorWindow.colCode')" required>
          <el-input v-model="form.color_code" maxlength="64" :placeholder="t('pages.colorWindow.formCodePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('common.color')" required>
          <el-input v-model="form.color_name" maxlength="255" :placeholder="t('pages.colorWindow.formColorPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('pages.colorWindow.brandFilter')" required>
          <el-select v-model="form.brand_code" filterable class="w-full" :placeholder="t('pages.colorWindow.formBrandPlaceholder')">
            <el-option v-for="b in formOptions.brand_codes" :key="b" :label="b" :value="b" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.remark')">
          <el-input v-model="form.remark" type="textarea" :rows="3" maxlength="4000" />
        </el-form-item>
        <el-form-item :label="t('pages.colorWindow.colCreatedAt')">
          <div class="cw-date-row">
            <el-date-picker
              v-model="form.created_at"
              type="datetime"
              value-format="YYYY-MM-DD HH:mm:ss"
              format="YYYY-MM-DD HH:mm:ss"
              class="cw-date-input"
              :disabled="!createdAtEditable"
              :clearable="createdAtEditable"
            />
            <el-button
              :icon="EditPen"
              circle
              :type="createdAtEditable ? 'primary' : 'default'"
              :aria-label="t('pages.colorWindow.editDate')"
              @click="createdAtEditable = !createdAtEditable"
            />
          </div>
        </el-form-item>
        <el-form-item :label="t('pages.colorWindow.colUpdatedAt')">
          <div class="cw-date-row">
            <el-date-picker
              v-model="form.updated_at"
              type="datetime"
              value-format="YYYY-MM-DD HH:mm:ss"
              format="YYYY-MM-DD HH:mm:ss"
              class="cw-date-input"
              :disabled="!updatedAtEditable"
              :clearable="updatedAtEditable"
            />
            <el-button
              :icon="EditPen"
              circle
              :type="updatedAtEditable ? 'primary' : 'default'"
              :aria-label="t('pages.colorWindow.editDate')"
              @click="updatedAtEditable = !updatedAtEditable"
            />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="save">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, EditPen, Plus, Refresh, Upload } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import {
  createColorWindow,
  deleteColorWindow,
  exportColorWindows,
  importColorWindows,
  listColorWindowFormOptions,
  listColorWindowsPage,
  updateColorWindow,
} from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canView, canCreate, canUpdate, canDelete } = useModulePermission('colorWindow')

const loading = ref(false)
const saving = ref(false)
const importing = ref(false)
const importDialogVisible = ref(false)
const importFile = ref(null)
const importResult = ref(null)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)
const keyword = ref('')
const filterBrand = ref('')
const sortBy = ref('')
const sortDir = ref('asc')
const formVisible = ref(false)
const editId = ref(null)
const createdAtEditable = ref(false)
const updatedAtEditable = ref(false)

const formOptions = ref({ brand_codes: [] })

const form = ref({
  color_code: '',
  color_name: '',
  brand_code: '',
  remark: '',
  created_at: '',
  updated_at: '',
})

async function loadFormOptions() {
  try {
    formOptions.value = await listColorWindowFormOptions()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function load() {
  loading.value = true
  try {
    const r = await listColorWindowsPage({
      brand_code: filterBrand.value || undefined,
      q: keyword.value || undefined,
      sort_by: sortBy.value || undefined,
      sort_dir: sortBy.value ? sortDir.value : undefined,
      limit: pageSize.value,
      offset: (page.value - 1) * pageSize.value,
    })
    rows.value = r.items || []
    total.value = Number(r.total || 0)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function formatAuditDateTime(value) {
  if (!value) return '—'
  const s = String(value).replace('T', ' ')
  return s.length > 19 ? s.slice(0, 19) : s
}

function onSortChange({ prop, order }) {
  if (!order || !prop) {
    sortBy.value = ''
    sortDir.value = 'asc'
  } else {
    sortBy.value = prop
    sortDir.value = order === 'descending' ? 'desc' : 'asc'
  }
  if (page.value !== 1) page.value = 1
  else load()
}

function reload() {
  page.value = 1
  load()
}

function stampNow() {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
}

function toPickerValue(value) {
  if (!value) return ''
  const s = String(value).replace('T', ' ')
  return s.length > 19 ? s.slice(0, 19) : s
}

function resetForm() {
  editId.value = null
  createdAtEditable.value = false
  updatedAtEditable.value = false
  form.value = { color_code: '', color_name: '', brand_code: '', remark: '', created_at: '', updated_at: '' }
}

function openCreate() {
  resetForm()
  const now = stampNow()
  form.value.created_at = now
  form.value.updated_at = now
  formVisible.value = true
}

function openEdit(row) {
  editId.value = row.id
  createdAtEditable.value = false
  updatedAtEditable.value = false
  form.value = {
    color_code: row.color_code || '',
    color_name: row.color_name || '',
    brand_code: row.brand_code || '',
    remark: row.remark || '',
    created_at: toPickerValue(row.created_at),
    updated_at: toPickerValue(row.updated_at) || stampNow(),
  }
  formVisible.value = true
}

async function save() {
  const body = {
    color_code: form.value.color_code.trim(),
    color_name: form.value.color_name.trim(),
    brand_code: form.value.brand_code.trim(),
    remark: form.value.remark?.trim() || null,
    created_at: form.value.created_at || null,
    updated_at: form.value.updated_at || null,
  }
  if (!body.color_code || !body.color_name || !body.brand_code) {
    ElMessage.warning(t('pages.colorWindow.requiredFields'))
    return
  }
  saving.value = true
  try {
    if (editId.value) await updateColorWindow(editId.value, body)
    else await createColorWindow(body)
    ElMessage.success(t('common.saveSuccess'))
    formVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(t('pages.colorWindow.deleteConfirm'), t('common.confirm'), { type: 'warning' })
    await deleteColorWindow(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function openImportDialog() {
  importDialogVisible.value = true
  importFile.value = null
  importResult.value = null
}

function handleImportFile(file) {
  importFile.value = file.raw
  importResult.value = null
}

async function handleExport() {
  try {
    await exportColorWindows()
    ElMessage.success(t('pages.colorWindow.exportSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadImportTemplate() {
  try {
    await exportColorWindows({ template: true })
    ElMessage.success(t('pages.colorWindow.templateSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function handleImport() {
  if (!importFile.value) return
  importing.value = true
  importResult.value = null
  try {
    const result = await importColorWindows(importFile.value)
    importResult.value = result
    ElMessage.success(
      t('pages.colorWindow.importResultSummary', {
        created: result.created || 0,
        updated: result.updated || 0,
        skipped: result.skipped || 0,
      }),
    )
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    importing.value = false
  }
}

watch([page, pageSize], () => load())
watch(keyword, () => {
  if (page.value !== 1) page.value = 1
  else load()
})
watch(filterBrand, () => {
  if (page.value !== 1) page.value = 1
  else load()
})

onMounted(() => {
  loadFormOptions()
  load()
})
</script>

<style scoped>
.cw-toolbar-search {
  width: min(280px, 42vw);
}
.cw-filter-brand {
  min-width: 160px;
}
.cw-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
.cw-dialog-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
}
.cw-dialog-sub {
  margin: 4px 0 0;
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
}
.cw-date-row {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}
.cw-date-input {
  flex: 1;
}
.cw-import-sub {
  margin: 0 0 6px;
  font-size: 14px;
}
.cw-import-hint,
.cw-import-cols {
  margin: 0 0 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.45;
}
.cw-import-cols {
  padding-left: 18px;
}
.cw-import-actions {
  margin-bottom: 12px;
}
.cw-import-panel-title {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 600;
}
.cw-import-result {
  margin-top: 14px;
  padding: 10px 12px;
  border-radius: 6px;
  background: var(--el-fill-color-light);
  font-size: 13px;
}
.cw-import-errors {
  margin: 8px 0 0;
  padding-left: 18px;
  font-size: 12px;
  color: var(--el-color-danger);
}
</style>
