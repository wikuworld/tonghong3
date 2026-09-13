<template>
  <el-dialog
    v-model="visible"
    class="mrp-rencana-create-dialog"
    :title="t('pages.mrpRencana.createTitle')"
    width="96%"
    top="4vh"
    destroy-on-close
    append-to-body
    :close-on-click-modal="!tourOpen"
    :close-on-press-escape="!tourOpen"
    @open="onOpen"
  >
    <el-form label-position="top">
      <el-form-item :label="t('pages.mrpRencana.name')" required>
        <div id="mrp-rencana-tour-create-name" class="max-w-xl">
          <el-input v-model="form.nama_rencana" />
        </div>
      </el-form-item>
      <el-form-item :label="t('pages.mrpRencana.datePlan')">
        <div id="mrp-rencana-tour-create-date" class="max-w-xs">
          <el-date-picker
            v-model="form.tanggal_rencana"
            type="date"
            value-format="YYYY-MM-DD"
            class="w-full"
            teleported
            :popper-class="selectPopperClass"
          />
        </div>
      </el-form-item>

      <p class="text-sm text-slate-500 mb-2">{{ t('pages.mrpRencana.createFromPoHint') }}</p>

      <div id="mrp-rencana-tour-create-items" class="mrp-rencana-create-items mb-3">
        <div class="px-3 pt-3">
          <el-input
            v-model="soKeyword"
            clearable
            size="small"
            class="max-w-md"
            :placeholder="t('pages.mrpRencana.searchPlaceholder')"
          />
        </div>
        <p class="admin-scroll-hint px-3 pt-2">{{ t('pages.mrpRencana.scrollHint') }}</p>
        <div class="admin-table-scroll">
          <el-table
            v-loading="loadingPo"
            :data="filteredPos"
            border
            stripe
            size="small"
            class="admin-table"
            row-key="id"
            :empty-text="t('pages.mrpRencana.soTableEmpty')"
            @selection-change="onSoSelect"
          >
            <el-table-column type="selection" width="44" fixed="left" :selectable="soSelectable" />
            <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" width="130" fixed="left" show-overflow-tooltip />
            <el-table-column prop="lot_number" :label="t('pages.mrpRencana.itemLot')" width="180" fixed="left" show-overflow-tooltip />
            <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="customer" :label="t('common.customer')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="item_name" :label="t('pages.mrpRencana.poItem')" min-width="150" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpRencana.color')" min-width="110" show-overflow-tooltip>
              <template #default="{ row }">{{ spekDisplay(row.warna) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.emboss')" width="100" show-overflow-tooltip>
              <template #default="{ row }">{{ spekDisplay(row.emboss) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.thickness')" width="100" show-overflow-tooltip>
              <template #default="{ row }">{{ spekDisplay(row.tebal) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.swatch')" width="90" show-overflow-tooltip>
              <template #default="{ row }">{{ spekDisplay(row.color_swatch) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.qtyAllocatable')" width="110" align="right">
              <template #default="{ row }">{{ formatQty(qtyOutstanding(row)) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.qtyPlan')" width="120">
              <template #default="{ row }">
                <el-input
                  v-model.number="soQty[row.id]"
                  type="number"
                  size="small"
                  min="0"
                  :disabled="!soSelectedIds.has(row.id)"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
        <p class="text-sm text-slate-600 px-3 py-2">
          {{ t('pages.mrpRencana.selectedQtyTotal') }}: {{ formatQty(selectedQtyTotal) }}
        </p>
      </div>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">{{ t('common.cancel') }}</el-button>
      <el-tooltip
        :content="t('pages.mrpRencana.tour.finishFirst')"
        :disabled="!tourOpen"
        placement="top"
      >
        <span id="mrp-rencana-tour-create-save" class="inline-block">
          <el-button type="primary" :loading="saving" :disabled="tourOpen" @click="submitCreate">
            {{ t('common.save') }}
          </el-button>
        </span>
      </el-tooltip>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { mrpCreateRencana, mrpListMasterPo, mrpSyncPo } from '../../../api/client'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  tourOpen: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'saved'])

const { t } = useI18n()
const selectPopperClass = 'mrp-rencana-create-select-popper'
const saving = ref(false)
const loadingPo = ref(false)
const soKeyword = ref('')
const poRows = ref([])
const soQty = reactive({})
const soSelected = ref([])
const form = reactive({
  nama_rencana: '',
  tanggal_rencana: new Date().toISOString().slice(0, 10),
})

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const soSelectedIds = computed(() => new Set(soSelected.value.map((r) => r.id)))

const selectedQtyTotal = computed(() =>
  soSelected.value.reduce((sum, row) => sum + Number(soQty[row.id] || 0), 0),
)

const filteredPos = computed(() => {
  const q = soKeyword.value.trim().toLowerCase()
  if (!q) return poRows.value
  return poRows.value.filter((row) => {
    const hay = [
      row.no_so,
      row.lot_number,
      row.no_po,
      row.customer,
      row.item_name,
      row.warna,
      row.emboss,
      row.tebal,
      row.color_swatch,
    ]
      .map((v) => String(v || '').toLowerCase())
      .join(' ')
    return hay.includes(q)
  })
})

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function spekDisplay(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function qtyOutstanding(row) {
  const explicit = Number(row?.qty_outstanding)
  if (Number.isFinite(explicit) && explicit >= 0) return explicit
  return Number(row?.qty_order || 0) - Number(row?.qty_processed || 0)
}

function hasCreateSpek(row) {
  return Boolean(
    String(row?.item_name || '').trim() &&
      String(row?.tebal || '').trim() &&
      String(row?.warna || '').trim(),
  )
}

function soSelectable(row) {
  return qtyOutstanding(row) > 0 && hasCreateSpek(row)
}

function onSoSelect(rowsSel) {
  soSelected.value = rowsSel
  for (const row of rowsSel) {
    if (soQty[row.id] == null || soQty[row.id] === '') {
      soQty[row.id] = qtyOutstanding(row)
    }
  }
}

async function loadOutstanding() {
  loadingPo.value = true
  try {
    try {
      await mrpSyncPo()
    } catch {
      /* daftar tetap diisi dari cache MRP */
    }
    const list = await mrpListMasterPo()
    poRows.value = Array.isArray(list) ? list : []
    Object.keys(soQty).forEach((k) => delete soQty[k])
    soSelected.value = []
  } catch (e) {
    poRows.value = []
    ElMessage.error(e.message || String(e))
  } finally {
    loadingPo.value = false
  }
}

function resetForm() {
  form.nama_rencana = ''
  form.tanggal_rencana = new Date().toISOString().slice(0, 10)
  soKeyword.value = ''
  poRows.value = []
  soSelected.value = []
  Object.keys(soQty).forEach((k) => delete soQty[k])
}

async function onOpen() {
  resetForm()
  await loadOutstanding()
}

async function submitCreate() {
  if (props.tourOpen) {
    ElMessage.info(t('pages.mrpRencana.tour.finishFirst'))
    return
  }
  if (!form.nama_rencana?.trim()) {
    ElMessage.warning(t('pages.mrpRencana.name'))
    return
  }
  if (!soSelected.value.length) {
    ElMessage.warning(t('pages.mrpRencana.selectPoRequired'))
    return
  }
  const po_lines = []
  for (const row of soSelected.value) {
    const qty = Number(soQty[row.id] || 0)
    if (qty <= 0) {
      ElMessage.warning(`${t('pages.mrpRencana.qtyPlan')}: ${row.no_so || row.no_po}`)
      return
    }
    if (qty > qtyOutstanding(row) + 1e-9) {
      ElMessage.warning(`${t('pages.mrpRencana.qtyExceeds')}: ${row.no_so || row.no_po}`)
      return
    }
    if (!hasCreateSpek(row)) {
      ElMessage.warning(`${t('pages.mrpRencana.spekIncomplete')}: ${row.no_so || row.no_po}`)
      return
    }
    po_lines.push({ po_id: row.id, qty })
  }
  saving.value = true
  try {
    await mrpCreateRencana({
      nama_rencana: form.nama_rencana.trim(),
      tanggal_rencana: form.tanggal_rencana,
      po_lines,
    })
    ElMessage.success(t('common.saved'))
    visible.value = false
    emit('saved')
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.mrp-rencana-create-items {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
  overflow: visible;
}

.mrp-rencana-create-dialog :deep(.el-dialog__body) {
  overflow: visible;
}
</style>

<style>
.mrp-rencana-create-select-popper {
  z-index: 6500 !important;
}
</style>
