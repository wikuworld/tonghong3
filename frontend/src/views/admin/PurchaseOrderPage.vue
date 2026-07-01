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
      <el-button :icon="Download" :loading="exportLoading" @click="exportPoList">{{ t('common.export') }}</el-button>
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

    <div class="mb-2 flex flex-wrap items-center gap-2">
      <el-switch v-model="poShowAllColumns" size="small" />
      <span class="text-sm text-slate-600">{{ t('pages.po.showAllColumns') }}</span>
    </div>

    <el-table
      :data="filteredRows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="fixed"
      :row-class-name="poRowClassName"
      :empty-text="t('pages.po.tableEmpty')"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="po_number" :label="t('common.poNo')" min-width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <div class="flex flex-wrap items-center gap-1">
            <span>{{ row.po_number || t('common.emptyValue') }}</span>
            <el-tag v-if="!row.detail_line_count" size="small" type="warning" effect="plain">
              {{ t('pages.po.noDetailLines') }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="po_customer_ref" :label="t('pages.po.poCustomerRef')" min-width="140" show-overflow-tooltip />
      <el-table-column prop="order_date_fmt" :label="t('common.orderDate')" width="112" align="center" />
      <el-table-column prop="customerName" :label="t('common.customer')" min-width="200" show-overflow-tooltip />
      <el-table-column prop="brand_name_snapshot" :label="t('pages.po.brand')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="buyer" :label="t('common.buyer')" min-width="120" show-overflow-tooltip />
      <el-table-column :label="t('common.material')" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.material_hint }}</span>
        </template>
      </el-table-column>
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
            <el-tag v-if="row.material_followup_done" size="small" type="success" effect="plain">{{ t('pages.po.done') }}</el-tag>
            <el-tag v-else size="small" type="info" effect="plain">{{ t('pages.po.followupOpen') }}</el-tag>
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
          <el-tag v-if="row.stuck_reason" type="warning" size="small" effect="plain">{{ row.stuck_reason }}</el-tag>
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
      <el-table-column
        :label="t('common.actions')"
        width="136"
        align="center"
        fixed="right"
        class-name="po-actions-col"
        :show-overflow-tooltip="false"
      >
        <template #default="{ row }">
          <div class="po-row-actions">
            <el-tooltip :content="t('common.detail')" placement="top">
              <el-button :icon="View" link type="primary" :aria-label="t('common.detail')" @click="openDetailDialog(row)" />
            </el-tooltip>
            <el-tooltip v-if="canManage" :content="t('common.edit')" placement="top">
              <el-button :icon="EditPen" link type="warning" :aria-label="t('common.edit')" @click="openEditDialog(row)" />
            </el-tooltip>
            <el-tooltip v-if="canManage" :content="t('common.delete')" placement="top">
              <el-button :icon="Delete" link type="danger" :aria-label="t('common.delete')" @click="removeRow(row)" />
            </el-tooltip>
            <el-dropdown trigger="click" @command="(cmd) => handlePoMoreAction(row, cmd)">
              <el-button link type="primary" class="po-more-trigger" :aria-label="t('pages.po.moreActions')">
                <span class="po-more-kebab" aria-hidden="true"><i /><i /><i /></span>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="canManage" command="duplicate" :icon="CopyDocument">
                    {{ t('pages.po.duplicatePo') }}
                  </el-dropdown-item>
                  <el-dropdown-item :divided="canManage" command="salesContractPdf" :icon="Document">
                    {{ t('pages.po.salesContractPdf') }}
                  </el-dropdown-item>
                  <el-dropdown-item command="salesContractDocx" :icon="FolderOpened">
                    {{ t('pages.po.salesContractDocx') }}
                  </el-dropdown-item>
                  <el-dropdown-item command="proformaInvoicePdf" :icon="Tickets">
                    {{ t('pages.po.proformaInvoicePdf') }}
                  </el-dropdown-item>
                  <el-dropdown-item command="proformaInvoiceDocx" :icon="Memo">
                    {{ t('pages.po.proformaInvoiceDocx') }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
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
  View,
  EditPen,
  Delete,
  Document,
  FolderOpened,
  CopyDocument,
  Tickets,
  Memo,
} from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import PoFormWizardDialog from '../../components/admin/PoFormWizardDialog.vue'
import PoAmbiguousMasterDialog from '../../components/admin/PoAmbiguousMasterDialog.vue'
import PoCopyItemDialog from '../../components/admin/PoCopyItemDialog.vue'
import PoDetailDialog from '../../components/admin/PoDetailDialog.vue'
import PoMarketingReviseDialog from '../../components/admin/PoMarketingReviseDialog.vue'
import { usePoFormWizard } from '../../composables/usePoFormWizard.js'
import { usePoList } from '../../composables/usePoList.js'
import { canWrite } from '../../security/permissions'
import { statusType } from '../../utils/format'
import { parseApiErrorMessage } from '../../utils/poApi.js'
import { createMktStageLabels, mktStageLabel } from '../../utils/mktStage.js'
import {
  downloadPoListCsv,
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
  listAuditLogs,
  listBrands,
  listBuyerPriceLists,
  listCustomers,
  listMasterItems,
  listMasterItemDimensionValues,
  listPoDetails,
  listPoPage,
  fetchPoMaterialHints,
  salesContractDocxPath,
  salesContractPdfPath,
  proformaInvoiceDocxPath,
  proformaInvoicePdfPath,
  updatePo,
} from '../../api/client'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const canManage = canWrite('po')
const highlightPoId = ref(null)

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
    wizard.materialDimensionOptions.value = dimMat.values || []
    buyerCodes.value = mergeExtraBuyerCodes(buyerCodes.value, bpl)
    let items = poPage.items || []
    const needsListSummaries = items.some((h) => {
      if (h.id == null) return false
      const missingMaterial = !(String(h.material_hint || '').trim())
      const missingEtd = !(String(h.etd_display || '').trim()) && !h.etd
      return missingMaterial || missingEtd
    })
    if (needsListSummaries) {
      try {
        const hintResp = await fetchPoMaterialHints(items.map((h) => h.id))
        items = mergePoMaterialHints(items, hintResp.items || [])
      } catch {
        /* list tetap tampil tanpa material hint */
      }
    }
    rows.value = enrichHeaders(items, cust, br)
    totalRows.value = Number(poPage.total || 0)
  } catch (e) {
    ElMessage.error(e.message || t('pages.po.loadFailed'))
  } finally {
    loading.value = false
  }
}

wizard = usePoFormWizard({ t, canManage, customers, brands, masterItems, buyerCodes, load })

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

async function quickChangeStatus(row, newStatus) {
  try {
    await updatePo(row.id, { status: newStatus })
    row.status = newStatus
    ElMessage.success(t('pages.po.statusChanged'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
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

async function downloadSalesContractPdf(row) {
  try {
    const path = salesContractPdfPath(row.id)
    await fetchAuthenticatedDocument(path, `sales-contract-${row.po_number || row.id}.pdf`)
  } catch (e) {
    ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
  }
}

async function downloadSalesContractDocx(row) {
  try {
    const path = salesContractDocxPath(row.id)
    await fetchAuthenticatedDocument(path, `sales-contract-${row.po_number || row.id}.docx`)
  } catch (e) {
    ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
  }
}

async function downloadProformaInvoicePdf(row) {
  try {
    const path = proformaInvoicePdfPath(row.id)
    await fetchAuthenticatedDocument(path, `proforma-invoice-${row.po_number || row.id}.pdf`)
  } catch (e) {
    ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
  }
}

async function downloadProformaInvoiceDocx(row) {
  try {
    const path = proformaInvoiceDocxPath(row.id)
    await fetchAuthenticatedDocument(path, `proforma-invoice-${row.po_number || row.id}.docx`)
  } catch (e) {
    ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
  }
}

function handlePoMoreAction(row, command) {
  switch (command) {
    case 'duplicate':
      onDuplicatePo(row)
      break
    case 'salesContractPdf':
      downloadSalesContractPdf(row)
      break
    case 'salesContractDocx':
      downloadSalesContractDocx(row)
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
      const poPage = await listPoPage({ ...buildPageQuery(), limit, offset })
      total = Number(poPage.total || 0)
      const batch = poPage.items || []
      if (!batch.length) break
      allRows.push(...enrichHeaders(batch, customers.value, brands.value))
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
.admin-table {
  width: 100%;
}

.po-row-actions {
  display: inline-flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.po-more-trigger {
  padding: 4px 6px;
  height: auto;
}

.po-more-kebab {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  width: 14px;
  height: 14px;
}

.po-more-kebab i {
  display: block;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: currentColor;
}

:deep(.po-actions-col .cell) {
  overflow: visible;
  text-overflow: clip;
}

:deep(.po-row-highlight > td) {
  background-color: rgb(255 251 235) !important;
}

</style>
