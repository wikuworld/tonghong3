<template>
  <AdminSection :title="t('pages.quotation.title')" :subtitle="t('pages.quotation.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        class="w-44"
        clearable
        :placeholder="t('pages.quotation.searchPlaceholder')"
        @keyup.enter="loadList"
      />
      <el-select v-model="filterCustomerId" clearable filterable class="w-52" :placeholder="t('common.customer')">
        <el-option v-for="c in customers" :key="c.id" :label="customerOptionLabel(c)" :value="c.id" />
      </el-select>
      <el-select v-model="filterStatus" clearable class="w-36" :placeholder="t('common.status')">
        <el-option :label="t('status.draft')" value="draft" />
        <el-option :label="t('pages.quotation.statusApproved')" value="approved" />
        <el-option :label="t('pages.quotation.statusCancelled')" value="cancelled" />
      </el-select>
      <el-date-picker
        v-model="filterDateFrom"
        type="date"
        value-format="YYYY-MM-DD"
        class="w-36"
        :placeholder="t('pages.quotation.filterDateFrom')"
        clearable
      />
      <el-date-picker
        v-model="filterDateTo"
        type="date"
        value-format="YYYY-MM-DD"
        class="w-36"
        :placeholder="t('pages.quotation.filterDateTo')"
        clearable
      />
      <el-button :icon="Refresh" :loading="loading" @click="loadList">{{ t('common.search') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-table
      :data="rows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="fixed"
      :empty-text="t('pages.quotation.tableEmpty')"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" fixed="left" />
      <el-table-column prop="quotation_number" :label="t('pages.quotation.colQuotationNo')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="customer_name" :label="t('pages.quotation.colCustomer')" min-width="160" show-overflow-tooltip />
      <el-table-column :label="t('pages.quotation.colDate')" width="110">
        <template #default="{ row }">{{ formatDate(row.quotation_date) }}</template>
      </el-table-column>
      <el-table-column prop="salesperson" :label="t('pages.quotation.colSalesperson')" width="110" show-overflow-tooltip />
      <el-table-column :label="t('pages.quotation.colTotal')" width="110" align="right">
        <template #default="{ row }">{{ formatNumber(row.total_amount, 2) }}</template>
      </el-table-column>
      <el-table-column :label="t('pages.quotation.colCurrency')" width="72" align="center">
        <template #default="{ row }">{{ row.currency || '—' }}</template>
      </el-table-column>
      <el-table-column :label="t('common.status')" width="100" fixed="right">
        <template #default="{ row }">
          <el-tag :type="quotationStatusType(row.status)" size="small">{{ quotationStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="120" fixed="right" align="center">
        <template #default="{ row }">
          <el-button :icon="View" link type="primary" @click="openDetail(row.id)" />
          <el-button v-if="canDelete" :icon="Delete" link type="danger" @click="confirmDelete(row)" />
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="createVisible" :title="t('pages.quotation.dialogCreate')" width="520px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('common.customer')" required>
          <el-select v-model="createForm.customer_id" filterable class="w-full" :placeholder="t('pages.quotation.pickCustomerWarning')">
            <el-option v-for="c in customers" :key="c.id" :label="customerOptionLabel(c)" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker v-model="createForm.quotation_date" type="date" value-format="YYYY-MM-DD" class="w-full" />
        </el-form-item>
        <el-form-item :label="t('pages.quotation.fieldCurrency')">
          <el-input v-model="createForm.currency" maxlength="3" class="w-32" />
        </el-form-item>
        <el-form-item :label="t('pages.quotation.fieldPaymentTerms')">
          <el-input v-model="createForm.payment_terms" maxlength="255" />
        </el-form-item>
        <el-form-item :label="t('pages.quotation.fieldValidUntil')">
          <el-date-picker v-model="createForm.valid_until" type="date" value-format="YYYY-MM-DD" class="w-full" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.quotation.fieldSalesperson')">
          <el-input v-model="createForm.salesperson" maxlength="100" />
        </el-form-item>
        <el-form-item :label="t('pages.quotation.fieldRemark')">
          <el-input v-model="createForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="createSaving" :disabled="!createForm.customer_id" @click="submitCreate">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailVisible"
      :title="detailTitle"
      width="960px"
      destroy-on-close
      align-center
      class="quotation-detail-dialog"
      @closed="onDetailClosed"
    >
      <div v-if="detailLoading" class="py-12 text-center text-slate-500">
        <el-icon class="is-loading text-2xl"><Loading /></el-icon>
        <p class="mt-2 text-sm">{{ t('common.loading') }}</p>
      </div>
      <template v-else-if="detailRow">
        <el-card shadow="never" class="mb-4">
          <template #header>
            <div class="flex items-center justify-between gap-2">
              <span class="font-semibold">{{ t('pages.quotation.headerSection') }}</span>
              <el-tag :type="quotationStatusType(detailRow.status)" size="small">{{ quotationStatusLabel(detailRow.status) }}</el-tag>
            </div>
          </template>
          <el-form v-if="canUpdate" label-position="top" class="quotation-header-form">
            <div class="flex flex-wrap gap-4">
              <el-form-item :label="t('common.customer')" class="min-w-[220px] flex-1">
                <el-select v-model="headerForm.customer_id" filterable class="w-full">
                  <el-option v-for="c in customers" :key="c.id" :label="customerOptionLabel(c)" :value="c.id" />
                </el-select>
              </el-form-item>
              <el-form-item :label="t('common.date')" class="w-44">
                <el-date-picker v-model="headerForm.quotation_date" type="date" value-format="YYYY-MM-DD" class="w-full" />
              </el-form-item>
              <el-form-item :label="t('pages.quotation.fieldCurrency')" class="w-28">
                <el-input v-model="headerForm.currency" maxlength="3" />
              </el-form-item>
              <el-form-item :label="t('common.status')" class="w-40">
                <el-select v-model="headerForm.status" class="w-full">
                  <el-option :label="t('status.draft')" value="draft" />
                  <el-option :label="t('pages.quotation.statusApproved')" value="approved" />
                  <el-option :label="t('pages.quotation.statusCancelled')" value="cancelled" />
                </el-select>
              </el-form-item>
            </div>
            <el-form-item :label="t('pages.quotation.fieldPaymentTerms')">
              <el-input v-model="headerForm.payment_terms" maxlength="255" />
            </el-form-item>
            <el-form-item :label="t('pages.quotation.fieldValidUntil')">
              <el-date-picker v-model="headerForm.valid_until" type="date" value-format="YYYY-MM-DD" class="w-full max-w-xs" clearable />
            </el-form-item>
            <el-form-item :label="t('pages.quotation.fieldSalesperson')">
              <el-input v-model="headerForm.salesperson" maxlength="100" />
            </el-form-item>
            <el-form-item :label="t('pages.quotation.fieldRemark')">
              <el-input v-model="headerForm.remark" type="textarea" :rows="2" />
            </el-form-item>
            <el-button type="primary" :loading="headerSaving" @click="saveHeader">{{ t('pages.quotation.saveHeader') }}</el-button>
          </el-form>
          <el-descriptions v-else :column="2" border size="small">
            <el-descriptions-item :label="t('pages.quotation.colQuotationNo')">{{ detailRow.quotation_number || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.customer')">{{ detailRow.customer_name || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.date')">{{ detailRow.quotation_date || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('pages.quotation.fieldCurrency')">{{ detailRow.currency || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('pages.quotation.fieldPaymentTerms')">{{ detailRow.payment_terms || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('pages.quotation.fieldValidUntil')">{{ detailRow.valid_until || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('pages.quotation.fieldSalesperson')">{{ detailRow.salesperson || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('pages.quotation.fieldRemark')">{{ detailRow.remark || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('pages.quotation.colTotal')">{{ formatNumber(detailRow.total_amount, 2) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <div class="mb-2 flex items-center justify-between">
          <h4 class="text-sm font-semibold text-slate-700">{{ t('pages.quotation.linesSection') }}</h4>
          <el-button v-if="canUpdate" type="primary" size="small" :icon="Plus" @click="openMaterialDialog">
            {{ t('pages.quotation.addLine') }}
          </el-button>
        </div>
        <el-table :data="detailLines" border size="small" max-height="360" :empty-text="t('pages.quotation.linesEmpty')">
          <el-table-column prop="line_no" :label="t('pages.quotation.colLineNo')" width="56" align="center" />
          <el-table-column prop="item_code" :label="t('pages.quotation.colItemCode')" width="110" show-overflow-tooltip />
          <el-table-column prop="description" :label="t('pages.quotation.colDescription')" min-width="140" show-overflow-tooltip />
          <el-table-column prop="color" :label="t('common.color')" width="90" show-overflow-tooltip />
          <el-table-column prop="specification" :label="t('pages.quotation.colSpec')" width="100" show-overflow-tooltip />
          <el-table-column :label="t('common.quantity')" width="100" align="right">
            <template #default="{ row }">
              <el-input v-if="canUpdate" v-model="row._edit_qty" size="small" class="!w-full" @blur="saveLine(row)" />
              <span v-else>{{ formatNumber(row.quantity, 2) }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.quotation.colUnit')" width="72">
            <template #default="{ row }">
              <el-input v-if="canUpdate" v-model="row._edit_unit" size="small" maxlength="16" @blur="saveLine(row)" />
              <span v-else>{{ row.unit || '—' }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.po.unitPriceUsd')" width="100" align="right">
            <template #default="{ row }">
              <el-input v-if="canUpdate" v-model="row._edit_price" size="small" class="!w-full" @blur="saveLine(row)" />
              <span v-else>{{ formatNumber(row.unit_price, 2) }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.quotation.colDiscount')" width="90" align="right">
            <template #default="{ row }">
              <el-input v-if="canUpdate" v-model="row._edit_disc" size="small" class="!w-full" @blur="saveLine(row)" />
              <span v-else>{{ formatNumber(row.discount_amount, 2) }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.quotation.colTaxRate')" width="72" align="right">
            <template #default="{ row }">
              <el-input v-if="canUpdate" v-model="row._edit_tax" size="small" class="!w-full" @blur="saveLine(row)" />
              <span v-else>{{ formatNumber(row.tax_rate, 2) }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.quotation.colLineAmount')" width="100" align="right">
            <template #default="{ row }">{{ formatNumber(row.line_amount, 2) }}</template>
          </el-table-column>
          <el-table-column v-if="canUpdate" :label="t('common.actions')" width="64" align="center" fixed="right">
            <template #default="{ row }">
              <el-button :icon="Delete" link type="danger" :loading="lineDeletingId === row.id" @click="removeLine(row)" />
            </template>
          </el-table-column>
        </el-table>
      </template>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('pages.delivery.closeDetail') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="materialVisible"
      :title="t('pages.quotation.pickMaterial')"
      width="720px"
      destroy-on-close
      align-center
    >
      <el-input v-model="materialSearch" class="mb-3" clearable :placeholder="t('pages.quotation.materialSearchPlaceholder')" />
      <el-table
        ref="materialTableRef"
        :data="filteredMasterItems"
        border
        size="small"
        max-height="380"
        @selection-change="onMaterialSelection"
      >
        <el-table-column type="selection" width="48" />
        <el-table-column prop="item_code" :label="t('pages.quotation.colItemCode')" width="120" />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="160" show-overflow-tooltip />
        <el-table-column prop="color" :label="t('common.color')" width="90" show-overflow-tooltip />
        <el-table-column prop="thickness_range" :label="t('common.thickness')" width="100" show-overflow-tooltip />
      </el-table>
      <template #footer>
        <el-button @click="materialVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="materialAdding" :disabled="!selectedMaterials.length" @click="confirmAddMaterials">
          {{ t('pages.po.addSelectedItems') }}
        </el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Loading, Plus, Refresh, View } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import { formatDate, formatNumber } from '../../utils/format'
import {
  addQuotationLine,
  createQuotation,
  deleteQuotation,
  deleteQuotationLine,
  getQuotation,
  listCustomers,
  listMasterItems,
  listQuotations,
  updateQuotation,
  updateQuotationLine,
} from '../../api/client'

const { t } = useI18n()

const canCreate = can('quotations', 'create')
const canUpdate = can('quotations', 'update')
const canDelete = can('quotations', 'delete')

const loading = ref(false)
const rows = ref([])
const customers = ref([])
const keyword = ref('')
const filterCustomerId = ref(null)
const filterStatus = ref('')
const filterDateFrom = ref('')
const filterDateTo = ref('')

const createVisible = ref(false)
const createSaving = ref(false)
const createForm = reactive({
  customer_id: null,
  quotation_date: '',
  currency: 'USD',
  payment_terms: '',
  valid_until: '',
  salesperson: '',
  remark: '',
})

const detailVisible = ref(false)
const detailLoading = ref(false)
const detailRow = ref(null)
const detailLines = ref([])
const headerSaving = ref(false)
const headerForm = reactive({
  customer_id: null,
  quotation_date: '',
  currency: 'USD',
  payment_terms: '',
  valid_until: '',
  salesperson: '',
  remark: '',
  status: 'draft',
})

const materialVisible = ref(false)
const materialSearch = ref('')
const masterItems = ref([])
const selectedMaterials = ref([])
const materialTableRef = ref(null)
const materialAdding = ref(false)
const lineDeletingId = ref(null)

const detailTitle = computed(() => {
  const n = detailRow.value?.quotation_number
  return n ? `${t('pages.quotation.dialogDetail')} — ${n}` : t('pages.quotation.dialogDetail')
})

const filteredMasterItems = computed(() => {
  const q = (materialSearch.value || '').trim().toLowerCase()
  if (!q) return masterItems.value
  return masterItems.value.filter((m) => {
    const parts = [m.item_code, m.material_name, m.color, m.thickness_range].filter(Boolean).join(' ').toLowerCase()
    return parts.includes(q)
  })
})

function customerOptionLabel(c) {
  const base = [c.code, c.name].filter(Boolean).join(` ${t('common.dashSeparator')} `)
  if (!base) return String(c.id)
  return c.city ? `${base} ${t('common.dotSeparator')} ${c.city}` : base
}

function quotationStatusType(s) {
  const x = (s || '').toLowerCase()
  if (x === 'approved') return 'success'
  if (x === 'cancelled') return 'danger'
  return 'info'
}

function quotationStatusLabel(s) {
  const x = (s || '').toLowerCase()
  if (x === 'draft') return t('status.draft')
  if (x === 'approved') return t('pages.quotation.statusApproved')
  if (x === 'cancelled') return t('pages.quotation.statusCancelled')
  return s || '—'
}

function toNum(v) {
  if (v === '' || v == null) return null
  const n = Number(v)
  return Number.isFinite(n) ? n : null
}

function decorateLine(row) {
  return {
    ...row,
    _edit_qty: row.quantity != null ? String(row.quantity) : '',
    _edit_unit: row.unit || 'S/F',
    _edit_price: row.unit_price != null ? String(row.unit_price) : '',
    _edit_disc: row.discount_amount != null ? String(row.discount_amount) : '0',
    _edit_tax: row.tax_rate != null ? String(row.tax_rate) : '0',
  }
}

function syncHeaderForm(h) {
  headerForm.customer_id = h.customer_id ?? null
  headerForm.quotation_date = h.quotation_date || ''
  headerForm.currency = h.currency || 'USD'
  headerForm.payment_terms = h.payment_terms || ''
  headerForm.valid_until = h.valid_until || ''
  headerForm.salesperson = h.salesperson || ''
  headerForm.remark = h.remark || ''
  headerForm.status = h.status || 'draft'
}

async function loadList() {
  loading.value = true
  try {
    const [list, cust] = await Promise.all([
      listQuotations({
        q: keyword.value,
        customer_id: filterCustomerId.value,
        status: filterStatus.value,
        date_from: filterDateFrom.value || undefined,
        date_to: filterDateTo.value || undefined,
      }),
      customers.value.length ? Promise.resolve(customers.value) : listCustomers(),
    ])
    rows.value = Array.isArray(list) ? list : []
    customers.value = cust
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function openCreate() {
  createForm.customer_id = null
  createForm.quotation_date = ''
  createForm.currency = 'USD'
  createForm.payment_terms = ''
  createForm.valid_until = ''
  createForm.salesperson = ''
  createForm.remark = ''
  createVisible.value = true
}

async function submitCreate() {
  if (!createForm.customer_id) {
    ElMessage.warning(t('pages.quotation.pickCustomerWarning'))
    return
  }
  createSaving.value = true
  try {
    const body = {
      customer_id: createForm.customer_id,
      quotation_date: createForm.quotation_date || undefined,
      currency: createForm.currency || 'USD',
      payment_terms: createForm.payment_terms.trim() || undefined,
      valid_until: createForm.valid_until || undefined,
      salesperson: createForm.salesperson.trim() || undefined,
      remark: createForm.remark.trim() || undefined,
    }
    const created = await createQuotation(body)
    createVisible.value = false
    ElMessage.success(t('pages.quotation.created'))
    await loadList()
    if (created?.id) await openDetail(created.id)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    createSaving.value = false
  }
}

async function openDetail(id) {
  detailVisible.value = true
  detailLoading.value = true
  detailRow.value = null
  detailLines.value = []
  try {
    const h = await getQuotation(id)
    detailRow.value = h
    const lines = Array.isArray(h.lines) ? h.lines : []
    detailLines.value = lines.map(decorateLine)
    syncHeaderForm(h)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    detailVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

function onDetailClosed() {
  detailRow.value = null
  detailLines.value = []
}

async function saveHeader() {
  if (!detailRow.value?.id) return
  headerSaving.value = true
  try {
    const body = {
      customer_id: headerForm.customer_id,
      quotation_date: headerForm.quotation_date || null,
      currency: headerForm.currency || 'USD',
      payment_terms: headerForm.payment_terms.trim() || null,
      valid_until: headerForm.valid_until || null,
      salesperson: headerForm.salesperson.trim() || null,
      remark: headerForm.remark.trim() || null,
      status: headerForm.status || 'draft',
    }
    const h = await updateQuotation(detailRow.value.id, body)
    detailRow.value = h
    detailLines.value = (Array.isArray(h.lines) ? h.lines : []).map(decorateLine)
    syncHeaderForm(h)
    ElMessage.success(t('pages.quotation.headerSaved'))
    await loadList()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    headerSaving.value = false
  }
}

async function saveLine(row) {
  if (!canUpdate || !row?.id) return
  try {
    const payload = {
      quantity: toNum(row._edit_qty),
      unit: (row._edit_unit || '').trim() || undefined,
      unit_price: toNum(row._edit_price),
      discount_amount: toNum(row._edit_disc) ?? 0,
      tax_rate: toNum(row._edit_tax) ?? 0,
    }
    const updated = await updateQuotationLine(row.id, payload)
    Object.assign(row, decorateLine(updated))
    const h = await getQuotation(detailRow.value.id)
    detailRow.value = h
    await loadList()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function removeLine(row) {
  if (!row?.id) return
  try {
    await ElMessageBox.confirm(t('pages.quotation.deleteLineConfirm'), t('common.confirm'), {
      type: 'warning',
      confirmButtonText: t('common.delete'),
      cancelButtonText: t('common.cancel'),
    })
  } catch {
    return
  }
  lineDeletingId.value = row.id
  try {
    await deleteQuotationLine(row.id)
    ElMessage.success(t('pages.quotation.lineDeleted'))
    const h = await getQuotation(detailRow.value.id)
    detailRow.value = h
    detailLines.value = (Array.isArray(h.lines) ? h.lines : []).map(decorateLine)
    await loadList()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    lineDeletingId.value = null
  }
}

async function openMaterialDialog() {
  if (!detailRow.value?.id) return
  materialSearch.value = ''
  selectedMaterials.value = []
  materialVisible.value = true
  try {
    masterItems.value = await listMasterItems()
    await nextTick()
    materialTableRef.value?.clearSelection?.()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function onMaterialSelection(sel) {
  selectedMaterials.value = sel
}

async function confirmAddMaterials() {
  if (!detailRow.value?.id || !selectedMaterials.value.length) return
  materialAdding.value = true
  try {
    for (const m of selectedMaterials.value) {
      await addQuotationLine(detailRow.value.id, {
        master_item_id: m.id,
        quantity: 1,
        unit: 'S/F',
        unit_price: null,
        discount_amount: 0,
        tax_rate: 0,
      })
    }
    ElMessage.success(t('pages.quotation.linesAdded', { count: selectedMaterials.value.length }))
    materialVisible.value = false
    const h = await getQuotation(detailRow.value.id)
    detailRow.value = h
    detailLines.value = (Array.isArray(h.lines) ? h.lines : []).map(decorateLine)
    await loadList()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    materialAdding.value = false
  }
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(
      t('pages.quotation.deleteQuotationConfirm', { no: row.quotation_number || row.id }),
      t('pages.quotation.deleteQuotationTitle'),
      { type: 'warning', confirmButtonText: t('common.delete'), cancelButtonText: t('common.cancel') },
    )
  } catch {
    return
  }
  try {
    await deleteQuotation(row.id)
    ElMessage.success(t('pages.quotation.deleted'))
    if (detailRow.value?.id === row.id) detailVisible.value = false
    await loadList()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

onMounted(() => {
  loadList()
})
</script>
