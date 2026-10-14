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
      <el-table
        :data="rows"
        v-loading="loading"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('common.tableEmpty')"
        @sort-change="onSortChange"
      >
        <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center">
          <template #default="{ $index }">{{ (page - 1) * pageSize + $index + 1 }}</template>
        </el-table-column>
        <el-table-column prop="kode_rencana" :label="t('pages.mrpRencana.code')" min-width="130" sortable="custom" />
        <el-table-column prop="nama_rencana" :label="t('pages.mrpRencana.name')" min-width="160" show-overflow-tooltip />
        <el-table-column prop="tanggal_rencana" :label="t('pages.mrpRencana.date')" width="110" sortable="custom" />
        <el-table-column prop="customers" :label="t('common.customer')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="po_numbers" :label="t('pages.mrpRencana.poNumbers')" min-width="150" show-overflow-tooltip />
        <el-table-column prop="jml_item" :label="t('pages.mrpRencana.itemCount')" width="80" align="right" />
        <el-table-column prop="jml_po" :label="t('pages.mrpRencana.poCount')" width="80" align="right" />
        <el-table-column :label="t('pages.mrpRencana.qtyAllocated')" width="110" align="right">
          <template #default="{ row }">{{ formatQty(row.total_qty_alokasi) }}</template>
        </el-table-column>
        <el-table-column prop="status" :label="t('common.status')" width="100" sortable="custom" />
        <el-table-column :label="t('common.actions')" :width="canUpdate ? 136 : 112" align="center" fixed="right">
          <template #default="{ row, $index }">
            <span :id="$index === 0 ? 'mrp-rencana-tour-detail' : undefined">
              <AdminTableActions
                :show-view="true"
                :show-edit="canUpdate"
                :more-items="[{ command: 'print', label: t('pages.mrpRencana.print'), icon: Printer }]"
                @view="openDetail(row)"
                @edit="openEdit(row)"
                @more="(cmd) => cmd === 'print' && printRencana(row)"
              />
            </span>
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
          @current-change="loadList"
          @size-change="onPageSizeChange"
        />
      </div>
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
        <div v-if="canUpdate" class="mb-3 flex justify-end">
          <el-button type="primary" @click="openEdit(detail.rencana)">
            {{ t('common.edit') }}
          </el-button>
        </div>
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
                  <el-table :data="row.po_allocations || []" border size="small" :empty-text="t('common.tableEmpty')">
                    <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="120" />
                    <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="110" show-overflow-tooltip />
                    <el-table-column prop="lot_no" :label="t('common.lotNo')" min-width="140" show-overflow-tooltip>
                      <template #default="{ row: al }">{{ al.lot_no || '—' }}</template>
                    </el-table-column>
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
            <el-table-column :label="t('common.actions')" width="112" align="center" fixed="right">
              <template #default="{ row, $index }">
                <span :id="$index === 0 ? 'mrp-rencana-tour-detail-actions' : undefined">
                  <AdminTableActions
                    :show-view="!canEditPo"
                    :show-edit="canEditPo"
                    :view-label="t('pages.mrpRencana.viewPo')"
                    :edit-label="t('pages.mrpRencana.editPo')"
                    :more-items="[{ command: 'barcode', label: 'Barcode', icon: Ticket }]"
                    @view="openPo(row)"
                    @edit="openPo(row)"
                    @more="(cmd) => cmd === 'barcode' && showBarcode(row)"
                  />
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </template>
    </el-drawer>

    <el-dialog
      v-model="poOpen"
      :title="canEditPo ? t('pages.mrpRencana.listPo') : t('pages.mrpRencana.viewPoTitle')"
      width="1040px"
      destroy-on-close
      append-to-body
      :z-index="4600"
    >
      <p v-if="currentPoItem" class="text-sm text-slate-500 mb-2">
        {{ t('pages.mrpRencana.poFilterHint', {
          material: spekDisplay(currentPoItem.material_name),
          emboss: spekDisplay(currentPoItem.emboss),
          thickness: spekDisplay(currentPoItem.thickness),
        }) }}
      </p>
      <p v-if="!canEditPo" class="text-sm text-amber-700 mb-2">{{ t('pages.mrpRencana.poViewOnlyHint') }}</p>
      <p v-else class="text-sm text-slate-500 mb-2">{{ t('pages.mrpRencana.replacePoHint') }}</p>
      <el-table
        ref="poTableRef"
        :data="poList"
        border
        size="small"
        class="mrp-rencana-so-table"
        row-key="id"
        @selection-change="onPoSelect"
      >
        <el-table-column
          v-if="canEditPo"
          type="selection"
          width="40"
          fixed="left"
          :selectable="poSelectable"
        />
        <el-table-column
          prop="lot_no"
          :label="t('common.lotNo')"
          min-width="168"
          fixed="left"
          class-name="mrp-lot-col"
          label-class-name="mrp-lot-col-header"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span class="mrp-lot-badge">{{ row.lot_no || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="110" />
        <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="100" show-overflow-tooltip />
        <el-table-column prop="item_name" :label="t('pages.mrpRencana.poItem')" min-width="130" show-overflow-tooltip />
        <el-table-column :label="t('pages.mrpRencana.color')" width="100" show-overflow-tooltip>
          <template #default="{ row }">{{ spekDisplay(row.warna) }}</template>
        </el-table-column>
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
            <el-input
              v-if="canEditPo"
              v-model.number="poQty[row.id]"
              type="number"
              size="small"
              min="0"
              :disabled="!poSelectable(row)"
              @change="onPoQtyChange(row)"
            />
            <span v-else>{{ formatQty(displayPoQty(row)) }}</span>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="poOpen = false">{{ canEditPo ? t('common.cancel') : t('common.close') }}</el-button>
        <el-button v-if="canEditPo" type="primary" :loading="savingPo" @click="savePo">
          {{ t('common.save') }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="barcodeOpen" title="Barcode" width="420px" append-to-body :z-index="4600">
      <div v-if="barcodeData" class="text-center space-y-2">
        <div class="text-2xl font-mono font-bold">{{ barcodeData.barcode }}</div>
        <div class="text-sm">{{ barcodeData.item?.nama_customer }}</div>
        <div class="text-sm text-slate-500">
          {{ barcodeData.item?.thickness }} / {{ barcodeData.item?.color }} / {{ barcodeData.item?.emboss }}
        </div>
      </div>
    </el-dialog>

    <MrpRencanaCreateDialog
      v-model="createOpen"
      :edit-id="editTargetId"
      :tour-open="tourOpen"
      @saved="onDialogSaved"
    />
  </AdminSection>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Plus, Printer, Refresh, Ticket } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import MrpRencanaCreateDialog from './MrpRencanaCreateDialog.vue'
import { printMrpRencana } from '../../../utils/mrpRencanaPrint'
import { can } from '../../../security/permissions'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'
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
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('tanggal_rencana')
const sortDir = ref('desc')
const detailOpen = ref(false)
const detail = ref(null)
const createOpen = ref(false)
const editTargetId = ref(null)
const poOpen = ref(false)
const barcodeOpen = ref(false)
const printingId = ref(null)
const poList = ref([])
const poTableRef = ref(null)
const selectedPoRows = ref([])
const poQty = reactive({})
const selectedPos = ref([])
const currentItemId = ref(null)
const currentPoItem = ref(null)
const barcodeData = ref(null)
const canCreate = computed(() => can('mrpShopfloor', 'create'))
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const canEditPo = computed(() => canUpdate.value)

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
        key: 'createItems',
        target: '#mrp-rencana-tour-create-items',
        placement: 'top',
        panel: 'create',
        title: t('pages.mrpRencana.tour.createItemsTitle'),
        description: t('pages.mrpRencana.tour.createItemsDesc'),
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

function poSelectable(row) {
  if (!canEditPo.value) return false
  return Number(row.qty_outstanding || 0) > 0 || Number(row.already_allocated_qty || 0) > 0
}

function isPoRowSelected(row) {
  return selectedPos.value.some((p) => Number(p.id) === Number(row.id))
}

function onPoQtyChange(row) {
  if (!poSelectable(row)) return
  const qty = Number(poQty[row.id] || 0)
  if (qty > 0 && !isPoRowSelected(row)) {
    poTableRef.value?.toggleRowSelection?.(row, true)
  }
}

function displayPoQty(row) {
  const allocated = Number(row.already_allocated_qty || 0)
  if (allocated > 0) return allocated
  return Number(row.qty_outstanding || 0)
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

async function loadList() {
  loading.value = true
  try {
    const data = await mrpListRencana(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items
    total.value = pageData.total
    page.value = pageData.page
    pageSize.value = pageData.page_size
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    loading.value = false
  }
}

function onPageSizeChange() {
  page.value = 1
  loadList()
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'tanggal_rencana'
  sortDir.value = mapped.sortDir || 'desc'
  page.value = 1
  loadList()
}

/** Sync master PO di background — jangan blokir render daftar rencana. */
let _syncBgInFlight = null
let _syncBgLastAt = 0
const SYNC_BG_MIN_INTERVAL_MS = 60_000

function syncPoBackground() {
  const now = Date.now()
  if (_syncBgInFlight) return
  if (now - _syncBgLastAt < SYNC_BG_MIN_INTERVAL_MS) return
  _syncBgLastAt = now
  _syncBgInFlight = syncPoSilent().finally(() => {
    _syncBgInFlight = null
  })
}

async function reload() {
  // Daftar rencana tidak bergantung pada sync; sync hanya diperlukan saat pilih SO.
  page.value = 1
  await loadList()
  syncPoBackground()
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
  printingId.value = row.id
  try {
    const data = await mrpRencanaPrint(row.id)
    await printMrpRencana(data, {
      title: t('pages.mrpRencana.print'),
      planName: t('pages.mrpRencana.printPlanName'),
      planNo: t('pages.mrpRencana.printPlanNo'),
      emboss: t('pages.mrpRencana.printEmboss'),
      customer: t('pages.mrpRencana.printCustomer'),
      color: t('pages.mrpRencana.printColor'),
      qty: t('pages.mrpRencana.printQty'),
      schedule: t('pages.mrpRencana.printSchedule'),
      cs: t('pages.mrpRencana.printCs'),
      remarks: t('pages.mrpRencana.printRemarks'),
      backer: t('pages.mrpRencana.printBacker'),
    })
  } catch (e) {
    ElMessage.error(e.message || String(e))
  } finally {
    printingId.value = null
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
  if (!row.material_name || !row.color || !row.emboss) {
    ElMessage.warning(t('pages.mrpRencana.poSpekRequired'))
    return
  }
  currentItemId.value = row.id
  currentPoItem.value = row
  selectedPos.value = []
  selectedPoRows.value = []
  try {
    await syncPoSilent()
    const data = await mrpRencanaItemListPo(row.id)
    const listed = new Set()
    poList.value = (data.po_list || []).map((p) => {
      listed.add(Number(p.id))
      return p
    })
    for (const sel of data.selected_po || []) {
      const pid = Number(sel.po_id)
      if (!pid || listed.has(pid)) continue
      poList.value.push({
        id: pid,
        no_po: sel.no_po,
        no_so: sel.no_so,
        customer: sel.customer,
        item_name: sel.item_name,
        warna: sel.warna,
        emboss: sel.emboss,
        tebal: sel.tebal,
        color_swatch: sel.color_swatch,
        qty_order: sel.qty_order,
        qty_outstanding: sel.qty_sisa_alokasi ?? sel.qty_outstanding,
        qty_balance_erp: sel.qty_balance_erp,
        already_allocated_qty: sel.already_allocated_qty ?? sel.qty_proses,
        status: sel.po_status,
      })
      listed.add(pid)
    }
    if (!poList.value.length) {
      ElMessage.info(t('pages.mrpRencana.poListEmpty'))
    }
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
    if (canEditPo.value) {
      await nextTick()
      const table = poTableRef.value
      if (table?.clearSelection) table.clearSelection()
      const preselected = []
      for (const p of poList.value) {
        if (allocatedIds.has(Number(p.id))) {
          table?.toggleRowSelection?.(p, true)
          preselected.push(p)
        }
      }
      selectedPos.value = preselected
    }
  } catch (e) {
    ElMessage.error(e.message || String(e))
  }
}

function onPoSelect(rowsSel) {
  selectedPos.value = rowsSel
}

async function savePo() {
  if (!canEditPo.value) return
  if (!selectedPos.value.length) {
    ElMessage.warning(t('pages.mrpRencana.selectPoRequired'))
    return
  }
  for (const p of selectedPos.value) {
    const qty = Number(poQty[p.id] || 0)
    if (qty <= 0) {
      ElMessage.warning(`${t('pages.mrpRencana.qtyPlan')}: ${p.no_po}`)
      return
    }
    const maxQty = Number(p.qty_outstanding || 0) + Number(p.already_allocated_qty || 0)
    if (qty > maxQty + 1e-9) {
      ElMessage.warning(`${t('pages.mrpRencana.qtyExceeds')}: ${p.no_po}`)
      return
    }
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
  editTargetId.value = null
  createOpen.value = true
}

function openEdit(row) {
  if (!row?.id) return
  editTargetId.value = Number(row.id)
  createOpen.value = true
}

async function onDialogSaved(payload) {
  const savedId = payload?.id ?? editTargetId.value
  editTargetId.value = null
  await reload()
  if (savedId && detailOpen.value && Number(detail.value?.rencana?.id) === Number(savedId)) {
    detail.value = await mrpGetRencana(savedId)
  }
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

<style>
.mrp-lot-badge {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  padding: 1px 7px;
  border-radius: 5px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  color: #64748b;
  font-weight: 500;
  font-size: 12px;
  letter-spacing: 0.01em;
  line-height: 1.35;
  word-break: break-all;
}

.mrp-rencana-so-table .mrp-lot-col {
  background: #f8fafc !important;
  border-left: 2px solid #cbd5e1 !important;
  border-right: 1px solid #e2e8f0 !important;
}

.mrp-rencana-so-table .mrp-lot-col-header {
  background: #f1f5f9 !important;
  color: #64748b !important;
  font-weight: 600 !important;
  border-left: 2px solid #cbd5e1 !important;
  border-right: 1px solid #e2e8f0 !important;
}

.mrp-rencana-so-table .el-table__body tr.hover-row > td.mrp-lot-col,
.mrp-rencana-so-table .el-table__body tr:hover > td.mrp-lot-col {
  background: #f1f5f9 !important;
}
</style>
