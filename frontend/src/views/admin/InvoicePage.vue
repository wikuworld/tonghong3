<template>
  <AdminSection :title="t('pages.invoice.title')" :subtitle="t('pages.invoice.subtitle')">
    <template #actions>
      <template v-if="tab === 'list'">
        <el-input v-model="keyword" :placeholder="t('pages.invoice.searchPlaceholder')" clearable class="invoice-toolbar-search" />
        <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
        <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
      </template>
    </template>

    <p class="mb-3 text-sm text-slate-600">
      Invoice membutuhkan <b>delivery</b> berstatus <code class="rounded bg-slate-100 px-1">sent</code> dengan minimal satu baris detail.
      Alur: Packing <code class="rounded bg-slate-100 px-1">done</code> → Delivery + detail → tandai terkirim → buat invoice.
    </p>

    <el-tabs v-model="tab">
      <el-tab-pane :label="t('pages.invoice.tabList')" name="list">
        <el-table :data="filteredRows" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('pages.invoice.tableEmpty')">
          <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
          <el-table-column prop="invoice_number" :label="t('common.invoiceNo')" min-width="150" />
          <el-table-column prop="delivery_id" :label="t('pages.invoice.deliveryId')" width="100" align="center" />
          <el-table-column prop="po_number" :label="t('common.poNo')" min-width="150" />
          <el-table-column prop="customer_name" :label="t('common.customer')" min-width="200" />
          <el-table-column prop="invoice_date" :label="t('common.date')" width="120" />
          <el-table-column prop="due_date" :label="t('pages.invoice.dueDate')" width="120" />
          <el-table-column :label="`${t('common.total')} (USD)`" min-width="120" align="right">
            <template #default="{ row }">{{ formatNum(row.total_amount) }}</template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="88" fixed="right" align="center">
            <template #default="{ row }">
              <el-tooltip :content="t('common.detail')" placement="top">
                <el-button :icon="View" link type="primary" :aria-label="t('common.detail')" @click="openDetail(row)" />
              </el-tooltip>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.invoice.tabOutstanding')" name="outstanding">
        <div class="mb-3 flex flex-wrap items-end gap-3">
          <el-form-item :label="t('pages.invoice.filter')" class="mb-0">
            <el-select v-model="outstandingMode" class="w-[220px]" @change="loadOutstanding">
              <el-option :label="t('pages.invoice.modeAll')" value="all" />
              <el-option :label="t('pages.invoice.modeDue7d')" value="due7" />
              <el-option :label="t('pages.invoice.modeOverdue')" value="overdue" />
            </el-select>
          </el-form-item>
          <el-checkbox v-model="hidePo" @change="loadOutstanding">{{ t('pages.invoice.hidePo') }}</el-checkbox>
          <el-button :loading="outstandingLoading" @click="loadOutstanding">{{ t('common.search') }}</el-button>
        </div>

        <el-table :data="outstandingRows" v-loading="outstandingLoading" border stripe size="small" class="admin-table" :empty-text="t('pages.invoice.tableEmpty')">
          <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
          <el-table-column prop="invoice_number" :label="t('common.invoiceNo')" min-width="150" />
          <el-table-column prop="po_number" :label="t('common.poNo')" min-width="150" />
          <el-table-column prop="customer_name" :label="t('common.customer')" min-width="200" />
          <el-table-column prop="invoice_date" :label="t('common.date')" width="120" />
          <el-table-column prop="due_date" :label="t('pages.invoice.dueDate')" width="120" />
          <el-table-column prop="tax_invoice_no" :label="t('pages.invoice.taxInvoiceNo')" min-width="140" />
          <el-table-column prop="receipt_no" :label="t('pages.invoice.receiptNo')" min-width="140" />
          <el-table-column prop="nomor_aju" :label="t('pages.invoice.nomorAju')" min-width="140" />
          <el-table-column :label="t('common.actions')" width="88" fixed="right" align="center">
            <template #default="{ row }">
              <el-tooltip v-if="canUpdate" :content="t('common.edit')" placement="top">
                <el-button
                  :icon="EditPen"
                  link
                  type="primary"
                  size="small"
                  :aria-label="t('common.edit')"
                  @click="openEditOutstanding(row)"
                />
              </el-tooltip>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="detailVisible" :title="t('pages.invoice.dialogDetail')" width="560px" destroy-on-close>
      <el-descriptions v-if="detailRow" :column="1" border size="small">
        <el-descriptions-item :label="t('common.invoiceNo')">{{ detailRow.invoice_number }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.invoice.deliveryId')">{{ detailRow.delivery_id }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.poNo')">{{ detailRow.po_number }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.customer')">{{ detailRow.customer_name }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.date')">{{ detailRow.invoice_date }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.invoice.dueDate')">{{ detailRow.due_date || t('common.emptyValue') }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.total')">{{ formatNum(detailRow.total_amount) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('pages.invoice.closeDetail') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="formVisible" :title="t('pages.invoice.dialogAdd')" width="560px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item :label="t('pages.invoice.deliverySentLabel')" required>
          <el-select v-model="form.delivery_id" filterable clearable class="w-full" :placeholder="t('pages.invoice.pickSentDelivery')" @change="onDeliveryPick">
            <el-option
              v-for="d in deliveriesReady"
              :key="d.id"
              :label="`${d.delivery_number || `DLV-${d.id}`} ${t('common.dotSeparator')} ${d.status}`"
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
          <el-input v-model="form.invoice_number" clearable :placeholder="t('pages.invoice.invoiceNoOptionalPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('common.customer')">
          <el-input v-model="form.customer_name" />
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker v-model="form.invoice_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.dueDate')">
          <el-date-picker v-model="form.due_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
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
        <el-button v-if="canCreate" type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="outstandingEditVisible" :title="t('pages.invoice.editOutstanding')" width="560px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item :label="t('pages.invoice.dueDate')">
          <el-date-picker v-model="outstandingEdit.due_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.taxInvoiceNo')">
          <el-input v-model="outstandingEdit.tax_invoice_no" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.taxInvoiceDate')">
          <el-date-picker v-model="outstandingEdit.tax_invoice_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.receiptNo')">
          <el-input v-model="outstandingEdit.receipt_no" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.receivedBy')">
          <el-input v-model="outstandingEdit.received_by" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.receivedDate')">
          <el-date-picker v-model="outstandingEdit.received_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.nopen')">
          <el-input v-model="outstandingEdit.nopen" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.nomorAju')">
          <el-input v-model="outstandingEdit.nomor_aju" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="outstandingEditVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canUpdate" type="primary" :loading="outstandingSaving" @click="saveOutstanding">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { EditPen, Plus, View } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import {
  createInvoice,
  listCustomers,
  listDelivery,
  listInvoice,
  listOutstandingInvoice,
  listPo,
  toIsoDate,
  updateInvoice,
} from '../../api/client'

const { t } = useI18n()
const route = useRoute()
const canCreate = can('invoice', 'create')
const canUpdate = can('invoice', 'update')
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const rows = ref([])
const tab = ref('list')
const outstandingRows = ref([])
const outstandingLoading = ref(false)
const outstandingMode = ref('overdue')
const hidePo = ref(false)
const outstandingEditVisible = ref(false)
const outstandingSaving = ref(false)
const outstandingEdit = reactive({
  id: null,
  due_date: '',
  tax_invoice_no: '',
  tax_invoice_date: '',
  receipt_no: '',
  received_by: '',
  received_date: '',
  nopen: '',
  nomor_aju: '',
})
const poList = ref([])
const customers = ref([])
const deliveries = ref([])

function formatNum(v) {
  if (v == null || v === '') return t('common.emptyValue')
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
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await load()
  const invoiceIdRaw = route.query.invoice_id
  const invoiceId = Number(invoiceIdRaw)
  if (!Number.isNaN(invoiceId) && invoiceId > 0) {
    tab.value = 'list'
    const target = rows.value.find((r) => Number(r.id) === invoiceId)
    if (target) openDetail(target)
  }
})

async function loadOutstanding() {
  outstandingLoading.value = true
  try {
    const params = { hide_po: hidePo.value }
    if (outstandingMode.value === 'overdue') params.overdue_only = true
    if (outstandingMode.value === 'due7') params.due_within_days = 7
    outstandingRows.value = await listOutstandingInvoice(params)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingLoading.value = false
  }
}

function openEditOutstanding(row) {
  outstandingEdit.id = row.id
  outstandingEdit.due_date = row.due_date || ''
  outstandingEdit.tax_invoice_no = row.tax_invoice_no || ''
  outstandingEdit.tax_invoice_date = row.tax_invoice_date || ''
  outstandingEdit.receipt_no = row.receipt_no || ''
  outstandingEdit.received_by = row.received_by || ''
  outstandingEdit.received_date = row.received_date || ''
  outstandingEdit.nopen = row.nopen || ''
  outstandingEdit.nomor_aju = row.nomor_aju || ''
  outstandingEditVisible.value = true
}

async function saveOutstanding() {
  if (!outstandingEdit.id) return
  outstandingSaving.value = true
  try {
    await updateInvoice(outstandingEdit.id, {
      due_date: toIsoDate(outstandingEdit.due_date) || undefined,
      tax_invoice_no: outstandingEdit.tax_invoice_no || undefined,
      tax_invoice_date: toIsoDate(outstandingEdit.tax_invoice_date) || undefined,
      receipt_no: outstandingEdit.receipt_no || undefined,
      received_by: outstandingEdit.received_by || undefined,
      received_date: toIsoDate(outstandingEdit.received_date) || undefined,
      nopen: outstandingEdit.nopen || undefined,
      nomor_aju: outstandingEdit.nomor_aju || undefined,
    })
    ElMessage.success(t('common.save'))
    outstandingEditVisible.value = false
    await loadOutstanding()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingSaving.value = false
  }
}

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
    ElMessage.warning(t('pages.invoice.pickSentDeliveryWarning'))
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
    ElMessage.error(e.message || t('common.errorGeneric'))
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
