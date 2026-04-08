<template>
  <AdminSection :title="t('pages.reports.title')" :subtitle="t('pages.reports.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.reports.searchPlaceholder')"
        clearable
        class="reports-toolbar-search"
      />
      <el-button :icon="Download" @click="exportSoCsv">{{ t('pages.reports.exportSo') }}</el-button>
      <el-button :icon="Download" @click="exportLinesCsv">{{ t('pages.reports.exportLines') }}</el-button>
      <el-button type="primary" :icon="Printer" @click="printReport">{{ t('common.print') }} {{ t('pages.reports.report') }}</el-button>
    </template>

    <div class="report-card">
      <div class="report-card__header">
        <div class="report-card__header-title">{{ t('pages.reports.poOrderDescription') }}</div>
        <div class="report-card__header-sub">PT. Tong Hong Tannery Indonesia</div>
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
              <el-form-item :label="t('common.status')">
                <el-select v-model="status" clearable class="w-full" :placeholder="t('pages.reports.allStatus')">
                  <el-option :label="t('pages.reports.allStatus')" value="" />
                  <el-option :label="t('status.production')" value="production" />
                  <el-option :label="t('status.sample')" value="sample" />
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
        </el-form>
      </div>

      <div v-loading="reportLoading" class="report-card__body">
        <h3 class="report-section-title">{{ t('pages.reports.reviseThickness') }}</h3>
        <el-table
          :data="filteredReviseRows"
          border
          stripe
          size="small"
          class="admin-table report-table"
          table-layout="auto"
          :empty-text="t('pages.reports.tableEmpty')"
        >
          <el-table-column type="index" :label="t('common.noLabel')" width="52" align="center" />
          <el-table-column prop="poNo" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="customer" :label="t('common.customer')" min-width="160" show-overflow-tooltip />
          <el-table-column prop="material" :label="t('common.material')" min-width="140" show-overflow-tooltip />
          <el-table-column prop="oldThickness" :label="t('pages.reports.oldThickness')" min-width="130" />
          <el-table-column prop="newThickness" :label="t('pages.reports.newThickness')" min-width="130">
            <template #default="{ row }">
              <span class="report-new-thickness">{{ row.newThickness }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="qty" :label="t('common.quantity')" min-width="100" align="right">
            <template #default="{ row }">{{ formatQty(row.qty) }}</template>
          </el-table-column>
        </el-table>

        <h3 class="report-section-title">{{ t('pages.reports.productionOrder') }}</h3>
        <el-table
          :data="filteredProductionRows"
          border
          stripe
          size="small"
          class="admin-table report-table"
          table-layout="auto"
          :empty-text="t('pages.reports.tableEmpty')"
        >
          <el-table-column type="index" :label="t('common.noLabel')" width="52" align="center" />
          <el-table-column prop="poNo" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="customer" :label="t('common.customer')" min-width="160" show-overflow-tooltip />
          <el-table-column prop="material" :label="t('common.material')" min-width="140" show-overflow-tooltip />
          <el-table-column prop="color" :label="t('common.color')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="qty" :label="t('common.quantity')" min-width="100" align="right">
            <template #default="{ row }">{{ formatQty(row.qty) }}</template>
          </el-table-column>
          <el-table-column prop="status" :label="t('common.status')" min-width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="poStatusTagType(row.status)" size="small">{{ poStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div class="report-total-line">
          {{ t('pages.reports.totalProductionOrder') }}: <b>{{ formatQty(productionQtySum) }}</b>
        </div>

        <h3 class="report-section-title">{{ t('pages.reports.sample') }}</h3>
        <el-table
          :data="filteredSampleRows"
          border
          stripe
          size="small"
          class="admin-table report-table"
          table-layout="auto"
          :empty-text="t('pages.reports.tableEmpty')"
        >
          <el-table-column type="index" :label="t('common.noLabel')" width="52" align="center" />
          <el-table-column prop="poNo" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="customer" :label="t('common.customer')" min-width="160" show-overflow-tooltip />
          <el-table-column prop="material" :label="t('common.material')" min-width="160" show-overflow-tooltip />
          <el-table-column prop="color" :label="t('common.color')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="qty" :label="t('common.quantity')" min-width="100" align="right">
            <template #default="{ row }">{{ formatQty(row.qty) }}</template>
          </el-table-column>
          <el-table-column prop="status" :label="t('common.status')" min-width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="poStatusTagType(row.status)" size="small">{{ poStatusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div class="report-total-line">
          {{ t('pages.reports.totalSample') }}: <b>{{ formatQty(sampleQtySum) }}</b>
        </div>
      </div>

      <div class="report-card__footer">
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
  reportSalesOrderLinesExportUrl,
  reportSalesOrdersExportUrl,
} from '../../api/client'

const { t, te } = useI18n()

const keyword = ref('')
const dateFrom = ref('')
const dateTo = ref('')
const customer = ref('')
const status = ref('')
const customers = ref([])

const reportLoading = ref(false)
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

async function fetchReport() {
  reportLoading.value = true
  try {
    const q = {}
    if (dateFrom.value) q.date_from = dateFrom.value
    if (dateTo.value) q.date_to = dateTo.value
    if (customer.value) q.customer = customer.value
    const data = await fetchReportPoOrderDescription(q)
    reviseRows.value = data.revise_thickness || []
    productionRows.value = data.production_orders || []
    sampleRows.value = data.samples || []
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    reportLoading.value = false
  }
}

function poStatusLabel(st) {
  if (st && te(`status.${st}`)) return t(`status.${st}`)
  return st || t('common.emptyValue')
}

function poStatusTagType(st) {
  if (st === 'confirmed') return 'success'
  if (st === 'production') return 'warning'
  if (st === 'completed') return 'success'
  if (st === 'draft') return 'info'
  return ''
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
  if (status.value === 'sample') return []
  return productionRows.value.filter((row) => rowMatchesKeyword(row) && rowMatchesCustomer(row))
})

const filteredSampleRows = computed(() => {
  if (status.value === 'production') return []
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

.report-card__filter {
  margin: 0;
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-top: none;
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

.report-table {
  margin-bottom: 12px;
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
