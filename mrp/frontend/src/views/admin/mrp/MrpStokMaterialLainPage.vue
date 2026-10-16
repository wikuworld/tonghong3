<template>
  <AdminSection :title="t('pages.mrpStokMaterialLain.title')" :subtitle="t('pages.mrpStokMaterialLain.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div v-if="canCreate" class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokMaterialLain.inTitle') }}</h3>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpStokMaterialLain.inHint') }}</p>
      <div class="flex flex-wrap gap-2 items-center">
        <el-select
          v-model="inForm.material_id"
          filterable
          clearable
          :placeholder="t('pages.mrpStokMaterialLain.material')"
          class="max-w-sm"
        >
          <el-option
            v-for="r in materialList"
            :key="r.id"
            :label="`${r.kode_material} — ${r.nama_material}${r.satuan ? ` (${r.satuan})` : ''}`"
            :value="r.id"
          />
        </el-select>
        <el-input
          v-model="inForm.qty"
          type="number"
          :placeholder="t('pages.mrpStokMaterialLain.qty')"
          class="w-28"
          @keyup.enter="doIn"
        />
        <el-date-picker v-model="inForm.tanggal" type="date" value-format="YYYY-MM-DD" />
        <el-button type="primary" :loading="saving" @click="doIn">{{ t('pages.mrpStokMaterialLain.inBtn') }}</el-button>
      </div>
      </div>
    </div>

    <div v-if="canUpdate" class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokMaterialLain.outTitle') }}</h3>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpStokMaterialLain.outHint') }}</p>
      <div class="flex flex-wrap gap-2 items-center">
        <el-select
          v-model="outForm.stok_in_id"
          filterable
          clearable
          :placeholder="t('pages.mrpStokMaterialLain.lot')"
          class="max-w-md"
          @change="onLotPick"
        >
          <el-option
            v-for="s in activeLots"
            :key="s.id"
            :label="lotLabel(s)"
            :value="s.id"
          />
        </el-select>
        <el-input
          v-model="outForm.qty"
          type="number"
          :placeholder="t('pages.mrpStokMaterialLain.qty')"
          class="w-28"
          @keyup.enter="doOut"
        />
        <el-input v-model="outForm.kode_wip" :placeholder="t('pages.mrpStokMaterialLain.wip')" class="max-w-xs" />
        <el-button type="danger" :loading="saving" @click="doOut">{{ t('pages.mrpStokMaterialLain.outBtn') }}</el-button>
      </div>
      <p v-if="outForm.stok != null" class="text-xs text-slate-500 mt-2 mb-0">
        {{ t('pages.mrpStokMaterialLain.sisaHint', { qty: formatQty(outForm.stok), unit: outForm.satuan || 'pcs' }) }}
      </p>
      </div>
    </div>

    <div class="admin-inner-card mb-4">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpStokMaterialLain.stokIn') }}</h3>
          <p class="admin-inner-card__sub">
            {{ t('pages.mrpStokMaterialLain.statsIn', { lots: stats.lots, qty: formatQty(stats.qty_sisa) }) }}
          </p>
        </div>
        <el-input
          v-model="searchIn"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpStokMaterialLain.searchPlaceholder')"
        />
      </div>
      <el-table
        :data="filteredIn"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('common.tableEmpty')"
        @sort-change="onSortChange"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_internal" sortable="custom" :label="t('pages.mrpStokMaterialLain.bc')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="kode_material" :label="t('pages.mrpStokMaterialLain.kode')" width="120" show-overflow-tooltip />
        <el-table-column prop="nama_material" :label="t('common.name')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpStokMaterialLain.sisa')" width="110" align="right">
          <template #default="{ row }">
            {{ formatQty(row.qty_sisa) }}
            <span class="text-slate-400 text-xs">{{ dash(row.satuan) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokMaterialLain.qtyIn')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="120">
          <template #default="{ row }">{{ formatDate(row.tanggal_in) }}</template>
        </el-table-column>
        <el-table-column v-if="canUpdate" :label="t('common.actions')" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions
              :show-edit="true"
              :show-delete="true"
              :more-items="Number(row.qty_sisa) > 0 ? [{ command: 'out', label: 'OUT', icon: Upload }] : []"
              @edit="openEditLot(row)"
              @delete="deleteLot(row)"
              @more="(cmd) => cmd === 'out' && outFromRow(row)"
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

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <h3 class="admin-inner-card__title">{{ t('pages.mrpStokMaterialLain.stokOut') }}</h3>
        <el-input
          v-model="searchOut"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpStokMaterialLain.searchOutPlaceholder')"
        />
      </div>
      <el-table :data="filteredOut" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="nama_material" :label="t('common.name')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpStokMaterialLain.qty')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokMaterialLain.wip')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.kode_wip) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.notes')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.keterangan) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="120">
          <template #default="{ row }">{{ formatDate(row.tanggal) }}</template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="editOpen"
      :title="t('pages.mrpStokMaterialLain.editTitle')"
      width="480px"
      destroy-on-close
      append-to-body
    >
      <p v-if="editLocked" class="text-sm text-amber-700 mb-3">{{ t('pages.mrpStokMaterialLain.editLocked') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpStokMaterialLain.bc')">
          <el-input :model-value="editForm.kode_internal" disabled />
        </el-form-item>
        <el-form-item :label="t('pages.mrpStokMaterialLain.qty')" required>
          <el-input v-model="editForm.qty" type="number" />
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker v-model="editForm.tanggal" type="date" value-format="YYYY-MM-DD" class="w-full" :disabled="editLocked" />
        </el-form-item>
        <el-form-item label="Satuan">
          <el-input v-model="editForm.satuan" :disabled="editLocked" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="editSaving" @click="saveEditLot">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Upload } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { can } from '../../../security/permissions'
import { mrpStokMaterialLain, mrpStokMaterialLainAction } from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const stokIn = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('tanggal_in')
const sortDir = ref('desc')
const stokOut = ref([])
const materialList = ref([])
const searchIn = ref('')
const searchOut = ref('')
const stats = ref({ lots: 0, qty_sisa: 0, out_rows: 0 })
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const inForm = reactive({
  material_id: null,
  qty: null,
  tanggal: new Date().toISOString().slice(0, 10),
})
const editOpen = ref(false)
const editSaving = ref(false)
const editIssued = ref(0)
const editForm = reactive({
  id: null,
  kode_internal: '',
  qty: '',
  tanggal: '',
  satuan: '',
})
const editLocked = computed(() => editIssued.value > 0.001)
const outForm = reactive({
  stok_in_id: null,
  qty: null,
  stok: null,
  satuan: '',
  kode_wip: '',
  tanggal: new Date().toISOString().slice(0, 10),
})

const activeLots = computed(() =>
  (stokIn.value || []).filter((s) => Number(s.qty_sisa) > 0),
)

const filteredIn = computed(() => {
  const q = searchIn.value.trim().toLowerCase()
  if (!q) return stokIn.value
  return stokIn.value.filter((r) =>
    [r.kode_internal, r.kode_material, r.nama_material]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

const filteredOut = computed(() => {
  const q = searchOut.value.trim().toLowerCase()
  if (!q) return stokOut.value
  return stokOut.value.filter((r) =>
    [r.nama_material, r.kode_material, r.kode_wip, r.keterangan]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 3 })
}

function formatDate(v) {
  if (!v) return '—'
  return String(v).slice(0, 10)
}

function lotLabel(s) {
  return `${s.kode_internal} · ${s.nama_material} · sisa ${formatQty(s.qty_sisa)} ${s.satuan || ''}`.trim()
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

function onLotPick(id) {
  const s = stokIn.value.find((r) => r.id === id)
  if (!s) {
    outForm.stok = null
    outForm.satuan = ''
    return
  }
  outForm.stok = Number(s.qty_sisa) || 0
  outForm.satuan = s.satuan || 'pcs'
  if (outForm.qty == null || outForm.qty === '') outForm.qty = outForm.stok
}

function outFromRow(row) {
  outForm.stok_in_id = row.id
  onLotPick(row.id)
  outForm.qty = Number(row.qty_sisa) || null
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'tanggal_in'
  sortDir.value = mapped.sortDir || 'desc'
  page.value = 1
  reload()
}

function openEditLot(row) {
  const booked = Number(row.qty)
  const sisa = Number(row.qty_sisa)
  editIssued.value = Number.isFinite(booked) && Number.isFinite(sisa) ? Math.max(0, booked - sisa) : 0
  editForm.id = row.id
  editForm.kode_internal = row.kode_internal || ''
  editForm.qty = row.qty ?? ''
  editForm.tanggal = String(row.tanggal_in || '').slice(0, 10)
  editForm.satuan = row.satuan || ''
  editOpen.value = true
}

function stockApiError(e) {
  const raw = e?.message || String(e)
  try {
    const body = JSON.parse(raw)
    if (body?.detail) return String(body.detail)
  } catch {
    /* teks biasa */
  }
  return raw
}

async function saveEditLot() {
  editSaving.value = true
  try {
    await mrpStokMaterialLainAction({
      action: 'update',
      id: editForm.id,
      qty: editForm.qty,
      tanggal: editForm.tanggal,
      satuan: editForm.satuan,
    })
    ElMessage.success(t('pages.mrpStokMaterialLain.editOk', { kode: editForm.kode_internal }))
    editOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(stockApiError(e))
  } finally {
    editSaving.value = false
  }
}

async function deleteLot(row) {
  try {
    await ElMessageBox.confirm(
      t('pages.mrpStokMaterialLain.deleteConfirm', { kode: row.kode_internal }),
      { type: 'warning' },
    )
  } catch {
    return
  }
  try {
    await mrpStokMaterialLainAction({ action: 'delete', id: row.id })
    ElMessage.success(t('pages.mrpStokMaterialLain.deleteOk', { kode: row.kode_internal }))
    await reload()
  } catch (e) {
    ElMessage.error(stockApiError(e))
  }
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpStokMaterialLain(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    stokIn.value = pageData.items.length ? pageData.items : (data.stok_in || [])
    total.value = pageData.total || stokIn.value.length
    stokOut.value = data.stok_out || []
    materialList.value = data.material_list || []
    stats.value = data.stats || {
      lots: stokIn.value.length,
      qty_sisa: stokIn.value.reduce((a, r) => a + (Number(r.qty_sisa) || 0), 0),
      out_rows: stokOut.value.length,
    }
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    loading.value = false
  }
}

async function doIn() {
  if (!inForm.material_id) {
    ElMessage.warning(t('pages.mrpStokMaterialLain.materialRequired'))
    return
  }
  const qty = Number(inForm.qty)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpStokMaterialLain.qtyInvalid'))
    return
  }
  saving.value = true
  try {
    const res = await mrpStokMaterialLainAction({
      action: 'in',
      material_id: inForm.material_id,
      qty,
      tanggal: inForm.tanggal,
    })
    ElMessage.success(t('pages.mrpStokMaterialLain.inOk', { kode: res?.kode_internal || '' }))
    inForm.material_id = null
    inForm.qty = null
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

async function doOut() {
  if (!outForm.stok_in_id) {
    ElMessage.warning(t('pages.mrpStokMaterialLain.lotRequired'))
    return
  }
  const qty = Number(outForm.qty)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpStokMaterialLain.qtyInvalid'))
    return
  }
  if (outForm.stok != null && qty > Number(outForm.stok)) {
    ElMessage.warning(t('pages.mrpStokMaterialLain.qtyExceed', { sisa: formatQty(outForm.stok) }))
    return
  }
  try {
    await ElMessageBox.confirm(
      t('pages.mrpStokMaterialLain.outConfirm', { qty: formatQty(qty) }),
      t('pages.mrpStokMaterialLain.outBtn'),
      {
        type: 'warning',
        confirmButtonText: t('pages.mrpStokMaterialLain.outBtn'),
        cancelButtonText: t('common.cancel'),
      },
    )
  } catch {
    return
  }
  saving.value = true
  try {
    await mrpStokMaterialLainAction({
      action: 'out',
      stok_in_id: outForm.stok_in_id,
      qty,
      kode_wip: (outForm.kode_wip || '').trim() || null,
      tanggal: outForm.tanggal,
    })
    ElMessage.success(t('common.saved'))
    outForm.stok_in_id = null
    outForm.qty = null
    outForm.stok = null
    outForm.kode_wip = ''
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
    await reload()
  } finally {
    saving.value = false
  }
}

onMounted(reload)
</script>

<style scoped>
.w-28 {
  width: 7rem;
}
.w-56 {
  width: 14rem;
}
.max-w-sm {
  max-width: 24rem;
}
.max-w-md {
  max-width: 28rem;
}
.max-w-xs {
  max-width: 16rem;
}
</style>
