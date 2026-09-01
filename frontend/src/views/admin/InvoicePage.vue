<template>
  <AdminSection :title="t('pages.invoice.title')" :subtitle="t('pages.invoice.subtitle')">
    <template #actions>
      <el-input
        v-if="tab === 'list'"
        v-model="keyword"
        :placeholder="t('pages.invoice.searchPlaceholder')"
        clearable
        class="invoice-toolbar-search"
      />
      <span v-if="tabLoading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="tabLoading" @click="refreshCurrentTab">{{ t('common.refresh') }}</el-button>
      <el-button v-if="tab === 'list' && canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-alert type="info" :closable="false" show-icon class="invoice-flow-hint mb-4">
      <template #title>{{ t('pages.invoice.flowHintTitle') }}</template>
      {{ t('pages.invoice.flowHint') }}
    </el-alert>

    <el-tabs v-model="tab" @tab-change="onTabChange">
      <el-tab-pane name="list">
        <template #label>
          <span class="flex items-center gap-1">
            {{ t('pages.invoice.tabList') }}
            <el-badge v-if="invoiceListCount > 0" :value="invoiceListCount" :max="99" type="primary" />
          </span>
        </template>

        <div class="invoice-stats mb-4">
          <div class="invoice-stat">
            <span class="invoice-stat__value">{{ listStats.total }}</span>
            <span class="invoice-stat__label">{{ t('common.total') }}</span>
          </div>
          <div class="invoice-stat invoice-stat--shown">
            <span class="invoice-stat__value">{{ listStats.shown }}</span>
            <span class="invoice-stat__label">{{ t('pages.invoice.shownRows') }}</span>
          </div>
          <div class="invoice-stat invoice-stat--amount">
            <span class="invoice-stat__value">{{ formatNum(listStats.amount) }}</span>
            <span class="invoice-stat__label">{{ t('pages.invoice.totalAmount') }} (USD)</span>
          </div>
        </div>

        <div class="admin-table-scroll">
          <el-table
            :data="filteredRows"
            v-loading="loading"
            border
            stripe
            size="small"
            class="admin-table invoice-list-table"
            :empty-text="t('pages.invoice.tableEmpty')"
          >
            <el-table-column type="index" :label="t('common.noLabel')" width="50" align="center" fixed="left" />
            <el-table-column prop="invoice_number" :label="t('common.invoiceNo')" min-width="150" show-overflow-tooltip>
              <template #default="{ row }">
                <el-button link type="primary" @click="openDetail(row)">
                  {{ row.invoice_number || `#${row.id}` }}
                </el-button>
              </template>
            </el-table-column>
            <el-table-column prop="delivery_id" :label="t('pages.invoice.deliveryId')" width="110" align="center">
              <template #default="{ row }">
                <el-button v-if="row.delivery_id" link type="primary" @click="goDelivery(row.delivery_id)">
                  {{ row.delivery_id }}
                </el-button>
                <span v-else>—</span>
              </template>
            </el-table-column>
            <el-table-column prop="po_number" :label="t('pages.mrpRencana.soRef')" min-width="150" show-overflow-tooltip>
              <template #default="{ row }">
                <el-button v-if="row.po_id" link type="primary" @click="goPo(row.po_id)">
                  {{ row.po_number || `#${row.po_id}` }}
                </el-button>
                <span v-else>{{ row.po_number || '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="customer_name" :label="t('common.customer')" min-width="180" show-overflow-tooltip />
            <el-table-column :label="t('common.date')" width="120">
              <template #default="{ row }">{{ formatDate(row.invoice_date) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.dueDate')" width="120">
              <template #default="{ row }">{{ formatDate(row.due_date) }}</template>
            </el-table-column>
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
        </div>

        <div v-if="filteredRows.length" class="invoice-total-bar">
          <span>{{ t('pages.invoice.filteredTotal') }}: {{ formatCurrency(filteredTotalAmount, 'USD') }}</span>
        </div>
      </el-tab-pane>

      <el-tab-pane name="outstanding">
        <template #label>
          <span class="flex items-center gap-1">
            {{ t('pages.invoice.tabOutstanding') }}
            <el-badge v-if="outstandingCount > 0" :value="outstandingCount" :max="99" type="danger" />
          </span>
        </template>

        <div class="filter-panel mb-4">
          <p class="filter-panel__title">{{ t('common.filter') }}</p>
          <el-form class="filter-form" label-position="top">
            <el-row :gutter="12">
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item :label="t('pages.invoice.filter')">
                  <el-select v-model="outstandingMode" class="w-full" @change="loadOutstanding">
                    <el-option :label="t('pages.invoice.modeAll')" value="all" />
                    <el-option :label="t('pages.invoice.modeDue7d')" value="due7" />
                    <el-option :label="t('pages.invoice.modeOverdue')" value="overdue" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" :lg="6">
                <el-form-item :label="t('pages.invoice.displayOptions')">
                  <el-checkbox v-model="hidePo" @change="loadOutstanding">{{ t('pages.invoice.hidePo') }}</el-checkbox>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8" :md="6" :lg="3" class="invoice-filter-action-col">
                <el-form-item label="&nbsp;">
                  <el-button class="w-full" :icon="RefreshLeft" @click="resetOutstandingFilters">{{ t('common.reset') }}</el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <div class="invoice-stats mb-4">
          <div class="invoice-stat">
            <span class="invoice-stat__value">{{ outstandingStats.total }}</span>
            <span class="invoice-stat__label">{{ t('common.total') }}</span>
          </div>
          <div class="invoice-stat invoice-stat--unpaid">
            <span class="invoice-stat__value">{{ outstandingStats.unpaid }}</span>
            <span class="invoice-stat__label">{{ t('pages.invoice.unpaid') }}</span>
          </div>
          <div class="invoice-stat invoice-stat--paid">
            <span class="invoice-stat__value">{{ outstandingStats.paid }}</span>
            <span class="invoice-stat__label">{{ t('pages.invoice.paid') }}</span>
          </div>
        </div>

        <div class="admin-table-scroll">
          <el-table
            :data="outstandingRows"
            v-loading="outstandingLoading"
            border
            stripe
            size="small"
            class="admin-table invoice-outstanding-table"
            :empty-text="t('pages.invoice.tableEmpty')"
          >
            <el-table-column type="index" :label="t('common.noLabel')" width="50" align="center" fixed="left" />
            <el-table-column prop="invoice_number" :label="t('common.invoiceNo')" min-width="150" show-overflow-tooltip />
            <el-table-column prop="po_number" :label="t('pages.mrpRencana.soRef')" min-width="150" show-overflow-tooltip>
              <template #default="{ row }">
                <el-button v-if="row.po_id" link type="primary" @click="goPo(row.po_id)">
                  {{ row.po_number || `#${row.po_id}` }}
                </el-button>
                <span v-else>{{ row.po_number || '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="customer_name" :label="t('common.customer')" min-width="180" show-overflow-tooltip />
            <el-table-column :label="t('common.date')" width="120">
              <template #default="{ row }">{{ formatDate(row.invoice_date) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.dueDate')" width="120">
              <template #default="{ row }">{{ formatDate(row.due_date) }}</template>
            </el-table-column>
            <el-table-column prop="tax_invoice_no" :label="t('pages.invoice.taxInvoiceNo')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="receipt_no" :label="t('pages.invoice.receiptNo')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="nomor_aju" :label="t('pages.invoice.nomorAju')" min-width="140" show-overflow-tooltip />
            <el-table-column :label="t('pages.invoice.paymentStatus')" width="130" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="statusType(row.payment_status)">
                  {{ statusLabel(row.payment_status, { paid: t('pages.invoice.paid'), unpaid: t('pages.invoice.unpaid') }) }}
                </el-tag>
              </template>
            </el-table-column>
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
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="detailVisible" :title="t('pages.invoice.dialogDetail')" width="560px" destroy-on-close align-center>
      <el-descriptions v-if="detailRow" :column="1" border size="small">
        <el-descriptions-item :label="t('common.invoiceNo')">{{ detailRow.invoice_number }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.invoice.deliveryId')">
          <el-button v-if="detailRow.delivery_id" link type="primary" @click="goDelivery(detailRow.delivery_id)">
            {{ detailRow.delivery_id }}
          </el-button>
          <span v-else>—</span>
        </el-descriptions-item>
        <el-descriptions-item :label="t('pages.mrpRencana.soRef')">
          <el-button v-if="detailRow.po_id" link type="primary" @click="goPo(detailRow.po_id)">
            {{ detailRow.po_number || `#${detailRow.po_id}` }}
          </el-button>
          <span v-else>{{ detailRow.po_number || '—' }}</span>
        </el-descriptions-item>
        <el-descriptions-item :label="t('common.customer')">{{ detailRow.customer_name }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.date')">{{ detailRow.invoice_date }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.invoice.dueDate')">{{ detailRow.due_date || t('common.emptyValue') }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.total')">{{ formatNum(detailRow.total_amount) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" :icon="Close" @click="detailVisible = false">{{ t('pages.invoice.closeDetail') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="formVisible" :title="t('pages.invoice.dialogAdd')" width="560px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('pages.invoice.deliverySentLabel')" required>
          <el-select v-model="form.delivery_id" filterable clearable class="w-full" :placeholder="t('pages.invoice.pickSentDelivery')" @change="onDeliveryPick">
            <el-option
              v-for="d in deliveriesReady"
              :key="d.id"
              :label="deliveryOptionLabel(d)"
              :value="d.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.mrpRencana.soRef')">
          <el-select v-model="form.po_id" filterable clearable class="w-full" @change="onPoPick">
            <el-option v-for="p in poList" :key="p.id" :label="p.po_number" :value="p.id" />
          </el-select>
          <span class="mt-1 block text-xs text-slate-500">{{ t('pages.invoice.deliveryValidationHint') }}</span>
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
        <el-button :icon="Close" @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate" type="primary" :icon="Check" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="outstandingEditVisible" :title="t('pages.invoice.editOutstanding')" width="560px" destroy-on-close align-center>
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
        <el-form-item :label="t('pages.invoice.paymentStatus')">
          <el-select v-model="outstandingEdit.payment_status" class="w-full">
            <el-option :label="t('pages.invoice.unpaid')" value="unpaid" />
            <el-option :label="t('pages.invoice.paid')" value="paid" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.invoice.paymentAmount')">
          <el-input v-model="outstandingEdit.payment_amount" type="number" step="0.01" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.paymentDate')">
          <el-date-picker v-model="outstandingEdit.payment_date" type="date" value-format="YYYY-MM-DD" class="w-full" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.paymentRemark')">
          <el-input v-model="outstandingEdit.payment_remark" maxlength="120" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.paymentBankAccount')">
          <el-input v-model="outstandingEdit.payment_bank_account" maxlength="100" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.paymentProof')">
          <el-input v-model="outstandingEdit.payment_proof_url" maxlength="500" placeholder="URL atau path file" />
        </el-form-item>
        <el-divider content-position="left">{{ t('pages.invoice.creditNoteSection') }}</el-divider>
        <el-form-item :label="t('pages.invoice.creditNoteNo')">
          <el-input v-model="outstandingEdit.credit_note_no" maxlength="120" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.creditNoteDate')">
          <el-date-picker v-model="outstandingEdit.credit_note_date" type="date" value-format="YYYY-MM-DD" class="w-full" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.creditNoteAmount')">
          <el-input v-model="outstandingEdit.credit_note_amount" type="number" step="0.01" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.oiaExportUsd')">
          <el-input v-model="outstandingEdit.oia_export_usd" type="number" step="0.01" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="outstandingEditVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canUpdate" type="primary" :icon="Check" :loading="outstandingSaving" @click="saveOutstanding">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { EditPen, Plus, View, Check, Close, Refresh, RefreshLeft } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import { formatCurrency, formatDate, statusType, statusLabel } from '../../utils/format'
import {
  createInvoice,
  listCustomers,
  listDelivery,
  listDeliveryDetails,
  listInvoice,
  listOutstandingInvoice,
  listPo,
  toIsoDate,
  updateInvoice,
} from '../../api/client'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
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
  payment_status: 'unpaid',
  payment_amount: '',
  payment_date: '',
  payment_remark: '',
  payment_bank_account: '',
  payment_proof_url: '',
  credit_note_no: '',
  credit_note_date: '',
  credit_note_amount: '',
  oia_export_usd: '',
})
const poList = ref([])
const customers = ref([])
const deliveries = ref([])

const tabLoading = computed(() => (tab.value === 'list' ? loading.value : outstandingLoading.value))

function formatNum(v) {
  return formatCurrency(v, 'USD')
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

function refreshCurrentTab() {
  if (tab.value === 'list') load()
  else loadOutstanding()
}

function onTabChange(name) {
  if (name === 'outstanding') loadOutstanding()
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

function resetOutstandingFilters() {
  outstandingMode.value = 'overdue'
  hidePo.value = false
  loadOutstanding()
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
  outstandingEdit.payment_status = row.payment_status || 'unpaid'
  outstandingEdit.payment_amount = row.payment_amount ?? ''
  outstandingEdit.payment_date = row.payment_date || ''
  outstandingEdit.payment_remark = row.payment_remark || ''
  outstandingEdit.payment_bank_account = row.payment_bank_account || ''
  outstandingEdit.payment_proof_url = row.payment_proof_url || ''
  outstandingEdit.credit_note_no = row.credit_note_no || ''
  outstandingEdit.credit_note_date = row.credit_note_date || ''
  outstandingEdit.credit_note_amount = row.credit_note_amount ?? ''
  outstandingEdit.oia_export_usd = row.oia_export_usd ?? ''
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
      payment_status: outstandingEdit.payment_status || undefined,
      payment_amount: outstandingEdit.payment_amount === '' ? undefined : Number(outstandingEdit.payment_amount),
      payment_date: toIsoDate(outstandingEdit.payment_date) || undefined,
      payment_remark: outstandingEdit.payment_remark || undefined,
      payment_bank_account: outstandingEdit.payment_bank_account || undefined,
      payment_proof_url: outstandingEdit.payment_proof_url || undefined,
      credit_note_no: outstandingEdit.credit_note_no || undefined,
      credit_note_date: toIsoDate(outstandingEdit.credit_note_date) || undefined,
      credit_note_amount:
        outstandingEdit.credit_note_amount === '' ? undefined : Number(outstandingEdit.credit_note_amount),
      oia_export_usd: outstandingEdit.oia_export_usd === '' ? undefined : Number(outstandingEdit.oia_export_usd),
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
  return rows.value.filter((row) => {
    const haystack = [
      row.invoice_number,
      row.po_number,
      row.customer_name,
      row.delivery_id,
      row.invoice_date,
      row.due_date,
      row.total_amount,
    ]
      .filter((v) => v != null && v !== '')
      .join(' ')
      .toLowerCase()
    return haystack.includes(q)
  })
})

const filteredTotalAmount = computed(() =>
  filteredRows.value.reduce((sum, r) => sum + (Number(r.total_amount) || 0), 0),
)

const listStats = computed(() => ({
  total: rows.value.length,
  shown: filteredRows.value.length,
  amount: filteredTotalAmount.value,
}))

const outstandingStats = computed(() => ({
  total: outstandingRows.value.length,
  unpaid: outstandingRows.value.filter((r) => r.payment_status !== 'paid').length,
  paid: outstandingRows.value.filter((r) => r.payment_status === 'paid').length,
}))

const invoiceListCount = computed(() => rows.value.length)

const outstandingCount = computed(() => outstandingRows.value.filter((r) => r.payment_status !== 'paid').length)

const detailVisible = ref(false)
const detailRow = ref(null)

function openDetail(row) {
  detailRow.value = row
  detailVisible.value = true
}

function goPo(poId) {
  if (!poId) return
  router.push({ path: '/admin/po', query: { po_id: String(poId) } })
}

function goDelivery(deliveryId) {
  if (!deliveryId) return
  router.push({ path: '/admin/delivery', query: { delivery_id: String(deliveryId) } })
}

const formVisible = ref(false)
const form = reactive({
  delivery_id: null,
  customer_id: null,
  po_id: null,
  invoice_number: '',
  customer_name: '',
  invoice_date: '',
  due_date: '',
  total_amount: '',
  term_of_payment: '',
})

function onPoPick(pid) {
  if (!pid) return
  const p = poList.value.find((x) => x.id === pid)
  if (!p) return
  if (p.customer_id) {
    form.customer_id = p.customer_id
    const c = customers.value.find((x) => x.id === p.customer_id)
    form.customer_name = c?.name || ''
  }
  form.invoice_number = form.invoice_number || `INV-${p.po_number}`
}

function deliveryOptionLabel(d) {
  const no = d.delivery_number || `DLV-${d.id}`
  return `${no} ${t('common.dotSeparator')} ${d.status}`
}

async function onDeliveryPick(did) {
  if (!did) {
    form.customer_id = null
    form.customer_name = ''
    form.po_id = null
    return
  }
  const d = deliveries.value.find((x) => x.id === did)
  if (d?.customer_id) {
    form.customer_id = d.customer_id
    const c = customers.value.find((x) => x.id === d.customer_id)
    form.customer_name = c?.name || ''
  }
  form.po_id = null
  try {
    const lines = await listDeliveryDetails(did)
    const poIds = [...new Set((lines || []).map((l) => l.po_id).filter((id) => id != null))]
    if (poIds.length === 1) {
      form.po_id = poIds[0]
      onPoPick(poIds[0])
    }
  } catch {
    form.po_id = null
  }
}

function openCreate() {
  form.delivery_id = null
  form.customer_id = null
  form.po_id = null
  form.invoice_number = ''
  form.customer_name = ''
  form.invoice_date = ''
  form.due_date = ''
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
      customer_id: form.customer_id || undefined,
      po_id: form.po_id || undefined,
      invoice_number: form.invoice_number || undefined,
      po_number: p?.po_number || undefined,
      customer_name: form.customer_name || undefined,
      invoice_date: toIsoDate(form.invoice_date) || undefined,
      due_date: toIsoDate(form.due_date) || undefined,
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

watch(
  () => route.query.invoice_id,
  (invoiceIdRaw) => {
    const invoiceId = Number(invoiceIdRaw)
    if (!Number.isNaN(invoiceId) && invoiceId > 0) {
      tab.value = 'list'
      const target = rows.value.find((r) => Number(r.id) === invoiceId)
      if (target) openDetail(target)
    }
  },
)
</script>

<style scoped>
.invoice-flow-hint :deep(.el-alert__title) {
  font-weight: 600;
}

.invoice-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

@media (min-width: 640px) {
  .invoice-stats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.invoice-stat {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  padding: 12px 14px;
}

.invoice-stat__value {
  display: block;
  font-size: 1.2rem;
  font-weight: 700;
  line-height: 1.2;
  color: #0f172a;
  word-break: break-word;
}

.invoice-stat__label {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: #64748b;
}

.invoice-stat--shown .invoice-stat__value {
  color: #0369a1;
}

.invoice-stat--amount .invoice-stat__value {
  color: #15803d;
}

.invoice-stat--unpaid .invoice-stat__value {
  color: #b45309;
}

.invoice-stat--paid .invoice-stat__value {
  color: #15803d;
}

.invoice-filter-action-col {
  display: flex;
  align-items: flex-end;
}

.invoice-list-table {
  width: 100%;
  min-width: 1080px;
}

.invoice-outstanding-table {
  width: 100%;
  min-width: 1180px;
}

.invoice-total-bar {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  font-size: 14px;
  font-weight: 600;
  color: #334155;
}
</style>
