<template>
  <aside class="mrp-proses-ukur-panel" :class="{ 'is-inactive': !active }">
    <h3 class="mrp-proses-ukur-panel__title">{{ title || t('pages.mrpProses.ukurFormTitle') }}</h3>

    <div class="mrp-proses-ukur-panel__head">
      <div class="mrp-proses-ukur-panel__status">
        {{ t('pages.mrpProses.scaleStatus') }}:
        <strong>{{ online ? t('pages.mrpProses.scaleOnline') : t('pages.mrpProses.scaleOffline') }}</strong>
      </div>
      <div class="mrp-proses-ukur-panel__totals">
        <div class="mrp-proses-ukur-panel__total-size">
          {{ t('pages.mrpProses.totalSize') }}: {{ formatQty(totalSize) }}
        </div>
        <div class="mrp-proses-ukur-panel__total-qty">
          {{ t('pages.mrpProses.totalQty') }}: {{ totalQty }}
        </div>
      </div>
    </div>

    <div class="mrp-proses-ukur-panel__actions">
      <el-button
        size="small"
        class="mrp-proses-ukur-btn mrp-proses-ukur-btn--start"
        :disabled="!canStart"
        @click="$emit('start')"
      >
        {{ t('pages.mrpProses.panelStart') }}
      </el-button>
      <el-button
        size="small"
        class="mrp-proses-ukur-btn mrp-proses-ukur-btn--stop"
        :disabled="!canStop"
        @click="$emit('stop')"
      >
        {{ t('pages.mrpProses.panelStop') }}
      </el-button>
      <el-button
        size="small"
        class="mrp-proses-ukur-btn mrp-proses-ukur-btn--add"
        :disabled="!canAdd"
        @click="onAddClick"
      >
        {{ t('pages.mrpProses.panelAdd') }}
      </el-button>
      <el-button
        size="small"
        class="mrp-proses-ukur-btn mrp-proses-ukur-btn--print"
        :disabled="!canPrint"
        @click="$emit('print')"
      >
        {{ t('pages.mrpProses.panelLabel') }}
      </el-button>
      <el-button
        size="small"
        class="mrp-proses-ukur-btn mrp-proses-ukur-btn--save"
        :disabled="!canSave"
        @click="$emit('save')"
      >
        {{ t('pages.mrpProses.panelSave') }}
      </el-button>
    </div>

    <div class="mrp-proses-ukur-panel__table-wrap">
      <table class="mrp-proses-ukur-table">
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
              <button
                type="button"
                class="mrp-proses-ukur-delete"
                :disabled="!canDelete"
                :title="t('common.delete')"
                @click="$emit('delete', row)"
              >
                <el-icon><Delete /></el-icon>
              </button>
            </td>
          </tr>
          <tr v-if="!rows.length">
            <td colspan="3" class="is-empty">—</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="hint" class="mrp-proses-ukur-panel__hint">{{ hint }}</p>

    <el-dialog
      v-model="addDialogOpen"
      :title="t('pages.mrpProses.addUkurTitle')"
      width="360px"
      append-to-body
      destroy-on-close
    >
      <el-form label-position="top" @submit.prevent="confirmAdd">
        <el-form-item :label="t('pages.mrpProses.sizeUkur')" required>
          <el-input
            ref="addInputRef"
            v-model="addDialogValue"
            type="number"
            step="0.01"
            autofocus
            @keyup.enter="confirmAdd"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="addDialogOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="confirmAdd">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </aside>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'

const props = defineProps({
  title: { type: String, default: '' },
  rows: { type: Array, default: () => [] },
  totalSize: { type: Number, default: 0 },
  totalQty: { type: Number, default: 0 },
  online: { type: Boolean, default: false },
  active: { type: Boolean, default: true },
  canStart: { type: Boolean, default: true },
  canStop: { type: Boolean, default: true },
  canAdd: { type: Boolean, default: true },
  canPrint: { type: Boolean, default: true },
  canSave: { type: Boolean, default: true },
  canDelete: { type: Boolean, default: true },
  hint: { type: String, default: '' },
})

const emit = defineEmits(['start', 'stop', 'add', 'print', 'save', 'delete'])

const { t } = useI18n()
const addDialogOpen = ref(false)
const addDialogValue = ref('')
const addInputRef = ref(null)

watch(addDialogOpen, async (open) => {
  if (!open) return
  addDialogValue.value = ''
  await nextTick()
  addInputRef.value?.focus?.()
})

function onAddClick() {
  if (!props.canAdd) return
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

function rowKey(row, idx) {
  return row.id ?? row.key ?? idx
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '0.00'
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
</script>

<style scoped>
.mrp-proses-ukur-panel {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  background: var(--el-fill-color-blank);
  padding: 0.85rem;
  min-width: 320px;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.mrp-proses-ukur-panel.is-inactive {
  opacity: 0.72;
}
.mrp-proses-ukur-panel__title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
}
.mrp-proses-ukur-panel__head {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
  align-items: flex-start;
}
.mrp-proses-ukur-panel__status {
  font-size: 0.8rem;
  color: var(--el-text-color-primary);
}
.mrp-proses-ukur-panel__totals {
  text-align: right;
}
.mrp-proses-ukur-panel__total-size {
  font-size: 1.1rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--el-text-color-primary);
}
.mrp-proses-ukur-panel__total-qty {
  font-size: 0.8rem;
  color: var(--el-text-color-secondary);
  margin-top: 0.15rem;
}
.mrp-proses-ukur-panel__actions {
  display: flex;
  flex-wrap: nowrap;
  gap: 0.25rem;
}
.mrp-proses-ukur-btn {
  border: none;
  color: #fff;
  font-weight: 700;
  letter-spacing: 0.01em;
  min-width: 0;
  padding: 5px 8px;
  font-size: 0.68rem;
}
.mrp-proses-ukur-btn--start {
  --el-button-bg-color: #22c55e;
  --el-button-border-color: #22c55e;
  --el-button-hover-bg-color: #16a34a;
  --el-button-hover-border-color: #16a34a;
}
.mrp-proses-ukur-btn--stop {
  --el-button-bg-color: #ef4444;
  --el-button-border-color: #ef4444;
  --el-button-hover-bg-color: #dc2626;
  --el-button-hover-border-color: #dc2626;
}
.mrp-proses-ukur-btn--add {
  --el-button-bg-color: #8b5cf6;
  --el-button-border-color: #8b5cf6;
  --el-button-hover-bg-color: #7c3aed;
  --el-button-hover-border-color: #7c3aed;
}
.mrp-proses-ukur-btn--print {
  --el-button-bg-color: #3b82f6;
  --el-button-border-color: #3b82f6;
  --el-button-hover-bg-color: #2563eb;
  --el-button-hover-border-color: #2563eb;
}
.mrp-proses-ukur-btn--save {
  --el-button-bg-color: #f97316;
  --el-button-border-color: #f97316;
  --el-button-hover-bg-color: #ea580c;
  --el-button-hover-border-color: #ea580c;
}
.mrp-proses-ukur-panel__table-wrap {
  flex: 1;
  min-height: 220px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  overflow: auto;
}
.mrp-proses-ukur-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}
.mrp-proses-ukur-table th,
.mrp-proses-ukur-table td {
  border-bottom: 1px solid var(--el-border-color-lighter);
  padding: 0.55rem 0.65rem;
  text-align: left;
}
.mrp-proses-ukur-table th {
  background: var(--el-fill-color-light);
  font-weight: 600;
}
.mrp-proses-ukur-table td.is-no,
.mrp-proses-ukur-table th.is-no {
  width: 48px;
  text-align: center;
}
.mrp-proses-ukur-table td.is-action,
.mrp-proses-ukur-table th.is-action {
  width: 64px;
  text-align: center;
}
.mrp-proses-ukur-table td.is-empty {
  text-align: center;
  color: var(--el-text-color-secondary);
}
.mrp-proses-ukur-delete {
  border: none;
  background: none;
  color: #ef4444;
  cursor: pointer;
  font-size: 1rem;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.mrp-proses-ukur-delete:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}
.mrp-proses-ukur-panel__hint {
  margin: 0;
  font-size: 0.75rem;
  color: var(--el-text-color-secondary);
}
</style>
