<template>
  <AdminSection :title="t('pages.mrpGudangFg.title')" :subtitle="t('pages.mrpGudangFg.subtitle')">
    <template #actions>
      <el-button v-if="canUpdate" type="primary" @click="openScanSj">
        {{ t('pages.mrpGudangFg.scanSjBtn') }}
      </el-button>
      <el-button :icon="Refresh" :loading="loading" @click="reload">{{ t('common.refresh') }}</el-button>
    </template>

    <div v-if="failedBridgeCount" class="mb-3">
      <el-alert
        type="warning"
        :closable="false"
        show-icon
        :title="t('pages.mrpGudangFg.bridgeFailedAlert', { n: failedBridgeCount })"
      />
    </div>

    <div v-if="canUpdate" class="admin-inner-card mb-4">
      <div class="admin-inner-card__body">
        <h3 class="admin-inner-card__title mb-1">{{ t('pages.mrpGudangFg.outTitle') }}</h3>
        <p class="text-sm text-slate-500 mb-3">{{ t('pages.mrpGudangFg.outHint') }}</p>
        <div class="flex gap-2 flex-wrap items-center">
          <el-input
            v-model="outForm.kode_packing"
            :placeholder="t('pages.mrpGudangFg.outPlaceholder')"
            class="max-w-xs"
            clearable
            @keyup.enter="doOut"
          />
          <el-input
            v-model="outForm.keterangan"
            :placeholder="t('common.notes')"
            class="max-w-xs"
            clearable
            @keyup.enter="doOut"
          />
          <el-button type="danger" :loading="outing" @click="doOut">
            {{ t('pages.mrpGudangFg.outBtn') }}
          </el-button>
        </div>
      </div>
    </div>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.mrpGudangFg.listTitle') }}</h3>
          <p class="admin-inner-card__sub">
            {{ t('pages.mrpGudangFg.statsLine', { inStock: stats.inStock, out: stats.out, failed: stats.failed }) }}
          </p>
        </div>
        <div class="flex gap-2 flex-wrap items-center">
          <el-radio-group v-model="statusFilter" size="small" @change="reload">
            <el-radio-button value="">{{ t('pages.mrpGudangFg.filterAll') }}</el-radio-button>
            <el-radio-button value="in_stock">{{ t('pages.mrpGudangFg.statusInStock') }}</el-radio-button>
            <el-radio-button value="out">{{ t('pages.mrpGudangFg.statusOut') }}</el-radio-button>
            <el-radio-button value="repacked">{{ t('pages.mrpGudangFg.statusRepacked') }}</el-radio-button>
          </el-radio-group>
          <el-input
            v-model="search" @keyup.enter="() => { page = 1; reload() }" @clear="() => { page = 1; reload() }"
            clearable
            size="small"
            class="w-56"
            :placeholder="t('pages.mrpGudangFg.searchPlaceholder')"
          />
        </div>
      </div>

      <el-table
        :data="rows"
        v-loading="loading"
        @sort-change="onSortChange"
        border
        stripe
        size="small"
        class="admin-table"
        :empty-text="t('common.tableEmpty')"
      >
        <el-table-column type="index" width="56" :label="t('common.noLabel')" align="center" />
        <el-table-column
          prop="kode_packing" sortable="custom"
          :label="t('pages.mrpPacking.kodePacking')"
          min-width="140"
          show-overflow-tooltip
        />
        <el-table-column prop="kode_wip" label="WIP" min-width="120" show-overflow-tooltip />
        <el-table-column :label="t('common.customer')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ dash(row.customer) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpPacking.pieces')" width="90" align="right">
          <template #default="{ row }">{{ formatQty(row.total_lembar) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpPacking.quantity')" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.total_ukuran) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.status')" width="150" align="center">
          <template #default="{ row }">
            <div class="flex flex-col items-center gap-1">
              <el-tag :type="statusType(row.status)" size="small" effect="plain">
                {{ statusLabel(row.status) }}
              </el-tag>
              <el-tag v-if="row.packing_status === 'in_progress'" type="warning" size="small" effect="plain">
                {{ t('pages.mrpGudangFg.packingOpen') }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpGudangFg.erpDelivery')" min-width="170">
          <template #default="{ row }">
            <el-button
              v-if="row.erp_delivery_id"
              link
              type="primary"
              @click="goDelivery(row.erp_delivery_id)"
            >
              {{ row.erp_delivery_number || `#${row.erp_delivery_id}` }}
            </el-button>
            <el-tooltip
              v-else-if="row.bridge_status === 'failed'"
              :content="row.bridge_error || t('pages.mrpGudangFg.bridgeFailed')"
              placement="top"
            >
              <el-tag type="danger" size="small" effect="plain">
                {{ t('pages.mrpGudangFg.bridgeFailed') }}
              </el-tag>
            </el-tooltip>
            <span v-else class="text-gray-400">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpGudangFg.dateIn')" width="120">
          <template #default="{ row }">{{ formatDate(row.date_in) }}</template>
        </el-table-column>
        <el-table-column :label="t('pages.mrpGudangFg.dateOut')" width="120">
          <template #default="{ row }">{{ formatDate(row.date_out) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <AdminTableActions
              :show-view="true"
              :show-edit="canUpdate && row.status === 'in_stock' && !!row.packing_id"
              :more-items="fgMoreItems(row)"
              @view="openDetail(row)"
              @edit="goEdit(row)"
              @more="(cmd) => onFgMore(cmd, row)"
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

    <el-dialog
      v-model="scanSjOpen"
      :title="t('pages.mrpGudangFg.scanSjTitle')"
      width="780px"
      destroy-on-close
      @closed="resetScanSj"
    >
      <p class="text-sm text-slate-500 mt-0 mb-3">{{ t('pages.mrpGudangFg.scanSjHint') }}</p>

      <div class="mb-4">
        <div class="text-xs uppercase tracking-wide text-slate-500 mb-1">
          {{ t('pages.mrpGudangFg.scanSjCustomer') }}
        </div>
        <el-select
          v-model="sjCustomerName"
          filterable
          clearable
          class="w-full"
          :loading="scanSjPendingLoading"
          :placeholder="t('pages.mrpGudangFg.scanSjCustomerPlaceholder')"
          @change="onSjCustomerChange"
        >
          <el-option
            v-for="c in sjPendingCustomers"
            :key="c.customer"
            :label="c.customer"
            :value="c.customer"
          />
        </el-select>
      </div>

      <div v-if="sjCustomerName" class="mb-4">
        <h4 class="font-semibold mb-2">{{ t('pages.mrpGudangFg.scanSjPick') }}</h4>
        <el-table
          :data="sjDeliveryOptions"
          v-loading="scanSjLoading"
          border
          stripe
          size="small"
          highlight-current-row
          class="admin-table mb-2"
          :row-class-name="sjDeliveryRowClass"
          :empty-text="t('pages.mrpGudangFg.sjNoPending')"
          @row-click="onSjDeliveryClick"
        >
          <el-table-column
            prop="delivery_number"
            :label="t('pages.mrpGudangFg.scanSjPick')"
            min-width="180"
            show-overflow-tooltip
          />
          <el-table-column
            :label="t('pages.mrpGudangFg.scanSjRollCol')"
            width="110"
            align="right"
          >
            <template #default="{ row }">{{ row.roll_count ?? '—' }}</template>
          </el-table-column>
        </el-table>
      </div>

      <template v-if="sjSession">
        <div class="mrp-fg-sj-meta mb-3">
          <div class="mrp-fg-sj-meta__item">
            <span class="mrp-fg-sj-meta__label">SJ</span>
            <span>{{ dash(sjSession.delivery_number) }}</span>
          </div>
          <div class="mrp-fg-sj-meta__item">
            <span class="mrp-fg-sj-meta__label">{{ t('common.customer') }}</span>
            <span>{{ dash(sjSession.customer) }}</span>
          </div>
        </div>

        <div class="mrp-fg-sj-progress mb-2">
          {{ sjScannedCount }} / {{ sjTotalCount }}
        </div>

        <h4 class="font-semibold mb-2">{{ t('pages.mrpGudangFg.scanSjItemList') }}</h4>
        <el-table
          :data="sjSession.rolls"
          border
          stripe
          size="small"
          class="admin-table mb-4 mrp-fg-sj-table"
          :row-class-name="sjRowClassName"
          :empty-text="t('common.tableEmpty')"
        >
          <el-table-column width="52" align="center">
            <template #default="{ row }">
              <el-icon v-if="isSjItemDone(row)" class="text-emerald-600"><CircleCheckFilled /></el-icon>
              <el-icon v-else class="text-slate-300"><CircleCheck /></el-icon>
            </template>
          </el-table-column>
          <el-table-column
            :label="t('pages.mrpGudangFg.scanSjItemList')"
            min-width="200"
            show-overflow-tooltip
          >
            <template #default="{ row }">{{ sjRollLabel(row) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpPacking.pieces')" width="80" align="right">
            <template #default="{ row }">{{ formatQty(row.lembar) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpPacking.quantity')" width="90" align="right">
            <template #default="{ row }">{{ formatQty(row.ukuran) }}</template>
          </el-table-column>
          <el-table-column :label="t('common.status')" width="130" align="center">
            <template #default="{ row }">
              <el-tag
                :type="isSjItemDone(row) ? 'success' : 'info'"
                size="small"
                effect="plain"
              >
                {{
                  row.fg_status === 'out'
                    ? t('pages.mrpGudangFg.sjFgAlreadyOut')
                    : isSjItemDone(row)
                      ? t('pages.mrpGudangFg.sjFgVerified')
                      : t('pages.mrpGudangFg.sjFgPending')
                }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <h4 class="font-semibold mb-2">{{ t('pages.mrpGudangFg.scanFgTitle') }}</h4>
        <p class="text-sm text-slate-500 mt-0 mb-2">{{ t('pages.mrpGudangFg.scanFgHint') }}</p>
        <el-input
          ref="fgScanInput"
          v-model="fgScanCode"
          :placeholder="t('pages.mrpGudangFg.scanFgPlaceholder')"
          class="w-full mb-2"
          clearable
          @keyup.enter="matchFgScan"
        />
      </template>

      <template #footer>
        <el-button @click="scanSjOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button
          type="primary"
          :loading="scanSjSaving"
          :disabled="!canSaveSj"
          @click="saveSjScan"
        >
          {{ t('pages.mrpGudangFg.sjSave') }}
        </el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="detailOpen" size="48%" :title="detail?.fg?.kode_packing || t('common.detail')">
      <template v-if="detail?.fg">
        <el-alert
          v-if="detail.fg.bridge_status === 'failed'"
          class="mb-3"
          type="error"
          :closable="false"
          show-icon
          :title="t('pages.mrpGudangFg.bridgeFailed')"
          :description="detail.fg.bridge_error || ''"
        />

        <div class="mrp-fg-meta mb-4">
          <div class="mrp-fg-meta__item">
            <span class="mrp-fg-meta__label">WIP</span>
            <span>{{ dash(detail.fg.kode_wip) }}</span>
          </div>
          <div class="mrp-fg-meta__item">
            <span class="mrp-fg-meta__label">{{ t('common.customer') }}</span>
            <span>{{ dash(detail.fg.customer) }}</span>
          </div>
          <div class="mrp-fg-meta__item">
            <span class="mrp-fg-meta__label">{{ t('common.status') }}</span>
            <el-tag :type="statusType(detail.fg.status)" size="small" effect="plain">
              {{ statusLabel(detail.fg.status) }}
            </el-tag>
          </div>
          <div class="mrp-fg-meta__item">
            <span class="mrp-fg-meta__label">{{ t('pages.mrpPacking.pieces') }} / {{ t('pages.mrpGudangFg.qtyActual') }}</span>
            <span>{{ formatQty(detail.fg.total_lembar) }} / {{ formatQty(detail.fg.total_ukuran) }}</span>
          </div>
          <div class="mrp-fg-meta__item">
            <span class="mrp-fg-meta__label">{{ t('pages.mrpGudangFg.qtyAlloc') }}</span>
            <span>{{ formatQty(detailQtyAlloc) }}</span>
          </div>
          <div v-if="detailQtyDelta != null && Math.abs(detailQtyDelta) > 1e-9" class="mrp-fg-meta__item">
            <span class="mrp-fg-meta__label">{{ t('pages.mrpGudangFg.qtyDelta') }}</span>
            <span :class="detailQtyDelta > 0 ? 'text-amber-700 font-semibold' : 'text-rose-700 font-semibold'">
              {{ detailQtyDelta > 0 ? '+' : '' }}{{ formatQty(detailQtyDelta) }}
            </span>
          </div>
          <div class="mrp-fg-meta__item">
            <span class="mrp-fg-meta__label">{{ t('pages.mrpGudangFg.dateIn') }}</span>
            <span>{{ formatDateTime(detail.fg.date_in) }}</span>
          </div>
          <div v-if="detail.fg.date_out" class="mrp-fg-meta__item">
            <span class="mrp-fg-meta__label">{{ t('pages.mrpGudangFg.dateOut') }}</span>
            <span>{{ formatDateTime(detail.fg.date_out) }} — {{ dash(detail.fg.keterangan_out) }}</span>
          </div>
          <div v-if="detail.fg.erp_delivery_id" class="mrp-fg-meta__item">
            <span class="mrp-fg-meta__label">{{ t('pages.mrpGudangFg.erpDelivery') }}</span>
            <el-button link type="primary" @click="goDelivery(detail.fg.erp_delivery_id)">
              {{ detail.fg.erp_delivery_number || `#${detail.fg.erp_delivery_id}` }}
            </el-button>
          </div>
        </div>

        <div v-if="canUpdate && detail.fg.status === 'in_stock'" class="mb-4 flex gap-2 flex-wrap">
          <el-button
            v-if="detail.fg.packing_id"
            type="warning"
            size="small"
            @click="goEdit(detail.fg)"
          >
            {{ t('common.edit') }}
          </el-button>
          <el-button type="danger" size="small" :loading="outing" @click="outFromDetail">
            {{ t('pages.mrpGudangFg.outBtn') }}
          </el-button>
          <el-button
            v-if="canRepackFg(detail.fg, detail.packing?.status)"
            size="small"
            @click="openRepack(detail.fg, detail.packing?.status)"
          >
            {{ t('pages.mrpGudangFg.repack') }}
          </el-button>
        </div>

        <h4 class="mb-2 font-semibold">{{ t('pages.mrpPacking.rolls') }}</h4>
        <el-table :data="detail.rolls || []" border size="small" class="mb-4" :empty-text="t('common.tableEmpty')">
          <el-table-column prop="roll_no" :label="t('pages.mrpPacking.artNo')" width="70" />
          <el-table-column :label="t('pages.mrpPacking.pieces')" align="right">
            <template #default="{ row }">{{ formatQty(row.lembar) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpPacking.quantity')" align="right">
            <template #default="{ row }">{{ formatQty(row.ukuran) }}</template>
          </el-table-column>
        </el-table>

        <h4 class="mb-2 font-semibold">{{ t('pages.mrpPacking.poSection') }}</h4>
        <el-table :data="detail.packing_pos || []" border size="small" class="mb-4" :empty-text="t('common.tableEmpty')">
          <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="110" show-overflow-tooltip />
          <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="90" show-overflow-tooltip />
          <el-table-column prop="lot_no" :label="t('common.lotNo')" min-width="130" show-overflow-tooltip>
            <template #default="{ row }">{{ dash(row.lot_no || row.lot_number) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpPacking.poItem')" min-width="140" show-overflow-tooltip>
            <template #default="{ row }">{{ dash(row.item_name) }}</template>
          </el-table-column>
          <el-table-column :label="t('pages.mrpPacking.qtyPlan')" width="100" align="right">
            <template #default="{ row }">{{ formatQty(row.qty_sq) }}</template>
          </el-table-column>
          <el-table-column prop="source_detail_id" label="PO Detail" width="100" />
        </el-table>

        <template v-if="(detail.bridge_lines || []).length">
          <h4 class="mb-2 font-semibold">{{ t('pages.mrpGudangFg.bridgeLines') }}</h4>
          <el-table :data="detail.bridge_lines || []" border size="small" :empty-text="t('common.tableEmpty')">
            <el-table-column prop="no_po" :label="t('pages.mrpRencana.poCustomerRef')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="lot_no" :label="t('common.lotNo')" min-width="130" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.lot_no || row.lot_number) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpPacking.poItem')" min-width="140" show-overflow-tooltip>
              <template #default="{ row }">{{ dash(row.item_name) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.mrpPacking.quantity')" width="100" align="right">
              <template #default="{ row }">{{ formatQty(row.qty_sq) }}</template>
            </el-table-column>
            <el-table-column prop="source_detail_id" label="PO Detail" width="100" />
          </el-table>
        </template>
      </template>
    </el-drawer>

    <el-dialog
      v-model="repackOpen"
      :title="t('pages.mrpGudangFg.repackTitle', { kode: repackKode })"
      width="520px"
      destroy-on-close
      append-to-body
    >
      <p class="text-sm text-slate-500 mt-0 mb-3">{{ t('pages.mrpGudangFg.repackHint') }}</p>
      <div v-for="(line, index) in repackLines" :key="index" class="flex gap-2 mb-2 items-end">
        <el-form-item :label="t('pages.mrpPacking.pieces')" class="mb-0 flex-1">
          <el-input v-model="line.lembar" type="number" />
        </el-form-item>
        <el-form-item :label="t('pages.mrpPacking.quantity')" class="mb-0 flex-1">
          <el-input v-model="line.ukuran" type="number" />
        </el-form-item>
        <el-button v-if="repackLines.length > 1" text type="danger" @click="repackLines.splice(index, 1)">
          {{ t('common.delete') }}
        </el-button>
      </div>
      <el-button text type="primary" @click="repackLines.push({ lembar: '', ukuran: '' })">
        {{ t('pages.mrpGudangFg.repackAddLine') }}
      </el-button>
      <template #footer>
        <el-button @click="repackOpen = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="repackSaving" @click="saveRepack">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CircleCheck, CircleCheckFilled, Refresh, Upload } from '@element-plus/icons-vue'
import AdminSection from '../../../components/AdminSection.vue'
import AdminTableActions from '../../../components/admin/AdminTableActions.vue'
import { can } from '../../../security/permissions'
import {
  mrpGetGudangFg,
  mrpGudangFgOut,
  mrpGudangFgRepack,
  mrpGudangFgSuratJalan,
  mrpGudangFgSuratJalanOut,
  mrpGudangFgSuratJalanPending,
  mrpListGudangFg,
} from '../../../api/client'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../../utils/tableQuery'

const { t } = useI18n()
const router = useRouter()
const loading = ref(false)
const outing = ref(false)
const repackOpen = ref(false)
const repackSaving = ref(false)
const repackId = ref(null)
const repackKode = ref('')
const repackLines = ref([{ lembar: '', ukuran: '' }])
const rows = ref([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const sortBy = ref('date_in')
const sortDir = ref('desc')
const search = ref('')
const statusFilter = ref('')
const detailOpen = ref(false)
const detail = ref(null)
const detailQtyAlloc = computed(() => {
  const rowsPo = detail.value?.packing_pos || []
  if (!rowsPo.length) return null
  return rowsPo.reduce((sum, row) => sum + (Number(row.qty_sq) || 0), 0)
})
const detailQtyDelta = computed(() => {
  const actual = Number(detail.value?.fg?.total_ukuran)
  const alloc = detailQtyAlloc.value
  if (!Number.isFinite(actual) || alloc == null || !Number.isFinite(alloc)) return null
  return actual - alloc
})
const canUpdate = computed(() => can('mrpShopfloor', 'update'))
const outForm = reactive({ kode_packing: '', keterangan: '' })
const scanSjOpen = ref(false)
const scanSjLoading = ref(false)
const scanSjPendingLoading = ref(false)
const scanSjSaving = ref(false)
const sjPendingCustomers = ref([])
const sjCustomerName = ref('')
const sjDeliveryNumber = ref('')
const sjSession = ref(null)
const fgScanCode = ref('')
const fgScanInput = ref(null)

const sjDeliveryOptions = computed(() => {
  const name = (sjCustomerName.value || '').trim()
  const hit = (sjPendingCustomers.value || []).find((c) => c.customer === name)
  return hit?.deliveries || []
})

const sjRolls = computed(() => sjSession.value?.rolls || [])
const sjScannedCount = computed(() => sjRolls.value.filter((row) => isSjItemDone(row)).length)
const sjTotalCount = computed(() => sjRolls.value.length)

const canSaveSj = computed(() => {
  if (!sjTotalCount.value) return false
  return sjScannedCount.value === sjTotalCount.value
})

const filteredRows = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return rows.value
  return rows.value.filter((r) =>
    [
      r.kode_packing,
      r.kode_wip,
      r.customer,
      r.status,
      r.erp_delivery_number,
      r.bridge_status,
      r.bridge_error,
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

const stats = computed(() => {
  const list = rows.value || []
  return {
    inStock: list.filter((r) => r.status === 'in_stock').length,
    out: list.filter((r) => r.status === 'out').length,
    failed: list.filter((r) => r.bridge_status === 'failed').length,
  }
})

const failedBridgeCount = computed(() => stats.value.failed)

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
  return String(v).slice(0, 10)
}

function formatDateTime(v) {
  if (!v) return '—'
  return String(v).replace('T', ' ').slice(0, 19)
}

function statusType(status) {
  if (status === 'in_stock') return 'success'
  if (status === 'repacked') return 'info'
  if (status === 'out') return 'info'
  return 'warning'
}

function statusLabel(status) {
  if (status === 'in_stock') return t('pages.mrpGudangFg.statusInStock')
  if (status === 'repacked') return t('pages.mrpGudangFg.statusRepacked')
  if (status === 'out') return t('pages.mrpGudangFg.statusOut')
  return status || '—'
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

function goDelivery(id) {
  router.push({ path: '/admin/delivery', query: { delivery_id: id } })
}

function goEdit(row) {
  const packingId = row?.packing_id
  if (!packingId) {
    ElMessage.warning(t('pages.mrpGudangFg.editNoPacking'))
    return
  }
  detailOpen.value = false
  router.push({ path: `/admin/mrp/packing/${packingId}`, query: { from: 'gudang-fg' } })
}

function canRepackFg(fg, packingStatus) {
  return Boolean(
    canUpdate.value
    && fg
    && fg.status === 'in_stock'
    && packingStatus === 'finished'
    && !fg.erp_delivery_id,
  )
}

function fgMoreItems(row) {
  if (!canUpdate.value || row.status !== 'in_stock') return []
  const items = [{ command: 'out', label: 'OUT', icon: Upload }]
  if (canRepackFg(row, row.packing_status)) {
    items.push({ command: 'repack', label: t('pages.mrpGudangFg.repack'), icon: Refresh })
  }
  return items
}

function onFgMore(cmd, row) {
  if (cmd === 'out') fillOut(row)
  if (cmd === 'repack') openRepack(row, row.packing_status)
}

function openRepack(fg, packingStatus) {
  if (!canRepackFg(fg, packingStatus)) {
    ElMessage.warning(t('pages.mrpGudangFg.packingOpen'))
    return
  }
  repackId.value = fg.id
  repackKode.value = fg.kode_packing || ''
  repackLines.value = [{
    lembar: fg.total_lembar ?? '',
    ukuran: fg.total_ukuran ?? '',
  }]
  repackOpen.value = true
}

async function saveRepack() {
  const id = repackId.value
  if (!id) return
  repackSaving.value = true
  try {
    const res = await mrpGudangFgRepack(id, {
      lines: repackLines.value.map((line) => ({
        lembar: line.lembar,
        ukuran: line.ukuran,
      })),
    })
    ElMessage.success(t('pages.mrpGudangFg.repackOk', {
      kode: repackKode.value,
      n: (res?.created || []).length || repackLines.value.length,
    }))
    repackOpen.value = false
    detailOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    repackSaving.value = false
  }
}

function fillOut(row) {
  outForm.kode_packing = row?.kode_packing || ''
  if (row?.bridge_error) {
    ElMessage.warning(row.bridge_error)
  }
}

function outFromDetail() {
  if (!detail.value?.fg) return
  fillOut(detail.value.fg)
  doOut()
}

function onSortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy || 'date_in'
  sortDir.value = mapped.sortDir || 'desc'
  page.value = 1
  reload()
}

async function reload() {
  loading.value = true
  try {
    const data = await mrpListGudangFg(
      buildPageParams({
        page: page.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
        extra: {
          status: statusFilter.value || undefined,
          q: search.value.trim() || undefined,
        },
      }),
    )
    const pageData = normalizePageResult(data, { page: page.value, pageSize: pageSize.value })
    rows.value = pageData.items
    total.value = pageData.total
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    loading.value = false
  }
}

async function doOut() {
  const kode = outForm.kode_packing.trim()
  if (!kode) {
    ElMessage.warning(t('pages.mrpGudangFg.outPlaceholder'))
    return
  }
  try {
    await ElMessageBox.confirm(
      t('pages.mrpGudangFg.outConfirm', { kode }),
      t('pages.mrpGudangFg.outBtn'),
      { type: 'warning', confirmButtonText: t('pages.mrpGudangFg.outBtn'), cancelButtonText: t('common.cancel') },
    )
  } catch {
    return
  }
  outing.value = true
  try {
    const res = await mrpGudangFgOut({
      kode_packing: kode,
      keterangan: outForm.keterangan.trim(),
    })
    const dn = res?.erp_delivery_number || (res?.erp_delivery_id ? `#${res.erp_delivery_id}` : '')
    ElMessage.success(
      dn ? t('pages.mrpGudangFg.outBridged', { delivery: dn }) : t('common.saved'),
    )
    outForm.kode_packing = ''
    outForm.keterangan = ''
    detailOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
    await reload()
  } finally {
    outing.value = false
  }
}

async function openDetail(row) {
  try {
    detail.value = await mrpGetGudangFg(row.id)
    detailOpen.value = true
  } catch (e) {
    ElMessage.error(errMsg(e))
  }
}

function isSjItemDone(row) {
  return row?.fg_status === 'out' || row?.status === 'out' || !!row?.scanned
}

function sjRollLabel(row) {
  const kode = (row?.kode_fg || row?.kode_packing || '').trim() || '—'
  const roll = row?.roll_no == null || row?.roll_no === '' ? '—' : row.roll_no
  return `${kode}-${roll}`
}

function normalizeSjRolls(rolls = [], items = []) {
  if (rolls.length) {
    return rolls.map((row) => ({
      ...row,
      scanned: row.fg_status === 'out' || row.status === 'out' ? true : !!row.scanned,
    }))
  }
  return items.map((row) => ({
    roll_id: null,
    fg_id: row.id,
    kode_fg: row.kode_packing,
    kode_packing: row.kode_packing,
    packing_kode: row.kode_packing,
    roll_no: 1,
    lembar: row.total_lembar,
    ukuran: row.total_ukuran,
    fg_status: row.status,
    scanned: row.status === 'out',
  }))
}

function sjRowClassName({ row }) {
  return isSjItemDone(row) ? 'mrp-fg-sj-row--matched' : ''
}

async function openScanSj() {
  resetScanSj()
  scanSjOpen.value = true
  await loadPendingSuratJalan()
}

function resetScanSj() {
  sjCustomerName.value = ''
  sjDeliveryNumber.value = ''
  sjSession.value = null
  fgScanCode.value = ''
  scanSjLoading.value = false
  scanSjSaving.value = false
}

async function loadPendingSuratJalan() {
  scanSjPendingLoading.value = true
  try {
    const data = await mrpGudangFgSuratJalanPending()
    sjPendingCustomers.value = data?.customers || []
    if (!sjPendingCustomers.value.length) {
      ElMessage.info(t('pages.mrpGudangFg.sjNoPending'))
    }
  } catch (e) {
    sjPendingCustomers.value = []
    ElMessage.error(errMsg(e) || t('pages.mrpGudangFg.scanSjNotFound'))
  } finally {
    scanSjPendingLoading.value = false
  }
}

function onSjCustomerChange() {
  sjDeliveryNumber.value = ''
  sjSession.value = null
  fgScanCode.value = ''
}

function onSjDeliveryClick(row) {
  const code = (row?.delivery_number || '').trim()
  if (!code) return
  sjDeliveryNumber.value = code
  loadSuratJalan(code)
}

async function focusFgScan() {
  await nextTick()
  fgScanInput.value?.focus?.()
  fgScanInput.value?.input?.focus?.()
}

async function loadSuratJalan(deliveryNumber) {
  const code = String(deliveryNumber || sjDeliveryNumber.value || '').trim()
  if (!code) {
    ElMessage.warning(t('pages.mrpGudangFg.scanSjPickPlaceholder'))
    return
  }
  scanSjLoading.value = true
  try {
    const data = await mrpGudangFgSuratJalan(code)
    sjSession.value = {
      ...data,
      items: data.items || [],
      rolls: normalizeSjRolls(data.rolls || [], data.items || []),
    }
    fgScanCode.value = ''
    await focusFgScan()
  } catch (e) {
    sjSession.value = null
    ElMessage.error(errMsg(e) || t('pages.mrpGudangFg.scanSjNotFound'))
  } finally {
    scanSjLoading.value = false
  }
}

function markSjItemScanned(row) {
  if (!row || isSjItemDone(row)) return
  row.scanned = true
  ElMessage.success(t('pages.mrpGudangFg.sjFgMatched', { kode: sjRollLabel(row) }))
}

function matchFgScan() {
  const code = fgScanCode.value.trim()
  if (!code || !sjRolls.value.length) return
  const lower = code.toLowerCase()
  const matchesCode = (row) => {
    const kodeFg = String(row.kode_fg || row.kode_packing || '').trim().toLowerCase()
    const packing = String(row.packing_kode || '').trim().toLowerCase()
    const rollNo = String(row.roll_no ?? '').trim().toLowerCase()
    const label = `${kodeFg}-${rollNo}`
    return (
      kodeFg === lower ||
      packing === lower ||
      label === lower ||
      String(row.roll_id || '') === lower
    )
  }
  const matches = sjRolls.value.filter(matchesCode)
  if (!matches.length) {
    ElMessage.warning(t('pages.mrpGudangFg.sjFgNotFound'))
    return
  }
  const hit = matches.find((row) => !isSjItemDone(row))
  if (!hit) {
    fgScanCode.value = ''
    focusFgScan()
    return
  }
  markSjItemScanned(hit)
  fgScanCode.value = ''
  focusFgScan()
}

function sjDeliveryRowClass({ row }) {
  return row?.delivery_number === sjDeliveryNumber.value ? 'mrp-fg-sj-row--picked' : ''
}

async function saveSjScan() {
  if (!sjSession.value?.items?.length) return
  if (!canSaveSj.value) {
    ElMessage.warning(t('pages.mrpGudangFg.sjSaveNeedAll'))
    return
  }
  const inStockIds = sjSession.value.items
    .filter((row) => row.status === 'in_stock')
    .map((row) => row.id)
  if (!inStockIds.length) {
    ElMessage.success(t('pages.mrpGudangFg.sjAllAlreadyOut'))
    scanSjOpen.value = false
    await reload()
    return
  }
  try {
    await ElMessageBox.confirm(
      t('pages.mrpGudangFg.sjSaveConfirm', {
        n: inStockIds.length,
        sj: sjSession.value.delivery_number,
      }),
      t('pages.mrpGudangFg.sjSave'),
      { type: 'warning', confirmButtonText: t('pages.mrpGudangFg.sjSave'), cancelButtonText: t('common.cancel') },
    )
  } catch {
    return
  }
  scanSjSaving.value = true
  try {
    const res = await mrpGudangFgSuratJalanOut({
      delivery_number: sjSession.value.delivery_number,
      fg_ids: inStockIds,
      keterangan: `Scan SJ ${sjSession.value.delivery_number}`,
    })
    const n = res?.out_count ?? inStockIds.length
    ElMessage.success(t('pages.mrpGudangFg.sjSaveSuccess', { n }))
    scanSjOpen.value = false
    await reload()
  } catch (e) {
    ElMessage.error(errMsg(e))
  } finally {
    scanSjSaving.value = false
  }
}

onMounted(reload)
</script>

<style scoped>
.max-w-xs {
  max-width: 20rem;
}
.w-56 {
  width: 14rem;
}
.mrp-fg-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.55rem;
}
.mrp-fg-meta__item {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.55rem 0.7rem;
  font-size: 0.875rem;
}
.mrp-fg-meta__label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.15rem;
}
@media (max-width: 700px) {
  .mrp-fg-meta {
    grid-template-columns: 1fr;
  }
}
.mrp-fg-sj-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.55rem;
}
.mrp-fg-sj-meta__item {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 0.55rem 0.7rem;
  font-size: 0.875rem;
}
.mrp-fg-sj-meta__label {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--el-text-color-secondary);
  margin-bottom: 0.15rem;
}
:deep(.mrp-fg-sj-row--matched > td) {
  background-color: #ecfdf5 !important;
}
:deep(.mrp-fg-sj-row--picked > td) {
  background-color: #eff6ff !important;
}
.mrp-fg-sj-progress {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--el-color-primary);
}
</style>
