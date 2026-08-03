/** LocalStorage draft dialog input PO. */

import { emptyEtdScheduleRows, etdScheduleRowsToPayload, loadEtdScheduleRowsFromApi } from './poEtdSchedule.js'

export const PO_DRAFT_STORAGE_KEY = 'po_input_dialog_draft_v1'

function extractHeader(formModel) {
  return {
    po_number: formModel.po_number,
    customer_id: formModel.customer_id,
    brand_id: formModel.brand_id,
    po_category: formModel.po_category,
    factory_code: formModel.factory_code,
    order_date: formModel.order_date,
    buyer: formModel.buyer,
    etd: formModel.etd,
    po_customer_ref: formModel.po_customer_ref,
    billing_address: formModel.billing_address,
    delivery_address: formModel.delivery_address,
    status: formModel.status,
  }
}

function extractCurrentLine(formModel, etdScheduleRows) {
  return {
    master_item_id: formModel.master_item_id,
    material_name: formModel.material_name,
    thickness_text: formModel.thickness_text,
    color: formModel.color,
    color_family: formModel.color_family,
    emboss: formModel.emboss,
    vir_softness_type: formModel.vir_softness_type,
    softness: formModel.softness,
    color_reference: formModel.color_reference,
    color_standard: formModel.color_standard,
    backing: formModel.backing,
    quantity_order: formModel.quantity_order,
    style_article: formModel.style_article,
    model: formModel.model,
    detail_remark: formModel.detail_remark,
    thi_line_ref: formModel.thi_line_ref,
    unit_price_input: formModel.unit_price_input,
    is_special_price: formModel.is_special_price,
    discount_type: formModel.discount_type,
    discount_value: formModel.discount_value,
    etdScheduleRows,
  }
}

export function buildPoDraftPayload(formModel, etdScheduleRows, draftLines) {
  return {
    header: extractHeader(formModel),
    currentLine: extractCurrentLine(formModel, etdScheduleRows),
    draftLines,
  }
}

export function applyPoDraftData(data, { formModel, autoFieldMeta, etdScheduleRows, draftLines }) {
  if (!data || typeof data !== 'object') return
  const header = data.header || {}
  const line = data.currentLine || {}

  formModel.po_number = header.po_number || ''
  formModel.customer_id = header.customer_id ?? null
  formModel.brand_id = header.brand_id ?? null
  formModel.po_category = header.po_category || 'production'
  formModel.factory_code = header.factory_code || ''
  autoFieldMeta.factory_code = false
  formModel.order_date = header.order_date || ''
  formModel.buyer = header.buyer || ''
  formModel.etd = header.etd || ''
  formModel.po_customer_ref = header.po_customer_ref || ''
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
  formModel.color_standard = line.color_standard || ''
  formModel.backing = line.backing || ''
  formModel.quantity_order = line.quantity_order || ''
  formModel.style_article = line.style_article || ''
  formModel.model = line.model || ''
  formModel.detail_remark = line.detail_remark || ''
  formModel.thi_line_ref = line.thi_line_ref || ''
  formModel.unit_price_input = line.unit_price_input ?? null
  formModel.is_special_price = Boolean(line.is_special_price)
  formModel.discount_type = line.discount_type || 'percent'
  formModel.discount_value = Number(line.discount_value || 0)

  if (Array.isArray(line.etdScheduleRows) && line.etdScheduleRows.length) {
    etdScheduleRows.value = loadEtdScheduleRowsFromApi(
      etdScheduleRowsToPayload(line.etdScheduleRows),
    )
  } else {
    etdScheduleRows.value = emptyEtdScheduleRows()
  }

  draftLines.value = Array.isArray(data.draftLines) ? data.draftLines : []
}

export function savePoDraftLocalStorage(payload, key = PO_DRAFT_STORAGE_KEY) {
  try {
    localStorage.setItem(key, JSON.stringify(payload))
  } catch {
    // ignore local storage write error
  }
}

export function clearPoDraftLocalStorage(key = PO_DRAFT_STORAGE_KEY) {
  try {
    localStorage.removeItem(key)
  } catch {
    // ignore
  }
}

export function readPoDraftRaw(key = PO_DRAFT_STORAGE_KEY) {
  try {
    return localStorage.getItem(key) || ''
  } catch {
    return ''
  }
}
