<template>
  <div class="space-y-4">
    <AdminSection title="Packing (QC → Packing → Delivery)">
      <template #actions>
        <el-button v-if="canCreate" type="primary" :loading="loading" @click="openCreate">Tambah packing</el-button>
      </template>
      <p class="mb-3 text-sm text-slate-600">
        Header packing menghubungkan <b>Production</b> dan <b>QC</b>. Baris isi pakai
        <code class="rounded bg-slate-100 px-1">POST /packing/{id}/details</code>.
      </p>
      <el-table :data="rows" v-loading="loading" border stripe size="small">
        <el-table-column prop="packing_number" label="No. Packing" min-width="160" />
        <el-table-column label="Production" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ prodLabel(row.production_id) }}</template>
        </el-table-column>
        <el-table-column label="QC" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ qcLabel(row.qc_header_id) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100" />
        <el-table-column prop="created_at" label="Dibuat" min-width="160" />
        <el-table-column label="INVPL / done" width="220" fixed="right">
          <template #default="{ row }">
            <el-button v-if="canPrint" type="primary" link size="small" @click="openInvpl(row.id)">Cetak INVPL</el-button>
            <el-button v-if="canPrint" link size="small" @click="downloadInvplPdf(row.id)">PDF</el-button>
            <el-button v-if="canPrint" link size="small" @click="downloadInvplExcel(row.id)">Excel</el-button>
            <el-button v-if="canUpdate" link size="small" :loading="markInvplId === row.id" @click="markInvpl(row)">Tandai INVPL</el-button>
            <el-button
              v-if="canUpdate && (row.status || '').toLowerCase() !== 'done'"
              type="warning"
              link
              size="small"
              :loading="markingId === row.id"
              @click="markDone(row)"
            >
              Done
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </AdminSection>

    <el-dialog v-model="dlg" title="Packing baru" width="480px" destroy-on-close @closed="reset">
      <el-form label-position="top">
        <el-form-item label="Production" required>
          <el-select v-model="form.production_id" filterable clearable class="w-full">
            <el-option
              v-for="p in productions"
              :key="p.id"
              :label="`${p.production_number || p.id} · ${poNum(p.po_id)}`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="QC header" required>
          <el-select v-model="form.qc_header_id" filterable class="w-full" placeholder="Wajib — harus sama production">
            <el-option
              v-for="q in qcs"
              :key="q.id"
              :label="`${q.qc_number || 'QC-' + q.id} · prod ${q.production_id}`"
              :value="q.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Status">
          <el-select v-model="form.status" class="w-full">
            <el-option label="draft" value="draft" />
            <el-option label="done" value="done" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dlg = false">Batal</el-button>
        <el-button v-if="canCreate" type="primary" :loading="saving" @click="submit">Simpan</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import {
  createPacking,
  listPacking,
  listProduction,
  listPo,
  listQc,
  markInvplPrinted,
  updatePacking,
} from '../../api/client'

const rows = ref([])
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
    ElMessage.error(e.message || 'Error')
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
    ElMessage.warning('Pilih production')
    return
  }
  if (!form.qc_header_id) {
    ElMessage.warning('Pilih QC header (harus untuk production yang sama)')
    return
  }
  saving.value = true
  try {
    await createPacking({
      production_id: form.production_id,
      qc_header_id: form.qc_header_id,
      status: form.status,
    })
    ElMessage.success('Packing dibuat')
    dlg.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    saving.value = false
  }
}

function openInvpl(id) {
  window.open(`${window.location.origin}/api/v1/documents/invpl/${id}`, '_blank')
}

function downloadInvplPdf(id) {
  window.open(`${window.location.origin}/api/v1/documents/invpl/${id}.pdf`, '_blank')
}

function downloadInvplExcel(id) {
  window.open(`${window.location.origin}/api/v1/documents/invpl/${id}.xlsx`, '_blank')
}

async function markInvpl(row) {
  markInvplId.value = row.id
  try {
    await markInvplPrinted(row.id)
    ElMessage.success('INVPL ditandai sudah dicetak')
    await load()
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    markInvplId.value = null
  }
}

async function markDone(row) {
  markingId.value = row.id
  try {
    await updatePacking(row.id, { status: 'done' })
    ElMessage.success('Packing ditandai selesai')
    await load()
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    markingId.value = null
  }
}
</script>
