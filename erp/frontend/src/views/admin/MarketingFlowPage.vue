<template>
  <AdminSection :title="pageTitle" :subtitle="pageSubtitle">
    <template #actions>
      <template v-if="section === 'flow'">
        <el-input
          v-model="flowKeyword"
          clearable
          class="marketing-flow-search"
          :placeholder="t('pages.marketingFlow.flowSearchPlaceholder')"
        />
        <el-dropdown trigger="click" @command="handleFlowExportCommand">
          <el-button :icon="Download" :loading="poDailyXlsxLoading">
            {{ t('pages.marketingFlow.flowExportMenu') }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="daily">{{ t('pages.marketingFlow.dailyPoReportXlsx') }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="warning" plain @click="pullCrToday">{{ t('pages.marketingFlow.soToday') }}</el-button>
      </template>
      <template v-else-if="section === 'outstanding'">
        <div class="mkt-out-toolbar">
          <el-dropdown trigger="click" @command="handleOutstandingExportCommand">
            <el-button :icon="Download" :loading="outstandingXlsxLoading || outstandingReturnXlsxLoading || outstandingManualXlsxLoading">
              {{
                outstandingSelection.length
                  ? t('pages.marketingFlow.outstandingExportSelected', { n: outstandingSelection.length })
                  : t('pages.marketingFlow.outstandingExportMenu')
              }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="csv">{{ t('pages.marketingFlow.outstandingDownloadCsv') }}</el-dropdown-item>
                <el-dropdown-item command="xlsx">{{ t('pages.marketingFlow.outstandingDownloadXlsx') }}</el-dropdown-item>
                <el-dropdown-item command="retur">{{ t('pages.marketingFlow.outstandingDownloadReturXlsx') }}</el-dropdown-item>
                <el-dropdown-item command="manual">{{ t('pages.marketingFlow.outstandingDownloadManualXlsx') }}</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <el-button @click="openSnapshotArchive">
            {{ t('pages.marketingFlow.snapshotArchive') }}
          </el-button>
          <el-tooltip :content="t('pages.marketingFlow.checklistActionsHint')" placement="bottom" :disabled="Boolean(outstandingSelection.length)">
            <span class="mkt-out-toolbar-actions">
              <el-button
                type="success"
                plain
                :disabled="!outstandingSelection.length"
                @click="openOutstandingPi"
              >
                {{ t('pages.marketingFlow.actionMakePi') }}
              </el-button>
              <el-button
                type="warning"
                plain
                :disabled="!outstandingSelection.length"
                @click="openOutstandingShip"
              >
                {{ t('pages.marketingFlow.actionShipPacking') }}
              </el-button>
            </span>
          </el-tooltip>
        </div>
      </template>
    </template>

    <PoRekapPrintDialog
      v-if="section === 'flow'"
      v-model="rekapPrintVisible"
      :po-id="rekapPoId"
      :po-number="rekapPoNumber"
      @confirmed="onRekapConfirmed"
    />

    <div v-if="section === 'flow'" class="admin-inner-card mb-4">
      <div class="mkt-section-body">
      <div class="filter-panel mkt-flow-filter-panel mb-4">
        <p class="filter-panel__title">{{ t('common.filter') }}</p>

        <div class="mkt-flow-filter">
          <div class="mkt-flow-filter__fields">
            <label class="mkt-out-field">
              <span class="mkt-out-field__label">{{ t('pages.po.filterOrderDateRange') }}</span>
              <el-date-picker
                v-model="flowDateRange"
                type="daterange"
                unlink-panels
                range-separator="—"
                value-format="YYYY-MM-DD"
                class="mkt-out-field__control"
                :shortcuts="orderDateRangeShortcuts"
                clearable
                :start-placeholder="t('common.placeholder.fromDate')"
                :end-placeholder="t('common.placeholder.toDate')"
              />
            </label>
            <label class="mkt-out-field">
              <span class="mkt-out-field__label">{{ t('common.customer') }}</span>
              <el-select
                v-model="flowCustomerIds"
                clearable
                filterable
                multiple
                collapse-tags
                collapse-tags-tooltip
                class="mkt-out-field__control"
                :placeholder="t('pages.marketingFlow.filterCustomerMulti')"
                @change="onFlowCustomerChange"
              >
                <el-option
                  v-for="c in marketingCustomers"
                  :key="c.id"
                  :label="c.name || c.code || c.id"
                  :value="c.id"
                />
              </el-select>
            </label>
            <label class="mkt-out-field">
              <span class="mkt-out-field__label">{{ t('pages.marketingFlow.filterSoStatus') }}</span>
              <el-select
                v-model="flowSoStatus"
                clearable
                class="mkt-out-field__control"
                :placeholder="t('pages.marketingFlow.filterSoStatusAll')"
                @change="onFlowSoStatusChange"
              >
                <el-option :label="t('status.draft')" value="draft" />
                <el-option :label="t('status.confirmed')" value="confirmed" />
                <el-option :label="t('status.production')" value="production" />
                <el-option :label="t('status.completed')" value="completed" />
                <el-option :label="t('status.cancelled')" value="canceled" />
              </el-select>
            </label>
          </div>
          <p class="mkt-flow-howto">{{ t('pages.marketingFlow.listHowto') }}</p>

          <div class="mkt-flow-filter__footer">
            <div class="mkt-flow-filter__meta">
              <template v-if="filterStage || flowSoStatus">
                <span v-if="filterStage" class="mkt-active-filter">
                  {{ t('pages.marketingFlow.filterStage') }}: {{ labelFor(filterStage) }}
                </span>
                <span v-if="flowSoStatus" class="mkt-active-filter">
                  {{ t('pages.marketingFlow.filterSoStatus') }}: {{ soStatusLabel(flowSoStatus) }}
                </span>
                <el-button link type="primary" size="small" @click="clearFilter">
                  {{ t('common.reset') }}
                </el-button>
              </template>
              <div class="mkt-flow-stat-chips">
                <span class="mkt-flow-stat-chip">
                  {{ t('common.total') }}: <strong>{{ totalFlowRows }}</strong>
                </span>
                <span class="mkt-flow-stat-chip mkt-flow-stat-chip--warn">
                  {{ t('pages.marketingFlow.stuckReason') }}: <strong>{{ flowStats.stuck }}</strong>
                </span>
                <span class="mkt-flow-stat-chip mkt-flow-stat-chip--ok">
                  {{ t('pages.marketingFlow.needAction') }}: <strong>{{ flowStats.actionable }}</strong>
                </span>
              </div>
            </div>
            <div class="mkt-flow-filter__actions">
              <el-button type="primary" :icon="Refresh" :loading="loading" @click="load">
                {{ t('common.refresh') }}
              </el-button>
              <el-button :icon="RefreshLeft" @click="resetFlowFilters">
                {{ t('common.reset') }}
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <div class="mkt-stage-pipeline mb-4">
        <template v-for="(s, i) in stageList" :key="s">
          <div v-if="i > 0" class="mkt-stage-separator">›</div>
          <div
            class="mkt-stage-item"
            :class="pipelineItemClass(s)"
            @click="toggleStageFilter(s)"
          >
            <el-tag
              :type="stageTagType(s)"
              effect="light"
              size="small"
              :class="pipelineTagClass(s)"
            >
              {{ i + 1 }}. {{ labelFor(s) }}
            </el-tag>
            <el-badge
              :value="stageCounts[s]"
              :max="99"
              :type="stageCounts[s] > 0 ? 'primary' : 'info'"
              class="mt-1"
            />
          </div>
        </template>
      </div>

      <div class="admin-table-scroll">
        <el-table
          :data="rows"
          v-loading="loading"
          border
          stripe
          size="small"
          class="admin-table marketing-flow-table"
          :empty-text="t('common.tableEmpty')"
        >
        <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" fixed="left">
          <template #default="{ $index }">{{ flowRowNumber($index) }}</template>
        </el-table-column>
        <el-table-column prop="po_number" :label="t('common.poNo')" min-width="136" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex flex-wrap items-center gap-1">
              <PoItemRevisedDot :row="row" />
              <el-button link type="primary" @click="goPo(row.id)">
                {{ row.po_number || `#${row.id}` }}
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.colPoCustomer')" min-width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.po_customer_ref || t('common.emptyValue') }}
          </template>
        </el-table-column>
        <el-table-column :label="t('common.customerName')" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.customer_name_snapshot || row.customer_code || t('common.emptyValue') }}
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.colMktStage')" min-width="150">
          <template #default="{ row }">
            <el-tag size="small" effect="plain" type="success">
              {{ labelFor(normalizeFlowStage(row.mkt_workflow_stage)) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('pages.marketingFlow.colSoStatus')" width="128">
          <template #default="{ row }">
            <el-tag size="small" :type="statusType(row.status)" effect="plain">
              {{ soStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order_date" :label="t('common.orderDate')" width="110" />
        <el-table-column :label="t('pages.marketingFlow.nextStepCol')" min-width="240">
          <template #default="{ row }">
            <div class="mkt-next-cell">
              <el-tag
                size="small"
                effect="light"
                :type="soListNextStepTagType(row)"
                class="mkt-stuck-tag"
                :class="soListNextStepTagClass(row)"
              >
                <span class="mkt-stuck-tag__inner">
                  <el-icon v-if="soListNextStepKind(row) === 'done'"><CircleCheck /></el-icon>
                  <el-icon v-else-if="soListNextStepBlocked(row)"><Warning /></el-icon>
                  <span class="mkt-stuck-tag__text">{{ soListNextStepLabel(row) }}</span>
                </span>
              </el-tag>
              <p v-if="soListNextStepHint(row)" class="mkt-next-hint">{{ soListNextStepHint(row) }}</p>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <AdminTableActions
              :show-view="true"
              :view-label="t('pages.marketingFlow.openPoDetail')"
              :more-items="soListMoreItems(row)"
              :more-aria-label="t('pages.marketingFlow.moreActions')"
              @view="goPo(row.id)"
              @more="(cmd) => onSoListMore(row, cmd)"
            />
          </template>
        </el-table-column>
      </el-table>
      </div>
      <div class="master-items-pagination mt-3">
        <el-pagination
          v-model:current-page="flowPage"
          v-model:page-size="flowPageSize"
          :total="totalFlowRows"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
      </div>
    </div>

    <OutstandingWorkbenchDialogs
      v-if="section === 'outstanding' || section === 'planning'"
      v-model:schedule-visible="outstandingScheduleVisible"
      v-model:pi-visible="outstandingPiVisible"
      v-model:ship-visible="outstandingShipVisible"
      :rows="workbenchRows"
      @done="onWorkbenchDone"
    />

    <div v-if="section === 'outstanding'" class="admin-inner-card mkt-out-card">
      <div class="mkt-section-body mkt-out-body">
      <div class="filter-panel mkt-out-filter-panel">
        <div class="mkt-out-filter-panel__head">
          <p class="filter-panel__title">{{ t('common.filter') }}</p>
          <div class="mkt-out-filter__actions">
            <el-button type="primary" :icon="Refresh" :loading="outstandingLoading" @click="loadOutstanding">
              {{ t('common.refresh') }}
            </el-button>
            <el-button :icon="RefreshLeft" @click="resetOutstandingFilters">
              {{ t('common.reset') }}
            </el-button>
          </div>
        </div>
        <p class="mkt-flow-howto">{{ t('pages.marketingFlow.outstandingHowto') }}</p>

        <div class="mkt-out-filter">
          <div class="mkt-out-filter__fields">
            <label class="mkt-out-field">
              <span class="mkt-out-field__label">{{ t('pages.marketingFlow.outstandingPoSearch') }}</span>
              <el-input
                v-model="poSearch"
                clearable
                class="mkt-out-field__control"
                :placeholder="t('pages.marketingFlow.outstandingPoSearchPlaceholder')"
                :prefix-icon="Search"
                @change="onOutstandingPoSearchChange"
                @clear="onOutstandingPoSearchChange"
              />
            </label>

            <label class="mkt-out-field">
              <span class="mkt-out-field__label">{{ t('pages.po.filterOrderDateRange') }}</span>
              <el-date-picker
                v-model="outstandingDateRange"
                type="daterange"
                unlink-panels
                range-separator="—"
                value-format="YYYY-MM-DD"
                class="mkt-out-field__control"
                :shortcuts="orderDateRangeShortcuts"
                clearable
                :start-placeholder="t('common.placeholder.fromDate')"
                :end-placeholder="t('common.placeholder.toDate')"
                @change="loadOutstanding"
              />
            </label>

            <label class="mkt-out-field">
              <span class="mkt-out-field__label">{{ t('pages.marketingFlow.filterMaterialStatus') }}</span>
              <el-select
                v-model="materialStatus"
                clearable
                class="mkt-out-field__control"
                @change="loadOutstanding"
              >
                <el-option :label="t('pages.marketingFlow.materialFilterAll')" value="all" />
                <el-option :label="t('pages.marketingFlow.materialFilterSent')" value="sent" />
                <el-option :label="t('pages.marketingFlow.materialFilterNotSent')" value="not_sent" />
                <el-option :label="t('pages.marketingFlow.materialFilterCancelled')" value="cancelled" />
              </el-select>
            </label>

            <label class="mkt-out-field">
              <span class="mkt-out-field__label">{{ t('pages.marketingFlow.balanceFilter') }}</span>
              <el-select
                v-model="balanceFilter"
                class="mkt-out-field__control"
                @change="loadOutstanding"
              >
                <el-option
                  :label="t('pages.marketingFlow.balanceFilterExcludeZero')"
                  value="exclude_zero"
                />
                <el-option
                  :label="t('pages.marketingFlow.balanceFilterAll')"
                  value="all"
                />
                <el-option
                  :label="t('pages.marketingFlow.balanceFilterPositiveOnly')"
                  value="positive_only"
                />
              </el-select>
            </label>

            <label class="mkt-out-field">
              <span class="mkt-out-field__label">{{ t('common.customer') }}</span>
              <el-select
                v-model="outstandingCustomerIds"
                clearable
                filterable
                multiple
                collapse-tags
                collapse-tags-tooltip
                class="mkt-out-field__control"
                :placeholder="t('pages.marketingFlow.filterCustomerMulti')"
                @change="onOutstandingFactoryChange"
              >
                <el-option
                  v-for="c in marketingCustomers"
                  :key="c.id"
                  :label="c.name || c.code || c.id"
                  :value="c.id"
                />
              </el-select>
            </label>
            <label class="mkt-out-field">
              <span class="mkt-out-field__label">{{ t('pages.marketingFlow.filterFactoryCode') }}</span>
              <el-select
                v-model="factoryCode"
                clearable
                filterable
                multiple
                collapse-tags
                collapse-tags-tooltip
                class="mkt-out-field__control"
                :placeholder="t('pages.marketingFlow.filterFactoryCodePlaceholder')"
                @change="onOutstandingFactoryChange"
              >
                <el-option
                  v-for="code in outstandingFactoryOptions"
                  :key="code"
                  :label="code"
                  :value="code"
                />
              </el-select>
            </label>
          </div>

          <div class="mkt-out-filter__row mkt-out-filter__row--sheet">
            <div class="mkt-out-field mkt-out-field--segment">
              <span class="mkt-out-field__label">{{ t('pages.marketingFlow.outstandingSheetFilter') }}</span>
              <el-radio-group
                v-model="outstandingPoCategory"
                class="mkt-out-segment"
                @change="onOutstandingSheetChange"
              >
                <el-radio-button label="">{{ t('pages.marketingFlow.outstandingSheetAll') }}</el-radio-button>
                <el-radio-button label="production">{{ t('pages.marketingFlow.outstandingSheetProd') }}</el-radio-button>
                <el-radio-button label="claim">{{ t('pages.marketingFlow.outstandingSheetClaim') }}</el-radio-button>
                <el-radio-button label="sample">{{ t('pages.marketingFlow.outstandingSheetSample') }}</el-radio-button>
                <el-radio-button label="subcont">{{ t('pages.marketingFlow.outstandingSheetSubcont') }}</el-radio-button>
                <el-radio-button label="return">{{ t('pages.marketingFlow.outstandingSheetReturn') }}</el-radio-button>
              </el-radio-group>
            </div>
            <div class="mkt-out-field mkt-out-field--segment">
              <span class="mkt-out-field__label">{{ t('pages.marketingFlow.outstandingMaterialGroupFilter') }}</span>
              <el-radio-group
                v-model="outstandingMaterialGroup"
                class="mkt-out-segment"
                @change="onOutstandingSheetChange"
              >
                <el-radio-button label="">{{ t('pages.marketingFlow.outstandingSheetAll') }}</el-radio-button>
                <el-radio-button label="pu">{{ t('pages.marketingFlow.outstandingMaterialGroupPu') }}</el-radio-button>
                <el-radio-button label="suede">{{ t('pages.marketingFlow.outstandingMaterialGroupSuede') }}</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </div>
        <div class="mkt-out-filter__footer">
          <div class="mkt-flow-stat-chips">
            <span class="mkt-flow-stat-chip">
              {{ t('common.total') }}: <strong>{{ outstandingTotal }}</strong>
            </span>
            <span class="mkt-flow-stat-chip">
              {{ t('pages.marketingFlow.shownRows') }}: <strong>{{ outstandingStats.shown }}</strong>
            </span>
            <span class="mkt-flow-stat-chip mkt-flow-stat-chip--warn">
              {{ t('pages.marketingFlow.outNeedSchedule') }}: <strong>{{ outstandingStats.needSchedule }}</strong>
            </span>
            <span class="mkt-flow-stat-chip mkt-flow-stat-chip--ok">
              {{ t('pages.marketingFlow.outNeedShip') }}: <strong>{{ outstandingStats.needShip }}</strong>
            </span>
            <span v-if="outstandingStats.selected" class="mkt-flow-stat-chip">
              {{ t('pages.marketingFlow.selectedCount', { n: outstandingStats.selected }) }}
            </span>
          </div>
          <div class="mkt-out-view-toggle">
            <span class="mkt-out-view-toggle__label">{{ t('pages.marketingFlow.outstandingViewLabel') }}</span>
            <el-radio-group v-model="outstandingViewMode" size="small">
              <el-radio-button label="work">{{ t('pages.marketingFlow.outstandingViewWork') }}</el-radio-button>
              <el-radio-button label="excel">{{ t('pages.marketingFlow.outstandingViewExcel') }}</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </div>

      <p class="mkt-out-col-filter-tip">
        {{ outstandingCompactView ? t('pages.marketingFlow.outstandingWorkTip') : t('pages.marketingFlow.colFilterTip') }}
      </p>

      <div class="admin-table-scroll mkt-out-table-wrap">
      <el-table
        ref="outstandingTableRef"
        :key="outstandingTableKey"
        :data="outstandingDisplayRows"
        v-loading="outstandingLoading"
        border
        size="small"
        :class="[
          'outstanding-table',
          'marketing-outstanding-table',
          outstandingCompactView ? 'outstanding-table--work' : 'outstanding-table--col-filters',
        ]"
        :row-class-name="outstandingRowClassName"
        :empty-text="t('pages.marketingFlow.outstandingEmpty')"
        @selection-change="onOutstandingSelectionChange"
      >
        <el-table-column type="selection" width="42" fixed="left" />
        <!-- Fixed identitas: Tgl Order, No SO, No Lot (di luar grup agar sticky tetap jalan) -->
        <el-table-column
          v-for="col in outstandingFixedIdentityColumns"
          :key="`fixed-${col.prop}`"
          :prop="col.prop"
          :width="col.width"
          :min-width="col.minWidth"
          fixed="left"
          :align="col.align || 'left'"
          :class-name="[
            col.prop === 'thi_order' ? 'out-col-thi-order' : '',
            col.className || '',
          ].filter(Boolean).join(' ') || undefined"
          show-overflow-tooltip
        >
          <template v-if="!outstandingCompactView" #header>
            <OutstandingColFilterHeader
              v-model="outstandingTextFilters[col.prop]"
              :label="col.label"
              :options="outstandingColFilterOptions[col.prop] || []"
            />
          </template>
          <template v-else #header>
            <span>{{
              col.prop === 'order_date'
                ? t('common.orderDate')
                : col.prop === 'thi_order'
                  ? t('common.poNo')
                  : t('pages.marketingFlow.colLotNo')
            }}</span>
          </template>
          <template #default="{ row }">
            <el-button
              v-if="col.prop === 'thi_order'"
              link
              type="primary"
              @click="goPo(row.po_id)"
            >
              {{ row.thi_order || t('common.emptyValue') }}
            </el-button>
            <span v-else-if="col.kind === 'date'">{{ formatOutstandingDate(row[col.prop]) }}</span>
            <span v-else-if="col.kind === 'system_no'">{{ outstandingLotNo(row) || t('common.emptyValue') }}</span>
            <span v-else>{{ formatOutstandingCell(row[col.prop]) }}</span>
          </template>
        </el-table-column>

        <template v-if="outstandingCompactView">
          <el-table-column
            :label="t('pages.marketingFlow.colGroupSo')"
            align="center"
            class-name="out-col-group out-col-group--so"
            label-class-name="out-col-group-label out-col-group-label--so"
          >
            <el-table-column
              :label="t('pages.marketingFlow.colPoCustomer')"
              min-width="128"
              show-overflow-tooltip
              class-name="out-group-start out-group-start--so"
            >
              <template #default="{ row }">
                {{ row.po_customer_ref || row.no_po || t('common.emptyValue') }}
              </template>
            </el-table-column>
            <el-table-column
              prop="customer_name"
              :label="t('common.customerName')"
              min-width="180"
              show-overflow-tooltip
              class-name="out-group-end"
            />
          </el-table-column>

          <el-table-column
            :label="t('pages.marketingFlow.colGroupItem')"
            align="center"
            class-name="out-col-group out-col-group--item"
            label-class-name="out-col-group-label out-col-group-label--item"
          >
            <el-table-column
              prop="material_name"
              :label="t('common.material')"
              min-width="168"
              show-overflow-tooltip
              class-name="out-group-start out-group-start--item"
            />
            <el-table-column
              prop="qty_sf"
              :label="t('pages.marketingFlow.colQtySf')"
              width="100"
              align="right"
              class-name="out-group-end"
            />
          </el-table-column>

          <el-table-column
            :label="t('pages.marketingFlow.colGroupProduction')"
            align="center"
            class-name="out-col-group out-col-group--prod"
            label-class-name="out-col-group-label out-col-group-label--prod"
          >
            <el-table-column
              :label="t('pages.marketingFlow.outstandingColQtyPlan')"
              width="120"
              align="right"
              class-name="out-group-start out-group-start--prod"
            >
              <template #default="{ row }">
                <span class="out-mrp-qty">{{ formatMrpQtyCell(row.mrp_qty_processed) }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('pages.marketingFlow.outstandingColQtyWip')" width="104" align="right">
              <template #default="{ row }">
                <span class="out-mrp-qty">{{ formatMrpQtyCell(row.mrp_qty_wip) }}</span>
              </template>
            </el-table-column>
            <el-table-column
              prop="stock_wh_qty"
              :label="t('pages.marketingFlow.colStockWh')"
              width="104"
              align="right"
              class-name="out-group-end"
            >
              <template #default="{ row }">
                {{ formatOutstandingCell(row.stock_wh_qty) }}
              </template>
            </el-table-column>
          </el-table-column>

          <el-table-column
            :label="t('pages.marketingFlow.colGroupDelivery')"
            align="center"
            class-name="out-col-group out-col-group--delivery"
            label-class-name="out-col-group-label out-col-group-label--delivery"
          >
            <el-table-column
              prop="delivered_qty"
              :label="t('pages.marketingFlow.colDeliveredQty')"
              width="100"
              align="right"
              class-name="out-group-start out-group-start--delivery"
            />
            <el-table-column
              :label="t('pages.marketingFlow.colSuratJalan')"
              min-width="140"
              show-overflow-tooltip
            >
              <template #default="{ row }">
                <template v-if="outstandingSjEntries(row).length">
                  <template v-for="(sj, idx) in outstandingSjEntries(row)" :key="sj.number">
                    <el-button link type="primary" @click="openOutstandingFgPacking(row, sj.number)">
                      {{ sj.number }}
                    </el-button>
                    <span v-if="idx < outstandingSjEntries(row).length - 1">, </span>
                  </template>
                </template>
                <span v-else class="text-gray-400">—</span>
              </template>
            </el-table-column>
            <template v-for="n in 3" :key="`wave-${n}`">
              <el-table-column :label="`${outstandingOrdinalLabel(n)} Qty`" width="100" align="right">
                <template #default="{ row }">{{ formatOutstandingCell(row[`delivery_${n}_qty`]) }}</template>
              </el-table-column>
              <el-table-column
                :label="`${outstandingOrdinalLabel(n)} Date`"
                width="118"
                :class-name="n === 3 ? 'out-group-end' : undefined"
              >
                <template #default="{ row }">{{ formatOutstandingDate(row[`delivery_${n}_date`]) }}</template>
              </el-table-column>
            </template>
          </el-table-column>

          <el-table-column
            :label="t('pages.marketingFlow.colGroupStatus')"
            align="center"
            class-name="out-col-group out-col-group--status"
            label-class-name="out-col-group-label out-col-group-label--status"
          >
            <el-table-column
              :label="t('pages.marketingFlow.outWorkCol')"
              width="160"
              class-name="out-group-start out-group-start--status"
            >
              <template #default="{ row }">
                <el-tag size="small" effect="plain" :type="outstandingWorkStatusType(row)">
                  {{ outstandingWorkStatusLabel(row) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('pages.marketingFlow.outstandingColMktStage')" min-width="152">
              <template #default="{ row }">{{ labelFor(row.mkt_stage) }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.marketingFlow.nextStepCol')" min-width="160">
              <template #default="{ row }">{{ outstandingRowNextLabel(row) }}</template>
            </el-table-column>
            <el-table-column
              :label="t('pages.marketingFlow.colRemarkMarketing')"
              min-width="168"
              class-name="out-group-end"
            >
              <template #default="{ row }">
                <el-input
                  v-if="isOutstandingRowEditing(row)"
                  v-model="row.remark_marketing"
                  size="small"
                  type="textarea"
                  :rows="2"
                  :disabled="!canEditPoDetail"
                />
                <span v-else>{{ formatOutstandingCell(row.remark_marketing) }}</span>
              </template>
            </el-table-column>
          </el-table-column>
        </template>

        <template v-else>
          <el-table-column
            v-for="group in outstandingTableColumnGroups"
            :key="group.id"
            :label="group.label"
            align="center"
            :class-name="`out-col-group out-col-group--${group.id}`"
            :label-class-name="`out-col-group-label out-col-group-label--${group.id}`"
          >
            <el-table-column
              v-for="col in group.columns"
              :key="col.prop"
              :prop="col.prop"
              :width="col.width"
              :min-width="col.minWidth"
              :align="col.align || 'left'"
              :class-name="col.className"
              show-overflow-tooltip
            >
              <template #header>
                <OutstandingColFilterHeader
                  v-model="outstandingTextFilters[col.prop]"
                  :label="col.label"
                  :options="outstandingColFilterOptions[col.prop] || []"
                />
              </template>
              <template #default="{ row }">
                <el-input
                  v-if="col.kind === 'remark_marketing' && isOutstandingRowEditing(row)"
                  v-model="row.remark_marketing"
                  size="small"
                  type="textarea"
                  :rows="2"
                  :disabled="!canEditPoDetail"
                />
                <span v-else-if="col.kind === 'remark_marketing'">{{ formatOutstandingCell(row.remark_marketing) }}</span>
                <span v-else-if="col.kind === 'plan_qty'">{{ formatOutstandingCell(outstandingPlanSlotField(row, 'qty')) }}</span>
                <span v-else-if="col.kind === 'plan_date'">{{ formatOutstandingDate(outstandingPlanSlotField(row, 'delivery_date')) }}</span>
                <span v-else-if="col.kind === 'date'">{{ formatOutstandingDate(row[col.prop]) }}</span>
                <span v-else-if="col.kind === 'color_std'" class="out-color-std">
                  <span>{{ formatOutstandingCell(row.color_standard) }}</span>
                  <span v-if="row.color_standard_created_at" class="out-color-std__date">
                    {{ formatColorStdCreatedBadge(row.color_standard_created_at) }}
                  </span>
                </span>
                <span v-else-if="col.kind === 'mkt_stage'">{{ labelFor(row.mkt_stage) }}</span>
                <span v-else-if="col.kind === 'surat_jalan'">
                  <template v-if="outstandingSjEntries(row).length">
                    <template v-for="(sj, idx) in outstandingSjEntries(row)" :key="sj.number">
                      <el-button link type="primary" @click="openOutstandingFgPacking(row, sj.number)">
                        {{ sj.number }}
                      </el-button>
                      <span v-if="idx < outstandingSjEntries(row).length - 1">, </span>
                    </template>
                  </template>
                  <span v-else class="text-gray-400">—</span>
                </span>
                <span v-else-if="col.kind === 'mrp_qty'" class="out-mrp-qty">
                  {{ formatMrpQtyCell(row[col.prop]) }}
                </span>
                <span v-else>{{ formatOutstandingCell(row[col.prop]) }}</span>
              </template>
            </el-table-column>
          </el-table-column>
        </template>
        <el-table-column
          :label="t('common.actions')"
          width="120"
          align="center"
          fixed="right"
        >
          <template #default="{ row }">
            <div class="mkt-so-actions">
              <template v-if="isOutstandingRowEditing(row)">
                <el-button
                  type="primary"
                  size="small"
                  :icon="Check"
                  :loading="savingOutstandingId === row.po_detail_id"
                  @click="saveOutstandingRowEdit(row)"
                >
                  {{ t('common.save') }}
                </el-button>
                <el-button
                  size="small"
                  :icon="Close"
                  :disabled="savingOutstandingId === row.po_detail_id"
                  @click="cancelOutstandingRowEdit(row)"
                >
                  {{ t('common.cancel') }}
                </el-button>
              </template>
              <AdminTableActions
                v-else
                :show-view="true"
                :view-label="t('pages.marketingFlow.openPoDetail')"
                :more-items="outstandingMoreItems(row)"
                :more-aria-label="t('pages.marketingFlow.moreActions')"
                @view="goPo(row.po_id)"
                @more="(cmd) => onOutstandingRowMore(row, cmd)"
              />
            </div>
          </template>
        </el-table-column>
      </el-table>
      </div>
      <div class="master-items-pagination mkt-out-pagination">
        <el-pagination
          v-model:current-page="outstandingPage"
          v-model:page-size="outstandingPageSize"
          :total="outstandingTotal"
          :page-sizes="[50, 100, 200, 500]"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="loadOutstanding"
          @size-change="onOutstandingPageSizeChange"
        />
      </div>
      </div>
    </div>

    <div v-if="section === 'planning'" class="admin-inner-card marketing-tabs">
      <div class="mkt-section-body">
        <p class="mkt-flow-howto">{{ t('pages.marketingFlow.planningHowto') }}</p>
        <div class="mkt-plan-pane">
          <div class="filter-panel mkt-plan-filter-panel">
            <p class="filter-panel__title">{{ t('common.filter') }}</p>
            <div class="mkt-plan-filter">
              <div class="mkt-plan-filter__fields">
                <label class="mkt-out-field">
                  <span class="mkt-out-field__label">{{ t('pages.marketingFlow.planningDateRange') }}</span>
                  <el-date-picker
                    v-model="planningDateRange"
                    type="daterange"
                    unlink-panels
                    value-format="YYYY-MM-DD"
                    class="mkt-out-field__control"
                    range-separator="—"
                    :shortcuts="orderDateRangeShortcuts"
                    :start-placeholder="t('common.placeholder.fromDate')"
                    :end-placeholder="t('common.placeholder.toDate')"
                    @change="onPlanningDateRangeChange"
                  />
                </label>
                <label class="mkt-out-field">
                  <span class="mkt-out-field__label">{{ t('pages.marketingFlow.outstandingPoSearch') }}</span>
                  <el-input
                    v-model="planningPoSearch"
                    clearable
                    class="mkt-out-field__control"
                    :placeholder="t('pages.marketingFlow.outstandingPoSearchPlaceholder')"
                    @change="loadPlanning"
                    @clear="loadPlanning"
                  />
                </label>
                <label class="mkt-out-field">
                  <span class="mkt-out-field__label">{{ t('pages.marketingFlow.factoryFilterOptional') }}</span>
                  <el-select
                    v-model="planningFactory"
                    clearable
                    filterable
                    multiple
                    collapse-tags
                    collapse-tags-tooltip
                    class="mkt-out-field__control"
                    :placeholder="t('pages.marketingFlow.filterFactoryCodePlaceholder')"
                    @change="loadPlanning"
                  >
                    <el-option
                      v-for="code in planningFactoryOptions"
                      :key="code"
                      :label="code"
                      :value="code"
                    />
                  </el-select>
                </label>
                <label class="mkt-out-field">
                  <span class="mkt-out-field__label">{{ t('common.customer') }}</span>
                  <el-select
                    v-model="planningCustomerIds"
                    clearable
                    filterable
                    multiple
                    collapse-tags
                    collapse-tags-tooltip
                    class="mkt-out-field__control"
                    :placeholder="t('pages.marketingFlow.filterCustomerMulti')"
                  >
                    <el-option
                      v-for="c in marketingCustomers"
                      :key="c.id"
                      :label="c.name || c.code || c.id"
                      :value="c.id"
                    />
                  </el-select>
                </label>
                <div class="mkt-out-field mkt-out-field--segment">
                  <span class="mkt-out-field__label">{{ t('pages.marketingFlow.outstandingMktStageFilter') }}</span>
                  <el-radio-group
                    v-model="planningMktStageMin"
                    class="mkt-out-segment"
                    @change="loadPlanning"
                  >
                    <el-radio-button label="">{{ t('pages.marketingFlow.outstandingMktStageAll') }}</el-radio-button>
                    <el-radio-button label="in_outstanding">{{ t('pages.marketingFlow.outstandingMktStageReady') }}</el-radio-button>
                  </el-radio-group>
                </div>
                <div class="mkt-out-field mkt-out-field--segment">
                  <span class="mkt-out-field__label">{{ t('pages.marketingFlow.planningViewFilter') }}</span>
                  <el-radio-group
                    v-model="planningViewMode"
                    class="mkt-out-segment"
                    @change="onPlanningViewModeChange"
                  >
                    <el-radio-button label="range">{{ t('pages.marketingFlow.planningViewRange') }}</el-radio-button>
                    <el-radio-button label="today">{{ t('pages.marketingFlow.planningFilterToday') }}</el-radio-button>
                    <el-radio-button label="overdue">{{ t('pages.marketingFlow.planningFilterOverdueOnly') }}</el-radio-button>
                  </el-radio-group>
                </div>
              </div>
              <div class="mkt-plan-filter__footer">
                <div class="mkt-plan-stat-chips">
                  <span class="mkt-plan-stat-chip">
                    {{ t('common.total') }}: <strong>{{ planningTotal || planningDisplayRows.length }}</strong>
                  </span>
                  <span class="mkt-plan-stat-chip">
                    {{ t('pages.marketingFlow.planningShipStatusPlanned') }}:
                    <strong>{{ planningStats.planned }}</strong>
                  </span>
                  <span class="mkt-plan-stat-chip">
                    {{ t('pages.marketingFlow.planningShipStatusPartial') }}:
                    <strong>{{ planningStats.partial }}</strong>
                  </span>
                  <span class="mkt-plan-stat-chip">
                    {{ t('pages.marketingFlow.planningShipStatusShipped') }}:
                    <strong>{{ planningStats.shipped }}</strong>
                  </span>
                  <span v-if="planningStats.tooEarly" class="mkt-plan-stat-chip">
                    {{ t('pages.marketingFlow.planningShipStatusTooEarly') }}:
                    <strong>{{ planningStats.tooEarly }}</strong>
                  </span>
                  <span v-if="planningStats.overdue" class="mkt-plan-stat-chip mkt-plan-stat-chip--warn">
                    {{ t('pages.marketingFlow.planningOverdue') }}:
                    <strong>{{ planningStats.overdue }}</strong>
                  </span>
                </div>
                <div class="mkt-plan-filter__actions">
                  <el-button @click="goOpenDeliveryMenu">
                    {{ t('pages.marketingFlow.planningOpenDeliveryMenu') }}
                  </el-button>
                  <el-button type="primary" :icon="Refresh" :loading="planningLoading" @click="loadPlanning">
                    {{ t('common.refresh') }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <div class="mkt-plan-block">
            <div class="admin-table-scroll">
              <el-table
                :data="planningDisplayRows"
                border
                stripe
                size="small"
                class="admin-table mkt-plan-table"
                max-height="520"
                v-loading="planningLoading"
                :empty-text="t('pages.marketingFlow.planningEmpty')"
              >
                <el-table-column prop="delivery_date" :label="t('pages.marketingFlow.colShipDate')" width="110" />
                <el-table-column prop="sequence_no" label="#" width="44" align="center" />
                <el-table-column :label="t('common.poNo')" min-width="128" show-overflow-tooltip>
                  <template #default="{ row }">
                    <el-button link type="primary" @click="goPo(row.po_id)">
                      {{ row.po_number || t('common.emptyValue') }}
                    </el-button>
                  </template>
                </el-table-column>
                <el-table-column prop="po_customer_ref" :label="t('pages.marketingFlow.colPoCustomer')" min-width="110" show-overflow-tooltip />
                <el-table-column prop="customer_name" :label="t('common.customerName')" min-width="140" show-overflow-tooltip />
                <el-table-column :label="t('pages.marketingFlow.colMktStage')" min-width="130" show-overflow-tooltip>
                  <template #default="{ row }">{{ labelFor(row.mkt_stage) }}</template>
                </el-table-column>
                <el-table-column :label="t('common.status')" width="150" align="center">
                  <template #default="{ row }">
                    <div class="mkt-plan-status-cell">
                      <el-tag size="small" effect="plain" :type="planningShipTagType(row.ship_status)">
                        {{ planningShipStatusLabel(row.ship_status) }}
                      </el-tag>
                      <el-tag v-if="row.overdue" size="small" type="danger" effect="plain">
                        {{ t('pages.marketingFlow.planningOverdue') }}
                      </el-tag>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="factory_code" label="Factory" width="88" show-overflow-tooltip />
                <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
                <el-table-column prop="thi_line_ref" :label="t('pages.marketingFlow.planningColThiLine')" min-width="140" show-overflow-tooltip />
                <el-table-column prop="qty" :label="t('pages.marketingFlow.colQtyShip')" width="88" />
                <el-table-column :label="t('pages.marketingFlow.outstandingColQtyWip')" width="88" align="right">
                  <template #default="{ row }">
                    <span class="out-mrp-qty">{{ formatMrpQtyCell(row.mrp_qty_wip) }}</span>
                  </template>
                </el-table-column>
                <el-table-column :label="t('pages.marketingFlow.outstandingColQtyPlan')" width="96" align="right">
                  <template #default="{ row }">{{ formatMrpQtyCell(row.mrp_qty_processed) }}</template>
                </el-table-column>
                <el-table-column prop="delivered_qty" :label="t('pages.marketingFlow.planningColDelivered')" width="88" />
                <el-table-column :label="t('pages.marketingFlow.planningColSj')" min-width="130" show-overflow-tooltip>
                  <template #default="{ row }">
                    <div v-if="row.latest_delivery_id" class="mkt-plan-status-cell">
                      <el-button link type="primary" @click="goDeliveryById(row.latest_delivery_id)">
                        {{ row.latest_delivery_number || `#${row.latest_delivery_id}` }}
                      </el-button>
                      <el-tag
                        size="small"
                        effect="plain"
                        :type="planningDeliveryStatusTagType(row.latest_delivery_status)"
                      >
                        {{ planningDeliveryStatusLabel(row.latest_delivery_status) }}
                      </el-tag>
                    </div>
                    <span v-else>{{ t('common.emptyValue') }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="balance_qty" :label="t('pages.marketingFlow.colBalance')" width="88" />
                <el-table-column prop="line_etd" :label="t('pages.po.lineEtd')" width="110" />
                <el-table-column :label="t('common.actions')" width="100" align="center" fixed="right">
                  <template #default="{ row }">
                    <AdminTableActions
                      :show-view="true"
                      :view-label="t('pages.marketingFlow.planningOpenOutstanding')"
                      :more-items="planningSlotMoreItems(row)"
                      @view="goOutstandingFromPo(row)"
                      @more="(cmd) => handlePlanningSlotMore(row, cmd)"
                    />
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="master-items-pagination mt-3">
              <el-pagination
                v-model:current-page="planningPage"
                v-model:page-size="planningPageSize"
                :total="planningTotal"
                :page-sizes="[20, 50, 100, 200]"
                layout="total, sizes, prev, pager, next"
                background
                @current-change="loadPlanning"
                @size-change="() => { planningPage = 1; loadPlanning() }"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="snapshotArchiveVisible"
      :title="t('pages.marketingFlow.snapshotArchiveTitle')"
      width="720px"
      destroy-on-close
      align-center
    >
      <div class="mkt-plan-filter mb-3">
        <div class="mkt-plan-filter__fields">
          <label class="mkt-out-field mkt-out-field--span2">
            <span class="mkt-out-field__label">{{ t('common.remark') }}</span>
            <el-input
              v-model="snapshotLabel"
              clearable
              :placeholder="t('pages.marketingFlow.snapshotLabelPlaceholder')"
            />
          </label>
        </div>
        <div class="mkt-plan-filter__footer">
          <el-button type="success" :loading="snapshotSaving" @click="saveOutstandingSnapshot">
            {{ t('pages.marketingFlow.snapshotSave') }}
          </el-button>
          <el-button type="primary" :icon="Refresh" :loading="snapshotsLoading" @click="loadSnapshotList">
            {{ t('common.refresh') }}
          </el-button>
        </div>
      </div>
      <el-table
        :data="snapshots"
        border
        stripe
        size="small"
        v-loading="snapshotsLoading"
        max-height="360"
        :empty-text="t('common.tableEmpty')"
      >
        <el-table-column prop="id" label="ID" width="64" align="center" />
        <el-table-column prop="created_at" :label="t('common.date')" width="168" />
        <el-table-column prop="label" :label="t('common.remark')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="row_count" :label="t('pages.marketingFlow.rowCountLabel')" width="100" align="right" />
        <el-table-column :label="t('common.actions')" width="72" align="center">
          <template #default="{ row }">
            <AdminTableActions
              :show-view="true"
              :view-label="t('pages.marketingFlow.snapshotView')"
              @view="openSnapshotDetail(row.id)"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <el-dialog
      v-model="snapshotDetailVisible"
      :title="snapshotDetailTitle"
      width="92%"
      top="4vh"
      destroy-on-close
      align-center
    >
      <el-table v-if="snapshotDetailRows.length" :data="snapshotDetailRows" border stripe size="small" max-height="560">
        <el-table-column type="index" width="48" align="center" />
        <el-table-column prop="order_date" :label="t('common.orderDate')" width="100" />
        <el-table-column prop="thi_order" :label="t('pages.marketingFlow.colThiOrder')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="po_customer_ref" :label="t('pages.marketingFlow.colPoCustomer')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="customer_name" :label="t('common.customerName')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="balance_qty" :label="t('pages.marketingFlow.colBalance')" width="96" />
        <el-table-column prop="remark_marketing" :label="t('pages.marketingFlow.colRemarkMarketing')" min-width="160" show-overflow-tooltip />
      </el-table>
    </el-dialog>

    <el-dialog
      v-model="rollbackDialogVisible"
      :title="t('pages.marketingFlow.rollbackDialogTitle')"
      width="520px"
      destroy-on-close
      align-center
    >
      <el-alert
        class="mb-3"
        type="warning"
        :closable="false"
        show-icon
        :title="t('pages.marketingFlow.rollbackDialogHint')"
      />
      <el-form label-position="top">
        <el-form-item :label="t('common.poNo')">
          <el-input :model-value="rollbackTarget?.po_number" disabled />
        </el-form-item>
        <el-form-item :label="t('pages.marketingFlow.colMktStage')">
          <el-input :model-value="labelFor(rollbackTarget?.mkt_workflow_stage)" disabled />
        </el-form-item>
        <el-form-item :label="t('pages.marketingFlow.rollbackReason')" required>
          <el-input
            v-model="rollbackReason"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
            :placeholder="t('pages.marketingFlow.rollbackReasonPlaceholder')"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="rollbackDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="warning" :icon="Check" :loading="rollingBack != null" @click="submitRollback">
          {{ t('pages.marketingFlow.rollbackConfirm') }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="fgPackingOpen"
      :title="t('pages.marketingFlow.fgPackingDialogTitle')"
      width="820px"
      destroy-on-close
      align-center
      @closed="resetFgPackingDialog"
    >
      <p v-if="fgPackingMeta.delivery" class="text-sm text-slate-600 mt-0 mb-3">
        {{
          t('pages.marketingFlow.fgPackingDialogHint', {
            sj: fgPackingMeta.delivery,
            lot: fgPackingMeta.lot || '—',
          })
        }}
      </p>
      <div v-loading="fgPackingLoading">
        <template v-if="fgPackingItems.length">
          <div v-for="(block, bi) in fgPackingItems" :key="block.fg?.id || bi" class="mb-4">
            <div class="mkt-fg-pack-head">
              <strong>{{ block.fg?.kode_packing || '—' }}</strong>
              <span class="text-slate-500"> · WIP {{ block.fg?.kode_wip || '—' }}</span>
              <el-tag size="small" effect="plain" class="ml-2">{{ block.fg?.status || '—' }}</el-tag>
              <span class="ml-2 text-sm">
                {{ formatOutstandingCell(block.fg?.total_lembar) }} pcs /
                {{ formatOutstandingCell(block.fg?.total_ukuran) }} SF
              </span>
            </div>
            <el-table :data="block.rolls || []" border size="small" class="admin-table mb-2" :empty-text="t('common.tableEmpty')">
              <el-table-column prop="roll_no" :label="t('pages.marketingFlow.fgPackingRolls')" width="72" align="center" />
              <el-table-column :label="t('pages.marketingFlow.colQtyPcs')" width="90" align="right">
                <template #default="{ row }">{{ formatOutstandingCell(row.lembar) }}</template>
              </el-table-column>
              <el-table-column :label="t('pages.marketingFlow.colQtyShip')" width="100" align="right">
                <template #default="{ row }">{{ formatOutstandingCell(row.ukuran) }}</template>
              </el-table-column>
            </el-table>
            <el-table
              v-if="(block.packing_pos || []).length"
              :data="block.packing_pos || []"
              border
              size="small"
              class="admin-table"
              :empty-text="t('common.tableEmpty')"
            >
              <el-table-column prop="no_po" :label="t('pages.marketingFlow.colPoCustomerRef')" min-width="110" show-overflow-tooltip />
              <el-table-column prop="no_so" :label="t('pages.mrpRencana.soRef')" min-width="90" show-overflow-tooltip />
              <el-table-column :label="t('pages.marketingFlow.colLotNo')" min-width="120" show-overflow-tooltip>
                <template #default="{ row }">{{ formatOutstandingCell(row.lot_no || row.lot_number) }}</template>
              </el-table-column>
              <el-table-column :label="t('pages.marketingFlow.colQtyShip')" width="100" align="right">
                <template #default="{ row }">{{ formatOutstandingCell(row.qty_sq) }}</template>
              </el-table-column>
            </el-table>
          </div>
        </template>
        <el-empty v-else-if="!fgPackingLoading" :description="t('pages.marketingFlow.fgPackingEmpty')" />
      </div>
      <template #footer>
        <el-button @click="fgPackingOpen = false">{{ t('common.close') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="materialFollowUpDialogVisible" :title="t('pages.marketingFlow.materialFollowUp')" width="500px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('common.poNo')">
          <el-input :model-value="selectedPoForMaterialFollowUp?.po_number" disabled />
        </el-form-item>
        <p class="text-xs text-slate-600 mb-3">{{ t('pages.marketingFlow.materialDoneHint') }}</p>
        <el-form-item :label="t('pages.marketingFlow.materialRemark')">
          <el-input v-model="materialFollowUpForm.remark" type="textarea" :rows="4" :placeholder="t('pages.marketingFlow.materialRemarkPlaceholder')" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="materialFollowUpDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :icon="Check" :loading="savingMaterialFollowUp" @click="saveMaterialFollowUp">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Download, Close, Check, Warning, CircleCheck, Refresh, RefreshLeft, ArrowDown, Search } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import AdminTableActions from '../../components/admin/AdminTableActions.vue'
import OutstandingColFilterHeader from '../../components/admin/OutstandingColFilterHeader.vue'
import OutstandingWorkbenchDialogs from '../../components/admin/OutstandingWorkbenchDialogs.vue'
import PoItemRevisedDot from '../../components/admin/PoItemRevisedDot.vue'
import PoRekapPrintDialog from '../../components/admin/PoRekapPrintDialog.vue'
import {
  advanceMktWorkflow,
  rollbackMktWorkflow,
  createMarketingOutstandingSnapshot,
  fetchAuthenticatedDocument,
  getMarketingOutstandingSnapshot,
  listCustomers,
  listMarketingDeliveryPlanning,
  listMarketingOutstandingLines,
  listMarketingOutstandingSnapshots,
  listPoMktStages,
  listPoPage,
  marketingOutstandingCsvUrl,
  marketingOutstandingReturnXlsxPath,
  marketingOutstandingManualXlsxPath,
  marketingOutstandingXlsxPath,
  reportPoDailyMarketingXlsxPath,
  updatePo,
  updatePoDetail,
  mrpGudangFgPackingByDeliveryLot,
} from '../../api/client'
import { buildPageParams, normalizePageResult } from '../../utils/tableQuery'
import { can } from '../../security/permissions'
import { useModulePermission } from '../../composables/useModulePermission'
import { stuckReasonLabel as translateStuckReason } from '../../utils/mktStuckReason.js'
import { soListNextStep, soListNextStepActionable } from '../../utils/mktStage.js'
import { outstandingNextAction, outstandingWorkStatus, extractPlanSlots } from '../../utils/outstandingWork.js'
import { formatDate, statusType } from '../../utils/format.js'

const OUTSTANDING_LINES_LIMIT = 1000
const outstandingPage = ref(1)
const outstandingPageSize = ref(100)
const outstandingTotal = ref(0)

const { t, te } = useI18n()
const { canAdvance, canRollback, canUpdate: canFlowUpdate } = useModulePermission('marketingFlow')
const canEditPoDetail = can('po', 'update')
const route = useRoute()
const router = useRouter()

const section = computed(() => {
  const s = route.meta?.marketingSection
  if (s === 'outstanding' || s === 'planning' || s === 'flow') return s
  return 'flow'
})

const pageTitle = computed(() => {
  if (section.value === 'outstanding') return t('menu.marketingFlowOutstanding')
  if (section.value === 'planning') return t('menu.marketingFlowPlanning')
  return t('menu.marketingFlowPoList')
})

const pageSubtitle = computed(() => {
  if (section.value === 'flow') return t('pages.marketingFlow.subtitle')
  if (section.value === 'outstanding') return t('pages.marketingFlow.outstandingSubtitle')
  if (section.value === 'planning') return t('pages.marketingFlow.planningSubtitle')
  return ''
})
const loading = ref(false)
const advancing = ref(null)
const rollingBack = ref(null)
const rows = ref([])
const totalFlowRows = ref(0)
const flowPage = ref(1)
const flowPageSize = ref(20)
const stageCountMap = ref({})
const stageList = ref([])
const filterStage = ref(null)
const flowSoStatus = ref('')
const flowCustomerIds = ref([])
const marketingCustomers = ref([])
const flowKeyword = ref('')
let flowWatchReady = false
let flowKeywordTimer = null

function isoDateLocal(d) {
  const x = new Date(d)
  const p = (n) => String(n).padStart(2, '0')
  return `${x.getFullYear()}-${p(x.getMonth() + 1)}-${p(x.getDate())}`
}
function defaultMonthToTodayRange() {
  const e = new Date()
  const s = new Date(e.getFullYear(), e.getMonth(), 1)
  return [isoDateLocal(s), isoDateLocal(e)]
}
/** Daftar alur MKT: default kosong = semua tanggal (hindari list kosong di awal bulan) */
const flowDateRange = ref(null)
/** Outstanding: opsional; kosong = semua tanggal */
const outstandingDateRange = ref(null)

const orderDateRangeShortcuts = computed(() => [
  {
    text: t('pages.marketingFlow.shortcutToday'),
    value: () => {
      const e = new Date()
      return [e, e]
    },
  },
  {
    text: t('pages.marketingFlow.shortcutLast7Days'),
    value: () => {
      const e = new Date()
      const s = new Date()
      s.setDate(s.getDate() - 6)
      return [s, e]
    },
  },
  {
    text: t('pages.marketingFlow.shortcutLast30Days'),
    value: () => {
      const e = new Date()
      const s = new Date()
      s.setDate(s.getDate() - 29)
      return [s, e]
    },
  },
  {
    text: t('pages.marketingFlow.shortcutThisMonth'),
    value: () => {
      const e = new Date()
      return [new Date(e.getFullYear(), e.getMonth(), 1), e]
    },
  },
  {
    text: t('pages.marketingFlow.shortcutThisYear'),
    value: () => {
      const e = new Date()
      return [new Date(e.getFullYear(), 0, 1), e]
    },
  },
])


const outstandingRows = ref([])
const outstandingLoading = ref(false)
const outstandingXlsxLoading = ref(false)
const outstandingReturnXlsxLoading = ref(false)
const outstandingManualXlsxLoading = ref(false)
const poDailyXlsxLoading = ref(false)
const rekapPrintVisible = ref(false)
const rekapPoId = ref(null)
const rekapPoNumber = ref('')
const balanceFilter = ref('exclude_zero')
const shipmentTab = ref('all')
const poSearch = ref('')
const factoryCode = ref([])
const outstandingCustomerIds = ref([])
const outstandingFactoryOptions = ref([])
const outstandingPoCategory = ref('')
const outstandingMaterialGroup = ref('')
const outstandingViewMode = ref('work')
const outstandingCompactView = computed(() => outstandingViewMode.value === 'work')
const workbenchOverride = ref(null)
const materialStatus = ref('')
const outstandingTableRef = ref(null)
const outstandingSelection = ref([])
const outstandingScheduleVisible = ref(false)
const outstandingPiVisible = ref(false)
const outstandingShipVisible = ref(false)
const savingOutstandingId = ref(null)
const editingOutstandingId = ref(null)
const outstandingEditSnapshot = ref(null)

const outstandingTableKey = computed(
  () => `out-${outstandingPoCategory.value || 'all'}-${outstandingDeliverySlotCount.value}-${outstandingCompactView.value ? 'work' : 'xls'}`,
)

function formatColorStdCreatedBadge(val) {
  if (!val) return ''
  const s = String(val).trim().replace('T', ' ')
  return s.length > 19 ? s.slice(0, 19) : s
}

function formatOutstandingDate(val) {
  if (!val) return '—'
  // Jaga agar nilai tanggal ISO tidak terbaca sebagai nomor/serial
  const s = String(val).trim()
  if (/^\d{4}-\d{2}-\d{2}/.test(s)) return formatDate(s.slice(0, 10))
  return formatDate(s)
}

function formatOutstandingCell(val) {
  if (val === null || val === undefined || val === '') return '—'
  return val
}

function outstandingLotNo(row) {
  const raw = row?.lot_no || row?.thi_line_ref || row?.system_reference || ''
  const s = String(raw).trim()
  if (!s || s === '—') return ''
  return s
}

function outstandingSjEntries(row) {
  const out = []
  const seen = new Set()
  const latest = String(row?.latest_delivery_number || '').trim()
  if (latest) {
    seen.add(latest.toLowerCase())
    out.push({ number: latest, id: row?.latest_delivery_id })
  }
  const max = outstandingDeliverySlotCount.value || 21
  for (let n = 1; n <= max; n += 1) {
    const num = String(row?.[`delivery_${n}_number`] || '').trim()
    if (!num || seen.has(num.toLowerCase())) continue
    seen.add(num.toLowerCase())
    out.push({ number: num, id: row?.[`delivery_${n}_id`] })
  }
  return out
}

const fgPackingOpen = ref(false)
const fgPackingLoading = ref(false)
const fgPackingItems = ref([])
const fgPackingMeta = reactive({ delivery: '', lot: '' })

function resetFgPackingDialog() {
  fgPackingItems.value = []
  fgPackingMeta.delivery = ''
  fgPackingMeta.lot = ''
  fgPackingLoading.value = false
}

async function openOutstandingFgPacking(row, sjNumber) {
  const delivery = String(sjNumber || row?.latest_delivery_number || '').trim()
  const lot = outstandingLotNo(row)
  if (!delivery) {
    ElMessage.warning(t('pages.marketingFlow.colSuratJalan'))
    return
  }
  fgPackingMeta.delivery = delivery
  fgPackingMeta.lot = lot
  fgPackingOpen.value = true
  fgPackingLoading.value = true
  fgPackingItems.value = []
  try {
    const data = await mrpGudangFgPackingByDeliveryLot({
      delivery_number: delivery,
      lot_no: lot,
    })
    fgPackingItems.value = Array.isArray(data?.items) ? data.items : []
    if (!fgPackingItems.value.length) {
      ElMessage.info(t('pages.marketingFlow.fgPackingEmpty'))
    }
  } catch (e) {
    ElMessage.error(e?.message || String(e))
  } finally {
    fgPackingLoading.value = false
  }
}

function formatMrpQtyCell(value) {
  const s = String(value ?? '').trim()
  return s === '' ? t('common.emptyValue') : s
}

const materialFollowUpDialogVisible = ref(false)
const materialFollowUpForm = reactive({ remark: '' })
const selectedPoForMaterialFollowUp = ref(null)
const savingMaterialFollowUp = ref(false)

function outstandingOrdinalLabel(n) {
  if (n === 1) return '1st'
  if (n === 2) return '2nd'
  if (n === 3) return '3rd'
  return `${n}th`
}

/** Field qty/date dari rencana marketing (satu slot saja). */
function outstandingPlanSlotField(row, field) {
  const slots = extractPlanSlots(row, { maxSlots: 1 })
  const slot = slots[0]
  if (!slot) return ''
  return slot[field] ?? ''
}

function buildOutstandingDeliveryColumnDefs(maxDeliverySlots) {
  const d = []
  for (let i = 1; i <= maxDeliverySlots; i += 1) {
    const lab = outstandingOrdinalLabel(i)
    d.push(
      { prop: `delivery_${i}_qty`, label: `${lab} Qty`, width: 100, align: 'right', kind: 'text' },
      { prop: `delivery_${i}_date`, label: `${lab} Date`, width: 118, kind: 'date' },
    )
  }
  return d
}

const outstandingDeliverySlotCount = computed(() => {
  const cat = outstandingPoCategory.value
  if (cat === 'production' || cat === 'suede' || !cat) return 21
  if (['claim', 'sample', 'subcont'].includes(cat)) return 5
  if (cat === 'return') return 3
  return 21
})

const outstandingShowStatusMaterial = computed(() => {
  const cat = outstandingPoCategory.value
  return !cat || cat === 'production' || cat === 'suede'
})

/** Kolom fixed kiri (Tgl Order, No SO, No Lot) — di luar grup agar sticky Element Plus aman. */
const outstandingFixedIdentityColumns = computed(() => [
  { prop: 'order_date', label: 'DATE', width: 120, kind: 'date' },
  { prop: 'thi_order', label: 'THI ORDER', width: 148, kind: 'text' },
  {
    prop: 'system_reference',
    label: t('pages.marketingFlow.colLotNo'),
    minWidth: 148,
    kind: 'system_no',
    className: 'out-group-end',
  },
])

/** Kolom lengkap dikelompokkan: SO → Item → Produksi → Delivery → Status. */
const outstandingTableColumnGroups = computed(() => {
  const cat = outstandingPoCategory.value
  const usePoCust = ['claim', 'sample', 'subcont', 'return'].includes(cat)
  const poCol = usePoCust
    ? { prop: 'po_customer_ref', label: 'PO CUST', minWidth: 148, kind: 'text' }
    : { prop: 'no_po', label: 'NO PO', minWidth: 148, kind: 'text' }

  const so = {
    id: 'so',
    label: t('pages.marketingFlow.colGroupSo'),
    columns: [
      { prop: 'customer_name', label: 'CUSTOMER NAME', minWidth: 196, kind: 'text' },
      { prop: 'brand', label: 'BRAND', minWidth: 120, kind: 'text' },
      { prop: 'order_type', label: 'ORDER TYPE', width: 120, kind: 'text' },
      poCol,
    ],
  }

  const item = {
    id: 'item',
    label: t('pages.marketingFlow.colGroupItem'),
    columns: [
      { prop: 'material_name', label: 'MATERIAL NAME', minWidth: 172, kind: 'text' },
      { prop: 'thickness', label: 'THICKNESS', width: 104, kind: 'text' },
      { prop: 'emboss', label: 'EMBOSS', width: 88, kind: 'text' },
      { prop: 'color', label: 'COLOR', width: 96, kind: 'text' },
      { prop: 'qty_sf', label: 'QTY (S/F)', width: 108, align: 'right', kind: 'text' },
      { prop: 'unit_price', label: 'PRICE', width: 88, align: 'right', kind: 'text' },
      { prop: 'color_standard', label: 'COLOR STD', minWidth: 188, kind: 'color_std' },
      { prop: 'backing', label: 'BACKING', width: 96, kind: 'text' },
      { prop: 'model', label: 'MODEL', width: 96, kind: 'text' },
      { prop: 'style_article', label: 'ARTICLE', minWidth: 108, kind: 'text' },
    ],
  }

  const prodCols = [
    {
      prop: 'mrp_qty_processed',
      label: t('pages.marketingFlow.outstandingColQtyPlan'),
      width: 120,
      align: 'right',
      kind: 'mrp_qty',
    },
    {
      prop: 'mrp_qty_wip',
      label: t('pages.marketingFlow.outstandingColQtyWip'),
      width: 104,
      align: 'right',
      kind: 'mrp_qty',
    },
    { prop: 'stock_wh_qty', label: 'STOCK WH', width: 104, align: 'right', kind: 'text' },
  ]
  if (outstandingShowStatusMaterial.value) {
    prodCols.push(
      {
        prop: 'production_status',
        label: t('pages.marketingFlow.colProductionStatus'),
        minWidth: 120,
        kind: 'text',
      },
      {
        prop: 'material_followup_remark_header',
        label: t('pages.marketingFlow.colFollowupRemark'),
        minWidth: 160,
        kind: 'text',
      },
    )
  }
  const prod = {
    id: 'prod',
    label: t('pages.marketingFlow.colGroupProduction'),
    columns: prodCols,
  }

  const delivery = {
    id: 'delivery',
    label: t('pages.marketingFlow.colGroupDelivery'),
    columns: [
      {
        prop: 'delivered_qty',
        label: t('pages.marketingFlow.colDeliveredQty'),
        width: 108,
        align: 'right',
        kind: 'text',
      },
      {
        prop: 'latest_delivery_number',
        label: t('pages.marketingFlow.colSuratJalan'),
        minWidth: 140,
        kind: 'surat_jalan',
      },
      ...buildOutstandingDeliveryColumnDefs(outstandingDeliverySlotCount.value),
    ],
  }

  const status = {
    id: 'status',
    label: t('pages.marketingFlow.colGroupStatus'),
    columns: [
      { prop: 'mkt_stage', label: t('pages.marketingFlow.outstandingColMktStage'), minWidth: 152, kind: 'mkt_stage' },
      { prop: 'detail_remark', label: 'REMARK PO', minWidth: 148, kind: 'text' },
      { prop: 'remark_marketing', label: 'REMARK', minWidth: 200, kind: 'remark_marketing' },
    ],
  }

  return [so, item, prod, delivery, status].map((group) => {
    const cols = group.columns
    if (!cols.length) return group
    const first = cols[0]
    const last = cols[cols.length - 1]
    first.className = ['out-group-start', `out-group-start--${group.id}`, first.className]
      .filter(Boolean)
      .join(' ')
    if (last !== first) {
      last.className = ['out-group-end', last.className].filter(Boolean).join(' ')
    } else {
      first.className = [first.className, 'out-group-end'].filter(Boolean).join(' ')
    }
    return group
  })
})

const outstandingTableColumnDefs = computed(() => [
  ...outstandingFixedIdentityColumns.value,
  ...outstandingTableColumnGroups.value.flatMap((g) => g.columns),
])

const OUTSTANDING_TEXT_FILTER_KEYS = computed(() => {
  const keys = outstandingTableColumnDefs.value.map((c) => c.prop)
  for (let i = 1; i <= 21; i += 1) {
    keys.push(`delivery_${i}_qty`, `delivery_${i}_date`)
  }
  return [...new Set(keys)]
})

const outstandingTextFilters = reactive({})

function ensureOutstandingTextFilterKeys() {
  for (const key of OUTSTANDING_TEXT_FILTER_KEYS.value) {
    if (!(key in outstandingTextFilters)) outstandingTextFilters[key] = []
    else if (!Array.isArray(outstandingTextFilters[key])) {
      const raw = outstandingTextFilters[key]
      outstandingTextFilters[key] = raw == null || raw === '' ? [] : [String(raw)]
    }
  }
}

watch(
  OUTSTANDING_TEXT_FILTER_KEYS,
  () => {
    ensureOutstandingTextFilterKeys()
  },
  { immediate: true },
)

const outstandingColFilterOptions = computed(() => {
  const rows = outstandingRows.value || []
  const map = {}
  for (const key of OUTSTANDING_TEXT_FILTER_KEYS.value) {
    const set = new Set()
    for (const r of rows) {
      let v
      if (key === 'plan_qty') v = outstandingPlanSlotField(r, 'qty')
      else if (key === 'plan_date') v = outstandingPlanSlotField(r, 'delivery_date')
      else v = r?.[key]
      if (v === null || v === undefined || v === '') continue
      if (typeof v === 'string' && /^\d{4}-\d{2}-\d{2}/.test(v.trim())) {
        v = formatOutstandingDate(v)
        if (v === '—') continue
      }
      set.add(String(v))
    }
    map[key] = Array.from(set).sort((a, b) =>
      a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }),
    )
  }
  return map
})

function outstandingRowTextMatches(row, key, needles) {
  const list = Array.isArray(needles)
    ? needles.map((n) => String(n || '').trim()).filter(Boolean)
    : needles && String(needles).trim()
      ? [String(needles).trim()]
      : []
  if (!list.length) return true
  let cell
  if (key === 'plan_qty') cell = String(outstandingPlanSlotField(row, 'qty') ?? '')
  else if (key === 'plan_date') cell = String(outstandingPlanSlotField(row, 'delivery_date') ?? '')
  else cell = String(row[key] ?? '')
  if (/^\d{4}-\d{2}-\d{2}/.test(cell.trim())) {
    cell = formatOutstandingDate(cell)
  }
  const cellLc = cell.toLowerCase()
  return list.some((needle) => {
    const q = needle.toLowerCase()
    return cellLc === q || cellLc.includes(q)
  })
}

function buildOutstandingDateParams() {
  const od = outstandingDateRange.value
  if (Array.isArray(od) && od.length === 2 && od[0] && od[1]) {
    return { order_date_from: od[0], order_date_to: od[1] }
  }
  return {}
}

function buildOutstandingQueryParams(extra = {}) {
  const page = outstandingPage.value || 1
  const size = outstandingPageSize.value || 100
  return {
    balance_filter: balanceFilter.value,
    computed_balance: true,
    po_q: poSearch.value,
    shipment_status: shipmentTab.value,
    material_status: materialStatus.value || undefined,
    factory_code: Array.isArray(factoryCode.value) && factoryCode.value.length ? factoryCode.value : undefined,
    customer_ids: Array.isArray(outstandingCustomerIds.value) && outstandingCustomerIds.value.length
      ? outstandingCustomerIds.value
      : undefined,
    po_category: outstandingPoCategory.value || undefined,
    material_group: outstandingMaterialGroup.value || undefined,
    // Outstanding kerja: mulai dari tahap in_outstanding (bukan draft / input_system).
    mkt_stage_min: 'in_outstanding',
    // Default: SO order date terbaru dulu.
    sort_by: 'order_date',
    sort_dir: 'desc',
    skip: (page - 1) * size,
    limit: Math.min(size, OUTSTANDING_LINES_LIMIT),
    ...buildOutstandingDateParams(),
    ...extra,
  }
}

/** Export: filter server penuh (limit tinggi), bukan halaman UI; checklist membatasi baris. */
function buildOutstandingExportParams(extra = {}) {
  const params = buildOutstandingQueryParams({
    skip: 0,
    limit: OUTSTANDING_LINES_LIMIT,
    ...extra,
  })
  const ids = outstandingSelection.value
    .map((r) => r.po_detail_id)
    .filter((id) => id != null && Number.isFinite(Number(id)))
  if (ids.length) params.po_detail_ids = ids
  return params
}

function unwrapOutstandingLines(resp) {
  if (Array.isArray(resp)) return resp
  return Array.isArray(resp?.data) ? resp.data : []
}

const outstandingDisplayRows = computed(() => {
  let list = outstandingRows.value
  for (const [key, needles] of Object.entries(outstandingTextFilters)) {
    const active = Array.isArray(needles)
      ? needles.some((n) => String(n || '').trim())
      : Boolean(needles && String(needles).trim())
    if (!active) continue
    list = list.filter((r) => outstandingRowTextMatches(r, key, needles))
  }
  // Primary: Tanggal Order terbaru dulu; lalu THI sama berdekatan.
  return [...list].sort((a, b) => {
    const da = String(a?.order_date || '')
    const db = String(b?.order_date || '')
    if (da !== db) {
      if (!da) return 1
      if (!db) return -1
      return db.localeCompare(da)
    }
    const ta = String(a?.thi_order || '')
    const tb = String(b?.thi_order || '')
    if (ta !== tb) return ta.localeCompare(tb, undefined, { numeric: true, sensitivity: 'base' })
    return String(a?.material_name || '').localeCompare(String(b?.material_name || ''), undefined, {
      sensitivity: 'base',
    })
  })
})

function outstandingRowClassName({ row, rowIndex }) {
  const rows = outstandingDisplayRows.value
  let groupIdx = 0
  let prevThi = null
  for (let i = 0; i <= rowIndex; i += 1) {
    const thi = String(rows[i]?.thi_order || '')
    if (i === 0) {
      prevThi = thi
      continue
    }
    if (thi !== prevThi) {
      groupIdx += 1
      prevThi = thi
    }
  }
  // 6 warna soft berulang antar THI ORDER
  const classes = [`out-row--g${groupIdx % 6}`]
  const prev = rowIndex > 0 ? rows[rowIndex - 1] : null
  const currThi = String(row?.thi_order || '')
  if (!prev || String(prev.thi_order || '') !== currThi) {
    classes.push('out-row--group-start')
  }
  return classes.join(' ')
}

function clearOutstandingColFilters() {
  for (const key of Object.keys(outstandingTextFilters)) {
    outstandingTextFilters[key] = []
  }
}

function onOutstandingSelectionChange(sel) {
  outstandingSelection.value = sel
}

function isOutstandingRowEditing(row) {
  return Boolean(row?.po_detail_id) && editingOutstandingId.value === row.po_detail_id
}

function snapshotOutstandingEdit(row) {
  return { remark_marketing: row.remark_marketing || '' }
}

function restoreOutstandingEdit(row, snap) {
  if (!row || !snap) return
  row.remark_marketing = snap.remark_marketing
}

function startOutstandingRowEdit(row) {
  if (!canEditPoDetail || !row?.po_detail_id) return
  if (editingOutstandingId.value && editingOutstandingId.value !== row.po_detail_id) {
    const prev = outstandingDisplayRows.value.find((r) => r.po_detail_id === editingOutstandingId.value)
    if (prev) restoreOutstandingEdit(prev, outstandingEditSnapshot.value)
  }
  outstandingEditSnapshot.value = snapshotOutstandingEdit(row)
  editingOutstandingId.value = row.po_detail_id
}

function cancelOutstandingRowEdit(row) {
  restoreOutstandingEdit(row, outstandingEditSnapshot.value)
  editingOutstandingId.value = null
  outstandingEditSnapshot.value = null
}

async function saveOutstandingRowEdit(row) {
  if (!canEditPoDetail || !row?.po_detail_id) return
  savingOutstandingId.value = row.po_detail_id
  try {
    await updatePoDetail(row.po_detail_id, {
      marketing_outstanding_remark: String(row.remark_marketing || '').trim() || null,
    })
    editingOutstandingId.value = null
    outstandingEditSnapshot.value = null
    ElMessage.success(t('pages.marketingFlow.outstandingRowSaved'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    savingOutstandingId.value = null
  }
}

async function downloadOutstandingXlsx() {
  outstandingXlsxLoading.value = true
  try {
    await fetchAuthenticatedDocument(marketingOutstandingXlsxPath(buildOutstandingExportParams()), {
      mode: 'download',
      downloadFallbackName: 'marketing_outstanding.xlsx',
    })
    ElMessage.success(
      outstandingSelection.value.length
        ? t('pages.marketingFlow.outstandingXlsxOkSelected', { n: outstandingSelection.value.length })
        : t('pages.marketingFlow.outstandingXlsxOk'),
    )
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingXlsxLoading.value = false
  }
}

async function downloadReturnXlsx() {
  outstandingReturnXlsxLoading.value = true
  try {
    await fetchAuthenticatedDocument(marketingOutstandingReturnXlsxPath(buildOutstandingExportParams()), {
      mode: 'download',
      downloadFallbackName: 'marketing_outstanding_retur.xlsx',
    })
    ElMessage.success(t('pages.marketingFlow.outstandingReturXlsxOk'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingReturnXlsxLoading.value = false
  }
}

async function downloadManualWorkbook() {
  outstandingManualXlsxLoading.value = true
  try {
    await fetchAuthenticatedDocument(marketingOutstandingManualXlsxPath(buildOutstandingExportParams()), {
      mode: 'download',
      downloadFallbackName: 'data_outstanding_order.xlsx',
    })
    ElMessage.success(t('pages.marketingFlow.outstandingManualXlsxOk'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingManualXlsxLoading.value = false
  }
}

function planningDefaultRange() {
  const e = new Date()
  const s = new Date()
  s.setDate(s.getDate() - 7)
  return [isoDateLocal(s), isoDateLocal(e)]
}
const planningDateRange = ref(planningDefaultRange())
const planningFactory = ref([])
const planningCustomerIds = ref([])
const planningPoSearch = ref('')
/** Default sama Outstanding: hanya SO yang sudah lewat PPIC (siap jadwal/kirim). */
const planningMktStageMin = ref('in_outstanding')
/** range | today | overdue — shortcut pantauan (bukan tab terpisah). */
const planningViewMode = ref('range')
const planningRows = ref([])
const planningLoading = ref(false)
const planningPage = ref(1)
const planningPageSize = ref(50)
const planningTotal = ref(0)

const planningFactoryOptions = computed(() => {
  const set = new Set()
  for (const r of planningRows.value || []) {
    const c = String(r.factory_code || '').trim()
    if (c) set.add(c)
  }
  return [...set].sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }))
})

const planningDisplayRows = computed(() => {
  let rows = planningRows.value || []
  const ids = Array.isArray(planningCustomerIds.value) ? planningCustomerIds.value.map(Number) : []
  if (ids.length) {
    const idSet = new Set(ids)
    rows = rows.filter((r) => r.customer_id != null && idSet.has(Number(r.customer_id)))
  }
  if (planningViewMode.value === 'overdue') {
    rows = rows.filter((r) => r?.overdue)
  }
  return rows
})

const planningStats = computed(() => {
  const rows = planningDisplayRows.value || []
  let planned = 0
  let partial = 0
  let shipped = 0
  let tooEarly = 0
  let overdue = 0
  for (const r of rows) {
    const st = String(r?.ship_status || '')
    if (st === 'partial') partial += 1
    else if (st === 'shipped') shipped += 1
    else if (st === 'too_early') tooEarly += 1
    else planned += 1
    if (r?.overdue) overdue += 1
  }
  return { planned, partial, shipped, tooEarly, overdue }
})

const workbenchRows = computed(() => {
  if (workbenchOverride.value?.length) return workbenchOverride.value
  return outstandingSelection.value
})

const snapshots = ref([])
const snapshotsLoading = ref(false)
const snapshotLabel = ref('')
const snapshotSaving = ref(false)
const snapshotArchiveVisible = ref(false)
const snapshotDetailVisible = ref(false)
const snapshotDetailRows = ref([])
const snapshotDetailTitle = ref('')

const labels = computed(() => ({
  input_system: t('mktStage.input_system'),
  rekap_printed: t('mktStage.rekap_printed'),
  with_ppic: t('mktStage.with_ppic'),
  back_to_mkt: t('mktStage.in_outstanding'),
  in_outstanding: t('mktStage.in_outstanding'),
  material_followup: t('mktStage.material_followup'),
  delivery_arranged: t('mktStage.delivery_arranged'),
  sj_invpl: t('mktStage.sj_invpl'),
  invoice_billing: t('mktStage.invoice_billing'),
}))

function labelFor(stage) {
  return labels.value[stage] || stage || t('common.emptyValue')
}

function normalizeFlowStage(stage) {
  const s = (stage || 'input_system').trim() || 'input_system'
  return s === 'back_to_mkt' ? 'in_outstanding' : s
}

function nextFlowStage(stage) {
  const cur = normalizeFlowStage(stage)
  const idx = stageList.value.indexOf(cur)
  if (idx < 0 || idx + 1 >= stageList.value.length) return null
  return stageList.value[idx + 1]
}

/** Tahap yang sedang dihuni PO (dari agregat badge / filter aktif). */
const pipelineCurrentStages = computed(() => {
  if (filterStage.value) return new Set([normalizeFlowStage(filterStage.value)])
  const set = new Set()
  for (const s of stageList.value) {
    if (Number(stageCounts.value[s] || 0) > 0) set.add(s)
  }
  return set
})

const pipelineNextStages = computed(() => {
  const next = new Set()
  for (const s of pipelineCurrentStages.value) {
    const n = nextFlowStage(s)
    if (n && !pipelineCurrentStages.value.has(n)) next.add(n)
  }
  return next
})

function pipelineItemClass(stage) {
  return {
    'mkt-stage-item--active': filterStage.value === stage,
    'mkt-stage-item--current': pipelineCurrentStages.value.has(stage),
    'mkt-stage-item--next': pipelineNextStages.value.has(stage),
  }
}

function pipelineTagClass(stage) {
  return {
    'mkt-pulse-tag': true,
    'mkt-pulse-tag--current': pipelineCurrentStages.value.has(stage),
    'mkt-pulse-tag--next': pipelineNextStages.value.has(stage),
  }
}

function stageTagType(stage) {
  if (pipelineCurrentStages.value.has(stage)) return 'success'
  if (pipelineNextStages.value.has(stage)) return 'primary'
  return filterStage.value === stage ? 'primary' : 'info'
}

const stageCounts = computed(() => {
  const counts = {}
  for (const s of stageList.value) {
    counts[s] = Number(stageCountMap.value[s] || 0)
  }
  return counts
})

function flowRowNumber(index) {
  return (flowPage.value - 1) * flowPageSize.value + index + 1
}

function buildFlowPageParams() {
  const params = {
    limit: flowPageSize.value,
    offset: (flowPage.value - 1) * flowPageSize.value,
    include_stage_counts: true,
  }
  if (filterStage.value) {
    params.mkt_workflow_stage = filterStage.value
  }
  if (flowSoStatus.value) {
    params.status = flowSoStatus.value
  }
  if (Array.isArray(flowCustomerIds.value) && flowCustomerIds.value.length) {
    params.customer_id = flowCustomerIds.value
  }
  if (flowKeyword.value.trim()) {
    params.q = flowKeyword.value.trim()
  }
  if (Array.isArray(flowDateRange.value) && flowDateRange.value.length === 2 && flowDateRange.value[0] && flowDateRange.value[1]) {
    params.order_date_from = flowDateRange.value[0]
    params.order_date_to = flowDateRange.value[1]
  }
  return params
}

const flowStats = computed(() => ({
  stuck: rows.value.filter((row) => Boolean(row.stuck_reason) || soListNextStepBlocked(row)).length,
  actionable: rows.value.filter((row) => soListNextStepActionable(soListNextStepKind(row))).length,
}))

function needsRekapPrintConfirm(_row) {
  // Cetak RKPO bukan gerbang: Confirm SO langsung Outstanding.
  return false
}

function canAdvanceRow(row) {
  if (!row) return false
  if (row.stuck_reason) return false
  if (needsRekapPrintConfirm(row)) return false
  const s = row.mkt_workflow_stage
  const idx = stageList.value.indexOf(normalizeFlowStage(s))
  return idx >= 0 && idx < stageList.value.length - 1
}

function canRollbackRow(row) {
  const s = row.mkt_workflow_stage || 'input_system'
  if (s === 'input_system') return false
  const locked = new Set(['delivery_arranged', 'sj_invpl', 'invoice_billing'])
  return !locked.has(s)
}

function toggleStageFilter(stage) {
  if (filterStage.value === stage) {
    filterStage.value = null
  } else {
    filterStage.value = stage
  }
  flowPage.value = 1
  load()
}

function clearFilter() {
  filterStage.value = null
  flowSoStatus.value = ''
  flowPage.value = 1
  load()
}

async function load() {
  loading.value = true
  try {
    const page = await listPoPage(buildFlowPageParams())
    rows.value = page.items || []
    totalFlowRows.value = Number(page.total || 0)
    stageCountMap.value = page.stage_counts || {}
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

async function loadOutstanding() {
  outstandingLoading.value = true
  try {
    const resp = await listMarketingOutstandingLines(buildOutstandingQueryParams())
    outstandingRows.value = unwrapOutstandingLines(resp).map((row) => ({
      ...row,
      lot_no: outstandingLotNo(row),
    }))
    outstandingTotal.value = Number(resp?.total ?? outstandingRows.value.length) || 0
    editingOutstandingId.value = null
    outstandingEditSnapshot.value = null
    outstandingSelection.value = []
    outstandingTableRef.value?.clearSelection?.()
    syncOutstandingFactoryOptions(outstandingRows.value)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingLoading.value = false
  }
}

function syncOutstandingFactoryOptions(rows) {
  const fromRows = (rows || [])
    .map((r) => String(r?.factory_code || '').trim())
    .filter(Boolean)
  const set = new Set([...(outstandingFactoryOptions.value || []), ...fromRows])
  // Saat filter pabrik kosong, refresh opsi dari data terbaru agar daftar lengkap
  if (!Array.isArray(factoryCode.value) || !factoryCode.value.length) {
    outstandingFactoryOptions.value = fromRows.length
      ? [...new Set(fromRows)].sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }))
      : [...set].sort((a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }))
    return
  }
  outstandingFactoryOptions.value = [...set].sort((a, b) =>
    a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' }),
  )
}

function onOutstandingFactoryChange() {
  outstandingPage.value = 1
  loadOutstanding()
}

function onOutstandingPoSearchChange() {
  outstandingPage.value = 1
  loadOutstanding()
}

function onOutstandingSheetChange() {
  outstandingPage.value = 1
  loadOutstanding()
}

function onOutstandingPageSizeChange() {
  outstandingPage.value = 1
  loadOutstanding()
}

function resetOutstandingFilters() {
  outstandingDateRange.value = null
  outstandingPoCategory.value = ''
  outstandingMaterialGroup.value = ''
  balanceFilter.value = 'exclude_zero'
  poSearch.value = ''
  factoryCode.value = []
  outstandingCustomerIds.value = []
  materialStatus.value = ''
  outstandingPage.value = 1
  workbenchOverride.value = null
  clearOutstandingColFilters()
  if (route.query.po_q) {
    const nextQuery = { ...route.query }
    delete nextQuery.po_q
    router.replace({ path: route.path, query: nextQuery })
    return
  }
  loadOutstanding()
}

function openOutstandingPi() {
  workbenchOverride.value = null
  if (!outstandingSelection.value.length) {
    ElMessage.warning(t('pages.marketingFlow.selectRowsFirst'))
    return
  }
  outstandingPiVisible.value = true
}

function openOutstandingShip() {
  workbenchOverride.value = null
  if (!outstandingSelection.value.length) {
    ElMessage.warning(t('pages.marketingFlow.selectRowsFirst'))
    return
  }
  const names = [
    ...new Set(
      outstandingSelection.value
        .map((r) => String(r.customer_name || '').trim())
        .filter(Boolean),
    ),
  ]
  if (names.length > 1) {
    ElMessage.warning(t('pages.marketingFlow.shipCustomerMismatch'))
    return
  }
  outstandingShipVisible.value = true
}

function workOnOutstandingRow(row, action) {
  if (!row) return
  workbenchOverride.value = [row]
  if (action === 'schedule') outstandingScheduleVisible.value = true
  else if (action === 'ship') outstandingShipVisible.value = true
  else if (action === 'pi') outstandingPiVisible.value = true
}

function outstandingWorkStatusLabel(row) {
  return t(`pages.marketingFlow.outWorkStatus.${outstandingWorkStatus(row)}`)
}

function outstandingWorkStatusType(row) {
  const st = outstandingWorkStatus(row)
  if (st === 'shipped' || st === 'closed') return 'success'
  if (st === 'scheduled') return 'success'
  if (st === 'partial_ship' || st === 'partial_schedule') return 'warning'
  return 'info'
}

function outstandingRowNextLabel(row) {
  return t(`pages.marketingFlow.outNext.${outstandingNextAction(row)}`)
}

function outstandingRowNextType(row) {
  const a = outstandingNextAction(row)
  if (a === 'ship') return 'warning'
  if (a === 'schedule') return 'primary'
  return 'default'
}

function runOutstandingRowPrimary(row) {
  const a = outstandingNextAction(row)
  if (a === 'schedule') workOnOutstandingRow(row, 'schedule')
  else if (a === 'ship') workOnOutstandingRow(row, 'ship')
  else goDeliveryFromPo({ po_number: row.thi_order })
}

function outstandingMoreItems(row) {
  const items = []
  const next = outstandingNextAction(row)
  if (next !== 'done') {
    items.push({
      command: next === 'schedule' ? 'schedule' : next === 'ship' ? 'ship' : 'delivery',
      label: outstandingRowNextLabel(row),
    })
  }
  items.push(
    { command: 'planning', label: t('pages.marketingFlow.viewPlanningSo') },
    { command: 'delivery', label: t('pages.marketingFlow.viewDeliverySo') },
    { command: 'pi', label: t('pages.marketingFlow.actionMakePi') },
  )
  if (next !== 'schedule') {
    items.push({ command: 'schedule', label: t('pages.marketingFlow.scheduleDraftButton') })
  }
  if (next !== 'ship') {
    items.push({ command: 'ship', label: t('pages.marketingFlow.actionShipPacking') })
  }
  if (canEditPoDetail) {
    items.push({ command: 'edit', label: t('pages.marketingFlow.outstandingEditRow'), divided: true })
  }
  // Deduplicate delivery if primary already added it
  const seen = new Set()
  return items.filter((item) => {
    if (seen.has(item.command)) return false
    seen.add(item.command)
    return true
  })
}

function onOutstandingRowMore(row, command) {
  if (command === 'pi') workOnOutstandingRow(row, 'pi')
  else if (command === 'schedule') workOnOutstandingRow(row, 'schedule')
  else if (command === 'ship') workOnOutstandingRow(row, 'ship')
  else if (command === 'edit') startOutstandingRowEdit(row)
  else if (command === 'so') goPo(row.po_id)
  else if (command === 'planning') goPlanningFromPo({ po_number: row.thi_order })
  else if (command === 'delivery') goDeliveryFromPo({ po_number: row.thi_order })
}

const outstandingStats = computed(() => {
  const list = outstandingDisplayRows.value || []
  let needSchedule = 0
  let needShip = 0
  for (const row of list) {
    const a = outstandingNextAction(row)
    if (a === 'schedule') needSchedule += 1
    if (a === 'ship') needShip += 1
  }
  return {
    shown: list.length,
    needSchedule,
    needShip,
    selected: outstandingSelection.value.length,
  }
})

function resetFlowFilters() {
  flowDateRange.value = null
  flowKeyword.value = ''
  filterStage.value = null
  flowSoStatus.value = ''
  flowCustomerIds.value = []
  flowPage.value = 1
  load()
}

function onFlowSoStatusChange() {
  flowPage.value = 1
  load()
}

function onFlowCustomerChange() {
  flowPage.value = 1
  load()
}


function applyPlanningViewModeRange() {
  const today = isoDateLocal(new Date())
  if (planningViewMode.value === 'today') {
    planningDateRange.value = [today, today]
    return
  }
  if (planningViewMode.value === 'overdue') {
    const s = new Date()
    s.setDate(s.getDate() - 30)
    planningDateRange.value = [isoDateLocal(s), today]
    return
  }
}

async function onPlanningViewModeChange() {
  applyPlanningViewModeRange()
  await loadPlanning()
}

function onPlanningDateRangeChange() {
  planningViewMode.value = 'range'
  planningPage.value = 1
  loadPlanning()
}

function goOpenDeliveryMenu() {
  router.push({ path: '/admin/delivery' })
}

async function loadPlanning() {
  planningLoading.value = true
  try {
    const rge = planningDateRange.value
    const df = Array.isArray(rge) && rge[0] ? rge[0] : isoDateLocal(new Date())
    const dt = Array.isArray(rge) && rge[1] ? rge[1] : df
    const fc = Array.isArray(planningFactory.value) && planningFactory.value.length
      ? planningFactory.value.map((x) => String(x).trim()).filter(Boolean).join(',')
      : undefined
    const r = await listMarketingDeliveryPlanning(
      buildPageParams({
        page: planningPage.value,
        pageSize: planningPageSize.value,
        sortBy: 'delivery_date',
        sortDir: 'desc',
        extra: {
          date_from: df,
          date_to: dt,
          factory_code: fc,
          mkt_stage_min: planningMktStageMin.value || undefined,
          po_q: planningPoSearch.value?.trim() || undefined,
        },
      }),
    )
    const pageData = normalizePageResult(r, {
      page: planningPage.value,
      pageSize: planningPageSize.value,
    })
    const rows = pageData.items.length
      ? pageData.items
      : Array.isArray(r?.data)
        ? r.data
        : []
    planningRows.value = rows
    planningTotal.value = Number(r?.total ?? pageData.total ?? rows.length)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    planningRows.value = []
    planningTotal.value = 0
  } finally {
    planningLoading.value = false
  }
}

async function loadSnapshotList() {
  snapshotsLoading.value = true
  try {
    snapshots.value = await listMarketingOutstandingSnapshots({ limit: 50 })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    snapshots.value = []
  } finally {
    snapshotsLoading.value = false
  }
}

async function saveOutstandingSnapshot() {
  snapshotSaving.value = true
  try {
    const q = buildOutstandingQueryParams()
    await createMarketingOutstandingSnapshot({
      label: snapshotLabel.value?.trim() || null,
      filters: {
        balance_filter: q.balance_filter,
        computed_balance: q.computed_balance,
        po_q: poSearch.value?.trim() || null,
        shipment_status: q.shipment_status,
        material_status: materialStatus.value || null,
        factory_code: Array.isArray(factoryCode.value) && factoryCode.value.length
          ? factoryCode.value.join(',')
          : null,
        customer_ids: Array.isArray(outstandingCustomerIds.value) && outstandingCustomerIds.value.length
          ? outstandingCustomerIds.value.join(',')
          : null,
        po_category: outstandingPoCategory.value?.trim() || null,
        material_group: outstandingMaterialGroup.value?.trim() || null,
        ...buildOutstandingDateParams(),
      },
    })
    ElMessage.success(t('pages.marketingFlow.snapshotCreated'))
    snapshotLabel.value = ''
    await loadSnapshotList()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    snapshotSaving.value = false
  }
}

async function openSnapshotDetail(id) {
  try {
    const r = await getMarketingOutstandingSnapshot(id)
    snapshotDetailRows.value = Array.isArray(r?.rows_json) ? r.rows_json : []
    snapshotDetailTitle.value = r?.label ? `Snapshot #${id} — ${r.label}` : `Snapshot #${id}`
    snapshotDetailVisible.value = true
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

onMounted(async () => {
  try {
    const cust = await listCustomers()
    marketingCustomers.value = Array.isArray(cust) ? cust : (cust?.data || [])
  } catch {
    marketingCustomers.value = []
  }
  if (section.value === 'flow') {
    try {
      const data = await listPoMktStages()
      stageList.value = data.stages || []
    } catch {
      stageList.value = []
    }
    await Promise.all([
      load(),
    ])
    flowWatchReady = true
    return
  }
  if (section.value === 'outstanding') {
    poSearch.value = String(route.query.po_q || '').trim()
    await loadOutstanding()
    return
  }
  planningPoSearch.value = String(route.query.po_q || '').trim()
  await loadPlanning()
})

onUnmounted(() => {
  if (flowKeywordTimer) clearTimeout(flowKeywordTimer)
})

watch(flowKeyword, () => {
  if (section.value !== 'flow') return
  if (flowKeywordTimer) clearTimeout(flowKeywordTimer)
  flowKeywordTimer = setTimeout(() => {
    flowPage.value = 1
    if (flowWatchReady) load()
  }, 350)
})

watch(flowDateRange, () => {
  if (section.value !== 'flow' || !flowWatchReady) return
  flowPage.value = 1
  load()
})

watch([flowPage, flowPageSize], () => {
  if (section.value !== 'flow' || !flowWatchReady) return
  load()
})

function stuckReasonLabel(reason) {
  return translateStuckReason(reason, t)
}

function soListNextStepKind(row) {
  return soListNextStep(row)
}

function soListNextStepLabel(row) {
  return t(`pages.marketingFlow.nextStep.${soListNextStepKind(row)}`)
}

function soListNextStepBlocked(row) {
  const kind = soListNextStepKind(row)
  return Boolean(row?.stuck_reason) || needsRekapPrintConfirm(row) || kind === 'wait'
}

function soListNextStepHint(row) {
  const kind = soListNextStepKind(row)
  if (row?.stuck_reason) {
    const label = stuckReasonLabel(row.stuck_reason)
    if (String(row.stuck_reason).includes('Delivery belum')) {
      return `${label} ${t('pages.marketingFlow.deliveryDraftHint')}`
    }
    return label
  }
  if (needsRekapPrintConfirm(row)) return stuckReasonLabel('Menunggu rekap PO diprint')
  if (kind === 'advance' && canAdvanceRow(row)) return t('pages.marketingFlow.readyToAdvance')
  return t(`pages.marketingFlow.nextStepHint.${kind}`)
}

function soListNextStepTagType(row) {
  const kind = soListNextStepKind(row)
  if (kind === 'done') return 'success'
  if (kind === 'wait' || soListNextStepBlocked(row)) return 'warning'
  if (kind === 'advance' && canAdvanceRow(row)) return 'success'
  return 'primary'
}

function soListNextStepTagClass(row) {
  return {
    'mkt-stuck-tag--blocked': soListNextStepBlocked(row) && soListNextStepKind(row) !== 'done',
    'mkt-stuck-tag--ready': soListNextStepKind(row) === 'done' || (soListNextStepKind(row) === 'advance' && canAdvanceRow(row)),
  }
}

function soListPrimaryVisible(row) {
  const kind = soListNextStepKind(row)
  if (kind === 'wait' || kind === 'done') return false
  if (kind === 'advance' && !canAdvance.value) return false
  return true
}

function soListPrimaryLabel(row) {
  return soListNextStepLabel(row)
}

function soListPrimaryType(row) {
  const kind = soListNextStepKind(row)
  if (kind === 'rekap' || kind === 'delivery' || kind === 'invoice') return 'success'
  if (kind === 'planning') return 'warning'
  return 'primary'
}

function soListPrimaryLoading(row) {
  if (soListNextStepKind(row) === 'advance') return advancing.value === row?.id
  return false
}

function soListPrimaryDisabled(row) {
  if (advancing.value != null && advancing.value !== row?.id) return true
  if (soListNextStepKind(row) === 'advance') return !canAdvanceRow(row)
  return false
}

function runSoListPrimary(row) {
  const kind = soListNextStepKind(row)
  if (kind === 'rekap') openRekapPrintDialog(row)
  else if (kind === 'advance') advance(row)
  else if (kind === 'outstanding') goOutstandingFromPo(row)
  else if (kind === 'planning') goPlanningFromPo(row)
  else if (kind === 'delivery' || kind === 'invoice') goDeliveryFromPo(row)
}

function soListMoreItems(row) {
  const items = []
  const kind = soListNextStepKind(row)
  if (soListPrimaryVisible(row)) {
    const cmd = kind === 'invoice' ? 'delivery' : kind
    items.push({
      command: cmd,
      label: soListPrimaryLabel(row),
      disabled: soListPrimaryDisabled(row),
    })
  }
  if (kind !== 'rekap') {
    items.push({ command: 'rekap', label: t('pages.marketingFlow.rekapPrintAction') })
  }
  if (kind !== 'outstanding') {
    items.push({ command: 'outstanding', label: t('pages.marketingFlow.viewOutstandingSo') })
  }
  if (kind !== 'planning') {
    items.push({ command: 'planning', label: t('pages.marketingFlow.viewPlanningSo') })
  }
  if (kind !== 'delivery' && kind !== 'invoice') {
    items.push({ command: 'delivery', label: t('pages.marketingFlow.viewDeliverySo') })
  }
  if (canFlowUpdate.value) {
    items.push({ command: 'remark', label: t('pages.marketingFlow.materialRemark') })
  }
  if (canRollback.value && canRollbackRow(row)) {
    items.push({ command: 'rollback', label: t('pages.marketingFlow.rollbackStageHint'), divided: true })
  }
  return items
}

function onSoListMore(row, command) {
  if (command === 'detail') goPo(row.id)
  else if (command === 'advance') advance(row)
  else if (command === 'rekap') openRekapPrintDialog(row)
  else if (command === 'outstanding') goOutstandingFromPo(row)
  else if (command === 'planning') goPlanningFromPo(row)
  else if (command === 'delivery') goDeliveryFromPo(row)
  else if (command === 'remark') openMaterialFollowUpDialog(row)
  else if (command === 'rollback') openRollbackDialog(row)
}

function planningSlotMoreItems(row) {
  const items = []
  if (row.latest_delivery_id) {
    items.push({ command: 'openSj', label: t('pages.marketingFlow.planningOpenSj') })
  } else if (row.ship_status === 'shipped' || row.ship_status === 'partial') {
    items.push({ command: 'openDelivery', label: t('pages.marketingFlow.openDelivery') })
  }
  // Pantauan saja — buat SJ hanya di Outstanding
  items.push({ command: 'outstanding', label: t('pages.marketingFlow.planningOpenOutstanding') })
  return items
}

function handlePlanningSlotMore(row, command) {
  if (command === 'openSj') goDeliveryById(row.latest_delivery_id)
  else if (command === 'openDelivery') goDeliveryFromPlanning(row)
  else if (command === 'outstanding') goOutstandingFromPlanning(row)
}


function openMaterialFollowUpDialog(row) {
  selectedPoForMaterialFollowUp.value = row
  materialFollowUpForm.remark = row.material_followup_remark || ''
  materialFollowUpDialogVisible.value = true
}

async function saveMaterialFollowUp() {
  savingMaterialFollowUp.value = true
  try {
    await updatePo(selectedPoForMaterialFollowUp.value.id, {
      material_followup_remark: materialFollowUpForm.remark.trim() || null,
    })
    selectedPoForMaterialFollowUp.value.material_followup_remark = materialFollowUpForm.remark.trim() || null
    ElMessage.success(t('common.saveSuccess'))
    materialFollowUpDialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    savingMaterialFollowUp.value = false
  }
}

async function advance(row) {
  if (!canAdvanceRow(row)) {
    ElMessage.warning(
      needsRekapPrintConfirm(row) || row?.stuck_reason === 'Menunggu rekap PO diprint'
        ? t('pages.marketingFlow.advanceBlockedNeedRekapPrint')
        : stuckReasonLabel(row?.stuck_reason) || t('pages.marketingFlow.stuckReason'),
    )
    return
  }
  advancing.value = row.id
  try {
    await advanceMktWorkflow(row.id)
    ElMessage.success(t('pages.marketingFlow.advanced'))
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    advancing.value = null
  }
}

const rollbackDialogVisible = ref(false)
const rollbackTarget = ref(null)
const rollbackReason = ref('')

function openRollbackDialog(row) {
  rollbackTarget.value = row
  rollbackReason.value = ''
  rollbackDialogVisible.value = true
}

async function submitRollback() {
  const row = rollbackTarget.value
  if (!row) return
  const reason = String(rollbackReason.value || '').trim()
  if (reason.length < 5) {
    ElMessage.warning(t('pages.marketingFlow.rollbackReasonMin'))
    return
  }
  rollingBack.value = row.id
  try {
    await rollbackMktWorkflow(row.id, { reason })
    ElMessage.success(t('pages.marketingFlow.rolledBack'))
    rollbackDialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    rollingBack.value = null
  }
}

function goPo(id) {
  router.push({ path: '/admin/po', query: { po_id: String(id) } })
}

function soStatusLabel(st) {
  const key = String(st || '').trim().toLowerCase()
  if (!key) return t('common.emptyValue')
  if (key === 'canceled' && te('status.cancelled')) return t('status.cancelled')
  if (te(`status.${key}`)) return t(`status.${key}`)
  return st
}

function goOutstandingFromPo(row) {
  const q = String(row?.po_number || '').trim()
  router.push({
    path: '/admin/marketing-flow/outstanding',
    query: q ? { po_q: q } : {},
  })
}

function goPlanningFromPo(row) {
  const q = String(row?.po_number || '').trim()
  router.push({
    path: '/admin/marketing-flow/planning',
    query: q ? { po_q: q } : {},
  })
}

function goDeliveryFromPo(row) {
  const so = String(row?.po_number || '').trim()
  router.push({
    path: '/admin/delivery',
    query: so ? { keyword: so } : {},
  })
}

function planningShipStatusLabel(status) {
  const key = String(status || '').trim()
  if (key === 'partial') return t('pages.marketingFlow.planningShipStatusPartial')
  if (key === 'shipped') return t('pages.marketingFlow.planningShipStatusShipped')
  if (key === 'too_early') return t('pages.marketingFlow.planningShipStatusTooEarly')
  return t('pages.marketingFlow.planningShipStatusPlanned')
}

function planningShipTagType(status) {
  if (status === 'shipped') return 'success'
  if (status === 'partial') return 'warning'
  if (status === 'too_early') return 'info'
  return ''
}

function planningDeliveryStatusLabel(status) {
  const key = String(status || '').trim().toLowerCase()
  if (key === 'sent' && te('status.sent')) return t('status.sent')
  if ((key === 'draft' || !key) && te('status.draft')) return t('status.draft')
  if (key && te(`status.${key}`)) return t(`status.${key}`)
  return key || t('status.draft')
}

function planningDeliveryStatusTagType(status) {
  const key = String(status || '').trim().toLowerCase()
  if (key === 'sent') return 'success'
  if (key === 'draft' || !key) return 'warning'
  return 'info'
}

function goDeliveryFromPlanning(row) {
  if (row?.latest_delivery_id) {
    goDeliveryById(row.latest_delivery_id)
    return
  }
  const q = {}
  const so = String(row?.po_number || '').trim()
  if (so) q.keyword = so
  const fc = row?.factory_code != null ? String(row.factory_code).trim() : ''
  if (fc) q.factory_code = fc
  router.push({ path: '/admin/delivery', query: q })
}

function goDeliveryById(deliveryId) {
  const id = Number(deliveryId)
  if (!id || Number.isNaN(id)) return
  router.push({ path: '/admin/delivery', query: { delivery_id: String(id) } })
}

function goOutstandingFromPlanning(row) {
  const q = String(row?.po_number || '').trim()
  router.push({
    path: '/admin/marketing-flow/outstanding',
    query: q ? { po_q: q } : {},
  })
}

function onWorkbenchDone(_payload) {
  workbenchOverride.value = null
  if (section.value === 'outstanding') {
    loadOutstanding()
    return
  }
  loadPlanning()
}

async function openSnapshotArchive() {
  snapshotArchiveVisible.value = true
  await loadSnapshotList()
}

function openRekapPrintDialog(row) {
  if (!row?.id) return
  rekapPoId.value = row.id
  rekapPoNumber.value = row.po_number || ''
  rekapPrintVisible.value = true
}

async function onRekapConfirmed() {
  await load()
}

async function pullCrToday() {
  const today = new Date().toISOString().slice(0, 10)
  flowDateRange.value = [today, today]
  await load()
  ElMessage.success(t('pages.marketingFlow.soTodayDone'))
}

async function downloadDailyPoReportXlsx() {
  poDailyXlsxLoading.value = true
  try {
    const fr = flowDateRange.value
    const from = Array.isArray(fr) && fr[0] ? fr[0] : new Date().toISOString().slice(0, 10)
    const to = Array.isArray(fr) && fr[1] ? fr[1] : from
    const path = reportPoDailyMarketingXlsxPath({
      date_from: from,
      date_to: to,
      date_field: 'order',
    })
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null
    const r = await fetch(path, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (!r.ok) {
      const text = await r.text()
      throw new Error(text || r.statusText)
    }
    const blob = await r.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `laporan_po_harian_${from}_${to}.xlsx`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(t('pages.marketingFlow.dailyPoReportDone'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    poDailyXlsxLoading.value = false
  }
}

async function downloadOutstanding() {
  try {
    await fetchAuthenticatedDocument(marketingOutstandingCsvUrl(buildOutstandingExportParams()), {
      mode: 'download',
      downloadFallbackName: 'marketing-outstanding.csv',
    })
    ElMessage.success(
      outstandingSelection.value.length
        ? t('pages.marketingFlow.outstandingCsvOkSelected', { n: outstandingSelection.value.length })
        : t('pages.marketingFlow.outstandingCsvOk'),
    )
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}


function handleFlowExportCommand(command) {
  if (command === 'daily') downloadDailyPoReportXlsx()
}

function handleOutstandingExportCommand(command) {
  if (command === 'csv') downloadOutstanding()
  else if (command === 'xlsx') downloadOutstandingXlsx()
  else if (command === 'retur') downloadReturnXlsx()
  else if (command === 'manual') downloadManualWorkbook()
}
</script>

<style scoped>
.mkt-active-filter {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.mkt-stage-pipeline {
  display: flex;
  flex-wrap: nowrap;
  align-items: flex-start;
  gap: 8px;
  overflow-x: auto;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #f8fafc;
  -webkit-overflow-scrolling: touch;
}

.mkt-stage-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 0 0 auto;
  cursor: pointer;
  min-width: 88px;
  padding: 4px;
  border-radius: 8px;
  transition: background-color 0.15s ease;
}

.mkt-stage-item:hover {
  background: #eef2ff;
}

.mkt-stage-item--active {
  background: #e0e7ff;
  box-shadow: inset 0 0 0 1px #c7d2fe;
}

.mkt-stage-item--current {
  background: rgba(34, 197, 94, 0.08);
}

.mkt-stage-item--next {
  background: rgba(59, 130, 246, 0.08);
}

.mkt-stage-separator {
  flex: 0 0 auto;
  color: #94a3b8;
  font-size: 18px;
  line-height: 1;
  padding-top: 4px;
}

.mkt-row-stages {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
}

.mkt-row-stages__arrow {
  color: #94a3b8;
  font-size: 12px;
  line-height: 1;
}

.mkt-pulse-tag--current {
  --mkt-pulse: 34, 197, 94;
  border-color: rgb(var(--mkt-pulse)) !important;
  background: rgba(var(--mkt-pulse), 0.92) !important;
  color: #fff !important;
  animation: mkt-pulse-green 1.25s ease-in-out infinite;
}

.mkt-pulse-tag--next {
  --mkt-pulse: 59, 130, 246;
  border-color: rgb(var(--mkt-pulse)) !important;
  color: rgb(var(--mkt-pulse)) !important;
  background: rgba(var(--mkt-pulse), 0.12) !important;
  animation: mkt-pulse-blue 1.25s ease-in-out infinite;
}

@keyframes mkt-pulse-green {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.55);
    filter: brightness(1);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(34, 197, 94, 0);
    filter: brightness(1.12);
  }
}

@keyframes mkt-pulse-blue {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.45);
    filter: brightness(1);
  }
  50% {
    box-shadow: 0 0 0 6px rgba(59, 130, 246, 0);
    filter: brightness(1.08);
  }
}

@media (prefers-reduced-motion: reduce) {
  .mkt-pulse-tag--current,
  .mkt-pulse-tag--next {
    animation: none;
  }
}

.mkt-flow-filter-panel {
  padding-bottom: 12px;
}

.mkt-flow-filter {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mkt-flow-filter__fields {
  display: grid;
  grid-template-columns: minmax(240px, 420px) minmax(180px, 240px);
  gap: 12px 14px;
  align-items: end;
}

.mkt-flow-howto {
  margin: 0;
  font-size: 12px;
  line-height: 1.45;
  color: #64748b;
}

.mkt-flow-filter__footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px 16px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.mkt-flow-filter__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 12px;
  min-width: 0;
}

.mkt-flow-stat-chips {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.mkt-flow-stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  line-height: 1.3;
}

.mkt-flow-stat-chip strong {
  color: #0f172a;
  font-weight: 700;
}

.mkt-flow-stat-chip--warn {
  background: #fff7ed;
  color: #9a3412;
}

.mkt-flow-stat-chip--warn strong {
  color: #9a3412;
}

.mkt-flow-stat-chip--ok {
  background: #ecfdf5;
  color: #047857;
}

.mkt-flow-stat-chip--ok strong {
  color: #047857;
}

.mkt-flow-filter__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-left: auto;
}

.mkt-flow-filter__actions :deep(.el-button) {
  min-width: 108px;
}

@media (max-width: 640px) {
  .mkt-flow-filter__fields {
    grid-template-columns: 1fr;
  }

  .mkt-flow-filter__footer {
    flex-direction: column;
    align-items: stretch;
  }

  .mkt-flow-filter__actions {
    margin-left: 0;
  }

  .mkt-flow-filter__actions :deep(.el-button) {
    flex: 1 1 auto;
  }
}

.mkt-out-body {
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mkt-out-toolbar {
  display: inline-flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 8px;
}

.mkt-out-toolbar :deep(.el-button + .el-button) {
  margin-left: 0;
}

.mkt-out-toolbar-actions {
  display: inline-flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 8px;
}

.mkt-out-filter-panel {
  margin: 0;
  padding: 12px 14px;
  border: 1px solid #e8edf3;
  border-radius: 10px;
  background: #f8fafc;
}

.mkt-out-filter-panel__head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px 12px;
  margin: 0 0 10px;
  padding: 0 0 8px;
  border-bottom: 1px solid #e2e8f0;
}

.mkt-out-filter-panel__head .filter-panel__title {
  margin: 0;
  line-height: 1.3;
}

.mkt-out-filter {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mkt-out-filter__fields {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px 12px;
  align-items: end;
}

.mkt-out-filter__row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px 12px;
  align-items: end;
}

.mkt-out-filter__row--sheet {
  padding-top: 0;
}

.mkt-out-filter__footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px 16px;
  padding-top: 10px;
  border-top: 1px solid #e2e8f0;
}

.mkt-out-view-toggle {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  flex: 0 0 auto;
}

.mkt-out-view-toggle__label {
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.mkt-out-field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.mkt-out-field__label {
  font-size: 12px;
  font-weight: 600;
  line-height: 1.25;
  color: #475569;
  margin: 0;
}

.mkt-out-field__hint {
  margin: 0;
  font-size: 11px;
  line-height: 1.35;
  color: #64748b;
}

.mkt-out-field__control {
  width: 100%;
}

.mkt-out-field :deep(.el-input),
.mkt-out-field :deep(.el-select),
.mkt-out-field :deep(.el-date-editor),
.mkt-out-field :deep(.el-range-editor) {
  width: 100% !important;
}

.mkt-out-field :deep(.el-date-editor.el-input__wrapper),
.mkt-out-field :deep(.el-range-editor.el-input__wrapper),
.mkt-out-field :deep(.el-date-editor--daterange) {
  width: 100% !important;
  max-width: 100%;
  box-sizing: border-box;
}

.mkt-out-field--segment .mkt-out-segment {
  display: flex;
  flex-wrap: wrap;
  width: 100%;
}

.mkt-out-segment :deep(.el-radio-button__inner) {
  padding: 7px 11px;
  min-width: 60px;
  text-align: center;
}

.mkt-out-col-filter-tip {
  margin: 0;
  padding: 0 2px;
  font-size: 12px;
  line-height: 1.4;
  color: #64748b;
}

.mkt-fg-pack-head {
  font-size: 0.875rem;
  margin-bottom: 0.35rem;
}

.mkt-out-table-wrap {
  margin: 0;
  padding: 0;
}

.outstanding-table--col-filters :deep(th.el-table__cell) {
  vertical-align: top;
  padding: 8px 6px;
}

.mkt-out-pagination {
  margin: 0;
  padding: 10px 2px 0;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #eef2f6;
}

.mkt-out-filter__actions {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
}

.mkt-out-filter__actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.mkt-out-filter__actions :deep(.el-button.is-circle) {
  min-width: 32px;
}

@media (max-width: 1100px) {
  .mkt-out-filter__fields {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .mkt-out-body {
    padding: 12px;
    gap: 10px;
  }

  .mkt-out-filter-panel {
    padding: 10px 12px;
  }

  .mkt-out-filter__fields {
    grid-template-columns: 1fr;
  }

  .mkt-out-toolbar,
  .mkt-out-toolbar-actions {
    flex-wrap: wrap;
  }
}

.mkt-filter-form :deep(.el-form-item__content) {
  width: 100%;
}

.mkt-filter-form :deep(.mkt-filter-control),
.mkt-filter-form :deep(.mkt-filter-control.el-input),
.mkt-filter-form :deep(.mkt-filter-control.el-select),
.mkt-filter-form :deep(.mkt-filter-control.el-date-editor) {
  width: 100%;
}

.mkt-filter-form :deep(.el-date-editor.el-input__wrapper),
.mkt-filter-form :deep(.el-date-editor--daterange),
.mkt-filter-form :deep(.el-range-editor.el-input__wrapper) {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.mkt-filter-action-col :deep(.el-form-item__label) {
  visibility: hidden;
  user-select: none;
}

.mkt-filter-action-col :deep(.el-form-item__content) {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.mkt-filter-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding-bottom: 12px;
}

.mkt-filter-btn {
  min-width: 108px;
}

.mkt-filter-radios {
  display: flex;
  flex-wrap: wrap;
  width: 100%;
}

.mkt-filter-radios :deep(.el-radio-button__inner) {
  padding: 8px 12px;
}

.marketing-flow-table {
  width: 100%;
  min-width: 1180px;
}

.mkt-next-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.mkt-next-hint {
  margin: 0;
  font-size: 11px;
  line-height: 1.4;
  color: #64748b;
}

.mkt-so-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.marketing-outstanding-table {
  width: 100%;
  min-width: 1400px;
}

.marketing-outstanding-table.outstanding-table--work {
  min-width: 1280px;
}

/* Header kolom 1 baris — label tidak wrap antar kata */
.marketing-outstanding-table :deep(th.el-table__cell),
.marketing-outstanding-table :deep(th.el-table__cell > .cell) {
  white-space: nowrap;
  line-height: 1.25;
}

.marketing-outstanding-table :deep(th.el-table__cell > .cell) {
  overflow: hidden;
  text-overflow: ellipsis;
}

.marketing-outstanding-table :deep(tr.out-row--g0 > td.el-table__cell) {
  background-color: #f8fafc;
}
.marketing-outstanding-table :deep(tr.out-row--g1 > td.el-table__cell) {
  background-color: #f0f7ff;
}
.marketing-outstanding-table :deep(tr.out-row--g2 > td.el-table__cell) {
  background-color: #f0fdf6;
}
.marketing-outstanding-table :deep(tr.out-row--g3 > td.el-table__cell) {
  background-color: #fffbeb;
}
.marketing-outstanding-table :deep(tr.out-row--g4 > td.el-table__cell) {
  background-color: #faf5ff;
}
.marketing-outstanding-table :deep(tr.out-row--g5 > td.el-table__cell) {
  background-color: #fff1f2;
}

.marketing-outstanding-table :deep(tr.out-row--g0 > td.out-col-thi-order) {
  box-shadow: inset 3px 0 0 #94a3b8;
}
.marketing-outstanding-table :deep(tr.out-row--g1 > td.out-col-thi-order) {
  box-shadow: inset 3px 0 0 #93c5fd;
}
.marketing-outstanding-table :deep(tr.out-row--g2 > td.out-col-thi-order) {
  box-shadow: inset 3px 0 0 #86efac;
}
.marketing-outstanding-table :deep(tr.out-row--g3 > td.out-col-thi-order) {
  box-shadow: inset 3px 0 0 #fcd34d;
}
.marketing-outstanding-table :deep(tr.out-row--g4 > td.out-col-thi-order) {
  box-shadow: inset 3px 0 0 #d8b4fe;
}
.marketing-outstanding-table :deep(tr.out-row--g5 > td.out-col-thi-order) {
  box-shadow: inset 3px 0 0 #fda4af;
}

.marketing-outstanding-table :deep(tr.out-row--group-start > td.el-table__cell) {
  border-top: 1px solid #e2e8f0;
}

/* Angka yang berasal dari MRP, bukan dari order ERP. */
.out-color-std {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  line-height: 1.25;
}
.out-color-std__date {
  display: inline-flex;
  align-items: center;
  padding: 1px 8px;
  border-radius: 999px;
  border: 1px solid #99f6e4;
  background: #f0fdfa;
  color: #0f766e;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.01em;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.out-mrp-qty {
  color: #7c3aed;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

/* Header grup kolom Outstanding — border tipis, warna seragam. */
.marketing-outstanding-table :deep(th.out-col-group-label) {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: #64748b;
  background: #f1f5f9 !important;
  border: 1px solid #e2e8f0 !important;
}

/* Pemisah grup tipis di sub-header & body */
.marketing-outstanding-table :deep(th.out-group-start),
.marketing-outstanding-table :deep(td.out-group-start) {
  border-left: 1px solid #cbd5e1 !important;
}
.marketing-outstanding-table :deep(th.out-group-end),
.marketing-outstanding-table :deep(td.out-group-end) {
  border-right: 1px solid #cbd5e1 !important;
}

.marketing-outstanding-table :deep(tr.out-row--g0:hover > td.el-table__cell) {
  background-color: #f1f5f9 !important;
}
.marketing-outstanding-table :deep(tr.out-row--g1:hover > td.el-table__cell) {
  background-color: #e0effe !important;
}
.marketing-outstanding-table :deep(tr.out-row--g2:hover > td.el-table__cell) {
  background-color: #dcfce7 !important;
}
.marketing-outstanding-table :deep(tr.out-row--g3:hover > td.el-table__cell) {
  background-color: #fef3c7 !important;
}
.marketing-outstanding-table :deep(tr.out-row--g4:hover > td.el-table__cell) {
  background-color: #f3e8ff !important;
}
.marketing-outstanding-table :deep(tr.out-row--g5:hover > td.el-table__cell) {
  background-color: #ffe4e6 !important;
}

.admin-table {
  width: 100%;
}
.mkt-out-row-actions {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.mkt-out-date-edit {
  width: 100%;
}

.mkt-out-date-edit :deep(.el-input__wrapper) {
  padding-left: 6px;
  padding-right: 6px;
}

.outstanding-table {
  width: 100%;
}
.mkt-plan-pane {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mkt-plan-filter-panel {
  margin-bottom: 0;
  padding-bottom: 12px;
}

.mkt-plan-filter {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mkt-plan-filter__fields {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 14px;
  align-items: end;
  max-width: 720px;
}

.mkt-out-field--span2 {
  grid-column: 1 / -1;
}

.mkt-plan-filter__footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px 16px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.mkt-plan-stat-chips {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.mkt-plan-stat-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  line-height: 1.3;
}

.mkt-plan-stat-chip strong {
  color: #0f172a;
  font-weight: 700;
}

.mkt-plan-stat-chip--warn {
  background: #fef2f2;
  color: #b91c1c;
}

.mkt-plan-stat-chip--warn strong {
  color: #991b1b;
}

.mkt-plan-status-cell {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.mkt-plan-filter__actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-left: auto;
}

.mkt-plan-filter__actions :deep(.el-button) {
  min-width: 108px;
}

.mkt-plan-today {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.mkt-plan-block {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  padding: 12px;
}

.mkt-plan-block__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
}

.mkt-plan-block__title {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  color: #334155;
}

.mkt-plan-block__count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  font-weight: 700;
}

.mkt-plan-table {
  width: 100%;
}

.mkt-plan-tabs :deep(.el-tabs__header) {
  margin: 0 0 14px;
}

.mkt-plan-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: #e2e8f0;
}

.mkt-plan-tabs :deep(.el-tabs__item) {
  height: 40px;
  font-weight: 600;
}

.mkt-plan-tabs :deep(.el-tabs__content) {
  padding-top: 0;
  overflow: visible;
}

.marketing-tabs :deep(.el-tabs__header) {
  margin-bottom: 14px;
}

.marketing-tabs :deep(.el-tabs__content) {
  padding-top: 0;
}

@media (max-width: 640px) {
  .mkt-plan-filter__fields {
    grid-template-columns: 1fr;
    max-width: none;
  }

  .mkt-out-field--span2 {
    grid-column: auto;
  }

  .mkt-plan-filter__footer {
    flex-direction: column;
    align-items: stretch;
  }

  .mkt-plan-filter__actions {
    margin-left: 0;
    width: 100%;
  }

  .mkt-plan-filter__actions :deep(.el-button) {
    flex: 1 1 auto;
  }
}
.mkt-stuck-cell {
  display: flex;
  align-items: flex-start;
  min-height: 28px;
}
.mkt-stuck-tag {
  max-width: 100%;
  height: auto;
  white-space: normal;
  border: none;
}
.mkt-stuck-tag :deep(.el-tag__content) {
  white-space: normal;
  line-height: 1.35;
}
.mkt-stuck-tag__inner {
  display: inline-flex;
  align-items: flex-start;
  gap: 5px;
  text-align: left;
}
.mkt-stuck-tag__inner .el-icon {
  flex-shrink: 0;
  margin-top: 1px;
  font-size: 14px;
}
.mkt-stuck-tag__text {
  font-size: 12px;
  line-height: 1.4;
  word-break: break-word;
}
.mkt-stuck-tag--blocked {
  --el-tag-bg-color: var(--el-color-warning-light-9);
  --el-tag-text-color: var(--el-color-warning-dark-2);
}
.mkt-stuck-tag--ready {
  --el-tag-bg-color: var(--el-color-success-light-9);
  --el-tag-text-color: var(--el-color-success-dark-2);
}
.mkt-stuck-empty {
  color: var(--el-text-color-placeholder);
  font-size: 12px;
}
</style>
