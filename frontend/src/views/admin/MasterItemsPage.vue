<template>
  <AdminSection :title="t('pages.masterItems.title')" :subtitle="t('pages.masterItems.subtitle')">
    <template #actions>
      <el-input v-model="keyword" :placeholder="t('pages.masterItems.searchPlaceholder')" clearable class="master-items-toolbar-search" />
      <el-button @click="handleExport">{{ t('pages.masterItems.export') }}</el-button>
      <el-button type="success" @click="openImportDialog">{{ t('pages.masterItems.import') }}</el-button>
      <el-button type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table :data="filteredRows" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('pages.masterItems.tableEmpty')">
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="item_code" :label="t('common.code')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="material_name" :label="t('common.material')" min-width="180" show-overflow-tooltip />
      <el-table-column prop="thickness_mm" :label="t('common.thickness')" min-width="100" />
      <el-table-column prop="color" :label="t('common.color')" min-width="110" show-overflow-tooltip />
      <el-table-column prop="softness" :label="t('common.softness')" min-width="110" />
      <el-table-column prop="backing" :label="t('common.backing')" min-width="110" />
      <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="130" show-overflow-tooltip />
      <el-table-column prop="exim_material_code" :label="t('pages.masterItems.eximMaterialCode')" min-width="120" show-overflow-tooltip />
      <el-table-column :label="t('common.actions')" width="100" align="center" fixed="right">
        <template #default="{ row }">
          <div class="flex flex-wrap items-center justify-center gap-0">
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
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.softness')">
              <el-select
                v-model="form.softness"
                :placeholder="t('pages.masterItems.softnessPlaceholder')"
                clearable
                filterable
                allow-create
                class="w-full"
              >
                <el-option label="Soft" value="Soft" />
                <el-option label="Semi-Soft" value="Semi-Soft" />
                <el-option label="Medium" value="Medium" />
                <el-option label="Semi-Hard" value="Semi-Hard" />
                <el-option label="Hard" value="Hard" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.colorReference')">
              <el-input v-model="form.color_reference" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.masterItems.colorStandard')">
              <el-input v-model="form.color_standard" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.backing')">
              <el-input v-model="form.backing" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.masterItems.qtyDefault')">
              <el-input v-model="form.quantity_order_default" type="number" step="0.01" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.styleArticle')">
              <el-input v-model="form.style_article" maxlength="100" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.category')">
              <el-input v-model="form.category" maxlength="100" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.masterItems.eximMaterialCode')">
              <el-input v-model="form.exim_material_code" maxlength="80" clearable />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="master-items-dialog-footer">
          <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
        </div>
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
        <el-button @click="importDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :disabled="!importFile" @click="handleImport">
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
import { Delete, EditPen, Plus } from '@element-plus/icons-vue'
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
const importDialogVisible = ref(false)
const importFile = ref(null)
const uploadRef = ref(null)

const form = reactive({
  item_code: '',
  material_name: '',
  thickness_range: '',
  color: '',
  emboss: '',
  softness: '',
  color_reference: '',
  color_standard: '',
  backing: '',
  quantity_order_default: '',
  style_article: '',
  category: '',
  exim_material_code: '',
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
  form.softness = ''
  form.color_reference = ''
  form.color_standard = ''
  form.backing = ''
  form.quantity_order_default = ''
  form.style_article = ''
  form.category = ''
  form.exim_material_code = ''
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
  form.softness = row.softness || ''
  form.color_reference = row.color_reference || ''
  form.color_standard = row.color_standard || ''
  form.backing = row.backing || ''
  form.quantity_order_default = row.quantity_order_default ?? ''
  form.style_article = row.style_article || ''
  form.category = row.category || ''
  form.exim_material_code = row.exim_material_code || ''
  formVisible.value = true
}

async function submit() {
  if (!form.item_code?.trim()) {
    ElMessage.warning(t('pages.masterItems.codeRequired'))
    return
  }
  saving.value = true
  try {
    const payload = {
      item_code: form.item_code.trim(),
      material_name: form.material_name || undefined,
      thickness_range: form.thickness_range || undefined,
      color: form.color || undefined,
      emboss: form.emboss || undefined,
      softness: form.softness || undefined,
      color_reference: form.color_reference || undefined,
      color_standard: form.color_standard || undefined,
      backing: form.backing || undefined,
      quantity_order_default:
        form.quantity_order_default !== '' ? Number(form.quantity_order_default) : undefined,
      style_article: form.style_article || undefined,
      category: form.category || undefined,
      exim_material_code: form.exim_material_code?.trim() || undefined,
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
