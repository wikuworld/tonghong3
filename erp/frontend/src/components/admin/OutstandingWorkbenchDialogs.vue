<template>
  <!-- Dialog rencana kirim — satu qty + satu tanggal per baris -->
  <el-dialog
    :model-value="scheduleVisible"
    :title="t('pages.marketingFlow.scheduleDialogTitle')"
    width="960px"
    top="4vh"
    destroy-on-close
    class="out-schedule-dialog"
    @update:model-value="$emit('update:scheduleVisible', $event)"
  >
    <p class="out-dlg-hint">{{ t('pages.marketingFlow.scheduleDialogHint', { n: rows.length }) }}</p>
    <div class="out-dlg-toolbar">
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
    <el-table :data="scheduleRows" size="small" max-height="440" border>
      <el-table-column prop="system_reference" :label="t('pages.marketingFlow.colSystemNo')" min-width="108" fixed="left" />
      <el-table-column prop="material_name" :label="t('common.material')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="balance_qty" :label="t('pages.marketingFlow.colBalance')" width="72" align="right" />
      <el-table-column :label="t('pages.marketingFlow.outstandingColQtyWip')" width="72" align="right">
        <template #default="{ row }">{{ row.mrp_qty_wip || '—' }}</template>
      </el-table-column>
      <el-table-column :label="t('pages.po.lineEtd')" width="100">
        <template #default="{ row }">{{ row.line_etd || '—' }}</template>
      </el-table-column>
      <el-table-column :label="t('pages.marketingFlow.colPlanQty')" width="120" align="right">
        <template #default="{ row }">
          <el-input
            v-model="row.plan_qty"
            size="small"
            type="number"
            :placeholder="t('common.quantity')"
          />
        </template>
      </el-table-column>
      <el-table-column :label="t('pages.marketingFlow.colPlanDate')" width="150">
        <template #default="{ row }">
          <el-date-picker
            v-model="row.plan_date"
            type="date"
            value-format="YYYY-MM-DD"
            size="small"
            class="out-dlg-plan-date"
            :placeholder="t('pages.marketingFlow.scheduleDeliveryDate')"
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
      v-if="shipCustomerWarn"
      type="error"
      :closable="false"
      show-icon
      class="mb-3"
    >
      {{ shipCustomerWarn }}
    </el-alert>
    <el-alert
      v-else-if="shipSoCount > 1"
      type="success"
      :closable="false"
      show-icon
      class="mb-3"
    >
      {{ t('pages.marketingFlow.shipConsolidateHint', { n: shipSoCount }) }}
    </el-alert>
    <el-alert
      v-if="!shipCustomerWarn && shipPackingCodeCount > 1"
      type="info"
      :closable="false"
      show-icon
      class="mb-3"
    >
      {{ t('pages.marketingFlow.shipMultiPackingHint', { n: shipPackingCodeCount }) }}
    </el-alert>
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
    <div v-loading="loadingPacking">
      <el-table
        ref="shipTableRef"
        :data="shipRows"
        size="small"
        border
        max-height="420"
        row-key="rowKey"
        @selection-change="onShipSelectionChange"
      >
        <el-table-column type="selection" width="48" fixed="left" :selectable="shipRowSelectable" />
        <el-table-column prop="system_reference" :label="t('pages.marketingFlow.colSystemNo')" min-width="110" />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="130" />
        <el-table-column :label="t('pages.marketingFlow.colLotNo')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ row.lot_no || '—' }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.shipPackingInfo')" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.packing_id">{{ row.packing_number || '—' }}</span>
            <span v-else class="out-dlg-muted">{{ t('pages.marketingFlow.shipPackingRowEmpty') }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.shipFgQtySf')" width="88" align="right">
          <template #default="{ row }">{{ row.packing_id ? formatShipQty(row.qty_packed) : '—' }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.shipFgRolls')" width="72" align="right">
          <template #default="{ row }">{{ row.packing_id ? formatIntQty(row.qty_roll) : '—' }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.shipFgPieces')" width="72" align="right">
          <template #default="{ row }">{{ row.packing_id ? formatIntQty(row.qty_pcs) : '—' }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.scheduleDeliveryDate')" width="150">
          <template #default="{ row }">
            <el-date-picker
              v-model="row.delivery_date"
              type="date"
              value-format="YYYY-MM-DD"
              size="small"
              class="w-full"
              :disabled="!row.packing_id"
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
        :disabled="!shipSelected.length || Boolean(shipCustomerWarn)"
        @click="submitShip"
      >
        {{ t('pages.marketingFlow.shipConfirm') }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'

import {
  createOutstandingShipBatch,
  createOutstandingScheduleBatch,
  fetchAuthenticatedDocument,
  listOutstandingPackingOptions,
  proformaInvoiceBatchDocxPath,
  proformaInvoiceBatchPdfPath,
} from '../../api/client'
import {
  firstPlannedDeliveryDate,
  mostCommonPlannedDeliveryDate,
  extractPlanSlots,
} from '../../utils/outstandingWork.js'
import { withinOvershipTolerance } from '../../utils/overshipTolerance.js'

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
const router = useRouter()
const applyAllDate = ref('')
const scheduleRows = ref([])
const savingSchedule = ref(false)
const savingPi = ref(false)
const savingShip = ref(false)
const loadingPacking = ref(false)
const packingOptions = ref([])
const shipRows = ref([])
const shipSelected = ref([])
const shipTableRef = ref(null)

const uniquePoIds = computed(() => [...new Set(props.rows.map((r) => r.po_id).filter(Boolean))])
const shipSoCount = computed(() => uniquePoIds.value.length)
const shipPackingCodeCount = computed(() => {
  const ids = new Set(
    shipRows.value
      .map((r) => (r.packing_id != null ? Number(r.packing_id) : null))
      .filter((id) => id != null && id > 0),
  )
  return ids.size
})

const piCustomerWarn = computed(() => {
  const names = [...new Set(props.rows.map((r) => (r.customer_name || '').trim()).filter(Boolean))]
  if (names.length > 1) return t('pages.marketingFlow.piCustomerMismatch')
  return ''
})

const shipCustomerWarn = computed(() => {
  const names = [...new Set(props.rows.map((r) => (r.customer_name || '').trim()).filter(Boolean))]
  if (names.length > 1) return t('pages.marketingFlow.shipCustomerMismatch')
  return ''
})

function defaultRowDeliveryDate(row) {
  return firstPlannedDeliveryDate(row) || ''
}

function defaultBatchDeliveryDate(rows) {
  return mostCommonPlannedDeliveryDate(rows) || ''
}

function mapScheduleRows() {
  return props.rows.map((r) => {
    const existing = extractPlanSlots(r, { maxSlots: 1 })[0]
    return {
      po_detail_id: r.po_detail_id,
      system_reference: r.system_reference || r.thi_order,
      material_name: r.material_name,
      balance_qty: r.balance_qty,
      line_etd: r.line_etd || null,
      schedule_full: Number(r.schedule_unallocated_qty) === 0 && Number(r.schedule_qty_total) > 0,
      mrp_qty_wip: r.mrp_qty_wip || '',
      source: r,
      // Default kosong; terisi hanya jika sudah ada rencana, atau user isi saat buat baru.
      plan_qty: existing?.qty != null && existing.qty !== '' ? String(existing.qty) : '',
      plan_date: existing?.delivery_date || defaultRowDeliveryDate(r),
    }
  })
}

function applyDateToAll() {
  if (!applyAllDate.value) return
  for (const row of scheduleRows.value) {
    row.plan_date = applyAllDate.value
  }
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

function outstandingLotNo(row) {
  const raw = row?.lot_no || row?.lot_number || row?.thi_line_ref || row?.system_reference || ''
  const s = String(raw).trim()
  if (!s || s === '—') return ''
  return s
}

function shipRowSelectable(row) {
  return Boolean(row?.packing_id && row?.production_detail_id)
}

function onShipSelectionChange(rows) {
  shipSelected.value = rows || []
}

function emptyShipRow(source) {
  return {
    rowKey: `empty:${source.po_detail_id}`,
    po_detail_id: source.po_detail_id,
    system_reference: source.system_reference || source.thi_order,
    material_name: source.material_name,
    lot_no: outstandingLotNo(source),
    balance_qty: source.balance_qty,
    qty_sf: source.qty_sf,
    quantity_order: source.quantity_order ?? source.qty_sf,
    mrp_qty_wip: source.mrp_qty_wip || '',
    source,
    pickedKey: '',
    packing_id: null,
    packing_number: '',
    packing_detail_id: null,
    production_detail_id: null,
    qty_available: null,
    qty_packed: null,
    qty_roll: null,
    qty_pcs: null,
    qty: '',
    delivery_date: defaultRowDeliveryDate(source),
  }
}

function rebuildShipRows() {
  const soByDetail = new Map()
  for (const r of props.rows) {
    if (r.po_detail_id == null) continue
    soByDetail.set(Number(r.po_detail_id), r)
  }
  const covered = new Set()
  const rows = []
  for (const opt of packingOptions.value) {
    const source = soByDetail.get(Number(opt.po_detail_id))
    if (!source) continue
    covered.add(Number(opt.po_detail_id))
    const row = {
      rowKey: `pk:${opt.packing_id}:${opt.production_detail_id}:${opt.packing_detail_id || ''}:${opt.po_detail_id}`,
      po_detail_id: Number(opt.po_detail_id),
      system_reference: source.system_reference || source.thi_order,
      material_name: source.material_name || opt.material_name,
      lot_no: String(opt.lot_no || '').trim() || outstandingLotNo(source),
      balance_qty: source.balance_qty,
      qty_sf: source.qty_sf,
      quantity_order: source.quantity_order ?? source.qty_sf,
      mrp_qty_wip: source.mrp_qty_wip || '',
      source,
      pickedKey: '',
      packing_id: null,
      packing_number: '',
      packing_detail_id: null,
      production_detail_id: null,
      qty_available: null,
      qty_packed: null,
      qty_roll: null,
      qty_pcs: null,
      qty: '',
      delivery_date: defaultRowDeliveryDate(source),
    }
    bindPackingOption(row, opt)
    rows.push(row)
  }
  for (const r of props.rows) {
    if (r.po_detail_id == null) continue
    if (covered.has(Number(r.po_detail_id))) continue
    rows.push(emptyShipRow(r))
  }
  shipRows.value = rows
  shipSelected.value = []
}

async function selectAllShipPackingRows() {
  await nextTick()
  const table = shipTableRef.value
  if (!table) return
  table.clearSelection?.()
  for (const row of shipRows.value) {
    if (shipRowSelectable(row)) table.toggleRowSelection(row, true)
  }
}

function parseNum(v) {
  if (v === '' || v == null) return null
  const n = Number(String(v).replace(',', '.'))
  return Number.isFinite(n) ? n : null
}

function orderQtyForRow(row) {
  return parseNum(row?.quantity_order ?? row?.qty_sf ?? row?.source?.qty_sf ?? row?.source?.quantity_order)
}

function suggestedShipQty(row, opt) {
  // Prefer qty packing/FG aktual untuk QTY (S/F) surat jalan.
  // Overship vs saldo order diizinkan dalam toleransi ukur kecil (max 2 SF / 0.5%).
  const avail = parseNum(opt?.qty_available)
  const packed = parseNum(opt?.qty_packed)
  const bal = parseNum(row.balance_qty)
  const wip = parseNum(row.mrp_qty_wip)
  let q = avail != null && avail > 0 ? avail : packed
  if (q == null || q <= 0) {
    q = wip != null && wip > 0 ? wip : bal
  }
  if (q == null) return null
  if (bal != null && bal >= 0 && q > bal) {
    if (withinOvershipTolerance(q, bal, orderQtyForRow(row))) return q
    return bal
  }
  return q
}

function packingOptForRow(row) {
  if (!row?.packing_id || !row?.production_detail_id) return null
  return packingOptions.value.find(
    (o) =>
      Number(o.packing_id) === Number(row.packing_id) &&
      Number(o.production_detail_id) === Number(row.production_detail_id),
  )
}

function resolveShipQty(row) {
  const manual = parseNum(row?.qty)
  if (manual != null && manual > 0) return manual
  return suggestedShipQty(row, packingOptForRow(row))
}

function formatShipQty(n) {
  if (n == null || !Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function formatIntQty(n) {
  if (n == null || n === '') return '—'
  const v = Number(n)
  if (!Number.isFinite(v)) return '—'
  return String(Math.trunc(v))
}

function applyAutoShipQty(row) {
  const q = resolveShipQty(row)
  row.qty = q != null ? String(q) : ''
}

function bindPackingOption(row, opt) {
  if (!opt) {
    row.pickedKey = ''
    row.production_detail_id = null
    row.packing_id = null
    row.packing_detail_id = null
    row.packing_number = ''
    row.qty_available = null
    row.qty_packed = null
    row.qty_roll = null
    row.qty_pcs = null
    row.qty = ''
    return
  }
  row.pickedKey = `${opt.packing_id}:${opt.production_detail_id}:${opt.packing_detail_id || ''}`
  row.packing_id = Number(opt.packing_id)
  row.production_detail_id = Number(opt.production_detail_id)
  row.packing_detail_id = opt.packing_detail_id != null ? Number(opt.packing_detail_id) : null
  row.packing_number = opt.packing_number || ''
  row.qty_available = opt.qty_available ?? null
  row.qty_packed = opt.qty_packed ?? null
  row.qty_roll = opt.qty_roll ?? null
  row.qty_pcs = opt.qty_pcs ?? null
  applyAutoShipQty(row)
}

async function loadPackingOptions() {
  const ids = [...new Set(props.rows.map((r) => r.po_detail_id).filter(Boolean))]
  if (!ids.length) {
    packingOptions.value = []
    rebuildShipRows()
    return
  }
  loadingPacking.value = true
  try {
    const resp = await listOutstandingPackingOptions(ids)
    packingOptions.value = resp?.data || resp || []
    rebuildShipRows()
    await selectAllShipPackingRows()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    packingOptions.value = []
    rebuildShipRows()
  } finally {
    loadingPacking.value = false
  }
}

watch(
  () => props.shipVisible,
  async (open) => {
    if (!open) return
    shipSelected.value = []
    shipRows.value = props.rows.map((r) => emptyShipRow(r))
    await loadPackingOptions()
  },
)

watch(
  () => props.scheduleVisible,
  (open) => {
    if (!open) return
    applyAllDate.value = defaultBatchDeliveryDate(props.rows)
    scheduleRows.value = mapScheduleRows()
  },
)

async function submitSchedule() {
  const lines = []
  for (const row of scheduleRows.value) {
    if (!row.plan_date) {
      ElMessage.warning(t('pages.marketingFlow.scheduleDateRequired'))
      return
    }
    const qty = parseNum(row.plan_qty)
    if (qty == null) {
      ElMessage.warning(t('pages.marketingFlow.scheduleSlotQtyRequired'))
      return
    }
    lines.push({
      po_detail_id: row.po_detail_id,
      delivery_date: row.plan_date,
      qty,
      sequence_no: 1,
    })
  }
  if (!lines.length) {
    ElMessage.warning(t('pages.marketingFlow.scheduleAddSlotFirst'))
    return
  }

  const overWip = scheduleRows.value.filter((r) => {
    const totalQty = parseNum(r.plan_qty) || 0
    const wip = parseNum(r.mrp_qty_wip)
    return wip != null && wip > 0 && totalQty > wip
  })
  if (overWip.length) {
    ElMessage.warning(t('pages.marketingFlow.scheduleQtyOverWip', { n: overWip.length }))
  }

  savingSchedule.value = true
  try {
    await createOutstandingScheduleBatch({
      mode: 'replace',
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
  if (shipCustomerWarn.value) {
    ElMessage.warning(shipCustomerWarn.value)
    return
  }
  const picked = shipSelected.value.filter((r) => r.packing_id && r.production_detail_id)
  if (!picked.length) {
    ElMessage.warning(t('pages.marketingFlow.shipPickRequired'))
    return
  }
  const lines = []
  for (const r of picked) {
    const qty = resolveShipQty(r)
    if (qty == null || qty <= 0) {
      ElMessage.warning(t('pages.marketingFlow.shipQtyRequired'))
      return
    }
    const avail = parseNum(r.qty_available)
    if (avail != null && qty > avail) {
      ElMessage.warning(t('pages.marketingFlow.shipQtyExceedsAvailable', { avail }))
      return
    }
    const bal = parseNum(r.balance_qty)
    if (bal != null && qty > bal + 1e-9 && !withinOvershipTolerance(qty, bal, orderQtyForRow(r))) {
      ElMessage.warning(t('pages.marketingFlow.shipQtyExceedsBalance', { bal }))
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
  const overWip = picked.filter((r) => {
    const q = parseNum(r.qty)
    const wip = parseNum(r.mrp_qty_wip)
    return q != null && wip != null && wip > 0 && q > wip
  })
  if (overWip.length) {
    ElMessage.warning(t('pages.marketingFlow.scheduleQtyOverWip', { n: overWip.length }))
  }
  const overBalTol = picked.filter((r) => {
    const q = resolveShipQty(r)
    const bal = parseNum(r.balance_qty)
    return q != null && bal != null && q > bal + 1e-9 && withinOvershipTolerance(q, bal, orderQtyForRow(r))
  })
  if (overBalTol.length) {
    ElMessage.info(t('pages.marketingFlow.shipQtyOverBalanceTolerance', { n: overBalTol.length }))
  }
  if (shipSoCount.value > 1) {
    try {
      await ElMessageBox.confirm(
        t('pages.marketingFlow.shipOneSjConfirm', { n: shipSoCount.value }),
        t('pages.marketingFlow.shipDialogTitle'),
        { type: 'info', confirmButtonText: t('pages.marketingFlow.shipConfirm') },
      )
    } catch {
      return
    }
  }
  savingShip.value = true
  try {
    const res = await createOutstandingShipBatch({ lines })
    const ids = Array.isArray(res.delivery_ids) ? res.delivery_ids.map(Number).filter((id) => id > 0) : []
    const numbers = Array.isArray(res.delivery_numbers)
      ? res.delivery_numbers.map((n) => String(n || '').trim()).filter(Boolean)
      : []
    emit('update:shipVisible', false)
    emit('done', { deliveryIds: ids, deliveryNumbers: numbers })

    if (!ids.length) {
      ElMessage.success(res.message || t('pages.marketingFlow.shipSaved'))
      return
    }

    const sjList = (numbers.length ? numbers : ids.map((id) => `#${id}`)).join(', ')
    ElMessage.success(t('pages.marketingFlow.shipSavedWithSj', { n: ids.length }))

    try {
      await ElMessageBox.confirm(
        t('pages.marketingFlow.shipHandoffMessage', { n: ids.length, sjList }),
        t('pages.marketingFlow.shipHandoffTitle'),
        {
          type: 'success',
          confirmButtonText: t('pages.marketingFlow.shipHandoffOpenDelivery'),
          cancelButtonText: t('pages.marketingFlow.shipHandoffPrint'),
          distinguishCancelAndClose: true,
          closeOnClickModal: false,
        },
      )
      router.push({ path: '/admin/delivery', query: { delivery_id: String(ids[0]) } })
    } catch (action) {
      if (action === 'cancel') {
        try {
          for (const id of ids) {
            await fetchAuthenticatedDocument(`/documents/surat-jalan/${id}`, { mode: 'open' })
            await fetchAuthenticatedDocument(`/documents/invpl-by-delivery/${id}`, { mode: 'open' })
          }
        } catch (printErr) {
          ElMessage.error(printErr?.message || t('common.errorGeneric'))
        }
      }
      // close / stay — list already refreshed via emit('done')
    }
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
  align-items: center;
  justify-content: flex-end;
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
.out-dlg-plan-date {
  width: 100%;
}
.inline-flex {
  display: inline-flex;
}
.gap-2 {
  gap: 0.5rem;
}
</style>
