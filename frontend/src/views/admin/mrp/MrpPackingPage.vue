<template>
  <AdminSection :title="t('pages.mrpPacking.title')" :subtitle="t('pages.mrpPacking.subtitle')">
    <template #actions>
      <el-input
        v-model="search"
        clearable
        class="mrp-toolbar-search"
        :placeholder="t('pages.mrpPacking.searchPlaceholder')"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div v-if="canCreate" class="admin-inner-card mb-4">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpPacking.scanSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.mrpPacking.scanSectionSubtitle') }}</p>
        </div>
      </div>
      <div class="mkt-section-body">
      <div class="flex gap-2 mb-3 flex-wrap">
        <el-input
          v-model="wipCode"
          :placeholder="t('pages.mrpPacking.scanPlaceholder')"
          class="max-w-xs"
          @keyup.enter="scanWip"
        />
        <el-button type="primary" :loading="scanning" @click="scanWip">
          {{ t('pages.mrpPacking.scanBtn') }}
        </el-button>
      </div>

      <div v-if="prep" class="admin-stats-grid admin-stats-grid--3 mb-3">
        <div class="admin-stat-card">
          <span class="admin-stat-card__label">{{ t('pages.mrpPacking.wip') }}</span>
          <span class="admin-stat-card__value">{{ dash(scannedWip) }}</span>
        </div>
        <div class="admin-stat-card">
          <span class="admin-stat-card__label">{{ t('pages.mrpPacking.prepCode') }}</span>
          <span class="admin-stat-card__value">{{ dash(prep.kode_proses) }}</span>
        </div>
        <div class="admin-stat-card">
          <span class="admin-stat-card__label">{{ t('common.status') }}</span>
          <el-tag size="small" type="success" effect="plain">{{ dash(prep.status) }}</el-tag>
        </div>
        <div class="admin-stat-card">
          <span class="admin-stat-card__label">{{ t('common.color') }}</span>
          <span class="admin-stat-card__value">{{ dash(prep.warna) }}</span>
        </div>
        <div class="admin-stat-card">
          <span class="admin-stat-card__label">{{ t('pages.mrpPacking.thickness') }}</span>
          <span class="admin-stat-card__value">{{ dash(prep.tebal) }}</span>
        </div>
        <div class="admin-stat-card">
          <span class="admin-stat-card__label">{{ t('pages.mrpPacking.totalSize') }}</span>
          <span class="admin-stat-card__value">{{ formatQty(prep.total_size) }}</span>
        </div>
      </div>

      <el-table v-if="poList.length" :data="poList" border stripe size="small" class="admin-table" :empty-text="t('pages.mrpPacking.tableEmpty')">
        <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="100" show-overflow-tooltip />
        <el-table-column prop="item_name" :label="t('pages.mrpPacking.poItem')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="customer" :label="t('common.customer')" min-width="120" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpPacking.qtyPlan')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty_sq) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="110" fixed="right">
          <template #default="{ row }">
            <el-button link type="success" :loading="starting" @click="startPacking(row)">
              {{ t('pages.mrpPacking.start') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      </div>
    </div>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpPacking.listSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.mrpPacking.listSubtitle') }}</p>
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
                    <el-radio-button value="">{{ t('pages.mrpPacking.filterAll') }}</el-radio-button>
                    <el-radio-button value="in_progress">{{ t('pages.mrpPacking.statusInProgress') }}</el-radio-button>
                    <el-radio-button value="finished">{{ t('pages.mrpPacking.statusFinished') }}</el-radio-button>
                  </el-radio-group>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
        <p class="admin-scroll-hint">{{ t('pages.mrpPacking.scrollHint') }}</p>
        <div class="admin-table-scroll">
      <el-table
        :data="filteredRows"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('pages.mrpPacking.tableEmpty')"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_packing" :label="t('pages.mrpPacking.kodePacking')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="kode_wip" :label="t('pages.mrpPacking.wip')" min-width="120" show-overflow-tooltip />
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
            <el-tag :type="statusType(row.status)" size="small" effect="plain">
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
      </div>
    </div>
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
import { mrpListPacking, mrpPackingScanWip, mrpStartPacking } from '../../../api/client'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const scanning = ref(false)
const starting = ref(false)
const rows = ref([])
const search = ref('')
const statusFilter = ref('')
const wipCode = ref('')
const scannedWip = ref('')
const prep = ref(null)
const poList = ref([])
const canCreate = computed(() => can('mrpShopfloor', 'create'))

const filteredRows = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) =>
    [r.kode_packing, r.kode_wip, r.no_po, r.customer, r.status]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

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

function statusType(status) {
  if (status === 'finished') return 'success'
  if (status === 'in_progress') return 'warning'
  return 'info'
}

function statusLabel(status) {
  if (status === 'finished') return t('pages.mrpPacking.statusFinished')
  if (status === 'in_progress') return t('pages.mrpPacking.statusInProgress')
  return status || '—'
}

async function reload() {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    rows.value = await mrpListPacking(params)
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function scanWip() {
  if (!wipCode.value.trim()) {
    ElMessage.warning(t('pages.mrpPacking.scanWip'))
    return
  }
  scanning.value = true
  try {
    const data = await mrpPackingScanWip(wipCode.value.trim())
    scannedWip.value = data.kode_wip
    prep.value = data.prep || null
    poList.value = data.po_list || []
    if (!poList.value.length) ElMessage.warning(t('pages.mrpPacking.noPo'))
    else ElMessage.success(t('pages.mrpPacking.scanOk'))
  } catch (e) {
    poList.value = []
    prep.value = null
    ElMessage.error(e.message || String(e))
  } finally {
    scanning.value = false
  }
}

async function startPacking(row) {
  starting.value = true
  try {
    const res = await mrpStartPacking({
      kode_wip: scannedWip.value,
      no_po: row.no_po,
      no_so: row.no_so || '',
      customer: row.customer || '',
      qty_sq: row.qty_sq || 0,
      po_id: row.po_id || null,
    })
    ElMessage.success(res.message || t('common.saved'))
    router.push(`/admin/mrp/packing/${res.id}`)
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    starting.value = false
  }
}

onMounted(reload)
</script>

<style scoped>
.max-w-xs { max-width: 20rem; }
</style>
