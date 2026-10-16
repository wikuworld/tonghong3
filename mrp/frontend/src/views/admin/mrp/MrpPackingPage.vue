<template>
  <AdminSection :title="t('pages.mrpPacking.title')" :subtitle="t('pages.mrpPacking.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <el-tabs v-model="tab" class="admin-tabs" @tab-change="onTabChange">
      <el-tab-pane :label="t('pages.mrpPacking.tabWorkspace')" name="workspace">
        <div v-if="canCreate" class="admin-inner-card">
          <div class="admin-inner-card__body">
            <MrpPackingCreateDialog ref="workspaceRef" embedded />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.mrpPacking.tabHistory')" name="history">
        <div class="admin-inner-card">
          <div class="admin-inner-card__head">
            <h3 class="admin-inner-card__title">{{ t('pages.mrpPacking.historyTitle') }}</h3>
            <el-input
              v-model="historySearch"
              clearable
              size="small"
              class="w-52"
              :placeholder="t('pages.mrpPacking.searchPlaceholder')"
            />
          </div>
          <el-table
            :data="filteredHistoryRows"
            v-loading="loading"
            border
            stripe
            size="small"
            class="admin-table"
            :empty-text="t('common.tableEmpty')"
            @sort-change="onHistorySortChange"
          >
            <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
              <template #default="{ $index }">{{ (historyPage - 1) * historyPageSize + $index + 1 }}</template>
            </el-table-column>
            <el-table-column prop="kode_packing" :label="t('pages.mrpPacking.kodePacking')" min-width="140" show-overflow-tooltip sortable="custom" />
            <el-table-column prop="kode_wip" label="WIP" min-width="120" show-overflow-tooltip />
            <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="lot_no" :label="t('pages.mrpPacking.lotNo')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" width="120" show-overflow-tooltip />
            <el-table-column prop="customer" :label="t('common.customer')" min-width="120" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpPacking.pieces')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.total_lembar) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpPacking.quantity')" width="100" align="right">
              <template #default="{ row }">{{ formatQty(row.total_ukuran) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.status')" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="success" size="small" effect="plain">
                  {{ statusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="date_created" :label="t('common.date')" width="120" sortable="custom">
              <template #default="{ row }">{{ formatDate(row.date_created) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <AdminTableActions
                  :show-view="true"
                  :show-edit="canUpdate && !!row.can_correct"
                  @view="$router.push(`/admin/mrp/packing/${row.id}`)"
                  @edit="$router.push(`/admin/mrp/packing/${row.id}?edit=1`)"
                />
              </template>
            </el-table-column>
          </el-table>
          <div class="mt-3 flex justify-end">
            <el-pagination
              v-model:current-page="historyPage"
              v-model:page-size="historyPageSize"
              :total="historyTotal"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next"
              background
              small
              @current-change="loadHistory"
              @size-change="() => { historyPage = 1; loadHistory() }"
            />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </AdminSection>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import MrpPackingCreateDialog from './MrpPackingCreateDialog.vue'
import { can } from '../../../security/permissions'
import { mrpListPacking } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const workspaceRef = ref(null)
const loading = ref(false)
const tab = ref('workspace')
const historyRows = ref([])
const historySearch = ref('')
const historyPage = ref(1)
const historyPageSize = ref(20)
const historyTotal = ref(0)
const historySortBy = ref('date_created')
const historySortDir = ref('desc')
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))

const filteredHistoryRows = computed(() => {
  const q = historySearch.value.trim().toLowerCase()
  if (!q) return historyRows.value
  return historyRows.value.filter((r) =>
    [r.kode_packing, r.kode_wip, r.no_so, r.lot_no, r.no_po, r.customer, r.status]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function formatDate(v) {
  if (!v) return '—'
  return String(v).slice(0, 10)
}

function statusLabel(status) {
  if (status === 'finished') return t('pages.mrpPacking.statusFinished')
  if (status === 'in_progress') return t('pages.mrpPacking.statusInProgress')
  return status || '—'
}

async function loadHistory() {
  loading.value = true
  try {
    const data = await mrpListPacking(
      buildPageParams({
        page: historyPage.value,
        pageSize: historyPageSize.value,
        sortBy: historySortBy.value,
        sortDir: historySortDir.value,
        extra: { status: 'finished' },
      }),
    )
    const pageData = normalizePageResult(data, { page: historyPage.value, pageSize: historyPageSize.value })
    historyRows.value = pageData.items
    historyTotal.value = pageData.total
  } catch (e) {
    historyRows.value = []
    historyTotal.value = 0
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

function onHistorySortChange(payload) {
  const mapped = fromElSortChange(payload)
  historySortBy.value = mapped.sortBy || 'date_created'
  historySortDir.value = mapped.sortDir || 'desc'
  historyPage.value = 1
  loadHistory()
}

function onTabChange(name) {
  if (name === 'history') loadHistory()
}

async function reload() {
  if (tab.value === 'history') {
    await loadHistory()
    return
  }
  loading.value = true
  try {
    await workspaceRef.value?.reload?.()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.w-52 {
  width: 13rem;
}
</style>
