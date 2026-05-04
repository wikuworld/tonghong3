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
      <el-alert :title="t('pages.packing.guide')" type="info" show-icon :closable="false" class="mb-3" />
      <el-table :data="displayRows" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('pages.packing.tableEmpty')">
        <el-table-column prop="packing_number" :label="t('pages.packing.packingNo')" min-width="160" />
        <el-table-column :label="t('pages.packing.production')" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ prodLabel(row.production_id) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.packing.qc')" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ qcLabel(row.qc_header_id) }}</template>
        </el-table-column>
        <el-table-column prop="status" :label="t('common.status')" width="100" />
        <el-table-column prop="created_at" :label="t('pages.packing.createdAt')" min-width="160" />
        <el-table-column :label="t('pages.packing.actionsInvpl')" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <div class="flex flex-wrap items-center justify-center gap-0">
              <el-tooltip v-if="canPrint" :content="t('pages.packing.printInvpl')" placement="top">
                <el-button
                  :icon="Printer"
                  type="primary"
                  link
                  size="small"
                  :aria-label="t('pages.packing.printInvpl')"
                  @click="openInvpl(row.id)"
                />
              </el-tooltip>
              <el-tooltip v-if="canPrint" :content="t('pages.packing.pdf')" placement="top">
                <el-button
                  :icon="Document"
                  link
                  size="small"
                  :aria-label="t('pages.packing.pdf')"
                  @click="downloadInvplPdf(row.id)"
                />
              </el-tooltip>
              <el-tooltip v-if="canPrint" :content="t('pages.packing.excel')" placement="top">
                <el-button
                  :icon="Grid"
                  link
                  size="small"
                  :aria-label="t('pages.packing.excel')"
                  @click="downloadInvplExcel(row.id)"
                />
              </el-tooltip>
              <el-tooltip v-if="canUpdate" :content="t('pages.packing.markInvpl')" placement="top">
                <el-button
                  :icon="Stamp"
                  link
                  size="small"
                  :loading="markInvplId === row.id"
                  :aria-label="t('pages.packing.markInvpl')"
                  @click="markInvpl(row)"
                />
              </el-tooltip>
              <el-tooltip
                v-if="canUpdate && (row.status || '').toLowerCase() !== 'done'"
                :content="t('status.done')"
                placement="top"
              >
                <el-button
                  :icon="Select"
                  type="warning"
                  link
                  size="small"
                  :loading="markingId === row.id"
                  :aria-label="t('status.done')"
                  @click="markDone(row)"
                />
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>
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
        <div class="packing-dialog-footer">
          <el-button @click="dlg = false">{{ t('common.cancel') }}</el-button>
          <el-button v-if="canCreate" type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Document, Grid, Printer, Select, Stamp } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import {
  createPacking,
  fetchAuthenticatedDocument,
  listPacking,
  listProduction,
  listPo,
  listQc,
  markInvplPrinted,
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

async function load() {
  loading.value = true
  try {
    const [pk, pr, po, qc] = await Promise.all([
      listPacking(),
      listProduction(),
      listPo(),
      listQc(),
    ])
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
.packing-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
