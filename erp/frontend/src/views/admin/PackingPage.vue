<template>
  <div class="space-y-4">
    <el-alert class="mb-3" type="info" :closable="false" show-icon>
      <template #title>
        <span>{{ t('pages.packing.bookHint') }}</span>
        <a
          class="ml-2 text-primary underline"
          :href="mrpUiUrl('/admin/mrp/packing')"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ t('pages.packing.openMrpPacking') }}
        </a>
      </template>
    </el-alert>
    <AdminSection :title="t('pages.packing.title')" :subtitle="t('pages.packing.subtitle')">
      <template #actions>
        <el-select
          v-model="statusTableFilter"
          clearable
          :placeholder="t('pages.packing.filterPackingStatus')"
          class="w-36 mr-2"
          @change="onFilterChange"
        >
          <el-option :label="t('status.draft')" value="draft" />
          <el-option :label="t('status.done')" value="done" />
        </el-select>
        <el-switch
          v-model="filterMrpOnly"
          class="mr-2"
          :active-text="t('pages.packing.filterMrpOnly')"
          @change="onFilterChange"
        />
        <el-checkbox v-if="canPrint" v-model="invplFoc" class="mr-2">
          {{ t('pages.packing.invplFoc') }}
        </el-checkbox>
      </template>

      <div class="admin-inner-card">
        <div class="admin-inner-card__head">
          <div>
            <h3 class="admin-inner-card__title">{{ t('pages.packing.listSectionTitle') }}</h3>
            <p class="admin-inner-card__sub">{{ t('pages.packing.listSectionSub') }}</p>
          </div>
          <el-tooltip placement="top-start" :show-after="200">
            <template #content>{{ t('pages.packing.pageHint') }}</template>
            <el-icon class="packing-hint" :size="16" tabindex="0" :aria-label="t('pages.packing.pageHint')">
              <InfoFilled />
            </el-icon>
          </el-tooltip>
        </div>

        <p class="admin-scroll-hint px-4">{{ t('pages.packing.scrollHint') }}</p>

        <div class="admin-table-scroll px-4 pb-4">
          <el-table
            :data="displayRows"
            v-loading="loading"
            border
            stripe
            size="small"
            class="admin-table"
            table-layout="fixed"
            :empty-text="t('pages.packing.tableEmpty')"
            @sort-change="onSortChange"
          >
            <el-table-column
              type="index"
              :label="t('common.noLabel')"
              width="56"
              align="center"
              :index="(i) => (page - 1) * pageSize + i + 1"
            />
            <el-table-column prop="packing_number" :label="t('pages.packing.packingNo')" min-width="180" sortable="custom">
              <template #default="{ row }">
                <span>{{ row.packing_number }}</span>
                <el-tag v-if="isMrpStub(row)" size="small" type="warning" class="ml-1">{{ t('pages.packing.mrpBadge') }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('pages.packing.production')" min-width="180" show-overflow-tooltip>
              <template #default="{ row }">{{ prodLabel(row.production_id) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.packing.qc')" min-width="160" show-overflow-tooltip>
              <template #default="{ row }">{{ qcLabel(row.qc_header_id) }}</template>
            </el-table-column>
            <el-table-column prop="status" :label="t('common.status')" width="100" sortable="custom" />
            <el-table-column prop="created_at" :label="t('pages.packing.createdAt')" min-width="160" sortable="custom" />
            <el-table-column :label="t('common.actions')" width="72" fixed="right" align="center">
              <template #default="{ row }">
                <AdminTableActions
                  :more-items="packingMoreItems(row)"
                  @more="(cmd) => handlePackingMore(row, cmd)"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div class="px-4 pb-4 flex justify-end">
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
      </div>
    </AdminSection>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Document, Grid, InfoFilled, Printer, Stamp } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import { can } from '../../security/permissions'
import { mrpUiUrl } from '../../utils/mrpUi'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../utils/tableQuery'
import {
  fetchAuthenticatedDocument,
  listPacking,
  listProduction,
  listQc,
  markInvplPrinted,
} from '../../api/client'

const { t } = useI18n()
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const sortBy = ref(null)
const sortDir = ref('desc')
const statusTableFilter = ref('')
const filterMrpOnly = ref(false)

const displayRows = computed(() => {
  return (rows.value || []).filter((r) => {
    const mrpOk = !filterMrpOnly.value || isMrpStub(r)
    return mrpOk
  })
})
function isMrpStub(row) {
  return String(row?.source || '').toLowerCase() === 'mrp' || Boolean(row?.mrp_fg_id)
}
const canUpdate = can('packing', 'update')
const canPrint = can('packing', 'print')
const productions = ref([])
const qcs = ref([])
const loading = ref(false)
const markInvplId = ref(null)
const invplFoc = ref(false)

function invplPath(id, suffix = '') {
  const q = invplFoc.value ? '?foc=1' : ''
  return `/documents/invpl/${id}${suffix}${q}`
}

function prodLabel(pid) {
  const p = productions.value.find((x) => x.id === pid)
  return p ? `${p.production_number || p.id}` : pid
}

function qcLabel(qid) {
  const q = qcs.value.find((x) => x.id === qid)
  return q ? `${q.qc_number || q.id}` : qid
}

async function loadLookups() {
  const [pr, qc] = await Promise.all([
    listProduction({ page_size: 200 }),
    listQc({ page_size: 200 }),
  ])
  productions.value = normalizePageResult(pr).items
  qcs.value = normalizePageResult(qc).items
}

async function load() {
  loading.value = true
  try {
    const params = buildPageParams({
      page: page.value,
      pageSize: pageSize.value,
      sortBy: sortBy.value,
      sortDir: sortDir.value,
      extra: {
        status: statusTableFilter.value || undefined,
      },
    })
    const pageData = normalizePageResult(await listPacking(params), {
      page: page.value,
      pageSize: pageSize.value,
    })
    rows.value = pageData.items
    totalRows.value = pageData.total
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function onFilterChange() {
  page.value = 1
  load()
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy
  sortDir.value = mapped.sortDir
  page.value = 1
  load()
}

onMounted(async () => {
  await loadLookups()
  await load()
})

watch([page, pageSize], () => load())

async function openInvpl(id) {
  try {
    await fetchAuthenticatedDocument(invplPath(id), { mode: 'open' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadInvplPdf(id) {
  try {
    await fetchAuthenticatedDocument(invplPath(id, '/pdf'), { mode: 'open' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadInvplExcel(id) {
  try {
    await fetchAuthenticatedDocument(invplPath(id, '/xlsx'), {
      mode: 'download',
      downloadFallbackName: `invpl_${id}.xlsx`,
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function markInvpl(row) {
  markInvplId.value = row.id
  try {
    await markInvplPrinted(row.id)
    ElMessage.success(t('pages.packing.invplMarked'))
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    markInvplId.value = null
  }
}

function packingMoreItems(row) {
  const items = []
  if (canPrint) {
    items.push(
      { command: 'printInvpl', label: t('pages.packing.printInvpl'), icon: Printer },
      { command: 'pdf', label: t('pages.packing.pdf'), icon: Document },
      { command: 'excel', label: t('pages.packing.excel'), icon: Grid },
    )
  }
  if (canUpdate) {
    items.push({
      command: 'markInvpl',
      label: t('pages.packing.markInvpl'),
      icon: Stamp,
      disabled: markInvplId.value === row.id,
    })
  }
  return items
}

function handlePackingMore(row, command) {
  if (command === 'printInvpl') openInvpl(row.id)
  else if (command === 'pdf') downloadInvplPdf(row.id)
  else if (command === 'excel') downloadInvplExcel(row.id)
  else if (command === 'markInvpl') markInvpl(row)
}
</script>

<style scoped>
.packing-hint {
  color: #64748b;
  cursor: help;
}
</style>
