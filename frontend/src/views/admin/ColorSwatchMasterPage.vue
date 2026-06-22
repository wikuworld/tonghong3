<template>
  <AdminSection :title="t('pages.colorSwatch.title')" :subtitle="t('pages.colorSwatch.subtitle')">
    <template #actions>
      <el-input v-model="filterFactory" clearable :placeholder="t('pages.colorSwatch.filterFactory')" class="w-36" />
      <el-select v-model="filterBuyer" clearable filterable :placeholder="t('common.buyer')" class="w-32">
        <el-option v-for="b in formOptions.buyer_codes" :key="b" :label="b" :value="b" />
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
      <el-table-column prop="customer_code" :label="t('pages.colorSwatch.colCustomerCode')" width="100" show-overflow-tooltip />
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

    <el-dialog v-model="formVisible" :title="editId ? t('common.edit') : t('common.create')" width="680px" destroy-on-close>
      <el-form label-position="top">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item :label="t('pages.colorSwatch.formCustomer')" required>
              <el-select
                v-model="form.customer_id"
                filterable
                clearable
                class="w-full"
                :placeholder="t('pages.colorSwatch.formCustomerPlaceholder')"
                @change="onCustomerChange"
              >
                <el-option
                  v-for="c in formOptions.customers"
                  :key="c.id"
                  :label="customerOptionLabel(c)"
                  :value="c.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('pages.colorSwatch.colFactory')" required>
              <el-select
                v-model="form.factory_key"
                filterable
                allow-create
                default-first-option
                class="w-full"
                :placeholder="t('pages.colorSwatch.formFactoryPlaceholder')"
              >
                <el-option v-for="fk in factoryKeyOptions" :key="fk" :label="fk" :value="fk" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('common.buyer')" required>
              <el-select v-model="form.buyer_code" filterable class="w-full" :placeholder="t('common.buyer')">
                <el-option v-for="b in formOptions.buyer_codes" :key="b" :label="b" :value="b" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('common.material')" required>
              <el-select
                v-model="form.material_name"
                filterable
                allow-create
                default-first-option
                class="w-full"
                :placeholder="t('pages.colorSwatch.formMaterialPlaceholder')"
                @change="onMaterialChange"
              >
                <el-option v-for="m in formOptions.materials" :key="m" :label="m" :value="m" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('pages.colorSwatch.colCode')">
              <el-input v-model="form.color_code" maxlength="64" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('common.color')" required>
              <el-select
                v-model="form.color_name"
                filterable
                allow-create
                default-first-option
                class="w-full"
                :placeholder="t('pages.colorSwatch.formColorPlaceholder')"
              >
                <el-option v-for="c in colorOptions" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('pages.po.emboss')">
              <el-select
                v-model="form.emboss"
                filterable
                allow-create
                default-first-option
                clearable
                class="w-full"
                :placeholder="t('pages.colorSwatch.formEmbossPlaceholder')"
              >
                <el-option v-for="e in embossOptions" :key="e" :label="e" :value="e" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('pages.po.colorStandart')">
              <el-input v-model="form.color_standard" maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item :label="t('common.backing')">
              <el-select
                v-model="form.backing"
                filterable
                allow-create
                default-first-option
                clearable
                class="w-full"
                :placeholder="t('pages.colorSwatch.formBackingPlaceholder')"
              >
                <el-option v-for="b in formOptions.backings" :key="b" :label="b" :value="b" />
              </el-select>
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
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  createColorSwatchRecipe,
  deleteColorSwatchRecipe,
  importColorSwatchBundled,
  importColorSwatchCsv,
  listColorSwatchFormOptions,
  listColorSwatchRecipesPage,
  me,
  updateColorSwatchRecipe,
} from '../../api/client'

const { t } = useI18n()
import { useModulePermission } from '../../composables/useModulePermission'

const { canCreate, canUpdate, canDelete } = useModulePermission('colorSwatch')
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

const formOptions = reactive({
  customers: [],
  factory_keys: [],
  factory_keys_by_customer: {},
  buyer_codes: [],
  materials: [],
  colors_by_material: {},
  embosses_by_material: {},
  backings: [],
})

const form = reactive({
  customer_id: null,
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

const factoryKeyOptions = computed(() => {
  const cid = form.customer_id
  if (cid && formOptions.factory_keys_by_customer[cid]?.length) {
    const keys = [...formOptions.factory_keys_by_customer[cid]]
    if (form.factory_key && !keys.includes(form.factory_key)) keys.unshift(form.factory_key)
    return keys
  }
  return formOptions.factory_keys
})

const colorOptions = computed(() => {
  const mat = String(form.material_name || '').trim()
  if (!mat) return []
  return formOptions.colors_by_material[mat] || []
})

const embossOptions = computed(() => {
  const mat = String(form.material_name || '').trim()
  if (!mat) return []
  return formOptions.embosses_by_material[mat] || []
})

function customerOptionLabel(c) {
  const code = String(c.code || '').trim()
  const name = String(c.name || '').trim()
  if (code && name) return `${code} — ${name}`
  return code || name || `#${c.id}`
}

function onCustomerChange() {
  const keys = form.customer_id ? formOptions.factory_keys_by_customer[form.customer_id] : null
  if (keys?.length === 1) {
    form.factory_key = keys[0]
  } else if (form.factory_key && keys?.length && !keys.includes(form.factory_key)) {
    form.factory_key = ''
  }
}

function onMaterialChange() {
  if (form.color_name && colorOptions.value.length && !colorOptions.value.includes(form.color_name)) {
    // keep custom value (allow-create)
  }
  if (form.emboss && embossOptions.value.length && !embossOptions.value.includes(form.emboss)) {
    // keep custom value
  }
}

async function loadFormOptions() {
  try {
    const r = await listColorSwatchFormOptions()
    formOptions.customers = r.customers || []
    formOptions.factory_keys = r.factory_keys || []
    const byCustomer = {}
    for (const [k, v] of Object.entries(r.factory_keys_by_customer || {})) {
      byCustomer[Number(k)] = v
    }
    formOptions.factory_keys_by_customer = byCustomer
    formOptions.buyer_codes = r.buyer_codes || []
    formOptions.materials = r.materials || []
    formOptions.colors_by_material = r.colors_by_material || {}
    formOptions.embosses_by_material = r.embosses_by_material || {}
    formOptions.backings = r.backings || []
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

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
  form.customer_id = null
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
  form.customer_id = row.customer_id || null
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
  if (
    !form.customer_id
    || !form.factory_key.trim()
    || !form.buyer_code.trim()
    || !form.color_name.trim()
    || !form.material_name.trim()
  ) {
    ElMessage.warning(t('pages.colorSwatch.requiredFields'))
    return
  }
  saving.value = true
  try {
    const body = {
      customer_id: form.customer_id,
      factory_key: form.factory_key.trim(),
      buyer_code: form.buyer_code.trim(),
      color_code: form.color_code.trim(),
      color_name: form.color_name.trim(),
      material_name: form.material_name.trim(),
      emboss: form.emboss.trim(),
      color_standard: form.color_standard.trim() || null,
      backing: form.backing.trim() || null,
      legacy_urut: form.legacy_urut.trim() || null,
    }
    if (editId.value) {
      await updateColorSwatchRecipe(editId.value, body)
    } else {
      await createColorSwatchRecipe(body)
    }
    ElMessage.success(t('common.saveSuccess'))
    formVisible.value = false
    await Promise.all([load(), loadFormOptions()])
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
    await Promise.all([load(), loadFormOptions()])
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
    await Promise.all([load(), loadFormOptions()])
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
  await Promise.all([loadFormOptions(), load()])
})
</script>
