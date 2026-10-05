<template>
  <AdminSection :title="t('pages.mrpReportSelisihWip.title')" :subtitle="t('pages.mrpReportSelisihWip.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>
    <div class="admin-inner-card mb-4">
      <div class="admin-inner-card__body flex flex-wrap gap-2 items-end">
        <el-date-picker v-model="range" type="daterange" value-format="YYYY-MM-DD" />
        <el-input
          v-model="searchQ"
          clearable
          class="w-56"
          :placeholder="t('pages.mrpReportSelisihWip.searchPlaceholder')"
          @keyup.enter="onSearch"
        />
        <el-button type="primary" @click="onSearch">{{ t('common.search') }}</el-button>
        <span class="text-sm text-slate-500">
          {{ t('pages.mrpReportSelisihWip.totalsHint', {
            wip: formatQty(totals.qtyWip),
            actual: formatQty(totals.qtyActual),
            selisih: formatQty(totals.selisihQty),
          }) }}
        </span>
      </div>
    </div>
    <div class="admin-inner-card">
      <el-table
        :data="rows"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('pages.mrpReportSelisihWip.tableEmpty')"
        @sort-change="onSortChange"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="kode_wip" :label="t('pages.mrpReportSelisihWip.colKodeWip')" min-width="130" sortable="custom" />
        <el-table-column prop="nama_material" :label="t('pages.mrpReportSelisihWip.colNamaMaterial')" min-width="160" sortable="custom" />
        <el-table-column prop="thickness" :label="t('pages.mrpReportSelisihWip.colThickness')" width="100" sortable="custom" />
        <el-table-column prop="emboss" :label="t('pages.mrpReportSelisihWip.colEmboss')" min-width="100" sortable="custom" />
        <el-table-column prop="warna" :label="t('pages.mrpReportSelisihWip.colWarna')" min-width="100" sortable="custom" />
        <el-table-column prop="qty_wip" :label="t('pages.mrpPacking.colQtyWip')" width="100" align="right" sortable="custom">
          <template #default="{ row }">{{ formatQty(row.qty_wip) }}</template>
        </el-table-column>
        <el-table-column prop="qty_actual" :label="t('pages.mrpPacking.colQtyActual')" width="100" align="right" sortable="custom">
          <template #default="{ row }">{{ formatQty(row.qty_actual) }}</template>
        </el-table-column>
        <el-table-column prop="selisih_qty" :label="t('pages.mrpReportSelisihWip.colSelisihQty')" width="110" align="right" sortable="custom">
          <template #default="{ row }">
            <span :class="selisihClass(row.selisih_qty)">{{ formatQty(row.selisih_qty) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="selisih_pct" :label="t('pages.mrpReportSelisihWip.colSelisihPct')" width="100" align="right" sortable="custom">
          <template #default="{ row }">
            <span v-if="row.selisih_pct == null">—</span>
            <span v-else :class="selisihClass(row.selisih_qty)">{{ formatPct(row.selisih_pct) }}</span>
          </template>
        </el-table-column>
      </el-table>
      <div class="mt-3 flex justify-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          background
          small
          @current-change="reload"
          @size-change="() => { page = 1; reload() }"
        />
      </div>
    </div>
  </AdminSection>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { mrpReportSelisihWip } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const rows = ref([])
const searchQ = ref('')
const today = new Date().toISOString().slice(0, 10)
const range = ref([today, today])
const totals = reactive({ qtyWip: 0, qtyActual: 0, selisihQty: 0 })
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const sortBy = ref('tanggal')
const sortDir = ref('desc')

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return n.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

function formatPct(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  const sign = n > 0 ? '+' : ''
  return `${sign}${n.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })}%`
}

function selisihClass(selisih) {
  const n = Number(selisih)
  if (n > 1e-9) return 'text-emerald-600 font-medium'
  if (n < -1e-9) return 'text-red-600 font-medium'
  return ''
}

function onSearch() {
  page.value = 1
  reload()
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'tanggal'
  sortDir.value = mapped.sortDir || 'desc'
  page.value = 1
  reload()
}

async function reload() {
  loading.value = true
  try {
    const [start_date, end_date] = range.value || [today, today]
    const data = await mrpReportSelisihWip(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
        extra: { start_date, end_date, q: searchQ.value.trim() },
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items.length ? pageData.items : (data.rows || [])
    total.value = pageData.total || (data.rows || []).length
    totals.qtyWip = data.total_qty_wip || 0
    totals.qtyActual = data.total_qty_actual || 0
    totals.selisihQty = data.total_selisih_qty || 0
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}
onMounted(reload)
</script>
