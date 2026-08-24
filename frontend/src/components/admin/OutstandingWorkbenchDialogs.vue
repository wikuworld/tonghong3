<template>
  <!-- Dialog jadwal kirim batch — qty + tanggal per baris -->
  <el-dialog
    :model-value="scheduleVisible"
    :title="t('pages.marketingFlow.scheduleDialogTitle')"
    width="820px"
    top="6vh"
    destroy-on-close
    @update:model-value="$emit('update:scheduleVisible', $event)"
  >
    <p class="out-dlg-hint">{{ t('pages.marketingFlow.scheduleDialogHint', { n: rows.length }) }}</p>
    <div class="out-dlg-toolbar">
      <el-form-item :label="t('pages.marketingFlow.scheduleMode')" class="out-dlg-toolbar__mode mb-0">
        <el-radio-group v-model="scheduleMode" size="small">
          <el-radio-button label="append">{{ t('pages.marketingFlow.scheduleModeAppend') }}</el-radio-button>
          <el-radio-button label="replace">{{ t('pages.marketingFlow.scheduleModeReplace') }}</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <div class="out-dlg-toolbar__apply">
        <el-date-picker
          v-model="applyAllDate"
          type="date"
          value-format="YYYY-MM-DD"
          size="small"
          :placeholder="t('pages.marketingFlow.scheduleApplyAllDatePlaceholder')"
        />
        <el-button size="small" :disabled="!applyAllDate" @click="applyDateToAll">
          {{ t('pages.marketingFlow.scheduleApplyAllDate') }}
        </el-button>
      </div>
    </div>
    <el-table :data="scheduleRows" size="small" max-height="360" border>
      <el-table-column prop="system_reference" :label="t('pages.marketingFlow.colSystemNo')" min-width="120" />
      <el-table-column prop="material_name" :label="t('common.material')" min-width="140" />
      <el-table-column prop="balance_qty" :label="t('pages.marketingFlow.colBalance')" width="90" />
      <el-table-column :label="t('pages.po.lineEtd')" width="110">
        <template #default="{ row }">{{ row.line_etd || '—' }}</template>
      </el-table-column>
      <el-table-column :label="t('pages.marketingFlow.scheduleRowStatus')" width="110">
        <template #default="{ row }">
          <el-tag v-if="row.schedule_full" type="warning" size="small" effect="plain">
            {{ t('pages.marketingFlow.scheduleRowFull') }}
          </el-tag>
          <span v-else class="out-dlg-muted">—</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.quantity')" width="120">
        <template #default="{ row }">
          <el-input
            v-model="row.qty"
            size="small"
            type="number"
            :disabled="scheduleMode === 'append' && row.schedule_full"
          />
        </template>
      </el-table-column>
      <el-table-column :label="t('pages.marketingFlow.scheduleDeliveryDate')" width="160">
        <template #default="{ row }">
          <el-date-picker
            v-model="row.delivery_date"
            type="date"
            value-format="YYYY-MM-DD"
            size="small"
            class="w-full"
            :disabled="scheduleMode === 'append' && row.schedule_full"
          />
        </template>
      </el-table-column>
    </el-table>
    <template #footer>
      <el-button @click="$emit('update:scheduleVisible', false)">{{ t('common.cancel') }}</el-button>
      <el-button type="primary" :loading="savingSchedule" @click="submitSchedule">
        {{ t('pages.marketingFlow.scheduleConfirm') }}
      </el-button>
    </template>
  </el-dialog>

  <!-- Dialog PI multi-SO -->
  <el-dialog
    :model-value="piVisible"
    :title="t('pages.marketingFlow.piDialogTitle')"
    width="560px"
    destroy-on-close
    @update:model-value="$emit('update:piVisible', $event)"
  >
    <p class="out-dlg-hint">
      {{ t('pages.marketingFlow.piDialogHint', { n: uniquePoIds.length, lines: rows.length }) }}
    </p>
    <ul class="out-dlg-list">
      <li v-for="id in uniquePoIds" :key="id">{{ poLabel(id) }} — {{ lineCountForPo(id) }} {{ t('pages.marketingFlow.piLineCountSuffix') }}</li>
    </ul>
    <p v-if="piCustomerWarn" class="out-dlg-warn">{{ piCustomerWarn }}</p>
    <template #footer>
      <el-button @click="$emit('update:piVisible', false)">{{ t('common.cancel') }}</el-button>
      <el-button :disabled="Boolean(piCustomerWarn)" :loading="savingPi" @click="downloadPi('docx')">
        {{ t('pages.po.proformaInvoiceDocx') }}
      </el-button>
      <el-button type="primary" :disabled="Boolean(piCustomerWarn)" :loading="savingPi" @click="downloadPi('pdf')">
        {{ t('pages.po.proformaInvoicePdf') }}
      </el-button>
    </template>
  </el-dialog>

  <!-- Dialog packing per baris -->
  <el-dialog
    :model-value="shipVisible"
    :title="t('pages.marketingFlow.shipDialogTitle')"
    width="1020px"
    top="4vh"
    destroy-on-close
    @update:model-value="$emit('update:shipVisible', $event)"
  >
    <p class="out-dlg-hint">{{ t('pages.marketingFlow.shipDialogHint') }}</p>
    <el-alert
      v-if="!loadingPacking && !packingOptions.length"
      :title="t('pages.marketingFlow.shipPackingEmptyTitle')"
      type="info"
      :closable="false"
      show-icon
      class="mb-3"
    >
      {{ t('pages.marketingFlow.shipPackingEmptyHint') }}
    </el-alert>
    <div class="out-dlg-toolbar mb-3" v-if="packingOptions.length">
      <el-button size="small" @click="fillAllFullLot">{{ t('pages.marketingFlow.shipFillAllFullLot') }}</el-button>
      <span class="out-dlg-muted">{{ t('pages.marketingFlow.shipFullLotHint') }}</span>
    </div>
    <div v-loading="loadingPacking">
      <el-table :data="shipRows" size="small" border max-height="420">
        <el-table-column prop="system_reference" :label="t('pages.marketingFlow.colSystemNo')" min-width="110" />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="130" />
        <el-table-column :label="t('pages.marketingFlow.colBalance')" width="88" align="right">
          <template #default="{ row }">{{ row.balance_qty || '—' }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.shipPackingPick')" min-width="230">
          <template #default="{ row }">
            <template v-if="optionsFor(row.po_detail_id).length">
              <el-select
                v-model="row.pickedKey"
                filterable
                clearable
                class="w-full"
                :placeholder="t('pages.marketingFlow.shipPackingPlaceholder')"
                @change="onPickPacking(row)"
              >
                <el-option
                  v-for="opt in optionsFor(row.po_detail_id)"
                  :key="`${opt.packing_id}-${opt.production_detail_id}`"
                  :label="`${opt.packing_number} · ${opt.lot_no || '—'} · avail ${opt.qty_available}`"
                  :value="`${opt.packing_id}:${opt.production_detail_id}:${opt.packing_detail_id || ''}`"
                />
              </el-select>
            </template>
            <span v-else class="out-dlg-muted">{{ t('pages.marketingFlow.shipPackingRowEmpty') }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.shipQtyPacked')" width="90" align="right">
          <template #default="{ row }">{{ row.pickedKey ? (row.qty_packed ?? '—') : '—' }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.shipQtyAvailable')" width="90" align="right">
          <template #default="{ row }">{{ row.pickedKey ? (row.qty_available ?? '—') : '—' }}</template>
        </el-table-column>
        <el-table-column :label="t('common.quantity')" width="150">
          <template #default="{ row }">
            <div class="out-dlg-qty-cell">
              <el-input v-model="row.qty" size="small" type="number" :disabled="!row.pickedKey" />
              <el-button
                size="small"
                link
                type="primary"
                :disabled="!row.pickedKey"
                @click="fillFullLot(row)"
              >
                {{ t('pages.marketingFlow.shipFillFullLot') }}
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.scheduleDeliveryDate')" width="150">
          <template #default="{ row }">
            <el-date-picker
              v-model="row.delivery_date"
              type="date"
              value-format="YYYY-MM-DD"
              size="small"
              class="w-full"
              :disabled="!row.pickedKey"
            />
          </template>
        </el-table-column>
      </el-table>
    </div>
    <template #footer>
      <el-button @click="$emit('update:shipVisible', false)">{{ t('common.cancel') }}</el-button>
      <el-button
        type="primary"
        :loading="savingShip"
        :disabled="!packingOptions.length"
        @click="submitShip"
      >
        {{ t('pages.marketingFlow.shipConfirm') }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

import {
  createOutstandingShipBatch,
  createOutstandingScheduleBatch,
  fetchAuthenticatedDocument,
  listOutstandingPackingOptions,
  proformaInvoiceBatchDocxPath,
  proformaInvoiceBatchPdfPath,
} from '../../api/client'

const props = defineProps({
  rows: { type: Array, default: () => [] },
  scheduleVisible: { type: Boolean, default: false },
  piVisible: { type: Boolean, default: false },
  shipVisible: { type: Boolean, default: false },
})

const emit = defineEmits([
  'update:scheduleVisible',
  'update:piVisible',
  'update:shipVisible',
  'done',
])

const { t } = useI18n()
const scheduleMode = ref('append')
const applyAllDate = ref('')
const scheduleRows = ref([])
const savingSchedule = ref(false)
const savingPi = ref(false)
const savingShip = ref(false)
const loadingPacking = ref(false)
const packingOptions = ref([])
const shipRows = ref([])

const uniquePoIds = computed(() => [...new Set(props.rows.map((r) => r.po_id).filter(Boolean))])

const piCustomerWarn = computed(() => {
  const names = [...new Set(props.rows.map((r) => (r.customer_name || '').trim()).filter(Boolean))]
  if (names.length > 1) return t('pages.marketingFlow.piCustomerMismatch')
  return ''
})

function todayIso() {
  return new Date().toISOString().slice(0, 10)
}

function poLabel(poId) {
  const row = props.rows.find((r) => r.po_id === poId)
  return row?.system_reference || row?.no_po || row?.thi_order || `SO #${poId}`
}

function lineCountForPo(poId) {
  return props.rows.filter((r) => Number(r.po_id) === Number(poId)).length
}

function selectedPoDetailIds() {
  return [...new Set(props.rows.map((r) => r.po_detail_id).filter((id) => id != null))]
}

function optionsFor(poDetailId) {
  return packingOptions.value.filter((o) => Number(o.po_detail_id) === Number(poDetailId))
}

function parseNum(v) {
  if (v === '' || v == null) return null
  const n = Number(String(v).replace(',', '.'))
  return Number.isFinite(n) ? n : null
}

function suggestedShipQty(row, opt) {
  const avail = parseNum(opt?.qty_available)
  const bal = parseNum(row.balance_qty)
  if (avail != null && bal != null) return Math.min(avail, bal)
  if (avail != null) return avail
  if (bal != null) return bal
  return ''
}

function onPickPacking(row) {
  if (!row.pickedKey) {
    row.production_detail_id = null
    row.packing_id = null
    row.packing_detail_id = null
    row.qty_available = null
    row.qty_packed = null
    return
  }
  const [packingId, prodId, pkdId] = String(row.pickedKey).split(':')
  row.packing_id = Number(packingId)
  row.production_detail_id = Number(prodId)
  row.packing_detail_id = pkdId ? Number(pkdId) : null
  const opt = packingOptions.value.find(
    (o) =>
      Number(o.packing_id) === row.packing_id &&
      Number(o.production_detail_id) === row.production_detail_id,
  )
  row.qty_available = opt?.qty_available ?? null
  row.qty_packed = opt?.qty_packed ?? null
  row.qty = suggestedShipQty(row, opt)
}

function fillFullLot(row) {
  if (!row.pickedKey) return
  const opt = packingOptions.value.find(
    (o) =>
      Number(o.packing_id) === Number(row.packing_id) &&
      Number(o.production_detail_id) === Number(row.production_detail_id),
  )
  row.qty = suggestedShipQty(row, opt || { qty_available: row.qty_available })
}

function fillAllFullLot() {
  for (const row of shipRows.value) {
    if (row.pickedKey) fillFullLot(row)
  }
}

function applyDateToAll() {
  if (!applyAllDate.value) return
  for (const row of scheduleRows.value) {
    row.delivery_date = applyAllDate.value
  }
}

async function loadPackingOptions() {
  const ids = [...new Set(props.rows.map((r) => r.po_detail_id).filter(Boolean))]
  if (!ids.length) {
    packingOptions.value = []
    return
  }
  loadingPacking.value = true
  try {
    const resp = await listOutstandingPackingOptions(ids)
    packingOptions.value = resp?.data || resp || []
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    packingOptions.value = []
  } finally {
    loadingPacking.value = false
  }
}

watch(
  () => props.shipVisible,
  async (open) => {
    if (!open) return
    const today = todayIso()
    shipRows.value = props.rows.map((r) => ({
      po_detail_id: r.po_detail_id,
      system_reference: r.system_reference || r.thi_order,
      material_name: r.material_name,
      balance_qty: r.balance_qty,
      pickedKey: '',
      packing_id: null,
      packing_detail_id: null,
      production_detail_id: null,
      qty_available: null,
      qty_packed: null,
      qty: '',
      delivery_date: today,
    }))
    await loadPackingOptions()
  },
)

watch(
  () => props.scheduleVisible,
  (open) => {
    if (!open) return
    const today = todayIso()
    applyAllDate.value = today
    scheduleMode.value = 'append'
    scheduleRows.value = props.rows.map((r) => ({
      po_detail_id: r.po_detail_id,
      system_reference: r.system_reference || r.thi_order,
      material_name: r.material_name,
      balance_qty: r.balance_qty,
      line_etd: r.line_etd || null,
      qty: r.schedule_unallocated_qty || r.balance_qty || '',
      delivery_date: today,
      schedule_full: Number(r.schedule_unallocated_qty) === 0 && Number(r.schedule_qty_total) > 0,
    }))
    const fullCount = scheduleRows.value.filter((r) => r.schedule_full).length
    if (fullCount && fullCount === scheduleRows.value.length) {
      ElMessage.warning(t('pages.marketingFlow.scheduleAlreadyFullAll'))
    } else if (fullCount) {
      ElMessage.info(t('pages.marketingFlow.scheduleAlreadyFullSome', { n: fullCount }))
    }
  },
)

async function submitSchedule() {
  const activeRows = scheduleRows.value.filter(
    (r) => !(scheduleMode.value === 'append' && r.schedule_full),
  )
  if (!activeRows.length) {
    ElMessage.warning(t('pages.marketingFlow.scheduleAlreadyFullAll'))
    return
  }
  const lines = activeRows
    .filter((r) => r.delivery_date)
    .map((r) => ({
      po_detail_id: r.po_detail_id,
      delivery_date: r.delivery_date,
      qty: r.qty !== '' && r.qty != null ? Number(r.qty) : null,
    }))
  if (!lines.length) {
    ElMessage.warning(t('pages.marketingFlow.scheduleDateRequired'))
    return
  }
  const missingDate = activeRows.some((r) => !r.delivery_date)
  if (missingDate) {
    ElMessage.warning(t('pages.marketingFlow.scheduleDateRequired'))
    return
  }
  savingSchedule.value = true
  try {
    await createOutstandingScheduleBatch({
      mode: scheduleMode.value,
      lines,
    })
    ElMessage.success(t('pages.marketingFlow.scheduleSaved'))
    emit('update:scheduleVisible', false)
    emit('done')
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    savingSchedule.value = false
  }
}

async function downloadPi(fmt) {
  const detailIds = selectedPoDetailIds()
  if (!detailIds.length) {
    ElMessage.warning(t('pages.marketingFlow.selectRowsFirst'))
    return
  }
  savingPi.value = true
  try {
    const path = fmt === 'docx' ? proformaInvoiceBatchDocxPath() : proformaInvoiceBatchPdfPath()
    await fetchAuthenticatedDocument(path, {
      mode: 'download',
      method: 'POST',
      body: {
        po_ids: uniquePoIds.value,
        po_detail_ids: detailIds,
      },
      downloadFallbackName: `proforma-invoice-batch.${fmt}`,
    })
    ElMessage.success(t('pages.marketingFlow.piDownloaded'))
    emit('update:piVisible', false)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    savingPi.value = false
  }
}

async function submitShip() {
  const lines = []
  for (const r of shipRows.value) {
    if (!r.packing_id || !r.production_detail_id) continue
    const qty = parseNum(r.qty)
    if (qty == null || qty <= 0) {
      ElMessage.warning(t('pages.marketingFlow.shipQtyRequired'))
      return
    }
    const avail = parseNum(r.qty_available)
    if (avail != null && qty > avail) {
      ElMessage.warning(t('pages.marketingFlow.shipQtyExceedsAvailable', { avail }))
      return
    }
    lines.push({
      po_detail_id: r.po_detail_id,
      packing_id: r.packing_id,
      packing_detail_id: r.packing_detail_id,
      production_detail_id: r.production_detail_id,
      qty,
      delivery_date: r.delivery_date || null,
    })
  }
  if (!lines.length) {
    ElMessage.warning(t('pages.marketingFlow.shipPickRequired'))
    return
  }
  savingShip.value = true
  try {
    const res = await createOutstandingShipBatch({ lines })
    ElMessage.success(res.message || t('pages.marketingFlow.shipSaved'))
    emit('update:shipVisible', false)
    emit('done')
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    savingShip.value = false
  }
}
</script>

<style scoped>
.out-dlg-hint {
  margin: 0 0 12px;
  font-size: 13px;
  color: #64748b;
}
.out-dlg-list {
  margin: 0 0 12px;
  padding-left: 1.2em;
  font-size: 13px;
}
.out-dlg-warn {
  color: #b45309;
  font-weight: 600;
  font-size: 13px;
}
.out-dlg-muted {
  font-size: 12px;
  color: #94a3b8;
}
.out-dlg-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
.out-dlg-toolbar__apply {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}
.mb-0 {
  margin-bottom: 0;
}
.mb-3 {
  margin-bottom: 12px;
}
.w-full {
  width: 100%;
}
.out-dlg-qty-cell {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 2px;
}
.inline-flex {
  display: inline-flex;
}
.gap-2 {
  gap: 0.5rem;
}
</style>
