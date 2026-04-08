<template>
  <AdminSection :title="t('pages.po.title')" :subtitle="t('pages.po.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.po.searchPlaceholder')"
        clearable
        class="po-toolbar-search"
      />
      <el-button :icon="Download" @click="openExportHint">{{ t('common.export') }}</el-button>
      <el-button v-if="canManage" type="primary" :icon="Plus" :loading="loading" @click="openCreateDialog">{{ t('common.create') }}</el-button>
    </template>

    <div class="filter-panel mb-4">
      <p class="filter-panel__title">{{ t('common.filter') }}</p>
      <el-form class="filter-form" label-position="top">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :md="9" :lg="7">
            <el-form-item :label="t('common.customer')">
              <el-select
                v-model="filterCustomerId"
                clearable
                filterable
                class="w-full"
                :placeholder="t('common.placeholder.customer')"
              >
                <el-option
                  v-for="c in customers"
                  :key="c.id"
                  :label="customerOptionLabel(c)"
                  :value="c.id"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="12" :md="7" :lg="5">
            <el-form-item :label="t('common.status')">
              <el-select v-model="filterStatus" clearable class="w-full" :placeholder="t('common.status')">
                <el-option :label="t('status.draft')" value="draft" />
                <el-option :label="t('status.confirmed')" value="confirmed" />
                <el-option :label="t('status.production')" value="production" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="8" :lg="6" class="po-filter-action-col">
            <el-form-item label="&nbsp;">
              <el-button class="w-full" @click="resetFilter">{{ t('common.reset') }}</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <el-table
      :data="filteredRows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="auto"
      :empty-text="t('pages.po.tableEmpty')"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="po_number" :label="t('common.poNo')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="customerName" :label="t('common.customer')" min-width="200" show-overflow-tooltip />
      <el-table-column prop="buyer" :label="t('common.buyer')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="material_hint" :label="t('common.material')" min-width="140" show-overflow-tooltip />
      <el-table-column prop="po_category" :label="t('common.category')" min-width="110" align="center">
        <template #default="{ row }">
          <el-tag size="small" type="info" effect="plain">{{ t(`status.${row.po_category}`) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="etd" :label="t('common.etd')" min-width="110" align="center" />
      <el-table-column prop="mkt_workflow_stage" :label="t('pages.po.mktFlow')" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.mkt_workflow_stage || t('common.emptyValue') }}</template>
      </el-table-column>
      <el-table-column prop="status" :label="t('common.status')" min-width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ t(`status.${row.status}`) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="168" align="center" fixed="right">
        <template #default="{ row }">
          <div class="po-row-actions">
            <el-tooltip :content="t('common.detail')" placement="top">
              <el-button :icon="View" link type="primary" @click="openDetailDialog(row)" />
            </el-tooltip>
            <el-tooltip v-if="canManage" :content="t('common.edit')" placement="top">
              <el-button :icon="EditPen" link type="warning" @click="openEditDialog(row)" />
            </el-tooltip>
            <el-tooltip :content="t('common.print')" placement="top">
              <el-button :icon="Printer" link @click="openPrintDialog(row)" />
            </el-tooltip>
            <el-tooltip v-if="canManage" :content="t('common.delete')" placement="top">
              <el-button :icon="Delete" link type="danger" @click="removeRow(row)" />
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="formDialogVisible"
      :title="isEditMode ? `${t('pages.poEntry.title')} ${t('pages.po.editSuffix')}` : t('pages.poEntry.title')"
      width="1100px"
      destroy-on-close
      align-center
      class="po-dialog"
    >
      <el-form label-position="top" class="po-dialog-form">
        <el-divider content-position="left">{{ t('pages.po.customerSoSection') }}</el-divider>
        <el-row :gutter="12">
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.customer')" required>
              <el-select
                v-model="formModel.customer_id"
                filterable
                clearable
                class="w-full"
                :placeholder="t('common.placeholder.customer')"
                @change="onCustomerChange"
              >
                <el-option
                  v-for="c in customers"
                  :key="c.id"
                  :label="customerOptionLabel(c)"
                  :value="c.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.poNo')">
              <el-input v-model="formModel.po_number" :placeholder="t('common.placeholder.poNumber')" clearable />
              <span class="text-xs text-slate-500">{{ t('pages.po.autoGenerateHint') }}</span>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.po.brand')">
              <el-select v-model="formModel.brand_id" clearable filterable class="w-full" :placeholder="t('pages.po.brand')">
                <el-option
                  v-for="b in brandsFiltered"
                  :key="b.id"
                  :label="`${b.code || b.id} — ${b.name || ''}`"
                  :value="b.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="`${t('menu.customs')} (${t('common.aju')})`">
              <el-select
                v-model="formModel.customs_declaration_id"
                clearable
                filterable
                class="w-full"
                :placeholder="t('pages.po.customsPlaceholder')"
              >
                <el-option
                  v-for="d in customsList"
                  :key="d.id"
                  :label="`${d.nomor_aju || d.id} · ${d.kode_dokumen || ''}`"
                  :value="d.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.poCategory')">
              <el-select v-model="formModel.po_category" class="w-full" :placeholder="t('common.category')">
                <el-option :label="t('status.production')" value="production" />
                <el-option :label="t('status.sample')" value="sample" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.orderDate')">
              <el-date-picker v-model="formModel.order_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.buyer')">
              <el-select
                v-model="formModel.buyer"
                filterable
                allow-create
                default-first-option
                class="w-full"
                :placeholder="t('common.placeholder.buyer')"
              >
                <el-option v-for="b in buyerCodes" :key="b" :label="b" :value="b" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.etd')">
              <el-date-picker v-model="formModel.etd" type="date" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.status')">
              <el-select v-model="formModel.status" class="w-full">
                <el-option :label="t('status.draft')" value="draft" />
                <el-option :label="t('status.confirmed')" value="confirmed" />
                <el-option :label="t('status.production')" value="production" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-form-item :label="t('common.remark')">
              <el-input v-model="formModel.remark" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-divider content-position="left">{{ t('pages.po.materialFollowUpSection') }}</el-divider>
          </el-col>
          <el-col :xs="24" :md="18">
            <el-form-item :label="t('pages.po.materialFollowUpNote')">
              <el-input
                v-model="formModel.material_followup_remark"
                type="textarea"
                :rows="2"
                :placeholder="t('pages.po.materialFollowUpPlaceholder')"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item :label="t('pages.po.done')">
              <el-switch v-model="formModel.material_followup_done" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">{{ t('pages.po.materialLineOne') }}</el-divider>
        <el-row :gutter="12">
          <el-col :xs="24" :md="12">
            <el-form-item :label="`${t('common.material')} (${t('common.masterLabel')})`">
              <el-select
                v-model="formModel.master_item_id"
                clearable
                filterable
                class="w-full"
                :placeholder="t('pages.po.masterItemPlaceholder')"
              >
                <el-option
                  v-for="it in masterItems"
                  :key="it.id"
                  :label="`${it.item_code} — ${it.material_name || ''}`"
                  :value="it.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.material')">
              <el-input v-model="formModel.material_name" :placeholder="t('common.placeholder.material')" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.thickness')">
              <el-input v-model="formModel.thickness_text" :placeholder="t('common.placeholder.thickness')" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.color')">
              <el-input v-model="formModel.color" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.softness')">
              <el-input v-model="formModel.softness" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.colorReference')">
              <el-input v-model="formModel.color_reference" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.backing')">
              <el-input v-model="formModel.backing" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.quantityOrder')">
              <el-input v-model="formModel.quantity_order" type="number" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.styleArticle')">
              <el-input v-model="formModel.style_article" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.model')">
              <el-input v-model="formModel.model" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <div class="po-dialog-footer">
          <el-button @click="formDialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button v-if="canManage" type="primary" :loading="saving" @click="submitForm">{{ t('common.savePo') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailDialogVisible"
      :title="t('pages.poDetail.title')"
      width="900px"
      destroy-on-close
      align-center
      class="po-dialog"
    >
      <el-descriptions v-if="detailView" :column="2" border size="small">
        <el-descriptions-item :label="t('common.poNo')">{{ detailView.po_number }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.status')">{{ statusLabel(detailView.status) }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.customer')">{{ detailView.customerName }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.buyer')">{{ detailView.buyer || t('common.emptyValue') }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.etd')">{{ detailView.etd || t('common.emptyValue') }}</el-descriptions-item>
        <el-descriptions-item :label="t('menu.customs')">{{ detailView.customs_declaration_id || t('common.emptyValue') }}</el-descriptions-item>
      </el-descriptions>
      <el-table
        v-if="detailLines.length"
        :data="detailLines"
        class="mt-4"
        border
        size="small"
        table-layout="auto"
        max-height="360"
      >
        <el-table-column prop="material_name" :label="t('common.material')" min-width="140" />
        <el-table-column prop="thickness_text" :label="t('common.thickness')" width="120" />
        <el-table-column prop="color" :label="t('common.color')" width="100" />
        <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="100" />
      </el-table>
      <div v-if="detailAudit.length" class="mt-4 rounded border border-slate-200 bg-white p-3">
        <div class="mb-2 text-sm font-semibold text-slate-700">{{ t('pages.poDetail.revisionHistory') }}</div>
        <el-timeline>
          <el-timeline-item
            v-for="a in detailAudit"
            :key="a.id"
            :timestamp="a.created_at ? String(a.created_at).replace('T', ' ').slice(0, 19) : ''"
          >
            <div class="text-sm">
              <b>{{ a.action }}</b>
              <span class="text-slate-500"> {{ t('common.dashSeparator') }} {{ a.actor || t('common.system') }}</span>
            </div>
            <div v-if="a.before || a.after" class="mt-1 text-xs text-slate-600">
              <pre class="whitespace-pre-wrap break-words">{{ prettyAudit(a) }}</pre>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
      <template #footer>
        <el-button type="primary" @click="detailDialogVisible = false">{{ t('pages.customers.closeDetail') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="printDialogVisible"
      :title="`${t('common.print')} ${t('menu.po')}`"
      width="760px"
      destroy-on-close
      align-center
      class="po-dialog"
    >
      <div class="rounded border border-slate-200 p-4">
        <h3 class="mb-2 text-lg font-semibold">{{ selectedRow.po_number }}</h3>
        <p><b>{{ t('common.customer') }}:</b> {{ selectedRow.customerName }}</p>
        <p><b>{{ t('common.buyer') }}:</b> {{ selectedRow.buyer }}</p>
        <p><b>{{ t('common.poCategory') }}:</b> {{ statusLabel(selectedRow.po_category) }}</p>
        <p><b>{{ t('common.material') }}:</b> {{ selectedRow.material_hint }}</p>
        <p><b>{{ t('common.etd') }}:</b> {{ selectedRow.etd }}</p>
      </div>
      <template #footer>
        <div class="po-dialog-footer">
          <el-button @click="printDialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :icon="Printer" @click="printPage">{{ t('common.print') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Download, View, EditPen, Delete, Printer } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { canWrite } from '../../security/permissions'
import {
  addPoDetail,
  createPo,
  deletePo,
  listBrands,
  listBuyerPriceLists,
  listCustomsDeclarations,
  listCustomers,
  listMasterItems,
  listPo,
  listPoDetails,
  listAuditLogs,
  toIsoDate,
  updatePo,
  updatePoDetail,
} from '../../api/client'

const { t } = useI18n()
const route = useRoute()
const canManage = canWrite('po')

const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const filterCustomerId = ref(null)
const filterStatus = ref('')
const customers = ref([])
const brands = ref([])
const customsList = ref([])
const masterItems = ref([])
const buyerCodes = ref(['NB', 'ADIDAS', 'NIKE', 'UA'])

const rows = ref([])

const customerName = (id) => {
  const c = customers.value.find((x) => x.id === id)
  return c ? `${c.code || ''} ${c.name || ''}`.trim() : t('common.emptyValue')
}

function customerOptionLabel(c) {
  const base = [c.code, c.name].filter(Boolean).join(' — ')
  if (!base) return String(c.id)
  return c.city ? `${base} ${t('common.dotSeparator')} ${c.city}` : base
}

async function enrichPoRows(headers) {
  const detailsLists = await Promise.all(
    headers.map((h) => listPoDetails(h.id).catch(() => [])),
  )
  return headers.map((h, i) => {
    const first = detailsLists[i][0] || {}
    return {
      ...h,
      customerName: customerName(h.customer_id),
      material_hint: first.material_name || t('common.emptyValue'),
      etd: h.etd ? String(h.etd).slice(0, 10) : '',
    }
  })
}

async function load() {
  loading.value = true
  try {
    const [cust, br, cu, mi, bpl, pos] = await Promise.all([
      listCustomers(),
      listBrands(),
      listCustomsDeclarations(),
      listMasterItems(),
      listBuyerPriceLists().catch(() => []),
      listPo(),
    ])
    customers.value = cust
    brands.value = br
    customsList.value = cu
    masterItems.value = mi
    const extraBuyers = [...new Set(bpl.map((x) => x.buyer_code).filter(Boolean))]
    buyerCodes.value = [...new Set([...buyerCodes.value, ...extraBuyers])]
    rows.value = await enrichPoRows(pos)
  } catch (e) {
    ElMessage.error(e.message || t('pages.po.loadFailed'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await load()
  const poIdRaw = route.query.po_id
  const poId = Number(poIdRaw)
  if (!Number.isNaN(poId) && poId > 0) {
    const target = rows.value.find((r) => Number(r.id) === poId)
    if (target) await openDetailDialog(target)
  }
})

const brandsFiltered = computed(() => {
  const cid = formModel.customer_id
  if (!cid) return brands.value
  return brands.value.filter((b) => !b.customer_id || b.customer_id === cid)
})

const filteredRows = computed(() =>
  rows.value.filter((row) => {
    const customerMatch = !filterCustomerId.value || row.customer_id === filterCustomerId.value
    const statusMatch = !filterStatus.value || row.status === filterStatus.value
    const q = keyword.value.trim().toLowerCase()
    const keywordMatch =
      !q ||
      [row.po_number, row.customerName, row.buyer, row.material_hint]
        .join(' ')
        .toLowerCase()
        .includes(q)
    return customerMatch && statusMatch && keywordMatch
  }),
)

const resetFilter = () => {
  filterCustomerId.value = null
  filterStatus.value = ''
  keyword.value = ''
}

const statusType = (status) => {
  if (status === 'confirmed') return 'success'
  if (status === 'production') return 'warning'
  return 'info'
}

const statusLabel = (status) => (status ? t(`status.${status}`) : t('common.emptyValue'))

const formDialogVisible = ref(false)
const isEditMode = ref(false)
const editingPoId = ref(null)
const editingDetailId = ref(null)

const formModel = reactive({
  po_number: '',
  customer_id: null,
  brand_id: null,
  customs_declaration_id: null,
  po_category: 'production',
  order_date: '',
  buyer: '',
  etd: '',
  remark: '',
  status: 'draft',
  master_item_id: null,
  material_name: '',
  thickness_text: '',
  color: '',
  softness: '',
  color_reference: '',
  backing: '',
  quantity_order: '',
  style_article: '',
  model: '',
  material_followup_remark: '',
  material_followup_done: false,
})

function resetForm() {
  formModel.po_number = ''
  formModel.customer_id = null
  formModel.brand_id = null
  formModel.customs_declaration_id = null
  formModel.po_category = 'production'
  formModel.order_date = ''
  formModel.buyer = ''
  formModel.etd = ''
  formModel.remark = ''
  formModel.status = 'draft'
  formModel.master_item_id = null
  formModel.material_name = ''
  formModel.thickness_text = ''
  formModel.color = ''
  formModel.softness = ''
  formModel.color_reference = ''
  formModel.backing = ''
  formModel.quantity_order = ''
  formModel.style_article = ''
  formModel.model = ''
  formModel.material_followup_remark = ''
  formModel.material_followup_done = false
  editingPoId.value = null
  editingDetailId.value = null
}

function onCustomerChange() {
  formModel.brand_id = null
}

const openCreateDialog = () => {
  isEditMode.value = false
  resetForm()
  formDialogVisible.value = true
}

const openEditDialog = async (row) => {
  isEditMode.value = true
  editingPoId.value = row.id
  resetForm()
  formModel.po_number = row.po_number || ''
  formModel.customer_id = row.customer_id
  formModel.brand_id = row.brand_id ?? null
  formModel.customs_declaration_id = row.customs_declaration_id ?? null
  formModel.po_category = row.po_category || 'production'
  formModel.order_date = row.order_date ? String(row.order_date).slice(0, 10) : ''
  formModel.buyer = row.buyer || ''
  formModel.etd = row.etd ? String(row.etd).slice(0, 10) : ''
  formModel.remark = row.remark || ''
  formModel.status = row.status || 'draft'
  formModel.material_followup_remark = row.material_followup_remark || ''
  formModel.material_followup_done = Boolean(row.material_followup_done)
  try {
    const details = await listPoDetails(row.id)
    const d0 = details[0]
    if (d0) {
      editingDetailId.value = d0.id
      formModel.master_item_id = d0.master_item_id
      formModel.material_name = d0.material_name || ''
      formModel.thickness_text = d0.thickness_text || ''
      formModel.color = d0.color || ''
      formModel.softness = d0.softness || ''
      formModel.color_reference = d0.color_reference || ''
      formModel.backing = d0.backing || ''
      formModel.quantity_order = d0.quantity_order != null ? String(d0.quantity_order) : ''
      formModel.style_article = d0.style_article || ''
      formModel.model = d0.model || ''
    }
  } catch {
    editingDetailId.value = null
  }
  formDialogVisible.value = true
}

const submitForm = async () => {
  if (!formModel.customer_id) {
    ElMessage.warning(t('pages.po.pickCustomerWarning'))
    return
  }
  saving.value = true
  try {
    const header = {
      po_number: formModel.po_number?.trim() || undefined,
      customer_id: formModel.customer_id,
      brand_id: formModel.brand_id || undefined,
      customs_declaration_id: formModel.customs_declaration_id || undefined,
      buyer: formModel.buyer || undefined,
      po_category: formModel.po_category,
      order_date: toIsoDate(formModel.order_date) || undefined,
      etd: toIsoDate(formModel.etd) || undefined,
      remark: formModel.remark || undefined,
      status: formModel.status,
      material_followup_remark: formModel.material_followup_remark || undefined,
      material_followup_done: formModel.material_followup_done,
    }
    const detailBody = {
      master_item_id: formModel.master_item_id || undefined,
      material_name: formModel.material_name || undefined,
      thickness_text: formModel.thickness_text || undefined,
      color: formModel.color || undefined,
      softness: formModel.softness || undefined,
      color_reference: formModel.color_reference || undefined,
      backing: formModel.backing || undefined,
      quantity_order: formModel.quantity_order ? Number(formModel.quantity_order) : undefined,
      style_article: formModel.style_article || undefined,
      model: formModel.model || undefined,
      line_etd: toIsoDate(formModel.etd) || undefined,
    }

    if (isEditMode.value && editingPoId.value) {
      await updatePo(editingPoId.value, header)
      if (editingDetailId.value) {
        await updatePoDetail(editingDetailId.value, detailBody)
      } else {
        await addPoDetail(editingPoId.value, detailBody)
      }
    } else {
      const created = await createPo(header)
      await addPoDetail(created.id, detailBody)
    }
    ElMessage.success(t('pages.customers.saved'))
    formDialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

const detailDialogVisible = ref(false)
const detailView = ref(null)
const detailLines = ref([])
const detailAudit = ref([])

const openDetailDialog = async (row) => {
  detailView.value = { ...row, customerName: row.customerName }
  detailLines.value = []
  detailAudit.value = []
  try {
    detailLines.value = await listPoDetails(row.id)
  } catch {
    detailLines.value = []
  }
  try {
    detailAudit.value = await listAuditLogs({ entity_type: 'sales_order', entity_id: row.id, limit: 100 })
  } catch {
    detailAudit.value = []
  }
  detailDialogVisible.value = true
}

function prettyAudit(a) {
  const b = a.before ? JSON.stringify(a.before, null, 2) : ''
  const af = a.after ? JSON.stringify(a.after, null, 2) : ''
  if (b && af) return `${t('common.beforeLabel')}:\\n${b}\\n\\n${t('common.afterLabel')}:\\n${af}`
  return b || af || ''
}

const printDialogVisible = ref(false)
const selectedRow = reactive({})

const openPrintDialog = (row) => {
  Object.assign(selectedRow, row)
  printDialogVisible.value = true
}

const printPage = () => window.print()

const removeRow = async (row) => {
  try {
    await ElMessageBox.confirm(
      t('pages.po.deleteConfirm', { poNumber: row.po_number }),
      t('pages.po.deleteTitle'),
      {
        type: 'warning',
        distinguishCancelAndClose: true,
        confirmButtonText: t('common.delete'),
        cancelButtonText: t('common.cancel'),
      },
    )
    await deletePo(row.id)
    ElMessage.success(t('pages.po.deleted'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function openExportHint() {
  ElMessage.info(t('pages.po.exportHint'))
}
</script>

<style scoped>
.admin-table {
  width: 100%;
}

.po-row-actions {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 2px 4px;
}

.po-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

</style>
