<template>
  <AdminSection :title="t('pages.mrpStokKimia.title')" :subtitle="t('pages.mrpStokKimia.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div v-if="expiredCount" class="mb-3">
      <el-alert
        type="warning"
        :closable="false"
        show-icon
        :title="t('pages.mrpStokKimia.expiredAlert', { n: expiredCount })"
      />
    </div>

    <div v-if="canCreate" class="admin-inner-card mb-4">
      <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokKimia.inTitle') }}</h3>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpStokKimia.inHint') }}</p>
      <div class="flex flex-wrap gap-2 items-center">
        <el-select
          v-model="inForm.kimia_id"
          filterable
          clearable
          :placeholder="t('pages.mrpStokKimia.kimia')"
          class="max-w-sm"
        >
          <el-option
            v-for="k in kimiaList"
            :key="k.id"
            :label="`${k.kode_barang} — ${k.nama_barang}${k.satuan ? ` (${k.satuan})` : ''}`"
            :value="k.id"
          />
        </el-select>
        <el-input
          v-model="inForm.qty"
          type="number"
          :placeholder="t('pages.mrpStokKimia.qty')"
          class="w-28"
          @keyup.enter="doIn"
        />
        <el-input
          v-model="inForm.jumlah_kemasan"
          type="number"
          :placeholder="t('pages.mrpStokKimia.kemasan')"
          class="w-28"
        />
        <el-date-picker v-model="inForm.tanggal" type="date" value-format="YYYY-MM-DD" />
        <el-button type="primary" :loading="saving" @click="doIn">{{ t('pages.mrpStokKimia.inBtn') }}</el-button>
      </div>
    </div>

    <div v-if="canUpdate" class="admin-inner-card mb-4">
      <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokKimia.outTitle') }}</h3>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpStokKimia.outHint') }}</p>
      <div class="flex flex-wrap gap-2 items-center">
        <el-select
          v-model="outForm.stok_in_id"
          filterable
          clearable
          :placeholder="t('pages.mrpStokKimia.lot')"
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
          v-model="outForm.qty"
          type="number"
          :placeholder="t('pages.mrpStokKimia.qty')"
          class="w-28"
          @keyup.enter="doOut"
        />
        <el-select v-model="outForm.tujuan" class="w-36">
          <el-option :label="t('pages.mrpStokKimia.tujuanMixing')" value="mixing" />
          <el-option :label="t('pages.mrpStokKimia.tujuanProduksi')" value="produksi" />
          <el-option :label="t('pages.mrpStokKimia.tujuanReturn')" value="return" />
        </el-select>
        <el-input v-model="outForm.kode_wip" :placeholder="t('pages.mrpStokKimia.wip')" class="max-w-xs" />
        <el-button type="danger" :loading="saving" @click="doOut">{{ t('pages.mrpStokKimia.outBtn') }}</el-button>
      </div>
      <p v-if="outForm.stok != null" class="text-xs text-slate-500 mt-2 mb-0">
        {{ t('pages.mrpStokKimia.sisaHint', { qty: formatQty(outForm.stok), unit: outForm.satuan || 'kg' }) }}
      </p>
    </div>

    <div class="admin-inner-card mb-4">
      <div class="mrp-sk-list-head mb-3">
        <div>
          <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokKimia.stokIn') }}</h3>
          <p class="text-xs text-slate-500 mb-0">
            {{ t('pages.mrpStokKimia.statsIn', { lots: stats.lots, qty: formatQty(stats.qty_sisa) }) }}
          </p>
        </div>
        <el-input
          v-model="searchIn"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpStokKimia.searchPlaceholder')"
        />
      </div>
      <el-table
        :data="filteredIn"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        empty-text="—"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_internal" :label="t('pages.mrpStokKimia.bc')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="kode_barang" :label="t('pages.mrpStokKimia.kode')" width="120" show-overflow-tooltip />
        <el-table-column prop="nama_barang" :label="t('common.name')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpStokKimia.sisa')" width="100" align="right">
          <template #default="{ row }">
            {{ formatQty(row.qty_sisa) }}
            <span class="text-slate-400 text-xs">{{ dash(row.satuan) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokKimia.gudang')" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ dash(row.gudang) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokKimia.expired')" width="120">
          <template #default="{ row }">
            <span :class="{ 'text-amber-700 font-medium': isExpiredSoon(row.expired_date) }">
              {{ formatDate(row.expired_date) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="120">
          <template #default="{ row }">{{ formatDate(row.tanggal_in) }}</template>
        </el-table-column>
        <el-table-column v-if="canUpdate" :label="t('common.actions')" width="90" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="Number(row.qty_sisa) > 0"
              link
              type="danger"
              @click="outFromRow(row)"
            >
              OUT
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="admin-inner-card">
      <div class="mrp-sk-list-head mb-3">
        <h3 class="admin-inner-card__title mb-0">{{ t('pages.mrpStokKimia.stokOut') }}</h3>
        <el-input
          v-model="searchOut"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpStokKimia.searchOutPlaceholder')"
        />
      </div>
      <el-table :data="filteredOut" border stripe size="small" class="admin-table" empty-text="—">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="nama_barang" :label="t('common.name')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpStokKimia.qty')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokKimia.tujuan')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="tujuanType(row.tujuan)" size="small" effect="plain">
              {{ tujuanLabel(row.tujuan) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokKimia.wip')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.kode_wip) }}</template>
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
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import { mrpStokKimia, mrpStokKimiaAction } from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const stokIn = ref([])
const stokOut = ref([])
const kimiaList = ref([])
const searchIn = ref('')
const searchOut = ref('')
const stats = ref({ lots: 0, qty_sisa: 0, out_rows: 0 })
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const inForm = reactive({
  kimia_id: null,
  qty: null,
  jumlah_kemasan: null,
  tanggal: new Date().toISOString().slice(0, 10),
})
const outForm = reactive({
  stok_in_id: null,
  qty: null,
  stok: null,
  satuan: '',
  tujuan: 'mixing',
  kode_wip: '',
  tanggal: new Date().toISOString().slice(0, 10),
})

const activeLots = computed(() =>
  (stokIn.value || []).filter((s) => Number(s.qty_sisa) > 0),
)

const filteredIn = computed(() => {
  const q = searchIn.value.trim().toLowerCase()
  if (!q) return stokIn.value
  return stokIn.value.filter((r) =>
    [r.kode_internal, r.kode_barang, r.nama_barang, r.gudang]
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
    [r.nama_barang, r.kode_barang, r.tujuan, r.kode_wip]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

const expiredCount = computed(() =>
  (stokIn.value || []).filter((r) => Number(r.qty_sisa) > 0 && isExpiredSoon(r.expired_date)).length,
)

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

function isExpiredSoon(v) {
  if (!v) return false
  const d = new Date(String(v).slice(0, 10))
  if (Number.isNaN(d.getTime())) return false
  const soon = new Date()
  soon.setDate(soon.getDate() + 30)
  return d <= soon
}

function lotLabel(s) {
  return `${s.kode_internal} · ${s.nama_barang} · sisa ${formatQty(s.qty_sisa)} ${s.satuan || ''}`.trim()
}

function tujuanType(v) {
  if (v === 'mixing') return 'warning'
  if (v === 'produksi') return 'success'
  if (v === 'return') return 'info'
  return ''
}

function tujuanLabel(v) {
  if (v === 'mixing') return t('pages.mrpStokKimia.tujuanMixing')
  if (v === 'produksi') return t('pages.mrpStokKimia.tujuanProduksi')
  if (v === 'return') return t('pages.mrpStokKimia.tujuanReturn')
  return v || '—'
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
  outForm.satuan = s.satuan || 'kg'
  if (outForm.qty == null || outForm.qty === '') outForm.qty = outForm.stok
}

function outFromRow(row) {
  outForm.stok_in_id = row.id
  onLotPick(row.id)
  outForm.qty = Number(row.qty_sisa) || null
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpStokKimia()
    stokIn.value = data.stok_in || []
    stokOut.value = data.stok_out || []
    kimiaList.value = data.kimia_list || []
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
  if (!inForm.kimia_id) {
    ElMessage.warning(t('pages.mrpStokKimia.kimiaRequired'))
    return
  }
  const qty = Number(inForm.qty)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpStokKimia.qtyInvalid'))
    return
  }
  saving.value = true
  try {
    const res = await mrpStokKimiaAction({
      action: 'in',
      kimia_id: inForm.kimia_id,
      qty,
      jumlah_kemasan: inForm.jumlah_kemasan === '' || inForm.jumlah_kemasan == null
        ? null
        : Number(inForm.jumlah_kemasan),
      tanggal: inForm.tanggal,
    })
    ElMessage.success(
      t('pages.mrpStokKimia.inOk', { kode: res?.kode_internal || '' }),
    )
    inForm.kimia_id = null
    inForm.qty = null
    inForm.jumlah_kemasan = null
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

async function doOut() {
  if (!outForm.stok_in_id) {
    ElMessage.warning(t('pages.mrpStokKimia.lotRequired'))
    return
  }
  const qty = Number(outForm.qty)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpStokKimia.qtyInvalid'))
    return
  }
  if (outForm.stok != null && qty > Number(outForm.stok)) {
    ElMessage.warning(t('pages.mrpStokKimia.qtyExceed', { sisa: formatQty(outForm.stok) }))
    return
  }
  try {
    await ElMessageBox.confirm(
      t('pages.mrpStokKimia.outConfirm', { qty: formatQty(qty) }),
      t('pages.mrpStokKimia.outBtn'),
      { type: 'warning', confirmButtonText: t('pages.mrpStokKimia.outBtn'), cancelButtonText: t('common.cancel') },
    )
  } catch {
    return
  }
  saving.value = true
  try {
    await mrpStokKimiaAction({
      action: 'out',
      stok_in_id: outForm.stok_in_id,
      qty,
      tujuan: outForm.tujuan,
      kode_wip: (outForm.kode_wip || '').trim() || null,
      tanggal: outForm.tanggal,
    })
    ElMessage.success(t('common.saved'))
    outForm.stok_in_id = null
    outForm.qty = null
    outForm.stok = null
    outForm.kode_wip = ''
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
.w-36 {
  width: 9rem;
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
.mrp-sk-list-head {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-start;
  justify-content: space-between;
}
</style>
