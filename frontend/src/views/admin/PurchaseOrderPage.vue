<template>
  <AdminSection :title="t('pages.po.title')" :subtitle="t('pages.po.subtitle')">
    <template #actions>
      <el-input
        v-model="keyword"
        :placeholder="t('pages.po.searchPlaceholder')"
        clearable
        class="po-toolbar-search"
      />
      <span v-if="loading" class="text-xs text-slate-500">{{ t('common.loadingData') }}</span>
      <el-button :icon="Download" @click="openExportHint">{{ t('common.export') }}</el-button>
      <el-button v-if="canManage" type="primary" :icon="Plus" @click="openCreateDialog">{{ t('common.create') }}</el-button>
    </template>

    <div class="filter-panel mb-4">
      <p class="filter-panel__title">{{ t('common.filter') }}</p>
      <el-form class="filter-form" label-position="top">
        <el-row :gutter="12">
          <el-col :xs="24" :sm="12" :md="9" :lg="7">
            <el-form-item :label="t('common.customer')">
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

          <el-col :xs="24" :sm="12" :md="7" :lg="5">
            <el-form-item :label="t('common.status')">
              <el-select v-model="filterStatus" clearable class="w-full" :placeholder="t('common.status')">
                <el-option :label="t('status.draft')" value="draft" />
                <el-option :label="t('status.confirmed')" value="confirmed" />
                <el-option :label="t('status.production')" value="production" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="8" :lg="6" class="po-filter-action-col">
            <el-form-item label="&nbsp;">
              <el-button class="w-full" @click="resetFilter">{{ t('common.reset') }}</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <el-table
      :data="filteredRows"
      v-loading="loading"
      border
      stripe
      size="small"
      class="admin-table"
      table-layout="auto"
      :empty-text="t('pages.po.tableEmpty')"
    >
      <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
      <el-table-column prop="po_number" :label="t('common.poNo')" min-width="160" show-overflow-tooltip />
      <el-table-column prop="po_customer_ref" :label="t('pages.po.poCustomerRef')" min-width="140" show-overflow-tooltip />
      <el-table-column prop="customerName" :label="t('common.customer')" min-width="200" show-overflow-tooltip />
      <el-table-column prop="buyer" :label="t('common.buyer')" min-width="120" show-overflow-tooltip />
      <el-table-column prop="material_hint" :label="t('common.material')" min-width="140" show-overflow-tooltip />
      <el-table-column prop="po_category" :label="t('common.category')" min-width="110" align="center">
        <template #default="{ row }">
          <el-tag size="small" type="info" effect="plain">{{ t(`status.${row.po_category}`) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="etd" :label="t('common.etd')" min-width="110" align="center" />
      <el-table-column prop="mkt_workflow_stage" :label="t('pages.po.mktFlow')" min-width="140" show-overflow-tooltip>
        <template #default="{ row }">{{ row.mkt_workflow_stage || t('common.emptyValue') }}</template>
      </el-table-column>
      <el-table-column prop="status" :label="t('common.status')" min-width="120" align="center">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ t(`status.${row.status}`) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="200" align="center" fixed="right">
        <template #default="{ row }">
          <div class="po-row-actions">
            <el-tooltip :content="t('common.detail')" placement="top">
              <el-button :icon="View" link type="primary" :aria-label="t('common.detail')" @click="openDetailDialog(row)" />
            </el-tooltip>
            <el-tooltip v-if="canManage" :content="t('common.edit')" placement="top">
              <el-button :icon="EditPen" link type="warning" :aria-label="t('common.edit')" @click="openEditDialog(row)" />
            </el-tooltip>
            <el-tooltip v-if="canManage" :content="t('pages.po.duplicatePo')" placement="top">
              <el-button
                :icon="CopyDocument"
                link
                type="primary"
                :aria-label="t('pages.po.duplicatePo')"
                @click="onDuplicatePo(row)"
              />
            </el-tooltip>
            <el-tooltip :content="t('common.print')" placement="top">
              <el-button :icon="Printer" link :aria-label="t('common.print')" @click="openPrintDialog(row)" />
            </el-tooltip>
            <el-tooltip v-if="canManage" :content="t('common.delete')" placement="top">
              <el-button :icon="Delete" link type="danger" :aria-label="t('common.delete')" @click="removeRow(row)" />
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="formDialogVisible"
      :title="isEditMode ? `${t('pages.poEntry.title')} ${t('pages.po.editSuffix')}` : t('pages.poEntry.title')"
      width="1100px"
      destroy-on-close
      align-center
      class="po-dialog"
    >
      <el-form label-position="top" class="po-dialog-form">
        <el-divider content-position="left">{{ t('pages.po.customerSoSection') }}</el-divider>
        <el-row :gutter="12">
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.customer')" required>
              <el-select
                v-model="formModel.customer_id"
                filterable
                clearable
                class="w-full"
                :placeholder="t('common.placeholder.customer')"
                :disabled="Boolean(brandLockedCustomerId)"
                @change="onCustomerChange"
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
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.poNo')">
              <el-input
                :model-value="isEditMode ? formModel.po_number : t('common.autoGenerate')"
                disabled
              />
              <span class="text-xs text-slate-500">{{ t('pages.po.autoGenerateHint') }}</span>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.po.poCustomerRef')">
              <el-input v-model="formModel.po_customer_ref" clearable maxlength="255" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.po.brand')">
              <el-select
                v-model="formModel.brand_id"
                clearable
                filterable
                class="w-full"
                :placeholder="t('pages.po.brand')"
                @change="onBrandChange"
              >
                <el-option
                  v-for="b in brandsFiltered"
                  :key="b.id"
                  :label="`${b.code || b.id} — ${b.name || ''}`"
                  :value="b.id"
                />
              </el-select>
              <div class="mt-2">
                <el-button type="primary" link :icon="Plus" @click="openInlineBrandDialog">
                  {{ t('pages.po.addBrandInline') }}
                </el-button>
              </div>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.poCategory')">
              <el-select v-model="formModel.po_category" class="w-full" :placeholder="t('common.category')">
                <el-option :label="t('status.production')" value="production" />
                <el-option :label="t('status.subkon')" value="subcont" />
                <el-option :label="t('status.retur')" value="return" />
                <el-option :label="t('status.sample')" value="sample" />
                <el-option :label="t('status.claim')" value="claim" />
                <el-option :label="t('status.suede')" value="suede" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.orderDate')">
              <el-date-picker v-model="formModel.order_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.buyer')">
              <el-select
                v-model="formModel.buyer"
                filterable
                class="w-full"
                :placeholder="t('common.placeholder.buyer')"
              >
                <el-option v-for="b in buyerCodesFiltered" :key="b" :label="b" :value="b" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.po.headerEtd')">
              <el-date-picker v-model="formModel.etd" type="date" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.status')">
              <el-select v-model="formModel.status" class="w-full">
                <el-option :label="t('status.draft')" value="draft" />
                <el-option :label="t('status.confirmed')" value="confirmed" />
                <el-option :label="t('status.production')" value="production" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-form-item :label="t('common.remark')">
              <el-input v-model="formModel.remark" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.po.billingAddress')">
              <el-input v-model="formModel.billing_address" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.po.deliveryAddress')">
              <el-input v-model="formModel.delivery_address" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-divider content-position="left">{{ t('pages.po.materialFollowUpSection') }}</el-divider>
          </el-col>
          <el-col :xs="24" :md="18">
            <el-form-item :label="t('pages.po.materialFollowUpNote')">
              <el-input
                v-model="formModel.material_followup_remark"
                type="textarea"
                :rows="2"
                :placeholder="t('pages.po.materialFollowUpPlaceholder')"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="6">
            <el-form-item :label="t('pages.po.done')">
              <el-switch v-model="formModel.material_followup_done" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">{{ t('pages.po.materialLineOne') }}</el-divider>
        <p class="mb-2 text-xs text-slate-500">{{ t('pages.po.materialEditableHint') }}</p>
        <el-row :gutter="12">
          <el-col :xs="24" :md="12">
            <el-form-item :label="`${t('common.material')} (${t('common.masterLabel')})`">
              <el-select
                v-model="formModel.master_item_id"
                clearable
                filterable
                class="w-full"
                :placeholder="t('pages.po.masterItemPlaceholder')"
                @change="onMasterItemChange"
              >
                <el-option
                  v-for="it in masterItems"
                  :key="it.id"
                  :label="`${it.item_code} — ${it.material_name || ''}`"
                  :value="it.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.material')">
              <el-input v-model="formModel.material_name" :placeholder="t('common.placeholder.material')" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.thickness')">
              <el-select
                v-model="formModel.thickness_text"
                clearable
                filterable
                allow-create
                class="w-full"
                :placeholder="t('common.placeholder.thickness')"
              >
                <el-option label="1.0-1.2" value="1.0-1.2" />
                <el-option label="1.2-1.4" value="1.2-1.4" />
                <el-option label="1.4-1.6" value="1.4-1.6" />
                <el-option label="1.6-1.8" value="1.6-1.8" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.color')">
              <el-input v-model="formModel.color" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.po.colorFamily')">
              <el-select v-model="formModel.color_family" clearable class="w-full">
                <el-option :label="t('pages.po.colorFamilyBlack')" value="black" />
                <el-option :label="t('pages.po.colorFamilyColor')" value="color" />
                <el-option :label="t('pages.po.colorFamilyFluorescent')" value="fluorescent" />
              </el-select>
              <span class="mt-1 block text-xs text-slate-500">{{ t('pages.po.colorFamilyHint') }}</span>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.po.emboss')">
              <el-input v-model="formModel.emboss" clearable />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.po.virSoftnessType')">
              <el-input v-model="formModel.vir_softness_type" clearable />
              <span class="mt-1 block text-xs text-slate-500">{{ t('pages.po.suggestVirSoft') }}</span>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.softness')">
              <el-select v-model="formModel.softness" clearable filterable allow-create class="w-full">
                <el-option label="Soft" value="Soft" />
                <el-option label="Medium" value="Medium" />
                <el-option label="Hard" value="Hard" />
                <el-option label="Extra Soft" value="Extra Soft" />
                <el-option label="Super Soft" value="Super Soft" />
              </el-select>
              <span class="mt-1 block text-xs text-slate-500">{{ t('pages.po.softnessRangesHint') }}</span>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.colorReference')">
              <el-input v-model="formModel.color_reference" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.backing')">
              <el-input v-model="formModel.backing" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.quantityOrder')">
              <el-input v-model="formModel.quantity_order" type="number" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.styleArticle')">
              <el-input v-model="formModel.style_article" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.model')">
              <el-input v-model="formModel.model" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.po.lineEtd')">
              <el-date-picker v-model="formModel.line_etd" type="date" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.po.thiLineRef')">
              <div class="flex flex-wrap items-center gap-2">
                <el-input v-model="formModel.thi_line_ref" class="min-w-[200px] flex-1" clearable />
                <el-button size="small" @click="applyLotPrefix">{{ t('pages.po.applyLotPrefix') }}</el-button>
              </div>
              <span class="mt-1 block text-xs text-slate-500">{{ t('pages.po.lotPrefixHint') }}</span>
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-form-item :label="t('pages.po.detailRemark')">
              <el-input v-model="formModel.detail_remark" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('pages.po.unitPriceUsd')">
              <el-input
                v-model.number="formModel.unit_price_input"
                type="number"
                :step="0.01"
                :controls="false"
                class="w-full"
              />
              <div class="mt-1 flex items-center gap-2">
                <span v-if="previewResolvedUnitPrice.value != null" class="text-xs text-slate-500">
                  {{ t('pages.po.autoResolved') }}: {{ previewResolvedUnitPrice.value }}
                </span>
                <el-tag v-if="formModel.unit_price_input && previewResolvedUnitPrice.value != null && formModel.unit_price_input !== previewResolvedUnitPrice.value" size="small" type="warning">
                  {{ t('pages.po.overridden') }}
                </el-tag>
              </div>
            </el-form-item>
          </el-col>
          <el-col :xs="24">
            <el-form-item :label="t('pages.po.etdSchedule')">
              <el-table :data="etdScheduleRows" border size="small" class="etd-schedule-table">
                <el-table-column :label="t('common.noLabel')" width="60" align="center">
                  <template #default="{ $index }">{{ $index + 1 }}{{ ordinalSuffix($index + 1) }}</template>
                </el-table-column>
                <el-table-column :label="t('pages.po.etdQty')" width="120">
                  <template #default="{ $index }">
                    <el-input-number
                      v-model="etdScheduleRows[$index].qty"
                      :min="0"
                      :controls="false"
                      size="small"
                      class="w-full"
                    />
                  </template>
                </el-table-column>
                <el-table-column :label="t('pages.po.etdDate')">
                  <template #default="{ $index }">
                    <el-date-picker
                      v-model="etdScheduleRows[$index].date"
                      type="date"
                      size="small"
                      class="w-full"
                      value-format="YYYY-MM-DD"
                    />
                  </template>
                </el-table-column>
              </el-table>
              <div class="mt-2">
                <el-button size="small" @click="clearEtdSchedule">{{ t('common.clear') }}</el-button>
                <el-button size="small" type="primary" @click="autoFillEtdSchedule">{{ t('pages.po.autoFillFromEtd') }}</el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        <div class="po-line-actions">
          <el-button :icon="Plus" @click="pushCurrentLine(false)">{{ t('common.add') }} Line</el-button>
          <el-button :icon="DocumentCopy" @click="pushCurrentLine(true)">{{ t('pages.po.copyLine') }}</el-button>
          <el-button :icon="DocumentCopy" @click="openCopyItemDialog">{{ t('pages.po.copyItemFromOtherPo') }}</el-button>
        </div>
        <el-table
          v-if="draftLines.length"
          :data="draftLines"
          border
          stripe
          size="small"
          class="admin-table mt-3"
          table-layout="auto"
        >
          <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
          <el-table-column prop="material_name" :label="t('common.material')" min-width="160" show-overflow-tooltip />
          <el-table-column prop="thickness_text" :label="t('common.thickness')" width="100" />
          <el-table-column prop="color" :label="t('common.color')" width="88" />
          <el-table-column prop="color_family" :label="t('pages.po.colorFamily')" width="120" show-overflow-tooltip>
            <template #default="{ row }">{{ colorFamilyLabel(row.color_family) }}</template>
          </el-table-column>
          <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="96" />
          <el-table-column prop="unit_price" :label="t('pages.po.unitPriceUsd')" width="100" align="right">
            <template #default="{ row }">{{ row.unit_price != null ? row.unit_price : '—' }}</template>
          </el-table-column>
          <el-table-column prop="line_etd" :label="t('pages.po.lineEtd')" width="112" />
          <el-table-column prop="thi_line_ref" :label="t('pages.po.thiLineRef')" min-width="100" show-overflow-tooltip />
          <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="120" show-overflow-tooltip />
          <el-table-column :label="t('common.actions')" width="90" align="center">
            <template #default="{ $index }">
              <el-tooltip :content="t('common.delete')" placement="top">
                <el-button
                  link
                  type="danger"
                  :icon="Delete"
                  :aria-label="t('common.delete')"
                  @click="removeDraftLine($index)"
                />
              </el-tooltip>
            </template>
          </el-table-column>
        </el-table>
      </el-form>
      <template #footer>
        <div class="po-dialog-footer">
          <el-button @click="formDialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button v-if="canManage" type="primary" :loading="saving" @click="submitForm">{{ t('common.savePo') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailDialogVisible"
      :title="t('pages.poDetail.title')"
      width="900px"
      destroy-on-close
      align-center
      class="po-dialog"
    >
      <el-descriptions v-if="detailView" :column="2" border size="small">
        <el-descriptions-item :label="t('common.poNo')">{{ detailView.po_number }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.status')">{{ statusLabel(detailView.status) }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.po.poCustomerRef')">{{ detailView.po_customer_ref || t('common.emptyValue') }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.customer')">{{ detailView.customerName }}</el-descriptions-item>
        <el-descriptions-item :label="t('common.buyer')">{{ detailView.buyer || t('common.emptyValue') }}</el-descriptions-item>
        <el-descriptions-item :label="t('pages.po.headerEtd')">{{ detailView.etd || t('common.emptyValue') }}</el-descriptions-item>
      </el-descriptions>
      <p class="mt-2 text-xs text-slate-500">{{ t('pages.poDetail.lineRevisionHint') }}</p>
      <el-table
        v-if="detailLines.length"
        :data="detailLines"
        class="mt-4"
        border
        size="small"
        table-layout="auto"
        max-height="360"
      >
        <el-table-column prop="material_name" :label="t('common.material')" min-width="130" show-overflow-tooltip />
        <el-table-column prop="thickness_text" :label="t('common.thickness')" width="100" />
        <el-table-column prop="color" :label="t('common.color')" width="88" />
        <el-table-column prop="color_family" :label="t('pages.po.colorFamily')" width="120" show-overflow-tooltip>
          <template #default="{ row }">{{ colorFamilyLabel(row.color_family) }}</template>
        </el-table-column>
        <el-table-column prop="emboss" :label="t('pages.po.emboss')" width="88" show-overflow-tooltip />
        <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="96" />
        <el-table-column prop="unit_price" :label="t('pages.po.unitPriceUsd')" width="100" align="right">
          <template #default="{ row }">{{ row.unit_price != null ? row.unit_price : t('common.emptyValue') }}</template>
        </el-table-column>
        <el-table-column prop="line_etd" :label="t('pages.po.lineEtd')" width="112" />
        <el-table-column prop="thi_line_ref" :label="t('pages.po.thiLineRef')" min-width="110" show-overflow-tooltip />
        <el-table-column prop="style_article" :label="t('common.styleArticle')" min-width="100" show-overflow-tooltip />
        <el-table-column prop="model" :label="t('common.model')" width="96" show-overflow-tooltip />
      </el-table>
      <div v-if="detailAudit.length" class="mt-4 rounded border border-slate-200 bg-white p-3">
        <div class="mb-2 text-sm font-semibold text-slate-700">{{ t('pages.po.lineRevisionHistory') }}</div>
        <el-timeline>
          <el-timeline-item
            v-for="a in detailAudit"
            :key="a.id"
            :timestamp="a.created_at ? String(a.created_at).replace('T', ' ').slice(0, 19) : ''"
          >
            <div class="text-sm">
              <b>{{ a.action }}</b>
              <span v-if="a.entity_type === 'sales_order_line'" class="text-slate-400"> ({{ t('pages.poDetail.auditLine') }} #{{ a.entity_id }})</span>
              <span class="text-slate-500"> {{ t('common.dashSeparator') }} {{ a.actor || t('common.system') }}</span>
            </div>
            <div v-if="a.before || a.after" class="mt-1 text-xs text-slate-600">
              <pre class="whitespace-pre-wrap break-words">{{ prettyAudit(a) }}</pre>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
      <template #footer>
        <el-button type="primary" @click="detailDialogVisible = false">{{ t('pages.customers.closeDetail') }}</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="printDialogVisible"
      :title="`${t('common.print')} ${t('menu.po')}`"
      width="760px"
      destroy-on-close
      align-center
      class="po-dialog"
    >
      <div class="rounded border border-slate-200 p-4">
        <h3 class="mb-2 text-lg font-semibold">{{ selectedRow.po_number }}</h3>
        <p><b>{{ t('common.customer') }}:</b> {{ selectedRow.customerName }}</p>
        <p><b>{{ t('common.buyer') }}:</b> {{ selectedRow.buyer }}</p>
        <p><b>{{ t('common.poCategory') }}:</b> {{ statusLabel(selectedRow.po_category) }}</p>
        <p><b>{{ t('common.material') }}:</b> {{ selectedRow.material_hint }}</p>
        <p><b>{{ t('common.etd') }}:</b> {{ selectedRow.etd }}</p>
      </div>
      <template #footer>
        <div class="po-dialog-footer">
          <el-button @click="printDialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :icon="Printer" @click="printPage">{{ t('common.print') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="brandDialogVisible"
      :title="t('pages.po.addBrandInline')"
      width="460px"
      destroy-on-close
      align-center
    >
      <el-form label-position="top">
        <el-form-item :label="t('common.code')" required>
          <el-input v-model="inlineBrand.code" maxlength="50" />
        </el-form-item>
        <el-form-item :label="t('common.name')">
          <el-input v-model="inlineBrand.name" maxlength="255" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="po-dialog-footer">
          <el-button @click="brandDialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :loading="brandSaving" @click="submitInlineBrand">{{ t('common.save') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="copyItemDialogVisible"
      :title="t('pages.po.copyItemFromOtherPo')"
      width="900px"
      destroy-on-close
      align-center
    >
      <el-form label-position="top">
        <el-form-item :label="t('common.customer')">
          <el-select
            v-model="copyItemCustomerId"
            clearable
            filterable
            class="w-full"
            :placeholder="t('common.placeholder.customer')"
            @change="onCopyItemCustomerChange"
          >
            <el-option
              v-for="c in customers"
              :key="c.id"
              :label="customerOptionLabel(c)"
              :value="c.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <el-table
        v-if="copyItemSourcePo.length"
        :data="copyItemSourcePo"
        border
        size="small"
        max-height="300"
        @selection-change="onCopyItemSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="source_po_number" :label="t('common.poNo')" width="150" />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="160" />
        <el-table-column prop="thickness_text" :label="t('common.thickness')" width="100" />
        <el-table-column prop="color" :label="t('common.color')" width="100" />
        <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="100" />
      </el-table>
      <div v-else class="text-center text-slate-500 py-8">
        {{ t('pages.po.selectCustomerToSeeItems') }}
      </div>
      <template #footer>
        <div class="po-dialog-footer">
          <el-button @click="copyItemDialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :disabled="!copyItemSelected.length" @click="addCopiedItems">
            {{ t('pages.po.addSelectedItems') }} ({{ copyItemSelected.length }})
          </el-button>
        </div>
      </template>
    </el-dialog>
  </AdminSection>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Download,
  View,
  EditPen,
  Delete,
  Printer,
  DocumentCopy,
  CopyDocument,
} from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { canWrite } from '../../security/permissions'
import {
  addPoDetail,
  createBrand,
  createPo,
  deletePoDetail,
  deletePo,
  duplicatePo,
  getAllowedBrands,
  listBrands,
  listBrandBuyers,
  listBuyerPriceLists,
  listCustomers,
  listMasterItems,
  listPo,
  listPoDetails,
  listPoForCopy,
  listAuditLogs,
  resolveBuyerUnitPrice,
  setPoDetailDeliverySchedules,
  toIsoDate,
  updatePo,
  updatePoDetail,
} from '../../api/client'

const { t } = useI18n()
const route = useRoute()
const canManage = canWrite('po')

const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const filterCustomerId = ref(null)
const filterStatus = ref('')
const customers = ref([])
const brands = ref([])
const masterItems = ref([])
const buyerCodes = ref(['NB', 'ADIDAS', 'NIKE', 'UA'])
const brandBuyerCodes = ref([])
const brandLockedCustomerId = ref(null)
const allowedBrandIds = ref([])

const rows = ref([])
const brandDialogVisible = ref(false)
const brandSaving = ref(false)
const inlineBrand = reactive({
  code: '',
  name: '',
})

const customerName = (id) => {
  const c = customers.value.find((x) => x.id === id)
  return c ? `${c.code || ''} ${c.name || ''}`.trim() : t('common.emptyValue')
}

function customerOptionLabel(c) {
  const base = [c.code, c.name].filter(Boolean).join(' — ')
  if (!base) return String(c.id)
  return c.city ? `${base} ${t('common.dotSeparator')} ${c.city}` : base
}

async function enrichPoRows(headers) {
  const detailsLists = await Promise.all(
    headers.map((h) => listPoDetails(h.id).catch(() => [])),
  )
  return headers.map((h, i) => {
    const first = detailsLists[i][0] || {}
    return {
      ...h,
      customerName: customerName(h.customer_id),
      material_hint: first.material_name || t('common.emptyValue'),
      etd: h.etd ? String(h.etd).slice(0, 10) : '',
    }
  })
}

async function load() {
  loading.value = true
  try {
    const [cust, br, mi, bpl, pos] = await Promise.all([
      listCustomers(),
      listBrands(),
      listMasterItems(),
      listBuyerPriceLists().catch(() => []),
      listPo(),
    ])
    customers.value = cust
    brands.value = br
    masterItems.value = mi
    const extraBuyers = [...new Set(bpl.map((x) => x.buyer_code).filter(Boolean))]
    buyerCodes.value = [...new Set([...buyerCodes.value, ...extraBuyers])]
    rows.value = await enrichPoRows(pos)
  } catch (e) {
    ElMessage.error(e.message || t('pages.po.loadFailed'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await load()
  const poIdRaw = route.query.po_id
  const poId = Number(poIdRaw)
  if (!Number.isNaN(poId) && poId > 0) {
    const target = rows.value.find((r) => Number(r.id) === poId)
    if (target) await openDetailDialog(target)
  }
})

const brandsFiltered = computed(() => {
  const cid = formModel.customer_id
  let filtered = brands.value
  if (cid) {
    filtered = brands.value.filter((b) => !b.customer_id || b.customer_id === cid)
  }
  if (allowedBrandIds.value.length > 0) {
    filtered = filtered.filter((b) => allowedBrandIds.value.includes(b.id))
  }
  return filtered
})

const buyerCodesFiltered = computed(() => {
  if (brandBuyerCodes.value.length) return brandBuyerCodes.value
  return buyerCodes.value
})

const filteredRows = computed(() =>
  rows.value.filter((row) => {
    const customerMatch = !filterCustomerId.value || row.customer_id === filterCustomerId.value
    const statusMatch = !filterStatus.value || row.status === filterStatus.value
    const q = keyword.value.trim().toLowerCase()
    const keywordMatch =
      !q ||
      [row.po_number, row.customerName, row.buyer, row.material_hint]
        .join(' ')
        .toLowerCase()
        .includes(q)
    return customerMatch && statusMatch && keywordMatch
  }),
)

const resetFilter = () => {
  filterCustomerId.value = null
  filterStatus.value = ''
  keyword.value = ''
}

const statusType = (status) => {
  if (status === 'confirmed') return 'success'
  if (status === 'production') return 'warning'
  return 'info'
}

const statusLabel = (status) => (status ? t(`status.${status}`) : t('common.emptyValue'))

const formDialogVisible = ref(false)
const isEditMode = ref(false)
const editingPoId = ref(null)
const editingDetailIds = ref([])
const draftLines = ref([])

const copyItemDialogVisible = ref(false)
const copyItemCustomerId = ref(null)
const copyItemSourcePo = ref([])
const copyItemSelected = ref([])

const etdScheduleRows = ref([
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
  { qty: null, date: '' },
])

function ordinalSuffix(index) {
  const j = index % 10
  const k = index % 100
  if (j === 1 && k !== 11) return 'st'
  if (j === 2 && k !== 12) return 'nd'
  if (j === 3 && k !== 13) return 'rd'
  return 'th'
}

function clearEtdSchedule() {
  etdScheduleRows.value = Array.from({ length: 12 }, () => ({ qty: null, date: '' }))
}

function autoFillEtdSchedule() {
  const qty = formModel.quantity_order ? Number(formModel.quantity_order) : 0
  if (!qty) return
  const eachQty = Math.floor(qty / 12)
  const remainder = qty % 12
  const baseDate = formModel.line_etd ? new Date(formModel.line_etd) : new Date()
  etdScheduleRows.value = Array.from({ length: 12 }, (_, i) => {
    const d = new Date(baseDate)
    d.setDate(d.getDate() + i * 7)
    return {
      qty: i < remainder ? eachQty + 1 : eachQty,
      date: i < remainder && i === 0 ? formModel.line_etd : d.toISOString().slice(0, 10),
    }
  })
}

const formModel = reactive({
  po_number: '',
  customer_id: null,
  brand_id: null,
  po_category: 'production',
  order_date: '',
  buyer: '',
  etd: '',
  po_customer_ref: '',
  remark: '',
  billing_address: '',
  delivery_address: '',
  status: 'draft',
  master_item_id: null,
  material_name: '',
  thickness_text: '',
  color: '',
  color_family: null,
  emboss: '',
  vir_softness_type: '',
  softness: '',
  color_reference: '',
  backing: '',
  quantity_order: '',
  style_article: '',
  model: '',
  line_etd: '',
  detail_remark: '',
  thi_line_ref: '',
  material_followup_remark: '',
  material_followup_done: false,
  unit_price_input: null,
  autoPricingEnabled: true,
})

const pricePreviewLoading = ref(false)
const previewResolvedUnitPrice = ref(null)

let pricePreviewTimer = null
function schedulePricePreview() {
  clearTimeout(pricePreviewTimer)
  pricePreviewTimer = setTimeout(() => {
    fetchResolvedUnitPricePreview()
  }, 400)
}

async function fetchResolvedUnitPricePreview() {
  const b = (formModel.buyer || '').trim()
  if (!b) {
    previewResolvedUnitPrice.value = null
    return
  }
  pricePreviewLoading.value = true
  try {
    const r = await resolveBuyerUnitPrice({
      buyer_code: b,
      material_name: formModel.material_name || null,
      color: formModel.color || null,
      style_article: formModel.style_article || null,
      thickness_text: formModel.thickness_text || null,
      color_family: formModel.color_family || null,
    })
    previewResolvedUnitPrice.value = r.unit_price != null ? Number(r.unit_price) : null
  } catch {
    previewResolvedUnitPrice.value = null
  } finally {
    pricePreviewLoading.value = false
  }
}

const displayResolvedUnitPrice = computed(() => {
  if (pricePreviewLoading.value) return '…'
  if (previewResolvedUnitPrice.value != null) return String(previewResolvedUnitPrice.value)
  return '—'
})

function colorFamilyLabel(v) {
  if (!v) return t('common.emptyValue')
  const k = String(v).toLowerCase()
  if (k === 'black') return t('pages.po.colorFamilyBlack')
  if (k === 'color') return t('pages.po.colorFamilyColor')
  if (k === 'fluorescent') return t('pages.po.colorFamilyFluorescent')
  return String(v)
}

function applyVirSoftDefault() {
  const b = (formModel.buyer || '').toUpperCase()
  if (!b) return
  if (b.includes('NIKE')) {
    if (!formModel.vir_softness_type) formModel.vir_softness_type = 'Vir Soft'
  } else if (!formModel.vir_softness_type) {
    formModel.vir_softness_type = 'Soft'
  }
}

function applyLotPrefix() {
  const cat = formModel.po_category
  let p = ''
  if (cat === 'subcont') p = 'SC-'
  else if (cat === 'return') p = 'RTN-'
  else if (cat === 'claim') p = 'CLM-'
  else if (cat === 'sample') p = 'SMP-'
  else if (cat === 'suede') p = 'SDE-'
  else if (cat === 'production') {
    const vt = (formModel.vir_softness_type || '').toLowerCase()
    if (vt.includes('vir') || vt.includes('pu')) p = 'PU-'
    else p = 'THI-'
  }
  if (!p) return
  const cur = (formModel.thi_line_ref || '').trim()
  if (!cur) {
    formModel.thi_line_ref = p
    return
  }
  if (cur.startsWith(p)) return
  formModel.thi_line_ref = p + cur
}

watch(
  () => formModel.buyer,
  () => {
    formModel.vir_softness_type = ''
    previewResolvedUnitPrice.value = null
    schedulePricePreview()
    applyVirSoftDefault()
  },
)

watch(
  () => [
    formModel.material_name,
    formModel.color,
    formModel.style_article,
    formModel.thickness_text,
    formModel.color_family,
  ],
  () => schedulePricePreview(),
)

watch(
  () => formModel.po_category,
  (newCategory) => {
    const isSubkonOrRetur = newCategory === 'subcont' || newCategory === 'return'
    formModel.autoPricingEnabled = !isSubkonOrRetur
    if (isSubkonOrRetur) {
      formModel.unit_price_input = null
    }
  },
)

function resetForm() {
  formModel.po_number = ''
  formModel.customer_id = null
  formModel.brand_id = null
  formModel.po_category = 'production'
  formModel.order_date = ''
  formModel.buyer = ''
  formModel.etd = ''
  formModel.po_customer_ref = ''
  formModel.remark = ''
  formModel.billing_address = ''
  formModel.delivery_address = ''
  formModel.status = 'draft'
  formModel.master_item_id = null
  formModel.material_name = ''
  formModel.thickness_text = ''
  formModel.color = ''
  formModel.color_family = null
  formModel.emboss = ''
  formModel.vir_softness_type = ''
  formModel.softness = ''
  formModel.color_reference = ''
  formModel.backing = ''
  formModel.quantity_order = ''
  formModel.style_article = ''
  formModel.model = ''
  formModel.line_etd = ''
  formModel.detail_remark = ''
  formModel.thi_line_ref = ''
  formModel.material_followup_remark = ''
  formModel.material_followup_done = false
  formModel.autoPricingEnabled = true
  editingPoId.value = null
  editingDetailIds.value = []
  draftLines.value = []
  brandLockedCustomerId.value = null
  previewResolvedUnitPrice.value = null
  clearEtdSchedule()
}

async function onCustomerChange() {
  if (brandLockedCustomerId.value) {
    formModel.customer_id = brandLockedCustomerId.value
    return
  }
  formModel.brand_id = null
  brandBuyerCodes.value = []
  formModel.buyer = ''
  allowedBrandIds.value = []
  const cid = formModel.customer_id
  if (cid) {
    try {
      const allowed = await getAllowedBrands(cid)
      allowedBrandIds.value = allowed.map((b) => b.id)
    } catch {
      allowedBrandIds.value = []
    }
  }
}

async function onBrandChange(brandId) {
  brandBuyerCodes.value = []
  brandLockedCustomerId.value = null
  if (!brandId) return
  try {
    const selectedBrand = brands.value.find((b) => b.id === brandId)
    if (selectedBrand?.customer_id) {
      brandLockedCustomerId.value = selectedBrand.customer_id
      formModel.customer_id = selectedBrand.customer_id
    }
    const rows = await listBrandBuyers(brandId)
    brandBuyerCodes.value = rows.map((x) => x.buyer_code).filter(Boolean)
    if (formModel.buyer && brandBuyerCodes.value.length && !brandBuyerCodes.value.includes(formModel.buyer)) {
      formModel.buyer = ''
    }
  } catch {
    brandBuyerCodes.value = []
  }
}

function onMasterItemChange(masterItemId) {
  const item = masterItems.value.find((x) => x.id === masterItemId)
  if (!item) {
    formModel.material_name = ''
    formModel.thickness_text = ''
    formModel.color = ''
    formModel.color_family = null
    formModel.emboss = ''
    formModel.softness = ''
    formModel.color_reference = ''
    formModel.backing = ''
    formModel.quantity_order = ''
    formModel.style_article = ''
    formModel.model = ''
    formModel.line_etd = ''
    formModel.detail_remark = ''
    formModel.thi_line_ref = ''
    return
  }
  formModel.material_name = item.material_name || ''
  formModel.color = item.color || ''
  formModel.emboss = item.emboss || ''
  formModel.thickness_text = item.thickness_mm != null ? String(item.thickness_mm) : ''
  formModel.softness = item.softness || ''
  formModel.color_reference = item.color_reference || ''
  formModel.backing = item.backing || ''
  formModel.quantity_order = item.quantity_order_default != null ? String(item.quantity_order_default) : ''
  formModel.style_article = item.style_article || ''
  formModel.model = item.model || ''
  if (item && previewResolvedUnitPrice.value != null) {
    formModel.unit_price_input = previewResolvedUnitPrice.value
  } else {
    formModel.unit_price_input = null
  }
}

const openCreateDialog = () => {
  isEditMode.value = false
  resetForm()
  brandLockedCustomerId.value = null
  formDialogVisible.value = true
}

async function buildCurrentDetailBody() {
  const body = {
    master_item_id: formModel.master_item_id || undefined,
    material_name: formModel.material_name || undefined,
    thickness_text: formModel.thickness_text || undefined,
    color: formModel.color || undefined,
    color_family: formModel.color_family || undefined,
    emboss: formModel.emboss || undefined,
    vir_softness_type: formModel.vir_softness_type || undefined,
    softness: formModel.softness || undefined,
    color_reference: formModel.color_reference || undefined,
    backing: formModel.backing || undefined,
    quantity_order: formModel.quantity_order ? Number(formModel.quantity_order) : undefined,
    style_article: formModel.style_article || undefined,
    model: formModel.model || undefined,
    line_etd: toIsoDate(formModel.line_etd) || undefined,
    detail_remark: formModel.detail_remark || undefined,
    thi_line_ref: formModel.thi_line_ref || undefined,
  }
  const isFreePrice = formModel.po_category === 'subcont' || formModel.po_category === 'return'
  if (isFreePrice) {
    if (formModel.unit_price_input != null) {
      body.unit_price = Number(formModel.unit_price_input)
    }
  } else {
    const b = (formModel.buyer || '').trim()
    if (b) {
      try {
        const r = await resolveBuyerUnitPrice({
          buyer_code: b,
          material_name: formModel.material_name || null,
          color: formModel.color || null,
          style_article: formModel.style_article || null,
          thickness_text: formModel.thickness_text || null,
          color_family: formModel.color_family || null,
        })
        if (formModel.unit_price_input != null) {
          body.unit_price = Number(formModel.unit_price_input)
        } else if (r.unit_price != null) {
          body.unit_price = Number(r.unit_price)
        }
      } catch {
        if (formModel.unit_price_input != null) {
          body.unit_price = Number(formModel.unit_price_input)
        }
      }
    } else if (formModel.unit_price_input != null) {
      body.unit_price = Number(formModel.unit_price_input)
    }
  }
  body.delivery_schedules = etdScheduleRows.value
    .filter((r) => r.qty != null || r.date)
    .map((r, i) => ({ sequence_no: i + 1, qty: r.qty, delivery_date: r.date }))
  return body
}

/** Update baris: jangan kirim ulang unit_price (kunci harga di server untuk non-finance). */
function detailPayloadForUpdate(body) {
  const o = { ...body }
  delete o.unit_price
  delete o.id
  return o
}

function sanitizeNewDetailBody(body) {
  const o = { ...body }
  delete o.id
  return o
}

async function pushCurrentLine(copyCurrent = false) {
  const line = await buildCurrentDetailBody()
  if (!line.material_name && !line.master_item_id) {
    ElMessage.warning(t('common.material'))
    return
  }
  if (formModel.buyer?.trim() && line.unit_price == null) {
    ElMessage.warning(t('pages.po.priceNotFound'))
  }
  draftLines.value.push({ ...line })
  if (!copyCurrent) {
    formModel.master_item_id = null
    formModel.material_name = ''
    formModel.thickness_text = ''
    formModel.color = ''
    formModel.color_family = null
    formModel.emboss = ''
    formModel.vir_softness_type = ''
    formModel.softness = ''
    formModel.color_reference = ''
    formModel.backing = ''
    formModel.quantity_order = ''
    formModel.style_article = ''
    formModel.model = ''
    formModel.line_etd = ''
    formModel.detail_remark = ''
    formModel.thi_line_ref = ''
  }
}

function removeDraftLine(index) {
  draftLines.value.splice(index, 1)
}

function openInlineBrandDialog() {
  inlineBrand.code = ''
  inlineBrand.name = ''
  brandDialogVisible.value = true
}

async function submitInlineBrand() {
  if (!inlineBrand.code?.trim()) {
    ElMessage.warning(t('pages.brandMaster.codeRequired'))
    return
  }
  brandSaving.value = true
  try {
    const created = await createBrand({
      code: inlineBrand.code.trim(),
      name: inlineBrand.name?.trim() || undefined,
      customer_id: formModel.customer_id || undefined,
    })
    brands.value = [created, ...brands.value]
    formModel.brand_id = created.id
    brandDialogVisible.value = false
    ElMessage.success(t('common.save'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    brandSaving.value = false
  }
}

const openEditDialog = async (row) => {
  isEditMode.value = true
  editingPoId.value = row.id
  resetForm()
  formModel.po_number = row.po_number || ''
  formModel.customer_id = row.customer_id
  formModel.brand_id = row.brand_id ?? null
  formModel.po_category = row.po_category || 'production'
  formModel.order_date = row.order_date ? String(row.order_date).slice(0, 10) : ''
  formModel.buyer = row.buyer || ''
  formModel.etd = row.etd ? String(row.etd).slice(0, 10) : ''
  formModel.po_customer_ref = row.po_customer_ref || ''
  formModel.remark = row.remark || ''
  formModel.billing_address = row.billing_address || ''
  formModel.delivery_address = row.delivery_address || ''
  formModel.status = row.status || 'draft'
  formModel.material_followup_remark = row.material_followup_remark || ''
  formModel.material_followup_done = Boolean(row.material_followup_done)
  await onBrandChange(formModel.brand_id)
  schedulePricePreview()
    try {
    const details = await listPoDetails(row.id)
    draftLines.value = details.map((d) => ({
      id: d.id,
      master_item_id: d.master_item_id || undefined,
      material_name: d.material_name || undefined,
      thickness_text: d.thickness_text || undefined,
      color: d.color || undefined,
      color_family: d.color_family || undefined,
      emboss: d.emboss || undefined,
      vir_softness_type: d.vir_softness_type || undefined,
      softness: d.softness || undefined,
      color_reference: d.color_reference || undefined,
      backing: d.backing || undefined,
      quantity_order: d.quantity_order != null ? Number(d.quantity_order) : undefined,
      style_article: d.style_article || undefined,
      model: d.model || undefined,
      line_etd: d.line_etd ? String(d.line_etd).slice(0, 10) : undefined,
      detail_remark: d.detail_remark || undefined,
      thi_line_ref: d.thi_line_ref || undefined,
      unit_price: d.unit_price != null ? Number(d.unit_price) : undefined,
      delivery_schedules: d.delivery_schedules || [],
    }))
    editingDetailIds.value = details.map((d) => d.id)
    const d0 = details[0]
    if (d0) {
      formModel.master_item_id = d0.master_item_id
      formModel.material_name = d0.material_name || ''
      formModel.thickness_text = d0.thickness_text || ''
      formModel.color = d0.color || ''
      formModel.color_family = d0.color_family || null
      formModel.emboss = d0.emboss || ''
      formModel.vir_softness_type = d0.vir_softness_type || ''
      formModel.softness = d0.softness || ''
      formModel.color_reference = d0.color_reference || ''
      formModel.backing = d0.backing || ''
      formModel.quantity_order = d0.quantity_order != null ? String(d0.quantity_order) : ''
      formModel.style_article = d0.style_article || ''
      formModel.model = d0.model || ''
      formModel.line_etd = d0.line_etd ? String(d0.line_etd).slice(0, 10) : ''
      formModel.detail_remark = d0.detail_remark || ''
      formModel.thi_line_ref = d0.thi_line_ref || ''
      if (d0.delivery_schedules && d0.delivery_schedules.length) {
        const rows = Array.from({ length: 12 }, () => ({ qty: null, date: '' }))
        d0.delivery_schedules.forEach((s, idx) => {
          if (idx < 12) {
            rows[idx].qty = s.qty != null ? Number(s.qty) : null
            rows[idx].date = s.delivery_date ? String(s.delivery_date).slice(0, 10) : ''
          }
        })
        etdScheduleRows.value = rows
      } else {
        clearEtdSchedule()
      }
    }
  } catch {
    editingDetailIds.value = []
    draftLines.value = []
  }
  formDialogVisible.value = true
}

const submitForm = async () => {
  if (!formModel.customer_id) {
    ElMessage.warning(t('pages.po.pickCustomerWarning'))
    return
  }
  saving.value = true
  try {
    const header = {
      po_number: isEditMode.value ? formModel.po_number?.trim() || undefined : undefined,
      customer_id: formModel.customer_id,
      brand_id: formModel.brand_id || undefined,
      buyer: formModel.buyer || undefined,
      po_category: formModel.po_category,
      order_date: toIsoDate(formModel.order_date) || undefined,
      etd: toIsoDate(formModel.etd) || undefined,
      po_customer_ref: formModel.po_customer_ref?.trim() || undefined,
      remark: formModel.remark || undefined,
      billing_address: formModel.billing_address?.trim() || undefined,
      delivery_address: formModel.delivery_address?.trim() || undefined,
      status: formModel.status,
      material_followup_remark: formModel.material_followup_remark || undefined,
      material_followup_done: formModel.material_followup_done,
    }
    const detailBodies = draftLines.value.length ? draftLines.value : [await buildCurrentDetailBody()]

    if (isEditMode.value && editingPoId.value) {
      await updatePo(editingPoId.value, header)
      const keepIds = []
      for (let i = 0; i < detailBodies.length; i += 1) {
        const rowBody = { ...sanitizeNewDetailBody(detailBodies[i]) }
        const schedules = rowBody.delivery_schedules || []
        delete rowBody.delivery_schedules
        const existingId = editingDetailIds.value[i]
        if (existingId) {
          await updatePoDetail(existingId, detailPayloadForUpdate(rowBody))
          if (schedules.length) {
            await setPoDetailDeliverySchedules(existingId, { schedules })
          }
          keepIds.push(existingId)
        } else {
          const createdDetail = await addPoDetail(editingPoId.value, rowBody)
          if (schedules.length) {
            await setPoDetailDeliverySchedules(createdDetail.id, { schedules })
          }
          keepIds.push(createdDetail.id)
        }
      }
      const staleIds = editingDetailIds.value.filter((id) => !keepIds.includes(id))
      for (const staleId of staleIds) {
        await deletePoDetail(staleId)
      }
    } else {
      const created = await createPo(header)
      for (const raw of detailBodies) {
        const rowBody = { ...sanitizeNewDetailBody(raw) }
        const schedules = rowBody.delivery_schedules || []
        delete rowBody.delivery_schedules
        const createdDetail = await addPoDetail(created.id, rowBody)
        if (schedules.length) {
          await setPoDetailDeliverySchedules(createdDetail.id, { schedules })
        }
      }
    }
    ElMessage.success(t('pages.customers.saved'))
    formDialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  } finally {
    saving.value = false
  }
}

const detailDialogVisible = ref(false)
const detailView = ref(null)
const detailLines = ref([])
const detailAudit = ref([])

const openDetailDialog = async (row) => {
  detailView.value = { ...row, customerName: row.customerName }
  detailLines.value = []
  detailAudit.value = []
  try {
    detailLines.value = await listPoDetails(row.id)
  } catch {
    detailLines.value = []
  }
  try {
    const logsHeader = await listAuditLogs({ entity_type: 'sales_order', entity_id: row.id, limit: 120 })
    const lineLogsLists = await Promise.all(
      detailLines.value.map((d) =>
        listAuditLogs({ entity_type: 'sales_order_line', entity_id: d.id, limit: 60 }).catch(() => []),
      ),
    )
    const merged = [...logsHeader, ...lineLogsLists.flat()]
    merged.sort((a, b) => String(b.created_at || '').localeCompare(String(a.created_at || '')))
    detailAudit.value = merged
  } catch {
    detailAudit.value = []
  }
  detailDialogVisible.value = true
}

function prettyAudit(a) {
  const b = a.before ? JSON.stringify(a.before, null, 2) : ''
  const af = a.after ? JSON.stringify(a.after, null, 2) : ''
  if (b && af) return `${t('common.beforeLabel')}:\\n${b}\\n\\n${t('common.afterLabel')}:\\n${af}`
  return b || af || ''
}

const printDialogVisible = ref(false)
const selectedRow = reactive({})

const openPrintDialog = (row) => {
  Object.assign(selectedRow, row)
  printDialogVisible.value = true
}

const printPage = () => window.print()

const removeRow = async (row) => {
  try {
    await ElMessageBox.confirm(
      t('pages.po.deleteConfirm', { poNumber: row.po_number }),
      t('pages.po.deleteTitle'),
      {
        type: 'warning',
        distinguishCancelAndClose: true,
        confirmButtonText: t('common.delete'),
        cancelButtonText: t('common.cancel'),
      },
    )
    await deletePo(row.id)
    ElMessage.success(t('pages.po.deleted'))
    await load()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function openExportHint() {
  ElMessage.info(t('pages.po.exportHint'))
}

async function onDuplicatePo(row) {
  const poNo = row.po_number || `#${row.id}`
  try {
    await ElMessageBox.confirm(
      t('pages.po.duplicatePoConfirm', { poNumber: poNo }),
      t('pages.po.duplicatePo'),
      {
        type: 'info',
        distinguishCancelAndClose: true,
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
      },
    )
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message || t('common.errorGeneric'))
    return
  }
  try {
    const created = await duplicatePo(row.id)
    await load()
    const nr = rows.value.find((r) => Number(r.id) === Number(created.id))
    ElMessage.success(t('pages.po.duplicatePoSuccess', { poNumber: created.po_number || created.id }))
    if (nr) await openEditDialog(nr)
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function openCopyItemDialog() {
  copyItemCustomerId.value = formModel.customer_id
  copyItemSelected.value = []
  copyItemSourcePo.value = []
  if (copyItemCustomerId.value) {
    await loadCopyItemSourcePos()
  }
  copyItemDialogVisible.value = true
}

async function loadCopyItemSourcePos() {
  if (!copyItemCustomerId.value) {
    copyItemSourcePo.value = []
    return
  }
  try {
    const pos = await listPoForCopy({ customer_id: copyItemCustomerId.value })
    const otherPos = pos.filter(p => p.id !== editingPoId.value)
    const allDetails = await Promise.all(
      otherPos.map(p => listPoDetails(p.id).catch(() => []))
    )
    copyItemSourcePo.value = allDetails.flat().map(d => ({
      ...d,
      source_po_number: otherPos.find(p => p.id === d.po_id)?.po_number
    }))
  } catch {
    copyItemSourcePo.value = []
  }
}

async function onCopyItemCustomerChange() {
  await loadCopyItemSourcePos()
}

function onCopyItemSelectionChange(selection) {
  copyItemSelected.value = selection
}

function addCopiedItems() {
  const newLines = copyItemSelected.value.map(d => ({
    master_item_id: d.master_item_id,
    material_name: d.material_name,
    thickness_text: d.thickness_text,
    color: d.color,
    color_family: d.color_family,
    emboss: d.emboss,
    vir_softness_type: d.vir_softness_type,
    softness: d.softness,
    color_reference: d.color_reference,
    backing: d.backing,
    quantity_order: d.quantity_order,
    style_article: d.style_article,
    model: d.model,
    line_etd: d.line_etd,
    detail_remark: d.detail_remark,
    thi_line_ref: d.thi_line_ref,
    unit_price: d.unit_price,
    copied_from_detail_id: d.id
  }))
  draftLines.value.push(...newLines)
  copyItemDialogVisible.value = false
  ElMessage.success(t('pages.po.itemsCopied', { count: newLines.length }))
}
</script>

<style scoped>
.admin-table {
  width: 100%;
}

.po-row-actions {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 2px 4px;
}

.po-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.po-price-readonly :deep(.el-input__wrapper) {
  background-color: var(--el-fill-color-light);
}

.etd-schedule-table {
  width: 100%;
}

.etd-schedule-table :deep(.el-table__header-wrapper) {
  display: none;
}

</style>
