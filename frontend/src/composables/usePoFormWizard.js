import { computed, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { providePoWizardContext } from './poFormWizardContext.js'
import { usePoMarketingRevise } from './usePoMarketingRevise.js'
import { usePoStepCustomer, brandCustomerIds, inferSoMaterialGroup } from './usePoStepCustomer.js'
import { usePoStepLines } from './usePoStepLines.js'
import { usePoStepReview } from './usePoStepReview.js'
import {
  normalizeSchedulesFromApi,
  etdScheduleRowsToPayload,
  formatLineEtdScheduleDisplay,
  loadEtdScheduleRowsFromApi,
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
import { parseApiErrorMessage } from '../utils/poApi.js'
import { customerOptionLabel } from '../utils/poList.js'
import {
  inferColorFamilyFromColor,
  applyReferenceDefaults as applyReferenceDefaultsFromMaster,
  hydrateFormFromMasterItemRow as applyMasterItemToForm,
  resetMaterialFieldToMaster as resetMaterialFieldToMasterValues,
  isThicknessPricingFormatValid,
  formatThicknessDisplay,
  detailMasterSnapshot,
  resolveMaterialGroupLabel,
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
  checkPoCustomerRef,
  getCustomer,
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
const isBrandDisabled = computed(() => Boolean(formModel.customer_id))
const isBuyerDisabled = computed(() => Boolean(formModel.customer_id) || !formModel.brand_id || buyerCodesFiltered.value.length === 0)
const isPoCategoryDisabled = computed(() => !formModel.customer_id || !formModel.brand_id || !formModel.buyer)
const isSubkonPo = computed(() => formModel.po_category === 'subcont')
const subkonMasterItems = computed(() =>
  (masterItems.value || []).filter((x) => String(x.category || '').trim().toLowerCase() === 'subkon'),
)
const subkonItemCodePicker = ref('')

function masterDimensionCategoryParam() {
  return isSubkonPo.value ? 'SubKon' : undefined
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
const isEditMode = ref(false)
/** Tanggal order dari DB saat buka edit — jika ada, tanggal tidak boleh diubah lewat form simpan penuh. */
const savedHeaderOrderDate = ref('')
const orderDateLocked = computed(() => isEditMode.value && Boolean(savedHeaderOrderDate.value))

const editingPoId = ref(null)
const editingDetailIds = ref([])
const draftLines = ref([])
const draftRiskOnly = ref(false)
const editingDraftLineIndex = ref(-1)
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

const selectedSwatchRecipe = computed(() => {
  const id = selectedSwatchId.value
  if (!id) return null
  return colorSwatchOptions.value.find((x) => x.id === id) || null
})

const swatchFieldsLocked = computed(
  () => Boolean(selectedSwatchId.value) && !swatchFieldsManualEdit.value,
)

/** Color standart & backing tampil manual; disembunyikan saat resep swatch aktif (nilai ada di kartu resep). */
const showColorStandardBackingFields = computed(
  () => !selectedSwatchId.value || swatchFieldsManualEdit.value,
)

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
  const idx = draftLines.value.indexOf(row)
  return idx >= 0 && idx === editingDraftLineIndex.value ? 'draft-line-active' : ''
}

async function applyLineToForm(line) {
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
  etdScheduleRows.value = loadEtdScheduleRowsFromApi(line.delivery_schedules || [])
  await refreshThicknessOptionsFromApi()
  await refreshColorOptionsFromApi()
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

async function saveDetailSchedules(detailId, schedules) {
  const rows = loadEtdScheduleRowsFromApi(schedules || [])
  await setPoDetailDeliverySchedules(
    detailId,
    etdScheduleRowsToPayload(rows, formModel.quantity_order),
  )
}

const materialDimensionOptions = ref([])
const thicknessDimensionOptions = ref([])
const colorDimensionOptions = ref([])
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
  return !String(formModel.material_name || '').trim() || !String(formModel.thickness_text || '').trim() || !String(formModel.color_family || '').trim()
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
  if (!selectedSwatchId.value && !String(formModel.color_standard || '').trim()) return 5
  return 0
})

const swatchHelperMessage = computed(() => {
  if (colorSwatchLoading.value) return ''
  if (!poFactoryKeyForSwatch() || !formModel.buyer) {
    return t('pages.po.swatchNeedCustomerBuyer')
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

let lastSwatchScopeKey = ''
let lastAutoSwatchDimensionKey = ''

function swatchScopeKey() {
  return [
    formModel.customer_id,
    formModel.factory_code,
    formModel.buyer,
    formModel.material_name,
    swatchAllMaterials.value,
  ]
    .map((x) => String(x ?? '').trim().toLowerCase())
    .join('|')
}

function swatchDimensionKey() {
  return [formModel.material_name, formModel.color, formModel.emboss]
    .map((x) => String(x || '').trim().toLowerCase())
    .join('|')
}

function autoApplyColorSwatchFromDimensions() {
  const material = String(formModel.material_name || '').trim()
  const color = String(formModel.color || '').trim()
  const emboss = String(formModel.emboss || '').trim()
  if (!material || !color || !emboss) return

  const dimKey = swatchDimensionKey()
  if (dimKey === lastAutoSwatchDimensionKey) return

  const recipe = pickBestSwatchRecipe(colorSwatchOptions.value, { material, color, emboss })
  if (!recipe) return
  lastAutoSwatchDimensionKey = dimKey
  applySwatchRecipeOption(recipe, {
    formModel,
    autoFieldMeta,
    materialFieldOverride,
    selectedSwatchId,
  })
  swatchFieldsManualEdit.value = false
  swatchPickerOpen.value = false
}

function reapplySelectedSwatchRecipe({ silent = false } = {}) {
  const picked = selectedSwatchRecipe.value
  if (!picked) return false
  applySwatchRecipeOption(picked, {
    formModel,
    autoFieldMeta,
    materialFieldOverride,
    selectedSwatchId,
  })
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
  if (!swatchFieldsManualEdit.value) {
    formModel.color_standard = ''
    formModel.backing = ''
    formModel.color_reference = ''
    autoFieldMeta.color_standard = false
    autoFieldMeta.backing = false
    autoFieldMeta.color_reference = false
  }
  selectedSwatchId.value = null
  swatchFieldsManualEdit.value = false
  swatchPickerOpen.value = true
  lastAutoSwatchDimensionKey = ''
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
    lastAutoSwatchDimensionKey = swatchDimensionKey()
    applySwatchRecipeOption(picked, {
      formModel,
      autoFieldMeta,
      materialFieldOverride,
      selectedSwatchId,
    })
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
    swatchFieldsManualEdit.value = false
    swatchPickerOpen.value = false
    ElMessage.success(t('pages.po.swatchApplied'))
  } catch (e) {
    ElMessage.error(e.message || t('common.errorGeneric'))
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
  if (vt.includes('pu')) return true
  if (mn.includes('pu') || mn.includes('suede') || mn.includes('suide')) return true
  return false
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
    formModel.thi_line_ref = r.lot_number || ''
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
          formModel.color_reference = item.color_reference || ''
          autoFieldMeta.color_reference = Boolean(item.color_reference)
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
  () => [
    formModel.customer_id,
    formModel.factory_code,
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
    if (scopeChanged) {
      selectedSwatchId.value = null
      lastAutoSwatchDimensionKey = ''
      swatchFieldsManualEdit.value = false
      swatchPickerOpen.value = false
    }
    void loadColorSwatchOptions()
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
  thicknessDimensionOptions.value = []
  colorDimensionOptions.value = []
  colorFamilyAutoMode.value = true
  lotAutoFromMaterial.value = false
  selectedSwatchId.value = null
  swatchFieldsManualEdit.value = false
  swatchPickerOpen.value = false
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
}

async function restorePoDraftIfAny() {
  const raw = readPoDraftRaw()
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
    if (formModel.brand_id) await onBrandChange(formModel.brand_id, { fromCustomerChange: true })
    ElMessage.success('Draft PO berhasil dimuat.')
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

async function onPickedMaterialDimension() {
  formModel.thickness_text = ''
  formModel.color = ''
  formModel.master_item_id = null
  subkonItemCodePicker.value = ''
  formModel.thi_line_ref = ''
  lotAutoFromMaterial.value = false
  skipMasterResolve.value = false
  lastResolveHadNoMaster.value = false
  thicknessDimensionOptions.value = []
  colorDimensionOptions.value = []
  const m = String(formModel.material_name || '').trim()
  if (m) {
    await refreshThicknessOptionsFromApi()
    if (isSubkonPo.value) await refreshColorOptionsFromApi()
    scheduleAutoLotGenerate()
  }
}

async function onPickedThicknessDimension() {
  formModel.color = ''
  formModel.master_item_id = null
  subkonItemCodePicker.value = ''
  skipMasterResolve.value = false
  lastResolveHadNoMaster.value = false
  colorDimensionOptions.value = []
  const m = String(formModel.material_name || '').trim()
  const tt = String(formModel.thickness_text || '').trim()
  if (m && tt) await refreshColorOptionsFromApi()
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
}

function clearLinkedMasterItem() {
  formModel.master_item_id = null
  subkonItemCodePicker.value = ''
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
  if (!mn || !tt || !co) {
    lastResolveHadNoMaster.value = false
    formModel.master_item_id = null
    return
  }
  masterResolveLoading.value = true
  try {
    const res = await resolveMasterItemByDimensions({
      material_name: mn,
      thickness_text: tt,
      color: co,
      category: masterDimensionCategoryParam(),
    })
    if (seq !== masterResolveSeq) return
    lastResolveHadNoMaster.value = res.status === 'none'
    if (res.status === 'single' && res.item) {
      upsertMasterItemInCache(res.item)
      resetMaterialFieldOverride()
      colorFamilyAutoMode.value = true
      formModel.master_item_id = res.item.id
      hydrateFormFromMasterItemRow(res.item, { syncDimensions: false })
      scheduleAutoLotGenerate()
    } else if (res.status === 'ambiguous' && (res.candidates || []).length) {
      formModel.master_item_id = null
      skipMasterResolve.value = true
      ambiguousMasterCandidates.value = res.candidates
      selectedAmbiguousMasterId.value = res.candidates[0]?.id ?? null
      ambiguousMasterVisible.value = true
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
  upsertMasterItemInCache(c)
  formModel.master_item_id = c.id
  skipMasterResolve.value = false
  ambiguousMasterVisible.value = false
  resetMaterialFieldOverride()
  colorFamilyAutoMode.value = true
  hydrateFormFromMasterItemRow(c, { syncDimensions: false })
  lastResolveHadNoMaster.value = false
  scheduleAutoLotGenerate()
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
  () => [formModel.material_name, formModel.thickness_text, formModel.color],
  () => {
    if (isSubkonPo.value && subkonItemCodePicker.value) return
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
  await restorePoDraftIfAny()
}

async function buildCurrentDetailBody() {
  const body = buildDetailBodyCore(formModel, etdScheduleRows.value, selectedSwatchId.value)
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
    ElMessage.warning(t('pages.po.manualPriceRemarkRequired'))
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
    clearEtdScheduleRows()
    resetMaterialFieldOverride()
    colorFamilyAutoMode.value = true
    lastResolveHadNoMaster.value = false
    thicknessDimensionOptions.value = []
    colorDimensionOptions.value = []
    formErrors.material_name = ''
    formErrors.quantity_order = ''
    scheduleAutoLotGenerate()
  }
}

function removeDraftLine(index) {
  draftLines.value.splice(index, 1)
}

const openEditDialog = async (row) => {
  isEditMode.value = true
  editingPoId.value = row.id
  resetForm()
  savedHeaderOrderDate.value = row.order_date ? String(row.order_date).slice(0, 10) : ''
  formModel.po_number = row.po_number || ''
  formModel.customer_id = row.customer_id
  formModel.brand_id = row.brand_id ?? null
  formModel.po_category = row.po_category || 'production'
  formModel.order_date = row.order_date ? String(row.order_date).slice(0, 10) : ''
  formModel.buyer = row.buyer || ''
  formModel.etd = row.etd ? String(row.etd).slice(0, 10) : ''
  formModel.po_customer_ref = row.po_customer_ref || ''
  formModel.billing_address = row.billing_address || ''
  formModel.delivery_address = row.delivery_address || ''
  formModel.status = row.status || 'draft'
  try {
    selectedCustomer.value = formModel.customer_id ? await getCustomer(formModel.customer_id) : null
  } catch {
    selectedCustomer.value = null
  }
  if (selectedCustomer.value) {
    applyAutoFactoryCode(selectedCustomer.value, { force: true })
  } else {
    formModel.factory_code = row.factory_code || ''
    autoFieldMeta.factory_code = false
  }
  pauseLotAutoBriefly()
  await onBrandChange(formModel.brand_id, { fromCustomerChange: true })
  schedulePricePreview()
  try {
    const details = await listPoDetails(row.id)
    const scheduleLists = await Promise.all(
      details.map((d) => listPoDetailDeliverySchedules(d.id).catch(() => [])),
    )
    draftLines.value = details.map((d, idx) => ({
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
      color_standard: d.color_standard || undefined,
      backing: d.backing || undefined,
      quantity_order: d.quantity_order != null ? Number(d.quantity_order) : undefined,
      style_article: d.style_article || undefined,
      model: d.model || undefined,
      detail_remark: d.detail_remark || undefined,
      thi_line_ref: d.thi_line_ref || undefined,
      color_swatch_recipe_id: d.color_swatch_recipe_id || undefined,
      unit_price: d.unit_price != null ? Number(d.unit_price) : undefined,
      delivery_schedules: normalizeSchedulesFromApi(scheduleLists[idx]),
      manual_override: false,
      material_master_override: false,
      material_master_matched: Boolean(d.master_item_id),
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
      formModel.color_standard = d0.color_standard || ''
      formModel.backing = d0.backing || ''
      formModel.quantity_order = d0.quantity_order != null ? String(d0.quantity_order) : ''
      formModel.style_article = d0.style_article || ''
      formModel.model = d0.model || ''
      formModel.detail_remark = d0.detail_remark || ''
      formModel.thi_line_ref = d0.thi_line_ref || ''
      etdScheduleRows.value = loadEtdScheduleRowsFromApi(scheduleLists[0] || [])
      editingDraftLineIndex.value = 0
      loadedDetailMasterSnapshot.value = `${String(d0.material_name || '').trim()}|${String(d0.thickness_text || '').trim()}|${String(d0.color || '').trim()}|${d0.master_item_id ?? ''}`
      if (d0.master_item_id) {
        const cacheIt = masterItems.value.find((x) => x.id === d0.master_item_id)
        if (cacheIt) upsertMasterItemInCache(cacheIt)
      }
      await refreshThicknessOptionsFromApi()
      await refreshColorOptionsFromApi()
      lastResolveHadNoMaster.value = false
    } else {
      loadedDetailMasterSnapshot.value = null
    }
  } catch {
    editingDetailIds.value = []
    draftLines.value = []
    loadedDetailMasterSnapshot.value = null
  }
  formDialogVisible.value = true
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
      await syncCurrentFormToDraftLine()
    }
    const bodiesFinal = draftLines.value.length ? draftLines.value : [await buildCurrentDetailBody()]
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
        const schedules = rowBody.delivery_schedules || []
        delete rowBody.delivery_schedules
        const existingId = editingDetailIds.value[i]
        if (existingId) {
          await updatePoDetail(existingId, detailPayloadForUpdate(rowBody))
          await saveDetailSchedules(existingId, schedules)
          keepIds.push(existingId)
        } else {
          const createdDetail = await addPoDetail(editingPoId.value, rowBody)
          await saveDetailSchedules(createdDetail.id, schedules)
          keepIds.push(createdDetail.id)
        }
      }
      const staleIds = editingDetailIds.value.filter((id) => !keepIds.includes(id))
      for (const staleId of staleIds) {
        await deletePoDetail(staleId)
      }
    } else {
      const created = await createPo(header)
      for (const raw of bodiesFinal) {
        const rowBody = { ...sanitizeNewDetailBody(raw) }
        const schedules = rowBody.delivery_schedules || []
        delete rowBody.delivery_schedules
        const createdDetail = await addPoDetail(created.id, rowBody)
        await saveDetailSchedules(createdDetail.id, schedules)
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
    enableMaterialOverride,
    isMaterialFieldLocked,
    materialFieldOverride,
    resetMaterialFieldToMaster,
    activeSeasonLabel,
    fluorescentColorOptions,
    selectedSwatchId,
    selectedSwatchRecipe,
    swatchFieldsLocked,
    showColorStandardBackingFields,
    swatchFieldsManualEdit,
    swatchPickerOpen,
    colorSwatchLoading,
    colorSwatchOptions,
    swatchOptionLabel,
    poFactoryKeyForSwatch,
    materialStepFillStep,
    swatchHelperMessage,
    applyColorSwatch,
    enableSwatchManualEdit,
    reapplySelectedSwatchRecipe,
    openSwatchPicker,
    clearSwatchSelection,
    swatchAllMaterials,
    loadColorSwatchOptions,
    swatchRetriedWithoutMaterial,
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
    formatLineEtdScheduleDisplay,
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
    materialGroupLabel,
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
