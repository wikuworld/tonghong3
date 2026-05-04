<template>
  <AdminSection :title="t('pages.marketingFlow.title')" :subtitle="t('pages.marketingFlow.subtitle')">
    <el-card shadow="never" class="mb-4">
      <template #header>
        <div class="flex items-center justify-between flex-wrap gap-2">
          <span class="font-semibold">{{ t('pages.marketingFlow.tabFlow') }}</span>
          <div class="flex items-center gap-2">
            <el-date-picker v-model="rekapDate" type="date" value-format="YYYY-MM-DD" size="small" class="w-32" @change="load" />
            <el-button type="warning" size="small" @click="pullCrToday">
              {{ t('pages.marketingFlow.pullCrToday') }}
            </el-button>
            <el-button type="success" size="small" :loading="poDailyXlsxLoading" @click="downloadDailyPoReportXlsx">
              {{ t('pages.marketingFlow.dailyPoReportXlsx') }}
            </el-button>
            <el-button type="primary" size="small" :icon="Download" @click="downloadRekap">{{ t('pages.marketingFlow.rekapToday') }}</el-button>
          </div>
        </div>
      </template>
      
      <div class="flex items-center gap-2 overflow-x-auto py-2">
        <template v-for="(s, i) in stageList" :key="s">
          <div v-if="i > 0" class="text-gray-400 flex-shrink-0 text-lg leading-none">›</div>
          <div class="flex flex-col items-center flex-shrink-0 cursor-pointer" @click="toggleStageFilter(s)">
            <el-tag :type="filterStage === s ? 'primary' : (i <= activeStep ? 'success' : 'info')" effect="light" size="small">
              {{ labelFor(s) }}
            </el-tag>
            <el-badge :value="stageCounts[s]" :max="99" :type="stageCounts[s] > 0 ? 'primary' : 'info'" class="mt-1" />
          </div>
        </template>
        <el-tag v-if="filterStage" type="info" effect="plain" size="small" class="cursor-pointer ml-2" @click="clearFilter">
          <el-icon class="cursor-pointer" @click.stop="clearFilter"><Close /></el-icon>
        </el-tag>
      </div>
    </el-card>

    <div>
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
        <el-table-column :label="t('pages.marketingFlow.materialDone')" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="Boolean(row.material_followup_done)"
              size="small"
              @change="(val) => toggleMaterialFollowUp(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.materialRemark')" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.material_followup_remark" class="text-xs">{{ row.material_followup_remark }}</span>
            <el-button v-else type="primary" link size="small" @click="openMaterialFollowUpDialog(row)">
              {{ t('pages.marketingFlow.addRemark') }}
            </el-button>
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
        <el-table-column :label="t('pages.marketingFlow.stuckReason')" min-width="200">
          <template #default="{ row }">
            <el-tag v-if="row.stuck_reason" type="warning" size="small" effect="plain">
              <el-icon class="mr-1"><Warning /></el-icon>
              {{ row.stuck_reason }}
            </el-tag>
            <el-tag v-else-if="isStageComplete(row)" type="success" size="small" effect="plain">
              <el-icon class="mr-1"><CircleCheck /></el-icon>
              {{ t('pages.marketingFlow.readyToAdvance') }}
            </el-tag>
            <span v-else class="text-gray-400 text-xs">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="80" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="default" link size="small" @click="goPo(row.id)">
              <el-icon><Document /></el-icon>
            </el-button>
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
        <el-button :icon="Close" @click="assignDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :icon="Check" :loading="assigning" @click="submitAssignment">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="materialFollowUpDialogVisible" :title="t('pages.marketingFlow.materialFollowUp')" width="500px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('common.poNo')">
          <el-input :model-value="selectedPoForMaterialFollowUp?.po_number" disabled />
        </el-form-item>
        <el-form-item :label="t('pages.marketingFlow.materialDone')">
          <el-switch v-model="materialFollowUpForm.done" />
        </el-form-item>
        <el-form-item :label="t('pages.marketingFlow.materialRemark')">
          <el-input v-model="materialFollowUpForm.remark" type="textarea" :rows="4" :placeholder="t('pages.marketingFlow.materialRemarkPlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="materialFollowUpDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :icon="Check" :loading="savingMaterialFollowUp" @click="saveMaterialFollowUp">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DArrowRight, Document, Download, Van, User, Search, Close, Check, Warning, CircleCheck } from '@element-plus/icons-vue'
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
  reportPoDailyMarketingXlsxPath,
  reportPoDailyRecapUrl,
  updatePo,
  updatePoDetail,
} from '../../api/client'
import { can } from '../../security/permissions'
import { formatNumber } from '../../utils/format'

const { t } = useI18n()
const canAdvance = can('po', 'advance')
const canEditPoDetail = can('po', 'update')
const router = useRouter()
const loading = ref(false)
const advancing = ref(null)
const rows = ref([])
const stageList = ref([])
const filterStage = ref(null)
const rekapDate = ref(new Date().toISOString().slice(0, 10))

const outstandingRows = ref([])
const outstandingLoading = ref(false)
const outstandingXlsxLoading = ref(false)
const poDailyXlsxLoading = ref(false)
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

const materialFollowUpDialogVisible = ref(false)
const materialFollowUpForm = reactive({ done: false, remark: '' })
const selectedPoForMaterialFollowUp = ref(null)
const savingMaterialFollowUp = ref(false)

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
  const s = rows.value[0]?.mkt_workflow_stage || 'input_system'
  const i = stageList.value.indexOf(s)
  return i >= 0 ? i : 0
})

const stageCounts = computed(() => {
  const counts = {}
  for (const s of stageList.value) {
    counts[s] = 0
  }
  for (const row of rows.value) {
    const s = row.mkt_workflow_stage
    if (s && counts[s] !== undefined) {
      counts[s]++
    }
  }
  return counts
})

function isStageComplete(row) {
  const s = row.mkt_workflow_stage
  if (!s) return false
  const idx = stageList.value.indexOf(s)
  return idx >= 0 && idx < stageList.value.length - 1 && !row.stuck_reason
}

function toggleStageFilter(stage) {
  if (filterStage.value === stage) {
    filterStage.value = null
  } else {
    filterStage.value = stage
  }
  load()
}

function clearFilter() {
  filterStage.value = null
  load()
}

async function load() {
  loading.value = true
  try {
    const params = {}
    if (filterStage.value) {
      params.mkt_workflow_stage = filterStage.value
    }
    if (rekapDate.value) {
      params.order_date = rekapDate.value
    }
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

function openMaterialFollowUpDialog(row) {
  selectedPoForMaterialFollowUp.value = row
  materialFollowUpForm.done = Boolean(row.material_followup_done)
  materialFollowUpForm.remark = row.material_followup_remark || ''
  materialFollowUpDialogVisible.value = true
}

async function toggleMaterialFollowUp(row, done) {
  try {
    await updatePo(row.id, {
      material_followup_done: done,
      material_followup_remark: row.material_followup_remark || undefined,
    })
    row.material_followup_done = done
    ElMessage.success(t('common.saveSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function saveMaterialFollowUp() {
  savingMaterialFollowUp.value = true
  try {
    await updatePo(selectedPoForMaterialFollowUp.value.id, {
      material_followup_done: materialFollowUpForm.done,
      material_followup_remark: materialFollowUpForm.remark.trim() || null,
    })
    selectedPoForMaterialFollowUp.value.material_followup_done = materialFollowUpForm.done
    selectedPoForMaterialFollowUp.value.material_followup_remark = materialFollowUpForm.remark.trim() || null
    ElMessage.success(t('common.saveSuccess'))
    materialFollowUpDialogVisible.value = false
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    savingMaterialFollowUp.value = false
  }
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

async function pullCrToday() {
  rekapDate.value = new Date().toISOString().slice(0, 10)
  await load()
  ElMessage.success(t('pages.marketingFlow.pullCrTodayDone'))
}

async function downloadDailyPoReportXlsx() {
  poDailyXlsxLoading.value = true
  try {
    const path = reportPoDailyMarketingXlsxPath({
      date_from: rekapDate.value,
      date_to: rekapDate.value,
      date_field: 'order',
    })
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
    a.download = `laporan_po_harian_${rekapDate.value || 'today'}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(t('pages.marketingFlow.dailyPoReportDone'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    poDailyXlsxLoading.value = false
  }
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
