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
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">
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
        table-layout="auto"
        :empty-text="t('pages.buyerPrices.tableEmpty')"
      >
        <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
        <el-table-column prop="buyer_code" :label="t('pages.buyerPrices.buyerCode')" width="120" show-overflow-tooltip />
        <el-table-column prop="title" :label="t('pages.buyerPrices.listTitle')" min-width="160" show-overflow-tooltip />
        <el-table-column prop="period_label" :label="t('pages.buyerPrices.period')" min-width="180" show-overflow-tooltip />
        <el-table-column prop="source_label" :label="t('pages.buyerPrices.source')" min-width="140" show-overflow-tooltip />
        <el-table-column :label="t('common.actions')" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <div class="flex flex-wrap items-center justify-center gap-0">
              <el-tooltip :content="t('pages.buyerPrices.manageData')" placement="top">
                <el-button
                  :icon="EditPen"
                  link
                  type="primary"
                  :aria-label="t('pages.buyerPrices.manageData')"
                  @click="openMaster(row.id)"
                />
              </el-tooltip>
              <el-tooltip :content="t('common.delete')" placement="top">
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
      width="480px"
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
        <el-form-item :label="t('pages.buyerPrices.listTitle')" prop="title">
          <el-input v-model="createForm.title" maxlength="255" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="createSaving" @click="submitCreate">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <!-- Drawer: master data (header + grid) -->
    <el-drawer v-model="masterDrawer" size="92%" :title="masterDrawerTitle" destroy-on-close @closed="onMasterClosed">
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
            <el-col :span="24">
              <el-form-item :label="t('pages.buyerPrices.source')">
                <el-input v-model="headerForm.source_label" maxlength="255" clearable />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <el-divider content-position="left">{{ t('pages.buyerPrices.sectionSheet') }}</el-divider>
        <div class="flex flex-wrap items-center gap-2 pb-2">
          <el-button type="primary" plain @click="promptAddColumn">{{ t('pages.buyerPrices.addColumn') }}</el-button>
          <el-button @click="addSheetRow">{{ t('pages.buyerPrices.addRow') }}</el-button>
          <el-button type="primary" :loading="masterSaving" @click="saveMaster">{{ t('pages.buyerPrices.saveSheet') }}</el-button>
        </div>

        <el-table :data="sheetRows" border stripe size="small" class="admin-table" max-height="52vh" table-layout="auto">
          <el-table-column type="index" :label="t('common.noLabel')" width="52" align="center" fixed />
          <el-table-column
            v-for="key in sheetColumnKeys"
            :key="key"
            :label="key"
            :min-width="key.length > 12 ? 160 : 120"
          >
            <template #default="{ row }">
              <el-input v-model="row[key]" size="small" clearable />
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
import { Delete, EditPen, Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import {
  createBuyerPriceList,
  deleteBuyerPriceList,
  getBuyerPriceList,
  listBuyerPriceLists,
  saveBuyerPriceSheet,
  toIsoDate,
  updateBuyerPriceList,
} from '../../api/client'

const { t } = useI18n()

const DEFAULT_COLUMNS = ['NO', 'ITEM', 'DESCRIPTION', 'UOM', 'PRICE']

const rows = ref([])
const loading = ref(false)
const keyword = ref('')

const createVisible = ref(false)
const createSaving = ref(false)
const createFormRef = ref(null)
const createForm = reactive({
  buyer_code: '',
  title: '',
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
  period_label: '',
  period_start: '',
  period_end: '',
  source_label: '',
})

const sheetColumnKeys = ref([])
const sheetRows = ref([])

const masterDrawerTitle = computed(() => {
  const code = masterBuyerCode.value || ''
  return code ? `${code} · ${t('pages.buyerPrices.masterDrawerTitle')}` : t('pages.buyerPrices.masterDrawerTitle')
})

const filteredRows = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  if (!k) return rows.value
  return rows.value.filter((r) => {
    const hay = [r.buyer_code, r.title, r.period_label, r.source_label]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return hay.includes(k)
  })
})

function inferColumnKeys(meta, dataRows) {
  const mk = meta?.column_keys
  if (Array.isArray(mk) && mk.length) {
    const seen = new Set(mk)
    const extra = []
    for (const r of dataRows || []) {
      if (r && typeof r === 'object') {
        for (const key of Object.keys(r)) {
          if (!seen.has(key)) {
            seen.add(key)
            extra.push(key)
          }
        }
      }
    }
    extra.sort((a, b) => a.localeCompare(b))
    return [...mk, ...extra]
  }
  const u = new Set()
  for (const r of dataRows || []) {
    if (r && typeof r === 'object') Object.keys(r).forEach((k) => u.add(k))
  }
  if (u.size) return [...u].sort((a, b) => a.localeCompare(b))
  return [...DEFAULT_COLUMNS]
}

function normalizeRows(dataRows, keys) {
  return (dataRows || []).map((r) => {
    const o = {}
    for (const k of keys) {
      const v = r && typeof r === 'object' ? r[k] : undefined
      o[k] = v != null && v !== '' ? String(v) : ''
    }
    return o
  })
}

function resetCreateForm() {
  createForm.buyer_code = ''
  createForm.title = ''
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
  sheetColumnKeys.value = []
}

async function openMaster(id) {
  activeListId.value = id
  masterDrawer.value = true
  masterLoading.value = true
  try {
    const d = await getBuyerPriceList(id)
    masterBuyerCode.value = d.buyer_code || ''
    headerForm.title = d.title || ''
    headerForm.period_label = d.period_label || ''
    headerForm.period_start = d.period_start || ''
    headerForm.period_end = d.period_end || ''
    headerForm.source_label = d.source_label || ''
    const keys = inferColumnKeys(d.meta_json, d.rows)
    sheetColumnKeys.value = keys
    sheetRows.value = normalizeRows(d.rows, keys)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    masterDrawer.value = false
  } finally {
    masterLoading.value = false
  }
}

function promptAddColumn() {
  ElMessageBox.prompt(t('pages.buyerPrices.columnNamePrompt'), t('pages.buyerPrices.addColumn'), {
    confirmButtonText: t('common.save'),
    cancelButtonText: t('common.cancel'),
    inputPattern: /\S/,
    inputErrorMessage: t('pages.buyerPrices.columnNamePrompt'),
  })
    .then(({ value }) => {
      const name = String(value).trim()
      if (!name) return
      if (sheetColumnKeys.value.includes(name)) {
        ElMessage.error(t('pages.buyerPrices.duplicateColumn'))
        return
      }
      sheetColumnKeys.value.push(name)
      sheetRows.value.forEach((r) => {
        r[name] = ''
      })
    })
    .catch(() => {})
}

function addSheetRow() {
  if (!sheetColumnKeys.value.length) {
    ElMessage.warning(t('pages.buyerPrices.needColumnFirst'))
    return
  }
  const o = {}
  sheetColumnKeys.value.forEach((k) => {
    o[k] = ''
  })
  sheetRows.value.push(o)
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
      period_label: emptyToNull(headerForm.period_label),
      period_start: toIsoDate(headerForm.period_start),
      period_end: toIsoDate(headerForm.period_end),
      source_label: emptyToNull(headerForm.source_label),
    })
    const keys = [...sheetColumnKeys.value]
    const rowsPayload = sheetRows.value.map((r) => {
      const o = {}
      keys.forEach((k) => {
        o[k] = r[k] ?? ''
      })
      return o
    })
    await saveBuyerPriceSheet(activeListId.value, {
      column_keys: keys,
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
</style>
