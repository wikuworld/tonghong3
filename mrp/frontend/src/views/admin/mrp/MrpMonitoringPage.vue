<template>
  <AdminSection :title="t('pages.mrpMonitoring.title')" :subtitle="t('pages.mrpMonitoring.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpMonitoring.listTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.mrpMonitoring.listSubtitle') }}</p>
        </div>
        <el-input
          v-model="search"
          clearable
          size="small"
          class="w-64"
          :placeholder="t('pages.mrpMonitoring.searchPlaceholder')"
          @keyup.enter="() => { page = 1; reload() }"
          @clear="() => { page = 1; reload() }"
        />
      </div>

      <el-table
        :data="rows"
        v-loading="loading"
        @sort-change="onSortChange"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('pages.mrpMonitoring.tableEmpty')"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="no_so" sortable="custom" :label="t('pages.mrpMonitoring.so')" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.no_so) }}</template>
        </el-table-column>
        <el-table-column prop="nama_rencana" :label="t('pages.mrpMonitoring.namaRencana')" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.nama_rencana) }}</template>
        </el-table-column>
        <el-table-column prop="lot_no" sortable="custom" :label="t('pages.mrpMonitoring.lotNo')" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.lot_no) }}</template>
        </el-table-column>
        <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.material_name) }}</template>
        </el-table-column>
        <el-table-column prop="emboss" :label="t('common.emboss')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.emboss) }}</template>
        </el-table-column>
        <el-table-column prop="thickness" :label="t('pages.mrpRencana.thickness')" min-width="100" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.thickness) }}</template>
        </el-table-column>
        <el-table-column prop="kode_lot_wip" sortable="custom" :label="t('pages.mrpMonitoring.wip')" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">{{ wipLabel(row) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpMonitoring.statusLast')" min-width="180">
          <template #default="{ row }">
            <el-tag size="small" :type="statusType(row.status_terakhir)" effect="plain">
              {{ statusLabel(row.status_terakhir) }}
            </el-tag>
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
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          background
          small
          @current-change="reload"
          @size-change="() => { page = 1; reload() }"
        />
      </div>
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

        <h4 class="mb-2 font-semibold">{{ t('pages.mrpMonitoring.statusLog') }}</h4>
        <el-table
          :data="detail.status_log || []"
          border
          size="small"
          class="mb-4"
          :empty-text="t('pages.mrpMonitoring.statusLogEmpty')"
        >
          <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
          <el-table-column :label="t('common.date')" width="130">
            <template #default="{ row }">{{ formatLogDate(row.tanggal) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpMonitoring.jam')" width="110">
            <template #default="{ row }">{{ formatLogTime(row.jam) }}</template>
          </el-table-column>
          <el-table-column :label="t('common.process')" min-width="220">
            <template #default="{ row }">
              <div class="mrp-mon-log-proses">
                <el-tag size="small" :type="statusType(row.proses)" effect="plain">
                  {{ statusLabel(row.proses) }}
                </el-tag>
                <span v-if="row.keterangan" class="mrp-mon-log-ket">{{ row.keterangan }}</span>
              </div>
            </template>
          </el-table-column>
        </el-table>

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
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { mrpGetMonitoring, mrpListMonitoring } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('no_so')
const sortDir = ref('asc')
const search = ref('')
const detailOpen = ref(false)
const detail = ref(null)

const filteredRows = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) =>
    [
      r.no_so,
      r.nama_rencana,
      r.lot_no,
      r.material_name,
      r.emboss,
      r.thickness,
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

function wipLabel(row) {
  const lotWip = (row?.kode_lot_wip || '').trim()
  if (lotWip) return lotWip
  const list = (row?.kode_wip_list || []).filter(Boolean)
  if (list.length) return list.join(' / ')
  return '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function formatLogDate(v) {
  if (!v) return '—'
  const s = String(v).trim()
  if (/^\d{4}-\d{2}-\d{2}/.test(s)) {
    const [y, m, d] = s.slice(0, 10).split('-')
    return `${d}/${m}/${y}`
  }
  return s
}

function formatLogTime(v) {
  if (!v) return '—'
  const s = String(v).trim()
  if (/^\d{2}:\d{2}/.test(s)) return s.slice(0, 8)
  return s
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

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'no_so'
  sortDir.value = mapped.sortDir || 'asc'
  page.value = 1
  reload()
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpListMonitoring(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
        extra: { q: search.value.trim() || undefined },
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items
    total.value = pageData.total
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
.mrp-mon-log-proses {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.4rem;
}
.mrp-mon-log-ket {
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}
@media (max-width: 700px) {
  .mrp-mon-meta {
    grid-template-columns: 1fr;
  }
}
</style>
