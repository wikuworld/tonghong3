<template>
  <AdminSection :title="t('pages.mrpStokKimia.title')" :subtitle="t('pages.mrpStokKimia.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div class="mb-4">
      <el-radio-group v-model="gudangTab" size="default" @change="onGudangTab">
        <el-radio-button value="utama">{{ t('pages.mrpStokKimia.gudangUtama') }}</el-radio-button>
        <el-radio-button value="lapangan">{{ t('pages.mrpStokKimia.gudangLapangan') }}</el-radio-button>
      </el-radio-group>
    </div>

    <div v-if="expiredCount" class="mb-3">
      <el-alert
        type="warning"
        :closable="false"
        show-icon
        :title="t('pages.mrpStokKimia.expiredAlert', { n: expiredCount })"
      />
    </div>

    <div v-if="canCreate && gudangTab === 'utama'" class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokKimia.inTitle') }}</h3>
        <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpStokKimia.inHint') }}</p>
        <el-form label-position="top" class="mrp-sk-in-form" @submit.prevent="doIn">
          <div class="mrp-sk-in-form__grid">
            <el-form-item :label="t('pages.mrpStokKimia.bahanBaku')" required>
              <el-select
                v-model="inForm.kimia_id"
                filterable
                clearable
                :placeholder="t('pages.mrpStokKimia.bahanBakuPlaceholder')"
                class="w-full"
                @change="onInKimiaChange"
              >
                <el-option
                  v-for="k in kimiaList"
                  :key="k.id"
                  :label="`${k.kode_barang} — ${k.nama_barang}${k.satuan ? ` (${k.satuan})` : ''}`"
                  :value="k.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item :label="t('pages.mrpStokKimia.lotNumber')">
              <el-input
                v-model="inForm.lot_number"
                :placeholder="t('pages.mrpStokKimia.lotNumber')"
                clearable
                @keyup.enter="doIn"
              />
            </el-form-item>
            <el-form-item :label="t('pages.mrpStokKimia.kemasan')">
              <el-input
                v-model="inForm.kemasan"
                readonly
                :placeholder="t('pages.mrpStokKimia.kemasanAutoPlaceholder')"
              />
            </el-form-item>
            <el-form-item :label="t('pages.mrpStokKimia.qty')" required>
              <el-input
                v-model="inForm.qty"
                type="number"
                :placeholder="t('pages.mrpStokKimia.qty')"
                @keyup.enter="doIn"
              />
            </el-form-item>
            <el-form-item :label="t('common.date')">
              <el-date-picker
                v-model="inForm.tanggal"
                type="date"
                value-format="YYYY-MM-DD"
                class="w-full"
              />
            </el-form-item>
            <el-form-item class="mrp-sk-in-form__action" label=" ">
              <el-button type="primary" :loading="saving" @click="doIn">
                {{ t('pages.mrpStokKimia.inBtn') }}
              </el-button>
            </el-form-item>
          </div>
        </el-form>
      </div>
    </div>

    <div v-if="canUpdate && gudangTab === 'utama'" class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokKimia.outTitle') }}</h3>
        <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpStokKimia.outHint') }}</p>
        <div class="flex flex-wrap gap-2 items-center">
          <el-select
            v-model="outForm.kimia_id"
            filterable
            clearable
            :placeholder="t('pages.mrpStokKimia.kimia')"
            class="max-w-sm"
            @change="onKimiaPickForOut"
          >
            <el-option
              v-for="k in kimiaList"
              :key="k.id"
              :label="`${k.kode_barang} — ${k.nama_barang}${k.satuan ? ` (${k.satuan})` : ''}`"
              :value="k.id"
            />
          </el-select>
          <el-input
            v-model="outForm.qty"
            type="number"
            :placeholder="t('pages.mrpStokKimia.qty')"
            class="w-28"
            @keyup.enter="doOut"
          />
          <el-select v-model="outForm.tujuan" class="w-40">
            <el-option :label="t('pages.mrpStokKimia.tujuanLapangan')" value="lapangan" />
            <el-option :label="t('pages.mrpStokKimia.tujuanProduksi')" value="produksi" />
            <el-option :label="t('pages.mrpStokKimia.tujuanReturn')" value="return" />
          </el-select>
          <el-button type="danger" :loading="saving" @click="doOut">{{ t('pages.mrpStokKimia.outBtn') }}</el-button>
        </div>
        <p v-if="outForm.stok != null" class="text-xs text-slate-500 mt-2 mb-0">
          {{ t('pages.mrpStokKimia.outFifoHint', { qty: formatQty(outForm.stok), unit: outForm.satuan || 'kg' }) }}
        </p>
      </div>
    </div>

    <div v-if="canUpdate && gudangTab === 'utama'" class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokKimia.sisaTitle') }}</h3>
        <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpStokKimia.sisaFormHint') }}</p>
        <div class="flex flex-wrap gap-2 items-center">
          <el-input
            v-model="sisaForm.barcode"
            :placeholder="t('pages.mrpStokKimia.sisaBarcode')"
            class="max-w-xs"
            clearable
            @keyup.enter="doSisa"
          />
          <el-input
            v-model="sisaForm.qty"
            type="number"
            :placeholder="t('pages.mrpStokKimia.qty')"
            class="w-28"
            @keyup.enter="doSisa"
          />
          <el-input
            v-model="sisaForm.notes"
            :placeholder="t('common.notes')"
            class="max-w-xs"
            clearable
          />
          <el-button type="success" :loading="saving" @click="doSisa">
            {{ t('pages.mrpStokKimia.sisaBtn') }}
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="canUpdate && gudangTab === 'lapangan'" class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpStokKimia.outLapanganTitle') }}</h3>
        <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpStokKimia.outLapanganHint') }}</p>
        <div class="flex flex-wrap gap-2 items-center">
          <el-select
            v-model="lapanganForm.stok_in_id"
            filterable
            clearable
            :placeholder="t('pages.mrpStokKimia.lot')"
            class="max-w-md"
            @change="onLapanganLotPick"
          >
            <el-option
              v-for="s in activeLots"
              :key="s.id"
              :label="lotLabel(s)"
              :value="s.id"
            />
          </el-select>
          <el-input
            v-model="lapanganForm.qty"
            type="number"
            :placeholder="t('pages.mrpStokKimia.qty')"
            class="w-28"
            @keyup.enter="doOutLapangan"
          />
          <el-input
            v-model="lapanganForm.keterangan"
            :placeholder="t('common.notes')"
            class="max-w-xs"
          />
          <el-button type="danger" :loading="saving" @click="doOutLapangan">
            {{ t('pages.mrpStokKimia.outLapanganBtn') }}
          </el-button>
        </div>
        <p v-if="lapanganForm.stok != null" class="text-xs text-slate-500 mt-2 mb-0">
          {{ t('pages.mrpStokKimia.sisaHint', { qty: formatQty(lapanganForm.stok), unit: lapanganForm.satuan || 'kg' }) }}
        </p>
      </div>
    </div>

    <div class="admin-inner-card mb-4">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpStokKimia.summaryTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.mrpStokKimia.summaryHint') }}</p>
        </div>
        <el-input
          v-model="searchSummary"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpStokKimia.summarySearchPlaceholder')"
        />
      </div>
      <el-table
        ref="summaryTableRef"
        :data="filteredSummary"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        row-key="kode_barang"
        :empty-text="t('pages.mrpStokKimia.summaryEmpty')"
        @expand-change="onSummaryExpand"
      >
        <el-table-column type="expand">
          <template #default="{ row }">
            <div v-loading="historyLoading[row.kode_barang]" class="mrp-sk-summary-expand">
              <h4 class="mrp-sk-summary-expand__title">{{ t('pages.mrpStokKimia.historyIn') }}</h4>
              <el-table
                :data="historyCache[row.kode_barang]?.in || []"
                border
                size="small"
                class="admin-table mb-4"
                :empty-text="t('common.tableEmpty')"
              >
                <el-table-column prop="kode_internal" :label="t('pages.mrpStokKimia.bc')" min-width="130" show-overflow-tooltip />
                <el-table-column :label="t('pages.mrpStokKimia.lotNumber')" min-width="120" show-overflow-tooltip>
                  <template #default="{ row: lot }">{{ dash(lot.lot_number) }}</template>
                </el-table-column>
                <el-table-column :label="t('pages.mrpStokKimia.qty')" width="90" align="right">
                  <template #default="{ row: lot }">{{ formatQty(lot.qty) }}</template>
                </el-table-column>
                <el-table-column :label="t('pages.mrpStokKimia.sisa')" width="90" align="right">
                  <template #default="{ row: lot }">{{ formatQty(lot.qty_sisa) }}</template>
                </el-table-column>
                <el-table-column :label="t('common.date')" width="110">
                  <template #default="{ row: lot }">{{ formatDate(lot.tanggal_in) }}</template>
                </el-table-column>
              </el-table>
              <h4 class="mrp-sk-summary-expand__title">{{ t('pages.mrpStokKimia.historyOut') }}</h4>
              <el-table
                :data="historyCache[row.kode_barang]?.out || []"
                border
                size="small"
                class="admin-table"
                :empty-text="t('common.tableEmpty')"
              >
                <el-table-column prop="kode_internal" :label="t('pages.mrpStokKimia.bc')" min-width="130" show-overflow-tooltip />
                <el-table-column :label="t('pages.mrpStokKimia.qty')" width="90" align="right">
                  <template #default="{ row: out }">{{ formatQty(out.qty) }}</template>
                </el-table-column>
                <el-table-column :label="t('pages.mrpStokKimia.tujuan')" width="110" align="center">
                  <template #default="{ row: out }">
                    <el-tag :type="tujuanType(out.tujuan)" size="small" effect="plain">
                      {{ tujuanLabel(out.tujuan) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column :label="t('pages.mrpStokKimia.wip')" min-width="110" show-overflow-tooltip>
                  <template #default="{ row: out }">{{ dash(out.kode_wip) }}</template>
                </el-table-column>
                <el-table-column :label="t('common.date')" width="110">
                  <template #default="{ row: out }">{{ formatDate(out.tanggal) }}</template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </el-table-column>
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column :label="t('pages.mrpStokKimia.kode')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            <el-button link type="primary" class="font-medium" @click="toggleSummaryRow(row)">
              {{ row.kode_barang }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column prop="nama_barang" :label="t('common.name')" min-width="160" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpStokKimia.summaryLots')" width="90" align="right">
          <template #default="{ row }">{{ row.lot_count ?? 0 }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokKimia.sisa')" width="110" align="right">
          <template #default="{ row }">
            {{ formatQty(row.qty_sisa) }}
            <span class="text-slate-400 text-xs">{{ dash(row.satuan) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokKimia.summaryQtyIn')" width="110" align="right">
          <template #default="{ row }">
            {{ formatQty(row.qty_in) }}
            <span class="text-slate-400 text-xs">{{ dash(row.satuan) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="admin-inner-card mb-4">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpStokKimia.stokIn') }}</h3>
          <p class="admin-inner-card__sub">
            {{ t('pages.mrpStokKimia.statsIn', { lots: stats.lots, qty: formatQty(stats.qty_sisa) }) }}
          </p>
        </div>
        <el-input
          v-model="searchIn"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpStokKimia.searchPlaceholder')"
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
        <el-table-column prop="kode_internal" sortable="custom" :label="t('pages.mrpStokKimia.bc')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="lot_number" :label="t('pages.mrpStokKimia.lotNumber')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.lot_number) }}</template>
        </el-table-column>
        <el-table-column prop="kode_barang" :label="t('pages.mrpStokKimia.kode')" width="120" show-overflow-tooltip />
        <el-table-column prop="nama_barang" :label="t('common.name')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpStokKimia.sisa')" width="100" align="right">
          <template #default="{ row }">
            {{ formatQty(row.qty_sisa) }}
            <span class="text-slate-400 text-xs">{{ dash(row.satuan) }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokKimia.gudang')" width="110" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" :type="gudangTagType(row.gudang)">
              {{ gudangLabel(row.gudang) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokKimia.expired')" width="120">
          <template #default="{ row }">
            <span :class="{ 'text-amber-700 font-medium': isExpiredSoon(row.expired_date) }">
              {{ formatDate(row.expired_date) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="120">
          <template #default="{ row }">{{ formatDate(row.tanggal_in) }}</template>
        </el-table-column>
        <el-table-column v-if="canUpdate" :label="t('common.actions')" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions
              :show-edit="true"
              :show-delete="true"
              :more-items="Number(row.qty_sisa) > 0 ? [{ command: 'out', label: gudangTab === 'lapangan' ? t('pages.mrpStokKimia.outLapanganBtn') : 'OUT', icon: Upload }] : []"
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
        <h3 class="admin-inner-card__title">{{ t('pages.mrpStokKimia.stokOut') }}</h3>
        <el-input
          v-model="searchOut"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpStokKimia.searchOutPlaceholder')"
        />
      </div>
      <el-table :data="filteredOut" border stripe size="small" class="admin-table" :empty-text="t('common.tableEmpty')">
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="nama_barang" :label="t('common.name')" min-width="150" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpStokKimia.qty')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokKimia.tujuan')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="tujuanType(row.tujuan)" size="small" effect="plain">
              {{ tujuanLabel(row.tujuan) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpStokKimia.wip')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.kode_wip) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="120">
          <template #default="{ row }">{{ formatDate(row.tanggal) }}</template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="editOpen"
      :title="t('pages.mrpStokKimia.editTitle')"
      width="480px"
      destroy-on-close
      append-to-body
    >
      <p v-if="editLocked" class="text-sm text-amber-700 mb-3">{{ t('pages.mrpStokKimia.editLocked') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpStokKimia.bc')">
          <el-input :model-value="editForm.kode_internal" disabled />
        </el-form-item>
        <el-form-item :label="t('pages.mrpStokKimia.qty')" required>
          <el-input v-model="editForm.qty" type="number" />
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker v-model="editForm.tanggal" type="date" value-format="YYYY-MM-DD" class="w-full" :disabled="editLocked" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpStokKimia.lotNumber')">
          <el-input v-model="editForm.lot_number" :disabled="editLocked" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpStokKimia.kemasan')">
          <el-input v-model="editForm.jumlah_kemasan" :disabled="editLocked" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpStokKimia.expired')">
          <el-date-picker v-model="editForm.expired_date" type="date" value-format="YYYY-MM-DD" class="w-full" :disabled="editLocked" />
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
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Upload } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { can } from '../../../security/permissions'
import {
  getMaterial,
  mrpGetMasterKimia,
  mrpStokKimia,
  mrpStokKimiaAction,
} from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const gudangTab = ref('utama')
const stokIn = ref([])
const summaryRows = ref([])
const summaryTableRef = ref(null)
const historyCache = reactive({})
const historyLoading = reactive({})
const searchSummary = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('tanggal_in')
const sortDir = ref('desc')
const stokOut = ref([])
const kimiaList = ref([])
const searchIn = ref('')
const searchOut = ref('')
const stats = ref({ lots: 0, qty_sisa: 0, out_rows: 0 })
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const inForm = reactive({
  kimia_id: null,
  qty: null,
  lot_number: '',
  kemasan: '',
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
  lot_number: '',
  jumlah_kemasan: '',
  expired_date: '',
  satuan: '',
})
const editLocked = computed(() => editIssued.value > 0.001)

function findKimiaInList(id) {
  if (id == null || id === '') return null
  const key = String(id)
  return kimiaList.value.find((k) => String(k.id) === key || String(k.erp_material_id) === key) || null
}

function materialUkuranText(mat) {
  if (!mat) return ''
  for (const key of ['ukuran', 'size', 'kemasan']) {
    const raw = mat[key]
    if (raw == null || raw === '') continue
    const s = String(raw).trim()
    if (s) return s
  }
  return ''
}

function applyKimiaUkuranToList(id, ukuran) {
  if (!ukuran) return
  const hit = findKimiaInList(id)
  if (hit) {
    hit.ukuran = ukuran
    hit.size = ukuran
  }
}

async function fetchKimiaUkuran(id) {
  const fromList = materialUkuranText(findKimiaInList(id))
  if (fromList) return fromList
  try {
    const detail = await mrpGetMasterKimia(id)
    const u = materialUkuranText(detail)
    if (u) return u
  } catch {
    /* Flask route may be unavailable on older deploy */
  }
  try {
    const mat = await getMaterial(id)
    return materialUkuranText(mat)
  } catch {
    return ''
  }
}

async function onInKimiaChange(id) {
  inForm.kemasan = ''
  if (id == null || id === '') return
  const ukuran = await fetchKimiaUkuran(id)
  if (ukuran) {
    inForm.kemasan = ukuran
    applyKimiaUkuranToList(id, ukuran)
  }
}

watch(
  () => inForm.kimia_id,
  (id) => {
    onInKimiaChange(id)
  },
)

watch(kimiaList, () => {
  if (inForm.kimia_id != null && inForm.kimia_id !== '') onInKimiaChange(inForm.kimia_id)
})
const outForm = reactive({
  kimia_id: null,
  qty: null,
  stok: null,
  satuan: '',
  tujuan: 'produksi',
  tanggal: new Date().toISOString().slice(0, 10),
})
const lapanganForm = reactive({
  stok_in_id: null,
  qty: null,
  stok: null,
  satuan: '',
  keterangan: '',
  tanggal: new Date().toISOString().slice(0, 10),
})
const sisaForm = reactive({
  barcode: '',
  qty: null,
  notes: '',
})

const activeLots = computed(() =>
  (stokIn.value || []).filter((s) => Number(s.qty_sisa) > 0),
)

const filteredSummary = computed(() => {
  const q = searchSummary.value.trim().toLowerCase()
  if (!q) return summaryRows.value
  return summaryRows.value.filter((r) =>
    [r.kode_barang, r.nama_barang]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

const filteredIn = computed(() => {
  const q = searchIn.value.trim().toLowerCase()
  if (!q) return stokIn.value
  return stokIn.value.filter((r) =>
    [r.kode_internal, r.kode_barang, r.nama_barang, r.gudang, r.lot_number]
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
    [r.nama_barang, r.kode_barang, r.tujuan, r.kode_wip]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

const expiredCount = computed(() =>
  (stokIn.value || []).filter((r) => Number(r.qty_sisa) > 0 && isExpiredSoon(r.expired_date)).length,
)

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

function isExpiredSoon(v) {
  if (!v) return false
  const d = new Date(String(v).slice(0, 10))
  if (Number.isNaN(d.getTime())) return false
  const soon = new Date()
  soon.setDate(soon.getDate() + 30)
  return d <= soon
}

function lotLabel(s) {
  const lotNo = (s.lot_number || '').trim()
  const lotPart = lotNo ? ` · Lot ${lotNo}` : ''
  return `${s.kode_internal}${lotPart} · ${s.nama_barang} · sisa ${formatQty(s.qty_sisa)} ${s.satuan || ''}`.trim()
}

function gudangLabel(v) {
  const g = String(v || '').toLowerCase()
  if (g === 'lapangan' || g === 'mixing') return t('pages.mrpStokKimia.gudangLapangan')
  return t('pages.mrpStokKimia.gudangUtama')
}

function gudangTagType(v) {
  const g = String(v || '').toLowerCase()
  if (g === 'lapangan' || g === 'mixing') return 'warning'
  return 'success'
}

function tujuanType(v) {
  if (v === 'mixing' || v === 'lapangan') return 'warning'
  if (v === 'produksi') return 'success'
  if (v === 'return') return 'info'
  if (v === 'keluar') return 'danger'
  return ''
}

function tujuanLabel(v) {
  if (v === 'mixing' || v === 'lapangan') return t('pages.mrpStokKimia.tujuanLapangan')
  if (v === 'produksi') return t('pages.mrpStokKimia.tujuanProduksi')
  if (v === 'return') return t('pages.mrpStokKimia.tujuanReturn')
  if (v === 'keluar') return t('pages.mrpStokKimia.tujuanKeluar')
  return v || '—'
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

function fifoLotsForKimia(kimiaId) {
  if (!kimiaId) return []
  const key = String(kimiaId)
  return activeLots.value
    .filter((s) => String(s.erp_material_id || s.kimia_id) === key)
    .slice()
    .sort((a, b) => {
      const da = String(a.tanggal_in || '')
      const db = String(b.tanggal_in || '')
      if (da !== db) return da.localeCompare(db)
      return (Number(a.id) || 0) - (Number(b.id) || 0)
    })
}

function onKimiaPickForOut(id) {
  const lots = fifoLotsForKimia(id)
  const total = lots.reduce((sum, s) => sum + (Number(s.qty_sisa) || 0), 0)
  const k = kimiaList.value.find((x) => x.id === id)
  outForm.stok = total
  outForm.satuan = k?.satuan || lots[0]?.satuan || 'kg'
  if (outForm.qty == null || outForm.qty === '') outForm.qty = total > 0 ? total : null
}

function onLapanganLotPick(id) {
  const s = stokIn.value.find((r) => r.id === id)
  if (!s) {
    lapanganForm.stok = null
    lapanganForm.satuan = ''
    return
  }
  lapanganForm.stok = Number(s.qty_sisa) || 0
  lapanganForm.satuan = s.satuan || 'kg'
  if (lapanganForm.qty == null || lapanganForm.qty === '') lapanganForm.qty = lapanganForm.stok
}

function outFromRow(row) {
  if (gudangTab.value === 'lapangan') {
    lapanganForm.stok_in_id = row.id
    onLapanganLotPick(row.id)
    lapanganForm.qty = Number(row.qty_sisa) || null
    return
  }
  const erpId = row.erp_material_id || row.kimia_id
  outForm.kimia_id = erpId || null
  onKimiaPickForOut(outForm.kimia_id)
  outForm.qty = Number(row.qty_sisa) || null
}

function clearSummaryHistory() {
  Object.keys(historyCache).forEach((k) => {
    delete historyCache[k]
    delete historyLoading[k]
  })
}

async function loadSummaryHistory(kode) {
  if (!kode || historyCache[kode]) return
  historyLoading[kode] = true
  try {
    const data = await mrpStokKimia({
      gudang: gudangTab.value,
      kode,
      all: 1,
      page: 1,
      pageSize: 500,
    })
    historyCache[kode] = {
      in: data.stok_in || [],
      out: data.stok_out || [],
    }
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    historyLoading[kode] = false
  }
}

async function onSummaryExpand(row, expandedRows) {
  if (!expandedRows.some((r) => r.kode_barang === row.kode_barang)) return
  await loadSummaryHistory(row.kode_barang)
}

function toggleSummaryRow(row) {
  summaryTableRef.value?.toggleRowExpansion(row)
}

function onGudangTab() {
  outForm.stok_in_id = null
  outForm.qty = null
  outForm.stok = null
  lapanganForm.stok_in_id = null
  lapanganForm.qty = null
  lapanganForm.stok = null
  summaryRows.value = []
  clearSummaryHistory()
  reload()
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
  editForm.lot_number = row.lot_number || ''
  editForm.jumlah_kemasan = row.jumlah_kemasan ?? ''
  editForm.expired_date = String(row.expired_date || '').slice(0, 10)
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
    await mrpStokKimiaAction({
      action: 'update',
      id: editForm.id,
      qty: editForm.qty,
      tanggal: editForm.tanggal,
      lot_number: editForm.lot_number,
      jumlah_kemasan: editForm.jumlah_kemasan,
      expired_date: editForm.expired_date || null,
      satuan: editForm.satuan,
    })
    ElMessage.success(t('pages.mrpStokKimia.editOk', { kode: editForm.kode_internal }))
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
      t('pages.mrpStokKimia.deleteConfirm', { kode: row.kode_internal }),
      { type: 'warning' },
    )
  } catch {
    return
  }
  try {
    await mrpStokKimiaAction({ action: 'delete', id: row.id })
    ElMessage.success(t('pages.mrpStokKimia.deleteOk', { kode: row.kode_internal }))
    await reload()
  } catch (e) {
    ElMessage.error(stockApiError(e))
  }
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpStokKimia(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
        extra: { gudang: gudangTab.value },
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    stokIn.value = pageData.items.length ? pageData.items : (data.stok_in || [])
    total.value = pageData.total || stokIn.value.length
    summaryRows.value = data.summary || []
    clearSummaryHistory()
    stokOut.value = data.stok_out || []
    kimiaList.value = data.kimia_list || []
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
  if (!inForm.kimia_id) {
    ElMessage.warning(t('pages.mrpStokKimia.kimiaRequired'))
    return
  }
  const qty = Number(inForm.qty)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpStokKimia.qtyInvalid'))
    return
  }
  saving.value = true
  try {
    const res = await mrpStokKimiaAction({
      action: 'in',
      kimia_id: inForm.kimia_id,
      qty,
      gudang: 'utama',
      lot_number: (inForm.lot_number || '').trim() || null,
      tanggal: inForm.tanggal,
    })
    ElMessage.success(
      t('pages.mrpStokKimia.inOk', { kode: res?.kode_internal || '' }),
    )
    inForm.kimia_id = null
    inForm.qty = null
    inForm.lot_number = ''
    inForm.kemasan = ''
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

async function doSisa() {
  const barcode = (sisaForm.barcode || '').trim()
  if (!barcode) {
    ElMessage.warning(t('pages.mrpStokKimia.sisaBarcodeRequired'))
    return
  }
  const qty = Number(sisaForm.qty)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpStokKimia.qtyInvalid'))
    return
  }
  saving.value = true
  try {
    const res = await mrpStokKimiaAction({
      action: 'sisa',
      barcode,
      qty,
      notes: sisaForm.notes || null,
      record_stock_sisa: true,
    })
    ElMessage.success(
      t('pages.mrpStokKimia.sisaOk', {
        qty: formatQty(res?.qty_added ?? qty),
        kode: res?.kode_internal || barcode,
        sisa: formatQty(res?.qty_sisa),
      }),
    )
    sisaForm.barcode = ''
    sisaForm.qty = null
    sisaForm.notes = ''
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

async function doOut() {
  if (!outForm.kimia_id) {
    ElMessage.warning(t('pages.mrpStokKimia.kimiaRequired'))
    return
  }
  const qty = Number(outForm.qty)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpStokKimia.qtyInvalid'))
    return
  }
  if (outForm.stok != null && qty > Number(outForm.stok)) {
    ElMessage.warning(t('pages.mrpStokKimia.qtyExceed', { sisa: formatQty(outForm.stok) }))
    return
  }
  try {
    await ElMessageBox.confirm(
      t('pages.mrpStokKimia.outConfirm', { qty: formatQty(qty) }),
      t('pages.mrpStokKimia.outBtn'),
      { type: 'warning', confirmButtonText: t('pages.mrpStokKimia.outBtn'), cancelButtonText: t('common.cancel') },
    )
  } catch {
    return
  }
  saving.value = true
  try {
    const res = await mrpStokKimiaAction({
      action: 'out',
      kimia_id: outForm.kimia_id,
      fifo: true,
      qty,
      tujuan: outForm.tujuan,
      tanggal: outForm.tanggal,
    })
    if (res?.lapangan_lot) {
      ElMessage.success(
        t('pages.mrpStokKimia.outLapanganTransferOk', {
          kode: res.lapangan_lot.kode_internal || '',
          qty: formatQty(res.lapangan_lot.qty_sisa ?? qty),
        }),
      )
    } else {
      ElMessage.success(t('common.saved'))
    }
    outForm.kimia_id = null
    outForm.qty = null
    outForm.stok = null
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
    await reload()
  } finally {
    saving.value = false
  }
}

async function doOutLapangan() {
  if (!lapanganForm.stok_in_id) {
    ElMessage.warning(t('pages.mrpStokKimia.lotRequired'))
    return
  }
  const qty = Number(lapanganForm.qty)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpStokKimia.qtyInvalid'))
    return
  }
  if (lapanganForm.stok != null && qty > Number(lapanganForm.stok)) {
    ElMessage.warning(t('pages.mrpStokKimia.qtyExceed', { sisa: formatQty(lapanganForm.stok) }))
    return
  }
  try {
    await ElMessageBox.confirm(
      t('pages.mrpStokKimia.outLapanganConfirm', { qty: formatQty(qty) }),
      t('pages.mrpStokKimia.outLapanganBtn'),
      {
        type: 'warning',
        confirmButtonText: t('pages.mrpStokKimia.outLapanganBtn'),
        cancelButtonText: t('common.cancel'),
      },
    )
  } catch {
    return
  }
  saving.value = true
  try {
    await mrpStokKimiaAction({
      action: 'out_lapangan',
      stok_in_id: lapanganForm.stok_in_id,
      qty,
      keterangan: (lapanganForm.keterangan || '').trim() || null,
      tanggal: lapanganForm.tanggal,
    })
    ElMessage.success(t('common.saved'))
    lapanganForm.stok_in_id = null
    lapanganForm.qty = null
    lapanganForm.stok = null
    lapanganForm.keterangan = ''
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
.w-40 {
  width: 10rem;
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
.mrp-sk-summary-expand {
  padding: 0.35rem 0.5rem 0.75rem;
}
.mrp-sk-summary-expand__title {
  margin: 0 0 0.5rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--el-text-color-secondary);
}
.mrp-sk-in-form :deep(.el-form-item) {
  margin-bottom: 0;
}
.mrp-sk-in-form__grid {
  display: grid;
  grid-template-columns: minmax(12rem, 1.4fr) minmax(9rem, 1fr) minmax(8rem, 0.9fr) minmax(6rem, 0.65fr) minmax(9rem, 0.85fr) auto;
  gap: 0.75rem 1rem;
  align-items: end;
}
.mrp-sk-in-form__action :deep(.el-form-item__content) {
  justify-content: flex-start;
}
@media (max-width: 1100px) {
  .mrp-sk-in-form__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .mrp-sk-in-form__action {
    grid-column: 1 / -1;
  }
}
</style>
