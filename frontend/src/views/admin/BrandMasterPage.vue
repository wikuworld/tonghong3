<template>
  <AdminSection :title="t('pages.brandMaster.title')" :subtitle="t('pages.brandMaster.subtitle')">
    <template #actions>
      <div class="brand-master-toolbar">
        <el-input
          v-model="keyword"
          :placeholder="t('pages.brandMaster.searchPlaceholder')"
          clearable
          class="brand-master-toolbar-search"
          :prefix-icon="Search"
        />
        <el-select v-model="filterCustomerId" clearable filterable class="brand-master-filter-customer" :placeholder="t('pages.brandMaster.filterCustomer')">
          <el-option :label="t('pages.brandMaster.allCustomer')" value="" />
          <el-option v-for="c in customers" :key="c.id" :label="`${c.code || ''} ${c.name || ''}`.trim()" :value="c.id" />
        </el-select>
        <el-switch v-model="groupByCustomer" />
        <span class="text-sm text-slate-600">{{ t('pages.brandMaster.groupByCustomer') }}</span>
        <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
      </div>
    </template>

    <el-table
      :data="filteredRows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="fixed"
      row-key="id"
      :tree-props="{ children: 'children' }"
      :empty-text="t('pages.brandMaster.tableEmpty')"
      :default-expand-all="groupByCustomer"
      max-height="68vh"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="name" :label="t('common.name')" min-width="220" show-overflow-tooltip />
      <el-table-column :label="t('common.customer')" min-width="320">
        <template #default="{ row }">
          <template v-if="row.actions_disabled">
            <span class="brand-master-group-label">{{ row.customer_name }}</span>
          </template>
          <template v-else>
            <div class="brand-master-customer-cell">
              <span class="brand-master-customer-text">{{ customerSummary(row) }}</span>
              <el-tag
                v-if="(row.customer_names || []).length > 1"
                size="small"
                type="info"
                effect="plain"
              >
                +{{ (row.customer_names || []).length - 1 }}
              </el-tag>
            </div>
          </template>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="132" align="center" fixed="right">
        <template #default="{ row }">
          <template v-if="!row.actions_disabled">
            <div class="flex flex-wrap items-center justify-center gap-0">
              <el-tooltip content="Detail" placement="top">
                <el-button :icon="View" link type="info" aria-label="Detail" @click="openDetail(row)" />
              </el-tooltip>
              <el-tooltip v-if="canUpdate" :content="t('common.edit')" placement="top">
                <el-button :icon="EditPen" link type="warning" :aria-label="t('common.edit')" @click="openEdit(row)" />
              </el-tooltip>
              <el-tooltip v-if="canDelete" :content="t('common.delete')" placement="top">
                <el-button :icon="Delete" link type="danger" :aria-label="t('common.delete')" @click="removeRow(row)" />
              </el-tooltip>
            </div>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="formVisible" :title="isEdit ? t('pages.brandMaster.editTitle') : t('pages.brandMaster.createTitle')" width="520px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('common.name')" required>
          <el-input v-model="form.name" maxlength="255" />
        </el-form-item>
        <el-form-item :label="t('common.customer')">
          <el-select v-model="form.customer_ids" multiple clearable filterable class="w-full">
            <el-option v-for="c in customers" :key="c.id" :label="`${c.code || ''} ${c.name || ''}`.trim()" :value="c.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="brand-master-dialog-footer">
          <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button v-if="canCreate || canUpdate" type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="Detail Brand" width="620px" destroy-on-close align-center>
      <el-descriptions :column="1" border>
        <el-descriptions-item :label="t('common.name')">{{ detailRow?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.customer')">
          <div class="brand-master-detail-customers">
            <el-tag
              v-for="(c, idx) in detailCustomers"
              :key="`${c}-${idx}`"
              size="small"
              effect="plain"
              type="info"
            >
              {{ c }}
            </el-tag>
            <span v-if="!detailCustomers.length" class="text-slate-500">{{ t('common.emptyValue') }}</span>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <div class="brand-master-dialog-footer">
          <el-button type="primary" @click="detailVisible = false">{{ t('common.close') || 'Tutup' }}</el-button>
        </div>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, EditPen, Plus, Search, View } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  createBrand,
  deleteBrand,
  listBrands,
  listCustomers,
  updateBrand,
} from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canCreate, canUpdate, canDelete } = useModulePermission('brandMaster')
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const filterCustomerId = ref('')
const groupByCustomer = ref(false)
const rows = ref([])
const customers = ref([])

const formVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const detailVisible = ref(false)
const detailRow = ref(null)
const form = reactive({
  name: '',
  customer_ids: [],
})

async function load() {
  loading.value = true
  try {
    const [brands, cust] = await Promise.all([listBrands(), listCustomers()])
    customers.value = cust
    rows.value = brands.map((b) => ({
      ...b,
      customer_names: (b.customer_ids || []).map((id) => cust.find((c) => c.id === id)?.name).filter(Boolean),
      customer_name: (b.customer_ids || []).map((id) => cust.find((c) => c.id === id)?.name).filter(Boolean).join(', ') || t('common.emptyValue'),
    }))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

const filteredRows = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  const base = rows.value.filter((r) => {
    if (filterCustomerId.value && !(r.customer_ids || []).includes(filterCustomerId.value)) return false
    if (!q) return true
    return JSON.stringify(r).toLowerCase().includes(q)
  })
  if (!groupByCustomer.value) return base
  const groups = new Map()
  for (const row of base) {
    const assigned = (row.customer_ids || []).length ? row.customer_ids : [0]
    for (const gid of assigned) {
      if (!groups.has(gid)) {
        const cname = gid
          ? customers.value.find((c) => c.id === gid)?.name || t('common.emptyValue')
          : t('common.emptyValue')
        groups.set(gid, {
          id: `g-${gid}`,
          code: '',
          name: cname,
          customer_name: cname,
          customer_names: [cname],
          actions_disabled: true,
          children: [],
        })
      }
      groups.get(gid).children.push({
        ...row,
        source_id: row.id,
        id: `g-${gid}-b-${row.id}`,
      })
    }
  }
  return Array.from(groups.values())
})

function customerSummary(row) {
  const names = (row.customer_names || []).filter(Boolean)
  if (!names.length) return t('common.emptyValue')
  if (names.length === 1) return names[0]
  return `${names[0]} +${names.length - 1}`
}

function openCreate() {
  isEdit.value = false
  editingId.value = null
  form.name = ''
  form.customer_ids = []
  formVisible.value = true
}

function openEdit(row) {
  isEdit.value = true
  editingId.value = row.source_id || row.id
  form.name = row.name || ''
  form.customer_ids = [...(row.customer_ids || [])]
  formVisible.value = true
}

function openDetail(row) {
  detailRow.value = row
  detailVisible.value = true
}

const detailCustomers = computed(() => {
  if (!detailRow.value) return []
  return (detailRow.value.customer_names || []).filter(Boolean)
})

async function submit() {
  if (!form.name?.trim()) {
    ElMessage.warning(t('pages.brandMaster.codeRequired'))
    return
  }
  saving.value = true
  try {
    const payload = {
      name: form.name?.trim() || undefined,
      customer_ids: [...(form.customer_ids || [])],
    }
    if (isEdit.value && editingId.value) {
      await updateBrand(editingId.value, payload)
    } else {
      await createBrand(payload)
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
  const targetId = row.source_id || row.id
  try {
    await ElMessageBox.confirm(
      t('pages.brandMaster.deleteConfirm', { name: row.name || row.id }),
      t('pages.brandMaster.deleteTitle'),
      {
        type: 'warning',
        confirmButtonText: t('common.delete'),
        cancelButtonText: t('common.cancel'),
      },
    )
    await deleteBrand(targetId)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

onMounted(load)
</script>

<style scoped>
.brand-master-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.brand-master-toolbar-search {
  width: 320px;
}

.brand-master-filter-customer {
  width: 240px;
}

.brand-master-customer-cell {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  max-width: 100%;
}

.brand-master-customer-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.brand-master-group-label {
  font-weight: 600;
  color: #334155;
}

.brand-master-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.brand-master-detail-customers {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
