<template>
  <div class="space-y-5">
    <el-alert v-if="apiError" type="warning" :title="apiError" show-icon class="mb-2" />
    <el-row :gutter="12">
      <el-col :md="6" :sm="12" :xs="24" v-for="card in topDigestCards" :key="card.title">
        <el-card shadow="hover" class="top-digest-card">
          <div class="top-digest-title">{{ card.title }}</div>
          <div class="top-digest-value">{{ card.value }}</div>
          <div class="top-digest-note">{{ card.note }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <div class="text-xl font-semibold text-slate-800">{{ t('dashboard.title') }}</div>
          <div class="mt-1 text-sm text-slate-500">{{ t('dashboard.subtitle') }}</div>
        </div>
        <div class="flex items-center gap-2">
          <el-tag type="success" effect="light">{{ t('common.realtime') }}</el-tag>
          <el-tag v-if="asOfLabel" effect="plain">{{ asOfLabel }}</el-tag>
          <el-tag v-else effect="plain">{{ t('common.updatedAgo') }}</el-tag>
        </div>
      </div>
    </el-card>

    <el-row :gutter="12">
      <el-col :md="6" :sm="12" :xs="24" v-for="item in stats" :key="item.label">
        <el-card shadow="hover" class="border-indigo-50">
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-2">
                <div class="text-xs font-medium uppercase tracking-wide text-slate-500">{{ item.label }}</div>
                <el-badge v-if="item.badge > 0" :value="item.badge" :max="99" type="danger" />
              </div>
              <div class="mt-2 text-3xl font-semibold text-slate-800">{{ item.value }}</div>
            </div>
            <el-icon class="rounded-lg p-2 text-white" :class="item.iconBg">
              <component :is="item.icon" />
            </el-icon>
          </div>
          <div class="mt-3 text-xs" :class="item.deltaColor">{{ item.delta }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="12">
      <el-col :md="16" :xs="24">
        <AdminSection :title="t('dashboard.trendTitle')">
          <VChart class="chart-lg" :option="productionTrendOption" autoresize />
        </AdminSection>
      </el-col>
      <el-col :md="8" :xs="24">
        <AdminSection :title="t('dashboard.compositionTitle')">
          <VChart class="chart-lg" :option="poCompositionOption" autoresize />
        </AdminSection>
      </el-col>
    </el-row>

    <el-row :gutter="12">
      <el-col :md="12" :xs="24">
        <AdminSection title="Received PO PU">
          <div class="rcvd-card-body">
            <div v-for="group in rcvdPoPu" :key="group.buyer" class="rcvd-group">
              <div class="rcvd-group-title">{{ group.buyer }}</div>
              <div v-for="line in group.lines" :key="`${group.buyer}-${line.factory}`" class="rcvd-line">
                <span>{{ line.factory }}</span>
                <strong>{{ formatSf(line.sf) }} sf</strong>
              </div>
            </div>
            <el-divider class="rcvd-divider" />
            <div class="rcvd-total">TOTAL RECEIVED PO PU : {{ formatSf(totalPoPu) }} sf</div>
          </div>
        </AdminSection>
      </el-col>
      <el-col :md="12" :xs="24">
        <AdminSection title="Received PO SUEDE">
          <div class="rcvd-card-body">
            <div v-for="group in rcvdPoSuede" :key="group.buyer" class="rcvd-group">
              <div class="rcvd-group-title">{{ group.buyer }}</div>
              <div v-for="line in group.lines" :key="`${group.buyer}-${line.factory}`" class="rcvd-line">
                <span>{{ line.factory }}</span>
                <strong>{{ formatSf(line.sf) }} sf</strong>
              </div>
            </div>
            <el-divider class="rcvd-divider" />
            <div class="rcvd-total">TOTAL RECEIVED PO SUEDE : {{ formatSf(totalPoSuede) }} sf</div>
          </div>
        </AdminSection>
      </el-col>
    </el-row>

    <el-row :gutter="12">
      <el-col :md="12" :xs="24" v-for="day in deliveryDays" :key="day.date">
        <AdminSection title="Delivery">
          <div class="delivery-subtitle">DOK {{ deliveryDateLabel(day.date) }}</div>
          <div v-if="day.lines?.length" class="rcvd-card-body">
            <div v-for="line in day.lines" :key="`${day.date}-${line.customer_code}-${line.status_label}`" class="rcvd-line">
              <span>{{ line.customer_code }} : {{ formatSf(line.sf) }} sf</span>
              <strong>{{ line.status_label }}</strong>
            </div>
            <el-divider class="rcvd-divider" />
            <div class="rcvd-total">TOTAL DELIVERY {{ deliveryDateLabel(day.date) }} : {{ formatSf(day.total_sf) }} sf</div>
          </div>
          <el-empty v-else description="Belum ada data delivery pada tanggal ini" />
        </AdminSection>
      </el-col>
    </el-row>

    <el-row :gutter="12">
      <el-col :md="12" :xs="24">
        <AdminSection :title="t('dashboard.pipelineTitle')">
          <VChart class="chart-md" :option="pipelineStatusOption" autoresize />
        </AdminSection>
      </el-col>
      <el-col :md="12" :xs="24">
        <AdminSection :title="t('dashboard.recentActivities')">
          <el-empty v-if="!activityFeed.length" :description="t('dashboard.activityEmpty')" />
          <el-timeline v-else>
            <el-timeline-item
              v-for="(ev, i) in activityFeed"
              :key="i"
              :timestamp="formatActivityTime(ev.occurred_at)"
              :type="timelineType(ev)"
            >
              {{ activityText(ev) }}
            </el-timeline-item>
          </el-timeline>
        </AdminSection>
      </el-col>
    </el-row>

    <AdminSection :title="t('dashboard.monitoringTitle')">
      <el-table :data="monitoringRows" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('common.tableEmpty')">
        <el-table-column prop="process" :label="t('common.process')" min-width="190" show-overflow-tooltip />
        <el-table-column prop="target" :label="t('common.target')" min-width="110" align="right" />
        <el-table-column prop="actual" :label="t('common.actual')" min-width="110" align="right" />
        <el-table-column :label="t('common.achievement')" min-width="220">
          <template #default="{ row }">
            <el-progress :percentage="row.achievement" :status="row.achievement >= 95 ? 'success' : ''" />
          </template>
        </el-table-column>
        <el-table-column prop="remark" :label="t('common.remark')" min-width="220" show-overflow-tooltip />
      </el-table>
    </AdminSection>
  </div>
</template>

<script setup>
import { computed, onMounted, provide, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { dashboardSummary } from '../../api/client'
import VChart, { THEME_KEY } from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart, BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
} from 'echarts/components'
import { DataLine, TrendCharts, CircleCheck, Tickets } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'

const { t, te } = useI18n()

const apiSummary = ref(null)
const apiError = ref('')

onMounted(async () => {
  try {
    apiSummary.value = await dashboardSummary()
  } catch (e) {
    apiError.value = e?.message || String(e)
  }
})

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
])

provide(THEME_KEY, 'light')

const asOfLabel = computed(() => {
  const d = apiSummary.value?.as_of
  if (!d) return ''
  return t('dashboard.asOf', { date: d })
})

const activityFeed = computed(() => apiSummary.value?.activity_feed ?? [])

function formatActivityTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return ''
  return d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}

function statusLabel(st) {
  if (st && te(`status.${st}`)) return t(`status.${st}`)
  return st || t('common.emptyValue')
}

function activityText(ev) {
  const st = statusLabel(ev.status)
  if (ev.kind === 'po') return t('dashboard.feedPo', { ref: ev.ref, status: st })
  if (ev.kind === 'prod') return t('dashboard.feedProd', { ref: ev.ref, status: st })
  if (ev.kind === 'del') return t('dashboard.feedDel', { ref: ev.ref, status: st })
  return ev.ref
}

function timelineType(ev) {
  if (ev.kind === 'po' && (ev.status === 'confirmed' || ev.status === 'production')) return 'success'
  if (ev.kind === 'del') return 'warning'
  if (ev.kind === 'prod' && ev.status === 'in_progress') return 'warning'
  return 'primary'
}

function weekdayLabelFromIso(iso) {
  const d = new Date(`${iso}T12:00:00`)
  if (Number.isNaN(d.getTime())) return iso
  const keys = ['daySun', 'dayMon', 'dayTue', 'dayWed', 'dayThu', 'dayFri', 'daySat']
  return t(`dashboard.${keys[d.getDay()]}`)
}

function categoryPieLabel(cat) {
  if (cat && te(`status.${cat}`)) return t(`status.${cat}`)
  return cat || t('common.emptyValue')
}

const stats = computed(() => {
  const c = apiSummary.value?.counts
  const rate = apiSummary.value?.exchange_rate
  const rateLabel = rate
    ? `1 USD = ${Number(rate.idr_per_usd).toLocaleString()} IDR`
    : t('common.emptyValue')
  return [
    {
      label: t('dashboard.kpiTotalSo'),
      value: c?.sales_orders ?? t('common.emptyValue'),
      badge: c?.sales_orders_open ?? 0,
      delta: t('dashboard.kpiOpenSoHint', { n: c?.sales_orders_open ?? t('common.emptyValue') }),
      deltaColor: 'text-slate-600',
      icon: Tickets,
      iconBg: 'bg-blue-600',
    },
    {
      label: t('dashboard.kpiProduction'),
      value: c?.production_orders ?? t('common.emptyValue'),
      badge: c?.production_in_progress ?? 0,
      delta: t('dashboard.kpiProdInProgress', { n: c?.production_in_progress ?? 0 }),
      deltaColor: 'text-emerald-600',
      icon: TrendCharts,
      iconBg: 'bg-violet-600',
    },
    {
      label: t('dashboard.kpiQcReject'),
      value: c?.qc_reject_lines ?? t('common.emptyValue'),
      badge: c?.qc_reject_lines ?? 0,
      delta:
        c?.qc_total_lines != null && c.qc_total_lines > 0
          ? `${t('dashboard.qcPassRate')}: ${Math.round((100 * (c.qc_ok_lines || 0)) / c.qc_total_lines)}%`
          : t('dashboard.kpiQcRejectHint'),
      deltaColor: 'text-rose-600',
      icon: CircleCheck,
      iconBg: 'bg-emerald-600',
    },
    {
      label: t('dashboard.kpiExchange'),
      value: rateLabel,
      badge: 0,
      delta: t('dashboard.kpiDeliveryHint', { n: c?.deliveries ?? t('common.emptyValue') }),
      deltaColor: 'text-amber-600',
      icon: DataLine,
      iconBg: 'bg-amber-500',
    },
  ]
})

const productionTrendOption = computed(() => {
  const tr = apiSummary.value?.trend_7d
  const labels = (tr?.labels ?? []).map((iso) => weekdayLabelFromIso(iso))
  const prod = tr?.production_orders_per_day ?? []
  const del = tr?.deliveries_per_day ?? []
  return {
    tooltip: { trigger: 'axis' },
    legend: { top: 0 },
    grid: { left: 48, right: 20, top: 36, bottom: 24 },
    xAxis: {
      type: 'category',
      data: labels.length ? labels : [t('dashboard.dayMon')],
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: t('dashboard.trendLegendProd'),
        type: 'line',
        smooth: true,
        data: prod.length ? prod : [0],
        lineStyle: { width: 3 },
        areaStyle: { opacity: 0.1 },
        color: '#2563eb',
      },
      {
        name: t('dashboard.trendLegendDel'),
        type: 'line',
        smooth: true,
        data: del.length ? del : [0],
        lineStyle: { width: 3 },
        areaStyle: { opacity: 0.08 },
        color: '#14b8a6',
      },
    ],
  }
})

const poCompositionOption = computed(() => {
  const raw = apiSummary.value?.po_by_category ?? []
  const data =
    raw.length > 0
      ? raw.map((row) => ({
          value: row.count,
          name: categoryPieLabel(row.category),
          itemStyle: {
            color:
              row.category === 'sample'
                ? '#14b8a6'
                : row.category === 'production'
                  ? '#2563eb'
                  : row.category === 'claim'
                    ? '#ef4444'
                    : row.category === 'return'
                      ? '#f97316'
                      : row.category === 'subcont'
                        ? '#8b5cf6'
                        : '#f59e0b',
          },
        }))
      : [{ value: 1, name: t('dashboard.noPoCategory'), itemStyle: { color: '#e2e8f0' } }]
  return {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, left: 'center' },
    series: [
      {
        name: t('dashboard.chartPoComposition'),
        type: 'pie',
        radius: ['40%', '68%'],
        avoidLabelOverlap: false,
        label: { show: raw.length > 0 },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' } },
        data,
      },
    ],
  }
})

const pipelineStatusOption = computed(() => {
  const p = apiSummary.value?.pipeline
  const vals = p
    ? [p.po_total, p.production_orders, p.qc_ok_lines, p.deliveries, p.invoices]
    : [0, 0, 0, 0, 0]
  const colors = ['#334155', '#2563eb', '#16a34a', '#0ea5e9', '#f59e0b']
  return {
    tooltip: { trigger: 'axis' },
    grid: { left: 48, right: 20, top: 12, bottom: 24 },
    xAxis: {
      type: 'category',
      data: [
        t('dashboard.chartPO'),
        t('dashboard.chartProduction'),
        t('dashboard.chartQcOk'),
        t('menu.delivery'),
        t('menu.invoice'),
      ],
      axisLabel: { interval: 0 },
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        type: 'bar',
        data: vals.map((v, i) => ({ value: v, itemStyle: { color: colors[i] } })),
        barWidth: 28,
        borderRadius: [6, 6, 0, 0],
      },
    ],
  }
})

const monitoringRows = computed(() => {
  const m = apiSummary.value?.monitoring
  if (!m) return []
  const pct = (v) => (v != null ? `${v}%` : t('common.emptyValue'))
  const ach = (v) => (v != null ? Math.min(100, Math.round(Number(v))) : 0)
  return [
    {
      process: t('dashboard.monitoringProcessPo'),
      target: 100,
      actual: pct(m.so_pipeline_pct),
      achievement: ach(m.so_pipeline_pct),
      remark: t('dashboard.monitoringRemarkPo'),
    },
    {
      process: t('dashboard.monitoringProcessProduction'),
      target: 100,
      actual: pct(m.production_active_pct),
      achievement: ach(m.production_active_pct),
      remark: t('dashboard.monitoringRemarkProduction'),
    },
    {
      process: t('dashboard.monitoringProcessQc'),
      target: 100,
      actual: pct(m.qc_pass_pct),
      achievement: ach(m.qc_pass_pct),
      remark: t('dashboard.monitoringRemarkQc'),
    },
    {
      process: t('dashboard.monitoringProcessDelivery'),
      target: 100,
      actual: pct(m.delivery_coverage_pct),
      achievement: ach(m.delivery_coverage_pct),
      remark: t('dashboard.monitoringRemarkDelivery'),
    },
  ]
})

const rcvdDateLabel = computed(() => {
  const d = apiSummary.value?.rcvd_po?.as_of
  if (!d) return '-'
  const dt = new Date(`${d}T00:00:00`)
  if (Number.isNaN(dt.getTime())) return d
  const mm = String(dt.getMonth() + 1).padStart(2, '0')
  const dd = String(dt.getDate()).padStart(2, '0')
  return `${mm}/${dd}`
})

function groupRcvdLines(lines) {
  const grouped = new Map()
  for (const line of lines || []) {
    const buyer = (line?.buyer || '-').toString()
    if (!grouped.has(buyer)) grouped.set(buyer, [])
    grouped.get(buyer).push({
      factory: (line?.factory || '-').toString(),
      sf: Number(line?.sf || 0),
    })
  }
  return Array.from(grouped.entries()).map(([buyer, buyerLines]) => ({
    buyer,
    lines: buyerLines,
  }))
}

const rcvdPoPu = computed(() => groupRcvdLines(apiSummary.value?.rcvd_po?.pu_lines || []))
const rcvdPoSuede = computed(() => groupRcvdLines(apiSummary.value?.rcvd_po?.suede_lines || []))
const totalPoPu = computed(() => Number(apiSummary.value?.rcvd_po?.total_pu_sf || 0))
const totalPoSuede = computed(() => Number(apiSummary.value?.rcvd_po?.total_suede_sf || 0))
const deliveryDays = computed(() => apiSummary.value?.delivery_digest?.days || [])
const topDigestCards = computed(() => {
  const firstDay = deliveryDays.value[0]
  const secondDay = deliveryDays.value[1]
  return [
    {
      title: `Received PO PU ${rcvdDateLabel.value}`,
      value: `${formatSf(totalPoPu.value)} sf`,
      note: `${rcvdPoPu.value.reduce((n, g) => n + (g.lines?.length || 0), 0)} baris buyer/factory`,
    },
    {
      title: `Received PO SUEDE ${rcvdDateLabel.value}`,
      value: `${formatSf(totalPoSuede.value)} sf`,
      note: `${rcvdPoSuede.value.reduce((n, g) => n + (g.lines?.length || 0), 0)} baris buyer/factory`,
    },
    {
      title: 'Delivery',
      value: `${formatSf(firstDay?.total_sf || 0)} sf`,
      note: firstDay?.lines?.length ? `${firstDay.lines.length} baris dok` : 'Belum ada data',
    },
    {
      title: 'Delivery',
      value: `${formatSf(secondDay?.total_sf || 0)} sf`,
      note: secondDay?.lines?.length ? `${secondDay.lines.length} baris dok` : 'Belum ada data',
    },
  ]
})

function formatSf(v) {
  return Number(v || 0).toLocaleString()
}

function deliveryDateLabel(iso) {
  if (!iso) return '-'
  const dt = new Date(`${iso}T00:00:00`)
  if (Number.isNaN(dt.getTime())) return iso
  const mm = String(dt.getMonth() + 1).padStart(2, '0')
  const dd = String(dt.getDate()).padStart(2, '0')
  return `${mm}/${dd}`
}
</script>

<style scoped>
.chart-lg {
  height: 320px;
}

.chart-md {
  height: 300px;
}

.admin-table {
  width: 100%;
}

.top-digest-card {
  border: 1px solid #e2e8f0;
}

.top-digest-title {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  margin-bottom: 6px;
}

.top-digest-value {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.2;
}

.top-digest-note {
  margin-top: 6px;
  font-size: 12px;
  color: #94a3b8;
}

.rcvd-card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rcvd-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rcvd-group-title {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
  margin-top: 4px;
}

.rcvd-line {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
  color: #475569;
}

.rcvd-divider {
  margin: 6px 0 2px;
}

.rcvd-total {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.delivery-subtitle {
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}
</style>
