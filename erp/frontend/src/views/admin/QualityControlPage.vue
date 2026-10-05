<template>
  <AdminSection :title="t('pages.qc.title')" :subtitle="t('pages.qc.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.qc.searchPlaceholder')"
        clearable
        class="qc-toolbar-search"
      />
    </template>

    <el-alert class="mb-3" type="info" :closable="false" show-icon>
      <template #title>
        <span>{{ t('pages.qc.bookHint') }}</span>
        <a
          class="ml-2 text-primary underline"
          :href="mrpUiUrl('/admin/mrp/checkpoint')"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ t('pages.qc.openMrpCheckpoint') }}
        </a>
      </template>
    </el-alert>

    <div class="mb-3">
      <el-switch v-model="filterMrpOnly" :active-text="t('pages.qc.filterMrpOnly')" />
    </div>

    <el-table
      :data="rows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="fixed"
      :empty-text="t('pages.qc.tableEmpty')"
      @sort-change="onSortChange"
    >
      <el-table-column
        type="index"
        :label="t('common.noLabel')"
        width="56"
        align="center"
        :index="(i) => (page - 1) * pageSize + i + 1"
      />
      <el-table-column prop="qc_number" :label="t('common.qcNo')" min-width="130" sortable="custom">
        <template #default="{ row }">
          <span>{{ row.qc_number }}</span>
          <el-tag v-if="isMrpBook(row)" size="small" type="warning" class="ml-1">{{ t('pages.qc.mrpBadge') }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="production_label" :label="t('common.productionNo')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="qc_date" :label="t('common.date')" width="120" sortable="custom" />
      <el-table-column :label="t('common.result')" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.sample_result" :type="row.sample_result === 'ok' ? 'success' : 'danger'" size="small">
            {{ row.sample_result === 'ok' ? t('status.ok') : t('status.ng') }}
          </el-tag>
          <span v-else>{{ t('common.emptyValue') }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="88" align="center" fixed="right">
        <template #default="{ row }">
          <AdminTableActions :show-view="true" @view="openDetail(row)" />
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-3 flex justify-end">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        size="small"
        background
        layout="total, sizes, prev, pager, next"
        :total="totalRows"
        :page-sizes="[20, 50, 100, 200]"
      />
    </div>

    <el-dialog v-model="detailVisible" :title="t('pages.qc.dialogDetail')" width="640px" destroy-on-close align-center>
      <el-descriptions v-if="detailHdr" :column="1" border size="small">
        <el-descriptions-item :label="t('common.qcNo')">{{ detailHdr.qc_number }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.productionNo')">{{ detailHdr.production_id }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.date')">{{ detailHdr.qc_date || t('common.emptyValue') }}</el-descriptions-item>
      </el-descriptions>
      <el-table v-if="detailLines.length" :data="detailLines" class="mt-3" border size="small" table-layout="auto" max-height="280">
        <el-table-column prop="thickness_actual" :label="t('common.actual')" width="100" />
        <el-table-column prop="thickness_min" :label="t('common.min')" width="80" />
        <el-table-column prop="thickness_max" :label="t('common.max')" width="80" />
        <el-table-column prop="is_ok" :label="t('common.result')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_ok ? 'success' : 'danger'" size="small">{{ row.is_ok ? t('status.ok') : t('status.ng') }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('pages.qc.closeDetail') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import { mrpUiUrl } from '../../utils/mrpUi'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../utils/tableQuery'
import {
  listProduction,
  listQc,
  listQcDetails,
} from '../../api/client'

const { t } = useI18n()
const route = useRoute()
const loading = ref(false)
const keyword = ref('')
const filterMrpOnly = ref(false)
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const sortBy = ref(null)
const sortDir = ref('desc')

async function load() {
  loading.value = true
  try {
    const [qcRaw, prRaw] = await Promise.all([
      listQc(
        buildPageParams({
          page: page.value,
          pageSize: pageSize.value,
          sortBy: sortBy.value,
          sortDir: sortDir.value,
          extra: { q: keyword.value.trim() || undefined },
        }),
      ),
      listProduction({ page_size: 200 }),
    ])
    const qcPage = normalizePageResult(qcRaw, { page: page.value, pageSize: pageSize.value })
    const pr = normalizePageResult(prRaw).items
    const detailLists = await Promise.all(qcPage.items.map((q) => listQcDetails(q.id).catch(() => [])))
    let mapped = qcPage.items.map((q, i) => {
      const lines = detailLists[i]
      const ok = lines.find((l) => l.is_ok)
      const ng = lines.find((l) => l.is_ok === false)
      return {
        ...q,
        qc_date: q.qc_date ? String(q.qc_date).slice(0, 10) : '',
        production_label: `${pr.find((x) => x.id === q.production_id)?.production_number || q.production_id}`,
        sample_result: ok ? 'ok' : ng ? 'ng' : null,
      }
    })
    if (filterMrpOnly.value) mapped = mapped.filter((r) => isMrpBook(r))
    rows.value = mapped
    totalRows.value = filterMrpOnly.value ? mapped.length : qcPage.total
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
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

onMounted(async () => {
  await load()
  const qcIdRaw = route.query.qc_id
  const qcId = Number(qcIdRaw)
  if (!Number.isNaN(qcId) && qcId > 0) {
    const target = rows.value.find((r) => Number(r.id) === qcId)
    if (target) await openDetail(target)
  }
})

watch([page, pageSize], () => load())
let filterTimer = null
watch([keyword, filterMrpOnly], () => {
  page.value = 1
  if (filterTimer) clearTimeout(filterTimer)
  filterTimer = setTimeout(() => load(), 300)
})

function isMrpBook(row) {
  const prod = String(row?.production_label || '').toUpperCase()
  const qcNo = String(row?.qc_number || '').toUpperCase()
  return prod.startsWith('MRP-') || qcNo.startsWith('MRP-')
}

const detailVisible = ref(false)
const detailHdr = ref(null)
const detailLines = ref([])

async function openDetail(row) {
  detailHdr.value = row
  detailLines.value = await listQcDetails(row.id).catch(() => [])
  detailVisible.value = true
}
</script>

<style scoped>
</style>
