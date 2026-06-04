<template>
  <AdminSection :title="t('pages.po.title')" :subtitle="t('pages.po.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.po.searchPlaceholder')"
        clearable
        class="po-toolbar-search"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Download" @click="openExportHint">{{ t('common.export') }}</el-button>
      <el-button v-if="canManage" type="primary" :icon="Plus" @click="openCreateDialog">{{ t('common.create') }}</el-button>
    </template>

    <div class="filter-panel mb-4">
      <p class="filter-panel__title">{{ t('common.filter') }}</p>
      <el-form class="filter-form" label-position="top">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :md="8" :lg="5">
            <el-form-item :label="t('common.customer')">
              <el-select
                v-model="filterCustomerId"
                clearable
                filterable
                class="w-full"
                :placeholder="t('common.placeholder.customer')"
              >
                <el-option
                  v-for="c in customers"
                  :key="c.id"
                  :label="formatCustomerOption(c)"
                  :value="c.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="8" :lg="4">
            <el-form-item :label="t('common.status')">
              <el-select v-model="filterStatus" clearable class="w-full" :placeholder="t('common.status')">
                <el-option :label="t('status.draft')" value="draft" />
                <el-option :label="t('status.confirmed')" value="confirmed" />
                <el-option :label="t('status.production')" value="production" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="4">
            <el-form-item :label="t('common.buyer')">
              <el-select v-model="filterBuyer" clearable filterable class="w-full" :placeholder="t('common.placeholder.buyer')">
                <el-option v-for="b in buyerCodes" :key="b" :label="b" :value="b" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="18" :md="16" :lg="8">
            <el-form-item :label="t('pages.po.filterOrderDateRange')">
              <el-date-picker
                v-model="filterOrderDateRange"
                type="daterange"
                unlink-panels
                range-separator="—"
                value-format="YYYY-MM-DD"
                size="small"
                class="w-full min-w-[200px] max-w-full"
                :shortcuts="poOrderDateShortcuts"
                clearable
                :start-placeholder="t('common.fromDate')"
                :end-placeholder="t('common.toDate')"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="6" :md="8" :lg="3" class="po-filter-action-col">
            <el-form-item label="&nbsp;">
              <el-button class="w-full" :icon="RefreshLeft" @click="resetFilter">{{ t('common.reset') }}</el-button>
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
      :empty-text="t('pages.po.tableEmpty')"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="po_number" :label="t('common.poNo')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="po_customer_ref" :label="t('pages.po.poCustomerRef')" min-width="140" show-overflow-tooltip />
      <el-table-column prop="order_date_fmt" :label="t('common.orderDate')" width="112" align="center" />
      <el-table-column prop="customerName" :label="t('common.customer')" min-width="200" show-overflow-tooltip />
      <el-table-column prop="brand_name_snapshot" :label="t('pages.po.brand')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="buyer" :label="t('common.buyer')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="material_hint" :label="t('common.material')" min-width="140" show-overflow-tooltip />
      <el-table-column :label="t('pages.po.colOrderTypeFactory')" min-width="130" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.order_type_label || t('common.emptyValue') }}</span>
          <span v-if="row.factory_code" class="text-slate-500"> · {{ row.factory_code }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="po_category" :label="t('common.category')" min-width="110" align="center">
        <template #default="{ row }">
          <el-tag size="small" type="info" effect="plain">{{ t(`status.${row.po_category}`) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="etd" :label="t('common.etd')" min-width="110" align="center" />
      <el-table-column prop="delivery_address" :label="t('pages.po.deliveryAddress')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="remark" :label="t('pages.po.colHeaderRemarkSo')" min-width="140" show-overflow-tooltip />
      <el-table-column :label="t('pages.marketingFlow.materialFollowUp')" min-width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="flex flex-wrap items-center gap-1">
            <el-tag v-if="row.material_followup_done" size="small" type="success" effect="plain">{{ t('pages.po.done') }}</el-tag>
            <el-tag v-else size="small" type="info" effect="plain">{{ t('pages.po.followupOpen') }}</el-tag>
            <span v-if="row.material_followup_remark" class="text-xs text-slate-700">{{ row.material_followup_remark }}</span>
            <span v-else class="text-xs text-slate-400">—</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column :label="t('pages.marketingFlow.stuckReason')" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">
          <el-tag v-if="row.stuck_reason" type="warning" size="small" effect="plain">{{ row.stuck_reason }}</el-tag>
          <span v-else class="text-slate-400 text-xs">—</span>
        </template>
      </el-table-column>
      <el-table-column prop="mkt_workflow_stage" :label="t('pages.po.mktFlow')" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.mkt_workflow_stage || t('common.emptyValue') }}</template>
      </el-table-column>
      <el-table-column prop="status" :label="t('common.status')" width="140" align="center">
        <template #default="{ row }">
          <el-popconfirm
            v-if="canManage"
            :title="t('pages.po.confirmPo')"
            :confirm-button-text="t('common.yes')"
            :cancel-button-text="t('common.no')"
            @confirm="quickChangeStatus(row, 'confirmed')"
          >
            <template #reference>
              <el-tag :type="statusType(row.status)" size="small" class="cursor-pointer hover:opacity-70">
                {{ t(`status.${row.status}`) }}
              </el-tag>
            </template>
          </el-popconfirm>
          <el-tag v-else :type="statusType(row.status)" size="small">
            {{ t(`status.${row.status}`) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="268" align="center" fixed="right">
        <template #default="{ row }">
          <div class="po-row-actions">
            <el-tooltip :content="t('common.detail')" placement="top">
              <el-button :icon="View" link type="primary" :aria-label="t('common.detail')" @click="openDetailDialog(row)" />
            </el-tooltip>
            <el-tooltip v-if="canManage" :content="t('common.edit')" placement="top">
              <el-button :icon="EditPen" link type="warning" :aria-label="t('common.edit')" @click="openEditDialog(row)" />
            </el-tooltip>
            <el-tooltip v-if="canManage" :content="t('pages.po.duplicatePo')" placement="top">
              <el-button
                :icon="CopyDocument"
                link
                type="primary"
                :aria-label="t('pages.po.duplicatePo')"
                @click="onDuplicatePo(row)"
              />
            </el-tooltip>
            <el-tooltip :content="t('pages.po.salesContractPdf')" placement="top">
              <el-button :icon="Document" link type="primary" :aria-label="t('pages.po.salesContractPdf')" @click="downloadSalesContractPdf(row)" />
            </el-tooltip>
            <el-tooltip :content="t('pages.po.salesContractDocx')" placement="top">
              <el-button :icon="FolderOpened" link type="primary" :aria-label="t('pages.po.salesContractDocx')" @click="downloadSalesContractDocx(row)" />
            </el-tooltip>
            <el-tooltip :content="t('common.print')" placement="top">
              <el-button :icon="Printer" link :aria-label="t('common.print')" @click="openPrintDialog(row)" />
            </el-tooltip>
            <el-tooltip v-if="canManage" :content="t('common.delete')" placement="top">
              <el-button :icon="Delete" link type="danger" :aria-label="t('common.delete')" @click="removeRow(row)" />
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <div class="mt-3 flex justify-end">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        size="small"
        layout="total, sizes, prev, pager, next"
        :total="totalRows"
        :page-sizes="[20, 50, 100, 200]"
      />
    </div>

    <PoFormWizardDialog />


    <PoMarketingReviseDialog
      v-model="marketingReviseVisible"
      v-model:header="marketingReviseHeader"
      v-model:lines="marketingReviseLines"
      :loading="marketingReviseLoading"
      :saving="marketingReviseSaving"
      @save="submitMarketingRevise"
    />

    <PoDetailDialog
      v-model="detailDialogVisible"
      :detail-view="detailView"
      :detail-lines="detailLines"
      :detail-audit="detailAudit"
      :color-family-label="colorFamilyLabel"
    />

    <PoPrintPreviewDialog
      v-model="printDialogVisible"
      :row="selectedRow"
      @print="printPage"
    />

    <PoCopyItemDialog
      v-model="copyItemDialogVisible"
      :customers="customers"
      :customer-id="copyItemCustomerId"
      :search="copyItemSearch"
      :source-items="copyItemSourcePo"
      :filtered-items="copyItemFilteredPo"
      :selected-count="copyItemSelected.length"
      :format-customer-option="formatCustomerOption"
      @update:customer-id="onCopyItemCustomerChange"
      @update:search="copyItemSearch = $event"
      @selection-change="onCopyItemSelectionChange"
      @add-selected="addCopiedItems"
    />

    <PoAmbiguousMasterDialog
      v-model="ambiguousMasterVisible"
      v-model:selected-id="selectedAmbiguousMasterId"
      :candidates="ambiguousMasterCandidates"
      @confirm="confirmAmbiguousMasterPick"
    />
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Download,
  View,
  EditPen,
  Delete,
  Printer,
  RefreshLeft,
  Search,
  Document,
  FolderOpened,
  ArrowLeft,
  ArrowRight,
} from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import PoFormWizardDialog from '../../components/admin/PoFormWizardDialog.vue'
import PoAmbiguousMasterDialog from '../../components/admin/PoAmbiguousMasterDialog.vue'
import PoCopyItemDialog from '../../components/admin/PoCopyItemDialog.vue'
import PoDetailDialog from '../../components/admin/PoDetailDialog.vue'
import PoMarketingReviseDialog from '../../components/admin/PoMarketingReviseDialog.vue'
import PoPrintPreviewDialog from '../../components/admin/PoPrintPreviewDialog.vue'
import { usePoList } from '../../composables/usePoList.js'
import { usePoMarketingRevise } from '../../composables/usePoMarketingRevise.js'
import { providePoWizardContext } from '../../composables/poFormWizardContext.js'
import { canWrite } from '../../security/permissions'
import { statusType, statusLabel } from '../../utils/format'
import {
  emptyEtdScheduleRows,
  normalizeSchedulesFromApi,
  etdScheduleRowsToPayload,
  loadEtdScheduleRowsFromApi,
  lineHasScheduleMismatch,
  buildEvenEtdScheduleRows,
} from '../../utils/poEtdSchedule.js'
import {
  buildPoDraftPayload,
  applyPoDraftData,
  savePoDraftLocalStorage,
  clearPoDraftLocalStorage,
  readPoDraftRaw,
} from '../../utils/poDraft.js'
import {
  factoryCodeFromCustomer,
  swatchFactoryHint,
  swatchOptionLabel,
  fetchColorSwatchOptionList,
  applyColorSwatchFill,
} from '../../utils/poColorSwatch.js'
import { parseApiErrorMessage } from '../../utils/poApi.js'
import { customerOptionLabel, mergeExtraBuyerCodes, parsePoRoutePoId, resolvePoDeepLinkRow } from '../../utils/poList.js'
import {
  inferColorFamilyFromColor,
  applyReferenceDefaults as applyReferenceDefaultsFromMaster,
  hydrateFormFromMasterItemRow as applyMasterItemToForm,
  resetMaterialFieldToMaster as resetMaterialFieldToMasterValues,
  isThicknessPricingFormatValid,
  detailMasterSnapshot,
} from '../../utils/poMasterResolve.js'
import {
  buildDetailBodyCore,
  appendDetailUnitPrice,
  detailPayloadForUpdate,
  sanitizeNewDetailBody,
} from '../../utils/poDetailPayload.js'
import {
  addPoDetail,
  createPo,
  deletePoDetail,
  deletePo,
  duplicatePo,
  generatePoDetailLot,
  generateLotPreview,
  fetchNextPoNumber,
  fetchAuthenticatedDocument,
  getAllowedBrands,
  getCustomer,
  getPo,
  listBrands,
  listBrandBuyers,
  listBuyerPriceLists,
  listCustomers,
  listMasterItems,
  listMasterItemDimensionValues,
  resolveMasterItemByDimensions,
  listFluorescentColors,
  lookupColorSwatchRecipes,
  getColorSwatchPoFill,
  listPoPage,
  listPoDetails,
  listPoForCopy,
  listAuditLogs,
  resolveBuyerUnitPrice,
  salesContractDocxPath,
  salesContractPdfPath,
  setPoDetailDeliverySchedules,
  listPoDetailDeliverySchedules,
  toIsoDate,
  updatePo,
  updatePoDetail,
} from '../../api/client'

const { t } = useI18n()

const route = useRoute()
const canManage = canWrite('po')

const {
  keyword,
  filterCustomerId,
  filterStatus,
  filterBuyer,
  filterOrderDateRange,
  rows,
  totalRows,
  page,
  pageSize,
  loading,
  poOrderDateShortcuts,
  buildPageQuery,
  enrichHeaders,
  resetFilters,
  registerFilterWatch,
} = usePoList({ t })

const saving = ref(false)
const customers = ref([])
const brands = ref([])
const masterItems = ref([])
const buyerCodes = ref(['NB', 'ADIDAS', 'NIKE', 'UA'])
const brandBuyerCodes = ref([])
const customerBuyerCodes = ref([])
const brandLockedCustomerId = ref(null)
const allowedBrandIds = ref([])
const selectedCustomer = ref(null)
const autoFieldMeta = reactive({
  buyer: false,
  factory_code: false,
  vir_softness_type: false,
  softness: false,
  color_reference: false,
  color_standard: false,
  backing: false,
  model: false,
})
const materialAdvancedOpen = ref([])
const materialFieldOverride = reactive({
  material_name: false,
  thickness_text: false,
  color: false,
  color_family: false,
  emboss: false,
  style_article: false,
})
const colorFamilyAutoMode = ref(true)
const lotAutoFromMaterial = ref(false)
const lotGenerateLoading = ref(false)
let lotAutoTimer = null
let skipLotAutoUntil = 0
let lotAutoSeq = 0

function formatCustomerOption(c) {
  return customerOptionLabel(c, t)
}

async function quickChangeStatus(row, newStatus) {
  try {
    await updatePo(row.id, { status: newStatus })
    row.status = newStatus
    ElMessage.success(t('pages.po.statusChanged'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function load() {
  loading.value = true
  try {
    const [cust, br, mi, bpl, poPage, dimMat] = await Promise.all([
      listCustomers(),
      listBrands(),
      listMasterItems(),
      listBuyerPriceLists().catch(() => []),
      listPoPage(buildPageQuery()),
      listMasterItemDimensionValues('materials').catch(() => ({ values: [] })),
    ])
    customers.value = cust
    brands.value = br
    masterItems.value = mi
    materialDimensionOptions.value = dimMat.values || []
    buyerCodes.value = mergeExtraBuyerCodes(buyerCodes.value, bpl)
    rows.value = await enrichHeaders(poPage.items || [], cust)
    totalRows.value = Number(poPage.total || 0)
  } catch (e) {
    ElMessage.error(e.message || t('pages.po.loadFailed'))
  } finally {
    loading.value = false
  }
}

registerFilterWatch(load)

onMounted(async () => {
  await load()
  await openPoFromRouteQuery()
})

async function openPoFromRouteQuery() {
  const poId = parsePoRoutePoId(route)
  if (!poId) return
  const target = await resolvePoDeepLinkRow({ poId, rows: rows.value, getPo })
  if (!target) return
  await openEditDialog(target)
}

const brandsFiltered = computed(() => {
  if (allowedBrandIds.value.length > 0) {
    return brands.value.filter((b) => allowedBrandIds.value.includes(b.id))
  }
  const cid = formModel.customer_id
  if (cid) {
    return brands.value.filter((b) => !b.customer_id || b.customer_id === cid)
  }
  return brands.value
})

const buyerCodesFiltered = computed(() => {
  if (brandBuyerCodes.value.length) return brandBuyerCodes.value
  if (customerBuyerCodes.value.length) return customerBuyerCodes.value
  if (formModel.customer_id || formModel.brand_id) return []
  return buyerCodes.value
})
const isBrandDisabled = computed(() => Boolean(formModel.customer_id))
const isBuyerDisabled = computed(() => Boolean(formModel.customer_id) || !formModel.brand_id || buyerCodesFiltered.value.length === 0)
const isPoCategoryDisabled = computed(() => !formModel.customer_id || !formModel.brand_id || !formModel.buyer)

const customerPicDisplay = computed(() => {
  if (!selectedCustomer.value) return t('common.emptyValue')
  const name = selectedCustomer.value.contact_person || selectedCustomer.value.name || ''
  const position = selectedCustomer.value.position || ''
  if (name && position) return `${name} (${position})`
  return name || position || t('common.emptyValue')
})

function parseSoftnessValue(raw) {
  const str = String(raw || '').trim()
  const first = str.match(/(\d+(?:\.\d+)?)/)
  return first ? Number(first[1]) : null
}

const softnessRangeWarning = computed(() => {
  const v = parseSoftnessValue(formModel.softness)
  if (v == null) return ''
  const buyer = String(formModel.buyer || '').toUpperCase()
  if (buyer.includes('NIKE')) {
    if (v < 2.8 || v > 3.2) return t('pages.po.softnessWarningNike')
    return ''
  }
  if (v < 2.0 || v > 3.0) return t('pages.po.softnessWarningGeneral')
  return ''
})

const nextPoNumberPreview = ref('')

const nextPoNumberDisplay = computed(() => {
  if (isEditMode.value) return formModel.po_number || ''
  return nextPoNumberPreview.value || '…'
})

async function refreshNextPoNumberPreview() {
  if (isEditMode.value) return
  try {
    const r = await fetchNextPoNumber()
    nextPoNumberPreview.value = r?.po_number || ''
  } catch {
    nextPoNumberPreview.value = ''
  }
}

const currentStep = ref(0)

function nextStep() {
  if (currentStep.value === 0) {
    if (!formModel.customer_id) {
      formErrors.customer_id = t('pages.po.customerRequired')
      ElMessage.warning(t('pages.po.customerRequired'))
      return
    }
    if (!formModel.brand_id) {
      ElMessage.warning('Brand wajib dipilih setelah customer.')
      return
    }
    if (!formModel.buyer) {
      ElMessage.warning('Buyer wajib dipilih setelah brand.')
      return
    }
    formErrors.customer_id = ''
  }
  if (currentStep.value < 2) {
    currentStep.value++
    if (currentStep.value === 1) {
      void refreshMaterialDimensionOptions()
    }
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const filteredRows = computed(() =>
  rows.value,
)

const resetFilter = () => resetFilters(load)

const formDialogVisible = ref(false)
const isEditMode = ref(false)
/** Tanggal order dari DB saat buka edit — jika ada, tanggal tidak boleh diubah lewat form simpan penuh. */
const savedHeaderOrderDate = ref('')
const orderDateLocked = computed(() => isEditMode.value && Boolean(savedHeaderOrderDate.value))

const editingPoId = ref(null)
const editingDetailIds = ref([])
const draftLines = ref([])
const draftRiskOnly = ref(false)
const editingDraftLineIndex = ref(-1)
const draftLinesDisplay = computed(() => {
  if (!draftRiskOnly.value) return draftLines.value
  return draftLines.value.filter((line) => Boolean(line.manual_override) || Boolean(line.material_master_override))
})

const copyItemDialogVisible = ref(false)
const copyItemCustomerId = ref(null)
const copyItemSourcePo = ref([])
const copyItemSelected = ref([])
const copyItemSearch = ref('')

const copyItemFilteredPo = computed(() => {
  if (!copyItemSearch.value) return copyItemSourcePo.value
  const search = copyItemSearch.value.toLowerCase()
  return copyItemSourcePo.value.filter(item =>
    (item.material_name || '').toLowerCase().includes(search) ||
    (item.color || '').toLowerCase().includes(search) ||
    (item.source_po_number || '').toLowerCase().includes(search) ||
    (item.thickness_text || '').toLowerCase().includes(search)
  )
})

const formModel = reactive({
  po_number: '',
  customer_id: null,
  brand_id: null,
  po_category: 'production',
  factory_code: '',
  order_date: '',
  buyer: '',
  etd: '',
  po_customer_ref: '',
  remark: '',
  billing_address: '',
  delivery_address: '',
  status: 'draft',
  master_item_id: null,
  material_name: '',
  thickness_text: '',
  color: '',
  color_family: null,
  emboss: '',
  vir_softness_type: '',
  softness: '',
  color_reference: '',
  color_standard: '',
  backing: '',
  quantity_order: '',
  style_article: '',
  model: '',
  detail_remark: '',
  thi_line_ref: '',
  unit_price_input: null,
  autoPricingEnabled: true,
  is_special_price: false,
  discount_type: 'percent',
  discount_value: 0,
})

const {
  visible: marketingReviseVisible,
  loading: marketingReviseLoading,
  saving: marketingReviseSaving,
  header: marketingReviseHeader,
  lines: marketingReviseLines,
  open: openMarketingReviseDialog,
  submit: submitMarketingRevise,
} = usePoMarketingRevise({ t, editingPoId, formModel })

const pricePreviewLoading = ref(false)
const previewResolvedUnitPrice = ref(null)
const fluorescentColorOptions = ref([])
const colorSwatchOptions = ref([])
const colorSwatchLoading = ref(false)
const swatchAllMaterials = ref(false)
const swatchRetriedWithoutMaterial = ref(false)
const selectedSwatchId = ref(null)

const etdScheduleOpen = ref(['schedule'])
const etdScheduleRows = ref(emptyEtdScheduleRows())

function clearEtdScheduleRows() {
  etdScheduleRows.value = emptyEtdScheduleRows()
}

const etdScheduleTotal = computed(() =>
  etdScheduleRows.value.reduce((sum, r) => sum + (Number(r.qty) || 0), 0),
)

const etdScheduleTotalDisplay = computed(() => {
  const t = etdScheduleTotal.value
  return t ? String(t) : '0'
})

const etdScheduleMismatch = computed(() => lineHasScheduleMismatch({
  quantity_order: formModel.quantity_order,
  delivery_schedules: etdScheduleRowsToPayload(etdScheduleRows.value),
}, etdScheduleRows.value))

function autoFillEtdScheduleWave1() {
  const qty = Number(formModel.quantity_order)
  if (!qty) {
    ElMessage.warning(t('pages.po.scheduleNeedQty'))
    return
  }
  clearEtdScheduleRows()
  etdScheduleRows.value[0].qty = qty
  etdScheduleRows.value[0].date = formModel.etd ? String(formModel.etd).slice(0, 10) : ''
}

function autoFillEtdScheduleEvenly() {
  const qty = Number(formModel.quantity_order)
  if (!qty) {
    ElMessage.warning(t('pages.po.scheduleNeedQty'))
    return
  }
  etdScheduleRows.value = buildEvenEtdScheduleRows(qty, formModel.etd)
}

async function syncCurrentFormToDraftLine() {
  if (editingDraftLineIndex.value < 0) return
  const idx = editingDraftLineIndex.value
  if (idx >= draftLines.value.length) return
  const cur = await buildCurrentDetailBody()
  draftLines.value[idx] = {
    ...draftLines.value[idx],
    ...cur,
    delivery_schedules: cur.delivery_schedules || [],
  }
}

function draftRowClassName({ row }) {
  const idx = draftLines.value.indexOf(row)
  return idx >= 0 && idx === editingDraftLineIndex.value ? 'draft-line-active' : ''
}

async function applyLineToForm(line) {
  formModel.master_item_id = line.master_item_id ?? null
  formModel.material_name = line.material_name || ''
  formModel.thickness_text = line.thickness_text || ''
  formModel.color = line.color || ''
  formModel.color_family = line.color_family || null
  formModel.emboss = line.emboss || ''
  formModel.vir_softness_type = line.vir_softness_type || ''
  formModel.softness = line.softness || ''
  formModel.color_reference = line.color_reference || ''
  formModel.color_standard = line.color_standard || ''
  formModel.backing = line.backing || ''
  formModel.quantity_order = line.quantity_order != null ? String(line.quantity_order) : ''
  formModel.style_article = line.style_article || ''
  formModel.model = line.model || ''
  formModel.detail_remark = line.detail_remark || ''
  formModel.thi_line_ref = line.thi_line_ref || ''
  formModel.unit_price_input = line.unit_price != null ? Number(line.unit_price) : null
  selectedSwatchId.value = line.color_swatch_recipe_id ?? null
  etdScheduleRows.value = loadEtdScheduleRowsFromApi(line.delivery_schedules || [])
  await refreshThicknessOptionsFromApi()
  await refreshColorOptionsFromApi()
}

async function editDraftLine(row) {
  const idx = draftLines.value.indexOf(row)
  if (idx < 0) return
  if (editingDraftLineIndex.value >= 0 && editingDraftLineIndex.value !== idx) {
    await syncCurrentFormToDraftLine()
  }
  editingDraftLineIndex.value = idx
  await applyLineToForm(draftLines.value[idx])
  currentStep.value = 1
  ElMessage.info(t('pages.po.editingDraftLine', { n: idx + 1 }))
}

async function saveDetailSchedules(detailId, schedules) {
  await setPoDetailDeliverySchedules(detailId, etdScheduleRowsToPayload(
    (schedules || []).map((s) => ({
      sequence_no: s.sequence_no,
      qty: s.qty,
      date: s.delivery_date || s.date || '',
    })),
  ))
}

const materialDimensionOptions = ref([])
const thicknessDimensionOptions = ref([])
const colorDimensionOptions = ref([])
const masterResolveLoading = ref(false)
const ambiguousMasterVisible = ref(false)
const ambiguousMasterCandidates = ref([])
const selectedAmbiguousMasterId = ref(null)
const lastResolveHadNoMaster = ref(false)
/** Hindari resolve berulang saat dialog ambigu ditutup tanpa pilihan (kombinasi sama). */
const skipMasterResolve = ref(false)
/** Cegah resolve ulang saat buka edit PO selama kombinasi material|ketebalan|warna|master_id sama seperti yang dimuat dari DB. */
const loadedDetailMasterSnapshot = ref(null)

let pricePreviewTimer = null
function schedulePricePreview() {
  clearTimeout(pricePreviewTimer)
  pricePreviewTimer = setTimeout(() => {
    fetchResolvedUnitPricePreview()
  }, 400)
}

async function fetchResolvedUnitPricePreview() {
  const b = (formModel.buyer || '').trim()
  if (!b) {
    previewResolvedUnitPrice.value = null
    return
  }
  const prevPreview = previewResolvedUnitPrice.value
  pricePreviewLoading.value = true
  try {
    const r = await resolveBuyerUnitPrice({
      buyer_code: b,
      material_name: formModel.material_name || null,
      color: formModel.color || null,
      style_article: formModel.style_article || null,
      thickness_text: formModel.thickness_text || null,
      color_family: formModel.color_family || null,
    })
    const nextPreview = r.unit_price != null ? Number(r.unit_price) : null
    previewResolvedUnitPrice.value = nextPreview
    // Sinkronkan otomatis ke input harga selama user belum override manual.
    const userHasManualValue =
      formModel.unit_price_input != null &&
      prevPreview != null &&
      Number(formModel.unit_price_input) !== Number(prevPreview)
    if (!formModel.is_special_price && !userHasManualValue) {
      formModel.unit_price_input = nextPreview
    }
  } catch (e) {
    console.error('Error resolving unit price:', e)
    previewResolvedUnitPrice.value = null
  } finally {
    pricePreviewLoading.value = false
  }
}

const displayResolvedUnitPrice = computed(() => {
  if (pricePreviewLoading.value) return '…'
  if (previewResolvedUnitPrice.value != null) return String(previewResolvedUnitPrice.value)
  return '—'
})
const isFluorescentFamily = computed(() => String(formModel.color_family || '').toLowerCase() === 'fluorescent')
const materialThicknessColorComplete = computed(() => {
  return (
    String(formModel.material_name || '').trim().length > 0 &&
    String(formModel.thickness_text || '').trim().length > 0 &&
    String(formModel.color || '').trim().length > 0
  )
})
const resolvedMasterItemLabel = computed(() => {
  const id = formModel.master_item_id
  if (!id) return ''
  const it = masterItems.value.find((x) => x.id === id)
  if (!it) return `#${id}`
  return `${it.item_code} — ${it.material_name || ''}`
})
const activeSeasonLabel = computed(() => deriveSeasonLabel(formModel.order_date))
const pricingKeyIncomplete = computed(() => {
  if (!(formModel.buyer || '').trim()) return false
  return !String(formModel.material_name || '').trim() || !String(formModel.thickness_text || '').trim() || !String(formModel.color_family || '').trim()
})

const hasSpecialPriceInLines = computed(() => {
  return draftLines.value.some(line => line.is_special_price)
})

function onSpecialPriceChange(val) {
  if (val) {
    formModel.discount_value = 0
    calculateSpecialPrice()
  } else {
    formModel.discount_value = 0
  }
}

function calculateSpecialPrice() {
  if (!formModel.is_special_price || previewResolvedUnitPrice.value == null) {
    return
  }

  const basePrice = previewResolvedUnitPrice.value
  const adjustValue = Number(formModel.discount_value || 0)

  if (formModel.discount_type === 'percent') {
    // adjustment percent: bisa + / -
    formModel.unit_price_input = basePrice * (1 + adjustValue / 100)
  } else {
    // adjustment nominal USD: bisa + / -
    formModel.unit_price_input = Math.max(0, basePrice + adjustValue)
  }
}

function colorFamilyLabel(v) {
  if (!v) return t('common.emptyValue')
  const k = String(v).toLowerCase()
  if (k === 'black') return t('pages.po.colorFamilyBlack')
  if (k === 'color') return t('pages.po.colorFamilyColor')
  if (k === 'fluorescent') return t('pages.po.colorFamilyFluorescent')
  return String(v)
}

function materialQualityLabel(row) {
  if (row?.material_master_matched) return 'Master matched'
  if (row?.master_item_id) return 'Master override'
  return 'Input manual'
}

function materialQualityType(row) {
  if (row?.material_master_matched) return 'success'
  if (row?.master_item_id) return 'warning'
  return 'info'
}

function materialQualityTooltip(row) {
  if (row?.material_master_matched) {
    return 'Line mengikuti data master item tanpa perubahan field inti material.'
  }
  if (row?.master_item_id) {
    return 'Line pakai master item, namun ada field inti material yang dioverride.'
  }
  return 'Line diinput manual tanpa referensi master item.'
}

function deriveSeasonLabel(orderDate) {
  if (!orderDate) return ''
  const dt = new Date(orderDate)
  if (Number.isNaN(dt.getTime())) return ''
  const year = dt.getFullYear()
  const month = dt.getMonth() + 1
  return month <= 6 ? `SS ${year}` : `FW ${year}`
}

function formatFluorescentOption(opt) {
  if (!opt) return ''
  const code = opt.color_code ? ` (${opt.color_code})` : ''
  return `${opt.color_name}${code}`
}

const poColorCascadeOptions = computed(() => {
  if (!isFluorescentFamily.value) return []
  const dimSet = new Set(colorDimensionOptions.value.map((x) => String(x).trim().toLowerCase()))
  const all = fluorescentColorOptions.value || []
  const inter = all.filter((o) => dimSet.has(String(o.color_name || '').trim().toLowerCase()))
  const src = inter.length ? inter : all
  return src.map((o) => ({
    ...o,
    _label: formatFluorescentOption(o),
  }))
})

async function loadFluorescentOptions() {
  if (!isFluorescentFamily.value) {
    fluorescentColorOptions.value = []
    return
  }
  const buyer = String(formModel.buyer || '').trim().toUpperCase()
  if (!buyer) {
    fluorescentColorOptions.value = []
    return
  }
  try {
    const seasonLabel = deriveSeasonLabel(formModel.order_date)
    fluorescentColorOptions.value = await listFluorescentColors({
      buyer_code: buyer,
      season_label: seasonLabel || undefined,
    })
  } catch {
    fluorescentColorOptions.value = []
  }
}

async function fetchFluorescentOptionsForValidation() {
  const buyer = String(formModel.buyer || '').trim().toUpperCase()
  if (!buyer) return []
  try {
    const seasonLabel = deriveSeasonLabel(formModel.order_date)
    return await listFluorescentColors({
      buyer_code: buyer,
      season_label: seasonLabel || undefined,
    })
  } catch {
    return []
  }
}

async function validateFluorescentLinesOrThrow(lines) {
  const opts = await fetchFluorescentOptionsForValidation()
  if (!opts.length) return
  const validNames = new Set(opts.map((x) => String(x.color_name || '').trim().toLowerCase()).filter(Boolean))
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i] || {}
    if (String(line.color_family || '').toLowerCase() !== 'fluorescent') continue
    const color = String(line.color || '').trim().toLowerCase()
    if (!color) continue
    if (!validNames.has(color)) {
      throw new Error(`Line ${i + 1}: warna fluorescent wajib dipilih dari master fluorescent sesuai buyer/season.`)
    }
  }
}

function isSelectedFluorescentColorValid() {
  if (!isFluorescentFamily.value) return true
  const chosen = String(formModel.color || '').trim().toLowerCase()
  if (!chosen) return true
  if (!fluorescentColorOptions.value.length) return true
  return fluorescentColorOptions.value.some((opt) => String(opt.color_name || '').trim().toLowerCase() === chosen)
}

function applyAutoFactoryCode(customer, { force = false } = {}) {
  const code = factoryCodeFromCustomer(customer)
  if (!code) return
  const current = String(formModel.factory_code || '').trim()
  if (force || autoFieldMeta.factory_code || !current) {
    formModel.factory_code = code
    autoFieldMeta.factory_code = true
  }
}

function poFactoryKeyForSwatch() {
  return swatchFactoryHint(formModel, {
    customers: customers.value,
    selectedCustomer: selectedCustomer.value,
  })
}

async function loadColorSwatchOptions() {
  colorSwatchLoading.value = true
  try {
    const { options, retriedWithoutMaterial } = await fetchColorSwatchOptionList({
      formModel,
      swatchAllMaterials: swatchAllMaterials.value,
      lookupColorSwatchRecipes,
      customers: customers.value,
      selectedCustomer: selectedCustomer.value,
    })
    colorSwatchOptions.value = options
    swatchRetriedWithoutMaterial.value = retriedWithoutMaterial
  } catch {
    colorSwatchOptions.value = []
    swatchRetriedWithoutMaterial.value = false
  } finally {
    colorSwatchLoading.value = false
  }
}

async function applyColorSwatch(recipeId) {
  if (!recipeId) return
  try {
    const fill = await getColorSwatchPoFill(recipeId)
    applyColorSwatchFill(fill, {
      formModel,
      autoFieldMeta,
      materialFieldOverride,
      selectedSwatchId,
    })
    ElMessage.success(t('pages.po.swatchApplied'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function applyVirSoftDefault() {
  const b = (formModel.buyer || '').toUpperCase()
  if (!b) return
  if (b.includes('NIKE')) {
    if (!formModel.vir_softness_type) {
      formModel.vir_softness_type = 'Vir Soft'
      autoFieldMeta.vir_softness_type = true
    }
  } else if (!formModel.vir_softness_type) {
    formModel.vir_softness_type = 'Soft'
    autoFieldMeta.vir_softness_type = true
  }
}

function canInferMaterialGroupForLot() {
  const mn = String(formModel.material_name || '').trim().toLowerCase()
  const vt = String(formModel.vir_softness_type || '').trim().toLowerCase()
  if (formModel.master_item_id) return true
  if (vt.includes('pu')) return true
  if (mn.includes('pu') || mn.includes('suede') || mn.includes('suide')) return true
  return false
}

function pauseLotAutoBriefly(ms = 900) {
  skipLotAutoUntil = Date.now() + ms
}

function scheduleAutoLotGenerate() {
  if (Date.now() < skipLotAutoUntil) return
  if (!String(formModel.material_name || '').trim()) return
  if (!String(formModel.factory_code || '').trim()) return
  if (!canInferMaterialGroupForLot()) return
  clearTimeout(lotAutoTimer)
  lotAutoTimer = setTimeout(() => {
    void autoGenerateLotFromMaterial({ showSuccess: false, showError: false })
  }, 380)
}

async function autoGenerateLotFromMaterial({ showSuccess = false, showError = false } = {}) {
  if (!String(formModel.factory_code || '').trim()) {
    if (showError) ElMessage.warning('Factory code wajib diisi sebelum generate lot.')
    return false
  }
  if (!String(formModel.material_name || '').trim()) return false
  if (!canInferMaterialGroupForLot()) {
    if (showError) {
      ElMessage.warning('Material harus mengandung PU/Suede atau terhubung master item agar lot bisa dibentuk.')
    }
    return false
  }
  const seq = ++lotAutoSeq
  lotGenerateLoading.value = true
  try {
    const r = await generateLotPreview({
      po_category: formModel.po_category,
      factory_code: String(formModel.factory_code || '').trim(),
      master_item_id: formModel.master_item_id || undefined,
      material_name: formModel.material_name || undefined,
      vir_softness_type: formModel.vir_softness_type || undefined,
    })
    if (seq !== lotAutoSeq) return false
    formModel.thi_line_ref = r.lot_number || ''
    lotAutoFromMaterial.value = true
    if (showSuccess) ElMessage.success('Lot draft berhasil digenerate.')
    return true
  } catch (e) {
    if (seq !== lotAutoSeq) return false
    if (showError) ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
    return false
  } finally {
    if (seq === lotAutoSeq) lotGenerateLoading.value = false
  }
}

async function generateLotNumber(forceDetailId = null) {
  const poId = editingPoId.value
  const isPersist = Boolean(poId && forceDetailId)
  if (!String(formModel.factory_code || '').trim()) {
    ElMessage.warning('Factory code wajib diisi sebelum generate lot.')
    return
  }
  const loadingFlag = isPersist ? saving : lotGenerateLoading
  loadingFlag.value = true
  try {
    if (isPersist) {
      await updatePo(poId, { factory_code: String(formModel.factory_code || '').trim() || null })
      const updated = await generatePoDetailLot(forceDetailId)
      if (Array.isArray(draftLines.value) && draftLines.value.length) {
        const i = draftLines.value.findIndex((d) => d && d.id === forceDetailId)
        if (i >= 0) draftLines.value[i].thi_line_ref = updated.thi_line_ref || undefined
      }
      if (editingDetailIds.value?.[0] === forceDetailId) {
        formModel.thi_line_ref = updated.thi_line_ref || ''
        lotAutoFromMaterial.value = true
      }
      ElMessage.success('Lot berhasil digenerate.')
      return
    }

    const ok = await autoGenerateLotFromMaterial({ showSuccess: true, showError: true })
    if (ok) lotAutoFromMaterial.value = true
  } finally {
    loadingFlag.value = false
  }
}

function applyReferenceDefaults(forceFields = []) {
  applyReferenceDefaultsFromMaster(formModel, masterItems.value, autoFieldMeta, forceFields)
}

function resetMaterialFieldOverride() {
  materialFieldOverride.material_name = false
  materialFieldOverride.thickness_text = false
  materialFieldOverride.color = false
  materialFieldOverride.color_family = false
  materialFieldOverride.emboss = false
  materialFieldOverride.style_article = false
}

function isMaterialFieldLocked(field) {
  if (!formModel.master_item_id) return false
  return !materialFieldOverride[field]
}

function enableMaterialOverride(field) {
  if (!formModel.master_item_id) return
  materialFieldOverride[field] = true
  if (field === 'color_family') colorFamilyAutoMode.value = false
}

function resetMaterialFieldToMaster(field) {
  resetMaterialFieldToMasterValues(
    field,
    formModel,
    masterItems.value,
    materialFieldOverride,
    colorFamilyAutoMode,
  )
}

function resetToAuto(field) {
  if (field === 'buyer') {
    const firstBuyer = buyerCodesFiltered.value[0]
    if (firstBuyer) {
      formModel.buyer = firstBuyer
      autoFieldMeta.buyer = true
    }
    return
  }

  if (field === 'factory_code') {
    const cust =
      selectedCustomer.value || customers.value.find((x) => x.id === formModel.customer_id) || null
    applyAutoFactoryCode(cust, { force: true })
    return
  }

  if (field === 'vir_softness_type') {
    formModel.vir_softness_type = ''
    autoFieldMeta.vir_softness_type = false
    applyVirSoftDefault()
    return
  }

  if (field === 'color_reference' || field === 'color_standard' || field === 'backing' || field === 'model') {
    if (formModel.master_item_id) {
      const item = masterItems.value.find((x) => x.id === formModel.master_item_id)
      if (item) {
        if (field === 'color_reference') {
          formModel.color_reference = item.color_reference || ''
          autoFieldMeta.color_reference = Boolean(item.color_reference)
        }
        if (field === 'color_standard') {
          formModel.color_standard = item.color_standard || ''
          autoFieldMeta.color_standard = Boolean(item.color_standard)
        }
        if (field === 'backing') {
          formModel.backing = item.backing || ''
          autoFieldMeta.backing = Boolean(item.backing)
        }
        if (field === 'model') {
          formModel.model = item.model || ''
          autoFieldMeta.model = Boolean(item.model)
        }
      }
      return
    }
    if (field === 'color_reference') formModel.color_reference = ''
    if (field === 'color_standard') formModel.color_standard = ''
    if (field === 'backing') formModel.backing = ''
    if (field === 'model') formModel.model = ''
    applyReferenceDefaults([field])
  }
}

watch(
  () => formModel.buyer,
  () => {
    formModel.vir_softness_type = ''
  autoFieldMeta.vir_softness_type = false
    previewResolvedUnitPrice.value = null
    schedulePricePreview()
    applyVirSoftDefault()
  },
)

watch(
  () => [
    formModel.material_name,
    formModel.color,
    formModel.style_article,
    formModel.thickness_text,
    formModel.color_family,
  ],
  () => {
    schedulePricePreview()
    applyReferenceDefaults()
  },
)

watch(
  () => formModel.color,
  (newColor) => {
    if (!colorFamilyAutoMode.value) return
    const inferred = inferColorFamilyFromColor(newColor)
    if (inferred) formModel.color_family = inferred
  },
)

watch(
  () => [formModel.color_family, formModel.buyer, formModel.order_date],
  () => {
    loadFluorescentOptions()
  },
)

watch(
  () => [formModel.customer_id, formModel.factory_code, formModel.buyer, formModel.material_name],
  () => {
    selectedSwatchId.value = null
    loadColorSwatchOptions()
  },
)

watch(
  () => formModel.po_category,
  (newCategory) => {
    const isSubkonOrRetur = newCategory === 'subcont' || newCategory === 'return'
    formModel.autoPricingEnabled = !isSubkonOrRetur
    if (isSubkonOrRetur) {
      formModel.unit_price_input = null
    }
  },
)

const formErrors = reactive({
  customer_id: '',
  brand_id: '',
  material_name: '',
  quantity_order: '',
})

function resetForm() {
  formModel.po_number = ''
  formModel.customer_id = null
  formModel.brand_id = null
  formModel.po_category = 'production'
  formModel.factory_code = ''
  autoFieldMeta.factory_code = false
  formModel.order_date = ''
  formModel.buyer = ''
  formModel.etd = ''
  formModel.po_customer_ref = ''
  formModel.remark = ''
  formModel.billing_address = ''
  formModel.delivery_address = ''
  formModel.status = 'draft'
  formModel.master_item_id = null
  formModel.material_name = ''
  formModel.thickness_text = ''
  formModel.color = ''
  formModel.color_family = null
  formModel.emboss = ''
  formModel.vir_softness_type = ''
  formModel.softness = ''
  formModel.color_reference = ''
  formModel.color_standard = ''
  formModel.backing = ''
  formModel.quantity_order = ''
  formModel.style_article = ''
  formModel.model = ''
  formModel.detail_remark = ''
  formModel.thi_line_ref = ''
  formModel.unit_price_input = null
  formModel.autoPricingEnabled = true
  formModel.is_special_price = false
  formModel.discount_type = 'percent'
  formModel.discount_value = 0
  autoFieldMeta.buyer = false
  autoFieldMeta.factory_code = false
  autoFieldMeta.vir_softness_type = false
  autoFieldMeta.softness = false
  autoFieldMeta.color_reference = false
  autoFieldMeta.color_standard = false
  autoFieldMeta.backing = false
  autoFieldMeta.model = false
  editingDetailIds.value = []
  draftLines.value = []
  editingDraftLineIndex.value = -1
  draftRiskOnly.value = false
  brandLockedCustomerId.value = null
  selectedCustomer.value = null
  previewResolvedUnitPrice.value = null
  fluorescentColorOptions.value = []
  ambiguousMasterVisible.value = false
  ambiguousMasterCandidates.value = []
  selectedAmbiguousMasterId.value = null
  lastResolveHadNoMaster.value = false
  skipMasterResolve.value = false
  loadedDetailMasterSnapshot.value = null
  thicknessDimensionOptions.value = []
  colorDimensionOptions.value = []
  colorFamilyAutoMode.value = true
  lotAutoFromMaterial.value = false
  materialAdvancedOpen.value = []
  resetMaterialFieldOverride()
  formErrors.customer_id = ''
  formErrors.brand_id = ''
  formErrors.material_name = ''
  formErrors.quantity_order = ''
  savedHeaderOrderDate.value = ''
  clearEtdScheduleRows()
}

function getPoDraftPayload() {
  return buildPoDraftPayload(formModel, etdScheduleRows.value, draftLines.value)
}

function savePoDraftToLocal() {
  savePoDraftLocalStorage(getPoDraftPayload())
}

function clearPoDraftLocal() {
  clearPoDraftLocalStorage()
}

function applyPoDraft(data) {
  applyPoDraftData(data, { formModel, autoFieldMeta, etdScheduleRows, draftLines })
}

async function restorePoDraftIfAny() {
  const raw = readPoDraftRaw()
  if (!raw) return
  try {
    await ElMessageBox.confirm(
      'Ditemukan draft input PO. Lanjutkan dari draft terakhir?',
      'Lanjutkan Draft PO',
      {
        type: 'info',
        confirmButtonText: 'Lanjutkan Draft',
        cancelButtonText: 'Mulai Baru',
      },
    )
    const parsed = JSON.parse(raw)
    applyPoDraft(parsed)
    if (formModel.customer_id) await onCustomerChange()
    if (formModel.brand_id) await onBrandChange(formModel.brand_id)
    ElMessage.success('Draft PO berhasil dimuat.')
    await refreshThicknessOptionsFromApi()
    await refreshColorOptionsFromApi()
    lastResolveHadNoMaster.value = false
  } catch (e) {
    if (e === 'cancel') {
      clearPoDraftLocal()
    }
  }
}

function requestCloseFormDialog() {
  handlePoDialogBeforeClose(() => {
    formDialogVisible.value = false
  })
}

async function handlePoDialogBeforeClose(done) {
  if (saving.value) {
    done()
    return
  }
  if (isEditMode.value) {
    done()
    return
  }
  try {
    await ElMessageBox.confirm(
      'Simpan draft PO sebelum menutup dialog?',
      'Konfirmasi Tutup',
      {
        type: 'warning',
        distinguishCancelAndClose: true,
        confirmButtonText: 'Simpan Draft',
        cancelButtonText: 'Tutup Tanpa Simpan',
      },
    )
    savePoDraftToLocal()
    ElMessage.success('Draft PO disimpan. Kamu bisa lanjutkan nanti.')
    done()
  } catch {
    clearPoDraftLocal()
    done()
  }
}

function saveDraftAndClose() {
  savePoDraftToLocal()
  ElMessage.success('Draft PO disimpan. Kamu bisa lanjutkan nanti.')
  formDialogVisible.value = false
}

async function onCustomerChange() {
  if (brandLockedCustomerId.value) {
    formModel.customer_id = brandLockedCustomerId.value
    return
  }
  formModel.brand_id = null
  brandBuyerCodes.value = []
  customerBuyerCodes.value = []
  formModel.buyer = ''
  allowedBrandIds.value = []
  const cid = formModel.customer_id
  if (cid) {
    try {
      const [allowed, customer] = await Promise.all([
        getAllowedBrands(cid),
        getCustomer(cid),
      ])
      allowedBrandIds.value = allowed.map((b) => b.id)
      selectedCustomer.value = customer || null
      if (allowedBrandIds.value.length > 0) {
        const stillValid = formModel.brand_id && allowedBrandIds.value.includes(formModel.brand_id)
        formModel.brand_id = stillValid ? formModel.brand_id : allowedBrandIds.value[0]
        await onBrandChange(formModel.brand_id)
      } else {
        formModel.brand_id = null
      }
      if (allowedBrandIds.value.length) {
        const buyersByBrand = await Promise.all(
          allowedBrandIds.value.map((id) => listBrandBuyers(id).catch(() => [])),
        )
        customerBuyerCodes.value = [
          ...new Set(
            buyersByBrand
              .flat()
              .map((x) => (x?.buyer_code || '').trim())
              .filter(Boolean),
          ),
        ]
        if (customerBuyerCodes.value.length > 0) {
          formModel.buyer = customerBuyerCodes.value[0]
          autoFieldMeta.buyer = true
        } else {
          formModel.buyer = ''
          autoFieldMeta.buyer = false
        }
      }
      if (customer) {
        applyAutoFactoryCode(customer)
        formModel.billing_address = customer.address || ''
        formModel.delivery_address = customer.address || ''
      }
    } catch {
      allowedBrandIds.value = []
      selectedCustomer.value = null
    }
  } else {
    formModel.billing_address = ''
    formModel.delivery_address = ''
    formModel.factory_code = ''
    autoFieldMeta.factory_code = false
    customerBuyerCodes.value = []
    selectedCustomer.value = null
  }
}

async function onBrandChange(brandId) {
  brandBuyerCodes.value = []
  brandLockedCustomerId.value = null
  if (!brandId) return
  try {
    const selectedBrand = brands.value.find((b) => b.id === brandId)
    if (selectedBrand?.customer_id) {
      brandLockedCustomerId.value = selectedBrand.customer_id
      formModel.customer_id = selectedBrand.customer_id
      const cust =
        selectedCustomer.value || customers.value.find((x) => x.id === selectedBrand.customer_id)
      if (cust) {
        selectedCustomer.value = cust
        applyAutoFactoryCode(cust)
      }
    }
    const rows = await listBrandBuyers(brandId)
    brandBuyerCodes.value = rows.map((x) => x.buyer_code).filter(Boolean)
    if (brandBuyerCodes.value.length) {
      if (!brandBuyerCodes.value.includes(formModel.buyer)) {
        formModel.buyer = brandBuyerCodes.value[0]
        autoFieldMeta.buyer = true
      }
    } else if (formModel.brand_id) {
      formModel.buyer = ''
      autoFieldMeta.buyer = false
    }
  } catch {
    brandBuyerCodes.value = []
  }
}

function upsertMasterItemInCache(row) {
  if (!row?.id) return
  const rows = masterItems.value
  const idx = rows.findIndex((x) => x.id === row.id)
  if (idx >= 0) rows[idx] = { ...rows[idx], ...row }
  else rows.push(row)
}

async function refreshMaterialDimensionOptions() {
  try {
    const r = await listMasterItemDimensionValues('materials')
    materialDimensionOptions.value = r.values || []
  } catch {
    materialDimensionOptions.value = []
  }
}

async function refreshThicknessOptionsFromApi() {
  const m = String(formModel.material_name || '').trim()
  if (!m) {
    thicknessDimensionOptions.value = []
    return
  }
  try {
    const r = await listMasterItemDimensionValues('thicknesses', { material_name: m })
    thicknessDimensionOptions.value = r.values || []
  } catch {
    thicknessDimensionOptions.value = []
  }
}

async function refreshColorOptionsFromApi() {
  const m = String(formModel.material_name || '').trim()
  const tt = String(formModel.thickness_text || '').trim()
  if (!m || !tt) {
    colorDimensionOptions.value = []
    return
  }
  try {
    const r = await listMasterItemDimensionValues('colors', { material_name: m, thickness_text: tt })
    colorDimensionOptions.value = r.values || []
  } catch {
    colorDimensionOptions.value = []
  }
}

async function onPickedMaterialDimension() {
  formModel.thickness_text = ''
  formModel.color = ''
  formModel.master_item_id = null
  formModel.thi_line_ref = ''
  lotAutoFromMaterial.value = false
  skipMasterResolve.value = false
  lastResolveHadNoMaster.value = false
  thicknessDimensionOptions.value = []
  colorDimensionOptions.value = []
  const m = String(formModel.material_name || '').trim()
  if (m) {
    await refreshThicknessOptionsFromApi()
    scheduleAutoLotGenerate()
  }
}

async function onPickedThicknessDimension() {
  formModel.color = ''
  formModel.master_item_id = null
  skipMasterResolve.value = false
  lastResolveHadNoMaster.value = false
  colorDimensionOptions.value = []
  const m = String(formModel.material_name || '').trim()
  const tt = String(formModel.thickness_text || '').trim()
  if (m && tt) await refreshColorOptionsFromApi()
}

function hydrateFormFromMasterItemRow(item, { syncDimensions = true } = {}) {
  if (syncDimensions) resetMaterialFieldOverride()
  applyMasterItemToForm(item, {
    formModel,
    autoFieldMeta,
    previewResolvedUnitPrice: previewResolvedUnitPrice.value,
    colorFamilyAutoMode,
    syncDimensions,
  })
}

function clearLinkedMasterItem() {
  formModel.master_item_id = null
  resetMaterialFieldOverride()
  skipMasterResolve.value = false
  lastResolveHadNoMaster.value = false
}

let masterResolveTimer = null
let masterResolveSeq = 0

async function resolveMasterFromDimensionsTriple() {
  if (ambiguousMasterVisible.value || skipMasterResolve.value) return
  const mn = String(formModel.material_name || '').trim()
  const tt = String(formModel.thickness_text || '').trim()
  const co = String(formModel.color || '').trim()
  const curSnap = detailMasterSnapshot(formModel)
  if (
    isEditMode.value &&
    editingPoId.value &&
    loadedDetailMasterSnapshot.value != null &&
    curSnap === loadedDetailMasterSnapshot.value
  ) {
    return
  }
  const seq = ++masterResolveSeq
  if (!mn || !tt || !co) {
    lastResolveHadNoMaster.value = false
    formModel.master_item_id = null
    return
  }
  masterResolveLoading.value = true
  try {
    const res = await resolveMasterItemByDimensions({ material_name: mn, thickness_text: tt, color: co })
    if (seq !== masterResolveSeq) return
    lastResolveHadNoMaster.value = res.status === 'none'
    if (res.status === 'single' && res.item) {
      upsertMasterItemInCache(res.item)
      resetMaterialFieldOverride()
      colorFamilyAutoMode.value = true
      formModel.master_item_id = res.item.id
      hydrateFormFromMasterItemRow(res.item, { syncDimensions: false })
      scheduleAutoLotGenerate()
    } else if (res.status === 'ambiguous' && (res.candidates || []).length) {
      formModel.master_item_id = null
      skipMasterResolve.value = true
      ambiguousMasterCandidates.value = res.candidates
      selectedAmbiguousMasterId.value = res.candidates[0]?.id ?? null
      ambiguousMasterVisible.value = true
    } else {
      formModel.master_item_id = null
    }
  } catch {
    if (seq !== masterResolveSeq) return
    lastResolveHadNoMaster.value = true
    formModel.master_item_id = null
  } finally {
    if (seq === masterResolveSeq) masterResolveLoading.value = false
  }
}

function confirmAmbiguousMasterPick() {
  const id = selectedAmbiguousMasterId.value
  const c = ambiguousMasterCandidates.value.find((x) => x.id === id)
  if (!c) return
  upsertMasterItemInCache(c)
  formModel.master_item_id = c.id
  skipMasterResolve.value = false
  ambiguousMasterVisible.value = false
  resetMaterialFieldOverride()
  colorFamilyAutoMode.value = true
  hydrateFormFromMasterItemRow(c, { syncDimensions: false })
  lastResolveHadNoMaster.value = false
  scheduleAutoLotGenerate()
}

watch(
  () => [
    formModel.factory_code,
    formModel.po_category,
    formModel.master_item_id,
    formModel.vir_softness_type,
  ],
  () => scheduleAutoLotGenerate(),
)

watch(
  () => [formModel.material_name, formModel.thickness_text, formModel.color],
  () => {
    skipMasterResolve.value = false
    clearTimeout(masterResolveTimer)
    masterResolveTimer = setTimeout(() => {
      void resolveMasterFromDimensionsTriple()
    }, 420)
  },
)

watch(ambiguousMasterVisible, (open) => {
  if (!open && !formModel.master_item_id && materialThicknessColorComplete.value) {
    skipMasterResolve.value = true
  }
})

const openCreateDialog = async () => {
  isEditMode.value = false
  editingPoId.value = null
  resetForm()
  brandLockedCustomerId.value = null
  currentStep.value = 0
  formDialogVisible.value = true
  pauseLotAutoBriefly()
  void refreshNextPoNumberPreview()
  await restorePoDraftIfAny()
}

async function buildCurrentDetailBody() {
  const body = buildDetailBodyCore(formModel, etdScheduleRows.value, selectedSwatchId.value)
  return appendDetailUnitPrice(body, formModel, {
    resolveBuyerUnitPrice,
    previewResolvedUnitPrice: previewResolvedUnitPrice.value,
  })
}

function handleEnterKey(e) {
  if (e.ctrlKey || e.metaKey) {
    pushCurrentLine(false)
  }
}

async function pushCurrentLine(copyCurrent = false) {
  formErrors.material_name = ''
  formErrors.quantity_order = ''

  if (!copyCurrent) {
    if (!formModel.material_name && !formModel.master_item_id) {
      formErrors.material_name = t('pages.po.materialRequired')
      ElMessage.warning(t('pages.po.materialRequired'))
      return
    }
    if (!formModel.quantity_order) {
      formErrors.quantity_order = t('pages.po.qtyRequired')
      ElMessage.warning(t('pages.po.qtyRequired'))
      return
    }
    if (pricingKeyIncomplete.value) {
      ElMessage.warning('Untuk buyer pricing, material, ketebalan, dan kategori warna wajib terisi.')
      return
    }
    if (!isThicknessPricingFormatValid(formModel.thickness_text)) {
      ElMessage.warning('Format ketebalan harus angka tunggal (contoh: 1.4) atau rentang (contoh: 1.2-1.4).')
      return
    }
    if (!isSelectedFluorescentColorValid()) {
      ElMessage.warning('Warna fluorescent wajib dipilih dari master fluorescent sesuai buyer/season.')
      return
    }
  }

  const line = await buildCurrentDetailBody()
  if (formModel.buyer?.trim() && line.unit_price == null) {
    ElMessage.warning(t('pages.po.priceNotFound'))
  }
  const hasAutoPrice = previewResolvedUnitPrice.value != null
  const isManualOverride =
    hasAutoPrice &&
    line.unit_price != null &&
    Number(line.unit_price) !== Number(previewResolvedUnitPrice.value)
  const hasMaterialOverride = Object.values(materialFieldOverride).some(Boolean)
  line.manual_override = Boolean(isManualOverride)
  line.material_master_override = Boolean(hasMaterialOverride)
  line.material_master_matched = Boolean(line.master_item_id) && !hasMaterialOverride
  if (
    line.unit_price != null &&
    previewResolvedUnitPrice.value != null &&
    Number(line.unit_price) !== Number(previewResolvedUnitPrice.value) &&
    !String(formModel.detail_remark || '').trim()
  ) {
    ElMessage.warning('Jika harga diubah manual, mohon isi Detail Remark sebagai alasan override harga.')
    return
  }
  draftLines.value.push({ ...line })
  if (!copyCurrent) {
    formModel.master_item_id = null
    formModel.material_name = ''
    formModel.thickness_text = ''
    formModel.color = ''
    formModel.color_family = null
    formModel.emboss = ''
    formModel.vir_softness_type = ''
    formModel.softness = ''
    autoFieldMeta.softness = false
    formModel.color_reference = ''
    autoFieldMeta.color_reference = false
    formModel.color_standard = ''
    autoFieldMeta.color_standard = false
    formModel.backing = ''
    autoFieldMeta.backing = false
    formModel.quantity_order = ''
    formModel.style_article = ''
    formModel.model = ''
    autoFieldMeta.model = false
    formModel.detail_remark = ''
    formModel.thi_line_ref = ''
    clearEtdScheduleRows()
    resetMaterialFieldOverride()
    colorFamilyAutoMode.value = true
    lastResolveHadNoMaster.value = false
    thicknessDimensionOptions.value = []
    colorDimensionOptions.value = []
    formErrors.material_name = ''
    formErrors.quantity_order = ''
    scheduleAutoLotGenerate()
  }
}

function removeDraftLine(index) {
  draftLines.value.splice(index, 1)
}

const openEditDialog = async (row) => {
  isEditMode.value = true
  editingPoId.value = row.id
  resetForm()
  savedHeaderOrderDate.value = row.order_date ? String(row.order_date).slice(0, 10) : ''
  formModel.po_number = row.po_number || ''
  formModel.customer_id = row.customer_id
  formModel.brand_id = row.brand_id ?? null
  formModel.po_category = row.po_category || 'production'
  formModel.factory_code = row.factory_code || ''
  autoFieldMeta.factory_code = false
  formModel.order_date = row.order_date ? String(row.order_date).slice(0, 10) : ''
  formModel.buyer = row.buyer || ''
  formModel.etd = row.etd ? String(row.etd).slice(0, 10) : ''
  formModel.po_customer_ref = row.po_customer_ref || ''
  formModel.remark = row.remark || ''
  formModel.billing_address = row.billing_address || ''
  formModel.delivery_address = row.delivery_address || ''
  formModel.status = row.status || 'draft'
  try {
    selectedCustomer.value = formModel.customer_id ? await getCustomer(formModel.customer_id) : null
  } catch {
    selectedCustomer.value = null
  }
  if (!String(formModel.factory_code || '').trim() && selectedCustomer.value) {
    applyAutoFactoryCode(selectedCustomer.value, { force: true })
  }
  pauseLotAutoBriefly()
  await onBrandChange(formModel.brand_id)
  schedulePricePreview()
  try {
    const details = await listPoDetails(row.id)
    const scheduleLists = await Promise.all(
      details.map((d) => listPoDetailDeliverySchedules(d.id).catch(() => [])),
    )
    draftLines.value = details.map((d, idx) => ({
      id: d.id,
      master_item_id: d.master_item_id || undefined,
      material_name: d.material_name || undefined,
      thickness_text: d.thickness_text || undefined,
      color: d.color || undefined,
      color_family: d.color_family || undefined,
      emboss: d.emboss || undefined,
      vir_softness_type: d.vir_softness_type || undefined,
      softness: d.softness || undefined,
      color_reference: d.color_reference || undefined,
      color_standard: d.color_standard || undefined,
      backing: d.backing || undefined,
      quantity_order: d.quantity_order != null ? Number(d.quantity_order) : undefined,
      style_article: d.style_article || undefined,
      model: d.model || undefined,
      detail_remark: d.detail_remark || undefined,
      thi_line_ref: d.thi_line_ref || undefined,
      color_swatch_recipe_id: d.color_swatch_recipe_id || undefined,
      unit_price: d.unit_price != null ? Number(d.unit_price) : undefined,
      delivery_schedules: normalizeSchedulesFromApi(scheduleLists[idx]),
      manual_override: false,
      material_master_override: false,
      material_master_matched: Boolean(d.master_item_id),
    }))
    editingDetailIds.value = details.map((d) => d.id)
    const d0 = details[0]
    if (d0) {
      formModel.master_item_id = d0.master_item_id
      formModel.material_name = d0.material_name || ''
      formModel.thickness_text = d0.thickness_text || ''
      formModel.color = d0.color || ''
      formModel.color_family = d0.color_family || null
      formModel.emboss = d0.emboss || ''
      formModel.vir_softness_type = d0.vir_softness_type || ''
      formModel.softness = d0.softness || ''
      formModel.color_reference = d0.color_reference || ''
      formModel.color_standard = d0.color_standard || ''
      formModel.backing = d0.backing || ''
      formModel.quantity_order = d0.quantity_order != null ? String(d0.quantity_order) : ''
      formModel.style_article = d0.style_article || ''
      formModel.model = d0.model || ''
      formModel.detail_remark = d0.detail_remark || ''
      formModel.thi_line_ref = d0.thi_line_ref || ''
      etdScheduleRows.value = loadEtdScheduleRowsFromApi(scheduleLists[0] || [])
      editingDraftLineIndex.value = 0
      loadedDetailMasterSnapshot.value = `${String(d0.material_name || '').trim()}|${String(d0.thickness_text || '').trim()}|${String(d0.color || '').trim()}|${d0.master_item_id ?? ''}`
      if (d0.master_item_id) {
        const cacheIt = masterItems.value.find((x) => x.id === d0.master_item_id)
        if (cacheIt) upsertMasterItemInCache(cacheIt)
      }
      await refreshThicknessOptionsFromApi()
      await refreshColorOptionsFromApi()
      lastResolveHadNoMaster.value = false
    } else {
      loadedDetailMasterSnapshot.value = null
    }
  } catch {
    editingDetailIds.value = []
    draftLines.value = []
    loadedDetailMasterSnapshot.value = null
  }
  formDialogVisible.value = true
}

const submitForm = async () => {
  if (!formModel.customer_id) {
    ElMessage.warning(t('pages.po.pickCustomerWarning'))
    return
  }
  if (!isSelectedFluorescentColorValid()) {
    ElMessage.warning('Warna fluorescent wajib dipilih dari master fluorescent sesuai buyer/season.')
    return
  }
  saving.value = true
  try {
    const header = {
      po_number: isEditMode.value ? formModel.po_number?.trim() || undefined : undefined,
      customer_id: formModel.customer_id,
      brand_id: formModel.brand_id || undefined,
      buyer: formModel.buyer || undefined,
      po_category: formModel.po_category,
      factory_code: formModel.factory_code?.trim() || undefined,
      etd: toIsoDate(formModel.etd) || undefined,
      po_customer_ref: formModel.po_customer_ref?.trim() || undefined,
      remark: formModel.remark || undefined,
      billing_address: formModel.billing_address?.trim() || undefined,
      delivery_address: formModel.delivery_address?.trim() || undefined,
      status: formModel.status,
    }
    if (!orderDateLocked.value) {
      header.order_date = toIsoDate(formModel.order_date) || undefined
    }
    const detailBodies = draftLines.value.length ? draftLines.value : [await buildCurrentDetailBody()]
    if (editingDraftLineIndex.value >= 0) {
      await syncCurrentFormToDraftLine()
    }
    const bodiesFinal = draftLines.value.length ? draftLines.value : [await buildCurrentDetailBody()]
    await validateFluorescentLinesOrThrow(bodiesFinal)
    const mismatchLines = bodiesFinal.filter((b) => lineHasScheduleMismatch(b))
    if (mismatchLines.length) {
      ElMessage.warning(t('pages.po.scheduleMismatchWarn'))
    }

    if (isEditMode.value && editingPoId.value) {
      await updatePo(editingPoId.value, header)
      const keepIds = []
      for (let i = 0; i < bodiesFinal.length; i += 1) {
        const rowBody = { ...sanitizeNewDetailBody(bodiesFinal[i]) }
        const schedules = rowBody.delivery_schedules || []
        delete rowBody.delivery_schedules
        const existingId = editingDetailIds.value[i]
        if (existingId) {
          await updatePoDetail(existingId, detailPayloadForUpdate(rowBody))
          await saveDetailSchedules(existingId, schedules)
          keepIds.push(existingId)
        } else {
          const createdDetail = await addPoDetail(editingPoId.value, rowBody)
          await saveDetailSchedules(createdDetail.id, schedules)
          keepIds.push(createdDetail.id)
        }
      }
      const staleIds = editingDetailIds.value.filter((id) => !keepIds.includes(id))
      for (const staleId of staleIds) {
        await deletePoDetail(staleId)
      }
    } else {
      const created = await createPo(header)
      for (const raw of bodiesFinal) {
        const rowBody = { ...sanitizeNewDetailBody(raw) }
        const schedules = rowBody.delivery_schedules || []
        delete rowBody.delivery_schedules
        const createdDetail = await addPoDetail(created.id, rowBody)
        await saveDetailSchedules(createdDetail.id, schedules)
      }
    }
    ElMessage.success(t('pages.customers.saved'))
    clearPoDraftLocal()
    formDialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
  } finally {
    saving.value = false
  }
}

providePoWizardContext({
  formDialogVisible,
  formModel,
  formErrors,
  currentStep,
  isEditMode,
  canManage,
  nextPoNumberDisplay,
  customers,
  formatCustomerOption,
  brandLockedCustomerId,
  onCustomerChange,
  customerPicDisplay,
  brandsFiltered,
  onBrandChange,
  isBrandDisabled,
  buyerCodesFiltered,
  isBuyerDisabled,
  autoFieldMeta,
  resetToAuto,
  isPoCategoryDisabled,
  orderDateLocked,
  brands,
  materialDimensionOptions,
  onPickedMaterialDimension,
  thicknessDimensionOptions,
  onPickedThicknessDimension,
  isFluorescentFamily,
  poColorCascadeOptions,
  colorDimensionOptions,
  enableMaterialOverride,
  isMaterialFieldLocked,
  materialFieldOverride,
  resetMaterialFieldToMaster,
  activeSeasonLabel,
  fluorescentColorOptions,
  selectedSwatchId,
  colorSwatchLoading,
  colorSwatchOptions,
  swatchOptionLabel,
  poFactoryKeyForSwatch,
  applyColorSwatch,
  swatchAllMaterials,
  loadColorSwatchOptions,
  swatchRetriedWithoutMaterial,
  masterResolveLoading,
  resolvedMasterItemLabel,
  clearLinkedMasterItem,
  lastResolveHadNoMaster,
  materialThicknessColorComplete,
  colorFamilyAutoMode,
  materialAdvancedOpen,
  pricingKeyIncomplete,
  etdScheduleOpen,
  etdScheduleRows,
  clearEtdScheduleRows,
  autoFillEtdScheduleWave1,
  autoFillEtdScheduleEvenly,
  etdScheduleTotalDisplay,
  etdScheduleMismatch,
  draftLinesDisplay,
  draftLines,
  draftRiskOnly,
  draftRowClassName,
  pushCurrentLine,
  openCopyItemDialog,
  colorFamilyLabel,
  materialQualityTooltip,
  materialQualityType,
  materialQualityLabel,
  hasSpecialPriceInLines,
  generateLotNumber,
  removeDraftLine,
  editDraftLine,
  previewResolvedUnitPrice,
  onSpecialPriceChange,
  calculateSpecialPrice,
  lotGenerateLoading,
  lotAutoFromMaterial,
  handleEnterKey,
  handlePoDialogBeforeClose,
  requestCloseFormDialog,
  openMarketingReviseDialog,
  nextStep,
  prevStep,
  submitForm,
  saveDraftAndClose,
  saving,
})

const detailDialogVisible = ref(false)
const detailView = ref(null)
const detailLines = ref([])
const detailAudit = ref([])

const openDetailDialog = async (row) => {
  detailView.value = { ...row, customerName: row.customerName }
  detailLines.value = []
  detailAudit.value = []
  try {
    detailLines.value = await listPoDetails(row.id)
  } catch {
    detailLines.value = []
  }
  try {
    const logsHeader = await listAuditLogs({ entity_type: 'sales_order', entity_id: row.id, limit: 120 })
    const lineLogsLists = await Promise.all(
      detailLines.value.map((d) =>
        listAuditLogs({ entity_type: 'sales_order_line', entity_id: d.id, limit: 60 }).catch(() => []),
      ),
    )
    const merged = [...logsHeader, ...lineLogsLists.flat()]
    merged.sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))
    detailAudit.value = merged
  } catch {
    detailAudit.value = []
  }
  detailDialogVisible.value = true
}

const printDialogVisible = ref(false)
const selectedRow = reactive({})

const openPrintDialog = (row) => {
  Object.assign(selectedRow, row)
  printDialogVisible.value = true
}

const printPage = () => window.print()

const removeRow = async (row) => {
  try {
    await ElMessageBox.confirm(
      t('pages.po.deleteConfirm', { poNumber: row.po_number }),
      t('pages.po.deleteTitle'),
      {
        type: 'warning',
        distinguishCancelAndClose: true,
        confirmButtonText: t('common.delete'),
        cancelButtonText: t('common.cancel'),
      },
    )
    await deletePo(row.id)
    ElMessage.success(t('pages.po.deleted'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadSalesContractPdf(row) {
  if (!row?.id) return
  try {
    await fetchAuthenticatedDocument(salesContractPdfPath(row.id), {
      mode: 'download',
      downloadFallbackName: `sales_contract_${row.po_number || row.id}.pdf`,
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadSalesContractDocx(row) {
  if (!row?.id) return
  try {
    await fetchAuthenticatedDocument(salesContractDocxPath(row.id), {
      mode: 'download',
      downloadFallbackName: `sales_contract_${row.po_number || row.id}.docx`,
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function openExportHint() {
  ElMessage.info(t('pages.po.exportHint'))
}

async function onDuplicatePo(row) {
  const poNo = row.po_number || `#${row.id}`
  try {
    await ElMessageBox.confirm(
      t('pages.po.duplicatePoConfirm', { poNumber: poNo }),
      t('pages.po.duplicatePo'),
      {
        type: 'info',
        distinguishCancelAndClose: true,
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
      },
    )
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
    return
  }
  try {
    const created = await duplicatePo(row.id)
    await load()
    const nr = rows.value.find((r) => Number(r.id) === Number(created.id))
    ElMessage.success(t('pages.po.duplicatePoSuccess', { poNumber: created.po_number || created.id }))
    if (nr) await openEditDialog(nr)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function openCopyItemDialog() {
  copyItemCustomerId.value = formModel.customer_id
  copyItemSelected.value = []
  copyItemSourcePo.value = []
  if (copyItemCustomerId.value) {
    await loadCopyItemSourcePos()
  }
  copyItemDialogVisible.value = true
}

async function loadCopyItemSourcePos() {
  if (!copyItemCustomerId.value) {
    copyItemSourcePo.value = []
    return
  }
  try {
    const pos = await listPoForCopy({ customer_id: copyItemCustomerId.value })
    const otherPos = pos.filter(p => p.id !== editingPoId.value)
    const allDetails = await Promise.all(
      otherPos.map(p => listPoDetails(p.id).catch(() => []))
    )
    copyItemSourcePo.value = allDetails.flat().map(d => ({
      ...d,
      source_po_number: otherPos.find(p => p.id === d.po_id)?.po_number
    }))
  } catch {
    copyItemSourcePo.value = []
  }
}

async function onCopyItemCustomerChange(id) {
  copyItemCustomerId.value = id ?? null
  await loadCopyItemSourcePos()
}

function onCopyItemSelectionChange(selection) {
  copyItemSelected.value = selection
}

function addCopiedItems() {
  const newLines = copyItemSelected.value.map(d => ({
    master_item_id: d.master_item_id,
    material_name: d.material_name,
    thickness_text: d.thickness_text,
    color: d.color,
    color_family: d.color_family,
    emboss: d.emboss,
    vir_softness_type: d.vir_softness_type,
    softness: d.softness,
    color_reference: d.color_reference,
    color_standard: d.color_standard,
    backing: d.backing,
    quantity_order: d.quantity_order,
    style_article: d.style_article,
    model: d.model,
    detail_remark: d.detail_remark,
    thi_line_ref: d.thi_line_ref,
    unit_price: d.unit_price,
    manual_override: false,
    material_master_override: false,
    material_master_matched: Boolean(d.master_item_id),
    copied_from_detail_id: d.id
  }))
  draftLines.value.push(...newLines)
  copyItemDialogVisible.value = false
  ElMessage.success(t('pages.po.itemsCopied', { count: newLines.length }))
}
</script>

<style scoped>
.admin-table {
  width: 100%;
}

.po-row-actions {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 2px 4px;
}

</style>
