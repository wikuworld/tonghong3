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
          <el-option :label="t('pages.mrpCheckpoint.qcOption')" :value="QC_TREATMENT" />
        </el-select>
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

    <div class="admin-inner-card">
      <div class="mrp-cp-list-head mb-3">
        <div>
          <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpCheckpoint.listTitle') }}</h3>
          <p class="text-xs text-slate-500 mb-0">
            {{ scanInfo ? t('pages.mrpCheckpoint.listHint') : t('pages.mrpCheckpoint.listEmpty') }}
          </p>
        </div>
      </div>

      <el-table
        :data="rows"
        v-loading="loading"
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

const QC_TREATMENT = 'QC'
const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const scanning = ref(false)
const rows = ref([])
const treatments = ref([])
const scanInfo = ref(null)
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const form = reactive({
  kode_wip: '',
  treatment: '',
  thickness_actual: '',
  softness_actual: '',
  result: 'OK',
  remark: '',
})

const isQc = computed(() => form.treatment === QC_TREATMENT)

const treatmentGroups = computed(() => {
  const byJenis = new Map()
  for (const tr of treatments.value || []) {
    const name = String(tr.nama_treatment || '').trim()
    if (!name || name.toUpperCase() === QC_TREATMENT) continue
    const jenis = String(tr.jenis || '').trim() || '—'
    if (!byJenis.has(jenis)) byJenis.set(jenis, [])
    byJenis.get(jenis).push(tr)
  }
  return [...byJenis.entries()].map(([jenis, items]) => ({ jenis, items }))
})

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function treatmentTagType(treatment) {
  if (String(treatment || '').toUpperCase() === QC_TREATMENT) return 'warning'
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
    const data = await mrpListTreatment()
    treatments.value = Array.isArray(data) ? data : data?.items || data?.treatments || []
  } catch (e) {
    treatments.value = []
    ElMessage.error(errMsg(e))
  }
}

async function reload() {
  const kode = scanInfo.value?.kode_wip
  if (!kode) {
    rows.value = []
    return
  }
  loading.value = true
  try {
    rows.value = await mrpListCheckpoint({ kode_wip: kode })
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
    const res = await mrpCreateCheckpoint(payload)
    const status = res?.checkpoint_status || res?.treatment || form.treatment
    if (scanInfo.value) scanInfo.value.checkpoint_status = status
    const qc = res?.erp_qc_detail_id
    ElMessage.success(
      qc
        ? t('pages.mrpCheckpoint.savedLinked', { qc })
        : t('pages.mrpCheckpoint.savedStatus', { status }),
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

onMounted(() => {
  loadTreatments()
})
</script>

<style scoped>
.max-w-xs {
  max-width: 20rem;
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
