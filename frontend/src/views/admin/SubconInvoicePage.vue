<template>
  <AdminSection :title="t('pages.subconInvoice.title')" :subtitle="t('pages.subconInvoice.subtitle')">
    <template #actions>
      <el-select v-model="filterStatus" class="w-[140px]" clearable :placeholder="t('pages.subconInvoice.allStatuses')">
        <el-option :label="t('pages.subconInvoice.allStatuses')" value="" />
        <el-option :label="t('pages.subconInvoice.draft')" value="draft" />
        <el-option :label="t('pages.subconInvoice.sent')" value="sent" />
        <el-option :label="t('pages.subconInvoice.paid')" value="paid" />
        <el-option :label="t('pages.subconInvoice.cancelled')" value="cancelled" />
      </el-select>
      <el-select v-model="filterType" class="w-[120px]" clearable :placeholder="t('pages.subconInvoice.allTypes')">
        <el-option :label="t('pages.subconInvoice.allTypes')" value="" />
        <el-option :label="t('pages.subconInvoice.barang')" value="barang" />
        <el-option :label="t('pages.subconInvoice.jasa')" value="jasa" />
      </el-select>
      <el-select v-model="filterPoId" class="w-[180px]" clearable filterable :placeholder="t('pages.subconInvoice.selectPo')">
        <el-option v-for="po in subconPOs" :key="po.id" :label="po.po_number" :value="po.id" />
      </el-select>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table :data="filteredRows" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed" :empty-text="t('pages.subconInvoice.tableEmpty')">
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="invoice_number" :label="t('pages.subconInvoice.invoiceNumber')" min-width="150" />
      <el-table-column prop="po_number" :label="t('pages.subconInvoice.poNumber')" min-width="130" />
      <el-table-column prop="customer_name" :label="t('common.customer')" min-width="180" />
      <el-table-column :label="t('pages.subconInvoice.invoiceType')" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.invoice_type === 'barang' ? 'success' : 'warning'" size="small">
            {{ row.invoice_type === 'barang' ? t('pages.subconInvoice.barang') : t('pages.subconInvoice.jasa') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('pages.subconInvoice.amount')" min-width="130" align="right">
        <template #default="{ row }">{{ formatNum(row.amount) }}</template>
      </el-table-column>
      <el-table-column :label="t('common.status')" width="110" align="center">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small">
            {{ t(`pages.subconInvoice.${row.status}`) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="140" fixed="right" align="center">
        <template #default="{ row }">
          <el-tooltip :content="t('common.edit')" placement="top">
            <el-button :icon="EditPen" link type="primary" size="small" :disabled="row.status === 'cancelled'" @click="openEdit(row)" />
          </el-tooltip>
          <el-tooltip :content="t('common.delete')" placement="top">
            <el-button :icon="Delete" link type="danger" size="small" :disabled="row.status === 'cancelled'" @click="confirmDelete(row)" />
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="formVisible" :title="isEditing ? t('pages.subconInvoice.dialogEdit') : t('pages.subconInvoice.dialogAdd')" width="600px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('pages.subconInvoice.poNumber')" required>
          <el-select v-model="form.po_id" filterable class="w-full" :placeholder="t('pages.subconInvoice.selectPo')" :disabled="isEditing" @change="onPoChange">
            <el-option v-for="po in subconPOs" :key="po.id" :label="po.po_number" :value="po.id" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.subconInvoice.invoiceType')" required>
          <el-select v-model="form.invoice_type" class="w-full" :disabled="isEditing">
            <el-option :label="t('pages.subconInvoice.barang')" value="barang" />
            <el-option :label="t('pages.subconInvoice.jasa')" value="jasa" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.subconInvoice.invoiceNumber')">
          <el-input v-model="form.invoice_number" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.subconInvoice.amount')" required>
          <el-input v-model="form.amount" type="number" step="0.01" class="w-full" />
        </el-form-item>
        <el-form-item :label="t('pages.subconInvoice.description')">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item v-if="isEditing" :label="t('common.status')">
          <el-select v-model="form.status" class="w-full">
            <el-option :label="t('pages.subconInvoice.draft')" value="draft" />
            <el-option :label="t('pages.subconInvoice.sent')" value="sent" />
            <el-option :label="t('pages.subconInvoice.paid')" value="paid" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate" type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="generateVisible" :title="t('pages.subconInvoice.generateFromPo')" width="600px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('pages.subconInvoice.poNumber')">
          <el-select v-model="generatePoId" filterable class="w-full" :placeholder="t('pages.subconInvoice.selectPo')">
            <el-option v-for="po in subconPOs" :key="po.id" :label="po.po_number" :value="po.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <p class="text-sm text-slate-500">{{ t('pages.subconInvoice.subconPoOnly') }}</p>
      <template #footer>
        <el-button @click="generateVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="generating" @click="doGenerate">{{ t('pages.subconInvoice.generateFromPo') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, EditPen, Plus } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import {
  createSubconInvoice,
  deleteSubconInvoice,
  generateSubconInvoicesFromPo,
  listSubconInvoices,
  listPo,
  updateSubconInvoice,
} from '../../api/client'

const { t } = useI18n()
const canCreate = can('subcon_invoices', 'create')
const canUpdate = can('subcon_invoices', 'update')
const loading = ref(false)
const saving = ref(false)
const generating = ref(false)
const rows = ref([])
const subconPOs = ref([])
const filterStatus = ref('')
const filterType = ref('')
const filterPoId = ref(null)

const formVisible = ref(false)
const generateVisible = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const generatePoId = ref(null)

const form = reactive({
  po_id: null,
  invoice_type: 'barang',
  invoice_number: '',
  amount: '',
  description: '',
  status: 'draft',
})

function formatNum(v) {
  if (v == null || v === '') return t('common.emptyValue')
  return Number(v).toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function statusTagType(status) {
  const map = {
    draft: 'info',
    sent: 'warning',
    paid: 'success',
    cancelled: 'danger',
  }
  return map[status] || 'info'
}

const filteredRows = computed(() => {
  return rows.value.filter((r) => {
    if (filterStatus.value && r.status !== filterStatus.value) return false
    if (filterType.value && r.invoice_type !== filterType.value) return false
    if (filterPoId.value && r.po_id !== filterPoId.value) return false
    return true
  })
})

async function load() {
  loading.value = true
  try {
    const [invoices, poList] = await Promise.all([
      listSubconInvoices(),
      listPo(),
    ])
    rows.value = invoices
    subconPOs.value = poList.filter((p) => (p.po_category || '').toLowerCase() === 'subcont')
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function onPoChange(poId) {
  if (!poId) return
}

function openCreate() {
  isEditing.value = false
  editingId.value = null
  form.po_id = null
  form.invoice_type = 'barang'
  form.invoice_number = ''
  form.amount = ''
  form.description = ''
  form.status = 'draft'
  formVisible.value = true
}

function openEdit(row) {
  isEditing.value = true
  editingId.value = row.id
  form.po_id = row.po_id
  form.invoice_type = row.invoice_type
  form.invoice_number = row.invoice_number || ''
  form.amount = row.amount || ''
  form.description = row.description || ''
  form.status = row.status
  formVisible.value = true
}

async function submit() {
  if (!form.po_id) {
    ElMessage.warning(t('pages.subconInvoice.rulePoRequired'))
    return
  }
  if (!form.amount) {
    ElMessage.warning(t('pages.subconInvoice.ruleAmountRequired'))
    return
  }
  saving.value = true
  try {
    const payload = {
      po_id: form.po_id,
      invoice_type: form.invoice_type,
      invoice_number: form.invoice_number || undefined,
      amount: Number(form.amount),
      description: form.description || undefined,
    }
    if (isEditing.value) {
      payload.status = form.status
      await updateSubconInvoice(editingId.value, payload)
    } else {
      await createSubconInvoice(payload)
    }
    ElMessage.success(t('pages.subconInvoice.saved'))
    formVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(t('pages.subconInvoice.deleteConfirm'), t('pages.subconInvoice.deleteTitle'), {
      confirmButtonText: t('common.confirm'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    })
    await deleteSubconInvoice(row.id)
    ElMessage.success(t('pages.subconInvoice.deleted'))
    await load()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || t('common.errorGeneric'))
    }
  }
}

function openGenerate() {
  generatePoId.value = null
  generateVisible.value = true
}

async function doGenerate() {
  if (!generatePoId.value) {
    ElMessage.warning(t('pages.subconInvoice.rulePoRequired'))
    return
  }
  generating.value = true
  try {
    const created = await generateSubconInvoicesFromPo(generatePoId.value)
    ElMessage.success(t('pages.subconInvoice.generateSuccess', { n: created.length }))
    generateVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    generating.value = false
  }
}

onMounted(async () => {
  await load()
})
</script>

<style scoped>
</style>
