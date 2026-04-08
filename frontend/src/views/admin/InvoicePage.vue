<template>
  <AdminSection :title="t('pages.invoice.title')" :subtitle="t('pages.invoice.subtitle')">
    <template #actions>
      <el-input v-model="keyword" :placeholder="t('pages.invoice.searchPlaceholder')" clearable class="invoice-toolbar-search" />
      <el-button type="primary" :icon="Plus" :loading="loading" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <p class="mb-3 text-sm text-slate-600">
      Invoice membutuhkan <b>delivery</b> berstatus <code class="rounded bg-slate-100 px-1">sent</code> dengan minimal satu baris detail.
      Alur: Packing <code class="rounded bg-slate-100 px-1">done</code> → Delivery + detail → tandai terkirim → buat invoice.
    </p>

    <el-table :data="filteredRows" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('pages.invoice.tableEmpty')">
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="invoice_number" :label="t('common.invoiceNo')" min-width="150" />
      <el-table-column prop="delivery_id" label="Delivery ID" width="100" align="center" />
      <el-table-column prop="po_number" :label="t('common.poNo')" min-width="150" />
      <el-table-column prop="customer_name" :label="t('common.customer')" min-width="200" />
      <el-table-column prop="invoice_date" :label="t('common.date')" width="120" />
      <el-table-column :label="`${t('common.total')} (USD)`" min-width="120" align="right">
        <template #default="{ row }">{{ formatNum(row.total_amount) }}</template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="100" fixed="right">
        <template #default="{ row }">
          <el-button :icon="View" link type="primary" @click="openDetail(row)" />
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="detailVisible" :title="t('pages.invoice.dialogDetail')" width="560px" destroy-on-close>
      <el-descriptions v-if="detailRow" :column="1" border size="small">
        <el-descriptions-item :label="t('common.invoiceNo')">{{ detailRow.invoice_number }}</el-descriptions-item>
        <el-descriptions-item label="Delivery ID">{{ detailRow.delivery_id }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.poNo')">{{ detailRow.po_number }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.customer')">{{ detailRow.customer_name }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.date')">{{ detailRow.invoice_date }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.total')">{{ formatNum(detailRow.total_amount) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('pages.invoice.closeDetail') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="formVisible" :title="t('pages.invoice.dialogAdd')" width="560px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="Delivery (harus sent)" required>
          <el-select v-model="form.delivery_id" filterable clearable class="w-full" placeholder="Pilih delivery terkirim" @change="onDeliveryPick">
            <el-option
              v-for="d in deliveriesReady"
              :key="d.id"
              :label="`${d.delivery_number || 'DLV-' + d.id} · ${d.status}`"
              :value="d.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.poNo')">
          <el-select v-model="form.po_id" filterable clearable class="w-full" @change="onPoPick">
            <el-option v-for="p in poList" :key="p.id" :label="p.po_number" :value="p.id" />
          </el-select>
          <span class="mt-1 block text-xs text-slate-500">Opsional — harus cocok dengan barang di delivery (validasi server).</span>
        </el-form-item>
        <el-form-item :label="t('common.invoiceNo')">
          <el-input v-model="form.invoice_number" clearable placeholder="Opsional — auto jika backend mendukung" />
        </el-form-item>
        <el-form-item :label="t('common.customer')">
          <el-input v-model="form.customer_name" />
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker v-model="form.invoice_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('common.total') + ' (USD)'">
          <el-input v-model="form.total_amount" type="number" step="0.01" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.termOfPayment')">
          <el-input v-model="form.term_of_payment" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
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
import {
  createInvoice,
  listCustomers,
  listDelivery,
  listInvoice,
  listPo,
  toIsoDate,
} from '../../api/client'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const rows = ref([])
const poList = ref([])
const customers = ref([])
const deliveries = ref([])

function formatNum(v) {
  if (v == null || v === '') return '—'
  return Number(v).toLocaleString(undefined, { maximumFractionDigits: 2 })
}

const deliveriesReady = computed(() =>
  (deliveries.value || []).filter((d) => (d.status || '').toLowerCase() === 'sent'),
)

async function load() {
  loading.value = true
  try {
    const [inv, po, cust, del] = await Promise.all([
      listInvoice(),
      listPo(),
      listCustomers(),
      listDelivery(),
    ])
    poList.value = po
    customers.value = cust
    deliveries.value = del
    rows.value = inv.map((r) => ({
      ...r,
      invoice_date: r.invoice_date ? String(r.invoice_date).slice(0, 10) : '',
    }))
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
const detailRow = ref(null)

function openDetail(row) {
  detailRow.value = row
  detailVisible.value = true
}

const formVisible = ref(false)
const form = reactive({
  delivery_id: null,
  po_id: null,
  invoice_number: '',
  customer_name: '',
  invoice_date: '',
  total_amount: '',
  term_of_payment: '',
})

function onPoPick(pid) {
  if (!pid) return
  const p = poList.value.find((x) => x.id === pid)
  if (!p?.customer_id) return
  const c = customers.value.find((x) => x.id === p.customer_id)
  form.customer_name = c?.name || ''
  form.invoice_number = form.invoice_number || `INV-${p.po_number}`
}

function onDeliveryPick(did) {
  if (!did) return
  const d = deliveries.value.find((x) => x.id === did)
  if (d?.customer_id) {
    const c = customers.value.find((x) => x.id === d.customer_id)
    form.customer_name = c?.name || form.customer_name
  }
}

function openCreate() {
  form.delivery_id = null
  form.po_id = null
  form.invoice_number = ''
  form.customer_name = ''
  form.invoice_date = ''
  form.total_amount = ''
  form.term_of_payment = ''
  formVisible.value = true
}

async function submit() {
  if (!form.delivery_id) {
    ElMessage.warning('Pilih delivery (status sent)')
    return
  }
  const p = poList.value.find((x) => x.id === form.po_id)
  saving.value = true
  try {
    await createInvoice({
      delivery_id: form.delivery_id,
      invoice_number: form.invoice_number || undefined,
      po_number: p?.po_number || undefined,
      customer_name: form.customer_name || undefined,
      invoice_date: toIsoDate(form.invoice_date) || undefined,
      total_amount: form.total_amount ? Number(form.total_amount) : undefined,
      term_of_payment: form.term_of_payment || undefined,
    })
    ElMessage.success(t('pages.invoice.saved'))
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
