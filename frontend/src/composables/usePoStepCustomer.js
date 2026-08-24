import { ElMessage } from 'element-plus'

import {
  getAllowedBrands,
  getCustomer,
  listBrandBuyers,
  listCustomerBrandMappings,
  fetchNextPoNumber,
} from '../api/client'
import { ITEM_CATEGORY_SUEDE, normalizeItemCategory } from '../utils/poMasterResolve.js'

export function brandCustomerIds(brand) {
  if (!brand) return []
  if (Array.isArray(brand.customer_ids) && brand.customer_ids.length) {
    return brand.customer_ids.map((id) => Number(id)).filter((id) => Number.isFinite(id))
  }
  if (brand.customer_id != null) return [Number(brand.customer_id)]
  return []
}

export function brandAllowedForCustomer(brand, customerId) {
  if (!customerId) return true
  const mapped = brandCustomerIds(brand)
  if (!mapped.length) return true
  return mapped.includes(Number(customerId))
}

export function pickDefaultBrandId(brandIds, mappings) {
  const allowed = new Set(brandIds.map((id) => Number(id)))
  const defaultRow = (mappings || []).find(
    (m) => m.is_default && allowed.has(Number(m.brand_id)),
  )
  if (defaultRow) return Number(defaultRow.brand_id)
  return brandIds.length ? Number(brandIds[0]) : null
}

/** Untuk preview/nomor SO: production + PU coated → prefix THIPM. */
export function inferSoMaterialGroup(formModel, draftLines = []) {
  const row = draftLines[0] || formModel
  const cat = normalizeItemCategory(formModel?.item_category || row?.item_category)
  if (cat === ITEM_CATEGORY_SUEDE) return undefined
  const vir = String(formModel?.vir_softness_type || row?.vir_softness_type || '').toLowerCase()
  const material = String(formModel?.material_name || row?.material_name || '').toLowerCase()
  const text = `${vir} ${material}`
  if (text.includes('pu') && !text.includes('suede') && !text.includes('suide')) return 'pu'
  return undefined
}

/** Step 0: customer, brand, buyer, preview nomor SO. */
export function usePoStepCustomer({
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
}) {
  async function refreshNextPoNumberPreview() {
    if (isEditMode.value) return
    try {
      const lines = draftLines?.value || []
      const params = {
        po_category: formModel.po_category,
        order_date: formModel.order_date || undefined,
      }
      const materialGroup = inferSoMaterialGroup(formModel, lines)
      if (materialGroup) params.material_group = materialGroup
      const r = await fetchNextPoNumber(params)
      nextPoNumberPreview.value = r?.po_number || ''
    } catch {
      nextPoNumberPreview.value = ''
    }
  }

  function validateStep0() {
    if (!formModel.customer_id) {
      formErrors.customer_id = t('pages.po.customerRequired')
      ElMessage.warning(t('pages.po.customerRequired'))
      return false
    }
    if (!formModel.brand_id) {
      ElMessage.warning('Brand wajib dipilih setelah customer.')
      return false
    }
    if (!formModel.buyer) {
      ElMessage.warning('Buyer wajib dipilih setelah brand.')
      return false
    }
    formErrors.customer_id = ''
    return true
  }

  async function onCustomerChange() {
    if (brandLockedCustomerId.value) {
      formModel.customer_id = brandLockedCustomerId.value
      return
    }
    brandLockedCustomerId.value = null
    formModel.brand_id = null
    brandBuyerCodes.value = []
    customerBuyerCodes.value = []
    formModel.buyer = ''
    allowedBrandIds.value = []
    const cid = formModel.customer_id
    if (cid) {
      try {
        const [allowed, customer, mappings] = await Promise.all([
          getAllowedBrands(cid),
          getCustomer(cid),
          listCustomerBrandMappings(cid).catch(() => []),
        ])
        allowedBrandIds.value = allowed.map((b) => b.id)
        selectedCustomer.value = customer || null
        if (allowedBrandIds.value.length > 0) {
          const stillValid =
            formModel.brand_id && allowedBrandIds.value.includes(formModel.brand_id)
          formModel.brand_id = stillValid
            ? formModel.brand_id
            : pickDefaultBrandId(allowedBrandIds.value, mappings)
          await onBrandChange(formModel.brand_id, { fromCustomerChange: true })
        } else {
          formModel.brand_id = null
        }
        if (customer) {
          applyAutoFactoryCode(customer, { force: true })
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
      formModel.factory_code = ''
      autoFieldMeta.factory_code = false
      customerBuyerCodes.value = []
      selectedCustomer.value = null
    }
  }

  async function onBrandChange(brandId, { fromCustomerChange = false } = {}) {
    brandBuyerCodes.value = []
    if (!fromCustomerChange) {
      brandLockedCustomerId.value = null
    }
    if (!brandId) return
    try {
      if (!fromCustomerChange) {
        const selectedBrand = brands.value.find((b) => b.id === brandId)
        const currentCustomerId = formModel.customer_id
        const mappedIds = brandCustomerIds(selectedBrand)
        if (currentCustomerId && mappedIds.length) {
          if (!mappedIds.includes(Number(currentCustomerId))) {
            const fallbackId = mappedIds[0]
            formModel.customer_id = fallbackId
            selectedCustomer.value =
              customers.value.find((x) => x.id === fallbackId) || selectedCustomer.value
            if (selectedCustomer.value) {
              applyAutoFactoryCode(selectedCustomer.value, { force: true })
              formModel.billing_address = selectedCustomer.value.address || ''
              formModel.delivery_address = selectedCustomer.value.address || ''
            }
          }
        } else if (!currentCustomerId && mappedIds.length === 1) {
          brandLockedCustomerId.value = mappedIds[0]
          formModel.customer_id = mappedIds[0]
          const cust = customers.value.find((x) => x.id === mappedIds[0])
          if (cust) {
            selectedCustomer.value = cust
            applyAutoFactoryCode(cust, { force: true })
            formModel.billing_address = cust.address || ''
            formModel.delivery_address = cust.address || ''
          }
        }
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

  return {
    refreshNextPoNumberPreview,
    validateStep0,
    onCustomerChange,
    onBrandChange,
  }
}
