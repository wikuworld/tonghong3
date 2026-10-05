import { describe, expect, it } from 'vitest'
import {
  colorsForMaterialEmboss,
  distinctSorted,
  embossesForMaterial,
  materialsWithEmboss,
  mergeStringMaps,
} from './mrpSwatchCascade.js'

describe('mrpSwatchCascade', () => {
  const embossesByMaterial = {
    '(PM) GENERIC PU COATED': ['AR-20 M', 'DE-73 SM'],
    'GENERIC PU COATED LEATHER': ['AR-107 M', 'AR-167 DM', 'DE-73 SM'],
    'VIRGIN HYDRO PU': ['AR-121'],
  }

  it('unions emboss from matching color-swatch material names', () => {
    const got = embossesForMaterial(embossesByMaterial, '(PM) GENERIC PU COATED')
    expect(got).toContain('AR-20 M')
    expect(got).toContain('AR-107 M')
    expect(got).toContain('AR-167 DM')
    expect(got).not.toContain('AR-121')
  })

  it('returns empty emboss when material is blank', () => {
    expect(embossesForMaterial(embossesByMaterial, '')).toEqual([])
  })

  it('matches colors across material/emboss variants', () => {
    const colors = {
      ['generic pu coated\x1ear-107 m']: ['METAL GREY'],
      ['generic pu coated leather\x1ear-107 m']: ['WOLF GREY'],
      ['virgin hydro pu\x1ear-121']: ['PINK SICLE'],
    }
    const got = colorsForMaterialEmboss(colors, 'GENERIC PU COATED LEATHER', 'AR-107 M')
    expect(got).toEqual(['METAL GREY', 'WOLF GREY'])
    expect(colorsForMaterialEmboss(colors, 'VIRGIN HYDRO PU', 'AR-107 M')).toEqual([])
  })

  it('merges maps and lists materials that have emboss', () => {
    const merged = mergeStringMaps(
      { A: ['X'] },
      { A: ['Y'], B: ['Z'] },
    )
    expect(merged.A).toEqual(['X', 'Y'])
    expect(materialsWithEmboss(['B'], { A: ['X'], C: [''] })).toEqual(['A', 'B'])
    expect(distinctSorted(['b', 'A', 'a'])).toEqual(['A', 'b'])
  })
})
