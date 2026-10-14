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
      <el-button :icon="Refresh" :loading="loading" @click="load">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreateDialog">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.po.listTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.po.listSubtitle') }}</p>
        </div>
      </div>

      <div class="admin-action-bar">
        <p class="admin-action-bar__hint">{{ t('pages.po.exportListHint') }}</p>
        <div class="admin-action-bar__buttons">
          <el-button :icon="Download" :loading="exportLoading" @click="exportPoList">{{ t('common.export') }} CSV</el-button>
        </div>
      </div>

      <div class="mkt-section-body">
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
                multiple
                collapse-tags
                collapse-tags-tooltip
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
            <el-form-item>
              <template #label>
                <span class="form-label-with-hint">
                  {{ t('common.status') }}
                  <el-tooltip placement="top" :show-after="200">
                    <template #content>{{ t('pages.po.statusLegend') }}</template>
                    <el-icon class="form-label-hint" :size="14" tabindex="0" :aria-label="t('pages.po.statusLegend')">
                      <InfoFilled />
                    </el-icon>
                  </el-tooltip>
                </span>
              </template>
              <el-select v-model="filterStatus" clearable class="w-full" :placeholder="t('common.status')">
                <el-option :label="t('status.draft')" value="draft" />
                <el-option :label="t('status.confirmed')" value="confirmed" />
                <el-option :label="t('status.production')" value="production" />
                <el-option :label="t('status.completed')" value="completed" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8" :lg="4">
            <el-form-item :label="t('common.category')">
              <el-select v-model="filterPoCategory" clearable class="w-full" :placeholder="t('common.category')">
                <el-option :label="t('status.production')" value="production" />
                <el-option :label="t('status.sample')" value="sample" />
                <el-option :label="t('status.claim')" value="claim" />
                <el-option :label="t('status.return')" value="return" />
                <el-option :label="t('status.subcont')" value="subcont" />
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
                :start-placeholder="t('common.placeholder.fromDate')"
                :end-placeholder="t('common.placeholder.toDate')"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="8" :md="6" :lg="4" class="po-filter-action-col">
            <el-form-item label="&nbsp;">
              <el-button class="w-full" :icon="RefreshLeft" @click="resetFilter">{{ t('common.reset') }}</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      </div>

      <div class="po-column-toggle mb-3">
        <el-switch v-model="poShowAllColumns" size="small" />
        <span class="text-sm text-slate-600">{{ t('pages.po.showAllColumns') }}</span>
      </div>

      <p class="admin-scroll-hint mb-3">{{ t('pages.po.scrollHint') }}</p>

      <div class="admin-table-scroll">
    <el-table
      :data="filteredRows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table po-list-table"
      table-layout="fixed"
      :row-class-name="poRowClassName"
      :empty-text="t('pages.po.tableEmpty')"
      @sort-change="onSortChange"
    >
      <el-table-column
        type="index"
        :label="t('common.noLabel')"
        width="56"
        align="center"
        :index="(i) => (page - 1) * pageSize + i + 1"
      />
      <el-table-column prop="order_date" :label="t('common.orderDate')" width="112" align="center" sortable="custom">
        <template #default="{ row }">{{ row.order_date_fmt }}</template>
      </el-table-column>
      <el-table-column prop="po_number" :label="t('common.poNo')" min-width="160" show-overflow-tooltip sortable="custom">
        <template #default="{ row }">
          <div class="flex flex-wrap items-center gap-1">
            <span>{{ row.po_number || t('common.emptyValue') }}</span>
            <el-tag v-if="!row.detail_line_count" size="small" type="warning" effect="plain">
              {{ t('pages.po.noDetailLines') }}
            </el-tag>
            <el-tooltip v-if="row.mrp_sync_error" :content="row.mrp_sync_error" placement="top">
              <el-tag size="small" type="danger" effect="plain">{{ t('pages.po.mrpSyncError') }}</el-tag>
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
      <el-table-column
        prop="lot_hint"
        :label="t('pages.marketingFlow.colLotNo')"
        min-width="140"
        show-overflow-tooltip
      >
        <template #default="{ row }">{{ row.lot_hint || t('common.emptyValue') }}</template>
      </el-table-column>
      <el-table-column prop="po_customer_ref" :label="t('pages.po.poCustomerRef')" min-width="140" show-overflow-tooltip />
      <el-table-column prop="customerName" :label="t('common.customer')" min-width="200" show-overflow-tooltip />
      <el-table-column prop="brand_name_snapshot" :label="t('pages.po.brand')" min-width="120" show-overflow-tooltip />
      <el-table-column :label="t('common.material')" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.material_hint }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="po_category" :label="t('common.category')" min-width="110" align="center">
        <template #default="{ row }">
          <el-tag size="small" type="info" effect="plain">{{ categoryLabel(row.po_category) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column
        v-if="poShowAllColumns"
        prop="delivery_address"
        :label="t('pages.po.deliveryAddress')"
        min-width="160"
        show-overflow-tooltip
      />
      <el-table-column
        v-if="poShowAllColumns"
        :label="t('pages.marketingFlow.materialFollowUp')"
        min-width="150"
        show-overflow-tooltip
      >
        <template #default="{ row }">
          <div class="flex flex-wrap items-center gap-1">
            <el-tag
              v-if="materialFollowUpAutoStatus(row.mkt_workflow_stage) === 'done'"
              size="small"
              type="success"
              effect="plain"
            >{{ t('pages.marketingFlow.materialDoneAuto.done') }}</el-tag>
            <el-tag
              v-else-if="materialFollowUpAutoStatus(row.mkt_workflow_stage) === 'in_progress'"
              size="small"
              type="warning"
              effect="plain"
            >{{ t('pages.marketingFlow.materialDoneAuto.in_progress') }}</el-tag>
            <el-tag
              v-else-if="materialFollowUpAutoStatus(row.mkt_workflow_stage) === 'pending'"
              size="small"
              type="info"
              effect="plain"
            >{{ t('pages.marketingFlow.materialDoneAuto.pending') }}</el-tag>
            <el-tag v-else size="small" type="info" effect="plain">{{ t('pages.marketingFlow.materialDoneAuto.idle') }}</el-tag>
            <span v-if="row.material_followup_remark" class="text-xs text-slate-700">{{ row.material_followup_remark }}</span>
            <span v-else class="text-xs text-slate-400">—</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column
        v-if="poShowAllColumns"
        :label="t('pages.marketingFlow.stuckReason')"
        min-width="140"
        show-overflow-tooltip
      >
        <template #default="{ row }">
            <el-tag v-if="row.stuck_reason" type="warning" size="small" effect="plain">{{ labelStuckReason(row.stuck_reason) }}</el-tag>
          <span v-else class="text-slate-400 text-xs">—</span>
        </template>
      </el-table-column>
      <el-table-column
        v-if="poShowAllColumns"
        prop="mkt_workflow_stage"
        :label="t('pages.po.mktFlow')"
        min-width="140"
        show-overflow-tooltip
      >
        <template #default="{ row }">{{ labelMktStage(row.mkt_workflow_stage) }}</template>
      </el-table-column>
      <el-table-column prop="status" :label="t('common.status')" width="140" align="center" sortable="custom">
        <template #header>
          <el-tooltip :content="t('pages.po.statusColumnHint')" placement="top">
            <span>{{ t('common.status') }}</span>
          </el-tooltip>
        </template>
        <template #default="{ row }">
          <el-tooltip
            v-if="canUpdate"
            :content="
              row.status === 'draft'
                ? t('pages.po.statusConfirmViaWizard')
                : t('pages.po.statusEditViaForm')
            "
            placement="top"
          >
            <el-tag :type="statusType(row.status)" size="small">
              {{ poStatusLabel(row.status) }}
            </el-tag>
          </el-tooltip>
          <el-tag v-else :type="statusType(row.status)" size="small">
            {{ poStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column
        :label="t('common.actions')"
        width="136"
        align="center"
        fixed="right"
        class-name="po-actions-col"
        :show-overflow-tooltip="false"
      >
        <template #default="{ row }">
          <AdminTableActions
            :show-view="true"
            :show-edit="canUpdate"
            :show-delete="canDelete"
            :more-items="poMoreItems"
            :more-aria-label="t('pages.po.moreActions')"
            @view="openDetailDialog(row)"
            @edit="openEditDialog(row)"
            @delete="removeRow(row)"
            @more="(cmd) => handlePoMoreAction(row, cmd)"
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
        layout="total, sizes, prev, pager, next"
        :total="totalRows"
        :page-sizes="[20, 50, 100, 200]"
      />
    </div>
      </div>
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
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Download,
  Refresh,
  RefreshLeft,
  CopyDocument,
  InfoFilled,
  Tickets,
  Memo,
} from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import PoFormWizardDialog from '../../components/admin/PoFormWizardDialog.vue'
import PoAmbiguousMasterDialog from '../../components/admin/PoAmbiguousMasterDialog.vue'
import PoCopyItemDialog from '../../components/admin/PoCopyItemDialog.vue'
import PoDetailDialog from '../../components/admin/PoDetailDialog.vue'
import PoMarketingReviseDialog from '../../components/admin/PoMarketingReviseDialog.vue'
import { usePoFormWizard } from '../../composables/usePoFormWizard.js'
import { usePoList } from '../../composables/usePoList.js'
import { useModulePermission } from '../../composables/useModulePermission.js'
import { statusType } from '../../utils/format'
import { parseApiErrorMessage } from '../../utils/poApi.js'
import { fromElSortChange } from '../../utils/tableQuery'
import { stuckReasonLabel } from '../../utils/mktStuckReason.js'
import { createMktStageLabels, materialFollowUpAutoStatus, mktStageLabel } from '../../utils/mktStage.js'
import {
  downloadPoListCsv,
  poOrderCategoryLabel,
  mergeExtraBuyerCodes,
  mergePoMaterialHints,
  parsePoRoutePoId,
  poRouteQueryWithoutDeepLink,
  resolvePoDeepLinkRow,
  shouldOpenPoRouteEdit,
} from '../../utils/poList.js'
import {
  deletePo,
  duplicatePo,
  fetchAuthenticatedDocument,
  getPo,
  listPoAuditLogs,
  listBrands,
  listBuyerPriceLists,
  listCustomers,
  listMasterItemDimensionValues,
  listPoDetails,
  listPoPage,
  fetchPoMaterialHints,
  proformaInvoiceDocxPath,
  proformaInvoicePdfPath,
} from '../../api/client'

const { t, te } = useI18n()
const route = useRoute()
const router = useRouter()
const { canCreate, canUpdate, canDelete } = useModulePermission('po')
const highlightPoId = ref(null)

const {
  keyword,
  filterCustomerId,
  filterStatus,
  filterBuyer,
  filterOrderDateRange,
  filterPoCategory,
  rows,
  totalRows,
  page,
  pageSize,
  sortBy,
  sortDir,
  loading,
  poOrderDateShortcuts,
  buildPageQuery,
  enrichHeaders,
  resetFilters,
  registerFilterWatch,
} = usePoList({ t })

const customers = ref([])
const brands = ref([])
const masterItems = ref([])
const buyerCodes = ref(['NB', 'ADIDAS', 'NIKE', 'UA'])
const poShowAllColumns = ref(false)
const exportLoading = ref(false)
const mktStageLabels = computed(() => createMktStageLabels(t))

function labelMktStage(stage) {
  return mktStageLabel(stage, mktStageLabels.value, t('common.emptyValue'))
}

let wizard
async function load() {
  loading.value = true
  try {
    const [cust, br, bpl, poPage, dimMat] = await Promise.all([
      listCustomers(),
      listBrands(),
      listBuyerPriceLists().catch(() => []),
      listPoPage(buildPageQuery()),
      listMasterItemDimensionValues('materials', { category: 'PU' }).catch(() => ({ values: [] })),
    ])
    customers.value = cust
    brands.value = br
    wizard.materialDimensionOptions.value = dimMat.values || []
    buyerCodes.value = mergeExtraBuyerCodes(buyerCodes.value, bpl?.items || bpl)
    let items = poPage.items || []
    items = await enrichPoRowsWithHints(items)
    rows.value = enrichHeaders(items, cust, br)
    totalRows.value = Number(poPage.total || 0)
  } catch (e) {
    ElMessage.error(e.message || t('pages.po.loadFailed'))
  } finally {
    loading.value = false
  }
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy
  sortDir.value = mapped.sortDir
  page.value = 1
  load()
}

wizard = usePoFormWizard({ t, canCreate, canUpdate, customers, brands, masterItems, buyerCodes, load })

const {
  openCreateDialog,
  openEditDialog,
  formatCustomerOption,
  colorFamilyLabel,
  marketingReviseVisible,
  marketingReviseLoading,
  marketingReviseSaving,
  marketingReviseHeader,
  marketingReviseLines,
  submitMarketingRevise,
  copyItemDialogVisible,
  copyItemCustomerId,
  copyItemSearch,
  copyItemSourcePo,
  copyItemFilteredPo,
  copyItemSelected,
  onCopyItemCustomerChange,
  onCopyItemSelectionChange,
  addCopiedItems,
  ambiguousMasterVisible,
  ambiguousMasterCandidates,
  selectedAmbiguousMasterId,
  confirmAmbiguousMasterPick,
} = wizard

function labelStuckReason(reason) {
  return stuckReasonLabel(reason, t, t('common.emptyValue'))
}

async function enrichPoRowsWithHints(items) {
  if (!items?.length) return items
  const needsHints = items.some((h) => {
    if (h.id == null) return false
    const missingMaterial = !(String(h.material_hint || '').trim())
    const missingEtd = !(String(h.etd_display || '').trim()) && !h.etd
    return missingMaterial || missingEtd
  })
  if (!needsHints) return items
  try {
    const hintResp = await fetchPoMaterialHints(items.map((h) => h.id))
    return mergePoMaterialHints(items, hintResp.items || [])
  } catch {
    return items
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

  if (shouldOpenPoRouteEdit(route)) {
    await openEditDialog(target)
  } else {
    highlightPoId.value = poId
  }

  const nextQuery = poRouteQueryWithoutDeepLink(route)
  if (JSON.stringify(nextQuery) !== JSON.stringify(route.query || {})) {
    await router.replace({ path: route.path, query: nextQuery })
  }
}

function poRowClassName({ row }) {
  return Number(row.id) === Number(highlightPoId.value) ? 'po-row-highlight' : ''
}

const filteredRows = computed(() => rows.value)
const resetFilter = () => resetFilters(load)

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
    detailAudit.value = await listPoAuditLogs(row.id, { limit: 300 })
  } catch {
    detailAudit.value = []
  }
  detailDialogVisible.value = true
}

const removeRow = async (row) => {
  try {
    await ElMessageBox.confirm(t('pages.po.deleteConfirm'), t('common.delete'), { type: 'warning' })
    await deletePo(row.id)
    ElMessage.success(t('pages.po.deleted'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function poStatusLabel(st) {
  if (st && te(`status.${st}`)) return t(`status.${st}`)
  return st || t('common.emptyValue')
}

function categoryLabel(cat) {
  return poOrderCategoryLabel(cat, t, te)
}

async function downloadProformaInvoicePdf(row) {
  try {
    const path = proformaInvoicePdfPath(row.id)
    await fetchAuthenticatedDocument(path, {
      mode: 'download',
      downloadFallbackName: `proforma-invoice-${row.po_number || row.id}.pdf`,
    })
  } catch (e) {
    ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
  }
}

async function downloadProformaInvoiceDocx(row) {
  try {
    const path = proformaInvoiceDocxPath(row.id)
    await fetchAuthenticatedDocument(path, {
      mode: 'download',
      downloadFallbackName: `proforma-invoice-${row.po_number || row.id}.docx`,
    })
  } catch (e) {
    ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
  }
}

const poMoreItems = computed(() => {
  const items = []
  if (canCreate.value) {
    items.push({ command: 'duplicate', label: t('pages.po.duplicatePo'), icon: CopyDocument })
  }
  items.push(
    { command: 'proformaInvoicePdf', label: t('pages.po.proformaInvoicePdf'), icon: Tickets },
    { command: 'proformaInvoiceDocx', label: t('pages.po.proformaInvoiceDocx'), icon: Memo },
  )
  return items
})

function handlePoMoreAction(row, command) {
  switch (command) {
    case 'duplicate':
      onDuplicatePo(row)
      break
    case 'proformaInvoicePdf':
      downloadProformaInvoicePdf(row)
      break
    case 'proformaInvoiceDocx':
      downloadProformaInvoiceDocx(row)
      break
    default:
      break
  }
}

async function exportPoList() {
  exportLoading.value = true
  try {
    const allRows = []
    const limit = 200
    let offset = 0
    let total = Infinity
    while (allRows.length < total) {
      const base = buildPageQuery()
      const { page: _p, pageSize: _ps, ...filters } = base
      const poPage = await listPoPage({ ...filters, limit, offset })
      total = Number(poPage.total || 0)
      const batch = poPage.items || []
      if (!batch.length) break
      const enrichedBatch = await enrichPoRowsWithHints(batch)
      allRows.push(...enrichHeaders(enrichedBatch, customers.value, brands.value))
      if (batch.length < limit) break
      offset += limit
    }
    if (!allRows.length) {
      ElMessage.warning(t('pages.po.exportEmpty'))
      return
    }
    downloadPoListCsv(allRows, {
      t,
      mktStageLabels: mktStageLabels.value,
      emptyValue: t('common.emptyValue'),
      filename: `po-list-${new Date().toISOString().slice(0, 10)}.csv`,
    })
    ElMessage.success(t('pages.po.exportSuccess', { count: allRows.length }))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    exportLoading.value = false
  }
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
</script>
<style scoped>
.po-filter-action-col {
  display: flex;
  align-items: flex-end;
}

.po-column-toggle {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.po-list-table {
  width: 100%;
  min-width: 1280px;
}

:deep(.po-actions-col .cell) {
  overflow: visible;
  text-overflow: clip;
}

:deep(.po-row-highlight > td) {
  background-color: rgb(255 251 235) !important;
}

.form-label-with-hint {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.form-label-hint {
  color: #94a3b8;
  cursor: help;
  outline: none;
}

.form-label-hint:hover,
.form-label-hint:focus-visible {
  color: var(--el-color-primary);
}

</style>
