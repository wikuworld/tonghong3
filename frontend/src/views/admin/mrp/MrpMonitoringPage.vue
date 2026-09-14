<template>
  <AdminSection :title="t('pages.mrpMonitoring.title')" :subtitle="t('pages.mrpMonitoring.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="mrp-mon-list-head mb-3">
        <div>
          <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpMonitoring.listTitle') }}</h3>
          <p class="text-xs text-slate-500 mb-0">{{ t('pages.mrpMonitoring.listSubtitle') }}</p>
        </div>
        <el-input
          v-model="search"
          clearable
          size="small"
          class="w-64"
          :placeholder="t('pages.mrpMonitoring.searchPlaceholder')"
        />
      </div>

      <el-table
        :data="filteredRows"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('pages.mrpMonitoring.tableEmpty')"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="no_so" :label="t('pages.mrpMonitoring.so')" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.no_so) }}</template>
        </el-table-column>
        <el-table-column prop="lot_no" :label="t('pages.mrpMonitoring.lotNo')" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.lot_no) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpMonitoring.statusLast')" min-width="180">
          <template #default="{ row }">
            <el-tag size="small" :type="statusType(row.status_terakhir)" effect="plain">
              {{ statusLabel(row.status_terakhir) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="110" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">{{ t('common.detail') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-drawer
      v-model="detailOpen"
      size="72%"
      :title="detailTitle"
      append-to-body
    >
      <template v-if="detail">
        <div class="mrp-mon-meta mb-4">
          <div class="mrp-mon-meta__item">
            <span class="mrp-mon-meta__label">{{ t('pages.mrpMonitoring.so') }}</span>
            <span>{{ dash(detail.no_so) }}</span>
          </div>
          <div class="mrp-mon-meta__item">
            <span class="mrp-mon-meta__label">{{ t('pages.mrpMonitoring.lotNo') }}</span>
            <span>{{ dash(detail.lot_no) }}</span>
          </div>
          <div class="mrp-mon-meta__item">
            <span class="mrp-mon-meta__label">{{ t('pages.mrpMonitoring.statusLast') }}</span>
            <el-tag size="small" :type="statusType(detail.status_terakhir)" effect="plain">
              {{ statusLabel(detail.status_terakhir) }}
            </el-tag>
          </div>
          <div class="mrp-mon-meta__item">
            <span class="mrp-mon-meta__label">{{ t('common.customer') }}</span>
            <span>{{ dash(detail.nama_customer) }}</span>
          </div>
          <div class="mrp-mon-meta__item">
            <span class="mrp-mon-meta__label">{{ t('pages.mrpMonitoring.qtyPersiapan') }}</span>
            <span>{{ formatQty(detail.total_qty_persiapan) }}</span>
          </div>
          <div class="mrp-mon-meta__item">
            <span class="mrp-mon-meta__label">{{ t('pages.mrpMonitoring.qtyFg') }}</span>
            <span v-if="detail.fg_measured">{{ formatQty(detail.total_qty_fg) }}</span>
            <span v-else class="text-slate-400">{{ t('pages.mrpMonitoring.qtyFgPending') }}</span>
          </div>
        </div>

        <h4 class="mb-2 font-semibold">{{ t('pages.mrpMonitoring.kyUsed') }}</h4>
        <el-table :data="detail.ky || []" border size="small" class="mb-4" :empty-text="t('pages.mrpMonitoring.noKy')">
          <el-table-column prop="kode_palet" :label="t('pages.mrpMonitoring.kodePalet')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="kode_yl" :label="t('pages.mrpMonitoring.kodeYl')" min-width="120" show-overflow-tooltip>
            <template #default="{ row }">{{ dash(row.kode_yl) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpMonitoring.qtyTarget')" width="110" align="right">
            <template #default="{ row }">{{ formatQty(row.target_qty) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpMonitoring.qtyActual')" width="110" align="right">
            <template #default="{ row }">{{ formatQty(row.actual_qty) }}</template>
          </el-table-column>
          <el-table-column prop="status" :label="t('common.status')" width="100" />
        </el-table>

        <h4 class="mb-2 font-semibold">{{ t('pages.mrpMonitoring.chemicalUsed') }}</h4>
        <el-table
          :data="detail.chemicals || []"
          border
          size="small"
          class="mb-4"
          :empty-text="t('pages.mrpMonitoring.noChemical')"
        >
          <el-table-column prop="kode_lot_warna" :label="t('pages.mrpMonitoring.lotWarna')" min-width="120" show-overflow-tooltip />
          <el-table-column :label="t('pages.mrpMonitoring.namaKimia')" min-width="160" show-overflow-tooltip>
            <template #default="{ row }">{{ dash(row.nama_kimia || row.nama_warna) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpMonitoring.qtyUsed')" width="120" align="right">
            <template #default="{ row }">{{ formatQty(row.qty) }}</template>
          </el-table-column>
          <el-table-column prop="satuan" :label="t('pages.mrpMonitoring.satuan')" width="90" />
        </el-table>
      </template>
    </el-drawer>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { mrpGetMonitoring, mrpListMonitoring } from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const rows = ref([])
const search = ref('')
const detailOpen = ref(false)
const detail = ref(null)

const filteredRows = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) =>
    [
      r.no_so,
      r.lot_no,
      r.status_terakhir,
      statusLabel(r.status_terakhir),
      r.nama_customer,
      r.kode_rencana_item,
      r.kode_lot_wip,
      r.no_po,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

const detailTitle = computed(() => {
  if (!detail.value) return t('common.detail')
  const so = detail.value.no_so || '—'
  const lot = detail.value.lot_no || '—'
  return `${so} · ${lot}`
})

function dash(v) {
  const s = v == null ? '' : String(v).trim()
  return s || '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function statusLabel(code) {
  const key = `pages.mrpMonitoring.status.${code}`
  const label = t(key)
  return label === key ? code || '—' : label
}

function statusType(code) {
  if (code === 'gudang_fg_out') return 'info'
  if (['checkpoint_ok', 'packing_finished', 'gudang_fg', 'proses_completed'].includes(code)) return 'success'
  if (['rencana'].includes(code)) return 'info'
  if (['checkpoint', 'packing', 'proses_draft'].includes(code)) return 'warning'
  return 'warning'
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

async function reload() {
  loading.value = true
  try {
    rows.value = await mrpListMonitoring()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    loading.value = false
  }
}

async function openDetail(row) {
  try {
    detail.value = await mrpGetMonitoring(row.rencana_item_id)
    detailOpen.value = true
  } catch (e) {
    ElMessage.error(errMsg(e))
  }
}

onMounted(reload)
</script>

<style scoped>
.w-64 {
  width: 16rem;
}
.mrp-mon-list-head {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-start;
  justify-content: space-between;
}
.mrp-mon-meta {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
}
.mrp-mon-meta__item {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.55rem 0.7rem;
  font-size: 0.875rem;
}
.mrp-mon-meta__label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.15rem;
}
@media (max-width: 700px) {
  .mrp-mon-meta {
    grid-template-columns: 1fr;
  }
}
</style>
