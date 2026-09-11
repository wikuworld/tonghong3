<template>
  <AdminSection :title="t('pages.mrpLab.title')" :subtitle="t('pages.mrpLab.subtitle')">
    <template #actions>
      <el-input
        v-model="search"
        clearable
        class="mrp-toolbar-search"
        :placeholder="t('pages.mrpLab.searchPlaceholder')"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpLab.listSectionTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.mrpLab.listSubtitle') }}</p>
        </div>
      </div>
      <div class="mkt-section-body">
        <p class="admin-scroll-hint">{{ t('pages.mrpLab.scrollHint') }}</p>
        <div class="admin-table-scroll">
      <el-table
        :data="filteredLots"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        row-key="kode_lot_warna"
        max-height="62vh"
        :empty-text="t('pages.mrpLab.tableEmpty')"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="mrp-lab-expand">
              <p class="text-xs text-slate-500 mb-2">{{ t('pages.mrpLab.items') }}</p>
              <el-table :data="row.items || []" border stripe size="small" class="admin-table" :empty-text="t('pages.mrpLab.tableEmpty')">
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
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="kode_lot_warna" :label="t('pages.mrpLab.kodeLot')" min-width="130" show-overflow-tooltip />
        <el-table-column prop="nama_lot_warna" :label="t('pages.mrpLab.namaLot')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpLab.rpi')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.kode_rencana_item) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpLab.wip')" min-width="120" show-overflow-tooltip>
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
      </el-table>
        </div>
      </div>
    </div>

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
              :label="`${k.kode_kimia} · ${k.nama_kimia || ''}`"
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
          <el-input v-model="row.remarks" :placeholder="t('pages.mrpLab.remarks')" class="mrp-lab-item-row__remarks" />
          <el-button link type="danger" :disabled="form.items.length <= 1" @click="form.items.splice(idx, 1)">
            {{ t('common.delete') }}
          </el-button>
        </div>
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
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import { can } from '../../../security/permissions'
import { mrpCreateLab, mrpLabOptions, mrpListLab } from '../../../api/client'

const { t } = useI18n()
const loading = ref(false)
const optionsLoading = ref(false)
const saving = ref(false)
const createOpen = ref(false)
const onlyWithProses = ref(true)
const search = ref('')
const lots = ref([])
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const options = reactive({ rencana_items: [], kimia_list: [], reseps: [] })
const form = reactive({
  nama_lot_warna: '',
  rencana_item_id: null,
  items: [],
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

function emptyRow() {
  return { kode_kimia: '', resep: '', qty: '', satuan: 'kg', remarks: '' }
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

function onKimiaChange(row, kode) {
  const hit = options.kimia_list.find((k) => k.kode_kimia === kode)
  if (hit?.satuan) row.satuan = hit.satuan
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpListLab()
    lots.value = data.lots || []
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
    ElMessage.success(
      res?.kode_lot_warna
        ? `${t('common.saved')}: ${res.kode_lot_warna}`
        : t('common.saved'),
    )
    createOpen.value = false
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
  grid-template-columns: minmax(0, 1.35fr) minmax(0, 0.9fr) 88px 72px minmax(0, 1fr) auto;
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
@media (max-width: 860px) {
  .mrp-lab-item-head {
    display: none;
  }
  .mrp-lab-item-row {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
