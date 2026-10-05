<template>
  <AdminSection :title="t('pages.mrpCheckpoint.title')" :subtitle="t('pages.mrpCheckpoint.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div v-if="canCreate" class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpCheckpoint.createTitle') }}</h3>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpCheckpoint.createHint') }}</p>

      <div class="flex gap-2 flex-wrap mb-3">
        <el-input
          v-model="form.kode_wip"
          :placeholder="t('pages.mrpCheckpoint.wipPlaceholder')"
          class="max-w-xs"
          clearable
          @keyup.enter="scanWip"
        />
        <el-button type="primary" :loading="scanning" @click="scanWip">
          {{ t('pages.mrpCheckpoint.scanBtn') }}
        </el-button>
      </div>

      <div v-if="scanInfo" class="mrp-cp-prep mb-3">
        <div class="mrp-cp-prep__item">
          <span class="mrp-cp-prep__label">WIP</span>
          <span>{{ dash(scanInfo.kode_wip) }}</span>
        </div>
        <div class="mrp-cp-prep__item">
          <span class="mrp-cp-prep__label">{{ t('common.customer') }}</span>
          <span>{{ dash(scanInfo.customer) }}</span>
        </div>
        <div class="mrp-cp-prep__item">
          <span class="mrp-cp-prep__label">{{ t('pages.mrpCheckpoint.currentStatus') }}</span>
          <el-tag v-if="scanInfo.checkpoint_status" size="small" effect="plain">
            {{ scanInfo.checkpoint_status }}
          </el-tag>
          <span v-else>{{ dash(scanInfo.prep_status) }}</span>
        </div>
        <div class="mrp-cp-prep__item">
          <span class="mrp-cp-prep__label">{{ t('pages.mrpCheckpoint.treatmentPlan') }}</span>
          <span>{{ dash(scanInfo.treatment_list) }}</span>
        </div>
        <div class="mrp-cp-prep__item">
          <span class="mrp-cp-prep__label">{{ t('pages.mrpCheckpoint.tebalTarget') }}</span>
          <span>{{ dash(scanInfo.tebal_target) }}</span>
        </div>
        <div class="mrp-cp-prep__item">
          <span class="mrp-cp-prep__label">{{ t('common.color') }}</span>
          <span>{{ dash(scanInfo.warna) }}</span>
        </div>
        <div class="mrp-cp-prep__item">
          <span class="mrp-cp-prep__label">{{ t('pages.mrpPacking.kodePacking') }}</span>
          <span>{{ dash(scanInfo.kode_packing) }}</span>
        </div>
        <div class="mrp-cp-prep__item">
          <span class="mrp-cp-prep__label">{{ t('pages.mrpCheckpoint.erpProd') }}</span>
          <span>{{ scanInfo.erp_production_detail_id || '—' }}</span>
        </div>
      </div>

      <p v-if="scanInfo && !allowedTreatmentNames.size" class="text-sm text-amber-700 mb-2">
        {{ t('pages.mrpCheckpoint.noPrepTreatments') }}
      </p>

      <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
        <el-select
          v-model="form.treatment"
          filterable
          :placeholder="t('pages.mrpCheckpoint.treatmentPlaceholder')"
          class="w-full"
          :disabled="!scanInfo"
        >
          <el-option-group v-for="group in treatmentGroups" :key="group.jenis" :label="group.jenis">
            <el-option
              v-for="tr in group.items"
              :key="tr.nama_treatment"
              :label="tr.nama_treatment"
              :value="tr.nama_treatment"
            />
          </el-option-group>
          <el-option :label="t('pages.mrpCheckpoint.usageColorOption')" :value="USAGE_COLOR_TREATMENT" />
          <el-option :label="t('pages.mrpCheckpoint.qcOption')" :value="QC_TREATMENT" />
        </el-select>
        <template v-if="isUsageColor">
          <el-select
            v-model="form.kode_lot_warna"
            filterable
            clearable
            :placeholder="t('pages.mrpCheckpoint.lotWarnaPlaceholder')"
            class="w-full sm:col-span-2"
          >
            <el-option
              v-for="lot in labLots"
              :key="lot.kode_lot_warna"
              :label="lotWarnaLabel(lot)"
              :value="lot.kode_lot_warna"
            />
          </el-select>
          <p v-if="!labLots.length" class="text-sm text-amber-700 sm:col-span-2 mb-0">
            {{ t('pages.mrpCheckpoint.noLabLots') }}
          </p>
          <div v-else-if="selectedLabLot" class="mrp-cp-lab-lot sm:col-span-2">
            <div class="mrp-cp-lab-lot__item">
              <span class="mrp-cp-lab-lot__label">{{ t('pages.mrpLab.kodeLot') }}</span>
              <span>{{ dash(selectedLabLot.kode_lot_warna) }}</span>
            </div>
            <div class="mrp-cp-lab-lot__item">
              <span class="mrp-cp-lab-lot__label">{{ t('pages.mrpLab.namaLot') }}</span>
              <span>{{ dash(selectedLabLot.nama_lot_warna) }}</span>
            </div>
            <div class="mrp-cp-lab-lot__item">
              <span class="mrp-cp-lab-lot__label">{{ t('pages.mrpLab.totalQty') }}</span>
              <span>{{ formatQty(selectedLabLot.qty_sisa ?? selectedLabLot.qty_pembuatan) }}</span>
            </div>
            <div class="mrp-cp-lab-lot__item">
              <span class="mrp-cp-lab-lot__label">{{ t('common.color') }}</span>
              <span>{{ dash(selectedLabLot.color) }}</span>
            </div>
          </div>
        </template>
        <template v-if="isQc">
          <el-input
            v-model="form.thickness_actual"
            :placeholder="t('pages.mrpCheckpoint.thickness')"
            @keyup.enter="save"
          />
          <el-input
            v-model="form.softness_actual"
            :placeholder="t('pages.mrpCheckpoint.softness')"
            @keyup.enter="save"
          />
          <el-select v-model="form.result" :placeholder="t('pages.mrpCheckpoint.result')" class="w-full">
            <el-option :label="t('pages.mrpCheckpoint.resultOk')" value="OK" />
            <el-option :label="t('pages.mrpCheckpoint.resultNg')" value="NG" />
          </el-select>
        </template>
        <el-input
          v-model="form.remark"
          :placeholder="t('common.notes')"
          class="sm:col-span-2"
          @keyup.enter="save"
        />
        <el-button type="primary" :loading="saving" :disabled="!scanInfo" @click="save">
          {{ t('common.save') }}
        </el-button>
      </div>
      </div>
    </div>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpCheckpoint.listTitle') }}</h3>
          <p class="admin-inner-card__sub">
            {{ scanInfo ? t('pages.mrpCheckpoint.listHint') : t('pages.mrpCheckpoint.listEmpty') }}
          </p>
        </div>
      </div>

      <el-table
        :data="rows"
        v-loading="loading"
        @sort-change="onSortChange"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('pages.mrpCheckpoint.listEmpty')"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_wip" :label="t('pages.mrpCheckpoint.wip')" min-width="140" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpProses.kodeRpi')" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.kode_rpi) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpCheckpoint.namaRencana')" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.nama_rencana) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.material')" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.material_name) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.emboss')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.emboss) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.color')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.warna) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpCheckpoint.treatment')" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <el-tag :type="treatmentTagType(row.treatment)" size="small" effect="plain">
              {{ dash(row.treatment || row.result) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <div class="mt-3 flex justify-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          background
          small
          @current-change="reload"
          @size-change="() => { page = 1; reload() }"
        />
      </div>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import {
  mrpCheckpointScanWip,
  mrpCreateCheckpoint,
  mrpListCheckpoint,
  mrpListTreatment,
} from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const QC_TREATMENT = 'QC'
const USAGE_COLOR_TREATMENT = 'Penggunaan Lot Warna'
const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const scanning = ref(false)
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('measured_at')
const sortDir = ref('desc')
const treatments = ref([])
const scanInfo = ref(null)
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const form = reactive({
  kode_wip: '',
  treatment: '',
  kode_lot_warna: '',
  thickness_actual: '',
  softness_actual: '',
  result: 'OK',
  remark: '',
})

const isQc = computed(() => form.treatment === QC_TREATMENT)
const isUsageColor = computed(() => form.treatment === USAGE_COLOR_TREATMENT)

const labLots = computed(() => {
  const rows = scanInfo.value?.lab_lots
  return Array.isArray(rows) ? rows : []
})

const selectedLabLot = computed(() =>
  labLots.value.find((lot) => lot.kode_lot_warna === form.kode_lot_warna) || null,
)

function parseTreatmentList(raw) {
  if (Array.isArray(raw)) {
    return raw.map((s) => String(s).trim()).filter(Boolean)
  }
  return String(raw || '')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean)
}

const allowedTreatmentNames = computed(() => {
  if (!scanInfo.value) return new Set()
  const raw = scanInfo.value.treatment_allowed ?? scanInfo.value.treatment_list
  return new Set(parseTreatmentList(raw))
})

const treatmentGroups = computed(() => {
  const allowed = allowedTreatmentNames.value
  if (!allowed.size) return []
  const byJenis = new Map()
  for (const tr of treatments.value || []) {
    const name = String(tr.nama_treatment || '').trim()
    if (!name || name.toUpperCase() === QC_TREATMENT) continue
    if (!allowed.has(name)) continue
    const jenis = String(tr.jenis || '').trim() || '—'
    if (!byJenis.has(jenis)) byJenis.set(jenis, [])
    byJenis.get(jenis).push(tr)
  }
  return [...byJenis.entries()].map(([jenis, items]) => ({ jenis, items }))
})

function syncTreatmentSelection() {
  if (!form.treatment || form.treatment === QC_TREATMENT || form.treatment === USAGE_COLOR_TREATMENT) {
    return
  }
  if (!allowedTreatmentNames.value.has(form.treatment)) {
    form.treatment = ''
  }
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function lotWarnaLabel(lot) {
  const kode = dash(lot.kode_lot_warna)
  const nama = dash(lot.nama_lot_warna)
  const wip = lot.kode_lot_wip ? ` · ${lot.kode_lot_wip}` : ''
  const qty = formatQty(lot.qty_sisa ?? lot.qty_pembuatan)
  return `${kode} · ${nama}${wip} · ${qty}`
}

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function treatmentTagType(treatment) {
  if (String(treatment || '').toUpperCase() === QC_TREATMENT) return 'warning'
  if (String(treatment || '') === USAGE_COLOR_TREATMENT) return 'success'
  return 'info'
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

async function loadTreatments() {
  try {
    const data = await mrpListTreatment({ page: 1, page_size: 200 })
    treatments.value = Array.isArray(data) ? data : data?.items || data?.treatments || []
  } catch (e) {
    treatments.value = []
    ElMessage.error(errMsg(e))
  }
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'measured_at'
  sortDir.value = mapped.sortDir || 'desc'
  page.value = 1
  reload()
}

async function reload() {
  const kode = scanInfo.value?.kode_wip
  if (!kode) {
    rows.value = []
    total.value = 0
    return
  }
  loading.value = true
  try {
    const data = await mrpListCheckpoint(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
        extra: { kode_wip: kode },
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

async function scanWip() {
  const kode = form.kode_wip.trim()
  if (!kode) {
    ElMessage.warning(t('pages.mrpCheckpoint.wipPlaceholder'))
    return
  }
  scanning.value = true
  try {
    const data = await mrpCheckpointScanWip(kode)
    scanInfo.value = data
    form.kode_wip = data.kode_wip || kode
    form.kode_lot_warna = ''
    syncTreatmentSelection()
    if (!form.thickness_actual && data.tebal_target) {
      const n = parseFloat(String(data.tebal_target).replace(/[^\d.]/g, ''))
      if (Number.isFinite(n) && n > 0) form.thickness_actual = String(n)
    }
    ElMessage.success(t('pages.mrpCheckpoint.scanOk'))
    await reload()
  } catch (e) {
    scanInfo.value = null
    rows.value = []
    ElMessage.error(errMsg(e))
  } finally {
    scanning.value = false
  }
}

async function save() {
  const kode = form.kode_wip.trim()
  if (!kode) {
    ElMessage.warning(t('pages.mrpCheckpoint.wipPlaceholder'))
    return
  }
  if (!form.treatment) {
    ElMessage.warning(t('pages.mrpCheckpoint.treatmentRequired'))
    return
  }
  if (isUsageColor.value && !form.kode_lot_warna.trim()) {
    ElMessage.warning(t('pages.mrpCheckpoint.lotWarnaRequired'))
    return
  }
  if (isQc.value) {
    if (!form.result) {
      ElMessage.warning(t('pages.mrpCheckpoint.resultRequired'))
      return
    }
    if (form.thickness_actual !== '' && form.thickness_actual != null) {
      const n = Number(form.thickness_actual)
      if (!Number.isFinite(n) || n <= 0) {
        ElMessage.warning(t('pages.mrpCheckpoint.thicknessInvalid'))
        return
      }
    }
  }
  if (!scanInfo.value || scanInfo.value.kode_wip !== kode) {
    await scanWip()
    if (!scanInfo.value) return
  }
  saving.value = true
  try {
    const payload = {
      kode_wip: kode,
      treatment: form.treatment,
      kode_packing: scanInfo.value?.kode_packing || null,
      remark: form.remark.trim() || null,
      erp_production_detail_id: scanInfo.value?.erp_production_detail_id || null,
    }
    if (isQc.value) {
      payload.thickness_actual = form.thickness_actual === '' ? null : Number(form.thickness_actual)
      payload.softness_actual = form.softness_actual.trim() || null
      payload.result = form.result
      payload.is_ok = form.result === 'OK'
    }
    if (isUsageColor.value) {
      payload.kode_lot_warna = form.kode_lot_warna.trim()
    }
    const res = await mrpCreateCheckpoint(payload)
    const status = res?.checkpoint_status || res?.treatment || form.treatment
    if (scanInfo.value) scanInfo.value.checkpoint_status = status
    const qc = res?.erp_qc_detail_id
    if (isUsageColor.value && res?.usage_color) {
      const lotKode = res.usage_color.kode_lot_warna || form.kode_lot_warna
      ElMessage.success(t('pages.mrpCheckpoint.savedUsageColor', { lot: lotKode }))
      form.kode_lot_warna = ''
      if (scanInfo.value?.lab_lots) {
        scanInfo.value.lab_lots = scanInfo.value.lab_lots.filter(
          (lot) => lot.kode_lot_warna !== lotKode,
        )
      }
    } else {
      ElMessage.success(
        qc
          ? t('pages.mrpCheckpoint.savedLinked', { qc })
          : t('pages.mrpCheckpoint.savedStatus', { status }),
      )
    }
    form.thickness_actual = ''
    form.softness_actual = ''
    form.remark = ''
    form.result = 'OK'
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadTreatments()
})
</script>

<style scoped>
.max-w-xs {
  max-width: 20rem;
}
.mrp-cp-prep {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
}
.mrp-cp-prep__item {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.55rem 0.7rem;
  font-size: 0.875rem;
}
.mrp-cp-prep__label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.15rem;
}
@media (max-width: 800px) {
  .mrp-cp-prep {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
.mrp-cp-lab-lot {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.55rem;
}
.mrp-cp-lab-lot__item {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.55rem 0.7rem;
  font-size: 0.875rem;
}
.mrp-cp-lab-lot__label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.15rem;
}
</style>
