<template>
  <AdminSection :title="t('pages.delivery.title')" :subtitle="t('pages.delivery.subtitle')">
    <template #actions>
      <el-input v-model="keyword" :placeholder="t('pages.delivery.listSearchPlaceholder')" clearable class="delivery-toolbar-search" />
      <el-button :icon="Download" :loading="exporting" @click="downloadDeliveryExcel">{{ t('pages.delivery.downloadExcel') }}</el-button>
      <el-button :icon="Van" @click="ElMessage.info(t('pages.delivery.flowInfo'))">{{ t('menu.deliveryPull') }}</el-button>
      <el-button :icon="Document" @click="ElMessage.info(t('pages.delivery.sjInfo'))">{{ t('menu.suratJalan') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" :loading="loading" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <p class="mb-2 text-sm font-medium text-slate-700">{{ t('pages.delivery.listSheetTitle') }}</p>
    <el-alert :title="t('pages.delivery.deliveryGuide')" type="info" show-icon :closable="false" class="mb-3" />

    <el-table
      :data="filteredRows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="auto"
      :empty-text="t('pages.delivery.tableEmpty')"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="52" align="center" fixed="left" />
      <el-table-column prop="surat_jalan_no" :label="t('pages.delivery.columns.noSj')" min-width="132" show-overflow-tooltip />
      <el-table-column prop="delivery_date" :label="t('pages.delivery.columns.shipDate')" width="112" />
      <el-table-column prop="factory_name" :label="t('pages.delivery.columns.factory')" min-width="140" show-overflow-tooltip />
      <el-table-column prop="system_no" :label="t('pages.delivery.columns.systemNo')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="po_date" :label="t('pages.delivery.columns.poDate')" width="112" />
      <el-table-column prop="po_number" :label="t('pages.delivery.columns.poNumber')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="lot_no" :label="t('pages.delivery.columns.lotNo')" min-width="100" show-overflow-tooltip />
      <el-table-column prop="thickness" :label="t('pages.delivery.columns.thickness')" width="100" show-overflow-tooltip />
      <el-table-column prop="color" :label="t('pages.delivery.columns.color')" min-width="100" show-overflow-tooltip />
      <el-table-column prop="material_type" :label="t('pages.delivery.columns.materialType')" min-width="100" show-overflow-tooltip />
      <el-table-column prop="material_name" :label="t('pages.delivery.columns.materialName')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="qty_po" :label="t('pages.delivery.columns.qtyPo')" width="88" align="right" />
      <el-table-column prop="unit_price" :label="t('pages.delivery.columns.unitPrice')" width="88" align="right" />
      <el-table-column prop="qty_roll" :label="t('pages.delivery.columns.roll')" width="72" align="right" />
      <el-table-column prop="qty_pcs" :label="t('pages.delivery.columns.pcs')" width="72" align="right" />
      <el-table-column prop="qty_sf" :label="t('pages.delivery.columns.sf')" width="88" align="right" />
      <el-table-column prop="gross_weight" :label="t('pages.delivery.columns.gw')" width="80" align="right" />
      <el-table-column prop="net_weight" :label="t('pages.delivery.columns.nw')" width="80" align="right" />
      <el-table-column prop="amount" :label="t('pages.delivery.columns.amount')" width="96" align="right" />
      <el-table-column prop="color_std" :label="t('pages.delivery.columns.colorStd')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="emboss" :label="t('pages.delivery.columns.emboss')" min-width="88" show-overflow-tooltip />
      <el-table-column prop="buyer" :label="t('pages.delivery.columns.buyer')" width="96" show-overflow-tooltip />
      <el-table-column prop="style_article" :label="t('pages.delivery.columns.style')" min-width="110" show-overflow-tooltip />
      <el-table-column prop="model" :label="t('pages.delivery.columns.model')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="invoice_number" :label="t('pages.delivery.columns.invNumber')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="pi_no" :label="t('pages.delivery.columns.piNo')" min-width="100" show-overflow-tooltip />
      <el-table-column prop="remark" :label="t('pages.delivery.columns.remark')" min-width="100" show-overflow-tooltip />
      <el-table-column prop="order_type" :label="t('pages.delivery.columns.orderType')" width="100" show-overflow-tooltip />
      <el-table-column prop="delivery_status" :label="t('pages.delivery.columns.status')" width="88" />
      <el-table-column :label="t('common.actions')" width="72" fixed="right" align="center">
        <template #default="{ row }">
          <el-tooltip :content="t('common.detail')" placement="top">
            <el-button
              :icon="View"
              link
              type="primary"
              :aria-label="t('common.detail')"
              @click="openDetailFromLine(row)"
            />
          </el-tooltip>
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
      width="640px"
      destroy-on-close
      align-center
      @closed="resetDetail"
    >
      <template v-if="detailRow">
        <el-descriptions :column="1" border size="small" class="mb-4">
          <el-descriptions-item :label="t('common.deliveryNo')">{{ detailRow.delivery_number }}</el-descriptions-item>
          <el-descriptions-item :label="t('common.customer')">{{ detailRow.customer_name }}</el-descriptions-item>
          <el-descriptions-item :label="t('common.date')">{{ detailRow.delivery_date }}</el-descriptions-item>
          <el-descriptions-item :label="t('common.vehicle')">{{ detailRow.vehicle_number }}</el-descriptions-item>
          <el-descriptions-item :label="t('common.driver')">{{ detailRow.driver_name }}</el-descriptions-item>
          <el-descriptions-item :label="t('pages.delivery.bcNumber')">{{ detailRow.bc_number || t('common.emptyValue') }}</el-descriptions-item>
          <el-descriptions-item :label="t('pages.delivery.bcDate')">
            {{ detailRow.bc_date ? String(detailRow.bc_date).slice(0, 10) : t('common.emptyValue') }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('common.status')">{{ detailRow.status }}</el-descriptions-item>
        </el-descriptions>

        <el-form v-if="canUpdate && detailRow" label-position="top" class="mb-4 border-t border-slate-100 pt-3">
          <el-form-item :label="t('pages.delivery.bcNumberEdit')">
            <el-input v-model="bcForm.bc_number" clearable maxlength="80" />
          </el-form-item>
          <el-form-item :label="t('pages.delivery.bcDateEdit')">
            <el-date-picker v-model="bcForm.bc_date" type="date" value-format="YYYY-MM-DD" class="w-full" clearable />
          </el-form-item>
          <el-button type="primary" plain :loading="bcSaving" @click="saveBcFields">{{ t('pages.delivery.saveBcFields') }}</el-button>
        </el-form>

        <div class="delivery-detail-actions">
          <el-button
            v-if="canUpdate"
            type="primary"
            :disabled="(detailRow.status || '').toLowerCase() === 'sent' || detailLines.length === 0"
            :loading="markingSent"
            @click="markSent"
          >
            {{ t('pages.delivery.markSent') }}
          </el-button>
          <el-button v-if="canPrint" @click="openSjPrint">{{ t('pages.delivery.printSj') }}</el-button>
          <el-button v-if="canPrint" @click="downloadSjPdf">{{ t('pages.delivery.downloadPdf') }}</el-button>
          <el-button v-if="canUpdate" type="success" plain :loading="markingSj" @click="markSjPrinted">{{ t('pages.delivery.markSjPrinted') }}</el-button>
          <span v-if="detailLines.length === 0" class="text-xs text-amber-600">{{ t('pages.delivery.needAtLeastOneLine') }}</span>
        </div>

        <h4 class="mb-2 text-sm font-medium text-slate-700">{{ t('pages.delivery.deliveryLines') }}</h4>
        <el-table :data="detailLines" border size="small" class="mb-4" table-layout="auto" :empty-text="t('pages.delivery.linesEmpty')">
          <el-table-column prop="id" :label="t('pages.delivery.lineId')" width="64" />
          <el-table-column prop="production_detail_id" :label="t('pages.delivery.productionDetailId')" min-width="120" />
          <el-table-column prop="qty" :label="t('common.quantity')" width="100" align="right" />
        </el-table>

        <el-form v-if="canUpdate && candidateProdDetails.length" label-position="top" class="border-t border-slate-100 pt-3">
          <el-form-item :label="t('pages.delivery.addLineLabel')">
            <el-select v-model="lineForm.production_detail_id" filterable clearable class="w-full" :placeholder="t('pages.delivery.productionDetailPlaceholder')">
              <el-option
                v-for="pd in candidateProdDetails"
                :key="pd.id"
                :label="`#${pd.id} ${t('common.dotSeparator')} ${t('common.actual').toLowerCase()} ${pd.qty_actual ?? t('common.emptyValue')}`"
                :value="pd.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('common.quantity')">
            <el-input v-model="lineForm.qty" type="number" step="0.01" />
          </el-form-item>
          <el-button type="primary" :loading="addingLine" @click="addLine">{{ t('pages.delivery.addToDelivery') }}</el-button>
        </el-form>
        <p v-else-if="detailRow && detailLoading === false" class="text-sm text-slate-500">
          {{ t('pages.delivery.noProductionLines') }}
        </p>
      </template>
      <template #footer>
        <div class="delivery-dialog-footer">
          <el-button type="primary" @click="detailVisible = false">{{ t('pages.delivery.closeDetail') }}</el-button>
        </div>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, View, Van, Document, Download } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
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
    const [lines, cust, pack] = await Promise.all([
      listMarketingDeliveryLines(),
      listCustomers(),
      listPacking(),
    ])
    customers.value = cust
    packings.value = pack
    lineRows.value = (lines || []).map((r) => ({
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
  const q = keyword.value.trim().toLowerCase()
  if (!q) return lineRows.value
  return lineRows.value.filter((r) => JSON.stringify(r).toLowerCase().includes(q))
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
      const pk = await getPacking(full.packing_id)
      if (pk?.production_id) {
        const pds = await listProductionDetails(pk.production_id)
        candidateProdDetails.value = pds
      }
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
.admin-table {
  width: 100%;
}

.delivery-detail-actions {
  margin-bottom: 8px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.delivery-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
