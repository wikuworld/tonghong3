<template>
  <AdminSection :title="title" :subtitle="t('pages.mrpProses.detailSubtitle')">
    <template #actions>
      <el-button @click="$router.push('/admin/mrp/proses')">{{ t('common.close') }}</el-button>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canUpdate && persiapan?.status === 'draft'" type="primary" @click="act('start')">
        {{ t('pages.mrpProses.start') }}
      </el-button>
      <el-button
        v-if="canUpdate && persiapan?.status === 'started'"
        type="success"
        @click="act('save')"
      >
        {{ t('pages.mrpProses.finishSave') }}
      </el-button>
      <el-button v-if="persiapan && isDone" @click="printLabel">{{ t('pages.mrpProses.label') }}</el-button>
      <el-button v-if="canUpdate && isDone" @click="act('reprint')">{{ t('pages.mrpProses.reprint') }}</el-button>
    </template>

    <div v-loading="loading" class="space-y-4">
      <div v-if="persiapan" class="admin-inner-card">
        <div class="mrp-proses-flow mb-3">
          <span
            v-for="step in flowSteps"
            :key="step.key"
            class="mrp-proses-flow__step"
            :class="{
              'is-done': step.done,
              'is-current': step.current,
            }"
          >
            {{ step.label }}
          </span>
        </div>

        <div class="mrp-proses-stats">
          <div class="mrp-proses-stat">
            <span class="mrp-proses-stat__label">{{ t('pages.mrpProses.kodeProses') }}</span>
            <span class="mrp-proses-stat__value mrp-proses-stat__value--text">{{ dash(persiapan.kode_proses) }}</span>
          </div>
          <div class="mrp-proses-stat">
            <span class="mrp-proses-stat__label">{{ t('pages.mrpProses.kodeRpi') }}</span>
            <span class="mrp-proses-stat__value mrp-proses-stat__value--text">{{ dash(persiapan.kode_rencana) }}</span>
          </div>
          <div class="mrp-proses-stat">
            <span class="mrp-proses-stat__label">WIP</span>
            <span class="mrp-proses-stat__value mrp-proses-stat__value--text">{{ dash(persiapan.kode_wip) }}</span>
          </div>
          <div class="mrp-proses-stat">
            <span class="mrp-proses-stat__label">{{ t('common.status') }}</span>
            <span class="mrp-proses-stat__value">
              <el-tag :type="statusType(persiapan.status)" size="small" effect="plain">
                {{ statusLabel(persiapan.status) }}
              </el-tag>
            </span>
          </div>
          <div class="mrp-proses-stat">
            <span class="mrp-proses-stat__label">{{ t('common.color') }}</span>
            <span class="mrp-proses-stat__value mrp-proses-stat__value--text">{{ dash(persiapan.warna) }}</span>
          </div>
          <div class="mrp-proses-stat">
            <span class="mrp-proses-stat__label">{{ t('pages.mrpProses.thickness') }}</span>
            <span class="mrp-proses-stat__value mrp-proses-stat__value--text">{{ dash(persiapan.tebal) }}</span>
          </div>
          <div class="mrp-proses-stat mrp-proses-stat--wide">
            <span class="mrp-proses-stat__label">{{ t('pages.mrpProses.treatmentList') }}</span>
            <span class="mrp-proses-stat__value mrp-proses-stat__value--text">
              {{ dash(persiapan.treatment_jenis) }} — {{ dash(persiapan.treatment_list) }}
            </span>
          </div>
          <div class="mrp-proses-stat">
            <span class="mrp-proses-stat__label">{{ t('pages.mrpProses.totalSize') }}</span>
            <span class="mrp-proses-stat__value">{{ formatQty(persiapan.total_size) }}</span>
          </div>
        </div>

        <el-alert
          v-if="persiapan.status === 'draft'"
          class="mt-3"
          type="warning"
          :closable="false"
          show-icon
          :title="t('pages.mrpProses.startHint')"
        />
        <el-alert
          v-else-if="isDone"
          class="mt-3"
          type="success"
          :closable="false"
          show-icon
          :title="t('pages.mrpProses.doneHint')"
        />
      </div>

      <div v-if="canUpdate && persiapan?.status === 'started'" class="admin-inner-card">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpProses.kySession') }}</h3>
        <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpProses.kyHint') }}</p>

        <div class="mrp-proses-form-row mb-3">
          <el-form-item :label="t('pages.mrpPalet.kodePalet')" class="mb-0">
            <el-input v-model="kyForm.kode_palet" class="w-40" />
          </el-form-item>
          <el-form-item label="YL" class="mb-0">
            <el-input v-model="kyForm.kode_yl" class="w-36" />
          </el-form-item>
          <el-form-item :label="t('pages.mrpProses.targetQty')" class="mb-0">
            <el-input v-model="kyForm.target_qty" type="number" class="w-28" />
          </el-form-item>
          <el-button type="primary" :disabled="!!activeKy" @click="scanKy">
            {{ t('pages.mrpProses.activateKy') }}
          </el-button>
        </div>

        <div v-if="activeKy" class="mrp-proses-form-row mrp-proses-form-row--accent">
          <el-form-item :label="t('pages.mrpProses.sizeUkur')" class="mb-0">
            <el-input v-model="ukurVal" type="number" class="w-32" @keyup.enter="addUkur" />
          </el-form-item>
          <el-button @click="addUkur">{{ t('pages.mrpProses.addUkur') }}</el-button>
          <el-button type="warning" @click="selesaiKy">{{ t('pages.mrpProses.finishKy') }}</el-button>
        </div>
      </div>

      <div class="admin-inner-card">
        <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpProses.kySessions') }}</h3>
        <el-table :data="kySessions" border size="small" empty-text="—">
          <el-table-column prop="kode_palet" :label="t('pages.mrpPalet.kodePalet')" min-width="110" />
          <el-table-column prop="kode_yl" label="YL" min-width="100" />
          <el-table-column :label="t('pages.mrpProses.targetQty')" width="90" align="right">
            <template #default="{ row }">{{ formatQty(row.target_qty) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpProses.actualQty')" width="90" align="right">
            <template #default="{ row }">{{ formatQty(row.actual_qty) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpProses.qtyConsumed')" width="100" align="right">
            <template #default="{ row }">{{ formatQty(row.qty_consumed) }}</template>
          </el-table-column>
          <el-table-column :label="t('common.status')" width="110" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'warning' : 'success'" size="small" effect="plain">
                {{ row.status === 'active' ? t('pages.mrpProses.kyActive') : t('pages.mrpProses.kyDone') }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="admin-inner-card">
        <h3 class="admin-inner-card__title mb-2">{{ t('pages.mrpProses.ukur') }}</h3>
        <el-table :data="ukurs" border size="small" empty-text="—">
          <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
          <el-table-column prop="ky_id" label="KY ID" width="80" />
          <el-table-column :label="t('pages.mrpProses.sizeUkur')" width="110" align="right">
            <template #default="{ row }">{{ formatQty(row.size_val) }}</template>
          </el-table-column>
          <el-table-column prop="created_at" :label="t('common.date')" min-width="150" />
          <el-table-column
            v-if="canUpdate && persiapan?.status === 'started'"
            :label="t('common.actions')"
            width="90"
            fixed="right"
          >
            <template #default="{ row }">
              <el-button link type="danger" @click="deleteUkur(row.id)">{{ t('common.delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import { mrpGetProses, mrpProsesAction, mrpProsesLabel } from '../../../api/client'

const { t } = useI18n()
const route = useRoute()
const loading = ref(false)
const persiapan = ref(null)
const kySessions = ref([])
const ukurs = ref([])
const activeKy = ref(null)
const ukurVal = ref('')
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const title = computed(() => persiapan.value?.kode_proses || t('pages.mrpProses.title'))
const isDone = computed(() => ['saved', 'completed'].includes(persiapan.value?.status || ''))
const kyForm = reactive({ kode_palet: '', kode_yl: '', target_qty: 0 })

const flowSteps = computed(() => {
  const s = persiapan.value?.status || 'draft'
  const order = ['draft', 'started', 'completed']
  const normalized = s === 'saved' ? 'completed' : s
  const idx = Math.max(0, order.indexOf(normalized))
  return [
    { key: 'draft', label: t('pages.mrpProses.statusDraft'), done: idx > 0, current: idx === 0 },
    { key: 'started', label: t('pages.mrpProses.statusStarted'), done: idx > 1, current: idx === 1 },
    { key: 'completed', label: t('pages.mrpProses.statusCompleted'), done: idx >= 2, current: idx === 2 },
  ]
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

function statusType(status) {
  const s = String(status || '')
  if (s === 'completed' || s === 'saved') return 'success'
  if (s === 'started') return 'warning'
  if (s === 'draft') return 'info'
  return ''
}

function statusLabel(status) {
  const s = String(status || '')
  const map = {
    draft: t('pages.mrpProses.statusDraft'),
    started: t('pages.mrpProses.statusStarted'),
    saved: t('pages.mrpProses.statusSaved'),
    completed: t('pages.mrpProses.statusCompleted'),
  }
  return map[s] || s || '—'
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpGetProses(route.params.id)
    persiapan.value = data.persiapan
    kySessions.value = data.ky_sessions || []
    ukurs.value = data.ukurs || []
    activeKy.value = data.active_ky
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function act(action, extra = {}) {
  try {
    const res = await mrpProsesAction(route.params.id, { action, ...extra })
    ElMessage.success(res.message || t('common.saved'))
    if (action === 'scan_ky') {
      kyForm.kode_palet = ''
      kyForm.kode_yl = ''
      kyForm.target_qty = 0
    }
    if (action === 'add_ukur') ukurVal.value = ''
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

function scanKy() {
  if (!kyForm.kode_palet?.trim() || !kyForm.kode_yl?.trim()) {
    ElMessage.warning(t('pages.mrpProses.kyRequired'))
    return
  }
  return act('scan_ky', { ...kyForm })
}

function addUkur() {
  if (!activeKy.value) return
  const size = Number(ukurVal.value)
  if (!(size > 0)) {
    ElMessage.warning(t('pages.mrpProses.sizeUkur'))
    return
  }
  return act('add_ukur', { ky_id: activeKy.value.id, size_val: size })
}

function selesaiKy() {
  if (!activeKy.value) return
  return act('selesai_ky', { ky_id: activeKy.value.id })
}

function deleteUkur(ukurId) {
  return act('delete_ukur', { ukur_id: ukurId })
}

function esc(v) {
  return String(v ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

async function printLabel() {
  try {
    const data = await mrpProsesLabel(route.params.id)
    const p = data.persiapan || {}
    const labelTitle = data.title || 'STIKER LOT WIP PRODUKSI'
    const tanggal = p.date_saved || p.date_created || ''
    const w = window.open('', '_blank')
    if (!w) {
      ElMessage.warning(t('pages.mrpProses.popupBlocked'))
      return
    }
    w.document.write(`<!DOCTYPE html>
<html lang="id"><head><meta charset="UTF-8"/>
<title>Label WIP - ${esc(p.kode_proses)}</title>
<style>
  body { font-family: Arial, sans-serif; padding: 20px; }
  .label { border: 2px solid #000; padding: 20px; max-width: 400px; margin: auto; }
  .label h2 { margin: 0 0 10px; font-size: 18px; }
  .label table { width: 100%; font-size: 14px; }
  .label td { padding: 4px 0; vertical-align: top; }
  .label td:first-child { width: 38%; color: #333; }
  @media print { .no-print { display: none; } }
</style></head><body>
  <div class="label">
    <h2>${esc(labelTitle)}</h2>
    <table>
      <tr><td>Kode Proses</td><td><strong>${esc(p.kode_proses)}</strong></td></tr>
      <tr><td>Kode WIP</td><td><strong>${esc(p.kode_wip)}</strong></td></tr>
      <tr><td>Rencana</td><td>${esc(p.kode_rencana || '—')}</td></tr>
      <tr><td>PO</td><td>${esc(p.no_po || '—')}</td></tr>
      <tr><td>Warna</td><td>${esc(p.warna || '—')}</td></tr>
      <tr><td>Tebal</td><td>${esc(p.tebal || '—')}</td></tr>
      <tr><td>Emboss</td><td>${esc(p.emboss || '—')}</td></tr>
      <tr><td>Jenis</td><td>${esc(p.treatment_jenis || '—')}</td></tr>
      <tr><td>Treatment</td><td>${esc(p.treatment_list || '—')}</td></tr>
      <tr><td>Total Size</td><td><strong>${esc(p.total_size ?? 0)}</strong></td></tr>
      <tr><td>Tanggal</td><td>${esc(tanggal)}</td></tr>
    </table>
  </div>
  <p class="no-print" style="text-align:center;margin-top:16px">
    <button onclick="window.print()">Cetak</button>
  </p>
</body></html>`)
    w.document.close()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

onMounted(reload)
</script>

<style scoped>
.mrp-proses-flow {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.mrp-proses-flow__step {
  font-size: 0.75rem;
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  border: 1px solid var(--el-border-color);
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-blank);
}
.mrp-proses-flow__step.is-done {
  border-color: var(--el-color-success-light-5);
  color: var(--el-color-success);
  background: var(--el-color-success-light-9);
}
.mrp-proses-flow__step.is-current {
  border-color: var(--el-color-primary-light-5);
  color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
  font-weight: 600;
}
.mrp-proses-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.6rem;
}
.mrp-proses-stat {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.65rem 0.75rem;
  min-height: 3.4rem;
}
.mrp-proses-stat--wide {
  grid-column: span 2;
}
.mrp-proses-stat__label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.2rem;
}
.mrp-proses-stat__value {
  font-size: 1rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.mrp-proses-stat__value--text {
  font-size: 0.875rem;
  font-weight: 500;
  word-break: break-word;
}
.mrp-proses-form-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: flex-end;
}
.mrp-proses-form-row--accent {
  border-top: 1px dashed var(--el-border-color);
  padding-top: 0.85rem;
}
@media (max-width: 900px) {
  .mrp-proses-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .mrp-proses-stat--wide {
    grid-column: span 2;
  }
}
</style>
