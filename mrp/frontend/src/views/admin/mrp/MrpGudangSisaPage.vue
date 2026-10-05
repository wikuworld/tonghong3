<template>
  <AdminSection :title="t('pages.mrpGudangSisa.title')" :subtitle="t('pages.mrpGudangSisa.subtitle')">
    <template #actions>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <el-tabs v-model="tab" class="admin-tabs mb-4" @tab-change="onTabChange">
      <el-tab-pane v-for="s in sumberOptions" :key="s" :label="sumberLabel(s)" :name="s" />
    </el-tabs>

    <div v-if="canCreate" class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpGudangSisa.createTitle') }}</h3>
        <p class="text-sm text-slate-500 mb-3">{{ createHintText }}</p>
        <div v-if="tab === 'fg'" class="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 mb-3">
          <el-input v-model="fgForm.barcode" :placeholder="t('pages.mrpGudangSisa.fgBarcode')" clearable />
          <el-input v-model="fgForm.kode_rpi" :placeholder="t('pages.mrpGudangSisa.kodeRpi')" clearable />
          <el-input v-model="fgForm.kode_wip" placeholder="WIP" clearable />
          <el-input v-model="fgForm.material_name" :placeholder="t('common.material')" clearable />
          <el-input v-model="fgForm.warna" :placeholder="t('common.color')" clearable />
          <el-input v-model="fgForm.tebal" :placeholder="t('pages.mrpGudangSisa.tebal')" clearable />
          <el-select v-model="fgForm.treatment_jenis" clearable :placeholder="t('pages.mrpGudangSisa.jenis')" class="w-full">
            <el-option label="PU" value="PU" />
            <el-option label="Suede" value="Suede" />
          </el-select>
          <el-input v-model="fgForm.qty" type="number" :placeholder="t('pages.mrpGudangSisa.qty')" />
          <el-input v-model="fgForm.notes" :placeholder="t('common.notes')" clearable />
        </div>
        <div v-else class="flex flex-wrap gap-2 items-center">
          <el-input v-model="form.barcode" :placeholder="t('pages.mrpGudangSisa.barcode')" class="max-w-xs" clearable />
          <el-input v-model="form.lot" :placeholder="t('pages.mrpGudangSisa.lot')" class="w-36" clearable />
          <el-input v-model="form.qty" type="number" :placeholder="t('pages.mrpGudangSisa.qty')" class="w-28" />
          <el-input v-model="form.notes" :placeholder="t('common.notes')" class="max-w-xs" clearable />
        </div>
        <el-button type="primary" :loading="saving" @click="doCreate">{{ t('common.add') }}</el-button>
      </div>
    </div>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpGudangSisa.listTitle') }}</h3>
          <p class="admin-inner-card__sub">
            {{ t('pages.mrpGudangSisa.statsLine', { n: rows.length, open: countStatus('open'), reserved: countStatus('reserved'), approved: countStatus('approved') }) }}
          </p>
        </div>
        <div class="flex gap-2 flex-wrap items-center">
          <el-radio-group v-model="statusFilter" size="small" @change="reload">
            <el-radio-button value="">{{ t('pages.mrpGudangSisa.filterAll') }}</el-radio-button>
            <el-radio-button value="open">open</el-radio-button>
            <el-radio-button v-if="tab !== 'fg'" value="reserved">reserved</el-radio-button>
            <el-radio-button v-if="tab !== 'fg'" value="approved">approved</el-radio-button>
            <el-radio-button value="consumed">consumed</el-radio-button>
          </el-radio-group>
          <el-input
            v-model="search"
            clearable
            size="small"
            class="w-56"
            :placeholder="t('pages.mrpGudangSisa.searchPlaceholder')"
          />
        </div>
      </div>

      <el-table
        v-if="tab === 'fg'"
        :data="filteredRows"
        @sort-change="onSortChange"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('common.tableEmpty')"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="kode_packing" :label="t('pages.mrpGudangSisa.kodePacking')" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.kode_packing) }}</template>
        </el-table-column>
        <el-table-column prop="kode_wip" label="WIP" min-width="130" show-overflow-tooltip />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="warna" :label="t('common.color')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="tebal" :label="t('pages.mrpGudangSisa.tebal')" width="100" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpGudangSisa.jenis')" width="90" align="center">
          <template #default="{ row }">{{ dash(row.treatment_jenis) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpGudangSisa.qtySisa')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="plain">{{ fgStatusLabel(row) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="canUpdate" :label="t('common.actions')" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions :more-items="rowActions(row)" @more="(cmd) => onRowAction(cmd, row)" />
          </template>
        </el-table-column>
      </el-table>

      <el-table
        v-else
        :data="filteredRows"
        @sort-change="onSortChange"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('common.tableEmpty')"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column prop="barcode" sortable="custom" :label="t('pages.mrpGudangSisa.barcode')" min-width="130" show-overflow-tooltip />
        <el-table-column prop="lot" :label="t('pages.mrpGudangSisa.lot')" min-width="110" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpGudangSisa.qty')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="110" align="center">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small" effect="plain">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="PO" width="90" align="center">
          <template #default="{ row }">{{ row.po_id || '—' }}</template>
        </el-table-column>
        <el-table-column :label="t('common.notes')" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.notes) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.date')" width="120">
          <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
        </el-table-column>
        <el-table-column v-if="canUpdate" :label="t('common.actions')" width="112" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions :more-items="rowActions(row)" @more="(cmd) => onRowAction(cmd, row)" />
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
      v-model="assignOpen"
      :title="t('pages.mrpGudangSisa.assignSoTitle')"
      width="920px"
      destroy-on-close
      append-to-body
    >
      <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpGudangSisa.assignSoHint') }}</p>
      <div v-if="assignSisa" class="mrp-gs-fg-spec mb-3">
        <span>{{ dash(assignSisa.material_name) }}</span>
        <span>{{ dash(assignSisa.warna) }}</span>
        <span>{{ dash(assignSisa.tebal) }}</span>
        <span>{{ t('pages.mrpGudangSisa.qtySisa') }}: {{ formatQty(assignSisa.qty) }}</span>
      </div>
      <el-form v-loading="assignLoading" label-position="top">
        <el-form-item :label="t('pages.mrpGudangSisa.assignSoPickPo')" required>
          <el-input
            v-model="assignSoSearch"
            clearable
            size="small"
            class="mb-2"
            :placeholder="t('pages.mrpGudangSisa.assignSoSearch')"
            :disabled="!assignSoRows.length"
          />
          <el-table
            :data="filteredAssignSoRows"
            border
            stripe
            size="small"
            class="admin-table mrp-gs-assign-so-table"
            row-key="id"
            highlight-current-row
            :current-row-key="assignSelectedPoId"
            :empty-text="assignSoRows.length ? t('common.tableEmpty') : t('pages.mrpGudangSisa.assignSoEmpty')"
            max-height="360"
            @current-change="onAssignSoTableChange"
          >
            <el-table-column :label="t('pages.mrpRencana.soRef')" min-width="140" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.no_so || row.no_po) }}</template>
            </el-table-column>
            <el-table-column prop="customer" :label="t('common.customer')" min-width="160" show-overflow-tooltip />
            <el-table-column prop="item_name" :label="t('common.material')" min-width="180" show-overflow-tooltip />
            <el-table-column prop="warna" :label="t('common.color')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="tebal" :label="t('pages.mrpGudangSisa.tebal')" width="90" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpGudangSisa.qtyOutstanding')" width="110" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_outstanding) }}</template>
            </el-table-column>
          </el-table>
        </el-form-item>
        <el-form-item v-if="assignSelectedPo" :label="t('pages.mrpGudangSisa.qtyAssign')" required>
          <el-input v-model="assignQty" type="number" class="max-w-xs" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="saving" :disabled="!assignSelectedPo" @click="submitAssignSo">
          {{ t('pages.mrpGudangSisa.assignSoBtn') }}
        </el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Promotion, Select, RefreshRight, Connection } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { can } from '../../../security/permissions'
import {
  assignPoToPpic,
  createPo,
  mrpStockSisaAction,
  mrpStockSisaCreate,
  mrpStockSisaFgOutstandingSo,
  mrpStockSisaList,
  mrpStockSisaSyncPpic,
  updatePo,
} from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const loading = ref(false)
const saving = ref(false)
const assignLoading = ref(false)
const assignOpen = ref(false)
const assignSisa = ref(null)
const assignSoRows = ref([])
const assignSoSearch = ref('')
const assignSelectedPoId = ref(null)
const assignQty = ref('')
const assignSelectedPo = computed(() =>
  assignSoRows.value.find((r) => r.id === assignSelectedPoId.value) || null,
)
const filteredAssignSoRows = computed(() => {
  const q = assignSoSearch.value.trim().toLowerCase()
  if (!q) return assignSoRows.value
  return assignSoRows.value.filter((po) =>
    [po.no_so, po.no_po, po.customer, po.item_name, po.warna, po.tebal, po.lot_number]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('created_at')
const sortDir = ref('desc')
const search = ref('')
const statusFilter = ref('')
const tab = ref('kulit')
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const sumberOptions = ['kulit', 'kimia', 'wip', 'fg']
const form = reactive({
  barcode: '',
  lot: '',
  qty: null,
  notes: '',
})
const fgForm = reactive({
  barcode: '',
  kode_rpi: '',
  kode_wip: '',
  material_name: '',
  warna: '',
  tebal: '',
  treatment_jenis: '',
  qty: null,
  notes: '',
})

const createHintText = computed(() => {
  const key = `pages.mrpGudangSisa.createHint_${tab.value}`
  const translated = t(key)
  return translated === key ? t('pages.mrpGudangSisa.createHint') : translated
})

const filteredRows = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) => {
    const blob = tab.value === 'fg'
      ? [
          r.kode_packing,
          r.kode_rpi,
          r.kode_wip,
          r.material_name,
          r.warna,
          r.tebal,
          r.treatment_jenis,
          r.status,
          r.notes,
        ]
      : [r.sumber, r.barcode, r.lot, r.status, r.notes, r.po_id]
    return blob
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q)
  })
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

function sumberLabel(s) {
  const key = `pages.mrpGudangSisa.sumber_${s}`
  const translated = t(key)
  return translated === key ? s : translated
}

function statusType(status) {
  if (status === 'approved') return 'success'
  if (status === 'reserved') return 'warning'
  if (status === 'consumed') return 'info'
  return ''
}

function fgStatusLabel(row) {
  if (row.status === 'consumed' || Number(row.qty) <= 0) return t('pages.mrpGudangSisa.statusConsumed')
  return t('pages.mrpGudangSisa.statusAvailable')
}

function countStatus(st) {
  return (rows.value || []).filter((r) => r.status === st).length
}

function rowActions(row) {
  if (tab.value === 'fg') {
    if (row.status !== 'consumed' && Number(row.qty) > 0) {
      return [{ command: 'assign-so', label: t('pages.mrpGudangSisa.assignSoBtn'), icon: Connection }]
    }
    return []
  }
  const items = []
  if (row.status === 'open') {
    items.push({ command: 'ajukan', label: t('pages.mrpGudangSisa.ajukanSo'), icon: Promotion })
  }
  if (row.status === 'reserved') {
    items.push({ command: 'sync', label: t('pages.mrpGudangSisa.syncPpic'), icon: RefreshRight })
    items.push({ command: 'approve', label: t('pages.mrpGudangSisa.approveManual'), icon: Select })
  }
  return items
}

function onTabChange() {
  page.value = 1
  search.value = ''
  statusFilter.value = ''
  reload()
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
  try {
    if (tab.value !== 'fg') {
      await mrpStockSisaSyncPpic().catch(() => null)
    }
    const data = await mrpStockSisaList(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
        extra: {
          sumber: tab.value,
          status: statusFilter.value || undefined,
        },
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items
    total.value = pageData.total
  } catch (e) {
    rows.value = []
    total.value = 0
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function doCreate() {
  saving.value = true
  try {
    if (tab.value === 'fg') {
      const qty = Number(fgForm.qty)
      if (!(qty > 0)) {
        ElMessage.warning(t('pages.mrpGudangSisa.qtyRequired'))
        return
      }
      if (!fgForm.material_name?.trim() || !fgForm.warna?.trim() || !fgForm.tebal?.trim()) {
        ElMessage.warning(t('pages.mrpGudangSisa.fgSpecRequired'))
        return
      }
      await mrpStockSisaCreate({
        sumber: 'fg',
        barcode: fgForm.barcode.trim() || null,
        lot: fgForm.barcode.trim() || null,
        qty,
        notes: fgForm.notes.trim() || null,
        kode_rpi: fgForm.kode_rpi.trim() || null,
        kode_wip: fgForm.kode_wip.trim() || null,
        material_name: fgForm.material_name.trim(),
        warna: fgForm.warna.trim(),
        tebal: fgForm.tebal.trim(),
        treatment_jenis: fgForm.treatment_jenis || null,
      })
      Object.assign(fgForm, {
        barcode: '',
        kode_rpi: '',
        kode_wip: '',
        material_name: '',
        warna: '',
        tebal: '',
        treatment_jenis: '',
        qty: null,
        notes: '',
      })
    } else {
      const qty = Number(form.qty)
      if (!(qty > 0)) {
        ElMessage.warning(t('pages.mrpGudangSisa.qtyRequired'))
        return
      }
      await mrpStockSisaCreate({
        sumber: tab.value,
        barcode: form.barcode || null,
        lot: form.lot || null,
        qty,
        notes: form.notes || null,
      })
      form.barcode = ''
      form.lot = ''
      form.qty = null
      form.notes = ''
    }
    ElMessage.success(t('pages.mrpGudangSisa.created'))
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

function onAssignSoTableChange(row) {
  const nextId = row?.id ?? null
  if (nextId === assignSelectedPoId.value) return
  assignSelectedPoId.value = nextId
  assignQty.value = ''
}

async function openAssignSo(row) {
  assignSisa.value = row
  assignSelectedPoId.value = null
  assignQty.value = ''
  assignSoSearch.value = ''
  assignSoRows.value = []
  assignOpen.value = true
  assignLoading.value = true
  try {
    const data = await mrpStockSisaFgOutstandingSo(row.id)
    assignSisa.value = data.sisa || row
    assignSoRows.value = data.items || []
    if (!assignSoRows.value.length) {
      ElMessage.warning(t('pages.mrpGudangSisa.assignSoEmpty'))
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
    assignOpen.value = false
  } finally {
    assignLoading.value = false
  }
}

async function submitAssignSo() {
  if (!assignSisa.value?.id || !assignSelectedPo.value?.id) {
    ElMessage.warning(t('pages.mrpGudangSisa.assignSoPickPo'))
    return
  }
  const qty = Number(assignQty.value)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.mrpGudangSisa.qtyRequired'))
    return
  }
  const maxSisa = Number(assignSisa.value.qty)
  if (qty > maxSisa) {
    ElMessage.warning(t('pages.mrpGudangSisa.qtyExceedSisa', { sisa: formatQty(maxSisa) }))
    return
  }
  saving.value = true
  try {
    const res = await mrpStockSisaAction(assignSisa.value.id, {
      action: 'assign-so-fg',
      po_id: assignSelectedPo.value.id,
      qty,
    })
    ElMessage.success(res.message || t('pages.mrpGudangSisa.assignSoOk'))
    assignOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

async function ajukanSo(row) {
  try {
    await ElMessageBox.confirm(
      t('pages.mrpGudangSisa.ajukanConfirm', { id: row.id }),
      t('pages.mrpGudangSisa.ajukanSo'),
      { type: 'warning' },
    )
  } catch {
    return
  }
  saving.value = true
  try {
    let poId = row.po_id
    if (!poId) {
      const po = await createPo({
        status: 'draft',
        po_category: 'production',
        customer_name_snapshot: 'STOCK SISA',
        po_customer_ref: `SISA-${row.id}`,
        order_type_label: 'stock-sisa',
      })
      poId = po?.id
      if (poId) {
        try {
          await updatePo(poId, { status: 'confirmed' })
        } catch {
          /* draft tetap dipakai bila confirm gagal */
        }
        try {
          await assignPoToPpic(poId, {
            notes: `Ajukan SO dari stock sisa #${row.id}`,
          })
        } catch (e) {
          ElMessage.warning(e.message || t('pages.mrpGudangSisa.assignPpicWarn'))
        }
      }
    }
    const res = await mrpStockSisaAction(row.id, {
      action: 'ajukan-so',
      po_id: poId,
      notes: row.notes || `Ajukan SO sisa #${row.id}`,
    })
    ElMessage.success(res.message || t('pages.mrpGudangSisa.ajukanOk'))
    await reload()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    saving.value = false
  }
}

async function onRowAction(cmd, row) {
  if (cmd === 'assign-so') {
    await openAssignSo(row)
    return
  }
  if (cmd === 'ajukan') {
    await ajukanSo(row)
    return
  }
  if (cmd === 'sync') {
    try {
      const res = await mrpStockSisaAction(row.id, { action: 'sync-ppic' })
      ElMessage.success(res.message || 'OK')
      await reload()
    } catch (e) {
      ElMessage.error(e.message || String(e))
    }
    return
  }
  if (cmd === 'approve') {
    try {
      const res = await mrpStockSisaAction(row.id, { action: 'approve' })
      ElMessage.success(res.message || 'OK')
      await reload()
    } catch (e) {
      ElMessage.error(e.message || String(e))
    }
  }
}

onMounted(reload)
</script>

<style scoped>
.w-28 {
  width: 7rem;
}
.w-36 {
  width: 9rem;
}
.w-56 {
  width: 14rem;
}
.max-w-xs {
  max-width: 18rem;
}
.mrp-gs-fg-spec {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.875rem;
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  background: var(--el-fill-color-blank);
}
.mrp-gs-assign-so-table {
  width: 100%;
}
:deep(.mrp-gs-assign-so-table .cell) {
  white-space: normal;
  line-height: 1.35;
  word-break: break-word;
}
</style>
