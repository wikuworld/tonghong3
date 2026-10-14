/** Master item matching & hydrate untuk form PO. */

export function normalizedText(v) {
  return String(v || '').trim().toLowerCase()
}

export const ITEM_CATEGORY_PU = 'PU'
export const ITEM_CATEGORY_SUEDE = 'Suede'

/** Nilai API master: PU | Suede | SubKon. */
export function normalizeItemCategory(raw) {
  const cat = normalizedText(raw)
  if (cat === 'suide' || cat === 'suede') return ITEM_CATEGORY_SUEDE
  if (cat === 'pu') return ITEM_CATEGORY_PU
  if (cat === 'subkon' || cat === 'subcont' || cat === 'subcontract') return 'SubKon'
  return ''
}

export function itemCategoryLabel(raw) {
  const cat = normalizeItemCategory(raw)
  if (cat === ITEM_CATEGORY_SUEDE) return 'Suede'
  if (cat === ITEM_CATEGORY_PU) return 'PU'
  if (cat === 'SubKon') return 'SubKon'
  return '—'
}

/** Kategori item baris: eksplisit, lalu master, lalu tebak dari nama/vir. Default PU. */
export function inferItemCategory(row, masterItems = []) {
  const explicit = normalizeItemCategory(row?.item_category)
  if (explicit === ITEM_CATEGORY_PU || explicit === ITEM_CATEGORY_SUEDE) return explicit
  const masterId = row?.master_item_id
  if (masterId) {
    const mi = masterItems.find((x) => x.id === masterId)
    const fromMaster = normalizeItemCategory(mi?.category)
    if (fromMaster === ITEM_CATEGORY_PU || fromMaster === ITEM_CATEGORY_SUEDE) return fromMaster
  }
  const vir = normalizedText(row?.vir_softness_type)
  if (vir.includes('suede') || vir.includes('suide')) return ITEM_CATEGORY_SUEDE
  if (vir.includes('pu')) return ITEM_CATEGORY_PU
  const mn = normalizedText(row?.material_name)
  if (mn.includes('suede') || mn.includes('suide')) return ITEM_CATEGORY_SUEDE
  if (mn.includes('pu')) return ITEM_CATEGORY_PU
  return ITEM_CATEGORY_PU
}

/** PU atau Suede — untuk kolom keterangan baris (ganti System No di ringkasan PO). */
export function resolveMaterialGroupLabel(row, masterItems = []) {
  const explicit = itemCategoryLabel(row?.item_category)
  if (explicit !== '—') return explicit
  const masterId = row?.master_item_id
  if (masterId) {
    const mi = masterItems.find((x) => x.id === masterId)
    const fromMaster = itemCategoryLabel(mi?.category)
    if (fromMaster !== '—') return fromMaster
  }
  if (normalizedText(row?.vir_softness_type).includes('pu')) return 'PU'
  const mn = normalizedText(row?.material_name)
  if (mn.includes('suede') || mn.includes('suide')) return 'Suede'
  if (mn.includes('pu')) return 'PU'
  return '—'
}

export function inferColorFamilyFromColor(colorValue) {
  const color = String(colorValue || '').trim().toLowerCase()
  if (!color) return null
  if (/\b(black|hitam)\b/.test(color)) return 'black'
  if (/\b(fluo|fluorescent|neon)\b/.test(color)) return 'fluorescent'
  if (/\b(white|putih)\b/.test(color)) return null
  return 'color'
}

export function scoreMasterItemReference(item, formModel) {
  const material = normalizedText(formModel.material_name)
  if (!material) return 0
  const thickness = normalizedText(formModel.thickness_text)
  const color = normalizedText(formModel.color)
  const style = normalizedText(formModel.style_article)
  const itemMaterial = normalizedText(item.material_name)
  if (!itemMaterial) return 0

  let score = 0
  if (formModel.master_item_id && item.id === formModel.master_item_id) score += 6
  if (itemMaterial === material) score += 4
  else if (itemMaterial.includes(material) || material.includes(itemMaterial)) score += 2
  if (thickness && normalizedText(item.thickness_range) === thickness) score += 2
  if (color && normalizedText(item.color) === color) score += 2
  if (style && normalizedText(item.style_article) === style) score += 2
  return score
}

export function findBestMasterReferenceItem(masterItems, formModel) {
  let best = null
  let bestScore = 0
  for (const item of masterItems) {
    const score = scoreMasterItemReference(item, formModel)
    if (score > bestScore) {
      best = item
      bestScore = score
    }
  }
  if (!best || bestScore < 2) return null
  return best
}

export function applyReferenceDefaults(formModel, masterItems, autoFieldMeta, forceFields = []) {
  if (formModel.master_item_id) return
  const best = findBestMasterReferenceItem(masterItems, formModel)
  if (!best) return

  const forceSet = new Set(forceFields)
  const suede = inferItemCategory(formModel, masterItems) === ITEM_CATEGORY_SUEDE
  if (!suede && (!formModel.backing || forceSet.has('backing')) && best.backing) {
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

export function hydrateFormFromMasterItemRow(
  item,
  {
    formModel,
    autoFieldMeta,
    previewResolvedUnitPrice = null,
    colorFamilyAutoMode,
    syncDimensions = true,
    subkonMode = false,
  },
) {
  if (!item) return
  if (syncDimensions) {
    formModel.material_name = item.material_name || ''
    formModel.thickness_text =
      item.thickness_range || (item.thickness_mm != null ? String(item.thickness_mm) : '')
    formModel.color = item.color || ''
  }
  if (subkonMode) return
  if (colorFamilyAutoMode) colorFamilyAutoMode.value = true
  formModel.emboss = item.emboss || ''
  formModel.softness = item.softness || ''
  autoFieldMeta.softness = Boolean(item.softness)
  const colorCode = String(item.color_code || item.color_reference || '').trim()
  formModel.color_reference = colorCode
  autoFieldMeta.color_reference = Boolean(colorCode)
  formModel.color_standard = item.color_standard || ''
  autoFieldMeta.color_standard = Boolean(item.color_standard)
  const suede =
    normalizeItemCategory(item.category) === ITEM_CATEGORY_SUEDE ||
    inferItemCategory({ ...formModel, material_name: item.material_name || formModel.material_name }, []) ===
      ITEM_CATEGORY_SUEDE
  if (suede) {
    formModel.backing = ''
    autoFieldMeta.backing = false
  } else {
    formModel.backing = item.backing || ''
    autoFieldMeta.backing = Boolean(item.backing)
  }
  formModel.quantity_order = item.quantity_order_default != null ? String(item.quantity_order_default) : ''
  formModel.style_article = item.style_article || ''
  formModel.model = item.model || ''
  autoFieldMeta.model = Boolean(item.model)
  if (item.color) {
    formModel.color_family = inferColorFamilyFromColor(item.color)
  }
  if (previewResolvedUnitPrice != null) {
    formModel.unit_price_input = previewResolvedUnitPrice
  } else {
    formModel.unit_price_input = null
  }
}

export function resetMaterialFieldToMaster(field, formModel, masterItems, materialFieldOverride, colorFamilyAutoMode) {
  if (!formModel.master_item_id) return
  const item = masterItems.find((x) => x.id === formModel.master_item_id)
  if (!item) return
  if (field === 'material_name') formModel.material_name = item.material_name || ''
  if (field === 'thickness_text') {
    formModel.thickness_text = item.thickness_range || (item.thickness_mm != null ? String(item.thickness_mm) : '')
  }
  if (field === 'color') formModel.color = item.color || ''
  if (field === 'emboss') formModel.emboss = item.emboss || ''
  if (field === 'style_article') formModel.style_article = item.style_article || ''
  if (field === 'color_family') {
    formModel.color_family = inferColorFamilyFromColor(item.color)
    if (colorFamilyAutoMode) colorFamilyAutoMode.value = true
  }
  materialFieldOverride[field] = false
}

export function formatThicknessDisplay(v) {
  const raw = String(v || '')
    .trim()
    .replace(/\s*mm\s*$/i, '')
    .trim()
  if (!raw) return ''
  const range = raw.match(/^(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)$/)
  if (range) return `${range[1]} - ${range[2]} mm`
  const single = raw.match(/^(\d+(?:\.\d+)?)$/)
  if (single) return `${single[1]} mm`
  // Sudah punya teks lain (mis. "1.2 - 1.4 MM") — pastikan akhiran mm.
  if (/\bmm\b/i.test(String(v || ''))) return String(v).trim()
  return `${raw} mm`
}

export function isThicknessPricingFormatValid(v) {
  const raw = String(v || '').trim()
  if (!raw) return true
  const single = /^\d+(\.\d+)?$/
  const range = /^\d+(\.\d+)?\s*[-–]\s*\d+(\.\d+)?$/
  return single.test(raw) || range.test(raw)
}

export function detailMasterSnapshot(formModel) {
  const mn = String(formModel.material_name || '').trim()
  const tt = String(formModel.thickness_text || '').trim()
  const co = String(formModel.color || '').trim()
  const em = String(formModel.emboss || '').trim()
  return `${mn}|${tt}|${co}|${em}|${formModel.master_item_id ?? ''}`
}
