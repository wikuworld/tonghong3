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
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
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
              <el-col :xs="24" :sm="12" :md="8" :lg="5">
                <el-form-item :label="t('pages.invoice.filterKeyword')">
                  <el-input v-model="outstandingQ" clearable :placeholder="t('pages.invoice.filterKeyword')" @keyup.enter="loadOutstanding" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" :lg="5">
                <el-form-item :label="t('pages.invoice.filterCustomer')">
                  <el-select v-model="outstandingCustomerId" clearable filterable class="w-full" @change="loadOutstanding">
                    <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" :lg="4">
                <el-form-item :label="t('pages.invoice.colStatusAr')">
                  <el-select v-model="outstandingArStatus" clearable class="w-full" @change="onArStatusChange">
                    <el-option :label="t('pages.invoice.modeStatusAll')" value="" />
                    <el-option :label="t('pages.invoice.statusNotOverdue')" value="not_overdue" />
                    <el-option :label="t('pages.invoice.statusOverdue')" value="overdue" />
                    <el-option :label="t('pages.invoice.statusClosed')" value="closed" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" :lg="4">
                <el-form-item :label="t('pages.invoice.filter')">
                  <el-select v-model="outstandingMode" class="w-full" @change="loadOutstanding">
                    <el-option :label="t('pages.invoice.modeAll')" value="all" />
                    <el-option :label="t('pages.invoice.modeDue7d')" value="due7" />
                    <el-option :label="t('pages.invoice.modeOverdue')" value="overdue" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="12" :md="8" :lg="4">
                <el-form-item :label="t('pages.invoice.displayOptions')">
                  <el-checkbox v-model="openOnly" @change="loadOutstanding">{{ t('pages.invoice.openOnly') }}</el-checkbox>
                  <el-checkbox v-model="hidePo" @change="loadOutstanding">{{ t('pages.invoice.hidePo') }}</el-checkbox>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8" :md="6" :lg="2" class="invoice-filter-action-col">
                <el-form-item label="&nbsp;">
                  <el-button class="w-full" :icon="RefreshLeft" @click="resetOutstandingFilters">{{ t('common.reset') }}</el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <div class="admin-action-bar mb-3">
          <p class="admin-action-bar__hint">{{ t('pages.invoice.printTandaTerima') }} — {{ outstandingSelected.length }} dipilih</p>
          <div class="admin-action-bar__buttons">
            <el-button
              v-if="canUpdate"
              type="primary"
              :disabled="!outstandingSelected.length"
              :loading="tandaTerimaSaving"
              @click="openTandaTerima"
            >
              {{ t('pages.invoice.printTandaTerima') }}
            </el-button>
          </div>
        </div>

        <div class="invoice-stats mb-4">
          <div class="invoice-stat">
            <span class="invoice-stat__value">{{ outstandingStats.total }}</span>
            <span class="invoice-stat__label">{{ t('common.total') }}</span>
          </div>
          <div class="invoice-stat invoice-stat--unpaid">
            <span class="invoice-stat__value">{{ outstandingStats.open }}</span>
            <span class="invoice-stat__label">{{ t('pages.invoice.unpaid') }}</span>
          </div>
          <div class="invoice-stat invoice-stat--paid">
            <span class="invoice-stat__value">{{ outstandingStats.closed }}</span>
            <span class="invoice-stat__label">{{ t('pages.invoice.statusClosed') }}</span>
          </div>
          <div class="invoice-stat invoice-stat--amount">
            <span class="invoice-stat__value">{{ formatNum(outstandingStats.balance) }}</span>
            <span class="invoice-stat__label">{{ t('pages.invoice.colBalance') }}</span>
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
            row-key="id"
            @selection-change="onOutstandingSelection"
          >
            <el-table-column type="selection" width="44" fixed="left" />
            <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" fixed="left" />
            <el-table-column prop="invoice_number" :label="t('common.invoiceNo')" min-width="140" show-overflow-tooltip fixed="left" />
            <el-table-column :label="t('common.date')" width="110">
              <template #default="{ row }">{{ formatDate(row.invoice_date) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.colQty')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_total) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.colAmount')" width="110" align="right">
              <template #default="{ row }">{{ formatNum(row.total_amount) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.colDeduction')" width="100" align="right">
              <template #default="{ row }">{{ formatNum(row.deduction_amount) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.paymentAmount')" width="110" align="right">
              <template #default="{ row }">{{ formatNum(row.payment_amount) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.paymentDate')" width="110">
              <template #default="{ row }">{{ formatDate(row.payment_date) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.colBalance')" width="110" align="right">
              <template #default="{ row }">{{ formatNum(row.balance_after_deduct) }}</template>
            </el-table-column>
            <el-table-column prop="term_of_payment" :label="t('pages.invoice.colTerms')" min-width="120" show-overflow-tooltip />
            <el-table-column :label="t('pages.invoice.dueDate')" width="110">
              <template #default="{ row }">{{ formatDate(row.due_date) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.colStatusAr')" width="120" align="center">
              <template #default="{ row }">
                <el-tag size="small" :type="arStatusType(row.ar_status)">{{ arStatusLabel(row.ar_status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="tax_invoice_no" :label="t('pages.invoice.taxInvoiceNo')" min-width="120" show-overflow-tooltip />
            <el-table-column :label="t('pages.invoice.colDokumenBc')" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ row.dokumen_bc || row.bc_number || row.nopen || '—' }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.invoice.colBcDate')" width="110">
              <template #default="{ row }">{{ formatDate(row.bc_date) }}</template>
            </el-table-column>
            <el-table-column prop="received_by" :label="t('pages.invoice.colReceivedBy')" min-width="140" show-overflow-tooltip />
            <el-table-column :label="t('pages.invoice.colReceivedDate')" width="110">
              <template #default="{ row }">{{ formatDate(row.received_date) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="168" fixed="right" align="center">
              <template #default="{ row }">
                <el-button v-if="canUpdate" link type="primary" size="small" @click="openExtraDetails(row)">
                  {{ t('pages.invoice.actionExtraDetails') }}
                </el-button>
                <el-button v-if="canUpdate" link type="success" size="small" @click="openReceivePayment(row)">
                  {{ t('pages.invoice.actionReceivePayment') }}
                </el-button>
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

    <el-dialog v-model="extraDetailsVisible" :title="t('pages.invoice.extraDetailsTitle')" width="520px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('pages.invoice.taxInvoiceNo')">
          <el-input v-model="extraDetails.tax_invoice_no" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.taxInvoiceDate')">
          <el-date-picker v-model="extraDetails.tax_invoice_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.colDokumenBc')">
          <el-input v-model="extraDetails.nopen" :placeholder="t('pages.invoice.nopen')" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.colBcDate')">
          <el-date-picker v-model="extraDetails.bc_date" type="date" class="w-full" value-format="YYYY-MM-DD" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.nomorAju')">
          <el-input v-model="extraDetails.nomor_aju" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.colReceivedBy')">
          <el-input v-model="extraDetails.received_by" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.colReceivedDate')">
          <el-date-picker v-model="extraDetails.received_date" type="date" class="w-full" value-format="YYYY-MM-DD" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.receiptNo')">
          <el-input v-model="extraDetails.receipt_no" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.dueDate')">
          <el-date-picker v-model="extraDetails.due_date" type="date" class="w-full" value-format="YYYY-MM-DD" clearable />
        </el-form-item>
        <el-divider content-position="left">{{ t('pages.invoice.creditNoteSection') }}</el-divider>
        <el-form-item :label="t('pages.invoice.creditNoteAmount')">
          <el-input v-model="extraDetails.credit_note_amount" type="number" step="0.01" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.oiaExportUsd')">
          <el-input v-model="extraDetails.oia_export_usd" type="number" step="0.01" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="extraDetailsVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canUpdate" type="primary" :icon="Check" :loading="extraDetailsSaving" @click="saveExtraDetails">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="paymentVisible" :title="t('pages.invoice.receivePaymentTitle')" width="440px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-alert v-if="paymentForm.invoice_number" type="info" :closable="false" class="mb-3" :title="paymentForm.invoice_number" />
        <el-form-item :label="t('pages.invoice.paymentAmount')" required>
          <el-input v-model="paymentForm.payment_amount" type="number" step="0.01" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.paymentDate')" required>
          <el-date-picker v-model="paymentForm.payment_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.paymentRemark')">
          <el-input v-model="paymentForm.payment_remark" maxlength="120" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.paymentBankAccount')">
          <el-input v-model="paymentForm.payment_bank_account" maxlength="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="paymentVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canUpdate" type="success" :icon="Check" :loading="paymentSaving" @click="savePayment">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="tandaTerimaVisible" :title="t('pages.invoice.tandaTerimaDialogTitle')" width="480px" destroy-on-close align-center>
      <el-form label-position="top">
        <p class="mb-3 text-sm text-slate-600">{{ outstandingSelected.length }} invoice · {{ tandaTerimaForm.customer_name || '—' }}</p>
        <el-form-item :label="t('pages.invoice.colReceivedBy')">
          <el-input v-model="tandaTerimaForm.received_by" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.colReceivedDate')">
          <el-date-picker v-model="tandaTerimaForm.received_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('pages.invoice.receiptNo')">
          <el-input v-model="tandaTerimaForm.receipt_no" clearable :placeholder="'Auto: NNN/MM/YYYY'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="tandaTerimaVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="default" :loading="tandaTerimaSaving" @click="submitTandaTerima('html')">HTML</el-button>
        <el-button type="primary" :loading="tandaTerimaSaving" @click="submitTandaTerima('pdf')">PDF</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, View, Check, Close, Refresh, RefreshLeft } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import { formatCurrency, formatDate, formatNumber } from '../../utils/format'
import {
  createInvoice,
  fetchAuthenticatedDocument,
  listCustomers,
  listDelivery,
  listDeliveryDetails,
  listInvoice,
  getDelivery,
  listOutstandingInvoice,
  listPo,
  tandaTerimaBatchHtmlPath,
  tandaTerimaBatchPdfPath,
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
const outstandingMode = ref('all')
const outstandingArStatus = ref('')
const outstandingCustomerId = ref(null)
const outstandingQ = ref('')
const openOnly = ref(true)
const hidePo = ref(false)
const outstandingSelected = ref([])
const extraDetailsVisible = ref(false)
const extraDetailsSaving = ref(false)
const extraDetails = reactive({
  id: null,
  tax_invoice_no: '',
  tax_invoice_date: '',
  nopen: '',
  bc_date: '',
  nomor_aju: '',
  received_by: '',
  received_date: '',
  receipt_no: '',
  due_date: '',
  credit_note_amount: '',
  oia_export_usd: '',
})
const paymentVisible = ref(false)
const paymentSaving = ref(false)
const paymentForm = reactive({
  id: null,
  invoice_number: '',
  payment_amount: '',
  payment_date: '',
  payment_remark: '',
  payment_bank_account: '',
})
const tandaTerimaVisible = ref(false)
const tandaTerimaSaving = ref(false)
const tandaTerimaForm = reactive({
  customer_name: '',
  received_by: '',
  received_date: '',
  receipt_no: '',
})
const poList = ref([])
const customers = ref([])
const deliveries = ref([])

const tabLoading = computed(() => (tab.value === 'list' ? loading.value : outstandingLoading.value))

function formatNum(v) {
  return formatCurrency(v, 'USD')
}

function formatQty(v) {
  return formatNumber(v, 2)
}

function arStatusLabel(st) {
  const key = String(st || '').toLowerCase()
  if (key === 'closed') return t('pages.invoice.statusClosed')
  if (key === 'overdue') return t('pages.invoice.statusOverdue')
  return t('pages.invoice.statusNotOverdue')
}

function arStatusType(st) {
  const key = String(st || '').toLowerCase()
  if (key === 'closed') return 'success'
  if (key === 'overdue') return 'danger'
  return 'warning'
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

function tabFromRoute() {
  return String(route.query.tab || '') === 'outstanding' ? 'outstanding' : 'list'
}

async function applyRouteQuery() {
  const nextTab = tabFromRoute()
  if (nextTab !== tab.value) tab.value = nextTab
  if (tab.value === 'outstanding') await loadOutstanding()

  const invoiceId = Number(route.query.invoice_id)
  if (!Number.isNaN(invoiceId) && invoiceId > 0) {
    tab.value = 'list'
    const target = rows.value.find((r) => Number(r.id) === invoiceId)
    if (target) openDetail(target)
    return
  }

  const deliveryId = Number(route.query.delivery_id)
  if (Number.isNaN(deliveryId) || deliveryId <= 0) return
  const wantCreate = String(route.query.create || '') === '1' || route.query.amount != null
  let existing = null
  try {
    const found = await listInvoice({ delivery_id: deliveryId })
    existing = Array.isArray(found) && found.length ? found[0] : null
  } catch {
    existing = (rows.value || []).find((r) => Number(r.delivery_id) === deliveryId) || null
  }
  if (existing) {
    tab.value = 'outstanding'
    outstandingQ.value = String(existing.invoice_number || '').trim()
    openOnly.value = false
    await loadOutstanding()
    return
  }
  if (!canCreate || !wantCreate) return
  if (formVisible.value && Number(form.delivery_id) === deliveryId) return
  await openCreateFromDelivery(deliveryId, route.query.amount)
}

onMounted(async () => {
  await load()
  await applyRouteQuery()
})

async function loadOutstanding() {
  outstandingLoading.value = true
  try {
    const params = {
      hide_po: hidePo.value,
      open_only: openOnly.value,
    }
    if (outstandingMode.value === 'overdue') params.overdue_only = true
    if (outstandingMode.value === 'due7') params.due_within_days = 7
    if (outstandingArStatus.value) params.ar_status = outstandingArStatus.value
    if (outstandingCustomerId.value) params.customer_id = outstandingCustomerId.value
    if (outstandingQ.value.trim()) params.q = outstandingQ.value.trim()
    // If filtering specifically for closed, don't force open_only
    if (outstandingArStatus.value === 'closed') params.open_only = false
    outstandingRows.value = await listOutstandingInvoice(params)
    outstandingSelected.value = []
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingLoading.value = false
  }
}

function onArStatusChange() {
  if (outstandingArStatus.value === 'closed') openOnly.value = false
  loadOutstanding()
}

function resetOutstandingFilters() {
  outstandingMode.value = 'all'
  outstandingArStatus.value = ''
  outstandingCustomerId.value = null
  outstandingQ.value = ''
  openOnly.value = true
  hidePo.value = false
  loadOutstanding()
}

function onOutstandingSelection(rows) {
  outstandingSelected.value = rows || []
}

function openExtraDetails(row) {
  extraDetails.id = row.id
  extraDetails.tax_invoice_no = row.tax_invoice_no || ''
  extraDetails.tax_invoice_date = row.tax_invoice_date || ''
  extraDetails.nopen = row.dokumen_bc || row.bc_number || row.nopen || ''
  extraDetails.bc_date = row.bc_date || ''
  extraDetails.nomor_aju = row.nomor_aju || ''
  extraDetails.received_by = row.received_by || ''
  extraDetails.received_date = row.received_date || ''
  extraDetails.receipt_no = row.receipt_no || ''
  extraDetails.due_date = row.due_date || ''
  extraDetails.credit_note_amount = row.credit_note_amount ?? ''
  extraDetails.oia_export_usd = row.oia_export_usd ?? ''
  extraDetailsVisible.value = true
}

async function saveExtraDetails() {
  if (!extraDetails.id) return
  extraDetailsSaving.value = true
  try {
    await updateInvoice(extraDetails.id, {
      tax_invoice_no: extraDetails.tax_invoice_no || undefined,
      tax_invoice_date: toIsoDate(extraDetails.tax_invoice_date) || undefined,
      nopen: extraDetails.nopen || undefined,
      bc_date: toIsoDate(extraDetails.bc_date) || undefined,
      nomor_aju: extraDetails.nomor_aju || undefined,
      received_by: extraDetails.received_by || undefined,
      received_date: toIsoDate(extraDetails.received_date) || undefined,
      receipt_no: extraDetails.receipt_no || undefined,
      due_date: toIsoDate(extraDetails.due_date) || undefined,
      credit_note_amount:
        extraDetails.credit_note_amount === '' ? undefined : Number(extraDetails.credit_note_amount),
      oia_export_usd: extraDetails.oia_export_usd === '' ? undefined : Number(extraDetails.oia_export_usd),
    })
    ElMessage.success(t('pages.invoice.detailsSaved'))
    extraDetailsVisible.value = false
    await loadOutstanding()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    extraDetailsSaving.value = false
  }
}

function openReceivePayment(row) {
  paymentForm.id = row.id
  paymentForm.invoice_number = row.invoice_number || `#${row.id}`
  paymentForm.payment_amount = row.payment_amount ?? row.balance_after_deduct ?? ''
  paymentForm.payment_date = row.payment_date || toIsoDate(new Date())
  paymentForm.payment_remark = row.payment_remark || ''
  paymentForm.payment_bank_account = row.payment_bank_account || ''
  paymentVisible.value = true
}

async function savePayment() {
  if (!paymentForm.id) return
  const amt = Number(paymentForm.payment_amount)
  if (!Number.isFinite(amt) || amt < 0) {
    ElMessage.warning(t('pages.invoice.paymentAmount'))
    return
  }
  if (!paymentForm.payment_date) {
    ElMessage.warning(t('pages.invoice.paymentDate'))
    return
  }
  paymentSaving.value = true
  try {
    await updateInvoice(paymentForm.id, {
      payment_amount: amt,
      payment_date: toIsoDate(paymentForm.payment_date),
      payment_remark: paymentForm.payment_remark || undefined,
      payment_bank_account: paymentForm.payment_bank_account || undefined,
    })
    ElMessage.success(t('pages.invoice.paymentSaved'))
    paymentVisible.value = false
    await loadOutstanding()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    paymentSaving.value = false
  }
}

function openTandaTerima() {
  if (!outstandingSelected.value.length) {
    ElMessage.warning(t('pages.invoice.tandaTerimaPickWarning'))
    return
  }
  const custKeys = new Set(
    outstandingSelected.value.map((r) => String(r.customer_id || r.customer_name || '')),
  )
  if (custKeys.size > 1) {
    ElMessage.warning(t('pages.invoice.tandaTerimaSameCustomer'))
    return
  }
  const first = outstandingSelected.value[0]
  tandaTerimaForm.customer_name = first.customer_name || ''
  tandaTerimaForm.received_by = first.received_by || ''
  tandaTerimaForm.received_date = toIsoDate(new Date())
  tandaTerimaForm.receipt_no = ''
  tandaTerimaVisible.value = true
}

async function submitTandaTerima(mode) {
  const ids = outstandingSelected.value.map((r) => r.id).filter(Boolean)
  if (!ids.length) {
    ElMessage.warning(t('pages.invoice.tandaTerimaPickWarning'))
    return
  }
  tandaTerimaSaving.value = true
  try {
    const body = {
      invoice_ids: ids,
      received_by: tandaTerimaForm.received_by || undefined,
      received_date: toIsoDate(tandaTerimaForm.received_date) || undefined,
      receipt_no: tandaTerimaForm.receipt_no || undefined,
      stamp_invoices: true,
    }
    const path = mode === 'pdf' ? tandaTerimaBatchPdfPath() : tandaTerimaBatchHtmlPath()
    await fetchAuthenticatedDocument(path, {
      method: 'POST',
      body,
      mode: mode === 'pdf' ? 'download' : 'open',
      downloadFallbackName: 'tanda_terima.pdf',
    })
    ElMessage.success(t('pages.invoice.tandaTerimaSuccess'))
    tandaTerimaVisible.value = false
    await loadOutstanding()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    tandaTerimaSaving.value = false
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

const outstandingStats = computed(() => {
  const rows = outstandingRows.value || []
  return {
    total: rows.length,
    open: rows.filter((r) => r.ar_status !== 'closed').length,
    closed: rows.filter((r) => r.ar_status === 'closed').length,
    balance: rows.reduce((s, r) => s + (Number(r.balance_after_deduct) || 0), 0),
  }
})

const invoiceListCount = computed(() => rows.value.length)

const outstandingCount = computed(() => outstandingRows.value.filter((r) => r.ar_status !== 'closed').length)

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
  let d = deliveries.value.find((x) => x.id === did)
  if (!d) {
    try {
      d = await getDelivery(did)
      if (d && !deliveries.value.some((x) => Number(x.id) === Number(d.id))) {
        deliveries.value = [...deliveries.value, d]
      }
    } catch {
      d = null
    }
  }
  if (d?.customer_id) {
    form.customer_id = d.customer_id
    const c = customers.value.find((x) => x.id === d.customer_id)
    form.customer_name = c?.name || d.customer_name || ''
  }
  if (!form.invoice_date) {
    form.invoice_date = toIsoDate(d?.delivery_date || new Date())
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

function resetCreateForm() {
  form.delivery_id = null
  form.customer_id = null
  form.po_id = null
  form.invoice_number = ''
  form.customer_name = ''
  form.invoice_date = ''
  form.due_date = ''
  form.total_amount = ''
  form.term_of_payment = ''
}

function openCreate() {
  resetCreateForm()
  formVisible.value = true
}

async function openCreateFromDelivery(deliveryId, amountRaw) {
  resetCreateForm()
  form.delivery_id = deliveryId
  form.invoice_date = toIsoDate(new Date())
  const amt = Number(amountRaw)
  if (Number.isFinite(amt) && amt > 0) form.total_amount = String(amt)
  formVisible.value = true
  await onDeliveryPick(deliveryId)
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
    tab.value = 'outstanding'
    await loadOutstanding()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

watch(
  () => [route.query.invoice_id, route.query.tab, route.query.delivery_id, route.query.amount, route.query.create],
  async () => {
    await applyRouteQuery()
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
