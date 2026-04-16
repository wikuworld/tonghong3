<template>
  <AdminSection :title="t('pages.marketingFlow.title')" :subtitle="t('pages.marketingFlow.subtitle')">
    <template #actions>
      <el-select v-model="mainTab" class="w-40">
        <el-option label="Flow" value="flow" />
        <el-option label="Outstanding" value="outstanding" />
        <el-option label="Delivery" value="delivery" />
      </el-select>
    </template>

    <el-card shadow="never" class="mb-4" v-if="mainTab === 'flow'">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold">{{ t('pages.marketingFlow.tabFlow') }}</span>
          <el-date-picker v-model="rekapDate" type="date" value-format="YYYY-MM-DD" size="small" class="w-36" />
        </div>
      </template>
      <el-steps :active="activeStep" finish-status="success" align-center class="mb-4">
        <el-step v-for="(s, i) in stageList" :key="s" :title="labelFor(s)" />
      </el-steps>
      <div class="flex flex-wrap items-center gap-3">
        <el-select v-model="filterStage" clearable size="small" class="w-48" :placeholder="t('pages.marketingFlow.allStages')" @change="load">
          <el-option v-for="s in stageList" :key="s" :label="labelFor(s)" :value="s" />
        </el-select>
        <el-button size="small" @click="load">{{ t('common.search') }}</el-button>
        <el-button type="primary" size="small" :icon="Download" @click="downloadRekap">{{ t('pages.marketingFlow.rekapToday') }}</el-button>
      </div>
    </el-card>

    <el-card shadow="never" class="mb-4" v-else-if="mainTab === 'outstanding'">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold">{{ t('pages.marketingFlow.tabOutstanding') }}</span>
          <div class="flex gap-2">
            <el-button size="small" :loading="outstandingLoading" @click="loadOutstanding">{{ t('pages.marketingFlow.outstandingRefresh') }}</el-button>
            <el-button size="small" type="primary" :icon="Download" :loading="outstandingXlsxLoading" @click="downloadOutstandingXlsx">
              Excel
            </el-button>
          </div>
        </div>
      </template>
      <div class="flex flex-wrap items-end gap-3">
        <el-select v-model="balanceFilter" size="small" class="w-40" @change="loadOutstanding">
          <el-option :label="t('pages.marketingFlow.balanceFilterAll')" value="all" />
          <el-option :label="t('pages.marketingFlow.balanceFilterExcludeZero')" value="exclude_zero" />
          <el-option :label="t('pages.marketingFlow.balanceFilterPositiveOnly')" value="positive_only" />
        </el-select>
        <el-radio-group v-model="shipmentTab" size="small" @change="loadOutstanding">
          <el-radio-button label="all">{{ t('pages.marketingFlow.shipmentTabAll') }}</el-radio-button>
          <el-radio-button label="not_sent">{{ t('pages.marketingFlow.shipmentTabNotSent') }}</el-radio-button>
          <el-radio-button label="sent">{{ t('pages.marketingFlow.shipmentTabSent') }}</el-radio-button>
        </el-radio-group>
        <el-select v-model="outstandingViewMode" size="small" class="w-40">
          <el-option :label="t('pages.marketingFlow.viewModeAll')" value="all" />
          <el-option :label="t('pages.marketingFlow.viewModeWarehouse')" value="warehouse_qc" />
          <el-option :label="t('pages.marketingFlow.viewModeMktDelivery')" value="mkt_delivery" />
        </el-select>
        <el-input v-model="poSearch" size="small" clearable class="w-40" :placeholder="t('pages.marketingFlow.searchPoPlaceholder')" @keyup.enter="loadOutstanding" />
      </div>
    </el-card>

    <el-card shadow="never" class="mb-4" v-else-if="mainTab === 'delivery'">
      <template #header>
        <div class="flex items-center justify-between">
          <span class="font-semibold">{{ t('pages.marketingFlow.tabDelivery') }}</span>
          <el-button size="small" :loading="deliveryLoading" @click="loadDelivery">{{ t('pages.marketingFlow.deliveryRefresh') }}</el-button>
        </div>
      </template>
    </el-card>

    <div v-show="mainTab === 'flow'">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed">
        <el-table-column type="index" width="50" align="center" fixed="left" />
        <el-table-column prop="po_number" :label="t('common.poNo')" min-width="140" show-overflow-tooltip />
        <el-table-column :label="t('pages.marketingFlow.stage')" width="150">
          <template #default="{ row }">
            <el-tag size="small">{{ labelFor(row.mkt_workflow_stage) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('common.status')" width="100" />
        <el-table-column prop="order_date" :label="t('common.orderDate')" width="110" />
        <el-table-column :label="t('pages.marketingFlow.materialDone')" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.material_followup_done" type="success" size="small">✓</el-tag>
            <span v-else class="text-gray-400">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('ppicWorkflow.status')" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="ppicAssignments[row.id]" size="small" :type="ppicAssignments[row.id].status === 'completed' ? 'success' : ppicAssignments[row.id].status === 'in_progress' ? 'warning' : 'info'">
              {{ ppicStatusLabel(ppicAssignments[row.id].status) }}
            </el-tag>
            <span v-else class="text-gray-400 text-xs">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="120" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="warning" link size="small" :aria-label="t('ppicWorkflow.assignToPpic')" @click="openAssignDialog(row)">
              <el-icon><User /></el-icon>
            </el-button>
            <el-button v-if="canAdvance" type="primary" link size="small" :loading="advancing === row.id" @click="advance(row)">
              <el-icon><DArrowRight /></el-icon>
            </el-button>
            <el-button type="default" link size="small" @click="goPo(row.id)">
              <el-icon><Document /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-alert class="mt-4" type="info" :closable="false" show-icon>
        <template #title>{{ t('pages.marketingFlow.hintTitle') }}</template>
        <p class="text-sm">{{ t('pages.marketingFlow.hintBody') }}</p>
      </el-alert>
    </div>

    <div v-show="mainTab === 'outstanding'">
      <div class="mb-3 flex items-center gap-2">
        <el-button type="primary" plain size="small" :disabled="!outstandingSelection.length" @click="proposeScheduleFromSelection">
          {{ t('pages.marketingFlow.scheduleDraftButton') }} ({{ outstandingSelection.length }})
        </el-button>
      </div>
      <el-collapse class="mb-3">
        <el-collapse-item :title="t('pages.marketingFlow.filterColumnsTitle')" name="filters">
          <p class="mb-2 text-xs text-gray-500">{{ t('pages.marketingFlow.filterHint') }}</p>
          <div class="grid max-h-48 grid-cols-2 gap-2 overflow-y-auto md:grid-cols-4 lg:grid-cols-6">
            <div v-for="f in outstandingTextFilterFields" :key="f.key" class="flex min-w-0 flex-col gap-0.5">
              <span class="text-xs text-gray-600">{{ f.label }}</span>
              <el-input v-model="outstandingTextFilters[f.key]" size="small" clearable />
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
      <el-table
        ref="outstandingTableRef"
        :data="outstandingDisplayRows"
        v-loading="outstandingLoading"
        border
        stripe
        size="small"
        class="admin-table"
        max-height="480"
        :empty-text="t('pages.marketingFlow.outstandingEmpty')"
        show-summary
        :summary-method="outstandingSummary"
        @selection-change="onOutstandingSelectionChange"
      >
        <el-table-column type="selection" width="44" fixed />
        <el-table-column type="index" width="44" fixed />
        <el-table-column prop="order_date" :label="t('common.orderDate')" width="105" />
        <el-table-column prop="no_po" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="customer_name" :label="t('common.customerName')" min-width="130" show-overflow-tooltip />
        <el-table-column prop="brand" :label="t('pages.marketingFlow.colBrand')" width="90" />
        <el-table-column prop="order_type" :label="t('pages.marketingFlow.colOrderType')" width="90" />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="thickness" :label="t('common.thickness')" width="90" />
        <el-table-column prop="color" :label="t('common.color')" min-width="90" show-overflow-tooltip />
        <el-table-column :label="t('pages.marketingFlow.colQtySf')" width="90" align="right">
          <template #default="{ row }">{{ formatNumber(row.qty_sf, 2) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.colUnitPrice')" width="85" align="right">
          <template #default="{ row }">{{ formatNumber(row.unit_price, 2) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.colBalance')" width="90" align="right">
          <template #default="{ row }">{{ formatNumber(row.balance_qty, 2) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.colDeliveredQty')" width="90" align="right">
          <template #default="{ row }">{{ formatNumber(row.delivered_qty, 2) }}</template>
        </el-table-column>
        <el-table-column prop="production_status" :label="t('pages.marketingFlow.colProductionStatus')" width="100" show-overflow-tooltip />
        <el-table-column prop="remark_marketing" :label="t('pages.marketingFlow.colRemarkMarketing')" min-width="140">
          <template #default="{ row }">
            <el-input
              v-model="row.remark_marketing"
              type="textarea"
              :autosize="{ minRows: 1, maxRows: 2 }"
              size="small"
              :disabled="!canEditPoDetail || savingRemarkId === row.po_detail_id"
              @change="saveMarketingRemark(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="mkt_stage" :label="t('pages.marketingFlow.colMktStage')" width="130">
          <template #default="{ row }">
            <el-tag size="small">{{ labelFor(row.mkt_stage) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="70" fixed="right" align="center">
          <template #default="{ row }">
            <el-button :icon="Document" link type="primary" size="small" @click="goPo(row.po_id)" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div v-show="mainTab === 'delivery'">
      <el-table
        :data="deliveryRows"
        v-loading="deliveryLoading"
        border
        stripe
        size="small"
        class="admin-table"
        table-layout="fixed"
        max-height="520"
        :empty-text="t('pages.marketingFlow.deliveryEmpty')"
      >
        <el-table-column type="index" width="50" fixed="left" />
        <el-table-column prop="surat_jalan_no" :label="t('pages.marketingFlow.colSuratJalan')" min-width="130" show-overflow-tooltip />
        <el-table-column prop="delivery_date" :label="t('pages.marketingFlow.colShipDate')" width="100" />
        <el-table-column prop="factory_name" :label="t('pages.marketingFlow.colFactoryName')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="po_number" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="buyer" :label="t('common.buyer')" width="90" show-overflow-tooltip />
        <el-table-column prop="lot_no" :label="t('pages.marketingFlow.colLotNo')" width="100" show-overflow-tooltip />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="120" show-overflow-tooltip />
        <el-table-column :label="t('pages.marketingFlow.colQtyShip')" width="80" align="right">
          <template #default="{ row }">{{ formatNumber(row.qty_sf, 2) }}</template>
        </el-table-column>
        <el-table-column prop="qty_roll" :label="t('pages.marketingFlow.colQtyRoll')" width="60" align="right" />
        <el-table-column prop="qty_pcs" :label="t('pages.marketingFlow.colQtyPcs')" width="60" align="right" />
        <el-table-column :label="t('pages.delivery.columns.nw')" width="70" align="right">
          <template #default="{ row }">{{ formatNumber(row.net_weight, 2) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.delivery.columns.amount')" width="90" align="right">
          <template #default="{ row }">{{ formatNumber(row.amount, 0) }}</template>
        </el-table-column>
        <el-table-column prop="delivery_status" :label="t('common.status')" width="90">
          <template #default="{ row }">
            <el-tag size="small">{{ row.delivery_status || '—' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="70" fixed="right" align="center">
          <template #default="{ row }">
            <el-button :icon="Van" link type="primary" size="small" @click="goDelivery(row)" />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="assignDialogVisible" :title="t('ppicWorkflow.assignToPpic')" width="600px" destroy-on-close align-center>
      <el-form label-width="120px">
        <el-form-item :label="t('common.poNo')">
          <el-input :model-value="selectedPoForAssignment?.po_number" disabled />
        </el-form-item>
        <el-form-item :label="t('ppicWorkflow.ppicUser')" required>
          <el-select v-model="assignForm.ppic_user_id" class="w-full" clearable :placeholder="t('ppicWorkflow.ppicUser')">
            <el-option v-for="u in ppicUsers" :key="u.id" :label="u.username" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('ppicWorkflow.notes')">
          <el-input v-model="assignForm.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="assigning" @click="submitAssignment">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DArrowRight, Document, Download, Van, User } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  advanceMktWorkflow,
  assignPoToPpic,
  getPoPpicAssignment,
  listMarketingDeliveryLines,
  listMarketingOutstandingLines,
  listPo,
  listPoMktStages,
  listPpicUsers,
  marketingDeliveryCsvUrl,
  marketingOutstandingCsvUrl,
  marketingOutstandingXlsxPath,
  reportPoDailyRecapUrl,
  updatePoDetail,
} from '../../api/client'
import { can } from '../../security/permissions'
import { formatNumber } from '../../utils/format'

const { t } = useI18n()
const canAdvance = can('po', 'advance')
const canEditPoDetail = can('po', 'update')
const router = useRouter()
const mainTab = ref('flow')
const loading = ref(false)
const advancing = ref(null)
const rows = ref([])
const stageList = ref([])
const filterStage = ref(null)
const rekapDate = ref(new Date().toISOString().slice(0, 10))

const outstandingRows = ref([])
const outstandingLoading = ref(false)
const outstandingXlsxLoading = ref(false)
const balanceFilter = ref('exclude_zero')
const shipmentTab = ref('all')
const poSearch = ref('')
const outstandingViewMode = ref('all')
const outstandingTableRef = ref(null)
const outstandingSelection = ref([])
const savingRemarkId = ref(null)

const ppicUsers = ref([])
const ppicAssignments = ref({})
const assignDialogVisible = ref(false)
const assignForm = ref({ ppic_user_id: null, notes: '' })
const selectedPoForAssignment = ref(null)
const assigning = ref(false)

const OUTSTANDING_TEXT_FILTER_KEYS = [
  'order_date',
  'thi_order',
  'customer_name',
  'brand',
  'order_type',
  'no_po',
  'material_name',
  'thickness',
  'emboss',
  'softness_type',
  'color',
  'softness',
  'qty_sf',
  'unit_price',
  'color_reference',
  'backing',
  'style_article',
  'rtd_text',
  'line_etd',
  'stock_wh_qty',
  'balance_qty',
  'delivered_qty',
  'system_reference',
  'production_status',
  'remark_system',
  'remark_marketing',
  'detail_remark',
  'mkt_stage',
  'delivery_1_qty',
  'delivery_1_date',
  'delivery_2_qty',
  'delivery_2_date',
  'delivery_3_qty',
  'delivery_3_date',
  'delivery_4_qty',
  'delivery_4_date',
  'delivery_5_qty',
  'delivery_5_date',
  'delivery_6_qty',
  'delivery_6_date',
]

const outstandingTextFilters = reactive(
  Object.fromEntries(OUTSTANDING_TEXT_FILTER_KEYS.map((k) => [k, ''])),
)

const outstandingTextFilterFields = computed(() => {
  const map = {
    order_date: 'common.orderDate',
    thi_order: 'pages.marketingFlow.colThiOrder',
    customer_name: 'common.customerName',
    brand: 'pages.marketingFlow.colBrand',
    order_type: 'pages.marketingFlow.colOrderType',
    no_po: 'common.poNo',
    material_name: 'common.material',
    thickness: 'common.thickness',
    emboss: 'common.emboss',
    softness_type: 'pages.marketingFlow.colSoftnessType',
    color: 'common.color',
    softness: 'common.softness',
    qty_sf: 'pages.marketingFlow.colQtySf',
    unit_price: 'pages.marketingFlow.colUnitPrice',
    color_reference: 'common.colorReference',
    backing: 'common.backing',
    style_article: 'common.styleArticle',
    rtd_text: 'pages.marketingFlow.colRtd',
    line_etd: 'pages.marketingFlow.colReplyEtd',
    stock_wh_qty: 'pages.marketingFlow.colStockWh',
    balance_qty: 'pages.marketingFlow.colBalance',
    delivered_qty: 'pages.marketingFlow.colDeliveredQty',
    system_reference: 'pages.marketingFlow.colSystemNo',
    production_status: 'pages.marketingFlow.colProductionStatus',
    remark_system: 'pages.marketingFlow.colRemarkSystem',
    remark_marketing: 'pages.marketingFlow.colRemarkMarketing',
    detail_remark: 'pages.marketingFlow.colPoLineRemark',
    mkt_stage: 'pages.marketingFlow.colMktStage',
    delivery_1_qty: 'pages.marketingFlow.filterDelivery1Qty',
    delivery_1_date: 'pages.marketingFlow.filterDelivery1Date',
    delivery_2_qty: 'pages.marketingFlow.filterDelivery2Qty',
    delivery_2_date: 'pages.marketingFlow.filterDelivery2Date',
    delivery_3_qty: 'pages.marketingFlow.filterDelivery3Qty',
    delivery_3_date: 'pages.marketingFlow.filterDelivery3Date',
    delivery_4_qty: 'pages.marketingFlow.filterDelivery4Qty',
    delivery_4_date: 'pages.marketingFlow.filterDelivery4Date',
    delivery_5_qty: 'pages.marketingFlow.filterDelivery5Qty',
    delivery_5_date: 'pages.marketingFlow.filterDelivery5Date',
    delivery_6_qty: 'pages.marketingFlow.filterDelivery6Qty',
    delivery_6_date: 'pages.marketingFlow.filterDelivery6Date',
  }
  return OUTSTANDING_TEXT_FILTER_KEYS.map((key) => ({
    key,
    label: t(map[key] || key),
  }))
})

function parseOutstandingBalance(row) {
  const n = parseFloat(String(row.balance_qty ?? '').replace(',', '.'))
  return Number.isFinite(n) ? n : 0
}

function outstandingHasSchedule(row) {
  for (let i = 1; i <= 6; i += 1) {
    const q = row[`delivery_${i}_qty`]
    const d = row[`delivery_${i}_date`]
    if ((q != null && String(q).trim() !== '') || (d != null && String(d).trim() !== '')) return true
  }
  return false
}

function isOutstandingProdFinished(st) {
  const s = String(st || '').toLowerCase()
  return ['done', 'completed', 'packed', 'released', 'finished'].includes(s)
}

function outstandingRowTextMatches(row, key, needle) {
  if (!needle || !String(needle).trim()) return true
  const q = String(needle).trim().toLowerCase()
  return String(row[key] ?? '').toLowerCase().includes(q)
}

const outstandingDisplayRows = computed(() => {
  let list = outstandingRows.value
  if (outstandingViewMode.value === 'warehouse_qc') {
    list = list.filter(
      (r) =>
        parseOutstandingBalance(r) > 0 &&
        outstandingHasSchedule(r) &&
        !isOutstandingProdFinished(r.production_status),
    )
  } else if (outstandingViewMode.value === 'mkt_delivery') {
    list = list.filter((r) => parseOutstandingBalance(r) > 0 && isOutstandingProdFinished(r.production_status))
  }
  for (const key of OUTSTANDING_TEXT_FILTER_KEYS) {
    const needle = outstandingTextFilters[key]
    if (!needle || !String(needle).trim()) continue
    list = list.filter((r) => outstandingRowTextMatches(r, key, needle))
  }
  return list
})

function outstandingSummary({ columns, data }) {
  return columns.map((col) => {
    if (col.type === 'selection') return ''
    if (col.type === 'index') return t('pages.marketingFlow.summaryLabel')
    const prop = col.property
    if (prop && ['qty_sf', 'stock_wh_qty', 'balance_qty', 'delivered_qty'].includes(prop)) {
      let total = 0
      for (const row of data) {
        const n = parseFloat(String(row[prop] ?? '').replace(',', '.'))
        if (Number.isFinite(n)) total += n
      }
      return total ? String(total) : ''
    }
    return ''
  })
}

function onOutstandingSelectionChange(sel) {
  outstandingSelection.value = sel
}

function proposeScheduleFromSelection() {
  const sel = outstandingSelection.value
  if (!sel.length) {
    ElMessage.warning(t('pages.marketingFlow.selectRowsFirst'))
    return
  }
  ElMessage.info(t('pages.marketingFlow.scheduleDraftHint', { n: sel.length }))
}

async function saveMarketingRemark(row) {
  if (!canEditPoDetail) return
  savingRemarkId.value = row.po_detail_id
  try {
    await updatePoDetail(row.po_detail_id, { marketing_outstanding_remark: row.remark_marketing || null })
    ElMessage.success(t('pages.marketingFlow.remarkSaved'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    savingRemarkId.value = null
  }
}

async function downloadOutstandingXlsx() {
  outstandingXlsxLoading.value = true
  try {
    const suffix = marketingOutstandingXlsxPath({
      balance_filter: balanceFilter.value,
      computed_balance: true,
      po_q: poSearch.value,
      shipment_status: shipmentTab.value,
    })
    const path = `/api/v1${suffix}`
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null
    const r = await fetch(path, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (!r.ok) {
      const text = await r.text()
      throw new Error(text || r.statusText)
    }
    const blob = await r.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'marketing_outstanding.xlsx'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(t('pages.marketingFlow.outstandingXlsxOk'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingXlsxLoading.value = false
  }
}

const deliveryRows = ref([])
const deliveryLoading = ref(false)

const specItems = computed(() => [
  { title: t('pages.marketingFlow.collapseSop'), body: 'pages.marketingFlow.specSop' },
  { title: t('pages.marketingFlow.collapseInputPo'), body: 'pages.marketingFlow.specInputPo' },
  { title: t('pages.marketingFlow.collapseDaily'), body: 'pages.marketingFlow.specDaily' },
  { title: t('pages.marketingFlow.collapseOutstanding'), body: 'pages.marketingFlow.specOutstandingSheet' },
  { title: t('pages.marketingFlow.collapseInvplSj'), body: 'pages.marketingFlow.specInvplSj' },
  { title: t('pages.marketingFlow.collapseDelivery'), body: 'pages.marketingFlow.specDelivery' },
  { title: t('pages.marketingFlow.collapseCustomer'), body: 'pages.marketingFlow.specCustomer' },
  { title: t('pages.marketingFlow.collapseInvoice'), body: 'pages.marketingFlow.specInvoice' },
])

const labels = computed(() => ({
  input_system: t('mktStage.input_system'),
  rekap_printed: t('mktStage.rekap_printed'),
  with_ppic: t('mktStage.with_ppic'),
  back_to_mkt: t('mktStage.back_to_mkt'),
  in_outstanding: t('mktStage.in_outstanding'),
  material_followup: t('mktStage.material_followup'),
  delivery_arranged: t('mktStage.delivery_arranged'),
  sj_invpl: t('mktStage.sj_invpl'),
  invoice_billing: t('mktStage.invoice_billing'),
}))

function labelFor(stage) {
  return labels.value[stage] || stage || t('common.emptyValue')
}

const activeStep = computed(() => {
  const s = filterStage.value || rows.value[0]?.mkt_workflow_stage || 'input_system'
  const i = stageList.value.indexOf(s)
  return i >= 0 ? i : 0
})

async function load() {
  loading.value = true
  try {
    const params = filterStage.value ? { mkt_workflow_stage: filterStage.value } : {}
    rows.value = await listPo(params)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

async function loadOutstanding() {
  outstandingLoading.value = true
  try {
    outstandingRows.value = await listMarketingOutstandingLines({
      balance_filter: balanceFilter.value,
      computed_balance: true,
      po_q: poSearch.value,
      shipment_status: shipmentTab.value,
    })
    outstandingSelection.value = []
    outstandingTableRef.value?.clearSelection?.()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingLoading.value = false
  }
}

async function loadDelivery() {
  deliveryLoading.value = true
  try {
    const linesResp = await listMarketingDeliveryLines()
    const lines = Array.isArray(linesResp) ? linesResp : (linesResp?.data || [])
    deliveryRows.value = lines.map((r) => ({
      ...r,
      delivery_date: r.delivery_date ? String(r.delivery_date).slice(0, 10) : '',
      po_date: r.po_date ? String(r.po_date).slice(0, 10) : '',
    }))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    deliveryLoading.value = false
  }
}

watch(mainTab, (tab) => {
  if (tab === 'outstanding') loadOutstanding()
  if (tab === 'delivery') loadDelivery()
})

onMounted(async () => {
  try {
    const data = await listPoMktStages()
    stageList.value = data.stages || []
  } catch {
    stageList.value = []
  }
  await Promise.all([
    load(),
    loadPpicUsers(),
    loadAssignments(),
  ])
})

async function loadPpicUsers() {
  try {
    ppicUsers.value = await listPpicUsers()
  } catch {
    ppicUsers.value = []
  }
}

async function loadAssignments() {
  try {
    const data = await getPpicDashboard()
    const map = {}
    for (const a of data) {
      map[a.po_id] = a
    }
    ppicAssignments.value = map
  } catch {
    ppicAssignments.value = {}
  }
}

function openAssignDialog(row) {
  selectedPoForAssignment.value = row
  assignForm.value = { ppic_user_id: null, notes: '' }
  assignDialogVisible.value = true
}

async function submitAssignment() {
  if (!assignForm.value.ppic_user_id) {
    ElMessage.warning(t('ppicWorkflow.ppicUser') + ' ' + t('common.required'))
    return
  }
  assigning.value = true
  try {
    await assignPoToPpic(selectedPoForAssignment.value.id, {
      ppic_user_id: assignForm.value.ppic_user_id,
      notes: assignForm.value.notes || null,
    })
    ElMessage.success(t('common.saveSuccess'))
    assignDialogVisible.value = false
    await loadAssignments()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    assigning.value = false
  }
}

function ppicStatusLabel(status) {
  const labels = {
    pending: t('ppicWorkflow.pending'),
    in_progress: t('ppicWorkflow.inProgress'),
    completed: t('ppicWorkflow.completed'),
  }
  return labels[status] || status || '—'
}

async function advance(row) {
  advancing.value = row.id
  try {
    await advanceMktWorkflow(row.id)
    ElMessage.success(t('pages.marketingFlow.advanced'))
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    advancing.value = null
  }
}

function goPo(id) {
  router.push({ path: '/admin/po', query: { highlight: String(id) } })
}

function goDelivery(row) {
  const kw = (row.surat_jalan_no && row.surat_jalan_no !== t('common.emptyValue') ? row.surat_jalan_no : '') || String(row.delivery_id || '')
  router.push({ path: '/admin/delivery', query: kw ? { keyword: kw } : {} })
}

function downloadRekap() {
  const path = reportPoDailyRecapUrl(rekapDate.value)
  window.open(path.startsWith('/') ? `/api/v1${path}` : path, '_blank')
}

function downloadOutstanding() {
  const suffix = marketingOutstandingCsvUrl({
    balance_filter: balanceFilter.value,
    computed_balance: true,
    po_q: poSearch.value,
    shipment_status: shipmentTab.value,
  })
  window.open(`/api/v1${suffix}`, '_blank')
}

function downloadDelivery() {
  const suffix = marketingDeliveryCsvUrl()
  window.open(`/api/v1${suffix}`, '_blank')
}
</script>

<style scoped>
.admin-table {
  width: 100%;
}
.outstanding-table {
  width: 100%;
}
.marketing-tabs :deep(.el-tabs__content) {
  padding-top: 0.5rem;
}
</style>
