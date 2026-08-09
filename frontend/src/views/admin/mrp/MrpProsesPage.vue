<template>
  <AdminSection :title="t('pages.mrpProses.title')" :subtitle="t('pages.mrpProses.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <el-table
        :data="rows"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        empty-text="—"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_proses" :label="t('pages.mrpProses.kodeProses')" min-width="130" show-overflow-tooltip />
        <el-table-column prop="kode_rencana" :label="t('pages.mrpProses.kodeRpi')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="kode_wip" label="WIP" min-width="120" show-overflow-tooltip />
        <el-table-column prop="no_po" label="PO" width="110" show-overflow-tooltip />
        <el-table-column :label="t('common.color')" width="110" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.warna) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.thickness')" width="90">
          <template #default="{ row }">{{ dash(row.tebal) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.treatmentJenis')" width="90">
          <template #default="{ row }">{{ dash(row.treatment_jenis) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="plain">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpProses.totalSize')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.total_size) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row.id)">{{ t('common.detail') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="createOpen"
      :title="t('pages.mrpProses.createTitle')"
      width="640px"
      destroy-on-close
      append-to-body
    >
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpProses.createHint') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpProses.scanRpi')">
          <div class="flex gap-2 w-full">
            <el-input
              v-model="form.kode_scan"
              :placeholder="t('pages.mrpProses.scanPlaceholder')"
              class="flex-1"
              @keyup.enter="doScan"
            />
            <el-button @click="doScan">{{ t('pages.mrpProses.scan') }}</el-button>
          </div>
        </el-form-item>
        <el-form-item :label="t('pages.mrpProses.pilihItem')">
          <el-select v-model="form.rencana_item_id" filterable clearable class="w-full">
            <el-option
              v-for="it in rencanaItems"
              :key="it.id"
              :label="`${it.kode_rencana_item} · ${it.nama_customer || ''} · ${it.color || ''}`"
              :value="it.id"
            />
          </el-select>
        </el-form-item>
        <div v-if="scanned" class="mrp-proses-scan-card mb-3">
          <span class="mrp-proses-scan-card__label">{{ t('common.detail') }}</span>
          <span class="mrp-proses-scan-card__value">
            {{ scanned.kode_rencana_item }} — {{ dash(scanned.nama_customer) }} /
            {{ dash(scanned.color) }} / {{ dash(scanned.thickness) }}
          </span>
        </div>
        <el-form-item :label="t('pages.mrpProses.treatmentJenis')" required>
          <el-radio-group v-model="form.treatment_jenis" @change="form.treatment_list = []">
            <el-radio-button value="PU">PU</el-radio-button>
            <el-radio-button value="Suede">Suede</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('pages.mrpProses.treatmentList')" required>
          <el-select
            v-model="form.treatment_list"
            multiple
            filterable
            class="w-full"
            :placeholder="t('pages.mrpProses.treatmentRequired')"
          >
            <el-option
              v-for="tr in treatmentsFiltered"
              :key="tr.nama_treatment"
              :label="tr.nama_treatment"
              :value="tr.nama_treatment"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import { mrpCreateProses, mrpListProses, mrpProsesScanRencana } from '../../../api/client'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const createOpen = ref(false)
const rows = ref([])
const rencanaItems = ref([])
const treatments = ref([])
const scanned = ref(null)
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const form = reactive({
  kode_scan: '',
  rencana_item_id: null,
  treatment_jenis: 'PU',
  treatment_list: [],
})

const treatmentsFiltered = computed(() =>
  treatments.value.filter((tr) => tr.jenis === form.treatment_jenis),
)

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
    const data = await mrpListProses()
    rows.value = data.persiapan_list || []
    rencanaItems.value = data.rencana_items || []
    treatments.value = data.treatments || []
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  form.kode_scan = ''
  form.rencana_item_id = null
  form.treatment_jenis = 'PU'
  form.treatment_list = []
  scanned.value = null
  createOpen.value = true
}

async function doScan() {
  if (!form.kode_scan.trim()) return
  try {
    scanned.value = await mrpProsesScanRencana(form.kode_scan.trim())
    form.rencana_item_id = scanned.value.id
  } catch (e) {
    scanned.value = null
    ElMessage.error(e.message || String(e))
  }
}

async function submit() {
  if (!form.rencana_item_id && !form.kode_scan?.trim()) {
    ElMessage.warning(t('pages.mrpProses.scanRpi'))
    return
  }
  if (!form.treatment_list?.length) {
    ElMessage.warning(t('pages.mrpProses.treatmentRequired'))
    return
  }
  saving.value = true
  try {
    const res = await mrpCreateProses({
      rencana_item_id: form.rencana_item_id,
      kode_scan: form.kode_scan,
      treatment_jenis: form.treatment_jenis,
      treatment_list: form.treatment_list,
    })
    ElMessage.success(t('common.saved'))
    createOpen.value = false
    router.push(`/admin/mrp/proses/${res.id}`)
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

function goDetail(id) {
  router.push(`/admin/mrp/proses/${id}`)
}

onMounted(reload)
</script>

<style scoped>
.mrp-proses-scan-card {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.65rem 0.85rem;
  background: var(--el-fill-color-blank);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.mrp-proses-scan-card__label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
}
.mrp-proses-scan-card__value {
  font-size: 0.875rem;
  color: var(--el-text-color-primary);
}
</style>
