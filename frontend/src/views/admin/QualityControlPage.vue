<template>
  <AdminSection :title="t('pages.qc.title')" :subtitle="t('pages.qc.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.qc.searchPlaceholder')"
        clearable
        class="qc-toolbar-search"
      />
      <el-button v-if="canManage" type="primary" :icon="Plus" :loading="loading" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table :data="filteredRows" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('pages.qc.tableEmpty')">
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="qc_number" :label="t('common.qcNo')" min-width="130" />
      <el-table-column prop="production_label" label="Production" min-width="160" show-overflow-tooltip />
      <el-table-column prop="qc_date" :label="t('common.date')" width="120" />
      <el-table-column :label="t('common.result')" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.sample_result" :type="row.sample_result === 'ok' ? 'success' : 'danger'" size="small">
            {{ row.sample_result === 'ok' ? t('status.ok') : t('status.ng') }}
          </el-tag>
          <span v-else>—</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="90" align="center" fixed="right">
        <template #default="{ row }">
          <el-button :icon="View" link type="primary" @click="openDetail(row)" />
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailVisible" :title="t('pages.qc.dialogDetail')" width="640px" destroy-on-close>
      <el-descriptions v-if="detailHdr" :column="1" border size="small">
        <el-descriptions-item :label="t('common.qcNo')">{{ detailHdr.qc_number }}</el-descriptions-item>
        <el-descriptions-item label="Production ID">{{ detailHdr.production_id }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.date')">{{ detailHdr.qc_date || '—' }}</el-descriptions-item>
      </el-descriptions>
      <el-table v-if="detailLines.length" :data="detailLines" class="mt-3" border size="small" max-height="280">
        <el-table-column prop="thickness_actual" :label="t('common.actual')" width="100" />
        <el-table-column prop="thickness_min" label="Min" width="80" />
        <el-table-column prop="thickness_max" label="Max" width="80" />
        <el-table-column prop="is_ok" :label="t('common.result')" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_ok ? 'success' : 'danger'" size="small">{{ row.is_ok ? 'OK' : 'NG' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('pages.qc.closeDetail') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="formVisible" :title="t('pages.qc.dialogAdd')" width="560px" destroy-on-close @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="Production" prop="production_id">
          <el-select v-model="form.production_id" filterable class="w-full" @change="onProdChange">
            <el-option
              v-for="p in productions"
              :key="p.id"
              :label="`${p.production_number || p.id} · PO ${poNum(p.po_id)}`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Baris produksi (lot)" prop="production_detail_id">
          <el-select v-model="form.production_detail_id" filterable clearable class="w-full" placeholder="Pilih lot / baris">
            <el-option
              v-for="d in prodDetails"
              :key="d.id"
              :label="`#${d.id} lot ${d.lot_number || '—'}`"
              :value="d.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker v-model="form.qc_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('common.actual') + ' (thickness)'">
          <el-input v-model="form.thickness_actual" type="number" step="0.01" />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="Min">
              <el-input v-model="form.thickness_min" type="number" step="0.01" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Max">
              <el-input v-model="form.thickness_max" type="number" step="0.01" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canManage" type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Plus, View } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { canWrite } from '../../security/permissions'
import {
  addQcDetail,
  createQc,
  listProduction,
  listProductionDetails,
  listPo,
  listQc,
  listQcDetails,
} from '../../api/client'

const { t } = useI18n()
const canManage = canWrite('qc')
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const rows = ref([])
const productions = ref([])
const poList = ref([])
const prodDetails = ref([])

const poNum = (id) => {
  const p = poList.value.find((x) => x.id === id)
  return p?.po_number || id
}

async function load() {
  loading.value = true
  try {
    const [qc, pr, po] = await Promise.all([listQc(), listProduction(), listPo()])
    poList.value = po
    productions.value = pr
    const detailLists = await Promise.all(qc.map((q) => listQcDetails(q.id).catch(() => [])))
    rows.value = qc.map((q, i) => {
      const lines = detailLists[i]
      const ok = lines.find((l) => l.is_ok)
      const ng = lines.find((l) => l.is_ok === false)
      return {
        ...q,
        qc_date: q.qc_date ? String(q.qc_date).slice(0, 10) : '',
        production_label: `${pr.find((x) => x.id === q.production_id)?.production_number || q.production_id}`,
        sample_result: ok ? 'ok' : ng ? 'ng' : null,
      }
    })
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    loading.value = false
  }
}

onMounted(load)

const filteredRows = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) => JSON.stringify(r).toLowerCase().includes(q))
})

const detailVisible = ref(false)
const detailHdr = ref(null)
const detailLines = ref([])

async function openDetail(row) {
  detailHdr.value = row
  detailLines.value = await listQcDetails(row.id).catch(() => [])
  detailVisible.value = true
}

const formVisible = ref(false)
const formRef = ref(null)
const form = reactive({
  production_id: null,
  production_detail_id: null,
  qc_date: '',
  thickness_actual: '',
  thickness_min: '',
  thickness_max: '',
})

const rules = {
  production_id: [{ required: true, message: 'Pilih production', trigger: 'change' }],
}

function resetForm() {
  form.production_id = null
  form.production_detail_id = null
  form.qc_date = ''
  form.thickness_actual = ''
  form.thickness_min = ''
  form.thickness_max = ''
  prodDetails.value = []
}

async function onProdChange(pid) {
  form.production_detail_id = null
  prodDetails.value = pid ? await listProductionDetails(pid).catch(() => []) : []
}

function openCreate() {
  resetForm()
  formVisible.value = true
}

async function submit() {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  if (!form.production_detail_id) {
    ElMessage.warning('Pilih baris produksi')
    return
  }
  saving.value = true
  try {
    const poId = productions.value.find((x) => x.id === form.production_id)?.po_id
    const hdr = await createQc({
      production_id: form.production_id,
      po_id: poId || undefined,
      qc_date: form.qc_date || undefined,
    })
    await addQcDetail(hdr.id, {
      production_detail_id: form.production_detail_id,
      thickness_actual: form.thickness_actual ? Number(form.thickness_actual) : undefined,
      thickness_min: form.thickness_min ? Number(form.thickness_min) : undefined,
      thickness_max: form.thickness_max ? Number(form.thickness_max) : undefined,
    })
    ElMessage.success(t('pages.customers.saved'))
    formVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || 'Error')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.admin-table {
  width: 100%;
}
</style>
