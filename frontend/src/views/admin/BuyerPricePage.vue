<template>
  <div class="space-y-4">
    <AdminSection :title="t('pages.buyerPrices.title')" :subtitle="t('pages.buyerPrices.subtitle')">
      <template #actions>
        <el-input
          v-model="keyword"
          :placeholder="t('pages.buyerPrices.searchPlaceholder')"
          clearable
          class="buyer-price-toolbar-search"
        />
        <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
        <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreateDialog">
          {{ t('common.create') }}
        </el-button>
      </template>

      <el-table
        :data="filteredRows"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        table-layout="fixed"
        :empty-text="t('pages.buyerPrices.tableEmpty')"
      >
        <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
        <el-table-column prop="buyer_code" :label="t('pages.buyerPrices.buyerCode')" width="120" show-overflow-tooltip />
        <el-table-column prop="currency" :label="t('pages.buyerPrices.currency')" width="90" align="center" />
        <el-table-column prop="title" :label="t('pages.buyerPrices.listTitle')" min-width="160" show-overflow-tooltip />
        <el-table-column prop="period_label" :label="t('pages.buyerPrices.period')" min-width="180" show-overflow-tooltip />
        <el-table-column :label="t('pages.buyerPrices.itemList')" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            {{ previewList(row.item_codes) }}
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.buyerPrices.priceComponentsFilled')" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            {{ previewList(row.filled_price_components) }}
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="130" align="center" fixed="right">
          <template #default="{ row }">
            <div class="flex flex-wrap items-center justify-center gap-0">
              <el-tooltip :content="t('pages.buyerPrices.viewDetail')" placement="top">
                <el-button
                  :icon="View"
                  link
                  type="info"
                  :aria-label="t('pages.buyerPrices.viewDetail')"
                  @click="openDetail(row.id)"
                />
              </el-tooltip>
              <el-tooltip v-if="canUpdate" :content="t('pages.buyerPrices.manageData')" placement="top">
                <el-button
                  :icon="EditPen"
                  link
                  type="primary"
                  :aria-label="t('pages.buyerPrices.manageData')"
                  @click="openMaster(row.id)"
                />
              </el-tooltip>
              <el-tooltip v-if="canDelete" :content="t('common.delete')" placement="top">
                <el-button
                  :icon="Delete"
                  link
                  type="danger"
                  :aria-label="t('common.delete')"
                  @click="confirmDelete(row)"
                />
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </AdminSection>

    <!-- Dialog: buat list buyer baru -->
    <el-dialog
      v-model="createVisible"
      :title="t('pages.buyerPrices.dialogAdd')"
      width="600px"
      destroy-on-close
      align-center
      @closed="resetCreateForm"
    >
      <p class="mb-3 text-sm text-slate-600">{{ t('pages.buyerPrices.formHint') }}</p>
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-position="top" @submit.prevent>
        <el-form-item :label="t('pages.buyerPrices.buyerCode')" prop="buyer_code">
          <el-input
            v-model="createForm.buyer_code"
            :placeholder="t('pages.buyerPrices.placeholderBuyerCode')"
            maxlength="32"
            show-word-limit
            clearable
          />
        </el-form-item>
        <el-form-item :label="t('pages.buyerPrices.currency')">
          <el-select v-model="createForm.currency" class="w-full">
            <el-option label="USD" value="USD" />
            <el-option label="IDR" value="IDR" />
            <el-option label="EUR" value="EUR" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.buyerPrices.listTitle')" prop="title">
          <el-input v-model="createForm.title" maxlength="255" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="createVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate" type="primary" :icon="Check" :loading="createSaving" @click="submitCreate">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailVisible"
      :title="t('pages.buyerPrices.detailDialogTitle')"
      width="900px"
      destroy-on-close
      align-center
    >
      <div v-loading="detailLoading" class="space-y-3">
        <el-descriptions v-if="detailData" :column="2" border size="small">
          <el-descriptions-item :label="t('pages.buyerPrices.buyerCode')">{{ detailData.buyer_code || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="t('pages.buyerPrices.currency')">{{ detailData.currency || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="t('pages.buyerPrices.listTitle')">{{ detailData.title || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="t('pages.buyerPrices.period')">{{ detailData.period_label || '-' }}</el-descriptions-item>
          <el-descriptions-item :label="t('pages.buyerPrices.itemList')" :span="2">
            {{ previewList(extractUniqueItems(detailData.rows), 30) }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.buyerPrices.priceComponentsFilled')" :span="2">
            {{ previewList(extractFilledComponents(detailData.rows), 30) }}
          </el-descriptions-item>
        </el-descriptions>
        <el-table
          v-if="detailData"
          :data="normalizeRows(detailData.rows)"
          border
          stripe
          size="small"
          class="admin-table"
          max-height="48vh"
          table-layout="auto"
        >
          <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
          <el-table-column prop="ITEM" label="ITEM" min-width="180" show-overflow-tooltip />
          <el-table-column prop="THICKNESS" label="THICKNESS" min-width="110" show-overflow-tooltip />
          <el-table-column prop="COLOR" label="COLOR" min-width="110" show-overflow-tooltip />
          <el-table-column prop="COLOR WHITE" label="COLOR WHITE" min-width="130" />
          <el-table-column prop="COLOR BLACK" label="COLOR BLACK" min-width="130" />
          <el-table-column prop="FLOURASENT" label="FLOURASENT" min-width="120" />
          <el-table-column prop="METALIC" label="METALIC" min-width="110" />
          <el-table-column prop="EMBOSS" label="EMBOSS" min-width="110" />
          <el-table-column prop="SPESIAL EMBOSS" label="SPESIAL EMBOSS" min-width="150" />
        </el-table>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">{{ t('common.close') }}</el-button>
      </template>
    </el-dialog>

    <!-- Drawer: master data (header + grid) -->
    <el-drawer v-model="masterDrawer" :size="drawerSize" :title="masterDrawerTitle" destroy-on-close @closed="onMasterClosed">
      <div v-loading="masterLoading" class="buyer-master space-y-4">
        <el-divider content-position="left">{{ t('pages.buyerPrices.sectionHeader') }}</el-divider>
        <el-form label-position="top" class="max-w-4xl">
          <el-row :gutter="16">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="t('pages.buyerPrices.listTitle')">
                <el-input v-model="headerForm.title" maxlength="255" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item :label="t('pages.buyerPrices.periodLabel')">
                <el-input v-model="headerForm.period_label" maxlength="255" clearable />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="t('pages.buyerPrices.currency')">
                <el-select v-model="headerForm.currency" class="w-full">
                  <el-option label="USD" value="USD" />
                  <el-option label="IDR" value="IDR" />
                  <el-option label="EUR" value="EUR" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="t('pages.buyerPrices.periodStart')">
                <el-date-picker
                  v-model="headerForm.period_start"
                  type="date"
                  value-format="YYYY-MM-DD"
                  class="w-full"
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="t('pages.buyerPrices.periodEnd')">
                <el-date-picker
                  v-model="headerForm.period_end"
                  type="date"
                  value-format="YYYY-MM-DD"
                  class="w-full"
                  clearable
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <el-divider content-position="left">{{ t('pages.buyerPrices.sectionSheet') }}</el-divider>
        <el-alert type="info" :closable="false" class="mb-2">
          Harga dihitung dari base <strong>COLOR WHITE</strong>. Kolom +COLOR BLACK, +FLOURASENT, +METALIC, +EMBOSS,
          dan +SPESIAL EMBOSS adalah nilai penambahan dari base.
        </el-alert>
        <div class="flex flex-wrap items-center gap-2 pb-2">
          <el-button @click="addSheetRow">{{ t('pages.buyerPrices.addRow') }}</el-button>
          <el-button v-if="canUpdate" type="primary" :loading="masterSaving" @click="saveMaster">{{ t('pages.buyerPrices.saveSheet') }}</el-button>
        </div>

        <el-table :data="sheetRows" border stripe size="small" class="admin-table" max-height="52vh" table-layout="auto">
          <el-table-column type="index" label="NO" width="52" align="center" fixed />
          <el-table-column label="ITEM" min-width="200" fixed>
            <template #default="{ row }">
              <el-select
                v-model="row.ITEM"
                filterable
                clearable
                placeholder="Pilih Material"
                class="w-full"
                size="small"
                @change="onItemChange(row)"
              >
                <el-option
                  v-for="item in masterItems"
                  :key="`${item.item_code}-${item.material_name}`"
                  :label="itemOptionLabel(item)"
                  :value="item.material_name || item.item_code || ''"
                />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column label="THICKNESS" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.THICKNESS" size="small" disabled />
            </template>
          </el-table-column>
          <el-table-column label="COLOR" min-width="120">
            <template #default="{ row }">
              <el-input v-model="row.COLOR" size="small" disabled />
            </template>
          </el-table-column>
          <el-table-column label="COLOR WHITE (BASE)" min-width="150">
            <template #default="{ row }">
              <el-input-number
                v-model="row['COLOR WHITE']"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column label="+ COLOR BLACK" min-width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row['COLOR BLACK']"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
                @change="(val) => onAddonPriceChange(row, 'COLOR BLACK', val)"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column label="+ FLOURASENT" min-width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row.FLOURASENT"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
                @change="(val) => onAddonPriceChange(row, 'FLOURASENT', val)"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column label="+ METALIC" min-width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row.METALIC"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
                @change="(val) => onAddonPriceChange(row, 'METALIC', val)"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column label="+ EMBOSS" min-width="120">
            <template #default="{ row }">
              <el-input-number
                v-model="row.EMBOSS"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
                @change="(val) => onAddonPriceChange(row, 'EMBOSS', val)"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column label="+ SPESIAL EMBOSS" min-width="140">
            <template #default="{ row }">
              <el-input-number
                v-model="row['SPESIAL EMBOSS']"
                size="small"
                :controls="false"
                :min="0"
                :precision="2"
                :step="0.01"
                class="w-full"
                placeholder="0"
                @change="(val) => onAddonPriceChange(row, 'SPESIAL EMBOSS', val)"
              >
                <template #suffix>
                  <span class="buyer-price-currency-suffix">{{ headerForm.currency || 'USD' }}</span>
                </template>
              </el-input-number>
            </template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="72" align="center" fixed="right">
            <template #default="{ $index }">
              <el-tooltip :content="t('pages.buyerPrices.removeRow')" placement="top">
                <el-button
                  link
                  type="danger"
                  size="small"
                  :icon="Delete"
                  :aria-label="t('pages.buyerPrices.removeRow')"
                  @click="removeSheetRow($index)"
                />
              </el-tooltip>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Delete, EditPen, Plus, Close, Check, View } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import {
  createBuyerPriceList,
  deleteBuyerPriceList,
  getBuyerPriceList,
  listBuyerPriceLists,
  listMasterItems,
  saveBuyerPriceSheet,
  toIsoDate,
  updateBuyerPriceList,
} from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canCreate, canUpdate, canDelete } = useModulePermission('buyerPrices')

const SHEET_COLUMNS = ['ITEM', 'THICKNESS', 'COLOR', 'COLOR WHITE', 'COLOR BLACK', 'FLOURASENT', 'METALIC', 'EMBOSS', 'SPESIAL EMBOSS']

const rows = ref([])
const loading = ref(false)
const keyword = ref('')
const masterItems = ref([])
const detailVisible = ref(false)
const detailLoading = ref(false)
const detailData = ref(null)

const createVisible = ref(false)
const createSaving = ref(false)
const createFormRef = ref(null)
const createForm = reactive({
  buyer_code: '',
  title: '',
  currency: 'USD',
})
const createRules = computed(() => ({
  buyer_code: [{ required: true, message: t('pages.buyerPrices.ruleBuyerCode'), trigger: 'blur' }],
}))

const masterDrawer = ref(false)
const masterLoading = ref(false)
const masterSaving = ref(false)
const activeListId = ref(null)
const masterBuyerCode = ref('')

const headerForm = reactive({
  title: '',
  currency: 'USD',
  period_label: '',
  period_start: '',
  period_end: '',
})

const sheetRows = ref([])

const masterDrawerTitle = computed(() => {
  const code = masterBuyerCode.value || ''
  return code ? `${code} · ${t('pages.buyerPrices.masterDrawerTitle')}` : t('pages.buyerPrices.masterDrawerTitle')
})

const filteredRows = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  if (!k) return rows.value
  return rows.value.filter((r) => {
    const hay = [r.buyer_code, r.title, r.period_label, r.currency]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return hay.includes(k)
  })
})

function normalizeRows(dataRows) {
  return (dataRows || []).map((r) => {
    const o = {}
    for (const k of SHEET_COLUMNS) {
      const v = r && typeof r === 'object' ? r[k] : undefined
      if (v == null || v === '') {
        o[k] = ''
      } else if (isPriceColumn(k)) {
        const num = Number(v)
        o[k] = Number.isFinite(num) ? num : ''
      } else {
        o[k] = String(v)
      }
    }
    return o
  })
}

function createEmptyRow() {
  const o = {}
  SHEET_COLUMNS.forEach((k) => {
    o[k] = isPriceColumn(k) ? null : ''
  })
  return o
}

const PRICE_COLUMNS = new Set(['COLOR WHITE', 'COLOR BLACK', 'FLOURASENT', 'METALIC', 'EMBOSS', 'SPESIAL EMBOSS'])

function isPriceColumn(key) {
  return PRICE_COLUMNS.has(String(key || '').trim().toUpperCase())
}

function parseNumber(val) {
  if (val == null || val === '') return null
  const n = Number(val)
  return Number.isFinite(n) ? n : null
}

function previewList(arr, max = 3) {
  const list = (arr || []).filter(Boolean)
  if (!list.length) return '-'
  if (list.length <= max) return list.join(', ')
  return `${list.slice(0, max).join(', ')} +${list.length - max}`
}

function extractUniqueItems(dataRows) {
  const seen = new Set()
  const out = []
  for (const row of dataRows || []) {
    const code = String(row?.ITEM || '').trim()
    if (!code || seen.has(code)) continue
    seen.add(code)
    out.push(code)
  }
  return out
}

function extractFilledComponents(dataRows) {
  const keys = ['COLOR WHITE', 'COLOR BLACK', 'FLOURASENT', 'METALIC', 'EMBOSS', 'SPESIAL EMBOSS']
  const out = []
  for (const key of keys) {
    const hasValue = (dataRows || []).some((row) => {
      const v = row?.[key]
      if (v == null || v === '') return false
      const n = Number(v)
      return Number.isFinite(n) && n > 0
    })
    if (hasValue) out.push(key)
  }
  return out
}

function formatPopupNumber(val) {
  return Number(val).toLocaleString('id-ID', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function onAddonPriceChange(row, addonKey, addonValue) {
  const addon = parseNumber(addonValue)
  if (addon == null) return
  const base = parseNumber(row['COLOR WHITE'])
  if (base == null) {
    ElMessage.warning(t('pages.buyerPrices.popupNeedBase'))
    return
  }
  const total = base + addon
  ElMessage.info(
    t('pages.buyerPrices.popupAddonTotal', {
      addon: addonKey,
      value: formatPopupNumber(addon),
      total: formatPopupNumber(total),
    }),
  )
}

function onItemChange(row) {
  const selected = masterItems.value.find((i) => (i.material_name || '') === row.ITEM)
  if (selected) {
    row.THICKNESS = selected.thickness_range || ''
    const suggestions = colorSuggestionsFromItem(selected)
    row.COLOR = suggestions[0] || selected.color_standard || selected.color_reference || selected.color || ''
  }
}

function itemOptionLabel(item) {
  return item.material_name || item.item_code || '-'
}

function colorSuggestionsFromItem(item) {
  const src = [item?.color_standard, item?.color_reference]
    .filter(Boolean)
    .join(',')
  const out = []
  for (const raw of src.split(/[,/;|]/)) {
    const v = String(raw || '').trim()
    if (v && !out.includes(v)) out.push(v)
  }
  return out
}

function queryColorSuggestions(row, queryString, cb) {
  const selected = masterItems.value.find((i) => (i.material_name || '') === row.ITEM)
  const options = selected ? colorSuggestionsFromItem(selected) : []
  const q = (queryString || '').trim().toLowerCase()
  cb(options.filter((x) => !q || x.toLowerCase().includes(q)).slice(0, 12).map((x) => ({ value: x })))
}

function resetCreateForm() {
  createForm.buyer_code = ''
  createForm.title = ''
  createForm.currency = 'USD'
  headerForm.currency = 'USD'
}

function openCreateDialog() {
  resetCreateForm()
  createVisible.value = true
}

function emptyToNull(s) {
  const v = typeof s === 'string' ? s.trim() : s
  return v === '' || v == null ? null : v
}

async function submitCreate() {
  if (!createFormRef.value) return
  try {
    await createFormRef.value.validate()
  } catch {
    return
  }
  createSaving.value = true
  try {
    const created = await createBuyerPriceList({
      buyer_code: createForm.buyer_code.trim(),
      currency: createForm.currency || 'USD',
      title: emptyToNull(createForm.title),
    })
    ElMessage.success(t('pages.buyerPrices.saved'))
    createVisible.value = false
    await load()
    await openMaster(created.id)
  } catch (e) {
    const msg = e?.message || ''
    if (msg.includes('409') || msg.toLowerCase().includes('already')) {
      ElMessage.error(t('pages.buyerPrices.duplicateBuyer'))
    } else {
      ElMessage.error(msg || t('common.errorGeneric'))
    }
  } finally {
    createSaving.value = false
  }
}

function onMasterClosed() {
  activeListId.value = null
  masterBuyerCode.value = ''
  sheetRows.value = []
}

const drawerSize = computed(() => {
  const w = window.innerWidth
  if (w < 768) return '100%'
  if (w < 1200) return '80%'
  return '90%'
})

async function openMaster(id) {
  activeListId.value = id
  masterDrawer.value = true
  masterLoading.value = true
  try {
    const d = await getBuyerPriceList(id)
    masterBuyerCode.value = d.buyer_code || ''
    headerForm.title = d.title || ''
    headerForm.currency = d.currency || 'USD'
    headerForm.period_label = d.period_label || ''
    headerForm.period_start = d.period_start || ''
    headerForm.period_end = d.period_end || ''
    sheetRows.value = normalizeRows(d.rows)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    masterDrawer.value = false
    masterLoading.value = false
    return
  }
  try {
    const items = await listMasterItems()
    masterItems.value = items || []
  } catch (e) {
    console.warn('Failed to load master items:', e)
    masterItems.value = []
  } finally {
    masterLoading.value = false
  }
}

async function openDetail(id) {
  detailVisible.value = true
  detailLoading.value = true
  try {
    detailData.value = await getBuyerPriceList(id)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    detailVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

function addSheetRow() {
  sheetRows.value.push(createEmptyRow())
}

function removeSheetRow(index) {
  sheetRows.value.splice(index, 1)
}

async function saveMaster() {
  if (activeListId.value == null) return
  masterSaving.value = true
  try {
    await updateBuyerPriceList(activeListId.value, {
      title: emptyToNull(headerForm.title),
      currency: emptyToNull(headerForm.currency) || 'USD',
      period_label: emptyToNull(headerForm.period_label),
      period_start: toIsoDate(headerForm.period_start),
      period_end: toIsoDate(headerForm.period_end),
    })
    const rowsPayload = sheetRows.value.map((r) => {
      const o = {}
      SHEET_COLUMNS.forEach((k) => {
        o[k] = r[k] ?? ''
      })
      return o
    })
    await saveBuyerPriceSheet(activeListId.value, {
      column_keys: SHEET_COLUMNS,
      rows: rowsPayload,
    })
    ElMessage.success(t('pages.buyerPrices.sheetSaved'))
    await load()
    await openMaster(activeListId.value)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    masterSaving.value = false
  }
}

async function load() {
  loading.value = true
  try {
    rows.value = await listBuyerPriceLists()
  } finally {
    loading.value = false
  }
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(t('pages.buyerPrices.confirmDelete'), t('common.confirm'), {
      type: 'warning',
    })
    await deleteBuyerPriceList(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
    if (activeListId.value === row.id) {
      masterDrawer.value = false
    }
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

onMounted(load)
</script>

<style scoped>
.buyer-price-toolbar-search {
  min-width: 220px;
  flex: 1 1 220px;
  max-width: 100%;
  margin-right: 8px;
  vertical-align: middle;
}
.buyer-master :deep(.el-drawer__body) {
  padding-top: 0;
}
.buyer-price-currency-suffix {
  display: inline-block;
  min-width: 2.5rem;
  text-align: right;
  font-size: 12px;
  color: #64748b;
}
@media (max-width: 768px) {
  :deep(.el-drawer) {
    width: 100% !important;
  }
}
</style>
