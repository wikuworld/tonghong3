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
        <el-button type="warning" @click="pullCrToday">{{ t('pages.marketingFlow.pullCrToday') }}</el-button>
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
                type="primary"
                plain
                :disabled="!outstandingSelection.length"
                @click="openOutstandingSchedule"
              >
                {{ t('pages.marketingFlow.scheduleDraftButton') }}
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
          </div>

          <div class="mkt-flow-filter__footer">
            <div class="mkt-flow-filter__meta">
              <template v-if="filterStage">
                <span class="mkt-active-filter">
                  {{ t('pages.marketingFlow.filterStage') }}: {{ labelFor(filterStage) }}
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
                  {{ t('pages.marketingFlow.readyToAdvance') }}: <strong>{{ flowStats.ready }}</strong>
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
        <el-table-column prop="po_number" :label="t('common.poNo')" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex flex-wrap items-center gap-1">
              <PoItemRevisedDot :row="row" />
              <el-button link type="primary" @click="goPo(row.id)">
                {{ row.po_number || `#${row.id}` }}
              </el-button>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.colMktStage')" min-width="200">
          <template #default="{ row }">
            <div class="mkt-row-stages">
              <el-tag size="small" effect="dark" class="mkt-pulse-tag mkt-pulse-tag--current">
                {{ labelFor(normalizeFlowStage(row.mkt_workflow_stage)) }}
              </el-tag>
              <template v-if="nextFlowStage(row.mkt_workflow_stage)">
                <span class="mkt-row-stages__arrow">›</span>
                <el-tag size="small" effect="plain" class="mkt-pulse-tag mkt-pulse-tag--next">
                  {{ labelFor(nextFlowStage(row.mkt_workflow_stage)) }}
                </el-tag>
              </template>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('pages.marketingFlow.colSoStatus')" width="120">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.status || t('common.emptyValue') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order_date" :label="t('common.orderDate')" width="110" />
        <el-table-column :label="t('pages.marketingFlow.materialDone')" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="Boolean(row.material_followup_done)"
              size="small"
              :disabled="!canFlowUpdate"
              @change="(val) => toggleMaterialFollowUp(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.materialRemark')" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.material_followup_remark" class="text-xs">{{ row.material_followup_remark }}</span>
            <el-button v-else-if="canFlowUpdate" type="primary" link size="small" @click="openMaterialFollowUpDialog(row)">
              {{ t('pages.marketingFlow.addRemark') }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column :label="t('ppicWorkflow.status')" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="ppicAssignments[row.id]" size="small" :type="ppicAssignments[row.id].status === 'completed' ? 'success' : ppicAssignments[row.id].status === 'in_progress' ? 'warning' : 'info'">
              {{ ppicStatusLabel(ppicAssignments[row.id].status) }}
            </el-tag>
            <span v-else class="text-gray-400 text-xs">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.stuckReason')" min-width="220">
          <template #default="{ row }">
            <div class="mkt-stuck-cell">
              <el-tag
                v-if="row.stuck_reason || needsRekapPrintConfirm(row)"
                type="warning"
                size="small"
                effect="light"
                class="mkt-stuck-tag mkt-stuck-tag--blocked"
              >
                <span class="mkt-stuck-tag__inner">
                  <el-icon><Warning /></el-icon>
                  <span class="mkt-stuck-tag__text">{{
                    stuckReasonLabel(row.stuck_reason || 'Menunggu rekap PO diprint')
                  }}</span>
                </span>
              </el-tag>
              <el-tag
                v-else-if="canAdvanceRow(row)"
                type="success"
                size="small"
                effect="light"
                class="mkt-stuck-tag mkt-stuck-tag--ready"
              >
                <span class="mkt-stuck-tag__inner">
                  <el-icon><CircleCheck /></el-icon>
                  <span class="mkt-stuck-tag__text">{{ t('pages.marketingFlow.readyToAdvance') }}</span>
                </span>
              </el-tag>
              <span v-else class="mkt-stuck-empty">{{ t('common.emptyValue') }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <el-tooltip v-if="canAdvance" :content="advanceTooltip(row)" placement="top">
              <el-button
                type="primary"
                link
                size="small"
                :loading="advancing === row.id"
                :disabled="!canAdvanceRow(row) || (advancing != null && advancing !== row.id)"
                @click="advance(row)"
              >
                <el-icon><DArrowRight /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip v-if="canRollback && canRollbackRow(row)" :content="t('pages.marketingFlow.rollbackStageHint')" placement="top">
              <el-button
                type="warning"
                link
                size="small"
                :loading="rollingBack === row.id"
                :disabled="rollingBack != null && rollingBack !== row.id"
                @click="openRollbackDialog(row)"
              >
                <el-icon><DArrowLeft /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip :content="t('pages.marketingFlow.rekapPrintAction')" placement="top">
              <el-button type="success" link size="small" @click="openRekapPrintDialog(row)">
                <el-icon><Printer /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip :content="t('pages.marketingFlow.openPoDetail')" placement="top">
              <el-button type="default" link size="small" @click="goPo(row.id)">
                <el-icon><Document /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip v-if="canEditPoDetail" :content="t('ppicWorkflow.assignToPpic')" placement="top">
              <el-button type="warning" link size="small" @click="openAssignDialog(row)">
                <el-icon><User /></el-icon>
              </el-button>
            </el-tooltip>
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
      v-if="section === 'outstanding'"
      v-model:schedule-visible="outstandingScheduleVisible"
      v-model:pi-visible="outstandingPiVisible"
      v-model:ship-visible="outstandingShipVisible"
      :rows="outstandingSelection"
      @done="loadOutstanding"
    />

    <div v-if="section === 'outstanding'" class="admin-inner-card mkt-out-card">
      <div class="mkt-section-body mkt-out-body">
      <div class="filter-panel mkt-out-filter-panel">
        <div class="mkt-out-filter-panel__head">
          <p class="filter-panel__title">{{ t('pages.marketingFlow.dataScopeTitle') }}</p>
          <div class="mkt-out-filter__actions">
            <el-tooltip :content="t('pages.marketingFlow.outstandingRefresh')" placement="top">
              <el-button
                type="primary"
                :icon="Refresh"
                :loading="outstandingLoading"
                circle
                @click="loadOutstanding"
              />
            </el-tooltip>
            <el-tooltip :content="t('common.reset')" placement="top">
              <el-button :icon="RefreshLeft" circle @click="resetOutstandingFilters" />
            </el-tooltip>
          </div>
        </div>

        <div class="mkt-out-filter">
          <div class="mkt-out-filter__fields">
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
              <span class="mkt-out-field__label">{{ t('pages.marketingFlow.filterFactoryCode') }}</span>
              <el-select
                v-model="factoryCode"
                clearable
                filterable
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
                @change="loadOutstanding"
              >
                <el-radio-button label="">{{ t('pages.marketingFlow.outstandingSheetAll') }}</el-radio-button>
                <el-radio-button label="production">{{ t('pages.marketingFlow.outstandingSheetProd') }}</el-radio-button>
                <el-radio-button label="claim">{{ t('pages.marketingFlow.outstandingSheetClaim') }}</el-radio-button>
                <el-radio-button label="sample">{{ t('pages.marketingFlow.outstandingSheetSample') }}</el-radio-button>
                <el-radio-button label="subcont">{{ t('pages.marketingFlow.outstandingSheetSubcont') }}</el-radio-button>
                <el-radio-button label="return">{{ t('pages.marketingFlow.outstandingSheetReturn') }}</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </div>
      </div>

      <p class="mkt-out-col-filter-tip">
        {{ t('pages.marketingFlow.colFilterTip') }}
      </p>

      <div class="admin-table-scroll mkt-out-table-wrap">
      <el-table
        ref="outstandingTableRef"
        :key="outstandingTableKey"
        :data="outstandingDisplayRows"
        v-loading="outstandingLoading"
        border
        size="small"
        class="outstanding-table marketing-outstanding-table outstanding-table--col-filters"
        :row-class-name="outstandingRowClassName"
        @selection-change="onOutstandingSelectionChange"
      >
        <el-table-column type="selection" width="42" fixed="left" />
        <el-table-column
          v-for="col in outstandingTableColumnDefs"
          :key="col.prop"
          :prop="col.prop"
          :width="col.width"
          :min-width="col.minWidth"
          :fixed="col.fixed"
          :align="col.align || 'left'"
          :class-name="col.prop === 'thi_order' ? 'out-col-thi-order' : undefined"
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
            <el-date-picker
              v-else-if="isOutstandingDeliveryDateCol(col.prop) && isOutstandingRowEditing(row)"
              v-model="row[col.prop]"
              type="date"
              value-format="YYYY-MM-DD"
              size="small"
              class="mkt-out-date-edit"
              :disabled="!canEditPoDetail"
              :placeholder="t('pages.marketingFlow.scheduleDeliveryDate')"
            />
            <span v-else-if="col.kind === 'date'">{{ formatOutstandingDate(row[col.prop]) }}</span>
            <span v-else>{{ formatOutstandingCell(row[col.prop]) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="canEditPoDetail"
          :label="t('common.actions')"
          width="132"
          align="center"
          fixed="right"
        >
          <template #default="{ row }">
            <div class="mkt-out-row-actions">
              <template v-if="isOutstandingRowEditing(row)">
                <el-tooltip :content="t('common.save')" placement="top">
                  <el-button
                    link
                    type="primary"
                    :icon="Check"
                    :loading="savingOutstandingId === row.po_detail_id"
                    :aria-label="t('common.save')"
                    @click="saveOutstandingRowEdit(row)"
                  />
                </el-tooltip>
                <el-tooltip :content="t('common.cancel')" placement="top">
                  <el-button
                    link
                    :icon="Close"
                    :disabled="savingOutstandingId === row.po_detail_id"
                    :aria-label="t('common.cancel')"
                    @click="cancelOutstandingRowEdit(row)"
                  />
                </el-tooltip>
              </template>
              <el-tooltip v-else :content="t('pages.marketingFlow.outstandingEditRow')" placement="top">
                <el-button
                  link
                  type="primary"
                  :icon="EditPen"
                  :aria-label="t('pages.marketingFlow.outstandingEditRow')"
                  @click="startOutstandingRowEdit(row)"
                />
              </el-tooltip>
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
      <el-tabs v-model="masterPlanningTab" class="mkt-plan-tabs" @tab-change="onMasterPlanningTabChange">
        <el-tab-pane name="planning" :label="t('pages.marketingFlow.planningTitle')">
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
                      @change="loadPlanning"
                    />
                  </label>
                  <label class="mkt-out-field">
                    <span class="mkt-out-field__label">{{ t('pages.marketingFlow.factoryFilterOptional') }}</span>
                    <el-input
                      v-model="planningFactory"
                      clearable
                      class="mkt-out-field__control"
                    />
                  </label>
                </div>
                <div class="mkt-plan-filter__footer">
                  <div class="mkt-plan-stat-chips">
                    <span class="mkt-plan-stat-chip">
                      {{ t('common.total') }}: <strong>{{ planningRows.length }}</strong>
                    </span>
                  </div>
                  <div class="mkt-plan-filter__actions">
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
                  :data="planningRows"
                  border
                  stripe
                  size="small"
                  class="admin-table mkt-plan-table"
                  max-height="420"
                  v-loading="planningLoading"
                  :empty-text="t('pages.marketingFlow.planningEmpty')"
                >
                  <el-table-column prop="delivery_date" :label="t('pages.marketingFlow.colShipDate')" width="110" />
                  <el-table-column prop="sequence_no" label="#" width="44" align="center" />
                  <el-table-column prop="po_number" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
                  <el-table-column prop="factory_code" label="Factory" width="88" show-overflow-tooltip />
                  <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
                  <el-table-column prop="lot_no" :label="t('common.lotNo')" min-width="140" show-overflow-tooltip />
                  <el-table-column prop="qty" :label="t('pages.marketingFlow.colQtyShip')" width="88" />
                  <el-table-column prop="line_etd" :label="t('pages.po.lineEtd')" width="110" />
                </el-table>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane name="today" :label="t('pages.marketingFlow.deliveryTodayTitle')">
          <div class="mkt-plan-pane">
            <div class="filter-panel mkt-plan-filter-panel">
              <p class="filter-panel__title">{{ t('common.filter') }}</p>
              <div class="mkt-plan-filter">
                <div class="mkt-plan-filter__fields">
                  <label class="mkt-out-field">
                    <span class="mkt-out-field__label">{{ t('pages.marketingFlow.todayAsOfDate') }}</span>
                    <el-date-picker
                      v-model="todayOnDate"
                      type="date"
                      value-format="YYYY-MM-DD"
                      class="mkt-out-field__control"
                      :shortcuts="todayDateShortcuts"
                      @change="loadDeliveryToday"
                    />
                  </label>
                  <label class="mkt-out-field">
                    <span class="mkt-out-field__label">{{ t('pages.marketingFlow.factoryFilterOptional') }}</span>
                    <el-input
                      v-model="todayFactory"
                      clearable
                      class="mkt-out-field__control"
                    />
                  </label>
                </div>
                <div class="mkt-plan-filter__footer">
                  <div class="mkt-plan-stat-chips">
                    <span class="mkt-plan-stat-chip">
                      {{ t('pages.marketingFlow.deliveryTodayPlanned') }}: <strong>{{ todayPlanned.length }}</strong>
                    </span>
                    <span class="mkt-plan-stat-chip">
                      {{ t('pages.marketingFlow.deliveryTodayEtd') }}: <strong>{{ todayEtd.length }}</strong>
                    </span>
                    <span class="mkt-plan-stat-chip">
                      {{ t('pages.marketingFlow.deliveryTodaySj') }}: <strong>{{ todaySj.length }}</strong>
                    </span>
                  </div>
                  <div class="mkt-plan-filter__actions">
                    <el-button type="primary" :icon="Refresh" :loading="todayLoading" @click="loadDeliveryToday">
                      {{ t('common.refresh') }}
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <div v-loading="todayLoading" class="mkt-plan-today">
              <section class="mkt-plan-block">
                <div class="mkt-plan-block__head">
                  <h4 class="mkt-plan-block__title">{{ t('pages.marketingFlow.deliveryTodayPlanned') }}</h4>
                  <span class="mkt-plan-block__count">{{ todayPlanned.length }}</span>
                </div>
                <div class="admin-table-scroll">
                  <el-table
                    :data="todayPlanned"
                    border
                    stripe
                    size="small"
                    class="admin-table mkt-plan-table"
                    max-height="240"
                    :empty-text="t('common.tableEmpty')"
                  >
                    <el-table-column prop="delivery_date" :label="t('pages.marketingFlow.colShipDate')" width="110" />
                    <el-table-column prop="po_number" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
                    <el-table-column prop="material_name" :label="t('common.material')" min-width="120" show-overflow-tooltip />
                    <el-table-column prop="qty" :label="t('pages.marketingFlow.colQtyShip')" width="80" />
                  </el-table>
                </div>
              </section>

              <section class="mkt-plan-block">
                <div class="mkt-plan-block__head">
                  <h4 class="mkt-plan-block__title">{{ t('pages.marketingFlow.deliveryTodayEtd') }}</h4>
                  <span class="mkt-plan-block__count">{{ todayEtd.length }}</span>
                </div>
                <div class="admin-table-scroll">
                  <el-table
                    :data="todayEtd"
                    border
                    stripe
                    size="small"
                    class="admin-table mkt-plan-table"
                    max-height="200"
                    :empty-text="t('common.tableEmpty')"
                  >
                    <el-table-column prop="line_etd" :label="t('pages.po.lineEtd')" width="110" />
                    <el-table-column prop="po_number" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
                    <el-table-column prop="customer_name" :label="t('common.customerName')" min-width="120" show-overflow-tooltip />
                    <el-table-column prop="material_name" :label="t('common.material')" min-width="120" show-overflow-tooltip />
                  </el-table>
                </div>
              </section>

              <section class="mkt-plan-block">
                <div class="mkt-plan-block__head">
                  <h4 class="mkt-plan-block__title">{{ t('pages.marketingFlow.deliveryTodaySj') }}</h4>
                  <span class="mkt-plan-block__count">{{ todaySj.length }}</span>
                </div>
                <div class="admin-table-scroll">
                  <el-table
                    :data="todaySj"
                    border
                    stripe
                    size="small"
                    class="admin-table mkt-plan-table"
                    max-height="260"
                    :empty-text="t('common.tableEmpty')"
                  >
                    <el-table-column prop="surat_jalan_no" :label="t('pages.marketingFlow.colSuratJalan')" min-width="120" show-overflow-tooltip />
                    <el-table-column prop="delivery_date" :label="t('pages.marketingFlow.colShipDate')" width="110" />
                    <el-table-column prop="po_number" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
                    <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
                  </el-table>
                </div>
              </section>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane name="master" :label="t('pages.marketingFlow.snapshotListTitle')">
          <div class="mkt-plan-pane">
            <div class="filter-panel mkt-plan-filter-panel">
              <p class="filter-panel__title">{{ t('common.filter') }}</p>
              <div class="mkt-plan-filter">
                <div class="mkt-plan-filter__fields">
                  <label class="mkt-out-field mkt-out-field--span2">
                    <span class="mkt-out-field__label">{{ t('common.remark') }}</span>
                    <el-input
                      v-model="snapshotLabel"
                      clearable
                      class="mkt-out-field__control"
                      :placeholder="t('pages.marketingFlow.snapshotLabelPlaceholder')"
                    />
                  </label>
                </div>
                <div class="mkt-plan-filter__footer">
                  <div class="mkt-plan-stat-chips">
                    <span class="mkt-plan-stat-chip">
                      {{ t('common.total') }}: <strong>{{ snapshots.length }}</strong>
                    </span>
                  </div>
                  <div class="mkt-plan-filter__actions">
                    <el-button type="success" :loading="snapshotSaving" @click="saveOutstandingSnapshot">
                      {{ t('pages.marketingFlow.snapshotSave') }}
                    </el-button>
                    <el-button type="primary" :icon="Refresh" :loading="snapshotsLoading" @click="loadSnapshotList">
                      {{ t('common.refresh') }}
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <div class="mkt-plan-block">
              <div class="admin-table-scroll">
                <el-table
                  :data="snapshots"
                  border
                  stripe
                  size="small"
                  class="admin-table mkt-plan-table"
                  v-loading="snapshotsLoading"
                  max-height="420"
                  :empty-text="t('common.tableEmpty')"
                >
                  <el-table-column prop="id" label="ID" width="64" align="center" />
                  <el-table-column prop="created_at" :label="t('common.date')" width="168" />
                  <el-table-column prop="label" :label="t('common.remark')" min-width="120" show-overflow-tooltip />
                  <el-table-column prop="row_count" :label="t('pages.marketingFlow.rowCountLabel')" width="100" align="right" />
                  <el-table-column :label="t('common.actions')" width="100" align="center" fixed="right">
                    <template #default="{ row }">
                      <el-button type="primary" link size="small" @click="openSnapshotDetail(row.id)">
                        {{ t('pages.marketingFlow.snapshotView') }}
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane name="delivery" :label="t('pages.marketingFlow.tabDelivery')">
          <div class="mkt-plan-pane">
            <div class="filter-panel mkt-plan-filter-panel">
              <p class="filter-panel__title">{{ t('common.filter') }}</p>
              <div class="mkt-plan-filter">
                <div class="mkt-plan-filter__fields">
                  <label class="mkt-out-field mkt-out-field--span2">
                    <span class="mkt-out-field__label">{{ t('pages.marketingFlow.deliveryShipDateRange') }}</span>
                    <el-date-picker
                      v-model="deliveryDateRange"
                      type="daterange"
                      unlink-panels
                      value-format="YYYY-MM-DD"
                      class="mkt-out-field__control"
                      range-separator="—"
                      :shortcuts="orderDateRangeShortcuts"
                      clearable
                      :start-placeholder="t('common.placeholder.fromDate')"
                      :end-placeholder="t('common.placeholder.toDate')"
                      @change="loadDelivery"
                    />
                  </label>
                </div>
                <div class="mkt-plan-filter__footer">
                  <div class="mkt-plan-stat-chips">
                    <span class="mkt-plan-stat-chip">
                      {{ t('common.total') }}: <strong>{{ deliveryRows.length }}</strong>
                    </span>
                  </div>
                  <div class="mkt-plan-filter__actions">
                    <el-button type="primary" :icon="Refresh" :loading="deliveryLoading" @click="loadDelivery">
                      {{ t('common.refresh') }}
                    </el-button>
                    <el-button :icon="Download" @click="downloadDelivery">
                      {{ t('pages.marketingFlow.deliveryDownloadCsv') }}
                    </el-button>
                    <el-button :icon="Download" @click="downloadDeliveryXlsx">
                      {{ t('pages.marketingFlow.deliveryDownloadXlsx') }}
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <div class="mkt-plan-block">
              <div class="admin-table-scroll">
                <el-table
                  :data="deliveryRows"
                  v-loading="deliveryLoading"
                  border
                  stripe
                  size="small"
                  class="admin-table mkt-plan-table"
                  max-height="420"
                  :empty-text="t('pages.marketingFlow.deliveryEmpty')"
                >
                  <el-table-column prop="surat_jalan_no" :label="t('pages.marketingFlow.colSuratJalan')" min-width="120" show-overflow-tooltip />
                  <el-table-column prop="delivery_date" :label="t('pages.marketingFlow.colShipDate')" width="110" />
                  <el-table-column prop="factory_name" :label="t('pages.marketingFlow.colFactoryName')" min-width="140" show-overflow-tooltip />
                  <el-table-column prop="system_no" :label="t('pages.marketingFlow.colSystemNo')" min-width="120" show-overflow-tooltip />
                  <el-table-column prop="po_number" :label="t('pages.marketingFlow.colPoCustomerRef')" min-width="120" show-overflow-tooltip />
                  <el-table-column prop="lot_no" :label="t('pages.marketingFlow.colLotNo')" min-width="130" show-overflow-tooltip />
                  <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
                  <el-table-column prop="qty_sf" :label="t('pages.marketingFlow.colQtyShip')" width="90" />
                  <el-table-column prop="gross_weight" :label="t('pages.marketingFlow.colGrossWeight')" width="72" />
                  <el-table-column prop="net_weight" :label="t('pages.marketingFlow.colNetWeight')" width="72" />
                  <el-table-column prop="amount" :label="t('pages.marketingFlow.colAmount')" width="96" />
                  <el-table-column :label="t('common.actions')" width="100" align="center" fixed="right">
                    <template #default="{ row }">
                      <el-button link type="primary" size="small" @click="goDelivery(row)">
                        {{ t('pages.marketingFlow.openDelivery') }}
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      </div>
    </div>

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

    <el-dialog v-model="assignDialogVisible" :title="t('ppicWorkflow.assignToPpic')" width="600px" destroy-on-close align-center>
      <el-alert
        class="mb-3"
        type="info"
        :closable="false"
        show-icon
        :title="t('ppicWorkflow.assignPrerequisite')"
      />
      <el-form label-width="120px">
        <el-form-item :label="t('common.poNo')">
          <el-input :model-value="selectedPoForAssignment?.po_number" disabled />
        </el-form-item>
        <el-form-item :label="t('ppicWorkflow.ppicUser')" required>
          <el-select v-model="assignForm.ppic_user_id" class="w-full" clearable :placeholder="t('ppicWorkflow.ppicUser')">
            <el-option v-for="u in ppicUsers" :key="u.id" :label="u.username" :value="u.id" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('ppicWorkflow.notes')">
          <el-input v-model="assignForm.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button :icon="Close" @click="assignDialogVisible = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :icon="Check" :loading="assigning" @click="submitAssignment">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="materialFollowUpDialogVisible" :title="t('pages.marketingFlow.materialFollowUp')" width="500px" destroy-on-close align-center>
      <el-form label-position="top">
        <el-form-item :label="t('common.poNo')">
          <el-input :model-value="selectedPoForMaterialFollowUp?.po_number" disabled />
        </el-form-item>
        <el-form-item :label="t('pages.marketingFlow.materialDone')">
          <el-switch v-model="materialFollowUpForm.done" />
        </el-form-item>
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
import { DArrowLeft, DArrowRight, Document, Download, Printer, User, Close, Check, Warning, CircleCheck, Refresh, RefreshLeft, ArrowDown, EditPen } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import OutstandingColFilterHeader from '../../components/admin/OutstandingColFilterHeader.vue'
import OutstandingWorkbenchDialogs from '../../components/admin/OutstandingWorkbenchDialogs.vue'
import PoItemRevisedDot from '../../components/admin/PoItemRevisedDot.vue'
import PoRekapPrintDialog from '../../components/admin/PoRekapPrintDialog.vue'
import {
  advanceMktWorkflow,
  rollbackMktWorkflow,
  assignPoToPpic,
  createMarketingOutstandingSnapshot,
  fetchAuthenticatedDocument,
  getMarketingDeliveryToday,
  getMarketingOutstandingSnapshot,
  getPpicDashboard,
  listMarketingDeliveryLines,
  listMarketingDeliveryPlanning,
  listMarketingOutstandingLines,
  listMarketingOutstandingSnapshots,
  listPoMktStages,
  listPoPage,
  listPpicUsers,
  marketingDeliveryCsvUrl,
  marketingDeliveryXlsxPath,
  marketingOutstandingCsvUrl,
  marketingOutstandingReturnXlsxPath,
  marketingOutstandingManualXlsxPath,
  marketingOutstandingXlsxPath,
  reportPoDailyMarketingXlsxPath,
  setPoDetailDeliverySchedules,
  updatePo,
  updatePoDetail,
} from '../../api/client'
import { can } from '../../security/permissions'
import { useModulePermission } from '../../composables/useModulePermission'
import { stuckReasonLabel as translateStuckReason } from '../../utils/mktStuckReason.js'
import { formatDate } from '../../utils/format.js'

const OUTSTANDING_LINES_LIMIT = 1000
const outstandingPage = ref(1)
const outstandingPageSize = ref(100)
const outstandingTotal = ref(0)

const { t } = useI18n()
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

const todayDateShortcuts = computed(() => [
  {
    text: t('pages.marketingFlow.shortcutToday'),
    value: () => new Date(),
  },
  {
    text: t('pages.marketingFlow.shortcutYesterday'),
    value: () => {
      const d = new Date()
      d.setDate(d.getDate() - 1)
      return d
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
const factoryCode = ref('')
const outstandingFactoryOptions = ref([])
const outstandingPoCategory = ref('')
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
  () => `out-${outstandingPoCategory.value || 'all'}-${outstandingDeliverySlotCount.value}`,
)

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

const ppicUsers = ref([])
const ppicAssignments = ref({})
const assignDialogVisible = ref(false)
const assignForm = ref({ ppic_user_id: null, notes: '' })
const selectedPoForAssignment = ref(null)
const assigning = ref(false)

const materialFollowUpDialogVisible = ref(false)
const materialFollowUpForm = reactive({ done: false, remark: '' })
const selectedPoForMaterialFollowUp = ref(null)
const savingMaterialFollowUp = ref(false)

function outstandingOrdinalLabel(n) {
  if (n === 1) return '1st'
  if (n === 2) return '2nd'
  if (n === 3) return '3rd'
  return `${n}th`
}

function buildOutstandingDeliveryColumnDefs(maxDeliverySlots) {
  const d = []
  for (let i = 1; i <= maxDeliverySlots; i += 1) {
    const lab = outstandingOrdinalLabel(i)
    d.push(
      { prop: `delivery_${i}_qty`, label: `${lab} Qty`, width: 88, align: 'right', kind: 'text' },
      { prop: `delivery_${i}_date`, label: `${lab} Date`, width: 112, kind: 'date' },
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

/** Kolom tabel selaras Excel manual PROD / CLAIM / SAMPLE / SUBCONT. */
const outstandingTableColumnDefs = computed(() => {
  const cat = outstandingPoCategory.value
  const usePoCust = ['claim', 'sample', 'subcont', 'return'].includes(cat)
  const poCol = usePoCust
    ? { prop: 'po_customer_ref', label: 'PO CUST', minWidth: 140, kind: 'text' }
    : { prop: 'no_po', label: 'NO PO', minWidth: 140, kind: 'text' }

  const cols = [
    { prop: 'order_date', label: 'DATE', width: 120, fixed: 'left', kind: 'date' },
    { prop: 'thi_order', label: 'THI ORDER', width: 140, fixed: 'left', kind: 'text' },
    { prop: 'customer_name', label: 'CUSTOMER NAME', minWidth: 180, kind: 'text' },
    { prop: 'brand', label: 'BRAND', minWidth: 110, kind: 'text' },
    { prop: 'order_type', label: 'ORDER TYPE', width: 110, kind: 'text' },
    poCol,
    { prop: 'material_name', label: 'MATERIAL NAME', minWidth: 160, kind: 'text' },
    { prop: 'thickness', label: 'THICKNESS', width: 92, kind: 'text' },
    { prop: 'emboss', label: 'EMBOSS', width: 80, kind: 'text' },
    { prop: 'softness_type', label: 'SOFTNESS TYPE', minWidth: 168, kind: 'text' },
    { prop: 'color', label: 'COLOR', width: 90, kind: 'text' },
    { prop: 'softness', label: 'SOFTNESS', width: 90, kind: 'text' },
    { prop: 'qty_sf', label: 'QTY (S/F)', width: 100, align: 'right', kind: 'text' },
    { prop: 'unit_price', label: 'PRICE', width: 88, align: 'right', kind: 'text' },
    { prop: 'color_reference', label: 'COLOR S/W', minWidth: 110, kind: 'text' },
    { prop: 'color_standard', label: 'COLOR STD', minWidth: 100, kind: 'text' },
    { prop: 'backing', label: 'BACKING', width: 90, kind: 'text' },
    { prop: 'model', label: 'MODEL', width: 90, kind: 'text' },
    { prop: 'style_article', label: 'ARTICLE', minWidth: 100, kind: 'text' },
    { prop: 'rtd_text', label: 'RTA', width: 96, kind: 'text' },
    { prop: 'line_etd', label: 'REPLY ETD', width: 110, kind: 'date' },
    { prop: 'stock_wh_qty', label: 'STOCK WH', width: 96, align: 'right', kind: 'text' },
    { prop: 'balance_qty', label: 'BALANCE', width: 100, align: 'right', kind: 'text' },
    { prop: 'system_reference', label: 'SYSTEM NO', minWidth: 140, kind: 'text' },
    { prop: 'detail_remark', label: 'REMARK PO', minWidth: 140, kind: 'text' },
    { prop: 'remark_marketing', label: 'REMARK', minWidth: 200, kind: 'remark_marketing' },
  ]
  if (outstandingShowStatusMaterial.value) {
    cols.push({
      prop: 'status_material',
      label: 'STATUS MATERIAL',
      minWidth: 160,
      kind: 'text',
    })
  }
  cols.push(...buildOutstandingDeliveryColumnDefs(outstandingDeliverySlotCount.value))
  return cols
})

const OUTSTANDING_TEXT_FILTER_KEYS = computed(() => {
  const keys = outstandingTableColumnDefs.value.map((c) => c.prop)
  // Pastikan reactive filter punya key untuk semua slot max (21)
  for (let i = 1; i <= 21; i += 1) {
    keys.push(`delivery_${i}_qty`, `delivery_${i}_date`)
  }
  return [...new Set(keys)]
})

const outstandingTextFilters = reactive({})

function ensureOutstandingTextFilterKeys() {
  for (const key of OUTSTANDING_TEXT_FILTER_KEYS.value) {
    if (!(key in outstandingTextFilters)) outstandingTextFilters[key] = ''
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
      let v = r?.[key]
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

function outstandingRowTextMatches(row, key, needle) {
  if (!needle || !String(needle).trim()) return true
  const q = String(needle).trim().toLowerCase()
  let cell = String(row[key] ?? '')
  if (/^\d{4}-\d{2}-\d{2}/.test(cell.trim())) {
    cell = formatOutstandingDate(cell)
  }
  const cellLc = cell.toLowerCase()
  return cellLc === q || cellLc.includes(q)
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
    factory_code: factoryCode.value || undefined,
    po_category: outstandingPoCategory.value || undefined,
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
  for (const [key, needle] of Object.entries(outstandingTextFilters)) {
    if (!needle || !String(needle).trim()) continue
    list = list.filter((r) => outstandingRowTextMatches(r, key, needle))
  }
  // Kelompokkan visual: THI ORDER sama berdekatan
  return [...list].sort((a, b) => {
    const ta = String(a?.thi_order || '')
    const tb = String(b?.thi_order || '')
    if (ta !== tb) return ta.localeCompare(tb, undefined, { numeric: true, sensitivity: 'base' })
    const da = String(a?.order_date || '')
    const db = String(b?.order_date || '')
    if (da !== db) return da.localeCompare(db)
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
    outstandingTextFilters[key] = ''
  }
}

function onOutstandingSelectionChange(sel) {
  outstandingSelection.value = sel
}

function isOutstandingDeliveryDateCol(prop) {
  return /^delivery_\d+_date$/.test(String(prop || ''))
}

function isOutstandingRowEditing(row) {
  return Boolean(row?.po_detail_id) && editingOutstandingId.value === row.po_detail_id
}

function snapshotOutstandingEdit(row) {
  const snap = { remark_marketing: row.remark_marketing || '' }
  for (let i = 1; i <= 21; i += 1) {
    snap[`delivery_${i}_date`] = row[`delivery_${i}_date`] || ''
  }
  return snap
}

function restoreOutstandingEdit(row, snap) {
  if (!row || !snap) return
  row.remark_marketing = snap.remark_marketing
  for (let i = 1; i <= 21; i += 1) {
    row[`delivery_${i}_date`] = snap[`delivery_${i}_date`] || ''
  }
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

function schedulesFromOutstandingRow(row) {
  const slotCount = outstandingDeliverySlotCount.value
  const schedules = []
  for (let i = 1; i <= slotCount; i += 1) {
    const qtyRaw = row[`delivery_${i}_qty`]
    const dateRaw = row[`delivery_${i}_date`]
    const qtyNum = qtyRaw !== '' && qtyRaw != null && Number.isFinite(Number(qtyRaw)) ? Number(qtyRaw) : null
    const delivery_date = dateRaw ? String(dateRaw).slice(0, 10) : null
    if (qtyNum == null && !delivery_date) continue
    schedules.push({
      sequence_no: i,
      qty: qtyNum,
      delivery_date,
    })
  }
  return schedules
}

async function saveOutstandingRowEdit(row) {
  if (!canEditPoDetail || !row?.po_detail_id) return
  savingOutstandingId.value = row.po_detail_id
  try {
    await updatePoDetail(row.po_detail_id, {
      marketing_outstanding_remark: String(row.remark_marketing || '').trim() || null,
    })
    const datesChanged =
      !outstandingEditSnapshot.value ||
      Array.from({ length: 21 }, (_, i) => i + 1).some((i) => {
        const a = String(row[`delivery_${i}_date`] || '').slice(0, 10)
        const b = String(outstandingEditSnapshot.value[`delivery_${i}_date`] || '').slice(0, 10)
        return a !== b
      })
    if (datesChanged) {
      await setPoDetailDeliverySchedules(row.po_detail_id, schedulesFromOutstandingRow(row))
    }
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

const deliveryRows = ref([])
const deliveryLoading = ref(false)

const masterPlanningTab = ref('planning')
function planningDefaultRange() {
  const e = new Date()
  const s = new Date()
  s.setDate(s.getDate() - 7)
  return [isoDateLocal(s), isoDateLocal(e)]
}
const planningDateRange = ref(planningDefaultRange())
const planningFactory = ref('')
const planningRows = ref([])
const planningLoading = ref(false)

const todayOnDate = ref(isoDateLocal(new Date()))
const deliveryDateRange = ref(null)

const todayFactory = ref('')
const todayLoading = ref(false)
const todayPlanned = ref([])
const todayEtd = ref([])
const todaySj = ref([])

const snapshots = ref([])
const snapshotsLoading = ref(false)
const snapshotLabel = ref('')
const snapshotSaving = ref(false)
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
  stuck: rows.value.filter((row) => Boolean(row.stuck_reason)).length,
  ready: rows.value.filter((row) => isStageComplete(row)).length,
}))

function isStageComplete(row) {
  const s = row.mkt_workflow_stage
  if (!s) return false
  const idx = stageList.value.indexOf(s)
  return idx >= 0 && idx < stageList.value.length - 1 && canAdvanceRow(row)
}

function needsRekapPrintConfirm(row) {
  const nxt = nextFlowStage(row?.mkt_workflow_stage)
  return nxt === 'rekap_printed' && !row?.rekap_printed_at
}

function canAdvanceRow(row) {
  if (!row) return false
  if (row.stuck_reason) return false
  if (needsRekapPrintConfirm(row)) return false
  const s = row.mkt_workflow_stage
  const idx = stageList.value.indexOf(normalizeFlowStage(s))
  return idx >= 0 && idx < stageList.value.length - 1
}

function advanceTooltip(row) {
  if (needsRekapPrintConfirm(row) || row?.stuck_reason === 'Menunggu rekap PO diprint') {
    return t('pages.marketingFlow.advanceBlockedNeedRekapPrint')
  }
  if (row?.stuck_reason) return stuckReasonLabel(row.stuck_reason)
  return t('pages.marketingFlow.advanceStageHint')
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
    outstandingRows.value = unwrapOutstandingLines(resp)
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
  if (!(factoryCode.value || '').trim()) {
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

function onOutstandingPageSizeChange() {
  outstandingPage.value = 1
  loadOutstanding()
}

function resetOutstandingFilters() {
  outstandingDateRange.value = null
  outstandingPoCategory.value = ''
  balanceFilter.value = 'exclude_zero'
  poSearch.value = ''
  factoryCode.value = ''
  materialStatus.value = ''
  outstandingPage.value = 1
  clearOutstandingColFilters()
  loadOutstanding()
}

function openOutstandingSchedule() {
  if (!outstandingSelection.value.length) {
    ElMessage.warning(t('pages.marketingFlow.selectRowsFirst'))
    return
  }
  outstandingScheduleVisible.value = true
}

function openOutstandingPi() {
  if (!outstandingSelection.value.length) {
    ElMessage.warning(t('pages.marketingFlow.selectRowsFirst'))
    return
  }
  outstandingPiVisible.value = true
}

function openOutstandingShip() {
  if (!outstandingSelection.value.length) {
    ElMessage.warning(t('pages.marketingFlow.selectRowsFirst'))
    return
  }
  outstandingShipVisible.value = true
}

function resetFlowFilters() {
  flowDateRange.value = null
  flowKeyword.value = ''
  filterStage.value = null
  flowPage.value = 1
  load()
}

async function loadDelivery() {
  deliveryLoading.value = true
  try {
    const dr = deliveryDateRange.value
    const drParams =
      Array.isArray(dr) && dr.length === 2 && dr[0] && dr[1]
        ? { delivery_date_from: dr[0], delivery_date_to: dr[1] }
        : {}
    const linesResp = await listMarketingDeliveryLines({ limit: 500, ...drParams })
    const lines = Array.isArray(linesResp) ? linesResp : (linesResp?.data || [])
    deliveryRows.value = lines.map((r) => ({
      ...r,
      delivery_date: r.delivery_date ? String(r.delivery_date).slice(0, 10) : '',
      po_date: r.po_date ? String(r.po_date).slice(0, 10) : '',
    }))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    deliveryLoading.value = false
  }
}

function onMasterPlanningTabChange(name) {
  if (name === 'planning') loadPlanning()
  else if (name === 'delivery') loadDelivery()
  else if (name === 'today') loadDeliveryToday()
  else if (name === 'master') loadSnapshotList()
}

async function loadPlanning() {
  planningLoading.value = true
  try {
    const rge = planningDateRange.value
    const df = Array.isArray(rge) && rge[0] ? rge[0] : isoDateLocal(new Date())
    const dt = Array.isArray(rge) && rge[1] ? rge[1] : df
    const r = await listMarketingDeliveryPlanning({
      date_from: df,
      date_to: dt,
      factory_code: planningFactory.value?.trim() || undefined,
    })
    planningRows.value = Array.isArray(r?.data) ? r.data : []
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    planningRows.value = []
  } finally {
    planningLoading.value = false
  }
}

async function loadDeliveryToday() {
  todayLoading.value = true
  try {
    const r = await getMarketingDeliveryToday({
      on_date: todayOnDate.value || undefined,
      factory_code: todayFactory.value?.trim() || undefined,
    })
    todayPlanned.value = Array.isArray(r?.planned_delivery_slots) ? r.planned_delivery_slots : []
    todayEtd.value = Array.isArray(r?.lines_reply_etd_today) ? r.lines_reply_etd_today : []
    todaySj.value = Array.isArray(r?.surat_jalan_lines) ? r.surat_jalan_lines : []
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
    todayPlanned.value = []
    todayEtd.value = []
    todaySj.value = []
  } finally {
    todayLoading.value = false
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
        factory_code: factoryCode.value?.trim() || null,
        po_category: outstandingPoCategory.value?.trim() || null,
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
  if (section.value === 'flow') {
    try {
      const data = await listPoMktStages()
      stageList.value = data.stages || []
    } catch {
      stageList.value = []
    }
    await Promise.all([
      load(),
      loadPpicUsers(),
      loadAssignments(),
    ])
    flowWatchReady = true
    return
  }
  if (section.value === 'outstanding') {
    await loadOutstanding()
    return
  }
  const tab = masterPlanningTab.value
  if (tab === 'planning') await loadPlanning()
  else if (tab === 'delivery') await loadDelivery()
  else if (tab === 'today') await loadDeliveryToday()
  else await loadSnapshotList()
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

async function loadPpicUsers() {
  try {
    ppicUsers.value = await listPpicUsers()
  } catch {
    ppicUsers.value = []
  }
}

async function loadAssignments() {
  try {
    const data = await getPpicDashboard()
    const map = {}
    for (const a of data) {
      map[a.po_id] = a
    }
    ppicAssignments.value = map
  } catch {
    ppicAssignments.value = {}
  }
}

function openAssignDialog(row) {
  selectedPoForAssignment.value = row
  assignForm.value = { ppic_user_id: null, notes: '' }
  assignDialogVisible.value = true
}

async function submitAssignment() {
  if (!assignForm.value.ppic_user_id) {
    ElMessage.warning(t('common.fillRequired'))
    return
  }
  assigning.value = true
  try {
    await assignPoToPpic(selectedPoForAssignment.value.id, {
      po_id: selectedPoForAssignment.value.id,
      ppic_user_id: assignForm.value.ppic_user_id,
      notes: assignForm.value.notes || null,
    })
    ElMessage.success(t('common.saveSuccess'))
    assignDialogVisible.value = false
    await Promise.all([load(), loadAssignments()])
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    assigning.value = false
  }
}

function ppicStatusLabel(status) {
  const labels = {
    pending: t('ppicWorkflow.pending'),
    in_progress: t('ppicWorkflow.inProgress'),
    completed: t('ppicWorkflow.completed'),
  }
  return labels[status] || status || '—'
}

function stuckReasonLabel(reason) {
  return translateStuckReason(reason, t)
}

function openMaterialFollowUpDialog(row) {
  selectedPoForMaterialFollowUp.value = row
  materialFollowUpForm.done = Boolean(row.material_followup_done)
  materialFollowUpForm.remark = row.material_followup_remark || ''
  materialFollowUpDialogVisible.value = true
}

async function toggleMaterialFollowUp(row, done) {
  try {
    await updatePo(row.id, {
      material_followup_done: done,
      material_followup_remark: row.material_followup_remark || undefined,
    })
    row.material_followup_done = done
    ElMessage.success(t('common.saveSuccess'))
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function saveMaterialFollowUp() {
  savingMaterialFollowUp.value = true
  try {
    await updatePo(selectedPoForMaterialFollowUp.value.id, {
      material_followup_done: materialFollowUpForm.done,
      material_followup_remark: materialFollowUpForm.remark.trim() || null,
    })
    selectedPoForMaterialFollowUp.value.material_followup_done = materialFollowUpForm.done
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

function goDelivery(row) {
  const q = {}
  if (row.delivery_id != null && row.delivery_id !== '') q.delivery_id = String(row.delivery_id)
  const sjRaw = row.surat_jalan_no && row.surat_jalan_no !== t('common.emptyValue') ? String(row.surat_jalan_no).trim() : ''
  if (sjRaw && sjRaw !== '—') q.keyword = sjRaw
  if (row.delivery_date) {
    const d = String(row.delivery_date).slice(0, 10)
    q.delivery_date_from = d
    q.delivery_date_to = d
  }
  if (row.po_number && String(row.po_number).trim()) q.po_number = String(row.po_number).trim()
  const fc = row.factory_code != null ? String(row.factory_code).trim() : ''
  if (fc) q.factory_code = fc
  router.push({ path: '/admin/delivery', query: q })
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
  ElMessage.success(t('pages.marketingFlow.pullCrTodayDone'))
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

async function downloadDelivery() {
  const dr = deliveryDateRange.value
  const drParams =
    Array.isArray(dr) && dr.length === 2 && dr[0] && dr[1]
      ? { delivery_date_from: dr[0], delivery_date_to: dr[1] }
      : {}
  const suffix = marketingDeliveryCsvUrl(drParams)
  try {
    await fetchAuthenticatedDocument(suffix, { mode: 'download', downloadFallbackName: 'marketing-delivery.csv' })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadDeliveryXlsx() {
  const dr = deliveryDateRange.value
  const drParams =
    Array.isArray(dr) && dr.length === 2 && dr[0] && dr[1]
      ? { delivery_date_from: dr[0], delivery_date_to: dr[1] }
      : {}
  const suffix = marketingDeliveryXlsxPath(drParams)
  try {
    await fetchAuthenticatedDocument(suffix, { mode: 'download', downloadFallbackName: 'delivery_list_sistem.xlsx' })
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
  grid-template-columns: minmax(240px, 420px);
  gap: 12px 14px;
  align-items: end;
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
  grid-template-columns: repeat(4, minmax(0, 1fr));
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
  min-width: 1280px;
}

.marketing-outstanding-table {
  width: 100%;
  min-width: 1400px;
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
