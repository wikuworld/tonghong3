<template>
  <AdminSection :title="t('pages.marketingFlow.title')" :subtitle="t('pages.marketingFlow.subtitle')">
    <el-card shadow="never" class="mb-4">
      <template #header>
        <div class="flex items-center justify-between flex-wrap gap-2">
          <span class="font-semibold">{{ t('pages.marketingFlow.tabFlow') }}</span>
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-xs text-slate-600 shrink-0 max-md:hidden">{{ t('pages.marketingFlow.orderDateRangeFlow') }}</span>
            <el-date-picker
              v-model="flowDateRange"
              type="daterange"
              unlink-panels
              range-separator="—"
              value-format="YYYY-MM-DD"
              size="small"
              class="min-w-[220px] max-w-[340px]"
              :shortcuts="orderDateRangeShortcuts"
              clearable
              :start-placeholder="t('common.fromDate')"
              :end-placeholder="t('common.toDate')"
              @change="load"
            />
            <el-button type="warning" size="small" @click="pullCrToday">
              {{ t('pages.marketingFlow.pullCrToday') }}
            </el-button>
            <el-button type="success" size="small" :loading="poDailyXlsxLoading" @click="downloadDailyPoReportXlsx">
              {{ t('pages.marketingFlow.dailyPoReportXlsx') }}
            </el-button>
            <el-button type="primary" size="small" :icon="Download" @click="downloadRekap">{{ t('pages.marketingFlow.rekapToday') }}</el-button>
          </div>
        </div>
      </template>
      
      <div class="flex items-center gap-2 overflow-x-auto py-2">
        <template v-for="(s, i) in stageList" :key="s">
          <div v-if="i > 0" class="text-gray-400 flex-shrink-0 text-lg leading-none">›</div>
          <div class="flex flex-col items-center flex-shrink-0 cursor-pointer" @click="toggleStageFilter(s)">
            <el-tag :type="filterStage === s ? 'primary' : (i <= activeStep ? 'success' : 'info')" effect="light" size="small">
              {{ labelFor(s) }}
            </el-tag>
            <el-badge :value="stageCounts[s]" :max="99" :type="stageCounts[s] > 0 ? 'primary' : 'info'" class="mt-1" />
          </div>
        </template>
        <el-tag v-if="filterStage" type="info" effect="plain" size="small" class="cursor-pointer ml-2" @click="clearFilter">
          <el-icon class="cursor-pointer" @click.stop="clearFilter"><Close /></el-icon>
        </el-tag>
      </div>
    </el-card>

    <div>
      <el-table :data="rows" v-loading="loading" border stripe size="small" class="admin-table" table-layout="fixed">
        <el-table-column type="index" width="50" align="center" fixed="left" />
        <el-table-column prop="po_number" :label="t('common.poNo')" min-width="140" show-overflow-tooltip />
        <el-table-column :label="t('pages.marketingFlow.stage')" width="150">
          <template #default="{ row }">
            <el-tag size="small">{{ labelFor(row.mkt_workflow_stage) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" :label="t('common.status')" width="100" />
        <el-table-column prop="order_date" :label="t('common.orderDate')" width="110" />
        <el-table-column :label="t('pages.marketingFlow.materialDone')" width="100" align="center">
          <template #default="{ row }">
            <el-switch
              :model-value="Boolean(row.material_followup_done)"
              size="small"
              @change="(val) => toggleMaterialFollowUp(row, val)"
            />
          </template>
        </el-table-column>
        <el-table-column :label="t('pages.marketingFlow.materialRemark')" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.material_followup_remark" class="text-xs">{{ row.material_followup_remark }}</span>
            <el-button v-else type="primary" link size="small" @click="openMaterialFollowUpDialog(row)">
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
        <el-table-column :label="t('pages.marketingFlow.stuckReason')" min-width="200">
          <template #default="{ row }">
            <el-tag v-if="row.stuck_reason" type="warning" size="small" effect="plain">
              <el-icon class="mr-1"><Warning /></el-icon>
              {{ row.stuck_reason }}
            </el-tag>
            <el-tag v-else-if="isStageComplete(row)" type="success" size="small" effect="plain">
              <el-icon class="mr-1"><CircleCheck /></el-icon>
              {{ t('pages.marketingFlow.readyToAdvance') }}
            </el-tag>
            <span v-else class="text-gray-400 text-xs">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="120" fixed="right" align="center">
          <template #default="{ row }">
            <el-tooltip v-if="canAdvance" :content="t('pages.marketingFlow.advanceStageHint')" placement="top">
              <el-button
                type="primary"
                link
                size="small"
                :loading="advancing === row.id"
                :disabled="advancing != null && advancing !== row.id"
                @click="advance(row)"
              >
                <el-icon><DArrowRight /></el-icon>
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

    <el-card shadow="never" class="mt-4 marketing-tabs">
      <template #header>
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div class="font-semibold">{{ t('pages.marketingFlow.tabOutstanding') }}</div>
          <div class="flex items-center gap-2 flex-wrap">
            <el-button size="small" :icon="Search" @click="loadOutstanding">{{ t('pages.marketingFlow.outstandingRefresh') }}</el-button>
            <el-button size="small" :icon="Download" @click="downloadOutstanding">{{ t('pages.marketingFlow.outstandingDownloadCsv') }}</el-button>
            <el-button size="small" type="success" :icon="Download" :loading="outstandingXlsxLoading" @click="downloadOutstandingXlsx">
              {{ t('pages.marketingFlow.outstandingDownloadXlsx') }}
            </el-button>
            <el-button size="small" type="warning" :icon="Download" :loading="outstandingReturnXlsxLoading" @click="downloadReturnXlsx">
              {{ t('pages.marketingFlow.outstandingDownloadReturXlsx') }}
            </el-button>
            <el-button size="small" type="primary" plain @click="proposeScheduleFromSelection">
              {{ t('pages.marketingFlow.scheduleDraftButton') }}
            </el-button>
          </div>
        </div>
      </template>

      <div class="mb-2 flex flex-wrap items-center gap-2">
        <span class="text-sm text-slate-600 shrink-0">{{ t('pages.marketingFlow.orderDateRangeOutstanding') }}</span>
        <el-date-picker
          v-model="outstandingDateRange"
          type="daterange"
          unlink-panels
          range-separator="—"
          value-format="YYYY-MM-DD"
          size="small"
          class="min-w-[200px] max-w-[320px]"
          :shortcuts="orderDateRangeShortcuts"
          clearable
          :start-placeholder="t('common.fromDate')"
          :end-placeholder="t('common.toDate')"
          @change="loadOutstanding"
        />
      </div>
      <div class="mb-3 grid grid-cols-1 md:grid-cols-4 gap-2">
        <el-input v-model="poSearch" size="small" clearable :placeholder="t('common.poNo')" />
        <el-input v-model="factoryCode" size="small" clearable :placeholder="t('pages.marketingFlow.filterFactoryCode')" />
        <el-select v-model="outstandingPoCategory" size="small" clearable :placeholder="t('pages.marketingFlow.filterPoCategory')">
          <el-option :label="t('status.production')" value="production" />
          <el-option :label="t('status.sample')" value="sample" />
          <el-option :label="t('status.claim')" value="claim" />
          <el-option :label="t('status.return')" value="return" />
          <el-option :label="t('status.subcont')" value="subcont" />
          <el-option :label="t('status.suede')" value="suede" />
        </el-select>
        <el-select v-model="materialStatus" size="small" clearable :placeholder="t('pages.marketingFlow.filterMaterialStatus')">
          <el-option :label="t('pages.marketingFlow.materialFilterAll')" value="all" />
          <el-option :label="t('pages.marketingFlow.materialFilterSent')" value="sent" />
          <el-option :label="t('pages.marketingFlow.materialFilterNotSent')" value="not_sent" />
          <el-option :label="t('pages.marketingFlow.materialFilterCancelled')" value="cancelled" />
        </el-select>
      </div>

      <div class="mb-2 flex flex-wrap items-center gap-2">
        <el-switch v-model="outstandingShowAllColumns" size="small" />
        <span class="text-sm text-slate-600">{{ t('pages.marketingFlow.outstandingShowAllColumns') }}</span>
      </div>

      <el-table
        ref="outstandingTableRef"
        :data="outstandingDisplayRows"
        v-loading="outstandingLoading"
        border
        stripe
        size="small"
        class="outstanding-table"
        show-summary
        :summary-method="outstandingSummary"
        @selection-change="onOutstandingSelectionChange"
      >
        <el-table-column type="selection" width="42" fixed="left" />
        <el-table-column type="index" width="50" align="center" fixed="left" />
        <el-table-column prop="order_date" :label="t('common.orderDate')" width="110" />
        <el-table-column prop="thi_order" :label="t('pages.marketingFlow.colThiOrder')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="customer_name" :label="t('common.customerName')" min-width="180" show-overflow-tooltip />
        <el-table-column prop="brand" :label="t('pages.marketingFlow.colBrand')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="order_type" :label="t('pages.marketingFlow.colOrderType')" width="110" />
        <el-table-column prop="no_po" :label="t('common.poNo')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="po_customer_ref" :label="t('pages.marketingFlow.colPoCustomer')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="180" show-overflow-tooltip />
        <template v-for="col in outstandingExtraColumnDefs" :key="col.prop">
          <el-table-column
            v-if="outstandingShowAllColumns"
            :prop="col.prop"
            :label="t(col.labelKey)"
            :width="col.width"
            :min-width="col.minWidth"
            show-overflow-tooltip
          />
        </template>
        <el-table-column prop="qty_sf" :label="t('pages.marketingFlow.colQtySf')" width="110" />
        <el-table-column prop="schedule_qty_total" :label="t('pages.marketingFlow.colScheduleQtyTotal')" width="100" align="right" />
        <el-table-column prop="schedule_unallocated_qty" :label="t('pages.marketingFlow.colScheduleUnallocated')" width="110" align="right" />
        <el-table-column prop="delivered_qty" :label="t('pages.marketingFlow.colDeliveredQty')" width="96" align="right" />
        <el-table-column prop="actual_vs_schedule_qty" :label="t('pages.marketingFlow.colActualVsSchedule')" width="110" align="right" />
        <el-table-column prop="balance_qty" :label="t('pages.marketingFlow.colBalance')" width="110" />
        <el-table-column prop="status_material" :label="t('pages.marketingFlow.colStatusMaterial')" min-width="200" show-overflow-tooltip />
        <el-table-column prop="remark_system" :label="t('pages.marketingFlow.colRemarkSystem')" min-width="220" show-overflow-tooltip />
        <el-table-column :label="t('pages.marketingFlow.colRemarkMarketing')" min-width="220">
          <template #default="{ row }">
            <el-input
              v-model="row.remark_marketing"
              size="small"
              type="textarea"
              :rows="2"
              :disabled="!canEditPoDetail"
              @blur="saveMarketingRemark(row)"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="never" class="mt-4">
      <template #header>
        <div class="font-semibold">{{ t('pages.marketingFlow.tabMasterPlanning') }}</div>
      </template>
      <el-tabs v-model="masterPlanningTab" @tab-change="onMasterPlanningTabChange">
        <el-tab-pane name="planning" :label="t('pages.marketingFlow.planningTitle')">
          <div class="mb-2 flex flex-wrap items-center gap-2">
            <span class="text-sm text-slate-600 shrink-0">{{ t('pages.marketingFlow.planningDateRange') }}</span>
            <el-date-picker
              v-model="planningDateRange"
              type="daterange"
              unlink-panels
              value-format="YYYY-MM-DD"
              size="small"
              class="min-w-[200px] max-w-[320px]"
              range-separator="—"
              :shortcuts="orderDateRangeShortcuts"
              :start-placeholder="t('common.fromDate')"
              :end-placeholder="t('common.toDate')"
              @change="loadPlanning"
            />
            <el-input
              v-model="planningFactory"
              size="small"
              clearable
              class="w-40"
              :placeholder="t('pages.marketingFlow.factoryFilterOptional')"
            />
            <el-button size="small" type="primary" :loading="planningLoading" @click="loadPlanning">
              {{ t('pages.marketingFlow.planningLoad') }}
            </el-button>
          </div>
          <el-table :data="planningRows" border stripe size="small" max-height="380" v-loading="planningLoading">
            <el-table-column prop="delivery_date" :label="t('pages.marketingFlow.colShipDate')" width="110" />
            <el-table-column prop="sequence_no" label="#" width="44" align="center" />
            <el-table-column prop="po_number" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="factory_code" label="Factory" width="88" show-overflow-tooltip />
            <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="thi_order" :label="t('pages.marketingFlow.colThiOrder')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="qty" :label="t('pages.marketingFlow.colQtyShip')" width="88" />
            <el-table-column prop="line_etd" :label="t('pages.po.lineEtd')" width="110" />
          </el-table>
          <div v-if="!planningRows.length && !planningLoading" class="text-sm text-slate-500 py-3">
            {{ t('pages.marketingFlow.planningEmpty') }}
          </div>
        </el-tab-pane>
        <el-tab-pane name="today" :label="t('pages.marketingFlow.deliveryTodayTitle')">
          <div class="mb-2 flex flex-wrap items-center gap-2">
            <span class="text-sm text-slate-600 shrink-0">{{ t('pages.marketingFlow.todayAsOfDate') }}</span>
            <el-date-picker
              v-model="todayOnDate"
              type="date"
              value-format="YYYY-MM-DD"
              size="small"
              class="w-[140px]"
              :shortcuts="todayDateShortcuts"
              @change="loadDeliveryToday"
            />
            <el-input
              v-model="todayFactory"
              size="small"
              clearable
              class="w-40"
              :placeholder="t('pages.marketingFlow.factoryFilterOptional')"
            />
            <el-button size="small" type="primary" :loading="todayLoading" @click="loadDeliveryToday">
              {{ t('pages.marketingFlow.outstandingRefresh') }}
            </el-button>
          </div>
          <div v-loading="todayLoading">
            <div class="text-sm font-medium mb-1">{{ t('pages.marketingFlow.deliveryTodayPlanned') }}</div>
            <el-table :data="todayPlanned" border stripe size="small" class="mb-4" max-height="240">
              <el-table-column prop="delivery_date" :label="t('pages.marketingFlow.colShipDate')" width="110" />
              <el-table-column prop="po_number" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
              <el-table-column prop="material_name" :label="t('common.material')" min-width="120" show-overflow-tooltip />
              <el-table-column prop="qty" :label="t('pages.marketingFlow.colQtyShip')" width="80" />
            </el-table>
            <div class="text-sm font-medium mb-1">{{ t('pages.marketingFlow.deliveryTodayEtd') }}</div>
            <el-table :data="todayEtd" border stripe size="small" class="mb-4" max-height="200">
              <el-table-column prop="line_etd" :label="t('pages.po.lineEtd')" width="110" />
              <el-table-column prop="po_number" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
              <el-table-column prop="customer_name" :label="t('common.customerName')" min-width="120" show-overflow-tooltip />
              <el-table-column prop="material_name" :label="t('common.material')" min-width="120" show-overflow-tooltip />
            </el-table>
            <div class="text-sm font-medium mb-1">{{ t('pages.marketingFlow.deliveryTodaySj') }}</div>
            <el-table :data="todaySj" border stripe size="small" max-height="260">
              <el-table-column prop="surat_jalan_no" :label="t('pages.marketingFlow.colSuratJalan')" min-width="120" show-overflow-tooltip />
              <el-table-column prop="delivery_date" :label="t('pages.marketingFlow.colShipDate')" width="110" />
              <el-table-column prop="po_number" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
              <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
            </el-table>
          </div>
        </el-tab-pane>
        <el-tab-pane name="master" :label="t('pages.marketingFlow.snapshotListTitle')">
          <div class="mb-2 flex flex-wrap gap-2">
            <el-input
              v-model="snapshotLabel"
              size="small"
              clearable
              class="max-w-xs"
              :placeholder="t('pages.marketingFlow.snapshotLabelPlaceholder')"
            />
            <el-button size="small" type="success" :loading="snapshotSaving" @click="saveOutstandingSnapshot">
              {{ t('pages.marketingFlow.snapshotSave') }}
            </el-button>
            <el-button size="small" @click="loadSnapshotList">{{ t('pages.marketingFlow.outstandingRefresh') }}</el-button>
          </div>
          <el-table :data="snapshots" border stripe size="small" v-loading="snapshotsLoading" max-height="320">
            <el-table-column prop="id" label="ID" width="64" align="center" />
            <el-table-column prop="created_at" :label="t('common.date')" width="168" />
            <el-table-column prop="label" :label="t('common.remark')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="row_count" :label="t('pages.marketingFlow.rowCountLabel')" width="100" align="right" />
            <el-table-column :label="t('common.actions')" width="100" align="center">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="openSnapshotDetail(row.id)">
                  {{ t('pages.marketingFlow.snapshotView') }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane name="delivery" :label="t('pages.marketingFlow.tabDelivery')">
          <div class="mb-2 flex flex-wrap items-center gap-2">
            <span class="text-sm text-slate-600 shrink-0">{{ t('pages.marketingFlow.deliveryShipDateRange') }}</span>
            <el-date-picker
              v-model="deliveryDateRange"
              type="daterange"
              unlink-panels
              value-format="YYYY-MM-DD"
              size="small"
              class="min-w-[200px] max-w-[320px]"
              range-separator="—"
              :shortcuts="orderDateRangeShortcuts"
              clearable
              :start-placeholder="t('common.fromDate')"
              :end-placeholder="t('common.toDate')"
              @change="loadDelivery"
            />
            <el-button size="small" :icon="Search" @click="loadDelivery">{{ t('pages.marketingFlow.deliveryRefresh') }}</el-button>
            <el-button size="small" :icon="Download" @click="downloadDelivery">{{ t('pages.marketingFlow.deliveryDownloadCsv') }}</el-button>
          </div>
          <el-table :data="deliveryRows" v-loading="deliveryLoading" border stripe size="small" max-height="400">
            <el-table-column prop="surat_jalan_no" :label="t('pages.marketingFlow.colSuratJalan')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="delivery_date" :label="t('pages.marketingFlow.colShipDate')" width="110" />
            <el-table-column prop="factory_name" :label="t('pages.marketingFlow.colFactoryName')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="po_number" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="qty_sf" :label="t('pages.marketingFlow.colQtyShip')" width="90" />
            <el-table-column :label="t('common.actions')" width="100" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="goDelivery(row)">{{ t('pages.marketingFlow.openDelivery') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="!deliveryRows.length && !deliveryLoading" class="text-sm text-slate-500 py-3">
            {{ t('pages.marketingFlow.deliveryEmpty') }}
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

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
        <el-table-column prop="no_po" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="customer_name" :label="t('common.customerName')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
        <el-table-column prop="balance_qty" :label="t('pages.marketingFlow.colBalance')" width="96" />
        <el-table-column prop="remark_marketing" :label="t('pages.marketingFlow.colRemarkMarketing')" min-width="160" show-overflow-tooltip />
      </el-table>
    </el-dialog>

    <el-dialog v-model="assignDialogVisible" :title="t('ppicWorkflow.assignToPpic')" width="600px" destroy-on-close align-center>
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
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { DArrowRight, Document, Download, Van, User, Search, Close, Check, Warning, CircleCheck } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  advanceMktWorkflow,
  assignPoToPpic,
  createMarketingOutstandingSnapshot,
  fetchAuthenticatedDocument,
  getMarketingDeliveryToday,
  getMarketingOutstandingSnapshot,
  getPpicDashboard,
  getPoPpicAssignment,
  listMarketingDeliveryLines,
  listMarketingDeliveryPlanning,
  listMarketingOutstandingLines,
  listMarketingOutstandingSnapshots,
  listPo,
  listPoMktStages,
  listPpicUsers,
  marketingDeliveryCsvUrl,
  marketingOutstandingCsvUrl,
  marketingOutstandingReturnXlsxPath,
  marketingOutstandingXlsxPath,
  reportPoDailyMarketingXlsxPath,
  reportPoDailyRecapUrl,
  updatePo,
  updatePoDetail,
} from '../../api/client'
import { can } from '../../security/permissions'
import { formatNumber } from '../../utils/format'

const { t } = useI18n()
const canAdvance = can('po', 'advance')
const canEditPoDetail = can('po', 'update')
const router = useRouter()
const loading = ref(false)
const advancing = ref(null)
const rows = ref([])
const stageList = ref([])
const filterStage = ref(null)

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
/** Daftar alur MKT: rentang tanggal order PO header */
const flowDateRange = ref(defaultMonthToTodayRange())
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
const outstandingShowAllColumns = ref(false)
const poDailyXlsxLoading = ref(false)
const balanceFilter = ref('exclude_zero')
const shipmentTab = ref('all')
const poSearch = ref('')
const factoryCode = ref('')
const outstandingPoCategory = ref('')
const materialStatus = ref('')
const outstandingViewMode = ref('all')
const outstandingTableRef = ref(null)
const outstandingSelection = ref([])
const savingRemarkId = ref(null)

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

function buildOutstandingExtraColumnDefs() {
  const d = []
  for (let i = 1; i <= 8; i += 1) {
    d.push(
      { prop: `delivery_${i}_qty`, labelKey: `pages.marketingFlow.filterDelivery${i}Qty`, width: 82 },
      { prop: `delivery_${i}_date`, labelKey: `pages.marketingFlow.filterDelivery${i}Date`, width: 108 },
    )
  }
  return [
    { prop: 'thickness', labelKey: 'common.thickness', width: 92 },
    { prop: 'emboss', labelKey: 'common.emboss', width: 72 },
    { prop: 'softness_type', labelKey: 'pages.marketingFlow.colSoftnessType', minWidth: 110 },
    { prop: 'color', labelKey: 'common.color', width: 88 },
    { prop: 'softness', labelKey: 'common.softness', width: 88 },
    { prop: 'unit_price', labelKey: 'pages.marketingFlow.colUnitPrice', width: 88 },
    { prop: 'color_reference', labelKey: 'common.colorReference', minWidth: 110 },
    { prop: 'color_standard', labelKey: 'pages.marketingFlow.colColorStd', minWidth: 100 },
    { prop: 'backing', labelKey: 'common.backing', width: 88 },
    { prop: 'model', labelKey: 'common.model', width: 88 },
    { prop: 'style_article', labelKey: 'common.styleArticle', minWidth: 100 },
    { prop: 'rtd_text', labelKey: 'pages.marketingFlow.colRtd', width: 96 },
    { prop: 'line_etd', labelKey: 'pages.marketingFlow.colReplyEtd', width: 110 },
    { prop: 'stock_wh_qty', labelKey: 'pages.marketingFlow.colStockWh', width: 96 },
    { prop: 'delivered_qty', labelKey: 'pages.marketingFlow.colDeliveredQty', width: 96 },
    { prop: 'production_status', labelKey: 'pages.marketingFlow.colProductionStatus', minWidth: 120 },
    ...d,
  ]
}

const outstandingExtraColumnDefs = buildOutstandingExtraColumnDefs()

const OUTSTANDING_TEXT_FILTER_KEYS = [
  'order_date',
  'thi_order',
  'customer_name',
  'brand',
  'order_type',
  'no_po',
  'po_customer_ref',
  'material_name',
  'thickness',
  'emboss',
  'softness_type',
  'color',
  'softness',
  'qty_sf',
  'schedule_qty_total',
  'schedule_unallocated_qty',
  'delivered_qty',
  'actual_vs_schedule_qty',
  'unit_price',
  'color_reference',
  'color_standard',
  'backing',
  'model',
  'style_article',
  'rtd_text',
  'line_etd',
  'stock_wh_qty',
  'balance_qty',
  'delivered_qty',
  'system_reference',
  'production_status',
  'status_material',
  'remark_system',
  'remark_marketing',
  'detail_remark',
  'mkt_stage',
  'delivery_1_qty',
  'delivery_1_date',
  'delivery_2_qty',
  'delivery_2_date',
  'delivery_3_qty',
  'delivery_3_date',
  'delivery_4_qty',
  'delivery_4_date',
  'delivery_5_qty',
  'delivery_5_date',
  'delivery_6_qty',
  'delivery_6_date',
  'delivery_7_qty',
  'delivery_7_date',
  'delivery_8_qty',
  'delivery_8_date',
]

const outstandingTextFilters = reactive(
  Object.fromEntries(OUTSTANDING_TEXT_FILTER_KEYS.map((k) => [k, ''])),
)

const outstandingTextFilterFields = computed(() => {
  const map = {
    order_date: 'common.orderDate',
    thi_order: 'pages.marketingFlow.colThiOrder',
    customer_name: 'common.customerName',
    brand: 'pages.marketingFlow.colBrand',
    order_type: 'pages.marketingFlow.colOrderType',
    no_po: 'common.poNo',
    po_customer_ref: 'pages.marketingFlow.colPoCustomer',
    material_name: 'common.material',
    thickness: 'common.thickness',
    emboss: 'common.emboss',
    softness_type: 'pages.marketingFlow.colSoftnessType',
    color: 'common.color',
    softness: 'common.softness',
    qty_sf: 'pages.marketingFlow.colQtySf',
    schedule_qty_total: 'pages.marketingFlow.colScheduleQtyTotal',
    schedule_unallocated_qty: 'pages.marketingFlow.colScheduleUnallocated',
    actual_vs_schedule_qty: 'pages.marketingFlow.colActualVsSchedule',
    unit_price: 'pages.marketingFlow.colUnitPrice',
    color_reference: 'common.colorReference',
    color_standard: 'pages.marketingFlow.colColorStd',
    backing: 'common.backing',
    model: 'common.model',
    style_article: 'common.styleArticle',
    rtd_text: 'pages.marketingFlow.colRtd',
    line_etd: 'pages.marketingFlow.colReplyEtd',
    stock_wh_qty: 'pages.marketingFlow.colStockWh',
    balance_qty: 'pages.marketingFlow.colBalance',
    delivered_qty: 'pages.marketingFlow.colDeliveredQty',
    system_reference: 'pages.marketingFlow.colSystemNo',
    production_status: 'pages.marketingFlow.colProductionStatus',
    status_material: 'pages.marketingFlow.colStatusMaterial',
    remark_system: 'pages.marketingFlow.colRemarkSystem',
    remark_marketing: 'pages.marketingFlow.colRemarkMarketing',
    detail_remark: 'pages.marketingFlow.colPoLineRemark',
    mkt_stage: 'pages.marketingFlow.colMktStage',
    delivery_1_qty: 'pages.marketingFlow.filterDelivery1Qty',
    delivery_1_date: 'pages.marketingFlow.filterDelivery1Date',
    delivery_2_qty: 'pages.marketingFlow.filterDelivery2Qty',
    delivery_2_date: 'pages.marketingFlow.filterDelivery2Date',
    delivery_3_qty: 'pages.marketingFlow.filterDelivery3Qty',
    delivery_3_date: 'pages.marketingFlow.filterDelivery3Date',
    delivery_4_qty: 'pages.marketingFlow.filterDelivery4Qty',
    delivery_4_date: 'pages.marketingFlow.filterDelivery4Date',
    delivery_5_qty: 'pages.marketingFlow.filterDelivery5Qty',
    delivery_5_date: 'pages.marketingFlow.filterDelivery5Date',
    delivery_6_qty: 'pages.marketingFlow.filterDelivery6Qty',
    delivery_6_date: 'pages.marketingFlow.filterDelivery6Date',
    delivery_7_qty: 'pages.marketingFlow.filterDelivery7Qty',
    delivery_7_date: 'pages.marketingFlow.filterDelivery7Date',
    delivery_8_qty: 'pages.marketingFlow.filterDelivery8Qty',
    delivery_8_date: 'pages.marketingFlow.filterDelivery8Date',
  }
  return OUTSTANDING_TEXT_FILTER_KEYS.map((key) => ({
    key,
    label: t(map[key] || key),
  }))
})

function parseOutstandingBalance(row) {
  const n = parseFloat(String(row.balance_qty ?? '').replace(',', '.'))
  return Number.isFinite(n) ? n : 0
}

function outstandingHasSchedule(row) {
  for (let i = 1; i <= 8; i += 1) {
    const q = row[`delivery_${i}_qty`]
    const d = row[`delivery_${i}_date`]
    if ((q != null && String(q).trim() !== '') || (d != null && String(d).trim() !== '')) return true
  }
  return false
}

function isOutstandingProdFinished(st) {
  const s = String(st || '').toLowerCase()
  return ['done', 'completed', 'packed', 'released', 'finished'].includes(s)
}

function outstandingRowTextMatches(row, key, needle) {
  if (!needle || !String(needle).trim()) return true
  const q = String(needle).trim().toLowerCase()
  return String(row[key] ?? '').toLowerCase().includes(q)
}

const outstandingDisplayRows = computed(() => {
  let list = outstandingRows.value
  if (outstandingViewMode.value === 'warehouse_qc') {
    list = list.filter(
      (r) =>
        parseOutstandingBalance(r) > 0 &&
        outstandingHasSchedule(r) &&
        !isOutstandingProdFinished(r.production_status),
    )
  } else if (outstandingViewMode.value === 'mkt_delivery') {
    list = list.filter((r) => parseOutstandingBalance(r) > 0 && isOutstandingProdFinished(r.production_status))
  }
  for (const key of OUTSTANDING_TEXT_FILTER_KEYS) {
    const needle = outstandingTextFilters[key]
    if (!needle || !String(needle).trim()) continue
    list = list.filter((r) => outstandingRowTextMatches(r, key, needle))
  }
  return list
})

function outstandingSummary({ columns, data }) {
  return columns.map((col) => {
    if (col.type === 'selection') return ''
    if (col.type === 'index') return t('pages.marketingFlow.summaryLabel')
    const prop = col.property
    const isDeliveryQty = prop && /^delivery_\d+_qty$/.test(String(prop))
    if (prop && (['qty_sf', 'stock_wh_qty', 'balance_qty', 'delivered_qty', 'schedule_qty_total', 'schedule_unallocated_qty', 'actual_vs_schedule_qty'].includes(prop) || isDeliveryQty)) {
      let total = 0
      for (const row of data) {
        const n = parseFloat(String(row[prop] ?? '').replace(',', '.'))
        if (Number.isFinite(n)) total += n
      }
      return total ? String(total) : ''
    }
    return ''
  })
}

function onOutstandingSelectionChange(sel) {
  outstandingSelection.value = sel
}

function proposeScheduleFromSelection() {
  const sel = outstandingSelection.value
  if (!sel.length) {
    ElMessage.warning(t('pages.marketingFlow.selectRowsFirst'))
    return
  }
  const poIds = [...new Set(sel.map((r) => r.po_id).filter(Boolean))]
  if (poIds.length === 1) {
    router.push({ path: '/admin/po', query: { po_id: String(poIds[0]) } })
    return
  }
  if (poIds.length > 1) {
    ElMessage.warning(t('pages.marketingFlow.scheduleOnePoOnly'))
    return
  }
  ElMessage.info(t('pages.marketingFlow.scheduleDraftHint', { n: sel.length }))
}

async function saveMarketingRemark(row) {
  if (!canEditPoDetail) return
  savingRemarkId.value = row.po_detail_id
  try {
    await updatePoDetail(row.po_detail_id, { marketing_outstanding_remark: row.remark_marketing || null })
    ElMessage.success(t('pages.marketingFlow.remarkSaved'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    savingRemarkId.value = null
  }
}

async function downloadOutstandingXlsx() {
  outstandingXlsxLoading.value = true
  try {
    const od = outstandingDateRange.value
    const outstandingDateParams =
      Array.isArray(od) && od.length === 2 && od[0] && od[1] ? { order_date_from: od[0], order_date_to: od[1] } : {}
    const suffix = marketingOutstandingXlsxPath({
      balance_filter: balanceFilter.value,
      computed_balance: true,
      po_q: poSearch.value,
      shipment_status: shipmentTab.value,
      material_status: materialStatus.value || undefined,
      factory_code: factoryCode.value || undefined,
      po_category: outstandingPoCategory.value || undefined,
      ...outstandingDateParams,
    })
    const path = `/api/v1${suffix}`
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
    a.download = 'marketing_outstanding.xlsx'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(t('pages.marketingFlow.outstandingXlsxOk'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingXlsxLoading.value = false
  }
}

async function downloadReturnXlsx() {
  outstandingReturnXlsxLoading.value = true
  try {
    const od = outstandingDateRange.value
    const outstandingDateParams =
      Array.isArray(od) && od.length === 2 && od[0] && od[1] ? { order_date_from: od[0], order_date_to: od[1] } : {}
    const suffix = marketingOutstandingReturnXlsxPath({
      balance_filter: balanceFilter.value,
      computed_balance: true,
      po_q: poSearch.value,
      shipment_status: shipmentTab.value,
      material_status: materialStatus.value || undefined,
      factory_code: factoryCode.value || undefined,
      ...outstandingDateParams,
    })
    const path = `/api/v1${suffix}`
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
    a.download = 'marketing_outstanding_retur.xlsx'
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(t('pages.marketingFlow.outstandingReturXlsxOk'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingReturnXlsxLoading.value = false
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

const specItems = computed(() => [
  { title: t('pages.marketingFlow.collapseSop'), body: 'pages.marketingFlow.specSop' },
  { title: t('pages.marketingFlow.collapseInputPo'), body: 'pages.marketingFlow.specInputPo' },
  { title: t('pages.marketingFlow.collapseDaily'), body: 'pages.marketingFlow.specDaily' },
  { title: t('pages.marketingFlow.collapseOutstanding'), body: 'pages.marketingFlow.specOutstandingSheet' },
  { title: t('pages.marketingFlow.collapseInvplSj'), body: 'pages.marketingFlow.specInvplSj' },
  { title: t('pages.marketingFlow.collapseDelivery'), body: 'pages.marketingFlow.specDelivery' },
  { title: t('pages.marketingFlow.collapseCustomer'), body: 'pages.marketingFlow.specCustomer' },
  { title: t('pages.marketingFlow.collapseInvoice'), body: 'pages.marketingFlow.specInvoice' },
])

const labels = computed(() => ({
  input_system: t('mktStage.input_system'),
  rekap_printed: t('mktStage.rekap_printed'),
  with_ppic: t('mktStage.with_ppic'),
  back_to_mkt: t('mktStage.back_to_mkt'),
  in_outstanding: t('mktStage.in_outstanding'),
  material_followup: t('mktStage.material_followup'),
  delivery_arranged: t('mktStage.delivery_arranged'),
  sj_invpl: t('mktStage.sj_invpl'),
  invoice_billing: t('mktStage.invoice_billing'),
}))

function labelFor(stage) {
  return labels.value[stage] || stage || t('common.emptyValue')
}

const activeStep = computed(() => {
  const s = rows.value[0]?.mkt_workflow_stage || 'input_system'
  const i = stageList.value.indexOf(s)
  return i >= 0 ? i : 0
})

const stageCounts = computed(() => {
  const counts = {}
  for (const s of stageList.value) {
    counts[s] = 0
  }
  for (const row of rows.value) {
    const s = row.mkt_workflow_stage
    if (s && counts[s] !== undefined) {
      counts[s]++
    }
  }
  return counts
})

function isStageComplete(row) {
  const s = row.mkt_workflow_stage
  if (!s) return false
  const idx = stageList.value.indexOf(s)
  return idx >= 0 && idx < stageList.value.length - 1 && !row.stuck_reason
}

function toggleStageFilter(stage) {
  if (filterStage.value === stage) {
    filterStage.value = null
  } else {
    filterStage.value = stage
  }
  load()
}

function clearFilter() {
  filterStage.value = null
  load()
}

async function load() {
  loading.value = true
  try {
    const params = {}
    if (filterStage.value) {
      params.mkt_workflow_stage = filterStage.value
    }
    if (Array.isArray(flowDateRange.value) && flowDateRange.value.length === 2 && flowDateRange.value[0] && flowDateRange.value[1]) {
      params.order_date_from = flowDateRange.value[0]
      params.order_date_to = flowDateRange.value[1]
    }
    rows.value = await listPo(params)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    loading.value = false
  }
}

async function loadOutstanding() {
  outstandingLoading.value = true
  try {
    const od = outstandingDateRange.value
    const outstandingDateParams =
      Array.isArray(od) && od.length === 2 && od[0] && od[1] ? { order_date_from: od[0], order_date_to: od[1] } : {}
    outstandingRows.value = await listMarketingOutstandingLines({
      balance_filter: balanceFilter.value,
      computed_balance: true,
      po_q: poSearch.value,
      shipment_status: shipmentTab.value,
      material_status: materialStatus.value || undefined,
      factory_code: factoryCode.value || undefined,
      po_category: outstandingPoCategory.value || undefined,
      ...outstandingDateParams,
    })
    outstandingSelection.value = []
    outstandingTableRef.value?.clearSelection?.()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    outstandingLoading.value = false
  }
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
    const od = outstandingDateRange.value
    const outstandingDateParams =
      Array.isArray(od) && od.length === 2 && od[0] && od[1] ? { order_date_from: od[0], order_date_to: od[1] } : {}
    await createMarketingOutstandingSnapshot({
      label: snapshotLabel.value?.trim() || null,
      filters: {
        balance_filter: balanceFilter.value,
        computed_balance: true,
        po_q: poSearch.value?.trim() || null,
        shipment_status: shipmentTab.value,
        material_status: materialStatus.value || null,
        factory_code: factoryCode.value?.trim() || null,
        po_category: outstandingPoCategory.value?.trim() || null,
        ...outstandingDateParams,
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
    const data = await listPoMktStages()
    stageList.value = data.stages || []
  } catch {
    stageList.value = []
  }
  await Promise.all([
    load(),
    loadPpicUsers(),
    loadAssignments(),
    loadOutstanding(),
    loadPlanning().catch(() => {}),
  ])
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
    ElMessage.warning(t('ppicWorkflow.ppicUser') + ' ' + t('common.required'))
    return
  }
  assigning.value = true
  try {
    await assignPoToPpic(selectedPoForAssignment.value.id, {
      ppic_user_id: assignForm.value.ppic_user_id,
      notes: assignForm.value.notes || null,
    })
    ElMessage.success(t('common.saveSuccess'))
    assignDialogVisible.value = false
    await loadAssignments()
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
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    savingMaterialFollowUp.value = false
  }
}

async function advance(row) {
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

async function downloadRekap() {
  const r = flowDateRange.value
  const day = Array.isArray(r) && r.length === 2 && r[1] ? r[1] : Array.isArray(r) && r[0] ? r[0] : new Date().toISOString().slice(0, 10)
  const path = reportPoDailyRecapUrl(day).replace(/^\/api\/v1/, '')
  try {
    await fetchAuthenticatedDocument(path, { mode: 'download', downloadFallbackName: `po-daily-recap-${day}.csv` })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
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
  const od = outstandingDateRange.value
  const outstandingDateParams =
    Array.isArray(od) && od.length === 2 && od[0] && od[1] ? { order_date_from: od[0], order_date_to: od[1] } : {}
  const suffix = marketingOutstandingCsvUrl({
    balance_filter: balanceFilter.value,
    computed_balance: true,
    po_q: poSearch.value,
    shipment_status: shipmentTab.value,
    material_status: materialStatus.value || undefined,
    factory_code: factoryCode.value || undefined,
    po_category: outstandingPoCategory.value || undefined,
    ...outstandingDateParams,
  })
  try {
    await fetchAuthenticatedDocument(suffix, { mode: 'download', downloadFallbackName: 'marketing-outstanding.csv' })
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
</script>

<style scoped>
.admin-table {
  width: 100%;
}
.outstanding-table {
  width: 100%;
}
.marketing-tabs :deep(.el-tabs__content) {
  padding-top: 0.5rem;
}
</style>
