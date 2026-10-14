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
