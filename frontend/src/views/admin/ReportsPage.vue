<template>
  <AdminSection :title="t('pages.reports.title')" :subtitle="t('pages.reports.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.reports.searchPlaceholder')"
        clearable
        class="reports-toolbar-search"
      />
      <el-button :icon="Download" :loading="dailyCsvLoading" @click="exportDailyMarketingCsv">
        {{ t('pages.reports.exportDailyMarketing') }}
      </el-button>
      <el-button :icon="Download" @click="exportSoCsv">{{ t('pages.reports.exportSo') }}</el-button>
      <el-button :icon="Download" @click="exportLinesCsv">{{ t('pages.reports.exportLines') }}</el-button>
      <el-button type="primary" :icon="Printer" @click="printReport">{{ t('common.print') }} {{ t('pages.reports.report') }}</el-button>
    </template>

    <div class="report-card">
      <div class="report-card__header">
        <div class="report-card__header-title">{{ t('pages.reports.poOrderDescription') }}</div>
        <div class="report-card__header-sub">PT. Tong Hong Tannery Indonesia</div>
        <div class="report-card__header-daily">{{ t('pages.reports.dailyMarketingSheet') }}</div>
      </div>

      <div class="filter-panel report-card__filter">
        <p class="filter-panel__title">{{ t('common.filter') }}</p>
        <el-form class="filter-form" label-position="top">
          <el-row :gutter="12">
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item :label="`${t('common.date')} ${t('common.from')}`">
                <el-date-picker
                  v-model="dateFrom"
                  type="date"
                  value-format="YYYY-MM-DD"
                  class="w-full"
                  :placeholder="t('common.placeholder.fromDate')"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-form-item :label="`${t('common.date')} ${t('common.to')}`">
                <el-date-picker
                  v-model="dateTo"
                  type="date"
                  value-format="YYYY-MM-DD"
                  class="w-full"
                  :placeholder="t('common.placeholder.toDate')"
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="5">
              <el-form-item :label="t('common.customer')">
                <el-select v-model="customer" clearable filterable class="w-full" :placeholder="t('common.allCustomer')">
                  <el-option :label="t('common.allCustomer')" value="" />
                  <el-option v-for="c in customers" :key="c.id" :label="c.name || c.code" :value="c.name || c.code" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12" :md="5">
              <el-form-item :label="t('common.poCategory')">
                <el-select v-model="category" clearable class="w-full" :placeholder="t('pages.reports.allStatus')">
                  <el-option :label="t('pages.reports.allStatus')" value="" />
                  <el-option :label="t('status.production')" value="production" />
                  <el-option :label="t('status.sample')" value="sample" />
                  <el-option :label="t('status.claim')" value="claim" />
                  <el-option :label="t('status.return')" value="return" />
                  <el-option :label="t('status.subcont')" value="subcont" />
                  <el-option :label="t('status.suede')" value="suede" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="2" class="reports-filter-action">
              <el-form-item label="&nbsp;">
                <el-button type="primary" class="w-full" :loading="reportLoading" @click="runGenerateReport">
                  {{ t('pages.reports.generateReport') }}
                </el-button>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="12" class="report-filter-row-2">
            <el-col :xs="24" :sm="12" :md="8">
              <el-form-item :label="t('pages.reports.dateFieldLabel')">
                <el-select v-model="dateField" class="w-full">
                  <el-option :label="t('pages.reports.dateFieldOrder')" value="order" />
                  <el-option :label="t('pages.reports.dateFieldCreated')" value="created" />
                  <el-option :label="t('pages.reports.dateFieldEither')" value="either" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <div v-loading="reportLoading" class="report-card__body">
        <h3 class="report-section-title">{{ t('pages.reports.reviseThickness') }}</h3>
        <div class="report-table-scroll">
          <el-table
            :data="filteredReviseRows"
            border
            stripe
            size="small"
            class="admin-table report-table report-table--wide"
            table-layout="auto"
            :empty-text="t('pages.reports.tableEmpty')"
          >
            <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" fixed />
            <el-table-column :label="t('pages.reports.colOrderDate')" min-width="112" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateIso(row.order_date) }}</template>
            </el-table-column>
            <el-table-column prop="thi_line_ref" :label="t('pages.reports.colThiLine')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="customer" :label="t('common.customer')" min-width="150" show-overflow-tooltip />
            <el-table-column prop="brand" :label="t('pages.reports.colBrand')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="order_type" :label="t('pages.reports.colOrderType')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="poNo" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="po_customer_ref" :label="t('pages.reports.colPoCustomerRef')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="material" :label="t('common.material')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="oldThickness" :label="t('pages.reports.oldThickness')" min-width="100" />
            <el-table-column prop="newThickness" :label="t('pages.reports.newThickness')" min-width="100">
              <template #default="{ row }">
                <span class="report-new-thickness">{{ row.newThickness }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="emboss" :label="t('pages.po.emboss')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="softness_type" :label="t('pages.reports.colSoftnessType')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="pu_production" :label="t('pages.reports.colPuProduction')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="color" :label="t('common.color')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="softness" :label="t('common.softness')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="qty" :label="t('common.quantity')" min-width="88" align="right">
              <template #default="{ row }">{{ formatQty(row.qty) }}</template>
            </el-table-column>
            <el-table-column prop="unit_price" :label="t('pages.reports.colUnitPrice')" min-width="90" align="right" show-overflow-tooltip />
            <el-table-column prop="color_reference" :label="t('common.colorReference')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="backing" :label="t('common.backing')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="model" :label="t('common.model')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="110" show-overflow-tooltip />
            <el-table-column :label="t('pages.po.lineEtd')" min-width="110" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateIso(row.line_etd) }}</template>
            </el-table-column>
            <el-table-column prop="buyer" :label="t('common.buyer')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="status" :label="t('common.status')" min-width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="poStatusTagType(row.status)" size="small">{{ poStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <h3 class="report-section-title">{{ t('pages.reports.productionOrder') }}</h3>
        <div class="report-table-scroll">
          <el-table
            :data="filteredProductionRows"
            border
            stripe
            size="small"
            class="admin-table report-table report-table--wide"
            table-layout="auto"
            :empty-text="t('pages.reports.tableEmpty')"
          >
            <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" fixed />
            <el-table-column :label="t('pages.reports.colOrderDate')" min-width="112" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateIso(row.order_date) }}</template>
            </el-table-column>
            <el-table-column prop="thi_line_ref" :label="t('pages.reports.colThiLine')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="customer" :label="t('common.customer')" min-width="150" show-overflow-tooltip />
            <el-table-column prop="brand" :label="t('pages.reports.colBrand')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="order_type" :label="t('pages.reports.colOrderType')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="poNo" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="po_customer_ref" :label="t('pages.reports.colPoCustomerRef')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="material" :label="t('common.material')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="thickness" :label="t('common.thickness')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="emboss" :label="t('pages.po.emboss')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="softness_type" :label="t('pages.reports.colSoftnessType')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="pu_production" :label="t('pages.reports.colPuProduction')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="color" :label="t('common.color')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="softness" :label="t('common.softness')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="qty" :label="t('common.quantity')" min-width="88" align="right">
              <template #default="{ row }">{{ formatQty(row.qty) }}</template>
            </el-table-column>
            <el-table-column prop="unit_price" :label="t('pages.reports.colUnitPrice')" min-width="90" align="right" show-overflow-tooltip />
            <el-table-column prop="color_reference" :label="t('common.colorReference')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="backing" :label="t('common.backing')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="model" :label="t('common.model')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="110" show-overflow-tooltip />
            <el-table-column :label="t('pages.po.lineEtd')" min-width="110" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateIso(row.line_etd) }}</template>
            </el-table-column>
            <el-table-column prop="buyer" :label="t('common.buyer')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="po_category" :label="t('common.poCategory')" min-width="100" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.po_category" size="small" type="info" effect="plain">{{ categoryLabel(row.po_category) }}</el-tag>
                <span v-else>—</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" :label="t('common.status')" min-width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="poStatusTagType(row.status)" size="small">{{ poStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="report-total-line">
          {{ t('pages.reports.totalProductionOrder') }}: <b>{{ formatQty(productionQtySum) }}</b>
        </div>

        <h3 class="report-section-title">{{ t('pages.reports.sample') }}</h3>
        <div class="report-table-scroll">
          <el-table
            :data="filteredSampleRows"
            border
            stripe
            size="small"
            class="admin-table report-table report-table--wide"
            table-layout="auto"
            :empty-text="t('pages.reports.tableEmpty')"
          >
            <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" fixed />
            <el-table-column :label="t('pages.reports.colOrderDate')" min-width="112" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateIso(row.order_date) }}</template>
            </el-table-column>
            <el-table-column prop="thi_line_ref" :label="t('pages.reports.colThiLine')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="customer" :label="t('common.customer')" min-width="150" show-overflow-tooltip />
            <el-table-column prop="brand" :label="t('pages.reports.colBrand')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="order_type" :label="t('pages.reports.colOrderType')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="poNo" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="po_customer_ref" :label="t('pages.reports.colPoCustomerRef')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="material" :label="t('common.material')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="thickness" :label="t('common.thickness')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="emboss" :label="t('pages.po.emboss')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="softness_type" :label="t('pages.reports.colSoftnessType')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="pu_production" :label="t('pages.reports.colPuProduction')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="color" :label="t('common.color')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="softness" :label="t('common.softness')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="qty" :label="t('common.quantity')" min-width="88" align="right">
              <template #default="{ row }">{{ formatQty(row.qty) }}</template>
            </el-table-column>
            <el-table-column prop="unit_price" :label="t('pages.reports.colUnitPrice')" min-width="90" align="right" show-overflow-tooltip />
            <el-table-column prop="color_reference" :label="t('common.colorReference')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="backing" :label="t('common.backing')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="model" :label="t('common.model')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="110" show-overflow-tooltip />
            <el-table-column :label="t('pages.po.lineEtd')" min-width="110" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateIso(row.line_etd) }}</template>
            </el-table-column>
            <el-table-column prop="buyer" :label="t('common.buyer')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="status" :label="t('common.status')" min-width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="poStatusTagType(row.status)" size="small">{{ poStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="report-total-line">
          {{ t('pages.reports.totalSample') }}: <b>{{ formatQty(sampleQtySum) }}</b>
        </div>
      </div>

      <div class="report-card__footer">
        <el-button :icon="Download" :loading="dailyCsvLoading" @click="exportDailyMarketingCsv">
          {{ t('pages.reports.exportDailyMarketing') }}
        </el-button>
        <el-button :icon="Download" @click="exportSoCsv">{{ t('pages.reports.exportSo') }}</el-button>
        <el-button :icon="Download" @click="exportLinesCsv">{{ t('pages.reports.exportLines') }}</el-button>
        <el-button type="primary" :icon="Printer" @click="printReport">{{ t('common.print') }} {{ t('pages.reports.report') }}</el-button>
      </div>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Download, Printer } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  fetchReportPoOrderDescription,
  listCustomers,
  reportPoDailyMarketingCsvPath,
  reportSalesOrderLinesExportUrl,
  reportSalesOrdersExportUrl,
} from '../../api/client'

const { t, te } = useI18n()

const keyword = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const customer = ref('')
const category = ref('')
const dateField = ref('order')
const customers = ref([])

const reportLoading = ref(false)
const dailyCsvLoading = ref(false)
const reviseRows = ref([])
const productionRows = ref([])
const sampleRows = ref([])

onMounted(async () => {
  try {
    customers.value = await listCustomers()
  } catch {
    customers.value = []
  }
  await fetchReport()
})

function exportSoCsv() {
  window.open(reportSalesOrdersExportUrl(), '_blank')
}

function exportLinesCsv() {
  window.open(reportSalesOrderLinesExportUrl(), '_blank')
}

function buildReportQuery() {
  const q = {}
  if (dateFrom.value) q.date_from = dateFrom.value
  if (dateTo.value) q.date_to = dateTo.value
  if (customer.value) q.customer = customer.value
  if (dateField.value) q.date_field = dateField.value
  return q
}

async function fetchReport() {
  reportLoading.value = true
  try {
    const data = await fetchReportPoOrderDescription(buildReportQuery())
    reviseRows.value = data.revise_thickness || []
    productionRows.value = data.production_orders || []
    sampleRows.value = data.samples || []
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    reportLoading.value = false
  }
}

async function exportDailyMarketingCsv() {
  dailyCsvLoading.value = true
  try {
    const path = reportPoDailyMarketingCsvPath(buildReportQuery())
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null
    const r = await fetch(path, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (!r.ok) {
      const text = await r.text()
      throw new Error(text || r.statusText)
    }
    const blob = await r.blob()
    const dispo = r.headers.get('content-disposition') || ''
    const m = dispo.match(/filename="?([^";]+)"?/i)
    const name = m ? m[1] : 'laporan_po_harian_marketing.csv'
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = name
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(t('pages.reports.dailyCsvOk'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    dailyCsvLoading.value = false
  }
}

function poStatusLabel(st) {
  if (st && te(`status.${st}`)) return t(`status.${st}`)
  return st || t('common.emptyValue')
}

function categoryLabel(cat) {
  if (cat && te(`status.${cat}`)) return t(`status.${cat}`)
  return cat || '—'
}

function poStatusTagType(st) {
  if (st === 'confirmed') return 'success'
  if (st === 'production') return 'warning'
  if (st === 'completed') return 'success'
  if (st === 'draft') return 'info'
  return ''
}

function formatDateIso(val) {
  if (val == null || val === '') return '—'
  const s = String(val)
  return s.length >= 10 ? s.slice(0, 10) : s
}

function rowMatchesKeyword(row) {
  const q = keyword.value.trim().toLowerCase()
  if (!q) return true
  return Object.values(row)
    .filter((v) => v !== null && v !== undefined)
    .join(' ')
    .toLowerCase()
    .includes(q)
}

function rowMatchesCustomer(row) {
  if (!customer.value) return true
  return (row.customer || '') === customer.value
}

const filteredReviseRows = computed(() =>
  reviseRows.value.filter((row) => rowMatchesKeyword(row) && rowMatchesCustomer(row)),
)

const filteredProductionRows = computed(() => {
  if (category.value === 'sample') return []
  return productionRows.value.filter((row) => {
    const categoryMatch =
      !category.value ||
      row.po_category === category.value ||
      (category.value === 'production' && !row.po_category)
    return categoryMatch && rowMatchesKeyword(row) && rowMatchesCustomer(row)
  })
})

const filteredSampleRows = computed(() => {
  if (category.value && category.value !== 'sample') return []
  return sampleRows.value.filter((row) => rowMatchesKeyword(row) && rowMatchesCustomer(row))
})

const productionQtySum = computed(() =>
  filteredProductionRows.value.reduce((s, r) => s + (Number(r.qty) || 0), 0),
)

const sampleQtySum = computed(() => filteredSampleRows.value.reduce((s, r) => s + (Number(r.qty) || 0), 0))

function formatQty(n) {
  if (n === null || n === undefined) return '0'
  return Number(n).toLocaleString()
}

async function runGenerateReport() {
  await fetchReport()
  ElMessage.success(t('pages.reports.generated'))
}

function printReport() {
  window.print()
}
</script>

<style scoped>
.report-card {
  width: 100%;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
}

.report-card__header {
  padding: 14px 18px;
  background: #0f172a;
  color: #fff;
}

.report-card__header-title {
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.report-card__header-sub {
  margin-top: 4px;
  font-size: 0.8125rem;
  color: #cbd5e1;
}

.report-card__header-daily {
  margin-top: 6px;
  font-size: 0.75rem;
  color: #94a3b8;
  font-style: italic;
}

.report-card__filter {
  margin: 0;
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-top: none;
}

.report-filter-row-2 {
  margin-top: 4px;
}

.reports-filter-action {
  display: flex;
  align-items: flex-end;
}

.report-card__body {
  padding: 16px 16px 8px;
  background: #fff;
}

.report-section-title {
  margin: 20px 0 10px;
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
}

.report-section-title:first-child {
  margin-top: 0;
}

.report-table-scroll {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 4px;
}

.report-table {
  margin-bottom: 12px;
}

.report-table--wide {
  min-width: 2100px;
}

.report-table :deep(.el-table__header-wrapper th.el-table__cell) {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
}

.report-new-thickness {
  color: #a16207;
  font-weight: 700;
}

.report-total-line {
  margin: 0 0 20px;
  text-align: right;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #0f172a;
}

.report-card__footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #e2e8f0;
  background: #f1f5f9;
}

.w-full {
  width: 100%;
}

.reports-toolbar-search {
  width: 220px;
  max-width: 100%;
  margin-right: 8px;
  vertical-align: middle;
}

@media (max-width: 767px) {
  .report-card__footer {
    flex-direction: column;
  }

  .report-card__footer .el-button {
    width: 100%;
    margin: 0;
  }
}
</style>
