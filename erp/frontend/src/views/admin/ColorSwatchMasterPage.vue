<template>
  <AdminSection :title="t('pages.colorSwatch.title')" :subtitle="t('pages.colorSwatch.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        clearable
        :placeholder="t('pages.colorSwatch.searchPlaceholder')"
        class="color-swatch-toolbar-search"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canView" :icon="Download" @click="handleExport">{{ t('pages.colorSwatch.export') }}</el-button>
      <el-button v-if="canCreate" type="success" :icon="Upload" @click="openExcelImportDialog">{{ t('pages.colorSwatch.importExcel') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head color-swatch-inner-head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.colorSwatch.listSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.colorSwatch.listSubtitle') }}</p>
        </div>
        <el-tooltip placement="top-start" :show-after="200">
          <template #content>{{ t('pages.colorSwatch.pageHint') }}</template>
          <el-icon class="color-swatch-page-hint" :size="16" tabindex="0" :aria-label="t('pages.colorSwatch.pageHint')">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>

      <div class="admin-stats-grid admin-stats-grid--4 color-swatch-stats">
        <div class="admin-stat-card admin-stat-card--info">
          <span class="admin-stat-card__value">{{ total }}</span>
          <span class="admin-stat-card__label">{{ t('pages.colorSwatch.statShown') }}</span>
        </div>
        <div class="admin-stat-card">
          <span class="admin-stat-card__value">{{ listStats.factories }}</span>
          <span class="admin-stat-card__label">{{ t('pages.colorSwatch.statFactories') }}</span>
        </div>
        <div class="admin-stat-card admin-stat-card--success">
          <span class="admin-stat-card__value">{{ listStats.buyers }}</span>
          <span class="admin-stat-card__label">{{ t('pages.colorSwatch.statBuyers') }}</span>
        </div>
        <div class="admin-stat-card admin-stat-card--warn">
          <span class="admin-stat-card__value">{{ listStats.materials }}</span>
          <span class="admin-stat-card__label">{{ t('pages.colorSwatch.statMaterials') }}</span>
        </div>
      </div>

      <div class="filter-panel color-swatch-filter-panel">
        <p class="filter-panel__title">{{ t('common.filter') }}</p>
        <div class="color-swatch-filter-row">
          <el-input
            v-model="filterFactory"
            clearable
            :placeholder="t('pages.colorSwatch.filterFactory')"
            class="color-swatch-filter-factory"
          />
          <el-select
            v-model="filterBuyer"
            clearable
            filterable
            class="color-swatch-filter-buyer"
            :placeholder="t('common.buyer')"
          >
            <el-option v-for="b in formOptions.buyer_codes" :key="b" :label="b" :value="b" />
          </el-select>
        </div>
      </div>

      <p class="admin-scroll-hint">{{ t('pages.colorSwatch.scrollHint') }}</p>

      <div class="admin-table-scroll color-swatch-table-wrap">
        <el-table
          :data="rows"
          v-loading="loading"
          border
          stripe
          size="small"
          class="admin-table color-swatch-table"
          table-layout="fixed"
          max-height="52vh"
          :empty-text="t('pages.colorSwatch.tableEmpty')"
          @sort-change="onSortChange"
        >
          <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
          <el-table-column prop="factory_key" :label="t('pages.colorSwatch.colFactory')" width="120" show-overflow-tooltip />
          <el-table-column prop="customer_code" :label="t('pages.colorSwatch.colCustomerCode')" width="100" show-overflow-tooltip />
          <el-table-column prop="buyer_code" :label="t('common.buyer')" width="100" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.buyer_code" size="small" effect="plain" type="info">{{ row.buyer_code }}</el-tag>
              <span v-else class="color-swatch-cell-empty">—</span>
            </template>
          </el-table-column>
          <el-table-column prop="color_code" :label="t('pages.colorSwatch.colCode')" width="100" show-overflow-tooltip />
          <el-table-column :label="t('pages.colorSwatch.colCsi')" width="72" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.csi_color_master_id" size="small" type="success" effect="plain">CSI</el-tag>
              <span v-else class="color-swatch-cell-empty">—</span>
            </template>
          </el-table-column>
          <el-table-column prop="color_name" :label="t('common.color')" min-width="140" show-overflow-tooltip />
          <el-table-column prop="material_name" :label="t('common.material')" min-width="160" show-overflow-tooltip />
          <el-table-column prop="emboss" :label="t('pages.po.emboss')" width="100" show-overflow-tooltip />
          <el-table-column prop="color_standard" :label="t('pages.po.colorStandart')" width="120" show-overflow-tooltip />
          <el-table-column prop="backing" :label="t('common.backing')" width="90" show-overflow-tooltip />
          <el-table-column prop="legacy_urut" :label="t('pages.colorSwatch.colUrut')" width="80" align="center" />
          <el-table-column
            prop="entered_at"
            :label="t('pages.colorSwatch.colEnteredAt')"
            width="118"
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">{{ formatAuditDate(row.entered_at) }}</template>
          </el-table-column>
          <el-table-column
            prop="created_at"
            :label="t('pages.colorSwatch.colCreatedAt')"
            width="148"
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">{{ formatAuditDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column
            prop="updated_at"
            :label="t('pages.colorSwatch.colUpdatedAt')"
            width="148"
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">{{ formatAuditDateTime(row.updated_at) }}</template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="88" fixed="right" align="center">
            <template #default="{ row }">
              <AdminTableActions
                :show-edit="canUpdate"
                :show-delete="canDelete"
                @edit="openEdit(row)"
                @delete="remove(row)"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="color-swatch-pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          size="small"
          background
          layout="total, sizes, prev, pager, next"
          :total="total"
          :page-sizes="[25, 50, 100, 200]"
        />
      </div>
    </div>

    <el-dialog
      v-model="formVisible"
      width="720px"
      destroy-on-close
      align-center
      class="color-swatch-dialog"
      :show-close="true"
      @closed="resetForm"
    >
      <template #header>
        <div class="color-swatch-dialog-header">
          <div class="color-swatch-dialog-header__main">
            <h3 class="color-swatch-dialog-header__title">
              {{ editId ? t('pages.colorSwatch.editTitle') : t('pages.colorSwatch.createTitle') }}
            </h3>
            <p class="color-swatch-dialog-header__sub">{{ t('pages.colorSwatch.dialogFormSub') }}</p>
          </div>
        </div>
      </template>

      <div class="color-swatch-dialog-body color-swatch-dialog-body--stack">
        <div class="color-swatch-dialog-panel">
          <div class="color-swatch-dialog-panel__head">
            <h4 class="color-swatch-dialog-panel__title">{{ t('pages.colorSwatch.dialogGroupLocation') }}</h4>
          </div>
          <div class="color-swatch-dialog-panel__body">
            <el-form label-position="top" @submit.prevent>
              <el-row :gutter="16">
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('pages.colorSwatch.formCustomer')" required>
                    <el-select
                      v-model="form.customer_id"
                      filterable
                      clearable
                      class="w-full"
                      :placeholder="t('pages.colorSwatch.formCustomerPlaceholder')"
                      @change="onCustomerChange"
                    >
                      <el-option
                        v-for="c in formOptions.customers"
                        :key="c.id"
                        :label="customerOptionLabel(c)"
                        :value="c.id"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('pages.colorSwatch.colFactory')" required>
                    <el-select
                      v-model="form.factory_key"
                      filterable
                      allow-create
                      default-first-option
                      class="w-full"
                      :placeholder="t('pages.colorSwatch.formFactoryPlaceholder')"
                    >
                      <el-option v-for="fk in factoryKeyOptions" :key="fk" :label="fk" :value="fk" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('common.buyer')" required>
                    <el-select
                      v-model="form.buyer_code"
                      filterable
                      class="w-full"
                      :placeholder="t('common.buyer')"
                      @change="onBuyerChange"
                    >
                      <el-option v-for="b in formOptions.buyer_codes" :key="b" :label="b" :value="b" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('pages.colorSwatch.formCsi')">
                    <el-select
                      v-model="form.csi_color_master_id"
                      filterable
                      clearable
                      class="w-full"
                      :placeholder="t('pages.colorSwatch.formCsiPlaceholder')"
                      :disabled="!form.buyer_code"
                      @change="onCsiChange"
                    >
                      <el-option
                        v-for="c in csiOptions"
                        :key="c.id"
                        :label="c.label || `${c.color_code} — ${c.color_name}`"
                        :value="c.id"
                      />
                    </el-select>
                    <p v-if="csiOptions.length && !form.csi_color_master_id" class="color-swatch-csi-hint">
                      {{ t('pages.colorSwatch.formCsiRecommended') }}
                    </p>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </div>

        <div class="color-swatch-dialog-panel color-swatch-dialog-panel--sub">
          <div class="color-swatch-dialog-panel__head">
            <h4 class="color-swatch-dialog-panel__title">{{ t('pages.colorSwatch.dialogGroupRecipe') }}</h4>
          </div>
          <div class="color-swatch-dialog-panel__body">
            <el-form label-position="top" @submit.prevent>
              <el-row :gutter="16">
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('common.material')" required>
                    <el-select
                      v-model="form.material_name"
                      filterable
                      allow-create
                      default-first-option
                      class="w-full"
                      :placeholder="t('pages.colorSwatch.formMaterialPlaceholder')"
                      @change="onMaterialChange"
                    >
                      <el-option v-for="m in formOptions.materials" :key="m" :label="m" :value="m" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('pages.colorSwatch.colCode')">
                    <el-input
                      v-model="form.color_code"
                      maxlength="64"
                      clearable
                      :placeholder="t('pages.colorSwatch.formColorCodePlaceholder')"
                    />
                    <p v-if="form.csi_color_master_id" class="color-swatch-csi-hint">
                      {{ t('pages.colorSwatch.formColorCodeEditableHint') }}
                    </p>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('common.color')" required>
                    <el-select
                      v-model="form.color_name"
                      filterable
                      allow-create
                      default-first-option
                      class="w-full"
                      :placeholder="t('pages.colorSwatch.formColorPlaceholder')"
                    >
                      <el-option v-for="c in colorOptions" :key="c" :label="c" :value="c" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('pages.po.emboss')">
                    <el-select
                      v-model="form.emboss"
                      filterable
                      allow-create
                      default-first-option
                      clearable
                      class="w-full"
                      :placeholder="t('pages.colorSwatch.formEmbossPlaceholder')"
                    >
                      <el-option v-for="e in embossOptions" :key="e" :label="e" :value="e" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </div>

        <div class="color-swatch-dialog-panel color-swatch-dialog-panel--sub">
          <div class="color-swatch-dialog-panel__head">
            <h4 class="color-swatch-dialog-panel__title">{{ t('pages.colorSwatch.dialogGroupDetail') }}</h4>
          </div>
          <div class="color-swatch-dialog-panel__body">
            <el-form label-position="top" @submit.prevent>
              <el-row :gutter="16">
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('pages.po.colorStandart')">
                    <el-input
                      v-model="form.color_standard"
                      maxlength="255"
                      clearable
                      :placeholder="t('pages.colorSwatch.formColorStandardPlaceholder')"
                      @input="colorStandardManual = true"
                    />
                    <div class="mt-1 flex flex-wrap items-center gap-2">
                      <el-tag v-if="colorStandardAuto && form.color_standard" size="small" type="success">
                        {{ t('pages.po.autoFilled') }}
                      </el-tag>
                      <el-button
                        v-if="colorStandardManual && (form.customer_id || form.factory_key)"
                        link
                        type="primary"
                        size="small"
                        @click="refreshColorStandardSuggest({ force: true })"
                      >
                        {{ t('pages.colorSwatch.formColorStandardResetAuto') }}
                      </el-button>
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('common.backing')">
                    <el-select
                      v-model="form.backing"
                      filterable
                      allow-create
                      default-first-option
                      clearable
                      class="w-full"
                      :placeholder="t('pages.colorSwatch.formBackingPlaceholder')"
                    >
                      <el-option v-for="b in formOptions.backings" :key="b" :label="b" :value="b" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('pages.colorSwatch.colUrut')">
                    <el-input v-model="form.legacy_urut" maxlength="32" clearable />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="color-swatch-dialog-footer">
          <el-button :icon="Close" @click="formVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :icon="Check" :loading="saving" @click="save">{{ t('common.save') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="excelImportDialogVisible"
      :title="t('pages.colorSwatch.importExcelTitle')"
      width="640px"
      destroy-on-close
      align-center
    >
      <p class="cs-excel-sub">{{ t('pages.colorSwatch.importExcelSub') }}</p>
      <p class="cs-excel-hint">{{ t('pages.colorSwatch.importExcelHint') }}</p>
      <ul class="cs-excel-cols">
        <li>{{ t('pages.colorSwatch.importExcelColsRequired') }}</li>
        <li>{{ t('pages.colorSwatch.importExcelColsOptional') }}</li>
      </ul>
      <div class="cs-excel-actions">
        <el-button :icon="Download" @click="downloadImportTemplate">{{ t('pages.colorSwatch.downloadTemplate') }}</el-button>
      </div>
      <p class="cs-excel-panel-title">{{ t('pages.colorSwatch.importExcelPanelTitle') }}</p>
      <el-upload
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleExcelImportFile"
      >
        <el-button type="primary">{{ t('pages.colorSwatch.selectFile') }}</el-button>
      </el-upload>
      <div v-if="excelImportResult" class="cs-excel-result">
        <p>
          {{
            t('pages.colorSwatch.importResultSummary', {
              created: excelImportResult.created || 0,
              updated: excelImportResult.updated || 0,
              skipped: excelImportResult.skipped || 0,
            })
          }}
        </p>
        <ul v-if="excelImportResult.errors?.length" class="cs-excel-errors">
          <li v-for="(err, idx) in excelImportResult.errors.slice(0, 8)" :key="idx">
            {{ t('pages.colorSwatch.importErrorRow', { row: err.row, code: err.color_code || '—', reason: err.reason }) }}
          </li>
          <li v-if="excelImportResult.errors.length > 8">
            {{ t('pages.colorSwatch.importErrorMore', { n: excelImportResult.errors.length - 8 }) }}
          </li>
        </ul>
      </div>
      <template #footer>
        <el-button @click="excelImportDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :disabled="!excelImportFile || excelImporting" :loading="excelImporting" @click="handleExcelImport">
          {{ t('pages.colorSwatch.doImport') }}
        </el-button>
      </template>
    </el-dialog>

  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Close, Download, InfoFilled, Plus, Refresh, Upload } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import {
  createColorSwatchRecipe,
  deleteColorSwatchRecipe,
  exportColorSwatches,
  importColorSwatches,
  listColorSwatchFormOptions,
  listColorSwatchRecipesPage,
  suggestColorSwatchStandard,
  updateColorSwatchRecipe,
} from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canView, canCreate, canUpdate, canDelete } = useModulePermission('colorSwatch')

const loading = ref(false)
const saving = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)
const keyword = ref('')
const filterFactory = ref('')
const filterBuyer = ref('')
const sortBy = ref('')
const sortDir = ref('asc')
const formVisible = ref(false)
const excelImportDialogVisible = ref(false)
const excelImportFile = ref(null)
const excelImportResult = ref(null)
const excelImporting = ref(false)
const editId = ref(null)
/** User mengubah Color standard manual — jangan ditimpa autofill. */
const colorStandardManual = ref(false)
const colorStandardAuto = ref(false)
let colorStandardSuggestSeq = 0

const formOptions = reactive({
  customers: [],
  factory_keys: [],
  factory_keys_by_customer: {},
  buyer_codes: [],
  materials: [],
  colors_by_material: {},
  embosses_by_material: {},
  backings: [],
  csi_by_buyer: {},
})

const form = reactive({
  customer_id: null,
  factory_key: '',
  buyer_code: '',
  csi_color_master_id: null,
  color_code: '',
  color_name: '',
  material_name: '',
  emboss: '',
  color_standard: '',
  backing: '',
  legacy_urut: '',
})

const listStats = computed(() => ({
  factories: formOptions.factory_keys.length,
  buyers: formOptions.buyer_codes.length,
  materials: formOptions.materials.length,
}))

const factoryKeyOptions = computed(() => {
  const cid = form.customer_id
  if (cid && formOptions.factory_keys_by_customer[cid]?.length) {
    const keys = [...formOptions.factory_keys_by_customer[cid]]
    if (form.factory_key && !keys.includes(form.factory_key)) keys.unshift(form.factory_key)
    return keys
  }
  return formOptions.factory_keys
})

const csiOptions = computed(() => {
  const buyer = String(form.buyer_code || '').trim().toUpperCase()
  return formOptions.csi_by_buyer[buyer] || []
})

const colorOptions = computed(() => {
  const mat = String(form.material_name || '').trim()
  if (!mat) return []
  return formOptions.colors_by_material[mat] || []
})

const embossOptions = computed(() => {
  const mat = String(form.material_name || '').trim()
  if (!mat) return []
  return formOptions.embosses_by_material[mat] || []
})

function customerOptionLabel(c) {
  const code = String(c.code || '').trim()
  const name = String(c.name || '').trim()
  if (code && name) return `${code} — ${name}`
  return code || name || `#${c.id}`
}

function onCustomerChange() {
  // Pabrik bebas diedit; hanya isi default jika masih kosong & customer punya 1 opsi.
  const keys = form.customer_id ? formOptions.factory_keys_by_customer[form.customer_id] : null
  if (!form.factory_key.trim() && keys?.length === 1) {
    form.factory_key = keys[0]
  }
  void refreshColorStandardSuggest()
}

function onMaterialChange() {
  // keep custom values via allow-create
}

function onBuyerChange() {
  const ids = new Set(csiOptions.value.map((c) => c.id))
  if (form.csi_color_master_id && !ids.has(form.csi_color_master_id)) {
    form.csi_color_master_id = null
  }
}

function onCsiChange(id) {
  if (!id) return
  const hit = csiOptions.value.find((c) => c.id === id)
  if (!hit) return
  // Prefill dari CSI hanya jika field masih kosong — tetap bisa diedit manual.
  if (!String(form.color_code || '').trim()) form.color_code = hit.color_code || ''
  if (!String(form.color_name || '').trim()) form.color_name = hit.color_name || ''
}

async function refreshColorStandardSuggest({ force = false } = {}) {
  if (editId.value && !force) return
  if (colorStandardManual.value && !force) return
  if (!form.customer_id && !String(form.factory_key || '').trim()) return
  const seq = ++colorStandardSuggestSeq
  try {
    const r = await suggestColorSwatchStandard({
      customerId: form.customer_id || undefined,
      factoryKey: form.factory_key.trim() || undefined,
    })
    if (seq !== colorStandardSuggestSeq) return
    const next = String(r?.color_standard || '').trim()
    if (!next) return
    form.color_standard = next
    colorStandardAuto.value = true
    colorStandardManual.value = false
  } catch {
    // biarkan user isi manual jika suggest gagal
  }
}

async function loadFormOptions() {
  try {
    const r = await listColorSwatchFormOptions()
    formOptions.customers = r.customers || []
    formOptions.factory_keys = r.factory_keys || []
    const byCustomer = {}
    for (const [k, v] of Object.entries(r.factory_keys_by_customer || {})) {
      byCustomer[Number(k)] = v
    }
    formOptions.factory_keys_by_customer = byCustomer
    formOptions.buyer_codes = r.buyer_codes || []
    formOptions.materials = r.materials || []
    formOptions.colors_by_material = r.colors_by_material || {}
    formOptions.embosses_by_material = r.embosses_by_material || {}
    formOptions.backings = r.backings || []
    formOptions.csi_by_buyer = r.csi_by_buyer || {}
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function load() {
  loading.value = true
  try {
    const r = await listColorSwatchRecipesPage({
      factory_key: filterFactory.value || undefined,
      buyer_code: filterBuyer.value || undefined,
      q: keyword.value || undefined,
      sort_by: sortBy.value || undefined,
      sort_dir: sortBy.value ? sortDir.value : undefined,
      limit: pageSize.value,
      offset: (page.value - 1) * pageSize.value,
    })
    rows.value = r.items || []
    total.value = Number(r.total || 0)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function formatAuditDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value).slice(0, 10) || '—'
  return d.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' })
}

function formatAuditDateTime(value) {
  if (!value) return '—'
  const s = String(value).replace('T', ' ')
  return s.length > 19 ? s.slice(0, 19) : s
}

function onSortChange({ prop, order }) {
  if (!order || !prop) {
    sortBy.value = ''
    sortDir.value = 'asc'
  } else {
    sortBy.value = prop
    sortDir.value = order === 'descending' ? 'desc' : 'asc'
  }
  if (page.value !== 1) page.value = 1
  else load()
}

function reload() {
  page.value = 1
  load()
}

function resetForm() {
  editId.value = null
  form.customer_id = null
  form.factory_key = ''
  form.buyer_code = ''
  form.csi_color_master_id = null
  form.color_code = ''
  form.color_name = ''
  form.material_name = ''
  form.emboss = ''
  form.color_standard = ''
  form.backing = ''
  form.legacy_urut = ''
  colorStandardManual.value = false
  colorStandardAuto.value = false
}

function openExcelImportDialog() {
  excelImportDialogVisible.value = true
  excelImportFile.value = null
  excelImportResult.value = null
}

function handleExcelImportFile(file) {
  excelImportFile.value = file.raw
  excelImportResult.value = null
}

async function handleExport() {
  try {
    await exportColorSwatches()
    ElMessage.success(t('pages.colorSwatch.exportSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadImportTemplate() {
  try {
    await exportColorSwatches({ template: true })
    ElMessage.success(t('pages.colorSwatch.templateSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function handleExcelImport() {
  if (!excelImportFile.value) return
  excelImporting.value = true
  excelImportResult.value = null
  try {
    const result = await importColorSwatches(excelImportFile.value)
    excelImportResult.value = result
    ElMessage.success(
      t('pages.colorSwatch.importResultSummary', {
        created: result.created || 0,
        updated: result.updated || 0,
        skipped: result.skipped || 0,
      }),
    )
    await Promise.all([load(), loadFormOptions()])
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    excelImporting.value = false
  }
}

function openCreate() {
  resetForm()
  formVisible.value = true
}

function openEdit(row) {
  editId.value = row.id
  form.customer_id = row.customer_id || null
  form.factory_key = row.factory_key || ''
  form.buyer_code = row.buyer_code || ''
  form.csi_color_master_id = row.csi_color_master_id || null
  form.color_code = row.color_code || ''
  form.color_name = row.color_name || ''
  form.material_name = row.material_name || ''
  form.emboss = row.emboss || ''
  form.color_standard = row.color_standard || ''
  form.backing = row.backing || ''
  form.legacy_urut = row.legacy_urut || ''
  colorStandardManual.value = true
  colorStandardAuto.value = false
  formVisible.value = true
}

async function save() {
  if (
    !form.customer_id
    || !form.factory_key.trim()
    || !form.buyer_code.trim()
    || !form.color_name.trim()
    || !form.material_name.trim()
  ) {
    ElMessage.warning(t('pages.colorSwatch.requiredFields'))
    return
  }
  saving.value = true
  try {
    const body = {
      customer_id: form.customer_id,
      factory_key: form.factory_key.trim(),
      buyer_code: form.buyer_code.trim(),
      csi_color_master_id: form.csi_color_master_id || null,
      color_code: form.color_code.trim(),
      color_name: form.color_name.trim(),
      material_name: form.material_name.trim(),
      emboss: form.emboss.trim(),
      color_standard: form.color_standard.trim() || null,
      backing: form.backing.trim() || null,
      legacy_urut: form.legacy_urut.trim() || null,
    }
    if (editId.value) {
      await updateColorSwatchRecipe(editId.value, body)
    } else {
      await createColorSwatchRecipe(body)
    }
    ElMessage.success(t('common.saveSuccess'))
    formVisible.value = false
    await Promise.all([load(), loadFormOptions()])
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(t('pages.colorSwatch.deleteConfirm'), t('common.confirm'), { type: 'warning' })
    await deleteColorSwatchRecipe(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

watch(
  () => form.factory_key,
  () => {
    if (!formVisible.value || editId.value) return
    void refreshColorStandardSuggest()
  },
)

watch([page, pageSize], () => load())
watch([filterFactory, filterBuyer, keyword], () => {
  page.value = 1
  load()
})

onMounted(() => {
  loadFormOptions()
  load()
})
</script>

<style scoped>
.color-swatch-csi-hint {
  margin: 6px 0 0;
  font-size: 12px;
  line-height: 1.4;
  color: #b45309;
}
.color-swatch-inner-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.color-swatch-page-hint {
  color: #94a3b8;
  cursor: help;
  flex-shrink: 0;
  outline: none;
}

.color-swatch-page-hint:hover,
.color-swatch-page-hint:focus-visible {
  color: var(--el-color-primary);
}

.color-swatch-stats {
  border-bottom: 1px solid #e2e8f0;
}

.color-swatch-filter-panel {
  margin: 0 16px;
}

.color-swatch-filter-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.color-swatch-filter-factory,
.color-swatch-filter-buyer {
  min-width: 0;
  flex: 1 1 180px;
  max-width: 280px;
}

.color-swatch-table-wrap {
  padding: 0 16px;
}

.color-swatch-pagination {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px 16px;
  border-top: 1px solid #e2e8f0;
}

.color-swatch-cell-empty {
  color: #94a3b8;
  font-size: 13px;
}

:deep(.color-swatch-dialog.el-dialog) {
  border-radius: 14px;
  overflow: hidden;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
}

:deep(.color-swatch-dialog .el-dialog__header) {
  padding: 16px 20px 12px;
  margin: 0;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.color-swatch-dialog .el-dialog__body) {
  padding: 0;
  background: #f8fafc;
  overflow-y: auto;
}

:deep(.color-swatch-dialog .el-dialog__footer) {
  padding: 12px 20px 16px;
  border-top: 1px solid #e2e8f0;
}

.color-swatch-dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding-right: 28px;
}

.color-swatch-dialog-header__title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.3;
}

.color-swatch-dialog-header__sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.45;
}

.color-swatch-dialog-body {
  padding: 16px;
}

.color-swatch-dialog-body--stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.color-swatch-dialog-panel {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  overflow: hidden;
}

.color-swatch-dialog-panel--sub {
  background: #f8fafc;
}

.color-swatch-dialog-panel__head {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.color-swatch-dialog-panel__title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #0f172a;
}

.color-swatch-dialog-panel__body {
  padding: 16px;
}

.color-swatch-dialog-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  width: 100%;
}

.cs-excel-sub {
  margin: 0 0 6px;
  font-size: 14px;
}

.cs-excel-hint,
.cs-excel-cols {
  margin: 0 0 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.45;
}

.cs-excel-cols {
  padding-left: 18px;
}

.cs-excel-actions {
  margin-bottom: 12px;
}

.cs-excel-panel-title {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 600;
}

.cs-excel-result {
  margin-top: 14px;
  padding: 10px 12px;
  border-radius: 6px;
  background: var(--el-fill-color-light);
  font-size: 13px;
}

.cs-excel-errors {
  margin: 8px 0 0;
  padding-left: 18px;
  font-size: 12px;
  color: var(--el-color-danger);
}
</style>
