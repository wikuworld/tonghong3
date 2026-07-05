<template>
  <AdminSection :title="t('pages.masterItems.title')" :subtitle="t('pages.masterItems.subtitle')">
    <template #actions>
      <el-input v-model="keyword" :placeholder="t('pages.masterItems.searchPlaceholder')" clearable class="master-items-toolbar-search" />
      <el-select v-model="filterCategory" clearable :placeholder="t('pages.masterItems.filterCategory')" class="master-items-filter-category">
        <el-option :label="t('pages.masterItems.allCategory')" value="" />
        <el-option label="PU" value="PU" />
        <el-option label="Suide" value="Suide" />
        <el-option label="SubKon" value="SubKon" />
      </el-select>
      <el-button v-if="canView" :icon="Download" @click="handleExport">{{ t('pages.masterItems.export') }}</el-button>
      <el-button v-if="canCreate" type="success" :icon="Upload" @click="openImportDialog">{{ t('pages.masterItems.import') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <p v-if="stats.total" class="master-items-stats-hint">
      {{ t('pages.masterItems.statTotal') }}: {{ stats.total }}
      · PU {{ stats.pu }}
      · Suide {{ stats.suide }}
      · SubKon {{ stats.subkon }}
      · {{ t('pages.masterItems.statShown') }}: {{ total }}
    </p>

    <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" max-height="58vh" :empty-text="t('pages.masterItems.tableEmpty')">
      <el-table-column :label="t('common.noLabel')" width="56" align="center">
        <template #default="{ $index }">{{ rowNumber($index) }}</template>
      </el-table-column>
      <el-table-column prop="category" :label="t('common.category')" width="100" align="center" />
      <el-table-column prop="item_code" :label="t('common.code')" min-width="90" show-overflow-tooltip />
      <el-table-column prop="material_name" :label="t('common.material')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="thickness_range" :label="t('common.thickness')" width="90" align="center" />
      <el-table-column prop="color" :label="t('common.color')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="emboss" :label="t('common.emboss')" min-width="120" show-overflow-tooltip />
      <el-table-column :label="t('common.actions')" width="120" align="center" fixed="right">
        <template #default="{ row }">
          <div class="flex flex-wrap items-center justify-center gap-1">
            <el-tooltip :content="t('common.detail')" placement="top">
              <el-button :icon="View" link type="info" :aria-label="t('common.detail')" @click="openDetail(row)" />
            </el-tooltip>
            <el-tooltip :content="t('common.edit')" placement="top">
              <el-button v-if="canUpdate" :icon="EditPen" link type="primary" :aria-label="t('common.edit')" @click="openEdit(row)" />
            </el-tooltip>
            <el-tooltip :content="t('common.delete')" placement="top">
              <el-button v-if="canDelete" :icon="Delete" link type="danger" :aria-label="t('common.delete')" @click="removeRow(row)" />
            </el-tooltip>
          </div>
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
                <el-option label="Suide" value="Suide" />
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
              <el-input v-model="form.color" maxlength="500" />
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
        <el-descriptions-item :label="t('common.emboss')">{{ detailRow.emboss || '-' }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" :icon="Close" @click="detailVisible = false">{{ t('common.close') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialogVisible" :title="t('pages.masterItems.importTitle')" width="600px" destroy-on-close align-center>
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
        <el-button :icon="Close" @click="importDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate" type="primary" :icon="Check" :disabled="!importFile" @click="handleImport">
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
import { Delete, EditPen, Plus, Close, Check, Upload, Download, View } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { createMasterItem, deleteMasterItem, listMasterItemsPage, updateMasterItem, exportMasterItems, importMasterItems } from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canCreate, canUpdate, canDelete, canView } = useModulePermission('masterItems')
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const filterCategory = ref('')
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

async function load() {
  loading.value = true
  try {
    const data = await listMasterItemsPage({
      limit: pageSize.value,
      offset: (page.value - 1) * pageSize.value,
      keyword: keyword.value,
      category: filterCategory.value,
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

function rowNumber(index) {
  return (page.value - 1) * pageSize.value + index + 1
}

watch([page, pageSize, filterCategory], () => {
  load()
})

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
}

function openDetail(row) {
  detailRow.value = row
  detailVisible.value = true
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

function openImportDialog() {
  importDialogVisible.value = true
  importFile.value = null
}

function handleFileChange(file) {
  importFile.value = file.raw
}

async function handleExport() {
  try {
    await exportMasterItems()
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

onMounted(load)
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

.master-items-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>
