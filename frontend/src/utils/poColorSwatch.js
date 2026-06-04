/** Lookup & apply master color swatch untuk form PO. */

export function factoryCodeFromCustomer(customer) {
  if (!customer) return ''
  return String(customer.code || '').trim()
}

export function swatchFactoryHint(formModel, { customers = [], selectedCustomer = null } = {}) {
  const fc = String(formModel.factory_code || '').trim()
  if (fc) return fc.toUpperCase()
  const c = selectedCustomer || customers.find((x) => x.id === formModel.customer_id)
  if (!c) return ''
  return factoryCodeFromCustomer(c) || String(c.name || '').trim().slice(0, 80).toUpperCase()
}

export function swatchOptionLabel(s) {
  if (!s) return ''
  const code = s.color_code ? ` [${s.color_code}]` : ''
  const emb = s.emboss ? ` · ${s.emboss}` : ''
  return `${s.color_name || ''}${code}${emb}`
}

/**
 * Muat opsi resep swatch dari API.
 * @returns {{ options: array, retriedWithoutMaterial: boolean }}
 */
export async function fetchColorSwatchOptionList({
  formModel,
  swatchAllMaterials,
  lookupColorSwatchRecipes,
  customers = [],
  selectedCustomer = null,
}) {
  const fk = swatchFactoryHint(formModel, { customers, selectedCustomer })
  const buyer = String(formModel.buyer || '').trim().toUpperCase()
  if ((!fk && !formModel.customer_id) || !buyer) {
    return { options: [], retriedWithoutMaterial: false }
  }

  const material = String(formModel.material_name || '').trim()
  const base = {
    factory_key: fk || undefined,
    customer_id: formModel.customer_id || undefined,
    buyer_code: buyer,
    limit: 60,
  }
  const withMaterial = !swatchAllMaterials && material
  let options = await lookupColorSwatchRecipes({
    ...base,
    material_name: withMaterial ? material : undefined,
    include_all_materials: swatchAllMaterials || undefined,
  })

  let retriedWithoutMaterial = false
  if (!options.length && withMaterial) {
    options = await lookupColorSwatchRecipes({
      ...base,
      include_all_materials: true,
    })
    retriedWithoutMaterial = options.length > 0
  }

  return { options, retriedWithoutMaterial }
}

/** Terapkan payload fill dari API ke form baris PO. */
export function applyColorSwatchFill(
  fill,
  { formModel, autoFieldMeta, materialFieldOverride, selectedSwatchId },
) {
  if (fill.color) {
    formModel.color = fill.color
    autoFieldMeta.color = false
  }
  if (fill.color_reference) {
    formModel.color_reference = fill.color_reference
    autoFieldMeta.color_reference = false
  }
  if (fill.color_standard) {
    formModel.color_standard = fill.color_standard
    autoFieldMeta.color_standard = false
  }
  if (fill.emboss) {
    formModel.emboss = fill.emboss
    materialFieldOverride.emboss = true
  }
  if (fill.backing) {
    formModel.backing = fill.backing
    autoFieldMeta.backing = false
  }
  if (fill.material_name && !formModel.material_name) {
    formModel.material_name = fill.material_name
  }
  if (fill.thi_line_ref) {
    formModel.thi_line_ref = fill.thi_line_ref
  }
  if (fill.color_swatch_recipe_id) {
    selectedSwatchId.value = fill.color_swatch_recipe_id
  }
}
