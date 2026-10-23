<template>
  <AdminSection :title="t('pages.mrpPalet.title')" :subtitle="t('pages.mrpPalet.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" @click="openIn">{{ t('pages.mrpPalet.paletIn') }}</el-button>
      <el-button v-if="canUpdate" type="warning" @click="openPaletOut">{{ t('pages.mrpPalet.paletOut') }}</el-button>
      <el-button v-if="canUpdate" type="danger" @click="openYlOut">{{ t('pages.mrpPalet.ylOut') }}</el-button>
    </template>

    <div class="admin-inner-card mb-4">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpPalet.movements') }}</h3>
          <p class="admin-inner-card__sub">
            {{ t('pages.mrpPalet.statsMovements', { in: stats.in, out: stats.out, yl: ylRows.length }) }}
          </p>
        </div>
        <div class="flex gap-2 flex-wrap items-center">
          <el-radio-group v-model="directionFilter" size="small" @change="reload">
            <el-radio-button value="">{{ t('pages.mrpPalet.filterAll') }}</el-radio-button>
            <el-radio-button value="IN">IN</el-radio-button>
            <el-radio-button value="OUT">OUT</el-radio-button>
          </el-radio-group>
          <el-input
            v-model="searchMov"
            clearable
            size="small"
            class="w-52"
            :placeholder="t('pages.mrpPalet.searchMovements')"
          />
        </div>
      </div>
      <el-table
        :data="filteredMovements"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('common.tableEmpty')"
        @sort-change="onSortChange"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="kode_palet" :label="t('pages.mrpPalet.kodePalet')" min-width="130" show-overflow-tooltip sortable="custom" />
        <el-table-column :label="t('pages.mrpPalet.direction')" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="row.direction === 'IN' ? 'success' : 'warning'" size="small" effect="plain">
              {{ row.direction || '—' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tanggal" :label="t('common.date')" width="120" sortable="custom">
          <template #default="{ row }">{{ formatDate(row.tanggal) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpInbound.supplier')" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.supplier_name) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpPalet.ylCount')" width="80" align="right">
          <template #default="{ row }">{{ formatQty(row.jml_yl) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.notes')" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.keterangan) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="88" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions
              :show-view="true"
              view-label="YL"
              @view="showYl(row.kode_palet)"
            />
          </template>
        </el-table-column>
      </el-table>
      <div class="mt-3 flex justify-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
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
        <h3 class="admin-inner-card__title">{{ t('pages.mrpPalet.ylStock') }}</h3>
        <el-input
          v-model="searchYl"
          clearable
          size="small"
          class="w-56"
          :placeholder="t('pages.mrpPalet.searchYl')"
        />
      </div>
      <el-table
        :data="filteredYl"
        v-loading="loadingYl"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('common.tableEmpty')"
      >
        <el-table-column prop="kode_palet" :label="t('pages.mrpPalet.kodePalet')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="kode_yl" :label="t('pages.mrpPalet.kulitMaster')" min-width="120" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpPalet.thickness')" width="100" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.thickness) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.color')" width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.warna) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpInbound.bentukKulit')" min-width="110" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.bentuk_kulit) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpInbound.skala')" width="90" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.skala) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpInbound.unitPrice')" width="100" align="right">
          <template #default="{ row }">{{ formatPrice(row.unit_price) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpInbound.supplier')" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.supplier_name) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpPalet.qty')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty) }}</template>
        </el-table-column>
        <el-table-column v-if="canUpdate" :label="t('common.actions')" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions
              :show-edit="true"
              :show-delete="true"
              :more-items="ylMoreItems"
              @edit="openYlEdit(row)"
              @delete="deleteYl(row)"
              @more="(cmd) => onYlMore(cmd, row)"
            />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-alert
      v-if="pendingLabels.length"
      class="mb-3"
      type="success"
      show-icon
      :closable="true"
      :title="t('pages.mrpInbound.printReady')"
      @close="pendingLabels = []"
    >
      <el-button type="primary" size="small" class="mt-2" @click="printPendingLabels">
        {{ t('pages.mrpInbound.printLabel') }}
      </el-button>
    </el-alert>

    <el-dialog v-model="inOpen" :title="t('pages.mrpPalet.paletIn')" width="920px" destroy-on-close append-to-body>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpPalet.paletInHint') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpPalet.kodePalet')" required>
          <el-input v-model="form.kode_palet" :placeholder="t('pages.mrpPalet.kodePaletPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker v-model="form.tanggal" type="date" value-format="YYYY-MM-DD" class="w-full" />
        </el-form-item>
        <el-form-item :label="t('common.notes')">
          <el-input v-model="form.keterangan" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpInbound.supplier')">
          <el-select
            v-model="form.supplier_name"
            filterable
            clearable
            class="w-full"
            :loading="loadingInboundMasters"
            :placeholder="t('pages.mrpInbound.supplier')"
          >
            <el-option
              v-for="s in supplierOptionsFor(form.supplier_name)"
              :key="s.id || s.nama"
              :label="s.nama"
              :value="s.nama"
            />
          </el-select>
        </el-form-item>
        <div class="mb-2 flex justify-between items-center">
          <strong>{{ t('pages.mrpPalet.ylItems') }}</strong>
          <el-button size="small" @click="form.items.push(emptyYlItem())">
            {{ t('common.add') }}
          </el-button>
        </div>
        <div v-for="(item, idx) in form.items" :key="idx" class="mb-3 rounded border border-slate-200 p-2">
        <div class="grid gap-2" style="grid-template-columns: 0.72fr 1.15fr 1fr 1fr 0.75fr auto;">
          <el-select
            v-model="item.type"
            class="w-full"
            :placeholder="t('pages.mrpMasterKulit.kulitTypePick')"
            @change="onItemTypeChange(item)"
          >
            <el-option label="PU" value="PU" />
            <el-option label="SUEDE" value="SUEDE" />
          </el-select>
          <el-select
            v-if="item.type === 'PU'"
            v-model="item.kode_yl"
            filterable
            class="w-full"
            :loading="loadingMaster"
            :placeholder="t('pages.mrpPalet.kulitMasterPick')"
            @change="onKulitPick(item)"
          >
            <el-option
              v-for="k in kulitRowsForPu"
              :key="k.id || k.kode_kulit"
              :label="kulitOptionLabel(k)"
              :value="k.kode_kulit"
            />
          </el-select>
          <el-input
            v-else-if="item.type === 'SUEDE'"
            model-value="SUEDE"
            class="w-full"
            disabled
          />
          <el-input v-else v-model="item.kode_yl" class="w-full" disabled :placeholder="t('pages.mrpMasterKulit.kulitTypePick')" />
          <el-input
            v-model="item.thickness"
            class="w-full"
            :placeholder="t('pages.mrpPalet.thickness')"
            :disabled="item.type === 'PU' && !!kulitForItem(item)?.thickness"
          />
          <el-input
            v-model="item.warna"
            class="w-full"
            :placeholder="t('common.color')"
            :disabled="item.type === 'PU' && !!kulitColor(kulitForItem(item))"
          />
          <el-input v-model="item.qty" type="number" :placeholder="t('pages.mrpPalet.qty')" />
          <el-button
            link
            type="danger"
            :disabled="form.items.length <= 1"
            @click="form.items.splice(idx, 1)"
          >
            {{ t('common.delete') }}
          </el-button>
        </div>
        <div class="mt-2 grid gap-2" style="grid-template-columns: 1fr 1fr 1fr;">
          <el-select
            v-model="item.bentuk_kulit"
            filterable
            clearable
            class="w-full"
            :loading="loadingInboundMasters"
            :placeholder="t('pages.mrpInbound.bentukKulit')"
          >
            <el-option
              v-for="b in bentukOptionsFor(item.bentuk_kulit)"
              :key="b.id || b.nama"
              :label="b.nama"
              :value="b.nama"
            />
          </el-select>
          <el-select
            v-model="item.skala"
            filterable
            clearable
            class="w-full"
            :loading="loadingInboundMasters"
            :placeholder="t('pages.mrpInbound.skala')"
          >
            <el-option
              v-for="s in skalaOptionsFor(item.skala)"
              :key="s.id || s.nama"
              :label="s.nama"
              :value="s.nama"
            />
          </el-select>
          <el-input v-model="item.unit_price" type="number" :placeholder="t('pages.mrpInbound.unitPrice')" />
        </div>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="inOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="submitIn">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="ylOpen" :title="`${t('pages.mrpPalet.ylStock')} · ${ylPalet}`" size="42%">
      <el-table :data="ylDetail" border size="small" :empty-text="t('common.tableEmpty')">
        <el-table-column prop="kode_yl" :label="t('pages.mrpPalet.kulitMaster')" min-width="110" />
        <el-table-column :label="t('pages.mrpPalet.thickness')" width="100">
          <template #default="{ row }">{{ dash(row.thickness) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.color')" min-width="100">
          <template #default="{ row }">{{ dash(row.warna) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpPalet.qty')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty) }}</template>
        </el-table-column>
      </el-table>
    </el-drawer>

    <el-dialog v-model="paletOutOpen" :title="t('pages.mrpPalet.paletOut')" width="480px" destroy-on-close append-to-body>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpPalet.paletOutHint') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpPalet.kodePalet')" required>
          <el-select v-model="paletOutForm.kode_palet" filterable allow-create default-first-option class="w-full">
            <el-option v-for="k in paletCodes" :key="k" :label="k" :value="k" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.notes')">
          <el-input v-model="paletOutForm.keterangan" />
        </el-form-item>
        <el-checkbox v-model="paletOutForm.clear_yl">{{ t('pages.mrpPalet.clearYl') }}</el-checkbox>
      </el-form>
      <template #footer>
        <el-button @click="paletOutOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="warning" :loading="saving" @click="submitPaletOut">{{ t('pages.mrpPalet.paletOut') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="ylOutOpen" :title="t('pages.mrpPalet.ylOut')" width="480px" destroy-on-close append-to-body>
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpPalet.ylOutHint') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpPalet.kulitMaster')" required>
          <el-select v-model="ylOutKey" filterable class="w-full" @change="onYlPick">
            <el-option
              v-for="y in ylRows"
              :key="`${y.kode_palet}::${y.kode_yl}`"
              :label="`${y.kode_yl} · ${y.kode_palet} (${formatQty(y.qty)})`"
              :value="`${y.kode_palet}::${y.kode_yl}`"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.mrpPalet.kodePalet')" required>
          <el-input v-model="ylOutForm.kode_palet" disabled />
        </el-form-item>
        <el-form-item :label="t('pages.mrpPalet.qty')" required>
          <el-input v-model.number="ylOutForm.qty" type="number" :min="0" />
          <p v-if="ylOutForm.stok != null" class="text-xs text-slate-500 mt-1 mb-0">
            {{ t('pages.mrpPalet.stokHint', { qty: formatQty(ylOutForm.stok) }) }}
          </p>
        </el-form-item>
        <el-form-item :label="t('common.notes')">
          <el-input v-model="ylOutForm.keterangan" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ylOutOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="danger" :loading="saving" @click="submitYlOut">{{ t('pages.mrpPalet.ylOut') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="ylEditOpen"
      :title="t('pages.mrpPalet.ylEditTitle')"
      width="440px"
      destroy-on-close
      append-to-body
    >
      <p v-if="ylEditForm.spek_locked" class="text-sm text-amber-700 mb-3">{{ t('pages.mrpPalet.ylEditLocked') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.mrpPalet.kodePalet')">
          <el-input :model-value="ylEditForm.kode_palet" disabled />
        </el-form-item>
        <el-form-item :label="t('pages.mrpPalet.kulitMaster')">
          <el-input :model-value="ylEditForm.kode_yl" disabled />
        </el-form-item>
        <el-form-item :label="t('pages.mrpPalet.qty')" required>
          <el-input v-model="ylEditForm.qty" type="number" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpPalet.thickness')">
          <el-input v-model="ylEditForm.thickness" :disabled="ylEditForm.spek_locked" />
        </el-form-item>
        <el-form-item :label="t('common.color')">
          <el-input v-model="ylEditForm.warna" :disabled="ylEditForm.spek_locked" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpInbound.bentukKulit')">
          <el-select
            v-model="ylEditForm.bentuk_kulit"
            filterable
            clearable
            class="w-full"
            :loading="loadingInboundMasters"
          >
            <el-option
              v-for="b in bentukOptionsFor(ylEditForm.bentuk_kulit)"
              :key="b.id || b.nama"
              :label="b.nama"
              :value="b.nama"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.mrpInbound.skala')">
          <el-select
            v-model="ylEditForm.skala"
            filterable
            clearable
            class="w-full"
            :loading="loadingInboundMasters"
          >
            <el-option
              v-for="s in skalaOptionsFor(ylEditForm.skala)"
              :key="s.id || s.nama"
              :label="s.nama"
              :value="s.nama"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.mrpInbound.unitPrice')">
          <el-input v-model="ylEditForm.unit_price" type="number" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpInbound.supplier')">
          <el-select
            v-model="ylEditForm.supplier_name"
            filterable
            clearable
            class="w-full"
            :loading="loadingInboundMasters"
          >
            <el-option
              v-for="s in supplierOptionsFor(ylEditForm.supplier_name)"
              :key="s.id || s.nama"
              :label="s.nama"
              :value="s.nama"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ylEditOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" @click="saveYlEdit">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Printer, Refresh, Upload } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { printInboundLabels } from '../../../utils/mrpInboundLabelPrint.js'
import { can } from '../../../security/permissions'
import {
  mrpListBentukKulit,
  mrpListMasterKulit,
  mrpListPaletMovements,
  mrpListSkala,
  mrpListSupplier,
  mrpListYl,
  mrpPaletIn,
  mrpPaletOut,
  mrpPaletYl,
  mrpPaletYlDelete,
  mrpPaletYlUpdate,
  mrpYlMovement,
} from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const loadingYl = ref(false)
const saving = ref(false)
const movements = ref([])
const page = ref(1)
const pageSize = ref(50)
const total = ref(0)
const sortBy = ref('created_at')
const sortDir = ref('desc')
const ylRows = ref([])
const searchMov = ref('')
const searchYl = ref('')
const directionFilter = ref('')
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const paletCodes = computed(() => [...new Set(ylRows.value.map((y) => y.kode_palet).filter(Boolean))])
const inOpen = ref(false)
const ylOpen = ref(false)
const paletOutOpen = ref(false)
const ylOutOpen = ref(false)
const ylEditOpen = ref(false)
const ylEditForm = reactive({
  kode_palet: '',
  kode_yl: '',
  qty: '',
  thickness: '',
  warna: '',
  bentuk_kulit: '',
  skala: '',
  unit_price: '',
  supplier_name: '',
  spek_locked: false,
})
const pendingLabels = ref([])
const ylMoreItems = computed(() => [
  { command: 'print', label: t('pages.mrpInbound.printLabel'), icon: Printer },
  { command: 'out', label: 'OUT', icon: Upload },
])
const ylPalet = ref('')
const ylDetail = ref([])
const ylOutKey = ref('')
const kulitRows = ref([])
const loadingMaster = ref(false)
const loadingInboundMasters = ref(false)
const supplierOptions = ref([])
const bentukKulitOptions = ref([])
const skalaOptions = ref([])

function emptyYlItem() {
  return {
    type: 'PU',
    kode_yl: '',
    thickness: '',
    warna: '',
    qty: null,
    bentuk_kulit: '',
    skala: '',
    unit_price: '',
    erp_material_id: null,
  }
}

function priceOrNull(value) {
  const raw = String(value ?? '').trim()
  if (!raw) return null
  const n = Number(raw)
  if (!Number.isFinite(n) || n < 0) return undefined
  return n
}

function normalizeKulitType(raw) {
  const s = String(raw ?? '').trim().toUpperCase()
  if (s === 'SUEDE' || s === 'SUIDE') return 'SUEDE'
  if (s === 'PU') return 'PU'
  return ''
}

function kulitTypeOf(row) {
  return normalizeKulitType(row?.type ?? row?.leather_type)
}

/** Sama sumber dengan halaman /admin/mrp/masters/kulit — type PU (+ data lama tanpa type). */
const kulitRowsForPu = computed(() =>
  kulitRows.value.filter((k) => {
    const kt = kulitTypeOf(k)
    return kt === 'PU' || !kt
  }),
)

function onItemTypeChange(item) {
  const tpe = normalizeKulitType(item?.type)
  if (tpe === 'SUEDE') {
    item.kode_yl = 'SUEDE'
    item.thickness = ''
    item.warna = ''
    item.erp_material_id = null
    return
  }
  if (tpe === 'PU') {
    const allowed = new Set(kulitRowsForPu.value.map((k) => String(k.kode_kulit || '').trim()))
    if (item.kode_yl && !allowed.has(String(item.kode_yl).trim())) {
      item.kode_yl = ''
      item.thickness = ''
      item.warna = ''
    }
    return
  }
  item.kode_yl = ''
  item.thickness = ''
  item.warna = ''
}

const form = reactive({
  kode_palet: '',
  tanggal: new Date().toISOString().slice(0, 10),
  keterangan: '',
  supplier_name: '',
  items: [emptyYlItem()],
})
const paletOutForm = reactive({
  kode_palet: '',
  tanggal: new Date().toISOString().slice(0, 10),
  keterangan: '',
  clear_yl: true,
})
const ylOutForm = reactive({
  kode_yl: '',
  kode_palet: '',
  thickness: '',
  warna: '',
  qty: null,
  stok: null,
  tanggal: new Date().toISOString().slice(0, 10),
  keterangan: '',
  direction: 'OUT',
})

const filteredMovements = computed(() => {
  const q = searchMov.value.trim().toLowerCase()
  if (!q) return movements.value
  return movements.value.filter((r) =>
    [r.kode_palet, r.direction, r.keterangan].filter(Boolean).join(' ').toLowerCase().includes(q),
  )
})

const filteredYl = computed(() => {
  const q = searchYl.value.trim().toLowerCase()
  if (!q) return ylRows.value
  return ylRows.value.filter((r) =>
    [r.kode_palet, r.kode_yl, r.thickness, r.warna].filter(Boolean).join(' ').toLowerCase().includes(q),
  )
})

const stats = computed(() => ({
  in: (movements.value || []).filter((r) => r.direction === 'IN').length,
  out: (movements.value || []).filter((r) => r.direction === 'OUT').length,
}))

function kulitColor(row) {
  return String(row?.color ?? row?.warna ?? '').trim()
}

function kulitOptionLabel(k) {
  const code = (k?.kode_kulit || '').trim()
  const name = (k?.nama_kulit || '').trim()
  if (code && name && name !== code) return `${code} — ${name}`
  return code || name || '—'
}

function kulitForItem(item) {
  const code = String(item?.kode_yl || '').trim()
  if (!code) return null
  return kulitRows.value.find((k) => String(k.kode_kulit || '').trim() === code) || null
}

function applyKulitMasterFields(item) {
  const k = kulitForItem(item)
  if (!k) {
    item.thickness = ''
    item.warna = ''
    return
  }
  item.thickness = String(k.thickness || '').trim()
  item.warna = kulitColor(k)
  item.erp_material_id = k.erp_material_id || k.id || null
}

function onKulitPick(item) {
  applyKulitMasterFields(item)
}

async function loadKulitMaster() {
  loadingMaster.value = true
  try {
    const all = []
    let pageNum = 1
    const pageSizeLoad = 200
    for (;;) {
      const data = await mrpListMasterKulit({
        page: pageNum,
        page_size: pageSizeLoad,
        sort_by: 'kode_kulit',
        sort_dir: 'asc',
      })
      const pageData = normalizePageResult(data, { page: pageNum, pageSize: pageSizeLoad })
      all.push(...pageData.items)
      if (!pageData.items.length || all.length >= pageData.total) break
      pageNum += 1
    }
    kulitRows.value = all
  } catch {
    kulitRows.value = []
  } finally {
    loadingMaster.value = false
  }
}

async function loadPagedMaster(listFn, extra = {}) {
  const all = []
  let pageNum = 1
  const pageSizeLoad = 200
  for (;;) {
    const data = await listFn({
      page: pageNum,
      page_size: pageSizeLoad,
      sort_by: 'nama',
      sort_dir: 'asc',
      ...extra,
    })
    const pageData = normalizePageResult(data, { page: pageNum, pageSize: pageSizeLoad })
    all.push(...pageData.items)
    if (!pageData.items.length || all.length >= pageData.total) break
    pageNum += 1
  }
  return all
}

async function loadInboundMasters() {
  loadingInboundMasters.value = true
  try {
    const [suppliers, bentuk, skala] = await Promise.all([
      loadPagedMaster(mrpListSupplier, { material: 'KULIT' }),
      loadPagedMaster(mrpListBentukKulit),
      loadPagedMaster(mrpListSkala),
    ])
    supplierOptions.value = suppliers
    bentukKulitOptions.value = bentuk
    skalaOptions.value = skala
  } catch {
    supplierOptions.value = []
    bentukKulitOptions.value = []
    skalaOptions.value = []
  } finally {
    loadingInboundMasters.value = false
  }
}

function withOrphanNama(options, value) {
  const nama = String(value || '').trim()
  if (!nama) return options
  if (options.some((o) => String(o.nama || '').trim() === nama)) return options
  return [...options, { id: `orphan-${nama}`, nama }]
}

function supplierOptionsFor(value) {
  return withOrphanNama(supplierOptions.value, value)
}

function bentukOptionsFor(value) {
  return withOrphanNama(bentukKulitOptions.value, value)
}

function skalaOptionsFor(value) {
  return withOrphanNama(skalaOptions.value, value)
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

function formatPrice(v) {
  if (v == null || v === '') return '—'
  return formatQty(v)
}

function formatDate(v) {
  if (!v) return '—'
  return String(v).slice(0, 10)
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
  sortBy.value = mapped.sortBy || 'created_at'
  sortDir.value = mapped.sortDir || 'desc'
  page.value = 1
  reload()
}

async function reload() {
  loading.value = true
  loadingYl.value = true
  try {
    const params = buildPageParams({
      page: page.value,
      pageSize: pageSize.value,
      sortBy: sortBy.value,
      sortDir: sortDir.value,
      extra: directionFilter.value ? { direction: directionFilter.value } : {},
    })
    const [movData, yl] = await Promise.all([
      mrpListPaletMovements(params),
      mrpListYl({ page: 1, pageSize: 200 }),
    ])
    const pageData = normalizePageResult(movData, { page: page.value, pageSize: pageSize.value })
    movements.value = pageData.items
    total.value = pageData.total
    ylRows.value = normalizePageResult(yl, { page: 1, pageSize: 200 }).items
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    loading.value = false
    loadingYl.value = false
  }
}

function openIn() {
  form.kode_palet = ''
  form.tanggal = new Date().toISOString().slice(0, 10)
  form.keterangan = ''
  form.supplier_name = ''
  form.items = [emptyYlItem()]
  loadKulitMaster()
  loadInboundMasters()
  inOpen.value = true
}

function ylLabel(item, header) {
  return {
    code: header.kode_palet,
    itemCode: item.kode_yl,
    qty: item.qty,
    thickness: item.thickness,
    color: item.warna,
    bentuk_kulit: item.bentuk_kulit,
    skala: item.skala,
    tanggal: header.tanggal,
    supplier_name: header.supplier_name || item.supplier_name,
  }
}

function printPendingLabels() {
  try {
    printInboundLabels(pendingLabels.value)
  } catch (e) {
    ElMessage.error(errMsg(e))
  }
}

function onYlMore(cmd, row) {
  if (cmd === 'print') {
    try {
      printInboundLabels([ylLabel(row, row)])
    } catch (e) {
      ElMessage.error(errMsg(e))
    }
    return
  }
  if (cmd === 'out') ylOutFromRow(row)
}

async function submitIn() {
  if (!form.kode_palet.trim()) {
    ElMessage.warning(t('pages.mrpPalet.kodePaletPlaceholder'))
    return
  }
  const items = form.items
    .map((it) => {
      const tpe = normalizeKulitType(it.type)
      let kodeYl = (it.kode_yl || '').trim()
      if (tpe === 'SUEDE') kodeYl = 'SUEDE'
      const price = priceOrNull(it.unit_price)
      return {
        kode_yl: kodeYl,
        thickness: (it.thickness || '').trim(),
        warna: (it.warna || '').trim(),
        qty: Number(it.qty),
        bentuk_kulit: (it.bentuk_kulit || '').trim(),
        skala: (it.skala || '').trim(),
        unit_price: price,
        erp_material_id: it.erp_material_id || null,
        _priceInvalid: price === undefined,
      }
    })
    .filter((it) => it.kode_yl)
  if (!items.length || items.some((it) => !Number.isFinite(it.qty) || it.qty <= 0)) {
    ElMessage.warning(t('pages.mrpPalet.ylItemsInvalid'))
    return
  }
  if (items.some((it) => it._priceInvalid)) {
    ElMessage.warning(t('pages.mrpInbound.priceInvalid'))
    return
  }
  const puMissingKode = form.items.some(
    (it) => normalizeKulitType(it.type) === 'PU' && !(it.kode_yl || '').trim(),
  )
  if (puMissingKode) {
    ElMessage.warning(t('pages.mrpPalet.kulitPuRequired'))
    return
  }
  saving.value = true
  try {
    const payloadItems = items.map(({ _priceInvalid, ...rest }) => rest)
    const res = await mrpPaletIn({
      kode_palet: form.kode_palet.trim(),
      tanggal: form.tanggal,
      keterangan: form.keterangan.trim() || null,
      supplier_name: form.supplier_name.trim() || null,
      items: payloadItems,
    })
    pendingLabels.value = (res?.items || payloadItems).map((item) =>
      ylLabel(item, {
        kode_palet: form.kode_palet.trim(),
        tanggal: form.tanggal,
        supplier_name: form.supplier_name.trim(),
      }),
    )
    ElMessage.success(t('pages.mrpPalet.paletInOk', { n: res?.yl_count || items.length }))
    inOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

async function showYl(kode) {
  ylPalet.value = kode
  try {
    ylDetail.value = await mrpPaletYl(kode)
    ylOpen.value = true
  } catch (e) {
    ElMessage.error(errMsg(e))
  }
}

function openPaletOut() {
  paletOutForm.kode_palet = paletCodes.value[0] || ''
  paletOutForm.tanggal = new Date().toISOString().slice(0, 10)
  paletOutForm.keterangan = ''
  paletOutForm.clear_yl = true
  paletOutOpen.value = true
}

async function submitPaletOut() {
  const kode = (paletOutForm.kode_palet || '').trim()
  if (!kode) {
    ElMessage.warning(t('pages.mrpPalet.kodePaletPlaceholder'))
    return
  }
  try {
    await ElMessageBox.confirm(
      t('pages.mrpPalet.paletOutConfirm', { kode }),
      t('pages.mrpPalet.paletOut'),
      { type: 'warning', confirmButtonText: t('pages.mrpPalet.paletOut'), cancelButtonText: t('common.cancel') },
    )
  } catch {
    return
  }
  saving.value = true
  try {
    const res = await mrpPaletOut({
      kode_palet: kode,
      tanggal: paletOutForm.tanggal,
      keterangan: paletOutForm.keterangan.trim() || null,
      clear_yl: !!paletOutForm.clear_yl,
    })
    ElMessage.success(
      t('pages.mrpPalet.paletOutOk', { n: res?.yl_cleared ?? 0 }),
    )
    paletOutOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

function openYlOut() {
  ylOutKey.value = ''
  ylOutForm.kode_yl = ''
  ylOutForm.kode_palet = ''
  ylOutForm.thickness = ''
  ylOutForm.warna = ''
  ylOutForm.qty = null
  ylOutForm.stok = null
  ylOutForm.keterangan = ''
  ylOutForm.tanggal = new Date().toISOString().slice(0, 10)
  ylOutOpen.value = true
}

function openYlEdit(row) {
  ylEditForm.kode_palet = row.kode_palet || ''
  ylEditForm.kode_yl = row.kode_yl || ''
  ylEditForm.qty = row.qty ?? ''
  ylEditForm.thickness = row.thickness || ''
  ylEditForm.warna = row.warna || ''
  ylEditForm.bentuk_kulit = row.bentuk_kulit || ''
  ylEditForm.skala = row.skala || ''
  ylEditForm.unit_price = row.unit_price ?? ''
  ylEditForm.supplier_name = row.supplier_name || ''
  ylEditForm.spek_locked = Boolean(row.spek_locked)
  loadInboundMasters()
  ylEditOpen.value = true
}

async function saveYlEdit() {
  const price = priceOrNull(ylEditForm.unit_price)
  if (price === undefined) {
    ElMessage.warning(t('pages.mrpInbound.priceInvalid'))
    return
  }
  saving.value = true
  try {
    await mrpPaletYlUpdate({
      kode_palet: ylEditForm.kode_palet,
      kode_yl: ylEditForm.kode_yl,
      qty: ylEditForm.qty,
      thickness: ylEditForm.thickness,
      warna: ylEditForm.warna,
      bentuk_kulit: ylEditForm.bentuk_kulit,
      skala: ylEditForm.skala,
      unit_price: price,
      supplier_name: ylEditForm.supplier_name,
    })
    ElMessage.success(t('pages.mrpPalet.ylEditOk', { kode: ylEditForm.kode_yl }))
    ylEditOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

async function deleteYl(row) {
  try {
    await ElMessageBox.confirm(
      t('pages.mrpPalet.ylDeleteConfirm', { kode: row.kode_yl, palet: row.kode_palet }),
      { type: 'warning' },
    )
  } catch {
    return
  }
  try {
    await mrpPaletYlDelete({ kode_palet: row.kode_palet, kode_yl: row.kode_yl })
    ElMessage.success(t('pages.mrpPalet.ylDeleteOk', { kode: row.kode_yl }))
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  }
}

function ylOutFromRow(row) {
  openYlOut()
  ylOutKey.value = `${row.kode_palet}::${row.kode_yl}`
  onYlPick(ylOutKey.value)
}

function onYlPick(key) {
  const [kodePalet, kodeYl] = String(key || '').split('::')
  const y = ylRows.value.find((r) => r.kode_palet === kodePalet && r.kode_yl === kodeYl)
  if (!y) return
  ylOutForm.kode_yl = y.kode_yl
  ylOutForm.kode_palet = y.kode_palet
  ylOutForm.thickness = y.thickness
  ylOutForm.warna = y.warna
  ylOutForm.stok = Number(y.qty) || 0
  ylOutForm.qty = ylOutForm.stok
}

async function submitYlOut() {
  if (!ylOutForm.kode_yl || !ylOutForm.kode_palet) {
    ElMessage.warning(t('pages.mrpPalet.ylPickRequired'))
    return
  }
  const qty = Number(ylOutForm.qty)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpPalet.qtyInvalid'))
    return
  }
  if (ylOutForm.stok != null && qty > Number(ylOutForm.stok)) {
    ElMessage.warning(t('pages.mrpPalet.qtyExceed', { stok: formatQty(ylOutForm.stok) }))
    return
  }
  saving.value = true
  try {
    await mrpYlMovement({
      kode_yl: ylOutForm.kode_yl,
      kode_palet: ylOutForm.kode_palet,
      thickness: ylOutForm.thickness,
      warna: ylOutForm.warna,
      qty,
      tanggal: ylOutForm.tanggal,
      keterangan: ylOutForm.keterangan.trim() || null,
      direction: 'OUT',
    })
    ElMessage.success(t('common.saved'))
    ylOutOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  reload()
})
</script>

<style scoped>
.w-52 {
  width: 13rem;
}
.w-56 {
  width: 14rem;
}
</style>
