import { computed, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { providePoWizardContext } from './poFormWizardContext.js'
import { usePoMarketingRevise } from './usePoMarketingRevise.js'
import { usePoStepCustomer, brandCustomerIds, inferSoMaterialGroup } from './usePoStepCustomer.js'
import { usePoStepLines } from './usePoStepLines.js'
import { usePoStepReview } from './usePoStepReview.js'
import {
  emptyEtdScheduleRows,
  lineHasScheduleMismatch,
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
  applySwatchRecipeOption,
  pickBestSwatchRecipe,
} from '../utils/poColorSwatch.js'
import {
  COLOR_STANDARD_SOURCE,
  applyCsiColorToForm,
  applyWaitingCsToForm,
  csiColorOptionLabel,
  extractColorCodeFromReference,
  hasColorStandardValue,
  inferColorStandardSource,
  isWaitingColorRef,
  lineHasColorStandard,
  matchCsiOption,
} from '../utils/poColorStandard.js'
import { parseApiErrorMessage } from '../utils/poApi.js'
import { customerOptionLabel, normalizePoOrderCategory } from '../utils/poList.js'
import {
  inferColorFamilyFromColor,
  applyReferenceDefaults as applyReferenceDefaultsFromMaster,
  hydrateFormFromMasterItemRow as applyMasterItemToForm,
  resetMaterialFieldToMaster as resetMaterialFieldToMasterValues,
  isThicknessPricingFormatValid,
  formatThicknessDisplay,
  detailMasterSnapshot,
  inferItemCategory,
  ITEM_CATEGORY_PU,
  ITEM_CATEGORY_SUEDE,
  normalizeItemCategory,
  resolveMaterialGroupLabel,
} from '../utils/poMasterResolve.js'
import {
  buildDetailBodyCore,
  appendDetailUnitPrice,
  detailPayloadForUpdate,
  sanitizeNewDetailBody,
} from '../utils/poDetailPayload.js'
import { collectReservedLots, nextLotAfterReserved } from '../utils/poLot.js'
import {
  addPoDetail,
  createPo,
  deletePoDetail,
  generatePoDetailLot,
  generateLotPreview,
  checkPoCustomerRef,
  getCustomer,
  listMasterItemDimensionValues,
  listMasterItems,
  resolveMasterItemByDimensions,
  listFluorescentColors,
  lookupColorSwatchRecipes,
  getColorSwatchPoFill,
  listCsiColorsPage,
  listPoDetails,
  listPoForCopy,
  resolveBuyerUnitPrice,
  toIsoDate,
  updatePo,
  updatePoDetail,
  mrpSyncPo,
} from '../api/client'

function localTodayIsoDate() {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/** State & handler wizard PO (form dialog 3-step). */
export function usePoFormWizard({
  t,
  canCreate,
  canUpdate,
  customers,
  brands,
  masterItems,
  buyerCodes,
  load,
}) {
  const canManage = computed(() => canCreate.value || canUpdate.value)
  function formatCustomerOption(c) {
    return customerOptionLabel(c, t)
  }

  let masterItemsLoad = null
  async function ensureMasterItemsLoaded() {
    if ((masterItems.value || []).length) return
    if (!masterItemsLoad) {
      masterItemsLoad = listMasterItems()
        .then((rows) => {
          masterItems.value = rows || []
        })
        .catch(() => {})
        .finally(() => {
          masterItemsLoad = null
        })
    }
    await masterItemsLoad
  }

  const saving = ref(false)

const formErrors = reactive({
  customer_id: '',
  brand_id: '',
  material_name: '',
  quantity_order: '',
  po_customer_ref: '',
})

const brandBuyerCodes = ref([])
const customerBuyerCodes = ref([])
const brandLockedCustomerId = ref(null)
const allowedBrandIds = ref([])
const selectedCustomer = ref(null)
const autoFieldMeta = reactive({
  buyer: false,
  factory_code: false,
  vir_softness_type: false,
  softness: false,
  color_reference: false,
  color_standard: false,
  backing: false,
  model: false,
})
const materialFieldOverride = reactive({
  material_name: false,
  thickness_text: false,
  color: false,
  color_family: false,
  emboss: false,
  style_article: false,
})
const colorFamilyAutoMode = ref(true)
const lotAutoFromMaterial = ref(false)
const lotGenerateLoading = ref(false)
let lotAutoTimer = null
let skipLotAutoUntil = 0
let lotAutoSeq = 0

function brandAllowedForCustomer(brand, customerId) {
  if (!customerId) return true
  const mapped = brandCustomerIds(brand)
  if (!mapped.length) return true
  return mapped.includes(Number(customerId))
}

const brandsFiltered = computed(() => {
  if (allowedBrandIds.value.length > 0) {
    return brands.value.filter((b) => allowedBrandIds.value.includes(b.id))
  }
  const cid = formModel.customer_id
  if (cid) {
    return brands.value.filter((b) => brandAllowedForCustomer(b, cid))
  }
  return brands.value
})

const buyerCodesFiltered = computed(() => {
  if (brandBuyerCodes.value.length) return brandBuyerCodes.value
  if (customerBuyerCodes.value.length) return customerBuyerCodes.value
  if (formModel.customer_id || formModel.brand_id) return []
  return buyerCodes.value
})
const isBrandDisabled = computed(() => !formModel.customer_id || allowedBrandIds.value.length === 0)
const isBuyerDisabled = computed(() => !formModel.customer_id || !formModel.brand_id || buyerCodesFiltered.value.length === 0)
const isPoCategoryDisabled = computed(() => !formModel.customer_id || !formModel.brand_id || !formModel.buyer)
const isSubkonPo = computed(() => formModel.po_category === 'subcont')
const subkonMasterItems = computed(() =>
  (masterItems.value || []).filter((x) => String(x.category || '').trim().toLowerCase() === 'subkon'),
)
const subkonItemCodePicker = ref('')

function masterDimensionCategoryParam() {
  if (isSubkonPo.value) return 'SubKon'
  return formModel.item_category || ITEM_CATEGORY_PU
}

const customerPicDisplay = computed(() => {
  if (!selectedCustomer.value) return t('common.emptyValue')
  const name = selectedCustomer.value.contact_person || selectedCustomer.value.name || ''
  const position = selectedCustomer.value.position || ''
  if (name && position) return `${name} (${position})`
  return name || position || t('common.emptyValue')
})

const nextPoNumberPreview = ref('')

const nextPoNumberDisplay = computed(() => {
  if (isEditMode.value) return formModel.po_number || ''
  return nextPoNumberPreview.value || '…'
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
      ElMessage.warning(t('pages.po.brandRequiredAfterCustomer'))
      return
    }
    if (!formModel.buyer) {
      ElMessage.warning(t('pages.po.buyerRequiredAfterBrand'))
      return
    }
    formErrors.customer_id = ''
  }
  if (currentStep.value < 2) {
    currentStep.value++
    if (currentStep.value === 1) {
      void refreshMaterialDimensionOptions()
    }
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const formDialogVisible = ref(false)
const formHydrating = ref(false)
const isEditMode = ref(false)
let editOpenSeq = 0
/** Tanggal order dari DB saat buka edit — jika ada, tanggal tidak boleh diubah lewat form simpan penuh. */
const savedHeaderOrderDate = ref('')
const orderDateLocked = computed(() => isEditMode.value && Boolean(savedHeaderOrderDate.value))

const editingPoId = ref(null)
const editingDetailIds = ref([])
const draftLines = ref([])
const draftRiskOnly = ref(false)
const editingDraftLineIndex = ref(-1)

const currentLineLocked = computed(() => {
  const idx = editingDraftLineIndex.value
  if (idx < 0) return false
  return Boolean(draftLines.value[idx]?.line_locked)
})
const onDraftLineAdded = ref(null)
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

const formModel = reactive({
  po_number: '',
  customer_id: null,
  brand_id: null,
  po_category: 'production',
  item_category: ITEM_CATEGORY_PU,
  factory_code: '',
  order_date: '',
  buyer: '',
  etd: '',
  po_customer_ref: '',
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
  color_standard: '',
  backing: '',
  quantity_order: '',
  style_article: '',
  model: '',
  detail_remark: '',
  thi_line_ref: '',
  unit_price_input: null,
  autoPricingEnabled: true,
  is_special_price: false,
  discount_type: 'percent',
  discount_value: 0,
})

const {
  visible: marketingReviseVisible,
  loading: marketingReviseLoading,
  saving: marketingReviseSaving,
  header: marketingReviseHeader,
  lines: marketingReviseLines,
  open: openMarketingReviseDialog,
  submit: submitMarketingRevise,
} = usePoMarketingRevise({ t, editingPoId, formModel })

const pricePreviewLoading = ref(false)
const previewResolvedUnitPrice = ref(null)
const fluorescentColorOptions = ref([])
const colorSwatchOptions = ref([])
const colorSwatchLoading = ref(false)
const swatchAllMaterials = ref(false)
const swatchRetriedWithoutMaterial = ref(false)
const selectedSwatchId = ref(null)
const swatchFieldsManualEdit = ref(false)
const swatchPickerOpen = ref(false)
const colorStandardSource = ref('')
const selectedCsiId = ref(null)
const csiOptions = ref([])
const csiLoading = ref(false)

const selectedSwatchRecipe = computed(() => {
  const id = selectedSwatchId.value
  if (!id) return null
  return colorSwatchOptions.value.find((x) => x.id === id) || null
})

/** Hanya kunci saat baris SO terkunci; CS/backing dari resep tetap bisa di-override langsung. */
const swatchFieldsLocked = computed(() => currentLineLocked.value)

/** Color standart & backing selalu tampil (auto-terisi dari resep; tetap overridable). */
const showColorStandardBackingFields = computed(() => true)

const {
  etdScheduleOpen,
  etdScheduleRows,
  clearEtdScheduleRows,
  copyEtdDateFromHeader,
  syncEtdQtyFromOrder,
  etdScheduleMismatch,
} = usePoStepReview({ formModel })

async function syncCurrentFormToDraftLine() {
  if (editingDraftLineIndex.value < 0) return
  const idx = editingDraftLineIndex.value
  if (idx >= draftLines.value.length) return
  const cur = await buildCurrentDetailBody()
  draftLines.value[idx] = {
    ...draftLines.value[idx],
    ...cur,
    delivery_schedules: cur.delivery_schedules || [],
  }
}

function draftRowClassName({ row }) {
  const classes = []
  const idx = draftLines.value.indexOf(row)
  if (idx >= 0 && idx === editingDraftLineIndex.value) classes.push('draft-line-active')
  if (row._uid) classes.push(`draft-line-uid-${row._uid}`)
  return classes.join(' ')
}

async function applyLineToForm(line) {
  formModel.item_category = inferItemCategory(line, masterItems.value)
  formModel.master_item_id = line.master_item_id ?? null
  formModel.material_name = line.material_name || ''
  formModel.thickness_text = line.thickness_text || ''
  formModel.color = line.color || ''
  formModel.color_family = line.color_family || null
  formModel.emboss = line.emboss || ''
  formModel.vir_softness_type = line.vir_softness_type || ''
  formModel.softness = line.softness || ''
  formModel.color_reference = line.color_reference || ''
  formModel.color_standard = line.color_standard || ''
  formModel.backing = line.backing || ''
  formModel.quantity_order = line.quantity_order != null ? String(line.quantity_order) : ''
  formModel.style_article = line.style_article || ''
  formModel.model = line.model || ''
  formModel.detail_remark = line.detail_remark || ''
  formModel.thi_line_ref = line.thi_line_ref || ''
  formModel.unit_price_input = line.unit_price != null ? Number(line.unit_price) : null
  selectedSwatchId.value = line.color_swatch_recipe_id ?? null
  clearBackingForSuede()
  await hydrateColorStandardFromLine(line)
  etdScheduleRows.value = line.line_etd
    ? [{ sequence_no: 1, qty: null, date: String(line.line_etd).slice(0, 10) }]
    : emptyEtdScheduleRows()
  const linked = masterItems.value.find((x) => x.id === line.master_item_id)
  masterItemCodePicker.value = linked?.item_code || ''
  await refreshMaterialDimensionOptions()
  await refreshThicknessOptionsFromApi()
  await refreshColorOptionsFromApi()
  await refreshEmbossOptionsFromApi()
  await refreshItemCodeOptionsFromApi()
}

async function editDraftLine(row) {
  const idx = draftLines.value.indexOf(row)
  if (idx < 0) return
  if (editingDraftLineIndex.value >= 0 && editingDraftLineIndex.value !== idx) {
    await syncCurrentFormToDraftLine()
  }
  editingDraftLineIndex.value = idx
  await applyLineToForm(draftLines.value[idx])
  currentStep.value = 1
  ElMessage.info(t('pages.po.editingDraftLine', { n: idx + 1 }))
}

function cloneDraftLinePayload(row) {
  return {
    item_category: inferItemCategory(row, masterItems.value),
    master_item_id: row.master_item_id,
    material_name: row.material_name,
    thickness_text: row.thickness_text,
    color: row.color,
    color_family: row.color_family,
    emboss: row.emboss,
    vir_softness_type: row.vir_softness_type,
    softness: row.softness,
    color_reference: row.color_reference,
    color_standard: row.color_standard,
    backing: row.backing,
    quantity_order: row.quantity_order,
    style_article: row.style_article,
    model: row.model,
    detail_remark: row.detail_remark,
    color_swatch_recipe_id: row.color_swatch_recipe_id,
    unit_price: row.unit_price,
    base_price: row.base_price,
    is_special_price: row.is_special_price,
    discount_type: row.discount_type,
    discount_value: row.discount_value,
    manual_override: Boolean(row.manual_override),
    material_master_override: Boolean(row.material_master_override),
    material_master_matched: Boolean(row.material_master_matched),
    line_etd: row.line_etd || undefined,
    delivery_schedules: [],
    copied_from_detail_id: row.id || row.copied_from_detail_id || undefined,
  }
}

function copyDraftLine(row) {
  const idx = draftLines.value.indexOf(row)
  if (idx < 0) return
  const clone = cloneDraftLinePayload(row)
  const sourceLot = String(row.thi_line_ref || '').trim()
  if (sourceLot) {
    clone.thi_line_ref = nextLotAfterReserved(sourceLot, collectReservedLots(draftLines.value))
  }
  draftLines.value.splice(idx + 1, 0, clone)
  if (editingDraftLineIndex.value > idx) {
    editingDraftLineIndex.value += 1
  }
  ElMessage.success(t('pages.po.lineCopied'))
}

function resetCurrentLineForm() {
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
  formModel.color_standard = ''
  autoFieldMeta.color_standard = false
  formModel.backing = ''
  autoFieldMeta.backing = false
  formModel.quantity_order = ''
  formModel.style_article = ''
  formModel.model = ''
  autoFieldMeta.model = false
  formModel.detail_remark = ''
  formModel.thi_line_ref = ''
  formModel.unit_price_input = null
  selectedSwatchId.value = null
  clearEtdScheduleRows()
  resetMaterialFieldOverride()
  colorFamilyAutoMode.value = true
  lastResolveHadNoMaster.value = false
  thicknessDimensionOptions.value = []
  colorDimensionOptions.value = []
  embossDimensionOptions.value = []
  itemCodeDimensionOptions.value = []
  masterItemCodePicker.value = ''
  formErrors.material_name = ''
  formErrors.quantity_order = ''
  resetColorStandardSourceState()
  scheduleAutoLotGenerate()
}

function cancelEditDraftLine() {
  editingDraftLineIndex.value = -1
  resetCurrentLineForm()
}

const materialDimensionOptions = ref([])
const thicknessDimensionOptions = ref([])
const colorDimensionOptions = ref([])
const embossDimensionOptions = ref([])
const itemCodeDimensionOptions = ref([])
const masterItemCodePicker = ref('')
const masterResolveLoading = ref(false)
const ambiguousMasterVisible = ref(false)
const ambiguousMasterCandidates = ref([])
const selectedAmbiguousMasterId = ref(null)
const lastResolveHadNoMaster = ref(false)
/** Hindari resolve berulang saat dialog ambigu ditutup tanpa pilihan (kombinasi sama). */
const skipMasterResolve = ref(false)
/** Cegah resolve ulang saat buka edit PO selama kombinasi material|ketebalan|warna|master_id sama seperti yang dimuat dari DB. */
const loadedDetailMasterSnapshot = ref(null)

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
      emboss: formModel.emboss || null,
      factory_code: formModel.factory_code || null,
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

const isFluorescentFamily = computed(() => String(formModel.color_family || '').toLowerCase() === 'fluorescent')
const materialThicknessColorComplete = computed(() => {
  return (
    String(formModel.material_name || '').trim().length > 0 &&
    String(formModel.thickness_text || '').trim().length > 0 &&
    String(formModel.color || '').trim().length > 0
  )
})
const resolvedMasterItemLabel = computed(() => {
  const id = formModel.master_item_id
  if (!id) return ''
  const it = masterItems.value.find((x) => x.id === id)
  if (!it) return `#${id}`
  return `${it.item_code} — ${it.material_name || ''}`
})
const activeSeasonLabel = computed(() => deriveSeasonLabel(formModel.order_date))
const pricingKeyIncomplete = computed(() => {
  if (formModel.po_category === 'subcont' || formModel.po_category === 'return') return false
  if (!(formModel.buyer || '').trim()) return false
  return !String(formModel.material_name || '').trim() || !String(formModel.thickness_text || '').trim()
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
  const adjustValue = Number(formModel.discount_value || 0)

  if (formModel.discount_type === 'percent') {
    // adjustment percent: bisa + / -
    formModel.unit_price_input = basePrice * (1 + adjustValue / 100)
  } else {
    // adjustment nominal USD: bisa + / -
    formModel.unit_price_input = Math.max(0, basePrice + adjustValue)
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

function materialGroupLabel(row) {
  return resolveMaterialGroupLabel(row, masterItems.value)
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

const poColorCascadeOptions = computed(() => {
  if (!isFluorescentFamily.value) return []
  const dimSet = new Set(colorDimensionOptions.value.map((x) => String(x).trim().toLowerCase()))
  const all = fluorescentColorOptions.value || []
  const inter = all.filter((o) => dimSet.has(String(o.color_name || '').trim().toLowerCase()))
  const src = inter.length ? inter : all
  return src.map((o) => ({
    ...o,
    _label: formatFluorescentOption(o),
  }))
})

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
    let rows = await listFluorescentColors({
      buyer_code: buyer,
      season_label: seasonLabel || undefined,
    })
    if (!rows.length && seasonLabel) {
      rows = await listFluorescentColors({ buyer_code: buyer })
    }
    fluorescentColorOptions.value = rows
  } catch {
    fluorescentColorOptions.value = []
  }
}

async function fetchFluorescentOptionsForValidation() {
  const buyer = String(formModel.buyer || '').trim().toUpperCase()
  if (!buyer) return []
  try {
    const seasonLabel = deriveSeasonLabel(formModel.order_date)
    let rows = await listFluorescentColors({
      buyer_code: buyer,
      season_label: seasonLabel || undefined,
    })
    if (!rows.length && seasonLabel) {
      rows = await listFluorescentColors({ buyer_code: buyer })
    }
    return rows
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
    const colorCode = extractColorCodeFromReference(line.color)
    const codeOk = colorCode && opts.some((x) => String(x.color_code || '').trim().toUpperCase() === colorCode)
    if (!validNames.has(color) && !codeOk) {
      throw new Error(`Line ${i + 1}: warna fluorescent wajib dipilih dari master fluorescent sesuai buyer/season.`)
    }
  }
}

function isSelectedFluorescentColorValid() {
  if (!isFluorescentFamily.value) return true
  const chosen = String(formModel.color || '').trim().toLowerCase()
  if (!chosen) return true
  if (!fluorescentColorOptions.value.length) return true
  const chosenCode = extractColorCodeFromReference(formModel.color)
  return fluorescentColorOptions.value.some((opt) => {
    const name = String(opt.color_name || '').trim().toLowerCase()
    if (name && name === chosen) return true
    const code = String(opt.color_code || '').trim().toUpperCase()
    return Boolean(chosenCode && code && code === chosenCode)
  })
}

function applyAutoFactoryCode(customer, { force = false } = {}) {
  const code = factoryCodeFromCustomer(customer)
  if (!code) return
  const current = String(formModel.factory_code || '').trim()
  if (force || autoFieldMeta.factory_code || !current) {
    formModel.factory_code = code
    autoFieldMeta.factory_code = true
  }
}

const stepCustomer = usePoStepCustomer({
  t,
  formModel,
  formErrors,
  brands,
  customers,
  brandBuyerCodes,
  customerBuyerCodes,
  brandLockedCustomerId,
  allowedBrandIds,
  selectedCustomer,
  autoFieldMeta,
  isEditMode,
  nextPoNumberPreview,
  draftLines,
  applyAutoFactoryCode,
})
const { refreshNextPoNumberPreview, onCustomerChange, onBrandChange } = stepCustomer

watch(
  () => [formModel.po_category, formModel.order_date, formModel.vir_softness_type, formModel.material_name, draftLines.value.length],
  () => {
    if (!formDialogVisible.value || isEditMode.value) return
    void refreshNextPoNumberPreview()
  },
)

const stepLines = usePoStepLines({
  materialDimensionOptions,
  thicknessDimensionOptions,
  masterDimensionCategoryParam,
})
const { refreshMaterialDimensionOptions } = stepLines

function upsertMasterItemInCache(row) {
  stepLines.upsertMasterItemInCache(masterItems, row)
}

function poFactoryKeyForSwatch() {
  return swatchFactoryHint(formModel, {
    customers: customers.value,
    selectedCustomer: selectedCustomer.value,
  })
}

/** Langkah isian material berikutnya (1–5); 0 = siap swatch/qty. */
const materialStepFillStep = computed(() => {
  if (isSubkonPo.value) {
    if (!String(formModel.material_name || '').trim()) return 1
    return 0
  }
  if (!String(formModel.material_name || '').trim()) return 1
  if (!String(formModel.thickness_text || '').trim()) return 2
  if (!String(formModel.color || '').trim()) return 3
  if (!String(formModel.emboss || '').trim()) return 4
  if (
    !hasColorStandardValue(formModel, {
      selectedSwatchId: selectedSwatchId.value,
      source: colorStandardSource.value,
    })
  ) {
    return 5
  }
  return 0
})

const swatchHelperMessage = computed(() => {
  if (colorSwatchLoading.value) return ''
  if (!formModel.buyer) {
    return t('pages.po.swatchNeedBuyer')
  }
  if (!String(formModel.material_name || '').trim()) {
    return t('pages.po.swatchNeedMaterial')
  }
  if (!String(formModel.color || '').trim() || !String(formModel.emboss || '').trim()) {
    return t('pages.po.swatchNeedColorEmboss')
  }
  if (!colorSwatchOptions.value.length) {
    return t('pages.po.swatchNoMatchInMaster')
  }
  return ''
})

/** Production/Suede: CS wajib sebelum baris bisa ditambah/lanjut. SubKon dikecualikan. */
const isColorStandardRequired = computed(() => !isSubkonPo.value)

const hasColorStandardReady = computed(() =>
  hasColorStandardValue(formModel, {
    selectedSwatchId: selectedSwatchId.value,
    source: colorStandardSource.value,
  }),
)

function ensureColorStandardReady({ warn = true } = {}) {
  if (!isColorStandardRequired.value) return true
  if (hasColorStandardReady.value) return true
  if (warn) ElMessage.warning(t('pages.po.colorStandardRequired'))
  return false
}

let lastSwatchScopeKey = ''
let lastAutoSwatchDimensionKey = ''

function swatchScopeKey() {
  return [formModel.buyer, formModel.material_name, swatchAllMaterials.value]
    .map((x) => String(x ?? '').trim().toLowerCase())
    .join('|')
}

/** Color Swatch (PU) vs Color Window (Suede) — label saja; sumber data sama. */
const isSuedeMaterial = computed(() => {
  if (normalizeItemCategory(formModel.item_category) === ITEM_CATEGORY_SUEDE) return true
  const linked = masterItems.value.find((x) => x.id === formModel.master_item_id)
  if (normalizeItemCategory(linked?.category) === ITEM_CATEGORY_SUEDE) return true
  const mat = String(formModel.material_name || '').trim().toLowerCase()
  return /\b(suede|suide)\b/.test(mat)
})

function isSuedeMaterialContext() {
  return isSuedeMaterial.value
}

/** Material Suede tidak memakai backing. */
const showBackingField = computed(() => !isSuedeMaterial.value)

function clearBackingForSuede() {
  if (!isSuedeMaterial.value) return
  formModel.backing = ''
  autoFieldMeta.backing = false
}

watch(isSuedeMaterial, (suede) => {
  if (suede) clearBackingForSuede()
})

const wizardColorSwatchGroupTitle = computed(() =>
  isSuedeMaterialContext()
    ? t('pages.po.wizardGroupColorWindow')
    : t('pages.po.wizardGroupColorStandard'),
)

const wizardColorSwatchGroupSub = computed(() =>
  isSuedeMaterialContext()
    ? t('pages.po.colorWindowPickerLabel')
    : t('pages.po.swatchPickerLabel'),
)

function swatchDimensionKey() {
  return [formModel.material_name, formModel.color, formModel.emboss]
    .map((x) => String(x || '').trim().toLowerCase())
    .join('|')
}

function autoApplyColorSwatchFromDimensions() {
  const source = colorStandardSource.value
  if (source && source !== COLOR_STANDARD_SOURCE.SWATCH) return

  const material = String(formModel.material_name || '').trim()
  const color = String(formModel.color || '').trim()
  const emboss = String(formModel.emboss || '').trim()
  if (!material || !color || !emboss) return

  const dimKey = swatchDimensionKey()
  if (dimKey === lastAutoSwatchDimensionKey) return

  const recipe = pickBestSwatchRecipe(colorSwatchOptions.value, { material, color, emboss })
  if (!recipe) return
  const applied = applySwatchRecipeOption(recipe, {
    formModel,
    autoFieldMeta,
    materialFieldOverride,
    selectedSwatchId,
  })
  if (!applied) return
  lastAutoSwatchDimensionKey = dimKey
  colorStandardSource.value = COLOR_STANDARD_SOURCE.SWATCH
  selectedCsiId.value = null
  swatchFieldsManualEdit.value = false
  swatchPickerOpen.value = false
}

function reapplySelectedSwatchRecipe({ silent = false } = {}) {
  const picked = selectedSwatchRecipe.value
  if (!picked) return false
  const applied = applySwatchRecipeOption(picked, {
    formModel,
    autoFieldMeta,
    materialFieldOverride,
    selectedSwatchId,
  })
  if (!applied) {
    if (!silent) ElMessage.error(t('pages.po.swatchMismatch'))
    return false
  }
  swatchFieldsManualEdit.value = false
  if (!silent) ElMessage.success(t('pages.po.swatchResynced'))
  return true
}

function enableSwatchManualEdit() {
  swatchFieldsManualEdit.value = true
}

function openSwatchPicker() {
  swatchPickerOpen.value = true
}

function clearSwatchSelection() {
  // Hapus hanya nilai yang masih dari resep/auto; override manual user dipertahankan.
  if (autoFieldMeta.color_standard) {
    formModel.color_standard = ''
    autoFieldMeta.color_standard = false
  }
  if (autoFieldMeta.backing) {
    formModel.backing = ''
    autoFieldMeta.backing = false
  }
  if (autoFieldMeta.color_reference) {
    formModel.color_reference = ''
    autoFieldMeta.color_reference = false
  }
  selectedSwatchId.value = null
  swatchFieldsManualEdit.value = false
  swatchPickerOpen.value = true
  lastAutoSwatchDimensionKey = swatchDimensionKey()
}

async function loadColorSwatchOptions() {
  colorSwatchLoading.value = true
  try {
    const { options, retriedWithoutMaterial } = await fetchColorSwatchOptionList({
      formModel,
      swatchAllMaterials: swatchAllMaterials.value,
      lookupColorSwatchRecipes,
      customers: customers.value,
      selectedCustomer: selectedCustomer.value,
    })
    colorSwatchOptions.value = options
    swatchRetriedWithoutMaterial.value = retriedWithoutMaterial
    autoApplyColorSwatchFromDimensions()
    if (!selectedSwatchId.value) {
      await autoApplyCsiFromColorField()
    }
  } catch {
    colorSwatchOptions.value = []
    swatchRetriedWithoutMaterial.value = false
  } finally {
    colorSwatchLoading.value = false
  }
}

async function applyColorSwatch(recipeId) {
  if (!recipeId) {
    clearSwatchSelection()
    return
  }
  const picked = colorSwatchOptions.value.find((x) => x.id === recipeId)
  if (picked) {
    const applied = applySwatchRecipeOption(picked, {
      formModel,
      autoFieldMeta,
      materialFieldOverride,
      selectedSwatchId,
    })
    if (!applied) {
      ElMessage.error(t('pages.po.swatchMismatch'))
      return
    }
    lastAutoSwatchDimensionKey = swatchDimensionKey()
    colorStandardSource.value = COLOR_STANDARD_SOURCE.SWATCH
    selectedCsiId.value = null
    swatchFieldsManualEdit.value = false
    swatchPickerOpen.value = false
    ElMessage.success(t('pages.po.swatchApplied'))
    return
  }
  try {
    const fill = await getColorSwatchPoFill(recipeId)
    lastAutoSwatchDimensionKey = swatchDimensionKey()
    applyColorSwatchFill(fill, {
      formModel,
      autoFieldMeta,
      materialFieldOverride,
      selectedSwatchId,
    })
    colorStandardSource.value = COLOR_STANDARD_SOURCE.SWATCH
    selectedCsiId.value = null
    swatchFieldsManualEdit.value = false
    swatchPickerOpen.value = false
    ElMessage.success(t('pages.po.swatchApplied'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
  }
}

function resetColorStandardSourceState() {
  colorStandardSource.value = ''
  selectedCsiId.value = null
  csiOptions.value = []
  selectedSwatchId.value = null
  swatchFieldsManualEdit.value = false
  swatchPickerOpen.value = false
  lastAutoSwatchDimensionKey = ''
}

async function loadCsiOptions(query = '') {
  const buyer = String(formModel.buyer || '').trim().toUpperCase()
  if (!buyer) {
    csiOptions.value = []
    return
  }
  csiLoading.value = true
  try {
    const page = await listCsiColorsPage({
      buyer_code: buyer,
      q: String(query || '').trim() || undefined,
      limit: 80,
      offset: 0,
    })
    csiOptions.value = page.items || []
  } catch {
    csiOptions.value = []
  } finally {
    csiLoading.value = false
  }
}

function searchCsiOptions(query) {
  void loadCsiOptions(query)
}

async function hydrateColorStandardFromLine(line) {
  const source = inferColorStandardSource(line)
  colorStandardSource.value = source
  selectedCsiId.value = null
  if (source === COLOR_STANDARD_SOURCE.CSI) {
    const q = extractColorCodeFromReference(line?.color_reference)
    await loadCsiOptions(q)
    const hit = matchCsiOption(csiOptions.value, line?.color_reference, q)
    selectedCsiId.value = hit?.id ?? null
    return
  }
  if (source === COLOR_STANDARD_SOURCE.SWATCH) {
    swatchPickerOpen.value = !line?.color_swatch_recipe_id
    lastAutoSwatchDimensionKey = swatchDimensionKey()
    return
  }
  if (source === COLOR_STANDARD_SOURCE.WAITING || source === COLOR_STANDARD_SOURCE.MANUAL) {
    lastAutoSwatchDimensionKey = swatchDimensionKey()
  }
}

async function autoApplyCsiFromColorField() {
  const source = colorStandardSource.value
  if (source && source !== COLOR_STANDARD_SOURCE.SWATCH && source !== COLOR_STANDARD_SOURCE.CSI) {
    return
  }
  if (selectedSwatchId.value) return
  const code =
    extractColorCodeFromReference(formModel.color) ||
    extractColorCodeFromReference(formModel.color_reference)
  if (!code) return
  await loadCsiOptions(code)
  const hit = matchCsiOption(csiOptions.value, formModel.color, code)
  if (!hit) return
  selectedCsiId.value = hit.id
  applyCsiColorToForm(hit, formModel, autoFieldMeta)
  colorStandardSource.value = COLOR_STANDARD_SOURCE.CSI
  lastAutoSwatchDimensionKey = swatchDimensionKey()
}

function applySelectedCsiColor(csiId) {
  if (!csiId) {
    selectedCsiId.value = null
    if (autoFieldMeta.color_reference) {
      formModel.color_reference = ''
      formModel.color_standard = ''
      autoFieldMeta.color_reference = false
      autoFieldMeta.color_standard = false
    }
    return
  }
  const row = csiOptions.value.find((x) => x.id === csiId)
  if (!row) return
  selectedCsiId.value = csiId
  selectedSwatchId.value = null
  lastAutoSwatchDimensionKey = swatchDimensionKey()
  applyCsiColorToForm(row, formModel, autoFieldMeta)
  ElMessage.success(t('pages.po.colorStandardCsiApplied'))
}

function onColorReferenceInput() {
  autoFieldMeta.color_reference = false
  const typed = String(formModel.color_reference || '').trim()
  if (!colorStandardSource.value && typed) {
    colorStandardSource.value = isWaitingColorRef(typed)
      ? COLOR_STANDARD_SOURCE.WAITING
      : COLOR_STANDARD_SOURCE.MANUAL
    lastAutoSwatchDimensionKey = swatchDimensionKey()
    return
  }
  if (colorStandardSource.value === COLOR_STANDARD_SOURCE.WAITING && !isWaitingColorRef(formModel.color_reference)) {
    colorStandardSource.value = COLOR_STANDARD_SOURCE.MANUAL
  }
}

function onColorStandardSourceChange(next) {
  const source = String(next || '')
  colorStandardSource.value = source
  if (source === COLOR_STANDARD_SOURCE.SWATCH) {
    selectedCsiId.value = null
    lastAutoSwatchDimensionKey = ''
    swatchPickerOpen.value = !selectedSwatchId.value
    void loadColorSwatchOptions()
    return
  }
  selectedSwatchId.value = null
  swatchFieldsManualEdit.value = false
  swatchPickerOpen.value = false
  lastAutoSwatchDimensionKey = swatchDimensionKey()
  if (source === COLOR_STANDARD_SOURCE.CSI) {
    if (isWaitingColorRef(formModel.color_reference)) {
      formModel.color_reference = ''
      formModel.color_standard = ''
      autoFieldMeta.color_reference = false
      autoFieldMeta.color_standard = false
    }
    void loadCsiOptions(extractColorCodeFromReference(formModel.color_reference))
    return
  }
  selectedCsiId.value = null
  if (source === COLOR_STANDARD_SOURCE.WAITING) {
    applyWaitingCsToForm(formModel, autoFieldMeta)
    return
  }
  if (source === COLOR_STANDARD_SOURCE.MANUAL) {
    autoFieldMeta.color_reference = false
    autoFieldMeta.color_standard = false
  }
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

function canInferMaterialGroupForLot() {
  const mn = String(formModel.material_name || '').trim().toLowerCase()
  const vt = String(formModel.vir_softness_type || '').trim().toLowerCase()
  if (formModel.master_item_id) return true
  if (formModel.item_category) return true
  if (vt.includes('pu')) return true
  if (mn.includes('pu') || mn.includes('suede') || mn.includes('suide')) return true
  return false
}

async function onItemCategoryChange() {
  const keep = formModel.item_category || ITEM_CATEGORY_PU
  resetCurrentLineForm()
  formModel.item_category = keep
  await refreshMaterialDimensionOptions()
}

function pauseLotAutoBriefly(ms = 900) {
  skipLotAutoUntil = Date.now() + ms
}

function scheduleAutoLotGenerate() {
  if (Date.now() < skipLotAutoUntil) return
  if (!String(formModel.material_name || '').trim()) return
  if (!String(formModel.factory_code || '').trim()) return
  if (!canInferMaterialGroupForLot()) return
  clearTimeout(lotAutoTimer)
  lotAutoTimer = setTimeout(() => {
    void autoGenerateLotFromMaterial({ showSuccess: false, showError: false })
  }, 380)
}

async function autoGenerateLotFromMaterial({ showSuccess = false, showError = false } = {}) {
  if (!String(formModel.factory_code || '').trim()) {
    if (showError) ElMessage.warning(t('pages.po.factoryRequiredForLot'))
    return false
  }
  if (!String(formModel.material_name || '').trim()) return false
  if (!canInferMaterialGroupForLot()) {
    if (showError) {
      ElMessage.warning(t('pages.po.materialRequiredForLot'))
    }
    return false
  }
  const seq = ++lotAutoSeq
  lotGenerateLoading.value = true
  try {
    const r = await generateLotPreview({
      po_category: formModel.po_category,
      factory_code: String(formModel.factory_code || '').trim(),
      master_item_id: formModel.master_item_id || undefined,
      material_name: formModel.material_name || undefined,
      vir_softness_type: formModel.vir_softness_type || undefined,
    })
    if (seq !== lotAutoSeq) return false
    const reserved = collectReservedLots(draftLines.value, {
      excludeIndex: editingDraftLineIndex.value,
    })
    formModel.thi_line_ref = nextLotAfterReserved(r.lot_number || '', reserved)
    lotAutoFromMaterial.value = true
    if (showSuccess) ElMessage.success('Lot draft berhasil digenerate.')
    return true
  } catch (e) {
    if (seq !== lotAutoSeq) return false
    if (showError) ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
    return false
  } finally {
    if (seq === lotAutoSeq) lotGenerateLoading.value = false
  }
}

async function generateLotNumber(forceDetailId = null) {
  const target = forceDetailId
    ? draftLines.value.find((d) => d && d.id === forceDetailId)
    : (editingDraftLineIndex.value >= 0 ? draftLines.value[editingDraftLineIndex.value] : null)
  if (target?.line_locked) {
    ElMessage.warning(target.line_lock_reason || t('pages.po.lineLockedHint'))
    return
  }
  const poId = editingPoId.value
  const isPersist = Boolean(poId && forceDetailId)
  if (!String(formModel.factory_code || '').trim()) {
    ElMessage.warning(t('pages.po.factoryRequiredForLot'))
    return
  }
  const loadingFlag = isPersist ? saving : lotGenerateLoading
  loadingFlag.value = true
  try {
    if (isPersist) {
      await updatePo(poId, { factory_code: String(formModel.factory_code || '').trim() || null })
      const updated = await generatePoDetailLot(forceDetailId)
      if (Array.isArray(draftLines.value) && draftLines.value.length) {
        const i = draftLines.value.findIndex((d) => d && d.id === forceDetailId)
        if (i >= 0) draftLines.value[i].thi_line_ref = updated.thi_line_ref || undefined
      }
      if (editingDetailIds.value?.[0] === forceDetailId) {
        formModel.thi_line_ref = updated.thi_line_ref || ''
        lotAutoFromMaterial.value = true
      }
      ElMessage.success('Lot berhasil digenerate.')
      return
    }

    const ok = await autoGenerateLotFromMaterial({ showSuccess: true, showError: true })
    if (ok) lotAutoFromMaterial.value = true
  } finally {
    loadingFlag.value = false
  }
}

function applyReferenceDefaults(forceFields = []) {
  if (formModel.po_category === 'subcont') return
  applyReferenceDefaultsFromMaster(formModel, masterItems.value, autoFieldMeta, forceFields)
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
  if (currentLineLocked.value) return true
  if (formModel.po_category === 'subcont') {
    if (!formModel.master_item_id) return false
    if (!['material_name', 'thickness_text', 'color'].includes(field)) return false
    const item = masterItems.value.find((x) => x.id === formModel.master_item_id)
    if (!item) return false
    const masterVal =
      field === 'material_name'
        ? item.material_name
        : field === 'thickness_text'
          ? item.thickness_range || (item.thickness_mm != null ? String(item.thickness_mm) : '')
          : item.color
    if (!String(masterVal || '').trim()) return false
    return !materialFieldOverride[field]
  }
  if (!formModel.master_item_id) return false
  // Artikel kosong di master: langsung bisa diisi tanpa klik Override.
  if (field === 'style_article') {
    const item = masterItems.value.find((x) => x.id === formModel.master_item_id)
    if (!item || !String(item.style_article || '').trim()) return false
  }
  return !materialFieldOverride[field]
}

function enableMaterialOverride(field) {
  if (!formModel.master_item_id) return
  materialFieldOverride[field] = true
  if (field === 'color_family') colorFamilyAutoMode.value = false
}

function resetMaterialFieldToMaster(field) {
  resetMaterialFieldToMasterValues(
    field,
    formModel,
    masterItems.value,
    materialFieldOverride,
    colorFamilyAutoMode,
  )
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

  if (field === 'factory_code') {
    const cust =
      selectedCustomer.value || customers.value.find((x) => x.id === formModel.customer_id) || null
    applyAutoFactoryCode(cust, { force: true })
    return
  }

  if (field === 'vir_softness_type') {
    formModel.vir_softness_type = ''
    autoFieldMeta.vir_softness_type = false
    applyVirSoftDefault()
    return
  }

  if (field === 'color_reference' || field === 'color_standard' || field === 'backing' || field === 'model') {
    if (formModel.master_item_id) {
      const item = masterItems.value.find((x) => x.id === formModel.master_item_id)
      if (item) {
        if (field === 'color_reference') {
          const colorCode = String(item.color_code || item.color_reference || '').trim()
          formModel.color_reference = colorCode
          autoFieldMeta.color_reference = Boolean(colorCode)
        }
        if (field === 'color_standard') {
          formModel.color_standard = item.color_standard || ''
          autoFieldMeta.color_standard = Boolean(item.color_standard)
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
    if (field === 'color_standard') formModel.color_standard = ''
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
    formModel.emboss,
    formModel.factory_code,
  ],
  () => {
    schedulePricePreview()
    applyReferenceDefaults()
  },
)

watch(
  () => formModel.color,
  (newColor) => {
    if (formModel.po_category === 'subcont') return
    if (!colorFamilyAutoMode.value) return
    formModel.color_family = inferColorFamilyFromColor(newColor)
  },
)

watch(
  () => [formModel.color_family, formModel.buyer, formModel.order_date],
  () => {
    loadFluorescentOptions()
  },
)

watch(
  () => [
    formModel.buyer,
    formModel.material_name,
    formModel.color,
    formModel.emboss,
    swatchAllMaterials.value,
  ],
  () => {
    const scopeKey = swatchScopeKey()
    const scopeChanged = scopeKey !== lastSwatchScopeKey
    lastSwatchScopeKey = scopeKey
    const source = colorStandardSource.value
    const allowAutoSwatch = !source || source === COLOR_STANDARD_SOURCE.SWATCH
    if (scopeChanged && allowAutoSwatch) {
      selectedSwatchId.value = null
      lastAutoSwatchDimensionKey = ''
      swatchFieldsManualEdit.value = false
      swatchPickerOpen.value = false
    }
    if (allowAutoSwatch) {
      void loadColorSwatchOptions()
    } else if (source === COLOR_STANDARD_SOURCE.CSI) {
      void autoApplyCsiFromColorField()
    }
  },
)

watch(
  () => formModel.buyer,
  () => {
    if (colorStandardSource.value !== COLOR_STANDARD_SOURCE.CSI) return
    selectedCsiId.value = null
    void loadCsiOptions('')
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
    if (newCategory === 'subcont') {
      void refreshMaterialDimensionOptions()
      const linked = masterItems.value.find((x) => x.id === formModel.master_item_id)
      if (linked && String(linked.category || '').trim().toLowerCase() !== 'subkon') {
        clearLinkedMasterItem()
        subkonItemCodePicker.value = ''
      }
    } else {
      subkonItemCodePicker.value = ''
      void refreshMaterialDimensionOptions()
    }
  },
)

let poCustomerRefCheckTimer = null

async function validatePoCustomerRefLive() {
  const ref = String(formModel.po_customer_ref || '').trim()
  const cid = formModel.customer_id
  if (!ref || !cid) {
    formErrors.po_customer_ref = ''
    return true
  }
  try {
    const r = await checkPoCustomerRef({
      customer_id: cid,
      po_customer_ref: ref,
      exclude_po_id: isEditMode.value ? editingPoId.value : undefined,
    })
    if (r?.exists) {
      formErrors.po_customer_ref = t('pages.po.poCustomerRefDuplicate', {
        ref,
        poNumber: r.po_number || r.po_id,
      })
      return false
    }
    formErrors.po_customer_ref = ''
    return true
  } catch {
    formErrors.po_customer_ref = ''
    return true
  }
}

watch(
  () => [formModel.po_customer_ref, formModel.customer_id, isEditMode.value, editingPoId.value],
  () => {
    if (poCustomerRefCheckTimer) clearTimeout(poCustomerRefCheckTimer)
    poCustomerRefCheckTimer = setTimeout(() => {
      void validatePoCustomerRefLive()
    }, 400)
  },
)

function resetForm() {
  formModel.po_number = ''
  formModel.customer_id = null
  formModel.brand_id = null
  formModel.po_category = 'production'
  formModel.item_category = ITEM_CATEGORY_PU
  formModel.factory_code = ''
  autoFieldMeta.factory_code = false
  formModel.order_date = localTodayIsoDate()
  formModel.buyer = ''
  formModel.etd = ''
  formModel.po_customer_ref = ''
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
  formModel.color_standard = ''
  formModel.backing = ''
  formModel.quantity_order = ''
  formModel.style_article = ''
  formModel.model = ''
  formModel.detail_remark = ''
  formModel.thi_line_ref = ''
  formModel.unit_price_input = null
  formModel.autoPricingEnabled = true
  formModel.is_special_price = false
  formModel.discount_type = 'percent'
  formModel.discount_value = 0
  autoFieldMeta.buyer = false
  autoFieldMeta.factory_code = false
  autoFieldMeta.vir_softness_type = false
  autoFieldMeta.softness = false
  autoFieldMeta.color_reference = false
  autoFieldMeta.color_standard = false
  autoFieldMeta.backing = false
  autoFieldMeta.model = false
  editingDetailIds.value = []
  draftLines.value = []
  editingDraftLineIndex.value = -1
  draftRiskOnly.value = false
  brandLockedCustomerId.value = null
  selectedCustomer.value = null
  previewResolvedUnitPrice.value = null
  fluorescentColorOptions.value = []
  ambiguousMasterVisible.value = false
  ambiguousMasterCandidates.value = []
  selectedAmbiguousMasterId.value = null
  lastResolveHadNoMaster.value = false
  skipMasterResolve.value = false
  loadedDetailMasterSnapshot.value = null
  subkonItemCodePicker.value = ''
  masterItemCodePicker.value = ''
  thicknessDimensionOptions.value = []
  colorDimensionOptions.value = []
  embossDimensionOptions.value = []
  itemCodeDimensionOptions.value = []
  colorFamilyAutoMode.value = true
  lotAutoFromMaterial.value = false
  resetColorStandardSourceState()
  colorSwatchOptions.value = []
  resetMaterialFieldOverride()
  formErrors.customer_id = ''
  formErrors.brand_id = ''
  formErrors.material_name = ''
  formErrors.quantity_order = ''
  formErrors.po_customer_ref = ''
  savedHeaderOrderDate.value = ''
  clearEtdScheduleRows()
}

function getPoDraftPayload() {
  return buildPoDraftPayload(formModel, etdScheduleRows.value, draftLines.value)
}

function savePoDraftToLocal() {
  savePoDraftLocalStorage(getPoDraftPayload())
}

function clearPoDraftLocal() {
  clearPoDraftLocalStorage()
}

function applyPoDraft(data) {
  applyPoDraftData(data, { formModel, autoFieldMeta, etdScheduleRows, draftLines })
  if (!formModel.order_date) {
    formModel.order_date = localTodayIsoDate()
  }
  colorStandardSource.value = inferColorStandardSource({
    color_swatch_recipe_id: selectedSwatchId.value,
    color_reference: formModel.color_reference,
    color_standard: formModel.color_standard,
  })
}

async function restorePoDraftIfAny() {
  const raw = readPoDraftRaw()
  if (!raw) return
  try {
    await ElMessageBox.confirm(
      'Ditemukan draft input SO. Lanjutkan dari draft terakhir?',
      'Lanjutkan Draft SO',
      {
        type: 'info',
        confirmButtonText: 'Lanjutkan Draft',
        cancelButtonText: 'Mulai Baru',
      },
    )
    const parsed = JSON.parse(raw)
    applyPoDraft(parsed)
    if (formModel.customer_id) await onCustomerChange()
    if (formModel.brand_id) await onBrandChange(formModel.brand_id, { fromCustomerChange: true })
    ElMessage.success('Draft SO berhasil dimuat.')
    formModel.item_category = inferItemCategory(formModel, masterItems.value)
    await refreshMaterialDimensionOptions()
    await refreshThicknessOptionsFromApi()
    await refreshColorOptionsFromApi()
    lastResolveHadNoMaster.value = false
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
      'Simpan draft SO sebelum menutup dialog?',
      'Konfirmasi Tutup',
      {
        type: 'warning',
        distinguishCancelAndClose: true,
        confirmButtonText: 'Simpan Draft',
        cancelButtonText: 'Tutup Tanpa Simpan',
      },
    )
    savePoDraftToLocal()
    ElMessage.success('Draft SO disimpan. Kamu bisa lanjutkan nanti.')
    done()
  } catch {
    clearPoDraftLocal()
    done()
  }
}

function saveDraftAndClose() {
  savePoDraftToLocal()
  ElMessage.success('Draft SO disimpan. Kamu bisa lanjutkan nanti.')
  formDialogVisible.value = false
}

async function refreshThicknessOptionsFromApi() {
  const m = String(formModel.material_name || '').trim()
  if (!m) {
    thicknessDimensionOptions.value = []
    return
  }
  try {
    const r = await listMasterItemDimensionValues('thicknesses', {
      material_name: m,
      category: masterDimensionCategoryParam(),
    })
    thicknessDimensionOptions.value = r.values || []
  } catch {
    thicknessDimensionOptions.value = []
  }
}

async function refreshEmbossOptionsFromApi() {
  const m = String(formModel.material_name || '').trim()
  const tt = String(formModel.thickness_text || '').trim()
  const co = String(formModel.color || '').trim()
  if (!m || !tt || !co) {
    embossDimensionOptions.value = []
    return
  }
  try {
    const r = await listMasterItemDimensionValues('embosses', {
      material_name: m,
      thickness_text: tt,
      color: co,
      category: masterDimensionCategoryParam(),
    })
    embossDimensionOptions.value = r.values || []
  } catch {
    embossDimensionOptions.value = []
  }
}

async function refreshItemCodeOptionsFromApi() {
  const m = String(formModel.material_name || '').trim()
  const tt = String(formModel.thickness_text || '').trim()
  const co = String(formModel.color || '').trim()
  const em = String(formModel.emboss || '').trim()
  if (!m || !tt || !co) {
    itemCodeDimensionOptions.value = []
    return
  }
  try {
    const r = await listMasterItemDimensionValues('item_codes', {
      material_name: m,
      thickness_text: tt,
      color: co,
      emboss: em || undefined,
      category: masterDimensionCategoryParam(),
    })
    itemCodeDimensionOptions.value = r.values || []
  } catch {
    itemCodeDimensionOptions.value = []
  }
}

function applyPickedMasterItem(item) {
  if (!item) return
  upsertMasterItemInCache(item)
  skipMasterResolve.value = true
  resetMaterialFieldOverride()
  colorFamilyAutoMode.value = true
  formModel.master_item_id = item.id
  masterItemCodePicker.value = item.item_code || ''
  hydrateFormFromMasterItemRow(item, { syncDimensions: false })
  if (!colorStandardSource.value) {
    const inferredSource = inferColorStandardSource({
      color_swatch_recipe_id: selectedSwatchId.value,
      color_reference: formModel.color_reference,
      color_standard: formModel.color_standard,
    })
    if (inferredSource) colorStandardSource.value = inferredSource
  }
  lastResolveHadNoMaster.value = false
  scheduleAutoLotGenerate()
}

async function refreshColorOptionsFromApi() {
  const m = String(formModel.material_name || '').trim()
  const tt = String(formModel.thickness_text || '').trim()
  if (!m) {
    colorDimensionOptions.value = []
    return
  }
  if (isSubkonPo.value && !tt) {
    const norm = m.trim().toLowerCase()
    const colors = [
      ...new Set(
        subkonMasterItems.value
          .filter((x) => String(x.material_name || '').trim().toLowerCase() === norm)
          .map((x) => String(x.color || '').trim())
          .filter(Boolean),
      ),
    ].sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }))
    colorDimensionOptions.value = colors
    return
  }
  if (!tt) {
    colorDimensionOptions.value = []
    return
  }
  try {
    const r = await listMasterItemDimensionValues('colors', {
      material_name: m,
      thickness_text: tt,
      category: masterDimensionCategoryParam(),
    })
    colorDimensionOptions.value = r.values || []
  } catch {
    colorDimensionOptions.value = []
  }
}

function onPickedSubkonItemCode(code) {
  const picked = String(code || '').trim()
  if (!picked) {
    subkonItemCodePicker.value = ''
    clearLinkedMasterItem()
    return
  }
  const item = subkonMasterItems.value.find((x) => x.item_code === picked)
  if (!item) return
  subkonItemCodePicker.value = picked
  skipMasterResolve.value = true
  resetMaterialFieldOverride()
  formModel.master_item_id = item.id
  formModel.material_name = item.material_name || ''
  formModel.thickness_text =
    item.thickness_range || (item.thickness_mm != null ? String(item.thickness_mm) : '')
  formModel.color = item.color || ''
  formModel.thi_line_ref = ''
  lotAutoFromMaterial.value = false
  void refreshThicknessOptionsFromApi()
  void refreshColorOptionsFromApi()
  scheduleAutoLotGenerate()
}

function clearDownstreamMasterPick({ clearThickness = false, clearColor = false, clearEmboss = false } = {}) {
  if (clearThickness) formModel.thickness_text = ''
  if (clearColor) formModel.color = ''
  if (clearEmboss) formModel.emboss = ''
  formModel.master_item_id = null
  subkonItemCodePicker.value = ''
  masterItemCodePicker.value = ''
  skipMasterResolve.value = false
  lastResolveHadNoMaster.value = false
  if (clearThickness) thicknessDimensionOptions.value = []
  if (clearColor) colorDimensionOptions.value = []
  if (clearEmboss) {
    embossDimensionOptions.value = []
    itemCodeDimensionOptions.value = []
  }
}

async function onPickedMaterialDimension() {
  clearDownstreamMasterPick({ clearThickness: true, clearColor: true, clearEmboss: true })
  formModel.thi_line_ref = ''
  lotAutoFromMaterial.value = false
  const m = String(formModel.material_name || '').trim()
  if (m) {
    await refreshThicknessOptionsFromApi()
    if (isSubkonPo.value) await refreshColorOptionsFromApi()
    scheduleAutoLotGenerate()
  }
}

async function onPickedThicknessDimension() {
  clearDownstreamMasterPick({ clearColor: true, clearEmboss: true })
  const m = String(formModel.material_name || '').trim()
  const tt = String(formModel.thickness_text || '').trim()
  if (m && tt) await refreshColorOptionsFromApi()
}

async function onPickedColorDimension() {
  clearDownstreamMasterPick({ clearEmboss: true })
  const m = String(formModel.material_name || '').trim()
  const tt = String(formModel.thickness_text || '').trim()
  const co = String(formModel.color || '').trim()
  if (!m || !tt || !co) return
  await refreshEmbossOptionsFromApi()
  if (embossDimensionOptions.value.length === 1) {
    formModel.emboss = embossDimensionOptions.value[0]
    await onPickedEmbossDimension()
  }
}

async function onPickedEmbossDimension() {
  formModel.master_item_id = null
  masterItemCodePicker.value = ''
  itemCodeDimensionOptions.value = []
  skipMasterResolve.value = false
  lastResolveHadNoMaster.value = false
  const em = String(formModel.emboss || '').trim()
  if (!em) return
  await refreshItemCodeOptionsFromApi()
  if (itemCodeDimensionOptions.value.length === 1) {
    masterItemCodePicker.value = itemCodeDimensionOptions.value[0]
    await onPickedMasterItemCode(masterItemCodePicker.value)
  }
}

async function onPickedMasterItemCode(code) {
  const picked = String(code || '').trim()
  if (!picked) {
    masterItemCodePicker.value = ''
    formModel.master_item_id = null
    return
  }
  masterItemCodePicker.value = picked
  const cached = masterItems.value.find((x) => String(x.item_code || '').trim() === picked)
  if (cached) {
    applyPickedMasterItem(cached)
    return
  }
  skipMasterResolve.value = false
  await resolveMasterFromDimensionsTriple()
  const linked = masterItems.value.find((x) => x.id === formModel.master_item_id)
  if (linked?.item_code) masterItemCodePicker.value = linked.item_code
}

function hydrateFormFromMasterItemRow(item, { syncDimensions = true } = {}) {
  if (syncDimensions) resetMaterialFieldOverride()
  applyMasterItemToForm(item, {
    formModel,
    autoFieldMeta,
    previewResolvedUnitPrice: previewResolvedUnitPrice.value,
    colorFamilyAutoMode,
    syncDimensions,
    subkonMode: formModel.po_category === 'subcont',
  })
  const cat = normalizeItemCategory(item.category)
  if (cat === ITEM_CATEGORY_PU || cat === ITEM_CATEGORY_SUEDE) formModel.item_category = cat
  clearBackingForSuede()
}

function clearLinkedMasterItem() {
  formModel.master_item_id = null
  subkonItemCodePicker.value = ''
  masterItemCodePicker.value = ''
  resetMaterialFieldOverride()
  skipMasterResolve.value = false
  lastResolveHadNoMaster.value = false
}

let masterResolveTimer = null
let masterResolveSeq = 0

async function resolveMasterFromDimensionsTriple() {
  if (ambiguousMasterVisible.value || skipMasterResolve.value) return
  const mn = String(formModel.material_name || '').trim()
  const tt = String(formModel.thickness_text || '').trim()
  const co = String(formModel.color || '').trim()
  const em = String(formModel.emboss || '').trim()
  const curSnap = detailMasterSnapshot(formModel)
  if (
    isEditMode.value &&
    editingPoId.value &&
    loadedDetailMasterSnapshot.value != null &&
    curSnap === loadedDetailMasterSnapshot.value
  ) {
    return
  }
  const seq = ++masterResolveSeq
  if (!mn || !tt || !co || !em) {
    lastResolveHadNoMaster.value = false
    if (!em) formModel.master_item_id = null
    return
  }
  masterResolveLoading.value = true
  try {
    const res = await resolveMasterItemByDimensions({
      material_name: mn,
      thickness_text: tt,
      color: co,
      emboss: em,
      category: masterDimensionCategoryParam(),
    })
    if (seq !== masterResolveSeq) return
    lastResolveHadNoMaster.value = res.status === 'none'
    if (res.status === 'single' && res.item) {
      applyPickedMasterItem(res.item)
    } else if (res.status === 'ambiguous' && (res.candidates || []).length) {
      formModel.master_item_id = null
      skipMasterResolve.value = true
      ambiguousMasterCandidates.value = res.candidates
      itemCodeDimensionOptions.value = [
        ...new Set(res.candidates.map((c) => String(c.item_code || '').trim()).filter(Boolean)),
      ]
      selectedAmbiguousMasterId.value = res.candidates[0]?.id ?? null
      if (masterItemCodePicker.value) {
        const picked = res.candidates.find(
          (c) => String(c.item_code || '').trim() === masterItemCodePicker.value,
        )
        if (picked) {
          applyPickedMasterItem(picked)
        } else {
          ambiguousMasterVisible.value = true
        }
      } else {
        ambiguousMasterVisible.value = true
      }
    } else {
      formModel.master_item_id = null
    }
  } catch {
    if (seq !== masterResolveSeq) return
    lastResolveHadNoMaster.value = true
    formModel.master_item_id = null
  } finally {
    if (seq === masterResolveSeq) masterResolveLoading.value = false
  }
}

function confirmAmbiguousMasterPick() {
  const id = selectedAmbiguousMasterId.value
  const c = ambiguousMasterCandidates.value.find((x) => x.id === id)
  if (!c) return
  ambiguousMasterVisible.value = false
  applyPickedMasterItem(c)
}

watch(
  () => [
    formModel.factory_code,
    formModel.po_category,
    formModel.master_item_id,
    formModel.vir_softness_type,
  ],
  () => scheduleAutoLotGenerate(),
)

watch(
  () => [formModel.material_name, formModel.thickness_text, formModel.color, formModel.emboss],
  () => {
    if (isSubkonPo.value && subkonItemCodePicker.value) return
    if (masterItemCodePicker.value && formModel.master_item_id) return
    skipMasterResolve.value = false
    clearTimeout(masterResolveTimer)
    masterResolveTimer = setTimeout(() => {
      void resolveMasterFromDimensionsTriple()
    }, 420)
  },
)

watch(
  () => formModel.master_item_id,
  (id) => {
    if (!isSubkonPo.value || !id) return
    const item = masterItems.value.find((x) => x.id === id)
    if (item?.item_code && String(item.category || '').trim().toLowerCase() === 'subkon') {
      subkonItemCodePicker.value = item.item_code
    }
  },
)

watch(ambiguousMasterVisible, (open) => {
  if (!open && !formModel.master_item_id && materialThicknessColorComplete.value) {
    skipMasterResolve.value = true
  }
})

const openCreateDialog = async () => {
  isEditMode.value = false
  editingPoId.value = null
  resetForm()
  brandLockedCustomerId.value = null
  currentStep.value = 0
  formDialogVisible.value = true
  pauseLotAutoBriefly()
  void refreshNextPoNumberPreview()
  await ensureMasterItemsLoaded()
  await restorePoDraftIfAny()
}

async function buildCurrentDetailBody() {
  clearBackingForSuede()
  const body = buildDetailBodyCore(formModel, etdScheduleRows.value, selectedSwatchId.value)
  if (isSuedeMaterial.value) body.backing = undefined
  return appendDetailUnitPrice(body, formModel, {
    resolveBuyerUnitPrice,
    previewResolvedUnitPrice: previewResolvedUnitPrice.value,
  })
}

function handleEnterKey(e) {
  if (e.ctrlKey || e.metaKey) {
    pushCurrentLine(false)
  }
}

async function pushCurrentLine(copyCurrent = false) {
  formErrors.material_name = ''
  formErrors.quantity_order = ''

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
      ElMessage.warning(t('pages.po.pricingKeyRequiredWarn'))
      return
    }
    if (!isThicknessPricingFormatValid(formModel.thickness_text)) {
      ElMessage.warning(t('pages.po.thicknessFormatWarn'))
      return
    }
    if (!isSelectedFluorescentColorValid()) {
      ElMessage.warning(t('pages.po.fluorescentColorRequired'))
      return
    }
    if (!ensureColorStandardReady()) return
  }

  const line = await buildCurrentDetailBody()
  line.item_category = formModel.item_category || inferItemCategory(formModel, masterItems.value)
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
    ElMessage.warning(t('pages.po.manualPriceRemarkRequired'))
    return
  }
  if (editingDraftLineIndex.value >= 0) {
    const idx = editingDraftLineIndex.value
    const prev = draftLines.value[idx] || {}
    draftLines.value[idx] = {
      ...prev,
      ...line,
      id: prev.id,
      thi_line_ref: line.thi_line_ref || prev.thi_line_ref,
      delivery_schedules: line.delivery_schedules || [],
    }
    editingDraftLineIndex.value = -1
    ElMessage.success(t('pages.po.draftLineSaved'))
  } else {
    const uid = `draft-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
    const added = { ...line, _uid: uid }
    draftLines.value.push(added)
    const notifyAdded = onDraftLineAdded.value
    if (typeof notifyAdded === 'function') {
      notifyAdded({ uid, label: String(line.material_name || '') })
    }
  }
  if (!copyCurrent) {
    resetCurrentLineForm()
  } else if (formModel.thi_line_ref) {
    formModel.thi_line_ref = nextLotAfterReserved(
      formModel.thi_line_ref,
      collectReservedLots(draftLines.value),
    )
    lotAutoFromMaterial.value = true
  } else {
    void autoGenerateLotFromMaterial({ showSuccess: false, showError: false })
  }
}

/** Tambah baris baru dari form, meskipun sedang mengedit baris draft. */
async function pushCurrentLineAsNew(copyCurrent = false) {
  editingDraftLineIndex.value = -1
  await pushCurrentLine(copyCurrent)
}

async function removeDraftLine(index) {
  const row = draftLines.value[index]
  if (!row) return
  if (row.line_locked) {
    ElMessage.warning(row.line_lock_reason || t('pages.po.lineLockedHint'))
    return
  }
  const material = String(row.material_name || '').trim() || '—'
  const color = String(row.color || '').trim() || '—'
  const qty = row.quantity_order != null && row.quantity_order !== '' ? row.quantity_order : '—'
  try {
    await ElMessageBox.confirm(
      t('pages.po.deleteLineConfirmDetail', { material, color, qty }),
      t('pages.po.deleteLineTitle'),
      { type: 'warning', confirmButtonText: t('common.delete'), cancelButtonText: t('common.cancel') },
    )
  } catch {
    return
  }
  draftLines.value.splice(index, 1)
  if (editingDraftLineIndex.value === index) {
    editingDraftLineIndex.value = -1
  } else if (editingDraftLineIndex.value > index) {
    editingDraftLineIndex.value -= 1
  }
}

const openEditDialog = async (row) => {
  const seq = ++editOpenSeq
  isEditMode.value = true
  editingPoId.value = row.id
  resetForm()
  savedHeaderOrderDate.value = row.order_date ? String(row.order_date).slice(0, 10) : ''
  formModel.po_number = row.po_number || ''
  formModel.customer_id = row.customer_id
  formModel.brand_id = row.brand_id ?? null
  formModel.po_category = normalizePoOrderCategory(row.po_category)
  formModel.order_date = row.order_date ? String(row.order_date).slice(0, 10) : ''
  formModel.buyer = row.buyer || ''
  formModel.etd = toIsoDate(row.etd) || ''
  formModel.po_customer_ref = row.po_customer_ref || ''
  formModel.billing_address = row.billing_address || ''
  formModel.delivery_address = row.delivery_address || ''
  formModel.status = row.status || 'draft'
  formModel.factory_code = row.factory_code || ''
  autoFieldMeta.factory_code = Boolean(row.factory_code)
  pauseLotAutoBriefly()
  schedulePricePreview()
  formDialogVisible.value = true
  formHydrating.value = true

  try {
    const [customer, details] = await Promise.all([
      formModel.customer_id ? getCustomer(formModel.customer_id).catch(() => null) : Promise.resolve(null),
      listPoDetails(row.id),
      onBrandChange(formModel.brand_id, { fromCustomerChange: true }),
      ensureMasterItemsLoaded(),
    ])
    if (seq !== editOpenSeq) return

    selectedCustomer.value = customer
    if (selectedCustomer.value) {
      applyAutoFactoryCode(selectedCustomer.value, { force: true })
    }

    draftLines.value = (details || []).map((d) => ({
      id: d.id,
      item_category: inferItemCategory(d, masterItems.value),
      master_item_id: d.master_item_id || undefined,
      material_name: d.material_name || undefined,
      thickness_text: d.thickness_text || undefined,
      color: d.color || undefined,
      color_family: d.color_family || undefined,
      emboss: d.emboss || undefined,
      vir_softness_type: d.vir_softness_type || undefined,
      softness: d.softness || undefined,
      color_reference: d.color_reference || undefined,
      color_standard: d.color_standard || undefined,
      backing: d.backing || undefined,
      quantity_order: d.quantity_order != null ? Number(d.quantity_order) : undefined,
      style_article: d.style_article || undefined,
      model: d.model || undefined,
      detail_remark: d.detail_remark || undefined,
      thi_line_ref: d.thi_line_ref || undefined,
      color_swatch_recipe_id: d.color_swatch_recipe_id || undefined,
      unit_price: d.unit_price != null ? Number(d.unit_price) : undefined,
      line_etd: d.line_etd ? String(d.line_etd).slice(0, 10) : undefined,
      delivery_schedules: [],
      line_locked: Boolean(d.line_locked),
      line_lock_reason: d.line_lock_reason || '',
      manual_override: false,
      material_master_override: false,
      material_master_matched: Boolean(d.master_item_id),
    }))
    editingDetailIds.value = (details || []).map((d) => d.id)
    draftLines.value = draftLines.value.map((line) => ({
      ...line,
      item_category: inferItemCategory(line, masterItems.value),
    }))

    const d0 = details?.[0]
    loadedDetailMasterSnapshot.value = d0
      ? detailMasterSnapshot({
          material_name: d0.material_name,
          thickness_text: d0.thickness_text,
          color: d0.color,
          emboss: d0.emboss,
          master_item_id: d0.master_item_id,
        })
      : null

    // Jangan auto-edit baris pertama: form kosong agar tombol «Tambah» tersedia.
    editingDraftLineIndex.value = -1
    resetCurrentLineForm()
    lastResolveHadNoMaster.value = false

    formHydrating.value = false
    await Promise.all([
      refreshMaterialDimensionOptions(),
      refreshThicknessOptionsFromApi(),
      refreshColorOptionsFromApi(),
      refreshEmbossOptionsFromApi(),
      refreshItemCodeOptionsFromApi(),
    ])
  } catch {
    if (seq !== editOpenSeq) return
    editingDetailIds.value = []
    draftLines.value = []
    loadedDetailMasterSnapshot.value = null
  } finally {
    if (seq === editOpenSeq) formHydrating.value = false
  }
}

const submitForm = async () => {
  if (!formModel.customer_id) {
    ElMessage.warning(t('pages.po.pickCustomerWarning'))
    return
  }
  const poRefOk = await validatePoCustomerRefLive()
  if (!poRefOk) {
    ElMessage.warning(formErrors.po_customer_ref || t('pages.po.poCustomerRefDuplicate', { ref: formModel.po_customer_ref, poNumber: '?' }))
    return
  }
  if (!isSelectedFluorescentColorValid()) {
    ElMessage.warning(t('pages.po.fluorescentColorRequired'))
    return
  }
  saving.value = true
  try {
    if (editingDraftLineIndex.value >= 0) {
      if (!ensureColorStandardReady()) {
        saving.value = false
        return
      }
      await syncCurrentFormToDraftLine()
    }
    const bodiesFinal = draftLines.value.length ? draftLines.value : [await buildCurrentDetailBody()]
    if (!isSubkonPo.value) {
      const missingCs = bodiesFinal.find((b) => !lineHasColorStandard(b))
      if (missingCs) {
        ElMessage.warning(t('pages.po.colorStandardRequired'))
        saving.value = false
        return
      }
    }
    await validateFluorescentLinesOrThrow(bodiesFinal)
    const mismatchLines = bodiesFinal.filter((b) => lineHasScheduleMismatch(b))
    if (mismatchLines.length) {
      ElMessage.warning(t('pages.po.scheduleMismatchWarn'))
    }

    const header = {
      po_number: isEditMode.value ? formModel.po_number?.trim() || undefined : undefined,
      customer_id: formModel.customer_id,
      brand_id: formModel.brand_id || undefined,
      buyer: formModel.buyer || undefined,
      po_category: formModel.po_category,
      factory_code: formModel.factory_code?.trim() || undefined,
      etd: toIsoDate(formModel.etd) || undefined,
      po_customer_ref: formModel.po_customer_ref?.trim() || undefined,
      billing_address: formModel.billing_address?.trim() || undefined,
      delivery_address: formModel.delivery_address?.trim() || undefined,
      status: formModel.status,
    }
    const soMaterialGroup = inferSoMaterialGroup(formModel, bodiesFinal)
    if (soMaterialGroup) header.material_group = soMaterialGroup
    if (!orderDateLocked.value) {
      header.order_date = toIsoDate(formModel.order_date) || undefined
    }

    if (isEditMode.value && editingPoId.value) {
      await updatePo(editingPoId.value, header)
      const keepIds = []
      for (let i = 0; i < bodiesFinal.length; i += 1) {
        const rowBody = { ...sanitizeNewDetailBody(bodiesFinal[i]) }
        // Jangan tulis/hapus delivery_schedules dari wizard — rencana kirim hanya dari Outstanding.
        delete rowBody.delivery_schedules
        const existingId = bodiesFinal[i].id || null
        if (existingId) {
          await updatePoDetail(existingId, detailPayloadForUpdate(rowBody))
          keepIds.push(existingId)
        } else {
          const createdDetail = await addPoDetail(editingPoId.value, rowBody)
          keepIds.push(createdDetail.id)
        }
      }
      const staleIds = editingDetailIds.value.filter((id) => !keepIds.includes(id))
      for (const staleId of staleIds) {
        await deletePoDetail(staleId)
      }
      ElMessage.success(t('pages.customers.saved'))
      if ((header.status || formModel.status) === 'draft' && bodiesFinal.length) {
        await offerConfirmAfterSave(editingPoId.value)
      }
    } else {
      const created = await createPo(header)
      let savedLines = 0
      try {
        for (const raw of bodiesFinal) {
          const rowBody = { ...sanitizeNewDetailBody(raw) }
          delete rowBody.delivery_schedules
          await addPoDetail(created.id, rowBody)
          savedLines += 1
        }
      } catch (e) {
        // Header sudah tersimpan; pindah ke mode edit supaya percobaan ulang
        // menambah baris ke SO yang sama, bukan membuat SO kedua.
        isEditMode.value = true
        editingPoId.value = created.id
        editingDetailIds.value = []
        formModel.po_number = created.po_number || formModel.po_number
        draftLines.value = bodiesFinal.slice(savedLines)
        clearPoDraftLocal()
        await load()
        ElMessage.error(
          t('pages.po.partialLinesSaved', {
            poNumber: created.po_number || created.id,
            saved: savedLines,
            total: bodiesFinal.length,
            reason: parseApiErrorMessage(e, t('common.errorGeneric')),
          }),
        )
        return
      }
      ElMessage.success(t('pages.customers.saved'))
      await offerConfirmAfterSave(created.id)
    }
    clearPoDraftLocal()
    formDialogVisible.value = false
    await load()
  } catch (e) {
    ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
  } finally {
    saving.value = false
  }
}

async function offerConfirmAfterSave(poId) {
  if (!poId) return
  const missingLot = (draftLines.value || []).filter((line) => {
    const lot = String(line?.thi_line_ref || line?.system_reference || '').trim()
    return !lot
  })
  if (missingLot.length) {
    ElMessage.warning(t('pages.po.confirmRequiresLot'))
    return
  }
  try {
    await ElMessageBox.confirm(t('pages.po.confirmPoAfterSave'), t('pages.po.confirmDraftAction'), {
      type: 'warning',
      confirmButtonText: t('common.yes'),
      cancelButtonText: t('common.no'),
      distinguishCancelAndClose: true,
    })
  } catch {
    return
  }
  try {
    const confirmed = await updatePo(poId, { status: 'confirmed' })
    ElMessage.success(t('pages.po.statusChanged'))
    await maybeRetryMrpSyncAfterConfirm(poId, confirmed)
  } catch (e) {
    ElMessage.error(parseApiErrorMessage(e, t('common.errorGeneric')))
  }
}

async function maybeRetryMrpSyncAfterConfirm(poId, confirmed) {
  const sync = confirmed?.mrp_sync
  if (!sync || sync.ok !== false) return
  const detail = (sync.error || t('pages.po.mrpSyncError')).toString().slice(0, 280)
  try {
    await ElMessageBox.confirm(
      t('pages.po.mrpSyncFailedAfterConfirm', { detail }),
      t('pages.po.mrpSyncError'),
      {
        type: 'error',
        confirmButtonText: t('pages.po.mrpSyncRetry'),
        cancelButtonText: t('common.cancel'),
        distinguishCancelAndClose: true,
      },
    )
  } catch {
    return
  }
  try {
    await mrpSyncPo({ po_id: poId })
    ElMessage.success(t('pages.po.mrpSyncRetryOk'))
  } catch (e) {
    ElMessage.error(parseApiErrorMessage(e, t('pages.po.mrpSyncError')))
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

async function onCopyItemCustomerChange(id) {
  copyItemCustomerId.value = id ?? null
  await loadCopyItemSourcePos()
}

function onCopyItemSelectionChange(selection) {
  copyItemSelected.value = selection
}

function addCopiedItems() {
  const newLines = copyItemSelected.value.map(d => ({
    item_category: inferItemCategory(d, masterItems.value),
    master_item_id: d.master_item_id,
    material_name: d.material_name,
    thickness_text: d.thickness_text,
    color: d.color,
    color_family: d.color_family,
    emboss: d.emboss,
    vir_softness_type: d.vir_softness_type,
    softness: d.softness,
    color_reference: d.color_reference,
    color_standard: d.color_standard,
    color_swatch_recipe_id: d.color_swatch_recipe_id,
    backing: d.backing,
    quantity_order: d.quantity_order,
    style_article: d.style_article,
    model: d.model,
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
  providePoWizardContext({
    formDialogVisible,
    formHydrating,
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
    isSubkonPo,
    subkonItemCodePicker,
    subkonMasterItems,
    onPickedSubkonItemCode,
    orderDateLocked,
    brands,
    materialDimensionOptions,
    onPickedMaterialDimension,
    thicknessDimensionOptions,
    formatThicknessDisplay,
    onPickedThicknessDimension,
    isFluorescentFamily,
    poColorCascadeOptions,
    colorDimensionOptions,
    onPickedColorDimension,
    embossDimensionOptions,
    onPickedEmbossDimension,
    itemCodeDimensionOptions,
    masterItemCodePicker,
    onPickedMasterItemCode,
    enableMaterialOverride,
    isMaterialFieldLocked,
    currentLineLocked,
    materialFieldOverride,
    resetMaterialFieldToMaster,
    activeSeasonLabel,
    fluorescentColorOptions,
    selectedSwatchId,
    selectedSwatchRecipe,
    swatchFieldsLocked,
    showColorStandardBackingFields,
    showBackingField,
    isSuedeMaterial,
    swatchFieldsManualEdit,
    swatchPickerOpen,
    colorSwatchLoading,
    colorSwatchOptions,
    swatchOptionLabel,
    poFactoryKeyForSwatch,
    materialStepFillStep,
    swatchHelperMessage,
    wizardColorSwatchGroupTitle,
    wizardColorSwatchGroupSub,
    isColorStandardRequired,
    hasColorStandardReady,
    applyColorSwatch,
    enableSwatchManualEdit,
    reapplySelectedSwatchRecipe,
    openSwatchPicker,
    clearSwatchSelection,
    swatchAllMaterials,
    loadColorSwatchOptions,
    swatchRetriedWithoutMaterial,
    colorStandardSource,
    selectedCsiId,
    csiOptions,
    csiLoading,
    csiColorOptionLabel,
    searchCsiOptions,
    applySelectedCsiColor,
    onColorStandardSourceChange,
    onColorReferenceInput,
    masterResolveLoading,
    resolvedMasterItemLabel,
    clearLinkedMasterItem,
    lastResolveHadNoMaster,
    materialThicknessColorComplete,
    colorFamilyAutoMode,
    pricingKeyIncomplete,
    etdScheduleOpen,
    etdScheduleRows,
    clearEtdScheduleRows,
    copyEtdDateFromHeader,
    syncEtdQtyFromOrder,
    etdScheduleMismatch,
    draftLinesDisplay,
    draftLines,
    draftRiskOnly,
    draftRowClassName,
    pushCurrentLine,
    pushCurrentLineAsNew,
    onDraftLineAdded,
    editingDraftLineIndex,
    cancelEditDraftLine,
    copyDraftLine,
    openCopyItemDialog,
    colorFamilyLabel,
    materialQualityTooltip,
    materialQualityType,
    materialQualityLabel,
    materialGroupLabel,
    onItemCategoryChange,
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
    formHydrating,
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
