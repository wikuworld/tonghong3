<template>
  <AdminSection :title="t('pages.delivery.title')" :subtitle="t('pages.delivery.subtitle')">
    <template #actions>
      <el-input v-model="keyword" :placeholder="t('pages.delivery.listSearchPlaceholder')" clearable class="delivery-toolbar-search" />
      <el-select v-model="statusFilter" clearable :placeholder="t('common.status')" class="w-32">
        <el-option label="Draft" value="draft" />
        <el-option label="Sent" value="sent" />
      </el-select>
      <el-button :icon="Download" :loading="exporting" @click="downloadDeliveryExcel">{{ t('pages.delivery.downloadExcel') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" :loading="loading" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-card shadow="never" class="mb-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-slate-800">{{ t('pages.delivery.listSheetTitle') }}</h3>
          <p class="text-sm text-slate-500 mt-1">
            {{ t('pages.delivery.flowInfo') }}
          </p>
        </div>
        <div class="flex items-center gap-4">
          <div class="text-right">
            <p class="text-2xl font-bold text-slate-700">{{ filteredRows.length }}</p>
            <p class="text-xs text-slate-500">{{ t('common.total') }}</p>
          </div>
        </div>
      </div>
    </el-card>

    <el-table
      :data="filteredRows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="fixed"
      :empty-text="t('pages.delivery.tableEmpty')"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="50" align="center" fixed="left" />
      <el-table-column prop="surat_jalan_no" :label="t('pages.delivery.columns.noSj')" min-width="130" show-overflow-tooltip />
      <el-table-column :label="t('pages.delivery.columns.shipDate')" width="100">
        <template #default="{ row }">{{ formatDate(row.delivery_date) }}</template>
      </el-table-column>
      <el-table-column prop="factory_name" :label="t('pages.delivery.columns.factory')" min-width="150" show-overflow-tooltip />
      <el-table-column prop="po_number" :label="t('pages.delivery.columns.poNumber')" min-width="130" show-overflow-tooltip />
      <el-table-column prop="buyer" :label="t('pages.delivery.columns.buyer')" width="90" show-overflow-tooltip />
      <el-table-column prop="lot_no" :label="t('pages.delivery.columns.lotNo')" width="100" show-overflow-tooltip />
      <el-table-column prop="material_name" :label="t('pages.delivery.columns.materialName')" min-width="140" show-overflow-tooltip />
      <el-table-column :label="t('pages.delivery.columns.sf')" width="80" align="right">
        <template #default="{ row }">{{ formatNumber(row.qty_sf, 2) }}</template>
      </el-table-column>
      <el-table-column prop="qty_roll" :label="t('pages.delivery.columns.roll')" width="60" align="right" />
      <el-table-column prop="qty_pcs" :label="t('pages.delivery.columns.pcs')" width="60" align="right" />
      <el-table-column :label="t('pages.delivery.columns.nw')" width="70" align="right">
        <template #default="{ row }">{{ formatNumber(row.net_weight, 2) }}</template>
      </el-table-column>
      <el-table-column :label="t('pages.delivery.columns.amount')" width="100" align="right">
        <template #default="{ row }">{{ formatNumber(row.amount, 0) }}</template>
      </el-table-column>
      <el-table-column :label="t('pages.delivery.columns.status')" width="90" fixed="right">
        <template #default="{ row }">
          <el-tag :type="statusType(row.delivery_status)" size="small">
            {{ statusLabel(row.delivery_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="70" fixed="right" align="center">
        <template #default="{ row }">
          <el-button :icon="View" link type="primary" @click="openDetailFromLine(row)" />
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="formVisible" :title="`${t('common.create')} ${t('menu.delivery')}`" width="560px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('common.customer')" required>
          <el-select v-model="form.customer_id" filterable class="w-full">
            <el-option
              v-for="c in customers"
              :key="c.id"
              :label="customerOptionLabel(c)"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.delivery.packingRequiredLabel')" required>
          <el-select v-model="form.packing_id" filterable class="w-full" :placeholder="t('pages.delivery.pickDonePacking')">
            <el-option
              v-for="p in packingsDone"
              :key="p.id"
              :label="`${p.packing_number || p.id} (${p.status})`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker v-model="form.delivery_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('common.vehicle')">
          <el-input v-model="form.vehicle_number" />
        </el-form-item>
        <el-form-item :label="t('common.driver')">
          <el-input v-model="form.driver_name" />
        </el-form-item>
        <el-form-item :label="t('common.status')">
          <el-select v-model="form.status" class="w-full" disabled>
            <el-option :label="t('status.draft')" value="draft" />
          </el-select>
          <span class="mt-1 block text-xs text-slate-500">{{ t('pages.delivery.markSentHint') }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="delivery-dialog-footer">
          <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button v-if="canCreate" type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailVisible"
      :title="t('pages.delivery.dialogDetail')"
      width="720px"
      destroy-on-close
      align-center
      @closed="resetDetail"
    >
      <div v-if="detailLoading" class="py-12 text-center">
        <el-icon class="is-loading text-2xl text-blue-500"><Loading /></el-icon>
        <p class="mt-2 text-sm text-slate-500">{{ t('common.loading') }}...</p>
      </div>
      <template v-else-if="detailRow">
        <el-card class="mb-4" shadow="never">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="font-semibold">{{ t('pages.delivery.basicInfo') }}</span>
              <el-tag :type="statusType(detailRow.status)" size="small">{{ statusLabel(detailRow.status) }}</el-tag>
            </div>
          </template>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item :label="t('common.deliveryNo')">{{ detailRow.delivery_number || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.customer')">{{ detailRow.customer_name || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.date')">{{ detailRow.delivery_date || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.vehicle')">{{ detailRow.vehicle_number || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.driver')">{{ detailRow.driver_name || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.destination')">{{ detailRow.destination || '—' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="mb-4" shadow="never" v-if="canUpdate">
          <template #header>
            <span class="font-semibold">{{ t('pages.delivery.customsInfo') }}</span>
          </template>
          <div class="grid grid-cols-2 gap-4">
            <el-form-item :label="t('pages.delivery.bcNumberEdit')" class="mb-0">
              <el-input v-model="bcForm.bc_number" clearable maxlength="80" />
            </el-form-item>
            <el-form-item :label="t('pages.delivery.bcDateEdit')" class="mb-0">
              <el-date-picker v-model="bcForm.bc_date" type="date" value-format="YYYY-MM-DD" class="w-full" clearable />
            </el-form-item>
          </div>
          <div class="mt-3">
            <el-button type="primary" plain :loading="bcSaving" size="small" @click="saveBcFields">{{ t('pages.delivery.saveBcFields') }}</el-button>
          </div>
        </el-card>

        <div class="mb-4">
          <div class="mb-2 flex items-center justify-between">
            <h4 class="text-sm font-semibold text-slate-700">{{ t('pages.delivery.deliveryLines') }} ({{ detailLines.length }})</h4>
            <el-button
              v-if="canUpdate"
              type="primary"
              size="small"
              :disabled="isSentOrCancelled || detailLines.length === 0"
              :loading="markingSent"
              @click="markSent"
            >
              {{ t('pages.delivery.markSent') }}
            </el-button>
          </div>
          <el-table :data="detailLines" border size="small" :empty-text="t('pages.delivery.linesEmpty')">
            <el-table-column type="index" :label="t('common.noLabel')" width="50" align="center" />
            <el-table-column prop="production_detail_id" :label="t('pages.delivery.productionDetailId')" min-width="120">
              <template #default="{ row }">#{{ row.production_detail_id }}</template>
            </el-table-column>
            <el-table-column prop="qty" :label="t('common.quantity')" min-width="100" align="right">
              <template #default="{ row }">{{ formatNumber(row.qty, 2) }}</template>
            </el-table-column>
            <el-table-column prop="qty_roll" :label="t('pages.delivery.roll')" width="80" align="right" />
            <el-table-column prop="qty_pcs" :label="t('pages.delivery.pcs')" width="80" align="right" />
            <el-table-column prop="weight" :label="t('pages.delivery.weight')" width="100" align="right">
              <template #default="{ row }">{{ formatNumber(row.weight, 2) }}</template>
            </el-table-column>
          </el-table>
          <p v-if="detailLines.length === 0" class="mt-2 text-xs text-amber-600">{{ t('pages.delivery.needAtLeastOneLine') }}</p>
        </div>

        <div class="flex gap-3">
          <el-button v-if="canPrint" type="default" @click="openSjPrint">{{ t('pages.delivery.printSj') }}</el-button>
          <el-button v-if="canPrint" type="default" @click="downloadSjPdf">{{ t('pages.delivery.downloadPdf') }}</el-button>
          <el-button v-if="canUpdate" type="success" plain :loading="markingSj" @click="markSjPrinted">{{ t('pages.delivery.markSjPrinted') }}</el-button>
        </div>

        <el-card v-if="canUpdate" class="mt-4" shadow="never">
          <template #header>
            <span class="font-semibold">{{ t('pages.delivery.addLineLabel') }}</span>
          </template>
          <div v-if="prodDetailsLoading" class="py-4 text-center">
            <el-icon class="is-loading"><Loading /></el-icon> {{ t('common.loading') }}
          </div>
          <template v-else-if="candidateProdDetails.length">
            <div class="grid grid-cols-2 gap-4">
              <el-form-item :label="t('pages.delivery.productionDetailPlaceholder')" class="mb-0">
                <el-select v-model="lineForm.production_detail_id" filterable clearable class="w-full" :placeholder="t('pages.delivery.productionDetailPlaceholder')">
                  <el-option
                    v-for="pd in candidateProdDetails"
                    :key="pd.id"
                    :label="`#${pd.id} ${t('common.dotSeparator')} ${t('common.actual').toLowerCase()} ${pd.qty_actual ?? t('common.emptyValue')}`"
                    :value="pd.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item :label="t('common.quantity')" class="mb-0">
                <el-input v-model="lineForm.qty" type="number" step="0.01" />
              </el-form-item>
            </div>
            <div class="mt-3">
              <el-button type="primary" :loading="addingLine" @click="addLine">{{ t('pages.delivery.addToDelivery') }}</el-button>
            </div>
          </template>
          <p v-else class="text-sm text-slate-500">{{ t('pages.delivery.noProductionLines') }}</p>
        </el-card>
      </template>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('pages.delivery.closeDetail') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, View, Van, Document, Download, Loading } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import { formatDate, formatNumber, statusType, statusLabel } from '../../utils/format'
import {
  addDeliveryDetail,
  createDelivery,
  fetchAuthenticatedDocument,
  getDelivery,
  getPacking,
  listCustomers,
  listDeliveryDetails,
  listMarketingDeliveryLines,
  listPacking,
  listProductionDetails,
  markSuratJalanPrinted,
  marketingDeliveryXlsxPath,
  toIsoDate,
  updateDelivery,
} from '../../api/client'

const { t } = useI18n()
const canCreate = can('delivery', 'create')
const canUpdate = can('delivery', 'update')
const canPrint = can('delivery', 'print')
const route = useRoute()
const loading = ref(false)
const saving = ref(false)
const exporting = ref(false)
const keyword = ref('')
const statusFilter = ref('')
const lineRows = ref([])
const customers = ref([])
const packings = ref([])

const packingsDone = computed(() =>
  (packings.value || []).filter((p) => (p.status || '').toLowerCase() === 'done'),
)

function custName(id) {
  const c = customers.value.find((x) => x.id === id)
  return c ? `${c.name}` : t('common.emptyValue')
}

function customerOptionLabel(c) {
  const base = [c.code, c.name].filter(Boolean).join(` ${t('common.dashSeparator')} `)
  if (!base) return String(c.id)
  return c.city ? `${base} ${t('common.dotSeparator')} ${c.city}` : base
}

async function load() {
  loading.value = true
  try {
    const [linesResp, cust, pack] = await Promise.all([
      listMarketingDeliveryLines(),
      listCustomers(),
      listPacking(),
    ])
    customers.value = cust
    packings.value = pack
    const lines = Array.isArray(linesResp) ? linesResp : (linesResp?.data || [])
    lineRows.value = lines.map((r) => ({
      ...r,
      delivery_date: r.delivery_date ? String(r.delivery_date).slice(0, 10) : '',
      po_date: r.po_date ? String(r.po_date).slice(0, 10) : '',
    }))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const kw = route.query.keyword
  if (kw != null && String(kw).trim()) keyword.value = String(kw).trim()
  load().then(() => {
    const deliveryIdRaw = route.query.delivery_id
    const deliveryId = Number(deliveryIdRaw)
    if (!Number.isNaN(deliveryId) && deliveryId > 0) {
      const target = lineRows.value.find((r) => Number(r.delivery_id) === deliveryId)
      if (target) openDetailFromLine(target)
    }
  })
})

const filteredRows = computed(() => {
  let rows = lineRows.value
  
  if (statusFilter.value) {
    const sf = statusFilter.value.toLowerCase()
    rows = rows.filter(r => (r.delivery_status || '').toLowerCase() === sf)
  }
  
  const q = keyword.value.trim().toLowerCase()
  if (!q) return rows
  
  return rows.filter((r) => {
    const searchableFields = [
      r.surat_jalan_no, r.factory_name, r.po_number, r.lot_no,
      r.buyer, r.material_name, r.color, r.delivery_status,
    ]
    return searchableFields.some(field => 
      field != null && String(field).toLowerCase().includes(q)
    )
  })
})

const isSentOrCancelled = computed(() => {
  const status = (detailRow.value?.status || '').toLowerCase()
  return status === 'sent' || status === 'cancelled' || status === 'canceled'
})

async function downloadDeliveryExcel() {
  exporting.value = true
  try {
    const q = keyword.value.trim() || undefined
    await fetchAuthenticatedDocument(marketingDeliveryXlsxPath({ q }), {
      mode: 'download',
      downloadFallbackName: 'delivery_list_sistem.xlsx',
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    exporting.value = false
  }
}

const formVisible = ref(false)
const form = reactive({
  customer_id: null,
  packing_id: null,
  delivery_date: '',
  vehicle_number: '',
  driver_name: '',
  status: 'draft',
})

function openCreate() {
  form.customer_id = null
  form.packing_id = null
  form.delivery_date = ''
  form.vehicle_number = ''
  form.driver_name = ''
  form.status = 'draft'
  formVisible.value = true
}

async function submit() {
  if (!form.customer_id) {
    ElMessage.warning(t('pages.delivery.pickCustomerWarning'))
    return
  }
  if (!form.packing_id) {
    ElMessage.warning(t('pages.delivery.pickDonePackingWarning'))
    return
  }
  saving.value = true
  try {
    await createDelivery({
      customer_id: form.customer_id,
      packing_id: form.packing_id,
      delivery_date: toIsoDate(form.delivery_date) || undefined,
      vehicle_number: form.vehicle_number || undefined,
      driver_name: form.driver_name || undefined,
      status: 'draft',
    })
    ElMessage.success(t('pages.delivery.saved'))
    formVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

const detailVisible = ref(false)
const detailRow = ref(null)
const detailLines = ref([])
const candidateProdDetails = ref([])
const detailLoading = ref(false)
const prodDetailsLoading = ref(false)
const markingSent = ref(false)
const markingSj = ref(false)
const addingLine = ref(false)

const lineForm = reactive({
  production_detail_id: null,
  qty: '',
})

const bcForm = reactive({
  bc_number: '',
  bc_date: '',
})
const bcSaving = ref(false)

function resetDetail() {
  detailLines.value = []
  candidateProdDetails.value = []
  lineForm.production_detail_id = null
  lineForm.qty = ''
  bcForm.bc_number = ''
  bcForm.bc_date = ''
}

function openDetailFromLine(row) {
  if (row?.delivery_id == null) return
  openDetailById(row.delivery_id)
}

async function loadProductionDetails(packingId) {
  prodDetailsLoading.value = true
  try {
    const pk = await getPacking(packingId)
    if (pk?.production_id) {
      const pds = await listProductionDetails(pk.production_id)
      candidateProdDetails.value = pds
    }
  } catch (e) {
    ElMessage.error(t('pages.delivery.loadProductionDetailsError'))
  } finally {
    prodDetailsLoading.value = false
  }
}

async function openDetailById(deliveryId) {
  detailVisible.value = true
  detailLoading.value = true
  resetDetail()
  try {
    const full = await getDelivery(deliveryId)
    detailRow.value = { ...full, customer_name: custName(full.customer_id) }
    bcForm.bc_number = full.bc_number || ''
    bcForm.bc_date = full.bc_date ? String(full.bc_date).slice(0, 10) : ''
    const lines = await listDeliveryDetails(deliveryId)
    detailLines.value = lines
    if (full.packing_id) {
      await loadProductionDetails(full.packing_id)
    }
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    detailLoading.value = false
  }
}

async function openSjPrint() {
  if (!detailRow.value?.id) return
  try {
    await fetchAuthenticatedDocument(`/documents/surat-jalan/${detailRow.value.id}`, { mode: 'open' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadSjPdf() {
  if (!detailRow.value?.id) return
  try {
    await fetchAuthenticatedDocument(`/documents/surat-jalan/${detailRow.value.id}/pdf`, { mode: 'open' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function saveBcFields() {
  if (!detailRow.value?.id) return
  bcSaving.value = true
  try {
    await updateDelivery(detailRow.value.id, {
      bc_number: bcForm.bc_number?.trim() || undefined,
      bc_date: bcForm.bc_date || undefined,
    })
    ElMessage.success(t('pages.delivery.bcSaved'))
    await load()
    const full = await getDelivery(detailRow.value.id)
    detailRow.value = { ...full, customer_name: custName(full.customer_id) }
    bcForm.bc_number = full.bc_number || ''
    bcForm.bc_date = full.bc_date ? String(full.bc_date).slice(0, 10) : ''
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    bcSaving.value = false
  }
}

async function markSjPrinted() {
  if (!detailRow.value?.id) return
  markingSj.value = true
  try {
    await markSuratJalanPrinted(detailRow.value.id)
    ElMessage.success(t('pages.delivery.sjMarkedPrinted'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    markingSj.value = false
  }
}

async function markSent() {
  if (!detailRow.value?.id) return
  markingSent.value = true
  try {
    await updateDelivery(detailRow.value.id, { status: 'sent' })
    ElMessage.success(t('pages.delivery.deliveryMarkedSent'))
    detailVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    markingSent.value = false
  }
}

async function addLine() {
  if (!detailRow.value?.id || !lineForm.production_detail_id) {
    ElMessage.warning(t('pages.delivery.pickProductionDetailWarning'))
    return
  }
  addingLine.value = true
  try {
    await addDeliveryDetail(detailRow.value.id, {
      production_detail_id: lineForm.production_detail_id,
      qty: lineForm.qty ? Number(lineForm.qty) : undefined,
    })
    ElMessage.success(t('pages.delivery.lineAdded'))
    detailLines.value = await listDeliveryDetails(detailRow.value.id)
    lineForm.production_detail_id = null
    lineForm.qty = ''
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    addingLine.value = false
  }
}
</script>

<style scoped>
.delivery-toolbar-search {
  width: 240px;
}
</style>
