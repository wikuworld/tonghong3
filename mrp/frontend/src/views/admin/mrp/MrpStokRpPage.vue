<template>
  <AdminSection :title="t('pages.mrpStokRp.title')" :subtitle="t('pages.mrpStokRp.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div class="mb-4">
      <el-radio-group v-model="gudangTab" size="default" @change="onGudangTab">
        <el-radio-button value="utama">{{ t('pages.mrpStokRp.gudangUtama') }}</el-radio-button>
        <el-radio-button value="lapangan">{{ t('pages.mrpStokRp.gudangLapangan') }}</el-radio-button>
      </el-radio-group>
    </div>

    <div v-if="canCreate && gudangTab === 'utama'" class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokRp.inTitle') }}</h3>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpStokRp.inHint') }}</p>
      <div class="flex flex-wrap gap-2 items-center">
        <el-select
          v-model="inForm.rp_id"
          filterable
          clearable
          :placeholder="t('pages.mrpStokRp.rp')"
          class="max-w-sm"
        >
          <el-option
            v-for="r in rpList"
            :key="r.id"
            :label="`${r.kode_rp} — ${r.nama_rp}${r.satuan ? ` (${r.satuan})` : ''}`"
            :value="r.id"
          />
        </el-select>
        <el-input
          v-model="inForm.meter_roll"
          type="number"
          :placeholder="t('pages.mrpStokRp.meter')"
          class="w-28"
          @keyup.enter="doIn"
        />
        <el-input
          v-model="inForm.lot_number"
          :placeholder="t('pages.mrpStokRp.lotNumber')"
          class="max-w-xs"
          clearable
        />
        <el-date-picker v-model="inForm.tanggal" type="date" value-format="YYYY-MM-DD" />
        <el-button type="primary" :loading="saving" @click="doIn">{{ t('pages.mrpStokRp.inBtn') }}</el-button>
      </div>
      </div>
    </div>

    <div v-if="canUpdate && gudangTab === 'utama'" class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokRp.outTitle') }}</h3>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpStokRp.outHint') }}</p>
      <div class="flex flex-wrap gap-2 items-center">
        <el-select
          v-model="outForm.stok_in_id"
          filterable
          clearable
          :placeholder="t('pages.mrpStokRp.lot')"
          class="max-w-md"
          @change="onLotPick"
        >
          <el-option
            v-for="s in activeLots"
            :key="s.id"
            :label="lotLabel(s)"
            :value="s.id"
          />
        </el-select>
        <el-input
          v-model="outForm.meter_roll"
          type="number"
          :placeholder="t('pages.mrpStokRp.meter')"
          class="w-28"
          @keyup.enter="doOut"
        />
        <el-select v-model="outForm.tujuan" class="w-40">
          <el-option :label="t('pages.mrpStokRp.tujuanLapangan')" value="lapangan" />
          <el-option :label="t('pages.mrpStokRp.tujuanProduksi')" value="produksi" />
        </el-select>
        <el-button type="danger" :loading="saving" @click="doOut">{{ t('pages.mrpStokRp.outBtn') }}</el-button>
      </div>
      <p v-if="outForm.stok != null" class="text-xs text-slate-500 mt-2 mb-0">
        {{ t('pages.mrpStokRp.sisaHint', { qty: formatQty(outForm.stok), unit: outForm.satuan || 'm' }) }}
      </p>
      </div>
    </div>

    <div v-if="canUpdate && gudangTab === 'lapangan'" class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokRp.outLapanganTitle') }}</h3>
        <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpStokRp.outLapanganHint') }}</p>
        <div class="flex flex-wrap gap-2 items-center">
          <el-select
            v-model="lapanganForm.stok_in_id"
            filterable
            clearable
            :placeholder="t('pages.mrpStokRp.lot')"
            class="max-w-md"
            @change="onLapanganLotPick"
          >
            <el-option
              v-for="s in activeLots"
              :key="s.id"
              :label="lotLabel(s)"
              :value="s.id"
            />
          </el-select>
          <el-input
            v-model="lapanganForm.meter_roll"
            type="number"
            :placeholder="t('pages.mrpStokRp.meter')"
            class="w-28"
            @keyup.enter="doOutLapangan"
          />
          <el-input
            v-model="lapanganForm.keterangan"
            :placeholder="t('common.notes')"
            class="max-w-xs"
          />
          <el-button type="danger" :loading="saving" @click="doOutLapangan">
            {{ t('pages.mrpStokRp.outLapanganBtn') }}
          </el-button>
        </div>
        <p v-if="lapanganForm.stok != null" class="text-xs text-slate-500 mt-2 mb-0">
          {{ t('pages.mrpStokRp.sisaHint', { qty: formatQty(lapanganForm.stok), unit: lapanganForm.satuan || 'm' }) }}
        </p>
      </div>
    </div>

    <div class="admin-inner-card mb-4">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpStokRp.summaryTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.mrpStokRp.summaryHint') }}</p>
        </div>
        <el-input
          v-model="searchSummary"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpStokRp.summarySearchPlaceholder')"
        />
      </div>
      <el-table
        ref="summaryTableRef"
        :data="filteredSummary"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        row-key="kode_barang"
        :empty-text="t('pages.mrpStokRp.summaryEmpty')"
        @expand-change="onSummaryExpand"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div v-loading="historyLoading[row.kode_barang]" class="mrp-rp-summary-expand">
              <h4 class="mrp-rp-summary-expand__title">{{ t('pages.mrpStokRp.historyIn') }}</h4>
              <el-table
                :data="historyCache[row.kode_barang]?.in || []"
                border
                size="small"
                class="admin-table mb-4"
                :empty-text="t('common.tableEmpty')"
              >
                <el-table-column prop="kode_internal" :label="t('pages.mrpStokRp.bc')" min-width="130" show-overflow-tooltip />
                <el-table-column :label="t('pages.mrpStokRp.lotNumber')" min-width="120" show-overflow-tooltip>
                  <template #default="{ row: lot }">{{ dash(lot.lot_number) }}</template>
                </el-table-column>
                <el-table-column :label="t('pages.mrpStokRp.meterIn')" width="100" align="right">
                  <template #default="{ row: lot }">{{ formatQty(lot.meter_roll) }}</template>
                </el-table-column>
                <el-table-column :label="t('pages.mrpStokRp.sisa')" width="100" align="right">
                  <template #default="{ row: lot }">{{ formatQty(lot.qty_sisa) }}</template>
                </el-table-column>
                <el-table-column :label="t('common.date')" width="110">
                  <template #default="{ row: lot }">{{ formatDate(lot.tanggal_in) }}</template>
                </el-table-column>
              </el-table>
              <h4 class="mrp-rp-summary-expand__title">{{ t('pages.mrpStokRp.historyOut') }}</h4>
              <el-table
                :data="historyCache[row.kode_barang]?.out || []"
                border
                size="small"
                class="admin-table"
                :empty-text="t('common.tableEmpty')"
              >
                <el-table-column prop="kode_internal" :label="t('pages.mrpStokRp.bc')" min-width="130" show-overflow-tooltip />
                <el-table-column :label="t('pages.mrpStokRp.meter')" width="100" align="right">
                  <template #default="{ row: out }">{{ formatQty(out.meter_roll) }}</template>
                </el-table-column>
                <el-table-column :label="t('pages.mrpStokRp.tujuan')" width="110" align="center">
                  <template #default="{ row: out }">
                    <el-tag :type="tujuanType(out.tujuan)" size="small" effect="plain">
                      {{ tujuanLabel(out.tujuan) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="t('pages.mrpStokRp.wip')" min-width="110" show-overflow-tooltip>
                  <template #default="{ row: out }">{{ dash(out.kode_wip) }}</template>
                </el-table-column>
                <el-table-column :label="t('common.date')" width="110">
                  <template #default="{ row: out }">{{ formatDate(out.tanggal) }}</template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column :label="t('pages.mrpStokRp.kode')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <el-button link type="primary" class="font-medium" @click="toggleSummaryRow(row)">
              {{ row.kode_barang }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="nama_barang" :label="t('pages.mrpStokRp.rp')" min-width="160" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpStokRp.summaryLots')" width="90" align="right">
          <template #default="{ row }">{{ row.lot_count ?? 0 }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokRp.sisa')" width="110" align="right">
          <template #default="{ row }">
            {{ formatQty(row.qty_sisa) }}
            <span class="text-slate-400 text-xs">m</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokRp.summaryMeterIn')" width="110" align="right">
          <template #default="{ row }">
            {{ formatQty(row.qty_in) }}
            <span class="text-slate-400 text-xs">m</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="admin-inner-card mb-4">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpStokRp.stokIn') }}</h3>
          <p class="admin-inner-card__sub">
            {{ t('pages.mrpStokRp.statsIn', { lots: stats.lots, qty: formatQty(stats.qty_sisa) }) }}
          </p>
        </div>
        <el-input
          v-model="searchIn"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpStokRp.searchPlaceholder')"
        />
      </div>
      <el-table
        :data="filteredIn"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('common.tableEmpty')"
        @sort-change="onSortChange"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_internal" sortable="custom" :label="t('pages.mrpStokRp.bc')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="lot_number" :label="t('pages.mrpStokRp.lotNumber')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.lot_number) }}</template>
        </el-table-column>
        <el-table-column prop="kode_rp" :label="t('pages.mrpStokRp.kode')" width="130" show-overflow-tooltip />
        <el-table-column prop="nama_jenis" :label="t('pages.mrpStokRp.rp')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpStokRp.sisa')" width="110" align="right">
          <template #default="{ row }">
            {{ formatQty(row.qty_sisa) }}
            <span class="text-slate-400 text-xs">{{ dash(row.satuan) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokRp.gudang')" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" :type="gudangTagType(row.gudang)">
              {{ gudangLabel(row.gudang) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokRp.meterIn')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.meter_roll) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="120">
          <template #default="{ row }">{{ formatDate(row.tanggal_in) }}</template>
        </el-table-column>
        <el-table-column v-if="canUpdate" :label="t('common.actions')" width="88" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions
              v-if="Number(row.qty_sisa) > 0"
              :more-items="[{ command: 'out', label: gudangTab === 'lapangan' ? t('pages.mrpStokRp.outLapanganBtn') : 'OUT', icon: Upload }]"
              @more="(cmd) => cmd === 'out' && outFromRow(row)"
            />
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

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <h3 class="admin-inner-card__title">{{ t('pages.mrpStokRp.stokOut') }}</h3>
        <el-input
          v-model="searchOut"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpStokRp.searchOutPlaceholder')"
        />
      </div>
      <el-table :data="filteredOut" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="nama_jenis" :label="t('pages.mrpStokRp.rp')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpStokRp.meter')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.meter_roll) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokRp.tujuan')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="tujuanType(row.tujuan)" size="small" effect="plain">
              {{ tujuanLabel(row.tujuan) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokRp.wip')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.kode_wip) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.notes')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.keterangan) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="120">
          <template #default="{ row }">{{ formatDate(row.tanggal) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Upload } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { can } from '../../../security/permissions'
import { mrpStokRp, mrpStokRpAction } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const gudangTab = ref('utama')
const stokIn = ref([])
const summaryRows = ref([])
const summaryTableRef = ref(null)
const historyCache = reactive({})
const historyLoading = reactive({})
const searchSummary = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('tanggal_in')
const sortDir = ref('desc')
const stokOut = ref([])
const rpList = ref([])
const searchIn = ref('')
const searchOut = ref('')
const stats = ref({ lots: 0, qty_sisa: 0, out_rows: 0 })
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const inForm = reactive({
  rp_id: null,
  meter_roll: null,
  lot_number: '',
  tanggal: new Date().toISOString().slice(0, 10),
})
const outForm = reactive({
  stok_in_id: null,
  meter_roll: null,
  stok: null,
  satuan: '',
  tujuan: 'produksi',
  tanggal: new Date().toISOString().slice(0, 10),
})
const lapanganForm = reactive({
  stok_in_id: null,
  meter_roll: null,
  stok: null,
  satuan: '',
  keterangan: '',
  tanggal: new Date().toISOString().slice(0, 10),
})

const activeLots = computed(() =>
  (stokIn.value || []).filter((s) => Number(s.qty_sisa) > 0),
)

const filteredSummary = computed(() => {
  const q = searchSummary.value.trim().toLowerCase()
  if (!q) return summaryRows.value
  return summaryRows.value.filter((r) =>
    [r.kode_barang, r.nama_barang]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

const filteredIn = computed(() => {
  const q = searchIn.value.trim().toLowerCase()
  if (!q) return stokIn.value
  return stokIn.value.filter((r) =>
    [r.kode_internal, r.kode_rp, r.nama_jenis, r.gudang, r.lot_number]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

const filteredOut = computed(() => {
  const q = searchOut.value.trim().toLowerCase()
  if (!q) return stokOut.value
  return stokOut.value.filter((r) =>
    [r.nama_jenis, r.kode_rp, r.kode_wip, r.keterangan]
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
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 3 })
}

function formatDate(v) {
  if (!v) return '—'
  return String(v).slice(0, 10)
}

function lotLabel(s) {
  const lotNo = (s.lot_number || '').trim()
  const lotPart = lotNo ? ` · Lot ${lotNo}` : ''
  return `${s.kode_internal}${lotPart} · ${s.nama_jenis} · sisa ${formatQty(s.qty_sisa)} ${s.satuan || 'm'}`.trim()
}

function gudangLabel(v) {
  const g = String(v || '').toLowerCase()
  if (g === 'lapangan' || g === 'mixing') return t('pages.mrpStokRp.gudangLapangan')
  return t('pages.mrpStokRp.gudangUtama')
}

function gudangTagType(v) {
  const g = String(v || '').toLowerCase()
  if (g === 'lapangan' || g === 'mixing') return 'warning'
  return 'success'
}

function tujuanType(v) {
  if (v === 'mixing' || v === 'lapangan') return 'warning'
  if (v === 'produksi') return 'success'
  return 'info'
}

function tujuanLabel(v) {
  if (v === 'mixing' || v === 'lapangan') return t('pages.mrpStokRp.tujuanLapangan')
  if (v === 'produksi') return t('pages.mrpStokRp.tujuanProduksi')
  if (v === 'keluar') return t('pages.mrpStokRp.tujuanKeluar')
  return dash(v)
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

function onLotPick(id) {
  const s = stokIn.value.find((r) => r.id === id)
  if (!s) {
    outForm.stok = null
    outForm.satuan = ''
    return
  }
  outForm.stok = Number(s.qty_sisa) || 0
  outForm.satuan = s.satuan || 'meter'
  if (outForm.meter_roll == null || outForm.meter_roll === '') outForm.meter_roll = outForm.stok
}

function onLapanganLotPick(id) {
  const s = stokIn.value.find((r) => r.id === id)
  if (!s) {
    lapanganForm.stok = null
    lapanganForm.satuan = ''
    return
  }
  lapanganForm.stok = Number(s.qty_sisa) || 0
  lapanganForm.satuan = s.satuan || 'meter'
  if (lapanganForm.meter_roll == null || lapanganForm.meter_roll === '') {
    lapanganForm.meter_roll = lapanganForm.stok
  }
}

function outFromRow(row) {
  if (gudangTab.value === 'lapangan') {
    lapanganForm.stok_in_id = row.id
    onLapanganLotPick(row.id)
    lapanganForm.meter_roll = Number(row.qty_sisa) || null
    return
  }
  outForm.stok_in_id = row.id
  onLotPick(row.id)
  outForm.meter_roll = Number(row.qty_sisa) || null
}

function clearSummaryHistory() {
  Object.keys(historyCache).forEach((k) => {
    delete historyCache[k]
    delete historyLoading[k]
  })
}

async function loadSummaryHistory(kode) {
  if (!kode || historyCache[kode]) return
  historyLoading[kode] = true
  try {
    const data = await mrpStokRp({
      gudang: gudangTab.value,
      kode,
      all: 1,
      page: 1,
      pageSize: 500,
    })
    historyCache[kode] = {
      in: data.stok_in || [],
      out: data.stok_out || [],
    }
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    historyLoading[kode] = false
  }
}

async function onSummaryExpand(row, expandedRows) {
  if (!expandedRows.some((r) => r.kode_barang === row.kode_barang)) return
  await loadSummaryHistory(row.kode_barang)
}

function toggleSummaryRow(row) {
  summaryTableRef.value?.toggleRowExpansion(row)
}

function onGudangTab() {
  outForm.stok_in_id = null
  outForm.meter_roll = null
  outForm.stok = null
  lapanganForm.stok_in_id = null
  lapanganForm.meter_roll = null
  lapanganForm.stok = null
  summaryRows.value = []
  clearSummaryHistory()
  reload()
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'tanggal_in'
  sortDir.value = mapped.sortDir || 'desc'
  page.value = 1
  reload()
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpStokRp(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
        extra: { gudang: gudangTab.value },
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    stokIn.value = pageData.items.length ? pageData.items : (data.stok_in || [])
    total.value = pageData.total || stokIn.value.length
    summaryRows.value = data.summary || []
    clearSummaryHistory()
    stokOut.value = data.stok_out || []
    rpList.value = data.rp_list || []
    stats.value = data.stats || {
      lots: stokIn.value.length,
      qty_sisa: stokIn.value.reduce((a, r) => a + (Number(r.qty_sisa) || 0), 0),
      out_rows: stokOut.value.length,
    }
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    loading.value = false
  }
}

async function doIn() {
  if (!inForm.rp_id) {
    ElMessage.warning(t('pages.mrpStokRp.rpRequired'))
    return
  }
  const meter = Number(inForm.meter_roll)
  if (!Number.isFinite(meter) || meter <= 0) {
    ElMessage.warning(t('pages.mrpStokRp.meterInvalid'))
    return
  }
  saving.value = true
  try {
    const res = await mrpStokRpAction({
      action: 'in',
      rp_id: inForm.rp_id,
      meter_roll: meter,
      gudang: 'utama',
      lot_number: (inForm.lot_number || '').trim() || null,
      tanggal: inForm.tanggal,
    })
    ElMessage.success(t('pages.mrpStokRp.inOk', { kode: res?.kode_internal || '' }))
    inForm.rp_id = null
    inForm.meter_roll = null
    inForm.lot_number = ''
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

async function doOut() {
  if (!outForm.stok_in_id) {
    ElMessage.warning(t('pages.mrpStokRp.lotRequired'))
    return
  }
  const meter = Number(outForm.meter_roll)
  if (!Number.isFinite(meter) || meter <= 0) {
    ElMessage.warning(t('pages.mrpStokRp.meterInvalid'))
    return
  }
  if (outForm.stok != null && meter > Number(outForm.stok)) {
    ElMessage.warning(t('pages.mrpStokRp.meterExceed', { sisa: formatQty(outForm.stok) }))
    return
  }
  try {
    await ElMessageBox.confirm(
      t('pages.mrpStokRp.outConfirm', { qty: formatQty(meter) }),
      t('pages.mrpStokRp.outBtn'),
      { type: 'warning', confirmButtonText: t('pages.mrpStokRp.outBtn'), cancelButtonText: t('common.cancel') },
    )
  } catch {
    return
  }
  saving.value = true
  try {
    const res = await mrpStokRpAction({
      action: 'out',
      stok_in_id: outForm.stok_in_id,
      meter_roll: meter,
      tujuan: outForm.tujuan,
      tanggal: outForm.tanggal,
    })
    if (res?.lapangan_lot?.kode_internal) {
      const cleared = (res.cleared_lapangan_lots || [])
        .map((x) => `${x.kode_internal || x.id} (${formatQty(x.meter_roll)} m)`)
        .join(', ')
      ElMessage.success(
        cleared
          ? t('pages.mrpStokRp.outOkLapangan', {
              sisa: formatQty(res.qty_sisa),
              kode: res.lapangan_lot.kode_internal,
              qty: formatQty(res.lapangan_lot.qty_sisa),
              cleared,
            })
          : t('pages.mrpStokRp.outOkLapanganNoClear', {
              sisa: formatQty(res.qty_sisa),
              kode: res.lapangan_lot.kode_internal,
              qty: formatQty(res.lapangan_lot.qty_sisa),
            }),
      )
    } else {
      ElMessage.success(t('common.saved'))
    }
    outForm.stok_in_id = null
    outForm.meter_roll = null
    outForm.stok = null
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
    await reload()
  } finally {
    saving.value = false
  }
}

async function doOutLapangan() {
  if (!lapanganForm.stok_in_id) {
    ElMessage.warning(t('pages.mrpStokRp.lotRequired'))
    return
  }
  const meter = Number(lapanganForm.meter_roll)
  if (!Number.isFinite(meter) || meter <= 0) {
    ElMessage.warning(t('pages.mrpStokRp.meterInvalid'))
    return
  }
  if (lapanganForm.stok != null && meter > Number(lapanganForm.stok)) {
    ElMessage.warning(t('pages.mrpStokRp.meterExceed', { sisa: formatQty(lapanganForm.stok) }))
    return
  }
  try {
    await ElMessageBox.confirm(
      t('pages.mrpStokRp.outLapanganConfirm', { qty: formatQty(meter) }),
      t('pages.mrpStokRp.outLapanganBtn'),
      {
        type: 'warning',
        confirmButtonText: t('pages.mrpStokRp.outLapanganBtn'),
        cancelButtonText: t('common.cancel'),
      },
    )
  } catch {
    return
  }
  saving.value = true
  try {
    await mrpStokRpAction({
      action: 'out_lapangan',
      stok_in_id: lapanganForm.stok_in_id,
      meter_roll: meter,
      keterangan: (lapanganForm.keterangan || '').trim() || null,
      tanggal: lapanganForm.tanggal,
    })
    ElMessage.success(t('common.saved'))
    lapanganForm.stok_in_id = null
    lapanganForm.meter_roll = null
    lapanganForm.stok = null
    lapanganForm.keterangan = ''
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
    await reload()
  } finally {
    saving.value = false
  }
}

onMounted(reload)
</script>

<style scoped>
.w-28 {
  width: 7rem;
}
.w-40 {
  width: 10rem;
}
.w-56 {
  width: 14rem;
}
.max-w-sm {
  max-width: 24rem;
}
.max-w-md {
  max-width: 28rem;
}
.max-w-xs {
  max-width: 16rem;
}
.mrp-rp-summary-expand {
  padding: 0.35rem 0.5rem 0.75rem;
}
.mrp-rp-summary-expand__title {
  margin: 0 0 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--el-text-color-secondary);
}
</style>
