<template>
  <AdminSection :title="t('pages.delivery.title')" :subtitle="t('pages.delivery.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.delivery.listSearchPlaceholder')"
        clearable
        class="delivery-toolbar-search"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Refresh" :loading="loading" @click="load">{{ t('common.refresh') }}</el-button>
      <el-button v-if="canCreate" :icon="Plus" @click="openCreate">{{ t('common.create') }}</el-button>
    </template>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.delivery.listTitle') }}</h3>
          <p class="admin-inner-card__sub">{{ t('pages.delivery.listSubtitle') }}</p>
        </div>
      </div>

      <div class="admin-action-bar">
        <p class="admin-action-bar__hint">{{ t('pages.delivery.exportListHint') }}</p>
        <div class="admin-action-bar__buttons">
          <el-button :icon="Download" :loading="exporting" @click="downloadDeliveryExcel">
            {{ t('pages.delivery.downloadExcel') }}
          </el-button>
          <el-button v-if="canCreate" plain :icon="Van" @click="openArrange">
            {{ t('pages.delivery.arrangeShipment') }}
          </el-button>
        </div>
      </div>

      <div v-if="canUpdate" class="filter-panel mb-4">
        <p class="filter-panel__title">{{ t('pages.delivery.scanOutTitle') }}</p>
        <div class="flex flex-wrap items-end gap-2">
          <el-input
            v-model="scanSjCode"
            clearable
            class="max-w-xs"
            :placeholder="t('pages.delivery.scanOutPlaceholder')"
            @keyup.enter="submitSjScanOut"
          />
          <el-button type="primary" :loading="scanningOut" @click="submitSjScanOut">
            {{ t('pages.delivery.scanOutSubmit') }}
          </el-button>
        </div>
        <p class="text-xs text-slate-500 mt-2">{{ t('pages.delivery.scanOutHint') }}</p>
      </div>

      <div class="mkt-section-body">
        <div class="filter-panel mb-4">
          <p class="filter-panel__title">{{ t('common.filter') }}</p>
          <el-form class="filter-form" label-position="top">
            <el-row :gutter="12">
              <el-col :xs="24" :sm="12" :md="8" :lg="5">
                <el-form-item :label="t('pages.delivery.filterCustomer')">
                  <el-select
                    v-model="filterCustomerId"
                    clearable
                    filterable
                    class="w-full"
                    :placeholder="t('common.placeholder.customer')"
                  >
                    <el-option
                      v-for="c in customers"
                      :key="c.id"
                      :label="customerOptionLabel(c)"
                      :value="c.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="8" :md="6" :lg="3">
                <el-form-item :label="t('common.status')">
                  <el-select v-model="statusFilter" clearable class="w-full" :placeholder="t('common.status')">
                    <el-option :label="t('status.draft')" value="draft" />
                    <el-option :label="t('status.sent')" value="sent" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="8" :md="6" :lg="3">
                <el-form-item :label="t('pages.delivery.filterPoCategory')">
                  <el-select v-model="poCategoryFilter" clearable class="w-full" :placeholder="t('common.category')">
                    <el-option :label="t('status.production')" value="production" />
                    <el-option :label="t('status.sample')" value="sample" />
                    <el-option :label="t('status.return')" value="return" />
                    <el-option :label="t('status.subcont')" value="subcont" />
                    <el-option :label="t('status.claim')" value="claim" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="8" :md="6" :lg="3">
                <el-form-item :label="t('pages.delivery.filterFactoryCode')">
                  <el-input
                    v-model="factoryCodeFilter"
                    clearable
                    class="w-full"
                    :placeholder="t('pages.delivery.filterFactoryCode')"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="8" :md="6" :lg="3">
                <el-form-item :label="t('pages.delivery.filterPackingStatus')">
                  <el-select
                    v-model="packingStatusFilter"
                    clearable
                    class="w-full"
                    :placeholder="t('pages.delivery.filterPackingStatus')"
                  >
                    <el-option :label="t('status.draft')" value="draft" />
                    <el-option :label="t('status.done')" value="done" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="12" :sm="8" :md="6" :lg="3">
                <el-form-item :label="t('pages.delivery.filterInvplPrinted')">
                  <el-select v-model="invplFilter" clearable class="w-full" :placeholder="t('pages.delivery.filterInvplPrinted')">
                    <el-option :label="t('pages.delivery.filterInvplYes')" value="yes" />
                    <el-option :label="t('pages.delivery.filterInvplNo')" value="no" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="18" :md="12" :lg="8">
                <el-form-item :label="t('pages.delivery.filterShipDateRange')">
                  <el-date-picker
                    v-model="shipDateRange"
                    type="daterange"
                    value-format="YYYY-MM-DD"
                    unlink-panels
                    range-separator="—"
                    size="small"
                    class="w-full min-w-[200px] max-w-full"
                    :shortcuts="deliveryDateShortcuts"
                    clearable
                    :start-placeholder="t('common.placeholder.fromDate')"
                    :end-placeholder="t('common.placeholder.toDate')"
                  />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8" :md="6" :lg="4" class="delivery-filter-action-col">
                <el-form-item label="&nbsp;">
                  <el-button class="w-full" :icon="RefreshLeft" @click="resetDeliveryFilters">{{ t('common.reset') }}</el-button>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>

        <div class="admin-stats-grid admin-stats-grid--4 mb-4">
          <div class="admin-stat-card">
            <span class="admin-stat-card__value">{{ deliveryListStats.total }}</span>
            <span class="admin-stat-card__label">{{ t('common.total') }}</span>
          </div>
          <div class="admin-stat-card admin-stat-card--info">
            <span class="admin-stat-card__value">{{ deliveryListStats.shown }}</span>
            <span class="admin-stat-card__label">{{ t('pages.delivery.shownOnPage') }}</span>
          </div>
          <div class="admin-stat-card admin-stat-card--warn">
            <span class="admin-stat-card__value">{{ deliveryListStats.draft }}</span>
            <span class="admin-stat-card__label">{{ t('pages.delivery.draftOnPage') }}</span>
          </div>
          <div class="admin-stat-card admin-stat-card--success">
            <span class="admin-stat-card__value">{{ deliveryListStats.sent }}</span>
            <span class="admin-stat-card__label">{{ t('pages.delivery.sentOnPage') }}</span>
          </div>
        </div>

        <div class="delivery-table-toolbar mb-3">
          <div class="delivery-column-toggle">
            <el-switch v-model="showDetailCols" size="small" />
            <span class="text-sm text-slate-600">{{ t('pages.delivery.showDetailColumns') }}</span>
          </div>
          <div v-if="canPrint" class="delivery-selection-actions">
            <el-tooltip
              :content="t('pages.delivery.checklistPrintHint')"
              placement="bottom"
              :disabled="Boolean(listSelection.length)"
            >
              <span class="delivery-selection-actions__btns">
                <el-button
                  size="small"
                  :disabled="!selectedDeliveryIds.length"
                  :loading="batchPrinting"
                  @click="printSelectedSj"
                >
                  {{ t('pages.delivery.printSj') }}
                </el-button>
                <el-button
                  size="small"
                  type="primary"
                  plain
                  :disabled="!selectedDeliveryIds.length"
                  :loading="batchPrinting"
                  @click="printSelectedSjAndInvpl"
                >
                  {{ t('pages.delivery.printSjAndInvpl') }}
                </el-button>
              </span>
            </el-tooltip>
            <span v-if="selectedDeliveryIds.length" class="delivery-selection-actions__count">
              {{ t('pages.delivery.selectedSjCount', { n: selectedDeliveryIds.length, lines: listSelection.length }) }}
            </span>
          </div>
          <p v-if="showDetailCols" class="delivery-scroll-hint">{{ t('pages.delivery.scrollHint') }}</p>
          <p v-else class="delivery-scroll-hint">{{ t('pages.delivery.summaryHint') }}</p>
        </div>

        <div class="admin-table-scroll">
          <el-table
            ref="listTableRef"
            :data="lineRows"
            v-loading="loading"
            border
            stripe
            size="small"
            class="admin-table delivery-list-table"
            table-layout="fixed"
            :empty-text="t('pages.delivery.tableEmpty')"
            :row-key="deliveryLineRowKey"
            @selection-change="onListSelectionChange"
            @sort-change="onDeliverySortChange"
          >
            <el-table-column
              v-if="canPrint"
              type="selection"
              width="42"
              fixed="left"
            />
            <el-table-column
              type="index"
              :label="t('common.noLabel')"
              width="50"
              align="center"
              fixed="left"
              :index="(i) => (currentPage - 1) * pageSize + i + 1"
            />
            <el-table-column
              prop="surat_jalan_no"
              :label="t('pages.delivery.columns.noSj')"
              min-width="150"
              fixed="left"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                <button
                  v-if="String(row.surat_jalan_no || '').trim()"
                  type="button"
                  class="delivery-sj-no"
                  @click="openDetailFromLine(row)"
                >
                  {{ row.surat_jalan_no }}
                </button>
                <span v-else class="delivery-sj-no delivery-sj-no--empty">—</span>
              </template>
            </el-table-column>
            <el-table-column prop="delivery_date" :label="t('pages.delivery.columns.shipDate')" width="104" sortable="custom">
              <template #default="{ row }">{{ formatDate(row.delivery_date) }}</template>
            </el-table-column>
            <el-table-column prop="factory_name" :label="t('pages.delivery.columns.factory')" min-width="160" show-overflow-tooltip />
            <el-table-column prop="destination" :label="t('common.destination')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="system_no" :label="t('pages.delivery.columns.systemNo')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="color" :label="t('pages.delivery.columns.color')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="leather_color" :label="t('pages.delivery.columns.leatherColor')" min-width="110" show-overflow-tooltip />
            <el-table-column :label="t('pages.delivery.columns.leatherInDate')" width="120">
              <template #default="{ row }">{{ formatDate(row.leather_in_date) }}</template>
            </el-table-column>
            <el-table-column prop="qty_roll" :label="t('pages.delivery.columns.roll')" width="64" align="right" />
            <el-table-column :label="t('pages.delivery.columns.invNumber')" min-width="130" show-overflow-tooltip>
              <template #default="{ row }">
                <el-button
                  v-if="String(row.invoice_number || '').trim()"
                  link
                  type="primary"
                  @click.stop="goViewOutstandingFromLine(row)"
                >
                  {{ row.invoice_number }}
                </el-button>
                <el-button
                  v-else-if="canCreateInvoiceFromLine(row)"
                  link
                  type="info"
                  @click.stop="goCreateInvoiceFromLine(row)"
                >
                  {{ t('pages.delivery.createArInvoice') }}
                </el-button>
                <span v-else>{{ row.invoice_number || '—' }}</span>
              </template>
            </el-table-column>

            <template v-if="showDetailCols">
              <el-table-column prop="lot_no" :label="t('pages.delivery.columns.lotNo')" min-width="130" show-overflow-tooltip />
              <el-table-column prop="material_name" :label="t('pages.delivery.columns.materialName')" min-width="140" show-overflow-tooltip />
              <el-table-column :label="t('pages.delivery.columns.sf')" width="88" align="right">
                <template #default="{ row }">{{ formatNumber(row.qty_sf, 2) }}</template>
              </el-table-column>
              <el-table-column prop="qty_pcs" :label="t('pages.delivery.columns.pcs')" width="64" align="right" />
              <el-table-column :label="t('pages.delivery.columns.poDate')" width="100">
                <template #default="{ row }">{{ formatDate(row.po_date) }}</template>
              </el-table-column>
              <el-table-column prop="po_number" :label="t('pages.delivery.columns.poNumber')" min-width="130" show-overflow-tooltip sortable="custom" />
              <el-table-column prop="thickness" :label="t('pages.delivery.columns.thickness')" width="90" show-overflow-tooltip />
              <el-table-column :label="t('pages.delivery.columns.qtyPo')" width="90" align="right">
                <template #default="{ row }">{{ formatNumber(row.qty_po, 2) }}</template>
              </el-table-column>
              <el-table-column :label="t('pages.delivery.columns.unitPrice')" width="90" align="right">
                <template #default="{ row }">{{ formatNumber(row.unit_price, 2) }}</template>
              </el-table-column>
              <el-table-column prop="color_std" :label="t('pages.delivery.columns.colorStd')" min-width="110" show-overflow-tooltip />
              <el-table-column prop="emboss" :label="t('pages.delivery.columns.emboss')" min-width="100" show-overflow-tooltip />
              <el-table-column prop="buyer" :label="t('pages.delivery.columns.buyer')" width="90" show-overflow-tooltip />
              <el-table-column prop="style_article" :label="t('pages.delivery.columns.style')" min-width="100" show-overflow-tooltip />
              <el-table-column prop="model" :label="t('pages.delivery.columns.model')" min-width="100" show-overflow-tooltip />
              <el-table-column prop="remark" :label="t('pages.delivery.columns.remark')" min-width="120" show-overflow-tooltip />
              <el-table-column :label="t('pages.delivery.columns.source')" width="88" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.source_mrp" size="small" type="warning">MRP</el-tag>
                  <span v-else class="text-gray-400">ERP</span>
                </template>
              </el-table-column>
              <el-table-column prop="factory_code" :label="t('pages.delivery.columns.factoryCode')" width="100" show-overflow-tooltip />
              <el-table-column prop="order_type" :label="t('pages.delivery.columns.orderType')" width="90" show-overflow-tooltip />
              <el-table-column :label="t('pages.delivery.columns.foc')" width="110" show-overflow-tooltip>
                <template #default="{ row }">
                  {{ row.is_foc ? t('pages.delivery.invplFoc') : t('pages.delivery.chargePaid') }}
                </template>
              </el-table-column>
              <el-table-column prop="pi_no" :label="t('pages.delivery.columns.piNo')" width="100" show-overflow-tooltip />
              <el-table-column prop="delivery_zone" :label="t('pages.delivery.deliveryZone')" width="100" show-overflow-tooltip />
              <el-table-column prop="packing_status" :label="t('pages.delivery.filterPackingStatus')" width="90" show-overflow-tooltip />
              <el-table-column :label="t('pages.delivery.filterInvplPrinted')" width="88" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.invpl_printed ? 'success' : 'info'" size="small">
                    {{ row.invpl_printed ? t('pages.delivery.filterInvplYes') : t('pages.delivery.filterInvplNo') }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('pages.delivery.columns.nw')" width="70" align="right">
                <template #default="{ row }">{{ formatNumber(row.net_weight, 2) }}</template>
              </el-table-column>
              <el-table-column :label="t('pages.delivery.columns.amount')" width="100" align="right">
                <template #default="{ row }">{{ formatNumber(row.amount, 0) }}</template>
              </el-table-column>
              <el-table-column :label="t('pages.delivery.colReturnedQty')" width="72" align="right">
                <template #default="{ row }">{{ formatNumber(row.returned_qty, 2) || '—' }}</template>
              </el-table-column>
            </template>

            <el-table-column prop="delivery_status" :label="t('pages.delivery.columns.status')" width="90" fixed="right" sortable="custom">
              <template #default="{ row }">
                <el-tag :type="statusType(row.delivery_status)" size="small">
                  {{ deliveryStatusLabel(row.delivery_status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="88" fixed="right" align="center">
              <template #default="{ row }">
                <AdminTableActions
                  :show-view="true"
                  :more-items="deliveryListMoreItems(row)"
                  @view="openDetailFromLine(row)"
                  @more="(cmd) => handleDeliveryListMore(row, cmd)"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="delivery-pagination">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :total="totalLines"
            :page-sizes="[25, 50, 100, 200]"
            layout="total, sizes, prev, pager, next"
            background
          />
        </div>
      </div>
    </div>

    <el-dialog
      v-model="formVisible"
      :title="t('pages.delivery.createDialogTitle')"
      width="960px"
      destroy-on-close
      align-center
      class="delivery-form-dialog"
      @closed="resetCreateForm"
    >
      <p class="delivery-dialog-sub">{{ t('pages.delivery.createDialogSub') }}</p>

      <el-form label-position="top" class="delivery-form">
        <section class="delivery-form-section">
          <header class="delivery-form-section__head">
            <h4 class="delivery-form-section__title">{{ t('pages.delivery.createGroupSource') }}</h4>
          </header>
          <el-row :gutter="16">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="t('pages.delivery.packingRequiredLabel')" required>
                <el-select
                  v-model="form.packing_id"
                  filterable
                  clearable
                  class="w-full"
                  :placeholder="t('pages.delivery.pickDonePacking')"
                  @change="onCreatePackingChange"
                >
                  <el-option
                    v-for="p in packingsDone"
                    :key="p.id"
                    :label="`${p.packing_number || p.id} (${packingStatusLabel(p.status)})`"
                    :value="p.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="t('common.customer')" required>
                <el-select
                  v-model="form.customer_id"
                  filterable
                  class="w-full"
                  :placeholder="t('common.placeholder.customer')"
                  :disabled="createCustomerFromPacking"
                >
                  <el-option
                    v-for="c in customers"
                    :key="c.id"
                    :label="customerOptionLabel(c)"
                    :value="c.id"
                  />
                </el-select>
                <p v-if="createCustomerFromPacking" class="delivery-field-hint">{{ t('pages.delivery.createCustomerAutoHint') }}</p>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="t('pages.delivery.deliveryType')" required>
                <el-select v-model="form.delivery_type" class="w-full" @change="createTypeTouched = true">
                  <el-option :label="t('status.production')" value="production" />
                  <el-option :label="t('status.sample')" value="sample" />
                  <el-option :label="t('status.return')" value="return" />
                  <el-option :label="t('status.subcont')" value="subcont" />
                  <el-option :label="t('status.claim')" value="claim" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </section>

        <section class="delivery-form-section">
          <header class="delivery-form-section__head">
            <h4 class="delivery-form-section__title">{{ t('pages.delivery.createGroupShipment') }}</h4>
          </header>
          <el-row :gutter="16">
            <el-col :xs="24" :sm="12">
              <el-form-item :label="t('common.date')">
                <el-date-picker v-model="form.delivery_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="t('pages.delivery.deliveryZone')">
                <el-select v-model="form.delivery_zone" class="w-full">
                  <el-option :label="t('pages.delivery.deliveryZoneOuttown')" value="outtown" />
                  <el-option :label="t('pages.delivery.deliveryZoneLocal')" value="local" />
                </el-select>
                <p class="delivery-field-hint">{{ t('pages.delivery.deliveryZoneHint') }}</p>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="t('common.vehicle')">
                <el-input v-model="form.vehicle_number" clearable />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="12">
              <el-form-item :label="t('common.driver')">
                <el-input v-model="form.driver_name" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item :label="t('pages.delivery.manualDeliveryRemark')">
                <el-input
                  v-model="form.destination"
                  type="textarea"
                  :rows="2"
                  :placeholder="t('pages.delivery.manualDeliveryRemarkHint')"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </section>

        <section class="delivery-form-section delivery-form-section--last">
          <header class="delivery-form-section__head delivery-form-section__head--row">
            <div>
              <h4 class="delivery-form-section__title">{{ t('pages.delivery.createGroupLines') }}</h4>
              <p class="delivery-form-section__sub">{{ t('pages.delivery.pickQtyToShipHint') }}</p>
            </div>
            <el-tag size="small" type="info" effect="plain">{{ t('status.draft') }}</el-tag>
          </header>
          <p class="delivery-field-hint mb-3">{{ t('pages.delivery.createDraftNote') }}</p>

          <div v-if="!form.packing_id" class="delivery-form-empty">
            {{ t('pages.delivery.createPickPackingFirst') }}
          </div>
          <div v-else-if="createProdDetailsLoading" class="delivery-form-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>{{ t('common.loadingData') }}</span>
          </div>
          <div v-else-if="!createCandidateProdDetails.length" class="delivery-form-empty">
            {{ t('pages.delivery.noProductionLines') }}
          </div>
          <div v-else class="admin-table-scroll delivery-form-table-wrap">
            <el-table
              :data="createCandidateProdDetails"
              border
              size="small"
              class="admin-table delivery-form-table"
              max-height="240"
              @selection-change="onCreateLineSelectionChange"
            >
              <el-table-column type="selection" width="48" fixed="left" />
              <el-table-column prop="id" :label="t('pages.delivery.productionDetailId')" width="100" fixed="left">
                <template #default="{ row }">#{{ row.id }}</template>
              </el-table-column>
              <el-table-column prop="qty_actual" :label="t('common.actual')" width="96" align="right">
                <template #default="{ row }">{{ formatNumber(row.qty_actual, 2) }}</template>
              </el-table-column>
              <el-table-column :label="t('pages.delivery.qtyToShip')" min-width="120">
                <template #default="{ row }">
                  <el-input
                    v-model="createLineQty[row.id]"
                    type="number"
                    step="0.01"
                    size="small"
                    :placeholder="t('common.quantity')"
                    @input="onCreateLineQtyInput(row)"
                  />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </section>
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
      width="1040px"
      destroy-on-close
      align-center
      class="delivery-detail-dialog"
      @closed="resetDetail"
    >
      <div v-if="detailLoading" class="delivery-detail-loading">
        <el-icon class="is-loading text-2xl text-slate-500"><Loading /></el-icon>
        <p>{{ t('common.loadingData') }}...</p>
      </div>
      <div v-else-if="!detailRow" class="delivery-detail-loading">
        <p>{{ t('pages.delivery.detailLoadFailed') }}</p>
      </div>
      <div v-else class="delivery-detail-body">
        <section class="delivery-form-section">
          <header class="delivery-form-section__head delivery-form-section__head--row">
            <h4 class="delivery-form-section__title">{{ t('pages.delivery.basicInfo') }}</h4>
            <el-tag :type="statusType(detailRow.status)" size="small" effect="plain">
              {{ deliveryStatusLabel(detailRow.status) }}
            </el-tag>
          </header>
          <el-descriptions :column="2" border size="small" class="delivery-detail-desc">
            <el-descriptions-item :label="t('common.deliveryNo')">
              <div v-if="canEditSjNumber" class="delivery-detail-sj-edit">
                <el-input
                  v-model="sjNumberEdit"
                  size="small"
                  clearable
                  maxlength="80"
                  class="delivery-detail-sj-input"
                />
                <el-button
                  type="primary"
                  plain
                  size="small"
                  :loading="sjNumberSaving"
                  @click="saveSjNumber"
                >
                  {{ t('pages.delivery.saveSjNumber') }}
                </el-button>
              </div>
              <span v-else class="delivery-detail-sj">{{ detailRow.delivery_number || '—' }}</span>
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.customer')">{{ detailRow.customer_name || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.date')">{{ detailRow.delivery_date || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.vehicle')">{{ detailRow.vehicle_number || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.driver')">{{ detailRow.driver_name || '—' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.destination')">{{ detailRow.destination || '—' }}</el-descriptions-item>
            <el-descriptions-item v-if="detailRow.delivery_type" :label="t('pages.delivery.deliveryType')">
              {{ categoryLabel(detailRow.delivery_type) }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.delivery.deliveryZone')">
              {{ deliveryZoneLabel(detailRow.delivery_zone) }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.invoiceNo')">
              <el-button
                v-if="detailInvoice?.invoice_number"
                link
                type="primary"
                @click="goViewOutstandingFromDetail"
              >
                {{ detailInvoice.invoice_number }}
              </el-button>
              <span v-else-if="showCreateInvoiceCta" class="delivery-detail-muted">{{ t('pages.delivery.invoicePending') }}</span>
              <span v-else class="delivery-detail-muted">—</span>
            </el-descriptions-item>
          </el-descriptions>
        </section>

        <section v-if="canUpdate" class="delivery-form-section">
          <header class="delivery-form-section__head">
            <h4 class="delivery-form-section__title">{{ t('pages.delivery.zoneCustomsSection') }}</h4>
          </header>
          <el-form label-position="top" class="delivery-detail-edit-form" size="small">
            <el-row :gutter="16">
              <el-col :xs="24" :sm="8">
                <el-form-item :label="t('pages.delivery.deliveryZone')">
                  <el-select v-model="zoneEdit" class="w-full">
                    <el-option :label="t('pages.delivery.deliveryZoneOuttown')" value="outtown" />
                    <el-option :label="t('pages.delivery.deliveryZoneLocal')" value="local" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item :label="t('pages.delivery.bcNumber')">
                  <el-input v-model="bcForm.bc_number" clearable maxlength="80" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :sm="8">
                <el-form-item :label="t('pages.delivery.bcDate')">
                  <el-date-picker
                    v-model="bcForm.bc_date"
                    type="date"
                    value-format="YYYY-MM-DD"
                    class="w-full"
                    clearable
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <div class="delivery-detail-edit-actions">
              <el-button type="primary" plain size="small" :loading="zoneSaving" @click="saveDeliveryZone">
                {{ t('pages.delivery.saveDeliveryZone') }}
              </el-button>
              <el-button type="primary" plain size="small" :loading="bcSaving" @click="saveBcFields">
                {{ t('pages.delivery.saveBcFields') }}
              </el-button>
            </div>
          </el-form>
        </section>

        <section class="delivery-form-section">
          <header class="delivery-form-section__head delivery-form-section__head--row">
            <h4 class="delivery-form-section__title">
              {{ t('pages.delivery.deliveryLines') }}
              <span class="delivery-detail-count">{{ detailLines.length }}</span>
            </h4>
          </header>
          <div class="delivery-detail-table-wrap">
            <el-table
              :data="detailLines"
              border
              size="small"
              class="delivery-detail-table"
              :empty-text="t('pages.delivery.linesEmpty')"
            >
              <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" />
              <el-table-column :label="t('pages.mrpRencana.soRef')" min-width="120" show-overflow-tooltip>
                <template #default="{ row }">
                  <span v-if="!row.po_id">{{ row.system_no || row.po_number || '—' }}</span>
                  <el-button v-else link type="primary" @click="goPoFromLine(row)">
                    {{ row.system_no || row.po_number || `#${row.po_id}` }}
                  </el-button>
                </template>
              </el-table-column>
              <el-table-column prop="po_customer_ref" :label="t('pages.mrpRencana.poCustomerRef')" min-width="110" show-overflow-tooltip />
              <el-table-column prop="lot_number" :label="t('pages.delivery.columns.lotNo')" min-width="120" show-overflow-tooltip />
              <el-table-column prop="material_name_line" :label="t('pages.delivery.columns.materialName')" min-width="130" show-overflow-tooltip />
              <el-table-column prop="thickness_display" :label="t('pages.delivery.columns.thickness')" width="88" show-overflow-tooltip />
              <el-table-column prop="color_line" :label="t('pages.delivery.columns.color')" width="100" show-overflow-tooltip />
              <el-table-column prop="leather_color" :label="t('pages.delivery.columns.leatherColor')" min-width="100" show-overflow-tooltip />
              <el-table-column :label="t('pages.delivery.columns.leatherInDate')" width="120">
                <template #default="{ row }">{{ formatDate(row.leather_in_date) }}</template>
              </el-table-column>
              <el-table-column prop="qty" :label="t('common.quantity')" width="120" align="right">
                <template #default="{ row }">
                  <el-input-number
                    v-if="canEditDraftLines"
                    v-model="row.qty"
                    size="small"
                    :min="0.01"
                    :precision="2"
                    :controls="false"
                    class="w-full"
                    @change="(val) => saveDetailLineQty(row, val)"
                  />
                  <span v-else>{{ formatNumber(row.qty, 2) }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="t('pages.delivery.colReturnedQty')" width="80" align="right">
                <template #default="{ row }">{{ formatNumber(row.returned_qty, 2) || '—' }}</template>
              </el-table-column>
              <el-table-column prop="qty_roll" :label="t('pages.delivery.roll')" width="64" align="right" />
              <el-table-column prop="qty_pcs" :label="t('pages.delivery.pcs')" width="64" align="right" />
              <el-table-column prop="weight" :label="t('pages.delivery.weight')" width="80" align="right">
                <template #default="{ row }">{{ formatNumber(row.weight, 2) }}</template>
              </el-table-column>
              <el-table-column
                v-if="canReturn || canEditDraftLines"
                :label="t('common.actions')"
                width="88"
                align="center"
                fixed="right"
              >
                <template #default="{ row }">
                  <AdminTableActions
                    v-if="detailLineMoreItems(row).length"
                    :more-items="detailLineMoreItems(row)"
                    @more="(cmd) => onDetailLineMore(cmd, row)"
                  />
                </template>
              </el-table-column>
            </el-table>
          </div>
          <p v-if="detailLines.length === 0" class="delivery-detail-warn">{{ t('pages.delivery.needAtLeastOneLine') }}</p>
        </section>

        <section class="delivery-form-section">
          <header class="delivery-form-section__head">
            <h4 class="delivery-form-section__title">{{ t('pages.delivery.documentsSection') }}</h4>
          </header>
          <div class="delivery-detail-toolbar">
            <el-checkbox
              v-if="canPrint || canUpdate"
              v-model="invplFoc"
              class="delivery-detail-foc"
              :title="t('pages.delivery.invplFocHint')"
              @change="saveInvplFoc"
            >
              {{ t('pages.delivery.invplFoc') }}
            </el-checkbox>
            <div class="delivery-detail-toolbar__btns">
              <el-button v-if="canPrint" size="small" type="primary" plain @click="openSjAndInvpl">{{ t('pages.delivery.printSjAndInvpl') }}</el-button>
              <el-button v-if="canPrint" size="small" @click="openSjDotmatrix">{{ t('pages.delivery.printSjDotmatrix') }}</el-button>
              <el-button v-if="canPrint" size="small" @click="downloadSjPdf">{{ t('pages.delivery.downloadPdf') }}</el-button>
              <el-button v-if="canPrint" size="small" type="primary" plain @click="openCommercialInvoice">{{ t('pages.delivery.openCommercialInvoice') }}</el-button>
              <el-button v-if="canPrint" size="small" type="primary" plain @click="downloadCommercialInvoicePdf">{{ t('pages.delivery.commercialInvoicePdf') }}</el-button>
              <el-button v-if="showCreateInvoiceCta" size="small" plain @click="goCreateInvoiceFromDetail">
                {{ t('pages.delivery.createArInvoice') }}
              </el-button>
              <el-button v-else-if="showViewOutstandingCta" size="small" type="primary" plain @click="goViewOutstandingFromDetail">
                {{ t('pages.delivery.viewOutstandingInvoice') }}
              </el-button>
              <el-button v-if="canUpdate" size="small" type="success" plain :loading="markingSj" @click="markSjPrinted">
                {{ t('pages.delivery.markSjPrinted') }}
              </el-button>
            </div>
          </div>
        </section>

      </div>
      <template #footer>
        <div class="delivery-dialog-footer">
          <el-button
            v-if="canDeleteCurrent"
            type="danger"
            plain
            @click="openDeleteFromDetail"
          >
            {{ t('pages.delivery.deleteAction') }}
          </el-button>
          <el-button type="primary" @click="detailVisible = false">{{ t('pages.delivery.closeDetail') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="arrangeVisible"
      :title="t('pages.delivery.arrangeDialogTitle')"
      width="1120px"
      destroy-on-close
      align-center
      class="delivery-arrange-dialog"
      @open="loadReadyToShip"
      @closed="resetArrange"
    >
      <p class="delivery-dialog-sub">{{ t('pages.delivery.arrangeDialogSub') }}</p>

      <section class="delivery-form-section">
        <header class="delivery-form-section__head delivery-form-section__head--row">
          <div>
            <h4 class="delivery-form-section__title">{{ t('pages.delivery.arrangeGroupLots') }}</h4>
            <p v-if="arrangeSelected.length" class="delivery-form-section__sub">
              {{ t('pages.delivery.arrangeSelectedCount', { n: arrangeSelected.length }) }}
            </p>
          </div>
          <div class="delivery-arrange-toolbar">
            <el-input
              v-model="arrangeKeyword"
              clearable
              class="delivery-arrange-search"
              :placeholder="t('pages.delivery.arrangeSearchPlaceholder')"
              @keyup.enter="loadReadyToShip"
            />
            <el-button :icon="RefreshLeft" :loading="arrangeLoading" @click="loadReadyToShip">
              {{ t('common.refresh') }}
            </el-button>
          </div>
        </header>

        <div class="admin-table-scroll delivery-arrange-table-wrap">
          <el-table
            ref="arrangeTableRef"
            :data="readyRows"
            v-loading="arrangeLoading"
            border
            size="small"
            class="admin-table delivery-arrange-table"
            max-height="42vh"
            :row-key="(row) => `${row.packing_id}:${row.production_detail_id}:${row.packing_detail_id || ''}`"
            :empty-text="t('pages.delivery.arrangeEmpty')"
            @selection-change="onArrangeSelectionChange"
          >
            <el-table-column type="selection" width="48" fixed="left" :selectable="arrangeRowSelectable" />
            <el-table-column prop="lot_no" :label="t('pages.delivery.columns.lotNo')" min-width="150" show-overflow-tooltip fixed="left" />
            <el-table-column prop="packing_number" :label="t('pages.delivery.columns.packingNumber')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="so_number" :label="t('pages.delivery.columns.soNumber')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="customer_name" :label="t('pages.delivery.columns.factory')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="brand" :label="t('pages.delivery.columns.buyer')" width="100" show-overflow-tooltip />
            <el-table-column prop="material_name" :label="t('pages.delivery.columns.materialName')" min-width="120" show-overflow-tooltip />
            <el-table-column :label="t('pages.delivery.arrangeQtyAvailable')" width="100" align="right">
              <template #default="{ row }">{{ formatNumber(row.qty_available, 2) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.delivery.qtyToShip')" width="120" fixed="right">
              <template #default="{ row }">
                <el-input
                  v-model="arrangeQty[`${row.packing_id}:${row.production_detail_id}`]"
                  type="number"
                  step="0.01"
                  size="small"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>

      <div v-if="arrangeSelected.length" class="delivery-arrange-summary">
        <p class="delivery-arrange-summary__title">{{ t('pages.delivery.overallTitle') }}</p>
        <div class="delivery-arrange-summary__grid">
          <div class="delivery-arrange-summary__item">
            <span class="delivery-arrange-summary__label">{{ t('pages.delivery.overallLines') }}</span>
            <span class="delivery-arrange-summary__value">{{ arrangeOverall.line_count }}</span>
          </div>
          <div class="delivery-arrange-summary__item">
            <span class="delivery-arrange-summary__label">{{ t('pages.delivery.columns.factory') }}</span>
            <span class="delivery-arrange-summary__value">{{ arrangeOverall.customer_name || '—' }}</span>
          </div>
          <div class="delivery-arrange-summary__item">
            <span class="delivery-arrange-summary__label">{{ t('pages.delivery.columns.buyer') }}</span>
            <span class="delivery-arrange-summary__value">{{ arrangeOverall.brand || '—' }}</span>
          </div>
          <div class="delivery-arrange-summary__item">
            <span class="delivery-arrange-summary__label">{{ t('pages.delivery.overallSf') }}</span>
            <span class="delivery-arrange-summary__value">{{ formatNumber(arrangeOverall.total_sf, 2) }}</span>
          </div>
          <div class="delivery-arrange-summary__item">
            <span class="delivery-arrange-summary__label">{{ t('pages.delivery.overallRoll') }}</span>
            <span class="delivery-arrange-summary__value">{{ arrangeOverall.total_roll }}</span>
          </div>
        </div>
      </div>

      <section class="delivery-form-section delivery-form-section--last">
        <header class="delivery-form-section__head">
          <h4 class="delivery-form-section__title">{{ t('pages.delivery.arrangeGroupShipment') }}</h4>
        </header>
        <el-form label-position="top" class="delivery-form">
          <el-row :gutter="16">
            <el-col :xs="24" :sm="8">
              <el-form-item :label="t('common.date')" required>
                <el-date-picker v-model="arrangeForm.delivery_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="8">
              <el-form-item :label="t('pages.delivery.deliveryType')">
                <el-select v-model="arrangeForm.delivery_type" class="w-full" @change="arrangeTypeTouched = true">
                  <el-option :label="t('status.production')" value="production" />
                  <el-option :label="t('status.sample')" value="sample" />
                  <el-option :label="t('status.return')" value="return" />
                  <el-option :label="t('status.subcont')" value="subcont" />
                  <el-option :label="t('status.claim')" value="claim" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="8">
              <el-form-item :label="t('common.vehicle')">
                <el-input v-model="arrangeForm.vehicle_number" clearable />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :sm="8">
              <el-form-item :label="t('common.driver')">
                <el-input v-model="arrangeForm.driver_name" clearable />
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <el-form-item :label="t('pages.delivery.manualDeliveryRemark')">
                <el-input v-model="arrangeForm.destination" type="textarea" :rows="2" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </section>

      <template #footer>
        <div class="delivery-dialog-footer">
          <el-button @click="arrangeVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button v-if="canCreate" type="primary" :loading="arrangeSaving" @click="submitArrange">
            {{ t('pages.delivery.arrangeSubmit') }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="returnVisible"
      :title="t('pages.delivery.returnDialogTitle')"
      width="480px"
      destroy-on-close
      align-center
      @closed="resetReturnForm"
    >
      <el-form v-if="returnCtx" label-position="top">
        <el-descriptions :column="1" border size="small" class="mb-4">
          <el-descriptions-item :label="t('pages.delivery.returnShippedQty')">
            {{ formatNumber(returnCtx.shipped, 2) }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.delivery.returnAlready')">
            {{ formatNumber(returnCtx.already, 2) }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.delivery.returnRemaining')">
            {{ formatNumber(returnCtx.remaining, 2) }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('pages.delivery.returnUnitPrice')">
            {{ formatNumber(returnCtx.unitPrice, 4) || '—' }}
          </el-descriptions-item>
          <el-descriptions-item v-if="returnCtx.invoiceNumber" :label="t('pages.delivery.columns.invNumber')">
            {{ returnCtx.invoiceNumber }}
          </el-descriptions-item>
        </el-descriptions>
        <el-form-item :label="t('pages.delivery.returnQtyLabel')" required>
          <el-input
            v-model="returnForm.qty"
            type="number"
            step="0.01"
            min="0"
            :placeholder="t('pages.delivery.returnQtyHint')"
          />
          <p class="delivery-field-hint mt-1">{{ t('pages.delivery.returnQtyHint') }}</p>
        </el-form-item>
        <el-form-item :label="t('pages.delivery.returnRemarkLabel')">
          <el-input v-model="returnForm.remark" type="textarea" :rows="2" clearable />
        </el-form-item>
        <el-alert
          type="info"
          :closable="false"
          show-icon
          :title="`${t('pages.delivery.returnCreditPreview')}: ${formatNumber(returnCreditPreview, 2)}`"
        />
      </el-form>
      <template #footer>
        <el-button @click="returnVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="warning" :loading="returnSaving" @click="submitReturn">
          {{ t('pages.delivery.returnAction') }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="deleteVisible"
      :title="t('pages.delivery.deleteDialogTitle')"
      width="480px"
      destroy-on-close
      align-center
      @closed="resetDeleteForm"
    >
      <p class="delivery-field-hint mb-3">{{ t('pages.delivery.deleteHint') }}</p>
      <el-form label-position="top">
        <el-form-item :label="t('pages.delivery.deleteReasonLabel')" required>
          <el-input v-model="deleteReason" type="textarea" :rows="3" maxlength="2000" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deleteVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="danger" :loading="deleteSaving" @click="submitDelete">
          {{ t('pages.delivery.deleteAction') }}
        </el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Van, Download, Loading, RefreshLeft, Refresh } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import { can } from '../../security/permissions'
import { formatDate, formatNumber, statusType } from '../../utils/format'
import { createPoOrderDateShortcuts, poOrderCategoryLabel } from '../../utils/poList.js'
import { buildPageParams, fromElSortChange, normalizePageResult } from '../../utils/tableQuery'
import {
  addDeliveryDetail,
  createDelivery,
  createDeliveryFromPackingLines,
  closeDocumentWindows,
  fetchAuthenticatedDocument,
  reserveDocumentWindows,
  getDelivery,
  getPacking,
  getPo,
  getProduction,
  listCustomers,
  listInvoice,
  listDeliveryDetails,
  listMarketingDeliveryLines,
  listPacking,
  listProductionDetails,
  listReadyToShip,
  markSuratJalanPrinted,
  marketingDeliveryXlsxPath,
  returnDeliveryDetail,
  scanDeliveryPackingOut,
  deleteDelivery,
  toIsoDate,
  setDeliveryFoc,
  updateDelivery,
  updateDeliveryDetail,
  deleteDeliveryDetail,
} from '../../api/client'

const { t, te } = useI18n()
const canCreate = can('delivery', 'create')
const canUpdate = can('delivery', 'update')
const canPrint = can('delivery', 'print')
const canCreateInvoice = can('invoice', 'create')
const canDeleteDelivery = canUpdate || can('invoice', 'update')
/** Align with API roles: admin, warehouse, finance, marketing */
const canReturn = canUpdate || can('invoice', 'update') || canPrint
const route = useRoute()
const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const exporting = ref(false)
const batchPrinting = ref(false)
const listTableRef = ref(null)
const listSelection = ref([])
const keyword = ref('')
const statusFilter = ref('')
const packingStatusFilter = ref('')
const invplFilter = ref('')
const shipDateRange = ref(null)
const factoryCodeFilter = ref('')
const poCategoryFilter = ref('')
const filterCustomerId = ref(null)
const showDetailCols = ref(false)
const deliveryDateShortcuts = computed(() => createPoOrderDateShortcuts(t))
const currentPage = ref(1)
const pageSize = ref(50)
const sortBy = ref(null)
const sortDir = ref('desc')
const totalLines = ref(0)

const selectedDeliveryIds = computed(() => {
  const ids = []
  const seen = new Set()
  for (const row of listSelection.value || []) {
    const id = Number(row?.delivery_id)
    if (!Number.isFinite(id) || id <= 0 || seen.has(id)) continue
    seen.add(id)
    ids.push(id)
  }
  return ids
})

function deliveryLineRowKey(row) {
  if (row?.delivery_detail_id != null) return `dd:${row.delivery_detail_id}`
  if (row?.id != null && row?.delivery_id != null) return `d:${row.delivery_id}:r:${row.id}`
  return `d:${row?.delivery_id || 'x'}:sj:${row?.surat_jalan_no || ''}:lot:${row?.lot_no || ''}`
}

function onListSelectionChange(sel) {
  listSelection.value = sel || []
}

function clearListSelection() {
  listSelection.value = []
  listTableRef.value?.clearSelection?.()
}

async function printSelectedSj() {
  const ids = selectedDeliveryIds.value
  if (!ids.length) {
    ElMessage.warning(t('pages.delivery.selectRowsToPrint'))
    return
  }
  let popups = []
  batchPrinting.value = true
  try {
    popups = reserveDocumentWindows(ids.length)
    for (let i = 0; i < ids.length; i += 1) {
      await fetchAuthenticatedDocument(`/documents/surat-jalan/${ids[i]}`, {
        mode: 'open',
        targetWindow: popups[i],
      })
      popups[i] = null
    }
    ElMessage.success(t('pages.delivery.batchPrintSjOk', { n: ids.length }))
  } catch (e) {
    closeDocumentWindows(popups)
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    batchPrinting.value = false
  }
}

async function printSelectedSjAndInvpl() {
  const ids = selectedDeliveryIds.value
  if (!ids.length) {
    ElMessage.warning(t('pages.delivery.selectRowsToPrint'))
    return
  }
  let popups = []
  batchPrinting.value = true
  try {
    popups = reserveDocumentWindows(ids.length * 2)
    for (let i = 0; i < ids.length; i += 1) {
      const foc = lineRows.value.some((row) => Number(row.delivery_id) === Number(ids[i]) && row.is_foc)
      await fetchAuthenticatedDocument(`/documents/surat-jalan/${ids[i]}`, {
        mode: 'open',
        targetWindow: popups[i * 2],
      })
      popups[i * 2] = null
      await fetchAuthenticatedDocument(invplByDeliveryPath(ids[i], foc), {
        mode: 'open',
        targetWindow: popups[i * 2 + 1],
      })
      popups[i * 2 + 1] = null
    }
    ElMessage.success(t('pages.delivery.batchPrintSjInvplOk', { n: ids.length }))
  } catch (e) {
    closeDocumentWindows(popups)
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    batchPrinting.value = false
  }
}
const filtersReady = ref(false)
const lineRows = ref([])
const customers = ref([])
const packings = ref([])

const deliveryListStats = computed(() => {
  const rows = lineRows.value || []
  let draft = 0
  let sent = 0
  for (const r of rows) {
    const st = (r.delivery_status || '').toLowerCase()
    if (st === 'sent') sent += 1
    else if (st === 'draft') draft += 1
  }
  return {
    total: totalLines.value,
    shown: rows.length,
    draft,
    sent,
  }
})

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

function customerFilterQuery() {
  if (!filterCustomerId.value) return ''
  const c = customers.value.find((x) => x.id === filterCustomerId.value)
  if (!c) return ''
  return [c.code, c.name].filter(Boolean).join(' ').trim()
}

function deliveryStatusLabel(st) {
  if (st && te(`status.${st}`)) return t(`status.${st}`)
  return st || t('common.emptyValue')
}

function categoryLabel(cat) {
  return poOrderCategoryLabel(cat, t, te)
}

function packingStatusLabel(st) {
  const key = (st || '').toLowerCase()
  if (key && te(`status.${key}`)) return t(`status.${key}`)
  return st || t('common.emptyValue')
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
  const cu = customerFilterQuery()
  if (cu) p.customer = cu
  const qkw = keyword.value.trim()
  if (qkw) p.q = qkw
  return p
}

function resetDeliveryFilters() {
  statusFilter.value = ''
  packingStatusFilter.value = ''
  invplFilter.value = ''
  shipDateRange.value = null
  factoryCodeFilter.value = ''
  poCategoryFilter.value = ''
  filterCustomerId.value = null
  keyword.value = ''
  currentPage.value = 1
  load()
}

async function loadMasterData() {
  try {
    const [cust, packRaw] = await Promise.all([listCustomers(), listPacking({ page_size: 200 })])
    customers.value = cust
    packings.value = normalizePageResult(packRaw).items
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function load() {
  loading.value = true
  try {
    const linesResp = await listMarketingDeliveryLines(
      buildPageParams({
        page: currentPage.value,
        pageSize: pageSize.value,
        sortBy: sortBy.value,
        sortDir: sortDir.value,
        extra: deliveryLinesQueryParams(),
      }),
    )
    const pageData = normalizePageResult(linesResp, {
      page: currentPage.value,
      pageSize: pageSize.value,
    })
    // legacy `data` field still supported by normalizePageResult via items fallback —
    // also accept marketing envelope shape
    const lines = pageData.items.length
      ? pageData.items
      : Array.isArray(linesResp?.data)
        ? linesResp.data
        : []
    const visible = lines.filter((r) => {
      if (r?.is_deleted) return false
      const st = String(r?.delivery_status || r?.status || '').toLowerCase()
      return st !== 'cancelled' && st !== 'canceled'
    })
    totalLines.value = Number(linesResp?.total ?? pageData.total ?? visible.length)
    lineRows.value = visible.map((r) => ({
      ...r,
      delivery_date: r.delivery_date ? String(r.delivery_date).slice(0, 10) : '',
      po_date: r.po_date ? String(r.po_date).slice(0, 10) : '',
    }))
    clearListSelection()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

function onDeliverySortChange(payload) {
  const mapped = fromElSortChange(payload)
  sortBy.value = mapped.sortBy
  sortDir.value = mapped.sortDir
  currentPage.value = 1
  load()
}

let filterLoadTimer = null
function scheduleLoad() {
  if (!filtersReady.value) return
  if (filterLoadTimer) clearTimeout(filterLoadTimer)
  filterLoadTimer = setTimeout(() => {
    load()
  }, 300)
}

watch(
  [keyword, statusFilter, packingStatusFilter, invplFilter, shipDateRange, factoryCodeFilter, poCategoryFilter, filterCustomerId],
  () => {
    currentPage.value = 1
    scheduleLoad()
  },
)

watch([currentPage, pageSize], () => {
  if (!filtersReady.value) return
  load()
})

onMounted(async () => {
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
  await loadMasterData()
  if (q.customer != null && String(q.customer).trim()) {
    const needle = String(q.customer).trim().toLowerCase()
    const matched = customers.value.find((c) => {
      const hay = [c.code, c.name].filter(Boolean).join(' ').toLowerCase()
      return hay.includes(needle)
    })
    if (matched) filterCustomerId.value = matched.id
    else keyword.value = needle
  }
  try {
    await load()
    const deliveryIdRaw = route.query.delivery_id
    const deliveryId = Number(deliveryIdRaw)
    if (!Number.isNaN(deliveryId) && deliveryId > 0) {
      const target = lineRows.value.find((r) => Number(r.delivery_id) === deliveryId)
      if (target) openDetailFromLine(target)
      else openDetailById(deliveryId)
    }
  } finally {
    filtersReady.value = true
  }
})

function goPoFromLine(row) {
  if (!row?.po_id) return
  router.push({ path: '/admin/po', query: { po_id: String(row.po_id) } })
}

const isSentOrDeleted = computed(() => {
  const row = detailRow.value
  if (row?.is_deleted) return true
  const status = (row?.status || '').toLowerCase()
  return status === 'sent' || status === 'cancelled' || status === 'canceled'
})
const isSentOrCancelled = isSentOrDeleted

const isDetailDraft = computed(() => {
  const status = String(detailRow.value?.status || '').toLowerCase()
  return status === 'draft' || status === ''
})

const canEditDraftLines = computed(() => canUpdate && isDetailDraft.value)
const canEditSjNumber = computed(() => canUpdate && isDetailDraft.value)

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
const createCustomerFromPacking = ref(false)
const createTypeTouched = ref(false)
const arrangeTypeTouched = ref(false)
const arrangeTableRef = ref(null)
const DELIVERY_TYPE_VALUES = new Set(['production', 'sample', 'return', 'subcont', 'claim'])

function sharedDeliveryType(rows) {
  const cats = [
    ...new Set(
      (rows || [])
        .map((row) => String(row?.po_category || '').trim().toLowerCase())
        .filter((cat) => DELIVERY_TYPE_VALUES.has(cat)),
    ),
  ]
  return cats.length === 1 ? cats[0] : ''
}

function resetCreateForm() {
  createCandidateProdDetails.value = []
  createSelectedLines.value = []
  createCustomerFromPacking.value = false
  Object.keys(createLineQty).forEach((k) => delete createLineQty[k])
}

function openCreate() {
  form.customer_id = null
  form.packing_id = null
  createTypeTouched.value = false
  form.delivery_type = 'production'
  form.delivery_date = new Date().toISOString().slice(0, 10)
  form.delivery_zone = 'outtown'
  form.vehicle_number = ''
  form.driver_name = ''
  form.destination = ''
  form.status = 'draft'
  resetCreateForm()
  formVisible.value = true
}

async function onCreatePackingChange(packingId) {
  resetCreateForm()
  createCustomerFromPacking.value = false
  if (!packingId) {
    form.customer_id = null
    return
  }
  createProdDetailsLoading.value = true
  try {
    const pk = await getPacking(packingId)
    if (!pk?.production_id) {
      ElMessage.warning(t('pages.delivery.noProductionLines'))
      return
    }
    const prod = await getProduction(pk.production_id)
    if (prod?.po_id) {
      const po = await getPo(prod.po_id)
      if (po?.customer_id) {
        form.customer_id = po.customer_id
        createCustomerFromPacking.value = true
      }
      const cat = String(po?.po_category || '').trim().toLowerCase()
      if (!createTypeTouched.value && DELIVERY_TYPE_VALUES.has(cat)) {
        form.delivery_type = cat
      }
    }
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
const detailInvoice = ref(null)
const detailLines = ref([])
const detailLoading = ref(false)
const markingSj = ref(false)
const scanSjCode = ref('')
const scanningOut = ref(false)
const invplFoc = ref(false)

function invplByDeliveryPath(deliveryId, foc = invplFoc.value) {
  const q = foc ? '?foc=1' : ''
  return `/documents/invpl-by-delivery/${deliveryId}${q}`
}

const bcForm = reactive({
  bc_number: '',
  bc_date: '',
})
const bcSaving = ref(false)
const zoneEdit = ref('outtown')
const zoneSaving = ref(false)
const sjNumberEdit = ref('')
const sjNumberSaving = ref(false)
const lineQtySavingId = ref(null)

function deliveryZoneLabel(z) {
  const v = (z || '').toLowerCase()
  if (v === 'local') return t('pages.delivery.deliveryZoneLocal')
  if (v === 'outtown') return t('pages.delivery.deliveryZoneOuttown')
  return t('pages.delivery.deliveryZoneOuttown')
}

function resetDetail() {
  detailRow.value = null
  detailLines.value = []
  detailInvoice.value = null
  bcForm.bc_number = ''
  bcForm.bc_date = ''
  sjNumberEdit.value = ''
  invplFoc.value = false
}

async function saveInvplFoc(value) {
  if (!detailRow.value?.id) return
  const next = !!value
  try {
    const full = await setDeliveryFoc(detailRow.value.id, { is_foc: next })
    detailRow.value = { ...detailRow.value, ...full, customer_name: detailRow.value.customer_name }
    invplFoc.value = !!full.is_foc
    const deliveryId = detailRow.value.id
    lineRows.value = lineRows.value.map((row) =>
      Number(row.delivery_id) === Number(deliveryId) ? { ...row, is_foc: !!full.is_foc } : row,
    )
  } catch (e) {
    invplFoc.value = !next
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function refreshDetailInvoice(deliveryId) {
  try {
    const invoices = await listInvoice({ delivery_id: deliveryId, page_size: 20 })
    const items = normalizePageResult(invoices).items
    detailInvoice.value = items.length ? items[0] : null
  } catch {
    detailInvoice.value = null
  }
}

function detailLineMoreItems(row) {
  const items = []
  if (canEditDraftLines.value) {
    items.push({ command: 'delete', label: t('pages.delivery.deleteLineAction') })
  }
  if (canShowReturn(row, true)) {
    items.push({ command: 'return', label: t('pages.delivery.returnAction') })
  }
  return items
}

async function onDetailLineMore(command, row) {
  if (command === 'return') {
    openReturnFromDetailLine(row)
    return
  }
  if (command === 'delete') {
    await deleteDetailLine(row)
  }
}

async function saveSjNumber() {
  if (!detailRow.value?.id) return
  const next = String(sjNumberEdit.value || '').trim()
  if (!next) {
    ElMessage.warning(t('pages.delivery.sjNumberRequired'))
    return
  }
  sjNumberSaving.value = true
  try {
    await updateDelivery(detailRow.value.id, { delivery_number: next })
    ElMessage.success(t('pages.delivery.sjNumberSaved'))
    await load()
    const full = await getDelivery(detailRow.value.id)
    detailRow.value = { ...full, customer_name: custName(full.customer_id) }
    sjNumberEdit.value = full.delivery_number || ''
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    sjNumberSaving.value = false
  }
}

async function saveDetailLineQty(row, val) {
  if (!canEditDraftLines.value || !row?.id) return
  const qty = Number(val)
  if (!Number.isFinite(qty) || qty <= 0) {
    ElMessage.warning(t('pages.delivery.lineQtyInvalid'))
    return
  }
  if (lineQtySavingId.value === row.id) return
  lineQtySavingId.value = row.id
  try {
    await updateDeliveryDetail(row.id, { qty })
    ElMessage.success(t('pages.delivery.lineQtySaved'))
    const lines = await listDeliveryDetails(detailRow.value.id)
    detailLines.value = lines
    await refreshDetailInvoice(detailRow.value.id)
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    try {
      const lines = await listDeliveryDetails(detailRow.value.id)
      detailLines.value = lines
    } catch {
      /* ignore */
    }
  } finally {
    lineQtySavingId.value = null
  }
}

async function deleteDetailLine(row) {
  if (!canEditDraftLines.value || !row?.id) return
  try {
    await ElMessageBox.confirm(
      t('pages.delivery.deleteLineConfirm'),
      t('pages.delivery.deleteLineAction'),
      { type: 'warning', confirmButtonText: t('common.delete'), cancelButtonText: t('common.cancel') },
    )
  } catch {
    return
  }
  try {
    await deleteDeliveryDetail(row.id)
    ElMessage.success(t('pages.delivery.deleteLineDone'))
    const lines = await listDeliveryDetails(detailRow.value.id)
    detailLines.value = lines
    await refreshDetailInvoice(detailRow.value.id)
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function isDeliverySent(row) {
  return String(row?.delivery_status || row?.status || '').toLowerCase() === 'sent'
}

function isDeliveryDeleted(row) {
  if (row?.is_deleted) return true
  const status = String(row?.delivery_status || row?.status || '').toLowerCase()
  return status === 'cancelled' || status === 'canceled'
}

function isDeliveryDraft(row) {
  const status = String(row?.delivery_status || row?.status || '').toLowerCase()
  return status === 'draft' || status === ''
}

function canDeleteRow(row) {
  return (
    canDeleteDelivery &&
    row &&
    isDeliveryDraft(row) &&
    !isDeliveryDeleted(row) &&
    !isDeliverySent(row) &&
    (row.delivery_id != null || row.id != null)
  )
}

const canDeleteCurrent = computed(() => canDeleteRow(detailRow.value))

const deleteVisible = ref(false)
const deleteSaving = ref(false)
const deleteReason = ref('')
const deleteTargetId = ref(null)

function resetDeleteForm() {
  deleteReason.value = ''
  deleteTargetId.value = null
}

function openDelete(deliveryId) {
  if (deliveryId == null) return
  deleteTargetId.value = deliveryId
  deleteReason.value = ''
  deleteVisible.value = true
}

function openDeleteFromDetail() {
  if (!detailRow.value?.id) return
  openDelete(detailRow.value.id)
}

async function submitDelete() {
  const reason = deleteReason.value.trim()
  if (!reason) {
    ElMessage.warning(t('pages.delivery.deleteReasonRequired'))
    return
  }
  if (deleteTargetId.value == null) return
  deleteSaving.value = true
  try {
    await deleteDelivery(deleteTargetId.value, reason)
    ElMessage.success(t('pages.delivery.deleteSuccess'))
    deleteVisible.value = false
    detailVisible.value = false
    detailRow.value = null
    await load()
  } catch (e) {
    ElMessage.error(e?.message || String(e))
  } finally {
    deleteSaving.value = false
  }
}

async function deliveryLineAmount(deliveryId) {
  try {
    const lines = await listDeliveryDetails(deliveryId)
    return (lines || []).reduce((sum, r) => sum + (Number(r.amount) || 0), 0)
  } catch {
    return (lineRows.value || [])
      .filter((r) => Number(r.delivery_id) === Number(deliveryId))
      .reduce((sum, r) => sum + (Number(r.amount) || 0), 0)
  }
}

function canCreateInvoiceFromLine(row) {
  return canCreateInvoice && isDeliverySent(row) && !String(row?.invoice_number || '').trim()
}

function canViewInvoiceFromLine(row) {
  return Boolean(String(row?.invoice_number || '').trim())
}

async function goCreateInvoiceFromLine(row) {
  if (!row?.delivery_id) return
  const amount = await deliveryLineAmount(row.delivery_id)
  goInvoiceFromDelivery(row.delivery_id, { create: true, amount })
}

function goViewOutstandingFromLine(row) {
  if (!row?.delivery_id) return
  goInvoiceFromDelivery(row.delivery_id, { create: false })
}

function deliveryListMoreItems(row) {
  const items = []
  if (canCreateInvoiceFromLine(row)) {
    items.push({ command: 'createArInvoice', label: t('pages.delivery.createArInvoice') })
  } else if (canViewInvoiceFromLine(row)) {
    items.push({ command: 'viewOutstanding', label: t('pages.delivery.viewOutstandingInvoice') })
  }
  if (canShowReturn(row)) {
    items.push({ command: 'return', label: t('pages.delivery.returnAction') })
  }
  if (canDeleteRow(row)) {
    items.push({ command: 'delete', label: t('pages.delivery.deleteAction') })
  }
  return items
}

function handleDeliveryListMore(row, command) {
  if (command === 'createArInvoice') goCreateInvoiceFromLine(row)
  else if (command === 'viewOutstanding') goViewOutstandingFromLine(row)
  else if (command === 'return') openReturnFromList(row)
  else if (command === 'delete') openDelete(row.delivery_id)
}

function goInvoiceFromDelivery(deliveryId, { create = false, amount = 0 } = {}) {
  const query = { tab: 'outstanding', delivery_id: String(deliveryId) }
  if (create) query.create = '1'
  if (create && Number(amount) > 0) query.amount = String(amount)
  router.push({ path: '/admin/invoice', query })
}

const showCreateInvoiceCta = computed(() => {
  return isDeliverySent(detailRow.value) && canCreateInvoice && !detailInvoice.value
})

const showViewOutstandingCta = computed(() => {
  return Boolean(detailInvoice.value)
})

async function goCreateInvoiceFromDetail() {
  if (!detailRow.value?.id) return
  const amount = await deliveryLineAmount(detailRow.value.id)
  goInvoiceFromDelivery(detailRow.value.id, {
    create: true,
    amount,
  })
}

function goViewOutstandingFromDetail() {
  if (!detailRow.value?.id) return
  goInvoiceFromDelivery(detailRow.value.id, { create: false })
}

const returnVisible = ref(false)
const returnSaving = ref(false)
const returnCtx = ref(null)
const returnForm = reactive({ qty: '', remark: '' })

const returnCreditPreview = computed(() => {
  const qty = Number(returnForm.qty)
  const price = Number(returnCtx.value?.unitPrice || 0)
  if (!Number.isFinite(qty) || qty <= 0 || !Number.isFinite(price)) return 0
  return Math.round(qty * price * 100) / 100
})

function _num(v) {
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

function canShowReturn(row, fromDetail = false) {
  if (!canReturn || !row) return false
  const detailId = fromDetail ? row.id : row.delivery_detail_id
  if (detailId == null) return false
  const shipped = fromDetail ? _num(row.qty) : _num(row.qty_sf ?? row.qty)
  const already = _num(row.returned_qty)
  if (shipped - already <= 0) return false
  let inv = String(row.invoice_number || '').trim()
  if (!inv && fromDetail) {
    const match = (lineRows.value || []).find((r) => r.delivery_detail_id === detailId)
    inv = String(match?.invoice_number || '').trim()
  }
  const st = String(row.delivery_status || detailRow.value?.status || '').toLowerCase()
  if (!inv && !['sent', 'delivered', 'completed'].includes(st)) return false
  // Require invoice for actionable retur (credit note)
  if (!inv) return false
  return true
}

function resetReturnForm() {
  returnCtx.value = null
  returnForm.qty = ''
  returnForm.remark = ''
}

function openReturnDialog({ detailId, shipped, already, unitPrice, invoiceNumber, deliveryId }) {
  const rem = Math.max(shipped - already, 0)
  if (rem <= 0) {
    ElMessage.warning(t('pages.delivery.returnQtyExceed'))
    return
  }
  returnCtx.value = {
    detailId,
    deliveryId,
    shipped,
    already,
    remaining: rem,
    unitPrice: unitPrice || 0,
    invoiceNumber: invoiceNumber || '',
  }
  returnForm.qty = ''
  returnForm.remark = ''
  returnVisible.value = true
}

function openReturnFromList(row) {
  if (!row?.delivery_detail_id) return
  const shipped = _num(row.qty_sf ?? row.qty)
  const already = _num(row.returned_qty)
  const inv = String(row.invoice_number || '').trim()
  if (!inv) {
    ElMessage.warning(t('pages.delivery.returnNeedInvoice'))
    return
  }
  openReturnDialog({
    detailId: row.delivery_detail_id,
    deliveryId: row.delivery_id,
    shipped,
    already,
    unitPrice: _num(row.unit_price),
    invoiceNumber: inv,
  })
}

function openReturnFromDetailLine(row) {
  if (!row?.id) return
  const match = (lineRows.value || []).find((r) => r.delivery_detail_id === row.id)
  const shipped = _num(row.qty)
  const already = _num(row.returned_qty)
  const inv = String(match?.invoice_number || '').trim()
  if (!inv) {
    ElMessage.warning(t('pages.delivery.returnNeedInvoice'))
    return
  }
  openReturnDialog({
    detailId: row.id,
    deliveryId: detailRow.value?.id || match?.delivery_id,
    shipped,
    already,
    unitPrice: _num(match?.unit_price),
    invoiceNumber: inv,
  })
}

async function submitReturn() {
  if (!returnCtx.value?.detailId) return
  const qty = _num(returnForm.qty)
  if (qty <= 0) {
    ElMessage.warning(t('pages.delivery.returnQtyRequired'))
    return
  }
  if (qty > returnCtx.value.remaining + 1e-9) {
    ElMessage.warning(t('pages.delivery.returnQtyExceed'))
    return
  }
  returnSaving.value = true
  try {
    const body = { qty }
    const remark = (returnForm.remark || '').trim()
    if (remark) body.remark = remark
    const res = await returnDeliveryDetail(returnCtx.value.detailId, body)
    ElMessage.success(
      `${t('pages.delivery.returnSuccess')} (−${formatNumber(res?.credit_amount, 2)})`,
    )
    returnVisible.value = false
    await load()
    if (detailVisible.value && detailRow.value?.id) {
      const lines = await listDeliveryDetails(detailRow.value.id)
      detailLines.value = lines
    }
  } catch (e) {
    ElMessage.error(e?.message || String(e))
  } finally {
    returnSaving.value = false
  }
}

function openDetailFromLine(row) {
  if (row?.delivery_id == null) return
  openDetailById(row.delivery_id)
}

async function openDetailById(deliveryId) {
  detailVisible.value = true
  detailLoading.value = true
  detailRow.value = null
  detailLines.value = []
  detailInvoice.value = null
  try {
    const full = await getDelivery(deliveryId)
    if (!full?.id) {
      throw new Error(t('pages.delivery.detailLoadFailed'))
    }
    detailRow.value = { ...full, customer_name: custName(full.customer_id) }
    zoneEdit.value = (full.delivery_zone || 'outtown').toLowerCase() === 'local' ? 'local' : 'outtown'
    bcForm.bc_number = full.bc_number || ''
    bcForm.bc_date = full.bc_date ? String(full.bc_date).slice(0, 10) : ''
    sjNumberEdit.value = full.delivery_number || ''
    invplFoc.value = !!full.is_foc
    const lines = await listDeliveryDetails(deliveryId)
    detailLines.value = lines
    await refreshDetailInvoice(deliveryId)
  } catch (e) {
    detailRow.value = null
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    detailLoading.value = false
  }
}

async function openSjAndInvpl() {
  if (!detailRow.value?.id) return
  let popups = []
  try {
    popups = reserveDocumentWindows(2)
    await fetchAuthenticatedDocument(`/documents/surat-jalan/${detailRow.value.id}`, {
      mode: 'open',
      targetWindow: popups[0],
    })
    popups[0] = null
    await fetchAuthenticatedDocument(invplByDeliveryPath(detailRow.value.id), {
      mode: 'open',
      targetWindow: popups[1],
    })
    popups[1] = null
  } catch (e) {
    closeDocumentWindows(popups)
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function openSjDotmatrix() {
  if (!detailRow.value?.id) return
  try {
    await fetchAuthenticatedDocument(`/documents/surat-jalan/${detailRow.value.id}/dotmatrix`, { mode: 'open' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadSjPdf() {
  if (!detailRow.value?.id) return
  try {
    await fetchAuthenticatedDocument(`/documents/surat-jalan/${detailRow.value.id}/pdf`, {
      mode: 'download',
      downloadFallbackName: `surat-jalan-${detailRow.value.delivery_number || detailRow.value.id}.pdf`,
    })
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

async function submitSjScanOut() {
  const code = String(scanSjCode.value || '').trim()
  if (!code) {
    ElMessage.warning(t('pages.delivery.scanOutPlaceholder'))
    return
  }
  scanningOut.value = true
  try {
    const res = await scanDeliveryPackingOut({ delivery_number: code })
    ElMessage.success(res?.message || t('pages.delivery.scanOutSuccess'))
    scanSjCode.value = ''
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    scanningOut.value = false
  }
}

const arrangeVisible = ref(false)
const arrangeLoading = ref(false)
const arrangeSaving = ref(false)
const arrangeKeyword = ref('')
const readyRows = ref([])
const arrangeSelected = ref([])
const arrangeQty = reactive({})
const arrangeForm = reactive({
  delivery_date: '',
  delivery_type: 'production',
  vehicle_number: '',
  driver_name: '',
  destination: '',
})

const arrangeOverall = computed(() => {
  let totalSf = 0
  let totalRoll = 0
  const brands = new Set()
  const customers = new Set()
  for (const row of arrangeSelected.value) {
    const qtyKey = `${row.packing_id}:${row.production_detail_id}`
    const raw = arrangeQty[qtyKey] ?? arrangeQty[row.production_detail_id]
    const q = raw != null && String(raw).trim() !== '' ? Number(raw) : row.qty_available
    if (Number.isFinite(q)) totalSf += q
    if (row.qty_roll != null) totalRoll += Number(row.qty_roll) || 0
    if (row.brand) brands.add(row.brand)
    if (row.customer_name) customers.add(row.customer_name)
  }
  return {
    line_count: arrangeSelected.value.length,
    total_sf: totalSf,
    total_roll: totalRoll,
    brand: brands.size === 1 ? [...brands][0] : '',
    customer_name: customers.size === 1 ? [...customers][0] : '',
  }
})

function openArrange() {
  arrangeForm.delivery_date = new Date().toISOString().slice(0, 10)
  arrangeTypeTouched.value = false
  arrangeForm.delivery_type = 'production'
  arrangeForm.vehicle_number = ''
  arrangeForm.driver_name = ''
  arrangeForm.destination = ''
  arrangeKeyword.value = ''
  arrangeVisible.value = true
}

function resetArrange() {
  readyRows.value = []
  arrangeSelected.value = []
  Object.keys(arrangeQty).forEach((k) => delete arrangeQty[k])
}

async function loadReadyToShip() {
  arrangeLoading.value = true
  try {
    const kw = arrangeKeyword.value.trim()
    readyRows.value = await listReadyToShip({ lot_keyword: kw || undefined, limit: 500 })
    for (const row of readyRows.value) {
      const qtyKey = `${row.packing_id}:${row.production_detail_id}`
      if (arrangeQty[qtyKey] == null) {
        arrangeQty[qtyKey] = String(row.qty_available ?? '')
      }
    }
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    readyRows.value = []
  } finally {
    arrangeLoading.value = false
  }
}

function onArrangeSelectionChange(selection) {
  arrangeSelected.value = selection || []
  if (arrangeTypeTouched.value) return
  const shared = sharedDeliveryType(arrangeSelected.value)
  if (shared) arrangeForm.delivery_type = shared
}

function arrangeRowSelectable(row) {
  if (!arrangeSelected.value.length) return true
  const first = arrangeSelected.value[0]
  return row.customer_id === first.customer_id && row.brand === first.brand
}

async function submitArrange() {
  if (!arrangeSelected.value.length) {
    ElMessage.warning(t('pages.delivery.arrangePickWarning'))
    return
  }
  if (!arrangeForm.delivery_date) {
    ElMessage.warning(t('pages.delivery.arrangeDateWarning'))
    return
  }
  const packingId = arrangeSelected.value[0].packing_id
  const lines = arrangeSelected.value.map((row) => {
    const qtyKey = `${row.packing_id}:${row.production_detail_id}`
    const raw = arrangeQty[qtyKey] ?? arrangeQty[row.production_detail_id]
    const qty = raw != null && String(raw).trim() !== '' ? Number(raw) : row.qty_available
    return {
      production_detail_id: row.production_detail_id,
      packing_id: row.packing_id != null ? Number(row.packing_id) : undefined,
      packing_detail_id: row.packing_detail_id || undefined,
      qty: Number.isFinite(qty) ? qty : undefined,
      qty_roll: row.qty_roll != null ? row.qty_roll : undefined,
      qty_pcs: row.qty_pcs != null ? row.qty_pcs : undefined,
      weight: row.weight_net != null ? row.weight_net : undefined,
    }
  })
  arrangeSaving.value = true
  try {
    const created = await createDeliveryFromPackingLines({
      packing_id: packingId,
      customer_id: arrangeSelected.value[0].customer_id,
      delivery_date: toIsoDate(arrangeForm.delivery_date) || undefined,
      delivery_type: arrangeForm.delivery_type || 'production',
      delivery_zone: 'outtown',
      vehicle_number: arrangeForm.vehicle_number || undefined,
      driver_name: arrangeForm.driver_name || undefined,
      destination: arrangeForm.destination || undefined,
      lines,
    })
    ElMessage.success(t('pages.delivery.saved'))
    arrangeVisible.value = false
    await load()
    if (created?.id) openDetailById(created.id)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    arrangeSaving.value = false
  }
}
</script>

<style scoped>
.delivery-filter-action-col {
  display: flex;
  align-items: flex-end;
}

.delivery-table-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px 16px;
}

.delivery-column-toggle {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.delivery-selection-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 12px;
}

.delivery-selection-actions__btns {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.delivery-selection-actions__count {
  font-size: 12px;
  color: #475569;
  font-weight: 600;
}

.delivery-scroll-hint {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.delivery-list-table {
  width: 100%;
  min-width: 1180px;
}

.delivery-sj-no {
  margin: 0;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  font: inherit;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
  color: #4a6b7c;
  text-align: left;
}

.delivery-sj-no:hover {
  color: #355566;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.delivery-sj-no--empty {
  cursor: default;
  font-weight: 400;
  color: #94a3b8;
}

.delivery-sj-no--empty:hover {
  color: #94a3b8;
  text-decoration: none;
}

.delivery-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.delivery-dialog-sub {
  margin: 0 0 16px;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: #64748b;
}

.delivery-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.delivery-form-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.delivery-form-section--last {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.delivery-form-section__head {
  margin-bottom: 12px;
}

.delivery-form-section__head--row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.delivery-form-section__title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 700;
  color: #334155;
}

.delivery-form-section__sub {
  margin: 4px 0 0;
  font-size: 0.75rem;
  color: #64748b;
}

.delivery-field-hint {
  margin: 4px 0 0;
  font-size: 0.75rem;
  line-height: 1.4;
  color: #64748b;
}

.delivery-form-empty,
.delivery-form-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 120px;
  padding: 16px;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  background: #f8fafc;
  font-size: 0.8125rem;
  color: #64748b;
  text-align: center;
}

.delivery-form-table-wrap {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.delivery-form-table {
  min-width: 560px;
}

.delivery-arrange-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex: 1 1 16rem;
  max-width: 100%;
  justify-content: flex-end;
}

.delivery-arrange-search {
  min-width: 0;
  flex: 1 1 12rem;
  max-width: 280px;
}

.delivery-arrange-table-wrap {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.delivery-arrange-table {
  min-width: 1040px;
}

.delivery-arrange-summary {
  margin: 16px 0 20px;
  padding: 14px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
}

.delivery-arrange-summary__title {
  margin: 0 0 12px;
  font-size: 0.8125rem;
  font-weight: 700;
  color: #334155;
}

.delivery-arrange-summary__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 16px;
}

@media (min-width: 640px) {
  .delivery-arrange-summary__grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}

.delivery-arrange-summary__item {
  min-width: 0;
}

.delivery-arrange-summary__label {
  display: block;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: #94a3b8;
}

.delivery-arrange-summary__value {
  display: block;
  margin-top: 2px;
  font-size: 0.9375rem;
  font-weight: 700;
  color: #0f172a;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.delivery-form-dialog .el-dialog__body),
:deep(.delivery-arrange-dialog .el-dialog__body),
:deep(.delivery-detail-dialog .el-dialog__body) {
  padding-top: 12px;
  padding-bottom: 8px;
}

:deep(.delivery-detail-dialog .el-dialog__header) {
  padding-bottom: 12px;
  margin-right: 0;
  border-bottom: 1px solid #e2e8f0;
}

:deep(.delivery-detail-dialog .el-dialog__footer) {
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.delivery-detail-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 200px;
  color: #64748b;
  font-size: 0.875rem;
}

.delivery-detail-body {
  max-height: min(72vh, 720px);
  overflow-y: auto;
  padding-right: 4px;
}

.delivery-detail-sj-edit {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}
.delivery-detail-sj-input {
  min-width: 12rem;
  flex: 1;
}
.delivery-detail-sj {
  font-weight: 700;
  letter-spacing: 0.01em;
  color: #0f172a;
}

.delivery-detail-muted {
  color: #94a3b8;
}

.delivery-detail-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.5rem;
  margin-left: 8px;
  padding: 0 6px;
  border-radius: 999px;
  background: #f1f5f9;
  font-size: 0.75rem;
  font-weight: 600;
  color: #475569;
  vertical-align: middle;
}

.delivery-detail-warn {
  margin: 10px 0 0;
  font-size: 0.75rem;
  color: #d97706;
}

.delivery-detail-edit-form :deep(.el-form-item) {
  margin-bottom: 12px;
}

.delivery-detail-edit-form :deep(.el-form-item__label) {
  padding-bottom: 4px;
  line-height: 1.3;
  color: #475569;
  font-weight: 600;
}

.delivery-detail-edit-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.delivery-detail-edit-actions :deep(.el-button) {
  margin-left: 0;
}

.delivery-detail-table-wrap {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: auto;
  max-height: 320px;
}

.delivery-detail-table {
  min-width: 920px;
}

.delivery-detail-table :deep(.el-table__header th) {
  background: #f8fafc;
  color: #475569;
  font-weight: 600;
}

.delivery-detail-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
}

.delivery-detail-foc {
  flex: 0 0 auto;
  height: 28px;
  margin-right: 0;
}

.delivery-detail-toolbar__btns {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  flex: 1 1 16rem;
  min-width: 0;
}

.delivery-detail-toolbar__btns :deep(.el-button) {
  margin-left: 0;
}

:deep(.delivery-detail-desc .el-descriptions__label) {
  width: 7.5rem;
  min-width: 7.5rem;
  color: #64748b;
  font-weight: 600;
  background: #f8fafc !important;
}

:deep(.delivery-detail-desc .el-descriptions__content) {
  color: #0f172a;
}
</style>
