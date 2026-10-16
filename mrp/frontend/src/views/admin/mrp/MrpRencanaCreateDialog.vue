<template>
  <el-dialog
    v-model="visible"
    class="mrp-rencana-create-dialog"
    :title="isEdit ? t('pages.mrpRencana.editTitle') : t('pages.mrpRencana.createTitle')"
    width="96%"
    top="4vh"
    destroy-on-close
    append-to-body
    :close-on-click-modal="!tourOpen"
    :close-on-press-escape="!tourOpen"
    @open="onOpen"
  >
    <el-form label-position="top">
      <el-form-item v-if="isEdit" :label="t('pages.mrpRencana.code')">
        <div class="max-w-xs">
          <el-input :model-value="editCode" disabled />
        </div>
      </el-form-item>

      <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
        <p class="text-sm text-slate-500 m-0">{{ t('pages.mrpRencana.createItemHint') }}</p>
        <el-button id="mrp-rencana-tour-pick-so" type="primary" @click="openSoDialog">
          {{ t('pages.mrpRencana.soBtn') }}
        </el-button>
      </div>

      <div id="mrp-rencana-tour-create-items" class="mrp-rencana-create-items mb-3">
        <div class="admin-table-scroll">
          <el-table
            :data="itemRows"
            border
            size="small"
            class="admin-table mrp-rencana-items-table"
            :empty-text="t('pages.mrpRencana.tableEmptyPickSo')"
          >
            <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" fixed="left" />
            <el-table-column
              :label="t('common.lotNo')"
              min-width="168"
              fixed="left"
              class-name="mrp-lot-col"
              label-class-name="mrp-lot-col-header"
            >
              <template #default="{ row }">
                <template v-if="rowLotList(row).length > 1">
                  <el-popover
                    placement="bottom-start"
                    :width="280"
                    trigger="click"
                    :teleported="true"
                    popper-class="mrp-lot-popover"
                  >
                    <template #reference>
                      <button
                        type="button"
                        class="mrp-lot-badge mrp-lot-badge--multi"
                        :title="t('pages.mrpRencana.lotCombinedHint')"
                      >
                        <span class="mrp-lot-badge__primary">{{ rowLotList(row)[0] }}</span>
                        <span class="mrp-lot-badge__more">+{{ rowLotList(row).length - 1 }}</span>
                      </button>
                    </template>
                    <p class="mrp-lot-popover__title">{{ t('pages.mrpRencana.lotCombinedTitle') }}</p>
                    <ul class="mrp-lot-popover__list">
                      <li v-for="lot in rowLotList(row)" :key="lot">{{ lot }}</li>
                    </ul>
                  </el-popover>
                </template>
                <span v-else class="mrp-lot-badge">{{ rowLotList(row)[0] || '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.customer')" min-width="140" show-overflow-tooltip>
              <template #default="{ row }">{{ row.customer || '—' }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.soRef')" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ rowSoRefs(row) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.material')" min-width="130" show-overflow-tooltip>
              <template #default="{ row }">{{ row.material_name || '—' }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.color')" min-width="100" show-overflow-tooltip>
              <template #default="{ row }">{{ row.color || '—' }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.emboss')" min-width="100" show-overflow-tooltip>
              <template #default="{ row }">{{ row.emboss || '—' }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.thickness')" min-width="90" show-overflow-tooltip>
              <template #default="{ row }">{{ row.thickness || '—' }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.swatch')" min-width="120">
              <template #default="{ row }">
                <el-select
                  v-model="row.color_swatch"
                  v-bind="selectPopperProps"
                  filterable
                  clearable
                  allow-create
                  default-first-option
                  size="small"
                  class="w-full"
                  @change="onSwatchChange(row)"
                >
                  <el-option v-for="s in row.swatchOptions" :key="s" :label="s" :value="s" />
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
                  allow-create
                  default-first-option
                  size="small"
                  class="w-full"
                >
                  <el-option v-for="b in row.backerOptions" :key="b" :label="b" :value="b" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.keterangan')" min-width="120">
              <template #default="{ row }">
                <el-input
                  v-model="row.keterangan"
                  size="small"
                  :placeholder="t('pages.mrpRencana.keteranganPlaceholder')"
                />
              </template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.qtySoTotal')" width="100" align="right">
              <template #default="{ row }">
                <span class="font-medium">{{ formatQty(rowSoTotal(row)) }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="88" fixed="right" align="center">
              <template #default="{ row, $index }">
                <AdminTableActions
                  :show-delete="!(isEdit && !!row.id)"
                  @delete="removeRow($index)"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <div v-if="showHeaderFields" class="mrp-rencana-header-fields mb-1">
        <p v-if="!isEdit" class="text-sm text-slate-500 mb-3 m-0">
          {{ t('pages.mrpRencana.headerAfterSoHint') }}
        </p>
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
      </div>
      <p v-else class="text-sm text-slate-500 mb-2">
        {{ t('pages.mrpRencana.headerWaitSoHint') }}
      </p>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">{{ t('common.cancel') }}</el-button>
      <el-tooltip
        :content="t('pages.mrpRencana.tour.finishFirst')"
        :disabled="!tourOpen"
        placement="top"
      >
        <span id="mrp-rencana-tour-create-save" class="inline-block">
          <el-button
            type="primary"
            :loading="saving"
            :disabled="tourOpen || !showHeaderFields"
            @click="submitSave"
          >
            {{ t('common.save') }}
          </el-button>
        </span>
      </el-tooltip>
    </template>

    <el-dialog
      v-model="soOpen"
      class="mrp-rencana-so-dialog"
      :title="t('pages.mrpRencana.soDialogTitle')"
      width="1100px"
      destroy-on-close
      append-to-body
    >
      <div class="mrp-rencana-so-filters mb-3 flex flex-wrap gap-2 items-end">
        <div class="min-w-[160px]">
          <div class="text-xs text-slate-500 mb-1">{{ t('pages.mrpRencana.color') }}</div>
          <el-select
            v-model="soSpek.color"
            clearable
            filterable
            size="small"
            class="w-full"
            :placeholder="t('pages.mrpRencana.color')"
            @change="onSpekFieldChange"
          >
            <el-option v-for="c in spekColorOptions" :key="c" :label="c" :value="c" />
          </el-select>
        </div>
        <div class="min-w-[140px]">
          <div class="text-xs text-slate-500 mb-1">{{ t('pages.mrpRencana.emboss') }}</div>
          <el-select
            v-model="soSpek.emboss"
            clearable
            filterable
            size="small"
            class="w-full"
            :placeholder="t('pages.mrpRencana.emboss')"
            @change="onSpekFieldChange"
          >
            <el-option v-for="e in spekEmbossOptions" :key="e" :label="e" :value="e" />
          </el-select>
        </div>
        <div class="min-w-[120px]">
          <div class="text-xs text-slate-500 mb-1">{{ t('pages.mrpRencana.thickness') }}</div>
          <el-select
            v-model="soSpek.thickness"
            clearable
            filterable
            size="small"
            class="w-full"
            :placeholder="t('pages.mrpRencana.thickness')"
            @change="onSpekFieldChange"
          >
            <el-option v-for="th in spekThicknessOptions" :key="th" :label="th" :value="th" />
          </el-select>
        </div>
        <div class="min-w-[220px] flex-1">
          <div class="text-xs text-slate-500 mb-1">{{ t('pages.mrpRencana.soSearch') }}</div>
          <el-input
            v-model="soFilter.q"
            clearable
            size="small"
            :placeholder="t('pages.mrpRencana.soSearchPlaceholder')"
          />
        </div>
        <el-button size="small" :loading="soLoading" @click="reloadSoList">
          {{ t('pages.mrpRencana.syncPo') }}
        </el-button>
      </div>
      <p class="text-sm text-slate-500 mb-2">
        {{ t('pages.mrpRencana.soCascadeHint') }}
        <span v-if="soListFiltered.length !== soListMatched.length">
          — {{ soListFiltered.length }}/{{ soListMatched.length }}
        </span>
        <span v-else-if="soListMatched.length"> — {{ soListMatched.length }}</span>
      </p>
      <p v-if="!spekComplete" class="text-sm text-amber-700 mb-2">
        {{ t('pages.mrpRencana.soSpekRequired') }}
      </p>
      <el-table
        ref="soTableRef"
        v-loading="soLoading"
        :data="soListFiltered"
        border
        size="small"
        class="mrp-rencana-so-table"
        row-key="id"
        max-height="420"
        :empty-text="soEmptyText"
        @selection-change="onSoSelect"
      >
        <el-table-column type="selection" width="40" fixed="left" :selectable="soSelectable" />
        <el-table-column
          prop="lot_no"
          :label="t('common.lotNo')"
          min-width="168"
          fixed="left"
          class-name="mrp-lot-col"
          label-class-name="mrp-lot-col-header"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span class="mrp-lot-badge">{{ row.lot_no || row.lot_number || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="110" />
        <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="100" show-overflow-tooltip />
        <el-table-column prop="customer" :label="t('common.customer')" min-width="110" show-overflow-tooltip />
        <el-table-column prop="item_name" :label="t('pages.mrpRencana.poItem')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="warna" :label="t('pages.mrpRencana.color')" width="90" show-overflow-tooltip />
        <el-table-column prop="emboss" :label="t('pages.mrpRencana.emboss')" width="90" show-overflow-tooltip />
        <el-table-column prop="tebal" :label="t('pages.mrpRencana.thickness')" width="80" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpRencana.qtyAllocatable')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.qty_outstanding) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpRencana.qtyPlan')" width="100">
          <template #default="{ row }">
            <el-input
              v-model.number="soQty[row.id]"
              type="number"
              size="small"
              min="0"
              :disabled="!soSelectable(row)"
              @change="onQtyPlanChange(row)"
            />
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="soOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :disabled="!spekComplete" @click="saveSoDialog">
          {{ t('pages.mrpRencana.addSelectedSo') }}
        </el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { computed, nextTick, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import {
  mrpCreateRencana,
  mrpErpCombination,
  mrpGetRencana,
  mrpRencanaPoByCombination,
  mrpSyncPo,
  mrpUpdateRencana,
} from '../../../api/client'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  tourOpen: { type: Boolean, default: false },
  editId: { type: Number, default: null },
})

const emit = defineEmits(['update:modelValue', 'saved'])

const { t } = useI18n()
const isEdit = computed(() => Number(props.editId) > 0)
const editCode = ref('')
const selectPopperClass = 'mrp-rencana-create-select-popper'
const selectPopperProps = {
  teleported: true,
  popperClass: selectPopperClass,
}
const saving = ref(false)
const form = reactive({
  nama_rencana: '',
  tanggal_rencana: new Date().toISOString().slice(0, 10),
})
const itemRows = ref([])
const soOpen = ref(false)
const soLoading = ref(false)
const soListAll = ref([])
const soListMatched = ref([])
const soSpek = reactive({
  color: '',
  emboss: '',
  thickness: '',
})
const soFilter = reactive({
  q: '',
})
const soQty = reactive({})
const soSelected = ref([])
const soTableRef = ref(null)
const soSyncWarning = ref('')
const soPoMeta = reactive({})
let rowUid = 0

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const showHeaderFields = computed(() => isEdit.value || itemRows.value.length > 0 || !!props.tourOpen)

const spekComplete = computed(
  () => !!(soSpek.color?.trim() && soSpek.emboss?.trim() && soSpek.thickness?.trim()),
)

const soSelectedIds = computed(() => new Set(soSelected.value.map((r) => r.id)))

const usedPoIds = computed(() => {
  const set = new Set()
  for (const row of itemRows.value) {
    for (const p of row.pos || []) {
      const id = Number(p.po_id)
      if (id) set.add(id)
    }
  }
  return set
})

function normText(v) {
  return String(v || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ')
}

function rowMatchesColor(row, color) {
  const want = normText(color).replace(/\s*\([^)]*\)\s*$/, '').trim()
  if (!want) return true
  const got = normText(row.warna).replace(/\s*\([^)]*\)\s*$/, '').trim()
  return got === want || got.startsWith(want) || want.startsWith(got)
}

function rowMatchesEmboss(row, emboss) {
  const want = normText(emboss)
  if (!want) return true
  const got = normText(row.emboss)
  return got === want || got.startsWith(want) || want.startsWith(got)
}

function rowMatchesThickness(row, thickness) {
  const want = String(thickness || '')
    .trim()
    .replace(/mm/gi, '')
    .replace(/\s+/g, '')
  if (!want) return true
  const got = String(row.tebal || '')
    .trim()
    .replace(/mm/gi, '')
    .replace(/\s+/g, '')
  return got.toLowerCase() === want.toLowerCase()
}

function uniqueSorted(values) {
  return [...new Set(values.map((v) => String(v || '').trim()).filter(Boolean))].sort((a, b) =>
    a.localeCompare(b),
  )
}

/** Opsi cascade: awalnya semua, lalu berkurang sesuai filter spek lain yang sudah dipilih. */
function rowsForSpekOptions(excludeField) {
  return soListAll.value.filter((r) => {
    if (excludeField !== 'color' && soSpek.color && !rowMatchesColor(r, soSpek.color)) {
      return false
    }
    if (excludeField !== 'emboss' && soSpek.emboss && !rowMatchesEmboss(r, soSpek.emboss)) {
      return false
    }
    if (
      excludeField !== 'thickness' &&
      soSpek.thickness &&
      !rowMatchesThickness(r, soSpek.thickness)
    ) {
      return false
    }
    return true
  })
}

const spekColorOptions = computed(() =>
  uniqueSorted(rowsForSpekOptions('color').map((r) => r.warna)),
)

const spekEmbossOptions = computed(() =>
  uniqueSorted(rowsForSpekOptions('emboss').map((r) => r.emboss)),
)

const spekThicknessOptions = computed(() =>
  uniqueSorted(rowsForSpekOptions('thickness').map((r) => r.tebal)),
)

const soListFiltered = computed(() => {
  const q = (soFilter.q || '').trim().toLowerCase()
  if (!q) return soListMatched.value
  return soListMatched.value.filter((row) => {
    const hay = [
      row.no_po,
      row.no_so,
      row.customer,
      row.item_name,
      row.lot_no,
      row.lot_number,
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

const soEmptyText = computed(() => {
  if (soLoading.value) return t('common.loadingData')
  if (soSyncWarning.value && !soListAll.value.length) return soSyncWarning.value
  if (!soListAll.value.length) return t('pages.mrpRencana.soListEmptyMaster')
  if (!soListMatched.value.length) return t('pages.mrpRencana.poListEmpty')
  return t('pages.mrpRencana.soListEmptyFilter')
})

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function createEmptyRow() {
  return {
    uid: ++rowUid,
    id: null,
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

function rowSoTotal(row) {
  return (row.pos || []).reduce((sum, p) => sum + Number(p.qty || 0), 0)
}

function rowSoRefs(row) {
  const refs = []
  for (const p of row.pos || []) {
    const meta = soPoMeta[p.po_id]
    const label = (meta?.no_so || meta?.no_po || '').trim()
    if (label) refs.push(label)
  }
  return refs.length ? [...new Set(refs)].join(' / ') : '—'
}

function rowLotList(row) {
  const refs = []
  for (const p of row.pos || []) {
    const meta = soPoMeta[p.po_id]
    const label = (meta?.lot_no || '').trim()
    if (label) refs.push(label)
  }
  return [...new Set(refs)]
}

function removeRow(index) {
  const row = itemRows.value[index]
  if (!row) return
  if (isEdit.value && row.id) {
    ElMessage.warning(t('pages.mrpRencana.cannotDeleteExistingItem'))
    return
  }
  itemRows.value.splice(index, 1)
}

function updateSwatchBackerOptions(row) {
  const opts = row.comboOptions || []
  const swatches = [...new Set(opts.map((o) => (o.color_swatch || o.factory_key || '').trim()).filter(Boolean))]
  const backers = [
    ...new Set(
      opts
        .map((o) => (o.backer || o.backing || '').trim())
        .filter(Boolean),
    ),
  ]
  row.swatchOptions = swatches
  row.backerOptions = backers
  if (row.color_swatch && !row.swatchOptions.includes(row.color_swatch)) {
    row.swatchOptions = [row.color_swatch, ...row.swatchOptions]
  }
  if (row.backer && !row.backerOptions.includes(row.backer)) {
    row.backerOptions = [row.backer, ...row.backerOptions]
  }
}

async function loadCombination(row) {
  if (!row.material_name || !row.color || !row.emboss) {
    if (row.color_swatch) row.swatchOptions = [row.color_swatch]
    if (row.backer) row.backerOptions = [row.backer]
    return
  }
  const tryParams = []
  const base = {
    material_name: row.material_name,
    color: row.color,
    emboss: row.emboss,
  }
  if (row.thickness) tryParams.push({ ...base, thickness: row.thickness })
  tryParams.push(base)

  let loaded = false
  for (const params of tryParams) {
    try {
      const data = await mrpErpCombination(params)
      row.comboOptions = data.options || []
      updateSwatchBackerOptions(row)
      loaded = true
      break
    } catch {
      /* coba tanpa thickness / biarkan fallback UI */
    }
  }
  if (!loaded) {
    if (row.color_swatch) row.swatchOptions = [row.color_swatch]
    if (row.backer) row.backerOptions = [row.backer]
    return
  }
  // Swatch = factory key dari kombinasi; jangan pertahankan color_code (mis. 06B) dari sync SO.
  if (row.swatchOptions.length) {
    if (!row.color_swatch || !row.swatchOptions.includes(row.color_swatch)) {
      row.color_swatch = row.swatchOptions[0]
    }
    onSwatchChange(row)
  }
  if (!row.backer && row.backerOptions.length === 1) {
    row.backer = row.backerOptions[0]
  } else if (row.backer && row.backerOptions.length && !row.backerOptions.includes(row.backer)) {
    row.backer = row.backerOptions[0] || ''
  }
}

function onSwatchChange(row) {
  const sw = (row.color_swatch || '').trim()
  if (!sw) {
    updateSwatchBackerOptions(row)
    return
  }
  const matches = (row.comboOptions || []).filter((o) => {
    const key = (o.color_swatch || o.factory_key || '').trim()
    return key === sw
  })
  if (!matches.length) {
    updateSwatchBackerOptions(row)
    return
  }
  row.backerOptions = [
    ...new Set(matches.map((o) => (o.backer || o.backing || '').trim()).filter(Boolean)),
  ]
  if (row.backerOptions.length === 1) {
    row.backer = row.backerOptions[0]
  } else if (row.backer && !row.backerOptions.includes(row.backer)) {
    row.backer = ''
  }
}

function soSelectable(row) {
  if (Number(row.qty_outstanding || 0) <= 0) return false
  return !usedPoIds.value.has(Number(row.id))
}

function normSpekKeyFromSoLine(p) {
  return [
    (p.item_name || '').trim().toLowerCase(),
    soSpek.emboss.trim().toLowerCase(),
    soSpek.thickness.trim().toLowerCase(),
    soSpek.color.trim().toLowerCase(),
  ].join('|')
}

function normSpekKeyFromRow(r) {
  return [
    (r.material_name || '').trim().toLowerCase(),
    (r.emboss || '').trim().toLowerCase(),
    (r.thickness || '').trim().toLowerCase(),
    (r.color || '').trim().toLowerCase(),
  ].join('|')
}

function mergeCustomerLabels(existing, incoming) {
  const seen = new Set()
  const ordered = []
  for (const raw of [existing, incoming]) {
    for (const part of String(raw || '').split(/[,;]/)) {
      const name = part.trim()
      if (!name) continue
      const key = name.toLowerCase()
      if (seen.has(key)) continue
      seen.add(key)
      ordered.push(name)
    }
  }
  return ordered.join(', ')
}

function rememberPoMeta(list) {
  for (const row of list || []) {
    const id = Number(row.id)
    if (!id) continue
    soPoMeta[id] = {
      no_so: row.no_so || '',
      no_po: row.no_po || '',
      customer: row.customer || '',
      lot_no: row.lot_no || row.lot_number || '',
    }
  }
}

async function syncPoWithFeedback() {
  soSyncWarning.value = ''
  try {
    return await mrpSyncPo()
  } catch (e) {
    soSyncWarning.value = e.message || String(e)
    ElMessage.warning(t('pages.mrpRencana.syncPoFailed', { error: soSyncWarning.value }))
    return null
  }
}

function applyMatchedFromAll() {
  soListMatched.value = soListAll.value.filter(
    (r) =>
      rowMatchesColor(r, soSpek.color) &&
      rowMatchesEmboss(r, soSpek.emboss) &&
      rowMatchesThickness(r, soSpek.thickness),
  )
  rememberPoMeta(soListMatched.value)
  for (const p of soListMatched.value) {
    if (soQty[p.id] == null) soQty[p.id] = Number(p.qty_outstanding || 0)
  }
}

function pruneSpekToAvailableOptions() {
  if (soSpek.color && !spekColorOptions.value.includes(soSpek.color)) {
    soSpek.color = ''
  }
  if (soSpek.emboss && !spekEmbossOptions.value.includes(soSpek.emboss)) {
    soSpek.emboss = ''
  }
  if (soSpek.thickness && !spekThicknessOptions.value.includes(soSpek.thickness)) {
    soSpek.thickness = ''
  }
}

async function refreshMatchedList() {
  applyMatchedFromAll()
  if (!spekComplete.value) return
  try {
    const list = await mrpRencanaPoByCombination({
      limit: 1000,
      color: soSpek.color,
      emboss: soSpek.emboss,
      thickness: soSpek.thickness,
    })
    if (Array.isArray(list) && list.length) {
      soListMatched.value = list
      rememberPoMeta(list)
      for (const p of list) {
        if (soQty[p.id] == null) soQty[p.id] = Number(p.qty_outstanding || 0)
      }
    }
  } catch {
    /* pakai hasil filter lokal */
  }
}

async function fetchSoMaster() {
  const list = await mrpRencanaPoByCombination({ limit: 1000 })
  soListAll.value = Array.isArray(list) ? list : []
  rememberPoMeta(soListAll.value)
  applyMatchedFromAll()
}

async function onSpekFieldChange() {
  soSelected.value = []
  soTableRef.value?.clearSelection?.()
  await nextTick()
  pruneSpekToAvailableOptions()
  await nextTick()
  pruneSpekToAvailableOptions()
  await refreshMatchedList()
}

async function openSoDialog() {
  soSelected.value = []
  soListAll.value = []
  soListMatched.value = []
  Object.keys(soQty).forEach((k) => delete soQty[k])
  soSpek.color = ''
  soSpek.emboss = ''
  soSpek.thickness = ''
  soFilter.q = ''
  soOpen.value = true
  soLoading.value = true
  try {
    await syncPoWithFeedback()
    await fetchSoMaster()
    await nextTick()
    soTableRef.value?.clearSelection?.()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    soLoading.value = false
  }
}

async function reloadSoList() {
  soLoading.value = true
  try {
    await syncPoWithFeedback()
    await fetchSoMaster()
    await refreshMatchedList()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    soLoading.value = false
  }
}

function onSoSelect(rowsSel) {
  soSelected.value = rowsSel
}

function onQtyPlanChange(row) {
  if (!soSelectable(row)) return
  const qty = Number(soQty[row.id] || 0)
  const selected = soSelectedIds.value.has(row.id)
  if (qty > 0 && !selected) {
    soTableRef.value?.toggleRowSelection?.(row, true)
  }
}

function findRowBySpekKey(key) {
  return itemRows.value.find((r) => normSpekKeyFromRow(r) === key)
}

async function saveSoDialog() {
  if (!spekComplete.value) {
    ElMessage.warning(t('pages.mrpRencana.soSpekRequired'))
    return
  }
  if (!soSelected.value.length) {
    ElMessage.warning(t('pages.mrpRencana.selectPoRequired'))
    return
  }

  const groups = new Map()
  for (const p of soSelected.value) {
    const qty = Number(soQty[p.id] || 0)
    if (qty <= 0) {
      ElMessage.warning(`${t('pages.mrpRencana.qtyPlan')}: ${p.no_po || p.no_so || p.id}`)
      return
    }
    if (qty > Number(p.qty_outstanding || 0) + 1e-9) {
      ElMessage.warning(`${t('pages.mrpRencana.qtyExceeds')}: ${p.no_po || p.no_so || p.id}`)
      return
    }
    if (usedPoIds.value.has(Number(p.id))) {
      ElMessage.warning(t('pages.mrpRencana.soAlreadyAdded', { so: p.no_so || p.no_po || p.id }))
      return
    }
    if (!(p.item_name || '').trim()) {
      ElMessage.warning(t('pages.mrpRencana.rowIncomplete', { n: p.no_so || p.no_po || p.id, field: t('pages.mrpRencana.material') }))
      return
    }
    const key = normSpekKeyFromSoLine(p)
    if (!groups.has(key)) groups.set(key, [])
    groups.get(key).push(p)
  }

  let added = 0
  const rowsToEnrich = []
  for (const [spekKey, lines] of groups) {
    const first = lines[0]
    let row = findRowBySpekKey(spekKey)
    const newPos = lines.map((p) => ({ po_id: p.id, qty: Number(soQty[p.id] || 0) }))
    rememberPoMeta(lines)

    if (row) {
      row.pos = [...(row.pos || []), ...newPos]
      row.customer = mergeCustomerLabels(row.customer, first.customer)
    } else {
      row = createEmptyRow()
      row.customer = lines.reduce(
        (acc, p) => mergeCustomerLabels(acc, p.customer),
        '',
      )
      row.material_name = (first.item_name || '').trim()
      row.emboss = soSpek.emboss.trim()
      row.color = soSpek.color.trim()
      row.thickness = soSpek.thickness.trim()
      // Swatch & backing diisi async dari /erp/combination (jangan tahan dialog).
      row.color_swatch = ''
      row.backer = ''
      row.pos = newPos
      itemRows.value.push(row)
      added += 1
    }
    rowsToEnrich.push(row)
  }

  // Tutup dialog & refresh tabel segera; enrich swatch/backing di belakang.
  soOpen.value = false
  ElMessage.success(
    t('pages.mrpRencana.soAddedRows', {
      n: added || groups.size,
      so: soSelected.value.length,
    }),
  )
  await nextTick()
  Promise.all(rowsToEnrich.map((row) => loadCombination(row))).catch(() => {})
}

function resetForm() {
  editCode.value = ''
  form.nama_rencana = ''
  form.tanggal_rencana = new Date().toISOString().slice(0, 10)
  itemRows.value = []
  Object.keys(soPoMeta).forEach((k) => delete soPoMeta[k])
}

function mapItemToRow(item) {
  const pos = (item.po_allocations || []).map((a) => ({
    po_id: a.po_id,
    qty: Number(a.qty_proses || 0),
  }))
  for (const a of item.po_allocations || []) {
    const id = Number(a.po_id)
    if (!id) continue
    soPoMeta[id] = {
      no_so: a.no_so || '',
      no_po: a.no_po || '',
      customer: item.nama_customer || '',
      lot_no: a.lot_no || a.lot_number || '',
    }
  }
  return {
    uid: ++rowUid,
    id: item.id ?? null,
    customer: item.nama_customer || '',
    material_name: item.material_name || '',
    emboss: item.emboss || '',
    color: item.color || '',
    color_swatch: item.color_swatch || '',
    thickness: item.thickness || '',
    backer: item.backer || '',
    keterangan: item.keterangan || '',
    pos,
    swatchOptions: item.color_swatch ? [item.color_swatch] : [],
    backerOptions: item.backer ? [item.backer] : [],
    comboOptions: [],
  }
}

async function loadEditData(id) {
  const data = await mrpGetRencana(id)
  editCode.value = data.rencana?.kode_rencana || ''
  form.nama_rencana = data.rencana?.nama_rencana || ''
  form.tanggal_rencana = data.rencana?.tanggal_rencana || new Date().toISOString().slice(0, 10)
  itemRows.value = (data.items || []).map(mapItemToRow)
  for (const row of itemRows.value) {
    await loadCombination(row)
  }
}

async function onOpen() {
  if (isEdit.value) {
    try {
      await loadEditData(props.editId)
    } catch (e) {
      ElMessage.error(e.message || String(e))
      visible.value = false
    }
    return
  }
  resetForm()
}

function validateRow(row, index) {
  const n = index + 1
  if (!row.pos?.length) return t('pages.mrpRencana.rowIncomplete', { n, field: t('pages.mrpRencana.soBtn') })
  if (!row.customer?.trim()) return t('pages.mrpRencana.rowIncomplete', { n, field: t('common.customer') })
  if (!row.material_name?.trim()) return t('pages.mrpRencana.rowIncomplete', { n, field: t('pages.mrpRencana.material') })
  if (!row.emboss?.trim()) return t('pages.mrpRencana.rowIncomplete', { n, field: t('pages.mrpRencana.emboss') })
  if (!row.color?.trim()) return t('pages.mrpRencana.rowIncomplete', { n, field: t('pages.mrpRencana.color') })
  if (!row.thickness?.trim()) return t('pages.mrpRencana.rowIncomplete', { n, field: t('pages.mrpRencana.thickness') })
  // Swatch & backing opsional
  return null
}

async function submitSave() {
  if (props.tourOpen) {
    ElMessage.info(t('pages.mrpRencana.tour.finishFirst'))
    return
  }
  if (!itemRows.value.length) {
    ElMessage.warning(t('pages.mrpRencana.selectPoRequired'))
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
    const payload = {
      customer: row.customer.trim(),
      material_name: row.material_name.trim(),
      emboss: row.emboss.trim(),
      color: row.color.trim(),
      color_swatch: (row.color_swatch || '').trim() || null,
      thickness: row.thickness.trim(),
      backer: (row.backer || '').trim() || null,
      keterangan: (row.keterangan || '').trim() || null,
      pos: (row.pos || []).map((p) => ({ po_id: p.po_id, qty: Number(p.qty || 0) })),
    }
    if (row.id) payload.id = row.id
    items.push(payload)
  }
  saving.value = true
  try {
    const body = {
      nama_rencana: form.nama_rencana.trim(),
      tanggal_rencana: form.tanggal_rencana,
      items,
    }
    if (isEdit.value) {
      await mrpUpdateRencana(props.editId, body)
    } else {
      await mrpCreateRencana(body)
    }
    ElMessage.success(t('common.saved'))
    visible.value = false
    emit('saved', { id: isEdit.value ? props.editId : null })
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

.mrp-rencana-header-fields {
  border-top: 1px dashed #cbd5e1;
  padding-top: 12px;
}

.mrp-rencana-create-dialog :deep(.el-dialog__body) {
  overflow: visible;
}

.mrp-lot-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  max-width: 100%;
  padding: 1px 7px;
  border-radius: 5px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  font-weight: 500;
  font-size: 12px;
  letter-spacing: 0.01em;
  line-height: 1.35;
  word-break: break-all;
}

.mrp-lot-badge--multi {
  cursor: pointer;
  appearance: none;
  font: inherit;
  text-align: left;
  border-color: #cbd5e1;
  background: #f1f5f9;
  color: #475569;
}

.mrp-lot-badge--multi:hover {
  border-color: #94a3b8;
  background: #e2e8f0;
  color: #334155;
}

.mrp-lot-badge__primary {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 9.5rem;
}

.mrp-lot-badge__more {
  flex-shrink: 0;
  padding: 0 4px;
  border-radius: 4px;
  background: #e2e8f0;
  color: #64748b;
  font-size: 11px;
  font-weight: 600;
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

.mrp-lot-popover {
  z-index: 6600 !important;
}

.mrp-lot-popover__title {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
}

.mrp-lot-popover__list {
  margin: 0;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.mrp-lot-popover__list li {
  padding: 4px 8px;
  border-radius: 4px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #475569;
  font-size: 12px;
  word-break: break-all;
}

.mrp-rencana-so-table .mrp-lot-col,
.mrp-rencana-items-table .mrp-lot-col {
  background: #f8fafc !important;
  border-left: 2px solid #cbd5e1 !important;
  border-right: 1px solid #e2e8f0 !important;
}

.mrp-rencana-so-table .mrp-lot-col-header,
.mrp-rencana-items-table .mrp-lot-col-header {
  background: #f1f5f9 !important;
  color: #64748b !important;
  font-weight: 600 !important;
  border-left: 2px solid #cbd5e1 !important;
  border-right: 1px solid #e2e8f0 !important;
}

.mrp-rencana-so-table .el-table__body tr.hover-row > td.mrp-lot-col,
.mrp-rencana-items-table .el-table__body tr.hover-row > td.mrp-lot-col,
.mrp-rencana-so-table .el-table__body tr:hover > td.mrp-lot-col,
.mrp-rencana-items-table .el-table__body tr:hover > td.mrp-lot-col {
  background: #f1f5f9 !important;
}
</style>
