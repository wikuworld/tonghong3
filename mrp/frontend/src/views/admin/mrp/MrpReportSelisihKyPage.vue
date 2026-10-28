<template>
  <AdminSection :title="t('pages.mrpReportSelisihKy.title')" :subtitle="t('pages.mrpReportSelisihKy.subtitle')">
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
          :placeholder="t('pages.mrpReportSelisihKy.searchPlaceholder')"
          @keyup.enter="onSearch"
        />
        <el-button type="primary" @click="onSearch">{{ t('common.search') }}</el-button>
        <span class="text-sm text-slate-500">
          {{ t('pages.mrpReportSelisihKy.totalsHint', {
            lebih: formatQty(totals.lebih),
            kurang: formatQty(totals.kurang),
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
        :empty-text="t('pages.mrpReportSelisihKy.tableEmpty')"
        @sort-change="onSortChange"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="tanggal" :label="t('pages.mrpReportSelisihKy.colTanggal')" width="120" sortable="custom" />
        <el-table-column prop="kode_wip" :label="t('pages.mrpReportSelisihKy.colWip')" min-width="130" sortable="custom" />
        <el-table-column prop="kode_palet" :label="t('pages.mrpReportSelisihKy.colKy')" min-width="120" sortable="custom" />
        <el-table-column prop="kode_yl" :label="t('pages.mrpReportSelisihKy.colYl')" min-width="120" sortable="custom" />
        <el-table-column prop="target_qty" :label="t('pages.mrpReportSelisihKy.colStok')" width="120" align="right" sortable="custom">
          <template #default="{ row }">{{ formatQty(row.target_qty) }}</template>
        </el-table-column>
        <el-table-column prop="actual_qty" :label="t('pages.mrpReportSelisihKy.colUkur')" width="110" align="right" sortable="custom">
          <template #default="{ row }">{{ formatQty(row.actual_qty) }}</template>
        </el-table-column>
        <el-table-column prop="selisih" :label="t('pages.mrpReportSelisihKy.colSelisih')" width="110" align="right" sortable="custom">
          <template #default="{ row }">
            <span :class="selisihClass(row.selisih)">{{ formatQty(row.selisih) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="keterangan" :label="t('pages.mrpReportSelisihKy.colKet')" min-width="120" sortable="custom" />
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
import { mrpReportSelisihKy } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const rows = ref([])
const searchQ = ref('')
const today = new Date().toISOString().slice(0, 10)
const range = ref([today, today])
const totals = reactive({ lebih: 0, kurang: 0 })
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
    const data = await mrpReportSelisihKy(
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
    totals.lebih = data.total_lebih || 0
    totals.kurang = data.total_kurang || 0
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}
onMounted(reload)
</script>
