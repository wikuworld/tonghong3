/** Payload baris detail PO untuk API. */

import { etdScheduleRowsToPayload } from './poEtdSchedule.js'

export function buildDetailBodyCore(formModel, etdScheduleRows, selectedSwatchId) {
  return {
    master_item_id: formModel.master_item_id || undefined,
    material_name: formModel.material_name || undefined,
    thickness_text: formModel.thickness_text || undefined,
    color: formModel.color || undefined,
    color_family: formModel.color_family || undefined,
    emboss: formModel.emboss || undefined,
    vir_softness_type: formModel.vir_softness_type || undefined,
    softness: formModel.softness || undefined,
    color_reference: formModel.color_reference || undefined,
    color_standard: formModel.color_standard || undefined,
    backing: formModel.backing || undefined,
    quantity_order: formModel.quantity_order ? Number(formModel.quantity_order) : undefined,
    style_article: formModel.style_article || undefined,
    model: formModel.model || undefined,
    detail_remark: formModel.detail_remark || undefined,
    thi_line_ref: formModel.thi_line_ref || undefined,
    delivery_schedules: etdScheduleRowsToPayload(etdScheduleRows, formModel.quantity_order),
    color_swatch_recipe_id: selectedSwatchId || undefined,
  }
}

function orderDateAsOf(formModel) {
  const raw = formModel?.order_date
  if (!raw) return null
  const s = String(raw).trim().slice(0, 10)
  return /^\d{4}-\d{2}-\d{2}$/.test(s) ? s : null
}

export async function appendDetailUnitPrice(body, formModel, { resolveBuyerUnitPrice, previewResolvedUnitPrice }) {
  const isFreePrice = formModel.po_category === 'subcont' || formModel.po_category === 'return'
  if (isFreePrice) {
    if (formModel.unit_price_input != null) {
      body.unit_price = Number(formModel.unit_price_input)
    }
    return body
  }

  const b = (formModel.buyer || '').trim()
  if (b) {
    try {
      const r = await resolveBuyerUnitPrice({
        buyer_code: b,
        as_of: orderDateAsOf(formModel),
        material_name: formModel.material_name || null,
        color: formModel.color || null,
        style_article: formModel.style_article || null,
        thickness_text: formModel.thickness_text || null,
        color_family: formModel.color_family || null,
        emboss: formModel.emboss || null,
        factory_code: formModel.factory_code || null,
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

  if (formModel.is_special_price && formModel.unit_price_input != null) {
    body.base_price = previewResolvedUnitPrice
    body.is_special_price = true
    body.discount_type = formModel.discount_type
    body.discount_value = formModel.discount_value
  }

  return body
}

export function detailPayloadForUpdate(body) {
  const o = { ...body }
  delete o.id
  delete o.item_category
  delete o._uid
  return o
}

export function sanitizeNewDetailBody(body) {
  const o = { ...body }
  delete o.id
  delete o.line_etd
  delete o.item_category
  delete o._uid
  return o
}
