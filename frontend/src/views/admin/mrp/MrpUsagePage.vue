<template>
  <AdminSection :title="t('pages.mrpUsage.title')" :subtitle="t('pages.mrpUsage.subtitle')">
    <template #actions>
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <el-tabs v-model="tab">
      <el-tab-pane :label="t('pages.mrpUsage.color')" name="color">
        <div v-if="canCreate" class="admin-inner-card mb-4">
          <div class="admin-inner-card__head">
            <div>
              <h3 class="admin-inner-card__title">{{ t('pages.mrpUsage.colorFormTitle') }}</h3>
              <p class="admin-inner-card__sub">{{ t('pages.mrpUsage.colorHint') }}</p>
            </div>
          </div>
          <div class="mkt-section-body">
          <div class="flex flex-wrap gap-2 mb-3 items-center">
            <el-input
              v-model="colorForm.kode_lot_warna"
              :placeholder="t('pages.mrpUsage.scanLot')"
              class="max-w-xs"
              clearable
              @keyup.enter="scanLot"
            />
            <el-button :loading="scanning" @click="scanLot">{{ t('pages.mrpUsage.scanBtn') }}</el-button>
            <el-select
              v-model="colorForm.kode_wip"
              filterable
              allow-create
              default-first-option
              :placeholder="t('pages.mrpUsage.wip')"
              class="max-w-xs"
            >
              <el-option v-for="w in colorWip" :key="w" :label="w" :value="w" />
            </el-select>
            <el-input
              v-model="colorForm.qty_digunakan"
              type="number"
              :placeholder="t('pages.mrpUsage.qty')"
              class="w-28"
            />
            <el-select
              v-model="colorForm.stok_in_id"
              clearable
              filterable
              :placeholder="t('pages.mrpUsage.stokLot')"
              class="max-w-sm"
            >
              <el-option
                v-for="s in kimiaLots"
                :key="s.id"
                :label="`${s.kode_internal} · ${s.nama_barang} · ${formatQty(s.qty_sisa)}`"
                :value="s.id"
              />
            </el-select>
            <el-button type="primary" :loading="saving" :disabled="!lotInfo" @click="saveColor">
              {{ t('common.save') }}
            </el-button>
          </div>
          <div v-if="lotInfo" class="admin-stats-grid admin-stats-grid--4 mb-3">
            <div class="admin-stat-card">
              <span class="admin-stat-card__label">{{ t('pages.mrpUsage.lot') }}</span>
              <span>{{ dash(lotInfo.kode_lot_warna) }}</span>
            </div>
            <div class="admin-stat-card">
              <span class="admin-stat-card__label">{{ t('common.name') }}</span>
              <span>{{ dash(lotInfo.nama_lot_warna) }}</span>
            </div>
            <div class="admin-stat-card">
              <span class="admin-stat-card__label">{{ t('pages.mrpUsage.qtyPembuatan') }}</span>
              <span>{{ formatQty(lotInfo.qty_pembuatan) }}</span>
            </div>
            <div class="admin-stat-card">
              <span class="admin-stat-card__label">{{ t('common.status') }}</span>
              <el-tag size="small" effect="plain" type="success">{{ dash(lotInfo.status) }}</el-tag>
            </div>
          </div>
        </div>
        </div>
        <div class="admin-inner-card">
          <div class="admin-inner-card__head">
            <div>
              <h3 class="admin-inner-card__title">{{ t('pages.mrpUsage.colorHistory') }}</h3>
              <p class="admin-inner-card__sub">{{ t('pages.mrpUsage.listSubtitle') }}</p>
            </div>
            <el-input v-model="searchColor" clearable size="small" class="mrp-toolbar-search" :placeholder="t('pages.mrpUsage.searchPlaceholder')" />
          </div>
          <div class="mkt-section-body">
          <div class="admin-table-scroll">
          <el-table :data="filteredColor" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('pages.mrpUsage.tableEmpty')">
            <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
            <el-table-column prop="kode_wip" :label="t('pages.mrpUsage.wip')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="kode_lot_warna" :label="t('pages.mrpUsage.lot')" min-width="120" show-overflow-tooltip />
            <el-table-column :label="t('common.color')" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.nama_warna) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpUsage.qtyPembuatan')" width="110" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_pembuatan) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpUsage.qtyDigunakan')" width="110" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_digunakan) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.date')" width="150">
              <template #default="{ row }">{{ formatDateTime(row.date_created) }}</template>
            </el-table-column>
          </el-table>
          </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.mrpUsage.rp')" name="rp">
        <div v-if="canCreate" class="admin-inner-card mb-4">
          <div class="admin-inner-card__head">
            <div>
              <h3 class="admin-inner-card__title">{{ t('pages.mrpUsage.rpFormTitle') }}</h3>
              <p class="admin-inner-card__sub">{{ t('pages.mrpUsage.rpHint') }}</p>
            </div>
          </div>
          <div class="mkt-section-body">
          <div class="flex flex-wrap gap-2 mb-3 items-center">
            <el-input
              v-model="rpForm.jenis_rp"
              :placeholder="t('pages.mrpUsage.scanRp')"
              class="max-w-xs"
              clearable
              @keyup.enter="scanRp"
            />
            <el-button :loading="scanning" @click="scanRp">{{ t('pages.mrpUsage.scanBtn') }}</el-button>
            <el-select
              v-model="rpForm.kode_wip"
              filterable
              allow-create
              default-first-option
              :placeholder="t('pages.mrpUsage.wip')"
              class="max-w-xs"
            >
              <el-option v-for="w in rpWip" :key="w" :label="w" :value="w" />
            </el-select>
            <el-input v-model="rpForm.qty_used" type="number" :placeholder="t('pages.mrpUsage.qty')" class="w-28" />
            <el-input v-model="rpForm.satuan" :placeholder="t('pages.mrpUsage.satuan')" class="w-24" />
            <el-select
              v-model="rpForm.stok_in_id"
              clearable
              filterable
              :placeholder="t('pages.mrpUsage.stokLot')"
              class="max-w-sm"
            >
              <el-option
                v-for="s in rpLots"
                :key="s.id"
                :label="`${s.kode_internal} · ${s.nama_jenis} · ${formatQty(s.qty_sisa)}`"
                :value="s.id"
              />
            </el-select>
            <el-button type="primary" :loading="saving" :disabled="!rpInfo" @click="saveRp">
              {{ t('common.save') }}
            </el-button>
          </div>
          <div v-if="rpInfo" class="admin-stats-grid admin-stats-grid--4 mb-3">
            <div class="admin-stat-card">
              <span class="admin-stat-card__label">{{ t('pages.mrpUsage.rp') }}</span>
              <span>{{ dash(rpInfo.kode_rp) }}</span>
            </div>
            <div class="admin-stat-card">
              <span class="admin-stat-card__label">{{ t('common.name') }}</span>
              <span>{{ dash(rpInfo.nama_jenis) }}</span>
            </div>
            <div class="admin-stat-card">
              <span class="admin-stat-card__label">{{ t('pages.mrpUsage.satuan') }}</span>
              <span>{{ dash(rpInfo.satuan) }}</span>
            </div>
          </div>
        </div>
        </div>
        <div class="admin-inner-card">
          <div class="admin-inner-card__head">
            <div>
              <h3 class="admin-inner-card__title">{{ t('pages.mrpUsage.rpHistory') }}</h3>
              <p class="admin-inner-card__sub">{{ t('pages.mrpUsage.listSubtitle') }}</p>
            </div>
            <el-input v-model="searchRp" clearable size="small" class="mrp-toolbar-search" :placeholder="t('pages.mrpUsage.searchPlaceholder')" />
          </div>
          <div class="mkt-section-body">
          <div class="admin-table-scroll">
          <el-table :data="filteredRp" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('pages.mrpUsage.tableEmpty')">
            <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
            <el-table-column prop="kode_wip" :label="t('pages.mrpUsage.wip')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="jenis_rp" :label="t('pages.mrpUsage.rp')" min-width="140" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpUsage.qty')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_used) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpUsage.satuan')" width="90">
              <template #default="{ row }">{{ dash(row.satuan) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.date')" width="150">
              <template #default="{ row }">{{ formatDateTime(row.date_created) }}</template>
            </el-table-column>
          </el-table>
          </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.mrpUsage.material')" name="material">
        <div v-if="canCreate" class="admin-inner-card mb-4">
          <div class="admin-inner-card__head">
            <div>
              <h3 class="admin-inner-card__title">{{ t('pages.mrpUsage.matFormTitle') }}</h3>
              <p class="admin-inner-card__sub">{{ t('pages.mrpUsage.matHint') }}</p>
            </div>
          </div>
          <div class="mkt-section-body">
          <div class="flex flex-wrap gap-2 mb-3 items-center">
            <el-input
              v-model="matForm.kode_material"
              :placeholder="t('pages.mrpUsage.scanMaterial')"
              class="max-w-xs"
              clearable
              @keyup.enter="scanMat"
            />
            <el-button :loading="scanning" @click="scanMat">{{ t('pages.mrpUsage.scanBtn') }}</el-button>
            <el-select
              v-model="matForm.kode_wip"
              filterable
              allow-create
              default-first-option
              :placeholder="t('pages.mrpUsage.wip')"
              class="max-w-xs"
            >
              <el-option v-for="w in matWip" :key="w" :label="w" :value="w" />
            </el-select>
            <el-input v-model="matForm.qty_used" type="number" :placeholder="t('pages.mrpUsage.qty')" class="w-28" />
            <el-input v-model="matForm.satuan" :placeholder="t('pages.mrpUsage.satuan')" class="w-24" />
            <el-select
              v-model="matForm.stok_in_id"
              clearable
              filterable
              :placeholder="t('pages.mrpUsage.stokLot')"
              class="max-w-sm"
            >
              <el-option
                v-for="s in matLots"
                :key="s.id"
                :label="`${s.kode_internal} · ${s.nama_material} · ${formatQty(s.qty_sisa)}`"
                :value="s.id"
              />
            </el-select>
            <el-button type="primary" :loading="saving" :disabled="!matInfo" @click="saveMat">
              {{ t('common.save') }}
            </el-button>
          </div>
          <div v-if="matInfo" class="admin-stats-grid admin-stats-grid--4 mb-3">
            <div class="admin-stat-card">
              <span class="admin-stat-card__label">{{ t('pages.mrpUsage.kode') }}</span>
              <span>{{ dash(matInfo.kode_material) }}</span>
            </div>
            <div class="admin-stat-card">
              <span class="admin-stat-card__label">{{ t('common.name') }}</span>
              <span>{{ dash(matInfo.nama_material) }}</span>
            </div>
            <div class="admin-stat-card">
              <span class="admin-stat-card__label">{{ t('pages.mrpUsage.satuan') }}</span>
              <span>{{ dash(matInfo.satuan) }}</span>
            </div>
          </div>
        </div>
        </div>
        <div class="admin-inner-card">
          <div class="admin-inner-card__head">
            <div>
              <h3 class="admin-inner-card__title">{{ t('pages.mrpUsage.matHistory') }}</h3>
              <p class="admin-inner-card__sub">{{ t('pages.mrpUsage.listSubtitle') }}</p>
            </div>
            <el-input v-model="searchMat" clearable size="small" class="mrp-toolbar-search" :placeholder="t('pages.mrpUsage.searchPlaceholder')" />
          </div>
          <div class="mkt-section-body">
          <div class="admin-table-scroll">
          <el-table :data="filteredMat" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('pages.mrpUsage.tableEmpty')">
            <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
            <el-table-column prop="kode_wip" :label="t('pages.mrpUsage.wip')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="kode_material" :label="t('pages.mrpUsage.kode')" min-width="120" show-overflow-tooltip />
            <el-table-column :label="t('common.name')" min-width="140" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.nama_material) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpUsage.qty')" width="90" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_used) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpUsage.satuan')" width="90">
              <template #default="{ row }">{{ dash(row.satuan) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.date')" width="150">
              <template #default="{ row }">{{ formatDateTime(row.date_created) }}</template>
            </el-table-column>
          </el-table>
          </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import {
  mrpStokKimia,
  mrpStokMaterialLain,
  mrpStokRp,
  mrpUsageColor,
  mrpUsageColorCreate,
  mrpUsageColorScanLot,
  mrpUsageMaterial,
  mrpUsageMaterialCreate,
  mrpUsageMaterialScan,
  mrpUsageRp,
  mrpUsageRpCreate,
  mrpUsageRpScan,
} from '../../../api/client'

const { t } = useI18n()
const tab = ref('color')
const loading = ref(false)
const saving = ref(false)
const scanning = ref(false)
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const colorRows = ref([])
const colorWip = ref([])
const rpRows = ref([])
const rpWip = ref([])
const matRows = ref([])
const matWip = ref([])
const kimiaLots = ref([])
const rpLots = ref([])
const matLots = ref([])
const lotInfo = ref(null)
const rpInfo = ref(null)
const matInfo = ref(null)
const searchColor = ref('')
const searchRp = ref('')
const searchMat = ref('')
const colorForm = reactive({ kode_lot_warna: '', kode_wip: '', qty_digunakan: null, stok_in_id: null })
const rpForm = reactive({ jenis_rp: '', kode_wip: '', qty_used: null, satuan: 'meter', stok_in_id: null })
const matForm = reactive({ kode_material: '', kode_wip: '', qty_used: null, satuan: 'pcs', stok_in_id: null })

const filteredColor = computed(() => filterRows(colorRows.value, searchColor.value, ['kode_wip', 'kode_lot_warna', 'nama_warna']))
const filteredRp = computed(() => filterRows(rpRows.value, searchRp.value, ['kode_wip', 'jenis_rp', 'satuan']))
const filteredMat = computed(() =>
  filterRows(matRows.value, searchMat.value, ['kode_wip', 'kode_material', 'nama_material']),
)

function filterRows(rows, q, keys) {
  const s = (q || '').trim().toLowerCase()
  if (!s) return rows
  return (rows || []).filter((r) => keys.map((k) => r[k]).filter(Boolean).join(' ').toLowerCase().includes(s))
}

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 3 })
}

function formatDateTime(v) {
  if (!v) return '—'
  return String(v).replace('T', ' ').slice(0, 19)
}

function errMsg(e) {
  const raw = e?.message || String(e)
  try {
    const j = JSON.parse(raw)
    const d = j?.detail
    if (typeof d === 'string') return d
    if (d && typeof d === 'object' && typeof d.detail === 'string') return d.detail
    if (typeof j?.message === 'string') return j.message
    return raw
  } catch {
    return raw
  }
}

async function reload() {
  loading.value = true
  try {
    if (tab.value === 'color') {
      const [d, stok] = await Promise.all([mrpUsageColor(), mrpStokKimia()])
      colorRows.value = d.usage_list || []
      colorWip.value = d.wip_list || []
      kimiaLots.value = stok.stok_in || []
    } else if (tab.value === 'rp') {
      const [d, stok] = await Promise.all([mrpUsageRp(), mrpStokRp()])
      rpRows.value = d.usage_list || []
      rpWip.value = d.wip_list || []
      rpLots.value = stok.stok_in || []
    } else {
      const [d, stok] = await Promise.all([mrpUsageMaterial(), mrpStokMaterialLain()])
      matRows.value = d.usage_list || []
      matWip.value = d.wip_list || []
      matLots.value = stok.stok_in || []
    }
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    loading.value = false
  }
}

async function scanLot() {
  const kode = colorForm.kode_lot_warna.trim()
  if (!kode) {
    ElMessage.warning(t('pages.mrpUsage.scanLot'))
    return
  }
  scanning.value = true
  try {
    lotInfo.value = await mrpUsageColorScanLot(kode)
    colorForm.kode_lot_warna = lotInfo.value.kode_lot_warna || kode
    ElMessage.success(t('pages.mrpUsage.scanOk'))
  } catch (e) {
    lotInfo.value = null
    ElMessage.error(errMsg(e))
  } finally {
    scanning.value = false
  }
}

async function scanRp() {
  const kode = rpForm.jenis_rp.trim()
  if (!kode) {
    ElMessage.warning(t('pages.mrpUsage.scanRp'))
    return
  }
  scanning.value = true
  try {
    rpInfo.value = await mrpUsageRpScan(kode)
    rpForm.jenis_rp = rpInfo.value.kode_rp || kode
    if (rpInfo.value?.satuan) rpForm.satuan = rpInfo.value.satuan
    ElMessage.success(t('pages.mrpUsage.scanOk'))
  } catch (e) {
    rpInfo.value = null
    ElMessage.error(errMsg(e))
  } finally {
    scanning.value = false
  }
}

async function scanMat() {
  const kode = matForm.kode_material.trim()
  if (!kode) {
    ElMessage.warning(t('pages.mrpUsage.scanMaterial'))
    return
  }
  scanning.value = true
  try {
    matInfo.value = await mrpUsageMaterialScan(kode)
    matForm.kode_material = matInfo.value.kode_material || kode
    if (matInfo.value?.satuan) matForm.satuan = matInfo.value.satuan
    ElMessage.success(t('pages.mrpUsage.scanOk'))
  } catch (e) {
    matInfo.value = null
    ElMessage.error(errMsg(e))
  } finally {
    scanning.value = false
  }
}

async function saveColor() {
  if (!colorForm.kode_wip.trim() || !colorForm.kode_lot_warna.trim()) {
    ElMessage.warning(t('pages.mrpUsage.wipLotRequired'))
    return
  }
  const qty = Number(colorForm.qty_digunakan)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpUsage.qtyInvalid'))
    return
  }
  if (!lotInfo.value) {
    await scanLot()
    if (!lotInfo.value) return
  }
  saving.value = true
  try {
    const res = await mrpUsageColorCreate({
      kode_lot_warna: colorForm.kode_lot_warna.trim(),
      kode_wip: colorForm.kode_wip.trim(),
      qty_digunakan: qty,
      stok_in_id: colorForm.stok_in_id || null,
    })
    ElMessage.success(
      res?.stok_deducted ? t('pages.mrpUsage.savedDeducted') : t('common.saved'),
    )
    colorForm.qty_digunakan = null
    colorForm.stok_in_id = null
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

async function saveRp() {
  if (!rpForm.kode_wip.trim() || !rpForm.jenis_rp.trim()) {
    ElMessage.warning(t('pages.mrpUsage.wipRpRequired'))
    return
  }
  const qty = Number(rpForm.qty_used)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpUsage.qtyInvalid'))
    return
  }
  if (!rpInfo.value) {
    await scanRp()
    if (!rpInfo.value) return
  }
  saving.value = true
  try {
    const res = await mrpUsageRpCreate({
      jenis_rp: rpForm.jenis_rp.trim(),
      kode_wip: rpForm.kode_wip.trim(),
      qty_used: qty,
      satuan: rpForm.satuan.trim() || 'meter',
      stok_in_id: rpForm.stok_in_id || null,
    })
    ElMessage.success(
      res?.stok_deducted ? t('pages.mrpUsage.savedDeducted') : t('common.saved'),
    )
    rpForm.qty_used = null
    rpForm.stok_in_id = null
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

async function saveMat() {
  if (!matForm.kode_wip.trim() || !matForm.kode_material.trim()) {
    ElMessage.warning(t('pages.mrpUsage.wipMatRequired'))
    return
  }
  const qty = Number(matForm.qty_used)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpUsage.qtyInvalid'))
    return
  }
  if (!matInfo.value) {
    await scanMat()
    if (!matInfo.value) return
  }
  saving.value = true
  try {
    const res = await mrpUsageMaterialCreate({
      kode_material: matForm.kode_material.trim(),
      kode_wip: matForm.kode_wip.trim(),
      qty_used: qty,
      satuan: matForm.satuan.trim() || 'pcs',
      stok_in_id: matForm.stok_in_id || null,
    })
    ElMessage.success(
      res?.stok_deducted ? t('pages.mrpUsage.savedDeducted') : t('common.saved'),
    )
    matForm.qty_used = null
    matForm.stok_in_id = null
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

watch(tab, reload)
onMounted(reload)
</script>

<style scoped>
.w-24 { width: 6rem; }
.w-28 { width: 7rem; }
.max-w-xs { max-width: 16rem; }
.max-w-sm { max-width: 24rem; }
</style>
