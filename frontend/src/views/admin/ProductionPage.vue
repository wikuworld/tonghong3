<template>
  <AdminSection :title="t('pages.production.title')" :subtitle="t('pages.production.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.production.searchPlaceholder')"
        clearable
        class="production-toolbar-search"
      />
    </template>

    <el-alert class="mb-3" type="info" :closable="false" show-icon>
      <template #title>
        <span>{{ t('pages.production.bookHint') }}</span>
        <router-link class="ml-2 text-primary underline" to="/admin/mrp/rencana-produksi">
          {{ t('pages.production.openMrpRencana') }}
        </router-link>
      </template>
    </el-alert>

    <div class="filter-panel mb-4">
      <p class="filter-panel__title">{{ t('common.filter') }}</p>
      <el-form class="filter-form" label-position="top">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item :label="t('common.status')">
              <el-select v-model="filterStatus" clearable class="w-full" :placeholder="t('common.status')">
                <el-option :label="t('status.planned')" value="planned" />
                <el-option :label="t('status.in_progress')" value="in_progress" />
                <el-option :label="t('status.done')" value="done" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item :label="t('pages.production.filterMrpOnly')">
              <el-switch v-model="filterMrpOnly" />
            </el-form-item>
            <el-form-item label="&nbsp;">
              <el-button class="w-full" @click="resetFilter">{{ t('common.reset') }}</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <el-table
      :data="filteredRows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="fixed"
      :empty-text="t('pages.production.tableEmpty')"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="production_number" :label="t('common.productionNo')" min-width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.production_number }}</span>
          <el-tag v-if="isMrpBook(row)" size="small" type="warning" class="ml-1">{{ t('pages.production.mrpBadge') }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="po_number_disp" :label="t('common.poNo')" min-width="140" show-overflow-tooltip />
      <el-table-column prop="customer_name" :label="t('common.customer')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="buyer_disp" :label="t('common.buyer')" min-width="110" show-overflow-tooltip />
      <el-table-column prop="etd_disp" :label="t('common.etd')" min-width="110" align="center" />
      <el-table-column prop="start_date" :label="t('common.startDate')" min-width="110" align="center" />
      <el-table-column prop="end_date" :label="t('common.endDate')" min-width="110" align="center" />
      <el-table-column prop="created_at_disp" :label="t('pages.production.fieldCreatedAt')" min-width="150" align="center" />
      <el-table-column prop="status" :label="t('common.status')" min-width="110" align="center">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">{{ productionStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="80" align="center" fixed="right">
        <template #default="{ row }">
          <el-tooltip :content="t('common.detail')" placement="top">
            <el-button :icon="View" link type="primary" :aria-label="t('common.detail')" @click="openDetail(row)" />
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="detailVisible"
      :title="t('pages.production.dialogDetail')"
      width="820px"
      destroy-on-close
      align-center
      class="production-dialog"
      @closed="onDetailClosed"
    >
      <div v-loading="detailLoading" class="min-h-[120px]">
        <template v-if="detailRow">
          <el-divider content-position="left">{{ t('pages.production.sectionPo') }}</el-divider>
          <el-descriptions :column="2" border size="small" class="production-descriptions mb-4">
            <el-descriptions-item :label="t('common.productionNo')" :span="1">
              {{ detailRow.production_number || t('common.emptyValue') }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.production.fieldCreatedAt')" :span="1">
              {{ detailRow.created_at_disp || t('common.emptyValue') }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.poNo')" :span="1">
              {{ detailRow.po_number_disp || t('common.emptyValue') }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.production.fieldPoStatus')" :span="1">
              <el-tag v-if="detailRow.po_status" size="small" type="info">{{ poStatusLabel(detailRow.po_status) }}</el-tag>
              <span v-else>{{ t('common.emptyValue') }}</span>
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.customer')" :span="1">
              {{ detailRow.customer_name || t('common.emptyValue') }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.buyer')" :span="1">
              {{ detailRow.buyer_disp || t('common.emptyValue') }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.etd')" :span="1">{{ detailRow.etd_disp || t('common.emptyValue') }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.orderDate')" :span="1">{{ detailRow.order_date_disp || t('common.emptyValue') }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.startDate')" :span="1">{{ detailRow.start_date || t('common.emptyValue') }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.endDate')" :span="1">{{ detailRow.end_date || t('common.emptyValue') }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.status')" :span="2">
              <el-tag :type="statusTagType(detailRow.status)" size="small">{{ productionStatusLabel(detailRow.status) }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <el-divider content-position="left">{{ t('pages.production.sectionLines') }}</el-divider>
          <el-table
            v-if="detailLines.length"
            :data="detailLines"
            border
            stripe
            size="small"
            max-height="320"
            class="admin-table"
          >
            <el-table-column prop="po_detail_id" :label="t('pages.production.poDetailRef')" width="110" align="center" />
            <el-table-column prop="qty_planned" :label="t('pages.production.qtyPlanned')" width="110" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_planned) }}</template>
            </el-table-column>
            <el-table-column prop="qty_actual" :label="t('pages.production.qtyActual')" width="110" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_actual) }}</template>
            </el-table-column>
            <el-table-column prop="lot_number" :label="t('pages.production.lotNumber')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="batch_number" :label="t('pages.production.batchNumber')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="status" :label="t('pages.production.lineStatus')" width="110" align="center">
              <template #default="{ row }">
                <el-tag size="small">{{ lineStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="is_over_production" :label="t('pages.production.overProduction')" width="100" align="center">
              <template #default="{ row }">
                {{ row.is_over_production ? t('common.yes') : t('common.no') }}
              </template>
            </el-table-column>
          </el-table>
          <p v-else class="text-sm text-slate-500">{{ t('pages.production.linesEmpty') }}</p>
        </template>
      </div>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('pages.production.closeDetail') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  getProduction,
  listPo,
  listProduction,
  listProductionDetails,
} from '../../api/client'

const { t, te } = useI18n()
const route = useRoute()

const loading = ref(false)
const keyword = ref('')
const filterStatus = ref('')
const filterMrpOnly = ref(false)
const rows = ref([])
const poList = ref([])

const poById = computed(() => {
  const m = {}
  for (const p of poList.value) m[p.id] = p
  return m
})

function sliceDate(v) {
  if (v == null || v === '') return ''
  return String(v).slice(0, 10)
}

function formatCreatedAt(v) {
  if (v == null || v === '') return t('common.emptyValue')
  const s = String(v).replace('T', ' ')
  return s.length > 19 ? s.slice(0, 19) : s
}

function enrichProduction(r) {
  const po = r.po_id ? poById.value[r.po_id] : null
  return {
    ...r,
    po_number_disp: po?.po_number || (r.po_id ? `PO #${r.po_id}` : t('common.emptyValue')),
    customer_name: po?.customer_name_snapshot || po?.customer_code || t('common.emptyValue'),
    buyer_disp: po?.buyer || t('common.emptyValue'),
    etd_disp: sliceDate(po?.etd) || t('common.emptyValue'),
    order_date_disp: sliceDate(po?.order_date) || t('common.emptyValue'),
    po_status: po?.status || null,
    start_date: sliceDate(r.start_date),
    end_date: sliceDate(r.end_date),
    created_at_disp: formatCreatedAt(r.created_at),
  }
}

function productionStatusLabel(status) {
  if (status && te(`status.${status}`)) return t(`status.${status}`)
  return status || t('common.emptyValue')
}

function poStatusLabel(status) {
  if (status && te(`status.${status}`)) return t(`status.${status}`)
  return status || t('common.emptyValue')
}

function lineStatusLabel(status) {
  if (status && te(`status.${status}`)) return t(`status.${status}`)
  return status || t('common.emptyValue')
}

function formatQty(v) {
  if (v == null || v === '') return t('common.emptyValue')
  const n = Number(v)
  return Number.isFinite(n) ? String(n) : String(v)
}

async function load() {
  loading.value = true
  try {
    const [pr, po] = await Promise.all([listProduction(), listPo()])
    poList.value = po
    rows.value = pr.map((r) => enrichProduction(r))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await load()
  const productionIdRaw = route.query.production_id
  const productionId = Number(productionIdRaw)
  if (!Number.isNaN(productionId) && productionId > 0) {
    const target = rows.value.find((r) => Number(r.id) === productionId)
    if (target) await openDetail(target)
  }
})

const filteredRows = computed(() => {
  return rows.value.filter((row) => {
    const statusMatch = !filterStatus.value || row.status === filterStatus.value
    const q = keyword.value.trim().toLowerCase()
    const keywordMatch =
      !q ||
      [row.production_number, row.po_number_disp, row.customer_name, row.buyer_disp]
        .filter(Boolean)
        .join(' ')
        .toLowerCase()
        .includes(q)
    const mrpMatch = !filterMrpOnly.value || isMrpBook(row)
    return statusMatch && keywordMatch && mrpMatch
  })
})

function isMrpBook(row) {
  return String(row?.production_number || '').startsWith('MRP-')
}

function statusTagType(status) {
  if (status === 'in_progress') return 'warning'
  if (status === 'done') return 'success'
  return 'info'
}

const resetFilter = () => {
  filterStatus.value = ''
  keyword.value = ''
  filterMrpOnly.value = false
}

const detailVisible = ref(false)
const detailLoading = ref(false)
const detailRow = ref(null)
const detailLines = ref([])

function onDetailClosed() {
  detailRow.value = null
  detailLines.value = []
}

async function openDetail(row) {
  detailVisible.value = true
  detailLoading.value = true
  detailRow.value = null
  detailLines.value = []
  try {
    const full = await getProduction(row.id)
    detailRow.value = enrichProduction(full)
    detailLines.value = await listProductionDetails(row.id)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    detailVisible.value = false
  } finally {
    detailLoading.value = false
  }
}
</script>

<style scoped>
.production-descriptions :deep(.el-descriptions__label) {
  width: 140px;
  font-weight: 600;
  color: text-slate-600;
}

.w-full {
  width: 100%;
}

.production-toolbar-search {
  width: 240px;
  max-width: 100%;
  margin-right: 8px;
  vertical-align: middle;
}
</style>
