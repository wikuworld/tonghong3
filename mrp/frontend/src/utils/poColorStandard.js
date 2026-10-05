/** Sumber color standard PU pada baris SO. */

export const COLOR_STANDARD_SOURCE = {
  SWATCH: 'swatch',
  CSI: 'csi',
  WAITING: 'waiting',
  MANUAL: 'manual',
}

export const WAITING_CS_LABEL = 'WAITING C/S'
export const CSI_STANDARD_LABEL = 'CSI'

export function normalizeColorRefKey(value) {
  return String(value || '')
    .trim()
    .toUpperCase()
    .replace(/[.\s]+/g, ' ')
    .replace(/\s*\/\s*/g, '/')
    .trim()
}

export function isWaitingColorRef(value) {
  const key = normalizeColorRefKey(value).replace(/\s/g, '')
  return key === 'WAITINGC/S' || key === 'WAITINGCS' || key === 'WAITC/S' || key === 'WAITCS'
}

export function extractColorCodeFromReference(value) {
  const raw = String(value || '').trim()
  if (!raw) return ''
  const m = raw.match(/\(([A-Za-z0-9][A-Za-z0-9._/\- ]{0,62})\)/)
  if (m) return String(m[1] || '').trim().toUpperCase()
  if (!/\s/.test(raw)) return raw.toUpperCase()
  return ''
}

export function csiColorOptionLabel(row) {
  if (!row) return ''
  const name = String(row.color_name || '').trim()
  const code = String(row.color_code || '').trim()
  if (name && code) return `${name} (${code})`
  return name || code
}

export function inferColorStandardSource(line) {
  if (line?.color_swatch_recipe_id) return COLOR_STANDARD_SOURCE.SWATCH
  if (isWaitingColorRef(line?.color_reference) || isWaitingColorRef(line?.color_standard)) {
    return COLOR_STANDARD_SOURCE.WAITING
  }
  if (normalizeColorRefKey(line?.color_standard) === CSI_STANDARD_LABEL) {
    return COLOR_STANDARD_SOURCE.CSI
  }
  if (String(line?.color_reference || '').trim() || String(line?.color_standard || '').trim()) {
    return COLOR_STANDARD_SOURCE.MANUAL
  }
  return ''
}

export function matchCsiOption(options, colorReference, colorCode) {
  const ref = normalizeColorRefKey(colorReference)
  const code = String(colorCode || extractColorCodeFromReference(colorReference) || '')
    .trim()
    .toUpperCase()
  return (options || []).find((row) => {
    const rowCode = String(row.color_code || '').trim().toUpperCase()
    const label = normalizeColorRefKey(csiColorOptionLabel(row))
    return (code && rowCode === code) || (ref && label === ref) || (ref && rowCode === ref)
  }) || null
}

export function applyCsiColorToForm(row, formModel, autoFieldMeta) {
  if (!row || !formModel) return
  formModel.color_reference = csiColorOptionLabel(row)
  formModel.color_standard = CSI_STANDARD_LABEL
  if (autoFieldMeta) {
    autoFieldMeta.color_reference = true
    autoFieldMeta.color_standard = true
  }
}

export function applyWaitingCsToForm(formModel, autoFieldMeta) {
  if (!formModel) return
  formModel.color_reference = WAITING_CS_LABEL
  formModel.color_standard = WAITING_CS_LABEL
  if (autoFieldMeta) {
    autoFieldMeta.color_reference = true
    autoFieldMeta.color_standard = true
  }
}

export function hasColorStandardValue(formModel, { selectedSwatchId, source } = {}) {
  if (selectedSwatchId) return true
  if (source === COLOR_STANDARD_SOURCE.WAITING) return true
  if (String(formModel?.color_reference || '').trim()) return true
  if (String(formModel?.color_standard || '').trim()) return true
  return false
}
