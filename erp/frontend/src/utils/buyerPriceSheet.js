export function uniqueMaterialNames(items) {
  const seen = new Set()
  const names = []
  for (const item of items || []) {
    const name = String(item?.material_name || '').trim()
    if (!name) continue
    const key = name.toLowerCase()
    if (seen.has(key)) continue
    seen.add(key)
    names.push(name)
  }
  names.sort((a, b) => a.localeCompare(b, 'en', { sensitivity: 'base' }))
  return names
}

export function thicknessOptionsForMaterial(items, materialName) {
  const want = String(materialName || '').trim().toLowerCase()
  if (!want) return []
  const seen = new Set()
  const out = []
  for (const item of items || []) {
    if (String(item?.material_name || '').trim().toLowerCase() !== want) continue
    const thick = String(item?.thickness_range || '').trim()
    if (!thick) continue
    const key = thick.toLowerCase()
    if (seen.has(key)) continue
    seen.add(key)
    out.push(thick)
  }
  return out
}

export const ADDON_FLAG_KEYS = [
  ['flag_color_black', 'COLOR BLACK'],
  ['flag_color', 'COLOR COLOR'],
  ['flag_flourasent', 'FLOURASENT'],
  ['flag_metalic', 'METALIC'],
  ['flag_emboss', 'EMBOSS'],
  ['flag_special_emboss', 'SPESIAL EMBOSS'],
]

function normKey(value) {
  return String(value || '').trim().toLowerCase()
}

export function priceAddonFilled(value) {
  if (value == null || value === '') return false
  const num = Number(value)
  return Number.isFinite(num) && num > 0
}

export function priceAddonEntered(value) {
  if (value == null || value === '') return false
  const num = Number(value)
  return Number.isFinite(num) && num >= 0
}

export function missingAddonsForRow(row, items) {
  const wantMat = normKey(row?.ITEM)
  const wantThick = normKey(row?.THICKNESS)
  if (!wantMat || !wantThick) return []
  const missing = []
  for (const [flag, key] of ADDON_FLAG_KEYS) {
    const required = (items || []).some((item) => {
      if (normKey(item?.material_name) !== wantMat) return false
      if (normKey(item?.thickness_range) !== wantThick) return false
      return Boolean(item?.[flag])
    })
    if (required && !priceAddonEntered(row?.[key])) missing.push(key)
  }
  return missing
}

export function missingRequiredPricesForRow(row) {
  const item = String(row?.ITEM || '').trim()
  if (!item) return []
  if (!priceAddonFilled(row?.['COLOR WHITE'])) return ['COLOR WHITE']
  return []
}

export function applyItemSelection(row, materialName, items) {
  const next = { ...(row || {}), ITEM: materialName || '' }
  const options = thicknessOptionsForMaterial(items, materialName)
  const current = String(row?.THICKNESS || '').trim()
  if (options.length === 1) {
    next.THICKNESS = options[0]
  } else if (!options.includes(current)) {
    next.THICKNESS = ''
  } else {
    next.THICKNESS = current
  }
  return next
}
