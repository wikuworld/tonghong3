<template>
  <AdminSection :title="t('pages.mrpReportPacking.title')" :subtitle="t('pages.mrpReportPacking.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>
    <div class="admin-inner-card mb-4">
      <div class="admin-inner-card__body flex flex-wrap gap-2 items-end">
        <el-date-picker v-model="range" type="daterange" value-format="YYYY-MM-DD" />
        <el-button type="primary" @click="onSearch">{{ t('common.search') }}</el-button>
      <span class="text-sm text-slate-500">Pack: {{ totals.pack }} · Lembar: {{ totals.lembar }} · Ukuran: {{ totals.ukuran }}</span>
      </div>
    </div>
    <div class="admin-inner-card">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')" @sort-change="onSortChange">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="tanggal" :label="t('common.date')" width="120" sortable="custom" />
        <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="120" sortable="custom" />
        <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="120" sortable="custom" />
        <el-table-column prop="kode_process" :label="t('pages.mrpPacking.kodePacking')" min-width="140" sortable="custom" />
        <el-table-column prop="pack" label="Pack" width="80" />
        <el-table-column prop="qty" label="Lembar" width="90" />
        <el-table-column prop="size" label="Ukuran" width="90" />
        <el-table-column prop="status" :label="t('common.status')" width="110" sortable="custom" />
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
import { mrpReportPacking } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const rows = ref([])
const today = new Date().toISOString().slice(0, 10)
const range = ref([today, today])
const totals = reactive({ pack: 0, lembar: 0, ukuran: 0 })
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const sortBy = ref('tanggal')
const sortDir = ref('desc')

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
    const data = await mrpReportPacking(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
        extra: { start_date, end_date },
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items.length ? pageData.items : (data.rows || [])
    total.value = pageData.total || (data.rows || []).length
    totals.pack = data.total_all_pack || 0
    totals.lembar = data.total_all_lembar || 0
    totals.ukuran = data.total_all_ukuran || 0
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}
onMounted(reload)
</script>
