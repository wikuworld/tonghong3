<template>
  <AdminSection :title="t('pages.fluorescentColors.title')" :subtitle="t('pages.fluorescentColors.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        clearable
        :placeholder="t('pages.fluorescentColors.searchPlaceholder')"
        class="fluorescent-toolbar-search"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canView" :icon="Download" @click="handleExport">{{ t('pages.fluorescentColors.export') }}</el-button>
      <el-button v-if="canCreate" type="success" :icon="Upload" @click="openImportDialog">{{ t('pages.fluorescentColors.importExcel') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head fluorescent-inner-head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.fluorescentColors.listSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.fluorescentColors.listSubtitle') }}</p>
        </div>
        <el-tooltip placement="top-start" :show-after="200">
          <template #content>{{ t('pages.fluorescentColors.pageHint') }}</template>
          <el-icon class="fluorescent-page-hint" :size="16" tabindex="0" :aria-label="t('pages.fluorescentColors.pageHint')">
            <InfoFilled />
          </el-icon>
        </el-tooltip>
      </div>

      <div class="admin-stats-grid admin-stats-grid--5 fluorescent-stats">
        <div class="admin-stat-card admin-stat-card--info">
          <span class="admin-stat-card__value">{{ total }}</span>
          <span class="admin-stat-card__label">{{ t('pages.fluorescentColors.statShown') }}</span>
        </div>
        <div class="admin-stat-card">
          <span class="admin-stat-card__value">{{ summary.GLOBAL }}</span>
          <span class="admin-stat-card__label">GLOBAL</span>
        </div>
        <div class="admin-stat-card admin-stat-card--success">
          <span class="admin-stat-card__value">{{ summary.NB }}</span>
          <span class="admin-stat-card__label">NB</span>
        </div>
        <div class="admin-stat-card admin-stat-card--warn">
          <span class="admin-stat-card__value">{{ summary.ADIDAS }}</span>
          <span class="admin-stat-card__label">ADIDAS</span>
        </div>
        <div class="admin-stat-card admin-stat-card--info">
          <span class="admin-stat-card__value">{{ summary.UA }}</span>
          <span class="admin-stat-card__label">UA</span>
        </div>
      </div>

      <div class="filter-panel fluorescent-filter-panel">
        <p class="filter-panel__title">{{ t('common.filter') }}</p>
        <div class="fluorescent-filter-row">
          <el-select
            v-model="filterBuyer"
            clearable
            filterable
            class="fluorescent-filter-buyer"
            :placeholder="t('common.buyer')"
          >
            <el-option v-for="b in formOptions.buyer_codes" :key="b" :label="b" :value="b" />
          </el-select>
          <el-select
            v-model="filterClass"
            clearable
            class="fluorescent-filter-class"
            :placeholder="t('pages.fluorescentColors.colClass')"
          >
            <el-option v-for="c in formOptions.color_classes" :key="c" :label="c" :value="c" />
          </el-select>
        </div>
      </div>

      <p class="admin-scroll-hint">{{ t('pages.fluorescentColors.scrollHint') }}</p>

      <div class="admin-table-scroll fluorescent-table-wrap">
        <el-table
          :data="rows"
          v-loading="loading"
          border
          stripe
          size="small"
          class="admin-table fluorescent-table"
          table-layout="fixed"
          max-height="52vh"
          :empty-text="t('pages.fluorescentColors.tableEmpty')"
          @sort-change="onSortChange"
        >
          <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
          <el-table-column prop="buyer_code" :label="t('common.buyer')" width="100" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="plain" type="info">{{ row.buyer_code || '—' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="season_label" :label="t('pages.fluorescentColors.colSeason')" min-width="130" show-overflow-tooltip />
          <el-table-column prop="season_year" :label="t('pages.fluorescentColors.colYear')" width="72" align="center" />
          <el-table-column prop="season_type" :label="t('pages.fluorescentColors.colSeasonType')" width="72" align="center" />
          <el-table-column prop="color_code" :label="t('pages.fluorescentColors.colCode')" width="120" show-overflow-tooltip />
          <el-table-column prop="color_name" :label="t('common.color')" min-width="180" show-overflow-tooltip />
          <el-table-column prop="color_class" :label="t('pages.fluorescentColors.colClass')" width="110" align="center">
            <template #default="{ row }">
              <el-tag size="small" effect="plain" :type="classTagType(row.color_class)">
                {{ row.color_class || '—' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="source_file" :label="t('pages.fluorescentColors.colSource')" min-width="120" show-overflow-tooltip />
          <el-table-column
            prop="created_at"
            :label="t('pages.fluorescentColors.colCreatedAt')"
            width="148"
            align="center"
            sortable="custom"
          >
            <template #default="{ row }">{{ formatAuditDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column
            prop="updated_at"
            :label="t('pages.fluorescentColors.colUpdatedAt')"
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

      <div class="fluorescent-pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          size="small"
          background
          layout="total, sizes, prev, pager, next"
          :total="total"
          :page-sizes="[20, 50, 100, 200]"
        />
      </div>
    </div>

    <el-dialog
      v-model="formVisible"
      width="680px"
      destroy-on-close
      align-center
      class="fluorescent-dialog"
      :show-close="true"
      @closed="resetForm"
    >
      <template #header>
        <div class="fluorescent-dialog-header">
          <div class="fluorescent-dialog-header__main">
            <h3 class="fluorescent-dialog-header__title">
              {{ editId ? t('pages.fluorescentColors.editTitle') : t('pages.fluorescentColors.createTitle') }}
            </h3>
            <p class="fluorescent-dialog-header__sub">{{ t('pages.fluorescentColors.dialogFormSub') }}</p>
          </div>
        </div>
      </template>

      <div class="fluorescent-dialog-body fluorescent-dialog-body--stack">
        <div class="fluorescent-dialog-panel">
          <div class="fluorescent-dialog-panel__head">
            <h4 class="fluorescent-dialog-panel__title">{{ t('pages.fluorescentColors.dialogGroupBuyer') }}</h4>
          </div>
          <div class="fluorescent-dialog-panel__body">
            <el-form label-position="top" @submit.prevent>
              <el-row :gutter="16">
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('common.buyer')" required>
                    <el-select
                      v-model="form.buyer_code"
                      filterable
                      class="w-full"
                      :placeholder="t('pages.fluorescentColors.formBuyerPlaceholder')"
                      @change="onBuyerChange"
                    >
                      <el-option v-for="b in formOptions.buyer_codes" :key="b" :label="b" :value="b" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('pages.fluorescentColors.colClass')" required>
                    <el-select v-model="form.color_class" class="w-full">
                      <el-option v-for="c in formOptions.color_classes" :key="c" :label="c" :value="c" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </div>

        <div class="fluorescent-dialog-panel fluorescent-dialog-panel--sub">
          <div class="fluorescent-dialog-panel__head">
            <h4 class="fluorescent-dialog-panel__title">{{ t('pages.fluorescentColors.dialogGroupSeason') }}</h4>
          </div>
          <div class="fluorescent-dialog-panel__body">
            <el-form label-position="top" @submit.prevent>
              <el-row :gutter="16">
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('pages.fluorescentColors.colSeason')">
                    <el-select
                      v-model="form.season_label"
                      filterable
                      allow-create
                      default-first-option
                      clearable
                      class="w-full"
                      :placeholder="t('pages.fluorescentColors.formSeasonPlaceholder')"
                      @change="onSeasonChange"
                    >
                      <el-option v-for="s in seasonLabelOptions" :key="s" :label="s" :value="s" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="12" :md="6">
                  <el-form-item :label="t('pages.fluorescentColors.colYear')">
                    <el-select
                      v-model="form.season_year"
                      filterable
                      allow-create
                      default-first-option
                      clearable
                      class="w-full"
                      :placeholder="t('pages.fluorescentColors.formYearPlaceholder')"
                    >
                      <el-option v-for="y in formOptions.season_years" :key="y" :label="String(y)" :value="y" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="12" :md="6">
                  <el-form-item :label="t('pages.fluorescentColors.colSeasonType')">
                    <el-select
                      v-model="form.season_type"
                      filterable
                      allow-create
                      default-first-option
                      clearable
                      class="w-full"
                      :placeholder="t('pages.fluorescentColors.formSeasonTypePlaceholder')"
                    >
                      <el-option v-for="st in seasonTypeOptions" :key="st" :label="st" :value="st" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </div>

        <div class="fluorescent-dialog-panel fluorescent-dialog-panel--sub">
          <div class="fluorescent-dialog-panel__head">
            <h4 class="fluorescent-dialog-panel__title">{{ t('pages.fluorescentColors.dialogGroupColor') }}</h4>
          </div>
          <div class="fluorescent-dialog-panel__body">
            <el-form label-position="top" @submit.prevent>
              <el-row :gutter="16">
                <el-col :xs="24" :md="12">
                  <el-form-item :label="t('pages.fluorescentColors.colCode')">
                    <el-select
                      v-model="form.color_code"
                      filterable
                      allow-create
                      default-first-option
                      clearable
                      class="w-full"
                      :placeholder="t('pages.fluorescentColors.formCodePlaceholder')"
                    >
                      <el-option v-for="c in colorCodeOptions" :key="c" :label="c" :value="c" />
                    </el-select>
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
                      :placeholder="t('pages.fluorescentColors.formColorPlaceholder')"
                    >
                      <el-option v-for="c in colorNameOptions" :key="c" :label="c" :value="c" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="fluorescent-dialog-footer">
          <el-button :icon="Close" @click="formVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :icon="Check" :loading="saving" @click="save">{{ t('common.save') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialogVisible" :title="t('pages.fluorescentColors.importExcelTitle')" width="640px" destroy-on-close align-center>
      <p class="fl-excel-sub">{{ t('pages.fluorescentColors.importExcelSub') }}</p>
      <p class="fl-excel-hint">{{ t('pages.fluorescentColors.importExcelHint') }}</p>
      <ul class="fl-excel-cols">
        <li>{{ t('pages.fluorescentColors.importExcelColsRequired') }}</li>
        <li>{{ t('pages.fluorescentColors.importExcelColsOptional') }}</li>
      </ul>
      <div class="fl-excel-actions">
        <el-button :icon="Download" @click="downloadImportTemplate">{{ t('pages.fluorescentColors.downloadTemplate') }}</el-button>
      </div>
      <p class="fl-excel-panel-title">{{ t('pages.fluorescentColors.importExcelPanelTitle') }}</p>
      <el-upload
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleImportFile"
      >
        <el-button type="primary">{{ t('pages.fluorescentColors.selectFile') }}</el-button>
      </el-upload>
      <div v-if="importResult" class="fl-excel-result">
        <p>
          {{
            t('pages.fluorescentColors.importResultSummary', {
              created: importResult.created || 0,
              updated: importResult.updated || 0,
              skipped: importResult.skipped || 0,
            })
          }}
        </p>
        <ul v-if="importResult.errors?.length" class="fl-excel-errors">
          <li v-for="(err, idx) in importResult.errors.slice(0, 8)" :key="idx">
            {{ t('pages.fluorescentColors.importErrorRow', { row: err.row, code: err.color_code || '—', reason: err.reason }) }}
          </li>
          <li v-if="importResult.errors.length > 8">
            {{ t('pages.fluorescentColors.importErrorMore', { n: importResult.errors.length - 8 }) }}
          </li>
        </ul>
      </div>
      <template #footer>
        <el-button @click="importDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :disabled="!importFile || importing" :loading="importing" @click="handleImport">
          {{ t('pages.fluorescentColors.doImport') }}
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
  createFluorescentColor,
  deleteFluorescentColor,
  exportFluorescentColors,
  importFluorescentColors,
  listFluorescentColorsPage,
  listFluorescentFormOptions,
  updateFluorescentColor,
} from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canView, canCreate, canUpdate, canDelete } = useModulePermission('fluorescentColors')

const loading = ref(false)
const saving = ref(false)
const importing = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)
const keyword = ref('')
const filterBuyer = ref('')
const filterClass = ref('')
const sortBy = ref('')
const sortDir = ref('asc')
const formVisible = ref(false)
const importDialogVisible = ref(false)
const importFile = ref(null)
const importResult = ref(null)
const editId = ref(null)

const formOptions = reactive({
  buyer_codes: [],
  color_classes: ['fluorescent', 'metallic'],
  season_labels: [],
  season_labels_by_buyer: {},
  season_years: [],
  season_types: [],
  color_names_by_buyer: {},
  color_codes_by_buyer: {},
  color_names_by_buyer_season: {},
})

const form = reactive({
  buyer_code: '',
  season_label: '',
  season_year: null,
  season_type: '',
  color_code: '',
  color_name: '',
  color_class: 'fluorescent',
})

const summary = ref({ GLOBAL: 0, NB: 0, ADIDAS: 0, UA: 0 })

const seasonLabelOptions = computed(() => {
  const buyer = String(form.buyer_code || '').trim().toUpperCase()
  if (buyer && formOptions.season_labels_by_buyer[buyer]?.length) {
    const list = [...formOptions.season_labels_by_buyer[buyer]]
    if (form.season_label && !list.includes(form.season_label)) list.unshift(form.season_label)
    return list
  }
  return formOptions.season_labels
})

const seasonTypeOptions = computed(() => {
  const defaults = ['SS', 'FW']
  const merged = new Set([...defaults, ...formOptions.season_types])
  return [...merged]
})

const colorNameOptions = computed(() => {
  const buyer = String(form.buyer_code || '').trim().toUpperCase()
  const season = String(form.season_label || '').trim()
  const bySeason = formOptions.color_names_by_buyer_season[buyer]
  if (bySeason && season && bySeason[season]?.length) {
    const list = [...bySeason[season]]
    if (form.color_name && !list.includes(form.color_name)) list.unshift(form.color_name)
    return list
  }
  const byBuyer = formOptions.color_names_by_buyer[buyer] || []
  if (form.color_name && !byBuyer.includes(form.color_name)) return [form.color_name, ...byBuyer]
  return byBuyer
})

const colorCodeOptions = computed(() => {
  const buyer = String(form.buyer_code || '').trim().toUpperCase()
  const list = [...(formOptions.color_codes_by_buyer[buyer] || [])]
  if (form.color_code && !list.includes(form.color_code)) list.unshift(form.color_code)
  return list
})

function classTagType(colorClass) {
  return String(colorClass || '').toLowerCase() === 'metallic' ? 'warning' : 'primary'
}

async function loadFormOptions() {
  try {
    const r = await listFluorescentFormOptions()
    formOptions.buyer_codes = r.buyer_codes || []
    formOptions.color_classes = r.color_classes || ['fluorescent', 'metallic']
    formOptions.season_labels = r.season_labels || []
    formOptions.season_labels_by_buyer = r.season_labels_by_buyer || {}
    formOptions.season_years = r.season_years || []
    formOptions.season_types = r.season_types || []
    formOptions.color_names_by_buyer = r.color_names_by_buyer || {}
    formOptions.color_codes_by_buyer = r.color_codes_by_buyer || {}
    formOptions.color_names_by_buyer_season = r.color_names_by_buyer_season || {}
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function onBuyerChange() {
  const seasons = form.buyer_code ? formOptions.season_labels_by_buyer[form.buyer_code] : null
  if (form.season_label && seasons?.length && !seasons.includes(form.season_label)) {
    form.season_label = ''
  }
}

function onSeasonChange() {
  // color options refresh via computed
}

async function loadSummary() {
  try {
    const [g, nb, adidas, ua] = await Promise.all([
      listFluorescentColorsPage({ buyer_code: 'GLOBAL', limit: 1, offset: 0 }),
      listFluorescentColorsPage({ buyer_code: 'NB', limit: 1, offset: 0 }),
      listFluorescentColorsPage({ buyer_code: 'ADIDAS', limit: 1, offset: 0 }),
      listFluorescentColorsPage({ buyer_code: 'UA', limit: 1, offset: 0 }),
    ])
    summary.value = {
      GLOBAL: Number(g?.total || 0),
      NB: Number(nb?.total || 0),
      ADIDAS: Number(adidas?.total || 0),
      UA: Number(ua?.total || 0),
    }
  } catch {
    summary.value = { GLOBAL: 0, NB: 0, ADIDAS: 0, UA: 0 }
  }
}

async function load() {
  loading.value = true
  try {
    const r = await listFluorescentColorsPage({
      buyer_code: filterBuyer.value || undefined,
      color_class: filterClass.value || undefined,
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
  loadSummary()
}

function resetForm() {
  editId.value = null
  form.buyer_code = ''
  form.season_label = ''
  form.season_year = null
  form.season_type = ''
  form.color_code = ''
  form.color_name = ''
  form.color_class = 'fluorescent'
}

function openImportDialog() {
  importDialogVisible.value = true
  importFile.value = null
  importResult.value = null
}

function handleImportFile(file) {
  importFile.value = file.raw
  importResult.value = null
}

async function handleExport() {
  try {
    await exportFluorescentColors()
    ElMessage.success(t('pages.fluorescentColors.exportSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadImportTemplate() {
  try {
    await exportFluorescentColors({ template: true })
    ElMessage.success(t('pages.fluorescentColors.templateSuccess'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function handleImport() {
  if (!importFile.value) return
  importing.value = true
  importResult.value = null
  try {
    const result = await importFluorescentColors(importFile.value)
    importResult.value = result
    ElMessage.success(
      t('pages.fluorescentColors.importResultSummary', {
        created: result.created || 0,
        updated: result.updated || 0,
        skipped: result.skipped || 0,
      }),
    )
    await Promise.all([load(), loadSummary(), loadFormOptions()])
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    importing.value = false
  }
}

function openCreate() {
  resetForm()
  formVisible.value = true
}

function openEdit(row) {
  editId.value = row.id
  form.buyer_code = row.buyer_code || ''
  form.season_label = row.season_label || ''
  form.season_year = row.season_year ?? null
  form.season_type = row.season_type || ''
  form.color_code = row.color_code || ''
  form.color_name = row.color_name || ''
  form.color_class = row.color_class || 'fluorescent'
  formVisible.value = true
}

function buildBody() {
  const seasonYear = form.season_year
  const parsedYear = seasonYear === '' || seasonYear == null ? null : Number(seasonYear)
  return {
    buyer_code: form.buyer_code.trim(),
    season_label: form.season_label.trim() || null,
    season_year: Number.isFinite(parsedYear) ? parsedYear : null,
    season_type: form.season_type.trim() || null,
    color_code: form.color_code.trim() || null,
    color_name: form.color_name.trim(),
    color_class: form.color_class,
  }
}

async function save() {
  if (!form.buyer_code.trim() || !form.color_name.trim()) {
    ElMessage.warning(t('pages.fluorescentColors.requiredFields'))
    return
  }
  saving.value = true
  try {
    const body = buildBody()
    if (editId.value) {
      await updateFluorescentColor(editId.value, body)
    } else {
      await createFluorescentColor(body)
    }
    ElMessage.success(t('common.saveSuccess'))
    formVisible.value = false
    await Promise.all([load(), loadSummary(), loadFormOptions()])
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

async function remove(row) {
  try {
    await ElMessageBox.confirm(t('pages.fluorescentColors.deleteConfirm'), t('common.confirm'), { type: 'warning' })
    await deleteFluorescentColor(row.id)
    ElMessage.success(t('common.deleteSuccess'))
    await load()
    await loadSummary()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

watch([page, pageSize], () => load())
watch([filterBuyer, filterClass, keyword], () => {
  page.value = 1
  load()
})

onMounted(() => {
  loadFormOptions()
  load()
  loadSummary()
})
</script>

<style scoped>
.fluorescent-inner-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.fluorescent-page-hint {
  color: #94a3b8;
  cursor: help;
  flex-shrink: 0;
  outline: none;
}

.fluorescent-page-hint:hover,
.fluorescent-page-hint:focus-visible {
  color: var(--el-color-primary);
}

.fluorescent-stats {
  border-bottom: 1px solid #e2e8f0;
}

.fluorescent-filter-panel {
  margin: 0 16px;
}

.fluorescent-filter-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.fluorescent-filter-buyer,
.fluorescent-filter-class {
  min-width: 0;
  flex: 1 1 180px;
  max-width: 280px;
}

.fluorescent-table-wrap {
  padding: 0 16px;
}

.fluorescent-pagination {
  display: flex;
  justify-content: flex-end;
  padding: 12px 16px 16px;
  border-top: 1px solid #e2e8f0;
}

:deep(.fluorescent-dialog.el-dialog) {
  border-radius: 14px;
  overflow: hidden;
  max-height: 92vh;
  display: flex;
  flex-direction: column;
}

:deep(.fluorescent-dialog .el-dialog__header) {
  padding: 16px 20px 12px;
  margin: 0;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.fluorescent-dialog .el-dialog__body) {
  padding: 0;
  background: #f8fafc;
  overflow-y: auto;
}

:deep(.fluorescent-dialog .el-dialog__footer) {
  padding: 12px 20px 16px;
  border-top: 1px solid #e2e8f0;
}

.fluorescent-dialog-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding-right: 28px;
}

.fluorescent-dialog-header__title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.3;
}

.fluorescent-dialog-header__sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.45;
}

.fluorescent-dialog-body {
  padding: 16px;
}

.fluorescent-dialog-body--stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.fluorescent-dialog-panel {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  overflow: hidden;
}

.fluorescent-dialog-panel--sub {
  background: #f8fafc;
}

.fluorescent-dialog-panel__head {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.fluorescent-dialog-panel__title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 600;
  color: #0f172a;
}

.fluorescent-dialog-panel__body {
  padding: 16px;
}

.fluorescent-dialog-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  width: 100%;
}

.fl-excel-sub {
  margin: 0 0 6px;
  font-size: 14px;
}

.fl-excel-hint,
.fl-excel-cols {
  margin: 0 0 8px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  line-height: 1.45;
}

.fl-excel-cols {
  padding-left: 18px;
}

.fl-excel-actions {
  margin-bottom: 12px;
}

.fl-excel-panel-title {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 600;
}

.fl-excel-result {
  margin-top: 14px;
  padding: 10px 12px;
  border-radius: 6px;
  background: var(--el-fill-color-light);
  font-size: 13px;
}

.fl-excel-errors {
  margin: 8px 0 0;
  padding-left: 18px;
  font-size: 12px;
  color: var(--el-color-danger);
}
</style>
