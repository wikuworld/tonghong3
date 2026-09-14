<template>
  <AdminSection :title="t('pages.mrpPacking.title')" :subtitle="t('pages.mrpPacking.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <el-tabs v-model="tab" @tab-change="onTabChange">
      <el-tab-pane :label="t('pages.mrpPacking.tabWorkspace')" name="workspace">
        <div v-if="canCreate" class="admin-inner-card">
          <MrpPackingCreateDialog ref="workspaceRef" embedded />
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.mrpPacking.tabHistory')" name="history">
        <div class="admin-inner-card">
          <div class="mrp-pack-list-head mb-3">
            <h3 class="admin-inner-card__title mb-0">{{ t('pages.mrpPacking.historyTitle') }}</h3>
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
            empty-text="—"
          >
            <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
            <el-table-column prop="kode_packing" :label="t('pages.mrpPacking.kodePacking')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="kode_wip" label="WIP" min-width="120" show-overflow-tooltip />
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
            <el-table-column :label="t('common.date')" width="120">
              <template #default="{ row }">{{ formatDate(row.date_created) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="100" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="$router.push(`/admin/mrp/packing/${row.id}`)">
                  {{ t('common.detail') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
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
import MrpPackingCreateDialog from './MrpPackingCreateDialog.vue'
import { can } from '../../../security/permissions'
import { mrpListPacking } from '../../../api/client'

const { t } = useI18n()
const workspaceRef = ref(null)
const loading = ref(false)
const tab = ref('workspace')
const historyRows = ref([])
const historySearch = ref('')
const canCreate = computed(() => can('mrpShopfloor', 'create'))

const filteredHistoryRows = computed(() => {
  const q = historySearch.value.trim().toLowerCase()
  if (!q) return historyRows.value
  return historyRows.value.filter((r) =>
    [r.kode_packing, r.kode_wip, r.no_po, r.customer, r.status]
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
    historyRows.value = await mrpListPacking({ status: 'finished', all: true })
  } catch (e) {
    historyRows.value = []
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
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
.mrp-pack-list-head {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
  justify-content: space-between;
}
</style>
