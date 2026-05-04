<template>
  <AdminSection :title="t('pages.masterItems.title')" :subtitle="t('pages.masterItems.subtitle')">
    <template #actions>
      <el-input v-model="keyword" :placeholder="t('pages.masterItems.searchPlaceholder')" clearable class="master-items-toolbar-search" />
      <el-button :icon="Download" @click="handleExport">{{ t('pages.masterItems.export') }}</el-button>
      <el-button type="success" :icon="Upload" @click="openImportDialog">{{ t('pages.masterItems.import') }}</el-button>
      <el-button type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table :data="filteredRows" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('pages.masterItems.tableEmpty')">
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
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
              <el-button :icon="EditPen" link type="primary" :aria-label="t('common.edit')" @click="openEdit(row)" />
            </el-tooltip>
            <el-tooltip :content="t('common.delete')" placement="top">
              <el-button :icon="Delete" link type="danger" :aria-label="t('common.delete')" @click="removeRow(row)" />
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </el-table>

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
          <el-button type="primary" :icon="Check" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
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
        <el-button type="primary" :icon="Check" :disabled="!importFile" @click="handleImport">
          {{ t('pages.masterItems.doImport') }}
        </el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, EditPen, Plus, Close, Check, Upload, Download, View } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { createMasterItem, deleteMasterItem, listMasterItems, updateMasterItem, exportMasterItems, importMasterItems } from '../../api/client'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const rows = ref([])
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
    rows.value = await listMasterItems()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

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

const filteredRows = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) => JSON.stringify(r).toLowerCase().includes(q))
})

onMounted(load)
</script>

<style scoped>
.master-items-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
