<template>
  <el-drawer
    v-model="w.formDialogVisible"
    direction="rtl"
    size="100%"
    destroy-on-close
    class="so-page-drawer po-wizard-dialog"
    :before-close="w.handlePoDialogBeforeClose"
    :show-close="true"
  >
    <template #header>
      <div class="po-wizard-header">
        <div class="po-wizard-header__main">
          <div class="po-wizard-header__title-row">
            <el-icon class="po-wizard-header__icon"><DocumentAdd /></el-icon>
            <div class="po-wizard-header__titles">
              <h2 class="po-wizard-header__title">
                {{ w.isEditMode ? t('pages.poEntry.title') + ' ' + t('pages.po.editSuffix') : t('pages.poEntry.title') }}
              </h2>
              <p class="po-wizard-header__sub">{{ t('pages.poEntry.subtitle') }}</p>
            </div>
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
              class="shrink-0"
              @click="w.openMarketingReviseDialog"
            >
              {{ t('pages.po.marketingReviseOpen') }}
            </el-button>
          </div>
        </div>
        <el-steps class="po-wizard-steps" :active="w.currentStep" align-center finish-status="success" simple>
          <el-step :title="t('pages.po.step1Title')" :icon="Edit" />
          <el-step :title="t('pages.po.step2Title')" :icon="UploadFilled" />
          <el-step :title="t('pages.po.step3Title')" :icon="Picture" />
        </el-steps>
        <p class="po-wizard-step-hint">
          {{ t('pages.po.wizardStepHint', {
            current: w.currentStep + 1,
            total: 3,
            label: w.currentStep === 0 ? t('pages.po.step1Title') : w.currentStep === 1 ? t('pages.po.step2Title') : t('pages.po.step3Title'),
          }) }}
        </p>
      </div>
    </template>

    <div class="po-wizard-body" v-loading="w.formHydrating">
      <el-form label-position="top" class="po-dialog-form" @keydown.enter.prevent="w.handleEnterKey">
        <div v-show="w.currentStep === 0" class="po-wizard-step">
          <div class="po-wizard-panel">
            <div class="po-wizard-panel__head">
              <h3 class="po-wizard-panel__title">{{ t('pages.po.customerSoSection') }}</h3>
              <p class="po-wizard-panel__sub">{{ t('pages.po.wizardStep1Hint') }}</p>
            </div>
            <div class="po-wizard-panel__body po-wizard-panel__body--stack">
              <section class="po-wizard-group">
                <header class="po-wizard-group__head">
                  <h4 class="po-wizard-group__title">{{ t('pages.po.wizardGroupCustomerIdentity') }}</h4>
                </header>
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
                </el-row>
              </section>

              <section class="po-wizard-group">
                <header class="po-wizard-group__head">
                  <h4 class="po-wizard-group__title">{{ t('pages.po.wizardGroupPoClassification') }}</h4>
                </header>
                <el-row :gutter="16" class="material-step-grid">
            <el-col :xs="24" :md="12">
              <el-form-item :label="t('common.poCategory')">
                <el-radio-group v-model="w.formModel.po_category" size="small" class="po-category-radio" :disabled="w.isPoCategoryDisabled">
                  <el-radio-button value="production">{{ t('status.production') }}</el-radio-button>
                  <el-radio-button value="sample">{{ t('status.sample') }}</el-radio-button>
                  <el-radio-button value="subcont">{{ t('status.subcont') }}</el-radio-button>
                  <el-radio-button value="return">{{ t('status.return') }}</el-radio-button>
                  <el-radio-button value="claim">{{ t('status.claim') }}</el-radio-button>
                </el-radio-group>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="12">
              <el-form-item>
                <template #label>
                  <span class="form-label-with-hint">
                    {{ t('common.factoryCode') }}
                    <el-tooltip placement="top" :show-after="200">
                      <template #content>{{ t('pages.po.factoryCodeHint') }}</template>
                      <el-icon class="form-label-hint" :size="14" tabindex="0" :aria-label="t('pages.po.factoryCodeHint')">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </span>
                </template>
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
              </el-form-item>
            </el-col>
                </el-row>
              </section>

              <section class="po-wizard-group">
                <header class="po-wizard-group__head">
                  <h4 class="po-wizard-group__title">{{ t('pages.po.wizardGroupOrderReference') }}</h4>
                </header>
                <el-row :gutter="16" class="material-step-grid">
            <el-col :xs="24" :md="12">
              <el-form-item>
                <template #label>
                  <span class="form-label-with-hint">
                    {{ t('common.poNo') }}
                    <el-tooltip placement="top" :show-after="200">
                      <template #content>{{ t('pages.po.autoGenerateHint') }}</template>
                      <el-icon class="form-label-hint" :size="14" tabindex="0" :aria-label="t('pages.po.autoGenerateHint')">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </span>
                </template>
                <el-input :model-value="w.isEditMode ? w.formModel.po_number : w.nextPoNumberDisplay" disabled />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="12">
              <el-form-item
                :error="w.formErrors.po_customer_ref || undefined"
              >
                <template #label>
                  <span class="form-label-with-hint">
                    {{ t('pages.po.poCustomerRef') }}
                    <el-tooltip placement="top" :show-after="200">
                      <template #content>{{ t('pages.po.poCustomerRefHint') }}</template>
                      <el-icon class="form-label-hint" :size="14" tabindex="0" :aria-label="t('pages.po.poCustomerRefHint')">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </span>
                </template>
                <el-input v-model="w.formModel.po_customer_ref" clearable maxlength="255" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="12">
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
                </el-row>
              </section>

              <section class="po-wizard-group">
                <header class="po-wizard-group__head">
                  <h4 class="po-wizard-group__title">{{ t('pages.po.wizardGroupAddresses') }}</h4>
                </header>
                <el-row :gutter="16" class="material-step-grid">
            <el-col :xs="24" :md="12">
              <el-form-item :label="t('pages.po.billingAddress')">
                <el-input v-model="w.formModel.billing_address" type="textarea" :rows="2" />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="12">
              <el-form-item :label="t('pages.po.deliveryAddress')">
                <el-input v-model="w.formModel.delivery_address" type="textarea" :rows="2" />
              </el-form-item>
            </el-col>
                </el-row>
              </section>
            </div>
          </div>
        </div>

        <div v-show="w.currentStep === 1" class="po-wizard-step po-material-split">
          <div class="po-material-split__form">
          <div class="po-wizard-panel">
            <div class="po-wizard-panel__head">
              <h3 class="po-wizard-panel__title">{{ t('pages.po.step2Title') }}</h3>
              <p class="po-wizard-panel__sub">{{ t('pages.po.wizardStep2Hint') }}</p>
            </div>
            <el-alert
              v-if="w.currentLineLocked"
              type="warning"
              show-icon
              :closable="false"
              class="mb-3"
              :title="t('pages.po.lineLockedHint')"
            />
            <div class="po-wizard-panel__body po-wizard-panel__body--stack">
          <section v-if="w.isSubkonPo" class="po-wizard-group">
            <header class="po-wizard-group__head">
              <h4 class="po-wizard-group__title">{{ t('pages.po.wizardGroupSubkon') }}</h4>
            </header>
          <el-row :gutter="16" class="mb-2">
            <el-col :span="24">
              <el-form-item :label="t('pages.po.subkonItemCode')">
                <el-select
                  v-model="w.subkonItemCodePicker"
                  filterable
                  clearable
                  class="w-full"
                  :placeholder="t('pages.po.subkonItemCodePlaceholder')"
                  @change="w.onPickedSubkonItemCode"
                >
                  <el-option
                    v-for="item in w.subkonMasterItems"
                    :key="item.id"
                    :label="`${item.item_code} — ${item.material_name || ''}${item.color ? ` · ${item.color}` : ''}`"
                    :value="item.item_code"
                  />
                </el-select>
                <p class="mt-1 text-xs text-slate-500">{{ t('pages.po.subkonMasterHint') }}</p>
              </el-form-item>
            </el-col>
          </el-row>
          </section>

          <section v-if="!w.isSubkonPo" class="po-wizard-group po-wizard-group--compact">
            <header class="po-wizard-group__head">
              <h4 class="po-wizard-group__title">{{ t('pages.po.itemCategory') }}</h4>
              <p class="po-wizard-group__sub">{{ t('pages.po.itemCategoryHint') }}</p>
            </header>
            <el-form-item>
              <el-radio-group
                v-model="w.formModel.item_category"
                size="small"
                class="po-category-radio"
                @change="w.onItemCategoryChange"
              >
                <el-radio-button value="PU">PU</el-radio-button>
                <el-radio-button value="Suede">{{ t('status.suede') }}</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </section>

          <section class="po-wizard-group">
            <header class="po-wizard-group__head po-wizard-group__head--row">
              <h4 class="po-wizard-group__title">{{ t('pages.po.wizardGroupMaterialSpec') }}</h4>
              <el-tooltip placement="top-start" :show-after="200">
                <template #content>
                  <div class="material-fill-order-tip">
                    <p class="material-fill-order-tip__title">
                      {{
                        w.materialStepFillStep > 0
                          ? t('pages.po.materialStepFillOrderTitle', { step: w.materialStepFillStep })
                          : t('pages.po.materialStepFillOrderDone')
                      }}
                    </p>
                    <p class="material-fill-order-tip__body">{{ t('pages.po.materialStepFillOrder1') }}</p>
                    <p v-if="w.materialStepFillStep === 2" class="material-fill-order-tip__next">
                      {{ t('pages.po.materialStepFillOrder2') }}
                    </p>
                    <p v-else-if="w.materialStepFillStep === 3" class="material-fill-order-tip__next">
                      {{ t('pages.po.materialStepFillOrder3') }}
                    </p>
                    <p v-else-if="w.materialStepFillStep === 4" class="material-fill-order-tip__next">
                      {{ t('pages.po.materialStepFillOrder4') }}
                    </p>
                    <p v-else-if="w.materialStepFillStep === 5" class="material-fill-order-tip__next">
                      {{ t('pages.po.materialStepFillOrder5') }}
                    </p>
                  </div>
                </template>
                <el-icon
                  class="po-wizard-group__info"
                  :size="16"
                  tabindex="0"
                  :aria-label="t('pages.po.materialStepFillOrderAria')"
                >
                  <InfoFilled />
                </el-icon>
              </el-tooltip>
            </header>
          <el-row :gutter="16" class="material-step-grid">
            <el-col :xs="24" :md="8">
              <el-form-item :label="t('common.material')" :error="w.formErrors.material_name">
                <div class="field-lock-row">
                  <el-select
                    v-model="w.formModel.material_name"
                    filterable
                    :allow-create="!w.isSubkonPo"
                    default-first-option
                    clearable
                    class="w-full"
                    :placeholder="w.isSubkonPo ? t('pages.po.subkonMaterialPlaceholder') : t('pages.po.materialCascadePlaceholder')"
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
                      {{ t('pages.po.fieldOverride') }}
                    </el-button>
                    <el-button
                      v-else-if="w.formModel.master_item_id && w.materialFieldOverride.material_name"
                      link
                      type="primary"
                      size="small"
                      @click="w.resetMaterialFieldToMaster('material_name')"
                    >
                      {{ t('pages.po.fieldReset') }}
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
                    :placeholder="w.isSubkonPo ? t('pages.po.subkonThicknessPlaceholder') : t('pages.po.thicknessCascadePlaceholder')"
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
                      {{ t('pages.po.fieldOverride') }}
                    </el-button>
                    <el-button
                      v-else-if="w.formModel.master_item_id && w.materialFieldOverride.thickness_text"
                      link
                      type="primary"
                      size="small"
                      @click="w.resetMaterialFieldToMaster('thickness_text')"
                    >
                      {{ t('pages.po.fieldReset') }}
                    </el-button>
                  </div>
                </div>
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
                    @change="w.onPickedColorDimension"
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
                    :allow-create="!w.isSubkonPo"
                    default-first-option
                    clearable
                    class="w-full"
                    :placeholder="t('common.placeholder.color')"
                    :disabled="w.isMaterialFieldLocked('color') || !String(w.formModel.material_name || '').trim() || (!w.isSubkonPo && !String(w.formModel.thickness_text || '').trim())"
                    @change="w.onPickedColorDimension"
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
                      {{ t('pages.po.colorFieldOverride') }}
                    </el-button>
                    <el-button
                      v-else-if="w.formModel.master_item_id && w.materialFieldOverride.color"
                      link
                      type="primary"
                      size="small"
                      @click="w.resetMaterialFieldToMaster('color')"
                    >
                      {{ t('pages.po.colorFieldReset') }}
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
                  <el-select
                    v-model="w.formModel.emboss"
                    filterable
                    :allow-create="!w.isSubkonPo"
                    default-first-option
                    clearable
                    class="w-full"
                    :placeholder="t('pages.po.embossCascadePlaceholder')"
                    :disabled="w.isMaterialFieldLocked('emboss') || !String(w.formModel.color || '').trim()"
                    @change="w.onPickedEmbossDimension"
                  >
                    <el-option v-for="e in w.embossDimensionOptions" :key="e" :label="e" :value="e" />
                  </el-select>
                  <el-button
                    v-if="w.isMaterialFieldLocked('emboss')"
                    link
                    type="primary"
                    size="small"
                    @click="w.enableMaterialOverride('emboss')"
                  >
                    {{ t('pages.po.fieldOverride') }}
                  </el-button>
                  <el-button
                    v-else-if="w.formModel.master_item_id && w.materialFieldOverride.emboss"
                    link
                    type="primary"
                    size="small"
                    @click="w.resetMaterialFieldToMaster('emboss')"
                  >
                    {{ t('pages.po.fieldReset') }}
                  </el-button>
                </div>
              </el-form-item>
            </el-col>
            <el-col v-if="!w.isSubkonPo" :xs="24" :md="8">
              <el-form-item :label="t('pages.po.masterItemCode')">
                <el-select
                  v-model="w.masterItemCodePicker"
                  filterable
                  clearable
                  class="w-full"
                  :placeholder="t('pages.po.itemCodeCascadePlaceholder')"
                  :disabled="!String(w.formModel.emboss || '').trim()"
                  @change="w.onPickedMasterItemCode"
                >
                  <el-option
                    v-for="code in w.itemCodeDimensionOptions"
                    :key="code"
                    :label="code"
                    :value="code"
                  />
                </el-select>
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
                    {{ t('pages.po.fieldOverride') }}
                  </el-button>
                  <el-button
                    v-else-if="w.formModel.master_item_id && w.materialFieldOverride.color_family"
                    link
                    type="primary"
                    size="small"
                    @click="w.resetMaterialFieldToMaster('color_family')"
                  >
                    {{ t('pages.po.fieldReset') }}
                  </el-button>
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="24">
              <div v-if="w.formModel.master_item_id" class="flex flex-wrap items-center gap-2 mb-2">
                <el-tag type="success" closable @close="w.clearLinkedMasterItem">
                  {{ w.isSubkonPo ? t('pages.po.subkonMasterLinkedTag') : t('pages.po.masterLinkedTag') }}: {{ w.resolvedMasterItemLabel }}
                </el-tag>
                <span v-if="w.masterResolveLoading" class="text-xs text-slate-500">{{ t('pages.po.resolvingMaster') }}</span>
              </div>
              <el-alert
                v-else-if="!w.isSubkonPo && w.lastResolveHadNoMaster && w.materialThicknessColorComplete"
                type="warning"
                :closable="false"
                show-icon
                class="mb-2"
                :title="t('pages.po.masterNotMatchedHint')"
              />
            </el-col>
          </el-row>
          </section>

          <section v-if="!w.isSubkonPo" class="po-wizard-group">
            <header class="po-wizard-group__head">
              <h4 class="po-wizard-group__title">{{ w.wizardColorSwatchGroupTitle }}</h4>
              <p class="po-wizard-group__sub">{{ w.wizardColorSwatchGroupSub }}</p>
            </header>
            <div class="mb-3">
              <p class="mb-1 text-xs text-slate-500">{{ t('pages.po.colorStandardSourceLabel') }}</p>
              <el-radio-group
                :model-value="w.colorStandardSource"
                size="small"
                class="po-color-source-radio"
                @change="w.onColorStandardSourceChange"
              >
                <el-radio-button value="swatch">
                  {{
                    w.isSuedeMaterial
                      ? t('pages.po.colorStandardSourceColorWindow')
                      : t('pages.po.colorStandardSourceSwatch')
                  }}
                </el-radio-button>
                <el-radio-button value="csi">{{ t('pages.po.colorStandardSourceCsi') }}</el-radio-button>
                <el-radio-button value="waiting">{{ t('pages.po.colorStandardSourceWaiting') }}</el-radio-button>
                <el-radio-button value="manual">{{ t('pages.po.colorStandardSourceManual') }}</el-radio-button>
              </el-radio-group>
            </div>
            <div v-if="w.colorStandardSource === 'swatch'" class="mb-2">
                <div
                  v-if="w.selectedSwatchRecipe && !w.swatchPickerOpen"
                  class="flex flex-wrap items-center gap-2 rounded border border-emerald-200 bg-emerald-50/80 px-3 py-2"
                >
                  <el-tag type="success" size="small">{{ t('pages.po.swatchActiveTag') }}</el-tag>
                  <span class="text-sm text-slate-700">
                    {{ w.colorReferenceOptionLabel(w.selectedSwatchRecipe) }}
                    <template v-if="w.showBackingField && w.formModel.backing">
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
                    v-model="w.colorReferencePickerId"
                    filterable
                    clearable
                    class="w-full"
                    :placeholder="
                      w.isSuedeMaterial
                        ? t('pages.po.colorWindowPickerPlaceholder')
                        : t('pages.po.swatchPickerPlaceholder')
                    "
                    :loading="w.colorSwatchLoading"
                    :disabled="w.isSuedeMaterial ? !w.formModel.brand_id : !w.formModel.buyer"
                    @change="w.applyColorSwatch"
                  >
                    <el-option
                      v-for="s in w.colorSwatchOptions"
                      :key="s.id"
                      :label="w.colorReferenceOptionLabel(s)"
                      :value="s.id"
                    />
                  </el-select>
                  <div v-if="!w.isSuedeMaterial" class="mt-1 flex flex-wrap items-center gap-2">
                    <el-checkbox v-model="w.swatchAllMaterials" @change="w.loadColorSwatchOptions">
                      {{ t('pages.po.swatchAllMaterials') }}
                    </el-checkbox>
                  </div>
                </template>
                <p
                  v-if="!w.isSuedeMaterial && w.swatchRetriedWithoutMaterial"
                  class="mt-1 text-xs text-slate-500"
                >
                  {{ t('pages.po.swatchRetriedHint') }}
                </p>
                <p v-if="w.swatchHelperMessage && !w.selectedSwatchRecipe" class="mt-1 text-xs text-amber-600">
                  {{ w.swatchHelperMessage }}
                </p>
                <p
                  v-if="w.selectedSwatchRecipe"
                  class="mt-1 text-xs text-slate-500"
                >
                  {{ t('pages.po.swatchFieldsLockedHint') }}
                </p>
            </div>
            <div v-else-if="w.colorStandardSource === 'csi'" class="mb-2">
              <el-select
                v-model="w.selectedCsiId"
                filterable
                remote
                clearable
                class="w-full"
                :placeholder="t('pages.po.colorStandardCsiPlaceholder')"
                :loading="w.csiLoading"
                :disabled="!w.formModel.buyer"
                :remote-method="w.searchCsiOptions"
                @change="w.applySelectedCsiColor"
              >
                <el-option
                  v-for="c in w.csiOptions"
                  :key="c.id"
                  :label="w.csiColorOptionLabel(c)"
                  :value="c.id"
                />
              </el-select>
              <p v-if="!w.formModel.buyer" class="mt-1 text-xs text-amber-600">
                {{ t('pages.po.colorStandardCsiNeedBuyer') }}
              </p>
              <p v-else class="mt-1 text-xs text-slate-500">{{ t('pages.po.colorStandardCsiHint') }}</p>
            </div>
            <el-alert
              v-else-if="w.colorStandardSource === 'waiting'"
              type="warning"
              :closable="false"
              show-icon
              class="mb-2"
              :title="t('pages.po.colorStandardWaitingHint')"
            />
            <p v-else-if="w.colorStandardSource === 'manual'" class="mb-2 text-xs text-slate-500">
              {{ t('pages.po.colorStandardManualHint') }}
            </p>
            <el-form-item :label="t('pages.po.colorReference')">
              <el-input
                v-model="w.formModel.color_reference"
                clearable
                :placeholder="t('pages.po.colorReferencePlaceholder')"
                @input="w.onColorReferenceInput"
              />
              <div class="mt-2 flex items-center gap-2">
                <el-tag v-if="w.autoFieldMeta.color_reference && w.formModel.color_reference" size="small" type="success">
                  {{ t('pages.po.autoFilled') }}
                </el-tag>
              </div>
              <div
                v-if="w.isSuedeMaterial && w.selectedSwatchRecipe"
                class="po-cw-audit"
              >
                <span class="po-cw-audit__badge po-cw-audit__badge--created">
                  <span class="po-cw-audit__label">{{ t('pages.colorWindow.colCreatedAt') }}</span>
                  <span class="po-cw-audit__value">{{ formatColorWindowAudit(w.selectedSwatchRecipe.created_at) }}</span>
                </span>
                <span class="po-cw-audit__badge po-cw-audit__badge--updated">
                  <span class="po-cw-audit__label">{{ t('pages.colorWindow.colUpdatedAt') }}</span>
                  <span class="po-cw-audit__value">{{ formatColorWindowAudit(w.selectedSwatchRecipe.updated_at) }}</span>
                </span>
              </div>
            </el-form-item>
          </section>

          <section class="po-wizard-group">
            <header class="po-wizard-group__head po-wizard-group__head--row">
              <h4 class="po-wizard-group__title">
                {{ t('pages.po.materialExtraGroupTitle') }}
              </h4>
              <el-tooltip v-if="w.pricingKeyIncomplete" placement="top-start" :show-after="200">
                <template #content>{{ t('pages.po.pricingKeyIncomplete') }}</template>
                <el-icon
                  class="po-wizard-group__info po-wizard-group__info--warn"
                  :size="16"
                  tabindex="0"
                  :aria-label="t('pages.po.pricingKeyIncomplete')"
                >
                  <WarningFilled />
                </el-icon>
              </el-tooltip>
            </header>
            <div
              v-if="w.selectedSwatchRecipe && !w.currentLineLocked"
              class="mb-3 flex flex-wrap items-center justify-end gap-2"
            >
              <el-button
                link
                type="primary"
                size="small"
                @click="w.reapplySelectedSwatchRecipe()"
              >
                {{ t('pages.po.swatchResyncFromRecipe') }}
              </el-button>
            </div>
            <el-row :gutter="16">
                <el-col :xs="24" :md="w.showBackingField ? 6 : 8">
                  <el-form-item :label="t('pages.po.colorStandart')">
                    <el-input
                      v-model="w.formModel.color_standard"
                      :readonly="w.swatchFieldsLocked"
                      :disabled="w.swatchFieldsLocked"
                      @input="w.autoFieldMeta.color_standard = false"
                    />
                    <div class="mt-2 flex items-center gap-2">
                      <el-tag
                        v-if="w.selectedSwatchId && w.autoFieldMeta.color_standard && w.formModel.color_standard"
                        size="small"
                        type="success"
                      >
                        {{ t('pages.po.swatchFilledFromRecipe') }}
                      </el-tag>
                      <el-tag v-else-if="w.autoFieldMeta.color_standard && w.formModel.color_standard" size="small" type="success">
                        {{ t('pages.po.autoFilled') }}
                      </el-tag>
                    </div>
                  </el-form-item>
                </el-col>
                <el-col v-if="w.showBackingField" :xs="24" :md="6">
                  <el-form-item :label="t('common.backing')">
                    <el-input
                      v-model="w.formModel.backing"
                      :readonly="w.swatchFieldsLocked"
                      :disabled="w.swatchFieldsLocked"
                      @input="w.autoFieldMeta.backing = false"
                    />
                    <div class="mt-2 flex items-center gap-2">
                      <el-tag
                        v-if="w.selectedSwatchId && w.autoFieldMeta.backing && w.formModel.backing"
                        size="small"
                        type="success"
                      >
                        {{ t('pages.po.swatchFilledFromRecipe') }}
                      </el-tag>
                      <el-tag v-else-if="w.autoFieldMeta.backing && w.formModel.backing" size="small" type="success">
                        {{ t('pages.po.autoFilled') }}
                      </el-tag>
                    </div>
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="w.showBackingField ? 6 : 8">
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
                <el-col :xs="24" :md="w.showBackingField ? 6 : 8">
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
                          {{ t('pages.po.fieldOverride') }}
                        </el-button>
                        <el-button
                          v-else-if="w.formModel.master_item_id && w.materialFieldOverride.style_article"
                          link
                          type="primary"
                          size="small"
                          @click="w.resetMaterialFieldToMaster('style_article')"
                        >
                          {{ t('pages.po.fieldReset') }}
                        </el-button>
                      </div>
                    </div>
                  </el-form-item>
                </el-col>
            </el-row>
          </section>

          <section class="po-wizard-group">
            <header class="po-wizard-group__head">
              <h4 class="po-wizard-group__title">{{ t('pages.po.wizardGroupQtyPrice') }}</h4>
            </header>
          <el-row :gutter="16" class="material-step-grid">
            <el-col :xs="24" :md="6">
              <el-form-item :label="t('common.quantityOrder')" :error="w.formErrors.quantity_order">
                <el-input v-model="w.formModel.quantity_order" type="number" />
                <p v-if="w.currentLineLocked" class="el-form-item__help text-xs text-amber-700 mt-1">
                  {{ t('pages.po.lineLockedQtyHint') }}
                </p>
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="6">
              <el-form-item>
                <template #label>
                  <span class="form-label-with-hint">
                    {{ t('pages.po.thiOrder') }}
                    <el-tooltip placement="top" :show-after="200">
                      <template #content>{{ t('pages.po.thiOrderSoHint') }}</template>
                      <el-icon class="form-label-hint" :size="14" tabindex="0" :aria-label="t('pages.po.thiOrderSoHint')">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </span>
                </template>
                <el-input :model-value="w.nextPoNumberDisplay" disabled />
              </el-form-item>
            </el-col>
            <el-col :xs="24" :md="6">
              <el-form-item>
                <template #label>
                  <span class="form-label-with-hint">
                    {{ t('common.lotNo') }}
                    <el-tooltip placement="top" :show-after="200">
                      <template #content>{{ t('pages.po.lotPreviewHint') }}</template>
                      <el-icon class="form-label-hint" :size="14" tabindex="0" :aria-label="t('pages.po.lotPreviewHint')">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </span>
                </template>
                <div class="field-stack-row">
                  <el-input
                    v-model="w.formModel.thi_line_ref"
                    class="w-full"
                    clearable
                    :disabled="w.currentLineLocked"
                    @input="w.lotAutoFromMaterial = false"
                  />
                  <el-button
                    size="small"
                    type="primary"
                    class="self-start"
                    :loading="w.lotGenerateLoading"
                    :disabled="w.currentLineLocked"
                    @click="w.generateLotNumber"
                  >
                    {{ t('pages.po.generateLotShort') }}
                  </el-button>
                </div>
                <div v-if="w.lotAutoFromMaterial && w.formModel.thi_line_ref" class="mt-1">
                  <el-tag size="small" type="success">{{ t('pages.po.autoFilled') }}</el-tag>
                </div>
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
                <p v-if="w.formModel.is_special_price && w.formModel.list_unit_price != null" class="po-price-source">
                  {{ t('pages.po.listPriceBasis', { price: Number(w.formModel.list_unit_price).toFixed(4) }) }}
                </p>
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
                <p v-if="w.previewResolvedUnitPrice == null && w.previewPriceDetail" class="po-price-miss">
                  {{ w.previewPriceDetail }}
                </p>
                <div v-if="w.previewPriceBase != null" class="po-price-addon-labels">
                  <p class="po-price-addon-note">{{ t('pages.po.priceAddonNote') }}</p>
                  <span class="po-price-addon-label">COLOR WHITE {{ Number(w.previewPriceBase).toFixed(2) }}</span>
                  <span v-for="addon in w.previewPriceAddons" :key="addon.key" class="po-price-addon-label">
                    {{ addon.label }} {{ Number(addon.amount).toFixed(2) }}
                  </span>
                </div>
                <p v-if="w.previewPriceListTitle || w.previewPricePeriodStart" class="po-price-source">
                  {{ t('pages.po.priceListSource', {
                    title: w.previewPriceListTitle || '—',
                    start: w.previewPricePeriodStart || '—',
                    end: w.previewPricePeriodEnd || '—',
                  }) }}
                </p>
                <p v-if="w.previewPriceBlock" class="po-price-source">
                  {{ t('pages.po.priceBlockLabel', { block: w.previewPriceBlock }) }}
                </p>
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
          </section>

          <section class="po-wizard-group">
            <header class="po-wizard-group__head">
              <h4 class="po-wizard-group__title">{{ t('pages.po.wizardGroupLineRemark') }}</h4>
            </header>
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
          </section>

          <section class="po-wizard-group">
            <header class="po-wizard-group__head">
              <h4 class="po-wizard-group__title">{{ t('pages.po.etdSchedule') }}</h4>
              <p class="po-wizard-group__sub">{{ t('pages.po.etdScheduleHint') }}</p>
            </header>
              <el-row :gutter="16" class="material-step-grid">
                <el-col :xs="24" :md="10">
                  <el-form-item :label="t('pages.po.etdDate')">
                    <el-date-picker
                      v-model="w.etdScheduleRows[0].date"
                      type="date"
                      class="w-full"
                      value-format="YYYY-MM-DD"
                      :placeholder="t('common.placeholder.etd')"
                      @change="w.syncEtdQtyFromOrder"
                    />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :md="14" class="po-wizard-inline-actions">
                  <el-button
                    size="small"
                    type="primary"
                    plain
                    :disabled="!w.formModel.etd"
                    @click="w.copyEtdDateFromHeader"
                  >
                    {{ t('pages.po.etdCopyFromHeader') }}
                  </el-button>
                  <el-button size="small" @click="w.clearEtdScheduleRows">
                    {{ t('common.clear') }}
                  </el-button>
                </el-col>
              </el-row>
              <el-alert
                v-if="w.etdScheduleMismatch"
                type="warning"
                :closable="false"
                show-icon
                class="mt-2"
                :title="t('pages.po.scheduleMismatch')"
              />
          </section>

          <div class="po-material-add-bar">
            <p
              v-if="w.isColorStandardRequired && !w.hasColorStandardReady"
              class="mb-2 w-full text-xs text-amber-600"
            >
              {{ t('pages.po.colorStandardRequired') }}
            </p>
            <template v-if="w.editingDraftLineIndex >= 0">
              <el-button size="small" @click="w.cancelEditDraftLine">
                {{ t('common.cancel') }}
              </el-button>
              <el-button
                type="primary"
                :icon="Check"
                class="po-wizard-add-line-btn"
                :disabled="w.isColorStandardRequired && !w.hasColorStandardReady"
                @click="w.pushCurrentLine(false)"
              >
                {{ t('pages.po.saveDraftLine') }}
              </el-button>
              <el-button
                ref="addLineBtnRef"
                type="success"
                plain
                :icon="Plus"
                class="po-wizard-add-line-btn"
                :disabled="w.isColorStandardRequired && !w.hasColorStandardReady"
                @click="w.pushCurrentLineAsNew(false)"
              >
                {{ t('pages.po.addDraftLineNew') }}
              </el-button>
            </template>
            <el-button
              v-else
              ref="addLineBtnRef"
              type="primary"
              :icon="Plus"
              class="po-wizard-add-line-btn"
              :disabled="w.isColorStandardRequired && !w.hasColorStandardReady"
              @click="w.pushCurrentLine(false)"
            >
              {{ t('common.add') }}
            </el-button>
          </div>
            </div>
          </div>
          </div>

          <div class="po-material-split__list">
          <div class="po-wizard-panel po-wizard-panel--sub po-material-list-panel">
            <div class="po-wizard-panel__head">
              <h4 class="po-wizard-panel__title">{{ t('pages.po.materialListTitle') }}</h4>
            </div>
            <div class="admin-action-bar">
              <p class="admin-action-bar__hint">
                {{ t('pages.po.draftLinesShown', { shown: w.draftLinesDisplay.length, total: w.draftLines.length }) }}
              </p>
              <div class="admin-action-bar__buttons">
                <el-button size="small" :icon="DocumentCopy" @click="w.openCopyItemDialog">{{ t('pages.po.copyItemFromOtherPo') }}</el-button>
                <el-switch
                  v-model="w.draftRiskOnly"
                  inline-prompt
                  :active-text="t('pages.po.draftRiskOnlyActive')"
                  :inactive-text="t('pages.po.draftRiskAllLines')"
                />
              </div>
            </div>
            <div class="po-wizard-panel__body">
            <p class="admin-scroll-hint mb-3">{{ t('pages.po.scrollHint') }}</p>
            <div class="admin-table-scroll">
          <el-table v-if="w.draftLinesDisplay.length" :data="w.draftLinesDisplay" border stripe size="small" class="po-draft-table mt-2" table-layout="auto" :row-class-name="w.draftRowClassName">
            <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
            <el-table-column prop="material_name" :label="t('common.material')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="thickness_text" :label="t('common.thickness')" width="90" />
            <el-table-column prop="color" :label="t('common.color')" width="80" />
            <el-table-column prop="color_family" :label="t('pages.po.colorFamily')" width="100">
              <template #default="{ row }">{{ w.colorFamilyLabel(row.color_family) }}</template>
            </el-table-column>
            <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="90" />
            <el-table-column :label="t('pages.po.lineEtd')" min-width="130" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.line_etd || '—' }}
              </template>
            </el-table-column>
            <el-table-column prop="detail_remark" :label="t('pages.po.detailRemark')" min-width="140" show-overflow-tooltip />
            <el-table-column :label="t('pages.po.unitPriceUsd')" width="168" align="right">
              <template #default="{ row }">
                <div class="flex flex-col items-end gap-1">
                  <span v-if="row.is_special_price" class="text-xs text-slate-400 line-through">
                    {{ row.base_price?.toFixed(2) || '—' }}
                  </span>
                  <span :class="row.is_special_price ? 'text-green-600 font-semibold' : ''">
                    {{ row.unit_price != null ? '$' + row.unit_price.toFixed(2) : '—' }}
                  </span>
                  <div v-if="row.price_base != null" class="po-price-addon-labels po-price-addon-labels--end">
                    <span class="po-price-addon-label">COLOR WHITE {{ Number(row.price_base).toFixed(2) }}</span>
                    <span v-for="addon in row.price_addons || []" :key="addon.key" class="po-price-addon-label">
                      {{ addon.label }} {{ Number(addon.amount).toFixed(2) }}
                    </span>
                  </div>
                  <el-tooltip v-if="row.manual_override" :content="t('pages.po.linePriceOverrideHint')" placement="top">
                    <el-tag size="small" type="danger" effect="plain">
                      {{ t('pages.po.linePriceOverride') }}
                    </el-tag>
                  </el-tooltip>
                </div>
              </template>
            </el-table-column>
            <el-table-column v-if="w.hasSpecialPriceInLines" :label="t('pages.po.priceAdjustShort')" width="80" align="center">
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
                  <el-tag v-if="row.line_locked" size="small" type="warning">{{ t('pages.po.lineLockedTag') }}</el-tag>
                  <el-button
                    v-if="w.isEditMode && row.id && !row.line_locked"
                    size="small"
                    type="primary"
                    plain
                    @click="w.generateLotNumber(row.id)"
                  >
                    {{ t('pages.po.generateLotShort') }}
                  </el-button>
                </div>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <AdminTableActions
                  :show-edit="true"
                  :show-delete="!row.line_locked"
                  :edit-label="t('pages.po.editDraftLine')"
                  :delete-label="row.line_locked ? (row.line_lock_reason || t('pages.po.lineLockedHint')) : t('common.delete')"
                  :more-items="[{ command: 'copy', label: t('pages.po.copyLine'), icon: DocumentCopy }]"
                  @edit="w.editDraftLine(row)"
                  @delete="w.removeDraftLine(w.draftLines.indexOf(row))"
                  @more="(cmd) => cmd === 'copy' && w.copyDraftLine(row)"
                />
              </template>
            </el-table-column>
          </el-table>
          </div>
          <el-empty v-if="!w.draftLinesDisplay.length" :description="t('pages.po.noItemsYet')" class="mt-2" />
            </div>
          </div>
          </div>
        </div>

        <div v-show="w.currentStep === 2" class="po-wizard-step">
          <div class="po-wizard-panel">
            <div class="po-wizard-panel__head">
              <h3 class="po-wizard-panel__title">{{ t('pages.po.reviewTitle') }}</h3>
              <p class="po-wizard-panel__sub">{{ t('pages.po.wizardStep3Hint') }}</p>
            </div>
            <div class="po-wizard-panel__body po-wizard-panel__body--stack">
              <section class="po-wizard-group">
                <header class="po-wizard-group__head">
                  <h4 class="po-wizard-group__title">{{ t('pages.po.wizardGroupReviewCommercial') }}</h4>
                </header>
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item :label="t('common.customer')">
                    {{ w.customers.find(c => c.id === w.formModel.customer_id)?.name || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('pages.po.brand')">
                    {{ w.brands.find(b => b.id === w.formModel.brand_id)?.name || '-' }}
                  </el-descriptions-item>
                  <el-descriptions-item :label="t('common.buyer')">{{ w.formModel.buyer || '-' }}</el-descriptions-item>
                  <el-descriptions-item :label="t('common.poCategory')">{{ w.formModel.po_category }}</el-descriptions-item>
                  <el-descriptions-item :label="t('common.status')">
                    <el-tag size="small">{{ w.formModel.status }}</el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </section>

              <section class="po-wizard-group">
                <header class="po-wizard-group__head">
                  <h4 class="po-wizard-group__title">{{ t('pages.po.wizardGroupOrderReference') }}</h4>
                </header>
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item :label="t('common.poNo')">{{ w.formModel.po_number || w.nextPoNumberDisplay }}</el-descriptions-item>
                  <el-descriptions-item :label="t('pages.po.poCustomerRef')">{{ w.formModel.po_customer_ref || '-' }}</el-descriptions-item>
                  <el-descriptions-item :label="t('common.orderDate')">{{ w.formModel.order_date || '-' }}</el-descriptions-item>
                  <el-descriptions-item :label="t('pages.po.headerEtd')">{{ w.formModel.etd || '-' }}</el-descriptions-item>
                </el-descriptions>
              </section>

              <section class="po-wizard-group">
                <header class="po-wizard-group__head">
                  <h4 class="po-wizard-group__title">{{ t('pages.po.wizardGroupReviewLines') }}</h4>
                  <p class="po-wizard-group__sub">{{ t('pages.po.itemsSummary', { count: w.draftLinesDisplay.length }) }}</p>
                </header>
                <p class="admin-scroll-hint mb-3">{{ t('pages.po.scrollHint') }}</p>
                <div class="admin-table-scroll">
          <el-table v-if="w.draftLinesDisplay.length" :data="w.draftLinesDisplay" border stripe size="small" class="po-draft-table" table-layout="auto">
            <el-table-column type="index" :label="t('common.noLabel')" width="56" align="center" />
            <el-table-column prop="material_name" :label="t('common.material')" min-width="140" />
            <el-table-column prop="thickness_text" :label="t('common.thickness')" width="90" />
            <el-table-column prop="color" :label="t('common.color')" width="80" />
            <el-table-column prop="quantity_order" :label="t('common.quantityOrder')" width="100" align="right" />
            <el-table-column :label="t('pages.po.lineEtd')" min-width="130" show-overflow-tooltip>
              <template #default="{ row }">
                {{ row.line_etd || '—' }}
              </template>
            </el-table-column>
            <el-table-column prop="detail_remark" :label="t('pages.po.detailRemark')" min-width="140" show-overflow-tooltip />
            <el-table-column prop="unit_price" :label="t('pages.po.unitPriceUsd')" width="100" align="right">
              <template #default="{ row }">{{ row.unit_price != null ? `$${row.unit_price}` : '—' }}</template>
            </el-table-column>
            <el-table-column :label="t('pages.po.lineTotal')" width="120" align="right">
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
              </section>
            </div>
          </div>
        </div>
      </el-form>
    </div>

    <template #footer>
      <div class="po-wizard-footer">
        <div class="po-wizard-footer__left">
        <el-button @click="w.requestCloseFormDialog">
          {{ t('common.cancel') }}
        </el-button>
        <el-button v-if="!w.isEditMode" type="warning" plain @click="w.saveDraftAndClose">
          {{ t('pages.po.saveDraft') }}
        </el-button>
        </div>

        <div class="po-wizard-footer__nav">
          <el-button :disabled="w.currentStep === 0" :icon="ArrowLeft" @click="w.prevStep">
            {{ t('pages.po.wizardPrev') }}
          </el-button>
          <span class="po-wizard-footer__step">
            {{ w.currentStep + 1 }} / 3 — {{ w.currentStep === 0 ? t('pages.po.step1Title') : w.currentStep === 1 ? t('pages.po.step2Title') : t('pages.po.step3Title') }}
          </span>
          <el-button :disabled="w.currentStep === 2" type="primary" :icon="ArrowRight" @click="w.nextStep">
            {{ t('pages.po.wizardNext') }}
          </el-button>
        </div>

        <div class="po-wizard-footer__right">
        <el-button :disabled="w.currentStep !== 2 || !w.canManage" type="success" :loading="w.saving" :icon="Check" @click="w.submitForm">
          {{ t('common.savePo') }}
        </el-button>
        </div>
      </div>
    </template>
  </el-drawer>
</template>

<script setup>
import {
  ArrowLeft,
  ArrowRight,
  Check,
  DocumentAdd,
  DocumentCopy,
  Edit,
  InfoFilled,
  Picture,
  Plus,
  UploadFilled,
  WarningFilled,
} from '@element-plus/icons-vue'
import { nextTick, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import AdminTableActions from './AdminTableActions.vue'
import { usePoWizardContext } from '../../composables/poFormWizardContext.js'
import { sendToRowAnimation } from '../../composables/useSendToRowAnimation.js'

const w = usePoWizardContext()
const { t } = useI18n()
const addLineBtnRef = ref(null)

function formatColorWindowAudit(value) {
  if (!value) return '—'
  const s = String(value).replace('T', ' ')
  return s.length > 19 ? s.slice(0, 19) : s
}

function addLineButtonEl() {
  const btn = addLineBtnRef.value
  if (!btn) return null
  return btn.$el instanceof HTMLElement ? btn.$el : btn
}

onMounted(() => {
  w.onDraftLineAdded = async ({ uid, label }) => {
    await nextTick()
    await nextTick()
    const toEl = document.querySelector(`.draft-line-uid-${uid}`)
    await sendToRowAnimation({
      fromEl: addLineButtonEl(),
      toEl,
      label,
    })
  }
})
</script>

<style scoped>
.po-cw-audit {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
.po-cw-audit__badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 32px;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid transparent;
  line-height: 1.2;
}
.po-cw-audit__label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.po-cw-audit__value {
  font-size: 14px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.po-cw-audit__badge--created {
  color: #0f766e;
  background: #f0fdfa;
  border-color: #99f6e4;
}
.po-cw-audit__badge--updated {
  color: #1d4ed8;
  background: #eff6ff;
  border-color: #bfdbfe;
}

:deep(.draft-line-active > td) {
  background-color: rgb(239 246 255) !important;
}

:deep(.draft-line-just-added > td) {
  animation: draft-line-flash 1.1s ease;
}

@keyframes draft-line-flash {
  0% {
    background-color: rgb(219 234 254);
  }
  100% {
    background-color: transparent;
  }
}

:deep(.po-wizard-dialog.el-drawer) {
  box-shadow: -12px 0 32px rgba(15, 23, 42, 0.12);
}

:deep(.po-wizard-dialog .el-drawer__header) {
  padding: 0 16px 0 0;
  margin: 0;
}

:deep(.po-wizard-dialog .el-drawer__body) {
  padding: 0;
}

:deep(.po-wizard-dialog .el-drawer__footer) {
  padding: 0;
}

.po-wizard-header {
  padding: 16px 20px 12px;
  background: #fff;
}

.po-wizard-header__title-row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 10px;
}

.po-wizard-header__icon {
  font-size: 22px;
  color: var(--el-color-primary);
  margin-top: 2px;
}

.po-wizard-header__titles {
  flex: 1 1 12rem;
  min-width: 0;
}

.po-wizard-header__title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.3;
}

.po-wizard-header__sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.4;
}

.po-wizard-steps {
  margin-top: 12px;
}

.po-wizard-step-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: #64748b;
  text-align: center;
}

.po-wizard-body {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  padding: 16px;
}

.po-wizard-step {
  min-height: 280px;
}

.po-material-split {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 16px;
  align-items: stretch;
  min-height: 0;
}

.po-material-split__form,
.po-material-split__list {
  min-width: 0;
  min-height: 0;
}

.po-material-split__form .po-wizard-panel,
.po-material-list-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
}

.po-material-split__form .po-wizard-panel__body--stack {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.po-material-list-panel .po-wizard-panel__body {
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.po-material-add-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 4px;
  padding: 12px 14px;
  border: 1px solid #dbeafe;
  border-radius: 10px;
  background: #eff6ff;
}

@media (min-width: 1100px) {
  .po-material-split {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  }

  .po-wizard-step.po-material-split {
    min-height: calc(100vh - 220px);
  }

  .po-material-split__list {
    position: sticky;
    top: 0;
    align-self: start;
  }

  .po-material-list-panel {
    max-height: calc(100vh - 200px);
  }

  .po-material-split__form .el-col[class*='el-col-md-'] {
    max-width: 50%;
    flex: 0 0 50%;
  }
}

.po-wizard-panel {
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  overflow: hidden;
}

.po-wizard-panel--sub {
  background: #f8fafc;
}

.po-wizard-panel__head {
  padding: 12px 16px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.po-wizard-panel__title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #0f172a;
}

.po-wizard-panel__title--sm {
  font-size: 0.9rem;
}

.po-wizard-panel__sub {
  margin: 4px 0 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.45;
}

.po-wizard-panel__body {
  padding: 16px;
}

.po-wizard-panel__body--stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.po-wizard-group {
  padding: 0 14px 6px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
}

.po-wizard-group:first-child {
  padding-top: 0;
}

.po-wizard-group--compact {
  padding-bottom: 10px;
}

.po-wizard-group__head {
  margin: 0 -14px 12px;
  padding: 10px 14px;
  border-bottom: 1px solid #eef2f7;
  background: #f8fafc;
  border-radius: 9px 9px 0 0;
}

.po-wizard-group__head--row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.po-wizard-group__info {
  color: #64748b;
  cursor: help;
  flex-shrink: 0;
  outline: none;
}

.po-wizard-group__info:hover,
.po-wizard-group__info:focus-visible {
  color: var(--el-color-primary);
}

.po-wizard-group__info--warn {
  color: var(--el-color-warning);
}

.po-wizard-group__info--warn:hover,
.po-wizard-group__info--warn:focus-visible {
  color: #d97706;
}

.form-label-with-hint {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.form-label-hint {
  color: #94a3b8;
  cursor: help;
  outline: none;
}

.form-label-hint:hover,
.form-label-hint:focus-visible {
  color: var(--el-color-primary);
}

.po-wizard-add-line-btn {
  font-weight: 600;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2);
}

.material-fill-order-tip {
  max-width: 22rem;
  line-height: 1.45;
}

.material-fill-order-tip__title {
  margin: 0;
  font-weight: 600;
}

.material-fill-order-tip__body,
.material-fill-order-tip__next {
  margin: 6px 0 0;
}

.material-fill-order-tip__next {
  color: #e2e8f0;
}

.po-wizard-group__title {
  margin: 0;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #64748b;
}

.po-wizard-group__sub {
  margin: 4px 0 0;
  font-size: 12px;
  font-weight: 400;
  letter-spacing: 0;
  text-transform: none;
  color: #64748b;
  line-height: 1.45;
}

.po-wizard-panel .admin-action-bar {
  border-bottom: 1px solid #e2e8f0;
  border-radius: 0;
}

.po-category-radio {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px;
  min-height: 32px;
}

.po-category-radio :deep(.el-radio-button__inner) {
  padding: 7px 12px;
}

.po-color-source-radio {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.po-color-source-radio :deep(.el-radio-button__inner) {
  padding: 6px 10px;
}

.po-dialog-form :deep(.el-form-item) {
  margin-bottom: 12px;
  width: 100%;
}

.po-dialog-form :deep(.el-form-item__label) {
  height: 38px;
  display: flex;
  align-items: flex-end;
  line-height: 1.25;
  margin-bottom: 4px !important;
  padding-bottom: 0 !important;
  color: #475569;
  font-weight: 600;
}

.po-dialog-form :deep(.el-form-item__content) {
  width: 100%;
  line-height: 1.4;
}

.material-step-grid :deep(.el-col) {
  display: flex;
  flex-direction: column;
}

.material-step-grid :deep(.el-input),
.material-step-grid :deep(.el-select),
.material-step-grid :deep(.el-date-editor),
.material-step-grid :deep(.el-input-number) {
  width: 100%;
}

.po-dialog-form :deep(.el-date-editor.el-input),
.po-dialog-form :deep(.el-date-editor.el-input__wrapper) {
  width: 100%;
}

.po-field-meta,
.field-lock-row > .mt-1,
.field-lock-row > .mt-2,
.field-stack-row > .mt-1,
.po-dialog-form :deep(.el-form-item__content > .mt-1),
.po-dialog-form :deep(.el-form-item__content > .mt-2) {
  min-height: 22px;
  margin-top: 4px;
}

.po-wizard-inline-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 8px;
  padding-bottom: 12px;
  min-height: 70px;
}

.field-lock-row,
.field-stack-row {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 4px;
  width: 100%;
}

.po-price-miss {
  margin: 6px 0 0;
  font-size: 12px;
  line-height: 1.4;
  color: #b45309;
}

.po-price-addon-labels {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 6px;
}

.po-price-addon-labels--end {
  justify-content: flex-end;
}

.po-price-addon-note,
.po-price-source {
  width: 100%;
  margin: 0;
  font-size: 11px;
  line-height: 1.35;
  color: #64748b;
}

.po-price-addon-label {
  display: inline-block;
  padding: 1px 6px;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: #f8fafc;
  color: #334155;
  font-size: 11px;
  line-height: 1.5;
  white-space: nowrap;
}

.field-lock-row :deep(.el-input),
.field-lock-row :deep(.el-select),
.field-stack-row :deep(.el-input),
.field-stack-row :deep(.el-select),
.field-stack-row :deep(.el-date-editor),
.field-stack-row :deep(.el-input-number) {
  width: 100%;
  min-width: 0;
}

.po-draft-table {
  width: 100%;
  min-width: 1100px;
}

.po-wizard-footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border-top: 1px solid #e2e8f0;
}

.po-wizard-footer__left,
.po-wizard-footer__right {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.po-wizard-footer__nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.po-wizard-footer__step {
  font-size: 12px;
  font-weight: 600;
  color: #0369a1;
  min-width: 10rem;
  text-align: center;
}

@media (max-width: 767px) {
  .po-wizard-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .po-wizard-footer__nav {
    order: -1;
  }

  .po-wizard-footer__left,
  .po-wizard-footer__right {
    justify-content: center;
  }
}

.etd-schedule-table :deep(.el-table__header-wrapper) {
  display: none;
}

:deep(.po-row-highlight > td) {
  background-color: rgb(255 251 235) !important;
}
</style>
