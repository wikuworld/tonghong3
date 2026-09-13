<template>
  <AdminSection :title="t('pages.mrpGudangFg.title')" :subtitle="t('pages.mrpGudangFg.subtitle')">
    <template #actions>
      <el-input
        v-model="search"
        clearable
        class="mrp-toolbar-search"
        :placeholder="t('pages.mrpGudangFg.searchPlaceholder')"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div v-if="failedBridgeCount" class="mb-3">
      <el-alert
        type="warning"
        :closable="false"
        show-icon
        :title="t('pages.mrpGudangFg.bridgeFailedAlert', { n: failedBridgeCount })"
      />
    </div>

    <div v-if="canUpdate" class="admin-inner-card mb-4">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpGudangFg.outTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.mrpGudangFg.outHint') }}</p>
        </div>
      </div>
      <div class="mkt-section-body">
        <el-button type="primary" @click="goOutstanding">{{ t('pages.mrpGudangFg.goOutstanding') }}</el-button>
      </div>
    </div>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpGudangFg.listSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.mrpGudangFg.listSubtitle') }}</p>
        </div>
      </div>
      <div class="admin-stats-grid admin-stats-grid--3">
        <div class="admin-stat-card admin-stat-card--success">
          <span class="admin-stat-card__value">{{ stats.inStock }}</span>
          <span class="admin-stat-card__label">{{ t('pages.mrpGudangFg.statInStock') }}</span>
        </div>
        <div class="admin-stat-card admin-stat-card--info">
          <span class="admin-stat-card__value">{{ stats.out }}</span>
          <span class="admin-stat-card__label">{{ t('pages.mrpGudangFg.statOut') }}</span>
        </div>
        <div class="admin-stat-card admin-stat-card--warn">
          <span class="admin-stat-card__value">{{ stats.failed }}</span>
          <span class="admin-stat-card__label">{{ t('pages.mrpGudangFg.statFailed') }}</span>
        </div>
      </div>
      <div class="mkt-section-body">
        <div class="filter-panel mb-4">
          <p class="filter-panel__title">{{ t('common.filter') }}</p>
          <el-form class="filter-form" label-position="top">
            <el-row :gutter="12">
              <el-col :xs="24" :sm="12" :md="10" :lg="8">
                <el-form-item :label="t('common.status')">
                  <el-radio-group v-model="statusFilter" size="small" @change="reload">
                    <el-radio-button value="">{{ t('pages.mrpGudangFg.filterAll') }}</el-radio-button>
                    <el-radio-button value="in_stock">{{ t('pages.mrpGudangFg.statusInStock') }}</el-radio-button>
                    <el-radio-button value="out">{{ t('pages.mrpGudangFg.statusOut') }}</el-radio-button>
                  </el-radio-group>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
        <p class="admin-scroll-hint">{{ t('pages.mrpGudangFg.scrollHint') }}</p>
        <div class="admin-table-scroll">
      <el-table
        :data="filteredRows"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('pages.mrpGudangFg.tableEmpty')"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column
          prop="kode_packing"
          :label="t('pages.mrpPacking.kodePacking')"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column prop="kode_wip" :label="t('pages.mrpGudangFg.wip')" min-width="120" show-overflow-tooltip />
        <el-table-column :label="t('common.customer')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.customer) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpPacking.pieces')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.total_lembar) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpPacking.quantity')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.total_ukuran) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="plain">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpGudangFg.erpDelivery')" min-width="170">
          <template #default="{ row }">
            <el-button
              v-if="row.erp_delivery_id"
              link
              type="primary"
              @click="goDelivery(row.erp_delivery_id)"
            >
              {{ row.erp_delivery_number || `#${row.erp_delivery_id}` }}
            </el-button>
            <el-tooltip
              v-else-if="row.bridge_status === 'failed'"
              :content="row.bridge_error || t('pages.mrpGudangFg.bridgeFailed')"
              placement="top"
            >
              <el-tag type="danger" size="small" effect="plain">
                {{ t('pages.mrpGudangFg.bridgeFailed') }}
              </el-tag>
            </el-tooltip>
            <span v-else class="text-slate-400">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpGudangFg.dateIn')" width="120">
          <template #default="{ row }">{{ formatDate(row.date_in) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpGudangFg.dateOut')" width="120">
          <template #default="{ row }">{{ formatDate(row.date_out) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">{{ t('common.detail') }}</el-button>
            <el-button
              v-if="canUpdate && row.status === 'in_stock'"
              link
              type="primary"
              @click="goOutstanding"
            >
              {{ t('pages.mrpGudangFg.goOutstanding') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
        </div>
      </div>
    </div>

    <el-drawer v-model="detailOpen" size="48%" :title="detail?.fg?.kode_packing || t('common.detail')">
      <template v-if="detail?.fg">
        <el-alert
          v-if="detail.fg.bridge_status === 'failed'"
          class="mb-3"
          type="error"
          :closable="false"
          show-icon
          :title="t('pages.mrpGudangFg.bridgeFailed')"
          :description="detail.fg.bridge_error || ''"
        />

        <div class="admin-stats-grid admin-stats-grid--3 mb-4">
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpGudangFg.wip') }}</span>
            <span>{{ dash(detail.fg.kode_wip) }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('common.customer') }}</span>
            <span>{{ dash(detail.fg.customer) }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('common.status') }}</span>
            <el-tag :type="statusType(detail.fg.status)" size="small" effect="plain">
              {{ statusLabel(detail.fg.status) }}
            </el-tag>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpPacking.pieces') }} / {{ t('pages.mrpPacking.quantity') }}</span>
            <span>{{ formatQty(detail.fg.total_lembar) }} / {{ formatQty(detail.fg.total_ukuran) }}</span>
          </div>
          <div class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpGudangFg.dateIn') }}</span>
            <span>{{ formatDateTime(detail.fg.date_in) }}</span>
          </div>
          <div v-if="detail.fg.date_out" class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpGudangFg.dateOut') }}</span>
            <span>{{ formatDateTime(detail.fg.date_out) }} — {{ dash(detail.fg.keterangan_out) }}</span>
          </div>
          <div v-if="detail.fg.erp_delivery_id" class="admin-stat-card">
            <span class="admin-stat-card__label">{{ t('pages.mrpGudangFg.erpDelivery') }}</span>
            <el-button link type="primary" @click="goDelivery(detail.fg.erp_delivery_id)">
              {{ detail.fg.erp_delivery_number || `#${detail.fg.erp_delivery_id}` }}
            </el-button>
          </div>
        </div>

        <div v-if="canUpdate && detail.fg.status === 'in_stock'" class="mb-4">
          <el-button type="primary" size="small" @click="goOutstanding">
            {{ t('pages.mrpGudangFg.goOutstanding') }}
          </el-button>
        </div>

        <h4 class="mb-2 font-semibold">{{ t('pages.mrpPacking.rolls') }}</h4>
        <el-table :data="detail.rolls || []" border stripe size="small" class="admin-table mb-4" :empty-text="t('pages.mrpGudangFg.tableEmpty')">
          <el-table-column prop="roll_no" :label="t('pages.mrpPacking.artNo')" width="70" />
          <el-table-column :label="t('pages.mrpPacking.pieces')" align="right">
            <template #default="{ row }">{{ formatQty(row.lembar) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpPacking.quantity')" align="right">
            <template #default="{ row }">{{ formatQty(row.ukuran) }}</template>
          </el-table-column>
        </el-table>

        <h4 class="mb-2 font-semibold">{{ t('pages.mrpPacking.poSection') }}</h4>
        <el-table :data="detail.packing_pos || []" border stripe size="small" class="admin-table mb-4" :empty-text="t('pages.mrpGudangFg.tableEmpty')">
          <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="90" show-overflow-tooltip />
          <el-table-column :label="t('pages.mrpPacking.poItem')" min-width="140" show-overflow-tooltip>
            <template #default="{ row }">{{ dash(row.item_name) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpPacking.qtyPlan')" width="100" align="right">
            <template #default="{ row }">{{ formatQty(row.qty_sq) }}</template>
          </el-table-column>
          <el-table-column prop="source_detail_id" :label="t('common.poDetail')" width="100" />
        </el-table>

        <template v-if="(detail.bridge_lines || []).length">
          <h4 class="mb-2 font-semibold">{{ t('pages.mrpGudangFg.bridgeLines') }}</h4>
          <el-table :data="detail.bridge_lines || []" border stripe size="small" class="admin-table" :empty-text="t('pages.mrpGudangFg.tableEmpty')">
            <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="90" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpPacking.poItem')" min-width="140" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.item_name) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpPacking.quantity')" width="100" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_sq) }}</template>
            </el-table-column>
            <el-table-column prop="source_detail_id" :label="t('common.poDetail')" width="100" />
          </el-table>
        </template>
      </template>
    </el-drawer>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import { mrpGetGudangFg, mrpListGudangFg } from '../../../api/client'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const rows = ref([])
const search = ref('')
const statusFilter = ref('')
const detailOpen = ref(false)
const detail = ref(null)
const canUpdate = computed(() => can('mrpShopfloor', 'update'))

const filteredRows = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) =>
    [
      r.kode_packing,
      r.kode_wip,
      r.customer,
      r.status,
      r.erp_delivery_number,
      r.bridge_status,
      r.bridge_error,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

const stats = computed(() => {
  const list = rows.value || []
  return {
    inStock: list.filter((r) => r.status === 'in_stock').length,
    out: list.filter((r) => r.status === 'out').length,
    failed: list.filter((r) => r.bridge_status === 'failed').length,
  }
})

const failedBridgeCount = computed(() => stats.value.failed)

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function formatDate(v) {
  if (!v) return '—'
  return String(v).slice(0, 10)
}

function formatDateTime(v) {
  if (!v) return '—'
  return String(v).replace('T', ' ').slice(0, 19)
}

function statusType(status) {
  if (status === 'in_stock') return 'success'
  if (status === 'out') return 'info'
  return 'warning'
}

function statusLabel(status) {
  if (status === 'in_stock') return t('pages.mrpGudangFg.statusInStock')
  if (status === 'out') return t('pages.mrpGudangFg.statusOut')
  return status || '—'
}

function errMsg(e) {
  const raw = e?.message || String(e)
  try {
    const j = JSON.parse(raw)
    const d = j?.detail
    if (typeof d === 'string') return d
    if (d && typeof d === 'object' && typeof d.detail === 'string') return d.detail
    if (typeof j?.message === 'string') return j.message
    return raw
  } catch {
    return raw
  }
}

function goDelivery(id) {
  router.push({ path: '/admin/delivery', query: { delivery_id: id } })
}

function goOutstanding() {
  router.push({ path: '/admin/marketing-flow/outstanding' })
}

async function reload() {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    rows.value = await mrpListGudangFg(params)
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    loading.value = false
  }
}

async function openDetail(row) {
  try {
    detail.value = await mrpGetGudangFg(row.id)
    detailOpen.value = true
  } catch (e) {
    ElMessage.error(errMsg(e))
  }
}

onMounted(reload)
</script>

<style scoped>
.max-w-xs { max-width: 20rem; }
</style>
