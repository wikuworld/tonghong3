<template>
  <AdminSection :title="t('pages.mrpStokRp.title')" :subtitle="t('pages.mrpStokRp.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div v-if="canCreate" class="admin-inner-card mb-4">
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
        <el-date-picker v-model="inForm.tanggal" type="date" value-format="YYYY-MM-DD" />
        <el-button type="primary" :loading="saving" @click="doIn">{{ t('pages.mrpStokRp.inBtn') }}</el-button>
      </div>
    </div>

    <div v-if="canUpdate" class="admin-inner-card mb-4">
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
        <el-input v-model="outForm.kode_wip" :placeholder="t('pages.mrpStokRp.wip')" class="max-w-xs" />
        <el-button type="danger" :loading="saving" @click="doOut">{{ t('pages.mrpStokRp.outBtn') }}</el-button>
      </div>
      <p v-if="outForm.stok != null" class="text-xs text-slate-500 mt-2 mb-0">
        {{ t('pages.mrpStokRp.sisaHint', { qty: formatQty(outForm.stok), unit: outForm.satuan || 'm' }) }}
      </p>
    </div>

    <div class="admin-inner-card mb-4">
      <div class="mrp-sr-list-head mb-3">
        <div>
          <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokRp.stokIn') }}</h3>
          <p class="text-xs text-slate-500 mb-0">
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
        empty-text="—"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_internal" :label="t('pages.mrpStokRp.bc')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="kode_rp" :label="t('pages.mrpStokRp.kode')" width="130" show-overflow-tooltip />
        <el-table-column prop="nama_jenis" :label="t('pages.mrpStokRp.rp')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpStokRp.sisa')" width="110" align="right">
          <template #default="{ row }">
            {{ formatQty(row.qty_sisa) }}
            <span class="text-slate-400 text-xs">{{ dash(row.satuan) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokRp.meterIn')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.meter_roll) }}</template>
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
      <div class="mrp-sr-list-head mb-3">
        <h3 class="admin-inner-card__title mb-0">{{ t('pages.mrpStokRp.stokOut') }}</h3>
        <el-input
          v-model="searchOut"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpStokRp.searchOutPlaceholder')"
        />
      </div>
      <el-table :data="filteredOut" border stripe size="small" class="admin-table" empty-text="—">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="nama_jenis" :label="t('pages.mrpStokRp.rp')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpStokRp.meter')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.meter_roll) }}</template>
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
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import { mrpStokRp, mrpStokRpAction } from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const stokIn = ref([])
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
  tanggal: new Date().toISOString().slice(0, 10),
})
const outForm = reactive({
  stok_in_id: null,
  meter_roll: null,
  stok: null,
  satuan: '',
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
    [r.kode_internal, r.kode_rp, r.nama_jenis].filter(Boolean).join(' ').toLowerCase().includes(q),
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
  return `${s.kode_internal} · ${s.nama_jenis} · sisa ${formatQty(s.qty_sisa)} ${s.satuan || 'm'}`.trim()
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

function outFromRow(row) {
  outForm.stok_in_id = row.id
  onLotPick(row.id)
  outForm.meter_roll = Number(row.qty_sisa) || null
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpStokRp()
    stokIn.value = data.stok_in || []
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
      tanggal: inForm.tanggal,
    })
    ElMessage.success(t('pages.mrpStokRp.inOk', { kode: res?.kode_internal || '' }))
    inForm.rp_id = null
    inForm.meter_roll = null
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
    await mrpStokRpAction({
      action: 'out',
      stok_in_id: outForm.stok_in_id,
      meter_roll: meter,
      kode_wip: (outForm.kode_wip || '').trim() || null,
      tanggal: outForm.tanggal,
    })
    ElMessage.success(t('common.saved'))
    outForm.stok_in_id = null
    outForm.meter_roll = null
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
.mrp-sr-list-head {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-start;
  justify-content: space-between;
}
</style>
