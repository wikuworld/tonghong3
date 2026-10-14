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
      width="920px"
      destroy-on-close
      append-to-body
    >
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpLab.createHint') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpLab.linkRpi')" required>
          <p class="text-sm text-slate-500 mb-2">{{ t('pages.mrpLab.linkRpiHint') }}</p>
          <el-checkbox v-model="onlyWithProses" class="mb-2" @change="onFilterProsesChange">
            {{ t('pages.mrpLab.onlyWithProses') }}
          </el-checkbox>
          <el-select
            v-model="form.rencana_item_id"
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
          <el-button size="small" type="primary" plain :disabled="!form.rencana_item_id" @click="openLotDraft">
            {{ t('common.add') }}
          </el-button>
        </div>
        <p v-if="!form.rencana_item_id" class="text-sm text-slate-500 mb-2">{{ t('pages.mrpLab.rpiPickFirst') }}</p>
        <div v-else-if="!form.colorLots.length" class="text-sm text-slate-500 mb-2">{{ t('pages.mrpLab.colorLotsEmpty') }}</div>

        <el-table
          v-if="form.colorLots.length"
          :data="form.colorLots"
          border
          size="small"
          class="admin-table mb-2"
          :empty-text="t('common.tableEmpty')"
        >
          <el-table-column :label="t('pages.mrpLab.kodeLw')" min-width="160" show-overflow-tooltip>
            <template #default="{ $index }">{{ previewLwCode($index) }}</template>
          </el-table-column>
          <el-table-column prop="nama_lot_warna" :label="t('pages.mrpLab.namaLot')" min-width="140" show-overflow-tooltip />
          <el-table-column :label="t('pages.mrpLab.qtySatuan')" min-width="160" show-overflow-tooltip>
            <template #default="{ row }">{{ formatQtySatuanTotal(row) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpLab.remarks')" min-width="140" show-overflow-tooltip>
            <template #default="{ row }">{{ dash(row.catatan) }}</template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="120" align="center">
            <template #default="{ $index }">
              <AdminTableActions
                show-view
                show-edit
                show-delete
                @view="viewColorLot($index)"
                @edit="editColorLot($index)"
                @delete="removeColorLot($index)"
              />
            </template>
          </el-table-column>
        </el-table>
        <p v-if="form.colorLots.length" class="text-xs text-slate-500 mt-1 mb-0">{{ t('pages.mrpLab.qtySatuanHint') }}</p>
        <p class="text-xs text-slate-500 mt-2 mb-0">{{ t('pages.mrpLab.stokLapanganHint') }}</p>
      </el-form>
      <template #footer>
        <el-button @click="createOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="colorLotViewOpen"
      :title="t('pages.mrpLab.colorLotDetailTitle')"
      width="720px"
      destroy-on-close
      append-to-body
    >
      <el-descriptions :column="1" border size="small" class="mb-3">
        <el-descriptions-item :label="t('pages.mrpLab.kodeLw')">{{ colorLotView.lwCode }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.mrpLab.namaLot')">{{ dash(colorLotView.nama_lot_warna) }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.mrpLab.remarks')">{{ dash(colorLotView.catatan) }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.mrpLab.qtySatuan')">
          {{ formatQtySatuanTotal(colorLotView) }}
        </el-descriptions-item>
      </el-descriptions>
      <p class="text-xs text-slate-500 mb-2">{{ t('pages.mrpLab.kimiaBahanList') }}</p>
      <el-table :data="colorLotView.items" border size="small" :empty-text="t('common.tableEmpty')">
        <el-table-column type="index" width="48" :label="t('common.noLabel')" align="center" />
        <el-table-column :label="t('pages.mrpLab.kimiaMaterial')" min-width="280" show-overflow-tooltip>
          <template #default="{ row }">{{ kimiaItemDisplayLabel(row) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpLab.qty')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty) }}</template>
        </el-table-column>
        <el-table-column prop="satuan" :label="t('pages.mrpLab.satuan')" width="72" />
      </el-table>
      <template #footer>
        <el-button type="primary" @click="colorLotViewOpen = false">{{ t('common.close') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="lotDraftOpen"
      :title="lotDraftDialogTitle"
      width="960px"
      destroy-on-close
      append-to-body
    >
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpLab.namaLot')" required>
          <el-input v-model="lotDraft.nama_lot_warna" :placeholder="t('pages.mrpLab.namaLotPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpLab.remarks')">
          <el-input v-model="lotDraft.catatan" :placeholder="t('pages.mrpLab.remarks')" clearable />
        </el-form-item>
        <div class="mrp-lab-items-head">
          <strong>{{ t('pages.mrpLab.kimiaBahanList') }}</strong>
          <el-button size="small" @click="addDraftKimiaRow">{{ t('common.add') }}</el-button>
        </div>
        <div v-if="!kimiaStockPickOptions.length" class="text-sm text-amber-700 mb-2">
          {{ t('pages.mrpLab.noKimiaStockLapangan') }}
        </div>
        <p v-else-if="labSisaPickCount" class="text-xs text-slate-500 mb-2">
          {{ t('pages.mrpLab.labSisaPickHint', { n: labSisaPickCount }) }}
        </p>
        <div class="mrp-lab-draft-head text-xs text-slate-500 mb-1">
          <span>{{ t('pages.mrpLab.kimiaMaterial') }}</span>
          <span>{{ t('pages.mrpLab.qty') }}</span>
          <span>{{ t('pages.mrpLab.satuan') }}</span>
          <span />
        </div>
        <div v-for="(row, idx) in lotDraft.items" :key="idx" class="mrp-lab-draft-row">
          <el-select
            v-model="row.pick_key"
            filterable
            clearable
            :placeholder="t('pages.mrpLab.kimiaPickPlaceholder')"
            class="w-full"
            @change="(key) => onDraftStockPick(row, key)"
          >
            <el-option
              v-for="lot in kimiaStockPickOptions"
              :key="lot.pick_key"
              :label="kimiaStockPickLabel(lot)"
              :value="lot.pick_key"
            />
          </el-select>
          <el-input v-model="row.qty" type="number" :placeholder="t('pages.mrpLab.qty')" />
          <el-input v-model="row.satuan" readonly :placeholder="t('pages.mrpLab.satuan')" />
          <el-button link type="danger" :disabled="lotDraft.items.length <= 1" @click="lotDraft.items.splice(idx, 1)">
            {{ t('common.delete') }}
          </el-button>
        </div>
        <p v-if="lotDraftQtySatuan !== '—'" class="text-sm text-slate-700 mt-2 mb-0">
          <strong>{{ t('pages.mrpLab.qtySatuan') }}:</strong> {{ lotDraftQtySatuan }}
        </p>
      </el-form>
      <template #footer>
        <el-button @click="cancelLotDraft">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="commitLotDraft">{{ lotDraftSubmitLabel }}</el-button>
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
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { can } from '../../../security/permissions'
import { mrpCreateLab, mrpCreateLabSisa, mrpLabOptions, mrpListLab, mrpMixedLabSisa } from '../../../api/client'
import { printLabLotQr } from '../../../utils/mrpLabQrPrint'
import {
  buildFarmasiSheetsFromCreate,
  printLabFarmasiInstructions,
} from '../../../utils/mrpLabFarmasiPrint'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const optionsLoading = ref(false)
const saving = ref(false)
const mixingId = ref(null)
const createOpen = ref(false)
const lotDraftOpen = ref(false)
const lotDraftEditIndex = ref(null)
const colorLotViewOpen = ref(false)
const colorLotView = reactive({
  lwCode: '',
  nama_lot_warna: '',
  catatan: '',
  items: [],
})
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
const options = reactive({
  rencana_items: [],
  kimia_list: [],
  kimia_stock_lots: [],
  lab_lot_sisa_picks: [],
  reseps: [],
})
const form = reactive({
  rencana_item_id: null,
  colorLots: [],
})
const lotDraft = reactive({
  nama_lot_warna: '',
  catatan: '',
  items: [],
})

const selectedRpiItem = computed(
  () => options.rencana_items.find((it) => it.id === form.rencana_item_id) || null,
)

const kimiaNameByCode = computed(() => {
  const map = new Map()
  for (const k of options.kimia_list || []) {
    const code = (k.kode_kimia || '').trim()
    if (code) map.set(code, (k.nama_kimia || '').trim())
  }
  return map
})

const lotDraftDialogTitle = computed(() =>
  lotDraftEditIndex.value != null
    ? t('pages.mrpLab.lotDraftEditTitle')
    : t('pages.mrpLab.lotDraftTitle'),
)
const lotDraftSubmitLabel = computed(() =>
  lotDraftEditIndex.value != null ? t('pages.mrpLab.lotDraftSaveEdit') : t('pages.mrpLab.lotDraftAdd'),
)

const lotDraftQtySatuan = computed(() =>
  formatQtySatuanTotal(lotDraft, { onlyCommittedRows: true }),
)

const kimiaStockPickOptions = computed(() => {
  const out = []
  for (const lot of options.kimia_stock_lots || []) {
    const kode = (lot.kode_kimia || '').trim()
    const sid = lot.stok_in_id
    if (sid == null || sid === '') continue
    out.push({
      ...lot,
      source: 'kimia',
      pick_key: `kimia-${sid}`,
      nama_kimia: (lot.nama_kimia || kimiaNameByCode.value.get(kode) || '').trim(),
    })
  }
  for (const s of options.lab_lot_sisa_picks || []) {
    const sid = s.lab_sisa_id
    if (sid == null || sid === '') continue
    out.push({
      ...s,
      source: 'lab_sisa',
      pick_key: `sisa-${sid}`,
      nama_kimia: (s.nama_kimia || s.kode_kimia || '').trim(),
    })
  }
  return out.sort((a, b) => {
    const ka = `${a.source || ''}-${a.kode_kimia || ''}-${a.lot_number || ''}`
    const kb = `${b.source || ''}-${b.kode_kimia || ''}-${b.lot_number || ''}`
    return ka.localeCompare(kb, undefined, { numeric: true })
  })
})

const labSisaPickCount = computed(
  () => (options.lab_lot_sisa_picks || []).filter((s) => s.lab_sisa_id != null).length,
)
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

function emptyKimiaRow() {
  return {
    pick_key: null,
    kode_kimia: '',
    stok_in_id: null,
    lab_sisa_id: null,
    lot_number: '',
    qty: '',
    satuan: 'kg',
    stok_lapangan: null,
  }
}

function lwBaseFromRpi(kodeRpi) {
  const s = (kodeRpi || '').trim()
  if (!s) return 'LW'
  const up = s.toUpperCase()
  if (up.startsWith('RPI-')) return `LW-${s.slice(4)}`
  if (up.startsWith('RPI')) return `LW-${s.slice(3).replace(/^-/, '')}`
  return `LW-${s}`
}

function previewLwCode(index) {
  const base = lwBaseFromRpi(selectedRpiItem.value?.kode_rencana_item)
  return `${base}-${index + 1}`
}

function parseItemQty(v) {
  if (v == null || v === '') return NaN
  if (typeof v === 'number') return Number.isFinite(v) ? v : NaN
  const s = String(v).trim().replace(/\s/g, '').replace(',', '.')
  if (!s) return NaN
  const n = Number(s)
  return Number.isFinite(n) ? n : NaN
}

/** Jumlah qty per satuan dari semua baris kimia lot (total per satuan jika campuran). */
function formatQtySatuanTotal(lot, opts = {}) {
  const onlyCommittedRows = Boolean(opts.onlyCommittedRows)
  const items = lot?.items || []
  if (!items.length) return '—'
  const byUnit = new Map()
  for (const it of items) {
    if (
      onlyCommittedRows &&
      !it.pick_key &&
      (it.stok_in_id == null || it.stok_in_id === '') &&
      (it.lab_sisa_id == null || it.lab_sisa_id === '')
    ) {
      continue
    }
    const u = (it.satuan || 'kg').trim() || 'kg'
    const q = parseItemQty(it.qty)
    if (!Number.isFinite(q) || q <= 0) continue
    byUnit.set(u, (byUnit.get(u) || 0) + q)
  }
  if (!byUnit.size) return '—'
  return [...byUnit.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([u, q]) => `${formatQty(q)} ${u}`)
    .join(' + ')
}

function kimiaStockPickLabel(lot) {
  const kode = (lot.kode_kimia || '').trim() || '—'
  const nama = (lot.nama_kimia || kimiaNameByCode.value.get(kode) || '').trim() || '—'
  const lotNo = (lot.lot_number || '').trim() || '—'
  const stokPart = `${formatQty(lot.qty_sisa)} ${(lot.satuan || '').trim()}`.trim()
  const base = [kode, nama, lotNo, stokPart || '—'].join(' - ')
  if (lot.source === 'lab_sisa') {
    return `${t('pages.mrpLab.labSisaPickTag')}: ${base}`
  }
  return base
}

function findMaterialPick(pickKey) {
  if (pickKey == null || pickKey === '') return null
  return kimiaStockPickOptions.value.find((l) => l.pick_key === pickKey) || null
}

function findMaterialPickForItem(item) {
  if (item?.pick_key) return findMaterialPick(item.pick_key)
  if (item?.lab_sisa_id != null && item.lab_sisa_id !== '') {
    return findMaterialPick(`sisa-${item.lab_sisa_id}`)
  }
  if (item?.stok_in_id != null && item.stok_in_id !== '') {
    return findMaterialPick(`kimia-${item.stok_in_id}`)
  }
  return null
}

/** @deprecated use findMaterialPickForItem */
function findKimiaStockLot(stokInId) {
  if (stokInId == null || stokInId === '') return null
  return findMaterialPick(`kimia-${stokInId}`)
}

function kimiaItemDisplayLabel(item) {
  const lot = findMaterialPickForItem(item)
  if (lot) return kimiaStockPickLabel(lot)
  const kode = (item?.kode_kimia || '').trim() || '—'
  const nama = kimiaNameByCode.value.get(kode) || '—'
  const lotNo = (item?.lot_number || '').trim() || '—'
  const stokPart = `${formatQty(item?.qty)} ${(item?.satuan || '').trim()}`.trim()
  return [kode, nama, lotNo, stokPart || '—'].join(' - ')
}

function cloneKimiaRowFromSaved(item) {
  const lot = findMaterialPickForItem(item)
  const qty = item?.qty
  const labSisaId = item?.lab_sisa_id ?? lot?.lab_sisa_id ?? null
  const stokInId = item?.stok_in_id ?? lot?.stok_in_id ?? null
  let pickKey = item?.pick_key ?? lot?.pick_key ?? null
  if (!pickKey && labSisaId != null) pickKey = `sisa-${labSisaId}`
  if (!pickKey && stokInId != null) pickKey = `kimia-${stokInId}`
  return {
    pick_key: pickKey,
    kode_kimia: (item?.kode_kimia || lot?.kode_kimia || '').trim(),
    stok_in_id: stokInId,
    lab_sisa_id: labSisaId,
    lot_number: (item?.lot_number ?? lot?.lot_number ?? '').trim(),
    qty: qty != null && qty !== '' ? String(qty) : '',
    satuan: (item?.satuan || lot?.satuan || 'kg').trim() || 'kg',
    stok_lapangan: lot != null ? Number(lot.qty_sisa) : null,
  }
}

function resetLotDraftForm() {
  lotDraft.nama_lot_warna = ''
  lotDraft.catatan = ''
  lotDraft.items = [emptyKimiaRow()]
  lotDraftEditIndex.value = null
}

function cancelLotDraft() {
  lotDraftOpen.value = false
  resetLotDraftForm()
}

async function ensureCreateOptionsLoaded() {
  if (!form.rencana_item_id) {
    ElMessage.warning(t('pages.mrpLab.rpiRequired'))
    return false
  }
  try {
    await reloadOptions()
    return true
  } catch (e) {
    ElMessage.error(e.message || String(e))
    return false
  }
}

async function openLotDraft() {
  if (!(await ensureCreateOptionsLoaded())) return
  resetLotDraftForm()
  lotDraftOpen.value = true
}

function viewColorLot(index) {
  const lot = form.colorLots[index]
  if (!lot) return
  colorLotView.lwCode = previewLwCode(index)
  colorLotView.nama_lot_warna = lot.nama_lot_warna || ''
  colorLotView.catatan = lot.catatan || ''
  colorLotView.items = (lot.items || []).map((it) => ({ ...it }))
  colorLotViewOpen.value = true
}

async function editColorLot(index) {
  const lot = form.colorLots[index]
  if (!lot) return
  if (!(await ensureCreateOptionsLoaded())) return
  lotDraftEditIndex.value = index
  lotDraft.nama_lot_warna = lot.nama_lot_warna || ''
  lotDraft.catatan = lot.catatan || ''
  const rows = (lot.items || []).map((it) => cloneKimiaRowFromSaved(it))
  lotDraft.items = rows.length ? rows : [emptyKimiaRow()]
  lotDraftOpen.value = true
}

async function removeColorLot(index) {
  const lot = form.colorLots[index]
  if (!lot) return
  try {
    await ElMessageBox.confirm(
      t('pages.mrpLab.colorLotDeleteConfirm', { nama: lot.nama_lot_warna || previewLwCode(index) }),
      t('common.confirm'),
      { type: 'warning' },
    )
    form.colorLots.splice(index, 1)
  } catch {
    /* cancelled */
  }
}

function addDraftKimiaRow() {
  lotDraft.items.push(emptyKimiaRow())
}

function onDraftStockPick(row, pickKey) {
  row.pick_key = pickKey || null
  if (!pickKey) {
    row.kode_kimia = ''
    row.stok_in_id = null
    row.lab_sisa_id = null
    row.lot_number = ''
    row.satuan = 'kg'
    row.stok_lapangan = null
    return
  }
  const lot = findMaterialPick(pickKey)
  if (!lot) return
  row.kode_kimia = (lot.kode_kimia || '').trim()
  row.lot_number = (lot.lot_number || '').trim()
  row.stok_lapangan = Number(lot.qty_sisa) || 0
  row.satuan = (lot.satuan || 'kg').trim() || 'kg'
  if (lot.source === 'lab_sisa') {
    row.lab_sisa_id = lot.lab_sisa_id
    row.stok_in_id = null
  } else {
    row.stok_in_id = lot.stok_in_id
    row.lab_sisa_id = null
  }
}

function commitLotDraft() {
  const nama = (lotDraft.nama_lot_warna || '').trim()
  if (!nama) {
    ElMessage.warning(t('pages.mrpLab.namaLot'))
    return
  }
  const items = lotDraft.items.filter(
    (r) =>
      (r.pick_key != null && r.pick_key !== '') ||
      r.stok_in_id != null ||
      r.lab_sisa_id != null,
  )
  if (!items.length) {
    ElMessage.warning(t('pages.mrpLab.itemsEmpty'))
    return
  }
  for (const r of items) {
    const qty = Number(r.qty)
    const pick = findMaterialPickForItem(r)
    const kode = r.kode_kimia || pick?.kode_kimia || '—'
    if (!(qty > 0)) {
      ElMessage.warning(`${t('pages.mrpLab.qtyInvalid')}: ${kode}`)
      return
    }
    if (!pick) {
      ElMessage.warning(t('pages.mrpLab.kimiaPickRequired'))
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
  const payload = {
    nama_lot_warna: nama,
    catatan: (lotDraft.catatan || '').trim(),
    items: items.map((r) => ({
      kode_kimia: r.kode_kimia,
      stok_in_id: r.lab_sisa_id ? null : r.stok_in_id,
      lab_sisa_id: r.lab_sisa_id ?? null,
      lot_number: r.lot_number,
      qty: Number(r.qty),
      satuan: r.satuan || 'kg',
    })),
  }
  if (lotDraftEditIndex.value != null) {
    form.colorLots[lotDraftEditIndex.value] = payload
  } else {
    form.colorLots.push(payload)
  }
  lotDraftOpen.value = false
  resetLotDraftForm()
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
      kimia_stock_lots: opt.kimia_stock_lots || [],
      lab_lot_sisa_picks: opt.lab_lot_sisa_picks || [],
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
  form.rencana_item_id = null
  form.colorLots = []
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
  if (!form.rencana_item_id) {
    ElMessage.warning(t('pages.mrpLab.rpiRequired'))
    return
  }
  const hit = options.rencana_items.find((it) => it.id === form.rencana_item_id)
  if (hit && !hit.has_proses) {
    ElMessage.warning(t('pages.mrpLab.prosesRequired'))
    return
  }
  if (!form.colorLots.length) {
    ElMessage.warning(t('pages.mrpLab.colorLotsEmpty'))
    return
  }
  saving.value = true
  try {
    const res = await mrpCreateLab({
      rencana_item_id: form.rencana_item_id,
      lots: form.colorLots.map((lot) => ({
        nama_lot_warna: lot.nama_lot_warna,
        catatan: lot.catatan || null,
        items: (lot.items || []).map((r) => ({
          kode_kimia: r.kode_kimia,
          stok_in_id: r.lab_sisa_id ? null : r.stok_in_id,
          lab_sisa_id: r.lab_sisa_id ?? null,
          lot_number: r.lot_number,
          qty: Number(r.qty),
          satuan: r.satuan || 'kg',
        })),
      })),
    })
    const kodes = res?.kode_lot_warna_list || (res?.kode_lot_warna ? [res.kode_lot_warna] : [])
    if (kodes.length && res?.stok_deducted) {
      ElMessage.success(
        t('pages.mrpLab.savedWithStokOut', { kode: kodes.join(', '), n: (res.stok_outs || []).length }),
      )
    } else {
      ElMessage.success(
        kodes.length ? `${t('common.saved')}: ${kodes.join(', ')}` : t('common.saved'),
      )
    }
    if (kodes.length && form.colorLots.length) {
      const sheets = buildFarmasiSheetsFromCreate({
        colorLots: form.colorLots,
        kodeList: kodes,
        rencanaItem: hit || selectedRpiItem.value,
        resolveKimiaName: (code) => kimiaNameByCode.value.get(code) || '',
        resolveStockLot: (_stokInId, item) => findMaterialPickForItem(item),
      })
      try {
        printLabFarmasiInstructions(sheets, {
          title: t('pages.mrpLab.printFarmasiTitle'),
          popupBlockedMessage: t('pages.mrpProses.popupBlocked'),
        })
      } catch (e) {
        ElMessage.warning(e.message || String(e))
      }
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
.mrp-lab-draft-head,
.mrp-lab-draft-row {
  display: grid;
  grid-template-columns: minmax(0, 2.2fr) 88px 72px auto;
  gap: 0.45rem;
  align-items: center;
}
.mrp-lab-draft-head {
  padding: 0 0.55rem;
}
.mrp-lab-draft-row {
  margin-bottom: 0.5rem;
  padding: 0.55rem;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  background: var(--el-fill-color-blank);
}
@media (max-width: 860px) {
  .mrp-lab-draft-head {
    display: none;
  }
  .mrp-lab-draft-row {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
