<template>
  <AdminSection :title="t('pages.colorSwatch.title')" :subtitle="t('pages.colorSwatch.subtitle')">
    <template #actions>
      <el-input v-model="filterFactory" clearable :placeholder="t('pages.colorSwatch.filterFactory')" class="w-36" />
      <el-select v-model="filterBuyer" clearable filterable :placeholder="t('common.buyer')" class="w-32">
        <el-option label="NIKE" value="NIKE" />
        <el-option label="ADIDAS" value="ADIDAS" />
        <el-option label="NB" value="NB" />
        <el-option label="UA" value="UA" />
        <el-option label="PUMA" value="PUMA" />
        <el-option label="REEBOK" value="REEBOK" />
      </el-select>
      <el-input v-model="keyword" clearable :placeholder="t('pages.colorSwatch.searchPlaceholder')" class="w-52" />
      <el-button :icon="Refresh" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
      <el-upload v-if="canCreate" :auto-upload="false" :show-file-list="false" accept=".csv" @change="onUploadCsv">
        <el-button type="success" :loading="importing">{{ t('pages.colorSwatch.importCsv') }}</el-button>
      </el-upload>
      <el-button v-if="isAdmin" type="warning" plain :loading="importingBundled" @click="importBundled">
        {{ t('pages.colorSwatch.importBundled') }}
      </el-button>
    </template>

    <el-tag type="info" class="mb-3">{{ t('common.total') }}: {{ total }}</el-tag>

    <el-table :data="rows" v-loading="loading" border stripe size="small" table-layout="fixed">
      <el-table-column type="index" :label="t('common.noLabel')" width="50" align="center" />
      <el-table-column prop="factory_key" :label="t('pages.colorSwatch.colFactory')" width="120" show-overflow-tooltip />
      <el-table-column prop="buyer_code" :label="t('common.buyer')" width="90" />
      <el-table-column prop="color_code" :label="t('pages.colorSwatch.colCode')" width="100" show-overflow-tooltip />
      <el-table-column prop="color_name" :label="t('common.color')" min-width="140" show-overflow-tooltip />
      <el-table-column prop="material_name" :label="t('common.material')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="emboss" :label="t('pages.po.emboss')" width="100" show-overflow-tooltip />
      <el-table-column prop="color_standard" :label="t('pages.po.colorStandart')" width="120" show-overflow-tooltip />
      <el-table-column prop="backing" :label="t('common.backing')" width="80" show-overflow-tooltip />
      <el-table-column prop="legacy_urut" :label="t('pages.colorSwatch.colUrut')" width="80" />
      <el-table-column :label="t('common.actions')" width="100" fixed="right" align="center">
        <template #default="{ row }">
          <el-button v-if="canUpdate" link type="primary" size="small" @click="openEdit(row)">{{ t('common.edit') }}</el-button>
          <el-button v-if="canDelete" link type="danger" size="small" @click="remove(row)">{{ t('common.delete') }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-3 flex justify-end">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        size="small"
        layout="total, sizes, prev, pager, next"
        :total="total"
        :page-sizes="[25, 50, 100, 200]"
      />
    </div>

    <el-dialog v-model="formVisible" :title="editId ? t('common.edit') : t('common.create')" width="640px" destroy-on-close>
      <el-form label-position="top">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item :label="t('pages.colorSwatch.colFactory')" required>
              <el-input v-model="form.factory_key" maxlength="80" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('common.buyer')" required>
              <el-input v-model="form.buyer_code" maxlength="32" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('pages.colorSwatch.colCode')">
              <el-input v-model="form.color_code" maxlength="64" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('common.color')" required>
              <el-input v-model="form.color_name" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :span="24">
            <el-form-item :label="t('common.material')" required>
              <el-input v-model="form.material_name" maxlength="500" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('pages.po.emboss')">
              <el-input v-model="form.emboss" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('pages.po.colorStandart')">
              <el-input v-model="form.color_standard" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('common.backing')">
              <el-input v-model="form.backing" maxlength="120" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('pages.colorSwatch.colUrut')">
              <el-input v-model="form.legacy_urut" maxlength="32" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="save">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import {
  createColorSwatchRecipe,
  deleteColorSwatchRecipe,
  importColorSwatchBundled,
  importColorSwatchCsv,
  listColorSwatchRecipesPage,
  me,
  updateColorSwatchRecipe,
} from '../../api/client'

const { t } = useI18n()
const canCreate = can('masterImport', 'create') || can('po', 'create')
const canUpdate = can('masterImport', 'create') || can('po', 'update')
const canDelete = can('masterImport', 'create')
const isAdmin = ref(false)

const loading = ref(false)
const saving = ref(false)
const importing = ref(false)
const importingBundled = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)
const keyword = ref('')
const filterFactory = ref('')
const filterBuyer = ref('')
const formVisible = ref(false)
const editId = ref(null)
const form = reactive({
  factory_key: '',
  buyer_code: '',
  color_code: '',
  color_name: '',
  material_name: '',
  emboss: '',
  color_standard: '',
  backing: '',
  legacy_urut: '',
})

async function load() {
  loading.value = true
  try {
    const r = await listColorSwatchRecipesPage({
      factory_key: filterFactory.value || undefined,
      buyer_code: filterBuyer.value || undefined,
      q: keyword.value || undefined,
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

function reload() {
  page.value = 1
  load()
}

function resetForm() {
  editId.value = null
  form.factory_key = ''
  form.buyer_code = ''
  form.color_code = ''
  form.color_name = ''
  form.material_name = ''
  form.emboss = ''
  form.color_standard = ''
  form.backing = ''
  form.legacy_urut = ''
}

function openCreate() {
  resetForm()
  formVisible.value = true
}

function openEdit(row) {
  editId.value = row.id
  form.factory_key = row.factory_key || ''
  form.buyer_code = row.buyer_code || ''
  form.color_code = row.color_code || ''
  form.color_name = row.color_name || ''
  form.material_name = row.material_name || ''
  form.emboss = row.emboss || ''
  form.color_standard = row.color_standard || ''
  form.backing = row.backing || ''
  form.legacy_urut = row.legacy_urut || ''
  formVisible.value = true
}

async function save() {
  if (!form.factory_key.trim() || !form.buyer_code.trim() || !form.color_name.trim() || !form.material_name.trim()) {
    ElMessage.warning(t('pages.colorSwatch.requiredFields'))
    return
  }
  saving.value = true
  try {
    const body = { ...form }
    if (editId.value) {
      await updateColorSwatchRecipe(editId.value, body)
    } else {
      await createColorSwatchRecipe(body)
    }
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
    await ElMessageBox.confirm(t('pages.colorSwatch.deleteConfirm'), t('common.confirm'), { type: 'warning' })
    await deleteColorSwatchRecipe(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function onUploadCsv(uploadFile) {
  const file = uploadFile?.raw
  if (!file) return
  importing.value = true
  try {
    const r = await importColorSwatchCsv(file)
    ElMessage.success(
      t('pages.colorSwatch.importDone', {
        inserted: r.inserted,
        updated: r.updated,
        total: r.total,
      }),
    )
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    importing.value = false
  }
}

async function importBundled() {
  importingBundled.value = true
  try {
    const r = await importColorSwatchBundled()
    ElMessage.success(
      t('pages.colorSwatch.importDone', {
        inserted: r.inserted,
        updated: r.updated,
        total: r.total,
      }),
    )
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    importingBundled.value = false
  }
}

watch([page, pageSize], () => load())
watch([filterFactory, filterBuyer, keyword], () => {
  page.value = 1
  load()
})

onMounted(async () => {
  try {
    const u = await me()
    isAdmin.value = (u?.role || '') === 'admin'
  } catch {
    isAdmin.value = false
  }
  load()
})
</script>
