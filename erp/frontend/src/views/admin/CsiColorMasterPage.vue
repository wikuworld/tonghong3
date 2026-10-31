<template>
  <AdminSection :title="t('pages.csiColors.title')" :subtitle="t('pages.csiColors.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        clearable
        :placeholder="t('pages.csiColors.searchPlaceholder')"
        class="csi-toolbar-search"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canView" :icon="Download" @click="handleExport">{{ t('pages.csiColors.export') }}</el-button>
      <el-button v-if="canCreate" type="success" :icon="Upload" @click="openImportDialog">{{ t('pages.csiColors.importExcel') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head csi-inner-head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.csiColors.listSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.csiColors.listSubtitle') }}</p>
        </div>
        <el-tooltip placement="top-start" :show-after="200">
          <template #content>{{ t('pages.csiColors.pageHint') }}</template>
          <el-icon class="csi-page-hint" :size="16" tabindex="0" :aria-label="t('pages.csiColors.pageHint')">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>

      <div class="admin-stats-grid admin-stats-grid--5 csi-stats">
        <div class="admin-stat-card admin-stat-card--info">
          <span class="admin-stat-card__value">{{ total }}</span>
          <span class="admin-stat-card__label">{{ t('pages.csiColors.statShown') }}</span>
        </div>
        <div class="admin-stat-card" v-for="b in summaryBuyers" :key="b">
          <span class="admin-stat-card__value">{{ summary[b] || 0 }}</span>
          <span class="admin-stat-card__label">{{ b }}</span>
        </div>
      </div>

      <div class="filter-panel csi-filter-panel">
        <p class="filter-panel__title">{{ t('common.filter') }}</p>
        <el-select
          v-model="filterBuyer"
          clearable
          filterable
          class="csi-filter-buyer"
          :placeholder="t('common.buyer')"
        >
          <el-option v-for="b in formOptions.buyer_codes" :key="b" :label="b" :value="b" />
        </el-select>
      </div>

      <p class="admin-scroll-hint">{{ t('pages.csiColors.scrollHint') }}</p>

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
          :empty-text="t('pages.csiColors.tableEmpty')"
          @sort-change="onSortChange"
        >
          <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
          <el-table-column prop="buyer_code" :label="t('common.buyer')" width="110" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="plain" type="info">{{ row.buyer_code || '—' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="color_code" :label="t('pages.csiColors.colCode')" width="140" show-overflow-tooltip />
          <el-table-column prop="color_name" :label="t('common.color')" min-width="200" show-overflow-tooltip />
          <el-table-column prop="source_file" :label="t('pages.csiColors.colSource')" min-width="140" show-overflow-tooltip />
          <el-table-column
            prop="created_at"
            :label="t('pages.csiColors.colCreatedAt')"
            width="148"
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">{{ formatAuditDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column
            prop="updated_at"
            :label="t('pages.csiColors.colUpdatedAt')"
            width="148"
            align="center"
            sortable="custom"
          >
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

      <div class="csi-pagination">
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

    <el-dialog
      v-model="formVisible"
      width="560px"
      destroy-on-close
      align-center
      @closed="resetForm"
    >
      <template #header>
        <div>
          <h3 class="csi-dialog-title">
            {{ editId ? t('pages.csiColors.editTitle') : t('pages.csiColors.createTitle') }}
          </h3>
          <p class="csi-dialog-sub">{{ t('pages.csiColors.dialogFormSub') }}</p>
        </div>
      </template>
      <el-form label-position="top" @submit.prevent>
        <el-form-item :label="t('common.buyer')" required>
          <el-select v-model="form.buyer_code" filterable class="w-full" :placeholder="t('pages.csiColors.formBuyerPlaceholder')">
            <el-option v-for="b in formOptions.buyer_codes" :key="b" :label="b" :value="b" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.csiColors.colCode')" required>
          <el-input v-model="form.color_code" maxlength="64" :placeholder="t('pages.csiColors.formCodePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('common.color')" required>
          <el-input v-model="form.color_name" maxlength="255" :placeholder="t('pages.csiColors.formColorPlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="save">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialogVisible" :title="t('pages.csiColors.importExcelTitle')" width="640px" destroy-on-close align-center>
      <p class="csi-excel-sub">{{ t('pages.csiColors.importExcelSub') }}</p>
      <p class="csi-excel-hint">{{ t('pages.csiColors.importExcelHint') }}</p>
      <ul class="csi-excel-cols">
        <li>{{ t('pages.csiColors.importExcelColsRequired') }}</li>
        <li>{{ t('pages.csiColors.importExcelColsOptional') }}</li>
      </ul>
      <div class="csi-excel-actions">
        <el-button :icon="Download" @click="downloadImportTemplate">{{ t('pages.csiColors.downloadTemplate') }}</el-button>
      </div>
      <p class="csi-excel-panel-title">{{ t('pages.csiColors.importExcelPanelTitle') }}</p>
      <el-upload :auto-upload="false" :limit="1" accept=".xlsx,.xls" :on-change="handleImportFile">
        <el-button type="primary">{{ t('pages.csiColors.selectFile') }}</el-button>
      </el-upload>
      <div v-if="importResult" class="csi-excel-result">
        <p>
          {{
            t('pages.csiColors.importResultSummary', {
              created: importResult.created || 0,
              updated: importResult.updated || 0,
              skipped: importResult.skipped || 0,
            })
          }}
        </p>
        <ul v-if="importResult.errors?.length" class="csi-excel-errors">
          <li v-for="(err, idx) in importResult.errors.slice(0, 8)" :key="idx">
            {{ t('pages.csiColors.importErrorRow', { row: err.row, code: err.color_code || '—', reason: err.reason }) }}
          </li>
          <li v-if="importResult.errors.length > 8">
            {{ t('pages.csiColors.importErrorMore', { n: importResult.errors.length - 8 }) }}
          </li>
        </ul>
      </div>
      <template #footer>
        <el-button @click="importDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :disabled="!importFile || importing" :loading="importing" @click="handleImport">
          {{ t('pages.csiColors.doImport') }}
        </el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, InfoFilled, Plus, Refresh, Upload } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import {
  createCsiColor,
  deleteCsiColor,
  exportCsiColors,
  importCsiColors,
  listCsiColorsPage,
  listCsiFormOptions,
  updateCsiColor,
} from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canView, canCreate, canUpdate, canDelete } = useModulePermission('csiColors')

const loading = ref(false)
const saving = ref(false)
const importing = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)
const keyword = ref('')
const filterBuyer = ref('')
const sortBy = ref('')
const sortDir = ref('asc')
const formVisible = ref(false)
const importDialogVisible = ref(false)
const importFile = ref(null)
const importResult = ref(null)
const editId = ref(null)
const summaryBuyers = ['NIKE', 'UA', 'NB', 'ADIDAS']
const summary = reactive({ NIKE: 0, UA: 0, NB: 0, ADIDAS: 0 })

const formOptions = reactive({
  buyer_codes: [],
})

const form = reactive({
  buyer_code: '',
  color_code: '',
  color_name: '',
})

async function loadFormOptions() {
  try {
    const r = await listCsiFormOptions()
    formOptions.buyer_codes = r.buyer_codes || []
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function loadSummary() {
  try {
    const parts = await Promise.all(
      summaryBuyers.map((b) => listCsiColorsPage({ buyer_code: b, limit: 1, offset: 0 })),
    )
    summaryBuyers.forEach((b, i) => {
      summary[b] = Number(parts[i]?.total || 0)
    })
  } catch {
    summaryBuyers.forEach((b) => {
      summary[b] = 0
    })
  }
}

async function load() {
  loading.value = true
  try {
    const r = await listCsiColorsPage({
      buyer_code: filterBuyer.value || undefined,
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
  loadSummary()
}

function resetForm() {
  editId.value = null
  form.buyer_code = ''
  form.color_code = ''
  form.color_name = ''
}

function openCreate() {
  resetForm()
  formVisible.value = true
}

function openEdit(row) {
  editId.value = row.id
  form.buyer_code = row.buyer_code || ''
  form.color_code = row.color_code || ''
  form.color_name = row.color_name || ''
  formVisible.value = true
}

async function save() {
  if (!form.buyer_code.trim() || !form.color_code.trim() || !form.color_name.trim()) {
    ElMessage.warning(t('pages.csiColors.requiredFields'))
    return
  }
  saving.value = true
  try {
    const body = {
      buyer_code: form.buyer_code.trim(),
      color_code: form.color_code.trim(),
      color_name: form.color_name.trim(),
    }
    if (editId.value) await updateCsiColor(editId.value, body)
    else await createCsiColor(body)
    ElMessage.success(t('common.saveSuccess'))
    formVisible.value = false
    await Promise.all([load(), loadSummary(), loadFormOptions()])
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(t('pages.csiColors.deleteConfirm'), t('common.confirm'), { type: 'warning' })
    await deleteCsiColor(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
    await loadSummary()
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
    await exportCsiColors()
    ElMessage.success(t('pages.csiColors.exportSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadImportTemplate() {
  try {
    await exportCsiColors({ template: true })
    ElMessage.success(t('pages.csiColors.templateSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function handleImport() {
  if (!importFile.value) return
  importing.value = true
  importResult.value = null
  try {
    const result = await importCsiColors(importFile.value)
    importResult.value = result
    ElMessage.success(
      t('pages.csiColors.importResultSummary', {
        created: result.created || 0,
        updated: result.updated || 0,
        skipped: result.skipped || 0,
      }),
    )
    await Promise.all([load(), loadSummary(), loadFormOptions()])
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    importing.value = false
  }
}

watch([page, pageSize], () => load())
watch([filterBuyer, keyword], () => {
  page.value = 1
  load()
})

onMounted(() => {
  loadFormOptions()
  load()
  loadSummary()
})
</script>

<style scoped>
.csi-toolbar-search { width: 240px; }
.csi-inner-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.csi-page-hint { color: #64748b; cursor: help; }
.csi-filter-panel { margin: 12px 0; }
.csi-filter-buyer { width: 200px; }
.csi-pagination { display: flex; justify-content: flex-end; margin-top: 12px; }
.csi-dialog-title { margin: 0; font-size: 16px; }
.csi-dialog-sub { margin: 4px 0 0; color: #64748b; font-size: 13px; }
.csi-excel-sub { margin: 0 0 6px; font-size: 14px; }
.csi-excel-hint, .csi-excel-cols { margin: 0 0 8px; font-size: 12px; color: var(--el-text-color-secondary); line-height: 1.45; }
.csi-excel-cols { padding-left: 18px; }
.csi-excel-actions { margin-bottom: 12px; }
.csi-excel-panel-title { margin: 0 0 8px; font-size: 13px; font-weight: 600; }
.csi-excel-result { margin-top: 14px; padding: 10px 12px; border-radius: 6px; background: var(--el-fill-color-light); font-size: 13px; }
.csi-excel-errors { margin: 8px 0 0; padding-left: 18px; font-size: 12px; color: var(--el-color-danger); }
</style>
