<template>
  <AdminSection :title="t('pages.mrpCheckpoint.title')" :subtitle="t('pages.mrpCheckpoint.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div v-if="canCreate" class="admin-inner-card mb-4">
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

      <div class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
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

    <div class="admin-inner-card">
      <div class="mrp-cp-list-head mb-3">
        <div>
          <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpCheckpoint.listTitle') }}</h3>
          <p class="text-xs text-slate-500 mb-0">
            {{ t('pages.mrpCheckpoint.statsLine', { ok: stats.ok, ng: stats.ng, linked: stats.linked }) }}
          </p>
        </div>
        <div class="flex gap-2 flex-wrap items-center">
          <el-radio-group v-model="resultFilter" size="small" @change="reload">
            <el-radio-button value="">{{ t('pages.mrpCheckpoint.filterAll') }}</el-radio-button>
            <el-radio-button value="OK">{{ t('pages.mrpCheckpoint.resultOk') }}</el-radio-button>
            <el-radio-button value="NG">{{ t('pages.mrpCheckpoint.resultNg') }}</el-radio-button>
          </el-radio-group>
          <el-input
            v-model="search"
            clearable
            size="small"
            class="w-56"
            :placeholder="t('pages.mrpCheckpoint.searchPlaceholder')"
          />
        </div>
      </div>

      <el-table
        :data="filteredRows"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        empty-text="—"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_wip" :label="t('pages.mrpCheckpoint.wip')" min-width="130" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpPacking.kodePacking')" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.kode_packing) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpCheckpoint.thickness')" width="110" align="right">
          <template #default="{ row }">{{ formatQty(row.thickness_actual) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpCheckpoint.softness')" min-width="100" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.softness_actual) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpCheckpoint.result')" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="resultType(row.result)" size="small" effect="plain">
              {{ resultLabel(row.result) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpCheckpoint.erpQc')" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.erp_qc_detail_id" type="success" size="small" effect="plain">
              #{{ row.erp_qc_detail_id }}
            </el-tag>
            <span v-else class="text-gray-400">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.notes')" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.remark) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="150">
          <template #default="{ row }">{{ formatDateTime(row.measured_at) }}</template>
        </el-table-column>
      </el-table>
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
import { mrpCheckpointScanWip, mrpCreateCheckpoint, mrpListCheckpoint } from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const scanning = ref(false)
const rows = ref([])
const search = ref('')
const resultFilter = ref('')
const scanInfo = ref(null)
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const form = reactive({
  kode_wip: '',
  thickness_actual: '',
  softness_actual: '',
  result: 'OK',
  remark: '',
})

const filteredRows = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) =>
    [r.kode_wip, r.kode_packing, r.result, r.remark, r.softness_actual]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

const stats = computed(() => {
  const list = rows.value || []
  return {
    ok: list.filter((r) => String(r.result || '').toUpperCase() === 'OK').length,
    ng: list.filter((r) => String(r.result || '').toUpperCase() === 'NG').length,
    linked: list.filter((r) => r.erp_qc_detail_id).length,
  }
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

function formatDateTime(v) {
  if (!v) return '—'
  return String(v).replace('T', ' ').slice(0, 19)
}

function resultType(result) {
  const r = String(result || '').toUpperCase()
  if (r === 'OK') return 'success'
  if (r === 'NG') return 'danger'
  return 'info'
}

function resultLabel(result) {
  const r = String(result || '').toUpperCase()
  if (r === 'OK') return t('pages.mrpCheckpoint.resultOk')
  if (r === 'NG') return t('pages.mrpCheckpoint.resultNg')
  return result || '—'
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
    const params = {}
    if (resultFilter.value) params.result = resultFilter.value
    rows.value = await mrpListCheckpoint(params)
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
    if (!form.thickness_actual && data.tebal_target) {
      const n = parseFloat(String(data.tebal_target).replace(/[^\d.]/g, ''))
      if (Number.isFinite(n) && n > 0) form.thickness_actual = String(n)
    }
    ElMessage.success(t('pages.mrpCheckpoint.scanOk'))
  } catch (e) {
    scanInfo.value = null
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
  if (!scanInfo.value || scanInfo.value.kode_wip !== kode) {
    await scanWip()
    if (!scanInfo.value) return
  }
  saving.value = true
  try {
    const res = await mrpCreateCheckpoint({
      kode_wip: kode,
      kode_packing: scanInfo.value?.kode_packing || null,
      thickness_actual: form.thickness_actual === '' ? null : Number(form.thickness_actual),
      softness_actual: form.softness_actual.trim() || null,
      result: form.result,
      is_ok: form.result === 'OK',
      remark: form.remark.trim() || null,
      erp_production_detail_id: scanInfo.value?.erp_production_detail_id || null,
    })
    const qc = res?.erp_qc_detail_id
    ElMessage.success(
      qc ? t('pages.mrpCheckpoint.savedLinked', { qc }) : t('common.saved'),
    )
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

onMounted(reload)
</script>

<style scoped>
.max-w-xs {
  max-width: 20rem;
}
.w-56 {
  width: 14rem;
}
.mrp-cp-list-head {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-start;
  justify-content: space-between;
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
</style>
