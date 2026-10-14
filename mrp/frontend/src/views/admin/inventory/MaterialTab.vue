<template>
  <div class="admin-inner-card">
    <div class="admin-inner-card__head">
      <div>
        <h3 class="admin-inner-card__title">{{ t('pages.inventory.materialListTitle') }}</h3>
        <p class="admin-inner-card__sub">
          {{ t('pages.inventory.materialListSubtitle', { n: filtered.length, total: materials.length }) }}
        </p>
      </div>
      <div class="inventory-toolbar">
        <el-select v-model="typeFilter" clearable size="small" class="inventory-toolbar__type" :placeholder="t('pages.inventory.type')">
          <el-option :label="t('pages.inventory.typeLeather')" value="leather" />
          <el-option :label="t('pages.inventory.typeChemical')" value="chemical" />
          <el-option :label="t('pages.inventory.typeAccessory')" value="accessory" />
        </el-select>
        <el-input
          v-model="search"
          clearable
          size="small"
          class="inventory-toolbar__search"
          :placeholder="t('pages.inventory.searchPlaceholder')"
        />
      </div>
    </div>

    <el-table
      :data="filtered"
      @sort-change="onSortChange"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="fixed"
      :empty-text="t('pages.inventory.tableEmpty')"
    >
      <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
      <el-table-column prop="code" :label="t('common.code')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="name" :label="t('common.name')" min-width="200" show-overflow-tooltip />
      <el-table-column :label="t('pages.inventory.type')" min-width="110">
        <template #default="{ row }">
          <el-tag size="small" effect="plain">{{ typeLabel(row.material_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="unit" :label="t('pages.inventory.unit')" width="90" align="center" />
      <el-table-column v-if="showKimiaColumns" :label="t('pages.inventory.size')" min-width="100" show-overflow-tooltip>
        <template #default="{ row }">{{ kimiaSizeCell(row) }}</template>
      </el-table-column>
      <el-table-column v-if="showKulitColumns" :label="t('common.thickness')" min-width="110" show-overflow-tooltip>
        <template #default="{ row }">{{ kulitCell(row, row.thickness) }}</template>
      </el-table-column>
      <el-table-column v-if="showKulitColumns" :label="t('common.color')" min-width="120" show-overflow-tooltip>
        <template #default="{ row }">{{ kulitCell(row, row.color) }}</template>
      </el-table-column>
      <el-table-column v-if="showCostColumns" :label="t('pages.inventory.minStock')" width="100" align="right">
        <template #default="{ row }">{{ costCell(row, row.min_stock) }}</template>
      </el-table-column>
      <el-table-column v-if="showCostColumns" :label="t('pages.inventory.cost')" width="120" align="right">
        <template #default="{ row }">{{ costCell(row, formatCurrency(row.cost_price)) }}</template>
      </el-table-column>
      <el-table-column :label="t('common.status')" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? t('status.active') : t('status.inactive') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="canUpdate" :label="t('common.actions')" width="88" align="center" fixed="right">
        <template #default="{ row }">
          <AdminTableActions :show-edit="true" @edit="openEdit(row)" />
        </template>
      </el-table-column>
    </el-table>
    <div class="flex justify-end mt-3">
      <el-pagination v-model:current-page="page" v-model:page-size="pageSize" :page-sizes="[10,20,50,100]" layout="total, sizes, prev, pager, next" :total="totalRows" background />
    </div>

    <el-dialog
      v-model="formVisible"
      :title="isEdit ? t('common.edit') : t('common.create')"
      width="560px"
      destroy-on-close
      align-center
    >
      <el-form :model="form" label-position="top" class="inventory-form">
        <el-form-item :label="t('common.code')" required>
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item :label="t('common.name')" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item :label="t('pages.inventory.type')">
          <el-select v-model="form.material_type" class="w-full">
            <el-option :label="t('pages.inventory.typeLeather')" value="leather" />
            <el-option :label="t('pages.inventory.typeChemical')" value="chemical" />
            <el-option :label="t('pages.inventory.typeAccessory')" value="accessory" />
          </el-select>
        </el-form-item>
        <template v-if="isChemicalForm">
          <el-form-item :label="t('pages.inventory.unit')" required>
            <el-select v-model="form.unit" filterable clearable class="w-full" :loading="unitOptionsLoading" :placeholder="t('pages.inventory.unitSelectPlaceholder')">
              <el-option v-for="u in unitOptions" :key="u.id" :label="u.unit" :value="u.unit" />
            </el-select>
            <p class="mt-1 text-xs text-slate-500">{{ t('pages.inventory.unitKimiaHint') }}</p>
          </el-form-item>
          <el-form-item :label="t('pages.inventory.size')">
            <el-input v-model="form.size" clearable :placeholder="t('pages.inventory.sizePlaceholder')" />
          </el-form-item>
        </template>
        <el-form-item v-else :label="t('pages.inventory.unit')">
          <el-input v-model="form.unit" />
        </el-form-item>
        <template v-if="isLeatherForm">
          <el-form-item :label="t('common.thickness')">
            <el-input v-model="form.thickness" :placeholder="t('pages.inventory.thicknessPlaceholder')" clearable />
          </el-form-item>
          <el-form-item :label="t('common.color')">
            <el-input v-model="form.color" clearable />
          </el-form-item>
        </template>
        <template v-else-if="!isChemicalForm">
          <el-form-item :label="t('pages.inventory.minStock')">
            <el-input-number v-model="form.min_stock" class="w-full" :controls="false" />
          </el-form-item>
          <el-form-item :label="t('pages.inventory.cost')">
            <el-input-number v-model="form.cost_price" class="w-full" :controls="false" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate || canUpdate" type="primary" :icon="Check" :loading="saving" @click="submit">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Check, Close } from '@element-plus/icons-vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { listMaterials, createMaterial, updateMaterial, listInventoryUnits } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'
import { formatCurrency } from '../../../utils/format'
import { useModulePermission } from '../../../composables/useModulePermission'

const emit = defineEmits(['loading'])
const { t } = useI18n()
const { canCreate, canUpdate } = useModulePermission('inventory')

const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const sortBy = ref(null)
const sortDir = ref('asc')
const saving = ref(false)
const materials = ref([])
const search = ref('')
const typeFilter = ref('')
const formVisible = ref(false)
const isEdit = ref(false)
const form = reactive({
  id: null,
  code: '',
  name: '',
  material_type: 'leather',
  unit: '',
  min_stock: null,
  cost_price: null,
  thickness: '',
  color: '',
  size: '',
})

const unitOptions = ref([])
const unitOptionsLoading = ref(false)

watch(loading, (v) => emit('loading', v))

const filtered = computed(() => materials.value)

const isLeatherForm = computed(() => isKulitType(form.material_type))

const isChemicalForm = computed(() => {
  const s = String(form.material_type || '').toLowerCase()
  return s === 'chemical' || s === 'kimia'
})

const showKulitColumns = computed(() => !typeFilter.value || typeFilter.value === 'leather')

const showKimiaColumns = computed(() => !typeFilter.value || typeFilter.value === 'chemical')

const showCostColumns = computed(() => {
  if (!typeFilter.value) return true
  return typeFilter.value !== 'leather' && typeFilter.value !== 'chemical'
})

function isKulitType(type) {
  const s = String(type || '').toLowerCase()
  return s === 'kulit' || s === 'leather'
}

function toApiMaterialType(uiType) {
  if (uiType === 'leather') return 'kulit'
  if (uiType === 'chemical') return 'kimia'
  if (uiType === 'accessory') return 'material_lain'
  return uiType
}

function toUiMaterialType(erpType) {
  const s = String(erpType || '').toLowerCase()
  if (s === 'kulit') return 'leather'
  if (s === 'kimia') return 'chemical'
  if (s === 'material_lain' || s === 'material') return 'accessory'
  return erpType || 'leather'
}

function kulitCell(row, value) {
  if (!isKulitType(row.material_type)) return '—'
  const s = (value == null ? '' : String(value)).trim()
  return s || '—'
}

function costCell(row, value) {
  if (isKulitType(row.material_type)) return '—'
  if (String(row.material_type || '').toLowerCase() === 'kimia') return '—'
  return value ?? '—'
}

function isKimiaType(type) {
  return String(type || '').toLowerCase() === 'kimia'
}

function kimiaSizeCell(row) {
  if (!isKimiaType(row.material_type)) return '—'
  const s = (row.size == null ? '' : String(row.size)).trim()
  return s || '—'
}

async function loadKimiaUnitOptions() {
  if (!isChemicalForm.value) {
    unitOptions.value = []
    return
  }
  unitOptionsLoading.value = true
  try {
    unitOptions.value = await listInventoryUnits({ material_type: 'kimia', active_only: true })
  } catch {
    unitOptions.value = []
  } finally {
    unitOptionsLoading.value = false
  }
}

watch(
  () => form.material_type,
  () => {
    void loadKimiaUnitOptions()
  },
)

function typeLabel(type) {
  const ui = toUiMaterialType(type)
  if (ui === 'leather') return t('pages.inventory.typeLeather')
  if (ui === 'chemical') return t('pages.inventory.typeChemical')
  if (ui === 'accessory') return t('pages.inventory.typeAccessory')
  return type || '-'
}

async function reload() {
  loading.value = true
  try {
    const params = buildPageParams({
      page: page.value,
      pageSize: pageSize.value,
      sortBy: sortBy.value,
      sortDir: sortDir.value,
      extra: {
        q: search.value.trim() || undefined,
        material_type: typeFilter.value ? toApiMaterialType(typeFilter.value) : undefined,
      },
    })
    const raw = await listMaterials(params)
    const pageData = normalizePageResult(raw, { page: page.value, pageSize: pageSize.value })
    materials.value = pageData.items
    totalRows.value = pageData.total
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy
  sortDir.value = mapped.sortDir
  page.value = 1
  reload()
}

watch([page, pageSize], () => reload())
watch([search, typeFilter], () => { page.value = 1; reload() })

function openCreate() {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    code: '',
    name: '',
    material_type: typeFilter.value === 'chemical' ? 'chemical' : 'leather',
    unit: typeFilter.value === 'chemical' ? '' : 'sqft',
    min_stock: null,
    cost_price: null,
    thickness: '',
    color: '',
    size: '',
  })
  void loadKimiaUnitOptions()
  formVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    code: row.code,
    name: row.name,
    material_type: toUiMaterialType(row.material_type),
    unit: row.unit || '',
    min_stock: row.min_stock,
    cost_price: row.cost_price,
    thickness: row.thickness || '',
    color: row.color || '',
    size: row.size || '',
  })
  void loadKimiaUnitOptions()
  formVisible.value = true
}

async function submit() {
  if (!form.code || !form.name) {
    ElMessage.warning(t('common.fillRequired'))
    return
  }
  if (isChemicalForm.value && !String(form.unit || '').trim()) {
    ElMessage.warning(t('pages.inventory.unitRequired'))
    return
  }
  saving.value = true
  try {
    const apiType = toApiMaterialType(form.material_type)
    const body = {
      code: form.code,
      name: form.name,
      material_type: apiType,
      unit: form.unit,
    }
    if (isLeatherForm.value) {
      body.thickness = form.thickness?.trim() || null
      body.color = form.color?.trim() || null
      body.size = null
      body.min_stock = null
      body.cost_price = null
    } else if (isChemicalForm.value) {
      body.size = form.size?.trim() || null
      body.min_stock = null
      body.cost_price = null
      body.thickness = null
      body.color = null
    } else {
      body.min_stock = form.min_stock
      body.cost_price = form.cost_price
      body.thickness = null
      body.color = null
      body.size = null
    }
    if (isEdit.value) await updateMaterial(form.id, body)
    else await createMaterial(body)
    formVisible.value = false
    await reload()
    ElMessage.success(t('common.saveSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

defineExpose({ reload, openCreate })
onMounted(reload)
</script>

<style scoped>
.inventory-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  min-width: 0;
}
.inventory-toolbar__type {
  width: 9.5rem;
  max-width: 100%;
}
.inventory-toolbar__search {
  width: 15rem;
  max-width: 100%;
  min-width: 0;
}
.inventory-form :deep(.el-form-item) {
  margin-bottom: 14px;
}
</style>
