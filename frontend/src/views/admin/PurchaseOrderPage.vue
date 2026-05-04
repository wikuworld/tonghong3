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
          <el-col :xs="24" :sm="12" :md="8" :lg="6">
            <el-form-item :label="t('common.buyer')">
              <el-select v-model="filterBuyer" clearable filterable class="w-full" :placeholder="t('common.placeholder.buyer')">
                <el-option v-for="b in buyerCodes" :key="b" :label="b" :value="b" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :xs="24" :sm="24" :md="8" :lg="6" class="po-filter-action-col">
            <el-form-item label="&nbsp;">
              <el-button class="w-full" :icon="RefreshLeft" @click="resetFilter">{{ t('common.reset') }}</el-button>
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
      table-layout="fixed"
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
      <el-table-column prop="status" :label="t('common.status')" width="140" align="center">
        <template #default="{ row }">
          <el-popconfirm
            v-if="canManage"
            :title="t('pages.po.confirmPo')"
            :confirm-button-text="t('common.yes')"
            :cancel-button-text="t('common.no')"
            @confirm="quickChangeStatus(row, 'confirmed')"
          >
            <template #reference>
              <el-tag :type="statusType(row.status)" size="small" class="cursor-pointer hover:opacity-70">
                {{ t(`status.${row.status}`) }}
              </el-tag>
            </template>
          </el-popconfirm>
          <el-tag v-else :type="statusType(row.status)" size="small">
            {{ t(`status.${row.status}`) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.actions')" width="268" align="center" fixed="right">
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
            <el-tooltip :content="t('pages.po.salesContractPdf')" placement="top">
              <el-button :icon="Document" link type="primary" :aria-label="t('pages.po.salesContractPdf')" @click="downloadSalesContractPdf(row)" />
            </el-tooltip>
            <el-tooltip :content="t('pages.po.salesContractDocx')" placement="top">
              <el-button :icon="FolderOpened" link type="primary" :aria-label="t('pages.po.salesContractDocx')" @click="downloadSalesContractDocx(row)" />
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
    <div class="mt-3 flex justify-end">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        size="small"
        layout="total, sizes, prev, pager, next"
        :total="totalRows"
        :page-sizes="[20, 50, 100, 200]"
      />
    </div>

    <el-dialog
      v-model="formDialogVisible"
      :fullscreen="false"
      width="90%"
      top="3vh"
      destroy-on-close
      class="po-fullscreen-dialog"
      :before-close="handlePoDialogBeforeClose"
    >
      <template #header>
        <div class="po-dialog-header">
          <el-icon class="po-dialog-close" @click="requestCloseFormDialog"><Close /></el-icon>
          <div class="po-dialog-title-area">
            <el-icon class="po-dialog-icon"><DocumentAdd /></el-icon>
            <span class="po-dialog-title">
              {{ isEditMode ? t('pages.poEntry.title') + ' ' + t('pages.po.editSuffix') : t('pages.poEntry.title') }}
            </span>
            <el-tag v-if="!isEditMode" type="info" effect="plain" size="small">
              {{ nextPoNumberDisplay }}
            </el-tag>
            <el-tag v-else type="primary" effect="plain" size="small">
              {{ formModel.po_number }}
            </el-tag>
          </div>
          <div class="po-dialog-steps-wrapper">
            <el-steps class="mb-4 po-dialog-steps w-full" :space="100" :active="currentStep" simple>
              <el-step :title="t('pages.po.step1Title')" :icon="Edit" />
              <el-step :title="t('pages.po.step2Title')" :icon="UploadFilled" />
              <el-step :title="t('pages.po.step3Title')" :icon="Picture" />
            </el-steps>
          </div>
        </div>
      </template>

      <div class="po-dialog-content">
        <el-form label-position="top" class="po-dialog-form" @keydown.enter.prevent="handleEnterKey">
          <div v-show="currentStep === 0" class="step-content">
            <h3 class="text-lg font-semibold mb-4">{{ t('pages.po.customerSoSection') }}</h3>
            <el-row :gutter="16" class="material-step-grid">
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('common.customer')" required>
                  <el-select
                    v-model="formModel.customer_id"
                    filterable
                    clearable
                    class="w-full"
                    :placeholder="t('common.placeholder.customer')"
                    :disabled="Boolean(brandLockedCustomerId)"
                    :error="formErrors.customer_id"
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
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('pages.po.customerPic')">
                  <el-input :model-value="customerPicDisplay" readonly />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('pages.po.brand')">
                  <el-select
                    v-model="formModel.brand_id"
                    clearable
                    filterable
                    class="w-full"
                    :placeholder="t('pages.po.brand')"
                    :disabled="isBrandDisabled"
                    @change="onBrandChange"
                  >
                    <el-option
                      v-for="b in brandsFiltered"
                      :key="b.id"
                      :label="`${b.code || b.id} — ${b.name || ''}`"
                      :value="b.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('common.buyer')">
                  <el-select
                    v-model="formModel.buyer"
                    filterable
                    class="w-full"
                    :placeholder="t('common.placeholder.buyer')"
                    :disabled="isBuyerDisabled"
                    @change="autoFieldMeta.buyer = false"
                  >
                    <el-option v-for="b in buyerCodesFiltered" :key="b" :label="b" :value="b" />
                  </el-select>
                  <div class="mt-2 flex items-center gap-2">
                    <el-tag v-if="autoFieldMeta.buyer && formModel.buyer" size="small" type="success">
                      {{ t('pages.po.autoFilled') }}
                    </el-tag>
                    <el-button v-if="formModel.buyer" link type="primary" size="small" @click="resetToAuto('buyer')">
                      {{ t('pages.po.resetToAuto') }}
                    </el-button>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('common.poCategory')">
                  <el-select v-model="formModel.po_category" class="w-full" :placeholder="t('common.category')" :disabled="isPoCategoryDisabled">
                    <el-option :label="t('status.production')" value="production" />
                    <el-option :label="t('status.subkon')" value="subcont" />
                    <el-option :label="t('status.retur')" value="return" />
                    <el-option :label="t('status.sample')" value="sample" />
                    <el-option :label="t('status.claim')" value="claim" />
                    <el-option :label="t('status.suede')" value="suede" />
                  </el-select>
                  <el-radio-group v-model="formModel.po_category" size="small" class="mt-2" :disabled="isPoCategoryDisabled">
                    <el-radio-button value="production">{{ t('status.production') }}</el-radio-button>
                    <el-radio-button value="sample">{{ t('status.sample') }}</el-radio-button>
                    <el-radio-button value="subcont">{{ t('status.subcont') }}</el-radio-button>
                    <el-radio-button value="return">{{ t('status.return') }}</el-radio-button>
                    <el-radio-button value="claim">{{ t('status.claim') }}</el-radio-button>
                  </el-radio-group>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('common.poNo')">
                  <el-input :model-value="isEditMode ? formModel.po_number : nextPoNumberDisplay" disabled />
                  <span class="text-xs text-slate-500">{{ t('pages.po.autoGenerateHint') }}</span>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('pages.po.poCustomerRef')">
                  <el-input v-model="formModel.po_customer_ref" clearable maxlength="255" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('common.orderDate')">
                  <el-date-picker v-model="formModel.order_date" type="date" class="w-full" value-format="YYYY-MM-DD" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('pages.po.headerEtd')">
                  <el-date-picker v-model="formModel.etd" type="date" class="w-full" value-format="YYYY-MM-DD" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('pages.po.billingAddress')">
                  <el-input v-model="formModel.billing_address" type="textarea" :rows="2" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('pages.po.deliveryAddress')">
                  <el-input v-model="formModel.delivery_address" type="textarea" :rows="2" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('common.remark')">
                  <el-input v-model="formModel.remark" type="textarea" :rows="2" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <div v-show="currentStep === 1" class="step-content">
            <h3 class="text-lg font-semibold mb-4">{{ t('pages.po.step2Title') }}</h3>
            <el-row :gutter="16" class="material-step-grid">
              <el-col :xs="24" :md="8">
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
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('common.material')" :error="formErrors.material_name">
                  <div class="field-lock-row">
                    <el-input
                      v-model="formModel.material_name"
                      class="w-full"
                      :placeholder="t('common.placeholder.material')"
                      :disabled="isMaterialFieldLocked('material_name')"
                      clearable
                    />
                    <div class="mt-1 flex items-center gap-2">
                      <el-button
                        v-if="isMaterialFieldLocked('material_name')"
                        link
                        type="primary"
                        size="small"
                        @click="enableMaterialOverride('material_name')"
                      >
                        Override
                      </el-button>
                      <el-button
                        v-else-if="formModel.master_item_id && materialFieldOverride.material_name"
                        link
                        type="primary"
                        size="small"
                        @click="resetMaterialFieldToMaster('material_name')"
                      >
                        Reset
                      </el-button>
                    </div>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item label="ARTICLE">
                  <div class="field-lock-row">
                    <el-input v-model="formModel.style_article" class="w-full" :disabled="isMaterialFieldLocked('style_article')" />
                    <div class="mt-1 flex items-center gap-2">
                      <el-button
                        v-if="isMaterialFieldLocked('style_article')"
                        link
                        type="primary"
                        size="small"
                        @click="enableMaterialOverride('style_article')"
                      >
                        Override
                      </el-button>
                      <el-button
                        v-else-if="formModel.master_item_id && materialFieldOverride.style_article"
                        link
                        type="primary"
                        size="small"
                        @click="resetMaterialFieldToMaster('style_article')"
                      >
                        Reset
                      </el-button>
                    </div>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('common.thickness')">
                  <div class="field-lock-row">
                    <el-select v-model="formModel.thickness_text" clearable filterable class="w-full" :disabled="isMaterialFieldLocked('thickness_text')">
                      <el-option label="1.0-1.2" value="1.0-1.2" />
                      <el-option label="1.2-1.4" value="1.2-1.4" />
                      <el-option label="1.4-1.6" value="1.4-1.6" />
                      <el-option label="1.6-1.8" value="1.6-1.8" />
                    </el-select>
                    <div class="mt-1 flex items-center gap-2">
                      <el-button
                        v-if="isMaterialFieldLocked('thickness_text')"
                        link
                        type="primary"
                        size="small"
                        @click="enableMaterialOverride('thickness_text')"
                      >
                        Override
                      </el-button>
                      <el-button
                        v-else-if="formModel.master_item_id && materialFieldOverride.thickness_text"
                        link
                        type="primary"
                        size="small"
                        @click="resetMaterialFieldToMaster('thickness_text')"
                      >
                        Reset
                      </el-button>
                    </div>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('common.color')">
                  <el-select
                    v-if="isFluorescentFamily"
                    v-model="formModel.color"
                    clearable
                    filterable
                    class="w-full"
                    :placeholder="t('common.placeholder.color')"
                    :disabled="isMaterialFieldLocked('color')"
                  >
                    <el-option
                      v-for="opt in fluorescentColorOptions"
                      :key="opt.id"
                      :label="formatFluorescentOption(opt)"
                      :value="opt.color_name"
                    />
                  </el-select>
                  <el-input v-else v-model="formModel.color" class="w-full" :disabled="isMaterialFieldLocked('color')" />
                  <div class="mt-1">
                    <el-button
                      v-if="isMaterialFieldLocked('color')"
                      link
                      type="primary"
                      size="small"
                      @click="enableMaterialOverride('color')"
                    >
                      Override warna
                    </el-button>
                    <el-button
                      v-else-if="formModel.master_item_id && materialFieldOverride.color"
                      link
                      type="primary"
                      size="small"
                      @click="resetMaterialFieldToMaster('color')"
                    >
                      Reset warna
                    </el-button>
                  </div>
                  <div v-if="isFluorescentFamily" class="mt-1 text-xs text-slate-500">
                    Season aktif: {{ activeSeasonLabel || '-' }} · {{ t('common.masterLabel') }} fluorescent: {{ fluorescentColorOptions.length }} opsi
                  </div>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('pages.po.colorFamily')">
                  <div class="field-lock-row">
                    <el-select
                      v-model="formModel.color_family"
                      clearable
                      class="w-full"
                      :disabled="isMaterialFieldLocked('color_family')"
                      @change="colorFamilyAutoMode = false"
                    >
                      <el-option :label="t('pages.po.colorFamilyBlack')" value="black" />
                      <el-option :label="t('pages.po.colorFamilyColor')" value="color" />
                      <el-option :label="t('pages.po.colorFamilyFluorescent')" value="fluorescent" />
                    </el-select>
                    <el-button
                      v-if="isMaterialFieldLocked('color_family')"
                      link
                      type="primary"
                      size="small"
                      @click="enableMaterialOverride('color_family')"
                    >
                      Override
                    </el-button>
                    <el-button
                      v-else-if="formModel.master_item_id && materialFieldOverride.color_family"
                      link
                      type="primary"
                      size="small"
                      @click="resetMaterialFieldToMaster('color_family')"
                    >
                      Reset
                    </el-button>
                  </div>
                  <div class="mt-1 text-xs text-slate-500">
                    Auto-kategori warna: {{ colorFamilyAutoMode ? 'aktif' : 'manual' }}
                  </div>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('pages.po.emboss')">
                  <div class="field-lock-row">
                    <el-input v-model="formModel.emboss" class="w-full" clearable :disabled="isMaterialFieldLocked('emboss')" />
                    <el-button
                      v-if="isMaterialFieldLocked('emboss')"
                      link
                      type="primary"
                      size="small"
                      @click="enableMaterialOverride('emboss')"
                    >
                      Override
                    </el-button>
                    <el-button
                      v-else-if="formModel.master_item_id && materialFieldOverride.emboss"
                      link
                      type="primary"
                      size="small"
                      @click="resetMaterialFieldToMaster('emboss')"
                    >
                      Reset
                    </el-button>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :xs="24">
                <el-alert
                  v-if="pricingKeyIncomplete"
                  title="Pricing key belum lengkap: buyer + material + ketebalan + kategori warna wajib terisi."
                  type="warning"
                  :closable="false"
                  show-icon
                  class="mb-2"
                />
                <el-collapse v-model="materialAdvancedOpen">
                  <el-collapse-item name="advanced-material">
                    <template #title>
                      <span class="font-medium">Advanced (opsional)</span>
                    </template>
                    <el-row :gutter="16">
                      <el-col :xs="24" :md="8">
                        <el-form-item :label="t('pages.po.virSoftnessType')">
                          <el-input v-model="formModel.vir_softness_type" clearable @input="autoFieldMeta.vir_softness_type = false" />
                          <div class="mt-2 flex items-center gap-2">
                            <el-tag v-if="autoFieldMeta.vir_softness_type && formModel.vir_softness_type" size="small" type="success">
                              {{ t('pages.po.autoFilled') }}
                            </el-tag>
                            <el-button
                              v-if="formModel.vir_softness_type"
                              link
                              type="primary"
                              size="small"
                              @click="resetToAuto('vir_softness_type')"
                            >
                              {{ t('pages.po.resetToAuto') }}
                            </el-button>
                          </div>
                        </el-form-item>
                      </el-col>
                      <el-col :xs="24" :md="8">
                        <el-form-item :label="t('common.softness')">
                          <el-select v-model="formModel.softness" clearable filterable allow-create class="w-full" @change="autoFieldMeta.softness = false">
                            <el-option label="Soft" value="Soft" />
                            <el-option label="Medium" value="Medium" />
                            <el-option label="Hard" value="Hard" />
                            <el-option label="Extra Soft" value="Extra Soft" />
                            <el-option label="Super Soft" value="Super Soft" />
                          </el-select>
                          <div v-if="softnessRangeWarning" class="mt-1 text-xs text-amber-600">
                            {{ softnessRangeWarning }}
                          </div>
                        </el-form-item>
                      </el-col>
                      <el-col :xs="24" :md="8">
                        <el-form-item :label="t('common.colorReference')">
                          <el-input v-model="formModel.color_reference" @input="autoFieldMeta.color_reference = false" />
                          <div class="mt-2 flex items-center gap-2">
                            <el-tag v-if="autoFieldMeta.color_reference && formModel.color_reference" size="small" type="success">
                              {{ t('pages.po.autoFilled') }}
                            </el-tag>
                            <el-button
                              v-if="formModel.color_reference"
                              link
                              type="primary"
                              size="small"
                              @click="resetToAuto('color_reference')"
                            >
                              {{ t('pages.po.resetToAuto') }}
                            </el-button>
                          </div>
                        </el-form-item>
                      </el-col>
                      <el-col :xs="24" :md="8">
                        <el-form-item :label="t('common.backing')">
                          <el-input v-model="formModel.backing" @input="autoFieldMeta.backing = false" />
                          <div class="mt-2 flex items-center gap-2">
                            <el-tag v-if="autoFieldMeta.backing && formModel.backing" size="small" type="success">
                              {{ t('pages.po.autoFilled') }}
                            </el-tag>
                            <el-button v-if="formModel.backing" link type="primary" size="small" @click="resetToAuto('backing')">
                              {{ t('pages.po.resetToAuto') }}
                            </el-button>
                          </div>
                        </el-form-item>
                      </el-col>
                      <el-col :xs="24" :md="8">
                        <el-form-item :label="t('common.model')">
                          <el-input v-model="formModel.model" :placeholder="t('common.placeholder.model')" @input="autoFieldMeta.model = false" />
                          <div class="mt-2 flex items-center gap-2">
                            <el-tag v-if="autoFieldMeta.model && formModel.model" size="small" type="success">
                              {{ t('pages.po.autoFilled') }}
                            </el-tag>
                            <el-button v-if="formModel.model" link type="primary" size="small" @click="resetToAuto('model')">
                              {{ t('pages.po.resetToAuto') }}
                            </el-button>
                          </div>
                        </el-form-item>
                      </el-col>
                    </el-row>
                  </el-collapse-item>
                </el-collapse>
              </el-col>
            </el-row>
            <el-row :gutter="16" class="material-step-grid">
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('common.quantityOrder')" :error="formErrors.quantity_order">
                  <el-input v-model="formModel.quantity_order" type="number" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item label="REPLY ETD">
                  <el-date-picker v-model="formModel.line_etd" type="date" class="w-full" value-format="YYYY-MM-DD" />
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item label="THI ORDER / LOT NO">
                  <div class="field-stack-row">
                    <el-input v-model="formModel.thi_line_ref" class="w-full" clearable />
                    <el-button size="small" class="self-start" @click="applyLotPrefix">{{ t('pages.po.applyLotPrefix') }}</el-button>
                  </div>
                </el-form-item>
              </el-col>
              <el-col :xs="24" :md="8">
                <el-form-item :label="t('pages.po.unitPriceUsd')">
                  <div class="field-stack-row">
                    <el-input v-model.number="formModel.unit_price_input" class="w-full" type="number" :step="0.01" :controls="false" />
                    <el-checkbox v-model="formModel.is_special_price" @change="onSpecialPriceChange">
                      {{ t('pages.po.specialPrice') }}
                    </el-checkbox>
                  </div>
                  <div v-if="formModel.is_special_price" class="mt-2 flex items-center gap-2">
                    <el-input-number
                      v-model="formModel.discount_value"
                      :min="0"
                      :max="formModel.discount_type === 'percent' ? 100 : 999999"
                      :controls="false"
                      class="flex-1"
                      @change="calculateSpecialPrice"
                    />
                    <el-radio-group v-model="formModel.discount_type" size="default" @change="calculateSpecialPrice">
                      <el-radio-button value="percent">{{ t('pages.po.percent') }}</el-radio-button>
                      <el-radio-button value="nominal">USD</el-radio-button>
                    </el-radio-group>
                  </div>
                  <div class="mt-1 flex items-center gap-2 flex-wrap">
                    <span v-if="previewResolvedUnitPrice != null" class="text-xs text-slate-500">
                      {{ t('pages.po.autoResolved') }}: {{ previewResolvedUnitPrice }}
                    </span>
                    <el-tag v-if="formModel.unit_price_input && previewResolvedUnitPrice != null && formModel.unit_price_input !== previewResolvedUnitPrice" size="small" type="warning">{{ t('pages.po.overridden') }}</el-tag>
                    <el-tag v-if="formModel.is_special_price && formModel.unit_price_input" size="small" type="success">
                      Final: ${{ formModel.unit_price_input?.toFixed(2) }}
                    </el-tag>
                  </div>
                </el-form-item>
              </el-col>
            </el-row>
            <div class="mt-1 text-sm font-semibold text-slate-700">Daftar Material</div>
            <div class="mt-1 flex gap-2 flex-wrap">
              <el-button :icon="Plus" @click="pushCurrentLine(false)">{{ t('common.add') }}</el-button>
              <el-button :icon="TopRight" @click="pushCurrentLine(true)">{{ t('pages.po.addAndContinue') }}</el-button>
              <el-button :icon="DocumentCopy" @click="openCopyItemDialog">{{ t('pages.po.copyItemFromOtherPo') }}</el-button>
              <el-switch
                v-model="draftRiskOnly"
                inline-prompt
                active-text="Override saja"
                inactive-text="Semua line"
              />
              <el-tag size="small" type="info" effect="plain">
                Ditampilkan: {{ draftLinesDisplay.length }} / {{ draftLines.length }}
              </el-tag>
            </div>
            <el-table v-if="draftLinesDisplay.length" :data="draftLinesDisplay" border stripe size="small" class="mt-4" table-layout="auto">
              <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
              <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
              <el-table-column prop="thickness_text" :label="t('common.thickness')" width="90" />
              <el-table-column prop="color" :label="t('common.color')" width="80" />
              <el-table-column prop="color_family" :label="t('pages.po.colorFamily')" width="100">
                <template #default="{ row }">{{ colorFamilyLabel(row.color_family) }}</template>
              </el-table-column>
              <el-table-column label="Kualitas Data" width="190" align="center">
                <template #default="{ row }">
                  <div class="flex flex-col items-center gap-1">
                    <el-tooltip :content="materialQualityTooltip(row)" placement="top">
                      <el-tag
                        :type="materialQualityType(row)"
                        size="small"
                        effect="plain"
                      >
                        {{ materialQualityLabel(row) }}
                      </el-tag>
                    </el-tooltip>
                    <el-tooltip v-if="row.manual_override" content="Harga line ini diubah manual dari harga auto-resolve buyer." placement="top">
                      <el-tag size="small" type="danger" effect="plain">
                        Harga override
                      </el-tag>
                    </el-tooltip>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="90" />
              <el-table-column :label="t('pages.po.unitPriceUsd')" width="100" align="right">
                <template #default="{ row }">
                  <div class="flex flex-col items-end">
                    <span v-if="row.is_special_price" class="text-xs text-slate-400 line-through">
                      {{ row.base_price?.toFixed(2) || '—' }}
                    </span>
                    <span :class="row.is_special_price ? 'text-green-600 font-semibold' : ''">
                      {{ row.unit_price != null ? '$' + row.unit_price.toFixed(2) : '—' }}
                    </span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column v-if="hasSpecialPriceInLines" :label="t('pages.po.discount')" width="80" align="center">
                <template #default="{ row }">
                  <el-tag v-if="row.is_special_price" size="small" type="warning">
                    {{ row.discount_value }}{{ row.discount_type === 'percent' ? '%' : '$' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="line_etd" label="REPLY ETD" width="110" />
              <el-table-column prop="thi_line_ref" label="THI ORDER / LOT NO" min-width="130" />
              <el-table-column :label="'SYSTEM NO'" min-width="120" show-overflow-tooltip>
                <template #default="{ row }">{{ row.system_reference || row.thi_line_ref || '—' }}</template>
              </el-table-column>
              <el-table-column :label="t('common.actions')" width="70" align="center">
                <template #default="{ $index }">
                  <el-button link type="danger" :icon="Delete" @click="removeDraftLine($index)" />
                </template>
              </el-table-column>
            </el-table>
            <div class="mt-2 text-sm font-semibold text-slate-700">Jadwal &amp; Catatan</div>
            <div class="mt-1">
              <el-form-item :label="t('pages.po.etdSchedule')">
                <el-table :data="etdScheduleRows" border size="small">
                  <el-table-column :label="t('common.noLabel')" width="60" align="center">
                    <template #default="{ $index }">{{ $index + 1 }}</template>
                  </el-table-column>
                  <el-table-column :label="t('pages.po.etdQty')" width="140">
                    <template #default="{ $index }">
                      <el-input-number v-model="etdScheduleRows[$index].qty" :min="0" :controls="false" size="small" class="w-full" />
                    </template>
                  </el-table-column>
                  <el-table-column :label="t('pages.po.etdDate')">
                    <template #default="{ $index }">
                      <el-date-picker v-model="etdScheduleRows[$index].date" type="date" size="small" class="w-full" value-format="YYYY-MM-DD" />
                    </template>
                  </el-table-column>
                </el-table>
                <div class="mt-2 flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <el-button size="small" @click="clearEtdSchedule">{{ t('common.clear') }}</el-button>
                    <el-button size="small" type="primary" @click="autoFillEtdSchedule">{{ t('pages.po.autoFillFromEtd') }}</el-button>
                  </div>
                  <div class="text-xs" :class="etdScheduleValid ? 'text-green-600' : 'text-red-500'">
                    {{ t('pages.po.scheduleTotal') }}: {{ etdScheduleTotal }} / {{ formModel.quantity_order || 0 }}
                    <el-tag v-if="!etdScheduleValid && etdScheduleTotal > 0" size="small" type="danger" class="ml-2">{{ t('pages.po.scheduleMismatch') }}</el-tag>
                  </div>
                </div>
              </el-form-item>
            </div>
            <div class="mt-1">
              <el-form-item label="REMARK">
                <el-input v-model="formModel.detail_remark" type="textarea" :rows="2" />
              </el-form-item>
            </div>
          </div>

          <div v-show="currentStep === 2" class="step-content">
            <h3 class="text-lg font-semibold mb-4">{{ t('pages.po.reviewTitle') }}</h3>
            <el-descriptions :column="2" border class="mb-6">
              <el-descriptions-item :label="t('common.customer')">
                {{ customers.find(c => c.id === formModel.customer_id)?.name || '-' }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('pages.po.brand')">
                {{ brands.find(b => b.id === formModel.brand_id)?.name || '-' }}
              </el-descriptions-item>
              <el-descriptions-item :label="t('common.buyer')">{{ formModel.buyer || '-' }}</el-descriptions-item>
              <el-descriptions-item :label="t('common.poCategory')">{{ formModel.po_category }}</el-descriptions-item>
              <el-descriptions-item :label="t('common.poNo')">{{ formModel.po_number || nextPoNumberDisplay }}</el-descriptions-item>
              <el-descriptions-item label="NO PO CUSTOMER">{{ formModel.po_customer_ref || '-' }}</el-descriptions-item>
              <el-descriptions-item :label="t('common.orderDate')">{{ formModel.order_date || '-' }}</el-descriptions-item>
              <el-descriptions-item :label="t('pages.po.headerEtd')">{{ formModel.etd || '-' }}</el-descriptions-item>
              <el-descriptions-item :label="t('common.status')">
                <el-tag size="small">{{ formModel.status }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="t('common.remark')" :span="2">{{ formModel.remark || '-' }}</el-descriptions-item>
            </el-descriptions>

            <h4 class="text-md font-semibold mb-2">{{ t('pages.po.itemsSummary', { count: draftLinesDisplay.length }) }}</h4>
            <el-table v-if="draftLinesDisplay.length" :data="draftLinesDisplay" border stripe size="small" table-layout="auto">
              <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
              <el-table-column prop="material_name" :label="t('common.material')" min-width="140" />
              <el-table-column prop="thickness_text" :label="t('common.thickness')" width="90" />
              <el-table-column prop="color" :label="t('common.color')" width="80" />
              <el-table-column :label="'Kualitas'" width="150" align="center">
                <template #default="{ row }">
                  <el-tooltip :content="materialQualityTooltip(row)" placement="top">
                    <el-tag :type="materialQualityType(row)" size="small" effect="plain">
                      {{ materialQualityLabel(row) }}
                    </el-tag>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="100" align="right" />
              <el-table-column prop="unit_price" :label="t('pages.po.unitPriceUsd')" width="100" align="right">
                <template #default="{ row }">{{ row.unit_price != null ? `$${row.unit_price}` : '—' }}</template>
              </el-table-column>
              <el-table-column :label="'Total'" width="120" align="right">
                <template #default="{ row }">
                  {{ row.unit_price != null && row.quantity_order ? `$${(row.unit_price * row.quantity_order).toFixed(2)}` : '—' }}
                </template>
              </el-table-column>
              <el-table-column prop="line_etd" label="REPLY ETD" width="110" />
              <el-table-column prop="thi_line_ref" label="THI ORDER / LOT NO" min-width="130" />
              <el-table-column :label="'SYSTEM NO'" min-width="120" show-overflow-tooltip>
                <template #default="{ row }">{{ row.system_reference || row.thi_line_ref || '—' }}</template>
              </el-table-column>
            </el-table>
            <el-empty v-else :description="t('pages.po.noItemsYet')" />
          </div>
        </el-form>
      </div>

      <template #footer>
        <div class="po-dialog-footer">
          <el-button type="danger" @click="requestCloseFormDialog">
            <el-icon><Close /></el-icon>
            {{ t('common.cancel') }}
          </el-button>
          <el-button v-if="!isEditMode" type="warning" @click="saveDraftAndClose">
            Simpan Draft
          </el-button>

          <div class="footer-nav">
            <el-button :disabled="currentStep === 0" @click="prevStep">&lt;</el-button>
            <span class="step-label">
              {{ currentStep === 0 ? t('pages.po.step1Title') : currentStep === 1 ? t('pages.po.step2Title') : t('pages.po.step3Title') }}
            </span>
            <el-button :disabled="currentStep === 2" type="primary" @click="nextStep">&gt;</el-button>
          </div>

          <el-button :disabled="currentStep !== 2 || !canManage" type="success" :loading="saving" @click="submitForm">
            <el-icon><Check /></el-icon>
            {{ t('common.savePo') }}
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailDialogVisible"
      :title="t('pages.poDetail.title')"
      width="95%" style="max-width: 900px"
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
      <div v-if="detailAudit.length" class="mt-4">
        <div class="mb-3 text-sm font-semibold text-slate-700">{{ t('pages.po.lineRevisionHistory') }}</div>
        <div class="space-y-3">
          <div
            v-for="a in nonEmptyAudit"
            :key="a.id"
            class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div class="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-2">
              <div class="flex items-center gap-2">
                <span
                  class="rounded-full px-2 py-0.5 text-xs font-medium"
                  :class="{
                    'bg-green-100 text-green-700': a.action === 'create',
                    'bg-blue-100 text-blue-700': a.action === 'update',
                    'bg-red-100 text-red-700': a.action === 'delete',
                    'bg-slate-100 text-slate-600': !['create', 'update', 'delete'].includes(a.action)
                  }"
                >
                  {{ a.action?.toUpperCase() }}
                </span>
                <span v-if="a.entity_type === 'sales_order_line'" class="text-xs text-slate-500">
                  {{ t('pages.poDetail.auditLine') }} #{{ a.entity_id }}
                </span>
              </div>
              <div class="flex items-center gap-2 text-xs text-slate-500">
                <span v-if="a.actor">{{ a.actor }}</span>
                <span v-else class="italic">{{ t('common.system') }}</span>
                <span>{{ t('common.dashSeparator') }}</span>
                <span>{{ a.created_at ? String(a.created_at).replace('T', ' ').slice(0, 16) : '' }}</span>
              </div>
            </div>
            <div class="space-y-2">
              <template v-if="auditChangedFields(a).length">
                <div
                  v-for="field in auditChangedFields(a)"
                  :key="field.key"
                  class="grid grid-cols-12 gap-2 rounded bg-slate-50 p-2 text-xs"
                >
                  <div class="col-span-12 font-medium text-slate-700 lg:col-span-2">
                    {{ field.displayLabel || auditFieldLabel(field.key) }}
                  </div>
                  <div class="col-span-12 lg:col-span-5">
                    <span class="text-slate-400">Sebelum: </span>
                    <span class="text-red-600 line-through">{{ field.before ?? '—' }}</span>
                  </div>
                  <div class="col-span-12 hidden items-center gap-1 lg:col-span-5 lg:flex">
                    <span class="text-slate-400">Sesudah: </span>
                    <span class="text-green-600">{{ field.after ?? '—' }}</span>
                    <span v-if="field.change" class="ml-auto rounded bg-green-100 px-1.5 py-0.5 text-green-700">
                      {{ field.change }}
                    </span>
                  </div>
                </div>
              </template>
              <div v-else class="text-xs italic text-slate-400">
                Tidak ada detail perubahan
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" :icon="Close" @click="detailDialogVisible = false">{{ t('pages.customers.closeDetail') }}</el-button>
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
          <el-button :icon="Close" @click="printDialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :icon="Printer" @click="printPage">{{ t('common.print') }}</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="copyItemDialogVisible"
      :title="t('pages.po.copyItemFromOtherPo')"
      width="95%" style="max-width: 900px"
      destroy-on-close
      align-center
    >
      <el-form label-position="top">
        <el-row :gutter="12">
          <el-col :xs="24" :md="12">
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
          </el-col>
          <el-col :xs="24" :md="12">
            <el-form-item :label="t('common.placeholder.search')">
              <el-input v-model="copyItemSearch" clearable :placeholder="t('pages.po.searchItems')" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <el-table
        v-if="copyItemSourcePo.length"
        :data="copyItemFilteredPo"
        border
        size="small"
        max-height="350"
        @selection-change="onCopyItemSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="source_po_number" :label="t('common.poNo')" width="140" />
        <el-table-column prop="material_name" :label="t('common.material')" min-width="160" show-overflow-tooltip />
        <el-table-column prop="thickness_text" :label="t('common.thickness')" width="90" />
        <el-table-column prop="color" :label="t('common.color')" width="90" />
        <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="100" align="right" />
        <el-table-column prop="unit_price" :label="t('pages.po.unitPriceUsd')" width="100" align="right">
          <template #default="{ row }">{{ row.unit_price != null ? row.unit_price : '—' }}</template>
        </el-table-column>
      </el-table>
      <div v-else-if="!copyItemCustomerId" class="text-center text-slate-500 py-8">
        {{ t('pages.po.selectCustomerToSeeItems') }}
      </div>
      <div v-else class="text-center text-slate-500 py-8">
        {{ t('pages.po.noItemsFound') }}
      </div>
      <div v-if="copyItemFilteredPo.length" class="mt-2 text-xs text-slate-500">
        {{ t('pages.po.showingItems', { count: copyItemFilteredPo.length }) }}
      </div>
      <template #footer>
        <div class="po-dialog-footer">
          <el-button :icon="Close" @click="copyItemDialogVisible = false">{{ t('common.cancel') }}</el-button>
          <el-button type="primary" :icon="Check" :disabled="!copyItemSelected.length" @click="addCopiedItems">
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
  RefreshLeft,
  Close,
  Search,
  Check,
  DocumentAdd,
  Document,
  FolderOpened,
  ArrowLeft,
  ArrowRight,
  TopRight,
  Edit,
  UploadFilled,
  Picture,
} from '@element-plus/icons-vue'
import AdminSection from '../../components/AdminSection.vue'
import { canWrite } from '../../security/permissions'
import { statusType, statusLabel } from '../../utils/format'
import {
  addPoDetail,
  createPo,
  deletePoDetail,
  deletePo,
  duplicatePo,
  fetchAuthenticatedDocument,
  getAllowedBrands,
  getCustomer,
  listBrands,
  listBrandBuyers,
  listBuyerPriceLists,
  listCustomers,
  listMasterItems,
  listFluorescentColors,
  listPoPage,
  listPoDetails,
  listPoForCopy,
  listAuditLogs,
  resolveBuyerUnitPrice,
  salesContractDocxPath,
  salesContractPdfPath,
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
const filterBuyer = ref('')
const customers = ref([])
const brands = ref([])
const masterItems = ref([])
const buyerCodes = ref(['NB', 'ADIDAS', 'NIKE', 'UA'])
const brandBuyerCodes = ref([])
const customerBuyerCodes = ref([])
const brandLockedCustomerId = ref(null)
const allowedBrandIds = ref([])
const selectedCustomer = ref(null)
const autoFieldMeta = reactive({
  buyer: false,
  vir_softness_type: false,
  softness: false,
  color_reference: false,
  backing: false,
  model: false,
})
const materialAdvancedOpen = ref([])
const materialFieldOverride = reactive({
  material_name: false,
  thickness_text: false,
  color: false,
  color_family: false,
  emboss: false,
  style_article: false,
})
const colorFamilyAutoMode = ref(true)

const rows = ref([])
const totalRows = ref(0)
const page = ref(1)
const pageSize = ref(20)

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
  return headers.map((h) => ({
    ...h,
    customerName: h.customer_name_snapshot || customerName(h.customer_id),
    material_hint: t('common.emptyValue'),
    etd: h.etd ? String(h.etd).slice(0, 10) : '',
  }))
}

async function quickChangeStatus(row, newStatus) {
  try {
    await updatePo(row.id, { status: newStatus })
    row.status = newStatus
    ElMessage.success(t('pages.po.statusChanged'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function load() {
  loading.value = true
  try {
    const [cust, br, mi, bpl, poPage] = await Promise.all([
      listCustomers(),
      listBrands(),
      listMasterItems(),
      listBuyerPriceLists().catch(() => []),
      listPoPage({
        q: keyword.value || undefined,
        customer_id: filterCustomerId.value || undefined,
        buyer: filterBuyer.value || undefined,
        status: filterStatus.value || undefined,
        limit: pageSize.value,
        offset: (page.value - 1) * pageSize.value,
      }),
    ])
    customers.value = cust
    brands.value = br
    masterItems.value = mi
    const extraBuyers = [...new Set(bpl.map((x) => x.buyer_code).filter(Boolean))]
    buyerCodes.value = [...new Set([...buyerCodes.value, ...extraBuyers])]
    rows.value = await enrichPoRows(poPage.items || [])
    totalRows.value = Number(poPage.total || 0)
  } catch (e) {
    ElMessage.error(e.message || t('pages.po.loadFailed'))
  } finally {
    loading.value = false
  }
}

let filterLoadTimer = null
watch([keyword, filterCustomerId, filterBuyer, filterStatus], () => {
  page.value = 1
  if (filterLoadTimer) clearTimeout(filterLoadTimer)
  filterLoadTimer = setTimeout(() => {
    load()
  }, 300)
})

watch([page, pageSize], () => {
  load()
})

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
  if (allowedBrandIds.value.length > 0) {
    return brands.value.filter((b) => allowedBrandIds.value.includes(b.id))
  }
  const cid = formModel.customer_id
  if (cid) {
    return brands.value.filter((b) => !b.customer_id || b.customer_id === cid)
  }
  return brands.value
})

const buyerCodesFiltered = computed(() => {
  if (brandBuyerCodes.value.length) return brandBuyerCodes.value
  if (customerBuyerCodes.value.length) return customerBuyerCodes.value
  if (formModel.customer_id || formModel.brand_id) return []
  return buyerCodes.value
})
const isBrandDisabled = computed(() => Boolean(formModel.customer_id))
const isBuyerDisabled = computed(() => Boolean(formModel.customer_id) || !formModel.brand_id || buyerCodesFiltered.value.length === 0)
const isPoCategoryDisabled = computed(() => !formModel.customer_id || !formModel.brand_id || !formModel.buyer)

const customerPicDisplay = computed(() => {
  if (!selectedCustomer.value) return t('common.emptyValue')
  const name = selectedCustomer.value.contact_person || selectedCustomer.value.name || ''
  const position = selectedCustomer.value.position || ''
  if (name && position) return `${name} (${position})`
  return name || position || t('common.emptyValue')
})

function parseSoftnessValue(raw) {
  const str = String(raw || '').trim()
  const first = str.match(/(\d+(?:\.\d+)?)/)
  return first ? Number(first[1]) : null
}

const softnessRangeWarning = computed(() => {
  const v = parseSoftnessValue(formModel.softness)
  if (v == null) return ''
  const buyer = String(formModel.buyer || '').toUpperCase()
  if (buyer.includes('NIKE')) {
    if (v < 2.8 || v > 3.2) return t('pages.po.softnessWarningNike')
    return ''
  }
  if (v < 2.0 || v > 3.0) return t('pages.po.softnessWarningGeneral')
  return ''
})

const nextPoNumberDisplay = computed(() => {
  if (isEditMode.value) return formModel.po_number || ''
  const now = new Date()
  const period = `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}`
  const maxSeq = rows.value.reduce((max, row) => {
    const match = row.po_number?.match(/SO-\d+-(\d+)/)
    if (match) {
      const seq = parseInt(match[1], 10)
      return Math.max(max, seq)
    }
    return max
  }, 0)
  return `SO-${period}-${String(maxSeq + 1).padStart(5, '0')}`
})

const currentStep = ref(0)

function nextStep() {
  if (currentStep.value === 0) {
    if (!formModel.customer_id) {
      formErrors.customer_id = t('pages.po.customerRequired')
      ElMessage.warning(t('pages.po.customerRequired'))
      return
    }
    if (!formModel.brand_id) {
      ElMessage.warning('Brand wajib dipilih setelah customer.')
      return
    }
    if (!formModel.buyer) {
      ElMessage.warning('Buyer wajib dipilih setelah brand.')
      return
    }
    formErrors.customer_id = ''
  }
  if (currentStep.value < 2) {
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const filteredRows = computed(() =>
  rows.value,
)

const resetFilter = () => {
  filterCustomerId.value = null
  filterStatus.value = ''
  filterBuyer.value = ''
  keyword.value = ''
  page.value = 1
  load()
}

const formDialogVisible = ref(false)
const isEditMode = ref(false)
const editingPoId = ref(null)
const editingDetailIds = ref([])
const draftLines = ref([])
const draftRiskOnly = ref(false)
const PO_DRAFT_KEY = 'po_input_dialog_draft_v1'
const draftLinesDisplay = computed(() => {
  if (!draftRiskOnly.value) return draftLines.value
  return draftLines.value.filter((line) => Boolean(line.manual_override) || Boolean(line.material_master_override))
})

const copyItemDialogVisible = ref(false)
const copyItemCustomerId = ref(null)
const copyItemSourcePo = ref([])
const copyItemSelected = ref([])
const copyItemSearch = ref('')

const copyItemFilteredPo = computed(() => {
  if (!copyItemSearch.value) return copyItemSourcePo.value
  const search = copyItemSearch.value.toLowerCase()
  return copyItemSourcePo.value.filter(item =>
    (item.material_name || '').toLowerCase().includes(search) ||
    (item.color || '').toLowerCase().includes(search) ||
    (item.source_po_number || '').toLowerCase().includes(search) ||
    (item.thickness_text || '').toLowerCase().includes(search)
  )
})

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
  unit_price_input: null,
  autoPricingEnabled: true,
  is_special_price: false,
  discount_type: 'percent',
  discount_value: 0,
})

const pricePreviewLoading = ref(false)
const previewResolvedUnitPrice = ref(null)
const fluorescentColorOptions = ref([])

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
  const prevPreview = previewResolvedUnitPrice.value
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
    const nextPreview = r.unit_price != null ? Number(r.unit_price) : null
    previewResolvedUnitPrice.value = nextPreview
    // Sinkronkan otomatis ke input harga selama user belum override manual.
    const userHasManualValue =
      formModel.unit_price_input != null &&
      prevPreview != null &&
      Number(formModel.unit_price_input) !== Number(prevPreview)
    if (!formModel.is_special_price && !userHasManualValue) {
      formModel.unit_price_input = nextPreview
    }
  } catch (e) {
    console.error('Error resolving unit price:', e)
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
const isFluorescentFamily = computed(() => String(formModel.color_family || '').toLowerCase() === 'fluorescent')
const activeSeasonLabel = computed(() => deriveSeasonLabel(formModel.order_date))
const pricingKeyIncomplete = computed(() => {
  if (!(formModel.buyer || '').trim()) return false
  return !String(formModel.material_name || '').trim() || !String(formModel.thickness_text || '').trim() || !String(formModel.color_family || '').trim()
})

const etdScheduleTotal = computed(() => {
  return etdScheduleRows.value.reduce((sum, row) => sum + (Number(row.qty) || 0), 0)
})

const etdScheduleValid = computed(() => {
  const qty = Number(formModel.quantity_order) || 0
  return etdScheduleTotal.value === qty
})

const hasSpecialPriceInLines = computed(() => {
  return draftLines.value.some(line => line.is_special_price)
})

function onSpecialPriceChange(val) {
  if (val) {
    formModel.discount_value = 0
    calculateSpecialPrice()
  } else {
    formModel.discount_value = 0
  }
}

function calculateSpecialPrice() {
  if (!formModel.is_special_price || previewResolvedUnitPrice.value == null) {
    return
  }

  const basePrice = previewResolvedUnitPrice.value
  const discountValue = formModel.discount_value || 0

  if (formModel.discount_type === 'percent') {
    formModel.unit_price_input = basePrice * (1 - discountValue / 100)
  } else {
    formModel.unit_price_input = Math.max(0, basePrice - discountValue)
  }
}

function colorFamilyLabel(v) {
  if (!v) return t('common.emptyValue')
  const k = String(v).toLowerCase()
  if (k === 'black') return t('pages.po.colorFamilyBlack')
  if (k === 'color') return t('pages.po.colorFamilyColor')
  if (k === 'fluorescent') return t('pages.po.colorFamilyFluorescent')
  return String(v)
}

function inferColorFamilyFromColor(colorValue) {
  const color = String(colorValue || '').toLowerCase()
  if (!color) return null
  if (color.includes('black') || color.includes('hitam')) return 'black'
  if (color.includes('fluo') || color.includes('fluorescent') || color.includes('neon')) return 'fluorescent'
  return 'color'
}

function materialQualityLabel(row) {
  if (row?.material_master_matched) return 'Master matched'
  if (row?.master_item_id) return 'Master override'
  return 'Input manual'
}

function materialQualityType(row) {
  if (row?.material_master_matched) return 'success'
  if (row?.master_item_id) return 'warning'
  return 'info'
}

function materialQualityTooltip(row) {
  if (row?.material_master_matched) {
    return 'Line mengikuti data master item tanpa perubahan field inti material.'
  }
  if (row?.master_item_id) {
    return 'Line pakai master item, namun ada field inti material yang dioverride.'
  }
  return 'Line diinput manual tanpa referensi master item.'
}

function deriveSeasonLabel(orderDate) {
  if (!orderDate) return ''
  const dt = new Date(orderDate)
  if (Number.isNaN(dt.getTime())) return ''
  const year = dt.getFullYear()
  const month = dt.getMonth() + 1
  return month <= 6 ? `SS ${year}` : `FW ${year}`
}

function formatFluorescentOption(opt) {
  if (!opt) return ''
  const code = opt.color_code ? ` (${opt.color_code})` : ''
  return `${opt.color_name}${code}`
}

async function loadFluorescentOptions() {
  if (!isFluorescentFamily.value) {
    fluorescentColorOptions.value = []
    return
  }
  const buyer = String(formModel.buyer || '').trim().toUpperCase()
  if (!buyer) {
    fluorescentColorOptions.value = []
    return
  }
  try {
    const seasonLabel = deriveSeasonLabel(formModel.order_date)
    fluorescentColorOptions.value = await listFluorescentColors({
      buyer_code: buyer,
      season_label: seasonLabel || undefined,
    })
  } catch {
    fluorescentColorOptions.value = []
  }
}

async function fetchFluorescentOptionsForValidation() {
  const buyer = String(formModel.buyer || '').trim().toUpperCase()
  if (!buyer) return []
  try {
    const seasonLabel = deriveSeasonLabel(formModel.order_date)
    return await listFluorescentColors({
      buyer_code: buyer,
      season_label: seasonLabel || undefined,
    })
  } catch {
    return []
  }
}

async function validateFluorescentLinesOrThrow(lines) {
  const opts = await fetchFluorescentOptionsForValidation()
  if (!opts.length) return
  const validNames = new Set(opts.map((x) => String(x.color_name || '').trim().toLowerCase()).filter(Boolean))
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i] || {}
    if (String(line.color_family || '').toLowerCase() !== 'fluorescent') continue
    const color = String(line.color || '').trim().toLowerCase()
    if (!color) continue
    if (!validNames.has(color)) {
      throw new Error(`Line ${i + 1}: warna fluorescent wajib dipilih dari master fluorescent sesuai buyer/season.`)
    }
  }
}

function isSelectedFluorescentColorValid() {
  if (!isFluorescentFamily.value) return true
  const chosen = String(formModel.color || '').trim().toLowerCase()
  if (!chosen) return true
  if (!fluorescentColorOptions.value.length) return true
  return fluorescentColorOptions.value.some((opt) => String(opt.color_name || '').trim().toLowerCase() === chosen)
}

function parseApiErrorMessage(err, fallback) {
  const raw = String(err?.message || '').trim()
  if (!raw) return fallback
  try {
    const parsed = JSON.parse(raw)
    if (typeof parsed?.detail === 'string') return parsed.detail
  } catch {
    // gunakan raw
  }
  return raw
}

function applyVirSoftDefault() {
  const b = (formModel.buyer || '').toUpperCase()
  if (!b) return
  if (b.includes('NIKE')) {
    if (!formModel.vir_softness_type) {
      formModel.vir_softness_type = 'Vir Soft'
      autoFieldMeta.vir_softness_type = true
    }
  } else if (!formModel.vir_softness_type) {
    formModel.vir_softness_type = 'Soft'
    autoFieldMeta.vir_softness_type = true
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

function normalizedText(v) {
  return String(v || '').trim().toLowerCase()
}

function applyReferenceDefaults(forceFields = []) {
  if (formModel.master_item_id) return
  const material = normalizedText(formModel.material_name)
  if (!material) return
  const thickness = normalizedText(formModel.thickness_text)
  const color = normalizedText(formModel.color)
  const style = normalizedText(formModel.style_article)

  let best = null
  let bestScore = 0
  for (const item of masterItems.value) {
    const itemMaterial = normalizedText(item.material_name)
    if (!itemMaterial) continue
    let score = 0
    if (formModel.master_item_id && item.id === formModel.master_item_id) score += 6
    if (itemMaterial === material) score += 4
    else if (itemMaterial.includes(material) || material.includes(itemMaterial)) score += 2
    if (thickness && normalizedText(item.thickness_range) === thickness) score += 2
    if (color && normalizedText(item.color) === color) score += 2
    if (style && normalizedText(item.style_article) === style) score += 2
    if (score > bestScore) {
      best = item
      bestScore = score
    }
  }

  if (!best || bestScore < 2) return
  const forceSet = new Set(forceFields)
  if ((!formModel.color_reference || forceSet.has('color_reference')) && best.color_reference) {
    formModel.color_reference = best.color_reference
    autoFieldMeta.color_reference = true
  }
  if ((!formModel.backing || forceSet.has('backing')) && best.backing) {
    formModel.backing = best.backing
    autoFieldMeta.backing = true
  }
  if ((!formModel.model || forceSet.has('model')) && best.model) {
    formModel.model = best.model
    autoFieldMeta.model = true
  }
  if ((!formModel.style_article || forceSet.has('style_article')) && best.style_article) {
    formModel.style_article = best.style_article
  }
  if ((!formModel.vir_softness_type || forceSet.has('vir_softness_type')) && best.vir_softness_type) {
    formModel.vir_softness_type = best.vir_softness_type
    autoFieldMeta.vir_softness_type = true
  }
  if ((!formModel.softness || forceSet.has('softness')) && best.softness) {
    formModel.softness = best.softness
    autoFieldMeta.softness = true
  }
}

function resetMaterialFieldOverride() {
  materialFieldOverride.material_name = false
  materialFieldOverride.thickness_text = false
  materialFieldOverride.color = false
  materialFieldOverride.color_family = false
  materialFieldOverride.emboss = false
  materialFieldOverride.style_article = false
}

function isMaterialFieldLocked(field) {
  if (!formModel.master_item_id) return false
  return !materialFieldOverride[field]
}

function enableMaterialOverride(field) {
  if (!formModel.master_item_id) return
  materialFieldOverride[field] = true
  if (field === 'color_family') colorFamilyAutoMode.value = false
}

function resetMaterialFieldToMaster(field) {
  if (!formModel.master_item_id) return
  const item = masterItems.value.find((x) => x.id === formModel.master_item_id)
  if (!item) return
  if (field === 'material_name') formModel.material_name = item.material_name || ''
  if (field === 'thickness_text') {
    formModel.thickness_text = item.thickness_range || (item.thickness_mm != null ? String(item.thickness_mm) : '')
  }
  if (field === 'color') formModel.color = item.color || ''
  if (field === 'emboss') formModel.emboss = item.emboss || ''
  if (field === 'style_article') formModel.style_article = item.style_article || ''
  if (field === 'color_family') {
    formModel.color_family = inferColorFamilyFromColor(item.color) || 'color'
    colorFamilyAutoMode.value = true
  }
  materialFieldOverride[field] = false
}

function isThicknessPricingFormatValid(v) {
  const raw = String(v || '').trim()
  if (!raw) return true
  const single = /^\d+(\.\d+)?$/
  const range = /^\d+(\.\d+)?\s*-\s*\d+(\.\d+)?$/
  return single.test(raw) || range.test(raw)
}

function resetToAuto(field) {
  if (field === 'buyer') {
    const firstBuyer = buyerCodesFiltered.value[0]
    if (firstBuyer) {
      formModel.buyer = firstBuyer
      autoFieldMeta.buyer = true
    }
    return
  }

  if (field === 'vir_softness_type') {
    formModel.vir_softness_type = ''
    autoFieldMeta.vir_softness_type = false
    applyVirSoftDefault()
    return
  }

  if (field === 'color_reference' || field === 'backing' || field === 'model') {
    if (formModel.master_item_id) {
      const item = masterItems.value.find((x) => x.id === formModel.master_item_id)
      if (item) {
        if (field === 'color_reference') {
          formModel.color_reference = item.color_reference || ''
          autoFieldMeta.color_reference = Boolean(item.color_reference)
        }
        if (field === 'backing') {
          formModel.backing = item.backing || ''
          autoFieldMeta.backing = Boolean(item.backing)
        }
        if (field === 'model') {
          formModel.model = item.model || ''
          autoFieldMeta.model = Boolean(item.model)
        }
      }
      return
    }
    if (field === 'color_reference') formModel.color_reference = ''
    if (field === 'backing') formModel.backing = ''
    if (field === 'model') formModel.model = ''
    applyReferenceDefaults([field])
  }
}

watch(
  () => formModel.buyer,
  () => {
    formModel.vir_softness_type = ''
  autoFieldMeta.vir_softness_type = false
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
  () => {
    schedulePricePreview()
    applyReferenceDefaults()
  },
)

watch(
  () => formModel.color,
  (newColor) => {
    if (!colorFamilyAutoMode.value) return
    const inferred = inferColorFamilyFromColor(newColor)
    if (inferred) formModel.color_family = inferred
  },
)

watch(
  () => [formModel.color_family, formModel.buyer, formModel.order_date],
  () => {
    loadFluorescentOptions()
  },
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

watch(
  () => formModel.etd,
  (newEtd) => {
    if (!formModel.line_etd && newEtd) {
      formModel.line_etd = newEtd
    }
  },
)

watch(
  () => formModel.line_etd,
  (newLineEtd) => {
    if (newLineEtd && formModel.quantity_order) {
      autoFillEtdSchedule()
    }
  },
)

watch(
  () => formModel.quantity_order,
  (newQty) => {
    if (newQty && formModel.line_etd) {
      autoFillEtdSchedule()
    }
  },
)

const formErrors = reactive({
  customer_id: '',
  brand_id: '',
  material_name: '',
  quantity_order: '',
  line_etd: '',
})

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
  formModel.unit_price_input = null
  formModel.autoPricingEnabled = true
  formModel.is_special_price = false
  formModel.discount_type = 'percent'
  formModel.discount_value = 0
  autoFieldMeta.buyer = false
  autoFieldMeta.vir_softness_type = false
  autoFieldMeta.softness = false
  autoFieldMeta.color_reference = false
  autoFieldMeta.backing = false
  autoFieldMeta.model = false
  editingDetailIds.value = []
  draftLines.value = []
  draftRiskOnly.value = false
  brandLockedCustomerId.value = null
  selectedCustomer.value = null
  previewResolvedUnitPrice.value = null
  fluorescentColorOptions.value = []
  colorFamilyAutoMode.value = true
  materialAdvancedOpen.value = []
  resetMaterialFieldOverride()
  clearEtdSchedule()
  formErrors.customer_id = ''
  formErrors.brand_id = ''
  formErrors.material_name = ''
  formErrors.quantity_order = ''
  formErrors.line_etd = ''
}

function getPoDraftPayload() {
  return {
    header: {
      po_number: formModel.po_number,
      customer_id: formModel.customer_id,
      brand_id: formModel.brand_id,
      po_category: formModel.po_category,
      order_date: formModel.order_date,
      buyer: formModel.buyer,
      etd: formModel.etd,
      po_customer_ref: formModel.po_customer_ref,
      remark: formModel.remark,
      billing_address: formModel.billing_address,
      delivery_address: formModel.delivery_address,
      status: formModel.status,
    },
    currentLine: {
      master_item_id: formModel.master_item_id,
      material_name: formModel.material_name,
      thickness_text: formModel.thickness_text,
      color: formModel.color,
      color_family: formModel.color_family,
      emboss: formModel.emboss,
      vir_softness_type: formModel.vir_softness_type,
      softness: formModel.softness,
      color_reference: formModel.color_reference,
      backing: formModel.backing,
      quantity_order: formModel.quantity_order,
      style_article: formModel.style_article,
      model: formModel.model,
      line_etd: formModel.line_etd,
      detail_remark: formModel.detail_remark,
      thi_line_ref: formModel.thi_line_ref,
      unit_price_input: formModel.unit_price_input,
      is_special_price: formModel.is_special_price,
      discount_type: formModel.discount_type,
      discount_value: formModel.discount_value,
    },
    draftLines: draftLines.value,
    etdScheduleRows: etdScheduleRows.value,
  }
}

function savePoDraftToLocal() {
  try {
    localStorage.setItem(PO_DRAFT_KEY, JSON.stringify(getPoDraftPayload()))
  } catch {
    // ignore local storage write error
  }
}

function clearPoDraftLocal() {
  try {
    localStorage.removeItem(PO_DRAFT_KEY)
  } catch {
    // ignore
  }
}

function applyPoDraft(data) {
  if (!data || typeof data !== 'object') return
  const header = data.header || {}
  const line = data.currentLine || {}
  formModel.po_number = header.po_number || ''
  formModel.customer_id = header.customer_id ?? null
  formModel.brand_id = header.brand_id ?? null
  formModel.po_category = header.po_category || 'production'
  formModel.order_date = header.order_date || ''
  formModel.buyer = header.buyer || ''
  formModel.etd = header.etd || ''
  formModel.po_customer_ref = header.po_customer_ref || ''
  formModel.remark = header.remark || ''
  formModel.billing_address = header.billing_address || ''
  formModel.delivery_address = header.delivery_address || ''
  formModel.status = header.status || 'draft'

  formModel.master_item_id = line.master_item_id ?? null
  formModel.material_name = line.material_name || ''
  formModel.thickness_text = line.thickness_text || ''
  formModel.color = line.color || ''
  formModel.color_family = line.color_family || null
  formModel.emboss = line.emboss || ''
  formModel.vir_softness_type = line.vir_softness_type || ''
  formModel.softness = line.softness || ''
  formModel.color_reference = line.color_reference || ''
  formModel.backing = line.backing || ''
  formModel.quantity_order = line.quantity_order || ''
  formModel.style_article = line.style_article || ''
  formModel.model = line.model || ''
  formModel.line_etd = line.line_etd || ''
  formModel.detail_remark = line.detail_remark || ''
  formModel.thi_line_ref = line.thi_line_ref || ''
  formModel.unit_price_input = line.unit_price_input ?? null
  formModel.is_special_price = Boolean(line.is_special_price)
  formModel.discount_type = line.discount_type || 'percent'
  formModel.discount_value = Number(line.discount_value || 0)

  draftLines.value = Array.isArray(data.draftLines) ? data.draftLines : []
  if (Array.isArray(data.etdScheduleRows) && data.etdScheduleRows.length) {
    etdScheduleRows.value = data.etdScheduleRows
  }
}

async function restorePoDraftIfAny() {
  let raw = ''
  try {
    raw = localStorage.getItem(PO_DRAFT_KEY) || ''
  } catch {
    raw = ''
  }
  if (!raw) return
  try {
    await ElMessageBox.confirm(
      'Ditemukan draft input PO. Lanjutkan dari draft terakhir?',
      'Lanjutkan Draft PO',
      {
        type: 'info',
        confirmButtonText: 'Lanjutkan Draft',
        cancelButtonText: 'Mulai Baru',
      },
    )
    const parsed = JSON.parse(raw)
    applyPoDraft(parsed)
    if (formModel.customer_id) await onCustomerChange()
    if (formModel.brand_id) await onBrandChange(formModel.brand_id)
    ElMessage.success('Draft PO berhasil dimuat.')
  } catch (e) {
    if (e === 'cancel') {
      clearPoDraftLocal()
    }
  }
}

function requestCloseFormDialog() {
  handlePoDialogBeforeClose(() => {
    formDialogVisible.value = false
  })
}

async function handlePoDialogBeforeClose(done) {
  if (saving.value) {
    done()
    return
  }
  if (isEditMode.value) {
    done()
    return
  }
  try {
    await ElMessageBox.confirm(
      'Simpan draft PO sebelum menutup dialog?',
      'Konfirmasi Tutup',
      {
        type: 'warning',
        distinguishCancelAndClose: true,
        confirmButtonText: 'Simpan Draft',
        cancelButtonText: 'Tutup Tanpa Simpan',
      },
    )
    savePoDraftToLocal()
    ElMessage.success('Draft PO disimpan. Kamu bisa lanjutkan nanti.')
    done()
  } catch {
    clearPoDraftLocal()
    done()
  }
}

function saveDraftAndClose() {
  savePoDraftToLocal()
  ElMessage.success('Draft PO disimpan. Kamu bisa lanjutkan nanti.')
  formDialogVisible.value = false
}

async function onCustomerChange() {
  if (brandLockedCustomerId.value) {
    formModel.customer_id = brandLockedCustomerId.value
    return
  }
  formModel.brand_id = null
  brandBuyerCodes.value = []
  customerBuyerCodes.value = []
  formModel.buyer = ''
  allowedBrandIds.value = []
  const cid = formModel.customer_id
  if (cid) {
    try {
      const [allowed, customer] = await Promise.all([
        getAllowedBrands(cid),
        getCustomer(cid),
      ])
      allowedBrandIds.value = allowed.map((b) => b.id)
      selectedCustomer.value = customer || null
      if (allowedBrandIds.value.length > 0) {
        const stillValid = formModel.brand_id && allowedBrandIds.value.includes(formModel.brand_id)
        formModel.brand_id = stillValid ? formModel.brand_id : allowedBrandIds.value[0]
        await onBrandChange(formModel.brand_id)
      } else {
        formModel.brand_id = null
      }
      if (allowedBrandIds.value.length) {
        const buyersByBrand = await Promise.all(
          allowedBrandIds.value.map((id) => listBrandBuyers(id).catch(() => [])),
        )
        customerBuyerCodes.value = [
          ...new Set(
            buyersByBrand
              .flat()
              .map((x) => (x?.buyer_code || '').trim())
              .filter(Boolean),
          ),
        ]
        if (customerBuyerCodes.value.length > 0) {
          formModel.buyer = customerBuyerCodes.value[0]
          autoFieldMeta.buyer = true
        } else {
          formModel.buyer = ''
          autoFieldMeta.buyer = false
        }
      }
      if (customer) {
        formModel.billing_address = customer.address || ''
        formModel.delivery_address = customer.address || ''
      }
    } catch {
      allowedBrandIds.value = []
      selectedCustomer.value = null
    }
  } else {
    formModel.billing_address = ''
    formModel.delivery_address = ''
    customerBuyerCodes.value = []
    selectedCustomer.value = null
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
    if (brandBuyerCodes.value.length) {
      if (!brandBuyerCodes.value.includes(formModel.buyer)) {
        formModel.buyer = brandBuyerCodes.value[0]
        autoFieldMeta.buyer = true
      }
    } else if (formModel.brand_id) {
      formModel.buyer = ''
      autoFieldMeta.buyer = false
    }
  } catch {
    brandBuyerCodes.value = []
  }
}

function onMasterItemChange(masterItemId) {
  const item = masterItems.value.find((x) => x.id === masterItemId)
  resetMaterialFieldOverride()
  colorFamilyAutoMode.value = true
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
  // Auto-fill dari MasterItem
  formModel.material_name = item.material_name || ''
  formModel.color = item.color || ''
  formModel.emboss = item.emboss || ''
  // Prioritaskan thickness_range, fallback ke thickness_mm
  formModel.thickness_text = item.thickness_range || (item.thickness_mm != null ? String(item.thickness_mm) : '')
  formModel.softness = item.softness || ''
  autoFieldMeta.softness = Boolean(item.softness)
  formModel.color_reference = item.color_reference || ''
  autoFieldMeta.color_reference = Boolean(item.color_reference)
  formModel.backing = item.backing || ''
  autoFieldMeta.backing = Boolean(item.backing)
  formModel.quantity_order = item.quantity_order_default != null ? String(item.quantity_order_default) : ''
  formModel.style_article = item.style_article || ''
  formModel.model = item.model || ''
  autoFieldMeta.model = Boolean(item.model)
  // Auto-detect color_family dari color name
  if (item.color) {
    formModel.color_family = inferColorFamilyFromColor(item.color)
  }
  // Set unit price dari resolved price jika ada
  if (previewResolvedUnitPrice.value != null) {
    formModel.unit_price_input = previewResolvedUnitPrice.value
  } else {
    formModel.unit_price_input = null
  }
  applyReferenceDefaults(['color_reference', 'backing', 'model', 'style_article', 'vir_softness_type', 'softness'])
  // Auto-generate thi_line_ref
  applyLotPrefix()
}

const openCreateDialog = async () => {
  isEditMode.value = false
  editingPoId.value = null
  resetForm()
  brandLockedCustomerId.value = null
  currentStep.value = 0
  formDialogVisible.value = true
  await restorePoDraftIfAny()
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

  if (formModel.is_special_price && formModel.unit_price_input != null) {
    body.base_price = previewResolvedUnitPrice.value
    body.is_special_price = true
    body.discount_type = formModel.discount_type
    body.discount_value = formModel.discount_value
  }

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

function handleEnterKey(e) {
  if (e.ctrlKey || e.metaKey) {
    pushCurrentLine(false)
  }
}

async function pushCurrentLine(copyCurrent = false) {
  formErrors.material_name = ''
  formErrors.quantity_order = ''
  formErrors.line_etd = ''

  if (!copyCurrent) {
    if (!formModel.material_name && !formModel.master_item_id) {
      formErrors.material_name = t('pages.po.materialRequired')
      ElMessage.warning(t('pages.po.materialRequired'))
      return
    }
    if (!formModel.quantity_order) {
      formErrors.quantity_order = t('pages.po.qtyRequired')
      ElMessage.warning(t('pages.po.qtyRequired'))
      return
    }
    if (pricingKeyIncomplete.value) {
      ElMessage.warning('Untuk buyer pricing, material, ketebalan, dan kategori warna wajib terisi.')
      return
    }
    if (!isThicknessPricingFormatValid(formModel.thickness_text)) {
      ElMessage.warning('Format ketebalan harus angka tunggal (contoh: 1.4) atau rentang (contoh: 1.2-1.4).')
      return
    }
    if (!isSelectedFluorescentColorValid()) {
      ElMessage.warning('Warna fluorescent wajib dipilih dari master fluorescent sesuai buyer/season.')
      return
    }
  }

  const line = await buildCurrentDetailBody()
  if (formModel.buyer?.trim() && line.unit_price == null) {
    ElMessage.warning(t('pages.po.priceNotFound'))
  }
  const hasAutoPrice = previewResolvedUnitPrice.value != null
  const isManualOverride =
    hasAutoPrice &&
    line.unit_price != null &&
    Number(line.unit_price) !== Number(previewResolvedUnitPrice.value)
  const hasMaterialOverride = Object.values(materialFieldOverride).some(Boolean)
  line.manual_override = Boolean(isManualOverride)
  line.material_master_override = Boolean(hasMaterialOverride)
  line.material_master_matched = Boolean(line.master_item_id) && !hasMaterialOverride
  if (
    line.unit_price != null &&
    previewResolvedUnitPrice.value != null &&
    Number(line.unit_price) !== Number(previewResolvedUnitPrice.value) &&
    !String(formModel.detail_remark || '').trim()
  ) {
    ElMessage.warning('Jika harga diubah manual, mohon isi Detail Remark sebagai alasan override harga.')
    return
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
    autoFieldMeta.softness = false
    formModel.color_reference = ''
    autoFieldMeta.color_reference = false
    formModel.backing = ''
    autoFieldMeta.backing = false
    formModel.quantity_order = ''
    formModel.style_article = ''
    formModel.model = ''
    autoFieldMeta.model = false
    formModel.line_etd = ''
    formModel.detail_remark = ''
    formModel.thi_line_ref = ''
    resetMaterialFieldOverride()
    colorFamilyAutoMode.value = true
    formErrors.material_name = ''
    formErrors.quantity_order = ''
    formErrors.line_etd = ''
  }
}

function removeDraftLine(index) {
  draftLines.value.splice(index, 1)
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
  try {
    selectedCustomer.value = formModel.customer_id ? await getCustomer(formModel.customer_id) : null
  } catch {
    selectedCustomer.value = null
  }
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
      manual_override: false,
      material_master_override: false,
      material_master_matched: Boolean(d.master_item_id),
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
  if (!isSelectedFluorescentColorValid()) {
    ElMessage.warning('Warna fluorescent wajib dipilih dari master fluorescent sesuai buyer/season.')
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
    }
    const detailBodies = draftLines.value.length ? draftLines.value : [await buildCurrentDetailBody()]
    await validateFluorescentLinesOrThrow(detailBodies)

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
            await setPoDetailDeliverySchedules(existingId, schedules)
          }
          keepIds.push(existingId)
        } else {
          const createdDetail = await addPoDetail(editingPoId.value, rowBody)
          if (schedules.length) {
            await setPoDetailDeliverySchedules(createdDetail.id, schedules)
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
          await setPoDetailDeliverySchedules(createdDetail.id, schedules)
        }
      }
    }
    ElMessage.success(t('pages.customers.saved'))
    clearPoDraftLocal()
    formDialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
  } finally {
    saving.value = false
  }
}

const detailDialogVisible = ref(false)
const detailView = ref(null)
const detailLines = ref([])
const detailAudit = ref([])

const nonEmptyAudit = computed(() => {
  return detailAudit.value.filter(a => a.before || a.after)
})

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

const FIELD_LABELS = {
  quantity_order: 'Qty Order',
  unit_price: 'Harga USD',
  line_etd: 'ETD Baris',
  thi_line_ref: 'THI/Lot',
  color_family: 'Kategori Warna',
  color_standard: 'Standard Warna',
  thickness: 'Ketebalan',
  softness: 'Kelembutan',
  backing: 'Backing',
  emboss: 'Timbulan',
  style_article: 'Style/Article',
  model: 'Model',
  material_name: 'Material',
  color: 'Warna',
  remark: 'Catatan',
  status: 'Status',
  delivery_schedules: 'Jadwal Pengiriman',
  po_number: 'No. PO',
  po_id: 'PO ID',
  po_header_id: 'PO Header ID',
}

function auditFieldLabel(key) {
  return FIELD_LABELS[key] || key
}

function auditChangedFields(a) {
  const before = a.before || {}
  const after = a.after || {}
  const allKeys = new Set([...Object.keys(before), ...Object.keys(after)])
  const changes = []
  const skipKeys = new Set(['id', 'created_at', 'updated_at', 'po_header_id'])

  for (const key of allKeys) {
    if (skipKeys.has(key)) continue
    const b = before[key]
    const af = after[key]
    if (JSON.stringify(b) !== JSON.stringify(af)) {
      let change = null
      if (typeof b === 'number' && typeof af === 'number') {
        const diff = af - b
        change = diff > 0 ? `+${diff}` : `${diff}`
      }
      changes.push({ key, before: b, after: af, change })
    }
  }

  // Deduplicate: combine color and color_family if both changed to same display value
  const colorIdx = changes.findIndex(c => c.key === 'color')
  const colorFamilyIdx = changes.findIndex(c => c.key === 'color_family')
  if (colorIdx !== -1 && colorFamilyIdx !== -1) {
    const colorVal = changes[colorIdx].after
    const colorFamilyVal = changes[colorFamilyIdx].after
    if (colorVal === colorFamilyVal) {
      // Merge into color, remove color_family
      changes[colorIdx].key = 'color_both'
      changes[colorIdx].displayLabel = 'Warna / Kategori'
      changes.splice(colorFamilyIdx, 1)
    }
  }

  return changes
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

async function downloadSalesContractPdf(row) {
  if (!row?.id) return
  try {
    await fetchAuthenticatedDocument(salesContractPdfPath(row.id), {
      mode: 'download',
      downloadFallbackName: `sales_contract_${row.po_number || row.id}.pdf`,
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

async function downloadSalesContractDocx(row) {
  if (!row?.id) return
  try {
    await fetchAuthenticatedDocument(salesContractDocxPath(row.id), {
      mode: 'download',
      downloadFallbackName: `sales_contract_${row.po_number || row.id}.docx`,
    })
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
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
    manual_override: false,
    material_master_override: false,
    material_master_matched: Boolean(d.master_item_id),
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

:deep(.po-fullscreen-dialog.el-dialog) {
  border-radius: 14px;
  overflow: hidden !important;
  box-shadow: 0 16px 44px rgba(15, 23, 42, 0.18);
  max-height: 92vh;
  display: flex !important;
  flex-direction: column !important;
}

:deep(.po-fullscreen-dialog .el-dialog__header) {
  padding: 0;
  margin: 0;
  background: transparent;
  border-bottom: 1px solid var(--el-border-color-light);
  flex-shrink: 0;
}

:deep(.po-fullscreen-dialog .el-dialog__headerbtn) {
  display: none !important;
}

:deep(.po-fullscreen-dialog .el-dialog__body) {
  flex: 1 !important;
  padding: 0 !important;
  background: var(--el-bg-color-page);
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
  min-height: 0 !important;
}

.po-dialog-header {
  padding: 16px 20px 12px;
  color: var(--el-text-color-primary);
  position: relative;
}

.po-dialog-close {
  position: absolute;
  top: 12px;
  right: 14px;
  font-size: 18px;
  color: var(--el-text-color-primary);
  cursor: pointer;
  opacity: 0.9;
  border-radius: 999px;
  padding: 4px;
  background: var(--el-fill-color-light);
}

.po-dialog-close:hover {
  opacity: 1;
  background: var(--el-fill-color);
}

.po-dialog-title-area {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.po-dialog-icon {
  font-size: 20px;
  color: var(--el-color-primary);
}

.po-dialog-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.po-dialog-steps-wrapper {
  width: 100%;
  margin: 8px 0 4px;
  padding: 0 4px;
  display: flex;
  justify-content: center;
}

:deep(.po-dialog-steps .el-step.is-simple .el-step__title) {
  font-size: 13px;
}

.po-dialog-content {
  width: 100%;
  background: var(--el-bg-color);
  padding: 20px 22px;
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.step-content {
  min-height: 320px;
}

.step-content :deep(h3) {
  margin-bottom: 14px;
}

.step-content :deep(.el-form-item) {
  margin-bottom: 10px;
}

.material-step-grid :deep(.el-form-item__label) {
  line-height: 1.35;
  margin-bottom: 2px;
}

.material-step-grid :deep(.el-input),
.material-step-grid :deep(.el-select),
.material-step-grid :deep(.el-date-editor),
.material-step-grid :deep(.el-input-number) {
  width: 100%;
}

.material-step-grid :deep(.el-form-item__content) {
  width: 100%;
}

.field-lock-row {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 4px;
  width: 100%;
}

.field-lock-row :deep(.el-input),
.field-lock-row :deep(.el-select) {
  width: 100%;
  min-width: 0;
}

.field-lock-row :deep(.el-button) {
  align-self: flex-start;
  margin-top: 0;
}

.field-stack-row {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 4px;
  width: 100%;
}

.field-stack-row :deep(.el-input),
.field-stack-row :deep(.el-select),
.field-stack-row :deep(.el-date-editor),
.field-stack-row :deep(.el-input-number) {
  width: 100%;
}

.po-dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
  background: var(--el-bg-color);
  border-top: 1px solid var(--el-border-color-light);
  flex-shrink: 0;
  gap: 10px;
}

.footer-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.step-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-color-primary);
  min-width: 120px;
  text-align: center;
}

:deep(.footer-nav .el-button) {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: 50%;
  font-size: 14px;
  font-weight: bold;
}

:deep(.po-dialog-footer .el-button) {
  padding: 8px 14px;
}

:deep(.po-dialog-footer .el-button .el-icon) {
  margin-right: 4px;
}

.po-price-readonly :deep(.el-input__wrapper) {
  background-color: var(--el-fill-color-light);
}

:deep(.po-fullscreen-dialog .el-divider__text) {
  font-weight: 600;
}

.etd-schedule-table {
  width: 100%;
}

.etd-schedule-table :deep(.el-table__header-wrapper) {
  display: none;
}

</style>
