<template>
  <div class="space-y-4">
    <AdminSection :title="t('pages.packing.title')" :subtitle="t('pages.packing.subtitle')">
      <template #actions>
        <el-select
          v-model="statusTableFilter"
          clearable
          :placeholder="t('pages.packing.filterPackingStatus')"
          class="w-36 mr-2"
        >
          <el-option :label="t('status.draft')" value="draft" />
          <el-option :label="t('status.done')" value="done" />
        </el-select>
        <el-button v-if="canCreate" type="primary" :loading="loading" @click="openCreate">{{ t('pages.packing.create') }}</el-button>
      </template>

      <div class="admin-inner-card">
        <div class="admin-inner-card__head">
          <div>
            <h3 class="admin-inner-card__title">{{ t('pages.packing.listSectionTitle') }}</h3>
            <p class="admin-inner-card__sub">{{ t('pages.packing.listSectionSub') }}</p>
          </div>
          <el-tooltip placement="top-start" :show-after="200">
            <template #content>{{ t('pages.packing.pageHint') }}</template>
            <el-icon class="packing-hint" :size="16" tabindex="0" :aria-label="t('pages.packing.pageHint')">
              <InfoFilled />
            </el-icon>
          </el-tooltip>
        </div>

        <p class="admin-scroll-hint px-4">{{ t('pages.packing.scrollHint') }}</p>

        <div class="admin-table-scroll px-4 pb-4">
          <el-table :data="displayRows" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('pages.packing.tableEmpty')">
            <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
            <el-table-column prop="packing_number" :label="t('pages.packing.packingNo')" min-width="160" />
            <el-table-column :label="t('pages.packing.production')" min-width="180" show-overflow-tooltip>
              <template #default="{ row }">{{ prodLabel(row.production_id) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.packing.qc')" min-width="160" show-overflow-tooltip>
              <template #default="{ row }">{{ qcLabel(row.qc_header_id) }}</template>
            </el-table-column>
            <el-table-column prop="status" :label="t('common.status')" width="100" />
            <el-table-column prop="created_at" :label="t('pages.packing.createdAt')" min-width="160" />
            <el-table-column :label="t('common.actions')" width="280" fixed="right" align="center">
              <template #default="{ row }">
                <div class="flex flex-wrap items-center justify-center gap-0">
                  <el-tooltip v-if="canUpdate" :content="t('pages.packing.manageLines')" placement="top">
                    <el-button :icon="EditPen" link type="primary" size="small" @click="openLines(row)" />
                  </el-tooltip>
                  <el-tooltip v-if="canPrint" :content="t('pages.packing.printInvpl')" placement="top">
                    <el-button :icon="Printer" type="primary" link size="small" @click="openInvpl(row.id)" />
                  </el-tooltip>
                  <el-tooltip v-if="canPrint" :content="t('pages.packing.pdf')" placement="top">
                    <el-button :icon="Document" link size="small" @click="downloadInvplPdf(row.id)" />
                  </el-tooltip>
                  <el-tooltip v-if="canPrint" :content="t('pages.packing.excel')" placement="top">
                    <el-button :icon="Grid" link size="small" @click="downloadInvplExcel(row.id)" />
                  </el-tooltip>
                  <el-tooltip v-if="canUpdate" :content="t('pages.packing.markInvpl')" placement="top">
                    <el-button :icon="Stamp" link size="small" :loading="markInvplId === row.id" @click="markInvpl(row)" />
                  </el-tooltip>
                  <el-tooltip
                    v-if="canUpdate && (row.status || '').toLowerCase() !== 'done'"
                    :content="t('status.done')"
                    placement="top"
                  >
                    <el-button :icon="Select" type="warning" link size="small" :loading="markingId === row.id" @click="markDone(row)" />
                  </el-tooltip>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </AdminSection>

    <el-dialog v-model="dlg" :title="t('pages.packing.dialogAdd')" width="480px" destroy-on-close align-center @closed="reset">
      <el-form label-position="top">
        <el-form-item :label="t('pages.packing.production')" required>
          <el-select v-model="form.production_id" filterable clearable class="w-full">
            <el-option
              v-for="p in productions"
              :key="p.id"
              :label="`${p.production_number || p.id} ${t('common.dotSeparator')} ${poNum(p.po_id)}`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.packing.qcHeader')" required>
          <el-select v-model="form.qc_header_id" filterable class="w-full" :placeholder="t('pages.packing.qcHeaderPlaceholder')">
            <el-option
              v-for="q in qcs"
              :key="q.id"
              :label="`${q.qc_number || `QC-${q.id}`} ${t('common.dotSeparator')} ${t('pages.packing.prodShort')} ${q.production_id}`"
              :value="q.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.status')">
          <el-select v-model="form.status" class="w-full">
            <el-option :label="t('status.draft')" value="draft" />
            <el-option :label="t('status.done')" value="done" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate" type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="linesDlg"
      width="920px"
      destroy-on-close
      align-center
      class="packing-lines-dialog"
      :title="t('pages.packing.linesDialogTitle')"
      @closed="resetLines"
    >
      <p v-if="linesPacking" class="mb-3 text-sm text-slate-600">
        {{ linesPacking.packing_number }} — {{ t('pages.packing.linesDialogSub') }}
      </p>
      <div v-if="linesLoading" class="py-8 text-center text-slate-500">{{ t('common.loadingData') }}</div>
      <el-table v-else :data="lineRows" border size="small" max-height="52vh" :empty-text="t('pages.packing.linesEmpty')">
        <el-table-column prop="lot_no" :label="t('pages.packing.colLotNo')" min-width="150" show-overflow-tooltip />
        <el-table-column prop="so_number" :label="t('pages.packing.colSoNumber')" min-width="130" show-overflow-tooltip />
        <el-table-column prop="material_name" :label="t('pages.delivery.columns.materialName')" min-width="140" show-overflow-tooltip />
        <el-table-column :label="t('pages.packing.colQtySf')" width="110">
          <template #default="{ row }">
            <el-input v-model="row._qty_packed" type="number" step="0.01" size="small" />
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.delivery.columns.roll')" width="80">
          <template #default="{ row }">
            <el-input v-model="row._qty_roll" type="number" step="1" size="small" />
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.delivery.columns.pcs')" width="80">
          <template #default="{ row }">
            <el-input v-model="row._qty_pcs" type="number" step="1" size="small" />
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.packing.colWeight')" width="100">
          <template #default="{ row }">
            <el-input v-model="row._weight_net" type="number" step="0.001" size="small" />
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="linesDlg = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canUpdate" type="primary" :loading="linesSaving" @click="saveLines">{{ t('pages.packing.saveLines') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Document, EditPen, Grid, InfoFilled, Printer, Select, Stamp } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import {
  createPacking,
  fetchAuthenticatedDocument,
  listPacking,
  listPackingCandidateLines,
  listProduction,
  listPo,
  listQc,
  markInvplPrinted,
  savePackingDetailsBatch,
  updatePacking,
} from '../../api/client'

const { t } = useI18n()
const rows = ref([])
const statusTableFilter = ref('')

const displayRows = computed(() => {
  const f = (statusTableFilter.value || '').toLowerCase()
  if (!f) return rows.value
  return (rows.value || []).filter((r) => (r.status || '').toLowerCase() === f)
})
const canCreate = can('packing', 'create')
const canUpdate = can('packing', 'update')
const canPrint = can('packing', 'print')
const productions = ref([])
const poList = ref([])
const qcs = ref([])
const loading = ref(false)
const saving = ref(false)
const dlg = ref(false)
const markingId = ref(null)
const markInvplId = ref(null)

const linesDlg = ref(false)
const linesPacking = ref(null)
const lineRows = ref([])
const linesLoading = ref(false)
const linesSaving = ref(false)

const form = reactive({
  production_id: null,
  qc_header_id: null,
  status: 'draft',
})

function poNum(poId) {
  const p = poList.value.find((x) => x.id === poId)
  return p?.po_number || poId
}

function prodLabel(pid) {
  const p = productions.value.find((x) => x.id === pid)
  return p ? `${p.production_number || p.id}` : pid
}

function qcLabel(qid) {
  const q = qcs.value.find((x) => x.id === qid)
  return q ? `${q.qc_number || q.id}` : qid
}

function mapLineRow(r) {
  return {
    ...r,
    _qty_packed: r.qty_packed != null ? String(r.qty_packed) : (r.qty_actual != null ? String(r.qty_actual) : ''),
    _qty_roll: r.qty_roll != null ? String(r.qty_roll) : '',
    _qty_pcs: r.qty_pcs != null ? String(r.qty_pcs) : '',
    _weight_net: r.weight_net != null ? String(r.weight_net) : '',
  }
}

async function load() {
  loading.value = true
  try {
    const [pk, pr, po, qc] = await Promise.all([listPacking(), listProduction(), listPo(), listQc()])
    rows.value = pk
    productions.value = pr
    poList.value = po
    qcs.value = qc
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

onMounted(load)

function openCreate() {
  form.production_id = null
  form.qc_header_id = null
  form.status = 'draft'
  dlg.value = true
}

function reset() {
  form.production_id = null
  form.qc_header_id = null
}

async function openLines(row) {
  linesPacking.value = row
  linesDlg.value = true
  linesLoading.value = true
  try {
    const data = await listPackingCandidateLines(row.id)
    lineRows.value = (data || []).map(mapLineRow)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    lineRows.value = []
  } finally {
    linesLoading.value = false
  }
}

function resetLines() {
  linesPacking.value = null
  lineRows.value = []
}

async function saveLines() {
  if (!linesPacking.value?.id) return
  const payload = lineRows.value
    .filter((r) => r.production_detail_id && String(r._qty_packed || '').trim() !== '')
    .map((r) => ({
      production_detail_id: r.production_detail_id,
      qty_packed: Number(r._qty_packed),
      qty_roll: r._qty_roll !== '' ? Number(r._qty_roll) : undefined,
      qty_pcs: r._qty_pcs !== '' ? Number(r._qty_pcs) : undefined,
      weight_net: r._weight_net !== '' ? Number(r._weight_net) : undefined,
    }))
  if (!payload.length) {
    ElMessage.warning(t('pages.packing.linesSaveWarning'))
    return
  }
  linesSaving.value = true
  try {
    await savePackingDetailsBatch(linesPacking.value.id, payload)
    ElMessage.success(t('pages.packing.linesSaved'))
    linesDlg.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    linesSaving.value = false
  }
}

async function submit() {
  if (!form.production_id) {
    ElMessage.warning(t('pages.packing.pickProductionWarning'))
    return
  }
  if (!form.qc_header_id) {
    ElMessage.warning(t('pages.packing.pickQcWarning'))
    return
  }
  saving.value = true
  try {
    await createPacking({
      production_id: form.production_id,
      qc_header_id: form.qc_header_id,
      status: form.status,
    })
    ElMessage.success(t('pages.packing.created'))
    dlg.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

async function openInvpl(id) {
  try {
    await fetchAuthenticatedDocument(`/documents/invpl/${id}`, { mode: 'open' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadInvplPdf(id) {
  try {
    await fetchAuthenticatedDocument(`/documents/invpl/${id}/pdf`, { mode: 'open' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadInvplExcel(id) {
  try {
    await fetchAuthenticatedDocument(`/documents/invpl/${id}/xlsx`, {
      mode: 'download',
      downloadFallbackName: `invpl_${id}.xlsx`,
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function markInvpl(row) {
  markInvplId.value = row.id
  try {
    await markInvplPrinted(row.id)
    ElMessage.success(t('pages.packing.invplMarked'))
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    markInvplId.value = null
  }
}

async function markDone(row) {
  markingId.value = row.id
  try {
    await updatePacking(row.id, { status: 'done' })
    ElMessage.success(t('pages.packing.doneMarked'))
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    markingId.value = null
  }
}
</script>

<style scoped>
.packing-hint {
  color: #64748b;
  cursor: help;
}
</style>
