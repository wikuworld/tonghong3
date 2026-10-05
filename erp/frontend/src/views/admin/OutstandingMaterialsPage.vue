<template>
  <AdminSection :title="t('outstandingMaterial.title')" :subtitle="t('outstandingMaterial.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        clearable
        class="outstanding-toolbar-search"
        :placeholder="t('outstandingMaterial.searchPlaceholder')"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="loadMaterials">{{ t('common.refresh') }}</el-button>
    </template>

    <div class="filter-panel mb-4">
      <p class="filter-panel__title">{{ t('common.filter') }}</p>
      <el-form class="filter-form" label-position="top">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item :label="t('outstandingMaterial.status')">
              <el-select v-model="filterStatus" clearable class="w-full" :placeholder="t('outstandingMaterial.status')">
                <el-option :label="t('outstandingMaterial.pending')" value="pending" />
                <el-option :label="t('outstandingMaterial.partial')" value="partial" />
                <el-option :label="t('outstandingMaterial.fulfilled')" value="fulfilled" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="10" :lg="8">
            <el-form-item :label="t('outstandingMaterial.customer')">
              <el-select
                v-model="filterCustomerId"
                clearable
                filterable
                class="w-full"
                :placeholder="t('outstandingMaterial.filterCustomer')"
              >
                <el-option
                  v-for="c in customers"
                  :key="c.id"
                  :label="customerOptionLabel(c)"
                  :value="c.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="8" :md="6" :lg="3" class="outstanding-filter-action-col">
            <el-form-item label="&nbsp;">
              <el-button class="w-full" :icon="RefreshLeft" @click="resetFilters">{{ t('common.reset') }}</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <div class="outstanding-stats mb-4">
      <div class="outstanding-stat">
        <span class="outstanding-stat__value">{{ stats.total }}</span>
        <span class="outstanding-stat__label">{{ t('common.total') }}</span>
      </div>
      <div class="outstanding-stat outstanding-stat--pending">
        <span class="outstanding-stat__value">{{ stats.pending }}</span>
        <span class="outstanding-stat__label">{{ t('outstandingMaterial.pending') }}</span>
      </div>
      <div class="outstanding-stat outstanding-stat--partial">
        <span class="outstanding-stat__value">{{ stats.partial }}</span>
        <span class="outstanding-stat__label">{{ t('outstandingMaterial.partial') }}</span>
      </div>
      <div class="outstanding-stat outstanding-stat--fulfilled">
        <span class="outstanding-stat__value">{{ stats.fulfilled }}</span>
        <span class="outstanding-stat__label">{{ t('outstandingMaterial.fulfilled') }}</span>
      </div>
    </div>

    <p class="mb-3 text-xs text-slate-500">{{ t('outstandingMaterial.flowHint') }}</p>

    <div class="admin-table-scroll">
      <el-table
        :data="displayedMaterials"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        table-layout="fixed"
        :empty-text="t('outstandingMaterial.tableEmpty')"
        @sort-change="onSortChange"
      >
        <el-table-column
          type="index"
          :label="t('common.noLabel')"
          width="50"
          align="center"
          fixed="left"
          :index="(i) => (page - 1) * pageSize + i + 1"
        />
        <el-table-column prop="po_number" :label="t('outstandingMaterial.poNumber')" min-width="140" show-overflow-tooltip sortable="custom">
          <template #default="{ row }">
            <el-button v-if="row.po_id" link type="primary" @click="goPo(row)">
              {{ row.po_number || `#${row.po_id}` }}
            </el-button>
            <span v-else>{{ row.po_number || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="customer_name" :label="t('outstandingMaterial.customer')" min-width="160" show-overflow-tooltip />
        <el-table-column prop="material_name" :label="t('outstandingMaterial.materialName')" min-width="200" show-overflow-tooltip />
        <el-table-column prop="total_qty" :label="t('outstandingMaterial.totalQty')" width="110" align="right">
          <template #default="{ row }">{{ formatQty(row.total_qty) }}</template>
        </el-table-column>
        <el-table-column prop="delivered_qty" :label="t('outstandingMaterial.deliveredQty')" width="110" align="right">
          <template #default="{ row }">{{ formatQty(row.delivered_qty) }}</template>
        </el-table-column>
        <el-table-column prop="balance_qty" :label="t('outstandingMaterial.balanceQty')" width="110" align="right">
          <template #default="{ row }">
            <span :class="{ 'font-semibold text-amber-700': Number(row.balance_qty) > 0 }">
              {{ formatQty(row.balance_qty) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('outstandingMaterial.status')" width="120" align="center" sortable="custom">
          <template #default="{ row }">
            <el-tag size="small" :type="statusTagType(row.status)">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" :label="t('common.updateDate')" width="130" sortable="custom">
          <template #default="{ row }">{{ formatDate(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="88" fixed="right" align="center">
          <template #default="{ row }">
            <AdminTableActions
              :show-view="Boolean(row.po_id)"
              :view-label="t('outstandingMaterial.openPo')"
              :more-items="outstandingMaterialMoreItems(row)"
              @view="goPo(row)"
              @more="(cmd) => cmd === 'markDelivered' && openDeliverDialog(row)"
            />
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="mt-3 flex justify-end">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        size="small"
        background
        layout="total, sizes, prev, pager, next"
        :total="totalRows"
        :page-sizes="[20, 50, 100, 200]"
      />
    </div>

    <el-dialog
      v-model="deliverDialogVisible"
      :title="t('outstandingMaterial.markDelivered')"
      width="520px"
      destroy-on-close
      align-center
    >
      <el-form label-position="top">
        <el-form-item :label="t('outstandingMaterial.materialName')">
          <el-input :model-value="currentMaterial.material_name" disabled />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item :label="t('outstandingMaterial.totalQty')">
              <el-input :model-value="formatQty(currentMaterial.total_qty)" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('outstandingMaterial.deliveredQty')">
              <el-input :model-value="formatQty(currentMaterial.delivered_qty)" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="t('outstandingMaterial.balanceQty')">
              <el-input :model-value="formatQty(currentMaterial.balance_qty)" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item :label="t('outstandingMaterial.deliverQty')" required>
          <el-input-number
            v-model="deliverQty"
            class="w-full"
            :min="0.01"
            :max="Number(currentMaterial.balance_qty) || 0"
            :precision="2"
            :step="1"
          />
          <span class="mt-1 block text-xs text-slate-500">{{ t('outstandingMaterial.deliverQtyHint') }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deliverDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canUpdate" type="primary" :loading="saving" @click="submitDelivery">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh, RefreshLeft } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import { listCustomers, listOutstandingMaterials, deliverOutstandingMaterial } from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../utils/tableQuery'

const { canUpdate } = useModulePermission('outstandingMaterials')

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const materials = ref([])
const page = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const sortBy = ref(null)
const sortDir = ref('desc')
const customers = ref([])
const filterStatus = ref('')
const filterCustomerId = ref(null)
const keyword = ref('')
const deliverDialogVisible = ref(false)
const currentMaterial = ref({})
const deliverQty = ref(0)

const stats = computed(() => {
  const list = materials.value
  return {
    total: totalRows.value,
    pending: list.filter((r) => r.status === 'pending').length,
    partial: list.filter((r) => r.status === 'partial').length,
    fulfilled: list.filter((r) => r.status === 'fulfilled').length,
  }
})

const displayedMaterials = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  if (!q) return materials.value
  return materials.value.filter((row) =>
    [row.po_number, row.customer_name, row.material_name].some((v) =>
      String(v || '')
        .toLowerCase()
        .includes(q),
    ),
  )
})

function customerOptionLabel(c) {
  const base = [c.code, c.name].filter(Boolean).join(' — ')
  return base || String(c.id)
}

function statusTagType(status) {
  const map = {
    pending: 'info',
    partial: 'warning',
    fulfilled: 'success',
  }
  return map[status] || ''
}

function statusLabel(status) {
  const map = {
    pending: t('outstandingMaterial.pending'),
    partial: t('outstandingMaterial.partial'),
    fulfilled: t('outstandingMaterial.fulfilled'),
  }
  return map[status] || status || '—'
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  try {
    const d = new Date(dateStr)
    return d.toLocaleDateString('id-ID', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

function formatQty(qty) {
  if (qty == null) return '—'
  return Number(qty).toLocaleString('id-ID', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

async function loadMaterials() {
  loading.value = true
  try {
    const params = buildPageParams({
      page: page.value,
      pageSize: pageSize.value,
      sortBy: sortBy.value,
      sortDir: sortDir.value,
      extra: {
        status: filterStatus.value || undefined,
        customer_id: filterCustomerId.value || undefined,
      },
    })
    const [raw, cust] = await Promise.all([listOutstandingMaterials(params), listCustomers()])
    const pageData = normalizePageResult(raw, { page: page.value, pageSize: pageSize.value })
    materials.value = pageData.items
    totalRows.value = pageData.total
    customers.value = cust
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
  loadMaterials()
}

function resetFilters() {
  filterStatus.value = ''
  filterCustomerId.value = null
  keyword.value = ''
  page.value = 1
  loadMaterials()
}

watch([filterStatus, filterCustomerId], () => {
  page.value = 1
  loadMaterials()
})
watch([page, pageSize], () => loadMaterials())

function openDeliverDialog(row) {
  currentMaterial.value = { ...row }
  deliverQty.value = Number(row.balance_qty) > 0 ? Number(row.balance_qty) : 0
  deliverDialogVisible.value = true
}

async function submitDelivery() {
  if (deliverQty.value <= 0) {
    ElMessage.warning(t('outstandingMaterial.deliverQtyMustPositive'))
    return
  }
  saving.value = true
  try {
    await deliverOutstandingMaterial(currentMaterial.value.id, deliverQty.value)
    ElMessage.success(t('common.saveSuccess'))
    deliverDialogVisible.value = false
    await loadMaterials()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

function goPo(row) {
  if (!row?.po_id) {
    ElMessage.warning(t('outstandingMaterial.poNotLinked'))
    return
  }
  router.push({ path: '/admin/po', query: { po_id: String(row.po_id) } })
}

function outstandingMaterialMoreItems(row) {
  if (!(canUpdate.value && row.status !== 'fulfilled')) return []
  return [{ command: 'markDelivered', label: t('outstandingMaterial.markDelivered') }]
}

onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.outstanding-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

@media (min-width: 768px) {
  .outstanding-stats {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .outstanding-filter-action-col {
    margin-left: auto;
  }
}

.outstanding-stat {
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  text-align: center;
}

.outstanding-stat__value {
  display: block;
  font-size: 1.375rem;
  font-weight: 700;
  line-height: 1.2;
  color: #0f172a;
}

.outstanding-stat__label {
  display: block;
  margin-top: 2px;
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #94a3b8;
}

.outstanding-stat--pending .outstanding-stat__value {
  color: #0369a1;
}

.outstanding-stat--partial .outstanding-stat__value {
  color: #b45309;
}

.outstanding-stat--fulfilled .outstanding-stat__value {
  color: #15803d;
}
</style>
