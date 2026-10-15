<template>
  <component :is="embedded ? 'div' : 'el-dialog'" v-bind="shellProps">
    <div class="mrp-pack-wip-bar mb-3 flex flex-wrap gap-3 items-end">
      <div class="mrp-pack-wip-bar__field">
        <label class="mrp-pack-wip-bar__label">{{ t('pages.mrpPacking.wip') }}</label>
        <el-autocomplete
          v-model="wipInput"
          class="mrp-pack-wip-bar__input"
          clearable
          :trigger-on-focus="true"
          :fetch-suggestions="fetchWipSuggestions"
          :placeholder="t('pages.mrpPacking.wipInputPlaceholder')"
          @keyup.enter="applyWipFilter"
          @select="onWipAutocompleteSelect"
        />
      </div>
      <el-button type="primary" :loading="loading" @click="applyWipFilter">
        {{ t('pages.mrpPacking.wipProses') }}
      </el-button>
    </div>

    <div class="mb-3 flex flex-wrap gap-2 items-center">
      <el-radio-group v-model="sourceMode" size="small" @change="onSourceModeChange">
        <el-radio-button value="rpi">{{ t('pages.mrpPacking.sourceModeRpi') }}</el-radio-button>
        <el-radio-button value="sisa">{{ t('pages.mrpPacking.sourceModeSisa') }}</el-radio-button>
      </el-radio-group>
    </div>

    <div class="mrp-pack-create-layout" :class="{ 'mrp-pack-create-layout--embedded': embedded }">
      <div class="mrp-pack-create-layout__main">
        <p v-if="sourceMode === 'rpi' && !rpiListVisible" class="mrp-pack-wip-hint">
          {{ t('pages.mrpPacking.wipFilterHint') }}
        </p>
        <el-table
          v-if="sourceMode === 'rpi' && rpiListVisible"
          :data="filteredRpiRows"
          v-loading="loading"
          border
          stripe
          size="small"
          class="admin-table"
          highlight-current-row
          :empty-text="t('common.tableEmpty')"
          @current-change="onRowSelect"
        >
          <el-table-column prop="kode_rencana_item" :label="t('pages.mrpPacking.colRpi')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="lot_no" :label="t('pages.mrpPacking.lotNo')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="deskripsi" :label="t('pages.mrpPacking.colDeskripsi')" min-width="140" show-overflow-tooltip />
          <el-table-column prop="material_name" :label="t('pages.mrpPacking.colMaterial')" min-width="100" show-overflow-tooltip />
          <el-table-column :label="t('pages.mrpPacking.colQtyRpi')" width="90" align="right">
            <template #default="{ row }">{{ formatQty(row.qty_rpi) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpPacking.colQtyActual')" width="95" align="right">
            <template #default="{ row }">{{ formatQty(row.qty_actual) }}</template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="112" align="center" fixed="right">
            <template #default="{ row }">
              <span @click.stop>
                <AdminTableActions
                  :show-view="true"
                  :view-label="t('pages.mrpPacking.rollHistoryTitle')"
                  :more-items="[
                    { command: 'play', label: t('pages.mrpPacking.playSession'), icon: VideoPlay },
                    {
                      command: 'stop',
                      label: t('pages.mrpPacking.stopSession'),
                      icon: VideoPause,
                      disabled: activeRowKey !== rowKey(row),
                    },
                    {
                      command: 'ukur-sisa',
                      label: t('pages.mrpPacking.startSisaMeasure'),
                      icon: Odometer,
                      divided: true,
                    },
                  ]"
                  @view="openRollHistory(row)"
                  @more="(cmd) => onPendingMore(cmd, row)"
                />
              </span>
            </template>
          </el-table-column>
        </el-table>

        <el-table
          v-else
          :data="sisaRows"
          v-loading="loading"
          border
          stripe
          size="small"
          class="admin-table"
          highlight-current-row
          :empty-text="t('pages.mrpPacking.sisaApprovedEmpty')"
          @current-change="onSisaSelect"
        >
          <el-table-column :label="t('pages.mrpPacking.sisaColId')" width="70" align="center">
            <template #default="{ row }">{{ row.id }}</template>
          </el-table-column>
          <el-table-column prop="sumber" :label="t('pages.mrpGudangSisa.sumber')" width="90" align="center" />
          <el-table-column prop="barcode" :label="t('pages.mrpGudangSisa.barcode')" min-width="120" show-overflow-tooltip />
          <el-table-column prop="lot" :label="t('pages.mrpGudangSisa.lot')" min-width="100" show-overflow-tooltip />
          <el-table-column :label="t('pages.mrpGudangSisa.qty')" width="90" align="right">
            <template #default="{ row }">{{ formatQty(row.qty) }}</template>
          </el-table-column>
          <el-table-column label="PO" width="80" align="center">
            <template #default="{ row }">{{ row.po_id || '—' }}</template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="112" align="center" fixed="right">
            <template #default="{ row }">
              <span @click.stop>
                <AdminTableActions
                  :more-items="[
                    { command: 'play', label: t('pages.mrpPacking.playSession'), icon: VideoPlay },
                    {
                      command: 'stop',
                      label: t('pages.mrpPacking.stopSession'),
                      icon: VideoPause,
                      disabled: activeRowKey !== sisaRowKey(row),
                    },
                  ]"
                  @more="(cmd) => onSisaMore(cmd, row)"
                />
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="mrp-pack-create-layout__side">
        <div v-if="showWipQtyCard" class="mrp-pack-wip-card">
          <div class="mrp-pack-wip-card__label">{{ t('pages.mrpPacking.colQtyWip') }}</div>
          <div class="mrp-pack-wip-card__value">{{ formatQty(activeWipQty) }}</div>
          <div v-if="activeRow?.lot_no" class="mrp-pack-wip-card__meta">
            {{ t('pages.mrpPacking.lotNo') }}: {{ dash(activeRow.lot_no) }}
          </div>
        </div>
        <MrpPackingUkurPanel
        :rows="ukurRows"
        :total-size="ukurTotalSize"
        :total-qty="ukurRows.length"
        :packing-no="kodePacking"
        :lot-no="lotNo"
        :factory-so="factorySo"
        :roll-no="rollNo"
        :online="scaleOnline"
        :active="sessionActive"
        :can-start="sessionActive && !scaleOnline"
        :can-stop="sessionActive && scaleOnline"
        :can-add="sessionActive && scaleOnline"
        :can-edit="sessionActive && scaleOnline"
        :can-delete="sessionActive && scaleOnline"
        :can-print-roll="sessionKind !== 'sisa' && sessionActive && ukurRows.length > 0 && !printing"
        :show-print-roll="sessionKind !== 'sisa'"
        :can-view-rolls="sessionKind !== 'sisa' && sessionActive"
        :can-finish="canFinishSession"
        :finishing="finishing"
        :hint="sessionHint"
        :title="sessionKind === 'sisa' ? t('pages.mrpPacking.sisaMeasureTitle') : ''"
        :finish-label="sessionKind === 'sisa' ? t('pages.mrpPacking.sisaMeasureFinish') : ''"
        @start="panelStart"
        @stop="panelStop"
        @add="panelAddUkur"
        @edit="panelEditUkur"
        @delete="panelDeleteUkur"
        @print-roll="printRollLabel"
        @cancel="cancelSession"
        @finish="finishLot"
        @view-rolls="openActiveRollHistory"
        />
      </div>
    </div>

    <el-dialog
      v-model="rollHistoryOpen"
      :title="t('pages.mrpPacking.rollHistoryTitle')"
      width="760px"
      destroy-on-close
      append-to-body
    >
      <p v-if="rollHistoryRow" class="text-sm text-slate-500 mb-3">
        {{ rollHistoryRow.kode_rencana_item }} · {{ dash(rollHistoryRow.lot_no) }} · {{ dash(rollHistoryRow.no_so) }}
      </p>
      <el-table :data="rollHistoryRows" v-loading="rollHistoryLoading" border size="small" :empty-text="t('common.tableEmpty')">
        <el-table-column prop="roll_no" :label="t('pages.mrpPacking.rollNo')" width="70" align="center" />
        <el-table-column prop="kode_packing" :label="t('pages.mrpPacking.kodePacking')" min-width="140" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpPacking.pieces')" width="70" align="right">
          <template #default="{ row }">{{ formatQty(row.lembar) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpPacking.quantity')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.ukuran) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="130">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="112" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions
              :show-view="true"
              :view-label="t('pages.mrpPacking.viewRollSizes')"
              :more-items="[{ command: 'reprint', label: t('pages.mrpPacking.reprintRollLabel'), icon: Printer }]"
              @view="openRollSizes(row)"
              @more="(cmd) => cmd === 'reprint' && reprintRollLabel(row)"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog
      v-model="rollSizesOpen"
      :title="rollSizesTitle"
      width="420px"
      destroy-on-close
      append-to-body
    >
      <p v-if="rollSizesRow" class="text-sm text-slate-500 mb-3">
        {{ dash(rollSizesRow.kode_packing) }} · Roll #{{ rollSizesRow.roll_no }}
      </p>
      <el-table :data="rollSizesItems" border size="small" :empty-text="t('common.tableEmpty')">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column :label="t('pages.mrpProses.sizeUkur')" align="right">
          <template #default="{ row }">{{ formatQty(row.size_val) }}</template>
        </el-table-column>
      </el-table>
      <p v-if="rollSizesRow?.sizes_text" class="text-sm mt-3 mb-0">
        {{ t('pages.mrpPacking.rollSizesSum') }}: <strong>{{ rollSizesRow.sizes_text }}</strong>
      </p>
    </el-dialog>
  </component>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Odometer, Printer, VideoPause, VideoPlay } from '@element-plus/icons-vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import MrpPackingUkurPanel from './MrpPackingUkurPanel.vue'
import { mrpPackingAction, mrpPackingPendingRpi, mrpPackingPrintedRolls, mrpPackingRollLabel, mrpPackingUkurSisa, mrpStartPacking, mrpStockSisaList } from '../../../api/client'
import { normalizePageResult } from '../../../utils/tableQuery'
import { printMrpPackingRollLabel } from '../../../utils/mrpPackingRollLabelPrint'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  embedded: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'saved'])

const { t } = useI18n()

const shellProps = computed(() => {
  if (props.embedded) return { class: 'mrp-pack-workspace' }
  return {
    modelValue: props.modelValue,
    title: t('pages.mrpPacking.createTitle'),
    width: '1280px',
    destroyOnClose: true,
    appendToBody: true,
    class: 'mrp-pack-create-dialog',
    'onUpdate:modelValue': (v) => emit('update:modelValue', v),
  }
})
const loading = ref(false)
const starting = ref(false)
const printing = ref(false)
const finishing = ref(false)
const sourceMode = ref('rpi')
const rpiRowsAll = ref([])
const wipInput = ref('')
const appliedWip = ref('')
const rpiListVisible = ref(false)
const sisaRows = ref([])
const activeRow = ref(null)
const activeRowKey = ref('')
const packingId = ref(null)
const kodePacking = ref('')
const lotNo = ref('')
const factorySo = ref('')
const rollNo = ref(1)
const scaleOnline = ref(false)
const ukurRows = ref([])
const sessionKind = ref('')
const rollHistoryOpen = ref(false)
const rollHistoryLoading = ref(false)
const rollHistoryRow = ref(null)
const rollHistoryRows = ref([])
const rollSizesOpen = ref(false)
const rollSizesRow = ref(null)
const reprintingRollId = ref(null)
let ukurSeq = 0

const rollSizesTitle = computed(() => {
  const n = rollSizesRow.value?.roll_no
  return n ? t('pages.mrpPacking.rollSizesDetailTitle', { roll: n }) : t('pages.mrpPacking.viewRollSizes')
})
const rollSizesItems = computed(() => {
  const row = rollSizesRow.value
  if (!row) return []
  const sizes = Array.isArray(row.sizes) ? row.sizes : parseSizesText(row.sizes_text)
  return sizes.map((size_val, idx) => ({ id: idx, size_val }))
})

const wipUnfinishedOptions = computed(() => {
  const byKey = new Map()
  for (const row of rpiRowsAll.value) {
    for (const raw of [row.kode_wip, row.prep_kode_wip, row.kode_lot_wip, row.lot_no]) {
      const code = String(raw || '').trim()
      if (!code) continue
      const key = code.toUpperCase()
      if (!byKey.has(key)) byKey.set(key, { value: code })
    }
  }
  return [...byKey.values()].sort((a, b) => a.value.localeCompare(b.value))
})

const filteredRpiRows = computed(() => {
  const q = normalizeWipToken(appliedWip.value)
  if (!q) return []
  return rpiRowsAll.value.filter((row) => rowMatchesWip(row, q))
})

const sessionActive = computed(() => {
  if (!activeRowKey.value) return false
  if (sessionKind.value === 'sisa') return true
  return !!packingId.value
})
const ukurTotalSize = computed(() =>
  ukurRows.value.reduce((sum, row) => sum + (Number(row.size_val) || 0), 0),
)
function packingQtyBalance(row) {
  const wip = Number(row?.qty_wip ?? row?.prep_total_size ?? 0)
  const actual = Number(row?.qty_actual || 0)
  return { wip, actual, shortfall: wip - actual }
}

function packingCanFinishRow(row) {
  if (!row?.rencana_item_id) return true
  const { wip, actual } = packingQtyBalance(row)
  if (actual <= 0) return false
  if (!Number.isFinite(wip) || wip <= 0) return true
  return actual <= wip + 1e-9
}

const canFinishSession = computed(() => {
  if (!sessionActive.value || finishing.value) return false
  if (sessionKind.value === 'sisa') return ukurRows.value.length > 0
  if (!packingId.value || !activeRow.value) return false
  return packingCanFinishRow(activeRow.value)
})
const activeWipQty = computed(() => {
  if (!activeRow.value || sourceMode.value !== 'rpi') return 0
  return packingQtyBalance(activeRow.value).wip
})

const showWipQtyCard = computed(() =>
  sourceMode.value === 'rpi' && !!activeRow.value?.rencana_item_id,
)

const sessionHint = computed(() => {
  if (sessionKind.value === 'sisa' && sessionActive.value && !ukurRows.value.length) {
    return t('pages.mrpPacking.sisaMeasureHint')
  }
  if (sessionActive.value && sessionKind.value === 'packing' && activeRow.value) {
    const { wip, actual, shortfall } = packingQtyBalance(activeRow.value)
    if (Number.isFinite(wip) && wip > 0 && shortfall > 0.009) {
      return t('pages.mrpPacking.finishShortfallHint', {
        actual: formatQty(actual),
        wip: formatQty(wip),
        selisih: formatQty(shortfall),
      })
    }
    if (Number.isFinite(wip) && wip > 0 && actual > wip + 1e-9) {
      return t('pages.mrpPacking.finishActualExceedsWip', {
        actual: formatQty(actual),
        wip: formatQty(wip),
      })
    }
  }
  if (sessionActive.value) return ''
  return t('pages.mrpPacking.playHint')
})

watch(
  () => props.modelValue,
  (open) => {
    if (!props.embedded && open) {
      reloadWorkspace()
    }
  },
)

onMounted(() => {
  if (props.embedded) {
    reloadWorkspace()
  }
})

defineExpose({ reload: reloadWorkspace })

function rowKey(row) {
  if (row._localKey) return row._localKey
  const parts = [row.rencana_item_id, row.po_id, row.lot_no].filter((x) => x != null && x !== '')
  return parts.length ? parts.join(':') : String(row.lot_no || '')
}

function sisaRowKey(row) {
  return `sisa-${row.id}`
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '0.00'
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function formatDateTime(v) {
  if (!v) return '—'
  return String(v).replace('T', ' ').slice(0, 19)
}

function parseSizesText(text) {
  if (!text) return []
  return String(text)
    .split('+')
    .map((s) => Number(s.trim()))
    .filter((n) => Number.isFinite(n) && n > 0)
}

function resetSession() {
  activeRow.value = null
  activeRowKey.value = ''
  sessionKind.value = ''
  packingId.value = null
  kodePacking.value = ''
  lotNo.value = ''
  factorySo.value = ''
  rollNo.value = 1
  scaleOnline.value = false
  ukurRows.value = []
}

function resetWipFilter() {
  wipInput.value = ''
  appliedWip.value = ''
  rpiListVisible.value = false
}

function normalizeWipToken(v) {
  return String(v || '').trim().toUpperCase()
}

function rowWipTokens(row) {
  return [row.kode_wip, row.prep_kode_wip, row.kode_lot_wip, row.lot_no]
    .map((f) => normalizeWipToken(f))
    .filter(Boolean)
}

function rowMatchesWip(row, q) {
  const tokens = rowWipTokens(row)
  return tokens.some((tok) => tok === q || tok.includes(q))
}

function fetchWipSuggestions(queryString, cb) {
  const q = normalizeWipToken(queryString)
  let list = wipUnfinishedOptions.value
  if (q) {
    list = list.filter((item) => normalizeWipToken(item.value).includes(q))
  }
  cb(list.slice(0, 50))
}

function onWipAutocompleteSelect(item) {
  if (item?.value) wipInput.value = item.value
}

async function applyWipFilter() {
  if (sourceMode.value !== 'rpi') {
    sourceMode.value = 'rpi'
  }
  const wip = String(wipInput.value || '').trim()
  if (!wip) {
    ElMessage.warning(t('pages.mrpPacking.wipRequired'))
    return
  }
  if (!rpiRowsAll.value.length) {
    await loadPendingRpi()
  }
  appliedWip.value = wip
  rpiListVisible.value = true
  if (!filteredRpiRows.value.length) {
    ElMessage.warning(t('pages.mrpPacking.wipNotFound', { wip }))
  }
}

async function loadPendingRpi() {
  loading.value = true
  try {
    const data = await mrpPackingPendingRpi()
    rpiRowsAll.value = (data || []).map((row) => ({ ...row }))
    if (rpiListVisible.value && appliedWip.value && !filteredRpiRows.value.length) {
      ElMessage.warning(t('pages.mrpPacking.wipNotFound', { wip: appliedWip.value }))
    }
  } catch (e) {
    rpiRowsAll.value = []
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function loadApprovedSisa() {
  loading.value = true
  try {
    const data = await mrpStockSisaList({ status: 'approved', page: 1, page_size: 200 })
    sisaRows.value = normalizePageResult(data).items
  } catch (e) {
    sisaRows.value = []
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function reloadWorkspace() {
  resetSession()
  resetWipFilter()
  await loadPendingRpi()
  if (sourceMode.value === 'sisa') await loadApprovedSisa()
}

function onSourceModeChange() {
  reloadWorkspace()
}

function onRowSelect(row) {
  if (row) activeRow.value = row
}

function onSisaSelect(row) {
  if (row) activeRow.value = row
}

async function playRow(row) {
  starting.value = true
  try {
    const body = row.rencana_item_id
      ? {
          rencana_item_id: row.rencana_item_id,
          po_id: row.po_id || null,
          no_po: row.no_po || null,
          no_so: row.no_so || null,
        }
      : {
          kode_wip: row.lot_no,
          no_po: row.no_po,
          no_so: row.no_so || '',
          po_id: row.po_id || null,
        }
    const res = await mrpStartPacking(body)
    activeRow.value = row
    activeRowKey.value = rowKey(row)
    packingId.value = res.id
    kodePacking.value = res.kode_packing || row.kode_packing || ''
    lotNo.value = row.lot_no || row.so_lot_no || res.kode_wip || ''
    factorySo.value = row.no_so || res.no_so || ''
    rollNo.value = Number(res.next_roll_no || row.next_roll_no || 1)
    sessionKind.value = 'packing'
    scaleOnline.value = false
    ukurRows.value = []
    ElMessage.success(res.message || t('pages.mrpPacking.sessionStarted'))
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    starting.value = false
  }
}

function startSisaMeasure(row) {
  if (packingId.value && sessionKind.value !== 'sisa') {
    ElMessage.warning(t('pages.mrpPacking.sisaMeasureBusy'))
    return
  }
  activeRow.value = row
  activeRowKey.value = rowKey(row)
  sessionKind.value = 'sisa'
  packingId.value = null
  kodePacking.value = row.kode_packing || ''
  lotNo.value = row.lot_no || row.kode_wip || ''
  factorySo.value = row.no_so || ''
  rollNo.value = 1
  scaleOnline.value = false
  ukurRows.value = []
  ElMessage.success(t('pages.mrpPacking.sisaMeasureStarted'))
}

async function playSisaRow(row) {
  starting.value = true
  try {
    const res = await mrpStartPacking({
      source_mode: 'sisa',
      stock_sisa_id: row.id,
      po_id: row.po_id || null,
      qty_sq: row.qty,
    })
    activeRow.value = row
    activeRowKey.value = sisaRowKey(row)
    packingId.value = res.id
    kodePacking.value = res.kode_packing || ''
    lotNo.value = row.barcode || row.lot || res.kode_wip || `SISA-${row.id}`
    factorySo.value = res.no_so || ''
    rollNo.value = Number(res.next_roll_no || 1)
    sessionKind.value = 'packing'
    scaleOnline.value = false
    ukurRows.value = []
    ElMessage.success(res.message || t('pages.mrpPacking.sessionStarted'))
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    starting.value = false
  }
}

function stopRow() {
  scaleOnline.value = false
}

function onPendingMore(cmd, row) {
  if (cmd === 'play') playRow(row)
  else if (cmd === 'stop') stopRow()
  else if (cmd === 'ukur-sisa') startSisaMeasure(row)
}

function onSisaMore(cmd, row) {
  if (cmd === 'play') playSisaRow(row)
  else if (cmd === 'stop') stopRow()
}

function panelStart() {
  if (!sessionActive.value) {
    ElMessage.warning(t('pages.mrpPacking.playHint'))
    return
  }
  scaleOnline.value = true
}

function panelStop() {
  scaleOnline.value = false
}

function panelAddUkur(size) {
  ukurSeq += 1
  ukurRows.value.push({ id: `u-${ukurSeq}`, size_val: size })
}

function panelEditUkur({ row, size }) {
  if (!row || !(size > 0)) return
  row.size_val = size
}

function panelDeleteUkur(row) {
  ukurRows.value = ukurRows.value.filter((r) => r !== row)
}

function cancelSession() {
  resetSession()
}

function labelQtyOverWip() {
  const row = activeRow.value
  if (!row?.rencana_item_id) return null
  const wip = Number(row.qty_wip ?? row.prep_total_size ?? 0)
  const actual = Number(row.qty_actual || 0)
  const measured = ukurTotalSize.value
  if (!Number.isFinite(wip) || !Number.isFinite(actual) || !Number.isFinite(measured)) return null
  if (Math.round((measured + actual) * 100) > Math.round(wip * 100)) {
    return { measured, actual, wip }
  }
  return null
}

async function printRollLabel(extra = {}) {
  if (!packingId.value || !ukurRows.value.length) return
  const over = labelQtyOverWip()
  if (over) {
    ElMessage.warning(
      t('pages.mrpPacking.labelExceedsWip', {
        ukur: formatQty(over.measured),
        actual: formatQty(over.actual),
        wip: formatQty(over.wip),
      }),
    )
    return
  }
  printing.value = true
  try {
    const res = await mrpPackingAction(packingId.value, {
      action: 'print_roll_label',
      sizes: ukurRows.value.map((r) => r.size_val),
      impactiva_grading: extra.impactiva_grading || '',
      moisture: extra.moisture || '',
    })
    printMrpPackingRollLabel(res.label, t)
    ukurRows.value = []
    scaleOnline.value = false
    kodePacking.value = res.kode_packing || kodePacking.value
    rollNo.value = Number(res.next_roll_no || rollNo.value + 1)
    if (activeRow.value) {
      const added = Number(res.label?.ukuran) || 0
      activeRow.value.qty_actual = Number(activeRow.value.qty_actual || 0) + added
      activeRow.value.kode_packing = kodePacking.value
      activeRow.value.next_roll_no = rollNo.value
    }
    if (rollHistoryOpen.value && rollHistoryRow.value) {
      await loadRollHistory(rollHistoryRow.value, false)
    }
    ElMessage.success(res.message || t('pages.mrpPacking.rollPrinted'))
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    printing.value = false
  }
}

async function loadRollHistory(row, openDialog = true) {
  if (!row?.rencana_item_id) {
    ElMessage.warning(t('pages.mrpPacking.rollHistoryEmpty'))
    return
  }
  rollHistoryRow.value = row
  if (openDialog) rollHistoryOpen.value = true
  rollHistoryLoading.value = true
  try {
    rollHistoryRows.value = await mrpPackingPrintedRolls(row.rencana_item_id)
  } catch (e) {
    rollHistoryRows.value = []
    ElMessage.error(e.message || String(e))
  } finally {
    rollHistoryLoading.value = false
  }
}

function openRollHistory(row) {
  loadRollHistory(row, true)
}

function openActiveRollHistory() {
  if (!activeRow.value) {
    ElMessage.warning(t('pages.mrpPacking.playHint'))
    return
  }
  openRollHistory(activeRow.value)
}

function openRollSizes(row) {
  rollSizesRow.value = row
  rollSizesOpen.value = true
}

async function reprintRollLabel(row) {
  if (!row?.id) return
  reprintingRollId.value = row.id
  try {
    const res = await mrpPackingRollLabel(row.id)
    printMrpPackingRollLabel(res.label, t)
    ElMessage.success(t('pages.mrpPacking.reprintOk'))
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    reprintingRollId.value = null
  }
}

async function saveSisaMeasure() {
  const row = activeRow.value
  if (!row?.rencana_item_id || !ukurRows.value.length) {
    ElMessage.warning(t('pages.mrpPacking.sisaMeasureNeedSize'))
    return
  }
  const qty = ukurTotalSize.value
  try {
    await ElMessageBox.confirm(t('pages.mrpPacking.sisaMeasureConfirm', { qty: formatQty(qty) }), {
      type: 'warning',
      confirmButtonText: t('pages.mrpPacking.sisaMeasureFinish'),
    })
  } catch {
    return
  }
  finishing.value = true
  try {
    const res = await mrpPackingUkurSisa({
      rencana_item_id: row.rencana_item_id,
      sizes: ukurRows.value.map((r) => r.size_val),
    })
    ElMessage.success(t('pages.mrpPacking.sisaMeasureSaved', { qty: formatQty(res?.qty ?? qty) }))
    await reloadWorkspace()
    emit('saved')
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    finishing.value = false
  }
}

async function confirmFinishDialogs(row) {
  const { wip, actual, shortfall } = packingQtyBalance(row || {})
  if (row && Number.isFinite(wip) && wip > 0 && actual > wip + 1e-9) {
    ElMessage.warning(
      t('pages.mrpPacking.finishActualExceedsWip', {
        actual: formatQty(actual),
        wip: formatQty(wip),
      }),
    )
    return false
  }
  if (row && Number.isFinite(wip) && wip > 0 && shortfall > 0.009) {
    try {
      await ElMessageBox.confirm(
        t('pages.mrpPacking.finishShortfallConfirm', {
          actual: formatQty(actual),
          wip: formatQty(wip),
          selisih: formatQty(shortfall),
        }),
        { type: 'warning', confirmButtonText: t('pages.mrpPacking.finishLot'), cancelButtonText: t('common.cancel') },
      )
    } catch {
      return false
    }
  }
  try {
    await ElMessageBox.confirm(t('pages.mrpPacking.finishConfirm'), { type: 'warning' })
    return true
  } catch {
    return false
  }
}

async function finishLot() {
  if (sessionKind.value === 'sisa') {
    await saveSisaMeasure()
    return
  }
  if (!packingId.value) return
  const row = activeRow.value
  if (row && !packingCanFinishRow(row)) {
    ElMessage.warning(t('pages.mrpPacking.needRollHint'))
    return
  }
  if (!(await confirmFinishDialogs(row))) return
  finishing.value = true
  try {
    const res = await mrpPackingAction(packingId.value, { action: 'finish' })
    ElMessage.success(res.message || t('pages.mrpPacking.lotFinished'))
    resetSession()
    await reloadWorkspace()
    emit('saved')
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    finishing.value = false
  }
}
</script>

<style scoped>
.mrp-pack-create-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 1rem;
  align-items: start;
}
.mrp-pack-create-layout__main {
  min-width: 0;
}
.mrp-pack-create-layout__side {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.mrp-pack-wip-card {
  margin-bottom: 12px;
  padding: 14px 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
  box-shadow: 0 1px 2px rgb(15 23 42 / 6%);
}
.mrp-pack-wip-card__label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.mrp-pack-wip-card__value {
  margin-top: 4px;
  font-size: 1.625rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  color: var(--el-text-color-primary);
  line-height: 1.2;
}
.mrp-pack-wip-card__meta {
  margin-top: 8px;
  font-size: 0.8125rem;
  color: var(--el-text-color-secondary);
}
.mrp-pack-create-layout--embedded {
  padding: 0;
}
.mrp-pack-workspace {
  width: 100%;
}
@media (max-width: 960px) {
  .mrp-pack-create-layout {
    grid-template-columns: 1fr;
  }
}
.mrp-pack-wip-bar__label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.25rem;
}
.mrp-pack-wip-bar__input {
  width: min(100%, 280px);
}
.mrp-pack-wip-hint {
  margin: 0 0 0.75rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: var(--el-text-color-secondary);
  background: var(--el-fill-color-light);
  border-radius: 6px;
  border: 1px dashed var(--el-border-color);
}
</style>
