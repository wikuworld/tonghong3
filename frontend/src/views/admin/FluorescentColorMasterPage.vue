<template>
  <AdminSection :title="t('pages.fluorescentColors.title')" :subtitle="t('pages.fluorescentColors.subtitle')">
    <template #actions>
      <el-select v-model="filterBuyer" clearable filterable :placeholder="t('common.buyer')" class="w-40">
        <el-option v-for="b in formOptions.buyer_codes" :key="b" :label="b" :value="b" />
      </el-select>
      <el-select v-model="filterClass" clearable :placeholder="t('pages.fluorescentColors.colClass')" class="w-36">
        <el-option v-for="c in formOptions.color_classes" :key="c" :label="c" :value="c" />
      </el-select>
      <el-input v-model="keyword" clearable :placeholder="t('pages.fluorescentColors.searchPlaceholder')" class="w-56" />
      <el-button :icon="Refresh" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
      <el-upload v-if="canCreate" :auto-upload="false" :show-file-list="false" accept=".csv" @change="onUploadCsv">
        <el-button type="success" :loading="importing">{{ t('pages.fluorescentColors.importCsv') }}</el-button>
      </el-upload>
      <el-button v-if="isAdmin" type="warning" plain :loading="importingBundled" @click="importBundled">
        {{ t('pages.fluorescentColors.importBundled') }}
      </el-button>
    </template>

    <div class="mb-3 flex flex-wrap items-center gap-2">
      <el-tag type="info">{{ t('common.total') }}: {{ total }}</el-tag>
      <el-tag>GLOBAL: {{ summary.GLOBAL }}</el-tag>
      <el-tag>NB: {{ summary.NB }}</el-tag>
      <el-tag>ADIDAS: {{ summary.ADIDAS }}</el-tag>
      <el-tag>UA: {{ summary.UA }}</el-tag>
    </div>

    <el-table :data="rows" v-loading="loading" border stripe size="small" table-layout="fixed">
      <el-table-column type="index" :label="t('common.noLabel')" width="50" align="center" />
      <el-table-column prop="buyer_code" :label="t('common.buyer')" width="100" align="center" />
      <el-table-column prop="season_label" :label="t('pages.fluorescentColors.colSeason')" min-width="130" show-overflow-tooltip />
      <el-table-column prop="season_year" :label="t('pages.fluorescentColors.colYear')" width="72" align="center" />
      <el-table-column prop="season_type" :label="t('pages.fluorescentColors.colSeasonType')" width="72" align="center" />
      <el-table-column prop="color_code" :label="t('pages.fluorescentColors.colCode')" width="120" show-overflow-tooltip />
      <el-table-column prop="color_name" :label="t('common.color')" min-width="180" show-overflow-tooltip />
      <el-table-column prop="color_class" :label="t('pages.fluorescentColors.colClass')" width="100" align="center" />
      <el-table-column prop="source_file" :label="t('pages.fluorescentColors.colSource')" min-width="120" show-overflow-tooltip />
      <el-table-column :label="t('common.actions')" width="100" fixed="right" align="center">
        <template #default="{ row }">
          <el-button v-if="canUpdate" link type="primary" size="small" @click="openEdit(row)">{{ t('common.edit') }}</el-button>
          <el-button v-if="canDelete" link type="danger" size="small" @click="remove(row)">{{ t('common.delete') }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-3 flex justify-end">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        size="small"
        layout="total, sizes, prev, pager, next"
        :total="total"
        :page-sizes="[20, 50, 100, 200]"
      />
    </div>

    <el-dialog v-model="formVisible" :title="editId ? t('common.edit') : t('common.create')" width="600px" destroy-on-close>
      <el-form label-position="top">
        <el-row :gutter="12">
          <el-col :span="12">
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
          <el-col :span="12">
            <el-form-item :label="t('pages.fluorescentColors.colClass')" required>
              <el-select v-model="form.color_class" class="w-full">
                <el-option v-for="c in formOptions.color_classes" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
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
          <el-col :span="6">
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
          <el-col :span="6">
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
          <el-col :span="12">
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
          <el-col :span="12">
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
      <template #footer>
        <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="save">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import {
  createFluorescentColor,
  deleteFluorescentColor,
  importFluorescentBundled,
  importFluorescentCsv,
  listFluorescentColorsPage,
  listFluorescentFormOptions,
  me,
  updateFluorescentColor,
} from '../../api/client'

const { t } = useI18n()
const canCreate = can('masterImport', 'create') || can('po', 'create')
const canUpdate = can('masterImport', 'create') || can('po', 'update')
const canDelete = can('masterImport', 'create')
const isAdmin = ref(false)

const loading = ref(false)
const saving = ref(false)
const importing = ref(false)
const importingBundled = ref(false)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)
const keyword = ref('')
const filterBuyer = ref('')
const filterClass = ref('')
const formVisible = ref(false)
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
  const seasons = form.buyer_code
    ? formOptions.season_labels_by_buyer[form.buyer_code]
    : null
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

async function onUploadCsv(uploadFile) {
  const file = uploadFile?.raw
  if (!file) return
  importing.value = true
  try {
    const r = await importFluorescentCsv(file)
    ElMessage.success(
      t('pages.fluorescentColors.importDone', {
        inserted: r.inserted,
        updated: r.updated,
        total: r.total,
      }),
    )
    await Promise.all([load(), loadSummary(), loadFormOptions()])
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    importing.value = false
  }
}

async function importBundled() {
  try {
    await ElMessageBox.confirm(t('pages.fluorescentColors.importBundledConfirm'), t('common.confirm'), { type: 'info' })
  } catch {
    return
  }
  importingBundled.value = true
  try {
    const r = await importFluorescentBundled()
    ElMessage.success(
      t('pages.fluorescentColors.importDone', {
        inserted: r.inserted,
        updated: r.updated,
        total: r.total,
      }),
    )
    await Promise.all([load(), loadSummary(), loadFormOptions()])
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    importingBundled.value = false
  }
}

watch([page, pageSize], () => load())
watch([filterBuyer, filterClass, keyword], () => {
  page.value = 1
  load()
})

onMounted(async () => {
  try {
    const u = await me()
    isAdmin.value = (u?.role || '') === 'admin'
  } catch {
    isAdmin.value = false
  }
  await Promise.all([loadFormOptions(), load(), loadSummary()])
})
</script>
