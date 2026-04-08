<template>
  <AdminSection :title="t('pages.marketingFlow.title')" :subtitle="t('pages.marketingFlow.subtitle')">
    <template #actions>
      <template v-if="mainTab === 'flow'">
        <el-date-picker v-model="rekapDate" type="date" value-format="YYYY-MM-DD" class="w-[160px]" />
        <el-button type="primary" :icon="Download" @click="downloadRekap">{{ t('pages.marketingFlow.rekapToday') }}</el-button>
      </template>
      <template v-else-if="mainTab === 'outstanding'">
        <el-button :icon="Download" @click="downloadOutstanding">{{ t('pages.marketingFlow.outstandingDownloadCsv') }}</el-button>
        <el-button :loading="outstandingLoading" @click="loadOutstanding">{{ t('pages.marketingFlow.outstandingRefresh') }}</el-button>
      </template>
      <template v-else-if="mainTab === 'delivery'">
        <el-button :icon="Download" @click="downloadDelivery">{{ t('pages.marketingFlow.deliveryDownloadCsv') }}</el-button>
        <el-button :loading="deliveryLoading" @click="loadDelivery">{{ t('pages.marketingFlow.deliveryRefresh') }}</el-button>
      </template>
    </template>

    <el-tabs v-model="mainTab" class="marketing-tabs">
      <el-tab-pane :label="t('pages.marketingFlow.tabFlow')" name="flow">
        <el-steps :active="activeStep" finish-status="success" align-center class="mb-6">
          <el-step v-for="(s, i) in stageList" :key="s" :title="labelFor(s)" :description="String(i + 1)" />
        </el-steps>

        <div class="mb-4 flex flex-wrap items-end gap-3">
          <el-form-item :label="t('pages.marketingFlow.filterStage')" class="mb-0">
            <el-select v-model="filterStage" clearable class="w-[220px]" :placeholder="t('pages.marketingFlow.allStages')" @change="load">
              <el-option v-for="s in stageList" :key="s" :label="labelFor(s)" :value="s" />
            </el-select>
          </el-form-item>
          <el-button :loading="loading" @click="load">{{ t('common.search') }}</el-button>
        </div>

        <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table">
          <el-table-column type="index" width="50" align="center" />
          <el-table-column prop="po_number" :label="t('common.poNo')" min-width="140" />
          <el-table-column prop="mkt_workflow_stage" :label="t('pages.marketingFlow.stage')" min-width="160">
            <template #default="{ row }">
              <el-tag size="small">{{ labelFor(row.mkt_workflow_stage) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" :label="t('common.status')" width="110" />
          <el-table-column prop="order_date" :label="t('common.orderDate')" width="120" />
          <el-table-column :label="t('pages.marketingFlow.materialDone')" width="120" align="center">
            <template #default="{ row }">{{ row.material_followup_done ? '✓' : '—' }}</template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="200" fixed="right">
            <template #default="{ row }">
              <el-button v-if="canAdvance" type="primary" link size="small" :loading="advancing === row.id" @click="advance(row)">
                {{ t('pages.marketingFlow.advance') }}
              </el-button>
              <el-button link size="small" @click="goPo(row.id)">{{ t('pages.marketingFlow.openPo') }}</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-alert class="mt-4" type="info" :closable="false" show-icon>
          <template #title>{{ t('pages.marketingFlow.hintTitle') }}</template>
          <p class="text-sm">{{ t('pages.marketingFlow.hintBody') }}</p>
        </el-alert>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.marketingFlow.tabOutstanding')" name="outstanding">
        <p class="mb-3 text-sm text-gray-600 dark:text-gray-400">{{ t('pages.marketingFlow.outstandingSubtitle') }}</p>
        <div class="mb-3 flex flex-wrap items-end gap-3">
          <el-form-item :label="t('pages.marketingFlow.balanceFilter')" class="mb-0">
            <el-select v-model="balanceFilter" class="w-[min(100%,320px)]" @change="loadOutstanding">
              <el-option :label="t('pages.marketingFlow.balanceFilterAll')" value="all" />
              <el-option :label="t('pages.marketingFlow.balanceFilterExcludeZero')" value="exclude_zero" />
              <el-option :label="t('pages.marketingFlow.balanceFilterPositiveOnly')" value="positive_only" />
            </el-select>
          </el-form-item>
        </div>
        <el-table
          :data="outstandingRows"
          v-loading="outstandingLoading"
          border
          stripe
          size="small"
          class="admin-table outstanding-table"
          max-height="560"
          :empty-text="t('pages.marketingFlow.outstandingEmpty')"
        >
          <el-table-column type="index" width="48" fixed />
          <el-table-column prop="order_date" :label="t('common.orderDate')" width="112" />
          <el-table-column prop="thi_order" :label="t('pages.marketingFlow.colThiOrder')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="customer_name" :label="t('common.customerName')" min-width="140" show-overflow-tooltip />
          <el-table-column prop="brand" :label="t('pages.marketingFlow.colBrand')" width="100" />
          <el-table-column prop="order_type" :label="t('pages.marketingFlow.colOrderType')" width="100" />
          <el-table-column prop="no_po" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="material_name" :label="t('common.material')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="thickness" :label="t('common.thickness')" width="100" />
          <el-table-column prop="emboss" :label="t('common.emboss')" width="90" show-overflow-tooltip />
          <el-table-column prop="softness_type" :label="t('pages.marketingFlow.colSoftnessType')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="color" :label="t('common.color')" min-width="100" show-overflow-tooltip />
          <el-table-column prop="softness" :label="t('common.softness')" width="90" />
          <el-table-column prop="qty_sf" :label="t('pages.marketingFlow.colQtySf')" width="100" align="right" />
          <el-table-column prop="unit_price" :label="t('pages.marketingFlow.colUnitPrice')" width="96" align="right" />
          <el-table-column prop="color_reference" :label="t('common.colorReference')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="backing" :label="t('common.backing')" width="100" show-overflow-tooltip />
          <el-table-column prop="model" :label="t('common.model')" width="100" show-overflow-tooltip />
          <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="rtd_text" :label="t('pages.marketingFlow.colRtd')" width="100" show-overflow-tooltip />
          <el-table-column prop="line_etd" :label="t('pages.marketingFlow.colReplyEtd')" width="120" />
          <el-table-column prop="stock_wh_qty" :label="t('pages.marketingFlow.colStockWh')" width="100" align="right" />
          <el-table-column prop="balance_qty" :label="t('pages.marketingFlow.colBalance')" width="100" align="right" />
          <el-table-column prop="system_reference" :label="t('pages.marketingFlow.colSystemNo')" min-width="130" show-overflow-tooltip />
          <el-table-column prop="detail_remark" :label="t('common.remark')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="mkt_stage" :label="t('pages.marketingFlow.colMktStage')" min-width="140">
            <template #default="{ row }">
              <el-tag size="small">{{ labelFor(row.mkt_stage) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="goPo(row.po_id)">{{ t('pages.marketingFlow.openPo') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.marketingFlow.tabDelivery')" name="delivery">
        <p class="mb-3 text-sm text-gray-600 dark:text-gray-400">{{ t('pages.marketingFlow.deliverySubtitle') }}</p>
        <el-table
          :data="deliveryRows"
          v-loading="deliveryLoading"
          border
          stripe
          size="small"
          class="admin-table outstanding-table"
          max-height="560"
          :empty-text="t('pages.marketingFlow.deliveryEmpty')"
        >
          <el-table-column type="index" width="48" fixed />
          <el-table-column prop="surat_jalan_no" :label="t('pages.marketingFlow.colSuratJalan')" min-width="130" show-overflow-tooltip />
          <el-table-column prop="delivery_date" :label="t('pages.marketingFlow.colShipDate')" width="118" />
          <el-table-column prop="factory_name" :label="t('pages.marketingFlow.colFactoryName')" min-width="160" show-overflow-tooltip />
          <el-table-column prop="system_no" :label="t('pages.marketingFlow.colSystemNo')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="po_date" :label="t('common.orderDate')" width="112" />
          <el-table-column prop="po_number" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="lot_no" :label="t('pages.marketingFlow.colLotNo')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="thickness" :label="t('common.thickness')" width="100" />
          <el-table-column prop="color" :label="t('common.color')" min-width="100" show-overflow-tooltip />
          <el-table-column prop="material_type" :label="t('pages.marketingFlow.colMaterialType')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="material_name" :label="t('common.material')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="qty_po" :label="t('pages.marketingFlow.colQtyPo')" width="96" align="right" />
          <el-table-column prop="unit_price" :label="t('pages.marketingFlow.colUnitPrice')" width="96" align="right" />
          <el-table-column prop="qty_roll" :label="t('pages.marketingFlow.colQtyRoll')" width="72" align="right" />
          <el-table-column prop="qty_pcs" :label="t('pages.marketingFlow.colQtyPcs')" width="72" align="right" />
          <el-table-column prop="qty_sf" :label="t('pages.marketingFlow.colQtyShip')" width="96" align="right" />
          <el-table-column prop="weight" :label="t('pages.marketingFlow.colWeight')" width="88" align="right" />
          <el-table-column prop="color_std" :label="t('common.colorStandard')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="emboss" :label="t('common.emboss')" width="90" show-overflow-tooltip />
          <el-table-column prop="buyer" :label="t('common.buyer')" width="100" show-overflow-tooltip />
          <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="model" :label="t('common.model')" width="100" show-overflow-tooltip />
          <el-table-column prop="invoice_number" :label="t('common.invoiceNo')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="pi_no" :label="t('pages.marketingFlow.colPiNo')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="remark" :label="t('common.remark')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="delivery_status" :label="t('common.status')" width="100" />
          <el-table-column :label="t('common.actions')" width="130" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="goDelivery(row)">{{ t('pages.marketingFlow.openDelivery') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.marketingFlow.tabSpec')" name="spec">
        <p class="mb-4 text-sm leading-relaxed">{{ t('pages.marketingFlow.specIntro') }}</p>
        <el-collapse>
          <el-collapse-item v-for="(item, idx) in specItems" :key="idx" :title="item.title" :name="String(idx)">
            <p class="text-sm leading-relaxed text-gray-700 dark:text-gray-300">{{ t(item.body) }}</p>
          </el-collapse-item>
        </el-collapse>
      </el-tab-pane>
    </el-tabs>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  advanceMktWorkflow,
  listMarketingDeliveryLines,
  listMarketingOutstandingLines,
  listPo,
  listPoMktStages,
  marketingDeliveryCsvUrl,
  marketingOutstandingCsvUrl,
  reportPoDailyRecapUrl,
} from '../../api/client'
import { can } from '../../security/permissions'

const { t } = useI18n()
const canAdvance = can('po', 'advance')
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
const balanceFilter = ref('exclude_zero')

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
  return labels.value[stage] || stage || '—'
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
    ElMessage.error(e.message || 'Error')
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
    })
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    outstandingLoading.value = false
  }
}

async function loadDelivery() {
  deliveryLoading.value = true
  try {
    deliveryRows.value = await listMarketingDeliveryLines()
  } catch (e) {
    ElMessage.error(e.message || 'Error')
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
  await load()
})

async function advance(row) {
  advancing.value = row.id
  try {
    await advanceMktWorkflow(row.id)
    ElMessage.success(t('pages.marketingFlow.advanced'))
    await load()
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    advancing.value = null
  }
}

function goPo(id) {
  router.push({ path: '/admin/po', query: { highlight: String(id) } })
}

function goDelivery(row) {
  const kw = (row.surat_jalan_no && row.surat_jalan_no !== '—' ? row.surat_jalan_no : '') || String(row.delivery_id || '')
  router.push({ path: '/admin/delivery', query: kw ? { keyword: kw } : {} })
}

function downloadRekap() {
  window.open(reportPoDailyRecapUrl(rekapDate.value), '_blank')
}

function downloadOutstanding() {
  window.open(marketingOutstandingCsvUrl({ balance_filter: balanceFilter.value, computed_balance: true }), '_blank')
}

function downloadDelivery() {
  window.open(marketingDeliveryCsvUrl(), '_blank')
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
