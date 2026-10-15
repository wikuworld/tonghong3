<template>
  <aside class="mrp-pack-ukur-panel" :class="{ 'is-inactive': !active }">
    <h3 class="mrp-pack-ukur-panel__title">{{ title || t('pages.mrpPacking.ukurFormTitle') }}</h3>

    <div class="mrp-pack-ukur-panel__meta">
      <div class="mrp-pack-ukur-panel__meta-row">
        <span>{{ t('pages.mrpProses.scaleStatus') }}:</span>
        <strong>{{ online ? t('pages.mrpProses.scaleOnline') : t('pages.mrpProses.scaleOffline') }}</strong>
      </div>
      <div class="mrp-pack-ukur-panel__meta-row">
        <span>{{ t('pages.mrpPacking.kodePacking') }}:</span>
        <strong>{{ dash(packingNo) }}</strong>
      </div>
      <div class="mrp-pack-ukur-panel__meta-row">
        <span>{{ t('pages.mrpPacking.lotNo') }}:</span>
        <strong>{{ dash(lotNo) }}</strong>
      </div>
      <div class="mrp-pack-ukur-panel__meta-row">
        <span>{{ t('pages.mrpPacking.factorySo') }}:</span>
        <strong>{{ dash(factorySo) }}</strong>
      </div>
      <div class="mrp-pack-ukur-panel__meta-row">
        <span>{{ t('pages.mrpProses.totalSize') }}:</span>
        <strong>{{ formatQty(totalSize) }}</strong>
      </div>
      <div class="mrp-pack-ukur-panel__meta-row">
        <span>{{ t('pages.mrpProses.totalQty') }}:</span>
        <strong>{{ totalQty }}</strong>
      </div>
      <div class="mrp-pack-ukur-panel__meta-row">
        <span>{{ t('pages.mrpPacking.rollNo') }}:</span>
        <strong>{{ rollNo }}</strong>
      </div>
    </div>

    <div class="mrp-pack-ukur-panel__actions">
      <el-button size="small" class="mrp-pack-ukur-btn mrp-pack-ukur-btn--start" :disabled="!canStart" @click="$emit('start')">
        {{ t('pages.mrpProses.panelStart') }}
      </el-button>
      <el-button size="small" class="mrp-pack-ukur-btn mrp-pack-ukur-btn--stop" :disabled="!canStop" @click="$emit('stop')">
        {{ t('pages.mrpProses.panelStop') }}
      </el-button>
      <el-button size="small" class="mrp-pack-ukur-btn mrp-pack-ukur-btn--add" :disabled="!canAdd" @click="onAddClick">
        {{ t('pages.mrpProses.panelAdd') }}
      </el-button>
      <el-button
        size="small"
        class="mrp-pack-ukur-btn mrp-pack-ukur-btn--view"
        :disabled="!canViewRolls"
        :title="t('pages.mrpPacking.rollHistoryTitle')"
        @click="$emit('view-rolls')"
      >
        <el-icon><View /></el-icon>
      </el-button>
    </div>

    <div class="mrp-pack-ukur-panel__table-wrap">
      <table class="mrp-pack-ukur-table">
        <thead>
          <tr>
            <th class="is-no">{{ t('common.noLabel') }}</th>
            <th>Size</th>
            <th class="is-action">{{ t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, idx) in rows" :key="rowKey(row, idx)">
            <td class="is-no">{{ idx + 1 }}</td>
            <td>{{ formatQty(row.size_val) }}</td>
            <td class="is-action">
              <AdminTableActions
                :show-edit="canEdit"
                :show-delete="canDelete"
                @edit="onEditClick(row)"
                @delete="$emit('delete', row)"
              />
            </td>
          </tr>
          <tr v-if="!rows.length">
            <td colspan="3" class="is-empty">—</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showPrintRoll" class="mrp-pack-ukur-panel__grade">
      <label>
        <span>{{ t('pages.mrpPacking.impactivaGrading') }}</span>
        <el-input v-model="impactivaGrading" size="small" clearable />
      </label>
      <label>
        <span>{{ t('pages.mrpPacking.moisture') }}</span>
        <el-input v-model="moisture" size="small" clearable placeholder="10,30" />
      </label>
    </div>

    <div class="mrp-pack-ukur-panel__footer">
      <el-button v-if="showPrintRoll" type="primary" :disabled="!canPrintRoll" @click="emitPrintRoll">
        {{ t('pages.mrpPacking.printRollLabel') }}
      </el-button>
      <el-button @click="$emit('cancel')">{{ t('common.cancel') }}</el-button>
      <el-button type="success" :disabled="!canFinish" :loading="finishing" @click="$emit('finish')">
        {{ finishLabel || t('pages.mrpPacking.finishLot') }}
      </el-button>
    </div>

    <p v-if="hint" class="mrp-pack-ukur-panel__hint">{{ hint }}</p>

    <el-dialog v-model="addDialogOpen" :title="t('pages.mrpProses.addUkurTitle')" width="360px" append-to-body destroy-on-close>
      <el-form label-position="top" @submit.prevent="confirmAdd">
        <el-form-item :label="t('pages.mrpProses.sizeUkur')" required>
          <el-input ref="addInputRef" v-model="addDialogValue" type="number" step="0.01" autofocus @keyup.enter="confirmAdd" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="confirmAdd">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogOpen" :title="t('pages.mrpProses.editUkurTitle')" width="360px" append-to-body destroy-on-close>
      <el-form label-position="top" @submit.prevent="confirmEdit">
        <el-form-item :label="t('pages.mrpProses.sizeUkur')" required>
          <el-input ref="editInputRef" v-model="editDialogValue" type="number" step="0.01" autofocus @keyup.enter="confirmEdit" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="confirmEdit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </aside>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { View } from '@element-plus/icons-vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'

defineProps({
  rows: { type: Array, default: () => [] },
  totalSize: { type: Number, default: 0 },
  totalQty: { type: Number, default: 0 },
  packingNo: { type: String, default: '' },
  lotNo: { type: String, default: '' },
  factorySo: { type: String, default: '' },
  rollNo: { type: Number, default: 1 },
  online: { type: Boolean, default: false },
  active: { type: Boolean, default: false },
  canStart: { type: Boolean, default: false },
  canStop: { type: Boolean, default: false },
  canAdd: { type: Boolean, default: false },
  canEdit: { type: Boolean, default: false },
  canDelete: { type: Boolean, default: false },
  canPrintRoll: { type: Boolean, default: false },
  canViewRolls: { type: Boolean, default: false },
  canFinish: { type: Boolean, default: false },
  finishing: { type: Boolean, default: false },
  hint: { type: String, default: '' },
  title: { type: String, default: '' },
  finishLabel: { type: String, default: '' },
  showPrintRoll: { type: Boolean, default: true },
})

const emit = defineEmits(['start', 'stop', 'add', 'edit', 'delete', 'print-roll', 'cancel', 'finish', 'view-rolls'])

const { t } = useI18n()
const impactivaGrading = ref('')
const moisture = ref('')

function emitPrintRoll() {
  emit('print-roll', {
    impactiva_grading: impactivaGrading.value.trim(),
    moisture: moisture.value.trim(),
  })
}
const addDialogOpen = ref(false)
const addDialogValue = ref('')
const addInputRef = ref(null)
const editDialogOpen = ref(false)
const editDialogValue = ref('')
const editDialogRow = ref(null)
const editInputRef = ref(null)

watch(addDialogOpen, async (open) => {
  if (!open) return
  addDialogValue.value = ''
  await nextTick()
  addInputRef.value?.focus?.()
})

watch(editDialogOpen, async (open) => {
  if (!open) {
    editDialogRow.value = null
    return
  }
  const n = Number(editDialogRow.value?.size_val)
  editDialogValue.value = Number.isFinite(n) ? String(n) : ''
  await nextTick()
  editInputRef.value?.focus?.()
})

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '0.00'
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function onAddClick() {
  addDialogOpen.value = true
}

function confirmAdd() {
  const size = Number(addDialogValue.value)
  if (!(size > 0)) {
    ElMessage.warning(t('pages.mrpProses.sizeUkur'))
    return
  }
  emit('add', size)
  addDialogOpen.value = false
}

function onEditClick(row) {
  editDialogRow.value = row
  editDialogOpen.value = true
}

function confirmEdit() {
  const row = editDialogRow.value
  if (!row) return
  const size = Number(editDialogValue.value)
  if (!(size > 0)) {
    ElMessage.warning(t('pages.mrpProses.sizeUkur'))
    return
  }
  emit('edit', { row, size })
  editDialogOpen.value = false
}

function rowKey(row, idx) {
  return row.id ?? row.key ?? idx
}
</script>

<style scoped>
.mrp-pack-ukur-panel {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  background: var(--el-fill-color-blank);
  padding: 0.85rem;
  min-width: 340px;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.mrp-pack-ukur-panel.is-inactive { opacity: 0.72; }
.mrp-pack-ukur-panel__title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
}
.mrp-pack-ukur-panel__meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.35rem 0.75rem;
  font-size: 0.78rem;
}
.mrp-pack-ukur-panel__meta-row strong { margin-left: 0.25rem; }
.mrp-pack-ukur-panel__actions {
  display: flex;
  flex-wrap: nowrap;
  gap: 0.25rem;
}
.mrp-pack-ukur-btn {
  border: none;
  color: #fff;
  font-weight: 700;
  font-size: 0.68rem;
  padding: 5px 8px;
}
.mrp-pack-ukur-btn--start {
  --el-button-bg-color: #22c55e;
  --el-button-border-color: #22c55e;
}
.mrp-pack-ukur-btn--stop {
  --el-button-bg-color: #ef4444;
  --el-button-border-color: #ef4444;
}
.mrp-pack-ukur-btn--add {
  --el-button-bg-color: #8b5cf6;
  --el-button-border-color: #8b5cf6;
}
.mrp-pack-ukur-btn--view {
  --el-button-bg-color: #0ea5e9;
  --el-button-border-color: #0ea5e9;
  min-width: 32px;
  padding-left: 8px;
  padding-right: 8px;
}
.mrp-pack-ukur-panel__table-wrap {
  flex: 1;
  min-height: 180px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: auto;
}
.mrp-pack-ukur-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}
.mrp-pack-ukur-table th,
.mrp-pack-ukur-table td {
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding: 0.55rem 0.65rem;
}
.mrp-pack-ukur-table th { background: var(--el-fill-color-light); font-weight: 600; }
.mrp-pack-ukur-table td.is-no,
.mrp-pack-ukur-table th.is-no { width: 48px; text-align: center; }
.mrp-pack-ukur-table td.is-action,
.mrp-pack-ukur-table th.is-action { width: 112px; text-align: center; }
.mrp-pack-ukur-table td.is-empty { text-align: center; color: var(--el-text-color-secondary); }
.mrp-pack-ukur-panel__grade {
  display: grid;
  gap: 0.35rem;
}
.mrp-pack-ukur-panel__grade label {
  display: grid;
  gap: 0.15rem;
  font-size: 0.75rem;
}
.mrp-pack-ukur-panel__footer {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.mrp-pack-ukur-panel__hint {
  margin: 0;
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}
</style>
