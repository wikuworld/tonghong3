/** Cascade opsi emboss/warna rencana produksi dari peta color swatch. */

import { swatchEmbossMatch, swatchMaterialsMatch } from './poColorSwatch.js'

const COMBO_SEP = '\x1e'

export function distinctSorted(values) {
  const seen = new Set()
  const out = []
  for (const raw of values || []) {
    const v = String(raw || '').trim()
    if (!v) continue
    const key = v.toLowerCase()
    if (seen.has(key)) continue
    seen.add(key)
    out.push(v)
  }
  return out.sort((a, b) => a.localeCompare(b, undefined, { sensitivity: 'base' }))
}

export function mergeStringMaps(...maps) {
  const out = {}
  for (const map of maps) {
    for (const [key, vals] of Object.entries(map || {})) {
      if (!out[key]) out[key] = []
      out[key].push(...(vals || []))
    }
  }
  for (const key of Object.keys(out)) {
    out[key] = distinctSorted(out[key])
  }
  return out
}

/** Emboss color swatch untuk material terpilih (nama longgar, sama seperti master swatch). */
export function embossesForMaterial(embossesByMaterial, materialName) {
  const mat = String(materialName || '').trim()
  if (!mat) return []
  const collected = []
  for (const [key, vals] of Object.entries(embossesByMaterial || {})) {
    const name = String(key || '').trim()
    if (!name) continue
    if (!swatchMaterialsMatch(name, mat)) continue
    collected.push(...(vals || []))
  }
  return distinctSorted(collected)
}

/** Warna swatch untuk pasangan material + emboss (nama/kode longgar). */
export function colorsForMaterialEmboss(colorsByMaterialEmboss, materialName, emboss) {
  const mat = String(materialName || '').trim()
  const emb = String(emboss || '').trim()
  if (!mat || !emb) return []
  const collected = []
  for (const [key, vals] of Object.entries(colorsByMaterialEmboss || {})) {
    const idx = String(key).indexOf(COMBO_SEP)
    const keyMat = (idx >= 0 ? key.slice(0, idx) : key).trim()
    const keyEmb = (idx >= 0 ? key.slice(idx + COMBO_SEP.length) : '').trim()
    if (!swatchMaterialsMatch(keyMat, mat)) continue
    const embOk =
      swatchEmbossMatch(keyEmb, emb) || keyEmb.toLowerCase() === emb.toLowerCase()
    if (!embOk) continue
    collected.push(...(vals || []))
  }
  return distinctSorted(collected)
}

export function materialsWithEmboss(materials, embossesByMaterial) {
  const fromMap = Object.entries(embossesByMaterial || {})
    .filter(([, vals]) => (vals || []).some((v) => String(v || '').trim()))
    .map(([key]) => key)
  return distinctSorted([...(materials || []), ...fromMap])
}
