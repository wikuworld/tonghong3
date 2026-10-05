<template>
  <div class="admin-inner-card">
    <div class="admin-inner-card__head">
      <div>
        <h3 class="admin-inner-card__title">{{ t('pages.inventory.warehouseListTitle') }}</h3>
        <p class="admin-inner-card__sub">
          {{ t('pages.inventory.warehouseListSubtitle', { n: filtered.length, total: warehouses.length }) }}
        </p>
      </div>
      <el-input
        v-model="search"
        clearable
        size="small"
        class="inventory-toolbar__search"
        :placeholder="t('pages.inventory.searchPlaceholder')"
      />
    </div>

    <el-table
      :data="filtered" @sort-change="onSortChange"
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
      <el-table-column prop="name" :label="t('common.name')" min-width="180" show-overflow-tooltip />
      <el-table-column prop="location" :label="t('pages.inventory.location')" min-width="180" show-overflow-tooltip />
      <el-table-column :label="t('common.status')" width="110" align="center">
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
      width="520px"
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
        <el-form-item :label="t('pages.inventory.location')">
          <el-input v-model="form.location" type="textarea" :rows="3" />
        </el-form-item>
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
import { listWarehouses, createWarehouse, updateWarehouse } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'
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
const warehouses = ref([])
const search = ref('')
const formVisible = ref(false)
const isEdit = ref(false)
const form = reactive({ id: null, code: '', name: '', location: '' })

watch(loading, (v) => emit('loading', v))

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return warehouses.value
  return warehouses.value.filter((row) =>
    [row.code, row.name, row.location].filter(Boolean).some((v) => String(v).toLowerCase().includes(q))
  )
})

async function reload() {
  loading.value = true
  try {
    const raw = await listWarehouses(buildPageParams({ page: page.value, pageSize: pageSize.value, sortBy: sortBy.value, sortDir: sortDir.value }))
    const pageData = normalizePageResult(raw, { page: page.value, pageSize: pageSize.value })
    warehouses.value = pageData.items
    totalRows.value = pageData.total
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  isEdit.value = false
  Object.assign(form, { id: null, code: '', name: '', location: '' })
  formVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  Object.assign(form, {
    id: row.id,
    code: row.code,
    name: row.name,
    location: row.location || '',
  })
  formVisible.value = true
}

async function submit() {
  if (!form.code || !form.name) {
    ElMessage.warning(t('common.fillRequired'))
    return
  }
  saving.value = true
  try {
    const body = { code: form.code, name: form.name, location: form.location }
    if (isEdit.value) await updateWarehouse(form.id, body)
    else await createWarehouse(body)
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
function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy
  sortDir.value = mapped.sortDir
  page.value = 1
  reload()
}
watch([page, pageSize], () => reload())
onMounted(reload)
</script>

<style scoped>
.inventory-toolbar__search {
  width: 15rem;
  max-width: 100%;
  min-width: 0;
}
.inventory-form :deep(.el-form-item) {
  margin-bottom: 14px;
}
</style>
