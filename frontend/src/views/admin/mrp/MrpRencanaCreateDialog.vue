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

      <p class="text-sm text-slate-500 mb-2">{{ t('pages.mrpRencana.createItemHint') }}</p>

      <div id="mrp-rencana-tour-create-items" class="mrp-rencana-create-items mb-3">
        <div class="admin-table-scroll">
        <el-table :data="itemRows" border stripe size="small" class="admin-table" :empty-text="t('common.emptyValue')">
          <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" />
          <el-table-column :label="t('common.customer')" min-width="130">
            <template #default="{ row }">
              <el-select
                v-model="row.customer"
                v-bind="selectPopperProps"
                filterable
                clearable
                size="small"
                class="w-full"
                :placeholder="t('common.placeholder.customer')"
                @change="clearRowAllocation(row)"
              >
                <el-option
                  v-for="c in customers"
                  :key="c.id"
                  :label="c.name || c.code"
                  :value="c.name || c.code"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpRencana.material')" min-width="130">
            <template #default="{ row }">
              <el-select
                v-model="row.material_name"
                v-bind="selectPopperProps"
                filterable
                clearable
                size="small"
                class="w-full"
                @change="onMaterialChange(row)"
              >
                <el-option v-for="m in erpOptions.materials" :key="m" :label="m" :value="m" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpRencana.emboss')" min-width="110">
            <template #default="{ row }">
              <el-select
                v-model="row.emboss"
                v-bind="selectPopperProps"
                filterable
                clearable
                size="small"
                class="w-full"
                :disabled="!row.material_name"
                @change="onEmbossChange(row)"
              >
                <el-option v-for="e in rowEmbossOptions(row)" :key="e" :label="e" :value="e" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpRencana.color')" min-width="110">
            <template #default="{ row }">
              <el-select
                v-model="row.color"
                v-bind="selectPopperProps"
                filterable
                clearable
                size="small"
                class="w-full"
                :disabled="!row.material_name || !row.emboss"
                @change="onColorChange(row)"
              >
                <el-option
                  v-for="c in rowColorOptions(row)"
                  :key="c"
                  :label="colorOptionLabel(c)"
                  :value="c"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpRencana.swatch')" min-width="120">
            <template #default="{ row }">
              <el-select
                v-model="row.color_swatch"
                v-bind="selectPopperProps"
                filterable
                clearable
                size="small"
                class="w-full"
                :disabled="!row.swatchOptions.length"
                @change="onSwatchChange(row)"
              >
                <el-option v-for="s in row.swatchOptions" :key="s" :label="s" :value="s" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpRencana.thickness')" min-width="100">
            <template #default="{ row }">
              <el-select
                v-model="row.thickness"
                v-bind="selectPopperProps"
                filterable
                clearable
                size="small"
                class="w-full"
                @change="onThicknessChange(row)"
              >
                <el-option v-for="th in erpOptions.thickness" :key="th" :label="th" :value="th" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpRencana.backer')" min-width="110">
            <template #default="{ row }">
              <el-select
                v-model="row.backer"
                v-bind="selectPopperProps"
                filterable
                clearable
                size="small"
                class="w-full"
                :disabled="!row.backerOptions.length"
              >
                <el-option v-for="b in row.backerOptions" :key="b" :label="b" :value="b" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpRencana.keterangan')" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.keterangan" size="small" :placeholder="t('pages.mrpRencana.keteranganPlaceholder')" />
            </template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpRencana.qtySoTotal')" width="100" align="right">
            <template #default="{ row }">
              <span class="font-medium">{{ formatQty(rowSoTotal(row)) }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="120" fixed="right" align="center">
            <template #default="{ $index }">
              <el-button link type="primary" size="small" @click="openSoDialog($index)">
                {{ t('pages.mrpRencana.soBtn') }}
              </el-button>
              <el-button
                link
                type="danger"
                size="small"
                :disabled="itemRows.length <= 1"
                @click="removeRow($index)"
              >
                {{ t('common.delete') }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        </div>

        <div class="mt-3 px-3 pb-3">
          <el-button size="small" @click="addRow">{{ t('pages.mrpRencana.addRow') }}</el-button>
        </div>
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

    <el-dialog
      v-model="soOpen"
      class="mrp-rencana-so-dialog"
      :title="t('pages.mrpRencana.soDialogTitle')"
      width="920px"
      destroy-on-close
      append-to-body
    >
      <p v-if="soRow" class="text-sm text-slate-500 mb-3">
        {{ t('pages.mrpRencana.soFilterHint') }}:
        {{ spekDisplay(soRow.thickness) }} / {{ spekDisplay(soRow.color) }} / {{ spekDisplay(soRow.emboss) }}
      </p>
      <el-table
        ref="soTableRef"
        v-loading="soLoading"
        :data="soList"
        border
        size="small"
        row-key="id"
        @selection-change="onSoSelect"
      >
        <el-table-column type="selection" width="40" :selectable="soSelectable" />
        <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="110" />
        <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="100" show-overflow-tooltip />
        <el-table-column prop="customer" :label="t('common.customer')" min-width="110" show-overflow-tooltip />
        <el-table-column prop="item_name" :label="t('pages.mrpRencana.poItem')" min-width="130" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpRencana.qtyAllocatable')" width="110" align="right">
          <template #default="{ row }">{{ formatQty(row.qty_outstanding) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpRencana.qtyPlan')" width="110">
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
      <template #footer>
        <el-button @click="soOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="saveSoDialog">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import {
  listCustomers,
  mrpCreateRencana,
  mrpErpCombination,
  mrpErpOptions,
  mrpRencanaPoByCombination,
  mrpSyncPo,
} from '../../../api/client'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  tourOpen: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'saved'])

const { t } = useI18n()
const selectPopperClass = 'mrp-rencana-create-select-popper'
const selectPopperProps = {
  teleported: true,
  popperClass: selectPopperClass,
}
const saving = ref(false)
const loadingMeta = ref(false)
const customers = ref([])
const erpOptions = reactive({
  thickness: [],
  materials: [],
  colors: [],
  emboss: [],
  embosses_by_material: {},
  colors_by_material_emboss: {},
  color_labels: {},
})
const form = reactive({
  nama_rencana: '',
  tanggal_rencana: new Date().toISOString().slice(0, 10),
})
const itemRows = ref([])
const soOpen = ref(false)
const soLoading = ref(false)
const soList = ref([])
const soQty = reactive({})
const soSelected = ref([])
const soTableRef = ref(null)
const soRowIndex = ref(-1)
let rowUid = 0

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const soRow = computed(() => (soRowIndex.value >= 0 ? itemRows.value[soRowIndex.value] : null))

const soSelectedIds = computed(() => new Set(soSelected.value.map((r) => r.id)))

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function spekDisplay(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function createEmptyRow() {
  return {
    uid: ++rowUid,
    customer: '',
    material_name: '',
    emboss: '',
    color: '',
    color_swatch: '',
    thickness: '',
    backer: '',
    keterangan: '',
    pos: [],
    swatchOptions: [],
    backerOptions: [],
    comboOptions: [],
  }
}

function comboKey(material, emboss) {
  const m = (material || '').trim().toLowerCase().replace(/\s+/g, ' ')
  const e = (emboss || '').trim().toLowerCase().replace(/\s+/g, ' ')
  return `${m}\x1e${e}`
}

function rowEmbossOptions(row) {
  const mat = (row.material_name || '').trim()
  if (!mat) return []
  const exact = erpOptions.embosses_by_material?.[mat]
  if (Array.isArray(exact) && exact.length) return exact
  const want = mat.toLowerCase()
  for (const [key, vals] of Object.entries(erpOptions.embosses_by_material || {})) {
    if ((key || '').trim().toLowerCase() === want) return vals
  }
  return []
}

function colorOptionLabel(name) {
  return erpOptions.color_labels?.[name] || name
}

function rowColorOptions(row) {
  const mat = (row.material_name || '').trim()
  const emb = (row.emboss || '').trim()
  if (!mat || !emb) return []
  const key = comboKey(mat, emb)
  const exact = erpOptions.colors_by_material_emboss?.[key]
  if (Array.isArray(exact) && exact.length) return exact
  for (const [k, vals] of Object.entries(erpOptions.colors_by_material_emboss || {})) {
    if (k === key) return vals
  }
  return []
}

function rowSoTotal(row) {
  return (row.pos || []).reduce((sum, p) => sum + Number(p.qty || 0), 0)
}

function addRow() {
  itemRows.value.push(createEmptyRow())
}

function removeRow(index) {
  if (itemRows.value.length <= 1) return
  itemRows.value.splice(index, 1)
}

function clearRowAllocation(row) {
  row.pos = []
}

function updateSwatchBackerOptions(row) {
  const opts = row.comboOptions || []
  row.swatchOptions = [...new Set(opts.map((o) => (o.color_swatch || '').trim()).filter(Boolean))]
  row.backerOptions = [...new Set(opts.map((o) => (o.backer || '').trim()).filter(Boolean))]
  if (row.color_swatch && !row.swatchOptions.includes(row.color_swatch)) {
    row.color_swatch = ''
  }
  if (row.backer && !row.backerOptions.includes(row.backer)) {
    row.backer = ''
  }
}

async function loadCombination(row) {
  if (!row.material_name || !row.color || !row.emboss) {
    row.comboOptions = []
    row.swatchOptions = []
    row.backerOptions = []
    row.color_swatch = ''
    row.backer = ''
    return
  }
  try {
    const params = {
      material_name: row.material_name,
      color: row.color,
      emboss: row.emboss,
    }
    if (row.thickness) params.thickness = row.thickness
    const data = await mrpErpCombination(params)
    row.comboOptions = data.options || []
    updateSwatchBackerOptions(row)
    if (row.swatchOptions.length === 1) {
      row.color_swatch = row.swatchOptions[0]
      onSwatchChange(row)
    }
  } catch {
    row.comboOptions = []
    row.swatchOptions = []
    row.backerOptions = []
  }
}

async function onMaterialChange(row) {
  row.emboss = ''
  row.color = ''
  row.color_swatch = ''
  row.backer = ''
  row.comboOptions = []
  row.swatchOptions = []
  row.backerOptions = []
  clearRowAllocation(row)
}

async function onEmbossChange(row) {
  row.color = ''
  row.color_swatch = ''
  row.backer = ''
  row.comboOptions = []
  row.swatchOptions = []
  row.backerOptions = []
  clearRowAllocation(row)
}

async function onColorChange(row) {
  row.color_swatch = ''
  row.backer = ''
  clearRowAllocation(row)
  await loadCombination(row)
}

async function onThicknessChange(row) {
  clearRowAllocation(row)
  await loadCombination(row)
}

function onSwatchChange(row) {
  const sw = (row.color_swatch || '').trim()
  if (!sw) {
    updateSwatchBackerOptions(row)
    return
  }
  const matches = (row.comboOptions || []).filter((o) => (o.color_swatch || '').trim() === sw)
  row.backerOptions = [...new Set(matches.map((o) => (o.backer || '').trim()).filter(Boolean))]
  if (row.backerOptions.length === 1) {
    row.backer = row.backerOptions[0]
  } else if (row.backer && !row.backerOptions.includes(row.backer)) {
    row.backer = ''
  }
  clearRowAllocation(row)
}

function rowSpekReady(row) {
  return Boolean(row.thickness && row.color && row.emboss)
}

function soSelectable(row) {
  return Number(row.qty_outstanding || 0) > 0
}

async function openSoDialog(index) {
  const row = itemRows.value[index]
  if (!rowSpekReady(row)) {
    ElMessage.warning(t('pages.mrpRencana.soSpekRequired'))
    return
  }
  soRowIndex.value = index
  soSelected.value = []
  soList.value = []
  Object.keys(soQty).forEach((k) => delete soQty[k])
  soOpen.value = true
  soLoading.value = true
  try {
    await syncPoSilent()
    const list = await mrpRencanaPoByCombination({
      thickness: row.thickness,
      color: row.color,
      emboss: row.emboss,
    })
    soList.value = list || []
    const selectedMap = new Map((row.pos || []).map((p) => [Number(p.po_id), p]))
    for (const p of soList.value) {
      const prev = selectedMap.get(Number(p.id))
      soQty[p.id] = prev ? Number(prev.qty || 0) : Number(p.qty_outstanding || 0)
    }
    await nextTick()
    const table = soTableRef.value
    if (table?.clearSelection) table.clearSelection()
    for (const p of soList.value) {
      if (selectedMap.has(Number(p.id))) {
        table?.toggleRowSelection?.(p, true)
      }
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    soLoading.value = false
  }
}

function onSoSelect(rowsSel) {
  soSelected.value = rowsSel
}

function saveSoDialog() {
  const row = soRow.value
  if (!row) return
  const pos = []
  for (const p of soSelected.value) {
    const qty = Number(soQty[p.id] || 0)
    if (qty <= 0) {
      ElMessage.warning(`${t('pages.mrpRencana.qtyPlan')}: ${p.no_po}`)
      return
    }
    if (qty > Number(p.qty_outstanding || 0) + 1e-9) {
      ElMessage.warning(`${t('pages.mrpRencana.qtyExceeds')}: ${p.no_po}`)
      return
    }
    pos.push({ po_id: p.id, qty })
  }
  row.pos = pos
  soOpen.value = false
  ElMessage.success(t('pages.mrpRencana.soSaved'))
}

async function syncPoSilent() {
  try {
    await mrpSyncPo()
  } catch {
    /* ignore */
  }
}

async function loadMeta() {
  loadingMeta.value = true
  try {
    const [cust, opts] = await Promise.all([listCustomers(), mrpErpOptions()])
    customers.value = cust || []
    erpOptions.thickness = opts?.thickness || []
    erpOptions.materials = opts?.materials || []
    erpOptions.colors = opts?.colors || []
    erpOptions.emboss = opts?.emboss || []
    erpOptions.embosses_by_material = opts?.embosses_by_material || {}
    erpOptions.colors_by_material_emboss = opts?.colors_by_material_emboss || {}
    erpOptions.color_labels = opts?.color_labels || {}
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loadingMeta.value = false
  }
}

function resetForm() {
  form.nama_rencana = ''
  form.tanggal_rencana = new Date().toISOString().slice(0, 10)
  itemRows.value = [createEmptyRow()]
}

async function onOpen() {
  resetForm()
  await loadMeta()
}

function validateRow(row, index) {
  const n = index + 1
  if (!row.customer?.trim()) return t('pages.mrpRencana.rowIncomplete', { n, field: t('common.customer') })
  if (!row.material_name?.trim()) return t('pages.mrpRencana.rowIncomplete', { n, field: t('pages.mrpRencana.material') })
  if (!row.emboss?.trim()) return t('pages.mrpRencana.rowIncomplete', { n, field: t('pages.mrpRencana.emboss') })
  if (!row.color?.trim()) return t('pages.mrpRencana.rowIncomplete', { n, field: t('pages.mrpRencana.color') })
  if (!row.color_swatch?.trim()) return t('pages.mrpRencana.rowIncomplete', { n, field: t('pages.mrpRencana.swatch') })
  if (!row.thickness?.trim()) return t('pages.mrpRencana.rowIncomplete', { n, field: t('pages.mrpRencana.thickness') })
  if (!row.backer?.trim()) return t('pages.mrpRencana.rowIncomplete', { n, field: t('pages.mrpRencana.backer') })
  return null
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
  const items = []
  for (let i = 0; i < itemRows.value.length; i += 1) {
    const row = itemRows.value[i]
    const err = validateRow(row, i)
    if (err) {
      ElMessage.warning(err)
      return
    }
    items.push({
      customer: row.customer.trim(),
      material_name: row.material_name.trim(),
      emboss: row.emboss.trim(),
      color: row.color.trim(),
      color_swatch: row.color_swatch.trim(),
      thickness: row.thickness.trim(),
      backer: row.backer.trim(),
      keterangan: (row.keterangan || '').trim() || null,
      pos: (row.pos || []).map((p) => ({ po_id: p.po_id, qty: Number(p.qty || 0) })),
    })
  }
  saving.value = true
  try {
    await mrpCreateRencana({
      nama_rencana: form.nama_rencana.trim(),
      tanggal_rencana: form.tanggal_rencana,
      items,
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

.mrp-rencana-so-dialog {
  z-index: 5000;
}

.mrp-rencana-create-dialog {
  z-index: 4200;
}
</style>
