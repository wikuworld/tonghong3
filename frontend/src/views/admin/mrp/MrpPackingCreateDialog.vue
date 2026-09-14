<template>
  <component :is="embedded ? 'div' : 'el-dialog'" v-bind="shellProps">
    <div class="mrp-pack-create-layout" :class="{ 'mrp-pack-create-layout--embedded': embedded }">
      <div class="mrp-pack-create-layout__main">
        <el-table
          :data="rpiRows"
          v-loading="loading"
          border
          stripe
          size="small"
          class="admin-table"
          highlight-current-row
          empty-text="—"
          @current-change="onRowSelect"
        >
          <el-table-column prop="kode_rencana_item" :label="t('pages.mrpPacking.colRpi')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="lot_no" :label="t('pages.mrpPacking.lotNo')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="deskripsi" :label="t('pages.mrpPacking.colDeskripsi')" min-width="140" show-overflow-tooltip />
          <el-table-column prop="material_name" :label="t('pages.mrpPacking.colMaterial')" min-width="100" show-overflow-tooltip />
          <el-table-column :label="t('pages.mrpPacking.colQtyRpi')" width="90" align="right">
            <template #default="{ row }">{{ formatQty(row.qty_rpi) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpPacking.colQtyActual')" width="95" align="right">
            <template #default="{ row }">{{ formatQty(row.qty_actual) }}</template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="118" align="center" fixed="right">
            <template #default="{ row }">
              <el-button
                link
                type="info"
                :title="t('pages.mrpPacking.rollHistoryTitle')"
                @click.stop="openRollHistory(row)"
              >
                <el-icon><View /></el-icon>
              </el-button>
              <el-button
                link
                type="success"
                :title="t('pages.mrpPacking.playSession')"
                :loading="starting && activeRowKey === rowKey(row)"
                @click.stop="playRow(row)"
              >
                <el-icon><VideoPlay /></el-icon>
              </el-button>
              <el-button
                link
                type="danger"
                :title="t('pages.mrpPacking.stopSession')"
                :disabled="activeRowKey !== rowKey(row)"
                @click.stop="stopRow"
              >
                <el-icon><VideoPause /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
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
        :can-delete="sessionActive && scaleOnline"
        :can-print-roll="sessionActive && ukurRows.length > 0 && !printing"
        :can-view-rolls="sessionActive"
        :can-finish="sessionActive && !!packingId && !finishing"
        :finishing="finishing"
        :hint="sessionHint"
        @start="panelStart"
        @stop="panelStop"
        @add="panelAddUkur"
        @delete="panelDeleteUkur"
        @print-roll="printRollLabel"
        @cancel="cancelSession"
        @finish="finishLot"
        @view-rolls="openActiveRollHistory"
      />
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
      <el-table :data="rollHistoryRows" v-loading="rollHistoryLoading" border size="small" empty-text="—">
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
        <el-table-column :label="t('common.actions')" width="88" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              link
              type="primary"
              :title="t('pages.mrpPacking.reprintRollLabel')"
              :loading="reprintingRollId === row.id"
              @click="reprintRollLabel(row)"
            >
              <el-icon><Printer /></el-icon>
            </el-button>
            <el-button
              link
              type="info"
              :title="t('pages.mrpPacking.viewRollSizes')"
              @click="openRollSizes(row)"
            >
              <el-icon><List /></el-icon>
            </el-button>
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
      <el-table :data="rollSizesItems" border size="small" empty-text="—">
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
import { List, Printer, VideoPause, VideoPlay, View } from '@element-plus/icons-vue'
import MrpPackingUkurPanel from './MrpPackingUkurPanel.vue'
import { mrpPackingAction, mrpPackingPendingRpi, mrpPackingPrintedRolls, mrpPackingRollLabel, mrpStartPacking } from '../../../api/client'
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
const rpiRows = ref([])
const activeRow = ref(null)
const activeRowKey = ref('')
const packingId = ref(null)
const kodePacking = ref('')
const lotNo = ref('')
const factorySo = ref('')
const rollNo = ref(1)
const scaleOnline = ref(false)
const ukurRows = ref([])
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

const sessionActive = computed(() => !!activeRowKey.value && !!packingId.value)
const ukurTotalSize = computed(() =>
  ukurRows.value.reduce((sum, row) => sum + (Number(row.size_val) || 0), 0),
)
const sessionHint = computed(() => {
  if (sessionActive.value) return ''
  return t('pages.mrpPacking.playHint')
})

watch(
  () => props.modelValue,
  (open) => {
    if (!props.embedded && open) {
      resetSession()
      loadPendingRpi()
    }
  },
)

onMounted(() => {
  if (props.embedded) {
    resetSession()
    loadPendingRpi()
  }
})

defineExpose({ reload: loadPendingRpi })

function rowKey(row) {
  return row._localKey || String(row.rencana_item_id || row.lot_no || '')
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
  packingId.value = null
  kodePacking.value = ''
  lotNo.value = ''
  factorySo.value = ''
  rollNo.value = 1
  scaleOnline.value = false
  ukurRows.value = []
}

async function loadPendingRpi() {
  loading.value = true
  try {
    const data = await mrpPackingPendingRpi()
    rpiRows.value = (data || []).map((row) => ({ ...row }))
  } catch (e) {
    rpiRows.value = []
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

function onRowSelect(row) {
  if (row) activeRow.value = row
}

async function playRow(row) {
  starting.value = true
  try {
    const body = row.rencana_item_id
      ? { rencana_item_id: row.rencana_item_id }
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

function panelDeleteUkur(row) {
  ukurRows.value = ukurRows.value.filter((r) => r !== row)
}

function cancelSession() {
  resetSession()
}

async function printRollLabel() {
  if (!packingId.value || !ukurRows.value.length) return
  printing.value = true
  try {
    const res = await mrpPackingAction(packingId.value, {
      action: 'print_roll_label',
      sizes: ukurRows.value.map((r) => r.size_val),
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

async function finishLot() {
  if (!packingId.value) return
  try {
    await ElMessageBox.confirm(t('pages.mrpPacking.finishConfirm'), { type: 'warning' })
  } catch {
    return
  }
  finishing.value = true
  try {
    const res = await mrpPackingAction(packingId.value, { action: 'finish' })
    ElMessage.success(res.message || t('pages.mrpPacking.lotFinished'))
    resetSession()
    await loadPendingRpi()
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
</style>
