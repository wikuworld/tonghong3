/** Master Color Window untuk baris SO material Suede. */

import { COLOR_WINDOW_STANDARD_LABEL, normalizeColorRefKey } from './poColorStandard.js'
import { compactSwatchColorName, normalizeSwatchColorName } from './poColorSwatch.js'

export { COLOR_WINDOW_STANDARD_LABEL }

export function colorWindowOptionLabel(row) {
  if (!row) return ''
  const name = String(row.color_name || '').trim()
  const code = String(row.color_code || '').trim()
  if (name && code) return `${name} (${code})`
  return name || code
}

export function poBrandCodeForColorWindow(formModel, brands = []) {
  const bid = formModel?.brand_id
  const brand = brands.find((b) => b.id === bid)
  const code = String(brand?.code || formModel?.buyer || '').trim().toUpperCase()
  return code
}

export async function fetchColorWindowOptionList({
  formModel,
  brands,
  listColorWindowsPage,
}) {
  const brandCode = poBrandCodeForColorWindow(formModel, brands)
  if (!brandCode) return []

  const color = String(formModel.color || '').trim()
  const page = await listColorWindowsPage({
    brand_code: brandCode,
    q: color || undefined,
    limit: 200,
    offset: 0,
    sort_by: 'color_name',
    sort_dir: 'asc',
  })
  let items = page.items || []

  if (color && items.length) {
    const matched = pickMatchingColorWindows(items, { color })
    if (matched.length) items = matched
  }

  return items
}

export function pickMatchingColorWindows(options, { color, colorCode } = {}) {
  const cn = normalizeSwatchColorName(color)
  const cc = String(colorCode || '').trim().toUpperCase()
  if (!cn && !cc) return options || []

  return (options || []).filter((row) => {
    const name = normalizeSwatchColorName(row.color_name)
    const code = String(row.color_code || '').trim().toUpperCase()
    if (cc && code === cc) return true
    if (!cn) return false
    if (name === cn || name.startsWith(cn) || cn.startsWith(name)) return true
    const compact = compactSwatchColorName(color)
    const rowCompact = compactSwatchColorName(row.color_name)
    return Boolean(compact && compact === rowCompact)
  })
}

export function pickBestColorWindow(options, { color, colorCode } = {}) {
  const matched = pickMatchingColorWindows(options, { color, colorCode })
  if (matched.length) return matched[0]
  return (options || [])[0] || null
}

export function matchColorWindowOption(options, colorReference, colorCode) {
  const ref = normalizeColorRefKey(colorReference)
  const code = String(colorCode || '').trim().toUpperCase()
  return (
    (options || []).find((row) => {
      const label = normalizeColorRefKey(colorWindowOptionLabel(row))
      const rowCode = String(row.color_code || '').trim().toUpperCase()
      return (code && rowCode === code) || (ref && label === ref)
    }) || null
  )
}

export function applyColorWindowRow(
  row,
  { formModel, autoFieldMeta, selectedColorWindowId, selectedSwatchId },
) {
  if (!row || !formModel) return false
  if (selectedSwatchId) selectedSwatchId.value = null
  if (selectedColorWindowId) selectedColorWindowId.value = row.id
  formModel.color_reference = colorWindowOptionLabel(row)
  formModel.color_standard = COLOR_WINDOW_STANDARD_LABEL
  if (autoFieldMeta) {
    autoFieldMeta.color_reference = true
    autoFieldMeta.color_standard = true
  }
  return true
}
