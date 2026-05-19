<template>
  <AdminSection :title="t('pages.delivery.title')" :subtitle="t('pages.delivery.subtitle')">
    <template #actions>
      <el-date-picker
        v-model="shipDateRange"
        type="daterange"
        value-format="YYYY-MM-DD"
        unlink-panels
        clearable
        class="w-[260px]"
        :start-placeholder="t('pages.delivery.filterShipDateFrom')"
        :end-placeholder="t('pages.delivery.filterShipDateTo')"
      />
      <el-input
        v-model="factoryCodeFilter"
        clearable
        class="w-28"
        :placeholder="t('pages.delivery.filterFactoryCode')"
      />
      <el-select v-model="poCategoryFilter" clearable class="w-32" :placeholder="t('pages.delivery.filterPoCategory')">
        <el-option :label="t('status.production')" value="production" />
        <el-option :label="t('status.sample')" value="sample" />
        <el-option :label="t('status.return')" value="return" />
        <el-option :label="t('status.subcont')" value="subcont" />
        <el-option :label="t('status.claim')" value="claim" />
        <el-option label="Suede" value="suede" />
      </el-select>
      <el-input v-model="customerFilter" clearable class="w-32" :placeholder="t('pages.delivery.filterCustomer')" />
      <el-input v-model="keyword" :placeholder="t('pages.delivery.listSearchPlaceholder')" clearable class="delivery-toolbar-search" />
      <el-switch v-model="showFullCols" :active-text="t('pages.delivery.showAllColumns')" class="ml-1" />
      <el-select v-model="statusFilter" clearable :placeholder="t('common.status')" class="w-32">
        <el-option label="Draft" value="draft" />
        <el-option label="Sent" value="sent" />
      </el-select>
      <el-select
        v-model="packingStatusFilter"
        clearable
        :placeholder="t('pages.delivery.filterPackingStatus')"
        class="w-36"
      >
        <el-option :label="t('status.draft')" value="draft" />
        <el-option :label="t('status.done')" value="done" />
      </el-select>
      <el-select
        v-model="invplFilter"
        clearable
        :placeholder="t('pages.delivery.filterInvplPrinted')"
        class="w-36"
      >
        <el-option :label="t('pages.delivery.filterInvplYes')" value="yes" />
        <el-option :label="t('pages.delivery.filterInvplNo')" value="no" />
      </el-select>
      <el-button :icon="Download" :loading="exporting" @click="downloadDeliveryExcel">{{ t('pages.delivery.downloadExcel') }}</el-button>
      <el-button v-if="canCreate" type="primary" :icon="Plus" :loading="loading" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <el-card shadow="never" class="mb-4">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-slate-800">{{ t('pages.delivery.listSheetTitle') }}</h3>
          <p class="text-sm text-slate-500 mt-1">
            {{ t('pages.delivery.flowInfo') }}
          </p>
        </div>
        <div class="flex items-center gap-4">
          <div class="text-right">
            <p class="text-2xl font-bold text-slate-700">{{ totalLines }}</p>
            <p class="text-xs text-slate-500">{{ t('common.total') }}</p>
          </div>
        </div>
      </div>
    </el-card>

    <el-table
      :data="lineRows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="fixed"
      :empty-text="t('pages.delivery.tableEmpty')"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="50" align="center" fixed="left" />
      <el-table-column prop="surat_jalan_no" :label="t('pages.delivery.columns.noSj')" min-width="130" show-overflow-tooltip />
      <el-table-column :label="t('pages.delivery.columns.shipDate')" width="100">
        <template #default="{ row }">{{ formatDate(row.delivery_date) }}</template>
      </el-table-column>
      <el-table-column prop="factory_name" :label="t('pages.delivery.columns.factory')" min-width="150" show-overflow-tooltip />
      <el-table-column prop="po_number" :label="t('pages.delivery.columns.poNumber')" min-width="130" show-overflow-tooltip />
      <el-table-column
        v-if="showFullCols"
        prop="system_no"
        :label="t('pages.delivery.columns.systemNo')"
        min-width="110"
        show-overflow-tooltip
      />
      <el-table-column
        v-if="showFullCols"
        prop="factory_code"
        :label="t('pages.delivery.columns.factoryCode')"
        width="100"
        show-overflow-tooltip
      />
      <el-table-column
        v-if="showFullCols"
        prop="thickness"
        :label="t('pages.delivery.columns.thickness')"
        width="90"
        show-overflow-tooltip
      />
      <el-table-column v-if="showFullCols" prop="color" :label="t('pages.delivery.columns.color')" width="90" show-overflow-tooltip />
      <el-table-column
        v-if="showFullCols"
        prop="order_type"
        :label="t('pages.delivery.columns.orderType')"
        width="90"
        show-overflow-tooltip
      />
      <el-table-column
        v-if="showFullCols"
        prop="invoice_number"
        :label="t('pages.delivery.columns.invNumber')"
        min-width="120"
        show-overflow-tooltip
      />
      <el-table-column v-if="showFullCols" prop="pi_no" :label="t('pages.delivery.columns.piNo')" width="100" show-overflow-tooltip />
      <el-table-column
        v-if="showFullCols"
        prop="delivery_zone"
        :label="t('pages.delivery.deliveryZone')"
        width="100"
        show-overflow-tooltip
      />
      <el-table-column
        v-if="showFullCols"
        prop="packing_status"
        :label="t('pages.delivery.filterPackingStatus')"
        width="90"
        show-overflow-tooltip
      />
      <el-table-column v-if="showFullCols" :label="t('pages.delivery.filterInvplPrinted')" width="88" align="center">
        <template #default="{ row }">
          <el-tag :type="row.invpl_printed ? 'success' : 'info'" size="small">
            {{ row.invpl_printed ? t('pages.delivery.filterInvplYes') : t('pages.delivery.filterInvplNo') }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="buyer" :label="t('pages.delivery.columns.buyer')" width="90" show-overflow-tooltip />
      <el-table-column prop="lot_no" :label="t('pages.delivery.columns.lotNo')" width="100" show-overflow-tooltip />
      <el-table-column prop="material_name" :label="t('pages.delivery.columns.materialName')" min-width="140" show-overflow-tooltip />
      <el-table-column :label="t('pages.delivery.columns.sf')" width="80" align="right">
        <template #default="{ row }">{{ formatNumber(row.qty_sf, 2) }}</template>
      </el-table-column>
      <el-table-column prop="qty_roll" :label="t('pages.delivery.columns.roll')" width="60" align="right" />
      <el-table-column prop="qty_pcs" :label="t('pages.delivery.columns.pcs')" width="60" align="right" />
      <el-table-column :label="t('pages.delivery.columns.nw')" width="70" align="right">
        <template #default="{ row }">{{ formatNumber(row.net_weight, 2) }}</template>
      </el-table-column>
      <el-table-column :label="t('pages.delivery.columns.amount')" width="100" align="right">
        <template #default="{ row }">{{ formatNumber(row.amount, 0) }}</template>
      </el-table-column>
      <el-table-column :label="t('pages.delivery.columns.status')" width="90" fixed="right">
        <template #default="{ row }">
          <el-tag :type="statusType(row.delivery_status)" size="small">
            {{ statusLabel(row.delivery_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="70" fixed="right" align="center">
        <template #default="{ row }">
          <el-button :icon="View" link type="primary" @click="openDetailFromLine(row)" />
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-4 flex justify-end">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="totalLines"
        :page-sizes="[25, 50, 100, 200]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="load"
        @size-change="onPageSizeChange"
      />
    </div>

    <el-dialog v-model="formVisible" :title="`${t('common.create')} ${t('menu.delivery')}`" width="560px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('common.customer')" required>
          <el-select v-model="form.customer_id" filterable class="w-full">
            <el-option
              v-for="c in customers"
              :key="c.id"
              :label="customerOptionLabel(c)"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.delivery.packingRequiredLabel')" required>
          <el-select v-model="form.packing_id" filterable class="w-full" :placeholder="t('pages.delivery.pickDonePacking')" @change="onCreatePackingChange">
            <el-option
              v-for="p in packingsDone"
              :key="p.id"
              :label="`${p.packing_number || p.id} (${p.status})`"
              :value="p.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('pages.delivery.deliveryType')" required>
          <el-radio-group v-model="form.delivery_type" class="w-full">
            <el-radio value="production">{{ t('status.production') }}</el-radio>
            <el-radio value="sample">{{ t('status.sample') }}</el-radio>
            <el-radio value="return">{{ t('status.return') }}</el-radio>
            <el-radio value="subcont">{{ t('status.subcont') }}</el-radio>
            <el-radio value="claim">{{ t('status.claim') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('common.date')">
          <el-date-picker v-model="form.delivery_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item :label="t('pages.delivery.deliveryZone')">
          <el-select v-model="form.delivery_zone" class="w-full">
            <el-option :label="t('pages.delivery.deliveryZoneOuttown')" value="outtown" />
            <el-option :label="t('pages.delivery.deliveryZoneLocal')" value="local" />
          </el-select>
          <span class="mt-1 block text-xs text-slate-500">{{ t('pages.delivery.deliveryZoneHint') }}</span>
        </el-form-item>
        <el-form-item :label="t('common.vehicle')">
          <el-input v-model="form.vehicle_number" />
        </el-form-item>
        <el-form-item :label="t('common.driver')">
          <el-input v-model="form.driver_name" />
        </el-form-item>
        <el-form-item :label="t('pages.delivery.manualDeliveryRemark')">
          <el-input v-model="form.destination" type="textarea" :rows="2" :placeholder="t('pages.delivery.manualDeliveryRemarkHint')" />
        </el-form-item>
        <el-form-item :label="t('common.status')">
          <el-select v-model="form.status" class="w-full" disabled>
            <el-option :label="t('status.draft')" value="draft" />
          </el-select>
          <span class="mt-1 block text-xs text-slate-500">{{ t('pages.delivery.markSentHint') }}</span>
        </el-form-item>
        <el-form-item :label="t('pages.delivery.pickQtyToShip')" required>
          <div v-if="createProdDetailsLoading" class="py-2 text-sm text-slate-500">
            <el-icon class="is-loading"><Loading /></el-icon> {{ t('common.loading') }}
          </div>
          <el-table
            v-else
            :data="createCandidateProdDetails"
            border
            size="small"
            max-height="220"
            @selection-change="onCreateLineSelectionChange"
          >
            <el-table-column type="selection" width="48" />
            <el-table-column prop="id" :label="t('pages.delivery.productionDetailId')" width="110">
              <template #default="{ row }">#{{ row.id }}</template>
            </el-table-column>
            <el-table-column prop="qty_actual" :label="t('common.actual')" width="90" align="right">
              <template #default="{ row }">{{ formatNumber(row.qty_actual, 2) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.delivery.qtyToShip')" min-width="140">
              <template #default="{ row }">
                <el-input
                  v-model="createLineQty[row.id]"
                  type="number"
                  step="0.01"
                  :placeholder="t('common.quantity')"
                  @input="onCreateLineQtyInput(row)"
                />
              </template>
            </el-table-column>
          </el-table>
          <span class="mt-1 block text-xs text-slate-500">{{ t('pages.delivery.pickQtyToShipHint') }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="delivery-dialog-footer">
          <el-button @click="formVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button v-if="canCreate" type="primary" :loading="saving" @click="submit">{{ t('common.save') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailVisible"
      :title="t('pages.delivery.dialogDetail')"
      width="720px"
      destroy-on-close
      align-center
      @closed="resetDetail"
    >
      <div v-if="detailLoading" class="py-12 text-center">
        <el-icon class="is-loading text-2xl text-blue-500"><Loading /></el-icon>
        <p class="mt-2 text-sm text-slate-500">{{ t('common.loading') }}...</p>
      </div>
      <template v-else-if="detailRow">
        <el-card class="mb-4" shadow="never">
          <template #header>
            <div class="flex items-center justify-between">
              <span class="font-semibold">{{ t('pages.delivery.basicInfo') }}</span>
              <el-tag :type="statusType(detailRow.status)" size="small">{{ statusLabel(detailRow.status) }}</el-tag>
            </div>
          </template>
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item :label="t('common.deliveryNo')">{{ detailRow.delivery_number || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.customer')">{{ detailRow.customer_name || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.date')">{{ detailRow.delivery_date || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.vehicle')">{{ detailRow.vehicle_number || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.driver')">{{ detailRow.driver_name || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.destination')">{{ detailRow.destination || '—' }}</el-descriptions-item>
            <el-descriptions-item v-if="detailRow.delivery_type" :label="t('pages.delivery.deliveryType')">
              {{ detailRow.delivery_type }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.delivery.deliveryZone')">
              {{ deliveryZoneLabel(detailRow.delivery_zone) }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card v-if="canUpdate" class="mb-4" shadow="never">
          <template #header>
            <span class="font-semibold">{{ t('pages.delivery.deliveryZone') }}</span>
          </template>
          <el-select v-model="zoneEdit" class="w-full max-w-md">
            <el-option :label="t('pages.delivery.deliveryZoneOuttown')" value="outtown" />
            <el-option :label="t('pages.delivery.deliveryZoneLocal')" value="local" />
          </el-select>
          <div class="mt-3">
            <el-button type="primary" plain size="small" :loading="zoneSaving" @click="saveDeliveryZone">
              {{ t('pages.delivery.saveDeliveryZone') }}
            </el-button>
          </div>
        </el-card>

        <el-card class="mb-4" shadow="never" v-if="canUpdate">
          <template #header>
            <span class="font-semibold">{{ t('pages.delivery.customsInfo') }}</span>
          </template>
          <div class="grid grid-cols-2 gap-4">
            <el-form-item :label="t('pages.delivery.bcNumberEdit')" class="mb-0">
              <el-input v-model="bcForm.bc_number" clearable maxlength="80" />
            </el-form-item>
            <el-form-item :label="t('pages.delivery.bcDateEdit')" class="mb-0">
              <el-date-picker v-model="bcForm.bc_date" type="date" value-format="YYYY-MM-DD" class="w-full" clearable />
            </el-form-item>
          </div>
          <div class="mt-3">
            <el-button type="primary" plain :loading="bcSaving" size="small" @click="saveBcFields">{{ t('pages.delivery.saveBcFields') }}</el-button>
          </div>
        </el-card>

        <div class="mb-4">
          <div class="mb-2 flex items-center justify-between">
            <h4 class="text-sm font-semibold text-slate-700">{{ t('pages.delivery.deliveryLines') }} ({{ detailLines.length }})</h4>
            <el-button
              v-if="canUpdate"
              type="primary"
              size="small"
              :disabled="isSentOrCancelled || detailLines.length === 0"
              :loading="markingSent"
              @click="markSent"
            >
              {{ t('pages.delivery.markSent') }}
            </el-button>
          </div>
          <el-table :data="detailLines" border size="small" :empty-text="t('pages.delivery.linesEmpty')">
            <el-table-column type="index" :label="t('common.noLabel')" width="50" align="center" />
            <el-table-column prop="production_detail_id" :label="t('pages.delivery.productionDetailId')" min-width="120">
              <template #default="{ row }">#{{ row.production_detail_id }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.delivery.columns.poNumber')" min-width="120" show-overflow-tooltip>
              <template #default="{ row }">
                <span v-if="!row.po_id">{{ row.po_number || '—' }}</span>
                <el-button v-else link type="primary" @click="goPoFromLine(row)">
                  {{ row.po_number || `#${row.po_id}` }}
                </el-button>
              </template>
            </el-table-column>
            <el-table-column prop="system_no" :label="t('pages.delivery.columns.systemNo')" width="110" show-overflow-tooltip />
            <el-table-column prop="lot_number" :label="t('pages.delivery.columns.lotNo')" width="100" show-overflow-tooltip />
            <el-table-column prop="material_name_line" :label="t('pages.delivery.columns.materialName')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="thickness_display" :label="t('pages.delivery.columns.thickness')" width="90" show-overflow-tooltip />
            <el-table-column prop="color_line" :label="t('pages.delivery.columns.color')" width="80" show-overflow-tooltip />
            <el-table-column prop="order_type" :label="t('pages.delivery.columns.orderType')" width="88" show-overflow-tooltip />
            <el-table-column prop="qty" :label="t('common.quantity')" min-width="100" align="right">
              <template #default="{ row }">{{ formatNumber(row.qty, 2) }}</template>
            </el-table-column>
            <el-table-column prop="qty_roll" :label="t('pages.delivery.roll')" width="80" align="right" />
            <el-table-column prop="qty_pcs" :label="t('pages.delivery.pcs')" width="80" align="right" />
            <el-table-column prop="weight" :label="t('pages.delivery.weight')" width="100" align="right">
              <template #default="{ row }">{{ formatNumber(row.weight, 2) }}</template>
            </el-table-column>
          </el-table>
          <p v-if="detailLines.length === 0" class="mt-2 text-xs text-amber-600">{{ t('pages.delivery.needAtLeastOneLine') }}</p>
        </div>

        <div class="flex flex-wrap gap-3">
          <el-button v-if="canPrint" type="default" @click="openSjPrint">{{ t('pages.delivery.printSj') }}</el-button>
          <el-button v-if="canPrint" type="default" @click="downloadSjPdf">{{ t('pages.delivery.downloadPdf') }}</el-button>
          <el-button v-if="canPrint" type="primary" plain @click="openCommercialInvoice">{{ t('pages.delivery.openCommercialInvoice') }}</el-button>
          <el-button v-if="canPrint" type="primary" plain @click="downloadCommercialInvoicePdf">{{ t('pages.delivery.commercialInvoicePdf') }}</el-button>
          <el-button v-if="canUpdate" type="success" plain :loading="markingSj" @click="markSjPrinted">{{ t('pages.delivery.markSjPrinted') }}</el-button>
        </div>

        <el-card v-if="canUpdate" class="mt-4" shadow="never">
          <template #header>
            <span class="font-semibold">{{ t('pages.delivery.addLineLabel') }}</span>
          </template>
          <div v-if="prodDetailsLoading" class="py-4 text-center">
            <el-icon class="is-loading"><Loading /></el-icon> {{ t('common.loading') }}
          </div>
          <template v-else-if="candidateProdDetails.length">
            <div class="grid grid-cols-2 gap-4">
              <el-form-item :label="t('pages.delivery.productionDetailPlaceholder')" class="mb-0">
                <el-select v-model="lineForm.production_detail_id" filterable clearable class="w-full" :placeholder="t('pages.delivery.productionDetailPlaceholder')">
                  <el-option
                    v-for="pd in candidateProdDetails"
                    :key="pd.id"
                    :label="`#${pd.id} ${t('common.dotSeparator')} ${t('common.actual').toLowerCase()} ${pd.qty_actual ?? t('common.emptyValue')}`"
                    :value="pd.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item :label="t('common.quantity')" class="mb-0">
                <el-input v-model="lineForm.qty" type="number" step="0.01" />
              </el-form-item>
            </div>
            <el-checkbox v-if="isAdminRole" v-model="lineForm.bypass_qc" class="mt-2">
              {{ t('pages.delivery.bypassQcAdmin') }}
            </el-checkbox>
            <div class="mt-3">
              <el-button type="primary" :loading="addingLine" @click="addLine">{{ t('pages.delivery.addToDelivery') }}</el-button>
            </div>
          </template>
          <p v-else class="text-sm text-slate-500">{{ t('pages.delivery.noProductionLines') }}</p>
        </el-card>
      </template>
      <template #footer>
        <el-button type="primary" @click="detailVisible = false">{{ t('pages.delivery.closeDetail') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, View, Van, Document, Download, Loading } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { can } from '../../security/permissions'
import { formatDate, formatNumber, statusType, statusLabel } from '../../utils/format'
import {
  addDeliveryDetail,
  createDelivery,
  fetchAuthenticatedDocument,
  getDelivery,
  getPacking,
  listCustomers,
  listDeliveryDetails,
  listMarketingDeliveryLines,
  listPacking,
  listProductionDetails,
  markSuratJalanPrinted,
  marketingDeliveryXlsxPath,
  me,
  toIsoDate,
  updateDelivery,
} from '../../api/client'

const { t } = useI18n()
const canCreate = can('delivery', 'create')
const canUpdate = can('delivery', 'update')
const canPrint = can('delivery', 'print')
const route = useRoute()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const exporting = ref(false)
const keyword = ref('')
const statusFilter = ref('')
const packingStatusFilter = ref('')
const invplFilter = ref('')
const shipDateRange = ref(null)
const factoryCodeFilter = ref('')
const poCategoryFilter = ref('')
const customerFilter = ref('')
const showFullCols = ref(false)
const currentPage = ref(1)
const pageSize = ref(50)
const totalLines = ref(0)
const isAdminRole = ref(false)
const keywordWatchActive = ref(false)
const lineRows = ref([])
const customers = ref([])
const packings = ref([])

const packingsDone = computed(() =>
  (packings.value || []).filter((p) => (p.status || '').toLowerCase() === 'done'),
)

function custName(id) {
  const c = customers.value.find((x) => x.id === id)
  return c ? `${c.name}` : t('common.emptyValue')
}

function customerOptionLabel(c) {
  const base = [c.code, c.name].filter(Boolean).join(` ${t('common.dashSeparator')} `)
  if (!base) return String(c.id)
  return c.city ? `${base} ${t('common.dotSeparator')} ${c.city}` : base
}

function deliveryLinesQueryParams() {
  const p = {}
  if (statusFilter.value) p.delivery_status = statusFilter.value
  if (packingStatusFilter.value) p.packing_status = packingStatusFilter.value
  if (invplFilter.value) p.invpl_printed = invplFilter.value
  const dr = shipDateRange.value
  if (Array.isArray(dr) && dr[0] && dr[1]) {
    p.delivery_date_from = String(dr[0]).slice(0, 10)
    p.delivery_date_to = String(dr[1]).slice(0, 10)
  }
  const fc = factoryCodeFilter.value.trim()
  if (fc) p.factory_code = fc
  if (poCategoryFilter.value) p.po_category = poCategoryFilter.value
  const cu = customerFilter.value.trim()
  if (cu) p.customer = cu
  const qkw = keyword.value.trim()
  if (qkw) p.q = qkw
  return p
}

function onPageSizeChange() {
  currentPage.value = 1
  load()
}

async function load() {
  loading.value = true
  try {
    const skip = (currentPage.value - 1) * pageSize.value
    const [linesResp, cust, pack] = await Promise.all([
      listMarketingDeliveryLines({
        ...deliveryLinesQueryParams(),
        skip,
        limit: pageSize.value,
      }),
      listCustomers(),
      listPacking(),
    ])
    customers.value = cust
    packings.value = pack
    const lines = Array.isArray(linesResp) ? linesResp : (linesResp?.data || [])
    totalLines.value = typeof linesResp?.total === 'number' ? linesResp.total : lines.length
    lineRows.value = lines.map((r) => ({
      ...r,
      delivery_date: r.delivery_date ? String(r.delivery_date).slice(0, 10) : '',
      po_date: r.po_date ? String(r.po_date).slice(0, 10) : '',
    }))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

watch(
  [statusFilter, packingStatusFilter, invplFilter, shipDateRange, factoryCodeFilter, poCategoryFilter, customerFilter],
  () => {
    currentPage.value = 1
    load()
  },
)

let keywordDebounce = null
watch(keyword, () => {
  if (!keywordWatchActive.value) return
  if (keywordDebounce) clearTimeout(keywordDebounce)
  keywordDebounce = setTimeout(() => {
    currentPage.value = 1
    load()
  }, 400)
})

onMounted(() => {
  try {
    me().then((u) => {
      isAdminRole.value = (u?.role || '') === 'admin'
    })
  } catch {
    isAdminRole.value = false
  }
  const q = route.query
  if (q.keyword != null && String(q.keyword).trim()) keyword.value = String(q.keyword).trim()
  if (q.delivery_date_from && q.delivery_date_to) {
    shipDateRange.value = [
      String(q.delivery_date_from).slice(0, 10),
      String(q.delivery_date_to).slice(0, 10),
    ]
  }
  if (q.factory_code != null && String(q.factory_code).trim()) factoryCodeFilter.value = String(q.factory_code).trim()
  if (q.po_category != null && String(q.po_category).trim()) poCategoryFilter.value = String(q.po_category).trim()
  if (q.po_number != null && String(q.po_number).trim()) keyword.value = String(q.po_number).trim()
  if (q.customer != null && String(q.customer).trim()) customerFilter.value = String(q.customer).trim()
  load()
    .then(() => {
      const deliveryIdRaw = route.query.delivery_id
      const deliveryId = Number(deliveryIdRaw)
      if (!Number.isNaN(deliveryId) && deliveryId > 0) {
        const target = lineRows.value.find((r) => Number(r.delivery_id) === deliveryId)
        if (target) openDetailFromLine(target)
        else openDetailById(deliveryId)
      }
    })
    .finally(() => {
      keywordWatchActive.value = true
    })
})

function goPoFromLine(row) {
  if (!row?.po_id) return
  router.push({ path: '/admin/po', query: { highlight: String(row.po_id) } })
}

const isSentOrCancelled = computed(() => {
  const status = (detailRow.value?.status || '').toLowerCase()
  return status === 'sent' || status === 'cancelled' || status === 'canceled'
})

async function downloadDeliveryExcel() {
  exporting.value = true
  try {
    await fetchAuthenticatedDocument(marketingDeliveryXlsxPath(deliveryLinesQueryParams()), {
      mode: 'download',
      downloadFallbackName: 'delivery_list_sistem.xlsx',
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    exporting.value = false
  }
}

const formVisible = ref(false)
const form = reactive({
  customer_id: null,
  packing_id: null,
  delivery_type: 'production',
  delivery_date: '',
  delivery_zone: 'outtown',
  vehicle_number: '',
  driver_name: '',
  destination: '',
  status: 'draft',
})
const createProdDetailsLoading = ref(false)
const createCandidateProdDetails = ref([])
const createSelectedLines = ref([])
const createLineQty = reactive({})

function openCreate() {
  form.customer_id = null
  form.packing_id = null
  form.delivery_type = 'production'
  form.delivery_date = new Date().toISOString().slice(0, 10)
  form.delivery_zone = 'outtown'
  form.vehicle_number = ''
  form.driver_name = ''
  form.destination = ''
  form.status = 'draft'
  createCandidateProdDetails.value = []
  createSelectedLines.value = []
  Object.keys(createLineQty).forEach((k) => delete createLineQty[k])
  formVisible.value = true
}

async function onCreatePackingChange(packingId) {
  createCandidateProdDetails.value = []
  createSelectedLines.value = []
  Object.keys(createLineQty).forEach((k) => delete createLineQty[k])
  if (!packingId) return
  createProdDetailsLoading.value = true
  try {
    const pk = await getPacking(packingId)
    if (!pk?.production_id) return
    const pds = await listProductionDetails(pk.production_id)
    createCandidateProdDetails.value = pds || []
    for (const pd of createCandidateProdDetails.value) {
      const fallbackQty = pd.qty_actual ?? pd.qty_planned ?? ''
      createLineQty[pd.id] = fallbackQty !== '' ? String(fallbackQty) : ''
    }
  } catch (e) {
    ElMessage.error(e.message || t('pages.delivery.loadProductionDetailsError'))
  } finally {
    createProdDetailsLoading.value = false
  }
}

function onCreateLineSelectionChange(selection) {
  createSelectedLines.value = selection || []
}

function onCreateLineQtyInput(row) {
  if (!row?.id) return
  if (!createSelectedLines.value.find((x) => x.id === row.id)) {
    const target = createCandidateProdDetails.value.find((x) => x.id === row.id)
    if (target) createSelectedLines.value = [...createSelectedLines.value, target]
  }
}

async function submit() {
  if (!form.customer_id) {
    ElMessage.warning(t('pages.delivery.pickCustomerWarning'))
    return
  }
  if (!form.packing_id) {
    ElMessage.warning(t('pages.delivery.pickDonePackingWarning'))
    return
  }
  if (!createSelectedLines.value.length) {
    ElMessage.warning(t('pages.delivery.pickQtyToShipWarning'))
    return
  }
  saving.value = true
  try {
    const remark = (form.destination || '').trim()
    const created = await createDelivery({
      customer_id: form.customer_id,
      packing_id: form.packing_id,
      delivery_type: form.delivery_type || undefined,
      delivery_date: toIsoDate(form.delivery_date) || undefined,
      delivery_zone: form.delivery_zone || undefined,
      vehicle_number: form.vehicle_number || undefined,
      driver_name: form.driver_name || undefined,
      destination: remark || undefined,
      status: 'draft',
    })
    for (const ln of createSelectedLines.value) {
      const rawQty = createLineQty[ln.id]
      const qty = rawQty != null && String(rawQty).trim() !== '' ? Number(rawQty) : undefined
      await addDeliveryDetail(created.id, {
        production_detail_id: ln.id,
        qty: Number.isFinite(qty) ? qty : undefined,
      })
    }
    ElMessage.success(t('pages.delivery.saved'))
    formVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

const detailVisible = ref(false)
const detailRow = ref(null)
const detailLines = ref([])
const candidateProdDetails = ref([])
const detailLoading = ref(false)
const prodDetailsLoading = ref(false)
const markingSent = ref(false)
const markingSj = ref(false)
const addingLine = ref(false)

const lineForm = reactive({
  production_detail_id: null,
  qty: '',
  bypass_qc: false,
})

const bcForm = reactive({
  bc_number: '',
  bc_date: '',
})
const bcSaving = ref(false)
const zoneEdit = ref('outtown')
const zoneSaving = ref(false)

function deliveryZoneLabel(z) {
  const v = (z || '').toLowerCase()
  if (v === 'local') return t('pages.delivery.deliveryZoneLocal')
  if (v === 'outtown') return t('pages.delivery.deliveryZoneOuttown')
  return t('pages.delivery.deliveryZoneOuttown')
}

function resetDetail() {
  detailLines.value = []
  candidateProdDetails.value = []
  lineForm.production_detail_id = null
  lineForm.qty = ''
  lineForm.bypass_qc = false
  bcForm.bc_number = ''
  bcForm.bc_date = ''
}

function openDetailFromLine(row) {
  if (row?.delivery_id == null) return
  openDetailById(row.delivery_id)
}

async function loadProductionDetails(packingId) {
  prodDetailsLoading.value = true
  try {
    const pk = await getPacking(packingId)
    if (pk?.production_id) {
      const pds = await listProductionDetails(pk.production_id)
      candidateProdDetails.value = pds
    }
  } catch (e) {
    ElMessage.error(t('pages.delivery.loadProductionDetailsError'))
  } finally {
    prodDetailsLoading.value = false
  }
}

async function openDetailById(deliveryId) {
  detailVisible.value = true
  detailLoading.value = true
  resetDetail()
  try {
    const full = await getDelivery(deliveryId)
    detailRow.value = { ...full, customer_name: custName(full.customer_id) }
    zoneEdit.value = (full.delivery_zone || 'outtown').toLowerCase() === 'local' ? 'local' : 'outtown'
    bcForm.bc_number = full.bc_number || ''
    bcForm.bc_date = full.bc_date ? String(full.bc_date).slice(0, 10) : ''
    const lines = await listDeliveryDetails(deliveryId)
    detailLines.value = lines
    if (full.packing_id) {
      await loadProductionDetails(full.packing_id)
    }
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    detailLoading.value = false
  }
}

async function openSjPrint() {
  if (!detailRow.value?.id) return
  try {
    await fetchAuthenticatedDocument(`/documents/surat-jalan/${detailRow.value.id}`, { mode: 'open' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadSjPdf() {
  if (!detailRow.value?.id) return
  try {
    await fetchAuthenticatedDocument(`/documents/surat-jalan/${detailRow.value.id}/pdf`, { mode: 'open' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function saveBcFields() {
  if (!detailRow.value?.id) return
  bcSaving.value = true
  try {
    await updateDelivery(detailRow.value.id, {
      bc_number: bcForm.bc_number?.trim() || undefined,
      bc_date: bcForm.bc_date || undefined,
    })
    ElMessage.success(t('pages.delivery.bcSaved'))
    await load()
    const full = await getDelivery(detailRow.value.id)
    detailRow.value = { ...full, customer_name: custName(full.customer_id) }
    bcForm.bc_number = full.bc_number || ''
    bcForm.bc_date = full.bc_date ? String(full.bc_date).slice(0, 10) : ''
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    bcSaving.value = false
  }
}

async function saveDeliveryZone() {
  if (!detailRow.value?.id) return
  zoneSaving.value = true
  try {
    await updateDelivery(detailRow.value.id, { delivery_zone: zoneEdit.value })
    ElMessage.success(t('pages.delivery.zoneSaved'))
    await load()
    const full = await getDelivery(detailRow.value.id)
    detailRow.value = { ...full, customer_name: custName(full.customer_id) }
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    zoneSaving.value = false
  }
}

async function openCommercialInvoice() {
  if (!detailRow.value?.id) return
  try {
    await fetchAuthenticatedDocument(`/documents/commercial-invoice/${detailRow.value.id}`, { mode: 'open' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadCommercialInvoicePdf() {
  if (!detailRow.value?.id) return
  try {
    await fetchAuthenticatedDocument(`/documents/commercial-invoice/${detailRow.value.id}/pdf`, {
      mode: 'download',
      downloadFallbackName: `commercial_invoice_${detailRow.value.id}.pdf`,
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function markSjPrinted() {
  if (!detailRow.value?.id) return
  markingSj.value = true
  try {
    await markSuratJalanPrinted(detailRow.value.id)
    ElMessage.success(t('pages.delivery.sjMarkedPrinted'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    markingSj.value = false
  }
}

async function markSent() {
  if (!detailRow.value?.id) return
  markingSent.value = true
  try {
    await updateDelivery(detailRow.value.id, { status: 'sent' })
    ElMessage.success(t('pages.delivery.deliveryMarkedSent'))
    detailVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    markingSent.value = false
  }
}

async function addLine() {
  if (!detailRow.value?.id || !lineForm.production_detail_id) {
    ElMessage.warning(t('pages.delivery.pickProductionDetailWarning'))
    return
  }
  addingLine.value = true
  try {
    await addDeliveryDetail(
      detailRow.value.id,
      {
        production_detail_id: lineForm.production_detail_id,
        qty: lineForm.qty ? Number(lineForm.qty) : undefined,
      },
      { bypass_qc: Boolean(lineForm.bypass_qc && isAdminRole.value) },
    )
    ElMessage.success(t('pages.delivery.lineAdded'))
    detailLines.value = await listDeliveryDetails(detailRow.value.id)
    lineForm.production_detail_id = null
    lineForm.qty = ''
    lineForm.bypass_qc = false
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    addingLine.value = false
  }
}
</script>

<style scoped>
.delivery-toolbar-search {
  width: 240px;
}
</style>
