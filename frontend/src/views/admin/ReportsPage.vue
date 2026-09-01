<template>
  <AdminSection :title="t('pages.reports.title')" :subtitle="t('pages.reports.subtitle')">
    <template #actions>
      <el-input
        v-if="reportTab === 'marketing'"
        v-model="keyword"
        :placeholder="t('pages.reports.searchPlaceholder')"
        clearable
        class="reports-toolbar-search"
      />
      <span v-if="reportTab === 'marketing' && reportLoading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button v-if="reportTab === 'marketing'" :icon="Refresh" :loading="reportLoading" @click="runGenerateReport">{{ t('common.refresh') }}</el-button>
      <el-button v-if="reportTab === 'rar'" :icon="Refresh" :loading="rarLoading" @click="fetchRarReport">{{ t('common.refresh') }}</el-button>
      <el-button v-if="reportTab === 'pending-payment'" :icon="Refresh" :loading="ppLoading" @click="fetchPendingPaymentReport">{{ t('common.refresh') }}</el-button>
    </template>

    <el-tabs v-model="reportTab" class="reports-tabs">
      <el-tab-pane :label="t('pages.reports.tabMarketing')" name="marketing">

    <div class="reports-action-bar">
      <p class="reports-action-bar__hint">{{ t('pages.reports.dailyMarketingSheet') }}</p>
      <div class="reports-action-bar__buttons">
        <el-dropdown v-if="canExport" trigger="click" @command="handleExportCommand">
          <el-button :icon="Download" :loading="dailyCsvLoading">
            {{ t('pages.reports.exportMenu') }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="daily">{{ t('pages.reports.exportDailyMarketing') }}</el-dropdown-item>
              <el-dropdown-item command="daily-xlsx">{{ t('pages.reports.exportDailyMarketingXlsx') }}</el-dropdown-item>
              <el-dropdown-item command="so">{{ t('pages.reports.exportSo') }}</el-dropdown-item>
              <el-dropdown-item command="lines">{{ t('pages.reports.exportLines') }}</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button v-if="canExport" type="primary" :icon="Printer" @click="printReport">
          {{ t('common.print') }} {{ t('pages.reports.report') }}
        </el-button>
      </div>
    </div>

    <div class="admin-inner-card">
      <div class="admin-inner-card__head">
        <div>
          <h3 class="admin-inner-card__title">{{ t('pages.reports.poOrderDescription') }}</h3>
          <p class="admin-inner-card__sub">PT. Tong Hong Tannery Indonesia</p>
        </div>
      </div>

      <div class="filter-panel report-card__filter">
        <p class="filter-panel__title">{{ t('common.filter') }}</p>
        <el-form class="filter-form" label-position="top">
          <el-row :gutter="12" align="bottom">
            <el-col :xs="24" :lg="9">
              <el-form-item :label="t('pages.reports.dateRange')">
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  range-separator="—"
                  :start-placeholder="t('common.startDate')"
                  :end-placeholder="t('common.endDate')"
                  value-format="YYYY-MM-DD"
                  class="w-full"
                  :shortcuts="dateShortcuts"
                  unlink-panels
                  clearable
                />
              </el-form-item>
            </el-col>
            <el-col :xs="12" :lg="5">
              <el-form-item :label="t('common.customer')">
                <el-select v-model="customer" clearable filterable class="w-full" :placeholder="t('common.allCustomer')">
                  <el-option :label="t('common.allCustomer')" value="" />
                  <el-option v-for="c in customers" :key="c.id" :label="c.name || c.code" :value="c.name || c.code" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="12" :lg="5">
              <el-form-item :label="t('common.poCategory')">
                <el-select v-model="category" clearable class="w-full" :placeholder="t('pages.reports.allStatus')">
                  <el-option :label="t('pages.reports.allStatus')" value="" />
                  <el-option :label="t('status.production')" value="production" />
                  <el-option :label="t('status.sample')" value="sample" />
                  <el-option :label="t('status.claim')" value="claim" />
                  <el-option :label="t('status.return')" value="return" />
                  <el-option :label="t('status.subcont')" value="subcont" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :lg="5" class="reports-filter-actions">
              <el-form-item label="&nbsp;">
                <div class="reports-filter-actions__row">
                  <el-button type="primary" :icon="DataAnalysis" :loading="reportLoading" @click="runGenerateReport">
                    {{ t('pages.reports.generateReport') }}
                  </el-button>
                  <el-button :icon="RefreshLeft" @click="resetFilters">{{ t('common.reset') }}</el-button>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="12">
            <el-col :xs="24" :sm="12" :md="8" :lg="6">
              <el-form-item :label="t('pages.reports.dateFieldLabel')">
                <el-select v-model="dateField" class="w-full">
                  <el-option :label="t('pages.reports.dateFieldOrder')" value="order" />
                  <el-option :label="t('pages.reports.dateFieldCreated')" value="created" />
                  <el-option :label="t('pages.reports.dateFieldEither')" value="either" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>

      <div class="admin-stats-grid admin-stats-grid--4">
        <div class="admin-stat-card">
          <span class="admin-stat-card__value">{{ reportStats.revise }}</span>
          <span class="admin-stat-card__label">{{ t('pages.reports.reviseThickness') }}</span>
        </div>
        <div class="admin-stat-card admin-stat-card--info">
          <span class="admin-stat-card__value">{{ reportStats.production }}</span>
          <span class="admin-stat-card__label">{{ t('pages.reports.productionOrder') }}</span>
        </div>
        <div class="admin-stat-card admin-stat-card--warn">
          <span class="admin-stat-card__value">{{ reportStats.sample }}</span>
          <span class="admin-stat-card__label">{{ t('pages.reports.sample') }}</span>
        </div>
        <div class="admin-stat-card admin-stat-card--success">
          <span class="admin-stat-card__value">{{ reportStats.claim + reportStats.return + reportStats.subcont }}</span>
          <span class="admin-stat-card__label">{{ t('pages.reports.otherCategories') }}</span>
        </div>
      </div>

      <p class="admin-scroll-hint">{{ t('pages.reports.scrollHint') }}</p>

      <div v-loading="reportLoading" class="report-card__body">
        <div v-if="showReviseSection">
        <div class="report-section-head">
          <div>
            <h3 class="report-section-title">{{ t('pages.reports.reviseThickness') }}</h3>
            <p class="report-section-sub">{{ t('pages.reports.reviseThicknessHint') }}</p>
          </div>
          <el-tag size="small" type="info" effect="plain">{{ reportStats.revise }}</el-tag>
        </div>
        <div class="report-table-scroll">
          <el-table
            :data="filteredReviseRows"
            border
            stripe
            size="small"
            class="admin-table report-table report-table--wide"
            table-layout="auto"
            :empty-text="t('pages.reports.tableEmpty')"
          >
            <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" fixed />
            <el-table-column :label="t('pages.reports.colRevisedAt')" min-width="150" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateTime(row.revised_at) }}</template>
            </el-table-column>
            <el-table-column prop="actor" :label="t('pages.reports.colActor')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="revise_action" :label="t('pages.reports.colReviseAction')" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" effect="plain">{{ row.revise_action || '—' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="change_summary" :label="t('pages.reports.colChangeSummary')" min-width="220" show-overflow-tooltip />
            <el-table-column :label="t('pages.reports.colOrderDate')" min-width="112" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateIso(row.order_date) }}</template>
            </el-table-column>
            <el-table-column prop="thi_line_ref" :label="t('pages.reports.colThiLine')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="customer" :label="t('common.customer')" min-width="150" show-overflow-tooltip />
            <el-table-column prop="brand" :label="t('pages.reports.colBrand')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="order_type" :label="t('pages.reports.colOrderType')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="poNo" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="po_customer_ref" :label="t('pages.reports.colPoCustomerRef')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="material" :label="t('common.material')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="oldThickness" :label="t('pages.reports.oldThickness')" min-width="100" />
            <el-table-column prop="newThickness" :label="t('pages.reports.newThickness')" min-width="100">
              <template #default="{ row }">
                <span class="text-amber-700 font-bold">{{ row.newThickness || '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="emboss" :label="t('pages.po.emboss')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="softness_type" :label="t('pages.reports.colSoftnessType')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="pu_production" :label="t('pages.reports.colPuProduction')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="color" :label="t('common.color')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="softness" :label="t('common.softness')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="qty" :label="t('common.quantity')" min-width="88" align="right">
              <template #default="{ row }">{{ formatQty(row.qty) }}</template>
            </el-table-column>
            <el-table-column prop="unit_price" :label="t('pages.reports.colUnitPrice')" min-width="90" align="right" show-overflow-tooltip />
            <el-table-column prop="color_reference" :label="t('common.colorReference')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="backing" :label="t('common.backing')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="model" :label="t('common.model')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="110" show-overflow-tooltip />
            <el-table-column :label="t('pages.po.lineEtd')" min-width="110" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateIso(row.line_etd) }}</template>
            </el-table-column>
            <el-table-column prop="buyer" :label="t('common.buyer')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="source" :label="t('pages.reports.colSource')" width="100" align="center" />
            <el-table-column prop="status" :label="t('common.status')" min-width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="poStatusTagType(row.status)" size="small">{{ poStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        </div>

        <div v-if="showOrderSection('production')" class="report-section-head">
          <h3 class="report-section-title">{{ t('pages.reports.productionOrder') }}</h3>
          <el-tag size="small" type="primary" effect="plain">{{ reportStats.production }}</el-tag>
        </div>
        <div v-if="showOrderSection('production')" class="report-table-scroll">
          <el-table
            :data="filteredProductionRows"
            border
            stripe
            size="small"
            class="admin-table report-table report-table--wide"
            table-layout="auto"
            :empty-text="t('pages.reports.tableEmpty')"
          >
            <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" fixed />
            <el-table-column :label="t('pages.reports.colOrderDate')" min-width="112" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateIso(row.order_date) }}</template>
            </el-table-column>
            <el-table-column prop="thi_line_ref" :label="t('pages.reports.colThiLine')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="customer" :label="t('common.customer')" min-width="150" show-overflow-tooltip />
            <el-table-column prop="brand" :label="t('pages.reports.colBrand')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="order_type" :label="t('pages.reports.colOrderType')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="poNo" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="po_customer_ref" :label="t('pages.reports.colPoCustomerRef')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="material" :label="t('common.material')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="thickness" :label="t('common.thickness')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="emboss" :label="t('pages.po.emboss')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="softness_type" :label="t('pages.reports.colSoftnessType')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="pu_production" :label="t('pages.reports.colPuProduction')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="color" :label="t('common.color')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="softness" :label="t('common.softness')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="qty" :label="t('common.quantity')" min-width="88" align="right">
              <template #default="{ row }">{{ formatQty(row.qty) }}</template>
            </el-table-column>
            <el-table-column prop="unit_price" :label="t('pages.reports.colUnitPrice')" min-width="90" align="right" show-overflow-tooltip />
            <el-table-column prop="color_reference" :label="t('common.colorReference')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="backing" :label="t('common.backing')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="model" :label="t('common.model')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="110" show-overflow-tooltip />
            <el-table-column :label="t('pages.po.lineEtd')" min-width="110" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateIso(row.line_etd) }}</template>
            </el-table-column>
            <el-table-column prop="buyer" :label="t('common.buyer')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="po_category" :label="t('common.poCategory')" min-width="100" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.po_category" size="small" type="info" effect="plain">{{ categoryLabel(row.po_category) }}</el-tag>
                <span v-else>—</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" :label="t('common.status')" min-width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="poStatusTagType(row.status)" size="small">{{ poStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-if="showOrderSection('production')" class="report-total-line">
          {{ t('pages.reports.totalProductionOrder') }}: <b>{{ formatQty(productionQtySum) }}</b>
        </div>

        <div v-if="showOrderSection('sample')" class="report-section-head">
          <h3 class="report-section-title">{{ t('pages.reports.sample') }}</h3>
          <el-tag size="small" type="warning" effect="plain">{{ reportStats.sample }}</el-tag>
        </div>
        <div v-if="showOrderSection('sample')" class="report-table-scroll">
          <el-table
            :data="filteredSampleRows"
            border
            stripe
            size="small"
            class="admin-table report-table report-table--wide"
            table-layout="auto"
            :empty-text="t('pages.reports.tableEmpty')"
          >
            <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" fixed />
            <el-table-column :label="t('pages.reports.colOrderDate')" min-width="112" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateIso(row.order_date) }}</template>
            </el-table-column>
            <el-table-column prop="thi_line_ref" :label="t('pages.reports.colThiLine')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="customer" :label="t('common.customer')" min-width="150" show-overflow-tooltip />
            <el-table-column prop="brand" :label="t('pages.reports.colBrand')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="order_type" :label="t('pages.reports.colOrderType')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="poNo" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="po_customer_ref" :label="t('pages.reports.colPoCustomerRef')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="material" :label="t('common.material')" min-width="130" show-overflow-tooltip />
            <el-table-column prop="thickness" :label="t('common.thickness')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="emboss" :label="t('pages.po.emboss')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="softness_type" :label="t('pages.reports.colSoftnessType')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="pu_production" :label="t('pages.reports.colPuProduction')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="color" :label="t('common.color')" min-width="110" show-overflow-tooltip />
            <el-table-column prop="softness" :label="t('common.softness')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="qty" :label="t('common.quantity')" min-width="88" align="right">
              <template #default="{ row }">{{ formatQty(row.qty) }}</template>
            </el-table-column>
            <el-table-column prop="unit_price" :label="t('pages.reports.colUnitPrice')" min-width="90" align="right" show-overflow-tooltip />
            <el-table-column prop="color_reference" :label="t('common.colorReference')" min-width="120" show-overflow-tooltip />
            <el-table-column prop="backing" :label="t('common.backing')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="model" :label="t('common.model')" min-width="100" show-overflow-tooltip />
            <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="110" show-overflow-tooltip />
            <el-table-column :label="t('pages.po.lineEtd')" min-width="110" show-overflow-tooltip>
              <template #default="{ row }">{{ formatDateIso(row.line_etd) }}</template>
            </el-table-column>
            <el-table-column prop="buyer" :label="t('common.buyer')" min-width="90" show-overflow-tooltip />
            <el-table-column prop="status" :label="t('common.status')" min-width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="poStatusTagType(row.status)" size="small">{{ poStatusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-if="showOrderSection('sample')" class="report-total-line">
          {{ t('pages.reports.totalSample') }}: <b>{{ formatQty(sampleQtySum) }}</b>
        </div>

        <template v-for="sec in extraCategorySections" :key="sec.key">
          <div class="report-section-head">
            <h3 class="report-section-title">{{ sec.title }}</h3>
            <el-tag size="small" :type="sec.tagType" effect="plain">{{ sec.rows.length }}</el-tag>
          </div>
          <div class="report-table-scroll">
            <el-table
              :data="sec.rows"
              border
              stripe
              size="small"
              class="admin-table report-table report-table--wide"
              table-layout="auto"
              :empty-text="t('pages.reports.tableEmpty')"
            >
              <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" fixed />
              <el-table-column :label="t('pages.reports.colOrderDate')" min-width="112" show-overflow-tooltip>
                <template #default="{ row }">{{ formatDateIso(row.order_date) }}</template>
              </el-table-column>
              <el-table-column prop="thi_line_ref" :label="t('pages.reports.colThiLine')" min-width="120" show-overflow-tooltip />
              <el-table-column prop="customer" :label="t('common.customer')" min-width="150" show-overflow-tooltip />
              <el-table-column prop="brand" :label="t('pages.reports.colBrand')" min-width="100" show-overflow-tooltip />
              <el-table-column prop="order_type" :label="t('pages.reports.colOrderType')" min-width="100" show-overflow-tooltip />
              <el-table-column prop="poNo" :label="t('common.poNo')" min-width="120" show-overflow-tooltip />
              <el-table-column prop="po_customer_ref" :label="t('pages.reports.colPoCustomerRef')" min-width="130" show-overflow-tooltip />
              <el-table-column prop="material" :label="t('common.material')" min-width="130" show-overflow-tooltip />
              <el-table-column prop="thickness" :label="t('common.thickness')" min-width="100" show-overflow-tooltip />
              <el-table-column prop="emboss" :label="t('pages.po.emboss')" min-width="100" show-overflow-tooltip />
              <el-table-column prop="color" :label="t('common.color')" min-width="110" show-overflow-tooltip />
              <el-table-column prop="qty" :label="t('common.quantity')" min-width="88" align="right">
                <template #default="{ row }">{{ formatQty(row.qty) }}</template>
              </el-table-column>
              <el-table-column prop="unit_price" :label="t('pages.reports.colUnitPrice')" min-width="90" align="right" show-overflow-tooltip />
              <el-table-column prop="buyer" :label="t('common.buyer')" min-width="90" show-overflow-tooltip />
              <el-table-column prop="po_category" :label="t('common.poCategory')" min-width="100" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.po_category" size="small" type="info" effect="plain">{{ categoryLabel(row.po_category) }}</el-tag>
                  <span v-else>—</span>
                </template>
              </el-table-column>
              <el-table-column prop="status" :label="t('common.status')" min-width="110" align="center">
                <template #default="{ row }">
                  <el-tag :type="poStatusTagType(row.status)" size="small">{{ poStatusLabel(row.status) }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <div class="report-total-line">
            {{ sec.totalLabel }}: <b>{{ formatQty(sec.qtySum) }}</b>
          </div>
        </template>
      </div>
    </div>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.reports.tabRar')" name="rar">
        <div class="admin-inner-card">
          <div class="admin-inner-card__head">
            <div>
              <h3 class="admin-inner-card__title">{{ t('pages.reports.rarTitle') }}</h3>
              <p class="admin-inner-card__sub">{{ t('pages.reports.rarSubtitle') }}</p>
            </div>
            <el-button v-if="canExport" type="primary" :icon="Download" :loading="rarXlsxLoading" @click="exportRarXlsx">
              {{ t('pages.reports.rarExportXlsx') }}
            </el-button>
          </div>

          <div class="filter-panel report-card__filter">
            <p class="filter-panel__title">{{ t('common.filter') }}</p>
            <el-form class="filter-form" label-position="top">
              <el-row :gutter="12" align="bottom">
                <el-col :xs="24" :lg="8">
                  <el-form-item :label="t('pages.reports.dateRange')">
                    <el-date-picker
                      v-model="rarDateRange"
                      type="daterange"
                      range-separator="—"
                      value-format="YYYY-MM-DD"
                      class="w-full"
                      unlink-panels
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :xs="12" :lg="5">
                  <el-form-item :label="t('common.customer')">
                    <el-select v-model="rarCustomer" clearable filterable class="w-full" :placeholder="t('common.allCustomer')">
                      <el-option :label="t('common.allCustomer')" value="" />
                      <el-option v-for="c in customers" :key="c.id" :label="c.name || c.code" :value="c.name || c.code" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="12" :lg="4">
                  <el-form-item :label="t('pages.reports.rarYear')">
                    <el-input-number v-model="rarYear" :min="2020" :max="2035" class="w-full" controls-position="right" />
                  </el-form-item>
                </el-col>
                <el-col :xs="12" :lg="4">
                  <el-form-item :label="t('pages.reports.rarPaymentStatus')">
                    <el-select v-model="rarPaymentStatus" class="w-full">
                      <el-option :label="t('pages.reports.rarPaymentAll')" value="all" />
                      <el-option :label="t('pages.reports.rarPaymentPaid')" value="paid" />
                      <el-option :label="t('pages.reports.rarPaymentUnpaid')" value="unpaid" />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :lg="3">
                  <el-form-item label="&nbsp;">
                    <el-button type="primary" :loading="rarLoading" @click="fetchRarReport">{{ t('pages.reports.generateReport') }}</el-button>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>

          <div class="admin-stats-grid admin-stats-grid--4">
            <div class="admin-stat-card">
              <span class="admin-stat-card__value">{{ rarStats.count }}</span>
              <span class="admin-stat-card__label">{{ t('pages.reports.rarStatCount') }}</span>
            </div>
            <div class="admin-stat-card admin-stat-card--info">
              <span class="admin-stat-card__value">{{ formatRarUsd(rarStats.amount_faktur_usd) }}</span>
              <span class="admin-stat-card__label">{{ t('pages.reports.rarStatFaktur') }}</span>
            </div>
            <div class="admin-stat-card admin-stat-card--success">
              <span class="admin-stat-card__value">{{ formatRarUsd(rarStats.amount_payment_usd) }}</span>
              <span class="admin-stat-card__label">{{ t('pages.reports.rarStatPaid') }}</span>
            </div>
            <div class="admin-stat-card admin-stat-card--warn">
              <span class="admin-stat-card__value">{{ rarStats.not_yet_count }}</span>
              <span class="admin-stat-card__label">{{ t('pages.reports.rarStatNotYet') }}</span>
            </div>
          </div>

          <div v-loading="rarLoading" class="report-card__body">
            <div class="report-table-scroll">
              <el-table
                :data="filteredRarRows"
                border
                stripe
                size="small"
                class="admin-table report-table"
                :empty-text="t('pages.reports.tableEmpty')"
              >
                <el-table-column type="index" :label="t('common.noLabel')" width="48" align="center" />
                <el-table-column prop="tax_invoice_no" :label="t('pages.reports.colTaxInvoiceNo')" min-width="150" show-overflow-tooltip />
                <el-table-column prop="customer_name" :label="t('common.customer')" min-width="180" show-overflow-tooltip />
                <el-table-column prop="invoice_number" :label="t('common.invoiceNo')" min-width="140" show-overflow-tooltip />
                <el-table-column :label="t('pages.reports.colOrderDate')" width="112">
                  <template #default="{ row }">{{ formatDateIso(row.tax_invoice_date || row.invoice_date) }}</template>
                </el-table-column>
                <el-table-column :label="t('common.total') + ' (USD)'" min-width="110" align="right">
                  <template #default="{ row }">{{ formatRarUsd(row.total_amount) }}</template>
                </el-table-column>
                <el-table-column :label="t('pages.reports.colAmountPayment')" min-width="110" align="right">
                  <template #default="{ row }">{{ formatRarUsd(row.payment_amount) }}</template>
                </el-table-column>
                <el-table-column :label="t('pages.reports.colBalance')" min-width="110" align="right">
                  <template #default="{ row }">{{ formatRarUsd(row.balance_after_deduct) }}</template>
                </el-table-column>
                <el-table-column prop="remark" :label="t('pages.reports.colRemark')" min-width="130" show-overflow-tooltip />
              </el-table>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="t('pages.reports.tabPendingPayment')" name="pending-payment">
        <div class="admin-inner-card">
          <div class="admin-inner-card__head">
            <div>
              <h3 class="admin-inner-card__title">{{ t('pages.reports.ppTitle') }}</h3>
              <p class="admin-inner-card__sub">{{ t('pages.reports.ppSubtitle') }}</p>
            </div>
            <el-button v-if="canExport" type="primary" :icon="Download" :loading="ppXlsxLoading" @click="exportPendingPaymentXlsx">
              {{ t('pages.reports.ppExportXlsx') }}
            </el-button>
          </div>

          <div class="filter-panel report-card__filter">
            <p class="filter-panel__title">{{ t('common.filter') }}</p>
            <el-form class="filter-form" label-position="top">
              <el-row :gutter="12" align="bottom">
                <el-col :xs="12" :lg="5">
                  <el-form-item :label="t('pages.reports.ppAsOf')">
                    <el-date-picker
                      v-model="ppAsOf"
                      type="date"
                      value-format="YYYY-MM-DD"
                      class="w-full"
                      clearable
                    />
                  </el-form-item>
                </el-col>
                <el-col :xs="12" :lg="4">
                  <el-form-item :label="t('pages.reports.ppYear')">
                    <el-input-number v-model="ppYear" :min="2020" :max="2035" class="w-full" controls-position="right" />
                  </el-form-item>
                </el-col>
                <el-col :xs="12" :lg="5">
                  <el-form-item :label="t('common.filter')">
                    <el-switch
                      v-model="ppOverdueOnly"
                      :active-text="t('pages.reports.ppShowOverdueOnly')"
                      :inactive-text="t('pages.reports.ppShowAll')"
                    />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :lg="4">
                  <el-form-item label="&nbsp;">
                    <el-button type="primary" :loading="ppLoading" @click="fetchPendingPaymentReport">{{ t('pages.reports.generateReport') }}</el-button>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </div>

          <div class="admin-stats-grid admin-stats-grid--4">
            <div class="admin-stat-card">
              <span class="admin-stat-card__value">{{ ppStats.master_count }}</span>
              <span class="admin-stat-card__label">{{ t('pages.reports.ppStatMaster') }}</span>
            </div>
            <div class="admin-stat-card admin-stat-card--warn">
              <span class="admin-stat-card__value">{{ ppStats.overdue_customer_count }}</span>
              <span class="admin-stat-card__label">{{ t('pages.reports.ppStatOverdueCustomers') }}</span>
            </div>
            <div class="admin-stat-card admin-stat-card--info">
              <span class="admin-stat-card__value">{{ ppStats.overdue_invoice_count }}</span>
              <span class="admin-stat-card__label">{{ t('pages.reports.ppStatOverdueInvoices') }}</span>
            </div>
            <div class="admin-stat-card admin-stat-card--success">
              <span class="admin-stat-card__value">{{ formatRarUsd(ppStats.amount_usd_total) }}</span>
              <span class="admin-stat-card__label">{{ t('pages.reports.ppStatTotal') }}</span>
            </div>
          </div>

          <div v-loading="ppLoading" class="report-card__body">
            <div class="report-table-scroll">
              <el-table
                :data="filteredPpRows"
                border
                stripe
                size="small"
                class="admin-table report-table report-table--wide"
                :empty-text="t('pages.reports.tableEmpty')"
                :row-class-name="ppRowClassName"
              >
                <el-table-column prop="no" :label="t('common.noLabel')" width="52" align="center" />
                <el-table-column prop="customer" :label="t('common.customer')" min-width="220" show-overflow-tooltip />
                <el-table-column prop="brand" :label="t('pages.reports.colBrand')" min-width="110" show-overflow-tooltip />
                <el-table-column prop="payment_term" label="T/T" min-width="80" show-overflow-tooltip />
                <el-table-column prop="closing_date" :label="t('pages.reports.ppColClosingDate')" width="100" align="center" />
                <el-table-column prop="payment_date" :label="t('pages.reports.ppColPaymentDate')" min-width="120" show-overflow-tooltip />
                <el-table-column prop="month" :label="t('pages.reports.ppColMonth')" width="72" align="center" />
                <el-table-column prop="receivable_date" :label="t('pages.reports.ppColReceivableDate')" min-width="130" show-overflow-tooltip />
                <el-table-column :label="t('pages.reports.ppColAmountUsd')" min-width="120" align="right">
                  <template #default="{ row }">
                    <span :class="{ 'font-semibold text-amber-700': row.amount_usd > 0 }">{{ formatRarUsd(row.amount_usd) }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="remarks" :label="t('pages.reports.colRemark')" min-width="220" show-overflow-tooltip />
              </el-table>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Download, Printer, DataAnalysis, Refresh, RefreshLeft, ArrowDown } from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import {
  fetchReportPoOrderDescription,
  fetchReportAccountsReceivable,
  fetchReportPendingPayment,
  fetchAuthenticatedDocument,
  listCustomers,
  reportPoDailyMarketingCsvPath,
  reportPoDailyMarketingXlsxPath,
  reportAccountsReceivableXlsxPath,
  reportPendingPaymentXlsxPath,
  reportSalesOrderLinesExportUrl,
  reportSalesOrdersExportUrl,
} from '../../api/client'
import { useModulePermission } from '../../composables/useModulePermission'

const { canExport } = useModulePermission('reports')

const { t, te } = useI18n()

const reportTab = ref('marketing')
const keyword = ref('')
const dateRange = ref([])
const customer = ref('')
const category = ref('')
const dateField = ref('order')
const customers = ref([])

const dateShortcuts = computed(() => [
  {
    text: t('pages.reports.shortcutToday'),
    value: () => {
      const end = new Date()
      const start = new Date()
      return [start, end]
    },
  },
  {
    text: t('pages.reports.shortcutLast7Days'),
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: t('pages.reports.shortcutLast30Days'),
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: t('pages.reports.shortcutLast90Days'),
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    },
  },
  {
    text: t('pages.reports.shortcutThisMonth'),
    value: () => {
      const end = new Date()
      const start = new Date(end.getFullYear(), end.getMonth(), 1)
      return [start, end]
    },
  },
  {
    text: t('pages.reports.shortcutLastMonth'),
    value: () => {
      const end = new Date()
      end.setDate(0)
      const start = new Date(end.getFullYear(), end.getMonth(), 1)
      return [start, end]
    },
  },
])

const reportLoading = ref(false)
const dailyCsvLoading = ref(false)
const reviseRows = ref([])
const productionRows = ref([])
const sampleRows = ref([])
const claimRows = ref([])
const returnRows = ref([])
const subcontRows = ref([])

const rarLoading = ref(false)
const rarXlsxLoading = ref(false)
const rarDateRange = ref([])
const rarCustomer = ref('')
const rarYear = ref(new Date().getFullYear())
const rarPaymentStatus = ref('all')
const rarRows = ref([])
const rarStats = ref({
  count: 0,
  amount_faktur_usd: 0,
  amount_payment_usd: 0,
  not_yet_count: 0,
})

const ppLoading = ref(false)
const ppXlsxLoading = ref(false)
const ppAsOf = ref(new Date().toISOString().slice(0, 10))
const ppYear = ref(new Date().getFullYear())
const ppOverdueOnly = ref(true)
const ppRows = ref([])
const ppStats = ref({
  master_count: 0,
  overdue_customer_count: 0,
  overdue_invoice_count: 0,
  amount_usd_total: 0,
})

onMounted(async () => {
  try {
    customers.value = await listCustomers()
  } catch {
    customers.value = []
  }
  await fetchReport()
  await fetchRarReport()
  await fetchPendingPaymentReport()
})

async function exportSoCsv() {
  try {
    await fetchAuthenticatedDocument('/reports/sales-orders-export.csv', {
      mode: 'download',
      downloadFallbackName: 'sales-orders.csv',
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function exportLinesCsv() {
  try {
    await fetchAuthenticatedDocument('/reports/sales-order-lines-export.csv', {
      mode: 'download',
      downloadFallbackName: 'sales-order-lines.csv',
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function buildReportQuery() {
  const q = {}
  if (dateRange.value && dateRange.value.length === 2) {
    q.date_from = dateRange.value[0]
    q.date_to = dateRange.value[1]
  }
  if (customer.value) q.customer = customer.value
  if (dateField.value) q.date_field = dateField.value
  return q
}

function buildRarQuery() {
  const q = { payment_status: rarPaymentStatus.value, year: rarYear.value }
  if (rarDateRange.value && rarDateRange.value.length === 2) {
    q.date_from = rarDateRange.value[0]
    q.date_to = rarDateRange.value[1]
  }
  if (rarCustomer.value) q.customer = rarCustomer.value
  return q
}

async function fetchRarReport() {
  rarLoading.value = true
  try {
    const data = await fetchReportAccountsReceivable(buildRarQuery())
    rarRows.value = data.rows || []
    rarStats.value = data.summary || {
      count: 0,
      amount_faktur_usd: 0,
      amount_payment_usd: 0,
      not_yet_count: 0,
    }
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    rarLoading.value = false
  }
}

async function exportRarXlsx() {
  rarXlsxLoading.value = true
  try {
    const path = reportAccountsReceivableXlsxPath(buildRarQuery())
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null
    const r = await fetch(path, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (!r.ok) {
      const text = await r.text()
      throw new Error(text || r.statusText)
    }
    const blob = await r.blob()
    const dispo = r.headers.get('content-disposition') || ''
    const m = dispo.match(/filename="?([^";]+)"?/i)
    const name = m ? m[1] : `RAR_${rarYear.value}.xlsx`
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = name
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(t('pages.reports.rarXlsxOk'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    rarXlsxLoading.value = false
  }
}

function formatRarUsd(val) {
  if (val === null || val === undefined || val === '') return '—'
  return Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const filteredRarRows = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  if (!q || reportTab.value !== 'rar') return rarRows.value
  return rarRows.value.filter((row) =>
    Object.values(row)
      .filter((v) => v != null && v !== '')
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

function buildPendingPaymentQuery() {
  const q = { year: ppYear.value }
  if (ppAsOf.value) q.as_of = ppAsOf.value
  return q
}

async function fetchPendingPaymentReport() {
  ppLoading.value = true
  try {
    const data = await fetchReportPendingPayment(buildPendingPaymentQuery())
    ppRows.value = data.rows || []
    ppStats.value = data.summary || {
      master_count: 0,
      overdue_customer_count: 0,
      overdue_invoice_count: 0,
      amount_usd_total: 0,
    }
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    ppLoading.value = false
  }
}

async function exportPendingPaymentXlsx() {
  ppXlsxLoading.value = true
  try {
    const path = reportPendingPaymentXlsxPath(buildPendingPaymentQuery())
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null
    const r = await fetch(path, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (!r.ok) {
      const text = await r.text()
      throw new Error(text || r.statusText)
    }
    const blob = await r.blob()
    const dispo = r.headers.get('content-disposition') || ''
    const m = dispo.match(/filename="?([^";]+)"?/i)
    const name = m ? m[1] : `PendingPayment_${ppYear.value}.xlsx`
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = name
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(t('pages.reports.ppXlsxOk'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    ppXlsxLoading.value = false
  }
}

const filteredPpRows = computed(() => {
  let rows = ppRows.value
  if (ppOverdueOnly.value) {
    rows = rows.filter((row) => Number(row.amount_usd) > 0)
  }
  const q = keyword.value.trim().toLowerCase()
  if (!q || reportTab.value !== 'pending-payment') return rows
  return rows.filter((row) =>
    Object.values(row)
      .filter((v) => v != null && v !== '')
      .join(' ')
      .toLowerCase()
      .includes(q),
  )
})

function ppRowClassName({ row }) {
  return Number(row.amount_usd) > 0 ? 'report-row--highlight' : ''
}

async function fetchReport() {
  reportLoading.value = true
  try {
    const data = await fetchReportPoOrderDescription(buildReportQuery())
    reviseRows.value = data.revise_thickness || []
    productionRows.value = data.production_orders || []
    sampleRows.value = data.samples || []
    claimRows.value = data.claim_orders || []
    returnRows.value = data.return_orders || []
    subcontRows.value = data.subcont_orders || []
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    reportLoading.value = false
  }
}

async function exportDailyMarketingFile(kind) {
  dailyCsvLoading.value = true
  try {
    const q = buildReportQuery()
    const path =
      kind === 'xlsx' ? reportPoDailyMarketingXlsxPath(q) : reportPoDailyMarketingCsvPath(q)
    const fallback = kind === 'xlsx' ? 'laporan_po_harian_marketing.xlsx' : 'laporan_po_harian_marketing.csv'
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('auth_token') : null
    const r = await fetch(path, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    if (!r.ok) {
      const text = await r.text()
      throw new Error(text || r.statusText)
    }
    const blob = await r.blob()
    const dispo = r.headers.get('content-disposition') || ''
    const m = dispo.match(/filename="?([^";]+)"?/i)
    const name = m ? m[1] : fallback
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = name
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success(kind === 'xlsx' ? t('pages.reports.dailyXlsxOk') : t('pages.reports.dailyCsvOk'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    dailyCsvLoading.value = false
  }
}

function poStatusLabel(st) {
  if (st && te(`status.${st}`)) return t(`status.${st}`)
  return st || t('common.emptyValue')
}

function categoryLabel(cat) {
  if (String(cat || '').trim().toLowerCase() === 'suede') return t('status.production')
  if (cat && te(`status.${cat}`)) return t(`status.${cat}`)
  return cat || '—'
}

function poStatusTagType(st) {
  if (st === 'confirmed') return 'success'
  if (st === 'production') return 'warning'
  if (st === 'completed') return 'success'
  if (st === 'draft') return 'info'
  return ''
}

function formatDateIso(val) {
  if (val == null || val === '') return '—'
  const s = String(val)
  return s.length >= 10 ? s.slice(0, 10) : s
}

function rowMatchesKeyword(row) {
  const q = keyword.value.trim().toLowerCase()
  if (!q) return true
  return Object.values(row)
    .filter((v) => v !== null && v !== undefined)
    .join(' ')
    .toLowerCase()
    .includes(q)
}

function rowMatchesCustomer(row) {
  if (!customer.value) return true
  return (row.customer || '') === customer.value
}

function filterOrderRows(rows, catKey) {
  return (rows || []).filter((row) => {
    if (category.value && category.value !== catKey) return false
    return rowMatchesKeyword(row) && rowMatchesCustomer(row)
  })
}

const showReviseSection = computed(() => !category.value)

function showOrderSection(catKey) {
  return !category.value || category.value === catKey
}

const filteredReviseRows = computed(() =>
  reviseRows.value.filter((row) => rowMatchesKeyword(row) && rowMatchesCustomer(row)),
)

const filteredProductionRows = computed(() => {
  if (category.value && category.value !== 'production') return []
  return productionRows.value.filter((row) => rowMatchesKeyword(row) && rowMatchesCustomer(row))
})

const filteredSampleRows = computed(() => filterOrderRows(sampleRows.value, 'sample'))
const filteredClaimRows = computed(() => filterOrderRows(claimRows.value, 'claim'))
const filteredReturnRows = computed(() => filterOrderRows(returnRows.value, 'return'))
const filteredSubcontRows = computed(() => filterOrderRows(subcontRows.value, 'subcont'))

const productionQtySum = computed(() =>
  filteredProductionRows.value.reduce((s, r) => s + (Number(r.qty) || 0), 0),
)
const sampleQtySum = computed(() => filteredSampleRows.value.reduce((s, r) => s + (Number(r.qty) || 0), 0))

const extraCategorySections = computed(() => {
  const specs = [
    { key: 'claim', title: t('status.claim'), tagType: 'danger', rows: filteredClaimRows.value, totalLabel: t('pages.reports.totalClaim') },
    { key: 'return', title: t('status.return'), tagType: 'warning', rows: filteredReturnRows.value, totalLabel: t('pages.reports.totalReturn') },
    { key: 'subcont', title: t('status.subcont'), tagType: 'info', rows: filteredSubcontRows.value, totalLabel: t('pages.reports.totalSubcont') },
  ]
  return specs
    .filter((s) => showOrderSection(s.key))
    .map((s) => ({ ...s, qtySum: s.rows.reduce((acc, r) => acc + (Number(r.qty) || 0), 0) }))
})

const reportStats = computed(() => ({
  revise: filteredReviseRows.value.length,
  production: filteredProductionRows.value.length,
  sample: filteredSampleRows.value.length,
  claim: filteredClaimRows.value.length,
  return: filteredReturnRows.value.length,
  subcont: filteredSubcontRows.value.length,
}))

function formatDateTime(val) {
  if (val == null || val === '') return '—'
  const s = String(val)
  if (s.length >= 16) return `${s.slice(0, 10)} ${s.slice(11, 16)}`
  return s.length >= 10 ? s.slice(0, 10) : s
}

function formatQty(n) {
  if (n === null || n === undefined) return '0'
  return Number(n).toLocaleString()
}

async function runGenerateReport() {
  await fetchReport()
  ElMessage.success(t('pages.reports.generated'))
}

function resetFilters() {
  dateRange.value = []
  customer.value = ''
  category.value = ''
  dateField.value = 'order'
  keyword.value = ''
  fetchReport()
}

function printReport() {
  window.print()
}

function handleExportCommand(command) {
  if (command === 'daily') exportDailyMarketingFile('csv')
  else if (command === 'daily-xlsx') exportDailyMarketingFile('xlsx')
  else if (command === 'so') exportSoCsv()
  else if (command === 'lines') exportLinesCsv()
}
</script>

<style scoped>
.reports-action-bar {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
  padding: 12px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #f8fafc;
}

@media (min-width: 768px) {
  .reports-action-bar {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }
}

.reports-action-bar__hint {
  margin: 0;
  font-size: 12px;
  line-height: 1.45;
  color: #64748b;
}

.reports-action-bar__buttons {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.report-card__filter {
  margin: 0;
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-top: none;
  border-bottom: 1px solid #e2e8f0;
}

.reports-filter-actions__row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  width: 100%;
}

.reports-filter-actions__row .el-button {
  flex: 1 1 auto;
  min-width: 7rem;
}

.report-card__body {
  padding: 16px;
  background: #fff;
}

.report-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: 20px 0 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}

.report-section-head:first-child {
  margin-top: 0;
}

.report-section-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
}

.report-section-sub {
  margin: 4px 0 0;
  font-size: 12px;
  font-weight: 400;
  color: #64748b;
}

.report-table-scroll {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 4px;
  -webkit-overflow-scrolling: touch;
}

.report-table {
  margin-bottom: 12px;
}

.report-table--wide {
  min-width: 2100px;
}

.report-total-line {
  margin: 0 0 20px;
  text-align: right;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #0f172a;
}

.w-full {
  width: 100%;
}

@media print {
  .reports-action-bar,
  .filter-panel,
  .admin-stats-grid,
  .admin-scroll-hint {
    display: none !important;
  }
}
</style>
