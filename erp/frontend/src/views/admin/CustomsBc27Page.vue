<template>
  <AdminSection :title="t('pages.customsBc27.title')" :subtitle="t('pages.customsBc27.subtitle')">
    <template #actions>
      <template v-if="activeTab === 'bc27'">
        <el-input
          v-model="keyword"
          clearable
          class="cbc-toolbar-search"
          :placeholder="t('pages.customsBc27.searchPlaceholder')"
        />
        <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
        <el-tooltip
          :content="t('pages.customsBc27.selectHint')"
          placement="bottom"
          :disabled="Boolean(selection.length)"
        >
          <span>
            <el-button
              type="warning"
              :icon="Download"
              :disabled="!selection.length || !canExport"
              :loading="exporting"
              @click="downloadExcel"
            >
              {{
                selection.length
                  ? t('pages.customsBc27.downloadSelected', { n: selection.length })
                  : t('pages.customsBc27.download')
              }}
            </el-button>
          </span>
        </el-tooltip>
      </template>
      <template v-else>
        <el-input
          v-model="scKeyword"
          clearable
          class="cbc-toolbar-search"
          :placeholder="t('pages.customsBc27.searchPlaceholder')"
        />
        <el-button :icon="Refresh" :loading="scLoading" @click="reloadSalesContracts">
          {{ t('common.refresh') }}
        </el-button>
        <el-tooltip
          :content="t('pages.customsBc27.scSelectHint')"
          placement="bottom"
          :disabled="Boolean(scSelection.length)"
        >
          <span class="cbc-sc-actions">
            <el-button
              type="primary"
              :icon="Document"
              :disabled="!scSelection.length || !canExport"
              :loading="scDownloading === 'pdf'"
              @click="downloadSalesContract('pdf')"
            >
              {{
                scSelection.length
                  ? t('pages.customsBc27.salesContractPdfSelected', { n: scSelection.length })
                  : t('pages.customsBc27.salesContractPdf')
              }}
            </el-button>
            <el-button
              :icon="FolderOpened"
              :disabled="!scSelection.length || !canExport"
              :loading="scDownloading === 'docx'"
              @click="downloadSalesContract('docx')"
            >
              {{
                scSelection.length
                  ? t('pages.customsBc27.salesContractDocxSelected', { n: scSelection.length })
                  : t('pages.customsBc27.salesContractDocx')
              }}
            </el-button>
          </span>
        </el-tooltip>
      </template>
    </template>

    <el-tabs v-model="activeTab" class="cbc-tabs" @tab-change="onTabChange">
      <el-tab-pane :label="t('pages.customsBc27.tabBc27')" name="bc27">
        <div class="admin-inner-card">
          <div class="admin-inner-card__head">
            <div>
              <h3 class="admin-inner-card__title">{{ t('pages.customsBc27.listTitle') }}</h3>
              <p class="admin-inner-card__sub">{{ t('pages.customsBc27.listSubtitle') }}</p>
            </div>
          </div>

          <div class="filter-panel mb-4">
            <p class="filter-panel__title">{{ t('common.filter') }}</p>
            <div class="cbc-filter">
              <label class="cbc-field">
                <span class="cbc-field__label">{{ t('common.customer') }}</span>
                <el-select
                  v-model="filterCustomerId"
                  clearable
                  filterable
                  class="cbc-field__control"
                  :placeholder="t('pages.customsBc27.customerFilter')"
                >
                  <el-option
                    v-for="c in customers"
                    :key="c.id"
                    :label="c.name || `#${c.id}`"
                    :value="c.id"
                  />
                </el-select>
              </label>
              <label class="cbc-field">
                <span class="cbc-field__label">{{ t('pages.customsBc27.dateRange') }}</span>
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  unlink-panels
                  range-separator="—"
                  value-format="YYYY-MM-DD"
                  class="cbc-field__control"
                  clearable
                  :start-placeholder="t('common.placeholder.fromDate')"
                  :end-placeholder="t('common.placeholder.toDate')"
                />
              </label>
            </div>
          </div>

          <div class="admin-table-scroll">
            <el-table
              ref="tableRef"
              v-loading="loading"
              :data="rows"
              border
              stripe
              size="small"
              class="admin-table"
              row-key="id"
              max-height="52vh"
              :empty-text="t('pages.customsBc27.tableEmpty')"
              @selection-change="onSelectionChange"
            >
              <el-table-column type="selection" width="48" align="center" reserve-selection />
              <el-table-column type="index" :label="t('common.noLabel')" width="52" align="center" />
              <el-table-column prop="delivery_number" :label="t('pages.customsBc27.colSj')" min-width="140" show-overflow-tooltip />
              <el-table-column :label="t('common.customer')" min-width="180" show-overflow-tooltip>
                <template #default="{ row }">{{ customerName(row.customer_id) }}</template>
              </el-table-column>
              <el-table-column prop="delivery_date" :label="t('pages.customsBc27.colDate')" width="120" align="center">
                <template #default="{ row }">{{ formatDate(row.delivery_date) }}</template>
              </el-table-column>
              <el-table-column prop="status" :label="t('common.status')" width="110" align="center" />
              <el-table-column prop="destination" :label="t('pages.customsBc27.colDestination')" min-width="140" show-overflow-tooltip />
              <el-table-column prop="bc_number" :label="t('pages.delivery.bcNumber')" width="120" show-overflow-tooltip />
            </el-table>
          </div>

          <div class="cbc-pagination">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              size="small"
              background
              layout="total, sizes, prev, pager, next"
              :total="total"
              :page-sizes="[20, 50, 100, 200]"
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.customsBc27.tabSalesContract')" name="salesContract">
        <div class="admin-inner-card">
          <div class="admin-inner-card__head">
            <div>
              <h3 class="admin-inner-card__title">{{ t('pages.customsBc27.scListTitle') }}</h3>
              <p class="admin-inner-card__sub">{{ t('pages.customsBc27.scListSubtitle') }}</p>
            </div>
          </div>

          <div class="filter-panel mb-4">
            <p class="filter-panel__title">{{ t('common.filter') }}</p>
            <div class="cbc-filter">
              <label class="cbc-field">
                <span class="cbc-field__label">{{ t('common.customer') }}</span>
                <el-select
                  v-model="scFilterCustomerId"
                  clearable
                  filterable
                  class="cbc-field__control"
                  :placeholder="t('pages.customsBc27.customerFilter')"
                >
                  <el-option
                    v-for="c in customers"
                    :key="c.id"
                    :label="c.name || `#${c.id}`"
                    :value="c.id"
                  />
                </el-select>
              </label>
              <label class="cbc-field">
                <span class="cbc-field__label">{{ t('pages.customsBc27.dateRange') }}</span>
                <el-date-picker
                  v-model="scDateRange"
                  type="daterange"
                  unlink-panels
                  range-separator="—"
                  value-format="YYYY-MM-DD"
                  class="cbc-field__control"
                  clearable
                  :start-placeholder="t('common.placeholder.fromDate')"
                  :end-placeholder="t('common.placeholder.toDate')"
                />
              </label>
            </div>
          </div>

          <div class="admin-table-scroll">
            <el-table
              ref="scTableRef"
              v-loading="scLoading"
              :data="scRows"
              border
              stripe
              size="small"
              class="admin-table"
              row-key="id"
              max-height="52vh"
              :empty-text="t('pages.customsBc27.tableEmpty')"
              @selection-change="onScSelectionChange"
            >
              <el-table-column type="selection" width="48" align="center" reserve-selection />
              <el-table-column type="index" :label="t('common.noLabel')" width="52" align="center" />
              <el-table-column prop="delivery_number" :label="t('pages.customsBc27.colSj')" min-width="140" show-overflow-tooltip />
              <el-table-column :label="t('common.customer')" min-width="180" show-overflow-tooltip>
                <template #default="{ row }">{{ customerName(row.customer_id) }}</template>
              </el-table-column>
              <el-table-column prop="delivery_date" :label="t('pages.customsBc27.colDate')" width="120" align="center">
                <template #default="{ row }">{{ formatDate(row.delivery_date) }}</template>
              </el-table-column>
              <el-table-column prop="status" :label="t('common.status')" width="110" align="center" />
              <el-table-column prop="destination" :label="t('pages.customsBc27.colDestination')" min-width="140" show-overflow-tooltip />
            </el-table>
          </div>

          <div class="cbc-pagination">
            <el-pagination
              v-model:current-page="scPage"
              v-model:page-size="scPageSize"
              size="small"
              background
              layout="total, sizes, prev, pager, next"
              :total="scTotal"
              :page-sizes="[20, 50, 100, 200]"
            />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      v-model="bcDialogVisible"
      :title="t('pages.customsBc27.bcDialogTitle')"
      width="440px"
      destroy-on-close
      align-center
    >
      <p class="cbc-dialog-hint">{{ t('pages.customsBc27.bcDialogHint') }}</p>
      <el-form label-position="top" @submit.prevent>
        <el-form-item :label="t('pages.customsBc27.ajuSeqLabel')" required>
          <el-input
            v-model="bcForm.aju_seq"
            maxlength="6"
            inputmode="numeric"
            :placeholder="t('pages.customsBc27.ajuSeqPlaceholder')"
          />
          <p class="cbc-field-hint">{{ t('pages.customsBc27.ajuSeqHint') }}</p>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bcDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="warning" :loading="exporting" @click="confirmDownloadExcel">
          {{ t('pages.customsBc27.download') }}
        </el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Download, FolderOpened, Refresh } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import AdminSection from '../../components/AdminSection.vue'
import {
  customsBc27XlsxPath,
  fetchAuthenticatedDocument,
  listCustomers,
  listDelivery,
  salesContractDocxPath,
  salesContractPdfPath,
} from '../../api/client'
import { can } from '../../security/permissions'
import { buildPageParams, normalizePageResult } from '../../utils/tableQuery'

const { t } = useI18n()
const canExport = computed(() => can('customsBc27', 'export'))

const activeTab = ref('bc27')

const loading = ref(false)
const exporting = ref(false)
const keyword = ref('')
const filterCustomerId = ref(null)
const dateRange = ref(null)
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const rows = ref([])
const customers = ref([])
const customerMap = ref({})
const selection = ref([])
const tableRef = ref(null)

const bcDialogVisible = ref(false)
const bcForm = reactive({ aju_seq: '' })

const scLoading = ref(false)
const scDownloading = ref('')
const scKeyword = ref('')
const scFilterCustomerId = ref(null)
const scDateRange = ref(null)
const scPage = ref(1)
const scPageSize = ref(50)
const scTotal = ref(0)
const scRows = ref([])
const scSelection = ref([])
const scTableRef = ref(null)
const scLoadedOnce = ref(false)

function customerName(id) {
  if (id == null) return '—'
  return customerMap.value[id] || `#${id}`
}

function formatDate(v) {
  if (!v) return '—'
  return String(v).slice(0, 10)
}

function digitsOnly(v, len) {
  const s = String(v || '').replace(/\D/g, '')
  return s.length === len ? s : null
}

function onSelectionChange(rowsSel) {
  selection.value = Array.isArray(rowsSel) ? rowsSel : []
}

function onScSelectionChange(rowsSel) {
  scSelection.value = Array.isArray(rowsSel) ? rowsSel : []
}

function clearSelection() {
  selection.value = []
  tableRef.value?.clearSelection?.()
}

function clearScSelection() {
  scSelection.value = []
  scTableRef.value?.clearSelection?.()
}

function assertSameCustomer(rowsSel) {
  const custIds = new Set(rowsSel.map((r) => r.customer_id).filter((x) => x != null))
  if (custIds.size > 1) {
    ElMessage.error(t('pages.customsBc27.sameCustomerRequired'))
    return false
  }
  return true
}

async function loadCustomers() {
  try {
    const raw = await listCustomers()
    const list = Array.isArray(raw) ? raw : raw?.items || []
    customers.value = list
    const map = {}
    for (const c of list) {
      if (c?.id != null) map[c.id] = c.name || `#${c.id}`
    }
    customerMap.value = map
  } catch {
    customers.value = []
    customerMap.value = {}
  }
}

async function reload() {
  loading.value = true
  try {
    const from = Array.isArray(dateRange.value) ? dateRange.value[0] : null
    const to = Array.isArray(dateRange.value) ? dateRange.value[1] : null
    const res = await listDelivery(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: 'delivery_date',
        sortDir: 'desc',
        extra: {
          q: keyword.value?.trim() || undefined,
          customer_id: filterCustomerId.value || undefined,
          delivery_date_from: from || undefined,
          delivery_date_to: to || undefined,
        },
      }),
    )
    const pageData = normalizePageResult(res, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items
    total.value = pageData.total
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

async function reloadSalesContracts() {
  scLoading.value = true
  try {
    const from = Array.isArray(scDateRange.value) ? scDateRange.value[0] : null
    const to = Array.isArray(scDateRange.value) ? scDateRange.value[1] : null
    const res = await listDelivery(
      buildPageParams({
        page: scPage.value,
        pageSize: scPageSize.value,
        sortBy: 'delivery_date',
        sortDir: 'desc',
        extra: {
          q: scKeyword.value?.trim() || undefined,
          customer_id: scFilterCustomerId.value || undefined,
          delivery_date_from: from || undefined,
          delivery_date_to: to || undefined,
        },
      }),
    )
    const pageData = normalizePageResult(res, { page: scPage.value, pageSize: scPageSize.value })
    scRows.value = pageData.items
    scTotal.value = pageData.total
    scLoadedOnce.value = true
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    scLoading.value = false
  }
}

function onTabChange(name) {
  if (name === 'salesContract' && !scLoadedOnce.value) {
    reloadSalesContracts()
  }
}

function downloadExcel() {
  if (!canExport.value) return
  const ids = selection.value.map((r) => r.id).filter(Boolean)
  if (!ids.length) {
    ElMessage.warning(t('pages.customsBc27.selectHint'))
    return
  }
  if (!assertSameCustomer(selection.value)) return
  bcForm.aju_seq = ''
  bcDialogVisible.value = true
}

async function confirmDownloadExcel() {
  const aju = digitsOnly(bcForm.aju_seq, 6)
  if (!aju) {
    ElMessage.warning(t('pages.customsBc27.ajuSeqInvalid'))
    return
  }
  const ids = selection.value.map((r) => r.id).filter(Boolean)
  exporting.value = true
  try {
    const stamp = new Date().toISOString().slice(0, 10)
    await fetchAuthenticatedDocument(customsBc27XlsxPath(ids, { aju_seq: aju }), {
      mode: 'download',
      downloadFallbackName: `customs_bc27_${stamp}.xlsx`,
    })
    bcDialogVisible.value = false
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    exporting.value = false
  }
}

async function downloadSalesContract(kind) {
  if (!canExport.value) return
  const ids = scSelection.value.map((r) => r.id).filter(Boolean)
  if (!ids.length) {
    ElMessage.warning(t('pages.customsBc27.scSelectHint'))
    return
  }
  if (!assertSameCustomer(scSelection.value)) return
  scDownloading.value = kind
  try {
    const path = kind === 'docx' ? salesContractDocxPath(ids) : salesContractPdfPath(ids)
    const stamp = new Date().toISOString().slice(0, 10)
    await fetchAuthenticatedDocument(path, {
      mode: 'download',
      downloadFallbackName: `KPJB_${stamp}.${kind}`,
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    scDownloading.value = ''
  }
}

let filterTimer = null
function scheduleReload() {
  if (filterTimer) clearTimeout(filterTimer)
  filterTimer = setTimeout(() => {
    page.value = 1
    reload()
  }, 300)
}

let scFilterTimer = null
function scheduleScReload() {
  if (scFilterTimer) clearTimeout(scFilterTimer)
  scFilterTimer = setTimeout(() => {
    scPage.value = 1
    reloadSalesContracts()
  }, 300)
}

watch([keyword, filterCustomerId, dateRange], () => {
  clearSelection()
  scheduleReload()
})

watch([page, pageSize], () => {
  reload()
})

watch([scKeyword, scFilterCustomerId, scDateRange], () => {
  clearScSelection()
  scheduleScReload()
})

watch([scPage, scPageSize], () => {
  if (activeTab.value === 'salesContract') reloadSalesContracts()
})

onMounted(async () => {
  await loadCustomers()
  await reload()
})
</script>

<style scoped>
.cbc-toolbar-search {
  width: min(280px, 40vw);
}
.cbc-tabs :deep(.el-tabs__header) {
  margin-bottom: 12px;
}
.cbc-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 16px;
  align-items: flex-end;
}
.cbc-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 200px;
}
.cbc-field__label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.cbc-field__control {
  width: min(280px, 100%);
}
.cbc-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
.cbc-dialog-hint {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.cbc-field-hint {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.35;
}
.cbc-sc-actions {
  display: inline-flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
