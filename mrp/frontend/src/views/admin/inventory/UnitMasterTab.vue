<template>
  <div class="admin-inner-card">
    <div class="admin-inner-card__head">
      <div>
        <h3 class="admin-inner-card__title">{{ t('pages.inventory.unitMasterListTitle') }}</h3>
        <p class="admin-inner-card__sub">{{ t('pages.inventory.unitMasterListSubtitle') }}</p>
      </div>
      <el-select v-model="typeFilter" clearable size="small" class="inventory-toolbar__type" :placeholder="t('pages.inventory.type')">
        <el-option :label="t('pages.inventory.typeLeather')" value="kulit" />
        <el-option :label="t('pages.inventory.typeChemical')" value="kimia" />
        <el-option :label="t('pages.inventory.typeAccessory')" value="material_lain" />
        <el-option :label="t('pages.inventory.typeRp')" value="rp" />
      </el-select>
    </div>

    <el-table
      :data="filtered"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      :empty-text="t('pages.inventory.tableEmpty')"
    >
      <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
      <el-table-column :label="t('pages.inventory.type')" min-width="120">
        <template #default="{ row }">{{ typeLabel(row.material_type) }}</template>
      </el-table-column>
      <el-table-column prop="unit" :label="t('pages.inventory.unit')" min-width="120" />
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

    <el-dialog v-model="formVisible" :title="isEdit ? t('common.edit') : t('common.create')" width="480px" destroy-on-close align-center>
      <el-form :model="form" label-position="top" class="inventory-form">
        <el-form-item :label="t('pages.inventory.type')" required>
          <el-select v-model="form.material_type" class="w-full" :disabled="isEdit">
            <el-option :label="t('pages.inventory.typeLeather')" value="kulit" />
            <el-option :label="t('pages.inventory.typeChemical')" value="kimia" />
            <el-option :label="t('pages.inventory.typeAccessory')" value="material_lain" />
            <el-option :label="t('pages.inventory.typeRp')" value="rp" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.inventory.unit')" required>
          <el-input v-model="form.unit" maxlength="50" />
        </el-form-item>
        <el-form-item v-if="isEdit" :label="t('common.status')">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :icon="Check" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
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
import { createInventoryUnit, listInventoryUnits, updateInventoryUnit } from '../../../api/client'
import { useModulePermission } from '../../../composables/useModulePermission'

const emit = defineEmits(['loading'])
const { t } = useI18n()
const { canCreate, canUpdate } = useModulePermission('inventory')

const loading = ref(false)
const saving = ref(false)
const rows = ref([])
const typeFilter = ref('')
const formVisible = ref(false)
const isEdit = ref(false)
const form = reactive({ id: null, material_type: 'kimia', unit: '', is_active: true })

watch(loading, (v) => emit('loading', v))

const filtered = computed(() => {
  if (!typeFilter.value) return rows.value
  return rows.value.filter((r) => r.material_type === typeFilter.value)
})

function typeLabel(mt) {
  const s = String(mt || '').toLowerCase()
  if (s === 'kulit') return t('pages.inventory.typeLeather')
  if (s === 'kimia') return t('pages.inventory.typeChemical')
  if (s === 'material_lain') return t('pages.inventory.typeAccessory')
  if (s === 'rp') return t('pages.inventory.typeRp')
  return mt || '—'
}

async function reload() {
  loading.value = true
  try {
    rows.value = await listInventoryUnits({ active_only: false })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    material_type: typeFilter.value || 'kimia',
    unit: '',
    is_active: true,
  })
  formVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    material_type: row.material_type,
    unit: row.unit,
    is_active: row.is_active !== false,
  })
  formVisible.value = true
}

async function submit() {
  if (!canCreate.value && !canUpdate.value) return
  const unit = String(form.unit || '').trim()
  if (!unit) {
    ElMessage.warning(t('common.fillRequired'))
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      await updateInventoryUnit(form.id, {
        material_type: form.material_type,
        unit,
        is_active: form.is_active,
      })
    } else {
      await createInventoryUnit({
        material_type: form.material_type,
        unit,
        is_active: true,
      })
    }
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
.inventory-toolbar__type {
  width: 10rem;
  max-width: 100%;
}
.inventory-form :deep(.el-form-item) {
  margin-bottom: 14px;
}
</style>
