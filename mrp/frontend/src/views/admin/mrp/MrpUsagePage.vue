<template>
  <AdminSection :title="t('pages.mrpUsage.title')" :subtitle="t('pages.mrpUsage.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <el-tabs v-model="tab" class="admin-tabs" @tab-change="() => { page = 1; reload() }">
      <el-tab-pane :label="t('pages.mrpUsage.color')" name="color">
        <div v-if="canCreate" class="admin-inner-card mb-4">
          <div class="admin-inner-card__body">
            <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpUsage.colorFormTitle') }}</h3>
          <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpUsage.colorHint') }}</p>
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
          <div v-if="lotInfo" class="mrp-usage-meta">
            <div class="mrp-usage-meta__item">
              <span class="mrp-usage-meta__label">{{ t('pages.mrpUsage.lot') }}</span>
              <span>{{ dash(lotInfo.kode_lot_warna) }}</span>
            </div>
            <div class="mrp-usage-meta__item">
              <span class="mrp-usage-meta__label">{{ t('common.name') }}</span>
              <span>{{ dash(lotInfo.nama_lot_warna) }}</span>
            </div>
            <div class="mrp-usage-meta__item">
              <span class="mrp-usage-meta__label">{{ t('pages.mrpUsage.qtyPembuatan') }}</span>
              <span>{{ formatQty(lotInfo.qty_pembuatan) }}</span>
            </div>
            <div class="mrp-usage-meta__item">
              <span class="mrp-usage-meta__label">{{ t('common.status') }}</span>
              <el-tag size="small" effect="plain" type="success">{{ dash(lotInfo.status) }}</el-tag>
            </div>
          </div>
          </div>
        </div>
        <div class="admin-inner-card">
          <div class="admin-inner-card__head">
            <h3 class="admin-inner-card__title">{{ t('pages.mrpUsage.colorHistory') }}</h3>
            <el-input v-model="searchColor" clearable size="small" class="w-52" :placeholder="t('pages.mrpUsage.searchPlaceholder')" />
          </div>
          <el-table :data="filteredColor" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
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
            <el-table-column v-if="canUpdate" :label="t('common.actions')" width="112" align="center" fixed="right">
              <template #default="{ row }">
                <AdminTableActions
                  :show-edit="!!row.stok_out_id"
                  :show-delete="!!row.stok_out_id"
                  @edit="openUsageEdit(row, 'color')"
                  @delete="deleteUsage(row, 'color')"
                />
              </template>
            </el-table-column>
          </el-table>
          <div class="mt-3 flex justify-end">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next"
              background
              small
              @current-change="reload"
              @size-change="() => { page = 1; reload() }"
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.mrpUsage.rp')" name="rp">
        <div v-if="canCreate" class="admin-inner-card mb-4">
          <div class="admin-inner-card__body">
            <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpUsage.rpFormTitle') }}</h3>
          <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpUsage.rpHint') }}</p>
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
          <div v-if="rpInfo" class="mrp-usage-meta">
            <div class="mrp-usage-meta__item">
              <span class="mrp-usage-meta__label">{{ t('pages.mrpUsage.rp') }}</span>
              <span>{{ dash(rpInfo.kode_rp) }}</span>
            </div>
            <div class="mrp-usage-meta__item">
              <span class="mrp-usage-meta__label">{{ t('common.name') }}</span>
              <span>{{ dash(rpInfo.nama_jenis) }}</span>
            </div>
            <div class="mrp-usage-meta__item">
              <span class="mrp-usage-meta__label">{{ t('pages.mrpUsage.satuan') }}</span>
              <span>{{ dash(rpInfo.satuan) }}</span>
            </div>
          </div>
          </div>
        </div>
        <div class="admin-inner-card">
          <div class="admin-inner-card__head">
            <h3 class="admin-inner-card__title">{{ t('pages.mrpUsage.rpHistory') }}</h3>
            <el-input v-model="searchRp" clearable size="small" class="w-52" :placeholder="t('pages.mrpUsage.searchPlaceholder')" />
          </div>
          <el-table :data="filteredRp" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
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
            <el-table-column v-if="canUpdate" :label="t('common.actions')" width="112" align="center" fixed="right">
              <template #default="{ row }">
                <AdminTableActions
                  :show-edit="!!row.stok_out_id"
                  :show-delete="!!row.stok_out_id"
                  @edit="openUsageEdit(row, 'rp')"
                  @delete="deleteUsage(row, 'rp')"
                />
              </template>
            </el-table-column>
          </el-table>
          <div class="mt-3 flex justify-end">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next"
              background
              small
              @current-change="reload"
              @size-change="() => { page = 1; reload() }"
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.mrpUsage.material')" name="material">
        <div v-if="canCreate" class="admin-inner-card mb-4">
          <div class="admin-inner-card__body">
            <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpUsage.matFormTitle') }}</h3>
          <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpUsage.matHint') }}</p>
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
          <div v-if="matInfo" class="mrp-usage-meta">
            <div class="mrp-usage-meta__item">
              <span class="mrp-usage-meta__label">{{ t('pages.mrpUsage.kode') }}</span>
              <span>{{ dash(matInfo.kode_material) }}</span>
            </div>
            <div class="mrp-usage-meta__item">
              <span class="mrp-usage-meta__label">{{ t('common.name') }}</span>
              <span>{{ dash(matInfo.nama_material) }}</span>
            </div>
            <div class="mrp-usage-meta__item">
              <span class="mrp-usage-meta__label">{{ t('pages.mrpUsage.satuan') }}</span>
              <span>{{ dash(matInfo.satuan) }}</span>
            </div>
          </div>
          </div>
        </div>
        <div class="admin-inner-card">
          <div class="admin-inner-card__head">
            <h3 class="admin-inner-card__title">{{ t('pages.mrpUsage.matHistory') }}</h3>
            <el-input v-model="searchMat" clearable size="small" class="w-52" :placeholder="t('pages.mrpUsage.searchPlaceholder')" />
          </div>
          <el-table :data="filteredMat" v-loading="loading" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
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
            <el-table-column v-if="canUpdate" :label="t('common.actions')" width="112" align="center" fixed="right">
              <template #default="{ row }">
                <AdminTableActions
                  :show-edit="!!row.stok_out_id"
                  :show-delete="!!row.stok_out_id"
                  @edit="openUsageEdit(row, 'material')"
                  @delete="deleteUsage(row, 'material')"
                />
              </template>
            </el-table-column>
          </el-table>
          <div class="mt-3 flex justify-end">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :total="total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next"
              background
              small
              @current-change="reload"
              @size-change="() => { page = 1; reload() }"
            />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      v-model="usageEditOpen"
      :title="t('pages.mrpUsage.editTitle')"
      width="420px"
      destroy-on-close
      append-to-body
    >
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpUsage.editHint') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpUsage.qty')" required>
          <el-input v-model="usageEditQty" type="number" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="usageEditOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="usageSaving" @click="saveUsageEdit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { can } from '../../../security/permissions'
import {
  mrpStokKimia,
  mrpStokMaterialLain,
  mrpStokRp,
  mrpUsageColor,
  mrpUsageColorCreate,
  mrpUsageColorDelete,
  mrpUsageColorScanLot,
  mrpUsageColorUpdate,
  mrpUsageMaterial,
  mrpUsageMaterialCreate,
  mrpUsageMaterialDelete,
  mrpUsageMaterialScan,
  mrpUsageMaterialUpdate,
  mrpUsageRp,
  mrpUsageRpCreate,
  mrpUsageRpDelete,
  mrpUsageRpScan,
  mrpUsageRpUpdate,
} from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const tab = ref('color')
const loading = ref(false)
const saving = ref(false)
const scanning = ref(false)
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const usageEditOpen = ref(false)
const usageSaving = ref(false)
const usageEditKind = ref('color')
const usageEditId = ref(null)
const usageEditQty = ref('')

function usageApiError(e) {
  const raw = e?.message || String(e)
  try {
    const body = JSON.parse(raw)
    if (body?.detail) return String(body.detail)
  } catch {
    /* teks biasa */
  }
  return raw
}

function openUsageEdit(row, kind) {
  if (!row.stok_out_id) {
    ElMessage.warning(t('pages.mrpUsage.noTrace'))
    return
  }
  usageEditKind.value = kind
  usageEditId.value = row.id
  usageEditQty.value = row.qty_digunakan ?? row.qty_used ?? ''
  usageEditOpen.value = true
}

async function saveUsageEdit() {
  const id = usageEditId.value
  const body = { qty: usageEditQty.value }
  const call = {
    color: () => mrpUsageColorUpdate(id, body),
    rp: () => mrpUsageRpUpdate(id, body),
    material: () => mrpUsageMaterialUpdate(id, body),
  }[usageEditKind.value]
  usageSaving.value = true
  try {
    await call()
    ElMessage.success(t('pages.mrpUsage.editOk'))
    usageEditOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(usageApiError(e))
  } finally {
    usageSaving.value = false
  }
}

async function deleteUsage(row, kind) {
  if (!row.stok_out_id) {
    ElMessage.warning(t('pages.mrpUsage.noTrace'))
    return
  }
  try {
    await ElMessageBox.confirm(t('pages.mrpUsage.deleteConfirm'), { type: 'warning' })
  } catch {
    return
  }
  const call = {
    color: () => mrpUsageColorDelete(row.id),
    rp: () => mrpUsageRpDelete(row.id),
    material: () => mrpUsageMaterialDelete(row.id),
  }[kind]
  try {
    await call()
    ElMessage.success(t('pages.mrpUsage.deleteOk'))
    await reload()
  } catch (e) {
    ElMessage.error(usageApiError(e))
  }
}

const colorRows = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('date_created')
const sortDir = ref('desc')
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

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'date_created'
  sortDir.value = mapped.sortDir || 'desc'
  page.value = 1
  reload()
}

async function reload() {
  loading.value = true
  try {
    const pageParams = buildPageParams({
      page: page.value,
      pageSize: pageSize.value,
      sortBy: sortBy.value,
      sortDir: sortDir.value,
    })
    if (tab.value === 'color') {
      const [d, stok] = await Promise.all([mrpUsageColor(pageParams), mrpStokKimia({ page: 1, page_size: 100 })])
      const pageData = normalizePageResult(d, { page: page.value, pageSize: pageSize.value })
      colorRows.value = pageData.items.length ? pageData.items : (d.usage_list || [])
      total.value = pageData.total || colorRows.value.length
      colorWip.value = d.wip_list || []
      kimiaLots.value = stok.stok_in || stok.items || []
    } else if (tab.value === 'rp') {
      const [d, stok] = await Promise.all([mrpUsageRp(pageParams), mrpStokRp({ page: 1, page_size: 100 })])
      const pageData = normalizePageResult(d, { page: page.value, pageSize: pageSize.value })
      rpRows.value = pageData.items.length ? pageData.items : (d.usage_list || [])
      total.value = pageData.total || rpRows.value.length
      rpWip.value = d.wip_list || []
      rpLots.value = stok.stok_in || stok.items || []
    } else {
      const [d, stok] = await Promise.all([mrpUsageMaterial(pageParams), mrpStokMaterialLain({ page: 1, page_size: 100 })])
      const pageData = normalizePageResult(d, { page: page.value, pageSize: pageSize.value })
      matRows.value = pageData.items.length ? pageData.items : (d.usage_list || [])
      total.value = pageData.total || matRows.value.length
      matWip.value = d.wip_list || []
      matLots.value = stok.stok_in || stok.items || []
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
.w-24 {
  width: 6rem;
}
.w-28 {
  width: 7rem;
}
.w-52 {
  width: 13rem;
}
.max-w-xs {
  max-width: 16rem;
}
.max-w-sm {
  max-width: 24rem;
}
.mrp-usage-meta {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.55rem;
}
.mrp-usage-meta__item {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.55rem 0.7rem;
  font-size: 0.875rem;
}
.mrp-usage-meta__label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.15rem;
}
@media (max-width: 900px) {
  .mrp-usage-meta {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
