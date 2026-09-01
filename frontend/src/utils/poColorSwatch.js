/** Lookup & apply master color swatch untuk form PO. */

import { extractColorCodeFromReference } from './poColorStandard.js'

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
  const std = s.color_standard ? ` → ${s.color_standard}` : ''
  const factory = s.factory_key ? ` · ${s.factory_key}` : ''
  return `${s.color_name || ''}${code}${emb}${std}${factory}`
}

export function normalizeSwatchText(value) {
  return String(value || '').trim().toLowerCase()
}

/** WOLF GREY (01V) / PINKSICLE (6FS) FLUORESCENT → wolf grey / pinksicle */
export function normalizeSwatchColorName(value) {
  return String(value || '')
    .trim()
    .replace(/\s*\([^)]*\)/gu, ' ')
    .replace(/\b(fluorescent|pearlized|metallic|mettalic|coloro)\b/giu, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
}

export function compactSwatchColorName(value) {
  return normalizeSwatchColorName(value).replace(/[^a-z0-9]/g, '')
}

function extractEmbossCodeToken(token) {
  const raw = String(token || '').trim().toUpperCase()
  if (!raw) return ''
  const codeRe = /^([A-Za-z]{1,4}-\d+[A-Za-z]?)/i
  const m = raw.match(codeRe)
  if (m) return m[1].toUpperCase()
  const m2 = raw.replace(/\s+/g, '').match(codeRe)
  return m2 ? m2[1].toUpperCase() : ''
}

/** AR-167 DM / R-8 M / UM-34T → kode dasar emboss */
export function swatchEmbossCode(value) {
  const base = String(value || '')
    .trim()
    .replace(/\s*\([^)]*\)\s*$/u, '')
    .trim()
  if (!base) return ''
  for (const token of base.split(/\s+/)) {
    const code = extractEmbossCodeToken(token)
    if (code) return code
  }
  return extractEmbossCodeToken(base) || (base.split(/\s+/)[0] || '').toUpperCase()
}

/** (PM) GENERIC PU COATED LEATHER → generic pu */
export function normalizeSwatchMaterialName(value) {
  let s = String(value || '')
    .trim()
    .replace(/^\(PM\)\s*/iu, '')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
  for (const suffix of [' coated leather', ' coated', ' leather', ' split suede']) {
    if (s.endsWith(suffix)) s = s.slice(0, -suffix.length).trim()
  }
  return s
}

export function swatchMaterialsMatch(a, b) {
  const na = normalizeSwatchMaterialName(a)
  const nb = normalizeSwatchMaterialName(b)
  if (!na || !nb) return true
  return na === nb || na.includes(nb) || nb.includes(na)
}

export function swatchColorsMatch(a, b) {
  const na = normalizeSwatchColorName(a)
  const nb = normalizeSwatchColorName(b)
  if (!na || !nb) return false
  if (na === nb || na.startsWith(nb) || nb.startsWith(na)) return true
  const ca = compactSwatchColorName(a)
  const cb = compactSwatchColorName(b)
  return Boolean(ca && ca === cb)
}

export function swatchEmbossMatch(a, b) {
  const ca = swatchEmbossCode(a)
  const cb = swatchEmbossCode(b)
  if (!ca || !cb) return false
  return ca === cb || ca.startsWith(cb) || cb.startsWith(ca)
}

export function materialNamesLooselyMatch(a, b) {
  return swatchMaterialsMatch(a, b)
}

/** Filter resep swatch yang cocok material + warna (kode CSI). Emboss opsional. */
export function pickMatchingSwatchRecipes(
  options,
  { material, color, emboss, requireEmboss = false, colorCode } = {},
) {
  const materialKey = normalizeSwatchText(material)
  const code = String(colorCode || extractColorCodeFromReference(color) || '')
    .trim()
    .toUpperCase()
  return (options || []).filter((recipe) => {
    if (materialKey && !materialNamesLooselyMatch(recipe.material_name, materialKey)) return false
    if (color) {
      const nameOk = swatchColorsMatch(recipe.color_name, color)
      const codeOk = Boolean(code && String(recipe.color_code || '').trim().toUpperCase() === code)
      if (!nameOk && !codeOk) return false
    }
    if (requireEmboss && emboss && !swatchEmbossMatch(recipe.emboss, emboss)) return false
    return true
  })
}

export function pickBestSwatchRecipe(options, { material, color, emboss } = {}) {
  const exact = pickMatchingSwatchRecipes(options, { material, color, emboss, requireEmboss: true })
  const matches = exact.length
    ? exact
    : pickMatchingSwatchRecipes(options, { material, color, emboss, requireEmboss: false })
  if (!matches.length) return null
  if (matches.length === 1) return matches[0]
  const embossCode = swatchEmbossCode(emboss)
  const colorNorm = normalizeSwatchColorName(color)
  const code = extractColorCodeFromReference(color)
  const ranked = matches
    .map((recipe) => {
      let score = 0
      if (code && String(recipe.color_code || '').trim().toUpperCase() === code) score += 8
      if (colorNorm && compactSwatchColorName(recipe.color_name) === compactSwatchColorName(color)) {
        score += 4
      }
      if (embossCode && swatchEmbossCode(recipe.emboss) === embossCode) score += 4
      if (recipe.csi_color_master_id) score += 3
      if (recipe.color_standard) score += 1
      return { recipe, score }
    })
    .sort((a, b) => b.score - a.score)
  return ranked[0]?.recipe || matches[0]
}

/** Isi form dari objek resep swatch (tanpa round-trip API). */
export function applySwatchRecipeOption(
  recipe,
  { formModel, autoFieldMeta, materialFieldOverride, selectedSwatchId },
) {
  if (!recipe) return
  if (selectedSwatchId) selectedSwatchId.value = recipe.id
  if (recipe.color_standard) {
    formModel.color_standard = recipe.color_standard
    autoFieldMeta.color_standard = true
  }
  if (recipe.color_code) {
    formModel.color_reference = recipe.color_code
    autoFieldMeta.color_reference = true
  }
  if (recipe.backing) {
    formModel.backing = recipe.backing
    autoFieldMeta.backing = true
  }
  if (recipe.emboss && !String(formModel.emboss || '').trim()) {
    formModel.emboss = recipe.emboss
    materialFieldOverride.emboss = false
  }
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
  // customers/selectedCustomer retained for API compat; factory no longer gates lookup
  void customers
  void selectedCustomer
  const buyer = String(formModel.buyer || '').trim().toUpperCase()
  if (!buyer) {
    return { options: [], retriedWithoutMaterial: false }
  }

  const material = String(formModel.material_name || '').trim()
  const color = String(formModel.color || '').trim()
  const emboss = String(formModel.emboss || '').trim()
  const base = {
    buyer_code: buyer,
    limit: 60,
  }
  const withMaterial = !swatchAllMaterials && material
  const dimensionFilters = {
    color_name: color || undefined,
    emboss: emboss || undefined,
  }
  let options = await lookupColorSwatchRecipes({
    ...base,
    material_name: withMaterial ? material : undefined,
    include_all_materials: swatchAllMaterials || undefined,
    ...dimensionFilters,
  })

  let retriedWithoutMaterial = false
  if (!options.length && withMaterial) {
    options = await lookupColorSwatchRecipes({
      ...base,
      include_all_materials: true,
      ...dimensionFilters,
    })
    retriedWithoutMaterial = options.length > 0
  }

  if (!options.length && (color || emboss)) {
    options = await lookupColorSwatchRecipes({
      ...base,
      material_name: withMaterial ? material : undefined,
      include_all_materials: swatchAllMaterials || undefined,
    })
    if (!options.length && withMaterial) {
      options = await lookupColorSwatchRecipes({
        ...base,
        include_all_materials: true,
      })
      retriedWithoutMaterial = options.length > 0
    }
  }

  if ((color || emboss) && options.length) {
    const best = pickBestSwatchRecipe(options, { material, color, emboss })
    const matched = pickMatchingSwatchRecipes(options, {
      material,
      color,
      emboss,
      requireEmboss: false,
    })
    if (best || matched.length) {
      const rest = matched.filter((x) => !best || x.id !== best.id)
      options = best ? [best, ...rest] : matched
    }
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
    autoFieldMeta.color_reference = true
  }
  if (fill.color_standard) {
    formModel.color_standard = fill.color_standard
    autoFieldMeta.color_standard = true
  }
  if (fill.emboss) {
    formModel.emboss = fill.emboss
    materialFieldOverride.emboss = true
  }
  if (fill.backing) {
    formModel.backing = fill.backing
    autoFieldMeta.backing = true
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
