<template>
  <div class="space-y-4">
    <AdminSection :title="t('pages.customs.title')" :hint="pageHint">
      <template #actions>
        <el-input
          v-model="keyword"
          :placeholder="t('pages.customs.searchPlaceholder')"
          clearable
          class="customs-toolbar-search"
        />
        <el-button v-if="canCreate" :icon="Upload" @click="openImportDialog">
          {{ t('pages.customs.importZip') }}
        </el-button>
        <el-button v-if="canCreate" type="primary" :icon="Plus" :loading="loading" @click="openCreateDialog">
          {{ t('common.create') }}
        </el-button>
      </template>

      <el-card class="mb-4" shadow="never">
        <template #header>
          <span class="font-medium">{{ t('pages.customs.generateFromDelivery') }}</span>
        </template>
        <el-row :gutter="16" align="middle">
          <el-col :xs="24" :sm="12" :md="8">
            <el-select
              v-model="selectedDeliveryId"
              :placeholder="t('pages.customs.selectDelivery')"
              filterable
              clearable
              class="w-full"
              @visible-change="onDeliveryDropdown"
            >
              <el-option
                v-for="d in deliveryOptions"
                :key="d.id"
                :label="deliveryOptionLabel(d)"
                :value="d.id"
              />
            </el-select>
          </el-col>
          <el-col :xs="24" :sm="12" :md="8">
            <el-button
              type="success"
              :loading="generating"
              :disabled="!selectedDeliveryId"
              @click="handleGenerateAju"
            >
              {{ t('pages.customs.generateFromDelivery') }}
            </el-button>
          </el-col>
        </el-row>

        <div v-if="generatedAju" class="mt-4">
          <el-divider content-position="left">{{ t('pages.customs.ajuData') }}</el-divider>
          <el-alert
            v-if="generatedAju.already_linked"
            type="info"
            :closable="false"
            class="mb-3"
            :title="t('pages.customs.alreadyLinked')"
          />
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item :label="t('pages.customs.ajuNumber')">
              <strong>{{ generatedAju.nomor_aju }}</strong>
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.customs.deliveryNumber')">
              {{ generatedAju.delivery_number }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.customs.customerName')">
              {{ generatedAju.customer_name }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.customs.poNumber')">
              {{ generatedAju.po_number }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.customs.totalQty')">
              {{ generatedAju.total_qty }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.customs.totalRoll')">
              {{ generatedAju.total_roll }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.customs.totalPcs')">
              {{ generatedAju.total_pcs }}
            </el-descriptions-item>
          </el-descriptions>
          <div v-if="generatedAju.id && canUpdate" class="mt-3">
            <el-button type="primary" @click="openMaster(generatedAju.id)">
              {{ t('pages.customs.manageDraft') }}
            </el-button>
          </div>
        </div>
      </el-card>

      <el-table
        :data="filteredRows"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        table-layout="fixed"
        :empty-text="t('pages.customs.tableEmpty')"
      >
        <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
        <el-table-column prop="nomor_aju" :label="t('pages.customs.nomorAju')" min-width="180" show-overflow-tooltip />
        <el-table-column prop="kode_dokumen" :label="t('pages.customs.kodeDok')" width="88" show-overflow-tooltip />
        <el-table-column prop="delivery_number" :label="t('pages.customs.deliveryNumber')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="customer_name" :label="t('pages.customs.customerName')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="source_label" :label="t('pages.customs.source')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="versi_template" :label="t('pages.customs.versi')" width="72" show-overflow-tooltip />
        <el-table-column :label="t('common.actions')" width="132" align="center" fixed="right">
          <template #default="{ row }">
            <div class="flex flex-wrap items-center justify-center gap-0">
              <el-tooltip v-if="canUpdate" :content="t('pages.customs.exportZip')" placement="top">
                <el-button
                  :icon="Download"
                  link
                  type="success"
                  :aria-label="t('pages.customs.exportZip')"
                  @click="handleExportZip(row.id)"
                />
              </el-tooltip>
              <el-tooltip v-if="canUpdate" :content="t('pages.customs.manageData')" placement="top">
                <el-button
                  :icon="EditPen"
                  link
                  type="primary"
                  :aria-label="t('pages.customs.manageData')"
                  @click="openMaster(row.id)"
                />
              </el-tooltip>
              <el-tooltip v-if="canDelete" :content="t('common.delete')" placement="top">
                <el-button :icon="Delete" link type="danger" :aria-label="t('common.delete')" @click="confirmDelete(row)" />
              </el-tooltip>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </AdminSection>

    <el-dialog
      v-model="createVisible"
      width="520px"
      destroy-on-close
      align-center
      @closed="resetCreateForm"
    >
      <template #header>
        <div class="customs-dialog-header">
          <h3 class="customs-dialog-header__title">{{ t('pages.customs.dialogAdd') }}</h3>
          <el-tooltip placement="top-start" :show-after="200">
            <template #content>{{ t('pages.customs.formHint') }}</template>
            <el-icon
              class="customs-hint-icon"
              :size="16"
              tabindex="0"
              :aria-label="t('pages.customs.formHint')"
            >
              <InfoFilled />
            </el-icon>
          </el-tooltip>
        </div>
      </template>
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-position="top" @submit.prevent>
        <el-form-item :label="t('pages.customs.nomorAju')" prop="nomor_aju">
          <el-input
            v-model="createForm.nomor_aju"
            :placeholder="t('pages.customs.placeholderNomorAju')"
            maxlength="64"
            show-word-limit
            clearable
          />
        </el-form-item>
        <el-form-item :label="t('pages.customs.kodeDok')">
          <el-input v-model="createForm.kode_dokumen" maxlength="16" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.customs.source')">
          <el-input v-model="createForm.source_label" maxlength="255" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.customs.versi')">
          <el-input v-model="createForm.versi_template" maxlength="32" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate" type="primary" :loading="createSaving" @click="submitCreate">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="masterDrawer" size="94%" :title="masterDrawerTitle" destroy-on-close @closed="onMasterClosed">
      <div v-loading="masterLoading" class="customs-master space-y-4">
        <el-divider content-position="left">{{ t('pages.customs.sectionHeader') }}</el-divider>
        <p class="text-sm text-slate-500">
          <span class="font-medium text-slate-700">{{ t('pages.customs.nomorAju') }}:</span>
          {{ masterNomorAju || t('common.emptyValue') }}
        </p>
        <el-form label-position="top" class="max-w-3xl">
          <el-row :gutter="16">
            <el-col :xs="24" :sm="8">
              <el-form-item :label="t('pages.customs.kodeDok')">
                <el-input v-model="headerForm.kode_dokumen" maxlength="16" clearable />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="8">
              <el-form-item :label="t('pages.customs.versi')">
                <el-input v-model="headerForm.versi_template" maxlength="32" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item :label="t('pages.customs.source')">
                <el-input v-model="headerForm.source_label" maxlength="255" clearable />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>

        <el-divider content-position="left">{{ t('pages.customs.sectionSheets') }}</el-divider>
        <div class="flex flex-wrap items-center gap-2 pb-2">
          <el-button v-if="canUpdate" type="primary" plain @click="promptAddSheet">{{ t('pages.customs.addSheet') }}</el-button>
          <el-button v-if="canUpdate" type="success" plain :icon="Download" @click="handleExportZip(activeListId)">
            {{ t('pages.customs.exportZip') }}
          </el-button>
          <el-button v-if="canUpdate" type="primary" :loading="masterSaving" @click="saveMaster">{{ t('pages.customs.saveSheets') }}</el-button>
        </div>

        <el-tabs v-if="tabCodes.length" v-model="activeSheetTab" type="border-card" class="customs-tabs">
          <el-tab-pane
            v-for="code in tabCodes"
            :key="code"
            :label="`${code} (${sheetRowCount(code)})`"
            :name="code"
          >
            <div class="mb-3 flex flex-wrap gap-2">
              <el-button size="small" @click="() => promptAddColumn(code)">{{ t('pages.customs.addColumn') }}</el-button>
              <el-button size="small" @click="() => addSheetRow(code)">{{ t('pages.customs.addRow') }}</el-button>
              <el-button size="small" type="danger" plain @click="() => removeSheet(code)">
                {{ t('pages.customs.removeSheet') }}
              </el-button>
            </div>
            <el-table
              :data="sheetBlock(code).rows"
              border
              stripe
              size="small"
              class="admin-table"
              max-height="48vh"
              table-layout="auto"
            >
              <el-table-column type="index" :label="t('common.noLabel')" width="52" align="center" fixed />
              <el-table-column
                v-for="key in sheetBlock(code).columnKeys"
                :key="`${code}-${key}`"
                :label="key"
                :min-width="key.length > 14 ? 168 : 120"
              >
                <template #default="{ row }">
                  <el-input v-model="row[key]" size="small" clearable />
                </template>
              </el-table-column>
              <el-table-column :label="t('common.actions')" width="72" align="center" fixed="right">
                <template #default="{ $index }">
                  <el-tooltip :content="t('pages.customs.removeRow')" placement="top">
                    <el-button
                      link
                      type="danger"
                      size="small"
                      :icon="Delete"
                      :aria-label="t('pages.customs.removeRow')"
                      @click="removeSheetRow(code, $index)"
                    />
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
        <p v-else class="text-sm text-slate-500">{{ t('pages.customs.addSheet') }}</p>
      </div>
    </el-drawer>

    <el-dialog
      v-model="importVisible"
      width="520px"
      destroy-on-close
      align-center
      @closed="resetImportForm"
    >
      <template #header>
        <div class="customs-dialog-header">
          <h3 class="customs-dialog-header__title">{{ t('pages.customs.importZip') }}</h3>
          <el-tooltip placement="top-start" :show-after="200">
            <template #content>{{ t('pages.customs.importHint') }}</template>
            <el-icon
              class="customs-hint-icon"
              :size="16"
              tabindex="0"
              :aria-label="t('pages.customs.importHint')"
            >
              <InfoFilled />
            </el-icon>
          </el-tooltip>
        </div>
      </template>
      <el-form label-position="top">
        <el-form-item :label="t('pages.customs.source')">
          <el-input v-model="importSourceLabel" maxlength="255" clearable />
        </el-form-item>
        <el-form-item :label="t('pages.customs.importZip')">
          <el-upload
            ref="importUploadRef"
            :auto-upload="false"
            :limit="1"
            accept=".zip"
            :on-change="onImportFileChange"
            :on-remove="onImportFileRemove"
          >
            <el-button type="primary">{{ t('pages.customs.selectZip') }}</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="importVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button v-if="canCreate" type="primary" :loading="importSaving" :disabled="!importFile" @click="submitImport">
          {{ t('pages.customs.importZip') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Delete, Download, EditPen, InfoFilled, Plus, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import AdminSection from '../../components/AdminSection.vue'
import {
  createCustomsDeclaration,
  deleteCustomsDeclaration,
  exportCustomsZip,
  generateCustomsFromDelivery,
  getCustomsDeclaration,
  importCustomsZip,
  listCustomsDeclarations,
  listDelivery,
  saveCustomsSheetsData,
  updateCustomsDeclaration,
} from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canCreate, canUpdate, canDelete } = useModulePermission('customs')

const pageHint = computed(() =>
  [t('pages.customs.subtitle'), '', `${t('pages.customs.workflowTitle')}:`, t('pages.customs.workflowHint')].join('\n')
)

const selectedDeliveryId = ref(null)
const deliveryOptions = ref([])
const generating = ref(false)
const generatedAju = ref(null)

const importVisible = ref(false)
const importSaving = ref(false)
const importFile = ref(null)
const importSourceLabel = ref('')
const importUploadRef = ref(null)

function openImportDialog() {
  resetImportForm()
  importVisible.value = true
}

function resetImportForm() {
  importFile.value = null
  importSourceLabel.value = ''
  importUploadRef.value?.clearFiles?.()
}

function onImportFileChange(uploadFile) {
  importFile.value = uploadFile?.raw || null
}

function onImportFileRemove() {
  importFile.value = null
}

async function submitImport() {
  if (!importFile.value) return
  importSaving.value = true
  try {
    const created = await importCustomsZip(importFile.value, importSourceLabel.value.trim() || undefined)
    ElMessage.success(t('pages.customs.importOk'))
    importVisible.value = false
    await load()
    if (created?.id) await openMaster(created.id)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    importSaving.value = false
  }
}

async function handleExportZip(id) {
  if (id == null) return
  try {
    await exportCustomsZip(id)
    ElMessage.success(t('pages.customs.exportOk'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function onDeliveryDropdown(open) {
  if (open) {
    try {
      const data = await listDelivery()
      deliveryOptions.value = data.map((d) => ({
        id: d.id,
        delivery_number: d.delivery_number,
        customer_name: d.customer_name || '',
        customs_declaration_id: d.customs_declaration_id || null,
      }))
    } catch {
      deliveryOptions.value = []
    }
  }
}

function deliveryOptionLabel(d) {
  const base = `${d.delivery_number || d.id} — ${d.customer_name || ''}`.trim()
  return d.customs_declaration_id ? `${base} (${t('pages.customs.hasAju')})` : base
}

async function handleGenerateAju() {
  if (!selectedDeliveryId.value) {
    ElMessage.warning(t('pages.customs.noDeliverySelected'))
    return
  }
  generating.value = true
  try {
    generatedAju.value = await generateCustomsFromDelivery(selectedDeliveryId.value)
    const msg = generatedAju.value?.already_linked
      ? t('pages.customs.alreadyLinked')
      : t('pages.customs.generatedSaved')
    ElMessage.success(msg)
    await load()
    if (generatedAju.value?.id) {
      const opt = deliveryOptions.value.find((d) => d.id === selectedDeliveryId.value)
      if (opt) opt.customs_declaration_id = generatedAju.value.id
    }
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    generating.value = false
  }
}

/** Selaras urutan tampilan backend `customs_import.SHEET_CODES_ORDER`. */
const SHEET_CODES_ORDER = [
  'HEADER',
  'ENTITAS',
  'DOKUMEN',
  'PENGANGKUT',
  'KEMASAN',
  'KONTAINER',
  'BARANG',
  'BARANGTARIF',
  'BARANGDOKUMEN',
  'BARANGENTITAS',
  'BARANGSPEKKHUSUS',
  'BARANGVD',
  'BAHANBAKU',
  'BAHANBAKUTARIF',
  'BAHANBAKUDOKUMEN',
  'PUNGUTAN',
  'JAMINAN',
  'BANKDEVISA',
  'VERSI',
]

const rows = ref([])
const loading = ref(false)
const keyword = ref('')

const createVisible = ref(false)
const createSaving = ref(false)
const createFormRef = ref(null)
const createForm = reactive({
  nomor_aju: '',
  kode_dokumen: '',
  source_label: '',
  versi_template: '',
})
const createRules = computed(() => ({
  nomor_aju: [{ required: true, message: t('pages.customs.ruleNomorAju'), trigger: 'blur' }],
}))

const masterDrawer = ref(false)
const masterLoading = ref(false)
const masterSaving = ref(false)
const activeListId = ref(null)
const masterNomorAju = ref('')
const headerForm = reactive({
  kode_dokumen: '',
  source_label: '',
  versi_template: '',
})

/** @type {import('vue').Ref<Record<string, { columnKeys: string[], rows: Record<string, string>[] }>>} */
const sheetsState = ref({})
const activeSheetTab = ref('HEADER')

const masterDrawerTitle = computed(() => {
  const n = masterNomorAju.value || ''
  return n ? `${n} · ${t('pages.customs.masterDrawerTitle')}` : t('pages.customs.masterDrawerTitle')
})

const tabCodes = computed(() => {
  const state = sheetsState.value
  const keys = Object.keys(state)
  const ordered = []
  for (const c of SHEET_CODES_ORDER) {
    if (keys.includes(c)) ordered.push(c)
  }
  for (const k of [...keys].sort((a, b) => a.localeCompare(b))) {
    if (!ordered.includes(k)) ordered.push(k)
  }
  return ordered
})

watch(tabCodes, (codes) => {
  if (!codes.length) return
  if (!codes.includes(activeSheetTab.value)) {
    activeSheetTab.value = codes[0]
  }
})

const filteredRows = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  if (!k) return rows.value
  return rows.value.filter((r) => {
    const hay = [
      r.nomor_aju,
      r.kode_dokumen,
      r.source_label,
      r.versi_template,
      r.delivery_number,
      r.customer_name,
      r.po_number,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return hay.includes(k)
  })
})

function sheetBlock(code) {
  return sheetsState.value[code] || { columnKeys: [], rows: [] }
}

function sheetRowCount(code) {
  return sheetBlock(code).rows?.length ?? 0
}

function inferKeysFromRows(dataRows) {
  const s = new Set()
  for (const r of dataRows || []) {
    if (r && typeof r === 'object') Object.keys(r).forEach((k) => s.add(k))
  }
  return s.size ? [...s].sort((a, b) => a.localeCompare(b)) : []
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

function sheetsFromApi(detail) {
  const meta = detail.meta_json || {}
  const sk = meta.sheet_column_keys || {}
  const out = {}
  for (const [code, dataRows] of Object.entries(detail.sheets || {})) {
    let keys = sk[code] && sk[code].length ? [...sk[code]] : inferKeysFromRows(dataRows)
    if (!keys.length) keys = ['COL1']
    out[code] = {
      columnKeys: keys,
      rows: normalizeRows(dataRows, keys),
    }
  }
  return out
}

function defaultInitialSheets(nomorAju) {
  const row = nomorAju
    ? { 'NOMOR AJU': String(nomorAju).trim(), 'KODE DOKUMEN': '' }
    : {}
  return {
    HEADER: {
      columnKeys: ['NOMOR AJU', 'KODE DOKUMEN'],
      rows: nomorAju ? [row] : [],
    },
  }
}

function resetCreateForm() {
  createForm.nomor_aju = ''
  createForm.kode_dokumen = ''
  createForm.source_label = ''
  createForm.versi_template = ''
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
    const created = await createCustomsDeclaration({
      nomor_aju: createForm.nomor_aju.trim(),
      kode_dokumen: emptyToNull(createForm.kode_dokumen),
      source_label: emptyToNull(createForm.source_label),
      versi_template: emptyToNull(createForm.versi_template),
    })
    ElMessage.success(t('pages.customs.saved'))
    createVisible.value = false
    await load()
    await openMaster(created.id)
  } catch (e) {
    const msg = e?.message || ''
    if (msg.includes('409')) {
      ElMessage.error(t('pages.customs.duplicateNomor'))
    } else {
      ElMessage.error(msg || t('common.errorGeneric'))
    }
  } finally {
    createSaving.value = false
  }
}

function onMasterClosed() {
  activeListId.value = null
  masterNomorAju.value = ''
  sheetsState.value = {}
  activeSheetTab.value = 'HEADER'
}

async function openMaster(id) {
  activeListId.value = id
  masterDrawer.value = true
  masterLoading.value = true
  try {
    const d = await getCustomsDeclaration(id)
    masterNomorAju.value = d.nomor_aju || ''
    headerForm.kode_dokumen = d.kode_dokumen || ''
    headerForm.source_label = d.source_label || ''
    headerForm.versi_template = d.versi_template || ''
    const hasSheets = d.sheets && Object.keys(d.sheets).length > 0
    sheetsState.value = hasSheets ? sheetsFromApi(d) : defaultInitialSheets(d.nomor_aju)
    activeSheetTab.value = tabCodes.value[0] || 'HEADER'
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    masterDrawer.value = false
  } finally {
    masterLoading.value = false
  }
}

function promptAddColumn(code) {
  ElMessageBox.prompt(t('pages.customs.columnNamePrompt'), t('pages.customs.addColumn'), {
    confirmButtonText: t('common.save'),
    cancelButtonText: t('common.cancel'),
    inputPattern: /\S/,
    inputErrorMessage: t('pages.customs.columnNamePrompt'),
  })
    .then(({ value }) => {
      const name = String(value).trim()
      if (!name) return
      const block = sheetsState.value[code]
      if (!block) return
      if (block.columnKeys.includes(name)) {
        ElMessage.error(t('pages.customs.duplicateColumn'))
        return
      }
      block.columnKeys.push(name)
      block.rows.forEach((r) => {
        r[name] = ''
      })
    })
    .catch(() => {})
}

function addSheetRow(code) {
  const block = sheetsState.value[code]
  if (!block) return
  if (!block.columnKeys.length) {
    ElMessage.warning(t('pages.customs.needColumnFirst'))
    return
  }
  const o = {}
  block.columnKeys.forEach((k) => {
    o[k] = ''
  })
  block.rows.push(o)
}

function removeSheetRow(code, index) {
  const block = sheetsState.value[code]
  if (!block) return
  block.rows.splice(index, 1)
}

function promptAddSheet() {
  const used = new Set(Object.keys(sheetsState.value))
  const options = SHEET_CODES_ORDER.filter((c) => !used.has(c))
  const hint =
    options.length > 0
      ? `${t('pages.customs.pickSheetCode')}: ${options.slice(0, 6).join(', ')}…`
      : t('pages.customs.pickSheetCode')
  ElMessageBox.prompt(hint, t('pages.customs.addSheet'), {
    confirmButtonText: t('common.save'),
    cancelButtonText: t('common.cancel'),
    inputPattern: /\S/,
    inputErrorMessage: t('pages.customs.pickSheetCode'),
  })
    .then(({ value }) => {
      const code = String(value).trim().toUpperCase()
      if (!code) return
      if (sheetsState.value[code]) {
        ElMessage.error(t('pages.customs.duplicateSheet'))
        return
      }
      sheetsState.value[code] = {
        columnKeys: ['COL1'],
        rows: [],
      }
      activeSheetTab.value = code
    })
    .catch(() => {})
}

function removeSheet(code) {
  ElMessageBox.confirm(t('pages.customs.confirmRemoveSheet'), t('common.confirm'), { type: 'warning' })
    .then(() => {
      const next = { ...sheetsState.value }
      delete next[code]
      sheetsState.value = next
      if (activeSheetTab.value === code) {
        activeSheetTab.value = tabCodes.value[0] || ''
      }
    })
    .catch(() => {})
}

function buildSheetsPayload() {
  const sheets = {}
  for (const [code, block] of Object.entries(sheetsState.value)) {
    const keys = [...block.columnKeys]
    const rowsPayload = block.rows.map((r) => {
      const o = {}
      keys.forEach((k) => {
        o[k] = r[k] ?? ''
      })
      return o
    })
    sheets[code] = {
      column_keys: keys,
      rows: rowsPayload,
    }
  }
  return sheets
}

async function saveMaster() {
  if (activeListId.value == null) return
  masterSaving.value = true
  try {
    await updateCustomsDeclaration(activeListId.value, {
      kode_dokumen: emptyToNull(headerForm.kode_dokumen),
      source_label: emptyToNull(headerForm.source_label),
      versi_template: emptyToNull(headerForm.versi_template),
    })
    await saveCustomsSheetsData(activeListId.value, { sheets: buildSheetsPayload() })
    ElMessage.success(t('pages.customs.sheetSaved'))
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
    rows.value = await listCustomsDeclarations()
  } finally {
    loading.value = false
  }
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(t('pages.customs.confirmDelete'), t('common.confirm'), {
      type: 'warning',
    })
    await deleteCustomsDeclaration(row.id)
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
.customs-toolbar-search {
  min-width: 220px;
  flex: 1 1 220px;
  max-width: 100%;
  margin-right: 8px;
  vertical-align: middle;
}
.customs-tabs :deep(.el-tabs__content) {
  padding-top: 8px;
}
.customs-dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding-right: 8px;
}
.customs-dialog-header__title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
}
.customs-hint-icon {
  color: #94a3b8;
  cursor: help;
  flex-shrink: 0;
  outline: none;
}
.customs-hint-icon:hover,
.customs-hint-icon:focus-visible {
  color: var(--el-color-primary);
}
</style>
