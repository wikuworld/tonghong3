<template>
  <AdminSection :title="t('pages.mrpLab.title')" :subtitle="t('pages.mrpLab.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" @click="openSisa">{{ t('pages.mrpLab.sisaBtn') }}</el-button>
      <el-button v-if="canCreate && tab === 'utama'" type="primary" :icon="Plus" @click="openCreate">
        {{ t('common.create') }}
      </el-button>
    </template>

    <el-tabs v-model="tab" class="admin-tabs mb-4" @tab-change="onTabChange">
      <el-tab-pane :label="t('pages.mrpLab.tabUtama')" name="utama" />
      <el-tab-pane :label="t('pages.mrpLab.tabTerpakai')" name="terpakai" />
      <el-tab-pane :label="t('pages.mrpLab.tabSisa')" name="sisa" />
    </el-tabs>

    <div class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <el-input
          v-model="search"
          clearable
          :placeholder="t('pages.mrpLab.searchPlaceholder')"
          class="max-w-md"
        />
      </div>
    </div>

    <div class="admin-inner-card">
      <el-table
        v-if="tab !== 'sisa'"
        :data="filteredLots"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        row-key="kode_lot_warna"
        max-height="62vh"
        :empty-text="t('common.tableEmpty')"
        @sort-change="onSortChange"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="mrp-lab-expand">
              <p class="text-xs text-slate-500 mb-2">{{ t('pages.mrpLab.items') }}</p>
              <el-table :data="row.items || []" border size="small" :empty-text="t('common.tableEmpty')">
                <el-table-column type="index" width="48" :label="t('common.noLabel')" align="center" />
                <el-table-column prop="kode_kimia" :label="t('pages.mrpLab.kimia')" min-width="110" show-overflow-tooltip />
                <el-table-column prop="nama_kimia" :label="t('common.name')" min-width="140" show-overflow-tooltip />
                <el-table-column prop="resep" :label="t('pages.mrpLab.resep')" width="110" show-overflow-tooltip />
                <el-table-column :label="t('pages.mrpLab.qty')" width="90" align="right">
                  <template #default="{ row: item }">{{ formatQty(item.qty) }}</template>
                </el-table-column>
                <el-table-column prop="satuan" :label="t('pages.mrpLab.satuan')" width="70" />
                <el-table-column :label="t('pages.mrpLab.remarks')" min-width="140" show-overflow-tooltip>
                  <template #default="{ row: item }">{{ dash(item.remarks) }}</template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="kode_lot_warna" :label="t('pages.mrpLab.kodeLot')" min-width="130" show-overflow-tooltip sortable="custom" />
        <el-table-column prop="nama_lot_warna" :label="t('pages.mrpLab.namaLot')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpLab.rpi')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.kode_rencana_item) }}</template>
        </el-table-column>
        <el-table-column label="WIP" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.kode_lot_wip) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.customer')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.nama_customer) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpLab.kimiaCount')" width="90" align="right">
          <template #default="{ row }">{{ row.jml_kimia ?? row.items?.length ?? 0 }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpLab.totalQty')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.total_qty) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="labStatusType(row.status)" size="small" effect="plain">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="120">
          <template #default="{ row }">{{ formatDate(row.date_created || row.tanggal_rencana) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="88" align="center" fixed="right">
          <template #default="{ row }">
            <el-tooltip :content="t('pages.mrpLab.printQr')" placement="top">
              <el-button
                link
                type="primary"
                :icon="Printer"
                :aria-label="t('pages.mrpLab.printQr')"
                @click="printQr(row)"
              />
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>

      <el-table
        v-else
        :data="filteredSisa"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        row-key="id"
        max-height="62vh"
        :empty-text="t('pages.mrpLab.sisaEmpty')"
        @sort-change="onSortChange"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="kode_lot_warna" :label="t('pages.mrpLab.lotNo')" min-width="140" show-overflow-tooltip sortable="custom" />
        <el-table-column prop="nama_lot_warna" :label="t('pages.mrpLab.namaLot')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpLab.qtySisa')" width="110" align="right" sortable="custom">
          <template #default="{ row }">{{ formatQty(row.qty_sisa) }}</template>
        </el-table-column>
        <el-table-column label="WIP" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.kode_lot_wip) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.color')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.color) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.notes')" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.notes) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="120">
          <template #default="{ row }">{{ formatDate(row.date_created) }}</template>
        </el-table-column>
        <el-table-column v-if="canUpdate" :label="t('common.actions')" width="110" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              type="warning"
              plain
              :loading="mixingId === row.id"
              @click="markMixed(row)"
            >
              {{ t('pages.mrpLab.mixedBtn') }}
            </el-button>
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

    <el-dialog
      v-model="sisaOpen"
      :title="t('pages.mrpLab.sisaTitle')"
      width="480px"
      destroy-on-close
      append-to-body
    >
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpLab.sisaHint') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpLab.lotNo')" required>
          <el-select
            v-model="sisaForm.kode_lot_warna"
            filterable
            clearable
            class="w-full"
            :placeholder="t('pages.mrpLab.lotNoPlaceholder')"
            :loading="sisaLotsLoading"
            :disabled="!sisaLotOptions.length && !sisaLotsLoading"
            @keyup.enter="submitSisa"
          >
            <el-option
              v-for="lot in sisaLotOptions"
              :key="lot.kode_lot_warna"
              :value="lot.kode_lot_warna"
              :label="sisaLotOptionLabel(lot)"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.mrpLab.qtySisa')" required>
          <el-input
            v-model="sisaForm.qty_sisa"
            type="number"
            :placeholder="t('pages.mrpLab.qtySisaPlaceholder')"
            @keyup.enter="submitSisa"
          />
        </el-form-item>
        <el-form-item :label="t('common.notes')">
          <el-input v-model="sisaForm.notes" :placeholder="t('common.notes')" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="sisaOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submitSisa">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="createOpen"
      :title="t('pages.mrpLab.createTitle')"
      width="880px"
      destroy-on-close
      append-to-body
    >
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpLab.createHint') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpLab.namaLot')" required>
          <el-input v-model="form.nama_lot_warna" :placeholder="t('pages.mrpLab.namaLotPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpLab.linkRpi')">
          <p class="text-sm text-slate-500 mb-2">{{ t('pages.mrpLab.linkRpiHint') }}</p>
          <el-checkbox v-model="onlyWithProses" class="mb-2" @change="onFilterProsesChange">
            {{ t('pages.mrpLab.onlyWithProses') }}
          </el-checkbox>
          <el-select
            v-model="form.rencana_item_id"
            clearable
            filterable
            class="w-full"
            :placeholder="t('pages.mrpLab.linkRpiPlaceholder')"
            :loading="optionsLoading"
          >
            <el-option
              v-for="it in options.rencana_items"
              :key="it.id"
              :label="rpiOptionLabel(it)"
              :value="it.id"
              :disabled="onlyWithProses && !it.has_proses"
            />
          </el-select>
        </el-form-item>

        <div class="mrp-lab-items-head">
          <strong>{{ t('pages.mrpLab.items') }}</strong>
          <el-button size="small" @click="addRow">{{ t('common.add') }}</el-button>
        </div>
        <div v-if="!options.kimia_list.length" class="text-sm text-amber-700 mb-2">
          {{ t('pages.mrpLab.noKimiaMaster') }}
        </div>
        <div v-if="!form.items.length" class="text-sm text-slate-500 mb-2">{{ t('pages.mrpLab.itemsEmpty') }}</div>

        <div class="mrp-lab-item-head text-xs text-slate-500 mb-1">
          <span>{{ t('pages.mrpLab.kimia') }}</span>
          <span>{{ t('pages.mrpLab.resep') }}</span>
          <span>{{ t('pages.mrpLab.qty') }}</span>
          <span>{{ t('pages.mrpLab.satuan') }}</span>
          <span>{{ t('pages.mrpLab.stokLapangan') }}</span>
          <span>{{ t('pages.mrpLab.remarks') }}</span>
          <span />
        </div>
        <div v-for="(row, idx) in form.items" :key="idx" class="mrp-lab-item-row">
          <el-select
            v-model="row.kode_kimia"
            filterable
            allow-create
            default-first-option
            :placeholder="t('pages.mrpLab.kimia')"
            class="mrp-lab-item-row__kimia"
            @change="(v) => onKimiaChange(row, v)"
          >
            <el-option
              v-for="k in options.kimia_list"
              :key="k.kode_kimia"
              :label="kimiaOptionLabel(k)"
              :value="k.kode_kimia"
            />
          </el-select>
          <el-select
            v-model="row.resep"
            filterable
            allow-create
            clearable
            default-first-option
            :placeholder="t('pages.mrpLab.resep')"
            class="mrp-lab-item-row__resep"
          >
            <el-option v-for="r in options.reseps" :key="r" :label="r" :value="r" />
          </el-select>
          <el-input v-model="row.qty" type="number" :placeholder="t('pages.mrpLab.qty')" class="mrp-lab-item-row__qty" />
          <el-input v-model="row.satuan" :placeholder="t('pages.mrpLab.satuan')" class="mrp-lab-item-row__sat" />
          <span
            class="mrp-lab-item-row__stok text-xs"
            :class="stokLapanganClass(row)"
          >{{ formatQty(row.stok_lapangan) }}</span>
          <el-input v-model="row.remarks" :placeholder="t('pages.mrpLab.remarks')" class="mrp-lab-item-row__remarks" />
          <el-button link type="danger" :disabled="form.items.length <= 1" @click="form.items.splice(idx, 1)">
            {{ t('common.delete') }}
          </el-button>
        </div>
        <p class="text-xs text-slate-500 mt-2 mb-0">{{ t('pages.mrpLab.stokLapanganHint') }}</p>
      </el-form>
      <template #footer>
        <el-button @click="createOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Printer, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import { mrpCreateLab, mrpCreateLabSisa, mrpLabOptions, mrpListLab, mrpMixedLabSisa } from '../../../api/client'
import { printLabLotQr } from '../../../utils/mrpLabQrPrint'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const optionsLoading = ref(false)
const saving = ref(false)
const mixingId = ref(null)
const createOpen = ref(false)
const sisaOpen = ref(false)
const sisaLotsLoading = ref(false)
const sisaLotOptions = ref([])
const onlyWithProses = ref(true)
const search = ref('')
const tab = ref('utama')
const lots = ref([])
const sisaRows = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('date_created')
const sortDir = ref('desc')
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const options = reactive({ rencana_items: [], kimia_list: [], reseps: [] })
const form = reactive({
  nama_lot_warna: '',
  rencana_item_id: null,
  items: [],
})
const sisaForm = reactive({
  kode_lot_warna: '',
  qty_sisa: '',
  notes: '',
})

const filteredLots = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return lots.value
  return lots.value.filter((lot) => {
    const blob = [
      lot.kode_lot_warna,
      lot.nama_lot_warna,
      lot.kode_rencana_item,
      lot.kode_lot_wip,
      lot.nama_customer,
      lot.status,
      ...(lot.items || []).flatMap((it) => [it.kode_kimia, it.nama_kimia, it.resep]),
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return blob.includes(q)
  })
})

const filteredSisa = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return sisaRows.value
  return sisaRows.value.filter((row) => {
    const blob = [
      row.kode_lot_warna,
      row.nama_lot_warna,
      row.kode_lot_wip,
      row.color,
      row.notes,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return blob.includes(q)
  })
})

function emptyRow() {
  return { kode_kimia: '', resep: '', qty: '', satuan: 'kg', remarks: '', stok_lapangan: null }
}

function addRow() {
  form.items.push(emptyRow())
}

function dash(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function formatDate(v) {
  if (!v) return '—'
  const s = String(v)
  return s.slice(0, 10)
}

function labStatusType(status) {
  const s = String(status || '')
  if (s === 'active') return 'success'
  if (s === 'used') return 'info'
  if (s === 'expired') return 'danger'
  return ''
}

function statusLabel(status) {
  const s = String(status || '')
  const map = {
    active: t('pages.mrpLab.statusActive'),
    used: t('pages.mrpLab.statusUsed'),
    expired: t('pages.mrpLab.statusExpired'),
  }
  return map[s] || s || '—'
}

function rpiOptionLabel(it) {
  const st = it.persiapan_status || '—'
  const wip = it.kode_lot_wip ? ` · ${it.kode_lot_wip}` : ''
  const prep = it.kode_proses ? ` · ${it.kode_proses}/${st}` : ` · ${t('pages.mrpLab.noProses')}`
  return `${it.kode_rencana_item} · ${it.nama_customer || ''} · ${it.color || ''}${wip}${prep}`
}

function kimiaOptionLabel(k) {
  const stok = Number(k.stok_lapangan)
  const stokTxt = Number.isFinite(stok)
    ? ` · ${t('pages.mrpLab.stokLapanganShort', { qty: formatQty(stok) })}`
    : ''
  return `${k.kode_kimia} · ${k.nama_kimia || ''}${stokTxt}`
}

function stokLapanganClass(row) {
  const avail = Number(row.stok_lapangan)
  const need = Number(row.qty)
  if (!Number.isFinite(avail)) return 'text-slate-400'
  if (Number.isFinite(need) && need > avail) return 'text-amber-700 font-medium'
  return 'text-slate-600'
}

function onKimiaChange(row, kode) {
  const hit = options.kimia_list.find((k) => k.kode_kimia === kode)
  if (hit?.satuan) row.satuan = hit.satuan
  row.stok_lapangan = hit?.stok_lapangan ?? 0
}

function onTabChange() {
  page.value = 1
  search.value = ''
  reload()
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
    const data = await mrpListLab(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
        extra: { tab: tab.value },
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    const items = pageData.items.length ? pageData.items : (data.lots || [])
    total.value = pageData.total || items.length
    if (tab.value === 'sisa') {
      sisaRows.value = items
      lots.value = []
    } else {
      lots.value = items
      sisaRows.value = []
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function reloadOptions() {
  optionsLoading.value = true
  try {
    const opt = await mrpLabOptions({
      only_with_proses: onlyWithProses.value ? 1 : 0,
    })
    Object.assign(options, {
      rencana_items: opt.rencana_items || [],
      kimia_list: opt.kimia_list || [],
      reseps: opt.reseps || [],
    })
    if (
      form.rencana_item_id &&
      !options.rencana_items.some((it) => it.id === form.rencana_item_id)
    ) {
      form.rencana_item_id = null
    }
  } finally {
    optionsLoading.value = false
  }
}

async function onFilterProsesChange() {
  try {
    await reloadOptions()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

function sisaLotOptionLabel(lot) {
  const parts = [
    lot.kode_lot_warna,
    lot.nama_lot_warna,
    lot.nama_customer,
    lot.kode_lot_wip ? `WIP ${lot.kode_lot_wip}` : '',
  ].filter(Boolean)
  return parts.join(' · ')
}

async function loadLabTab(tabName) {
  return mrpListLab(
    buildPageParams({
      page: 1,
      pageSize: 200,
      sortBy: 'kode_lot_warna',
      sortDir: 'asc',
      extra: { tab: tabName },
    }),
  )
}

async function openSisa() {
  sisaForm.kode_lot_warna = ''
  sisaForm.qty_sisa = ''
  sisaForm.notes = ''
  sisaLotOptions.value = []
  sisaOpen.value = true
  sisaLotsLoading.value = true
  try {
    const [utama, terpakai, sisa] = await Promise.all([
      loadLabTab('utama'),
      loadLabTab('terpakai'),
      loadLabTab('sisa'),
    ])
    const taken = new Set(
      (sisa.lots || sisa.items || []).map((row) => row.kode_lot_warna).filter(Boolean),
    )
    const merged = []
    const seen = new Set()
    for (const lot of [...(utama.lots || utama.items || []), ...(terpakai.lots || terpakai.items || [])]) {
      const kode = lot.kode_lot_warna
      if (!kode || seen.has(kode) || taken.has(kode)) continue
      seen.add(kode)
      merged.push(lot)
    }
    sisaLotOptions.value = merged
    if (!sisaLotOptions.value.length) {
      ElMessage.warning(t('pages.mrpLab.sisaLotEmpty'))
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
    sisaOpen.value = false
  } finally {
    sisaLotsLoading.value = false
  }
}

async function markMixed(row) {
  const lot = row.kode_lot_warna || ''
  try {
    await ElMessageBox.confirm(t('pages.mrpLab.mixedConfirm', { lot }), {
      type: 'warning',
      confirmButtonText: t('pages.mrpLab.mixedBtn'),
    })
  } catch {
    return
  }
  mixingId.value = row.id
  try {
    await mrpMixedLabSisa(row.id)
    ElMessage.success(t('pages.mrpLab.mixedDone', { lot }))
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    mixingId.value = null
  }
}

async function openCreate() {
  form.nama_lot_warna = ''
  form.rencana_item_id = null
  form.items = [emptyRow()]
  onlyWithProses.value = true
  createOpen.value = true
  try {
    await reloadOptions()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

async function printQr(row) {
  try {
    await printLabLotQr(row, t)
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

async function submitSisa() {
  const kode = sisaForm.kode_lot_warna.trim()
  if (!kode) {
    ElMessage.warning(t('pages.mrpLab.lotNoRequired'))
    return
  }
  const qty = Number(sisaForm.qty_sisa)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpLab.qtyInvalid'))
    return
  }
  saving.value = true
  try {
    const res = await mrpCreateLabSisa({
      kode_lot_warna: kode,
      qty_sisa: qty,
      notes: sisaForm.notes.trim() || null,
    })
    ElMessage.success(
      t('pages.mrpLab.sisaSaved', {
        lot: res?.item?.kode_lot_warna || kode,
        qty: formatQty(res?.item?.qty_sisa ?? qty),
      }),
    )
    sisaOpen.value = false
    tab.value = 'sisa'
    page.value = 1
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

async function submit() {
  if (!form.nama_lot_warna?.trim()) {
    ElMessage.warning(t('pages.mrpLab.namaLot'))
    return
  }
  const items = form.items.filter((r) => String(r.kode_kimia || '').trim())
  if (!items.length) {
    ElMessage.warning(t('pages.mrpLab.itemsEmpty'))
    return
  }
  for (const r of items) {
    const qty = Number(r.qty)
    if (!(qty > 0)) {
      ElMessage.warning(`${t('pages.mrpLab.qtyInvalid')}: ${r.kode_kimia}`)
      return
    }
    const avail = Number(r.stok_lapangan)
    if (Number.isFinite(avail) && qty > avail) {
      ElMessage.warning(
        t('pages.mrpLab.stokLapanganKurang', {
          kode: r.kode_kimia,
          need: formatQty(qty),
          avail: formatQty(avail),
        }),
      )
      return
    }
  }
  if (form.rencana_item_id) {
    const hit = options.rencana_items.find((it) => it.id === form.rencana_item_id)
    if (hit && !hit.has_proses) {
      ElMessage.warning(t('pages.mrpLab.prosesRequired'))
      return
    }
  }
  saving.value = true
  try {
    const res = await mrpCreateLab({
      nama_lot_warna: form.nama_lot_warna,
      rencana_item_id: form.rencana_item_id || null,
      items: items.map((r) => ({
        kode_kimia: r.kode_kimia,
        resep: r.resep,
        qty: Number(r.qty),
        satuan: r.satuan || 'kg',
        remarks: r.remarks,
      })),
    })
    if (res?.kode_lot_warna && res?.stok_deducted) {
      ElMessage.success(
        t('pages.mrpLab.savedWithStokOut', { kode: res.kode_lot_warna, n: (res.stok_outs || []).length }),
      )
    } else {
      ElMessage.success(
        res?.kode_lot_warna
          ? `${t('common.saved')}: ${res.kode_lot_warna}`
          : t('common.saved'),
      )
    }
    createOpen.value = false
    tab.value = 'utama'
    page.value = 1
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

onMounted(reload)
</script>

<style scoped>
.max-w-md {
  max-width: 28rem;
}
.mrp-lab-expand {
  padding: 0.35rem 0.5rem 0.75rem;
}
.mrp-lab-items-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0.5rem 0 0.65rem;
}
.mrp-lab-item-head,
.mrp-lab-item-row {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(0, 0.9fr) 88px 72px 72px minmax(0, 1fr) auto;
  gap: 0.45rem;
  align-items: center;
}
.mrp-lab-item-head {
  padding: 0 0.55rem;
}
.mrp-lab-item-row {
  margin-bottom: 0.5rem;
  padding: 0.55rem;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  background: var(--el-fill-color-blank);
}
.mrp-lab-item-row__kimia,
.mrp-lab-item-row__resep,
.mrp-lab-item-row__qty,
.mrp-lab-item-row__sat,
.mrp-lab-item-row__remarks {
  width: 100%;
}
.mrp-lab-item-row__stok {
  text-align: right;
}
@media (max-width: 860px) {
  .mrp-lab-item-head {
    display: none;
  }
  .mrp-lab-item-row {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
