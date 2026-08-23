<template>
  <AdminSection :title="t('pages.mrpRencana.title')" :subtitle="t('pages.mrpRencana.subtitle')">
    <template #actions>
      <el-button id="mrp-rencana-tour-guide" @click="startTour">
        {{ t('pages.mrpRencana.tourBtn') }}
      </el-button>
      <el-button
        id="mrp-rencana-tour-refresh"
        :icon="Refresh"
        :loading="loading"
        @click="reload"
      >
        {{ t('common.refresh') }}
      </el-button>
      <el-button
        v-if="canCreate"
        id="mrp-rencana-tour-create"
        type="primary"
        :icon="Plus"
        @click="openCreate"
      >
        {{ t('common.create') }}
      </el-button>
    </template>

    <div id="mrp-rencana-tour-list" class="admin-inner-card">
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table">
        <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
        <el-table-column prop="kode_rencana" :label="t('pages.mrpRencana.code')" min-width="130" />
        <el-table-column prop="nama_rencana" :label="t('pages.mrpRencana.name')" min-width="160" show-overflow-tooltip />
        <el-table-column prop="tanggal_rencana" :label="t('pages.mrpRencana.date')" width="110" />
        <el-table-column prop="customers" :label="t('common.customer')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="po_numbers" :label="t('pages.mrpRencana.poNumbers')" min-width="150" show-overflow-tooltip />
        <el-table-column prop="jml_item" :label="t('pages.mrpRencana.itemCount')" width="80" align="right" />
        <el-table-column prop="jml_po" :label="t('pages.mrpRencana.poCount')" width="80" align="right" />
        <el-table-column :label="t('pages.mrpRencana.qtyAllocated')" width="110" align="right">
          <template #default="{ row }">{{ formatQty(row.total_qty_alokasi) }}</template>
        </el-table-column>
        <el-table-column prop="status" :label="t('common.status')" width="100" />
        <el-table-column :label="t('common.actions')" width="150" fixed="right">
          <template #default="{ row, $index }">
            <el-button
              :id="$index === 0 ? 'mrp-rencana-tour-detail' : undefined"
              link
              type="primary"
              @click="openDetail(row)"
            >
              {{ t('common.detail') }}
            </el-button>
            <el-button link @click="printRencana(row)">{{ t('pages.mrpRencana.print') }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-tour
      v-model="tourOpen"
      v-model:current="tourCurrent"
      :z-index="5000"
      @change="onTourChange"
      @close="onTourEnd"
      @finish="onTourEnd"
    >
      <el-tour-step
        v-for="step in tourSteps"
        :key="step.key"
        :target="step.target"
        :placement="step.placement || 'bottom'"
        :title="step.title"
        :description="step.description"
      />
    </el-tour>

    <el-drawer
      id="mrp-rencana-tour-detail-drawer"
      v-model="detailOpen"
      size="72%"
      :title="detail?.rencana?.nama_rencana || t('common.detail')"
      append-to-body
      :z-index="3000"
    >
      <template v-if="detail">
        <div id="mrp-rencana-tour-detail-header" class="mrp-rencana-detail-summary mb-4">
          <p class="text-sm text-slate-500 mb-2">
            {{ detail.rencana.kode_rencana }} · {{ detail.rencana.tanggal_rencana }} · {{ detail.rencana.status }}
          </p>
          <div class="mrp-rencana-detail-stats">
            <div class="mrp-rencana-detail-stat">
              <span class="mrp-rencana-detail-stat__label">{{ t('pages.mrpRencana.itemCount') }}</span>
              <span class="mrp-rencana-detail-stat__value">{{ detail.summary?.jml_item ?? detail.items?.length ?? 0 }}</span>
            </div>
            <div class="mrp-rencana-detail-stat">
              <span class="mrp-rencana-detail-stat__label">{{ t('pages.mrpRencana.poCount') }}</span>
              <span class="mrp-rencana-detail-stat__value">{{ detail.summary?.jml_po ?? 0 }}</span>
            </div>
            <div class="mrp-rencana-detail-stat">
              <span class="mrp-rencana-detail-stat__label">{{ t('pages.mrpRencana.qtyAllocated') }}</span>
              <span class="mrp-rencana-detail-stat__value">{{ formatQty(detail.summary?.total_qty_alokasi) }}</span>
            </div>
            <div class="mrp-rencana-detail-stat mrp-rencana-detail-stat--wide">
              <span class="mrp-rencana-detail-stat__label">{{ t('common.customer') }}</span>
              <span class="mrp-rencana-detail-stat__value mrp-rencana-detail-stat__value--text">
                {{ detail.summary?.customers || '—' }}
              </span>
            </div>
            <div class="mrp-rencana-detail-stat mrp-rencana-detail-stat--wide">
              <span class="mrp-rencana-detail-stat__label">{{ t('pages.mrpRencana.poNumbers') }}</span>
              <span class="mrp-rencana-detail-stat__value mrp-rencana-detail-stat__value--text">
                {{ detail.summary?.po_numbers || '—' }}
              </span>
            </div>
          </div>
        </div>

        <div id="mrp-rencana-tour-detail-items">
          <h4 class="text-sm font-semibold mb-2">{{ t('pages.mrpRencana.items') }}</h4>
          <el-table :data="detail.items || []" border size="small" row-key="id">
            <el-table-column type="expand">
              <template #default="{ row }">
                <div class="mrp-rencana-alloc-wrap">
                  <p class="text-xs text-slate-500 mb-2">{{ t('pages.mrpRencana.poAllocationDetail') }}</p>
                  <el-table :data="row.po_allocations || []" border size="small" empty-text="—">
                    <el-table-column prop="no_po" label="PO" min-width="120" />
                    <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="110" show-overflow-tooltip />
                    <el-table-column prop="item_name" :label="t('pages.mrpRencana.poItem')" min-width="150" show-overflow-tooltip />
                    <el-table-column :label="t('pages.mrpRencana.color')" width="100" show-overflow-tooltip>
                      <template #default="{ row: al }">{{ spekDisplay(al.warna) }}</template>
                    </el-table-column>
                    <el-table-column :label="t('pages.mrpRencana.emboss')" width="90" show-overflow-tooltip>
                      <template #default="{ row: al }">{{ spekDisplay(al.emboss) }}</template>
                    </el-table-column>
                    <el-table-column :label="t('pages.mrpRencana.swatch')" width="90" show-overflow-tooltip>
                      <template #default="{ row: al }">{{ spekDisplay(al.color_swatch) }}</template>
                    </el-table-column>
                    <el-table-column prop="source_detail_id" :label="t('pages.mrpRencana.erpLine')" width="90" />
                    <el-table-column :label="t('pages.mrpRencana.qtyOrder')" width="90" align="right">
                      <template #default="{ row: al }">{{ formatQty(al.qty_order) }}</template>
                    </el-table-column>
                    <el-table-column :label="t('pages.mrpRencana.qtyAllocated')" width="100" align="right">
                      <template #default="{ row: al }">{{ formatQty(al.qty_proses) }}</template>
                    </el-table-column>
                    <el-table-column :label="t('pages.mrpRencana.qtyAllocatable')" width="120" align="right">
                      <template #default="{ row: al }">{{ formatQty(al.qty_sisa_alokasi) }}</template>
                    </el-table-column>
                    <el-table-column :label="t('pages.mrpRencana.qtyBalanceErp')" width="110" align="right">
                      <template #default="{ row: al }">{{ formatQty(al.qty_balance_erp) }}</template>
                    </el-table-column>
                    <el-table-column prop="po_status" :label="t('common.status')" width="100" />
                  </el-table>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="kode_rencana_item" label="Item" min-width="120" />
            <el-table-column prop="kode_lot_wip" label="WIP" min-width="120" />
            <el-table-column prop="nama_customer" :label="t('common.customer')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="material_name" label="Material" min-width="130" show-overflow-tooltip />
            <el-table-column :label="t('pages.mrpRencana.thickness')" width="90">
              <template #default="{ row }">{{ spekDisplay(row.thickness) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.color')" width="110" show-overflow-tooltip>
              <template #default="{ row }">{{ spekDisplay(row.color) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.emboss')" width="100" show-overflow-tooltip>
              <template #default="{ row }">{{ spekDisplay(row.emboss) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpRencana.swatch')" width="90" show-overflow-tooltip>
              <template #default="{ row }">{{ spekDisplay(row.color_swatch) }}</template>
            </el-table-column>
            <el-table-column prop="po_numbers" :label="t('pages.mrpRencana.poNumbers')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="jml_po" :label="t('pages.mrpRencana.poCount')" width="70" align="right" />
            <el-table-column :label="t('pages.mrpRencana.qtyAllocated')" width="100" align="right">
              <template #default="{ row }">{{ formatQty(row.total_qty_so) }}</template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="140" fixed="right">
              <template #default="{ row, $index }">
                <span :id="$index === 0 ? 'mrp-rencana-tour-detail-actions' : undefined">
                  <el-button link type="primary" @click="openPo(row)">PO</el-button>
                  <el-button link @click="showBarcode(row)">Barcode</el-button>
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </template>
    </el-drawer>

    <el-dialog
      v-model="poOpen"
      :title="t('pages.mrpRencana.listPo')"
      width="920px"
      destroy-on-close
      append-to-body
      :z-index="4600"
    >
      <p class="text-sm text-slate-500 mb-2">{{ t('pages.mrpRencana.replacePoHint') }}</p>
      <el-table
        v-if="selectedPoRows.length"
        :data="selectedPoRows"
        border
        size="small"
        class="mb-3"
      >
        <el-table-column prop="no_po" :label="t('pages.mrpRencana.currentlyAllocated')" min-width="120" />
        <el-table-column prop="item_name" :label="t('pages.mrpRencana.poItem')" min-width="140" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpRencana.qtyAllocated')" width="110" align="right">
          <template #default="{ row }">{{ formatQty(row.qty_proses) }}</template>
        </el-table-column>
      </el-table>
      <el-table
        ref="poTableRef"
        :data="poList"
        border
        size="small"
        row-key="id"
        @selection-change="onPoSelect"
      >
        <el-table-column type="selection" width="40" />
        <el-table-column prop="no_po" label="PO" min-width="110" />
        <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="100" show-overflow-tooltip />
        <el-table-column prop="item_name" :label="t('pages.mrpRencana.poItem')" min-width="130" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpRencana.emboss')" width="80">
          <template #default="{ row }">{{ spekDisplay(row.emboss) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpRencana.swatch')" width="80">
          <template #default="{ row }">{{ spekDisplay(row.color_swatch) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpRencana.qtyOrder')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.qty_order) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpRencana.qtyAllocatable')" width="120" align="right">
          <template #default="{ row }">{{ formatQty(row.qty_outstanding) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpRencana.qtyBalanceErp')" width="110" align="right">
          <template #default="{ row }">{{ formatQty(row.qty_balance_erp) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpRencana.qtyPlan')" width="120">
          <template #default="{ row }">
            <el-input v-model.number="poQty[row.id]" type="number" size="small" />
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="poOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="savingPo" @click="savePo">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="barcodeOpen" title="Barcode" width="420px" append-to-body :z-index="4600">
      <div v-if="barcodeData" class="text-center space-y-2">
        <div class="text-2xl font-mono font-bold">{{ barcodeData.barcode }}</div>
        <div class="text-sm">{{ barcodeData.item?.kode_rencana_item }} · {{ barcodeData.item?.nama_customer }}</div>
        <div class="text-sm text-slate-500">
          {{ barcodeData.item?.thickness }} / {{ barcodeData.item?.color }} / {{ barcodeData.item?.emboss }}
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="printOpen" :title="t('pages.mrpRencana.print')" width="640px" append-to-body :z-index="4600">
      <template v-if="printData">
        <h3 class="font-semibold mb-2">{{ printData.rencana?.nama_rencana }} ({{ printData.rencana?.kode_rencana }})</h3>
        <el-table :data="printData.items || []" border size="small">
          <el-table-column prop="kode_rencana_item" label="Item" />
          <el-table-column prop="nama_customer" :label="t('common.customer')" />
          <el-table-column prop="material_name" label="Material" />
          <el-table-column prop="total_qty_so" :label="t('pages.mrpRencana.qtyAllocated')" width="110" />
          <el-table-column prop="schedule_text" :label="t('pages.mrpRencana.soRef')" min-width="120" />
        </el-table>
      </template>
    </el-dialog>

    <MrpRencanaCreateDialog
      v-model="createOpen"
      :tour-open="tourOpen"
      @saved="reload"
    />
  </AdminSection>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import MrpRencanaCreateDialog from './MrpRencanaCreateDialog.vue'
import { can } from '../../../security/permissions'
import {
  mrpGetRencana,
  mrpListRencana,
  mrpRencanaItemBarcode,
  mrpRencanaItemListPo,
  mrpRencanaItemSavePo,
  mrpRencanaPrint,
  mrpSyncPo,
} from '../../../api/client'

const TOUR_STORAGE_KEY = 'mrp-rencana-tour-v1'

const { t } = useI18n()
const loading = ref(false)
const savingPo = ref(false)
const tourOpen = ref(false)
const tourCurrent = ref(0)
const tourDriven = ref(false)
const rows = ref([])
const detailOpen = ref(false)
const detail = ref(null)
const createOpen = ref(false)
const poOpen = ref(false)
const barcodeOpen = ref(false)
const printOpen = ref(false)
const poList = ref([])
const poTableRef = ref(null)
const selectedPoRows = ref([])
const poQty = reactive({})
const selectedPos = ref([])
const currentItemId = ref(null)
const barcodeData = ref(null)
const printData = ref(null)
const canCreate = computed(() => can('mrpShopfloor', 'create'))

const tourSteps = computed(() => {
  const steps = [
    {
      key: 'welcome',
      target: undefined,
      placement: 'bottom',
      panel: null,
      title: t('pages.mrpRencana.tour.welcomeTitle'),
      description: t('pages.mrpRencana.tour.welcomeDesc'),
    },
    {
      key: 'refresh',
      target: '#mrp-rencana-tour-refresh',
      placement: 'bottom',
      panel: null,
      title: t('pages.mrpRencana.tour.refreshTitle'),
      description: t('pages.mrpRencana.tour.refreshDesc'),
    },
  ]
  if (canCreate.value) {
    steps.push(
      {
        key: 'createBtn',
        target: '#mrp-rencana-tour-create',
        placement: 'bottom',
        panel: null,
        title: t('pages.mrpRencana.tour.createTitle'),
        description: t('pages.mrpRencana.tour.createDesc'),
      },
      {
        key: 'createName',
        target: '#mrp-rencana-tour-create-name',
        placement: 'bottom',
        panel: 'create',
        title: t('pages.mrpRencana.tour.createNameTitle'),
        description: t('pages.mrpRencana.tour.createNameDesc'),
      },
      {
        key: 'createDate',
        target: '#mrp-rencana-tour-create-date',
        placement: 'bottom',
        panel: 'create',
        title: t('pages.mrpRencana.tour.createDateTitle'),
        description: t('pages.mrpRencana.tour.createDateDesc'),
      },
      {
        key: 'createItems',
        target: '#mrp-rencana-tour-create-items',
        placement: 'top',
        panel: 'create',
        title: t('pages.mrpRencana.tour.createItemsTitle'),
        description: t('pages.mrpRencana.tour.createItemsDesc'),
      },
      {
        key: 'createSave',
        target: '#mrp-rencana-tour-create-save',
        placement: 'top',
        panel: 'create',
        title: t('pages.mrpRencana.tour.createSaveTitle'),
        description: t('pages.mrpRencana.tour.createSaveDesc'),
      },
    )
  }
  steps.push(
    {
      key: 'list',
      target: '#mrp-rencana-tour-list',
      placement: 'top',
      panel: null,
      title: t('pages.mrpRencana.tour.listTitle'),
      description: t('pages.mrpRencana.tour.listDesc'),
    },
    {
      key: 'detailBtn',
      target: rows.value.length ? '#mrp-rencana-tour-detail' : undefined,
      placement: 'left',
      panel: null,
      title: t('pages.mrpRencana.tour.detailBtnTitle'),
      description: rows.value.length
        ? t('pages.mrpRencana.tour.detailBtnDesc')
        : t('pages.mrpRencana.tour.detailBtnEmptyDesc'),
    },
    {
      key: 'detailHeader',
      target: rows.value.length ? '#mrp-rencana-tour-detail-header' : undefined,
      placement: 'bottom',
      panel: 'detail',
      title: t('pages.mrpRencana.tour.detailHeaderTitle'),
      description: t('pages.mrpRencana.tour.detailHeaderDesc'),
    },
    {
      key: 'detailItems',
      target: rows.value.length ? '#mrp-rencana-tour-detail-items' : undefined,
      placement: 'left',
      panel: 'detail',
      title: t('pages.mrpRencana.tour.detailItemsTitle'),
      description: t('pages.mrpRencana.tour.detailItemsDesc'),
    },
    {
      key: 'detailActions',
      target: () =>
        document.querySelector('#mrp-rencana-tour-detail-actions') ||
        document.querySelector('#mrp-rencana-tour-detail-items'),
      placement: 'left',
      panel: 'detail',
      title: t('pages.mrpRencana.tour.detailActionsTitle'),
      description: t('pages.mrpRencana.tour.detailActionsDesc'),
    },
    {
      key: 'next',
      target: '#mrp-rencana-tour-guide',
      placement: 'bottom',
      panel: null,
      title: t('pages.mrpRencana.tour.nextTitle'),
      description: t('pages.mrpRencana.tour.nextDesc'),
    },
  )
  return steps
})

function formatQty(v) {
  const n = Number(v)
  if (!Number.isFinite(n)) return '—'
  return Number.isInteger(n) ? String(n) : n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function spekDisplay(v) {
  const s = (v == null ? '' : String(v)).trim()
  return s || '—'
}

function markTourSeen() {
  try {
    localStorage.setItem(TOUR_STORAGE_KEY, '1')
  } catch {
    /* ignore */
  }
}

function closeTourPanels() {
  if (!tourDriven.value) return
  createOpen.value = false
  detailOpen.value = false
  poOpen.value = false
  barcodeOpen.value = false
}

async function prepareTourStep(index) {
  const step = tourSteps.value[index]
  if (!step) return
  tourDriven.value = true
  if (step.panel === 'create') {
    detailOpen.value = false
    if (!createOpen.value) await openCreate()
    await nextTick()
    await new Promise((r) => setTimeout(r, 120))
  } else if (step.panel === 'detail') {
    createOpen.value = false
    if (rows.value[0]) {
      const needOpen =
        !detailOpen.value || detail.value?.rencana?.id !== rows.value[0].id
      if (needOpen) await openDetail(rows.value[0])
      await nextTick()
      await new Promise((r) => setTimeout(r, 160))
    }
  } else {
    createOpen.value = false
    if (step.key !== 'detailBtn') detailOpen.value = false
  }
}

async function onTourChange(current) {
  await prepareTourStep(current)
}

async function startTour() {
  tourCurrent.value = 0
  tourOpen.value = true
  await nextTick()
  await prepareTourStep(0)
}

function onTourEnd() {
  markTourSeen()
  closeTourPanels()
  tourDriven.value = false
  tourCurrent.value = 0
}

async function syncPoSilent() {
  try {
    await mrpSyncPo()
  } catch (e) {
    ElMessage.warning(e.message || String(e))
  }
}

async function reload() {
  loading.value = true
  try {
    await syncPoSilent()
    rows.value = await mrpListRencana()
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

async function openDetail(row) {
  try {
    detail.value = await mrpGetRencana(row.id)
    detailOpen.value = true
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

async function printRencana(row) {
  try {
    printData.value = await mrpRencanaPrint(row.id)
    printOpen.value = true
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

async function showBarcode(row) {
  try {
    barcodeData.value = await mrpRencanaItemBarcode(row.id)
    barcodeOpen.value = true
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

async function openPo(row) {
  currentItemId.value = row.id
  selectedPos.value = []
  selectedPoRows.value = []
  try {
    await syncPoSilent()
    const data = await mrpRencanaItemListPo(row.id)
    poList.value = data.po_list || []
    selectedPoRows.value = data.selected_po || []
    const allocatedIds = new Set(
      selectedPoRows.value.map((s) => Number(s.po_id)).filter((id) => Number.isFinite(id)),
    )
    for (const p of poList.value) {
      const already = Number(p.already_allocated_qty || 0)
      if (already > 0) {
        poQty[p.id] = already
      } else {
        poQty[p.id] = Number(p.qty_outstanding || 0)
      }
    }
    for (const s of selectedPoRows.value) {
      if (s.po_id != null && poQty[s.po_id] == null) {
        poQty[s.po_id] = Number(s.already_allocated_qty ?? s.qty_proses ?? 0)
      }
    }
    poOpen.value = true
    await nextTick()
    const table = poTableRef.value
    if (table?.clearSelection) table.clearSelection()
    for (const p of poList.value) {
      if (allocatedIds.has(Number(p.id))) {
        table?.toggleRowSelection?.(p, true)
      }
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

function onPoSelect(rowsSel) {
  selectedPos.value = rowsSel
}

async function savePo() {
  if (!selectedPos.value.length) {
    ElMessage.warning(t('pages.mrpRencana.selectPoRequired'))
    return
  }
  savingPo.value = true
  try {
    await mrpRencanaItemSavePo(currentItemId.value, {
      pos: selectedPos.value.map((p) => ({ po_id: p.id, qty: poQty[p.id] || 0 })),
    })
    ElMessage.success(t('common.saved'))
    poOpen.value = false
    if (detail.value?.rencana?.id) {
      detail.value = await mrpGetRencana(detail.value.rencana.id)
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    savingPo.value = false
  }
}

function openCreate() {
  createOpen.value = true
}

onMounted(async () => {
  await reload()
  await nextTick()
  try {
    if (!localStorage.getItem(TOUR_STORAGE_KEY)) {
      await startTour()
    }
  } catch {
    /* ignore */
  }
})
</script>

<style scoped>
.mrp-rencana-detail-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.6rem;
}
.mrp-rencana-detail-stat {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.55rem 0.7rem;
  background: var(--el-fill-color-blank);
}
.mrp-rencana-detail-stat--wide {
  grid-column: span 3;
}
.mrp-rencana-detail-stat__label {
  display: block;
  font-size: 0.72rem;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.15rem;
}
.mrp-rencana-detail-stat__value {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.mrp-rencana-detail-stat__value--text {
  font-size: 0.88rem;
  font-weight: 500;
  line-height: 1.35;
  word-break: break-word;
}
.mrp-rencana-alloc-wrap {
  padding: 0.35rem 0.75rem 0.75rem;
}
@media (max-width: 900px) {
  .mrp-rencana-detail-stats {
    grid-template-columns: 1fr 1fr;
  }
  .mrp-rencana-detail-stat--wide {
    grid-column: span 2;
  }
}
</style>
