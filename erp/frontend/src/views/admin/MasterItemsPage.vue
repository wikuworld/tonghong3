<template>
  <AdminSection :title="t('pages.masterItems.title')" :subtitle="t('pages.masterItems.subtitle')">
    <template #actions>
      <el-input v-model="keyword" :placeholder="t('pages.masterItems.searchPlaceholder')" clearable class="master-items-toolbar-search" />
      <el-select v-model="filterCategory" clearable :placeholder="t('pages.masterItems.filterCategory')" class="master-items-filter-category">
        <el-option :label="t('pages.masterItems.allCategory')" value="" />
        <el-option label="PU" value="PU" />
        <el-option label="Suede" value="Suede" />
        <el-option label="SubKon" value="SubKon" />
      </el-select>
      <el-button v-if="canView" :icon="Download" @click="handleExport">{{ t('pages.masterItems.export') }}</el-button>
      <el-button v-if="canCreate" type="success" :icon="Upload" @click="openImportDialog">{{ t('pages.masterItems.import') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <p v-if="stats.total" class="master-items-stats-hint">
      {{ t('pages.masterItems.statTotal') }}: {{ stats.total }}
      · PU {{ stats.pu }}
      · Suede {{ stats.suide }}
      · SubKon {{ stats.subkon }}
      · {{ t('pages.masterItems.statShown') }}: {{ total }}
    </p>

    <el-table
      :data="rows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="fixed"
      max-height="58vh"
      :empty-text="t('pages.masterItems.tableEmpty')"
      @sort-change="onSortChange"
    >
      <el-table-column :label="t('common.noLabel')" width="56" align="center">
        <template #default="{ $index }">{{ rowNumber($index) }}</template>
      </el-table-column>
      <el-table-column prop="category" :label="t('common.category')" width="100" align="center" />
      <el-table-column prop="item_code" :label="t('common.code')" min-width="90" show-overflow-tooltip />
      <el-table-column prop="material_name" :label="t('common.material')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="thickness_range" :label="t('common.thickness')" width="90" align="center" />
      <el-table-column prop="color" :label="t('common.color')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="color_code" :label="t('pages.masterItems.colColorCode')" width="100" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.color_code || '—' }}</span>
          <div v-if="row.color_code" class="master-items-color-links">
            <el-tag v-if="row.in_csi" size="small" type="success" effect="plain">{{ t('pages.masterItems.linkCsi') }}</el-tag>
            <el-tag v-if="row.in_swatch" size="small" type="info" effect="plain">{{ t('pages.masterItems.linkSwatch') }}</el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="emboss" :label="t('common.emboss')" min-width="120" show-overflow-tooltip />
      <el-table-column
        prop="created_at"
        :label="t('pages.masterItems.colCreatedAt')"
        width="148"
        align="center"
        sortable="custom"
      >
        <template #default="{ row }">{{ formatAuditDateTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column
        prop="updated_at"
        :label="t('pages.masterItems.colUpdatedAt')"
        width="148"
        align="center"
        sortable="custom"
      >
        <template #default="{ row }">{{ formatAuditDateTime(row.updated_at) }}</template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="112" align="center" fixed="right">
        <template #default="{ row }">
          <AdminTableActions
            :show-view="true"
            :show-edit="canUpdate"
            :show-delete="canDelete"
            @view="openDetail(row)"
            @edit="openEdit(row)"
            @delete="removeRow(row)"
          />
        </template>
      </el-table-column>
    </el-table>

    <div class="master-items-pagination">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[25, 50, 100, 200]"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>

    <el-dialog v-model="formVisible" :title="isEdit ? t('pages.masterItems.editTitle') : t('pages.masterItems.createTitle')" width="720px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-row :gutter="12">
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.category')" required>
              <el-select v-model="form.category" clearable class="w-full">
                <el-option label="PU" value="PU" />
                <el-option label="Suede" value="Suede" />
                <el-option label="SubKon" value="SubKon" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.code')" required>
              <el-input v-model="form.item_code" maxlength="50" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.material')">
              <el-input v-model="form.material_name" maxlength="500" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.thickness')">
              <el-select
                v-model="form.thickness_range"
                :placeholder="t('pages.masterItems.thicknessRangePlaceholder')"
                clearable
                filterable
                allow-create
                class="w-full"
              >
                <el-option label="1.0-1.2" value="1.0-1.2" />
                <el-option label="1.2-1.4" value="1.2-1.4" />
                <el-option label="1.4-1.6" value="1.4-1.6" />
                <el-option label="1.6-1.8" value="1.6-1.8" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.color')">
              <el-select
                v-model="form.color"
                filterable
                allow-create
                default-first-option
                clearable
                class="w-full"
                :placeholder="t('pages.masterItems.colorFromCsi')"
                @change="onColorChange"
              >
                <el-option
                  v-for="opt in colorLinkOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
              <div v-if="colorLinks.color_code" class="master-items-color-panel">
                <div class="master-items-color-panel__row">
                  <span class="master-items-color-panel__code">{{ t('pages.masterItems.colorCodeLabel') }}: {{ colorLinks.color_code }}</span>
                  <el-tag v-if="colorLinks.in_csi" size="small" type="success" effect="plain">{{ t('pages.masterItems.linkCsi') }}</el-tag>
                  <el-tag v-if="colorLinks.in_swatch" size="small" type="info" effect="plain">{{ t('pages.masterItems.linkSwatch') }}</el-tag>
                </div>
                <p v-if="colorLinks.csi.length" class="master-items-color-panel__text">
                  {{ t('pages.masterItems.colorLinkedCsi') }}:
                  {{ colorLinks.csi.map((c) => `${c.buyer_code} · ${c.color_name}`).join(', ') }}
                </p>
                <p v-if="colorLinks.swatch_count" class="master-items-color-panel__text">
                  {{ t('pages.masterItems.colorLinkedSwatch', { n: colorLinks.swatch_count }) }}
                  <template v-if="colorLinks.swatch_factories.length">
                    · {{ t('pages.masterItems.colorLinkedFactories', { list: colorLinks.swatch_factories.join(', ') }) }}
                  </template>
                </p>
                <p v-if="colorLinks.fluorescent.length" class="master-items-color-panel__text">
                  {{ t('pages.masterItems.colorOverlayFluorescent') }}:
                  {{ colorLinks.fluorescent.map((f) => `${f.buyer_code} · ${f.color_name}`).join(', ') }}
                </p>
                <p v-if="!colorLinks.in_csi && !colorLinks.in_swatch" class="master-items-color-panel__muted">
                  {{ t('pages.masterItems.colorLinkedNone') }}
                </p>
              </div>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.emboss')">
              <el-input v-model="form.emboss" maxlength="500" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="master-items-dialog-footer">
          <el-button :icon="Close" @click="formVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button v-if="canCreate || canUpdate" type="primary" :icon="Check" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" :title="t('pages.masterItems.detailTitle')" width="640px" destroy-on-close align-center>
      <el-descriptions v-if="detailRow" :column="2" border>
        <el-descriptions-item :label="t('common.code')">{{ detailRow.item_code }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.category')">{{ detailRow.category || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.material')">{{ detailRow.material_name || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.thickness')">{{ detailRow.thickness_range || detailRow.thickness_mm || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.color')">{{ detailRow.color || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.masterItems.colColorCode')">
          <span>{{ detailRow.color_code || '—' }}</span>
          <span v-if="detailRow.color_code" class="master-items-color-links master-items-color-links--inline">
            <el-tag v-if="detailRow.in_csi" size="small" type="success" effect="plain">{{ t('pages.masterItems.linkCsi') }}</el-tag>
            <el-tag v-if="detailRow.in_swatch" size="small" type="info" effect="plain">{{ t('pages.masterItems.linkSwatch') }}</el-tag>
          </span>
        </el-descriptions-item>
        <el-descriptions-item v-if="detailColorLinks.csi.length" :label="t('pages.masterItems.colorLinkedCsi')" :span="2">
          {{ detailColorLinks.csi.map((c) => `${c.buyer_code} · ${c.color_name}`).join(', ') }}
        </el-descriptions-item>
        <el-descriptions-item v-if="detailColorLinks.swatch_count" :label="t('pages.masterItems.linkSwatch')">
          {{ t('pages.masterItems.colorLinkedSwatch', { n: detailColorLinks.swatch_count }) }}
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.emboss')">{{ detailRow.emboss || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.masterItems.colCreatedAt')">{{ formatAuditDateTime(detailRow.created_at) }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.masterItems.colUpdatedAt')">{{ formatAuditDateTime(detailRow.updated_at) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" :icon="Close" @click="detailVisible = false">{{ t('common.close') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialogVisible" :title="t('pages.masterItems.importTitle')" width="640px" destroy-on-close align-center>
      <p class="master-items-import-sub">{{ t('pages.masterItems.importSub') }}</p>
      <p class="master-items-import-hint">{{ t('pages.masterItems.importHint') }}</p>
      <ul class="master-items-import-cols">
        <li>{{ t('pages.masterItems.importColsRequired') }}</li>
        <li>{{ t('pages.masterItems.importColsOptional') }}</li>
        <li>{{ t('pages.masterItems.importPartialHint') }}</li>
      </ul>
      <div class="master-items-import-actions">
        <el-button :icon="Download" @click="downloadImportTemplate">{{ t('pages.masterItems.downloadTemplate') }}</el-button>
      </div>
      <p class="master-items-import-panel-title">{{ t('pages.masterItems.importPanelTitle') }}</p>
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleFileChange"
      >
        <el-button type="primary">{{ t('pages.masterItems.selectFile') }}</el-button>
      </el-upload>
      <div v-if="importResult" class="master-items-import-result">
        <p>
          {{
            t('pages.masterItems.importResultSummary', {
              created: importResult.created || 0,
              updated: importResult.updated || 0,
              skipped: importResult.skipped || 0,
            })
          }}
        </p>
        <ul v-if="importResult.errors?.length" class="master-items-import-errors">
          <li v-for="(err, idx) in importResult.errors.slice(0, 8)" :key="idx">
            {{ t('pages.masterItems.importErrorRow', { row: err.row, code: err.item_code || '—', reason: err.reason }) }}
          </li>
          <li v-if="importResult.errors.length > 8">
            {{ t('pages.masterItems.importErrorMore', { n: importResult.errors.length - 8 }) }}
          </li>
        </ul>
      </div>
      <template #footer>
        <el-button :icon="Close" @click="importDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate" type="primary" :icon="Check" :disabled="!importFile || importing" :loading="importing" @click="handleImport">
          {{ t('pages.masterItems.doImport') }}
        </el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Close, Check, Upload, Download } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import { createMasterItem, deleteMasterItem, listMasterItemsPage, updateMasterItem, exportMasterItems, importMasterItems, getColorLinks, listColorLinkOptions } from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canCreate, canUpdate, canDelete, canView } = useModulePermission('masterItems')
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const filterCategory = ref('')
const sortBy = ref('')
const sortDir = ref('asc')
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)
const stats = reactive({ total: 0, pu: 0, suide: 0, subkon: 0 })
let keywordTimer = null
const formVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const detailVisible = ref(false)
const detailRow = ref(null)
const importDialogVisible = ref(false)
const importFile = ref(null)
const uploadRef = ref(null)

const form = reactive({
  item_code: '',
  material_name: '',
  thickness_range: '',
  color: '',
  emboss: '',
  category: '',
})
const colorLinkOptions = ref([])
const colorLinks = reactive({
  color_code: '',
  color_qualifier: null,
  in_csi: false,
  in_swatch: false,
  csi: [],
  swatch_count: 0,
  swatch_factories: [],
  fluorescent: [],
})
const detailColorLinks = reactive({
  csi: [],
  swatch_count: 0,
})
let colorLinkTimer = null

function resetColorLinks(target = colorLinks) {
  target.color_code = ''
  target.color_qualifier = null
  target.in_csi = false
  target.in_swatch = false
  target.csi = []
  target.swatch_count = 0
  target.swatch_factories = []
  target.fluorescent = []
}

function applyColorLinksPayload(payload, target = colorLinks) {
  target.color_code = payload.color_code || ''
  target.color_qualifier = payload.color_qualifier || null
  target.in_csi = Boolean(payload.in_csi)
  target.in_swatch = Boolean(payload.in_swatch)
  target.csi = payload.csi || []
  target.swatch_count = Number(payload.swatch_count || 0)
  target.swatch_factories = payload.swatch_factories || []
  target.fluorescent = payload.fluorescent || []
}

async function refreshColorLinks(colorText, target = colorLinks) {
  const text = String(colorText || '').trim()
  if (!text) {
    resetColorLinks(target)
    return
  }
  try {
    const payload = await getColorLinks({ color: text })
    applyColorLinksPayload(payload, target)
  } catch {
    resetColorLinks(target)
  }
}

function onColorChange() {
  if (colorLinkTimer) clearTimeout(colorLinkTimer)
  colorLinkTimer = setTimeout(() => {
    void refreshColorLinks(form.color)
  }, 280)
}

async function loadColorLinkOptions() {
  try {
    const r = await listColorLinkOptions()
    colorLinkOptions.value = r.options || []
  } catch {
    colorLinkOptions.value = []
  }
}

async function load() {
  loading.value = true
  try {
    const data = await listMasterItemsPage({
      limit: pageSize.value,
      offset: (page.value - 1) * pageSize.value,
      keyword: keyword.value,
      category: filterCategory.value,
      sort_by: sortBy.value || undefined,
      sort_dir: sortBy.value ? sortDir.value : undefined,
    })
    rows.value = data.items || []
    total.value = data.total || 0
    if (data.stats) {
      stats.total = data.stats.total || 0
      stats.pu = data.stats.pu || 0
      stats.suide = data.stats.suide || 0
      stats.subkon = data.stats.subkon || 0
    }
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

function rowNumber(index) {
  return (page.value - 1) * pageSize.value + index + 1
}

watch([page, pageSize, filterCategory], () => {
  load()
})

watch(
  () => form.color,
  () => {
    if (!formVisible.value) return
    onColorChange()
  },
)

watch(keyword, () => {
  if (keywordTimer) clearTimeout(keywordTimer)
  keywordTimer = setTimeout(() => {
    page.value = 1
    load()
  }, 350)
})

function resetForm() {
  form.item_code = ''
  form.material_name = ''
  form.thickness_range = ''
  form.color = ''
  form.emboss = ''
  form.category = ''
  resetColorLinks()
}

function openDetail(row) {
  detailRow.value = row
  detailVisible.value = true
  resetColorLinks(detailColorLinks)
  if (row?.color || row?.color_code) {
    void refreshColorLinks(row.color || '', detailColorLinks)
  }
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
  form.item_code = row.item_code || ''
  form.material_name = row.material_name || ''
  form.thickness_range = row.thickness_range || ''
  form.color = row.color || ''
  form.emboss = row.emboss || ''
  form.category = row.category || ''
  formVisible.value = true
  void refreshColorLinks(form.color)
}

async function submit() {
  if (!form.item_code?.trim()) {
    ElMessage.warning(t('pages.masterItems.codeRequired'))
    return
  }
  if (!form.category?.trim()) {
    ElMessage.warning(t('pages.masterItems.categoryRequired'))
    return
  }
  saving.value = true
  try {
    const payload = {
      item_code: form.item_code.trim(),
      category: form.category || undefined,
      material_name: form.material_name || undefined,
      thickness_range: form.thickness_range || undefined,
      color: form.color || undefined,
      emboss: form.emboss || undefined,
    }
    if (isEdit.value && editingId.value) {
      await updateMasterItem(editingId.value, payload)
    } else {
      await createMasterItem(payload)
    }
    formVisible.value = false
    ElMessage.success(t('common.save'))
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

async function removeRow(row) {
  try {
    await ElMessageBox.confirm(
      t('pages.masterItems.deleteConfirm', { code: row.item_code || row.id }),
      t('pages.masterItems.deleteTitle'),
      {
        type: 'warning',
        confirmButtonText: t('common.delete'),
        cancelButtonText: t('common.cancel'),
      },
    )
    await deleteMasterItem(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

const importing = ref(false)
const importResult = ref(null)

function openImportDialog() {
  importDialogVisible.value = true
  importFile.value = null
  importResult.value = null
}

function handleFileChange(file) {
  importFile.value = file.raw
  importResult.value = null
}

async function handleExport() {
  try {
    await exportMasterItems()
    ElMessage.success(t('pages.masterItems.exportSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadImportTemplate() {
  try {
    await exportMasterItems({ template: true })
    ElMessage.success(t('pages.masterItems.templateSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function handleImport() {
  if (!importFile.value) return
  importing.value = true
  importResult.value = null
  try {
    const result = await importMasterItems(importFile.value)
    importResult.value = result
    ElMessage.success(
      t('pages.masterItems.importResultSummary', {
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

onMounted(() => {
  load()
  loadColorLinkOptions()
})
</script>

<style scoped>
.master-items-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.master-items-filter-category {
  width: 160px;
}

.master-items-stats-hint {
  margin: 0 0 12px;
  font-size: 12px;
  color: #64748b;
}

.master-items-color-links {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 2px;
}

.master-items-color-links--inline {
  display: inline-flex;
  margin-top: 0;
  margin-left: 6px;
  vertical-align: middle;
}

.master-items-color-panel {
  margin-top: 8px;
  padding: 8px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #f8fafc;
}

.master-items-color-panel__row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.master-items-color-panel__code {
  font-size: 12px;
  font-weight: 600;
  color: #334155;
}

.master-items-color-panel__text,
.master-items-color-panel__muted {
  margin: 6px 0 0;
  font-size: 12px;
  line-height: 1.4;
  color: #475569;
}

.master-items-color-panel__muted {
  color: #94a3b8;
}

.master-items-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

.master-items-import-sub {
  margin: 0 0 6px;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.master-items-import-hint {
  margin: 0 0 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.4;
}

.master-items-import-cols {
  margin: 0 0 12px;
  padding-left: 18px;
  font-size: 12px;
  color: var(--el-text-color-regular);
  line-height: 1.45;
}

.master-items-import-actions {
  margin-bottom: 12px;
}

.master-items-import-panel-title {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 600;
}

.master-items-import-result {
  margin-top: 14px;
  padding: 10px 12px;
  border-radius: 6px;
  background: var(--el-fill-color-light);
  font-size: 13px;
}

.master-items-import-errors {
  margin: 8px 0 0;
  padding-left: 18px;
  font-size: 12px;
  color: var(--el-color-danger);
  line-height: 1.4;
}
</style>
