<template>
  <AdminSection :title="t('pages.dataIntelligent.title')" :subtitle="t('pages.dataIntelligent.subtitle')">
    <template #actions>
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="load">{{ t('common.refresh') }}</el-button>
      <el-button type="primary" :icon="Download" :loading="downloading" @click="download">
        {{ t('pages.dataIntelligent.download') }}
      </el-button>
      <el-upload
        v-if="canUpdate"
        :show-file-list="false"
        accept=".xlsx"
        :http-request="upload"
      >
        <el-button type="success" :icon="Upload" :loading="uploading">
          {{ t('pages.dataIntelligent.upload') }}
        </el-button>
      </el-upload>
    </template>

    <div class="admin-inner-card">
      <p class="mb-4 text-sm text-slate-500">{{ t('pages.dataIntelligent.hint') }}</p>
      <h3 class="mb-3 text-sm font-semibold text-slate-700">{{ t('pages.dataIntelligent.unmappedTitle') }}</h3>
      <div class="admin-stats-grid admin-stats-grid--5">
        <button
          v-for="card in countCards"
          :key="card.key"
          type="button"
          class="admin-stat-card text-left"
          @click="openCard(card)"
        >
          <span class="admin-stat-card__value">{{ counts[card.key] ?? 0 }}</span>
          <span class="admin-stat-card__label">{{ t(`pages.dataIntelligent.${card.key}`) }}</span>
        </button>
      </div>
      <h3 class="mb-3 mt-6 text-sm font-semibold text-slate-700">{{ t('pages.dataIntelligent.matchedTitle') }}</h3>
      <div class="admin-stats-grid admin-stats-grid--5">
        <button
          v-for="card in matchedCards"
          :key="card.key"
          type="button"
          class="admin-stat-card admin-stat-card--success text-left"
          @click="openMatched(card)"
        >
          <span class="admin-stat-card__value">{{ counts[card.key] ?? 0 }}</span>
          <span class="admin-stat-card__label">{{ t(`pages.dataIntelligent.${card.key}`) }}</span>
        </button>
      </div>
      <div class="mt-4">
        <p class="mb-3 text-sm text-slate-500">{{ t('pages.dataIntelligent.matchedHint') }}</p>
        <div class="mb-3 flex flex-wrap gap-3">
          <el-select v-model="matchSheet" class="w-72" @change="loadMatched(1)">
            <el-option v-for="card in matchedCards" :key="card.sheet" :label="t(`pages.dataIntelligent.${card.key}`)" :value="card.sheet" />
          </el-select>
          <el-input v-model="matchQuery" clearable :placeholder="t('pages.dataIntelligent.search')" class="w-64" @change="loadMatched(1)" />
        </div>
        <el-table v-loading="matchLoading" :data="matchRows" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
          <el-table-column v-for="column in matchColumns" :key="column" :prop="column" :label="columnLabel(column)" min-width="140" />
        </el-table>
        <div class="mt-3 flex justify-end">
          <el-pagination
            layout="prev, pager, next"
            :current-page="matchPage"
            :page-size="50"
            :total="matchTotal"
            @current-change="loadMatched"
          />
        </div>
      </div>
    </div>

    <div class="admin-inner-card mt-4">
      <div class="admin-inner-card__head">
        <h3 class="admin-inner-card__title">{{ t('pages.dataIntelligent.webFix') }}</h3>
        <el-button v-if="canUpdate && activeTab !== 'reference'" type="primary" :loading="saving" @click="saveActive">
          {{ t('pages.dataIntelligent.save') }}
        </el-button>
      </div>
      <el-tabs v-model="activeTab">
        <el-tab-pane :label="t('pages.dataIntelligent.customer_tanpa_brand')" name="Map_Customer_Brand">
          <el-table :data="shown('Map_Customer_Brand')" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
            <el-table-column prop="customer_code" :label="t('pages.dataIntelligent.customer')" width="140" />
            <el-table-column prop="customer_name" :label="t('pages.dataIntelligent.customer')" min-width="220" />
            <el-table-column :label="t('pages.dataIntelligent.brand')" min-width="220">
              <template #default="{ row }">
                <el-select v-model="row.brand_code" filterable clearable :disabled="!canUpdate" class="w-full">
                  <el-option v-for="brand in brands" :key="brand.code" :label="brandLabel(brand)" :value="brand.code" />
                </el-select>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane :label="t('pages.dataIntelligent.brand_tanpa_buyer')" name="Map_Brand_Buyer">
          <el-table :data="shown('Map_Brand_Buyer')" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
            <el-table-column prop="brand_code" :label="t('pages.dataIntelligent.brand')" width="140" />
            <el-table-column prop="brand_name" :label="t('pages.dataIntelligent.brand')" min-width="220" />
            <el-table-column :label="t('pages.dataIntelligent.buyer')" min-width="220">
              <template #default="{ row }">
                <el-select v-model="row.buyer_code" filterable clearable :disabled="!canUpdate" class="w-full">
                  <el-option v-for="buyer in buyers" :key="buyer.code" :label="buyerLabel(buyer)" :value="buyer.code" />
                </el-select>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane :label="t('pages.dataIntelligent.swatch_tanpa_csi')" name="Swatch_Tanpa_CSI">
          <el-input v-model="keyword" clearable :placeholder="t('pages.dataIntelligent.search')" class="mb-3 max-w-sm" />
          <el-table :data="shown('Swatch_Tanpa_CSI')" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
            <el-table-column prop="factory_key" :label="t('pages.dataIntelligent.factory')" width="140" />
            <el-table-column prop="buyer_code" :label="t('pages.dataIntelligent.buyer')" width="110" />
            <el-table-column prop="color_code" :label="t('pages.dataIntelligent.colorCode')" width="120" />
            <el-table-column prop="color_name" :label="t('pages.dataIntelligent.colorName')" min-width="160" />
            <el-table-column prop="material_name" :label="t('pages.dataIntelligent.material')" min-width="160" />
            <el-table-column prop="emboss" :label="t('pages.dataIntelligent.emboss')" width="120" />
            <el-table-column :label="t('pages.dataIntelligent.csiCode')" min-width="240">
              <template #default="{ row }">
                <el-select v-model="row.csi_color_code" filterable clearable :disabled="!canUpdate" class="w-full">
                  <el-option
                    v-for="item in csiFor(row.buyer_code)"
                    :key="item.color_code"
                    :label="`${item.color_code} — ${item.color_name}`"
                    :value="item.color_code"
                  />
                </el-select>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane :label="t('pages.dataIntelligent.addCsi')" name="CSI_Baru">
          <div v-if="canUpdate" class="mb-4 flex flex-wrap items-end gap-3">
            <el-select v-model="csiForm.buyer_code" filterable :placeholder="t('pages.dataIntelligent.buyer')" class="w-48">
              <el-option v-for="buyer in buyers" :key="buyer.code" :label="buyerLabel(buyer)" :value="buyer.code" />
            </el-select>
            <el-input v-model="csiForm.color_code" :placeholder="t('pages.dataIntelligent.colorCode')" class="w-40" />
            <el-input v-model="csiForm.color_name" :placeholder="t('pages.dataIntelligent.colorName')" class="w-64" />
            <el-button @click="addCsiDraft">{{ t('pages.dataIntelligent.addCsi') }}</el-button>
          </div>
          <el-table :data="csiDrafts" border stripe size="small" class="admin-table" :empty-text="t('pages.dataIntelligent.csiDraft')">
            <el-table-column prop="buyer_code" :label="t('pages.dataIntelligent.buyer')" width="140" />
            <el-table-column prop="color_code" :label="t('pages.dataIntelligent.colorCode')" width="140" />
            <el-table-column prop="color_name" :label="t('pages.dataIntelligent.colorName')" min-width="220" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane :label="t('pages.dataIntelligent.nama_beda')" name="Nama_Beda">
          <el-input v-model="keyword" clearable :placeholder="t('pages.dataIntelligent.search')" class="mb-3 max-w-sm" />
          <el-table :data="shown('Nama_Beda')" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
            <el-table-column prop="buyer_code" :label="t('pages.dataIntelligent.buyer')" width="110" />
            <el-table-column prop="color_code" :label="t('pages.dataIntelligent.colorCode')" width="120" />
            <el-table-column prop="swatch_name" :label="t('pages.dataIntelligent.useSwatch')" min-width="180" />
            <el-table-column prop="csi_name" :label="t('pages.dataIntelligent.useCsi')" min-width="180" />
            <el-table-column :label="t('pages.dataIntelligent.decision')" min-width="220">
              <template #default="{ row }">
                <el-select v-model="row.keputusan" clearable :disabled="!canUpdate" class="w-full">
                  <el-option :label="t('pages.dataIntelligent.keep')" value="BIARKAN" />
                  <el-option :label="t('pages.dataIntelligent.useCsi')" value="IKUT_CSI" />
                  <el-option :label="t('pages.dataIntelligent.useSwatch')" value="IKUT_SWATCH" />
                </el-select>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane :label="t('pages.dataIntelligent.item_kode_kosong')" name="Item_Kode_Kosong">
          <el-table :data="shown('Item_Kode_Kosong')" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
            <el-table-column prop="item_code" :label="t('pages.dataIntelligent.item')" width="140" />
            <el-table-column prop="material_name" :label="t('pages.dataIntelligent.material')" min-width="180" />
            <el-table-column prop="color" :label="t('pages.dataIntelligent.colorName')" min-width="180" />
            <el-table-column prop="emboss" :label="t('pages.dataIntelligent.emboss')" width="140" />
            <el-table-column :label="t('pages.dataIntelligent.colorCode')" width="160">
              <template #default="{ row }">
                <el-input v-model="row.color_code" :disabled="!canUpdate" maxlength="64" />
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane :label="t('pages.dataIntelligent.reference')" name="reference">
          <p class="mb-3 text-sm text-slate-500">{{ t('pages.dataIntelligent.readOnlyHint') }}</p>
          <div class="mb-3 flex flex-wrap gap-3">
            <el-select v-model="refSheet" class="w-72" @change="loadReference(1)">
              <el-option v-for="name in referenceSheets" :key="name" :label="referenceLabel(name)" :value="name" />
            </el-select>
            <el-input v-model="refQuery" clearable :placeholder="t('pages.dataIntelligent.search')" class="w-64" @change="loadReference(1)" />
          </div>
          <el-table v-loading="refLoading" :data="refRows" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
            <el-table-column v-for="column in refColumns" :key="column" :prop="column" :label="columnLabel(column)" min-width="140" />
          </el-table>
          <div class="mt-3 flex justify-end">
            <el-pagination
              layout="prev, pager, next"
              :current-page="refPage"
              :page-size="50"
              :total="refTotal"
              @current-change="loadReference"
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <div class="admin-inner-card mt-4">
      <div class="admin-inner-card__head">
        <h3 class="admin-inner-card__title">{{ t('pages.dataIntelligent.resultTitle') }}</h3>
      </div>
      <el-table :data="results" border stripe size="small" class="admin-table" :empty-text="t('pages.dataIntelligent.resultEmpty')">
        <el-table-column prop="status" :label="t('common.status')" width="120" />
        <el-table-column prop="sheet" :label="t('pages.dataIntelligent.sheet')" width="220" />
        <el-table-column prop="row" :label="t('pages.dataIntelligent.row')" width="90" />
        <el-table-column prop="detail" :label="t('pages.dataIntelligent.detail')" />
      </el-table>
    </div>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Download, Refresh, Upload } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  applyDataIntelligent,
  downloadDataIntelligentWorkbook,
  getDataIntelligentWorkspace,
  importDataIntelligentWorkbook,
  listDataIntelligentGaps,
} from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { t } = useI18n()
const { canUpdate } = useModulePermission('dataIntelligent')

const matchedCards = [
  { key: 'match_customer_brand', sheet: 'Match_Customer_Brand' },
  { key: 'match_brand_buyer', sheet: 'Match_Brand_Buyer' },
  { key: 'match_swatch_csi', sheet: 'Match_Swatch_CSI' },
  { key: 'match_nama_sama', sheet: 'Match_Nama_Sama' },
  { key: 'match_item_kode', sheet: 'Match_Item_Kode' },
  { key: 'match_item_csi', sheet: 'Match_Item_CSI' },
  { key: 'match_fluorescent_csi', sheet: 'Match_Fluorescent_CSI' },
  { key: 'match_material_item', sheet: 'Match_Material_Item' },
  { key: 'match_item_swatch', sheet: 'Match_Item_Swatch' },
  { key: 'match_buyer_harga', sheet: 'Match_Buyer_Harga' },
]

const columnLabels = {
  customer_code: 'customer',
  customer_name: 'customer',
  brand_code: 'brand',
  brand_name: 'brand',
  buyer_code: 'buyer',
  factory_key: 'factory',
  color_code: 'colorCode',
  color_name: 'colorName',
  csi_color_code: 'csiCode',
  csi_color_name: 'useCsi',
  swatch_name: 'useSwatch',
  csi_name: 'useCsi',
  material_name: 'material',
  canonical_name: 'material',
  item_code: 'item',
  color: 'colorName',
  season_label: 'reference',
  name: 'buyer',
  recipe_count: 'detail',
}

const countCards = [
  { key: 'customer_tanpa_brand', tab: 'Map_Customer_Brand' },
  { key: 'brand_tanpa_buyer', tab: 'Map_Brand_Buyer' },
  { key: 'swatch_tanpa_csi', tab: 'Swatch_Tanpa_CSI' },
  { key: 'nama_beda', tab: 'Nama_Beda' },
  { key: 'item_kode_kosong', tab: 'Item_Kode_Kosong' },
  { key: 'item_tanpa_csi', tab: 'reference', sheet: 'Item_Tanpa_CSI' },
  { key: 'fluorescent_tanpa_csi', tab: 'reference', sheet: 'Fluorescent_Tanpa_CSI' },
  { key: 'material_swatch_tanpa_item', tab: 'reference', sheet: 'Material_Swatch_Tanpa_Item' },
  { key: 'item_tanpa_swatch', tab: 'reference', sheet: 'Item_Tanpa_Swatch' },
  { key: 'buyer_tanpa_harga', tab: 'reference', sheet: 'Buyer_Tanpa_Harga' },
]

const referenceSheets = [
  'Item_Tanpa_CSI',
  'Fluorescent_Tanpa_CSI',
  'Alias_Pabrik',
  'Material_Swatch_Tanpa_Item',
  'Item_Tanpa_Swatch',
  'Buyer_Tanpa_Harga',
]

const referenceLabels = {
  Item_Tanpa_CSI: 'item_tanpa_csi',
  Fluorescent_Tanpa_CSI: 'fluorescent_tanpa_csi',
  Alias_Pabrik: 'reference',
  Material_Swatch_Tanpa_Item: 'material_swatch_tanpa_item',
  Item_Tanpa_Swatch: 'item_tanpa_swatch',
  Buyer_Tanpa_Harga: 'buyer_tanpa_harga',
}

const loading = ref(false)
const downloading = ref(false)
const uploading = ref(false)
const saving = ref(false)
const counts = ref({})
const results = ref([])
const activeTab = ref('Map_Customer_Brand')
const keyword = ref('')
const brands = ref([])
const buyers = ref([])
const csi = ref([])
const sheets = ref({
  Map_Customer_Brand: [],
  Map_Brand_Buyer: [],
  Swatch_Tanpa_CSI: [],
  Nama_Beda: [],
  Item_Kode_Kosong: [],
})
const csiForm = ref({ buyer_code: '', color_code: '', color_name: '' })
const csiDrafts = ref([])
const refSheet = ref('Item_Tanpa_CSI')
const refRows = ref([])
const refColumns = ref([])
const refTotal = ref(0)
const refPage = ref(1)
const refQuery = ref('')
const refLoading = ref(false)
const matchSheet = ref('Match_Customer_Brand')
const matchRows = ref([])
const matchColumns = ref([])
const matchTotal = ref(0)
const matchPage = ref(1)
const matchQuery = ref('')
const matchLoading = ref(false)

const csiByBuyer = computed(() => {
  const grouped = {}
  for (const row of csi.value) {
    const key = String(row.buyer_code || '').toUpperCase()
    if (!grouped[key]) grouped[key] = []
    grouped[key].push(row)
  }
  return grouped
})

function csiFor(buyer) {
  return csiByBuyer.value[String(buyer || '').toUpperCase()] || []
}

function brandLabel(brand) {
  return brand.name ? `${brand.code} — ${brand.name}` : brand.code
}

function buyerLabel(buyer) {
  return buyer.name ? `${buyer.code} — ${buyer.name}` : buyer.code
}

function columnLabel(column) {
  const key = columnLabels[column]
  return key ? t(`pages.dataIntelligent.${key}`) : column
}

function referenceLabel(name) {
  return t(`pages.dataIntelligent.${referenceLabels[name] || 'reference'}`)
}

function shown(name) {
  const rows = sheets.value[name] || []
  const q = keyword.value.trim().toUpperCase()
  if (!q || (name !== 'Swatch_Tanpa_CSI' && name !== 'Nama_Beda')) return rows
  return rows.filter((row) => Object.values(row).join(' ').toUpperCase().includes(q))
}

function showResult(data) {
  const applied = data?.applied || []
  const rejected = data?.rejected || []
  results.value = [
    ...applied.map((row) => ({
      status: t('pages.dataIntelligent.applied'),
      sheet: row.sheet,
      row: row.row,
      detail: row.action,
    })),
    ...rejected.map((row) => ({
      status: t('pages.dataIntelligent.rejected'),
      sheet: row.sheet,
      row: row.row,
      detail: row.reason,
    })),
  ]
  ElMessage.success(t('pages.dataIntelligent.uploadOk', { applied: applied.length, rejected: rejected.length }))
}

async function load() {
  loading.value = true
  try {
    const data = await getDataIntelligentWorkspace()
    counts.value = data?.counts || {}
    brands.value = data?.brands || []
    buyers.value = data?.buyers || []
    csi.value = data?.csi || []
    sheets.value = {
      Map_Customer_Brand: data?.sheets?.Map_Customer_Brand || [],
      Map_Brand_Buyer: data?.sheets?.Map_Brand_Buyer || [],
      Swatch_Tanpa_CSI: data?.sheets?.Swatch_Tanpa_CSI || [],
      Nama_Beda: data?.sheets?.Nama_Beda || [],
      Item_Kode_Kosong: data?.sheets?.Item_Kode_Kosong || [],
    }
    await loadMatched(matchPage.value || 1)
  } catch (err) {
    ElMessage.error(err?.message || String(err))
  } finally {
    loading.value = false
  }
}

function filled(rows, field) {
  return rows.filter((row) => String(row[field] || '').trim())
}

function payloadFor(tab) {
  if (tab === 'Map_Customer_Brand') return { Map_Customer_Brand: filled(sheets.value.Map_Customer_Brand, 'brand_code') }
  if (tab === 'Map_Brand_Buyer') return { Map_Brand_Buyer: filled(sheets.value.Map_Brand_Buyer, 'buyer_code') }
  if (tab === 'Swatch_Tanpa_CSI') return { Swatch_Tanpa_CSI: filled(sheets.value.Swatch_Tanpa_CSI, 'csi_color_code') }
  if (tab === 'Nama_Beda') {
    return {
      Nama_Beda: (sheets.value.Nama_Beda || []).filter((row) => ['IKUT_CSI', 'IKUT_SWATCH'].includes(row.keputusan)),
    }
  }
  if (tab === 'Item_Kode_Kosong') return { Item_Kode_Kosong: filled(sheets.value.Item_Kode_Kosong, 'color_code') }
  if (tab === 'CSI_Baru') return { CSI_Baru: csiDrafts.value }
  return {}
}

async function saveActive() {
  const body = payloadFor(activeTab.value)
  const rows = Object.values(body)[0] || []
  if (!rows.length) {
    ElMessage.info(t('pages.dataIntelligent.nothingToSave'))
    return
  }
  saving.value = true
  try {
    const data = await applyDataIntelligent(body)
    showResult(data)
    if (activeTab.value === 'CSI_Baru' && !(data?.rejected || []).length) csiDrafts.value = []
    await load()
  } catch (err) {
    ElMessage.error(err?.message || String(err))
  } finally {
    saving.value = false
  }
}

function addCsiDraft() {
  const buyer = String(csiForm.value.buyer_code || '').trim()
  const code = String(csiForm.value.color_code || '').trim()
  const name = String(csiForm.value.color_name || '').trim()
  if (!buyer || !code || !name) {
    ElMessage.warning(t('pages.dataIntelligent.nothingToSave'))
    return
  }
  csiDrafts.value = [...csiDrafts.value, { buyer_code: buyer, color_code: code, color_name: name }]
  csiForm.value = { buyer_code: buyer, color_code: '', color_name: '' }
}

async function loadReference(page = 1) {
  refPage.value = page
  refLoading.value = true
  try {
    const data = await listDataIntelligentGaps({
      sheet: refSheet.value,
      page,
      page_size: 50,
      q: refQuery.value,
    })
    refRows.value = data?.rows || []
    refColumns.value = data?.columns || []
    refTotal.value = data?.total || 0
  } catch (err) {
    ElMessage.error(err?.message || String(err))
  } finally {
    refLoading.value = false
  }
}

async function loadMatched(page = 1) {
  matchPage.value = page
  matchLoading.value = true
  try {
    const data = await listDataIntelligentGaps({
      sheet: matchSheet.value,
      page,
      page_size: 50,
      q: matchQuery.value,
    })
    matchRows.value = data?.rows || []
    matchColumns.value = data?.columns || []
    matchTotal.value = data?.total || 0
  } catch (err) {
    ElMessage.error(err?.message || String(err))
  } finally {
    matchLoading.value = false
  }
}

function openMatched(card) {
  matchSheet.value = card.sheet
  loadMatched(1)
}

function openCard(card) {
  activeTab.value = card.tab
  if (card.sheet) {
    refSheet.value = card.sheet
    loadReference(1)
  }
}

async function download() {
  downloading.value = true
  try {
    await downloadDataIntelligentWorkbook()
    ElMessage.success(t('pages.dataIntelligent.downloadOk'))
  } catch (err) {
    ElMessage.error(err?.message || String(err))
  } finally {
    downloading.value = false
  }
}

async function upload(request) {
  uploading.value = true
  try {
    const data = await importDataIntelligentWorkbook(request.file)
    showResult(data)
    await load()
  } catch (err) {
    ElMessage.error(err?.message || String(err))
  } finally {
    uploading.value = false
  }
}

onMounted(load)
</script>
