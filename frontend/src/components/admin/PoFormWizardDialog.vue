<template>
  <el-dialog
    v-model="w.formDialogVisible"
    :fullscreen="false"
    width="90%"
    top="3vh"
    destroy-on-close
    class="po-fullscreen-dialog"
    :before-close="w.handlePoDialogBeforeClose"
  >
    <template #header>
      <div class="po-dialog-header">
        <el-icon class="po-dialog-close" @click="w.requestCloseFormDialog"><Close /></el-icon>
        <div class="po-dialog-title-area">
          <el-icon class="po-dialog-icon"><DocumentAdd /></el-icon>
          <span class="po-dialog-title">
            {{ w.isEditMode ? t('pages.poEntry.title') + ' ' + t('pages.po.editSuffix') : t('pages.poEntry.title') }}
          </span>
          <el-tag v-if="!w.isEditMode" type="info" effect="plain" size="small">
            {{ w.nextPoNumberDisplay }}
          </el-tag>
          <el-tag v-else type="primary" effect="plain" size="small">
            {{ w.formModel.po_number }}
          </el-tag>
          <el-button
            v-if="w.isEditMode && w.canManage"
            type="warning"
            size="small"
            class="ml-2 shrink-0"
            @click="w.openMarketingReviseDialog"
          >
            {{ t('pages.po.marketingReviseOpen') }}
          </el-button>
        </div>
        <div class="po-dialog-steps-wrapper">
          <el-steps class="mb-4 po-dialog-steps w-full" :space="100" :active="w.currentStep" simple>
            <el-step :title="t('pages.po.step1Title')" :icon="Edit" />
            <el-step :title="t('pages.po.step2Title')" :icon="UploadFilled" />
            <el-step :title="t('pages.po.step3Title')" :icon="Picture" />
          </el-steps>
        </div>
      </div>
    </template>

    <div class="po-dialog-content">
      <el-form label-position="top" class="po-dialog-form" @keydown.enter.prevent="w.handleEnterKey">
        <div v-show="w.currentStep === 0" class="step-content">
          <h3 class="text-lg font-semibold mb-4">{{ t('pages.po.customerSoSection') }}</h3>
          <el-row :gutter="16" class="material-step-grid">
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('common.customer')" required>
                <el-select
                  v-model="w.formModel.customer_id"
                  filterable
                  clearable
                  class="w-full"
                  :placeholder="t('common.placeholder.customer')"
                  :disabled="Boolean(w.brandLockedCustomerId)"
                  :error="w.formErrors.customer_id"
                  @change="w.onCustomerChange"
                >
                  <el-option
                    v-for="c in w.customers"
                    :key="c.id"
                    :label="w.formatCustomerOption(c)"
                    :value="c.id"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('pages.po.customerPic')">
                <el-input :model-value="w.customerPicDisplay" readonly />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('pages.po.brand')">
                <el-select
                  v-model="w.formModel.brand_id"
                  clearable
                  filterable
                  class="w-full"
                  :placeholder="t('pages.po.brand')"
                  :disabled="w.isBrandDisabled"
                  @change="w.onBrandChange"
                >
                  <el-option
                    v-for="b in w.brandsFiltered"
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
                  v-model="w.formModel.buyer"
                  filterable
                  class="w-full"
                  :placeholder="t('common.placeholder.buyer')"
                  :disabled="w.isBuyerDisabled"
                  @change="w.autoFieldMeta.buyer = false"
                >
                  <el-option v-for="b in w.buyerCodesFiltered" :key="b" :label="b" :value="b" />
                </el-select>
                <div class="mt-2 flex items-center gap-2">
                  <el-tag v-if="w.autoFieldMeta.buyer && w.formModel.buyer" size="small" type="success">
                    {{ t('pages.po.autoFilled') }}
                  </el-tag>
                  <el-button v-if="w.formModel.buyer" link type="primary" size="small" @click="w.resetToAuto('buyer')">
                    {{ t('pages.po.resetToAuto') }}
                  </el-button>
                </div>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('common.poCategory')">
                <el-select v-model="w.formModel.po_category" class="w-full" :placeholder="t('common.category')" :disabled="w.isPoCategoryDisabled">
                  <el-option :label="t('status.production')" value="production" />
                  <el-option :label="t('status.subkon')" value="subcont" />
                  <el-option :label="t('status.retur')" value="return" />
                  <el-option :label="t('status.sample')" value="sample" />
                  <el-option :label="t('status.claim')" value="claim" />
                  <el-option :label="t('status.suede')" value="suede" />
                </el-select>
                <el-radio-group v-model="w.formModel.po_category" size="small" class="mt-2" :disabled="w.isPoCategoryDisabled">
                  <el-radio-button value="production">{{ t('status.production') }}</el-radio-button>
                  <el-radio-button value="sample">{{ t('status.sample') }}</el-radio-button>
                  <el-radio-button value="subcont">{{ t('status.subcont') }}</el-radio-button>
                  <el-radio-button value="return">{{ t('status.return') }}</el-radio-button>
                  <el-radio-button value="claim">{{ t('status.claim') }}</el-radio-button>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('common.factoryCode')">
                <el-input
                  v-model="w.formModel.factory_code"
                  readonly
                  disabled
                  maxlength="32"
                  :placeholder="t('common.placeholder.factoryCode')"
                />
                <div class="mt-2 flex items-center gap-2">
                  <el-tag v-if="w.formModel.factory_code" size="small" type="success">
                    {{ t('pages.po.autoFilled') }}
                  </el-tag>
                </div>
                <span class="text-xs text-slate-500">{{ t('pages.po.factoryCodeHint') }}</span>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('common.poNo')">
                <el-input :model-value="w.isEditMode ? w.formModel.po_number : w.nextPoNumberDisplay" disabled />
                <span class="text-xs text-slate-500">{{ t('pages.po.autoGenerateHint') }}</span>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item
                :label="t('pages.po.poCustomerRef')"
                :error="w.formErrors.po_customer_ref || undefined"
              >
                <el-input v-model="w.formModel.po_customer_ref" clearable maxlength="255" />
                <span v-if="!w.formErrors.po_customer_ref" class="text-xs text-slate-500">{{ t('pages.po.poCustomerRefHint') }}</span>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('common.orderDate')">
                <el-date-picker
                  v-model="w.formModel.order_date"
                  type="date"
                  class="w-full"
                  value-format="YYYY-MM-DD"
                  :disabled="w.orderDateLocked"
                />
                <div v-if="w.orderDateLocked" class="text-xs text-slate-500 mt-1">{{ t('pages.po.orderDateLockedHint') }}</div>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('pages.po.billingAddress')">
                <el-input v-model="w.formModel.billing_address" type="textarea" :rows="2" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('pages.po.deliveryAddress')">
                <el-input v-model="w.formModel.delivery_address" type="textarea" :rows="2" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div v-show="w.currentStep === 1" class="step-content">
          <h3 class="text-lg font-semibold mb-4">{{ t('pages.po.step2Title') }}</h3>
          <el-row :gutter="16" class="material-step-grid">
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('common.material')" :error="w.formErrors.material_name">
                <div class="field-lock-row">
                  <el-select
                    v-model="w.formModel.material_name"
                    filterable
                    allow-create
                    default-first-option
                    clearable
                    class="w-full"
                    :placeholder="t('pages.po.materialCascadePlaceholder')"
                    :disabled="w.isMaterialFieldLocked('material_name')"
                    @change="w.onPickedMaterialDimension"
                  >
                    <el-option v-for="opt in w.materialDimensionOptions" :key="opt" :label="opt" :value="opt" />
                  </el-select>
                  <div class="mt-1 flex items-center gap-2">
                    <el-button
                      v-if="w.isMaterialFieldLocked('material_name')"
                      link
                      type="primary"
                      size="small"
                      @click="w.enableMaterialOverride('material_name')"
                    >
                      Override
                    </el-button>
                    <el-button
                      v-else-if="w.formModel.master_item_id && w.materialFieldOverride.material_name"
                      link
                      type="primary"
                      size="small"
                      @click="w.resetMaterialFieldToMaster('material_name')"
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
                  <el-select
                    v-model="w.formModel.thickness_text"
                    clearable
                    filterable
                    allow-create
                    default-first-option
                    class="w-full"
                    :placeholder="t('pages.po.thicknessCascadePlaceholder')"
                    :disabled="w.isMaterialFieldLocked('thickness_text') || !String(w.formModel.material_name || '').trim()"
                    @change="w.onPickedThicknessDimension"
                  >
                    <el-option
                      v-for="opt in w.thicknessDimensionOptions"
                      :key="opt"
                      :label="w.formatThicknessDisplay(opt)"
                      :value="opt"
                    />
                  </el-select>
                  <div class="mt-1 flex items-center gap-2">
                    <el-button
                      v-if="w.isMaterialFieldLocked('thickness_text')"
                      link
                      type="primary"
                      size="small"
                      @click="w.enableMaterialOverride('thickness_text')"
                    >
                      Override
                    </el-button>
                    <el-button
                      v-else-if="w.formModel.master_item_id && w.materialFieldOverride.thickness_text"
                      link
                      type="primary"
                      size="small"
                      @click="w.resetMaterialFieldToMaster('thickness_text')"
                    >
                      Reset
                    </el-button>
                  </div>
                </div>
                <span class="text-xs text-slate-500">{{ t('pages.po.thicknessRangeFormatHint') }}</span>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('common.color')">
                <div class="field-lock-row">
                  <el-select
                    v-if="w.isFluorescentFamily"
                    v-model="w.formModel.color"
                    clearable
                    filterable
                    class="w-full"
                    :placeholder="t('common.placeholder.color')"
                    :disabled="w.isMaterialFieldLocked('color') || !String(w.formModel.material_name || '').trim() || !String(w.formModel.thickness_text || '').trim()"
                  >
                    <el-option
                      v-for="opt in w.poColorCascadeOptions"
                      :key="opt.id"
                      :label="opt._label"
                      :value="opt.color_name"
                    />
                  </el-select>
                  <el-select
                    v-else
                    v-model="w.formModel.color"
                    filterable
                    allow-create
                    default-first-option
                    clearable
                    class="w-full"
                    :placeholder="t('common.placeholder.color')"
                    :disabled="w.isMaterialFieldLocked('color') || !String(w.formModel.material_name || '').trim() || !String(w.formModel.thickness_text || '').trim()"
                  >
                    <el-option v-for="c in w.colorDimensionOptions" :key="c" :label="c" :value="c" />
                  </el-select>
                  <div class="mt-1">
                    <el-button
                      v-if="w.isMaterialFieldLocked('color')"
                      link
                      type="primary"
                      size="small"
                      @click="w.enableMaterialOverride('color')"
                    >
                      Override warna
                    </el-button>
                    <el-button
                      v-else-if="w.formModel.master_item_id && w.materialFieldOverride.color"
                      link
                      type="primary"
                      size="small"
                      @click="w.resetMaterialFieldToMaster('color')"
                    >
                      Reset warna
                    </el-button>
                  </div>
                </div>
                <div v-if="w.isFluorescentFamily" class="mt-1 text-xs text-slate-500">
                  Season aktif: {{ w.activeSeasonLabel || '-' }} · {{ t('common.masterLabel') }} fluorescent: {{ w.fluorescentColorOptions.length }} opsi
                </div>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('pages.po.emboss')">
                <div class="field-lock-row">
                  <el-input v-model="w.formModel.emboss" class="w-full" clearable :disabled="w.isMaterialFieldLocked('emboss')" />
                  <el-button
                    v-if="w.isMaterialFieldLocked('emboss')"
                    link
                    type="primary"
                    size="small"
                    @click="w.enableMaterialOverride('emboss')"
                  >
                    Override
                  </el-button>
                  <el-button
                    v-else-if="w.formModel.master_item_id && w.materialFieldOverride.emboss"
                    link
                    type="primary"
                    size="small"
                    @click="w.resetMaterialFieldToMaster('emboss')"
                  >
                    Reset
                  </el-button>
                </div>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('pages.po.colorFamily')">
                <div class="field-lock-row">
                  <el-select
                    v-model="w.formModel.color_family"
                    clearable
                    class="w-full"
                    :disabled="w.isMaterialFieldLocked('color_family')"
                    @change="w.colorFamilyAutoMode = false"
                  >
                    <el-option :label="t('pages.po.colorFamilyBlack')" value="black" />
                    <el-option :label="t('pages.po.colorFamilyColor')" value="color" />
                    <el-option :label="t('pages.po.colorFamilyFluorescent')" value="fluorescent" />
                  </el-select>
                  <el-button
                    v-if="w.isMaterialFieldLocked('color_family')"
                    link
                    type="primary"
                    size="small"
                    @click="w.enableMaterialOverride('color_family')"
                  >
                    Override
                  </el-button>
                  <el-button
                    v-else-if="w.formModel.master_item_id && w.materialFieldOverride.color_family"
                    link
                    type="primary"
                    size="small"
                    @click="w.resetMaterialFieldToMaster('color_family')"
                  >
                    Reset
                  </el-button>
                </div>
              </el-form-item>
            </el-col>
            <el-col v-if="w.materialStepFillStep > 0" :span="24">
              <el-alert
                type="info"
                :closable="false"
                show-icon
                class="mb-2"
                :title="t('pages.po.materialStepFillOrderTitle', { step: w.materialStepFillStep })"
              >
                <p class="text-sm mb-1">{{ t('pages.po.materialStepFillOrder1') }}</p>
                <p v-if="w.materialStepFillStep === 2" class="text-sm">{{ t('pages.po.materialStepFillOrder2') }}</p>
                <p v-else-if="w.materialStepFillStep === 3" class="text-sm">{{ t('pages.po.materialStepFillOrder3') }}</p>
                <p v-else-if="w.materialStepFillStep === 4" class="text-sm">{{ t('pages.po.materialStepFillOrder4') }}</p>
                <p v-else-if="w.materialStepFillStep === 5" class="text-sm">{{ t('pages.po.materialStepFillOrder5') }}</p>
              </el-alert>
            </el-col>
            <el-col :span="24">
              <div v-if="w.formModel.master_item_id" class="flex flex-wrap items-center gap-2 mb-2">
                <el-tag type="success" closable @close="w.clearLinkedMasterItem">
                  {{ t('pages.po.masterLinkedTag') }}: {{ w.resolvedMasterItemLabel }}
                </el-tag>
                <span v-if="w.masterResolveLoading" class="text-xs text-slate-500">{{ t('pages.po.resolvingMaster') }}</span>
              </div>
              <el-alert
                v-else-if="w.lastResolveHadNoMaster && w.materialThicknessColorComplete"
                type="warning"
                :closable="false"
                show-icon
                class="mb-2"
                :title="t('pages.po.masterNotMatchedHint')"
              />
            </el-col>
            <el-col :span="24">
              <div class="mb-2">
                <div
                  v-if="w.selectedSwatchRecipe && !w.swatchPickerOpen"
                  class="flex flex-wrap items-center gap-2 rounded border border-emerald-200 bg-emerald-50/80 px-3 py-2"
                >
                  <el-tag type="success" size="small">{{ t('pages.po.swatchActiveTag') }}</el-tag>
                  <span class="text-sm text-slate-700">
                    {{ w.swatchOptionLabel(w.selectedSwatchRecipe) }}
                    <template v-if="w.formModel.backing">
                      · {{ t('common.backing') }}: {{ w.formModel.backing }}
                    </template>
                  </span>
                  <el-button link type="primary" size="small" @click="w.openSwatchPicker">
                    {{ t('pages.po.swatchChangeRecipe') }}
                  </el-button>
                  <el-button link type="danger" size="small" @click="w.clearSwatchSelection">
                    {{ t('pages.po.swatchClearRecipe') }}
                  </el-button>
                </div>
                <template v-else>
                  <el-select
                    v-model="w.selectedSwatchId"
                    filterable
                    clearable
                    class="w-full"
                    :placeholder="t('pages.po.swatchPickerPlaceholder')"
                    :loading="w.colorSwatchLoading"
                    :disabled="!w.poFactoryKeyForSwatch() || !w.formModel.buyer"
                    @change="w.applyColorSwatch"
                  >
                    <el-option
                      v-for="s in w.colorSwatchOptions"
                      :key="s.id"
                      :label="w.swatchOptionLabel(s)"
                      :value="s.id"
                    />
                  </el-select>
                  <div class="mt-1 flex flex-wrap items-center gap-2">
                    <el-checkbox v-model="w.swatchAllMaterials" @change="w.loadColorSwatchOptions">
                      {{ t('pages.po.swatchAllMaterials') }}
                    </el-checkbox>
                  </div>
                </template>
                <p v-if="w.swatchRetriedWithoutMaterial" class="mt-1 text-xs text-slate-500">
                  {{ t('pages.po.swatchRetriedHint') }}
                </p>
                <p v-if="w.swatchHelperMessage && !w.selectedSwatchRecipe" class="mt-1 text-xs text-amber-600">
                  {{ w.swatchHelperMessage }}
                </p>
                <p
                  v-if="w.swatchFieldsLocked && w.swatchPickerOpen && !w.selectedSwatchRecipe"
                  class="mt-1 text-xs text-slate-500"
                >
                  {{ t('pages.po.swatchFieldsLockedHint') }}
                </p>
              </div>
            </el-col>
            <el-col :xs="24">
              <el-alert
                v-if="w.pricingKeyIncomplete"
                title="Pricing key belum lengkap: buyer + material + ketebalan + kategori warna wajib terisi."
                type="warning"
                :closable="false"
                show-icon
                class="mb-2"
              />
              <div class="mb-2 flex flex-wrap items-center justify-between gap-2">
                <span class="font-medium text-slate-700">
                  {{
                    w.showColorStandardBackingFields
                      ? t('pages.po.materialExtraGroupTitle')
                      : t('pages.po.materialModelArticleTitle')
                  }}
                </span>
                <div class="flex flex-wrap items-center gap-2">
                  <el-button
                    v-if="w.swatchFieldsLocked"
                    link
                    type="primary"
                    size="small"
                    @click="w.enableSwatchManualEdit"
                  >
                    {{ t('pages.po.swatchEditFieldsManual') }}
                  </el-button>
                  <el-button
                    v-else-if="w.selectedSwatchRecipe && w.swatchFieldsManualEdit"
                    link
                    type="primary"
                    size="small"
                    @click="w.reapplySelectedSwatchRecipe()"
                  >
                    {{ t('pages.po.swatchResyncFromRecipe') }}
                  </el-button>
                </div>
              </div>
              <el-row :gutter="16">
                <el-col v-if="w.showColorStandardBackingFields" :xs="24" :md="6">
                  <el-form-item :label="t('pages.po.colorStandart')">
                    <el-input
                      v-model="w.formModel.color_standard"
                      :readonly="w.swatchFieldsLocked"
                      :disabled="w.swatchFieldsLocked"
                      @input="w.autoFieldMeta.color_standard = false"
                    />
                    <div class="mt-2 flex items-center gap-2">
                      <el-tag v-if="w.swatchFieldsLocked && w.formModel.color_standard" size="small" type="success">
                        {{ t('pages.po.swatchFilledFromRecipe') }}
                      </el-tag>
                      <el-tag v-else-if="w.autoFieldMeta.color_standard && w.formModel.color_standard" size="small" type="success">
                        {{ t('pages.po.autoFilled') }}
                      </el-tag>
                    </div>
                  </el-form-item>
                </el-col>
                <el-col v-if="w.showColorStandardBackingFields" :xs="24" :md="6">
                  <el-form-item :label="t('common.backing')">
                    <el-input
                      v-model="w.formModel.backing"
                      :readonly="w.swatchFieldsLocked"
                      :disabled="w.swatchFieldsLocked"
                      @input="w.autoFieldMeta.backing = false"
                    />
                    <div class="mt-2 flex items-center gap-2">
                      <el-tag v-if="w.swatchFieldsLocked && w.formModel.backing" size="small" type="success">
                        {{ t('pages.po.swatchFilledFromRecipe') }}
                      </el-tag>
                      <el-tag v-else-if="w.autoFieldMeta.backing && w.formModel.backing" size="small" type="success">
                        {{ t('pages.po.autoFilled') }}
                      </el-tag>
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="w.showColorStandardBackingFields ? 6 : 12">
                  <el-form-item :label="t('common.model')">
                    <el-input v-model="w.formModel.model" :placeholder="t('common.placeholder.model')" @input="w.autoFieldMeta.model = false" />
                    <div class="mt-2 flex items-center gap-2">
                      <el-tag v-if="w.autoFieldMeta.model && w.formModel.model" size="small" type="success">
                        {{ t('pages.po.autoFilled') }}
                      </el-tag>
                      <el-button v-if="w.formModel.model" link type="primary" size="small" @click="w.resetToAuto('model')">
                        {{ t('pages.po.resetToAuto') }}
                      </el-button>
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="w.showColorStandardBackingFields ? 6 : 12">
                  <el-form-item :label="t('pages.po.articleShort')">
                    <div class="field-lock-row">
                      <el-input v-model="w.formModel.style_article" class="w-full" :disabled="w.isMaterialFieldLocked('style_article')" />
                      <div class="mt-1 flex items-center gap-2">
                        <el-button
                          v-if="w.isMaterialFieldLocked('style_article')"
                          link
                          type="primary"
                          size="small"
                          @click="w.enableMaterialOverride('style_article')"
                        >
                          Override
                        </el-button>
                        <el-button
                          v-else-if="w.formModel.master_item_id && w.materialFieldOverride.style_article"
                          link
                          type="primary"
                          size="small"
                          @click="w.resetMaterialFieldToMaster('style_article')"
                        >
                          Reset
                        </el-button>
                      </div>
                    </div>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-col>
          </el-row>
          <el-row :gutter="16" class="material-step-grid">
            <el-col :xs="24" :md="6">
              <el-form-item :label="t('common.quantityOrder')" :error="w.formErrors.quantity_order">
                <el-input v-model="w.formModel.quantity_order" type="number" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="6">
              <el-form-item :label="t('pages.po.thiOrder')">
                <el-input :model-value="w.nextPoNumberDisplay" disabled />
                <p class="mt-1 text-xs text-slate-500">{{ t('pages.po.thiOrderSoHint') }}</p>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="6">
              <el-form-item :label="t('common.lotNo')">
                <div class="field-stack-row">
                  <el-input
                    v-model="w.formModel.thi_line_ref"
                    class="w-full"
                    clearable
                    @input="w.lotAutoFromMaterial = false"
                  />
                  <el-button
                    size="small"
                    type="primary"
                    class="self-start"
                    :loading="w.lotGenerateLoading"
                    @click="w.generateLotNumber"
                  >
                    Generate
                  </el-button>
                </div>
                <div v-if="w.lotAutoFromMaterial && w.formModel.thi_line_ref" class="mt-1">
                  <el-tag size="small" type="success">{{ t('pages.po.autoFilled') }}</el-tag>
                </div>
                <p class="mt-1 text-xs text-slate-500">{{ t('pages.po.lotPreviewHint') }}</p>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="6">
              <el-form-item :label="t('pages.po.unitPriceUsd')">
                <div class="field-stack-row">
                  <el-input v-model.number="w.formModel.unit_price_input" class="w-full" type="number" :step="0.01" :controls="false" />
                  <el-checkbox v-model="w.formModel.is_special_price" @change="w.onSpecialPriceChange">
                    {{ t('pages.po.specialPrice') }}
                  </el-checkbox>
                </div>
                <div v-if="w.formModel.is_special_price" class="mt-2 flex items-center gap-2">
                  <el-input-number
                    v-model="w.formModel.discount_value"
                    :min="w.formModel.discount_type === 'percent' ? -100 : -999999"
                    :max="w.formModel.discount_type === 'percent' ? 100 : 999999"
                    :controls="false"
                    class="flex-1"
                    @change="w.calculateSpecialPrice"
                  />
                  <el-radio-group v-model="w.formModel.discount_type" size="default" @change="w.calculateSpecialPrice">
                    <el-radio-button value="percent">{{ t('pages.po.percent') }}</el-radio-button>
                    <el-radio-button value="nominal">USD</el-radio-button>
                  </el-radio-group>
                </div>
                <div class="mt-1 flex items-center gap-2 flex-wrap">
                  <span v-if="w.previewResolvedUnitPrice != null" class="text-xs text-slate-500">
                    {{ t('pages.po.autoResolved') }}: {{ w.previewResolvedUnitPrice }}
                  </span>
                  <el-tag v-if="w.formModel.unit_price_input && w.previewResolvedUnitPrice != null && w.formModel.unit_price_input !== w.previewResolvedUnitPrice" size="small" type="warning">{{ t('pages.po.overridden') }}</el-tag>
                  <el-tag v-if="w.formModel.is_special_price && w.formModel.unit_price_input" size="small" type="success">
                    Final: ${{ w.formModel.unit_price_input?.toFixed(2) }}
                  </el-tag>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16" class="material-step-grid">
            <el-col :span="24">
              <el-form-item :label="t('pages.po.detailRemark')">
                <el-input
                  v-model="w.formModel.detail_remark"
                  type="textarea"
                  :rows="2"
                  :placeholder="t('pages.po.detailRemarkHint')"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <div class="mt-4">
            <div class="text-sm font-semibold text-slate-700">{{ t('pages.po.etdSchedule') }}</div>
            <p class="mb-2 mt-1 text-xs text-slate-500">{{ t('pages.po.etdScheduleHint') }}</p>
            <el-table :data="w.etdScheduleRows" border size="small" class="etd-schedule-table">
                <el-table-column :label="t('common.noLabel')" width="56" align="center">
                  <template #default="{ $index }">{{ $index + 1 }}</template>
                </el-table-column>
                <el-table-column :label="t('pages.po.etdQty')" width="130">
                  <template #default="{ $index }">
                    <el-input-number
                      v-model="w.etdScheduleRows[$index].qty"
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
                      v-model="w.etdScheduleRows[$index].date"
                      type="date"
                      size="small"
                      class="w-full"
                      value-format="YYYY-MM-DD"
                    />
                  </template>
                </el-table-column>
                <el-table-column :label="t('common.actions')" width="72" align="center">
                  <template #default="{ $index }">
                    <el-button
                      v-if="w.etdScheduleRows.length > 1"
                      link
                      type="danger"
                      :icon="Delete"
                      @click="w.removeEtdScheduleRow($index)"
                    />
                  </template>
                </el-table-column>
              </el-table>
              <div class="mt-2 flex flex-wrap items-center gap-2">
                <el-button size="small" :icon="Plus" :disabled="!w.etdScheduleCanAdd" @click="w.addEtdScheduleRow">
                  {{ t('pages.po.addScheduleWave') }}
                </el-button>
                <el-button size="small" @click="w.clearEtdScheduleRows">{{ t('common.clear') }}</el-button>
                <el-button size="small" type="primary" plain @click="w.autoFillEtdScheduleWave1">
                  {{ t('pages.po.autoFillScheduleWave1') }}
                </el-button>
                <el-button size="small" type="primary" plain @click="w.autoFillEtdScheduleEvenly">
                  {{ t('pages.po.autoFillScheduleEvenly') }}
                </el-button>
                <span class="text-xs text-slate-600">
                  {{ t('pages.po.scheduleTotal') }}: {{ w.etdScheduleTotalDisplay }}
                  <template v-if="w.formModel.quantity_order">
                    / {{ w.formModel.quantity_order }} SF
                  </template>
                </span>
              </div>
              <el-alert
                v-if="w.etdScheduleMismatch"
                type="warning"
                :closable="false"
                show-icon
                class="mt-2"
                :title="t('pages.po.scheduleMismatch')"
              />
          </div>
          <div class="mt-1 text-sm font-semibold text-slate-700">Daftar Material</div>
          <div class="mt-1 flex gap-2 flex-wrap">
            <el-button :icon="Plus" @click="w.pushCurrentLine(false)">{{ t('common.add') }}</el-button>
            <el-button :icon="TopRight" @click="w.pushCurrentLine(true)">{{ t('pages.po.addAndContinue') }}</el-button>
            <el-button :icon="DocumentCopy" @click="w.openCopyItemDialog">{{ t('pages.po.copyItemFromOtherPo') }}</el-button>
            <el-switch
              v-model="w.draftRiskOnly"
              inline-prompt
              active-text="Override saja"
              inactive-text="Semua line"
            />
            <el-tag size="small" type="info" effect="plain">
              Ditampilkan: {{ w.draftLinesDisplay.length }} / {{ w.draftLines.length }}
            </el-tag>
          </div>
          <el-table v-if="w.draftLinesDisplay.length" :data="w.draftLinesDisplay" border stripe size="small" class="mt-4" table-layout="auto" :row-class-name="w.draftRowClassName">
            <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
            <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="thickness_text" :label="t('common.thickness')" width="90" />
            <el-table-column prop="color" :label="t('common.color')" width="80" />
            <el-table-column prop="color_family" :label="t('pages.po.colorFamily')" width="100">
              <template #default="{ row }">{{ w.colorFamilyLabel(row.color_family) }}</template>
            </el-table-column>
            <el-table-column label="Kualitas Data" width="190" align="center">
              <template #default="{ row }">
                <div class="flex flex-col items-center gap-1">
                  <el-tooltip :content="w.materialQualityTooltip(row)" placement="top">
                    <el-tag
                      :type="w.materialQualityType(row)"
                      size="small"
                      effect="plain"
                    >
                      {{ w.materialQualityLabel(row) }}
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
            <el-table-column :label="t('pages.po.lineEtd')" min-width="130" show-overflow-tooltip>
              <template #default="{ row }">
                {{ w.formatLineEtdScheduleDisplay(row.delivery_schedules) }}
              </template>
            </el-table-column>
            <el-table-column prop="detail_remark" :label="t('pages.po.detailRemark')" min-width="140" show-overflow-tooltip />
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
            <el-table-column v-if="w.hasSpecialPriceInLines" label="Adj" width="80" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.is_special_price" size="small" type="warning">
                  {{ row.discount_value >= 0 ? '+' : '' }}{{ row.discount_value }}{{ row.discount_type === 'percent' ? '%' : '$' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('pages.po.thiOrder')" min-width="150" show-overflow-tooltip>
              <template #default>{{ w.nextPoNumberDisplay || '—' }}</template>
            </el-table-column>
            <el-table-column prop="thi_line_ref" :label="t('common.lotNo')" min-width="160">
              <template #default="{ row }">
                <div class="flex items-center gap-2">
                  <span class="truncate">{{ row.thi_line_ref || '—' }}</span>
                  <el-button
                    v-if="w.isEditMode && row.id"
                    size="small"
                    type="primary"
                    plain
                    @click="w.generateLotNumber(row.id)"
                  >
                    Gen
                  </el-button>
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="120" align="center">
              <template #default="{ row }">
                <el-button
                  v-if="w.isEditMode && w.draftLines.length > 1"
                  link
                  type="primary"
                  size="small"
                  @click="w.editDraftLine(row)"
                >
                  {{ t('pages.po.w.editDraftLine') }}
                </el-button>
                <el-button link type="danger" :icon="Delete" @click="w.removeDraftLine(w.draftLines.indexOf(row))" />
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!w.draftLinesDisplay.length" :description="t('pages.po.noItemsYet')" class="mt-2" />
        </div>

        <div v-show="w.currentStep === 2" class="step-content">
          <h3 class="text-lg font-semibold mb-4">{{ t('pages.po.reviewTitle') }}</h3>
          <el-descriptions :column="2" border class="mb-6">
            <el-descriptions-item :label="t('common.customer')">
              {{ w.customers.find(c => c.id === w.formModel.customer_id)?.name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('pages.po.brand')">
              {{ w.brands.find(b => b.id === w.formModel.brand_id)?.name || '-' }}
            </el-descriptions-item>
            <el-descriptions-item :label="t('common.buyer')">{{ w.formModel.buyer || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.poCategory')">{{ w.formModel.po_category }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.poNo')">{{ w.formModel.po_number || w.nextPoNumberDisplay }}</el-descriptions-item>
            <el-descriptions-item label="NO PO CUSTOMER">{{ w.formModel.po_customer_ref || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.orderDate')">{{ w.formModel.order_date || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="t('pages.po.headerEtd')">{{ w.formModel.etd || '-' }}</el-descriptions-item>
            <el-descriptions-item :label="t('common.status')">
              <el-tag size="small">{{ w.formModel.status }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>

          <h4 class="text-md font-semibold mb-2">{{ t('pages.po.itemsSummary', { count: w.draftLinesDisplay.length }) }}</h4>
          <el-table v-if="w.draftLinesDisplay.length" :data="w.draftLinesDisplay" border stripe size="small" table-layout="auto">
            <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
            <el-table-column prop="material_name" :label="t('common.material')" min-width="140" />
            <el-table-column prop="thickness_text" :label="t('common.thickness')" width="90" />
            <el-table-column prop="color" :label="t('common.color')" width="80" />
            <el-table-column :label="'Kualitas'" width="150" align="center">
              <template #default="{ row }">
                <el-tooltip :content="w.materialQualityTooltip(row)" placement="top">
                  <el-tag :type="w.materialQualityType(row)" size="small" effect="plain">
                    {{ w.materialQualityLabel(row) }}
                  </el-tag>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="100" align="right" />
            <el-table-column :label="t('pages.po.lineEtd')" min-width="130" show-overflow-tooltip>
              <template #default="{ row }">
                {{ w.formatLineEtdScheduleDisplay(row.delivery_schedules) }}
              </template>
            </el-table-column>
            <el-table-column prop="detail_remark" :label="t('pages.po.detailRemark')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="unit_price" :label="t('pages.po.unitPriceUsd')" width="100" align="right">
              <template #default="{ row }">{{ row.unit_price != null ? `$${row.unit_price}` : '—' }}</template>
            </el-table-column>
            <el-table-column :label="'Total'" width="120" align="right">
              <template #default="{ row }">
                {{ row.unit_price != null && row.quantity_order ? `$${(row.unit_price * row.quantity_order).toFixed(2)}` : '—' }}
              </template>
            </el-table-column>
            <el-table-column :label="t('pages.po.materialGroupLabel')" width="100" align="center">
              <template #default="{ row }">
                <el-tag size="small" type="info" effect="plain">{{ w.materialGroupLabel(row) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="thi_line_ref" :label="t('common.lotNo')" min-width="130" show-overflow-tooltip />
          </el-table>
          <el-empty v-else :description="t('pages.po.noItemsYet')" />
        </div>
      </el-form>
    </div>

    <template #footer>
      <div class="po-dialog-footer">
        <el-button type="danger" @click="w.requestCloseFormDialog">
          <el-icon><Close /></el-icon>
          {{ t('common.cancel') }}
        </el-button>
        <el-button v-if="!w.isEditMode" type="warning" @click="w.saveDraftAndClose">
          Simpan Draft
        </el-button>

        <div class="footer-nav">
          <el-button :disabled="w.currentStep === 0" @click="w.prevStep">&lt;</el-button>
          <span class="step-label">
            {{ w.currentStep === 0 ? t('pages.po.step1Title') : w.currentStep === 1 ? t('pages.po.step2Title') : t('pages.po.step3Title') }}
          </span>
          <el-button :disabled="w.currentStep === 2" type="primary" @click="w.nextStep">&gt;</el-button>
        </div>

        <el-button :disabled="w.currentStep !== 2 || !w.canManage" type="success" :loading="w.saving" @click="w.submitForm">
          <el-icon><Check /></el-icon>
          {{ t('common.savePo') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import {
  Check,
  Close,
  Delete,
  DocumentAdd,
  DocumentCopy,
  Edit,
  Picture,
  Plus,
  TopRight,
  UploadFilled,
} from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'

import { usePoWizardContext } from '../../composables/poFormWizardContext.js'

const w = usePoWizardContext()
const { t } = useI18n()
</script>

<style scoped>
:deep(.draft-line-active > td) {
  background-color: rgb(239 246 255) !important;
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
