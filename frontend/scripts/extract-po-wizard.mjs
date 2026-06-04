import fs from 'node:fs'
import path from 'node:path'

const root = path.resolve(import.meta.dirname, '..')
const pagePath = path.join(root, 'src/views/admin/PurchaseOrderPage.vue')
const page = fs.readFileSync(pagePath, 'utf8')
const lines = page.split('\n')
const tpl = lines.slice(195, 1044).join('\n')

const WIZARD_BINDINGS = [
  'formDialogVisible',
  'formModel',
  'formErrors',
  'currentStep',
  'isEditMode',
  'canManage',
  'nextPoNumberDisplay',
  'customers',
  'formatCustomerOption',
  'brandLockedCustomerId',
  'onCustomerChange',
  'customerPicDisplay',
  'brandsFiltered',
  'onBrandChange',
  'isBrandDisabled',
  'buyerCodesFiltered',
  'isBuyerDisabled',
  'autoFieldMeta',
  'resetToAuto',
  'isPoCategoryDisabled',
  'orderDateLocked',
  'brands',
  'materialDimensionOptions',
  'onPickedMaterialDimension',
  'thicknessDimensionOptions',
  'onPickedThicknessDimension',
  'isFluorescentFamily',
  'poColorCascadeOptions',
  'colorDimensionOptions',
  'enableMaterialOverride',
  'isMaterialFieldLocked',
  'materialFieldOverride',
  'resetMaterialFieldToMaster',
  'activeSeasonLabel',
  'fluorescentColorOptions',
  'selectedSwatchId',
  'colorSwatchLoading',
  'colorSwatchOptions',
  'swatchOptionLabel',
  'poFactoryKeyForSwatch',
  'applyColorSwatch',
  'swatchAllMaterials',
  'loadColorSwatchOptions',
  'swatchRetriedWithoutMaterial',
  'masterResolveLoading',
  'resolvedMasterItemLabel',
  'clearLinkedMasterItem',
  'lastResolveHadNoMaster',
  'materialThicknessColorComplete',
  'colorFamilyAutoMode',
  'materialAdvancedOpen',
  'pricingKeyIncomplete',
  'etdScheduleOpen',
  'etdScheduleRows',
  'clearEtdScheduleRows',
  'autoFillEtdScheduleWave1',
  'autoFillEtdScheduleEvenly',
  'etdScheduleTotalDisplay',
  'etdScheduleMismatch',
  'draftLinesDisplay',
  'draftLines',
  'draftRiskOnly',
  'draftRowClassName',
  'pushCurrentLine',
  'openCopyItemDialog',
  'colorFamilyLabel',
  'materialQualityTooltip',
  'materialQualityType',
  'materialQualityLabel',
  'hasSpecialPriceInLines',
  'generateLotNumber',
  'removeDraftLine',
  'editDraftLine',
  'previewResolvedUnitPrice',
  'onSpecialPriceChange',
  'calculateSpecialPrice',
  'lotGenerateLoading',
  'lotAutoFromMaterial',
  'handleEnterKey',
  'handlePoDialogBeforeClose',
  'requestCloseFormDialog',
  'openMarketingReviseDialog',
  'nextStep',
  'prevStep',
  'submitForm',
  'saveDraftAndClose',
  'saving',
]

function prefixBindings(source) {
  let out = source
  const sorted = [...WIZARD_BINDINGS].sort((a, b) => b.length - a.length)
  for (const id of sorted) {
    const re = new RegExp(`(?<!w\\.)\\b${id}\\b`, 'g')
    out = out.replace(re, `w.${id}`)
  }
  return out
}

const transformed = prefixBindings(tpl)

const component = `<template>
${transformed}
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

<style scoped src="../../styles/po-form-wizard-dialog.css"></style>
`

const stylesStart = lines.findIndex((l) => l.includes(':deep(.po-fullscreen-dialog.el-dialog)'))
const stylesEnd = lines.findIndex((l, i) => i > stylesStart && l.trim() === '.po-price-readonly :deep(.el-input__wrapper) {')
let styleLines = []
if (stylesStart >= 0) {
  const endLine = lines.findIndex((l, i) => i > stylesStart && l.startsWith('.po-row-actions'))
  const sliceEnd = endLine > stylesStart ? endLine : stylesStart + 220
  styleLines = lines.slice(stylesStart, sliceEnd)
}

const cssPath = path.join(root, 'src/styles/po-form-wizard-dialog.css')
fs.mkdirSync(path.dirname(cssPath), { recursive: true })
fs.writeFileSync(
  cssPath,
  styleLines
    .map((l) => l.replace(/^:deep\(/, ':deep('))
    .join('\n')
    .replace(/^\s*\/\* scoped from parent \*\//, ''),
)

const outPath = path.join(root, 'src/components/admin/PoFormWizardDialog.vue')
fs.writeFileSync(outPath, component)
console.log('Wrote', outPath, 'lines', component.split('\n').length)
