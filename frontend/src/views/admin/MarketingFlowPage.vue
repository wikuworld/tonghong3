<template>
  <AdminSection :title="t('pages.marketingFlow.title')" :subtitle="t('pages.marketingFlow.subtitle')">
    <template #actions>
      <template v-if="mainTab === 'flow'">
        <el-date-picker v-model="rekapDate" type="date" value-format="YYYY-MM-DD" class="w-[160px]" />
        <el-button type="primary" :icon="Download" @click="downloadRekap">{{ t('pages.marketingFlow.rekapToday') }}</el-button>
      </template>
      <template v-else-if="mainTab === 'outstanding'">
        <el-button :icon="Download" @click="downloadOutstanding">{{ t('pages.marketingFlow.outstandingDownloadCsv') }}</el-button>
        <el-button type="primary" :icon="Download" :loading="outstandingXlsxLoading" @click="downloadOutstandingXlsx">
          {{ t('pages.marketingFlow.outstandingDownloadXlsx') }}
        </el-button>
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
            <template #default="{ row }">{{ row.material_followup_done ? '✓' : t('common.emptyValue') }}</template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="112" fixed="right" align="center">
            <template #default="{ row }">
              <div class="flex flex-wrap items-center justify-center gap-0">
                <el-tooltip v-if="canAdvance" :content="t('pages.marketingFlow.advance')" placement="top">
                  <el-button
                    :icon="DArrowRight"
                    type="primary"
                    link
                    size="small"
                    :loading="advancing === row.id"
                    :aria-label="t('pages.marketingFlow.advance')"
                    @click="advance(row)"
                  />
                </el-tooltip>
                <el-tooltip :content="t('pages.marketingFlow.openPo')" placement="top">
                  <el-button
                    :icon="Document"
                    link
                    size="small"
                    :aria-label="t('pages.marketingFlow.openPo')"
                    @click="goPo(row.id)"
                  />
                </el-tooltip>
              </div>
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
          <el-form-item :label="t('pages.marketingFlow.shipmentFilter')" class="mb-0">
            <el-radio-group v-model="shipmentTab" size="small" @change="loadOutstanding">
              <el-radio-button label="all">{{ t('pages.marketingFlow.shipmentTabAll') }}</el-radio-button>
              <el-radio-button label="not_sent">{{ t('pages.marketingFlow.shipmentTabNotSent') }}</el-radio-button>
              <el-radio-button label="sent">{{ t('pages.marketingFlow.shipmentTabSent') }}</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item :label="t('pages.marketingFlow.viewMode')" class="mb-0">
            <el-select v-model="outstandingViewMode" class="w-[min(100%,280px)]">
              <el-option :label="t('pages.marketingFlow.viewModeAll')" value="all" />
              <el-option :label="t('pages.marketingFlow.viewModeWarehouse')" value="warehouse_qc" />
              <el-option :label="t('pages.marketingFlow.viewModeMktDelivery')" value="mkt_delivery" />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('pages.marketingFlow.searchPo')" class="mb-0">
            <div class="flex flex-wrap items-center gap-2">
              <el-input
                v-model="poSearch"
                clearable
                class="w-[200px]"
                :placeholder="t('pages.marketingFlow.searchPoPlaceholder')"
                @keyup.enter="loadOutstanding"
              />
              <el-button @click="loadOutstanding">{{ t('common.search') }}</el-button>
            </div>
          </el-form-item>
        </div>
        <div class="mb-3 flex flex-wrap items-center gap-2">
          <el-button type="primary" plain :disabled="!outstandingSelection.length" @click="proposeScheduleFromSelection">
            {{ t('pages.marketingFlow.scheduleDraftButton') }}
          </el-button>
          <span v-if="outstandingSelection.length" class="text-sm text-gray-600 dark:text-gray-400">
            {{ t('pages.marketingFlow.selectedCount', { n: outstandingSelection.length }) }}
          </span>
        </div>
        <el-collapse class="mb-3">
          <el-collapse-item :title="t('pages.marketingFlow.filterColumnsTitle')" name="filters">
            <p class="mb-2 text-xs text-gray-500">{{ t('pages.marketingFlow.filterHint') }}</p>
            <div class="grid max-h-48 grid-cols-2 gap-2 overflow-y-auto md:grid-cols-3 lg:grid-cols-4">
              <div v-for="f in outstandingTextFilterFields" :key="f.key" class="flex min-w-0 flex-col gap-0.5">
                <span class="text-xs text-gray-600 dark:text-gray-400">{{ f.label }}</span>
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
          class="admin-table outstanding-table"
          max-height="560"
          :empty-text="t('pages.marketingFlow.outstandingEmpty')"
          show-summary
          :summary-method="outstandingSummary"
          @selection-change="onOutstandingSelectionChange"
        >
          <el-table-column type="selection" width="44" fixed />
          <el-table-column type="index" width="44" fixed />
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
          <el-table-column prop="delivered_qty" :label="t('pages.marketingFlow.colDeliveredQty')" width="100" align="right" />
          <el-table-column prop="system_reference" :label="t('pages.marketingFlow.colSystemNo')" min-width="130" show-overflow-tooltip />
          <el-table-column prop="production_status" :label="t('pages.marketingFlow.colProductionStatus')" width="120" show-overflow-tooltip />
          <el-table-column prop="remark_system" :label="t('pages.marketingFlow.colRemarkSystem')" min-width="160" show-overflow-tooltip />
          <el-table-column prop="remark_marketing" :label="t('pages.marketingFlow.colRemarkMarketing')" min-width="160">
            <template #default="{ row }">
              <el-input
                v-model="row.remark_marketing"
                type="textarea"
                :autosize="{ minRows: 1, maxRows: 3 }"
                size="small"
                :disabled="!canEditPoDetail || savingRemarkId === row.po_detail_id"
                @change="saveMarketingRemark(row)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="detail_remark" :label="t('pages.marketingFlow.colPoLineRemark')" min-width="120" show-overflow-tooltip />
          <el-table-column :label="t('pages.marketingFlow.deliveryRound', { n: 1 })" align="center">
            <el-table-column prop="delivery_1_qty" :label="t('pages.marketingFlow.colShipQty')" width="72" align="right" />
            <el-table-column prop="delivery_1_date" :label="t('pages.marketingFlow.colShipDateShort')" width="96" />
          </el-table-column>
          <el-table-column :label="t('pages.marketingFlow.deliveryRound', { n: 2 })" align="center">
            <el-table-column prop="delivery_2_qty" :label="t('pages.marketingFlow.colShipQty')" width="72" align="right" />
            <el-table-column prop="delivery_2_date" :label="t('pages.marketingFlow.colShipDateShort')" width="96" />
          </el-table-column>
          <el-table-column :label="t('pages.marketingFlow.deliveryRound', { n: 3 })" align="center">
            <el-table-column prop="delivery_3_qty" :label="t('pages.marketingFlow.colShipQty')" width="72" align="right" />
            <el-table-column prop="delivery_3_date" :label="t('pages.marketingFlow.colShipDateShort')" width="96" />
          </el-table-column>
          <el-table-column :label="t('pages.marketingFlow.deliveryRound', { n: 4 })" align="center">
            <el-table-column prop="delivery_4_qty" :label="t('pages.marketingFlow.colShipQty')" width="72" align="right" />
            <el-table-column prop="delivery_4_date" :label="t('pages.marketingFlow.colShipDateShort')" width="96" />
          </el-table-column>
          <el-table-column :label="t('pages.marketingFlow.deliveryRound', { n: 5 })" align="center">
            <el-table-column prop="delivery_5_qty" :label="t('pages.marketingFlow.colShipQty')" width="72" align="right" />
            <el-table-column prop="delivery_5_date" :label="t('pages.marketingFlow.colShipDateShort')" width="96" />
          </el-table-column>
          <el-table-column :label="t('pages.marketingFlow.deliveryRound', { n: 6 })" align="center">
            <el-table-column prop="delivery_6_qty" :label="t('pages.marketingFlow.colShipQty')" width="72" align="right" />
            <el-table-column prop="delivery_6_date" :label="t('pages.marketingFlow.colShipDateShort')" width="96" />
          </el-table-column>
          <el-table-column prop="mkt_stage" :label="t('pages.marketingFlow.colMktStage')" min-width="140">
            <template #default="{ row }">
              <el-tag size="small">{{ labelFor(row.mkt_stage) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="88" fixed="right" align="center">
            <template #default="{ row }">
              <el-tooltip :content="t('pages.marketingFlow.openPo')" placement="top">
                <el-button
                  :icon="Document"
                  link
                  type="primary"
                  size="small"
                  :aria-label="t('pages.marketingFlow.openPo')"
                  @click="goPo(row.po_id)"
                />
              </el-tooltip>
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
          <el-table-column prop="gross_weight" :label="t('pages.delivery.columns.gw')" width="80" align="right" />
          <el-table-column prop="net_weight" :label="t('pages.delivery.columns.nw')" width="80" align="right" />
          <el-table-column prop="amount" :label="t('pages.delivery.columns.amount')" width="92" align="right" />
          <el-table-column prop="order_type" :label="t('pages.delivery.columns.orderType')" width="100" show-overflow-tooltip />
          <el-table-column prop="color_std" :label="t('common.colorStandard')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="emboss" :label="t('common.emboss')" width="90" show-overflow-tooltip />
          <el-table-column prop="buyer" :label="t('common.buyer')" width="100" show-overflow-tooltip />
          <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="model" :label="t('common.model')" width="100" show-overflow-tooltip />
          <el-table-column prop="invoice_number" :label="t('common.invoiceNo')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="pi_no" :label="t('pages.marketingFlow.colPiNo')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="remark" :label="t('common.remark')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="delivery_status" :label="t('common.status')" width="100" />
          <el-table-column :label="t('common.actions')" width="88" fixed="right" align="center">
            <template #default="{ row }">
              <el-tooltip :content="t('pages.marketingFlow.openDelivery')" placement="top">
                <el-button
                  :icon="Van"
                  link
                  type="primary"
                  size="small"
                  :aria-label="t('pages.marketingFlow.openDelivery')"
                  @click="goDelivery(row)"
                />
              </el-tooltip>
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
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DArrowRight, Document, Download, Van } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  advanceMktWorkflow,
  listMarketingDeliveryLines,
  listMarketingOutstandingLines,
  listPo,
  listPoMktStages,
  marketingDeliveryCsvUrl,
  marketingOutstandingCsvUrl,
  marketingOutstandingXlsxPath,
  reportPoDailyRecapUrl,
  updatePoDetail,
} from '../../api/client'
import { can } from '../../security/permissions'

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
  'model',
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
    model: 'common.model',
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
    const path = marketingOutstandingXlsxPath({
      balance_filter: balanceFilter.value,
      computed_balance: true,
      po_q: poSearch.value,
      shipment_status: shipmentTab.value,
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
    const lines = await listMarketingDeliveryLines()
    deliveryRows.value = (lines || []).map((r) => ({
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
  await load()
})

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
  window.open(reportPoDailyRecapUrl(rekapDate.value), '_blank')
}

function downloadOutstanding() {
  window.open(
    marketingOutstandingCsvUrl({
      balance_filter: balanceFilter.value,
      computed_balance: true,
      po_q: poSearch.value,
      shipment_status: shipmentTab.value,
    }),
    '_blank',
  )
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
