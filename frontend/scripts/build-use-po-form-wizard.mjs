import fs from 'node:fs'
import path from 'node:path'

const root = path.resolve(import.meta.dirname, '..')
const pagePath = process.argv[2] || path.join(root, 'src/views/admin/PurchaseOrderPage.vue')
const lines = fs.readFileSync(pagePath, 'utf8').split('\n')

/** 1-based inclusive line ranges (wizard-only; skip list handlers di tengah). */
const ranges = [
  [380, 409],
  [465, 560],
  [568, 2041],
  [2249, 2315],
]

const bodyParts = ranges.map(([start, end]) => lines.slice(start - 1, end).join('\n'))
const body = bodyParts.join('\n\n')

const header = `import { computed, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { providePoWizardContext } from './poFormWizardContext.js'
import { usePoMarketingRevise } from './usePoMarketingRevise.js'
import {
  emptyEtdScheduleRows,
  normalizeSchedulesFromApi,
  etdScheduleRowsToPayload,
  loadEtdScheduleRowsFromApi,
  lineHasScheduleMismatch,
  buildEvenEtdScheduleRows,
} from '../utils/poEtdSchedule.js'
import {
  buildPoDraftPayload,
  applyPoDraftData,
  savePoDraftLocalStorage,
  clearPoDraftLocalStorage,
  readPoDraftRaw,
} from '../utils/poDraft.js'
import {
  factoryCodeFromCustomer,
  swatchFactoryHint,
  swatchOptionLabel,
  fetchColorSwatchOptionList,
  applyColorSwatchFill,
} from '../utils/poColorSwatch.js'
import { parseApiErrorMessage } from '../utils/poApi.js'
import { customerOptionLabel } from '../utils/poList.js'
import {
  inferColorFamilyFromColor,
  applyReferenceDefaults as applyReferenceDefaultsFromMaster,
  hydrateFormFromMasterItemRow as applyMasterItemToForm,
  resetMaterialFieldToMaster as resetMaterialFieldToMasterValues,
  isThicknessPricingFormatValid,
  detailMasterSnapshot,
} from '../utils/poMasterResolve.js'
import {
  buildDetailBodyCore,
  appendDetailUnitPrice,
  detailPayloadForUpdate,
  sanitizeNewDetailBody,
} from '../utils/poDetailPayload.js'
import {
  addPoDetail,
  createPo,
  deletePoDetail,
  generatePoDetailLot,
  generateLotPreview,
  fetchNextPoNumber,
  getAllowedBrands,
  getCustomer,
  listBrandBuyers,
  listMasterItemDimensionValues,
  resolveMasterItemByDimensions,
  listFluorescentColors,
  lookupColorSwatchRecipes,
  getColorSwatchPoFill,
  listPoDetails,
  listPoForCopy,
  resolveBuyerUnitPrice,
  setPoDetailDeliverySchedules,
  listPoDetailDeliverySchedules,
  toIsoDate,
  updatePo,
  updatePoDetail,
} from '../api/client'

/** State & handler wizard PO (form dialog 3-step). */
export function usePoFormWizard({ t, canManage, customers, brands, masterItems, buyerCodes, load }) {
  function formatCustomerOption(c) {
    return customerOptionLabel(c, t)
  }

  const saving = ref(false)

`

const footer = `
  providePoWizardContext({
    formDialogVisible,
    formModel,
    formErrors,
    currentStep,
    isEditMode,
    canManage,
    nextPoNumberDisplay,
    customers,
    formatCustomerOption,
    brandLockedCustomerId,
    onCustomerChange,
    customerPicDisplay,
    brandsFiltered,
    onBrandChange,
    isBrandDisabled,
    buyerCodesFiltered,
    isBuyerDisabled,
    autoFieldMeta,
    resetToAuto,
    isPoCategoryDisabled,
    orderDateLocked,
    brands,
    materialDimensionOptions,
    onPickedMaterialDimension,
    thicknessDimensionOptions,
    onPickedThicknessDimension,
    isFluorescentFamily,
    poColorCascadeOptions,
    colorDimensionOptions,
    enableMaterialOverride,
    isMaterialFieldLocked,
    materialFieldOverride,
    resetMaterialFieldToMaster,
    activeSeasonLabel,
    fluorescentColorOptions,
    selectedSwatchId,
    colorSwatchLoading,
    colorSwatchOptions,
    swatchOptionLabel,
    poFactoryKeyForSwatch,
    applyColorSwatch,
    swatchAllMaterials,
    loadColorSwatchOptions,
    swatchRetriedWithoutMaterial,
    masterResolveLoading,
    resolvedMasterItemLabel,
    clearLinkedMasterItem,
    lastResolveHadNoMaster,
    materialThicknessColorComplete,
    colorFamilyAutoMode,
    materialAdvancedOpen,
    pricingKeyIncomplete,
    etdScheduleOpen,
    etdScheduleRows,
    clearEtdScheduleRows,
    autoFillEtdScheduleWave1,
    autoFillEtdScheduleEvenly,
    etdScheduleTotalDisplay,
    etdScheduleMismatch,
    draftLinesDisplay,
    draftLines,
    draftRiskOnly,
    draftRowClassName,
    pushCurrentLine,
    openCopyItemDialog,
    colorFamilyLabel,
    materialQualityTooltip,
    materialQualityType,
    materialQualityLabel,
    hasSpecialPriceInLines,
    generateLotNumber,
    removeDraftLine,
    editDraftLine,
    previewResolvedUnitPrice,
    onSpecialPriceChange,
    calculateSpecialPrice,
    lotGenerateLoading,
    lotAutoFromMaterial,
    handleEnterKey,
    handlePoDialogBeforeClose,
    requestCloseFormDialog,
    openMarketingReviseDialog,
    nextStep,
    prevStep,
    submitForm,
    saveDraftAndClose,
    saving,
  })

  return {
    formDialogVisible,
    openCreateDialog,
    openEditDialog,
    materialDimensionOptions,
    colorFamilyLabel,
    formatCustomerOption,
    marketingReviseVisible,
    marketingReviseLoading,
    marketingReviseSaving,
    marketingReviseHeader,
    marketingReviseLines,
    submitMarketingRevise,
    copyItemDialogVisible,
    copyItemCustomerId,
    copyItemSearch,
    copyItemSourcePo,
    copyItemFilteredPo,
    copyItemSelected,
    onCopyItemCustomerChange,
    onCopyItemSelectionChange,
    addCopiedItems,
    ambiguousMasterVisible,
    ambiguousMasterCandidates,
    selectedAmbiguousMasterId,
    confirmAmbiguousMasterPick,
  }
}
`

const outPath = path.join(root, 'src/composables/usePoFormWizard.js')
const content = header + body + footer
fs.writeFileSync(outPath, content)
console.log('Wrote', outPath, 'lines', content.split('\n').length)
